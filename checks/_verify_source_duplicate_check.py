#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rule 12 proof for C7, the source-duplicate auditor (G4).

RULE16: UNPROVEN - it imports source_duplicate_check and judges what that
function returns. The duplicate it must find is planted here, in a temp
snapshot root, so the auditor is answering a question this file knows the
answer to rather than one it has to be trusted about.
This is a RULE 12 control, and rule 16 is a different axis. Proving a
checker fires on input that must trip it and stays silent on clean input
is exactly what rule 12 asks for, and this file does both halves. Being
UNPROVEN under rule 16 is not a criticism of it - it is the observation
that a checker cannot be an independent source of truth about itself.

BOTH HALVES, LIKE C6
--------------------
A planted price CONFLICT must fire it. A planted BYTE-IDENTICAL repeat must
not. Either half alone is worthless: an auditor that fires on everything is
noise wearing a checker's name, and one that has never been seen firing is not
an auditor at all.

WHY THIS IS A SEPARATE FILE FROM _verify_shop_checks.py
-------------------------------------------------------
C1-C5 read the database, so their control needs a live session and plants rows
inside a rolled-back transaction. C7 reads the LANDED SNAPSHOT FILES, because
the duplicate it looks for does not survive the import - the importer resolves
it on the way in. So this plants files in a temp directory instead and needs no
database at all, which also means it still runs on a machine that has none.

THE CASES THAT MUST NOT FIRE ARE THE INTERESTING ONES
-----------------------------------------------------
The same commodity at two DIFFERENT terminals at different prices is the normal
state of the universe and flagging it would drown the real finding. So is a
pair whose buy and sell agree while a rolling AVERAGE differs. Both are here
explicitly, because the way this checker fails in practice is not by missing a
conflict - it is by calling everything one.

The real repo data is checked too, so the known case cannot quietly stop being
found: "Stims" at HUR-L5, 5,800 against 4,900.

`--self-test` inverts every assertion and requires this script to exit 1.

Run: venv/Scripts/python.exe checks/_verify_source_duplicate_check.py

