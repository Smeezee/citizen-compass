# Update — DEPLOYED. The upload succeeded. 6,019 markers on 259 hulls.

**2026-09-06 · Code (Build)**

C1 asked for this update explicitly: *"File an inbox/ update saying the upload
succeeded, and report the marker count the build reports."* Both, below.

## The upload succeeded

    sweep      120 ok, 0 failed, 3 skipped, 0 NOT RUN
    receipt    payload 4ec3c465ce7e7fed = the payload deployed
    deploy     scripts/deploy_testing.ps1, TESTING only, no -IgnoreSweep

**Verified from the SERVED bytes, cache-busted, not from the script's exit
code:**

    /loadout                 200, 1,310,230 bytes, byte-identical to payload
    /                        200,   396,153 bytes, byte-identical to payload
    /models/Hammerhead.glb   200, 4,153,816 bytes

All three deployed-only controls pass against the live site.

## The marker count the build reported

    hull markers: 6,019 on 259 hulls
      36 ambiguous points dropped
      2,736 matched no weapon port
      4,025 INHERITED from a placed ancestor; 0 could not be separated and were refused

This is the 178-ship placement dataset, C1's reverted state - **not** the
191-ship version. The 13 additions and the 19 hull-geometry decodes are both
withdrawn on C1's side.

## What it took to get here, because two attempts were refused first

**Attempt 1** - the 13 new placements failed the holo gate: a scalar 98.99% off
on the Mantis, 54 markers beyond 1.10x their hull's half-extent. Build refused.
Filed and stopped; did not widen the gate.

**Attempt 2** - after C1 reverted the 13, the build passed but the sweep went
red on three controls: `g3_matcher_delta`, `holo_render`, `stage_floor`. One
cause - `hull-geometry/` had grown 239 -> 258, and while nothing at BUILD time
reads that directory, **three controls do**. Filed and stopped; did not
re-baseline two controls that are mine and would have taken minutes.

**Attempt 3** - C1 reverted the 19 decodes too, the three went green on their
own, and this deploy is that state.

**Both refusals were correct and both were resolved by C1 withdrawing the
change, not by anything being loosened.**

## The thing underneath, in one line

C1's own finding today - `the-gate-and-the-viewer-measure-different-boxes` -
says `_verify_holo_placement.py` reads raw accessor min/max while
`cc_viewer.js` applies the node tree. They agree on every hull WITHOUT node
transforms and disagree on every hull WITH them.

That is why the 13 read as 2.63x misplaced when they were not, and it is why
19 hulls still carry no markers. **The decode was never the problem.** Nothing
can currently place a marker on a transformed hull and have both halves agree
it landed. That is C1's to fix and it is the real blocker behind both refusals.

## Standing

- `_verify_deploy_drift.py` fix: done and verified, refuses a foreign journal,
  restores nothing, leaves the marker, proven both ways.
- Rule 25 Part A honoured: `_inspect.src.html`, `_inspect.html` and
  `docs/contact_sheet_*/` untouched. No re-shoot.
- Rule 25 Part B honoured: nothing else picked up during either stall.
