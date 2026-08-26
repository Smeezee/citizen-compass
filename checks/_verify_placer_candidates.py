# -*- coding: utf-8 -*-
"""Rule 12 control on P1 - the placer's input must not come from its output.

THE DEFECT THIS GUARDS, STATED EXACTLY
======================================
`build_matched.py` seeded its candidate set from `hardpoints_fleet.json`, which
is the placer's OUTPUT, and then widened it with `if name in model_of: continue`
- which skipped every seeded hull. The set was monotonically closed: 235 hulls
had decoded geometry, 175 were ever considered, and all 175 traced to the
2026-08-10 sandbox run. Cutlass Black arrived on 2026-08-24 with 17 mounts and
could not reach the placer. Nothing reported the exclusion.

WHY THE OBVIOUS CHECK WOULD BE WORTHLESS
========================================
Asserting "the candidate count is 186" pins a number. It would pass on a build
that still read the output and simply had a bigger output, and it would pass on
a build that hard-coded 186 names. It proves nothing about the DIRECTION of the
join, which is the entire finding.

So the load-bearing test runs the real derivation TWICE - once against the real
`hardpoints_fleet.json`, once against an EMPTY one - and requires the two
candidate sets to be IDENTICAL, entry for entry. If any part of the input is
still drawn from the output, deleting the output changes the input and this
goes red. It cannot be satisfied by a build that reads the output for anything
the candidate set depends on.

THE NEGATIVE CONTROL IS THE OTHER HALF and it is what the order calls
load-bearing: widening the input must not move a single existing marker. The
169 hulls placed before this change are compared against the pre-P1 snapshot,
hardpoint by hardpoint. The answer must be zero.

PROVEN AGAINST KNOWN-BAD INPUT:
    --mutate-oldrules  restores the narrow slug-only resolution the closed
                       loop shipped with, on a real copy of the real file.
                       Cutlass Black drops out of the candidate set and
                       section 2 goes red.
    --self-test        inverts an expectation. Must exit 1.

ONE MUTATION I COULD NOT MAKE FIRE, REPORTED RATHER THAN QUIETLY DROPPED.
Putting the fleet SEED back - `model_of` starting from hardpoints_fleet
.json - changes nothing observable on today's data, so no behavioural test
can tell the two builds apart. The reason is the point: all 178 recorded
hulls resolve, under the new rules, to exactly the model file they were
already placed against, so seeding from them adds no member the derivation
would not produce anyway. That is the evidence that removing the seed was
safe, and it is ALSO the reason a mutation restoring it stays green. The
invariant is guarded instead by the planted ghost in section 1, which
catches any FUTURE divergence between the cache and the derivation. Rule
12: a mutation that cannot fail is not a mutation, so it is named here
rather than shipped as a passing flag.

Rule 15: every open states its encoding.

Usage: venv/Scripts/python.exe checks/_verify_placer_candidates.py
       [--self-test] [--mutate-oldrules]
"""
import argparse
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
HOLO = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints")
BUILDER = os.path.join(HOLO, "build_matched.py")
FLEET = os.path.join(HOLO, "hardpoints_fleet.json")
BEFORE = os.path.join(HOLO, "hardpoints_fleet.pre-P1-20260826.json")

FAILS, CHECKS = [], [0]


def ck(label, got, want):
    CHECKS[0] += 1
    ok = got == want
    if not ok:
        FAILS.append("%s: got %r, want %r" % (label, got, want))
    print("  %-62s %s" % (label, "ok" if ok else "FAIL got=%r want=%r"
                          % (got, want)))


