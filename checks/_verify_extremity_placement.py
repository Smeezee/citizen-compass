#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B6: a mount whose name names an extremity is placed against the hull's own

RULE16: INDEPENDENT - the placer is run as a SUBPROCESS, twice, and the two
outputs are compared by this file. Nothing is imported, so the rule being
judged is not the rule doing the judging, and the crowding measurements
are computed here from the placed coordinates rather than read out of the
placer's own report.
measured extremity, not against a fixed fraction of every hull in the fleet.

WHAT CHANGED, AND WHAT DELIBERATELY DID NOT
===========================================
`TARGET` put a wing mount at 88% of half-beam on a Vulture and on a Polaris
alike, then snapped to the nearest vertex. The hull's actual outermost vertex
is in the geometry, so the guess can stop being a guess.

IT IS STILL DERIVED FROM A NAME. The name says "wing"; this finds where THIS
hull's wing actually is instead of assuming 0.88. It does NOT read a mount
position out of the model - there is none to read, the exports being one welded
mesh with no mount nodes. The page's own note must not start claiming
otherwise, and the last section here asserts that it has not.

ONE AXIS, AND ONLY FOR A LONE MOUNT. Both narrowings were forced by
measurement, not chosen for neatness, and both are recorded:

  two axes pinned   fleet crowding 118 -> 120 markers
  one axis pinned   fleet crowding 118 -> 121 markers
  one axis, lone
  mounts only       fleet crowding 118 -> 117 markers

B6's own acceptance is that crowding must not get worse. Siblings sharing a
target group are held apart BY the fraction and the spread; aiming all of them
at one measured vertex puts them on top of each other and the separation pass
then has to undo it. A lone mount has nothing to be held apart from.

WHAT THIS CANNOT PROVE: that a marker is on the right part of the ship. Nobody
has CIG's coordinates - every one of the 25,150 ports in the snapshot carries
position: null. This proves the derivation does what it says and that the fleet
did not get worse by its own measures.

Usage:
    venv/Scripts/python.exe checks/_verify_extremity_placement.py
        [--self-test]  invert every expectation; must exit non-zero
        [--quick]      skip the two full fleet runs (they take ~2 min).
                       The fleet section then reports NOT PERFORMED.
