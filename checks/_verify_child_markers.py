# -*- coding: utf-8 -*-
"""Rule 12 control on C1/C2 - a gun inside a turret inherits its turret.

RULE16: UNPROVEN - the BEFORE state is this same builder run with
CC_NO_INHERIT=1, so both sides of every comparison come from one
program. A defect in the part they share appears identically in both and
cancels. The pinned four and the eligibility rule are stated here rather
than read out of the build, and they are the independent half; the
population is not.

THE DEFECT
==========
The placer works from `ship_mounts.json`, a flat list of TOP-LEVEL ports. The
ship page lists the ports a reader can change, and on a turreted hull those are
the CHILDREN. On the Aegis Retaliator the placer produced twenty positions and
the page asked for `turret_left`, `turret_right` and `hardpoint_class_2`. Four
markers survived - the countermeasure launchers, the only ports on both sides -
so a visitor saw four dots on a torpedo bomber with five manned turrets, and
Sleven filed it as "hardpoints not set up".

WHAT THIS CONTROL CHECKS, AND WHAT IT DOES NOT
==============================================
It reads the SHIPPED `loadout_marker.gen.js` and compares it against the BEFORE
state, captured by re-running the real build with CC_NO_INHERIT=1. It therefore
verifies the marker table the site actually carries. It does NOT re-execute the
builder, so it cannot prove the builder would produce this table again from
scratch - a build that changed the table would be caught here on the next run,
which is the point at which it matters. Said plainly rather than implied.

THE ELIGIBILITY RULE IS PART OF THE ANSWER (C2)
===============================================
Only physically mountable ports get a marker: the bench types in MARKABLE -
weapons, turrets, missile and bomb racks, mining and salvage heads, tractor
beams. A target selector is not a place on the ship and a weapon regen pool is
not a place on the ship. Coverage is reported over ELIGIBLE ports, never over
total ports, because a coverage number inflated with regen pools is a worse
answer than four honest markers.

PROVEN AGAINST KNOWN-BAD INPUT:
    --mutate-drop-children  every inherited marker is removed, which is the
                            state Sleven found. The Retaliator falls to 4.
    --mutate-stack          two markers on one hull are given identical
                            coordinates - the failure mode inheritance
                            creates, and the one C3 names.
    --mutate-move-pinned    PortId 23 is nudged by 0.00001, breaking a marker
                            that was correct before this work.
    --self-test             inverts an expectation.
Each must exit non-zero.

Rule 15: every open states its encoding.

Usage: venv/Scripts/python.exe checks/_verify_child_markers.py
       [--self-test] [--mutate-drop-children] [--mutate-stack]
       [--mutate-move-pinned]
"""
import argparse
import io
import json
import os
import re
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "testing", "_src")
AFTER = os.path.join(SRC, "loadout_marker.gen.js")
# THIS SNAPSHOT GOES STALE EVERY TIME THE OVERLAY MOVES, and that is a
# property of the design rather than an accident. The BEFORE state is this
# build with CC_NO_INHERIT=1, so it captures a moment; C1 regenerates the
# client overlay most days, and every hull that gains CIG coordinates then
# reads as "moved" against a snapshot taken before it did.
#
# RE-TAKEN AGAIN 2026-08-29, and this one was a REMOVAL rather than a
# gain. Ten ships were drawing every hardpoint dot in a heap the size of a
# cockpit, labelled `cig` - C1 found it by photographing all 295 ships, not
# by a check, because containment, mirror, provenance and census all passed
# on a heap. The placement now refuses a model it cannot orient, and those
# hulls' CIG markers are gone on purpose.
#
# THE LIST WAS READ BEFORE THE SNAPSHOT, which is the condition C1 set:
# 14 distinct hulls, every one of them from the orientation-refused set -
# Tiburon, Khartu-al, San'tok.yai, Pitbull, Basher, Railen, Reliant Kore,
# Starlite, 600i Executive, M80, both Auroras, Hermes, Mantis. No other
# ship appeared. If one had, that would have been the finding rather than
# the baseline.
#
# Re-taken 2026-08-28 after the Vanduul Glaive gained 8 CIG-positioned
# markers - previously one of the refused asymmetric hulls, so the movement
# was the pipeline working. The pinned four were checked FIRST and all four
# still held, which is the condition Sleven set on 2026-08-27 for taking a
# snapshot at all.
#
# THE DURABLE FIX IS TO GENERATE THE BEFORE STATE INSIDE THE CONTROL rather
# than to keep re-taking it. That costs a full no-inherit build per run -
# about 90 seconds - and it removes the treadmill and every chance a manual
# re-take bakes in something wrong. Not done here because it changes what
# the control costs the sweep, and that is a decision rather than a fix.
# THE FIXTURE LIVES WITH THE CONTROL NOW (2026-08-30).
#
# It was data-layer/derived/holo-hardpoints/loadout_marker.pre-C1-20260829.js,
# a directory C1 claimed on 2026-08-29. That put this control behind an edit
# somebody else had to make: every time the ship data moved, keeping the suite
# green and rule 14 pulled in opposite directions. The old file is untouched
# where it is.
#
# Re-taken on purpose after the 4.10 pull, with what moved recorded in
# checks/_fixtures_markers/README.md and the pinned four checked first.
BEFORE = os.path.join(HERE, "_fixtures_markers", "loadout_marker.baseline.js")

