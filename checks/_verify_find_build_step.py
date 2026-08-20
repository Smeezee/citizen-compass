#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_find_build_step.py - H6: the generator is a build step, and a stale
generated file is detectable.

THE TWO CONTROLS H6 NAMES, BOTH OF THEM, BY BEHAVIOUR:

  1. "change one row in the database, re-run the build, confirm the file
     changed."
  2. "AND the negative half: run the build twice with no database change and
     confirm the file is byte-identical - a generator with a timestamp baked
     into it churns git forever and nobody notices for a year."

The second is the one that is easy to skip and is the reason H6 exists. A
generator that regenerated correctly AND stamped the time into its output would
pass control 1 every single time.

Plus the thing both of those assume: that the BUILD runs the generator at all.
Proved by damaging the generated file and requiring the build to repair it -
not by grepping build_deploy.py for a filename, which proves only that
somebody typed it.

WHAT THIS DOES TO THE DATABASE, STATED PLAINLY
==============================================
It UPDATEs exactly one column of exactly one row of item_prices, and puts it
back. Not a DELETE, not a TRUNCATE, not a migration - none of the operations
hard rule 3 forbids. The old value is read first and printed, the restore runs
in a finally block, and the restore is then PROVEN: the regenerated file must
hash back to what it was before this harness ran. If that final comparison
fails, the harness says so loudly and prints the SQL to put it right by hand.

A verified backup was taken before this was first run (hard rule 4).

Rule 15: every open states its encoding.

Usage:  python checks/_verify_find_build_step.py [--self-test]
"""

import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

GEN = os.path.join(ROOT, "testing", "_src", "find_data.gen.js")
SUM = os.path.join(ROOT, "testing", "_src", "find_checksum.gen.js")
BUILD = os.path.join(ROOT, "testing", "_src", "build_deploy.py")

SELFTEST = "--self-test" in sys.argv

_passed, _failed = [], []


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run_build():
    """The NORMAL build, exactly as a person would run it."""
    proc = subprocess.run([sys.executable, BUILD], capture_output=True,
                          text=True, cwd=ROOT)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main():
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT, ".env"))
    from app.database import SessionLocal
    from sqlalchemy import text

    print("\n0. THE BUILD RUNS THE GENERATOR AT ALL")
    code, out = run_build()
    check("a normal build succeeds", code == 0)
    check("and says it generated the find data",
          "find data generated" in out)
    baseline = sha(GEN)
    baseline_sum = sha(SUM)
    print("     baseline sha256: %s" % baseline)

    # Proved by BEHAVIOUR: damage the generated file and require the build to
    # repair it. Grepping build_deploy.py for a filename would prove only that
    # somebody typed the filename.
    with open(GEN, "a", encoding="utf-8", newline="") as fh:
        fh.write("\n/* DAMAGE PLANTED BY _verify_find_build_step.py */\n")
    check("the planted damage really is in the file", sha(GEN) != baseline)
    code, out = run_build()
    check("the build succeeds with a damaged generated file present", code == 0)
    check("and REGENERATED it - the damage is gone", sha(GEN) == baseline)
    check("so the generator is genuinely part of the build, not a memo",
          "/* DAMAGE PLANTED" not in
          open(GEN, "r", encoding="utf-8", newline="").read())

    print("\n1. THE NEGATIVE HALF: two builds, no database change")
    # The one that is easy to skip and the reason H6 exists at all. A
    # generator that regenerated correctly AND stamped the time into its
    # output would sail through control 2 below on every run.
    code, _ = run_build()
    check("a second build succeeds", code == 0)
    check("and the data file is BYTE-IDENTICAL", sha(GEN) == baseline,
          )
    check("and so is the published checksum", sha(SUM) == baseline_sum)
    code, _ = run_build()
    check("and a third build changes nothing either", sha(GEN) == baseline)

    print("\n2. THE POSITIVE HALF: change one row, rebuild, the file changes")
    session = SessionLocal()
    row = session.execute(text(
        "SELECT id, price_buy FROM item_prices "
        "WHERE price_buy IS NOT NULL ORDER BY id LIMIT 1"
    )).first()
    if row is None:
        session.close()
        print("  NOT PERFORMED: no priced row to change. Reported as not "
              "performed, never as a pass.")
        return 1
    row_id, old_price = int(row[0]), int(row[1])
    new_price = old_price + 7
    restore_sql = ("UPDATE item_prices SET price_buy = %d WHERE id = %d;"
                   % (old_price, row_id))
    print("     item_prices id=%d  price_buy %d -> %d" % (row_id, old_price, new_price))
    print("     restore SQL, if this harness dies: %s" % restore_sql)

    changed_sha = None
    try:
        session.execute(text("UPDATE item_prices SET price_buy = :p "
                             "WHERE id = :i"), {"p": new_price, "i": row_id})
        session.commit()
        code, _ = run_build()
        check("the build succeeds after the row changed", code == 0)
        changed_sha = sha(GEN)
        check("and the generated file CHANGED", changed_sha != baseline)
        body = open(GEN, "r", encoding="utf-8", newline="").read()
        check("and the new value is actually in it", str(new_price) in body)
        check("and the published checksum changed with it",
              sha(SUM) != baseline_sum)
        check("and the checksum describes the NEW file",
              hashlib.sha256(open(GEN, "rb").read()).hexdigest() in
              open(SUM, "r", encoding="utf-8", newline="").read())

        print("\n3. AND --check NOTICES A FILE THAT NO LONGER MATCHES")
        # Put the database back but NOT the file, so the file on disk is
        # genuinely stale against the database - which is the exact condition
        # H6 says must be detectable.
        session.execute(text("UPDATE item_prices SET price_buy = :p "
                             "WHERE id = :i"), {"p": old_price, "i": row_id})
        session.commit()
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "build_find_data.py"), "--check"],
            capture_output=True, text=True, cwd=ROOT)
        check("--check refuses a file that no longer matches the database",
              proc.returncode != 0)
        check("and says STALE", "STALE" in (proc.stdout or "") + (proc.stderr or ""))
    finally:
        # Restore, whatever happened above.
        try:
            session.execute(text("UPDATE item_prices SET price_buy = :p "
                                 "WHERE id = :i"), {"p": old_price, "i": row_id})
            session.commit()
        except Exception as exc:      # pragma: no cover - reported, not hidden
            print("  RESTORE FAILED: %s" % exc)
            print("  RUN THIS BY HAND: %s" % restore_sql)
        session.close()

    print("\n4. THE DATABASE AND THE FILE ARE BACK WHERE THEY STARTED")
    code, _ = run_build()
    check("a final build succeeds", code == 0)
    restored = sha(GEN)
    check("and the file hashes back to the baseline", restored == baseline,
          )
    if restored != baseline:
        print("  THE DATABASE MAY STILL BE MODIFIED. RUN THIS BY HAND:")
        print("    " + restore_sql)
    check("and so does the published checksum", sha(SUM) == baseline_sum)
    check("which is what proves the restore, rather than the restore having "
          "merely been attempted", restored == baseline)

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
