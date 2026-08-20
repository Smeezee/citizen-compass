#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rule 12 proof for G5 / R1 - the commodity cross-reference.

THREE THINGS ARE PROVEN HERE, AND THEY FAIL IN DIFFERENT WAYS
==============================================================

1. THE MATCHER. Fed names that must link and names that must not, so a rule
   that matched everything or nothing would be caught. A cross-reference that
   linked the wrong substance would put one commodity's prices under another
   commodity's name - the same class of error as a Gladius wearing a
   Hammerhead's hardpoints, and just as invisible on the page.

2. THE CONSTRAINTS, each OBSERVED REFUSING a deliberately bad row and each
   naming the constraint that must do the rejecting. "Something raised" is not
   enough: a misspelled column also raises, and would make a missing constraint
   look enforced. Acceptance cases run alongside, because every constraint
   could be CHECK(false) and the refusal half would be perfectly happy.

3. NOTHING WAS MERGED AND NOTHING WAS DELETED. This is the half that is
   specific to R1 and the one worth being most careful about: the whole point
   of a link table is that both representations survive it. So the 158
   category-36 items and the 204 commodities are counted afterwards, and the
   link rows are required to point at rows that still exist on both sides with
   their original names intact.

Nothing is committed and nothing existing is touched. The control SEEDS ITS
OWN four shop_items rows at sentinel uex_ids and drives the constraints against
those, rather than clearing the real link table - hard rule 3 forbids DELETE
FROM against a database this process did not create, and it makes no exception
for "inside a transaction I meant to roll back". Every refusal case runs inside
a SAVEPOINT that is rolled back, inside an outer transaction that is also rolled
back, and the script checks afterwards that no seeded row survived.

`--self-test` inverts every assertion and requires this script to exit 1.

Run: venv/Scripts/python.exe checks/_verify_commodity_xref.py

Rule 15: encodings stated (no file reads - this is all database).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.database import engine  # noqa: E402
from checks._verify_shop_schema_db import TEST_ID_BASE  # noqa: E402
from build_commodity_xref import (  # noqa: E402
    COMMODITY_CATEGORY_UEX_ID,
    normalise,
    token_key,
)

# Names that must resolve to the same key, and names that must not.
EXACT_SAME = [
    ("Agricium", "agricium"),
    ("Aslarite (Raw)", "ASLARITE  (raw)"),
    ("Quantum Fuel", "quantum-fuel"),
]
EXACT_DIFFERENT = [
    ("Aslarite (Raw)", "Aslarite (Ore)"),
    ("Agricium", "Agricium (Ore)"),
    ("Ice (Raw)", "Pressurized Ice"),
    ("Boron", "Bor"),
]
TOKEN_SAME = [
    ("Raw Ice", "Ice (Raw)"),
]
TOKEN_DIFFERENT = [
    # The one that matters: same stem, different qualifier. A token-set match
    # must NOT collapse these, or every raw ore inherits its refined twin's
    # prices.
    ("Aslarite (Raw)", "Aslarite (Ore)"),
    ("Carinite (Pure)", "Carinite (Raw)"),
    ("Boron", "Bor"),
]


