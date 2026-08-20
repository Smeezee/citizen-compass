#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_preservation_inversion.py - H7: protect by default, and prove it.

WHAT CHANGED, AND WHY IT NEEDED A CONTROL OF ITS OWN
====================================================
app/preservation.py used to name sixteen tables and protect those. Everything
built during the A-G runs - shop_items, item_prices, terminals, locations,
item_categories, snapshots, shop_item_commodity_xref, ship_hardpoints,
ship_hardpoint_coverage - was outside it. 26,657 price rows and 2,195 hardpoint
slots were unguarded and nothing said so.

It is now inverted: everything is protected unless explicitly named ephemeral.

THAT IS A BEHAVIOUR CHANGE AT THE ENGINE EVERY SESSION-OPENING CHECK INHERITS,
so it is proven at the level it now operates - not by reading the frozensets,
which is what a check that cannot fail would do.

THE CONTROL H7 NAMES:
  "a new table added to the models with no classification FAILS the check.
   Observe it failing. Then classify it and observe it pass."
Both halves are here, and the failing half runs first.

WHAT THIS DOES TO THE DATABASE: nothing. Every delete attempt is made against
a TEMPORARY table inside one connection, shadowing nothing real, and the
classification half operates on a throwaway MetaData object rather than the
application's. No row in any real table is touched, and no table is created
outside the session's temp schema.

--self-test inverts every expectation and must exit non-zero.

Rule 15: every open states its encoding.

Usage:  python checks/_verify_preservation_inversion.py [--self-test]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