Rule 15: encodings stated.
"""

import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, REPO)

from checks.shop_checks import SNAPSHOT_ROOT, source_duplicate_check  # noqa: E402


def commodity_row(id_commodity, id_terminal, buy, sell, **extra):
    row = {
        "id": 1,
        "id_commodity": id_commodity,
        "id_terminal": id_terminal,
        "commodity_name": "Planted %s" % id_commodity,
        "terminal_name": "TERM-%s" % id_terminal,
        "price_buy": buy,
        "price_sell": sell,
        "price_buy_avg": buy,
        "price_sell_avg": sell,
        "date_modified": 1750000000,
    }
    row.update(extra)
    return row


def item_row(id_item, id_terminal, buy, sell):
    return {
        "id": 1,
        "id_item": id_item,
        "id_terminal": id_terminal,
        "item_name": "Planted item %s" % id_item,
        "item_uuid": "uuid-%s" % id_item,
        "terminal_name": "TERM-%s" % id_terminal,
        "price_buy": buy,
        "price_sell": sell,
        "date_modified": 1750000000,
    }


def plant(root, snapshot, filename, rows):
    """Write a UEX-shaped envelope into a fake snapshot tree."""
    d = os.path.join(root, SNAPSHOT_ROOT, snapshot)
    os.makedirs(d, exist_ok=True)
    with io.open(os.path.join(d, filename), "w", encoding="utf-8") as fh:
        json.dump({"status": "ok", "http_code": 200, "data": rows}, fh)


def fired(findings):
    return [f for f in findings if f.result == "WARNING"]


def main():
    self_test = "--self-test" in sys.argv
    passed = 0
    failed = []

    def record(ok, what):
        nonlocal passed
        if self_test:
            ok = not ok
        if ok:
            passed += 1
        else:
            failed.append(what)

    workdir = tempfile.mkdtemp(prefix="cc_c7_")

    # ---- HALF ONE: A PLANTED CONFLICT MUST FIRE IT ------------------------
    root = os.path.join(workdir, "conflict")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800),
        commodity_row(1, 5, 0, 4900),      # same pair, different sell price
    ])
    out = source_duplicate_check(None, root)
    hits = fired(out)
    record(len(hits) == 1, "a planted price conflict fires C7 exactly once")
    blob = " ".join(f.details for f in hits)
    record("5800" in blob and "4900" in blob,
           "and the finding carries BOTH prices, so the reader can see what "
           "the disagreement actually is")
    record(any("TERM-5" in f.details for f in hits),
           "and names the terminal it happened at")
    record(all(f.result != "PASS" for f in out),
           "a file with a conflict does not ALSO report PASS - one file, one "
           "verdict")

    # ---- HALF TWO: A BYTE-IDENTICAL REPEAT MUST NOT ----------------------
    root = os.path.join(workdir, "identical")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800),
        commodity_row(1, 5, 0, 5800),      # the same observation, listed twice
    ])
    out = source_duplicate_check(None, root)
    record(fired(out) == [],
           "a byte-identical repeat does NOT fire C7 - it is noise, and "
           "flagging it would bury the conflicts four deep")
    record(any(f.result == "PASS" for f in out),
           "and the file is reported PASS rather than silently omitted")
    record(any("1 pair(s) repeat with IDENTICAL prices" in f.details
               for f in out),
           "and the PASS still SAYS the repeat was seen and dismissed, rather "
           "than pretending the file was clean")

    # ---- THE THINGS THAT MUST NOT FIRE, WHICH IS HOW THIS ACTUALLY FAILS --
    root = os.path.join(workdir, "different_terminals")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800),
        commodity_row(1, 6, 0, 4900),      # SAME commodity, DIFFERENT terminal
    ])
    record(fired(source_duplicate_check(None, root)) == [],
           "the same commodity at two DIFFERENT terminals at different prices "
           "does not fire - that is the normal state of the universe")

    root = os.path.join(workdir, "different_items")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800),
        commodity_row(2, 5, 0, 4900),      # DIFFERENT commodities, one terminal
    ])
    record(fired(source_duplicate_check(None, root)) == [],
           "two different commodities at one terminal do not fire")

    root = os.path.join(workdir, "avg_only")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800, price_sell_avg=5000),
        commodity_row(1, 5, 0, 5800, price_sell_avg=5100),
    ])
    record(fired(source_duplicate_check(None, root)) == [],
           "a repeat that agrees on buy/sell but differs on a rolling AVERAGE "
           "does not fire - an average is not a price and section 3.1 forbids "
           "showing one as if it were")

    # ---- IT MUST SEE THE ITEMS FILE TOO, NOT ONLY COMMODITIES ------------
    root = os.path.join(workdir, "items")
    plant(root, "20990101T000000Z", "items_prices_all.json", [
        item_row(11, 5, 100, 50),
        item_row(11, 5, 100, 60),
    ])
    hits = fired(source_duplicate_check(None, root))
    record(len(hits) == 1,
           "a conflict in items_prices_all.json fires too - C7 is not "
           "commodity-only")

    # ---- ONE SNAPSHOT'S CONFLICT DOES NOT CONTAMINATE ANOTHER ------------
    root = os.path.join(workdir, "two_snapshots")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800),
        commodity_row(1, 5, 0, 4900),
    ])
    plant(root, "20990202T000000Z", "commodities_prices_all.json", [
        commodity_row(1, 5, 0, 5800),
    ])
    out = source_duplicate_check(None, root)
    record(len(fired(out)) == 1,
           "with two snapshots present, only the one holding the conflict "
           "fires")
    record(any(f.result == "PASS" and "20990202T000000Z" in (f.subject or "")
               for f in out),
           "and the clean snapshot is reported clean BY NAME - the check is "
           "per file, so a shared verdict could hide which one is bad")

    # ---- IT MUST NOT REPORT PASS WHEN IT LOOKED AT NOTHING ---------------
    #
    # The landed snapshots are gitignored. On a fresh clone this checker finds
    # no files at all, and "no files" reporting PASS is precisely the failure
    # this project calls SILENT SUCCESS.
    root = os.path.join(workdir, "empty")
    os.makedirs(root, exist_ok=True)
    out = source_duplicate_check(None, root)
    record(all(f.result != "PASS" for f in out),
           "NO SNAPSHOT DIRECTORY AT ALL does not report PASS")
    record(any(f.result == "LIMITATION" and "NOT PERFORMED" in f.details
               for f in out),
           "it says NOT PERFORMED instead, which is the honest answer")

    root = os.path.join(workdir, "no_price_files")
    os.makedirs(os.path.join(root, SNAPSHOT_ROOT, "20990101T000000Z"),
                exist_ok=True)
    out = source_duplicate_check(None, root)
    record(all(f.result != "PASS" for f in out),
           "a snapshot directory holding no price files does not report PASS "
           "either")
    record(any(f.result == "LIMITATION" for f in out),
           "it reports LIMITATION")

    # ---- AN EMPTY-BUT-VALID ENVELOPE IS NOT A BROKEN ONE -----------------
    root = os.path.join(workdir, "null_data")
    plant(root, "20990101T000000Z", "commodities_prices_all.json", None)
    try:
        out = source_duplicate_check(None, root)
        crashed = False
    except Exception as exc:  # noqa: BLE001
        out, crashed = [], repr(exc)
    record(crashed is False,
           "a valid envelope whose data is null does not crash the checker - "
           "44 of the 100 category files in the 08-01 snapshot look like that "
           "and they are genuinely empty, not broken")

    # ---- AND THE REAL DATA, SO THE KNOWN CASE CANNOT STOP BEING FOUND ----
    out = source_duplicate_check(None, REPO)
    hits = fired(out)
    if not out or all(f.result == "LIMITATION" for f in out):
        failed.append("REAL DATA: NOT PERFORMED - no landed snapshots in this "
                      "working copy, so the known Stims case was not "
                      "re-checked. Reported as not performed, never as passed.")
    else:
        blob = " ".join(f.details for f in hits)
        record(any("Stims" in f.details for f in hits),
               "REAL DATA: the known 'Stims' conflict at HUR-L5 is found")
        record("5800" in blob and "4900" in blob,
               "REAL DATA: and it reports both 5,800 and 4,900")
        record(len(hits) == 1,
               "REAL DATA: exactly ONE conflict across every landed price "
               "file - the other four repeats are byte-identical and stay "
               "silent, which is the point of the distinction")
        record(any(f.result == "PASS" and "items_prices_all" in (f.subject or "")
                   for f in out),
               "REAL DATA: the 23,734-row items file is clean and says so")

    print("=" * 62)
    print("(fixtures under %s - left in place, this project does not delete)"
          % workdir)
    if self_test:
        print("SELF-TEST: every assertion was inverted.")
    if failed:
        print("FAILED %d of %d:" % (len(failed), passed + len(failed)))
        for x in failed:
            print("  -", x)
        return 1
    print("All %d assertions passed." % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
