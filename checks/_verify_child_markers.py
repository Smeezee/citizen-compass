# -*- coding: utf-8 -*-
"""Rule 12 control on C1/C2 - a gun inside a turret inherits its turret.

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
BEFORE = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints",
                      "loadout_marker.pre-C1-20260826.js")

# C3's pinned four. These were correct before this work and a fix that moves
# them has broken what worked.
PINNED = {"23": [-0.03755, -0.02334, -0.95564],
          "24": [0.053, -0.00648, -0.97809],
          "39": [0.01037, -0.0012, -0.98118],
          "40": [-0.00836, 0.01415, -0.96836]}

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
        now[k] = [([r[0], round(r[1] + 0.00001, 5), r[2], r[3]]
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
    for c in was:
        if c not in now:
            lost.append(c)
            continue
        before = {str(x[0]): [x[1], x[2], x[3]] for x in was[c]}
        after = {str(x[0]): [x[1], x[2], x[3]] for x in now[c]}
        for pid, xyz in before.items():
            if after.get(pid) != xyz:
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
    ck("*** every marker that existed before is still there, unmoved ***",
       lost, [])
    ck("no hull changed without having a nested eligible port to inherit from",
       groundless, [])
    ck("and the population that proves it is the fleet, not a handful",
       len(changed) > 50, True)

    flat = [c for c in was if c in now
            and (LS.get(c) or {}).get("slots")
            and all("." not in str(s["p"])
                    for s in LS[c]["slots"]
                    if (LT.get(s["t"]) or {}).get("t") in MARKABLE)]
    moved = [c for c in flat if json.dumps(sorted(map(str, was[c])))
             != json.dumps(sorted(map(str, now[c])))]
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
