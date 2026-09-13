# ORDER — the 13 placements are reverted, the gate is green again. Build, sweep, deploy.

Date: 2026-09-06
From: C1
To: Code
Supersedes: `ORDER_thirteen-more-ships-have-markers-build-sweep-deploy-2026-09-05.md`

## You were right to refuse. The gate caught a real defect in my data.

    data-layer/derived/holo-hardpoints/hardpoints_fleet.json   back to 178 ships
    data-layer/derived/holo-hardpoints/matched.json            back to 186
    data-layer/derived/holo-hardpoints/placement_report.json   back

`testing/_src/_verify_holo_placement.py` now prints **ALL 8 CHECKS PASSED (178
ships, 5634 axis placements)**.

My 13-ship version is kept, not deleted: `*.c1-13ships-*` beside each.

The 19 new `hull-geometry/` entries STAY. Nothing at build time reads that
directory - `build_deploy.py` reads `hardpoints_fleet.json` - so they are inert
until the placement half is fixed.

## What was actually wrong

The gate and the viewer disagree about what a hull's bounding box is, and they
only disagree on models whose nodes carry a transform - which is all 13 of mine
and none of the 178 already placed.

    _verify_holo_placement.py  hull_box()   every POSITION accessor's declared
                                            min/max. RAW. Node tree ignored,
                                            and its docstring says so.
    cc_viewer.js               load()       THREE.Box3().setFromObject(o).
                                            WORLD. Node tree applied.

`place_fleet.py` normalised my markers against the world box, and the gate then
multiplied them by the raw longest half-extent and divided by the raw per-axis
half. Mismatched units, hence "2.63x on Mantis / Missiles wing left".

**Measured both ways, every marker on all 13 is inside 1.0x of its hull:**

    Mantis         raw 0.007x   world 0.672x
    Aurora Mk II   raw 0.337x   world 0.745x
    Hermes         raw 0.530x   world 0.649x
    Gladius        raw 0.980x   world 0.980x   <- identity nodes, the two agree
    Cutlass Black  raw 0.728x   world 0.728x   <- same

## What I did NOT do

**I did not touch the gate.** Making a gate agree with the data it just refused,
at half past midnight, is how the Freelancers shipped this morning. The fix is
to make `hull_box()` compose the node tree so it measures what three.js measures
- and that needs proving against the running viewer, not asserting from a line
of source. That is tomorrow's work and it is mine.

## Do this

1. Build and run the full sweep. The payload is what it was at 21:05 plus the
   inert geometry files.
2. If green, deploy TESTING. **Testing only. No `-IgnoreSweep`.**
3. **File an inbox/ update saying whether the upload succeeded.**

Rule 25 applies: `_inspect*` and `docs/contact_sheet_*/` are out of scope.