def main():
    self_test = "--self-test" in sys.argv
    passed, failed = 0, []

    def record(ok, label, detail=""):
        nonlocal passed
        if self_test:
            ok = not ok
        if ok:
            passed += 1
            print(f"  ok   {label}")
        else:
            failed.append(f"{label} {detail}".strip())
            print(f"  FAIL {label} {detail}")

    # ---- 1. THE MATCHER ---------------------------------------------------
    print("--- the matching rules, driven both ways ---")
    for a, b in EXACT_SAME:
        record(normalise(a) == normalise(b),
               f"exact: {a!r} and {b!r} are the same name",
               f"{normalise(a)!r} vs {normalise(b)!r}")
    for a, b in EXACT_DIFFERENT:
        record(normalise(a) != normalise(b),
               f"exact: NEGATIVE - {a!r} and {b!r} are NOT the same name",
               "they collapsed to the same key, which would link two different "
               "substances")
    for a, b in TOKEN_SAME:
        record(token_key(a) == token_key(b),
               f"token: {a!r} and {b!r} are the same words reordered")
    for a, b in TOKEN_DIFFERENT:
        record(token_key(a) != token_key(b),
               f"token: NEGATIVE - {a!r} and {b!r} stay distinct",
               "a token-set match that collapsed these would give every raw "
               "ore its refined twin's prices")

    # A rule that returned the same key for everything would satisfy every
    # positive case above. This is the guard against that.
    record(len({normalise(n) for n in
                ("Agricium", "Aluminum", "Boron", "Titanium")}) == 4,
           "matcher: four different names produce four different keys - the "
           "rule is not collapsing everything to one value")

    conn = engine.connect()
    outer = conn.begin()
    try:
        # ---- SEED OUR OWN ROWS. DO NOT TOUCH THE REAL LINKS ---------------
        #
        # The first version of this cleared shop_item_commodity_xref inside the
        # rolled-back transaction so the unique constraints would collide with
        # this script's rows instead of production ones. That worked and lost
        # nothing - but hard rule 3 forbids DELETE FROM against a database this
        # process did not create, and it does not carve out an exception for
        # "inside a transaction I intended to roll back". A rollback that does
        # not happen because the script died between the DELETE and the
        # rollback is exactly the accident the rule exists to prevent.
        #
        # So the control now builds its own population, the way
        # _verify_shop_schema_db.py does: four throwaway shop_items rows at
        # sentinel uex_ids, linked to each other. Nothing production-side is
        # read, written, or removed, and the unique constraints are driven just
        # as hard.
        seeded = {}
        for offset, (kind, name) in enumerate((
            ("item", "Control item A"),
            ("item", "Control item B"),
            ("commodity", "Control commodity A"),
            ("commodity", "Control commodity B"),
        )):
            seeded[offset] = conn.execute(text(
                "INSERT INTO shop_items (uex_id, name, source_kind, confidence) "
                "VALUES (:uex_id, :name, :kind, 'unverified') RETURNING id"
            ), {"uex_id": TEST_ID_BASE + offset, "name": name,
                "kind": kind}).scalar()

        item_ids = [seeded[0], seeded[1]]
        commodity_ids = [seeded[2], seeded[3]]

        INSERT = (
            "INSERT INTO shop_item_commodity_xref "
            "(item_shop_item_id, commodity_shop_item_id, match_method) "
            "VALUES (:i, :c, :m)"
        )

        print("\n--- ACCEPTED: the table takes the rows it should ---")
        for label, params in (
            ("a plain exact_name link",
             {"i": item_ids[0], "c": commodity_ids[0], "m": "exact_name"}),
            ("a token_set link - the weaker tier is storable, not silently "
             "dropped",
             {"i": item_ids[1], "c": commodity_ids[1], "m": "token_set"}),
        ):
            sp = conn.begin_nested()
            try:
                conn.execute(text(INSERT), params)
                sp.rollback()
                record(True, label)
            except Exception as exc:
                sp.rollback()
                record(False, label, f"was REJECTED: {str(exc)[:160]}")

        print("\n--- REFUSED: every constraint observed rejecting a bad row ---")
        conn.execute(text(INSERT), {"i": item_ids[0], "c": commodity_ids[0],
                                    "m": "exact_name"})

        refusals = [
            ("the SAME item linked to a second commodity",
             {"i": item_ids[0], "c": commodity_ids[1], "m": "exact_name"},
             "uq_shop_item_commodity_xref_item"),
            ("the SAME commodity linked from a second item",
             {"i": item_ids[1], "c": commodity_ids[0], "m": "exact_name"},
             "uq_shop_item_commodity_xref_commodity"),
            ("a row linked to itself",
             {"i": item_ids[1], "c": item_ids[1], "m": "exact_name"},
             "ck_shop_item_commodity_xref_distinct"),
            ("a match_method nobody defined",
             {"i": item_ids[1], "c": commodity_ids[1], "m": "vibes"},
             "ck_shop_item_commodity_xref_method_valid"),
            ("a link to a shop_items row that does not exist",
             {"i": item_ids[1], "c": -999, "m": "exact_name"},
             "foreign key"),
        ]
        for label, params, fragment in refusals:
            sp = conn.begin_nested()
            try:
                conn.execute(text(INSERT), params)
                sp.rollback()
                record(False, label,
                       "THE ROW WAS ACCEPTED - this constraint is not enforcing")
            except Exception as exc:
                sp.rollback()
                message = str(exc).lower()
                if fragment.lower() in message:
                    record(True, f"{label}  <- {fragment}")
                else:
                    record(False, label,
                           f"rejected, but NOT by {fragment}: {str(exc)[:160]}")
    except SystemExit:
        pass
    finally:
        outer.rollback()
        conn.close()

    # ---- 3. NOTHING WAS MERGED AND NOTHING WAS DELETED -------------------
    #
    # R1's actual requirement. A link table that quietly cost us the item-side
    # rows would satisfy every assertion above and still be the thing the
    # ruling forbade.
    print("\n--- R1: both representations still exist, unmodified ---")
    with engine.connect() as check:
        items = check.execute(text(
            "SELECT count(*) FROM shop_items si "
            "JOIN item_categories ic ON ic.id = si.category_id "
            "WHERE ic.uex_id = :cat AND si.source_kind = 'item'"
        ), {"cat": COMMODITY_CATEGORY_UEX_ID}).scalar()
        commodities = check.execute(text(
            "SELECT count(*) FROM shop_items WHERE source_kind = 'commodity'"
        )).scalar()
        links = check.execute(text(
            "SELECT count(*) FROM shop_item_commodity_xref"
        )).scalar()

        record(items == 158,
               f"all 158 category-36 item rows are still there ({items})")
        record(commodities == 204,
               f"all 204 commodity rows are still there ({commodities})")
        record(links == 157,
               f"157 links are held ({links})")

        # Every link points at rows that still exist on BOTH sides, and at one
        # of each KIND - a link from a commodity to a commodity would be a
        # merge wearing a link's clothes.
        broken = check.execute(text(
            "SELECT count(*) FROM shop_item_commodity_xref x "
            "LEFT JOIN shop_items i ON i.id = x.item_shop_item_id "
            "LEFT JOIN shop_items c ON c.id = x.commodity_shop_item_id "
            "WHERE i.id IS NULL OR c.id IS NULL "
            "   OR i.source_kind <> 'item' OR c.source_kind <> 'commodity'"
        )).scalar()
        record(broken == 0,
               "every link points at one surviving ITEM row and one surviving "
               "COMMODITY row",
               f"{broken} link(s) do not")

        # The item side still has ZERO prices of its own. If that ever changes
        # it is news, and if it changed because something merged the two, it is
        # the exact failure R1 forbids.
        item_side_prices = check.execute(text(
            "SELECT count(*) FROM item_prices p "
            "JOIN shop_items si ON si.id = p.shop_item_id "
            "JOIN item_categories ic ON ic.id = si.category_id "
            "WHERE ic.uex_id = :cat AND si.source_kind = 'item'"
        ), {"cat": COMMODITY_CATEGORY_UEX_ID}).scalar()
        record(item_side_prices == 0,
               "the item side still carries ZERO prices - the link did not "
               "copy anything across, which is what 'link, do not merge' means",
               f"it now carries {item_side_prices}")

        unmatched = check.execute(text(
            "SELECT si.name FROM shop_items si "
            "JOIN item_categories ic ON ic.id = si.category_id "
            "LEFT JOIN shop_item_commodity_xref x "
            "       ON x.item_shop_item_id = si.id "
            "WHERE ic.uex_id = :cat AND si.source_kind = 'item' "
            "  AND x.id IS NULL ORDER BY si.name"
        ), {"cat": COMMODITY_CATEGORY_UEX_ID}).scalars().all()
        record(list(unmatched) == ["Boron"],
               "exactly one category-36 item found no counterpart, and it is "
               "'Boron'",
               f"unmatched: {list(unmatched)}")

        # ---- the control left nothing behind -------------------------------
        leftovers = check.execute(text(
            "SELECT count(*) FROM shop_items WHERE uex_id >= :base"
        ), {"base": TEST_ID_BASE}).scalar()
        record(leftovers == 0,
               "the control committed none of its own seeded rows",
               f"{leftovers} test row(s) survived the rollback")
        stray_links = check.execute(text(
            "SELECT count(*) FROM shop_item_commodity_xref "
            "WHERE match_method NOT IN ('exact_name', 'token_set') "
            "   OR commodity_shop_item_id = item_shop_item_id"
        )).scalar()
        record(stray_links == 0,
               "and no malformed link survived either",
               f"{stray_links} stray link(s)")

    print("\n" + "=" * 62)
    if self_test:
        print("SELF-TEST: every assertion was inverted.")
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print("  -", x)
        return 1
    print(f"All {passed} assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
