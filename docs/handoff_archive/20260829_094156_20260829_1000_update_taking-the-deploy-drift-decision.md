# Update — taking the deploy-drift decision. Sleven said go; I am ruling on it rather than filing another flag.

**2026-08-29 10:00 local · Code (background session)**

I flagged this twice and did not rule. Sleven has now told me to go ahead, so
this is the third mention and the last one.

## THE DEFECT, STATED ONCE

`_verify_deploy_drift.py` proves `testing/_deploy/index.html` the only honest way
available — **it REBUILDS and requires the bytes not to move.** The rebuild
writes into the real `testing/_deploy`, and that is a shared artifact the rest of
the sweep reads.

**It has cost three separate things, none of them theoretical:**

    ordering       a control's result depends on where its name sorts
                   relative to "d". Controls before the rebuild measure one
                   state; controls after measure another.
    evidence       22:23 on the 28th - it rebuilt the payload after C1's 22:19
                   data fix, so the "before" copy I took at 23:37 was an
                   "after". I nearly reported 0 hulls lost markers when the
                   Tiburon had gone from seventeen to none.
    a real abort   Q10's gate refused a deploy because the payload hash moved
                   between Sleven's two commands. The thing that moved it was
                   the sweep's own drift control.

The one measurement that made it undeniable: `_verify_marker_provenance.py` and
`_verify_marker_spread.py` FAILED in the sweep and passed ten minutes later,
while `_verify_marker_census.py` passed in the sweep and failed after. **Three
controls disagreeing with themselves in both directions is one measurement taken
during a write, not three defects.**

## WHAT I AM ABOUT TO DO

I named three options on the 28th and said the choice was a design decision.
Having read the checker again, **I think there is a fourth that gives up
nothing**, and I am checking it before I commit to it: rebuild into a scratch
directory and compare there, so the proof survives and the mutation does not
happen at all.

If `build_deploy.py` cannot be pointed at an output directory, that option dies
and I will take one of the original three and say which.

**Ownership checked first:** `_verify_deploy_drift.py` is not in C1's list in
`OWNERS.md`, so it is Code's by the default clause. `testing/_src/build_deploy.py`
is explicitly Code's. Nothing here touches a C1 path.

Rule 12 applies to the result: whatever I build, the failure path gets exercised
on purpose before I call it working.
