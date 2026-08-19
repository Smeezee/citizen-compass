"""
UEX items importer, all categories (B5 of the shop/price layer order).

Runs the pipeline extracted at B4 over every `items_category_<N>.json` in a
snapshot. B2 did category 20 by hand; this does all 100, including the one B2
already did, so a single command brings the whole catalogue in.

THE NUMBER TO EXPECT, AND WHY IT IS NOT WHAT THE ORDER SAYS
------------------------------------------------------------
§2 of the order describes "~99 category files". There are 100, and 44 of them
carry `data: null` - no items at all. That is NOT a failed pull, and the
distinction was checked rather than assumed: all 100 entries in the snapshot's
own `_items_by_category_summary.json` record HTTP 200 with envelope status
"ok", and the manifest's record_count column totals 7,728, which matches an
independent recount of the files exactly.

So the acceptance figure for this item is **7,728 items across 56 non-empty
files**, not ~99 files' worth.

An empty category is therefore expected and is reported as empty. A category
that fails to PARSE is a different thing entirely and stops the run - see
load_envelope() in app/uex_pipeline.py, and the control in
checks/_verify_shop_importers.py that watches it refuse nine kinds of broken
file while still accepting the 44 legitimately-empty ones.

Usage:
    venv/Scripts/python.exe import_uex_items_all.py
    venv/Scripts/python.exe import_uex_items_all.py --dry-run
    venv/Scripts/python.exe import_uex_items_all.py --only 20,32
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import ItemCategory, ShopItem  # noqa: E402
from app.uex_pipeline import (  # noqa: E402
    clean,
    load_envelope,
    make_logger,
    split_detail,
    to_dt,
)

SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
DEFAULT_SNAPSHOT = "20260801T235530Z"
FILE_PATTERN = re.compile(r"^items_category_(\d+)\.json$")

# Same promoted set as B2. Deliberately one set for every category rather than
# a per-category map: the columns are the ones the site queries, and a field
# that is only meaningful to one category belongs in `detail` by definition.
PROMOTED = {
    "id", "uuid", "name", "id_category", "category", "section",
    "company_name", "vehicle_name", "size", "slug", "url_store",
    "date_modified",
}

log = make_logger("items_all")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only", default=None,
                        help="comma-separated category ids, for re-running one")
    args = parser.parse_args()

    base = SNAPSHOT_ROOT / args.snapshot
    if not base.is_dir():
        log(f"FAILED: no snapshot directory at {base}")
        return 1

    wanted = None
    if args.only:
        wanted = {int(x) for x in args.only.split(",") if x.strip()}

    files = []
    for path in sorted(base.glob("items_category_*.json")):
        match = FILE_PATTERN.match(path.name)
        if not match:
            continue
        category = int(match.group(1))
        if wanted is None or category in wanted:
            files.append((category, path))

    if not files:
        log("FAILED: no items_category_*.json files matched - refusing to "
            "report success on an empty run")
        return 1

    # Read every file BEFORE writing anything. A malformed file at position 90
    # must not leave 89 categories imported and the run half-done; this makes
    # the loud failure happen before the first insert.
    source = {}
    for category, path in files:
        source[category] = load_envelope(path)

    expected_total = sum(len(v) for v in source.values())
    empty = [c for c, rows in source.items() if not rows]

    # EVERY file empty is not a legitimate state, it is a broken pull.
    # 44 empty categories is normal; 100 would mean UEX returned null across
    # the board, and without this the run would report "0 source items" and
    # exit 0 - a textbook silent success. Caught here rather than in the
    # per-file guard, because each individual file would be perfectly valid.
    if expected_total == 0:
        log(f"FAILED: all {len(files)} category files are empty. That is not "
            f"a catalogue with no items in it, that is a pull that did not "
            f"land - refusing to report success.")
        return 1
    log(f"snapshot {args.snapshot}: {len(files)} category files, "
        f"{len(files) - len(empty)} with rows, {len(empty)} empty, "
        f"{expected_total} source items"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")
    log(f"empty categories (HTTP 200, envelope ok, no rows): "
        f"{sorted(empty)}")

    inserted = updated = unchanged = 0
    no_uuid = 0
    unknown_category = Counter()
    per_category = {}

    with Session(engine) as session:
        categories = {
            c.uex_id: c.id
            for c in session.execute(select(ItemCategory)).scalars()
        }
        existing = {
            i.uex_id: i
            for i in session.execute(select(ShopItem)).scalars()
        }

        for category, rows in source.items():
            before = (inserted, updated, unchanged)
            for row in rows:
                uex_id = row.get("id")
                if uex_id is None:
                    log(f"SKIPPED a row with no id in category {category}")
                    continue

                source_category = row.get("id_category")
                category_id = categories.get(source_category)
                if category_id is None and source_category is not None:
                    unknown_category[source_category] += 1

                uuid = clean(row.get("uuid"))
                if uuid is None:
                    no_uuid += 1

                values = {
                    "uuid": uuid,
                    "name": clean(row.get("name")) or f"item {uex_id}",
                    "category_id": category_id,
                    "category_name": clean(row.get("category")),
                    "section": clean(row.get("section")),
                    "company_name": clean(row.get("company_name")),
                    "vehicle_name": clean(row.get("vehicle_name")),
                    "size": clean(row.get("size")),
                    "slug": clean(row.get("slug")),
                    "url_store": clean(row.get("url_store")),
                    "source_date_modified": to_dt(row.get("date_modified")),
                    "detail": split_detail(row, PROMOTED),
                    "verification_source": f"uexcorp snapshot {args.snapshot}",
                    "confidence": "medium",
                }

                current = existing.get(uex_id)
                if current is None:
                    inserted += 1
                    if not args.dry_run:
                        obj = ShopItem(uex_id=uex_id, **values)
                        existing[uex_id] = obj
                        session.add(obj)
                elif any(getattr(current, k) != v for k, v in values.items()):
                    updated += 1
                    if not args.dry_run:
                        for k, v in values.items():
                            setattr(current, k, v)
                else:
                    unchanged += 1

            per_category[category] = (
                len(rows),
                inserted - before[0],
                updated - before[1],
                unchanged - before[2],
            )

        if args.dry_run:
            session.rollback()
        else:
            session.commit()

    log(f"inserted {inserted}, updated {updated}, unchanged {unchanged}")
    log(f"{no_uuid} of {expected_total} rows carry no uuid "
        f"({no_uuid / expected_total:.1%})" if expected_total else "no rows")
    if unknown_category:
        log(f"{sum(unknown_category.values())} row(s) reference a category id "
            f"not held in item_categories: "
            f"{dict(unknown_category.most_common(10))}")

    with Session(engine) as session:
        total = session.query(ShopItem).count()
    log(f"shop_items holds {total} rows (source across these files: "
        f"{expected_total})")

    if args.dry_run:
        return 0

    # Fail closed on the exact acceptance §B5 states: total imported items
    # equals the sum of the source file lengths.
    if wanted is None and total < expected_total:
        log(f"FAILED: source files summed to {expected_total} items, "
            f"shop_items holds {total}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
