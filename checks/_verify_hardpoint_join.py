#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the name join can REFUSE. Hard rule 12, and the order's own trap.

RULE16: UNPROVEN - it imports resolve_by_rule and the shape and hull gates from
build_hardpoint_join and drives the very functions it judges. The
expectations are independent - hand-written stems, the 25-name
must-not-match trap, published dimensions - but the rule doing the
resolving is the one under test, and a wrong rule cannot be caught by
asking it.

    "A wrong mapping is worse than a missing one. A bare hull is visibly
     incomplete; a Gladius wearing a Hammerhead's hardpoints looks
     authoritative and is a lie."

So the two things that decide whether a ship gets somebody else's hardpoints are
driven here with input that must fail them:

  1. the RULE that resolves an edition to its base hull
  2. the SHAPE CHECK that has the last word on every pair

and both are also driven with input that must pass, because a rule that resolves
nothing and a guard that refuses everything would leave 29 ships bare while
looking rigorous.

Run:  python checks/_verify_hardpoint_join.py

Rule 15: encodings stated.
"""

import io
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from build_hardpoint_join import (  # noqa: E402
    resolve_by_rule, resolve_frame, mount_signature, hull_matches,
    align_to_sibling, E1, MODELS, _resolve_by_rule_pass1_only,
)

HERE = os.path.dirname(os.path.abspath(__file__))
MOUNTS = os.path.join(HERE, "..", "data-layer", "derived", "holo-hardpoints",
                      "ship_mounts.json")
# What place_fleet.py already placed. build_hardpoint_join.py only ever looks at
# models ABSENT from this file, so it is what separates "the matcher changed its
# mind" from "the build changed its output".
FLEET = os.path.join(HERE, "..", "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")

failures = []


# G3'S TRAP, AND THE ONE PLACE IT IS WRITTEN DOWN.
#
# THIS IS THE LOAD-BEARING PART OF G3. Loosening a matcher to catch 2 ships is
# exactly how you silently join the wrong 25 - so the 25 are named, one at a
# time, rather than counted.
#
# Where the list comes from, so it is checkable and not a vibe: the join report
# before this change skipped 39 ships, of which 12 were "no decoded geometry" (a
# different cause entirely, untouched by any matcher) and 27 were name refusals.
# 27 minus the two Ares is 25. If any of these starts matching, the fix is wrong
# and gets reverted rather than accepted at 27.
#
# Imported by `_verify_g3_matcher_delta.py`, which checks the same 25 against
# the join REPORT while this file checks them against the RULE. One list, two
# subjects - rule 14.
STILL_REFUSED = [
    "Crucible", "E1_Spirit", "Endeavor", "Expanse", "G12", "G12a", "G12r",
    "Galaxy", "Genesis", "Hull_D", "Hull_E", "Kraken", "Kraken_Privateer",
    "Legionnaire", "Liberator", "Nautilus", "Nautilus_Solstice_Edition",
    "Odyssey", "Orion", "Pioneer", "Ranger_CV", "Ranger_RC", "Ranger_TR",
    "Vulcan", "Zeus_Mk_II_MR",
]


def model_stems():
    """Every model on disk, named the way the build names them.

    The G3 diff runs over ALL of them rather than a chosen sample: a
    hand-written list can only test what somebody thought of, and the whole
    risk of loosening a matcher is the ship nobody thought of.
    """
    return [f[:-4] for f in os.listdir(MODELS) if f.lower().endswith(".glb")]


def check(name, ok, detail):
    if ok:
        print("  [ok  ] %s" % name)
    else:
        failures.append(name)
        print("  [FAIL] %s\n         %s" % (name, detail))


def main():
    with io.open(MOUNTS, "r", encoding="utf-8") as fh:
        mounts = json.load(fh)
    keys = list(mounts.keys())
    with io.open(FLEET, "r", encoding="utf-8") as fh:
        fleet = json.load(fh)

    print("the join, driven with input that must fail it")
    print()

    # ---- 1. THE RULE RESOLVES A REAL EDITION ---------------------------
    for stem, want in (
        ("Caterpillar_Best_In_Show_Edition_2949", "Caterpillar"),
        ("Gladius_Pirate_Edition", "Gladius Pirate"),
        ("Carrack_w_C8X", "Carrack"),
        ("Carrack_Expedition_w_C8X", "Carrack Expedition"),
        ("Dragonfly_Black", "Dragonfly"),
    ):
        got, why = resolve_by_rule(stem, keys, mounts)
        check("rule: %s resolves to %r" % (stem, want), got == want,
              "got %r (%s)" % (got, why))

    # THE LONGER KEY MUST WIN, or an Expedition silently becomes a Carrack.
    got, _ = resolve_by_rule("Carrack_Expedition_w_C8X", keys, mounts)
    check("rule: NEGATIVE CONTROL - a variant is not swallowed by its base",
          got == "Carrack Expedition",
          "got %r - if this ever says 'Carrack', every Expedition on the site is "
          "showing the wrong ship's mounts" % got)

    # ---- 2. A FABRICATED EDITION, WITH NO CODE CHANGE ------------------
    #
    # THE ACCEPTANCE TEST FOR THE RULING. This name has never existed anywhere:
    # not in the data, not in the finding, not in this repo. If it resolves,
    # then the next Best In Show edition and every future Wikelo livery resolve
    # too, without anyone adding a line.
    for made_up, want in (
        ("Gladius_Emerald_Jubilee_Edition_2955", "Gladius"),
        ("Hammerhead_Wikelo_Sneak_Special", "Hammerhead"),
        ("Reclaimer_Luminalia_2957_Livery", "Reclaimer"),
    ):
        got, why = resolve_by_rule(made_up, keys, mounts)
        check("rule: a FABRICATED edition %r resolves to %r with no code change"
              % (made_up, want), got == want, "got %r (%s)" % (got, why))
        check("      and it is not in the written mapping",
              made_up not in E1, "it would prove nothing if it were")

    # ---- 2b. G3: THE ABBREVIATION RUNS BOTH WAYS -----------------------
    #
    # The rule used to be directional - every word of the mount-data KEY had to
    # appear in the MODEL name - so a key LONGER than the filename was refused.
    # Two ships were sitting on that: the data calls it "Ares Star Fighter
    # Inferno" and the model is Ares_Inferno, so the matcher went looking for
    # "star" and "fighter" in a two-word name.
    #
    # These two used to be negative controls in this very file, asserting they
    # must resolve to NOTHING. That assertion was wrong and the docstring of
    # build_hardpoint_join.py said so at the same time - it records that "Ares
    # Inferno" and "Starfighter Inferno" ARE the same ship. The assertion is
    # flipped here deliberately, not quietly relaxed.
    for stem, want in (
        ("Ares_Inferno", "Ares Star Fighter Inferno"),
        ("Ares_Ion", "Ares Star Fighter Ion"),
    ):
        got, why = resolve_by_rule(stem, keys, mounts)
        check("rule G3: %r resolves to %r (the key is the LONGER name)"
              % (stem, want), got == want, "got %r (%s)" % (got, why))

    # ---- 3. NEGATIVE CONTROL: A NAME THAT IS NOT AN EDITION ------------
    #
    # Without this, a rule that resolved everything to something would pass all
    # of the above and put a random hull's hardpoints on 40 bare ships.
    for stem in ("Zeus_Mk_II_MR", "Kraken_Privateer",
                 "Wobbly_Nonsense_Hull", "Galaxy"):
        got, why = resolve_by_rule(stem, keys, mounts)
        check("rule: NEGATIVE CONTROL - %r resolves to NOTHING" % stem,
              got is None, "it resolved to %r (%s) - that is a wrong hull's "
                           "hardpoints on a ship" % (got, why))

    # ---- 3b. G3'S TRAP, ASSERTED BY NAME -------------------------------
    #
    # THIS IS THE LOAD-BEARING PART OF G3. Loosening a matcher to catch 2 ships
    # is exactly how you silently join the wrong 25 - so the 25 are named, one
    # at a time, rather than counted.
    #
    # Where the list comes from, so it is checkable and not a vibe: the join
    # report before this change skipped 39 ships, of which 12 were "no decoded
    # geometry" (a different cause entirely, untouched by any matcher) and 27
    # were name refusals. 27 minus the two Ares is 25. If any of these starts
    # matching, the fix is wrong and gets reverted rather than accepted at 27.
    # MODULE-LEVEL SINCE 2026-08-27 so there is ONE copy of this list.
    # `_verify_g3_matcher_delta.py` asserts the same 25 against the join
    # REPORT rather than against the rule, and had been carrying the number 25
    # with no names behind it. Two copies of a must-not-match list is rule 14's
    # defect in miniature: the day somebody adds a 26th, one file learns it.
    check("G3 trap: the must-not-match list is the expected 25",
          len(STILL_REFUSED) == 25 and len(set(STILL_REFUSED)) == 25,
          "got %d (%d unique) - the list itself is wrong before it tests "
          "anything" % (len(STILL_REFUSED), len(set(STILL_REFUSED))))
    for stem in STILL_REFUSED:
        got, why = resolve_by_rule(stem, keys, mounts)
        check("G3 trap: %r STILL resolves to nothing after the loosening" % stem,
              got is None,
              "it resolved to %r (%s). The fix caught more than the two it was "
              "for - REVERT it rather than accept 27." % (got, why))

    # AND THE DIFFERENCE IS EXACTLY THOSE TWO, measured rather than asserted.
    #
    # The two lists above are hand-written, so on their own they prove only what
    # somebody thought to write down. This diffs the old matcher against the new
    # one across EVERY model stem on disk - 235 of them - and then splits the
    # result by whether the build can actually see the ship.
    #
    # WHAT THE FIRST RUN OF THIS TURNED UP, because it is the interesting part:
    # at the matcher level pass 2 changes 31 answers, not 2. Twenty-nine of them
    # are ships place_fleet.py ALREADY placed, so build_hardpoint_join.py never
    # asks about them - it iterates only models absent from
    # hardpoints_fleet.json. That is why the report moves by 2 while the matcher
    # moves by 31, and it is worth writing down rather than explaining away.
    #
    # Those 29 are also not wrong: they are manufacturer prefixes and full
    # names - Freelancer against "MISC Freelancer", Scythe against "Vanduul
    # Scythe", Hull_A against "MISC Hull A". Pass 2 handles them correctly and
    # they simply are not this build's business today.
    fleet_stems = {v.get("model", "")[:-4] for v in fleet.values()}
    in_scope = [s for s in sorted(model_stems()) if s not in fleet_stems]

    changed = []
    for stem in sorted(model_stems()):
        before, _ = _resolve_by_rule_pass1_only(stem, keys, mounts)
        after, _ = resolve_by_rule(stem, keys, mounts)
        if before != after:
            changed.append((stem, before, after))

    # And of the in-scope ships, the build asks the MATCHER only about those the
    # written E1 mapping does not already name - it checks `stem in E1` first.
    asked = [s for s in in_scope if s not in E1]
    in_scope_changed = sorted(c[0] for c in changed if c[0] in asked)

    # WHAT EACH ONE RESOLVES TO, not just that it changed.
    #
    # This was `== ["Ares_Inferno", "Ares_Ion"]` and went red on 2026-08-27 when
    # three models were imported at 12:31 - `85X.glb`, `Starlite.glb` and
    # `Aurora_SE.glb`. They were correct when written; new arrivals made them
    # stale. The Ares pair still dates from 2026-08-01.
    #
    # A NAME LIST WAS THE WEAKER HALF OF THE ASSERTION. It could tell you the
    # SET had grown and never that a member resolved to the WRONG hull, which is
    # the failure that matters when a matcher is loosened. Each entry now
    # records its answer, so a wrong match fails here even when the set is
    # exactly right - and a new import fails by name rather than by count.
    #
    # Every one of the five goes from NOTHING to a full name containing the
    # model stem's own words in order, which is the pass-2 rule doing precisely
    # what it was loosened to do. The 25-entry STILL_REFUSED trap above is what
    # proves it did not catch more than that.
    G3_INSCOPE_EXPECTED = {
        "Ares_Inferno": "Ares Star Fighter Inferno",
        "Ares_Ion": "Ares Star Fighter Ion",
        "85X": "85X Limited",                    # imported 2026-08-27 12:31
        "Aurora_SE": "Aurora Mk I SE",           # imported 2026-08-27 12:31
        "Starlite": "MISC Starlite",             # imported 2026-08-27 12:31
    }
    check("G3: of the ships this build actually asks the matcher about, pass 2 "
          "changed exactly the %d recorded below" % len(G3_INSCOPE_EXPECTED),
          in_scope_changed == sorted(G3_INSCOPE_EXPECTED),
          "it changed %d: %s - added %s, missing %s"
          % (len(in_scope_changed), in_scope_changed,
             sorted(set(in_scope_changed) - set(G3_INSCOPE_EXPECTED)) or "none",
             sorted(set(G3_INSCOPE_EXPECTED) - set(in_scope_changed)) or "none"))
    for _stem, _want in sorted(G3_INSCOPE_EXPECTED.items()):
        _after = dict((c[0], c[2]) for c in changed).get(_stem)
        check("G3: and %r resolves to %r" % (_stem, _want), _after == _want,
              "it resolved to %r - a matched hull that is not this ship's is "
              "worse than no match at all" % (_after,))

    # THE SECOND THING THE FULL DIFF TURNED UP, and it is a finding rather than
    # a failure: pass 2 now derives, BY RULE, eleven of the thirteen names E1
    # spells out by hand - every Aurora, all three Hercules, the M50, the
    # Mercury and the C8R Pisces. E1 still wins because the build consults it
    # first, so nothing about today's output depends on this. It is recorded
    # because "the written mapping is now mostly redundant" is worth knowing
    # before somebody adds a fourteenth line to it.
    #
    # NOT ACTED ON. Deleting entries from E1 is not what G3 asked for, and a
    # mapping that agrees with the rule costs nothing while it agrees.
    derived_now = sorted(c[0] for c in changed if c[0] in E1)
    check("G3 finding: pass 2 independently derives 11 of E1's 13 hand-written "
          "mappings (recorded, not acted on)",
          len(derived_now) == 11,
          "expected 11, got %d: %s" % (len(derived_now), derived_now))
    for stem in derived_now:
        got, _ = resolve_by_rule(stem, keys, mounts)
        check("G3 finding: the rule agrees with the hand-written E1 entry for "
              "%r" % stem, got == E1[stem],
              "rule says %r, E1 says %r - they DISAGREE, which means one of "
              "them is putting the wrong mounts on a ship" % (got, E1[stem]))

    out_of_scope = [c for c in changed if c[0] not in in_scope]
    check("G3: every OTHER answer pass 2 changed belongs to a ship already "
          "placed by place_fleet.py, so it cannot reach this build",
          all(c[0] in fleet_stems for c in out_of_scope),
          "a changed answer is neither in scope nor already placed: %s"
          % [c for c in out_of_scope if c[0] not in fleet_stems])

    check("G3: and pass 2 changed them all FROM NOTHING, never from one hull "
          "to another",
          all(c[1] is None for c in changed),
          "pass 2 overrode an answer pass 1 had already given, which the "
          "fallback structure is supposed to make impossible: %s"
          % [c for c in changed if c[1] is not None])

    # The Zeus is the sharpest of those: its ES and CL siblings ARE in the data,
    # so a fuzzy matcher hands the MR its sibling's mounts. C3's first pass did
    # exactly that and threw the result away.
    got, _ = resolve_by_rule("Zeus_Mk_II_MR", keys, mounts)
    check("rule: NEGATIVE CONTROL - the Zeus MR does not inherit its sibling's mounts",
          got is None,
          "a fuzzy matcher paired these; this rule must not, because 'similar "
          "name' is not 'same ship'")

    # ---- 4. THE SHAPE CHECK REFUSES A WRONG PAIR -----------------------
    #
    # Driven directly, because this is the guard that catches a mapping that
    # LOOKS right. A Gladius-shaped hull is offered Hammerhead dimensions.
    gladius_box = ([0.0, 0.0, 0.0], [13.0, 5.0, 20.0])       # roughly a Gladius
    hammerhead = {"length": 111.5, "width": 79.0, "height": 22.0}
    gladius = {"length": 20.0, "width": 13.0, "height": 5.0}

    axes, err, scale = resolve_frame(gladius_box[0], gladius_box[1], gladius)
    check("shape: the CORRECT pair is accepted",
          axes is not None, "the guard refused a hull against its own dimensions "
                            "(%s) - it would leave every ship bare" % (err,))

    # THE MEASURED TRUTH, RECORDED RATHER THAN THE ASSUMPTION.
    #
    # I wrote in the builder that a Gladius hull against Hammerhead dimensions
    # "is not close". It is: err 0.11, well inside the 0.35 threshold, because
    # the guard compares SHAPE and is blind to size on purpose - the model
    # library mixes metres, centimetres and normalised units. This check asserts
    # what actually happens, so nobody reads the proportion guard as protection
    # it does not give.
    axes, err, scale = resolve_frame(gladius_box[0], gladius_box[1], hammerhead)
    check("shape: KNOWN LIMIT - proportions alone do NOT catch a Gladius hull "
          "offered Hammerhead dimensions",
          axes is not None and err < 0.35,
          "if this starts failing the guard got stricter and that is good news, "
          "but the hull check below is what the order actually asked for")
    print("         proportion error was %.2f, threshold 0.35 - which is why "
          "hull_matches exists" % err)

    # AND THE CHECK THAT DOES CATCH IT.
    gladius_geo = {"min": [0, 0, 0], "max": [13.0, 5.0, 20.0]}
    gladius_twin = {"min": [0, 0, 0], "max": [13.05, 5.02, 20.1]}
    hammerhead_geo = {"min": [0, 0, 0], "max": [79.0, 22.0, 111.5]}

    ok, detail = hull_matches(gladius_geo, gladius_twin)
    check("hull: the same hull re-skinned is accepted", ok, detail)

    ok, detail = hull_matches(gladius_geo, hammerhead_geo)
    check("hull: NEGATIVE CONTROL - a Gladius against a Hammerhead is REFUSED",
          not ok,
          "it was ACCEPTED (%s). This is the exact failure the order names: a "
          "Gladius wearing a Hammerhead's hardpoints, looking authoritative." % detail)
    if not ok:
        print("         refused with: %s" % detail)

    # A HULL THAT IS THE SAME SHAPE BUT A DIFFERENT SIZE IS STILL NOT THE SAME
    # HULL. Without this, a check on proportions in disguise would pass.
    ok, detail = hull_matches(gladius_geo, {"min": [0, 0, 0], "max": [26.0, 10.0, 40.0]})
    check("hull: NEGATIVE CONTROL - the same shape at twice the size is refused",
          not ok, "got %s - an edition is the same mesh, not a scaled one" % detail)

    # AND A HULL WITH NO PUBLISHED DIMENSIONS IS REFUSED, not guessed at.
    axes, err, _ = resolve_frame(gladius_box[0], gladius_box[1], {})
    check("shape: NEGATIVE CONTROL - no published dimensions means refused",
          axes is None and "no published dimensions" in str(err),
          "got %r - the Javelin is in this state and must stay bare rather than "
          "be placed in a frame nobody checked" % (err,))

    # ---- 5. SAME HULL, SAME POSITIONS -----------------------------------
    #
    # The alignment pass takes an already-placed sibling's positions as targets
    # and re-snaps them to this hull. Driven here on a synthetic hull whose
    # vertices are known, so "it moved to the right place AND stayed on the
    # mesh" is checked rather than assumed - a copied position that floats off
    # the hull would be a worse defect than the one this replaces.
    #
    # A flat slab of vertices: a wing, essentially, which is where the problem
    # showed up in the first place.
    pts = []
    for i in range(41):
        for j in range(9):
            pts.extend([-1.0 + i * 0.05, 0.0, -1.0 + j * 0.25])
    geo = {"pts": pts, "min": [-1.0, 0.0, -1.0], "max": [1.0, 0.0, 1.0]}

    wrong = [{"port": "rack", "where": "Rack", "pos_model": [-0.5, 0.0, -0.75],
              "unit": [-0.5, 0.0, -0.75]}]
    sibling = [{"port": "rack", "unit": [0.5, 0.0, 0.5]}]
    moved, worst = align_to_sibling(wrong, geo, sibling)
    check("align: a marker is moved to where the same hull already has it",
          moved == 1 and abs(wrong[0]["unit"][2] - 0.5) < 0.1
          and abs(wrong[0]["unit"][0] - 0.5) < 0.1,
          "moved=%d worst=%s ended at %s" % (moved, worst, wrong[0]["unit"]))

    # AND IT LANDED ON THE MESH, not at the sibling's coordinates in mid-air.
    q = wrong[0]["pos_model"]
    near = min(math.sqrt((pts[i * 3] - q[0]) ** 2 + (pts[i * 3 + 1] - q[1]) ** 2 +
                         (pts[i * 3 + 2] - q[2]) ** 2)
               for i in range(len(pts) // 3))
    size = math.sqrt(sum((geo["max"][k] - geo["min"][k]) ** 2 for k in range(3)))
    check("align: and it is snapped to this hull's own geometry",
          near <= size * 0.02,
          "it sits %.3f from the nearest vertex (%.1f%% of hull size) - a copied "
          "position that floats is worse than the misplacement it replaced"
          % (near, near / size * 100))

    # NEGATIVE CONTROL: a marker already in the right place must STAY there.
    #
    # Not "must not move at all" - that expectation was wrong and this check
    # caught me writing it. The pass re-snaps every marker and push_out lifts
    # each one 1.2% clear of the surface, so a correct marker comes back a hair
    # away from where it started. What must be true is that it does not get
    # RELOCATED, and that is what is asserted.
    already = [{"port": "rack", "where": "Rack", "pos_model": [0.5, 0.0, 0.5],
                "unit": [0.5, 0.0, 0.5]}]
    align_to_sibling(already, geo, sibling)
    shift = math.sqrt((already[0]["unit"][0] - 0.5) ** 2 +
                      already[0]["unit"][1] ** 2 +
                      (already[0]["unit"][2] - 0.5) ** 2)
    check("align: NEGATIVE CONTROL - a marker already in place stays there",
          shift < 0.05,
          "it shifted by %.3f, which is a relocation rather than a re-snap" % shift)

    # NEGATIVE CONTROL: a port the sibling does not have is left alone.
    orphan = [{"port": "nothing_like_it", "where": "X", "pos_model": [-0.5, 0.0, -0.5],
               "unit": [-0.5, 0.0, -0.5]}]
    moved, _ = align_to_sibling(orphan, geo, sibling)
    check("align: NEGATIVE CONTROL - a port the sibling lacks is untouched",
          moved == 0 and orphan[0]["unit"] == [-0.5, 0.0, -0.5],
          "it was moved to a position no sibling ever stated")

    # ---- 6. THE MOUNT CHECK COMPARES WHAT IT CLAIMS TO ------------------
    a = {"mounts": [{"port": "p1"}, {"port": "p2"}]}
    b = {"mounts": [{"port": "p1"}, {"port": "p2"}]}
    c = {"mounts": [{"port": "p1"}, {"port": "p3"}]}
    d = {"mounts": [{"port": "p1"}]}
    check("mounts: identical sets compare equal",
          mount_signature(a) == mount_signature(b), "they do not")
    check("mounts: NEGATIVE CONTROL - the same COUNT with different PORTS differs",
          mount_signature(a) != mount_signature(c),
          "a count-only check would call these the same ship")
    check("mounts: NEGATIVE CONTROL - a different count differs",
          mount_signature(a) != mount_signature(d), "they compare equal")

    print()
    if failures:
        print("VERIFY FAILED (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("VERIFY PASSED - the rule resolves what it should, refuses what it "
          "should, and the shape check refuses a wrong pair on demand")
    return 0


if __name__ == "__main__":
    sys.exit(main())
