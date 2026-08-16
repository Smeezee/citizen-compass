#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the name join can REFUSE. Hard rule 12, and the order's own trap.

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
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from build_hardpoint_join import (  # noqa: E402
    resolve_by_rule, resolve_frame, mount_signature, hull_matches, E1,
)

HERE = os.path.dirname(os.path.abspath(__file__))
MOUNTS = os.path.join(HERE, "..", "data-layer", "derived", "holo-hardpoints",
                      "ship_mounts.json")

failures = []


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

    # ---- 3. NEGATIVE CONTROL: A NAME THAT IS NOT AN EDITION ------------
    #
    # Without this, a rule that resolved everything to something would pass all
    # of the above and put a random hull's hardpoints on 40 bare ships.
    for stem in ("Zeus_Mk_II_MR", "Ares_Inferno", "Kraken_Privateer",
                 "Wobbly_Nonsense_Hull", "Galaxy"):
        got, why = resolve_by_rule(stem, keys, mounts)
        check("rule: NEGATIVE CONTROL - %r resolves to NOTHING" % stem,
              got is None, "it resolved to %r (%s) - that is a wrong hull's "
                           "hardpoints on a ship" % (got, why))

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

    # ---- 5. THE MOUNT CHECK COMPARES WHAT IT CLAIMS TO ------------------
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