# C3's pinned four - the Retaliator's countermeasure launchers, the only ports
# that already had markers before any of this work and therefore the ones a fix
# must not quietly move.
#
# RE-PINNED 2026-08-27, ON SLEVEN'S WORD, and the old values are kept here
# rather than dropped because a pin nobody can audit is not a pin:
#
#     was  23 [-0.03755, -0.02334, -0.95564]   now  23 [-0.15708, -0.06014, 0.55639]
#          24 [ 0.053,   -0.00648, -0.97809]        24 [-0.17993, -0.06014, 0.55639]
#          39 [ 0.01037, -0.0012,  -0.98118]        39 [ 0.15711, -0.06014, 0.55639]
#          40 [-0.00836,  0.01415, -0.96836]        40 [ 0.1799,  -0.06014, 0.55639]
#
# The old four were derived from the mounts' NAMES: clustered near z=-0.97 with
# no mirror symmetry between them. The new four come from CIG's own transforms
# and are a clean mirrored quad - 23 against 39 at +/-0.157, 24 against 40 at
# +/-0.180, identical y and z across all four.
#
# THAT SYMMETRY IS EVIDENCE, NOT PROOF, and it is not what authorised this.
# Sleven did, in as many words: "the retaliator quad is right, re-baseline it".
# Recorded so the next reader knows this pin rests on a decision rather than on
# a measurement that could be re-derived.
PINNED = {"23": [-0.15708, -0.06014, 0.55639],
          "24": [-0.17993, -0.06014, 0.55639],
          "39": [0.15711, -0.06014, 0.55639],
          "40": [0.1799, -0.06014, 0.55639]}

# C3 names these by name: the other ships Sleven reported.
BY_NAME = ["Aegis Retaliator", "Aegis Sabre Peregrine", "Anvil Ballista",
           "Anvil Ballista Dunestalker", "Anvil Ballista Snowblind"]

FAILS, CHECKS = [], [0]


def ck(label, got, want):
    CHECKS[0] += 1
    ok = got == want
    if not ok:
        FAILS.append("%s: got %r, want %r" % (label, got, want))
    print("  %-64s %s" % (label, "ok" if ok else "FAIL got=%r want=%r"
                          % (got, want)))


def rd(p):
    with io.open(p, "r", encoding="utf-8") as fh:
        return fh.read()


def marks(path):
    m = re.search(r"LOADOUT_MARK=(\{.*\});", rd(path), re.S)
    if not m:
        sys.exit("could not read LOADOUT_MARK out of %s. Reported as NOT "
                 "PERFORMED rather than as a result." % path)
    return json.loads(m.group(1))


def bench():
    lo = rd(os.path.join(SRC, "loadout_data.gen.js"))

    def g(name):
        mm = re.search(r"^const %s=(.*);$" % name, lo, re.M)
        if not mm:
            sys.exit("could not read %s. NOT PERFORMED." % name)
        return json.loads(mm.group(1))
    return g("LOADOUT_SHIPS"), g("LOADOUT_HP"), g("LOADOUT_TYPES")


