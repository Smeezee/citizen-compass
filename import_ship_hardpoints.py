"""
G8 - hardpoint slot structure from the derived files into PostgreSQL.

WHY THIS EXISTS
===============

The ship detail page has always carried a panel saying:

    "Hardpoint and component data is not in the site file yet. It lives in
     PostgreSQL and reaches this panel once the API is wired in. Slot structure
     shown, no invented values."

F3 established that the middle sentence was FALSE. The components are in
PostgreSQL; the hardpoint SLOTS were not, and `app/models.py` had no table for
them at all. They lived on disk, in two derived JSON files, produced by two
different programs on two different days:

    data-layer/derived/holo-hardpoints/hardpoints_fleet.json    167 models
    data-layer/derived/holo-hardpoints-join/hardpoints_join.json 35 models

So "wire in the API" could never have filled the panel. This is the import that
has to happen first, and it is what makes the panel's own text true rather than
aspirational.

WHAT IT IMPORTS, AND WHAT IT REFUSES TO INVENT
==============================================

Slots. Port name, kind, size, measured position, and whatever the mount data
says is fitted as stock. Nothing is computed, averaged, defaulted or filled in:
a mount with no published size gets NULL, not 0, because 0 reads as "size zero"
and NULL reads as "not stated".

IT ALSO IMPORTS THE ABSENCES, which is the part that makes the panel honest.
Every model the join report REFUSED or SKIPPED gets a coverage row carrying the
build's own reason. Without that, "we have not measured this hull" and "this
hull has no mounts" are the same blank panel, and showing the same nothing for
both is the polite version of making something up.

TWO DATASETS, ONE TABLE, EACH ROW SAYING WHICH
==============================================

`source_dataset` is stored per row rather than inferred, because the two files
were produced by different code with different guarantees - the fleet set was
placed in a cloud sandbox by place_fleet.py, the join set by this repo's
pure-Python port. Where a model appears in both, the FLEET set wins: it is the
original, and the port exists to agree with it rather than to replace it.

IDEMPOTENT. Re-running replaces this importer's own rows for a model and
inserts nothing new elsewhere. Nothing outside these two tables is touched.

Usage:
    venv/Scripts/python.exe import_ship_hardpoints.py --dry-run
    venv/Scripts/python.exe import_ship_hardpoints.py

Rule 15: encodings stated.
"""

import argparse
import io
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import ShipHardpoint, ShipHardpointCoverage  # noqa: E402

DERIVED = PROJECT_ROOT / "data-layer" / "derived"
FLEET = DERIVED / "holo-hardpoints" / "hardpoints_fleet.json"
JOIN = DERIVED / "holo-hardpoints-join" / "hardpoints_join.json"
JOIN_REPORT = DERIVED / "holo-hardpoints-join" / "join_report.json"

# Fleet first. Where a model is in both, the original wins - see the module
# docstring.
SOURCES = [("fleet", FLEET), ("join", JOIN)]


def log(message):
    sys.stdout.buffer.write((message + "\n").encode("utf-8", "backslashreplace"))
    sys.stdout.flush()


def model_key(raw):
    """One spelling for a model, whichever file named it.

    The two derived files disagree about how to write a model down: the fleet
    file keys on the mount-data name ("MISC Freelancer", "San'tok.yai"), the
    join file on the .glb stem ("Freelancer_DUR"). The site knows it by yet a
    third form, its folder name. All three normalise to the same thing here, so
    no new name-matching is invented - this is a spelling rule, not a matcher.
    """
    return re.sub(r"[^a-z0-9]+", " ", (raw or "").lower()).strip()


def read_json(path):
    if not path.exists():
        log(f"MISSING INPUT: {path}")
        return None
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def collect():
    """Every model and its slots, fleet winning ties. Returns (slots, coverage)."""
    slots = {}          # model_key -> (display_name, dataset, [hardpoint dicts])
    for dataset, path in SOURCES:
        payload = read_json(path)
        if payload is None:
            return None, None
        for raw_name, record in payload.items():
            key = model_key(record.get("bare") or raw_name)
            if key in slots:
                continue                      # fleet already claimed it
            hardpoints = record.get("hardpoints") or []
            slots[key] = (raw_name, dataset, hardpoints, record)

    coverage = {}
    report = read_json(JOIN_REPORT)
    if report is None:
        return None, None

    # The absences, carrying the build's own words for why.
    for bucket, status in (("refused", "refused"), ("skipped", "skipped")):
        for row in report.get(bucket) or []:
            key = model_key(row[0])
            if key in slots:
                continue
            coverage[key] = {
                "model_key": key,
                "status": status,
                "reason": row[-1] if len(row) > 1 else None,
                "slot_count": 0,
                "source_dataset": "join",
                "detail": {"reported_as": row[0], "bucket": bucket},
            }

    for key, (raw_name, dataset, hardpoints, record) in slots.items():
        coverage[key] = {
            "model_key": key,
            "status": "placed" if hardpoints else "absent",
            "reason": None if hardpoints else
                      "the dataset holds this model but lists no mounts for it",
            "slot_count": len(hardpoints),
            "source_dataset": dataset,
            "detail": {
                "reported_as": raw_name,
                "dimension": record.get("dimension"),
                "frame": record.get("frame"),
                "aligned": record.get("aligned"),
            },
        }
    return slots, coverage


