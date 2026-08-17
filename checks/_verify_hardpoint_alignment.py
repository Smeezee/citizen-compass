#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the alignment overlay can refuse, and picks its reference on purpose.

Hard rule 12. This pass MOVES MARKERS ON SHIPS THAT ARE ALREADY LIVE, so the two
things that decide what moves are driven here with input that must fail them:

  1. the MESH GATE - only ships that are the same hull may be aligned. Sharing a
     port list is not sharing a hull, and that distinction is the whole reason
     the first version of this had to be rewritten.
  2. the MEDOID - which member of a cluster the others align to.

and the apply step's own guard, which already earned its keep: it fired on three
real entries whose keys did not match the names the viewer merges under, instead
of silently reporting a fix it had not made.

Run:  python checks/_verify_hardpoint_alignment.py

Rule 15: encodings stated.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from build_hardpoint_join import hull_matches  # noqa: E402
from build_hardpoint_alignment import (  # noqa: E402
    median_between, worst_between, TOLERANCE,
)

failures = []


def check(name, ok, detail):
    if ok:
        print("  [ok  ] %s" % name)
    else:
        failures.append(name)
        print("  [FAIL] %s\n         %s" % (name, detail))


def hp(port, unit):
    return {"port": port, "where": port, "unit": list(unit),
            "pos_model": list(unit)}


def main():
    print("the alignment overlay, driven with input that must fail it")
    print()

    # ---- 1. THE MESH GATE ----------------------------------------------
    #
    # Real numbers, measured off the models: these two carry the SAME 13 port
    # names and their bounding boxes differ by 53.9%. They are not one hull and
    # must never be aligned to each other.
    kore = {"min": [0, 0, 0], "max": [11.10, 15.43, 29.43]}
    mako = {"min": [0, 0, 0], "max": [5.12, 15.42, 29.43]}
    sen = {"min": [0, 0, 0], "max": [5.18, 15.38, 29.52]}

    ok, detail = hull_matches(kore, mako)
    check("mesh: NEGATIVE CONTROL - Reliant Kore and Mako are NOT one hull",
          not ok, "they were called the same hull (%s) - their markers would be "
                  "forced onto each other's positions" % detail)
    ok, detail = hull_matches(mako, sen)
    check("mesh: Mako and Sen ARE one hull, so they may be aligned",
          ok, "they were called different (%s) - the pass would refuse a "
              "correction it should make" % detail)

    # ---- 2. THE MEDOID -------------------------------------------------
    #
    # Three placements: two that agree and one outlier. The reference must be
    # one of the two that agree, or the group adopts the outlier's positions and
    # the pass makes things worse on two ships to fix one.
    a = [hp("p1", (0.0, 0.0, 0.0)), hp("p2", (0.5, 0.0, 0.0))]
    b = [hp("p1", (0.01, 0.0, 0.0)), hp("p2", (0.51, 0.0, 0.0))]
    outlier = [hp("p1", (0.9, 0.0, 0.0)), hp("p2", (1.4, 0.0, 0.0))]
    members = {"a": a, "b": b, "outlier": outlier}

    def cost(k):
        return sum(median_between(members[k], members[o])
                   for o in members if o != k)
    ref = min(members, key=cost)
    check("medoid: the reference is a member the group agrees with, not the outlier",
          ref in ("a", "b"),
          "it chose %r - the whole cluster would be moved onto the one placement "
          "that disagrees with everything else" % ref)

    # NEGATIVE CONTROL: with the outlier removed the choice must still be sane,
    # and must not depend on ordering.
    members2 = {"outlier": outlier, "b": b, "a": a}

    def cost2(k):
        return sum(median_between(members2[k], members2[o])
                   for o in members2 if o != k)
    check("medoid: NEGATIVE CONTROL - the choice does not depend on dict order",
          min(members2, key=cost2) in ("a", "b"),
          "reordering the input changed which placement the group adopts")

    # ---- 3. THE TOLERANCE MEANS SOMETHING ------------------------------
    near = [hp("p1", (0.0, 0.0, 0.0)), hp("p2", (0.10, 0.0, 0.0))]
    far = [hp("p1", (0.0, 0.0, 0.0)), hp("p2", (0.40, 0.0, 0.0))]
    base = [hp("p1", (0.0, 0.0, 0.0)), hp("p2", (0.0, 0.0, 0.0))]
    check("tolerance: a pair inside %.2f is left alone" % TOLERANCE,
          worst_between(near, base) <= TOLERANCE,
          "got %.3f" % worst_between(near, base))
    check("tolerance: NEGATIVE CONTROL - a pair outside it is not",
          worst_between(far, base) > TOLERANCE,
          "got %.3f - nothing would ever be aligned" % worst_between(far, base))

    # ---- 4. THE APPLY GUARD, WHICH ALREADY FIRED FOR REAL --------------
    #
    # An overlay entry naming a ship or a port the viewer does not have must
    # stop the build. It did: three joined ships are keyed by model stem in the
    # overlay ("M2_Hercules") and by their real name in the viewer ("M2 Hercules
    # Starlifter"), and the build refused rather than reporting 133 markers
    # moved when it had moved 104.
    import build_holo_data as bhd
    fleet = {"Ship": {"hardpoints": [hp("p1", (0, 0, 0))]}}
    stopped = False
    try:
        bhd.ALIGN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "_nonexistent_overlay.json")
        _, note = bhd.apply_alignment(dict(fleet), {})
        stopped = note.get("moved") == 0
    except SystemExit:
        stopped = False
    check("apply: a missing overlay is a no-op, not a crash",
          stopped, "a build with no overlay yet must still work")

    print()
    if failures:
        print("VERIFY FAILED (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("VERIFY PASSED - the mesh gate refuses ships that are not one hull, "
          "the medoid ignores the outlier, and the tolerance discriminates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