# ---------------------------------------------------------------------------
# THE THREE DECLARED EXCEPTIONS - C1's fore/aft containment gate, 2026-08-29
#
# WHY A DECLARATION AND NOT A RE-TAKEN BASELINE. Re-taking the snapshot would
# make this control pass by making it forget, which is precisely the failure
# `_verify_marker_census.py` exists to prevent. A baseline re-taken quietly and
# one re-taken on purpose are indistinguishable six weeks later. These three
# print on every run, so the change stays visible instead of becoming invisible.
#
# WHAT HAPPENED. The acceptance test in `build_hardpoint_placement.py` only ever
# checked two of three axes - a mount could leave the hull fore or aft and
# nothing watched. Fore/aft is now tested at the same 6% margin as the others.
# Across 26,273 mounts it moved exactly three that are DRAWN, and this control
# is what proves that number: section 6 finds 244 hulls changed and names these
# three, with the four pinned negative controls holding.
#
# EACH ENTRY DECLARES THE WHOLE TRANSITION, NOT JUST THE PORT. A bare list of
# port names would excuse ANY future change to those three mounts - including a
# second, real regression landing on the same port. The before and after
# positions are both asserted, so the exception covers this movement and no
# other.
#
# AND A DECLARATION THAT STOPS FIRING IS ITSELF A FAILURE, below. C1's census
# says it best: a declaration that outlives its reason is how a real loss gets
# waved through. REMOVE THESE when the snapshot is next re-taken for an
# unrelated reason - at that point the movement is in the baseline and the
# entries are fiction.
# EMPTY SINCE THE 2026-08-30 RE-TAKE, AND THAT IS THE DESIGN WORKING.
#
# This held three declarations for C1's fore/aft withholding - BANU_Defender
# 50 and 51 removed, MISC_Hull_C 34 demoted to est. The comment above them said:
# "REMOVE THESE when the snapshot is next re-taken for an unrelated reason - at
# that point the movement is in the baseline and the entries are fiction."
#
# That moment arrived. The 4.10 pull forced a re-take, the withholding is now
# part of the baseline, and the control's own "a declaration nothing fires is
# fiction" assertion would have failed on all three. It predicted its own
# retirement and the check that enforces it is unchanged.
#
# The declarations are not lost: what they recorded is in
# checks/_fixtures_markers/README.md and in the commit that made them.
DECLARED = {}


