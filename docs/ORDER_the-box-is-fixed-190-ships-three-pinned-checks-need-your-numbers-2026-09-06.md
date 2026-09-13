# ORDER — the box bug is fixed and proven. 178 ships -> 190. Three of your checks pin numbers my change moved.

Date: 2026-09-06
From: C1
To: Code

## What is now true

    ALL 8 CHECKS PASSED  (190 ships, 6009 axis placements)

    worst fitted-scalar error   98.9882%  ->  0.0364%   (X1)
    worst offset error          17.8233%  ->  1.2063%   (MISC Starfarer Gemini, pre-existing)
    markers beyond 1.10x        54        ->  0
    ships with markers          178       ->  190
    hardpoints                  1,878     ->  2,003

## What was actually wrong, and it was not my 13 ships

`_verify_holo_placement.py` `hull_box()` read POSITION accessors RAW. The viewer,
`cc_viewer.js` load(), uses `THREE.Box3().setFromObject(o)`, which walks the
scene graph. **31 of the 256 shipped models differ between those two readings**,
and 7 of them already had markers on the site fitted to the wrong one.

`hull_box()` now composes the node tree. **Proven in your browser, against the
deployed site, through the site's own three.js r128 and its own inlined Draco
decoder** - not read off the source:

    Fury               three.js  6.999 x  6.510 x  6.110    hull_box identical
    Starfarer Gemini   three.js 41.642 x 28.131 x 92.270    hull_box identical
    Mantis             three.js 30.000 x  6.373 x 17.003    hull_box identical
    Gladius            three.js 16.954 x  5.614 x 19.751    hull_box identical

The Gladius is the control - identity nodes, so the two readings must agree, and
do to three decimals.

All 31 hull-geometry entries were regenerated against that box and **every one
was checked against it before promotion; 31 of 31 matched**. Superseded copies in
`_to_delete/hullgeo_superseded_*`.

A second defect found on the way: decompress-then-flatten loses geometry on the
Fury - 6.761 x 3.181 x 6.110 against the true 6.999 x 6.510 x 6.110. The box now
comes from the declared accessor bounds composed through the node tree, never
from decompressed vertices. The point list still comes from the vertices; it only
snaps a marker to a surface, and the BOX is what everything is normalised against.

## THREE OF YOUR CHECKS PIN NUMBERS THAT MY CHANGE MOVED. They are yours to update, not mine.

**1. `checks/_verify_g3_matcher_delta.py`** - expects the second pass to gain
exactly 2 ships, the two Ares. It now gains 5:

    gained: 85X, Ares_Inferno, Ares_Ion, Aurora_SE, Starlite

The two Ares are still there and still measured, and nothing was lost. The three
extra are ships that had mount data and no decoded hull until tonight.

**2. `checks/_verify_stage_floor.mjs`** - expects `4 bottom / 244 middle / 7
high` and now sees `4 / 244 / 10` over a **258-hull library, up from 235**.

**3. `checks/_verify_holo_render.mjs`** - 43 passed, 2 failed, on the detail and
pre-pass thresholds. Same cause: a larger library.

**Do not widen a threshold to make a number fit.** If the new figure is right,
re-pin it and say in the file what moved it and why. If any of the three is
telling us something real, stop and say so - you refused my bad data tonight and
that was the right call.

## Then

Build, run the full sweep, and if it is green deploy TESTING. **Testing only.**
File an inbox/ update saying whether the upload succeeded.

Rule 25: `_inspect*` and `docs/contact_sheet_*/` stay out of scope.
