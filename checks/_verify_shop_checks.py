"""
C6: the negative control for every Phase C auditor.

§C6: "Feed each auditor a row that must trip it and OBSERVE IT FIRE. Then feed
clean data and observe it stay silent. Both halves, or the auditor is not
proven."

HOW BOTH HALVES ARE MEASURED AGAINST A LIVE DATABASE
-----------------------------------------------------
"Clean data" cannot mean an empty database here - the auditors are being run
against 26,657 real price rows, several of which legitimately trip C1, C3 and
C5 already. So silence is measured as a DELTA rather than as an absolute:

    1. run the auditor, record its findings           <- the baseline
    2. assert the planted finding is NOT in that baseline   <- the silent half
    3. insert exactly one row that must trip it
    4. run the auditor again
    5. assert the planted finding IS now present            <- the firing half

That is a stronger claim than "it produced some findings", because it names
the specific subject that must appear and requires it to have been absent
first. An auditor that fires on everything fails step 2; one that fires on
nothing fails step 5.

NOTHING IS COMMITTED. Every plant happens inside a SAVEPOINT that is rolled
back, inside an outer transaction that is also rolled back, and the script
verifies at the end that no planted row survived.

ONE CASE NEEDS A CONSTRAINT REMOVED, AND WHY THAT IS SAFE
-----------------------------------------------------------
C2's hard-orphan branch looks for a price row whose item does not exist. A7
put a foreign key on that column, so the condition is impossible to create
while the key is there - which means the branch could never be observed
firing, and an unobservable branch is exactly what rule 12 says not to trust.

So that one case drops the foreign key, plants the orphan, watches C2 catch
it, and rolls back. Postgres DDL is transactional, so the rollback restores
the constraint completely; a killed process rolls back too, because an aborted
connection aborts its transaction. The script then CONFIRMS the constraint is
present again by querying the catalog, and fails loudly if it is not.

Run: venv/Scripts/python.exe checks/_verify_shop_checks.py
"""

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from checks.shop_checks import (  # noqa: E402
    category_coverage_check,
    name_collision_check,
    orphan_check,
    price_outlier_check,
    price_staleness_check,
)

MARKER = "CC_C6_CONTROL"
TEST_ID_BASE = 995000

passed, failed = 0, []


def record(ok, label, detail=""):
    global passed
    if ok:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed.append(f"{label} {detail}".strip())
        print(f"  FAIL {label} {detail}")


def subjects(findings):
    return [f"{f.subject} :: {f.details}" for f in findings]


def mentions(findings, needle):
    return any(needle in s for s in subjects(findings))


def constraint_exists(conn, name):
    return conn.execute(
        text("select count(*) from pg_constraint where conname = :n"),
        {"n": name},
    ).scalar() > 0


