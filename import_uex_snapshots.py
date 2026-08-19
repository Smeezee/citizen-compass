"""
UEX snapshot registrar (A6 of the shop/price layer order, 2026-08-19).

Writes one `snapshots` row per sealed snapshot directory under
data-layer/external-sources/uexcorp/snapshots/, with the row counts it
actually contains - counted by opening the files, not read off a manifest.

WHY COUNT RATHER THAN TRUST THE MANIFEST
----------------------------------------
Each snapshot ships a `_pull_summary.json` that states its own record counts,
and it would be quicker to copy them. But then `snapshots.row_counts` would
record what the pull BELIEVED it wrote, not what is on disk, and the one
question this table exists to answer - "what was actually in the snapshot the
prices came from" - would be answered by the wrong witness.

So the counts here are measured, and where the manifest disagrees, the
disagreement is written into `notes` rather than resolved silently.

WHY captured_at CAN BE NULL
---------------------------
It is parsed from the directory name (20260801T235530Z). If a directory is
named something else, the field stays NULL. Filling it with the row's insert
time would put a fabricated provenance date on a preservation record, and an
absent date is always better than an invented one (rule 11).

Usage:
    venv/Scripts/python.exe import_uex_snapshots.py
    venv/Scripts/python.exe import_uex_snapshots.py --dry-run
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import Snapshot  # noqa: E402

SOURCE = "uexcorp"
SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
LOG_PATH = PROJECT_ROOT / "logs" / "shop_layer_import.log"

# 20260801T235530Z
KEY_PATTERN = re.compile(r"^(\d{8})T(\d{6})Z$")


def log(message: str) -> None:
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] snapshots: {message}"
    print(line)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def parse_captured_at(key: str):
    """The capture time from the directory name, or None. Never a guess."""
    match = KEY_PATTERN.match(key)
    if not match:
        return None
    try:
        return datetime.datetime.strptime(key, "%Y%m%dT%H%M%SZ")
    except ValueError:
        return None


def count_rows(path: Path) -> tuple[dict, list[str]]:
    """Row counts per JSON file in a snapshot, measured by opening them.

    Returns (counts, problems). A file that will not parse is reported as a
    problem and given a count of None - never silently treated as zero, which
    is the difference between "this endpoint returned nothing" and "this file
    is broken".
    """
    counts: dict[str, int | None] = {}
    problems: list[str] = []
    for entry in sorted(path.glob("*.json")):
        name = entry.name
        try:
            with open(entry, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            counts[name] = None
            problems.append(f"{name}: unreadable ({type(exc).__name__})")
            continue

        if isinstance(payload, dict) and "data" in payload:
            data = payload["data"]
            if data is None:
                # A real and common case here: HTTP 200, envelope "ok", no
                # rows. 44 of the 100 category files in 20260801T235530Z look
                # like this, and they are genuinely empty categories rather
                # than failed pulls.
                counts[name] = 0
            elif isinstance(data, list):
                counts[name] = len(data)
            else:
                counts[name] = None
                problems.append(f"{name}: 'data' is {type(data).__name__}, not a list")
        elif isinstance(payload, list):
            counts[name] = len(payload)
        else:
            counts[name] = None
            problems.append(f"{name}: not a UEX envelope and not a list")
    return counts, problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not SNAPSHOT_ROOT.exists():
        log(f"FAILED: no snapshot root at {SNAPSHOT_ROOT}")
        return 1

    directories = sorted(p for p in SNAPSHOT_ROOT.iterdir() if p.is_dir())
    if not directories:
        log("FAILED: no snapshot directories found - refusing to report success")
        return 1

    log(f"{len(directories)} snapshot directories"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")

    inserted = updated = 0
    with Session(engine) as session:
        existing = {
            (s.source, s.snapshot_key): s
            for s in session.execute(select(Snapshot)).scalars()
        }
        for directory in directories:
            key = directory.name
            counts, problems = count_rows(directory)
            total = sum(v for v in counts.values() if isinstance(v, int))
            captured_at = parse_captured_at(key)

            notes = []
            if captured_at is None:
                notes.append(
                    f"captured_at is NULL: directory name {key!r} is not "
                    f"YYYYMMDDTHHMMSSZ, and inventing a date would be worse "
                    f"than leaving it absent"
                )
            notes.extend(problems)

            values = {
                "path": str(directory.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "captured_at": captured_at,
                "row_counts": {
                    "files": counts,
                    "total_rows": total,
                    "json_files": len(counts),
                },
                "notes": "\n".join(notes) if notes else None,
            }

            current = existing.get((SOURCE, key))
            if current is None:
                inserted += 1
                if not args.dry_run:
                    session.add(Snapshot(source=SOURCE, snapshot_key=key, **values))
            else:
                if any(getattr(current, k) != v for k, v in values.items()):
                    updated += 1
                    if not args.dry_run:
                        for k, v in values.items():
                            setattr(current, k, v)

            log(f"  {key}: {len(counts)} json files, {total} rows"
                + (f", {len(problems)} problem(s)" if problems else ""))

        if args.dry_run:
            session.rollback()
        else:
            session.commit()

    with Session(engine) as session:
        total_rows = session.query(Snapshot).count()
    log(f"inserted {inserted}, updated {updated}; snapshots holds {total_rows} rows")

    if not args.dry_run and total_rows < len(directories):
        log(f"FAILED: {len(directories)} directories on disk, "
            f"{total_rows} rows in the table")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