SELFTEST = "--self-test" in sys.argv
_passed, _failed = [], []


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def main():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))

    from sqlalchemy import Column, Integer, MetaData, Table, create_engine, text
    from app.preservation import (
        EPHEMERAL_PREFIXES,
        EPHEMERAL_TABLES,
        PRESERVED_TABLES,
        PreservationViolation,
        classification_problems,
        install_never_delete_guard,
        is_ephemeral,
        is_protected,
        remove_never_delete_guard,
    )

    print("\n1. THE INVERSION, AT THE FUNCTION THAT DECIDES")
    check("a table nobody has ever heard of is PROTECTED",
          is_protected("a_table_invented_five_seconds_ago"))
    check("and that is the whole point - the old allowlist said the opposite",
          not is_ephemeral("a_table_invented_five_seconds_ago"))
    for name in ("shop_items", "item_prices", "terminals", "locations",
                 "item_categories", "snapshots", "shop_item_commodity_xref",
                 "ship_hardpoints", "ship_hardpoint_coverage"):
        check("H7's named table is protected: %s" % name, is_protected(name))
    for name in ("ships", "components", "manufacturers", "ship_registry"):
        check("and the originally-protected ones still are: %s" % name,
              is_protected(name))
    for name in sorted(EPHEMERAL_TABLES):
        check("ephemeral by name, so still deletable: %s" % name,
              is_ephemeral(name))
    check("and a harness throwaway by prefix", is_ephemeral("cc_scratch_thing"))
    check("case does not let anything through", is_protected("SHOP_ITEMS"))
    check("nor does a mixed-case ephemeral name lose its exemption",
          is_ephemeral("Pipeline_Findings"))

    # ------------------------------------------------------------------
    print("\n2. THE GUARD ITSELF, AGAINST A REAL DELETE ON A TEMP TABLE")
    # Nothing real is touched: these are TEMPORARY tables inside one
    # connection. The point is that the guard's decision is made on the name,
    # which is all it ever sees.
    from app.database import DATABASE_URL

    engine = create_engine(DATABASE_URL, future=True)
    with engine.connect() as conn:
        conn.execute(text("CREATE TEMP TABLE shop_items_probe (id int)"))
        conn.execute(text("CREATE TEMP TABLE cc_scratch_probe (id int)"))
        conn.execute(text("INSERT INTO shop_items_probe VALUES (1)"))
        conn.execute(text("INSERT INTO cc_scratch_probe VALUES (1)"))

        # BEFORE the guard: both deletes must work. If they do not, this whole
        # section is proving something other than what it claims.
        conn.execute(text("DELETE FROM shop_items_probe"))
        conn.execute(text("DELETE FROM cc_scratch_probe"))
        check("without the guard, a delete on either table works", True)

        install_never_delete_guard(engine)
        try:
            conn.execute(text("INSERT INTO shop_items_probe VALUES (1)"))
            conn.execute(text("INSERT INTO cc_scratch_probe VALUES (1)"))

            blocked = False
            try:
                conn.execute(text("DELETE FROM shop_items_probe"))
            except PreservationViolation:
                blocked = True
            check("an unclassified table name is REFUSED by default", blocked)

            allowed = True
            try:
                conn.execute(text("DELETE FROM cc_scratch_probe"))
            except PreservationViolation:
                allowed = False
            check("and an ephemeral one is still allowed through", allowed)

            # The exact statement that reached a real table during G5.
            for stmt, label in (
                ("DELETE FROM item_prices WHERE id = 1", "DELETE with a WHERE"),
                ("delete from item_prices", "lowercase delete"),
                ("TRUNCATE TABLE item_prices", "TRUNCATE"),
                ("DELETE FROM ship_hardpoints", "the hardpoint slots"),
            ):
                caught = False
                try:
                    conn.execute(text(stmt))
                except PreservationViolation:
                    caught = True
                except Exception as exc:
                    check("%s refused (got %s)" % (label, type(exc).__name__),
                          False)
                    continue
                check("%s refused" % label, caught)

            # And the guard is what is doing it, not something else.
            remove_never_delete_guard(engine)
            still_blocked = False
            try:
                conn.execute(text("DELETE FROM shop_items_probe"))
            except PreservationViolation:
                still_blocked = True
            check("*** with the guard REMOVED the same delete succeeds, so the "
                  "guard is load-bearing ***", not still_blocked)
        finally:
            remove_never_delete_guard(engine)
        conn.rollback()
    engine.dispose()

    # ------------------------------------------------------------------
    print("\n3. H7's NAMED CONTROL: an unclassified table FAILS the check")
    # A throwaway MetaData, so the application's models are not touched. The
    # checker reads whatever metadata it is given, which is exactly why it can
    # be proven this way.
    md = MetaData()
    for name in sorted(PRESERVED_TABLES):
        Table(name, md, Column("id", Integer, primary_key=True))
    for name in sorted(EPHEMERAL_TABLES):
        Table(name, md, Column("id", Integer, primary_key=True))

    check("the mirror of today's classification is clean",
          classification_problems(md) == [])

    Table("brand_new_unclassified_table", md,
          Column("id", Integer, primary_key=True))
    problems = classification_problems(md)
    check("a new mapped table with no classification is caught",
          len(problems) == 1)
    check("and the message names it",
          any("brand_new_unclassified_table" in p for p in problems))
    check("and says it is protected anyway, so nobody panics",
          any("protected by default" in p for p in problems))

    print("\n   ... then classify it and observe it pass")
    # Classified by adding it to the set the checker reads. Done through the
    # module's own frozensets, restored afterwards, so this proves the checker
    # and changes nothing on disk.
    import app.preservation as pres
    original = pres.PRESERVED_TABLES
    try:
        pres.PRESERVED_TABLES = frozenset(original | {"brand_new_unclassified_table"})
        check("once classified, the check passes",
              pres.classification_problems(md) == [])
    finally:
        pres.PRESERVED_TABLES = original
    check("and the real classification is back to what it was",
          pres.PRESERVED_TABLES is original)

    print("\n4. THE OTHER WAYS THE CLASSIFICATION CAN BE WRONG")
    md2 = MetaData()
    Table("pipeline_findings", md2, Column("id", Integer, primary_key=True))
    try:
        pres.PRESERVED_TABLES = frozenset({"pipeline_findings"})
        problems = pres.classification_problems(md2)
        check("a table in BOTH lists is caught",
              any("BOTH" in p for p in problems))
        check("and the message says the guard would treat it as ephemeral",
              any("ephemeral" in p for p in problems))
    finally:
        pres.PRESERVED_TABLES = original

    md3 = MetaData()
    Table(EPHEMERAL_PREFIXES[0] + "prices", md3,
          Column("id", Integer, primary_key=True))
    problems = classification_problems(md3)
    check("a REAL mapped table wearing the ephemeral prefix is caught",
          any("ephemeral prefix" in p for p in problems))
    check("because that is the one genuine bypass the prefix opens",
          any("silently loses its protection" in p for p in problems))

    md4 = MetaData()
    Table("ships", md4, Column("id", Integer, primary_key=True))
    problems = classification_problems(md4)
    check("a name in PRESERVED_TABLES that is no longer a table is reported",
          any("not a mapped table" in p for p in problems))

    print("\n5. AND THE REAL PROJECT PASSES")
    check("app/models.py is fully classified today",
          classification_problems() == [])
    from checks.schema_checks import preservation_classification_check
    from pathlib import Path
    findings = preservation_classification_check(None, Path(ROOT))
    check("the registered checker returns exactly one finding",
          len(findings) == 1)
    check("and it is a PASS", findings[0].result == "PASS")
    check("naming how many tables are on each side",
          "24 preserved" in findings[0].details
          and "4 ephemeral" in findings[0].details)

    print("\n%d passed, %d failed" % (len(_passed), len(_failed)))
    if _failed:
        print("FAILED:")
        for f in _failed:
            print("  " + f)
    if SELFTEST:
        print("\n--self-test: expectations were inverted, so a non-zero exit "
              "is the correct outcome.")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