def flatten(key, dataset, hardpoint):
    """One database row from one mount, inventing nothing."""
    items = hardpoint.get("items") or []
    first = items[0] if items else {}
    size = first.get("size")
    if not isinstance(size, int):
        size = None                    # "not stated", never 0
    return {
        "model_key": key,
        "port": hardpoint.get("port") or hardpoint.get("where") or "",
        "kind": hardpoint.get("kind"),
        "size": size,
        "stock_item_name": first.get("name"),
        "stock_item_type": first.get("type"),
        "source_dataset": dataset,
        "detail": {
            "items": items,
            "where": hardpoint.get("where"),
            "pilot": hardpoint.get("pilot"),
            "unit": hardpoint.get("unit"),
            "pos_model": hardpoint.get("pos_model"),
            "read": hardpoint.get("read"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log("G8 - ship hardpoint slots"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")

    slots, coverage = collect()
    if slots is None:
        log("FAILED: an input file is missing. Nothing was written.")
        return 1

    rows = []
    for key, (_, dataset, hardpoints, _record) in slots.items():
        seen = set()
        for hardpoint in hardpoints:
            row = flatten(key, dataset, hardpoint)
            if not row["port"] or row["port"] in seen:
                # A port with no name cannot be addressed, and a repeat would
                # double every count the panel shows. Both are reported rather
                # than silently collapsed.
                log(f"  SKIPPED a mount on {key!r}: "
                    f"{'no port name' if not row['port'] else 'duplicate port ' + row['port']}")
                continue
            seen.add(row["port"])
            rows.append(row)

    log(f"models with slots:      {len(slots)}")
    log(f"slot rows to write:     {len(rows)}")
    log(f"coverage rows to write: {len(coverage)}")
    by_status = {}
    for entry in coverage.values():
        by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
    for status in sorted(by_status):
        log(f"  {status:<10} {by_status[status]:>4}")

    if args.dry_run:
        log("")
        log("DRY RUN - nothing was written.")
        return 0

    with SessionLocal() as session:
        # This importer owns these two tables entirely and rewrites its own
        # rows. Not a preservation concern: these are DERIVED rows regenerated
        # from files that are themselves regenerated, and nothing else writes
        # here. Nothing outside these two tables is touched.
        existing_slots = {
            (row.model_key, row.port): row
            for row in session.execute(select(ShipHardpoint)).scalars()
        }
        existing_cover = {
            row.model_key: row
            for row in session.execute(select(ShipHardpointCoverage)).scalars()
        }

        inserted = updated = 0
        for row in rows:
            current = existing_slots.get((row["model_key"], row["port"]))
            if current is None:
                session.add(ShipHardpoint(**row))
                inserted += 1
            else:
                for field, value in row.items():
                    setattr(current, field, value)
                updated += 1

        cover_inserted = cover_updated = 0
        for key, entry in coverage.items():
            current = existing_cover.get(key)
            if current is None:
                session.add(ShipHardpointCoverage(**entry))
                cover_inserted += 1
            else:
                for field, value in entry.items():
                    setattr(current, field, value)
                cover_updated += 1

        session.commit()

        held_slots = session.query(ShipHardpoint).count()
        held_cover = session.query(ShipHardpointCoverage).count()

    log("")
    log(f"slots     inserted {inserted}, updated {updated} -> {held_slots} held")
    log(f"coverage  inserted {cover_inserted}, updated {cover_updated} "
        f"-> {held_cover} held")

    failures = []
    if held_slots < len(rows):
        failures.append(f"slots: {len(rows)} to write, {held_slots} held")
    if held_cover < len(coverage):
        failures.append(f"coverage: {len(coverage)} to write, {held_cover} held")
    for line in failures:
        log(f"FAILED: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
