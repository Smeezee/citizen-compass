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

import io
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from build_hardpoint_join import hull_matches  # noqa: E402
from build_hardpoint_alignment import (  # noqa: E402
    median_between, worst_between, mounts_clear_of_differences,
    difference_cells, cell_centre_unit, TOLERANCE,
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

    # ---- 4. THE CHECK THAT MATTERS ---------------------------------------
    #
    # A pair that PASSES the envelope test and is REFUSED by the mount test.
    # Sleven named this one exactly, because it is the case the envelope cannot
    # see: the Cutter Scout's dome and the Rambler's box make almost the same
    # bounding box, and only luck kept a marker off them.
    #
    # SYNTHETIC FIRST, so this runs anywhere. Two identical slabs; one of them
    # has a dome on top. Their envelopes match to within 2%, so the first pass
    # waves them through.
    # A DOME AGAINST A BOX, both the same height - which is what makes their
    # envelopes match and the first pass wave them through. Exactly the
    # Scout/Rambler shape of problem, in miniature.
    def slab(roof):
        pts = []
        # DENSE ENOUGH THAT A CELL HOLDS SEVERAL POINTS. At 0.04 the sample
        # was sparser than the 64-cell grid, so every cell held one point,
        # every cell was discarded as noise, and the fixture found no
        # difference between a box and a dome. The fixture was too coarse to
        # test what it claimed - caught by its own check.
        step = 0.015
        n = int(2.0 / step) + 1
        for i in range(n):
            for j in range(n):
                x = -1.0 + i * step
                z = -1.0 + j * step
                pts.extend([x, -1.0, z])                    # floor
                pts.extend([x, 0.0, z])                     # roof deck
                r2 = x * x + z * z
                if roof == "box" and abs(x) <= 0.5 and abs(z) <= 0.5:
                    pts.extend([x, 0.5, z])                 # square box on top
                if roof == "dome" and r2 <= 0.25:
                    pts.extend([x, 0.5, z])                 # round dome on top
        return {"pts": pts, "min": [-1.0, -1.0, -1.0], "max": [1.0, 0.5, 1.0]}

    rambler, scout = slab("box"), slab("dome")
    ok, detail = hull_matches(rambler, scout)
    check("gate: FIRST PASS - the envelope waves the dome/box pair through",
          ok, "the envelope refused them (%s), so this fixture would not be "
              "testing what it claims to" % detail)

    deck_mounts = [hp("cm_left", (-0.9, 0.0, 0.0)), hp("cm_right", (0.9, 0.0, 0.0))]
    clear, why = mounts_clear_of_differences("rambler", "scout", rambler, scout,
                                             deck_mounts, deck_mounts)
    check("gate: with no mount on the roof structure, the pair is allowed",
          clear, "it refused a pair whose only difference nothing sits on: %s" % why)

    # AND NOW THE ONE THE ORDER ASKS FOR. A scanner ON the part that differs -
    # the corner of the box, where the dome has nothing.
    #
    # THE POSITION IS COMPUTED, NOT TYPED. `unit` is normalised against the
    # hull's LONGEST half-extent, so a short axis never reaches 1.0 - my first
    # attempt put the mount at y=0.5 in unit space, which on this fixture is
    # below the deck rather than on the box, and the gate correctly allowed it.
    # The fixture was wrong, not the gate. Same trap caught the real-ship case
    # below, where the Scout's dome apex is at unit y 0.33 and not 1.0.
    only_box, only_dome, _ = difference_cells(rambler, scout)
    check("gate: the box corners ARE seen as structure the dome lacks",
          len(only_box) > 0,
          "the gate found no difference between a box and a dome, so nothing "
          "below could refuse anything")
    if not only_box:
        print("  [----] the dome/box fixture cannot continue - nothing to plant on")
        return 1
    scanner = deck_mounts + [hp("scanner", cell_centre_unit(sorted(only_box)[0]))]
    clear, why = mounts_clear_of_differences("rambler", "scout", rambler, scout,
                                             scanner, deck_mounts)
    check("gate: THE CASE THAT MATTERS - a mount ON the dome is REFUSED",
          not clear,
          "it ALLOWED it. A Scout's scanner would be dragged down to a roof line "
          "the Scout does not have, which is the exact failure this gate exists "
          "for.")
    if not clear:
        print("         refused with: %s" % why)
    check("gate: and the refusal NAMES the mount",
          "scanner" in (why or ""),
          "'these differ' is not actionable; 'the scanner sits on the dome' is")

    # ---- 4b. THE SAME CASE ON THE REAL SHIPS ---------------------------
    # DEFAULTS TO THE DECODED GEOMETRY THAT IS ACTUALLY IN THE REPO. This was
    # env-var-only, and nothing sets that env var, so 4b printed "COULD NOT RUN"
    # on every run it has ever had - two assertions about the REAL Rambler and
    # Scout that had never once executed. `data-layer/derived/hull-geometry/`
    # holds both files; pointing at it costs nothing and the two now run.
    #
    # STILL FAILS CLOSED. The env var still overrides, and if neither directory
    # is there this prints NOT PERFORMED exactly as before - a check that cannot
    # be run is never reported as one that passed.
    geo_dir = os.environ.get("CC_GEO_DIR", "") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data-layer", "derived", "hull-geometry")
    if geo_dir and os.path.isdir(geo_dir):
        import json as _json

        def load(stem):
            p = os.path.join(geo_dir, stem + ".json")
            if not os.path.exists(p):
                return None
            with io.open(p, encoding="utf-8") as fh:
                return _json.load(fh)

        ram, sco = load("Cutter_Rambler"), load("Cutter_Scout")
        if ram and sco:
            ok, _ = hull_matches(ram, sco)
            check("real: the Rambler and Scout PASS the envelope test",
                  ok, "the fixture rests on them passing it")
            # The dome apex in the Scout's OWN model coordinates, converted
            # to unit space the same way the markers are.
            _, only_scout, _ = difference_cells(ram, sco)
            if not only_scout:
                print("  [----] real Cutter fixture COULD NOT RUN - the gate sees "
                      "no Scout-only structure, so there is nothing to plant on")
                only_scout = None
            planted = ([hp("scanner_dome", cell_centre_unit(sorted(only_scout)[0]))]
                       if only_scout else [])
            clear, why = mounts_clear_of_differences(
                "Cutter Rambler", "Cutter Scout", ram, sco, [], planted)
            check("real: a planted Scout mount ON THE DOME is refused",
                  not clear, "it was allowed: %s" % why)
            if not clear:
                print("         refused with: %s" % why)
        else:
            print("  [----] real Cutter fixture COULD NOT RUN - geometry not decoded")
    else:
        print("  [----] real Cutter fixture COULD NOT RUN - no decoded geometry "
              "at %s. That is a check not performed, not a check that passed."
              % geo_dir)

    # ---- 5. THE APPLY GUARD, WHICH ALREADY FIRED FOR REAL --------------
    #
    # An overlay entry naming a ship or a port the viewer does not have must
    # stop the build. It did: three joined ships are keyed by model stem in the
    # overlay ("M2_Hercules") and by their real name in the viewer ("M2 Hercules
    # Starlifter"), and the build refused rather than reporting 133 markers
    # moved when it had moved 104.
    import build_holo_data as bhd

    # BOTH OVERLAYS, NOT ONE. `apply_alignment` applies ALIGN_CLIENT first and
    # ALIGN second - the client overlay was added on 2026-08-27 and this section
    # still redirected only ALIGN, so the one-ship fixture below met the REAL
    # client overlay and its 167 entries matched nothing. The guard refused,
    # correctly, and this assertion read that as "a missing overlay crashes".
    #
    # The saved originals are restored in the finally: leaving a module constant
    # pointing at a nonexistent file would silently disarm anything that ran
    # after this section in the same process.
    _saved = (bhd.ALIGN, bhd.ALIGN_CLIENT)
    _gone = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "_nonexistent_overlay.json")
    fleet = {"Ship": {"hardpoints": [hp("p1", (0, 0, 0))]}}
    stopped = False
    try:
        bhd.ALIGN, bhd.ALIGN_CLIENT = _gone, _gone
        _, note = bhd.apply_alignment(dict(fleet), {})
        stopped = note.get("moved") == 0 and note.get("client_moved") == 0
    except SystemExit:
        stopped = False
    finally:
        bhd.ALIGN, bhd.ALIGN_CLIENT = _saved
    check("apply: a missing overlay is a no-op, not a crash",
          stopped, "a build with no overlay yet must still work")

    # AND THE OTHER DIRECTION, which is what the fixture hit by accident: an
    # overlay that IS there and matches nothing must stop the build. That guard
    # is the whole reason the M2 Hercules incident was caught, and until now
    # nothing asserted it - it was only ever observed firing by surprise.
    refused, why = False, ""
    try:
        bhd.ALIGN = _gone                      # only the hand-made one is absent
        bhd.apply_alignment(dict(fleet), {})
    except SystemExit as exc:
        refused, why = True, str(exc)
    finally:
        bhd.ALIGN, bhd.ALIGN_CLIENT = _saved
    check("apply: a REAL overlay matching nothing is REFUSED, not reported as "
          "a fix it did not make", refused,
          "the client overlay met a fleet of one ship and should have stopped")
    check("and the refusal says how many entries matched nothing",
          refused and "matched nothing" in why, why[:90])

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
