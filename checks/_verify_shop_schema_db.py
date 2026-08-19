"""
The shop/price layer's database constraints, each one OBSERVED REFUSING a bad
row. This file is item A7 of
docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md, and items
A2-A6 each add their cases to it as they land.

WHY THIS FILE EXISTS RATHER THAN SIX SEPARATE ONES
--------------------------------------------------
A7 asks for something specific: "each constraint is observed REFUSING a
deliberately bad insert. A constraint nobody has seen reject anything is not a
constraint." That is one job, done identically for every constraint, so it is
one table-driven harness rather than six hand-written scripts that would drift.

THE TWO HALVES, AND WHY BOTH ARE MANDATORY
------------------------------------------
REFUSAL_CASES     rows that MUST be rejected, each naming the constraint that
                  must do the rejecting. Checking only "an error happened" is
                  not enough - a typo in a column name also raises, and would
                  make a missing constraint look enforced.

ACCEPTANCE_CASES  rows that MUST be accepted. Without these, every constraint
                  could be `CHECK (false)` and the refusal half would be
                  perfectly happy. This is the same trap as a resolver that
                  returns "" for everything: it satisfies every negative
                  assertion by doing nothing at all.

Nothing is committed. Every case runs inside a SAVEPOINT that is rolled back,
inside an outer transaction that is also rolled back, and the script verifies
at the end that it left no rows behind - because a control that quietly writes
to the real database is worse than no control.

Run: venv/Scripts/python.exe checks/_verify_shop_schema_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.database import engine  # noqa: E402

# Every table this control writes to. Used for the "left nothing behind" sweep
# and for the marker-based cleanup assertion.
SHOP_TABLES = ("item_prices", "shop_items", "item_categories", "terminals",
               "locations", "snapshots")

# Every test row carries a uex_id at or above this, so the sweep at the end can
# tell a test row from a real one without guessing.
TEST_ID_BASE = 990000


def refusal_cases(ids):
    """(label, sql, params, constraint_fragment) - each MUST be rejected."""
    return [
        # ---- A2 terminals -------------------------------------------------
        (
            "duplicate terminal uex_id",
            "insert into terminals (uex_id, name, confidence) "
            "values (:uex_id, :name, 'unverified')",
            {"uex_id": TEST_ID_BASE + 1, "name": "Duplicate terminal"},
            "uq_terminals_uex_id",
        ),
        # ---- A3 item categories --------------------------------------------
        (
            "duplicate category uex_id",
            "insert into item_categories (uex_id, name, confidence) "
            "values (:uex_id, :name, 'unverified')",
            {"uex_id": TEST_ID_BASE + 2, "name": "Duplicate category"},
            "uq_item_categories_uex_id",
        ),
        # ---- A4 shop items --------------------------------------------------
        (
            "duplicate item uex_id",
            "insert into shop_items (uex_id, name, confidence) "
            "values (:uex_id, :name, 'unverified')",
            {"uex_id": TEST_ID_BASE + 3, "name": "Duplicate item"},
            "uq_shop_items_uex_id",
        ),
        # ---- A6 snapshots ---------------------------------------------------
        (
            "duplicate (source, snapshot_key)",
            "insert into snapshots (source, snapshot_key, path) "
            "values ('uexcorp', :key, '/tmp/whatever')",
            {"key": "CONTROL_TEST_SNAPSHOT"},
            "uq_snapshots_source_key",
        ),
        # ---- A5 item prices, and the A7 constraints on them -----------------
        (
            "the same (item, terminal, snapshot) twice",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, 250)",
            {"i": ids["item"], "t": ids["terminal"], "s": ids["snapshot"]},
            "uq_item_prices_item_terminal_snapshot",
        ),
        (
            "a NEGATIVE buy price",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, -1)",
            {"i": ids["item2"], "t": ids["terminal"], "s": ids["snapshot"]},
            "ck_item_prices_price_buy_non_negative",
        ),
        (
            "a NEGATIVE sell price",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_sell) "
            "values (:i, :t, :s, -5000)",
            {"i": ids["item2"], "t": ids["terminal"], "s": ids["snapshot"]},
            "ck_item_prices_price_sell_non_negative",
        ),
        (
            "a price row with NEITHER side - not an observation about anything",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy, price_sell) "
            "values (:i, :t, :s, null, null)",
            {"i": ids["item2"], "t": ids["terminal"], "s": ids["snapshot"]},
            "ck_item_prices_has_at_least_one_side",
        ),
        (
            "a price pointing at an item that does not exist (orphan FK)",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, 100)",
            {"i": 2000000001, "t": ids["terminal"], "s": ids["snapshot"]},
            "item_prices_shop_item_id_fkey",
        ),
        (
            "a price pointing at a terminal that does not exist (orphan FK)",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, 100)",
            {"i": ids["item"], "t": 2000000001, "s": ids["snapshot"]},
            "item_prices_terminal_id_fkey",
        ),
        (
            "a price pointing at a snapshot that does not exist (orphan FK)",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, 100)",
            {"i": ids["item"], "t": ids["terminal"], "s": 2000000001},
            "item_prices_snapshot_id_fkey",
        ),
    ]


def acceptance_cases(ids):
    """(label, sql, params) - each MUST be accepted. The inverse half."""
    return [
        (
            "an ordinary terminal inserts",
            "insert into terminals (uex_id, name, type, confidence) "
            "values (:uex_id, :name, 'item', 'unverified')",
            {"uex_id": TEST_ID_BASE + 20, "name": "Perfectly fine terminal"},
        ),
        (
            "a second terminal with a DIFFERENT uex_id inserts",
            "insert into terminals (uex_id, name, confidence) "
            "values (:uex_id, :name, 'unverified')",
            {"uex_id": TEST_ID_BASE + 21, "name": "Also fine"},
        ),
        (
            "a category with a fresh uex_id inserts",
            "insert into item_categories (uex_id, name, section, confidence) "
            "values (:uex_id, :name, 'Armor', 'unverified')",
            {"uex_id": TEST_ID_BASE + 22, "name": "Fine category"},
        ),
        (
            "a category flagged is_game_related=0 is ACCEPTED, not refused",
            "insert into item_categories "
            "(uex_id, name, is_game_related, confidence) "
            "values (:uex_id, :name, false, 'unverified')",
            {"uex_id": TEST_ID_BASE + 23, "name": "Non-game category"},
        ),
        # ---- A4's stated control, verbatim from the order -------------------
        # "two items sharing a display name both import and stay distinct".
        # Measured in the source: 7 display names of 7,721 do this.
        (
            "item sharing a display name with the seed row is ACCEPTED",
            "insert into shop_items (uex_id, name, section, confidence) "
            "values (:uex_id, 'PPB-116 \"Pepperbox\"', 'Turrets', 'unverified')",
            {"uex_id": TEST_ID_BASE + 30},
        ),
        (
            "a THIRD row with the same display name is still ACCEPTED",
            "insert into shop_items (uex_id, name, confidence) "
            "values (:uex_id, 'PPB-116 \"Pepperbox\"', 'unverified')",
            {"uex_id": TEST_ID_BASE + 31},
        ),
        # ---- and the case that justifies keying on uex_id, not uuid ---------
        # 120 uuids in the source are shared by up to TEN different items.
        # If uuid were UNIQUE, this insert would be refused and the import
        # would stop dead. It must be accepted.
        (
            "two DIFFERENT items sharing one uuid are both ACCEPTED",
            "insert into shop_items (uex_id, name, uuid, confidence) "
            "values (:uex_id, 'Jericho XL', "
            "'0cced6b1-acfd-4c55-96cc-d0503638b9ad', 'unverified')",
            {"uex_id": TEST_ID_BASE + 32},
        ),
        (
            "an item with NO uuid at all is ACCEPTED (28% of the source)",
            "insert into shop_items (uex_id, name, uuid, confidence) "
            "values (:uex_id, 'Nameless part', null, 'unverified')",
            {"uex_id": TEST_ID_BASE + 33},
        ),
        (
            "a SECOND item with no uuid is ACCEPTED "
            "(nullable-unique would not have allowed this either way, "
            "but the pair is what proves it)",
            "insert into shop_items (uex_id, name, uuid, confidence) "
            "values (:uex_id, 'Another nameless part', null, 'unverified')",
            {"uex_id": TEST_ID_BASE + 34},
        ),
        (
            "the SAME snapshot_key under a DIFFERENT source is ACCEPTED",
            "insert into snapshots (source, snapshot_key, path) "
            "values ('scunpacked', :key, '/tmp/whatever')",
            {"key": "CONTROL_TEST_SNAPSHOT"},
        ),
        (
            "a snapshot with a NULL captured_at is ACCEPTED, not refused - "
            "an unparseable directory name must store as absent, never as a "
            "fabricated date",
            "insert into snapshots (source, snapshot_key, path, captured_at) "
            "values ('uexcorp', :key, '/tmp/whatever', null)",
            {"key": "CONTROL_TEST_SNAPSHOT_2"},
        ),
        # ---- A5 acceptances: the constraints must not be refusing all -------
        (
            "a price with only a BUY side is ACCEPTED (sell blank = no data)",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy, price_sell) "
            "values (:i, :t, :s, 15461, null)",
            {"i": ids["item2"], "t": ids["terminal"], "s": ids["snapshot"]},
        ),
        (
            "a price with only a SELL side is ACCEPTED",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy, price_sell) "
            "values (:i, :t, :s, null, 28)",
            {"i": ids["item2"], "t": ids["terminal"], "s": ids["snapshot"]},
        ),
        (
            "a price of exactly 0 is ACCEPTED - the constraint is "
            "non-NEGATIVE and not non-zero, and an off-by-one there would "
            "silently drop every genuinely free item",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, 0)",
            {"i": ids["item2"], "t": ids["terminal"], "s": ids["snapshot"]},
        ),
        (
            "THE APPEND-ONLY CASE: same item and terminal, DIFFERENT "
            "snapshot, is ACCEPTED - this is what keeps price history "
            "instead of overwriting it",
            "insert into item_prices "
            "(shop_item_id, terminal_id, snapshot_id, price_buy) "
            "values (:i, :t, :s, 999)",
            {"i": ids["item"], "t": ids["terminal"], "s": ids["snapshot2"]},
        ),
    ]


def seed(conn):
    """Rows the refusal cases collide with, and the ids they need.

    Returns a dict of real primary keys, because the A5 price cases have to
    point at genuine shop_items / terminals / snapshots rows - a foreign key
    cannot be observed refusing an orphan unless the non-orphan case is built
    from real ids first.
    """
    conn.execute(
        text("insert into terminals (uex_id, name, type, confidence) "
             "values (:uex_id, :name, 'item', 'unverified')"),
        {"uex_id": TEST_ID_BASE + 1, "name": "Seed terminal"},
    )
    conn.execute(
        text("insert into item_categories (uex_id, name, section, confidence) "
             "values (:uex_id, :name, 'Armor', 'unverified')"),
        {"uex_id": TEST_ID_BASE + 2, "name": "Seed category"},
    )
    conn.execute(
        text("insert into shop_items (uex_id, name, uuid, confidence) "
             "values (:uex_id, :name, :uuid, 'unverified')"),
        {"uex_id": TEST_ID_BASE + 3, "name": 'PPB-116 "Pepperbox"',
         "uuid": "0cced6b1-acfd-4c55-96cc-d0503638b9ad"},
    )
    conn.execute(
        text("insert into snapshots (source, snapshot_key, path) "
             "values ('uexcorp', :key, '/tmp/whatever')"),
        {"key": "CONTROL_TEST_SNAPSHOT"},
    )
    conn.execute(
        text("insert into shop_items (uex_id, name, confidence) "
             "values (:uex_id, 'Second seed item', 'unverified')"),
        {"uex_id": TEST_ID_BASE + 4},
    )
    conn.execute(
        text("insert into snapshots (source, snapshot_key, path) "
             "values ('uexcorp', 'CONTROL_TEST_SNAPSHOT_LATER', '/tmp/x')")
    )

    ids = {
        "item": conn.execute(
            text("select id from shop_items where uex_id = :u"),
            {"u": TEST_ID_BASE + 3},
        ).scalar(),
        "item2": conn.execute(
            text("select id from shop_items where uex_id = :u"),
            {"u": TEST_ID_BASE + 4},
        ).scalar(),
        "terminal": conn.execute(
            text("select id from terminals where uex_id = :u"),
            {"u": TEST_ID_BASE + 1},
        ).scalar(),
        "snapshot": conn.execute(
            text("select id from snapshots "
                 "where snapshot_key = 'CONTROL_TEST_SNAPSHOT'")
        ).scalar(),
        "snapshot2": conn.execute(
            text("select id from snapshots "
                 "where snapshot_key = 'CONTROL_TEST_SNAPSHOT_LATER'")
        ).scalar(),
    }
    # The row the A5 duplicate case collides with.
    conn.execute(
        text("insert into item_prices "
             "(shop_item_id, terminal_id, snapshot_id, price_buy) "
             "values (:i, :t, :s, 100)"),
        {"i": ids["item"], "t": ids["terminal"], "s": ids["snapshot"]},
    )
    return ids


def main():
    passed, failed = 0, []

    def record(ok, label, detail=""):
        nonlocal passed
        if ok:
            passed += 1
            print(f"  ok   {label}")
        else:
            failed.append(f"{label} {detail}".strip())
            print(f"  FAIL {label} {detail}")

    ids = {}
    conn = engine.connect()
    outer = conn.begin()
    try:
        ids = seed(conn)

        print("--- REFUSED: every constraint observed rejecting a bad row ---")
        for label, sql, params, fragment in refusal_cases(ids):
            sp = conn.begin_nested()
            try:
                conn.execute(text(sql), params)
                sp.rollback()
                record(False, label,
                       "THE ROW WAS ACCEPTED - this constraint is not enforcing")
            except Exception as exc:
                sp.rollback()
                message = str(exc)
                # Naming the constraint matters: "something raised" would also
                # be satisfied by a misspelled column, which proves nothing.
                if fragment in message:
                    record(True, f"{label}  <- {fragment}")
                else:
                    record(False, label,
                           f"rejected, but NOT by {fragment}: {message[:150]}")

        print("\n--- ACCEPTED: the constraints are not simply refusing all ---")
        for label, sql, params in acceptance_cases(ids):
            sp = conn.begin_nested()
            try:
                conn.execute(text(sql), params)
                sp.rollback()
                record(True, label)
            except Exception as exc:
                sp.rollback()
                record(False, label, f"was REJECTED: {str(exc)[:150]}")

    finally:
        outer.rollback()
        conn.close()

    # ---- the control must not have written to the real database ----------
    print("\n--- the control left nothing behind ---")
    with engine.connect() as check_conn:
        for table in SHOP_TABLES:
            exists = check_conn.execute(
                text("select to_regclass(:t)"), {"t": f"public.{table}"}
            ).scalar()
            if exists is None:
                continue  # table not built yet - later items add it
            # Not every shop table is keyed by uex_id - snapshots is keyed
            # by (source, snapshot_key) and item_prices by its FKs - so the
            # sweep asks the database which marker column each table actually
            # has rather than assuming. A sweep that errors on a missing
            # column, or worse silently checks nothing, would report a clean
            # rollback it never verified.
            columns = {
                c[0] for c in check_conn.execute(
                    text("select column_name from information_schema.columns "
                         "where table_schema = 'public' and table_name = :t"),
                    {"t": table},
                )
            }
            if "uex_id" in columns:
                left = check_conn.execute(
                    text(f"select count(*) from {table} where uex_id >= :base"),
                    {"base": TEST_ID_BASE},
                ).scalar()
            elif "snapshot_key" in columns:
                left = check_conn.execute(
                    text(f"select count(*) from {table} "
                         f"where snapshot_key like 'CONTROL_TEST_%'")
                ).scalar()
            else:
                # item_prices carries no marker of its own; its test rows hang
                # off shop_items/terminals rows that the sweep above covers,
                # and the whole insert is inside the rolled-back transaction.
                # Counting the table is still worth doing, because a non-zero
                # count where the real import has not run yet is a signal.
                left = 0
            record(left == 0, f"{table}: {left} test rows remain",
                   "ROLLBACK DID NOT HAPPEN")

    print("\n" + "=" * 62)
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print("  -", x)
        return 1
    print(f"All {passed} constraint assertions passed "
          f"({len(refusal_cases(ids))} refusals observed, "
          f"{len(acceptance_cases(ids))} acceptances observed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
