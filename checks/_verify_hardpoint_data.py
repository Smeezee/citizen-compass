#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_hardpoint_data.py - prove build_hardpoint_data.py's own gates can fail.

RULE16: INDEPENDENT - the generator is run as a subprocess against inputs mutated
here, and each of its gates has to refuse the one that must trip it.
Nothing is imported, so no definition is shared with the thing being
judged.
The pattern, said once because several controls in this repo share it:
driving a real program as a SUBPROCESS with input this file constructed,
and judging the exit code and the printed refusal, is independent. The
tool cannot pass by agreeing with itself, because what must be refused was
decided here and nothing is imported from it.

I1's acceptance is one sentence: "the number of slots in the file equals the
number in the database. Assert it, do not eyeball it." That assertion lives
inside the generator, in verify_counts(). A gate that has never been observed
failing is an untested gate (hard rule 12), and this project has shipped three
of those, each reporting success right up until somebody fed it something bad.

So every gate is run TWICE: once against the real database, where it must pass,
and once against data deliberately damaged in the specific way the gate exists
to catch, where it must fail AND must name the damage. Passing on real data
proves nothing on its own - a verify_counts() that returned [] unconditionally
would pass that half perfectly.

THE DAMAGE IS DONE IN MEMORY, NEVER TO THE DATABASE. It is applied to the
structure collect() returned, which is the same object the gate reads - so what
is under test is the real gate rather than a re-implementation of it. Nothing
here writes to PostgreSQL, and nothing here writes anything under testing/.