def rj(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_builder(path, name):
    """Import the builder, then PIN ITS INPUT PATHS BACK TO THE REAL ONES.

    A mutated copy lives in a temp directory, and the builder derives MOUNTS,
    SNAPDIR and the geometry directory from its own __file__. Without this the
    mutated run dies on "MISSING INPUT: <temp>/ship_mounts.json" and exits 1 -
    which LOOKS like the mutation being caught and is nothing of the kind. It
    happened on the first run of this control: the mutation reported red
    without a single assertion having executed. A mutation that fails for the
    wrong reason proves the same amount as no mutation at all.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.HERE = HOLO
    mod.REPO = REPO
    mod.MOUNTS = os.path.join(HOLO, "ship_mounts.json")
    mod.SNAPDIR = os.path.join(REPO, "data-layer", "external-sources",
                               "scunpacked-data", "snapshots")
    for attr, path_ in (("MOUNTS", mod.MOUNTS), ("SNAPDIR", mod.SNAPDIR)):
        if not os.path.exists(path_):
            sys.exit("the control cannot point the builder at a real %s (%s). "
                     "Reported as NOT PERFORMED rather than as a result."
                     % (attr, path_))
    return mod


def run_builder(mod, out, fleet_path):
    """Drive the real main() with argv, with FLEET pointed where we say.

    Patching the module attribute rather than the file on disk, so the code
    under test is the code that ships.
    """
    mod.FLEET = fleet_path
    argv = sys.argv
    buf = io.StringIO()
    stdout = sys.stdout
    try:
        sys.argv = ["build_matched.py", "--out", out]
        sys.stdout = buf
        mod.main()
    finally:
        sys.argv = argv
        sys.stdout = stdout
    return rj(out)["matched"], buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mutate-oldrules", action="store_true")
    a = ap.parse_args(argv)

    tmp = tempfile.mkdtemp(prefix="cc_p1_")
    builder_path = BUILDER

    if a.mutate_oldrules:
        # THE REAL FILE, COPIED AND BROKEN THE WAY IT USED TO BE BROKEN.
        # Not a simulation of the defect - the defect, re-planted in the code
        # under test, so a run that still passes has proved the check blind.
        #
        # The narrow rule is what shipped inside the closed loop: the slug's
        # stem, that stem title-cased, and the whole slug with dashes turned
        # into underscores. It resolved 6 hulls beyond the ones already placed.
        src = io.open(BUILDER, encoding="utf-8").read()
        needle = "        for rule, k in keys:"
        if needle not in src:
            print("MUTATION DID NOT APPLY - resolve_model is not where this "
                  "mutator looks, so the run proves nothing.")
            return 1
        src = src.replace(
            needle,
            "        slug_ = rec.get('slug') or ''\n"
            "        stem_ = slug_.split('-', 1)[-1].replace('-', '_')\n"
            "        for cand in (stem_, stem_.title(),\n"
            "                     slug_.replace('-', '_')):\n"
            "            if cand in have_geo:\n"
            "                return cand, 'narrow-slug'\n"
            "        return None, 'narrow rule found nothing'\n"
            "        for rule, k in keys:", 1)
        builder_path = os.path.join(tmp, "build_matched_mutated.py")
        shutil.copy(BUILDER, builder_path)
        io.open(builder_path, "w", encoding="utf-8", newline="").write(src)
        print("*** MUTATED: resolution is back to the narrow slug-only rule "
              "the closed loop shipped with. ***\n")

    mod = load_builder(builder_path, "cc_build_matched_under_test")

    # An empty fleet. Not a missing file - the builder is entitled to require
    # its inputs to exist; what it must not do is take CONTENT from this one.
    empty = os.path.join(tmp, "empty_fleet.json")
    with io.open(empty, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({}, fh)

    # A GHOST IN THE OUTPUT. This is the sharp instrument, and the
    # empty-fleet test on its own is not.
    #
    # Emptying the fleet turns out NOT to change the candidate set even
    # with the old seeding restored - because the new resolver reproduces
    # every one of the 169 recorded models exactly, so seeding from them
    # adds nothing today. A test that cannot tell the two builds apart is
    # not testing the thing it claims to. Found by running
    # --mutate-reseed and watching it pass.
    #
    # So the fleet is given an entry NO resolver could ever produce: a
    # ship name that is not in ship_mounts.json at all. If the output can
    # put a candidate into the input, this ghost appears. If the join has
    # really been inverted, it cannot.
    GHOST = "__ghost_hull_that_is_not_a_ship__"
    ghost_fleet = os.path.join(tmp, "ghost_fleet.json")
    gf = dict(rj(FLEET))
    gf[GHOST] = {"maker": "None", "bare": "Ghost",
                 "model": "Hammerhead.glb", "hardpoints": []}
    with io.open(ghost_fleet, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(gf, fh)

    print("1. THE JOIN'S DIRECTION - can the OUTPUT put a ship into the "
          "INPUT?")
    real, real_log = run_builder(mod, os.path.join(tmp, "real.json"), FLEET)
    void, void_log = run_builder(mod, os.path.join(tmp, "void.json"), empty)
    ghost, _ = run_builder(mod, os.path.join(tmp, "ghost.json"), ghost_fleet)
    print("     with the real hardpoints_fleet.json : %d candidates" % len(real))
    print("     with an EMPTY hardpoints_fleet.json : %d candidates" % len(void))
    print("     with a GHOST planted in the output  : %d candidates" % len(ghost))
    ck("a hull invented in the OUTPUT does not become an input candidate",
       GHOST in ghost, False)
    ck("and planting it changes nothing else either", set(ghost), set(real))
    ck("the candidate SET does not change when the output is emptied",
       set(real) == set(void), True)
    only_real = sorted(set(real) - set(void))
    if only_real:
        print("     candidates that exist ONLY because of the previous run:")
        for n in only_real[:10]:
            print("        %s" % n)
    ck("no candidate exists only because it was placed before",
       len(only_real), 0)
    differing = [k for k in real
                 if k in void
                 and json.dumps(real[k], sort_keys=True)
                 != json.dumps(void[k], sort_keys=True)]
    ck("and no candidate's CONTENT is drawn from the output either",
       len(differing), 0)
    if differing:
        print("     differing entries: %s" % ", ".join(differing[:6]))

    print("\n2. THE SET GREW, AND THE SHIP THAT PROVED THE DEFECT IS IN IT")
    ck("the candidate count rose above the closed-loop 175", len(real) > 175,
       True)
    print("     %d candidates (was 175)" % len(real))
    cb = real.get("Cutlass Black")
    ck("Cutlass Black is a candidate", cb is not None, True)
    if cb:
        ck("Cutlass Black brings its 17 mounts", len(cb["mounts"]), 17)
        ck("and resolves to its OWN hull, not a skin of it",
           cb["model"], "Cutlass_Black.glb")

    print("\n3. EVERY REFUSAL IS NAMED - silent exclusion is how this hid for "
          "sixteen days")
    m = re.search(r"rejected\s+: (\d+) ships", real_log)
    ck("the run reports a rejection count", bool(m), True)
    if m:
        n_rej = int(m.group(1))
        print("     %d rejected, %d accepted, %d in ship_mounts.json"
              % (n_rej, len(real), n_rej + len(real)))
        ck("accepted + rejected accounts for every ship with mount data",
           n_rej + len(real), len(mod.read_json(mod.MOUNTS)))
        named = re.findall(r"^    (\S.*?)\s{2,}(no decoded hull|ambiguous)",
                           real_log, re.M)
        ck("refusals are printed by name with a reason, not just counted",
           len(named) > 0, True)

    print("\n4. NEGATIVE CONTROL - widening the input moved no existing marker")
    if not os.path.exists(BEFORE):
        # NOT PERFORMED, NOT FAILED. The snapshot is derived output and is not
        # tracked, so a fresh checkout does not have one - and "the comparison
        # could not be made" is a different statement from "markers moved".
        # Reporting the second when the first is true would be a fabricated
        # finding, which rule 11 forbids in exactly these words.
        print("     NOT PERFORMED - no pre-P1 snapshot at %s, so there is "
              "nothing to compare today's placement against."
              % os.path.relpath(BEFORE, REPO))
        print("     Re-create one by copying hardpoints_fleet.json aside "
              "BEFORE the next placement run.")
        print("     Reported as NOT PERFORMED, never as passed.")
        print("\n%d assertions, %d failed, and the load-bearing negative "
              "control DID NOT RUN" % (CHECKS[0], len(FAILS)))
        shutil.rmtree(tmp, ignore_errors=True)
        return 2
    else:
        was, now = rj(BEFORE), rj(FLEET)
        missing = [k for k in was if k not in now]
        ck("no previously placed hull was lost", len(missing), 0)
        moved, changed = 0, []
        for k, v in was.items():
            if k not in now:
                continue
            if json.dumps(v, sort_keys=True) != json.dumps(now[k],
                                                           sort_keys=True):
                changed.append(k)
                a_ = {h["port"]: h.get("unit") for h in v.get("hardpoints") or []}
                b_ = {h["port"]: h.get("unit")
                      for h in now[k].get("hardpoints") or []}
                moved += sum(1 for p in a_ if a_[p] != b_.get(p))
        print("     %d hulls placed before, %d now" % (len(was), len(now)))
        ck("every one of the previously placed hulls is byte-identical",
           len(changed), 0)
        ck("*** markers that moved ***", moved, 0)
        if changed:
            print("     changed: %s" % ", ".join(changed[:8]))
        ck("and the fleet actually grew", len(now) > len(was), True)

    if a.self_test:
        print("\nSELF-TEST - one expectation inverted on purpose. Must exit 1.")
        ck("inverted: the empty-fleet run must produce a DIFFERENT set",
           set(real) == set(void), False)

    print("\n%d assertions, %d failed" % (CHECKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL %s" % f)
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
