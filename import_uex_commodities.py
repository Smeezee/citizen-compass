"""
UEX commodities importer (B6 of the shop/price layer order).

204 commodities and 2,597 commodity price rows from 20260806T033315Z, into the
same tables as items - `shop_items` and `item_prices` - per §B6 ("into the same
shape").

WHY shop_items NEEDED A NEW COLUMN TO ACCEPT THESE
---------------------------------------------------
Commodities are numbered from 1 in an id space entirely separate from items,
and **200 of the 204 commodity ids collide with item ids** while meaning
something completely different: id 1 is the "Omnisky III Cannon" as an item and
"Agricium" as a commodity. `uq_shop_items_uex_id` would have refused the second
of each pair. Migration 250bdcd72ac3 widens the key to (source_kind, uex_id).

Not one of the 204 commodities carries a uuid, which is worth recording next to
the A4 decision: had uuid been the join key, the entire commodity catalogue
would have been unkeyable.

WHAT GOES WHERE
---------------
Commodity prices carry fields items do not: scu_buy, scu_sell, scu_sell_stock,
status_buy, status_sell, container_sizes, and an `_avg` twin for nearly every
one. §B6 says those go in `detail`, and §3.1 independently forbids showing a
blended average as if it were a price - so `price_buy_avg` and `price_sell_avg`
go to `detail` too and are never written to the price columns. The columns get
the actual observed price and nothing else.

`commodities_status.json` is a legend, not data: it maps status codes 1-7 to
names like "Out of Stock (Empty)" and "Maximum Inventory (Full)". It is stored
on the snapshot row rather than duplicated onto 2,597 price rows.

RAW COMMODITY PRICES ARE A SEPARATE FILE AND ARE IMPORTED TOO
--------------------------------------------------------------
`commodities_raw_prices_all.json` holds 335 more rows for raw/unrefined
variants. They are the same shape and land the same way, flagged in `detail`
so the two are distinguishable.

Usage:
    venv/Scripts/python.exe import_uex_commodities.py
    venv/Scripts/python.exe import_uex_commodities.py --dry-run
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import ItemPrice, ShopItem, Snapshot, Terminal  # noqa: E402
from app.uex_pipeline import (  # noqa: E402
    append_only,
    clean,
    load_envelope,
    make_logger,
    split_detail,
    to_dt,
)

SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
DEFAULT_SNAPSHOT = "20260806T033315Z"
SOURCE_KIND = "commodity"
BATCH = 2000

COMMODITY_PROMOTED = {
    "id", "uuid", "name", "code", "kind", "date_modified",
}

log = make_logger("commodities")


def price_or_none(value):
    """Same rule as items: 0 means "not traded here", not "free"."""
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return None if number == 0 else number


def import_commodities(session, snapshot_key, rows, dry_run):
    existing = {
        item.uex_id: item
        for item in session.execute(
            select(ShopItem).where(ShopItem.source_kind == SOURCE_KIND)
        ).scalars()
    }
    inserted = updated = unchanged = 0

    for row in rows:
        uex_id = row.get("id")
        if uex_id is None:
            log(f"SKIPPED a commodity row with no id")
            continue

        values = {
            "uuid": clean(row.get("uuid")),
            "name": clean(row.get("name")) or f"commodity {uex_id}",
            "category_id": None,
            # UEX gives commodities a `kind` (Metal, Gas, Drug, ...) rather
            # than a category id. Stored as the category NAME with no FK,
            # because inventing an item_categories row for it would be
            # inventing an id UEX does not have (§3.5).
            "category_name": clean(row.get("kind")),
            "section": "Commodities",
            "company_name": None,
            "vehicle_name": None,
            "size": None,
            "slug": clean(row.get("code")),
            "url_store": clean(row.get("wiki")),
            "source_date_modified": to_dt(row.get("date_modified")),
            "detail": split_detail(row, COMMODITY_PROMOTED),
            "verification_source": f"uexcorp snapshot {snapshot_key}",
            "confidence": "medium",
        }

        current = existing.get(uex_id)
        if current is None:
            inserted += 1
            if not dry_run:
                obj = ShopItem(uex_id=uex_id, source_kind=SOURCE_KIND, **values)
                existing[uex_id] = obj
                session.add(obj)
        elif any(getattr(current, k) != v for k, v in values.items()):
            updated += 1
            if not dry_run:
                for k, v in values.items():
                    setattr(current, k, v)
        else:
            unchanged += 1

    return inserted, updated, unchanged


def build_price_rows(rows, commodities, terminals, snapshot_id, existing,
                     seen, is_raw):
    """Price dicts ready for append_only(), plus the counts of what was not
    placed. Nothing is silently dropped - every exclusion is counted."""
    pending = []
    skipped = Counter()

    for row in rows:
        item_id = commodities.get(row.get("id_commodity"))
        terminal_id = terminals.get(row.get("id_terminal"))
        if item_id is None:
            skipped["commodity not held"] += 1
            continue
        if terminal_id is None:
            skipped["terminal not held"] += 1
            continue

        key = (item_id, terminal_id)
        if key in existing or key in seen:
            skipped["already stored or duplicated in source"] += 1
            continue
        seen.add(key)

        buy = price_or_none(row.get("price_buy"))
        sell = price_or_none(row.get("price_sell"))
        if buy is None and sell is None:
            skipped["neither a buy nor a sell price"] += 1
            continue

        # Everything a commodity price carries that an item price does not.
        # The _avg twins live here and NEVER in the price columns: §3.1 says a
        # blended average is never shown as if it were a price, and the
        # cheapest way to guarantee that is for it not to be in the column the
        # site reads.
        detail = {
            "raw_price_buy": row.get("price_buy"),
            "raw_price_sell": row.get("price_sell"),
            "price_buy_avg": row.get("price_buy_avg"),
            "price_sell_avg": row.get("price_sell_avg"),
            "scu_buy": row.get("scu_buy"),
            "scu_buy_avg": row.get("scu_buy_avg"),
            "scu_sell": row.get("scu_sell"),
            "scu_sell_avg": row.get("scu_sell_avg"),
            "scu_sell_stock": row.get("scu_sell_stock"),
            "scu_sell_stock_avg": row.get("scu_sell_stock_avg"),
            "status_buy": row.get("status_buy"),
            "status_sell": row.get("status_sell"),
            "container_sizes": row.get("container_sizes"),
            "quality": row.get("quality"),
            "commodity_name": row.get("commodity_name"),
            "terminal_name": row.get("terminal_name"),
            "date_added": row.get("date_added"),
            # Which of the two source files this came from. Without it the
            # refined and raw prices for the same commodity are
            # indistinguishable once stored.
            "is_raw_commodity_price": is_raw,
        }

        pending.append({
            "shop_item_id": item_id,
            "terminal_id": terminal_id,
            "snapshot_id": snapshot_id,
            "price_buy": buy,
            "price_sell": sell,
            "uex_price_id": row.get("id"),
            "source_date_modified": to_dt(row.get("date_modified")),
            "detail": detail,
        })

    return pending, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = SNAPSHOT_ROOT / args.snapshot
    commodities_src = load_envelope(base / "commodities.json")
    prices_src = load_envelope(base / "commodities_prices_all.json")
    raw_prices_src = load_envelope(base / "commodities_raw_prices_all.json")

    log(f"snapshot {args.snapshot}: {len(commodities_src)} commodities, "
        f"{len(prices_src)} prices, {len(raw_prices_src)} raw prices"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")
    if not commodities_src or not prices_src:
        log("FAILED: commodities or commodity prices carried no rows - "
            "refusing to report success")
        return 1

    with Session(engine) as session:
        snapshot = session.execute(
            select(Snapshot).where(
                Snapshot.source == "uexcorp",
                Snapshot.snapshot_key == args.snapshot,
            )
        ).scalar_one_or_none()
        if snapshot is None:
            log(f"FAILED: no snapshots row for {args.snapshot} - run "
                f"import_uex_snapshots.py first. A price with no snapshot has "
                f"no provenance and will not be stored.")
            return 1
        snapshot_id = snapshot.id

        inserted, updated, unchanged = import_commodities(
            session, args.snapshot, commodities_src, args.dry_run
        )
        if not args.dry_run:
            session.flush()
        log(f"commodities: inserted {inserted}, updated {updated}, "
            f"unchanged {unchanged}")

        if args.dry_run:
            # Without the commodity rows committed there are no ids to hang
            # prices on. Reported honestly rather than pretending to have
            # counted them.
            session.rollback()
            log("DRY RUN: commodity prices not counted - they key on ids that "
                "only exist after the commodity rows are written. Re-run "
                "without --dry-run to see the price figures.")
            return 0

        commodities = {
            uex_id: row_id
            for uex_id, row_id in session.execute(
                select(ShopItem.uex_id, ShopItem.id)
                .where(ShopItem.source_kind == SOURCE_KIND)
            )
        }
        terminals = {
            uex_id: row_id
            for uex_id, row_id in session.execute(
                select(Terminal.uex_id, Terminal.id)
            )
        }
        existing = {
            (item_id, terminal_id)
            for item_id, terminal_id in session.execute(
                select(ItemPrice.shop_item_id, ItemPrice.terminal_id)
                .where(ItemPrice.snapshot_id == snapshot_id)
            )
        }
        seen = set()

        pending, skipped = build_price_rows(
            prices_src, commodities, terminals, snapshot_id, existing, seen,
            is_raw=False,
        )
        raw_pending, raw_skipped = build_price_rows(
            raw_prices_src, commodities, terminals, snapshot_id, existing,
            seen, is_raw=True,
        )

        log(f"prices ready: {len(pending)} refined, {len(raw_pending)} raw")
        for label, counter in (("refined", skipped), ("raw", raw_skipped)):
            for reason, count in counter.most_common():
                log(f"  {label}: {count} not placed - {reason}")

        append_only(session, ItemPrice, pending + raw_pending, batch_size=BATCH)
        session.commit()

    with Session(engine) as session:
        held_commodities = session.query(ShopItem).filter(
            ShopItem.source_kind == SOURCE_KIND
        ).count()
        held_prices = session.query(ItemPrice).filter(
            ItemPrice.snapshot_id == snapshot_id
        ).count()
        total_prices = session.query(ItemPrice).count()

    log(f"shop_items holds {held_commodities} commodities "
        f"(source had {len(commodities_src)})")
    log(f"item_prices holds {held_prices} rows for snapshot {args.snapshot} "
        f"(source had {len(prices_src)} + {len(raw_prices_src)} raw); "
        f"{total_prices} rows overall")

    failures = []
    if held_commodities < len(commodities_src):
        failures.append(f"commodities: {len(commodities_src)} source, "
                        f"{held_commodities} stored")
    placeable = (len(prices_src) + len(raw_prices_src)
                 - sum(skipped.values()) - sum(raw_skipped.values()))
    if held_prices < placeable:
        failures.append(f"prices: {placeable} placeable, {held_prices} stored")
    for line in failures:
        log(f"FAILED: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
