#!/usr/bin/env python3
"""
C5b - THE CHECK THE DIFF TOOL CANNOT PASS WHILE BROKEN.

RULE16: INDEPENDENT - the diff tool is run as a subprocess between two snapshots
built here, so the change it must report is one this file already knows.
The title is the rule: a broken tool cannot pass, because the expected
answer did not come from the tool.
The pattern, said once because several controls in this repo share it:
driving a real program as a SUBPROCESS with input this file constructed,
and judging the exit code and the printed refusal, is independent. The
tool cannot pass by agreeing with itself, because what must be refused was
decided here and nothing is imported from it.

A diff tool that reports spurious changes passes every other check you can
write against it. It parses, it runs, it produces plausible output, and the
output is wrong in the one way nobody can see without a known answer.

So this gives it known answers:

  1. A SNAPSHOT DIFFED AGAINST ITSELF MUST BE EMPTY. Every category, both
     sides. Any output at all here is the tool, never the data.

  2. A SINGLE PLANTED FIELD CHANGE MUST BE REPORTED EXACTLY ONCE - in the right
     file, on the right ID, naming the right field, with the right before and
     after. Not "some changes were found".

  3. A RENAME MUST NOT LOOK LIKE A REMOVAL PLUS AN ADDITION. This is the
     standing "join on IDs, never names" rule, asserted rather than trusted: a
     ship whose Name changes is the SAME ship, and a name join would report the
     fleet losing one and gaining one.

  4. A FIELD UPSTREAM NEVER EMITTED BEFORE IS A SCHEMA CHANGE, NOT A PATCH
     CHANGE. Counting it as the game changing poisons every number in the
     summary, which is the specific failure the order calls out.

Fixtures are built from the REAL sealed snapshot, in a temp directory, and
nothing under data-layer/ is written.

Usage: python checks/_verify_patch_diff.py [--self-test]
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SNAPS = os.path.join(REPO, "data-layer", "external-sources",
                     "scunpacked-data", "snapshots")
MANS = os.path.join(REPO, "data-layer", "external-source-manifests")
TOOL = os.path.join(REPO, "build_patch_diff.py")
BASE_RUN = "20260801T204744Z"

SELFTEST = "--self-test" in sys.argv
passed = 0
failures = []


def check(ok, label, detail=""):
    global passed
    want = (not ok) if SELFTEST else ok
    if want:
        passed += 1
        print("  ok   %s" % label)
    else:
        failures.append("%s %s" % (label, detail))
        print("  FAIL %s %s" % (label, detail))
    return want


def not_performed(why):
    print("\nNOT PERFORMED - reported, not passed over.\n" + why)
    sys.exit(2)


def run_diff(a, b, out, man_root):
    env = dict(os.environ)
    env["CC_MANIFEST_DIR"] = man_root
    r = subprocess.run([sys.executable, TOOL, "--from", a, "--to", b,
                        "--no-items", "--out", out],
                       capture_output=True, text=True, env=env,
                       encoding="utf-8", errors="replace")
    return r


def load(out, name):
    p = os.path.join(out, name)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    base = os.path.join(SNAPS, BASE_RUN)
    if not os.path.isdir(os.path.join(base, "ships")):
        not_performed("no sealed snapshot at %s - nothing to diff, so nothing "
                      "is claimed." % base)

    tmp = tempfile.mkdtemp(prefix="cc_c5b_")
    try:
        print("=" * 66)
        print("C5b - the patch diff, against known answers")
        print("fixtures from %s" % BASE_RUN)
        print("=" * 66)

        # ---------------------------------------------------- 1. self-diff
        print("\n--- 1. a snapshot against itself is empty ---")
        out1 = os.path.join(tmp, "self")
        r = run_diff(base, base, out1, MANS)
        check(r.returncode == 0, "the tool ran", r.stderr.strip()[:160])
        empty = True
        for f in ("ships_added.json", "ships_removed.json", "ships_changed.json",
                  "ships_schema_changes.json"):
            d = load(out1, f)
            if d is None or len(d) != 0:
                empty = False
                check(False, "%s is empty" % f,
                      "%s entries" % ("missing" if d is None else len(d)))
        if empty:
            check(True, "every ships category is empty - added, removed, "
                        "changed and schema")
        man = load(out1, "MANIFEST.json") or {}
        check((man.get("from") or {}).get("build") == "4.9.0-LIVE.12232306",
              "and both sides are named by their commit subject, not '4.9'",
              str((man.get("from") or {}).get("build")))

        # -------------------------------------- fixture: one field changed
        print("\n--- 2. one planted field change, reported exactly once ---")
        fix_run = "29990101T000000Z"
        fix = os.path.join(tmp, fix_run)
        shutil.copytree(os.path.join(base, "ships"), os.path.join(fix, "ships"))
        man_root = os.path.join(tmp, "manifests")
        os.makedirs(os.path.join(man_root, fix_run))
        os.makedirs(os.path.join(man_root, BASE_RUN))
        # The base side's manifest is the REAL one, copied - so the tool is
        # still reading a genuine build name for the left-hand side.
        real_man = os.path.join(MANS, BASE_RUN)
        for f in os.listdir(real_man):
            if f.endswith(".json"):
                shutil.copy(os.path.join(real_man, f),
                            os.path.join(man_root, BASE_RUN, f))
        with io.open(os.path.join(man_root, fix_run, "01_fixture.json"), "w",
                     encoding="utf-8", newline="\n") as f:
            json.dump({"git_metadata_captured_before_stripping": {
                "git_head_subject": "9.9.9-FIXTURE.00000001",
                "git_head_commit": "0" * 40,
                "git_commit_date": "2999-01-01T00:00:00+00:00"}}, f, indent=1)

        target_file = "aegs_avenger_stalker.json"
        tp = os.path.join(fix, "ships", target_file)
        rec = json.load(io.open(tp, encoding="utf-8"))
        target_uuid = rec["UUID"]
        old_crew = rec.get("Crew")
        rec["Crew"] = (old_crew or 0) + 7
        with io.open(tp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)

        out2 = os.path.join(tmp, "planted")
        r = run_diff(base, fix, out2, man_root)
        check(r.returncode == 0, "the tool ran on the planted fixture",
              r.stderr.strip()[:160])
        ch = load(out2, "ships_changed.json") or []
        check(len(ch) == 1, "exactly ONE ship is reported changed",
              "%d reported" % len(ch))
        if len(ch) == 1:
            e = ch[0]
            check(e["id"] == target_uuid, "and it is the right ID",
                  "%s vs %s" % (e["id"], target_uuid))
            check(len(e["changes"]) == 1, "and exactly ONE field on it",
                  "%d fields" % len(e["changes"]))
            if len(e["changes"]) == 1:
                c = e["changes"][0]
                check(c["field"] == "Crew", "and it names the right field",
                      c["field"])
                check(c["from"] == old_crew and c["to"] == (old_crew or 0) + 7,
                      "and reports the right before and after",
                      "%s -> %s" % (c["from"], c["to"]))
        check(len(load(out2, "ships_added.json") or []) == 0
              and len(load(out2, "ships_removed.json") or []) == 0,
              "and nothing is reported added or removed")

        # ---------- 2b. THE SUBJECT GATE, IN THE DIRECTION IT EXISTS FOR ----
        #
        # build_patch_diff.py refuses to diff a side it cannot name down to the
        # build number: "a diff whose sides are not named down to the build
        # number is not evidence of anything". That refusal had NEVER BEEN RUN.
        # Before this, `git_head_subject` appeared exactly once in this file -
        # in the fixture that PROVIDES it - and there was not one case anywhere
        # asserting a non-zero exit. The gate looked right, and looking right is
        # not having been run.
        #
        # Flagged in S11 of WORKORDER_the-4-10-pull as "not checked by anyone".
        print("\n--- 2b. the build-subject gate refuses a side it cannot name ---")
        man_bad = os.path.join(tmp, "manifests_nosubject")
        os.makedirs(os.path.join(man_bad, fix_run))
        os.makedirs(os.path.join(man_bad, BASE_RUN))
        for f in os.listdir(real_man):
            if f.endswith(".json"):
                shutil.copy(os.path.join(real_man, f),
                            os.path.join(man_bad, BASE_RUN, f))
        # Same manifest as the passing fixture, with the ONE field removed.
        with io.open(os.path.join(man_bad, fix_run, "01_fixture.json"), "w",
                     encoding="utf-8", newline="\n") as f:
            json.dump({"git_metadata_captured_before_stripping": {
                "git_head_commit": "0" * 40,
                "git_commit_date": "2999-01-01T00:00:00+00:00"}}, f, indent=1)
        rbad = run_diff(base, fix, os.path.join(tmp, "nosubject"), man_bad)
        check(rbad.returncode != 0,
              "a manifest with no git_head_subject is REFUSED",
              "exit %d - the gate did not fire, and a diff can be published "
              "with a side it cannot name" % rbad.returncode)
        check("git_head_subject" in (rbad.stdout + rbad.stderr),
              "and the refusal says which field was missing",
              (rbad.stdout + rbad.stderr).strip()[-160:])
        check(not os.path.exists(os.path.join(tmp, "nosubject",
                                              "ships_changed.json")),
              "and it wrote nothing - refusing after writing is not refusing")

        # ------------------------------------------- 3. a rename is not a swap
        print("\n--- 3. a rename is the same ship, not a removal plus an "
              "addition ---")
        rec2 = json.load(io.open(tp, encoding="utf-8"))
        rec2["Crew"] = old_crew
        old_name = rec2.get("Name")
        rec2["Name"] = "Totally Different Marketing Name"
        with io.open(tp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rec2, f, indent=1, ensure_ascii=False)
        out3 = os.path.join(tmp, "renamed")
        run_diff(base, fix, out3, man_root)
        add3 = load(out3, "ships_added.json") or []
        rem3 = load(out3, "ships_removed.json") or []
        ch3 = load(out3, "ships_changed.json") or []
        check(len(add3) == 0 and len(rem3) == 0,
              "a renamed ship is NOT reported as removed and re-added - the "
              "join is on UUID", "+%d -%d" % (len(add3), len(rem3)))
        check(len(ch3) == 1 and ch3[0]["id"] == target_uuid
              and any(c["field"] == "Name" for c in ch3[0]["changes"]),
              "it is reported as the same ship with a changed Name",
              "%d changed" % len(ch3))

        # ------------------------- 4. a new field is a schema change, not a patch
        print("\n--- 4. a field upstream never emitted is a SCHEMA change ---")
        rec3 = json.load(io.open(tp, encoding="utf-8"))
        rec3["Name"] = old_name
        rec3["SomeFieldUpstreamNeverEmittedBefore"] = 42
        with io.open(tp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rec3, f, indent=1, ensure_ascii=False)
        out4 = os.path.join(tmp, "schema")
        run_diff(base, fix, out4, man_root)
        ch4 = load(out4, "ships_changed.json") or []
        sc4 = load(out4, "ships_schema_changes.json") or []
        check(len(ch4) == 0,
              "it is NOT counted as the game changing something",
              "%d reported as changed" % len(ch4))
        check(len(sc4) == 1
              and any(c["field"] == "SomeFieldUpstreamNeverEmittedBefore"
                      for c in sc4[0]["schema_changes"]),
              "it is reported separately as a schema change, with its reason",
              "%d schema entries" % len(sc4))

        print("\n" + "=" * 66)
        if failures:
            print("FAILED: %d of %d" % (len(failures), passed + len(failures)))
            for f in failures[:10]:
                print("  " + f)
            return 1
        print("PASSED: %d assertions against known answers." % passed)
        if SELFTEST:
            print("\n*** --self-test inverts every expectation, so a PASS here "
                  "means the assertions do not actually test anything. ***")
            return 1
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
