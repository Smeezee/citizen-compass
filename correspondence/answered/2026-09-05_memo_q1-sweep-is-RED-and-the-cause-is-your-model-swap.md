# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: Q1 STOPPED - the sweep is red, 8 controls, and the root cause is the model swap invalidating the holo placement fit

**Not deployed. `-IgnoreSweep` not used**, per your instruction.

    111 passed, 8 failed

    _verify_holo_placement.py  (build gate)   <- THE CAUSE
    _verify_community_mark.py
    _verify_correspondence.py
    _verify_deploy_drift.py
    _verify_edge_detail.mjs
    _verify_find_build_step.py
    _verify_model_scale.mjs
    _verify_takedown.py
    _verify_version_single_source.py

## One cause, not eight

`_verify_holo_placement.py` is a **build gate**. It fails, the build refuses, and
every control that rebuilds to do its job fails behind it:

    GATE FAILED: _verify_holo_placement.py checks. Refusing to build.
    NOT PERFORMED: the build failed, so the rebuild half of this control
    could not run.

`deploy_drift`, `version_single_source`, `takedown`, `community_mark`,
`find_build_step` all rebuild. They are collateral. **Fix the gate and I expect
seven of the eight to clear on their own** - I will not assert that until a
sweep says so.

## What the gate is actually saying

    FAIL  that scalar IS the hull's longest half-extent, to within 0.5%
          worst 12.3801%, MISC Freelancer
    FAIL  the fitted offset IS the hull's own bbox centre
          worst 22.4289%, MISC Freelancer

    8 ship(s) offset by more than 0.5% of hull size:
       22.429%  MISC Freelancer
       22.247%  MISC Freelancer MAX
       20.922%  MISC Freelancer DUR
       20.300%  MISC Freelancer MIS
        1.934%  X1 Velocity
        0.971%  X1 Force
        0.970%  X1

**Those are your replaced hulls, and only your replaced hulls.**

`data-layer/derived/holo-hardpoints/` holds a fitted scale and offset per hull,
computed against the geometry that was there when it was fitted. You replaced
the geometry. The four Freelancers moved their bbox centre by ~20-22% of hull
size, so every marker on them is now placed against a hull that no longer
exists.

The 85X does not appear, which fits - it kept its extents. The three X1s are
under 2% and the Freelancers are the real break.

## This is the failure mode your own memo predicted, from the other end

You wrote that if a hull ever ships it ships under its existing filename, so the
register needs no edit. That held - the register is fine. **What no one said is
that the DERIVED data keyed to the old geometry also has to move**, and the
holo placement fit is exactly that.

`data-layer/derived/holo-hardpoints/` is yours in OWNERS.md. **I have not
touched it and I am not regenerating it** - I do not know whether the fit is
re-run by a script you hold or by a step in the placement pipeline, and guessing
at a marker-placement dataset is how markers end up on the wrong part of a ship.

## What I need to finish Q1

Either the holo placement fit regenerated against the new hulls, or a ruling
that the gate's 0.5% tolerance is wrong for these ships and why.

Everything else is ready: the payload is built, Q2 is answered against it - the
see-through is gone, the 85X is one ship, the X1s are correctly two-of-three
identical - and the sweep will run again the moment the fit is current.

**Q3 to Q6 are untouched.** Your Q1 says nothing else until it lands, and it has
not landed.

---

ANSWERS: C1, 2026-09-05, in `inbox/ORDER_regenerate-the-hull-geometry-and-the-fit-2026-09-05.md`.

You were right to stop and right about the cause. Ruling, in short:

1. **The 0.5% tolerance stands.** It is the correct order of magnitude for a
   marker that must sit on a named part of a ship. A gate widened until it
   passes is not a gate. Make the data true instead.
2. **Authorised** to run steps 1 and 2 into `_stage/` and hand over the
   staged-vs-current comparison. The order names the paths and states the
   change, so it is delegation, not a second writer. **Promotion stays C1's.**
3. **Nine hulls, not eight.** The Fury changed today - 9.35 x 6.15 x 8.57 down
   to 3.27 x 3.40 x 6.41, a bigger bbox move than any Freelancer - because five
   unplaced loadout assemblies were removed from it. It goes in the same
   re-decode.
4. Seven of eight reds being collateral behind one build gate is almost
   certainly right, and is not asserted until a sweep says so. Agreed.
