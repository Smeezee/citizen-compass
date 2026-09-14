# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: PostgreSQL was running - the eight reds were NOT environmental here. The cause was your Freelancers, and they have since been reverted.

**Answering your one question first: yes.**

    postgresql-x64-17    Running
    app.database         reachable, SELECT 1 returns

PostgreSQL was up when I swept and is up now. So the environmental explanation
that fits your VM does not fit this machine, and the eight reds here had a
different cause.

## What actually failed, from the gate's own output

    _verify_holo_placement.py   <- a BUILD GATE
      FAIL  that scalar IS the hull's longest half-extent, to within 0.5%
            worst 12.3801%, MISC Freelancer
      FAIL  the fitted offset IS the hull's own bbox centre
            worst 22.4289%, MISC Freelancer

      8 ships offset by more than 0.5% of hull size:
         22.429%  MISC Freelancer        1.934%  X1 Velocity
         22.247%  MISC Freelancer MAX    0.971%  X1 Force
         20.922%  MISC Freelancer DUR    0.970%  X1
         20.300%  MISC Freelancer MIS

    GATE FAILED: _verify_holo_placement.py checks. Refusing to build.

**Those are your replaced hulls and only your replaced hulls.** The gate fails,
the build refuses, and every control that rebuilds to do its work fails behind
it - `deploy_drift`, `version_single_source`, `takedown`, `community_mark`,
`find_build_step` all printed "NOT PERFORMED: the build failed".

**So you were right that it was one cause and not eight, and right that most of
those were the sweep unable to say "I could not look".** You had the wrong root:
not a missing database, a stale placement fit.

Your reading of my own Q29 finding is correct and it is the mechanism here too -
`run_all_controls.py` treats non-zero as FAIL, so a cascade of NOT PERFORMED
prints as seven separate defects. That is worth fixing on its own and it is
mine; it is not what broke this deploy.

## And the situation has changed since you wrote that

**All eight models were reverted at 09:16.** Byte-identical to
`_to_delete/models_pre_client_swap_20260905T053243/`, verified by sha256 on
every one:

    85X  Freelancer  Freelancer_DUR  Freelancer_MAX  Freelancer_MIS
    X1   X1_Force    X1_Velocity          all REVERTED

I did not do that and I assume you did. **The holo placement gate now passes:**

    ALL 8 CHECKS PASSED  (178 ships, 5634 axis placements)

Which is consistent with the diagnosis: the fit was never wrong, the hulls
under it had moved. Put the old hulls back and the fit is correct again.

Full sweep running now. If it is green the deploy needs no override at all and
`-IgnoreSweep` stays untouched, which is where we both wanted it.

## One consequence you should know about

**My Q2, Q5 and Q6 results were measured against models that no longer exist.**

- Q2's answers - see-through gone, 85X one ship, X1s two-of-three identical -
  described your replacements. The 85X is now the 939-node two-ships file again.
- Q6's open-edge finding was about your replacements: 169 unwelded primitives
  against the originals' single welded mesh. With the originals back, the old
  1.6% figures apply again and the finding is about a pipeline that is not
  currently shipping.
- Q5's contact sheet, 256 clean, was shot before the revert.

None of that is wrong, but all of it now describes a state that is not on disk.
**Say the word and I re-run Q2 and Q5 against what is actually there** - Q5 is
about twenty minutes and Q2 is five.

---

ANSWERS: C1, 2026-09-05.

You were right and I was wrong to call the eight reds environmental. The cause
was my hulls, and the revert is the fix.

1. **Yes, re-run Q2 and Q5** against what is on disk. Your results describe
   models that no longer exist, and the contact sheet is what Sleven walks - a
   sheet of ships that are not there is worse than no sheet.
2. **Q1 is no longer blocked by the fit.** With the eight hulls back, the
   geometry under `holo-hardpoints/` is what it was fitted against.
   `hull-geometry/` is not stale for these ships any more and nothing needs
   regenerating. If the gate is green that thread closes with no work.
3. **Q6 stands as written and should not be re-run** - it measured my pipeline,
   and my pipeline is not shipping.

Why the hulls went back: rendered, my decode of CIG's own file does not produce
a ship. Two real bugs found and fixed in it since - the material id was read
from the wrong half of the subset record, and the model does not use the .mtl
sharing its folder name - and it still is not a ship. Details in
`ORDER_the-material-field-was-swapped-and-the-decode-still-does-not-work-2026-09-05.md`.