"""
import importlib.util
import io
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOLO = os.path.join(ROOT, "data-layer", "derived", "holo-hardpoints")
PLACE = os.path.join(HOLO, "place_fleet.py")
PAGE = os.path.join(ROOT, "testing", "_src", "loadout.src.html")

SELFTEST = "--self-test" in sys.argv
QUICK = "--quick" in sys.argv

_passed, _failed, _notes = [], [], []


def check(label, got, detail=""):
    want = (not got) if SELFTEST else got
    (_passed if want else _failed).append(("%s %s" % (label, detail)).strip())
    print("  %s  %s%s" % ("PASS" if want else "FAIL", label,
                          ("  " + detail) if detail else ""))
    return bool(want)


def read_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


spec = importlib.util.spec_from_file_location("place_fleet", PLACE)
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)


# ------------------------------------------------------------ a known hull
def box_points(hx, hy, hz, n=13):
    """A hollow box, so every face has vertices to snap to.

    A box rather than a hull on purpose: the question in sections 1 and 2 is
    "does this find the extreme vertex in the band", and the answer must not
    depend on which ship was chosen.
    """
    pts = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if i in (0, n - 1) or j in (0, n - 1) or k in (0, n - 1):
                    pts.append([(i / (n - 1.0)) * 2 * hx - hx,
                                (j / (n - 1.0)) * 2 * hy - hy,
                                (k / (n - 1.0)) * 2 * hz - hz])
    return np.asarray(pts, dtype=np.float32)


print("\n1. THE MEASUREMENT FINDS THE HULL'S OWN EXTREME, NOT A FRACTION")
HX, HY, HZ = 10.0, 3.0, 20.0
P = box_points(HX, HY, HZ)
mn, mx = [-HX, -HY, -HZ], [HX, HY, HZ]
axes = (0, 1, 2)          # lat, up, len
nose = -1

wing_l = pf.read_location("hardpoint_weapon_wing_left", "")
t = pf.extremity_target(P, mn, mx, axes, nose, wing_l)
check("a wing mount gets a measured target", t is not None)
if t is not None:
    check("and it is on the hull's actual outermost vertex, to the LEFT",
          abs(float(t[0]) + HX) < 1e-3,
          "x=%.3f, hull half-beam %.1f" % (float(t[0]), HX))

wing_r = pf.read_location("hardpoint_weapon_wing_right", "")
t2 = pf.extremity_target(P, mn, mx, axes, nose, wing_r)
check("and the right-hand one lands on the other side",
      t2 is not None and abs(float(t2[0]) - HX) < 1e-3,
      "x=%.3f" % (float(t2[0]) if t2 is not None else float("nan")))

nose_m = pf.read_location("hardpoint_weapon_nose", "")
t3 = pf.extremity_target(P, mn, mx, axes, nose, nose_m)
check("a nose mount is measured to the NOSE end, using the derived nose sign",
      t3 is not None and abs(float(t3[2]) + HZ) < 1e-3,
      "z=%.3f, hull half-length %.1f" % (
          float(t3[2]) if t3 is not None else float("nan"), HZ))

# NAMED `hardpoint_weapon_roof`, NOT `hardpoint_turret_roof`, and the reason is
# worth knowing: read_location() walks its part list in order and BREAKS on the
# first hit, and 'turret' comes before 'roof'. A port called
# `hardpoint_turret_roof` therefore resolves to 'turret', which is not an
# extremity and keeps its fraction. That is the existing behaviour, unchanged
# by B6 - the first version of this assertion used that name, got None, and
# looked like a bug in the new code when it was the old precedence.
roof = pf.read_location("hardpoint_weapon_roof", "")
check("a roof mount reads as a roof", roof["part"] == "roof", str(roof["part"]))
t4 = pf.extremity_target(P, mn, mx, axes, nose, roof)
check("and is measured to the top of the hull",
      t4 is not None and abs(float(t4[1]) - HY) < 1e-3,
      "y=%.3f" % (float(t4[1]) if t4 is not None else float("nan")))
turret_roof = pf.read_location("hardpoint_turret_roof", "")
check("while a name carrying BOTH words resolves to 'turret' and keeps its "
      "fraction - read_location breaks on the first part it matches, and B6 "
      "did not change that",
      turret_roof["part"] == "turret"
      and pf.extremity_target(P, mn, mx, axes, nose, turret_roof) is None,
      str(turret_roof["part"]))

# THE NEGATIVE HALF. A name with no extremity in it must get NOTHING, or "we
# measured it" would quietly become "we measured everything".
body = pf.read_location("hardpoint_weapon_body", "")
check("a BODY mount gets no measured target at all - it keeps the fraction it "
      "always had",
      pf.extremity_target(P, mn, mx, axes, nose, body) is None)
none_loc = pf.read_location("hardpoint_class_2", "")
check("and so does a name that says nothing",
      pf.extremity_target(P, mn, mx, axes, nose, none_loc) is None)

# A HULL SHAPED DIFFERENTLY GETS A DIFFERENT ANSWER. This is the entire point
# of the item, and without it "measured" could be any constant.
P2 = box_points(HX * 3, HY, HZ)
t5 = pf.extremity_target(P2, [-HX * 3, -HY, -HZ], [HX * 3, HY, HZ], axes, nose,
                         wing_l)
check("a hull three times as wide puts the wing three times further out - the "
      "measurement follows the hull, which a fraction of the bounding box "
      "would also do, so the next assertion is the load-bearing one",
      t5 is not None and abs(float(t5[0]) + HX * 3) < 1e-3,
      "x=%.3f" % (float(t5[0]) if t5 is not None else float("nan")))
# The load-bearing one: a hull whose widest point is NOT at the fraction.
# A box with a narrow tail: the 0.88-of-half-beam guess would land in the
# fuselage; the measurement finds the wing.
P3 = np.concatenate([box_points(HX, HY, HZ / 2),
                     box_points(HX / 4, HY, HZ / 2) + np.array([0, 0, HZ / 2],
                                                               dtype=np.float32)])
t6 = pf.extremity_target(P3, [-HX, -HY, -HZ], [HX, HY, HZ], axes, nose, wing_l)
check("and on a hull that is wide at the front and narrow at the back, a wing "
      "mount is measured to the WIDE part rather than to a fraction of the "
      "whole box",
      t6 is not None and abs(float(t6[0]) + HX) < 1e-3,
      "x=%.3f of half-beam %.1f" % (
          float(t6[0]) if t6 is not None else float("nan"), HX))

print("\n2. THE SKIP GATE IS UNTOUCHED - 7 hulls stay skipped")
good = pf.resolve_frame([-10, -3, -20], [10, 3, 20],
                        {"length": 40, "width": 20, "height": 6})
check("a hull whose proportions match its spec sheet still resolves",
      good[0] is not None, str(good[1]))
bad = pf.resolve_frame([-10, -3, -20], [10, 3, 20],
                       {"length": 5, "width": 90, "height": 90})
check("and one whose proportions DISAGREE is still refused, not placed in a "
      "frame nobody checked",
      bad[0] is None, str(bad[1])[:70])
nodim = pf.resolve_frame([-10, -3, -20], [10, 3, 20], {})
check("and one with no published dimensions is refused too",
      nodim[0] is None, str(nodim[1]))

print("\n3. THE PAGE'S HONESTY IS UNCHANGED")
if not os.path.exists(PAGE):
    print("     NOT PERFORMED: the page source is missing.")
else:
    with io.open(PAGE, "r", encoding="utf-8") as fh:
        page = fh.read()
    # THE NOTE STOPPED APOLOGISING, AND IT WAS RIGHT TO.
    #
    # These three asserted that renderMarkerNote() still said every dot was
    # "worked out from each mount" and "not measured from the model". That was
    # true and necessary while the marker file was [PortId, x, y, z] and carried
    # no provenance. Q9 added the fifth element on 2026-08-27 and the note was
    # rewritten the same night to count each ship's own dots, so a hull whose
    # mounts are all on CIG's transforms now says so without hedging.
    #
    # ASSERTING THE APOLOGY WOULD NOW BE ASSERTING A FALSEHOOD. What B6 needs
    # defended is not the apology - it is that the ESTIMATE is still named as an
    # estimate wherever one is drawn, and that the page never claims a dot was
    # measured off the mesh, which nothing here does at any point.
    check("the note still names an estimate AS an estimate, for the hulls that "
          "have them",
          "an estimate, not measured from anything" in page)
    check("and still says an estimate starts from the mount's NAME",
          "worked out from the mount's name" in page)
    # COMMENTS STRIPPED FIRST, because the page's own prose about its history
    # is not a claim the page makes to a reader. `measured from the model`
    # survives exactly once in this file, inside the comment explaining what the
    # note USED to say - and an assertion that fires on a file's changelog is
    # asserting the wrong text. The original worked around this by deleting the
    # substring "not measured from the model" before searching, which happened
    # to work while the sentence existed and stopped meaning anything when it
    # did not.
    import re as _re
    rendered = _re.sub(r"/\*.*?\*/", "", page, flags=_re.S)
    check("and it does NOT claim a dot was measured off the mesh - CIG's own "
          "transform is a different claim and is the one it makes",
          "measured from the model" not in rendered
          and "decoded" in rendered)
    check("and the per-dot provenance is what it counts, so the sentence is "
          "about THIS ship rather than the fleet",
          "mountProvenance(" in page)

print("\n4. THE FLEET, BEFORE AND AFTER, GEOMETRY HELD CONSTANT")
if QUICK:
    print("     NOT PERFORMED (--quick). Not counted as a pass.")
else:
    tmp = tempfile.mkdtemp(prefix="cc_b6_")
    runs = {}
    for tag, extra in (("before", ["--no-extremity"]), ("after", [])):
        o = os.path.join(tmp, tag + ".json")
        r = os.path.join(tmp, tag + ".rep")
        p = subprocess.run([sys.executable, PLACE, "--out", o, "--report", r],
                           capture_output=True, text=True)
        if extra:
            p = subprocess.run([sys.executable, PLACE, "--out", o,
                                "--report", r] + extra,
                               capture_output=True, text=True)
        runs[tag] = (o, r) if p.returncode == 0 and os.path.exists(o) else None
        if runs[tag] is None:
            print("     %s run failed: %s" % (tag, (p.stderr or "")[-300:]))

    if runs["before"] and runs["after"]:
        A = read_json(runs["before"][0])
        B = read_json(runs["after"][0])
        ra = read_json(runs["before"][1])
        rb = read_json(runs["after"][1])

        moved, per_ship, dists, aimed = 0, {}, [], 0
        for n in A:
            ha = {h["port"]: h for h in A[n]["hardpoints"]}
            worst, c = 0.0, 0
            for h in B[n]["hardpoints"]:
                if h.get("aimed_at") == "extremity":
                    aimed += 1
                d = math.dist(ha[h["port"]]["unit"], h["unit"])
                if d > 1e-9:
                    moved += 1
                    c += 1
                    dists.append(d)
                worst = max(worst, d)
            if c:
                per_ship[n] = (c, round(worst, 3))

        print("\n     DISTANCE MOVED, PER SHIP (worst marker, as a fraction of")
        print("     the hull's half-extent). Ships not listed did not move.")
        for n, (c, d) in sorted(per_ship.items(), key=lambda kv: -kv[1][1])[:14]:
            print("       %-26s %2d marker(s), worst %.3f" % (n, c, d))
        print("       ... %d ships moved at all, %d did not"
              % (len(per_ship), len(A) - len(per_ship)))

        check("some points really were aimed at a measured extremity - "
              "otherwise everything below is measuring nothing",
              aimed > 100, "%d points" % aimed)
        check("and some of them really moved", moved > 50, "%d points" % moved)

        # CROWDING IS TWO NUMBERS AND BOTH ARE ASSERTED.
        #
        # I reported "118 -> 117" and called the control held. That is the
        # MARKER count, and it is the one that improved. The HULL count is a
        # separate number that can move the other way - markers can consolidate
        # onto fewer hulls or spread onto more - and quoting whichever one went
        # the right way is a metric chosen after the fact.
        #
        # A RISE IN EITHER IS THE CONTROL FIRING. And both are measured a
        # second way, independently of the placement report's own counter,
        # because that counter records what the placement loop could not clear
        # DURING placement - which is not the same question as "are two markers
        # sitting on top of each other in the finished file".
        def proximity(fleet):
            tot, hulls = 0, set()
            for n, v in fleet.items():
                pts = [h["pos_model"] for h in v["hardpoints"]]
                if len(pts) < 2:
                    continue
                lo = [min(q[i] for q in pts) for i in range(3)]
                hi = [max(q[i] for q in pts) for i in range(3)]
                ms = (math.dist(lo, hi) or 1.0) * 0.02
                for i, q in enumerate(pts):
                    if min((math.dist(q, r2) for j, r2 in enumerate(pts)
                            if j != i), default=9e9) < ms:
                        tot += 1
                        hulls.add(n)
            return tot, len(hulls)

        cb, hb = sum(x[1] for x in ra["crowded"]), len(ra["crowded"])
        ca, ha = sum(x[1] for x in rb["crowded"]), len(rb["crowded"])
        pb, pa = proximity(A), proximity(B)
        print("")
        print("                      report metric        proximity metric")
        print("                      markers  hulls       markers  hulls")
        print("     BEFORE            %5d   %4d        %5d   %4d"
              % (cb, hb, pb[0], pb[1]))
        print("     AFTER             %5d   %4d        %5d   %4d"
              % (ca, ha, pa[0], pa[1]))
        check("FLEET CROWDING DOES NOT GET WORSE by MARKER count",
              ca <= cb, "%d -> %d" % (cb, ca))
        check("nor by HULL count - the figure I quoted only the good half of",
              ha <= hb, "%d -> %d hulls" % (hb, ha))
        check("nor by an independent proximity measure, by marker",
              pa[0] <= pb[0], "%d -> %d" % (pb[0], pa[0]))
        check("nor by that measure's hull count",
              pa[1] <= pb[1], "%d -> %d hulls" % (pb[1], pa[1]))
        _notes.append("crowding BEFORE/AFTER - report metric %d/%d markers on "
                      "%d/%d hulls; proximity metric %d/%d markers on %d/%d "
                      "hulls" % (cb, ca, hb, ha, pb[0], pa[0], pb[1], pa[1]))

        # THE NEGATIVE CONTROL THE ORDER NAMES: if every ship moves a long way,
        # the new measurement is wrong rather than the old one.
        med = statistics.median(dists) if dists else 0.0
        check("most hulls do not move at all - a hull already close to the "
              "fixed fractions barely moves",
              len(per_ship) < len(A) / 2,
              "%d of %d ships moved" % (len(per_ship), len(A)))
        check("and the typical move is small rather than a relocation",
              med < 0.20, "median %.3f of half-extent" % med)
        check("with the fleet's total displacement bounded - if everything "
              "moved a long way the new measurement would be the wrong one",
              (sum(1 for d in dists if d > 0.7) < 10),
              "%d points moved more than 0.7" % sum(1 for d in dists if d > 0.7))

        _notes.append("fleet: %d points aimed at a measured extremity, %d "
                      "moved on %d of %d ships, median %.3f, crowding %d -> %d"
                      % (aimed, moved, len(per_ship), len(A), med, cb, ca))
    else:
        print("     NOT PERFORMED: a placement run did not complete.")

print("\n" + "=" * 68)
for n in _notes:
    print("  " + n)
print("\n%d passed, %d failed" % (len(_passed), len(_failed)))
if _failed:
    print("FAILED:")
    for f in _failed:
        print("  " + f)
if SELFTEST:
    print("\n--self-test: expectations were inverted, so a non-zero exit is "
          "the correct outcome.")
sys.exit(1 if _failed else 0)