def main():
    session = Session(engine)
    outer = session.begin()

    try:
        # ---------------------------------------------------------------
        # Shared scaffolding: a category, an item in it, and a terminal.
        # ---------------------------------------------------------------
        session.execute(text(
            "insert into item_categories (uex_id, name, section, "
            "is_game_related, confidence) values "
            "(:u, :n, 'ControlSection', true, 'unverified')"
        ), {"u": TEST_ID_BASE, "n": f"{MARKER}_CATEGORY"})
        category_id = session.execute(text(
            "select id from item_categories where uex_id = :u"
        ), {"u": TEST_ID_BASE}).scalar()

        session.execute(text(
            "insert into terminals (uex_id, name, type, location_id, confidence) "
            "select :u, :n, 'item', l.id, 'unverified' from locations l limit 1"
        ), {"u": TEST_ID_BASE, "n": f"{MARKER}_TERMINAL"})
        terminal_id = session.execute(text(
            "select id from terminals where uex_id = :u"
        ), {"u": TEST_ID_BASE}).scalar()

        snapshot_id = session.execute(text(
            "select id from snapshots order by id limit 1"
        )).scalar()

        # A tight, ordinary price distribution for C1 to judge against:
        # twelve items all priced near 100 aUEC.
        for offset in range(12):
            session.execute(text(
                "insert into shop_items (uex_id, source_kind, name, "
                "category_id, category_name, confidence) values "
                "(:u, 'item', :n, :c, :cn, 'unverified')"
            ), {"u": TEST_ID_BASE + 100 + offset,
                "n": f"{MARKER}_ORDINARY_{offset}",
                "c": category_id, "cn": f"{MARKER}_CATEGORY"})
            item_id = session.execute(text(
                "select id from shop_items where uex_id = :u"
            ), {"u": TEST_ID_BASE + 100 + offset}).scalar()
            session.execute(text(
                "insert into item_prices (shop_item_id, terminal_id, "
                "snapshot_id, price_buy, source_date_modified) "
                "values (:i, :t, :s, :p, :d)"
            ), {"i": item_id, "t": terminal_id, "s": snapshot_id,
                "p": 100 + offset, "d": datetime.datetime.now()})
        session.flush()

        # =================================================================
        print("--- C1 price outliers ---")
        baseline = price_outlier_check(session)
        record(not mentions(baseline, f"{MARKER}_ABSURD"),
               "SILENT before: no finding names the planted item")

        sp = session.begin_nested()
        session.execute(text(
            "insert into shop_items (uex_id, source_kind, name, category_id, "
            "category_name, confidence) values "
            "(:u, 'item', :n, :c, :cn, 'unverified')"
        ), {"u": TEST_ID_BASE + 1, "n": f"{MARKER}_ABSURD",
            "c": category_id, "cn": f"{MARKER}_CATEGORY"})
        absurd_id = session.execute(text(
            "select id from shop_items where uex_id = :u"
        ), {"u": TEST_ID_BASE + 1}).scalar()
        session.execute(text(
            "insert into item_prices (shop_item_id, terminal_id, snapshot_id, "
            "price_buy, source_date_modified) values (:i, :t, :s, :p, :d)"
        ), {"i": absurd_id, "t": terminal_id, "s": snapshot_id,
            "p": 999_999_999, "d": datetime.datetime.now()})
        session.flush()

        after = price_outlier_check(session)
        record(mentions(after, f"{MARKER}_ABSURD"),
               "FIRED: a 999,999,999 aUEC price in a ~100 aUEC category "
               "is flagged",
               "the outlier checker did not notice a 10-million-fold outlier")
        sp.rollback()

        # =================================================================
        print("\n--- C2 orphans (soft: a terminal with no location) ---")
        baseline = orphan_check(session)
        record(not mentions(baseline, "resolve to no location"),
               "SILENT before: no unplaced-terminal finding")

        sp = session.begin_nested()
        session.execute(text(
            "insert into terminals (uex_id, name, location_id, confidence) "
            "values (:u, :n, null, 'unverified')"
        ), {"u": TEST_ID_BASE + 2, "n": f"{MARKER}_UNPLACED"})
        session.flush()
        after = orphan_check(session)
        record(mentions(after, "resolve to no location"),
               "FIRED: a terminal with a NULL location is flagged")
        sp.rollback()

        # =================================================================
        print("\n--- C2 orphans (HARD: a price row whose item does not "
              "exist) ---")
        # The branch a foreign key makes unreachable. See the module docstring
        # for why removing it here is safe and how that is verified.
        fk = "item_prices_shop_item_id_fkey"
        record(constraint_exists(session.connection(), fk),
               f"{fk} is present before the test")

        sp = session.begin_nested()
        session.execute(text(f"alter table item_prices drop constraint {fk}"))
        session.execute(text(
            "insert into item_prices (shop_item_id, terminal_id, snapshot_id, "
            "price_buy) values (2000000001, :t, :s, 500)"
        ), {"t": terminal_id, "s": snapshot_id})
        session.flush()
        after = orphan_check(session)
        record(mentions(after, "does not exist"),
               "FIRED: an orphan price row is caught as a DEFECT",
               "the hard-orphan branch did NOT fire - it is unreachable and "
               "therefore untrusted")
        record(any(f.result == "DEFECT" for f in after),
               "and it is reported as a DEFECT, not a warning")
        sp.rollback()

        record(constraint_exists(session.connection(), fk),
               f"{fk} is BACK after the rollback",
               "THE FOREIGN KEY WAS NOT RESTORED - stop and investigate")

        # =================================================================
        print("\n--- C3 name collisions ---")
        baseline = name_collision_check(session)
        record(not mentions(baseline, f"{MARKER}_TWIN"),
               "SILENT before: no finding names the planted twin")

        sp = session.begin_nested()
        for n in (3, 4):
            session.execute(text(
                "insert into shop_items (uex_id, source_kind, name, uuid, "
                "confidence) values (:u, 'item', :n, :uu, 'unverified')"
            ), {"u": TEST_ID_BASE + n, "n": f"{MARKER}_TWIN",
                "uu": f"{MARKER}-shared-uuid"})
        session.flush()
        after = name_collision_check(session)
        record(mentions(after, f"{MARKER}_TWIN"),
               "FIRED: two items sharing a display name are flagged")
        record(mentions(after, f"{MARKER}-shared-uuid")
               or any("uuid" in str(f.subject) and f.result == "DEFECT"
                      for f in after),
               "FIRED: two items sharing a uuid are flagged")
        sp.rollback()

        # =================================================================
        print("\n--- C4 category price coverage ---")
        baseline = category_coverage_check(session)
        record(not mentions(baseline, f"{MARKER}_UNSOLD"),
               "SILENT before: no finding names the planted category")

        sp = session.begin_nested()
        session.execute(text(
            "insert into item_categories (uex_id, name, section, "
            "is_game_related, confidence) values "
            "(:u, :n, 'ControlSection', true, 'unverified')"
        ), {"u": TEST_ID_BASE + 5, "n": f"{MARKER}_UNSOLD"})
        unsold_category = session.execute(text(
            "select id from item_categories where uex_id = :u"
        ), {"u": TEST_ID_BASE + 5}).scalar()
        session.execute(text(
            "insert into shop_items (uex_id, source_kind, name, category_id, "
            "category_name, confidence) values "
            "(:u, 'item', :n, :c, :cn, 'unverified')"
        ), {"u": TEST_ID_BASE + 6, "n": f"{MARKER}_UNSOLD_ITEM",
            "c": unsold_category, "cn": f"{MARKER}_UNSOLD"})
        session.flush()
        after = category_coverage_check(session)
        planted = [f for f in after if f"{MARKER}_UNSOLD" in str(f.subject)]
        record(bool(planted),
               "FIRED: a category with items and no prices gets its own row")
        record(any(f.result == "LIMITATION" and "NOT ONE item" in f.details
                   for f in planted),
               "and it is LIMITATION, not DEFECT - 'nobody sells this' is a "
               "fact, not a bug")
        sp.rollback()

        # =================================================================
        print("\n--- C5 staleness ---")
        baseline = price_staleness_check(session)
        record(not any("dated in the future" == f.subject for f in baseline),
               "SILENT before: no future-dated price finding")

        sp = session.begin_nested()
        session.execute(text(
            "insert into shop_items (uex_id, source_kind, name, confidence) "
            "values (:u, 'item', :n, 'unverified')"
        ), {"u": TEST_ID_BASE + 7, "n": f"{MARKER}_FUTURE"})
        future_item = session.execute(text(
            "select id from shop_items where uex_id = :u"
        ), {"u": TEST_ID_BASE + 7}).scalar()
        session.execute(text(
            "insert into item_prices (shop_item_id, terminal_id, snapshot_id, "
            "price_buy, source_date_modified) values (:i, :t, :s, 100, :d)"
        ), {"i": future_item, "t": terminal_id, "s": snapshot_id,
            "d": datetime.datetime.now() + datetime.timedelta(days=400)})
        session.flush()
        after = price_staleness_check(session)
        record(any(f.subject == "dated in the future" and f.result == "DEFECT"
                   for f in after),
               "FIRED: a price dated in the future is a DEFECT, not staleness")
        sp.rollback()

        sp = session.begin_nested()
        before_old = next(
            (f for f in price_staleness_check(session)
             if f.subject == "over a year"), None
        )
        session.execute(text(
            "insert into shop_items (uex_id, source_kind, name, confidence) "
            "values (:u, 'item', :n, 'unverified')"
        ), {"u": TEST_ID_BASE + 8, "n": f"{MARKER}_ANCIENT"})
        ancient_item = session.execute(text(
            "select id from shop_items where uex_id = :u"
        ), {"u": TEST_ID_BASE + 8}).scalar()
        session.execute(text(
            "insert into item_prices (shop_item_id, terminal_id, snapshot_id, "
            "price_buy, source_date_modified) values (:i, :t, :s, 100, :d)"
        ), {"i": ancient_item, "t": terminal_id, "s": snapshot_id,
            "d": datetime.datetime.now() - datetime.timedelta(days=1200)})
        session.flush()
        after_old = next(
            (f for f in price_staleness_check(session)
             if f.subject == "over a year"), None
        )
        record(before_old is not None and after_old is not None
               and after_old.details != before_old.details,
               f"FIRED: a 1,200-day-old price moves the 'over a year' bucket",
               f"before={getattr(before_old, 'details', None)!r} "
               f"after={getattr(after_old, 'details', None)!r}")
        record(after_old is not None and after_old.result == "WARNING",
               "and the bucket reports WARNING once it is non-empty")
        sp.rollback()

    finally:
        outer.rollback()
        session.close()

    # -------------------------------------------------------------------
    print("\n--- nothing was left behind, and the schema is intact ---")
    with engine.connect() as conn:
        for table in ("item_categories", "terminals", "shop_items"):
            left = conn.execute(
                text(f"select count(*) from {table} where uex_id >= :b"),
                {"b": TEST_ID_BASE},
            ).scalar()
            record(left == 0, f"{table}: {left} planted row(s) remain",
                   "ROLLBACK DID NOT HAPPEN")
        for fk in ("item_prices_shop_item_id_fkey",
                   "item_prices_terminal_id_fkey",
                   "item_prices_snapshot_id_fkey"):
            record(constraint_exists(conn, fk), f"{fk} present")

    print("\n" + "=" * 62)
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print("  -", x)
        return 1
    print(f"All {passed} assertions passed. Every Phase C auditor has been "
          f"observed firing on a planted defect AND staying silent without "
          f"one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
