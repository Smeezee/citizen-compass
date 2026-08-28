#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_find_data.py - prove build_find_data.py's own gates can fail.

RULE16: UNPROVEN - it imports build_find_data and drives that module's OWN gates,
so a gate whose definition of 'equal' or 'under the ceiling' is wrong is
wrong on both sides of every assertion here. What it does prove, and what
it is for, is that each gate REFUSES input it must refuse: the row counts
and the payload are mutated here, by this file, and the generator has to
reject them. A gate that has been seen refusing is worth more than one
nobody has driven - it is just not an independent source of truth.

H1's acceptance has two gates inside the generator: the row counts in the file
must equal the row counts in the database, and the gzipped file must be under
250 KB. H6 adds a third: two renders of unchanged data must be byte-identical,
and a stale file on disk must be detectable.

A gate that has never been observed failing is an untested gate (hard rule 12).
This project has shipped three of those - a main() returning None, a glob that
opened nothing, and two pipeline gates returning 0 unconditionally - and every
one of them reported success right up until somebody fed it something bad.

So each gate here is run TWICE: once against the real database, where it must
pass, and once against data deliberately damaged in the specific way the gate
exists to catch, where it must fail and must name the damage.

WHAT IS DELIBERATELY NOT DONE HERE
==================================
Nothing is written to the database and nothing is deleted. The damage is done
to the in-memory structure the generator collected, which is the same object
the gate reads - so this tests the real gate, not a re-implementation of it.

`--self-test` inverts every expectation and must exit 1. A harness whose
assertions have quietly stopped asserting reports that instead of a pass.

Rule 15: every open states its encoding.
"""

import copy
import gzip
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

SELFTEST = "--self-test" in sys.argv

_passed = []
_failed = []


def check(label, got, want=True):
    """One assertion. Under --self-test the expectation is inverted."""
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def run_generator(*args):
    """Run build_find_data.py as a process, the way the build runs it."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "build_find_data.py")] + list(args),
        capture_output=True, text=True, cwd=ROOT,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main():
    import build_find_data as B

    B._load_env()
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        data = B.collect(session)

        print("\n1. THE ROW-COUNT GATE, AGAINST THE REAL DATABASE")
        db, in_file, problems = B.verify_counts(session, data)
        check("real data: no row-count problems reported", not problems)
        check("the gate actually counted item_prices (%d)" % in_file["item_prices"],
              in_file["item_prices"] > 0)
        check("the gate actually counted shop_items (%d)" % in_file["shop_items"],
              in_file["shop_items"] > 0)
        check("database counts were read, not assumed", set(db) == {
            "snapshots", "item_categories", "terminals", "shop_items",
            "item_prices"})

        print("\n2. THE SAME GATE, AGAINST DATA WITH ONE PRICE ROW REMOVED")
        # The exact failure the gate exists to catch: a generator that silently
        # drops rows produces a smaller file and a page that looks fine.
        damaged = copy.deepcopy(data)
        for item in damaged["items"]:
            if item[6]:
                item[6].pop()
                break
        _, _, problems = B.verify_counts(session, damaged)
        check("one missing price row is caught", bool(problems))
        check("and the message names item_prices",
              any("item_prices" in p for p in problems))

        print("\n3. THE SAME GATE, AGAINST DATA WITH ONE ITEM REMOVED")
        damaged = copy.deepcopy(data)
        damaged["items"].pop()
        _, _, problems = B.verify_counts(session, damaged)
        check("one missing item is caught", bool(problems))
        check("and the message names shop_items",
              any("shop_items" in p for p in problems))

        print("\n4. THE SAME GATE, AGAINST A DROPPED TERMINAL")
        damaged = copy.deepcopy(data)
        damaged["terms"].pop()
        _, _, problems = B.verify_counts(session, damaged)
        check("a dropped terminal is caught", bool(problems))

        print("\n5. THE SIZE CEILING, PROVEN BY MAKING IT FIRE")
        raw = B.render(data).encode("utf-8")
        kb = len(gzip.compress(raw, 9)) / 1024.0
        print("     real file: %.1f KB gzipped" % kb)
        check("the real file is under the 250 KB ceiling", kb <= 250.0)
        code, out = run_generator("--max-gzip-kb", "1",
                                  "--out", os.path.join(
                                      tempfile.gettempdir(),
                                      "_cc_find_ceiling_must_not_exist.js"))
        check("a 1 KB ceiling makes the generator refuse", code != 0)
        check("and it says TOO BIG rather than failing vaguely", "TOO BIG" in out)
        check("and it reports the actual number", "gzipped" in out)
        check("and NOTHING was written when it refused",
              not os.path.exists(os.path.join(
                  tempfile.gettempdir(),
                  "_cc_find_ceiling_must_not_exist.js")))

        print("\n6. DETERMINISM - H6's NEGATIVE HALF")
        first = B.render(data)
        second = B.render(data)
        check("two renders of the same data are byte-identical", first == second)
        check("and the output carries no generation timestamp",
              "generated at" not in first.lower()
              and "Generated:" not in first)
        code, out = run_generator("--verify-stable", "--check")
        check("--check against the file on disk passes", code == 0, want=True)
        check("and says so in as many words", "up to date" in out)

        print("\n7. THE STALENESS GATE, PROVEN BY MAKING IT FIRE")
        # A generated file that no longer matches the database must be
        # detectable. Written to a throwaway path - the real file is not
        # touched, and nothing under testing/ is written by this harness.
        tmp = os.path.join(tempfile.gettempdir(), "_cc_find_stale.gen.js")
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(first.replace("const FIND_DATA=", "const FIND_DATA_STALE="))
        code, out = run_generator("--check", "--out", tmp)
        check("a stale file on disk is caught", code != 0)
        check("and the message says STALE", "STALE" in out)
        os.remove(tmp)

        code, out = run_generator("--check", "--out", os.path.join(
            tempfile.gettempdir(), "_cc_find_absent.gen.js"))
        check("an ABSENT generated file is caught too", code != 0)
        check("and is reported as stale rather than as a crash", "STALE" in out)

        print("\n8. WHAT THE FILE ACTUALLY SAYS")
        # The shape the page depends on. If these move, the page breaks
        # silently rather than loudly, so they are asserted here.
        check("FIND_SCHEMA is emitted", "const FIND_SCHEMA=" in first)
        check("FIND_COUNTS is emitted", "const FIND_COUNTS=" in first)
        check("FIND_DATA is emitted", "const FIND_DATA=" in first)
        check("a snapshot key is present",
              any(s[1] for s in data["snaps"]))
        check("every snapshot carries a captured date",
              all(s[2] for s in data["snaps"]))
        check("no price row is a zero pretending to be a price",
              not any(p[1] == 0 or p[2] == 0
                      for it in data["items"] for p in it[6]))
        check("every price row has at least one side",
              all(p[1] is not None or p[2] is not None
                  for it in data["items"] for p in it[6]))
        check("items with no prices are still present",
              any(not it[6] for it in data["items"]))
        check("every price row points at a terminal that exists",
              all(0 <= p[0] < len(data["terms"])
                  for it in data["items"] for p in it[6]))
        check("every price row points at a snapshot that exists",
              all(0 <= p[3] < len(data["snaps"])
                  for it in data["items"] for p in it[6]))
        check("every date index resolves or is -1",
              all(p[4] == -1 or 0 <= p[4] < len(data["dates"])
                  for it in data["items"] for p in it[6]))
        check("both source kinds are present",
              {it[0] for it in data["items"]} == {0, 1})
    finally:
        session.close()

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
