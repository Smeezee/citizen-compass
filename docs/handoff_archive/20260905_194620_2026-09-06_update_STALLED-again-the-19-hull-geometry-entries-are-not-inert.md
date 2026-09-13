# Update — STALLED. Built fine, sweep is red: the 19 new hull-geometry entries are NOT inert.

**2026-09-06 · Code (Build)**

**Built clean. Swept. NOT deployed.** No `-IgnoreSweep`. Filing the stall and
stopping, per rule 25 Part B.

## The build was fine

    hull markers: 6019 on 259 hulls
    of those, 4025 INHERITED from a placed ancestor; 0 refused
    deploy guard: safe to deploy
    BUILD EXIT=0

The holo placement gate passes again after C1's revert, exactly as their order
said. That half is correct.

## The sweep is not green

    117 passed, 3 failed

    _verify_g3_matcher_delta.py
    _verify_holo_render.mjs
    _verify_stage_floor.mjs

## All three have ONE cause, and it is the thing C1 called inert

The order says:

> The 19 new `hull-geometry/` entries STAY. Nothing at build time reads that
> directory - `build_deploy.py` reads `hardpoints_fleet.json` - so they are
> inert until the placement half is fixed.

**Nothing at BUILD time reads it. Three CONTROLS do.**

    _verify_g3_matcher_delta.py   7 references to hull-geometry
    _verify_stage_floor.mjs       3
    _verify_holo_render.mjs       2

`data-layer/derived/hull-geometry/` now holds **258 entries**, five of them
written after 19:00. Each control's own output names the change:

    g3_matcher_delta   "geometry: ... (258 decoded hulls)"
                       [FAIL] the second pass places exactly 2 more ships
                       [FAIL] and skips exactly 2 fewer
                       [FAIL] the two ships gained are the two Ares, by name

    stage_floor        "with the other 244 in the middle of a 258-hull library
                        (was 235)"   4 / 244 / 10

    holo_render        detail changes the render between 8 and 70 on panel:
                       identical signature

**The build-time reasoning was right and the conclusion was too narrow.** The
directory is an input to the check suite as well as to the placement pipeline,
and three controls assert against counts and distributions taken when it held
235-239 hulls.

## What I am NOT doing

- **Not deploying.** The order says deploy if green. It is not green.
- **Not adjusting those three controls to accept 258.** Two of them
  (`holo_render`, `stage_floor`) are mine and I could make them pass in
  minutes. That is exactly the move rule 12 exists against: the numbers they
  assert were chosen from a 235-hull library, and re-baselining them to whatever
  the library now holds converts three checks into three restatements of the
  current data.
- **Not touching `hull-geometry/`.** It is C1's and they have work in flight.
- **Not picking up other work.** Rule 25 Part B.

## What unblocks it, and it is a decision rather than a fix

Someone has to say whether those three controls should be re-baselined against
a 258-hull library, and on what evidence. Two questions I cannot answer:

1. **g3_matcher_delta** asserts the second pass gains **exactly the two Ares by
   name**. With 19 more decoded hulls that delta is a different set. Is the
   assertion about the Ares specifically, or about "the pass gains what it
   should"? The first is now wrong; the second needs rewriting, not renumbering.
2. **stage_floor** wants y=0 to sit mid-distribution across the library. At 258
   it reads 4 low / 244 middle / 10 high. Whether 10 high is a real regression
   or just a wider library is a judgement about the fleet, not about the check.

**The 21:05 payload is still what the site serves, and it is green.** Nothing
has regressed for a visitor; this blocks a new deploy, not the live one.
