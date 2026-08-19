"""
UEX item prices importer (B3 of the shop/price layer order).

23,734 rows from 20260801T235530Z, APPEND-ONLY AND KEYED BY SNAPSHOT (§3.4).

WHAT APPEND-ONLY ACTUALLY MEANS HERE
------------------------------------
A price row is identified by (item, terminal, snapshot). Running this against
the SAME snapshot twice inserts nothing the second time. Running it against a
LATER snapshot inserts a whole new set of rows and touches none of the old
ones. Nothing in this file updates a price and nothing deletes one - the only
write is an insert.

That is deliberate to the point of being awkward: it would be less code to
upsert on (item, terminal). It would also destroy the history the table exists
to hold, which is what happened to the roadmap watcher on this project and
cost a rebuild.

ZERO IS NOT A PRICE
-------------------
UEX writes price_buy = 0 for "this terminal does not sell this". Stored as 0,
the site renders "0 aUEC" - a false statement about a real shop. §3.1 says
blank means no data, so 0 becomes NULL here and the untouched source values go
into `detail`, where the transformation stays reversible and auditable.
Measured before this was written: no row in the snapshot has both sides
absent, so nothing is ever blanked out entirely.

ROWS WHOSE ITEM IS NOT HELD ARE DEFERRED, NOT DROPPED
------------------------------------------------------
Prices reference items across every category. Until B5 has imported all of
them, some price rows have no item to attach to. Those are COUNTED AND
REPORTED, and the importer says exactly how many it could not place. It does
not quietly store fewer rows and report success - that is the silent-success
failure this project keeps finding. Re-run after B5 and the deferred rows land.

Usage:
    venv/Scripts/python.exe import_uex_prices.py
    venv/Scripts/python.exe import_uex_prices.py --dry-run
"""

import argparse
import datetime
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import insert, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import ItemPrice, ShopItem, Snapshot, Terminal  # noqa: E402
from import_uex_terminals import load_envelope, to_dt  # noqa: E402

SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
DEFAULT_SNAPSHOT = "20260801T235530Z"
LOG_PATH = PROJECT_ROOT / "logs" / "shop_layer_import.log"
BATCH = 2000


def log(message: str) -> None:
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] prices: {message}"
    print(line)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def price_or_none(value):
    """A UEX price as a real price, or None.

    0 means "not traded here", not "free". Returning None is what lets the
    front end leave the column blank instead of printing a price that is not
    true. A genuinely free item would arrive as 0 too - which is why the raw
    values are kept in `detail` rather than thrown away, and why the database
    constraint is non-NEGATIVE rather than non-zero.
    """
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return None if number == 0 else number


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = SNAPSHOT_ROOT / args.snapshot / "items_prices_all.json"
    rows = load_envelope(path)

    log(f"snapshot {args.snapshot}: {len(rows)} source price rows"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")
    if not rows:
        log("FAILED: items_prices_all.json carried no rows - "
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
            log(f"FAILED: no snapshots row for {args.snapshot} - "
                f"run import_uex_snapshots.py first. A price without a "
                f"snapshot has no provenance and will not be stored.")
            return 1
        snapshot_id = snapshot.id

        items = {
            uex_id: row_id
            for uex_id, row_id in session.execute(
                select(ShopItem.uex_id, ShopItem.id)
            )
        }
        terminals = {
            uex_id: row_id
            for uex_id, row_id in session.execute(
                select(Terminal.uex_id, Terminal.id)
            )
        }
        # Existing keys for THIS snapshot, so a re-run inserts nothing.
        existing = {
            (item_id, terminal_id)
            for item_id, terminal_id in session.execute(
                select(ItemPrice.shop_item_id, ItemPrice.terminal_id)
                .where(ItemPrice.snapshot_id == snapshot_id)
            )
        }

        log(f"holding {len(items)} items, {len(terminals)} terminals; "
            f"{len(existing)} price rows already stored for this snapshot")

        pending = []
        deferred = Counter()
        skipped_no_side = 0
        duplicates_in_source = 0
        seen_in_this_run = set()

        for row in rows:
            item_id = items.get(row.get("id_item"))
            terminal_id = terminals.get(row.get("id_terminal"))

            if item_id is None:
                deferred["item not imported yet"] += 1
                continue
            if terminal_id is None:
                deferred["terminal not held"] += 1
                continue

            key = (item_id, terminal_id)
            if key in existing:
                continue
            if key in seen_in_this_run:
                # Two source rows for the same item at the same terminal in one
                # snapshot. Counted rather than allowed to blow up the batch on
                # the unique constraint - and reported, because it is a fact
                # about UEX's data, not a nuisance.
                duplicates_in_source += 1
                continue
            seen_in_this_run.add(key)

            buy = price_or_none(row.get("price_buy"))
            sell = price_or_none(row.get("price_sell"))
            if buy is None and sell is None:
                # The database refuses this (ck_item_prices_has_at_least_one_
                # side) and it is right to. Counted here so the number is
                # visible rather than surfacing as a constraint violation.
                skipped_no_side += 1
                continue

            pending.append({
                "shop_item_id": item_id,
                "terminal_id": terminal_id,
                "snapshot_id": snapshot_id,
                "price_buy": buy,
                "price_sell": sell,
                "uex_price_id": row.get("id"),
                "source_date_modified": to_dt(row.get("date_modified")),
                # The raw values, so turning 0 into NULL stays reversible.
                "detail": {
                    "raw_price_buy": row.get("price_buy"),
                    "raw_price_sell": row.get("price_sell"),
                    "id_category": row.get("id_category"),
                    "item_uuid": row.get("item_uuid"),
                    "item_name": row.get("item_name"),
                    "terminal_name": row.get("terminal_name"),
                    "date_added": row.get("date_added"),
                },
            })

        log(f"{len(pending)} rows ready to insert")
        if deferred:
            for reason, count in deferred.most_common():
                log(f"  DEFERRED {count} row(s): {reason}")
        if skipped_no_side:
            log(f"  SKIPPED {skipped_no_side} row(s) with neither a buy nor a "
                f"sell price - not an observation about anything")
        if duplicates_in_source:
            log(f"  {duplicates_in_source} duplicate (item, terminal) pair(s) "
                f"within this one snapshot - first occurrence kept")

        if not args.dry_run and pending:
            for start in range(0, len(pending), BATCH):
                session.execute(insert(ItemPrice), pending[start:start + BATCH])
            session.commit()
        else:
            session.rollback()

    with Session(engine) as session:
        stored = session.query(ItemPrice).filter(
            ItemPrice.snapshot_id == snapshot_id
        ).count()
        total = session.query(ItemPrice).count()
    log(f"item_prices holds {total} rows; {stored} for snapshot {args.snapshot}")

    if args.dry_run:
        return 0

    placeable = len(rows) - sum(deferred.values()) - skipped_no_side - duplicates_in_source
    if stored < placeable:
        log(f"FAILED: {placeable} rows were placeable, only {stored} stored")
        return 1
    if deferred:
        log(f"NOT COMPLETE: {sum(deferred.values())} source rows could not be "
            f"placed yet. This is reported as incomplete rather than as "
            f"success. Re-run after B5 imports the remaining categories.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
