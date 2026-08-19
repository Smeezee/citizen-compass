"""
UEX item-category importer (A3 of the shop/price layer order, 2026-08-19).

Loads the 100 rows of `categories.json` from a sealed UEX snapshot into
`item_categories`. This is the smallest of the shop-layer importers and it
exists at A3 rather than in phase B because A3's acceptance is stated in rows,
not in DDL: "100 rows, sections group correctly".

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not skip `is_game_related = 0` rows. §3.8 of the order: those are
imported and flagged. Fourteen of the hundred are flagged that way, and
dropping them here would make "hide non-game categories" an irreversible
importer decision instead of a reversible display one.

It never deletes. A category that vanishes from a future snapshot is left in
place - app/preservation.py enforces that at the engine, but the importer is
written as if it did not, because a guard you rely on is one you stop thinking
about.

Usage:
    venv/Scripts/python.exe import_uex_categories.py
    venv/Scripts/python.exe import_uex_categories.py --dry-run
    venv/Scripts/python.exe import_uex_categories.py --snapshot 20260801T235530Z
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import ItemCategory  # noqa: E402

SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
DEFAULT_SNAPSHOT = "20260801T235530Z"
LOG_PATH = PROJECT_ROOT / "logs" / "shop_layer_import.log"

# Fields promoted to real columns. Everything else in the source row goes to
# `detail` untouched - §3.5, a field whose meaning is unclear is preserved, not
# dropped and not given a guessed column.
PROMOTED = {"id", "type", "section", "name", "is_game_related", "is_mining",
            "date_modified"}


def log(message: str) -> None:
    """One line per run, matching the project's per-tool log convention.

    No Unicode symbols: the known caveat in CLAUDE.md is that these log
    helpers can crash on them when running with no console attached, and the
    print() fails before the file write.
    """
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] categories: {message}"
    print(line)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_rows(snapshot: str) -> list[dict]:
    path = SNAPSHOT_ROOT / snapshot / "categories.json"
    if not path.exists():
        raise SystemExit(f"snapshot file not found: {path}")
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)

    # UEX wraps everything in {"status", "http_code", "data", "message"}. A
    # bare list would mean the file is not what this importer thinks it is, so
    # say that rather than guessing at the shape.
    if not isinstance(payload, dict) or "data" not in payload:
        raise SystemExit(
            f"{path} is not a UEX envelope (no 'data' key) - refusing to guess "
            f"at its shape"
        )
    rows = payload["data"]
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"{path} carries no rows - refusing to report success")
    return rows


def to_dt(value):
    """A UEX unix timestamp as a datetime, or None. 0 means 'never', not 1970."""
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return None
    if seconds <= 0:
        return None
    return datetime.datetime.fromtimestamp(seconds, tz=datetime.timezone.utc).replace(tzinfo=None)


def to_bool(value):
    if value is None:
        return None
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true",
                        help="parse and report, write nothing")
    args = parser.parse_args()

    rows = load_rows(args.snapshot)
    log(f"snapshot {args.snapshot}: {len(rows)} source rows"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")

    inserted = updated = unchanged = 0
    with Session(engine) as session:
        existing = {
            c.uex_id: c
            for c in session.execute(select(ItemCategory)).scalars()
        }
        for row in rows:
            uex_id = row.get("id")
            if uex_id is None:
                log(f"SKIPPED a row with no id: {row!r}")
                continue

            detail = {k: v for k, v in row.items() if k not in PROMOTED}
            values = {
                "type": row.get("type"),
                "section": row.get("section"),
                "name": row.get("name"),
                "is_game_related": to_bool(row.get("is_game_related")),
                "is_mining": to_bool(row.get("is_mining")),
                "source_date_modified": to_dt(row.get("date_modified")),
                "detail": detail or None,
                "verification_source": f"uexcorp snapshot {args.snapshot}",
                "confidence": "medium",
            }

            current = existing.get(uex_id)
            if current is None:
                inserted += 1
                if not args.dry_run:
                    session.add(ItemCategory(uex_id=uex_id, **values))
            else:
                changed = [
                    k for k, v in values.items()
                    if getattr(current, k) != v
                ]
                if changed:
                    updated += 1
                    if not args.dry_run:
                        for k, v in values.items():
                            setattr(current, k, v)
                else:
                    unchanged += 1

        if args.dry_run:
            session.rollback()
        else:
            session.commit()

    with Session(engine) as session:
        total = session.query(ItemCategory).count()
        sections = session.query(ItemCategory.section).distinct().count()
        non_game = session.query(ItemCategory).filter(
            ItemCategory.is_game_related.is_(False)
        ).count()

    log(f"inserted {inserted}, updated {updated}, unchanged {unchanged}")
    log(f"item_categories now holds {total} rows across {sections} sections "
        f"({non_game} flagged is_game_related=0, imported not skipped)")

    # Fail closed: the source said 100 rows, so the table must hold at least
    # 100. Reporting success on a short import is the exact silent-success
    # failure rule 12 is about.
    if not args.dry_run and total < len(rows):
        log(f"FAILED: source had {len(rows)} rows, table holds {total}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
