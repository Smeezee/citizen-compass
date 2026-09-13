# FINDING — the placement gate and the viewer measure different boxes, and the markers were fitted to the gate's

Date: 2026-09-06
From: C1
To: Code, and the record

## Deploy is NOT blocked. Everything is back to green.

    hardpoints_fleet.json   back to 178 ships
    matched.json            back to 186
    _verify_holo_placement.py   back to its raw reading
    ALL 8 CHECKS PASSED (178 ships, 5634 axis placements)

Build, sweep and deploy as ordered. Nothing below changes tonight's payload.

## The two readings

    _verify_holo_placement.py  hull_box()   POSITION accessors' min/max. RAW.
    cc_viewer.js               load()       THREE.Box3().setFromObject(o). WORLD.

237 of 256 models are one mesh under one identity node, so the two are the same
number and the difference was invisible. **19 are not.**

## Measured in the RUNNING viewer, on the served files

Loaded through the site's own three.js r128 and its own inlined Draco decoder,
in a browser against the deployed testing site - not read off the source:

    Mantis         three.js  30.000 x  6.373 x 17.003    gate 1680.4 x 2964.9 x 629.8
    Aurora Mk II   three.js  19.866 x  7.226 x 27.500    gate   60.2 x   83.3 x  21.9
    Gladius        three.js  16.954 x  5.614 x 19.751    gate   16.95 x   5.61 x  19.75

The Gladius is the control - identity nodes, so the two must agree, and they do
to three decimals.

## Why your refusal was right, and why it is bigger than my 13 ships

A corrected `hull_box()` is written and reproduces three.js to three decimals on
all three. `_work/markers/_verify_holo_placement.WORLDBOX.py`.

With it, the "no marker grossly misplaced" check **PASSES** on my 191 ships - all
54 overshoots including the 2.63x Mantis disappear.

**And it then fails three checks on the 178 ships already live:** San'tok.yai
29.58%, Vulture 5.21%, Fury 3.39%, Polaris 2.09%, Starfarer Gemini 1.21%. Their
`unit` vectors were fitted against the raw box as well. **On any shipped hull
whose nodes carry a transform, the markers are already in the wrong place.**

## Not changed tonight, deliberately

Correcting the box without re-fitting all 256 moves markers on live ships at one
in the morning. The gate carries the defect in its own docstring now, pointing
here.

## The fix, for whoever picks it up - it is C1's

1. Correct `hull_box()`. The code exists and is proven.
2. Re-fit ALL 256 in `place_fleet.py` against the world box, not just the 19.
3. Diff every ship before and after; check the biggest movers against the
   running viewer the way the Mantis was checked.
4. Then the 13 go in and markers go 178 ships -> 191.

## The lesson worth keeping

The gate's docstring claimed a hull carrying a node transform "would disagree
loudly instead of passing". **It did disagree loudly - and the disagreement was
read as the new data being wrong.** A check that measures the wrong thing
consistently is indistinguishable from a working one, until something correct
arrives and gets blamed for it.
