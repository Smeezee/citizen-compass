"""
UEX items importer for CATEGORY 20 ONLY (B2 of the shop/price layer order).

1,099 rows - the largest single category file in 20260801T235530Z. Category 20
is "Liveries": ship paints, section "Liveries", almost all of them carrying a
`vehicle_name` and a store URL.

CONCRETE ON PURPOSE. NOT GENERIC. RESIST.
-----------------------------------------
§B2 says so in those words, and the standing rule behind it is that the
abstraction guessed in advance is always the wrong one. This file therefore
hardcodes category 20, knows what a livery row looks like, and makes no
attempt to be reusable. B4 reads this and its two siblings and extracts what
they GENUINELY shared - which is not knowable yet.

WHAT THIS FILE LEARNED ABOUT CATEGORY 20, written down because B4 needs it
--------------------------------------------------------------------------
  * 1,099 rows, of which 299 (27%) carry NO uuid
  * `size` is the string "" for nearly all of them, and is not a number
  * `color` and `color2` exist here and in almost no other category
  * `id_vehicle` / `vehicle_name` are populated, which is unusual - most
    categories have no vehicle at all
  * `wiki` and `notification` are null on every single row

Usage:
    venv/Scripts/python.exe import_uex_items_category20.py
    venv/Scripts/python.exe import_uex_items_category20.py --dry-run
"""

import argparse
import datetime
import sys
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

CATEGORY_ID = 20
SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
DEFAULT_SNAPSHOT = "20260801T235530Z"
LOG_PATH = PROJECT_ROOT / "logs" / "shop_layer_import.log"

# Promoted to real columns. Everything else on the row goes to `detail`
# untouched - §3.5. For category 20 that tail is color, color2, quality,
# the three is_exclusive_* flags, is_commodity, is_harvestable, screenshot,
# game_version, wiki, notification, id_parent, id_company, id_vehicle and
# date_added.
PROMOTED = {
    "id", "uuid", "name", "id_category", "category", "section",
    "company_name", "vehicle_name", "size", "slug", "url_store",
    "date_modified",
}


log = make_logger(f"items_cat{CATEGORY_ID}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = SNAPSHOT_ROOT / args.snapshot / f"items_category_{CATEGORY_ID}.json"
    rows = load_envelope(path)

    log(f"snapshot {args.snapshot}, category {CATEGORY_ID}: {len(rows)} source rows"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")
    if not rows:
        log(f"FAILED: category {CATEGORY_ID} carried no rows, and this "
            f"category is known to hold 1,099 - refusing to report success")
        return 1

    inserted = updated = unchanged = 0
    no_uuid = 0
    unknown_category = []

    with Session(engine) as session:
        categories = {
            c.uex_id: c.id
            for c in session.execute(select(ItemCategory)).scalars()
        }
        existing = {
            i.uex_id: i
            for i in session.execute(
                select(ShopItem).where(ShopItem.uex_id.in_(
                    [r["id"] for r in rows if r.get("id") is not None]
                ))
            ).scalars()
        }

        for row in rows:
            uex_id = row.get("id")
            if uex_id is None:
                log(f"SKIPPED a row with no id: {row!r}")
                continue

            source_category = row.get("id_category")
            category_id = categories.get(source_category)
            if category_id is None and source_category is not None:
                # Reported, not invented. A row whose category is not held
                # still imports - §3.6's spirit, absence is data - but the
                # gap is named rather than papered over with a NULL nobody
                # notices.
                unknown_category.append(
                    f"item {uex_id} ({row.get('name')!r}) is in category "
                    f"{source_category}, which is not in item_categories"
                )

            uuid = clean(row.get("uuid"))
            if uuid is None:
                no_uuid += 1

            detail = split_detail(row, PROMOTED)
            values = {
                "uuid": uuid,
                "name": clean(row.get("name")) or f"item {uex_id}",
                "category_id": category_id,
                "category_name": clean(row.get("category")),
                "section": clean(row.get("section")),
                "company_name": clean(row.get("company_name")),
                "vehicle_name": clean(row.get("vehicle_name")),
                # A STRING. UEX sends "", "1" and "S3" in this field depending
                # on the category; coercing to int would either crash or
                # invent a number.
                "size": clean(row.get("size")),
                "slug": clean(row.get("slug")),
                "url_store": clean(row.get("url_store")),
                "source_date_modified": to_dt(row.get("date_modified")),
                "detail": detail,
                "verification_source": f"uexcorp snapshot {args.snapshot}",
                "confidence": "medium",
            }

            current = existing.get(uex_id)
            if current is None:
                inserted += 1
                if not args.dry_run:
                    session.add(ShopItem(uex_id=uex_id, **values))
            else:
                if any(getattr(current, k) != v for k, v in values.items()):
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

    log(f"inserted {inserted}, updated {updated}, unchanged {unchanged}")
    log(f"{no_uuid} of {len(rows)} rows carry no uuid "
        f"({no_uuid / len(rows):.1%}) - imported on uex_id, which is why "
        f"uex_id is the key and not uuid")
    if unknown_category:
        log(f"{len(unknown_category)} row(s) reference an unheld category:")
        for line in unknown_category[:10]:
            log(f"    {line}")

    with Session(engine) as session:
        stored = session.query(ShopItem).filter(
            ShopItem.category_name == "Liveries"
        ).count()
        total = session.query(ShopItem).count()
    log(f"shop_items holds {total} rows; {stored} in this category")

    if args.dry_run:
        return 0
    if stored < len(rows):
        log(f"FAILED: source had {len(rows)} rows, only {stored} stored")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