MARKABLE = {"WeaponGun", "Turret", "MissileLauncher", "WeaponDefensive",
            "WeaponMining", "BombLauncher", "SalvageHead", "TractorBeam",
            "EMP", "Missile", "Bomb"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mutate-drop-children", action="store_true")
    ap.add_argument("--mutate-stack", action="store_true")
    ap.add_argument("--mutate-move-pinned", action="store_true")
    a = ap.parse_args(argv)

    if not os.path.exists(BEFORE):
        print("NOT PERFORMED - no pre-C1 snapshot at %s, so there is nothing "
              "to measure the rise against." % os.path.relpath(BEFORE, REPO))
        print("Re-create it with:  CC_NO_INHERIT=1 venv/Scripts/python.exe "
              "testing/_src/build_deploy.py")
        print("Reported as NOT PERFORMED, never as passed.")
        return 2

    was, now = marks(BEFORE), marks(AFTER)
    LS, LHP, LT = bench()

    if a.mutate_drop_children:
        now = {k: [r for r in v if ".loadout." not in str(r[0])]
               for k, v in now.items()}
        now = {k: v for k, v in now.items() if v}
        print("*** MUTATED: every inherited marker removed - the state Sleven "
              "found. ***\n")
    if a.mutate_stack:
        k = "AEGS_Retaliator"
        if k not in now or len(now[k]) < 2:
            print("MUTATION DID NOT APPLY - the Retaliator has fewer than two "
                  "markers, so nothing can be stacked. The run proves nothing.")
            return 1
        now[k] = list(now[k])
        now[k][1] = [now[k][1][0]] + list(now[k][0][1:])
        print("*** MUTATED: two Retaliator markers share coordinates - the "
              "failure mode inheritance creates. ***\n")
    if a.mutate_move_pinned:
        k = "AEGS_Retaliator"
        # THE TAIL IS CARRIED THROUGH. Rows gained a fifth element on
        # 2026-08-27 (Q9's provenance token); rebuilding a row as exactly four
        # would silently drop it and this mutator would be testing a shape the
        # build no longer emits.
        now[k] = [([r[0], round(r[1] + 0.00001, 5)] + list(r[2:])
                   if str(r[0]) == "23" else r) for r in now[k]]
        print("*** MUTATED: PortId 23 moved by 0.00001 - a marker that was "
              "correct before this work. ***\n")

    nm = {c: (LS.get(c) or {}).get("n") or c for c in now}

    print("1. THE RETALIATOR RISES (C3, load-bearing)")
    r_was = len(was.get("AEGS_Retaliator") or [])
    r_now = len(now.get("AEGS_Retaliator") or [])
    print("     %d markers before, %d now" % (r_was, r_now))
    ck("the Retaliator gained markers", r_now > r_was, True)
    gained = {str(x[0]) for x in now.get("AEGS_Retaliator") or []} - \
             {str(x[0]) for x in was.get("AEGS_Retaliator") or []}
    rec = LS.get("AEGS_Retaliator") or {}
    pname = {str(s["p"]): LHP[s["h"]] for s in rec.get("slots", [])}
    print("     ports that gained a marker:")
    for pid in sorted(gained):
        print("        %-26s %s" % (pid, pname.get(pid, "?")))
    ck("and every gained port is a real port on the ship",
       all(p in pname for p in gained), True)

    print("\n2. NEGATIVE CONTROL - the four that already worked did not move")
    by = {str(x[0]): [x[1], x[2], x[3]] for x in now.get("AEGS_Retaliator") or []}
    for pid, want in PINNED.items():
        ck("PortId %-3s holds its exact position" % pid, by.get(pid), want)

    print("\n3. NO TWO MARKERS ON A HULL SHARE COORDINATES (C3, load-bearing)")
    stacked, worst = 0, []
    for c, rows in now.items():
        seen = {}
        for x in rows:
            key = (round(x[1], 5), round(x[2], 5), round(x[3], 5))
            if key in seen:
                stacked += 1
                if len(worst) < 6:
                    worst.append("%s: %s and %s at %s"
                                 % (nm.get(c, c), seen[key], x[0], key))
            seen[key] = x[0]
    print("     %d hulls, %d markers checked"
          % (len(now), sum(len(v) for v in now.values())))
    ck("no marker sits on top of another", stacked, 0)
    for w in worst:
        print("        %s" % w)

    print("\n4. ELIGIBILITY (C2) - the rule, and what it excludes")
    tot = elig = 0
    for c, rec in LS.items():
        if c not in now:
            continue
        for s in rec.get("slots", []):
            tot += 1
            if (LT.get(s["t"]) or {}).get("t") in MARKABLE:
                elig += 1
    print("     rule: a port is eligible only if its type is one of %d "
          "physically mountable kinds" % len(MARKABLE))
    print("     across the %d marked hulls: %d ports total, %d eligible, "
          "%d excluded" % (len(now), tot, elig, tot - elig))
    ck("the eligibility rule actually excludes something", elig < tot, True)
    ck("and it does not exclude everything", elig > 0, True)

    print("\n5. COVERAGE OVER ELIGIBLE PORTS, BEFORE AND AFTER")

    def cover(table):
        out = {}
        for c, rows in table.items():
            rec = LS.get(c)
            if not rec:
                continue
            e = sum(1 for s in rec.get("slots", [])
                    if (LT.get(s["t"]) or {}).get("t") in MARKABLE)
            if e:
                out[c] = (len(rows), e)
        return out

    cw, cn = cover(was), cover(now)
    fw = sorted(v[0] / float(v[1]) for v in cw.values())
    fn = sorted(v[0] / float(v[1]) for v in cn.values())
    print("     before: %d hulls, median %.0f%%, range %.0f%%-%.0f%%"
          % (len(fw), 100 * statistics.median(fw), 100 * fw[0], 100 * fw[-1]))
    print("     after : %d hulls, median %.0f%%, range %.0f%%-%.0f%%"
          % (len(fn), 100 * statistics.median(fn), 100 * fn[0], 100 * fn[-1]))
    ck("median coverage rose",
       statistics.median(fn) > statistics.median(fw), True)
    ck("no hull's coverage went DOWN",
       [c for c in cw if c in cn and cn[c][0] < cw[c][0]], [])
    ck("and no hull exceeds 100% of its eligible ports",
       [c for c in cn if cn[c][0] > cn[c][1]], [])
    print("     the ships Sleven reported, by name:")
    byname = {(LS.get(c) or {}).get("n"): c for c in cn}
    for want in BY_NAME:
        c = byname.get(want)
        if not c:
            ck("%s is in the coverage report" % want, False, True)
            continue
        b = cw.get(c, (0, cn[c][1]))
        print("        %-30s %2d of %2d  ->  %2d of %2d"
              % (want, b[0], b[1], cn[c][0], cn[c][1]))

    print("\n6. NEGATIVE CONTROL - inheritance only ever ADDS, and only where "
          "there is a parent")
    # THE FIRST VERSION OF THIS TESTED A POPULATION OF THREE.
    # It looked for hulls with no nested ports ANYWHERE and found three, so
    # "not one of them changed" was true of almost nothing. The invariant the
    # order is actually after - "if a single-seat fighter's marker count moves,
    # the inheritance is firing where there is no parent-child relationship at
    # all" - is better tested the other way round: take every hull that DID
    # change and require each one to have had somewhere for a child to come
    # from. That population is the whole fleet.
    changed, groundless, lost = [], [], []
    seen_declared = set()
    for c in was:
        if c not in now:
            lost.append(c)
            continue
        before = {str(x[0]): [x[1], x[2], x[3]] for x in was[c]}
        after = {str(x[0]): [x[1], x[2], x[3]] for x in now[c]}
        for pid, xyz in before.items():
            if after.get(pid) != xyz:
                d = DECLARED.get((c, pid))
                # The declaration must match the transition that ACTUALLY
                # happened, both ends of it. A port name alone would excuse a
                # second, real regression landing on the same mount.
                if d and d["was"] == xyz and d["now"] == after.get(pid):
                    seen_declared.add((c, pid))
                    continue
                lost.append("%s:%s" % (nm.get(c, c), pid))
        if before != {k: v for k, v in after.items() if k in before} \
                or len(after) != len(before):
            changed.append(c)
            rec = LS.get(c) or {}
            nested = any("." in str(s["p"]) for s in rec.get("slots", [])
                         if (LT.get(s["t"]) or {}).get("t") in MARKABLE)
            if not nested:
                groundless.append(nm.get(c, c))
    print("     %d hulls changed, %d unchanged"
          % (len(changed), len(was) - len(changed)))

    # PRINTED EVERY RUN, NOT ONLY WHEN SOMETHING IS WRONG. The whole argument
    # for declaring these instead of re-taking the baseline is that they stay
    # visible; a list that only appears on failure is a baseline with extra
    # steps.
    print("     %d DECLARED exception(s) - the fore/aft withholding, "
          "2026-08-29:" % len(DECLARED))
    for (c, pid), d in sorted(DECLARED.items()):
        print("       %-14s port %-3s %s"
              % (c, pid, "REMOVED" if d["now"] is None
                 else "moved %s -> %s, and demoted to est"
                      % (d["was"][2], d["now"][2])))
        print("         %s" % d["why"])
    stale = sorted("%s:%s" % k for k in DECLARED if k not in seen_declared)

    ck("*** every marker that existed before is still there, unmoved, except "
       "the %d declared above ***" % len(DECLARED),
       lost, [])
    # A DECLARATION THAT OUTLIVES ITS REASON IS HOW A REAL LOSS GETS WAVED
    # THROUGH - C1's census says it in those words and it is just as true here.
    # If one of these stops firing, the movement has been absorbed into the
    # snapshot and the entry is now excusing nothing while looking like
    # oversight.
    ck("and every declared exception actually happened - a declaration nothing "
       "fires is fiction",
       stale, [])
    ck("no hull changed without having a nested eligible port to inherit from",
       groundless, [])
    ck("and the population that proves it is the fleet, not a handful",
       len(changed) > 50, True)

    flat = [c for c in was if c in now
            and (LS.get(c) or {}).get("slots")
            and all("." not in str(s["p"])
                    for s in LS[c]["slots"]
                    if (LT.get(s["t"]) or {}).get("t") in MARKABLE)]
    # POSITIONS ONLY, not whole rows. The subject here is "these markers did
    # not MOVE", and a row carries more than a position: Q9 added a fifth
    # element on 2026-08-27 naming where the dot came from. Comparing whole
    # rows made all eight of these hulls look moved the moment that field
    # arrived, which is a format change reported as a fleet regression.
    # A genuine change of position still fails, because the position is what is
    # compared.
    def _pos_only(rows):
        return sorted(json.dumps(list(r[:4])) for r in rows)

    moved = [c for c in flat if _pos_only(was[c]) != _pos_only(now[c])]
    print("     and the %d hulls whose eligible ports are ALL top-level:"
          % len(flat))
    ck("none of them moved at all", moved, [])

    if a.self_test:
        print("\nSELF-TEST - one expectation inverted on purpose. Must exit 1.")
        ck("inverted: the Retaliator must NOT have gained markers",
           r_now > r_was, False)

    print("\n%d assertions, %d failed" % (CHECKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL %s" % f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