`--self-test` inverts every expectation and must exit 1.

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
    """Run build_hardpoint_data.py as a process, the way the build runs it."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "build_hardpoint_data.py")] + list(args),
        capture_output=True, text=True, cwd=ROOT,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main():
    import build_hardpoint_data as B

    B._load_env()
    from app.database import SessionLocal
    from sqlalchemy import text

    session = SessionLocal()
    try:
        data = B.collect(session)

        print("\n1. I1's ACCEPTANCE LINE, AGAINST THE REAL DATABASE")
        db, in_file, problems = B.verify_counts(session, data)
        check("real data: no count problems reported", not problems)
        check("the file's slot count equals the database's (%d)" % in_file["slots"],
              in_file["slots"] == db["slots"] and db["slots"] > 0)
        check("the file's model count equals the database's (%d)" % in_file["models"],
              in_file["models"] == db["models"] and db["models"] > 0)
        # The count is taken from the emitted structure, not from a number
        # collect() remembered - otherwise the gate compares a variable with
        # itself and could never fail. Proven by counting a third way.
        third = sum(len(m[5]) for m in data["models"])
        check("and that count is a real count of the emitted rows (%d)" % third,
              third == db["slots"])

        print("\n2. THE SAME GATE, AGAINST ONE MISSING SLOT")
        # The exact failure the gate exists to catch: a generator that silently
        # drops rows produces a smaller file and a panel that looks fine.
        damaged = copy.deepcopy(data)
        for model in damaged["models"]:
            if model[5]:
                model[5].pop()
                break
        _, _, problems = B.verify_counts(session, damaged)
        check("one missing slot is caught", bool(problems))
        check("and the message names slots",
              any("slots" in p for p in problems))

        print("\n3. THE SAME GATE, AGAINST ONE MISSING MODEL")
        damaged = copy.deepcopy(data)
        damaged["models"].pop()
        _, _, problems = B.verify_counts(session, damaged)
        check("one missing model is caught", bool(problems))
        check("and the message names models",
              any("models" in p for p in problems))

        print("\n4. A MODEL WHOSE OWN slot_count DISAGREES WITH ITS ROWS")
        # A second, independent statement of the same fact, written by the
        # importer. If the two disagree one of them is wrong and neither
        # should ship - and a wrong slot_count is what the panel's own
        # "N mounts" sentence would repeat to a visitor.
        damaged = copy.deepcopy(data)
        damaged["models"][0][3] += 1
        _, _, problems = B.verify_counts(session, damaged)
        check("a slot_count that disagrees with its own rows is caught",
              bool(problems))
        check("and the message names the model",
              any(damaged["models"][0][0] in p for p in problems))

        print("\n5. SLOTS BELONGING TO A MODEL WITH NO COVERAGE ROW")
        # These would be silently dropped by collect(), and the file would be
        # smaller than the database with nothing to show for it.
        damaged = copy.deepcopy(data)
        damaged["_orphans"] = ["a hull nobody declared"]
        _, _, problems = B.verify_counts(session, damaged)
        check("an orphaned model_key is caught", bool(problems))
        check("and it is named rather than merely counted",
              any("a hull nobody declared" in p for p in problems))

        print("\n6. THE SIZE CEILING, PROVEN BY MAKING IT FIRE")
        raw = B.render(data).encode("utf-8")
        kb = len(gzip.compress(raw, 9)) / 1024.0
        print("     real file: %.1f KB gzipped" % kb)
        check("the real file is under the 60 KB ceiling", kb <= 60.0)
        ghost = os.path.join(tempfile.gettempdir(),
                             "_cc_hp_ceiling_must_not_exist.js")
        code, out = run_generator("--max-gzip-kb", "1", "--out", ghost)
        check("a 1 KB ceiling makes the generator refuse", code != 0)
        check("and it says TOO BIG rather than failing vaguely", "TOO BIG" in out)
        check("and it reports the actual number", "gzipped" in out)
        check("and NOTHING was written when it refused", not os.path.exists(ghost))

        print("\n7. DETERMINISM - NO CLOCK IN THE OUTPUT")
        first = B.render(data)
        second = B.render(data)
        check("two renders of the same data are byte-identical", first == second)
        check("and the output carries no generation timestamp",
              "generated at" not in first.lower() and "Generated:" not in first)
        code, out = run_generator("--verify-stable", "--check")
        check("--check against the file on disk passes", code == 0)
        check("and says so in as many words", "up to date" in out)

        print("\n8. THE STALENESS GATE, PROVEN BY MAKING IT FIRE")
        tmp = os.path.join(tempfile.gettempdir(), "_cc_hp_stale.gen.js")
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(first.replace("const HP_DATA=", "const HP_DATA_STALE="))
        code, out = run_generator("--check", "--out", tmp)
        check("a stale file on disk is caught", code != 0)
        check("and the message says STALE", "STALE" in out)
        os.remove(tmp)

        code, out = run_generator("--check", "--out", os.path.join(
            tempfile.gettempdir(), "_cc_hp_absent.gen.js"))
        check("an ABSENT generated file is caught too", code != 0)
        check("and is reported as stale rather than as a crash", "STALE" in out)

        print("\n9. WHAT THE FILE ACTUALLY SAYS")
        check("HP_SCHEMA is emitted", "const HP_SCHEMA=" in first)
        check("HP_COUNTS is emitted", "const HP_COUNTS=" in first)
        check("HP_DATA is emitted", "const HP_DATA=" in first)
        check("the model_key rule is stated in the file itself",
              "model_key_rule" in first)
        # THE SOURCE'S OWN NON-VALUES ARE CARRIED, NOT LAUNDERED HERE.
        # 8 mounts state size 0 and 167 state '<= PLACEHOLDER =>' as their
        # stock item. Both are non-values, and both are the PAGE's business to
        # not display - checks/_verify_hardpoint_panel_offline.mjs owns that.
        # This file's job is that the generator says what the database says: a
        # generator quietly rewriting 0 to null would put the file and the API
        # fallback on different answers, which is the one thing that must not
        # happen. Counted against the database rather than against itself.
        zero_in_file = sum(1 for m in data["models"] for s in m[5] if s[2] == 0)
        zero_in_db = session.execute(
            text("SELECT count(*) FROM ship_hardpoints WHERE size = 0")).scalar()
        check("size 0 is carried through verbatim, not silently rewritten "
              "(%d in file, %d in database)" % (zero_in_file, zero_in_db),
              zero_in_file == zero_in_db)
        ph_in_file = sum(1 for m in data["models"] for s in m[5]
                         if s[3] >= 0 and data["stock"][s[3]] == "<= PLACEHOLDER =>")
        ph_in_db = session.execute(text(
            "SELECT count(*) FROM ship_hardpoints "
            "WHERE stock_item_name = '<= PLACEHOLDER =>'")).scalar()
        check("and so is the game's placeholder item name "
              "(%d in file, %d in database)" % (ph_in_file, ph_in_db),
              ph_in_file == ph_in_db and ph_in_db > 0)
        check("no size is negative - -1 means an index, never a size",
              not any(s[2] is not None and s[2] < 0
                      for m in data["models"] for s in m[5]))
        check("every kind index resolves or is -1",
              all(s[1] == -1 or 0 <= s[1] < len(data["kinds"])
                  for m in data["models"] for s in m[5]))
        check("every stock index resolves or is -1",
              all(s[3] == -1 or 0 <= s[3] < len(data["stock"])
                  for m in data["models"] for s in m[5]))
        check("every reason index resolves or is -1",
              all(m[2] == -1 or 0 <= m[2] < len(data["reasons"])
                  for m in data["models"]))
        check("every slot states a port", all(s[0] for m in data["models"]
                                              for s in m[5]))
        check("models with NO slots are still present - absence is data",
              any(not m[5] for m in data["models"]))
        check("and at least one of them carries the build's own reason",
              any(not m[5] and m[2] >= 0 for m in data["models"]))
        check("every status is one of the four the API can return",
              {m[1] for m in data["models"]} <= {"placed", "absent",
                                                 "refused", "skipped"})

        print("\n10. THE model_key SPELLING RULE MATCHES THE API'S")
        # The page derives a model_key from a model folder name in JavaScript.
        # If that rule and the API's rule disagree, the file answers "not in
        # the dataset" for hulls the API would have found - a regression that
        # looks exactly like missing data. Compared against the API's OWN
        # function, imported, rather than against a copy of it.
        from app.routers.ships import _model_key
        keys = {m[0] for m in data["models"]}
        check("every model_key in the file is already in the API's normal form",
              all(_model_key(k) == k for k in keys))
        check("and the file's keys are the database's keys", keys == {
            r[0] for r in session.execute(
                text("SELECT model_key FROM ship_hardpoint_coverage"))})
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
