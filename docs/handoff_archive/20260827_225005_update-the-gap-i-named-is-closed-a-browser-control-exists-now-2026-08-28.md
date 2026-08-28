# Update — I said the most important thing Sleven asked for had no check that fires. It does now. `checks/_verify_stage_still.mjs`.

**2026-08-27 22:45 local · C1** — closing my own gap rather than leaving it
with you.

## What I said an hour ago

> *"A RULE 12 GAP I AM NOT GOING TO PAPER OVER. The new 'the ship did not move'
> assertion reports NOT PERFORMED in the script harness... The single most
> important thing Sleven asked for has no check that actually fires."*

I also said browser checks are yours. **That was wrong** — I own
`_verify_panel_dismiss.mjs`, which is a real-browser control in my lane, so a
sibling for this is mine to write too. Written.

## What it does

Loads the **400i** — the ship Sleven was holding when he reported the shift —
in headless Chromium, reads the camera, clicks a marker, and reads it again.

    1. the hull and its markers are really there
    2. clicking a hardpoint does not move the ship        <- the load-bearing one
    3. the panel opens on the marker's own side
    4. the hull renders see-through, as asked for
    5. the page threw nothing while being driven

**Section 2 reads the WHOLE camera** — look-at point and eye position, rounded
to 1e-6 so floating-point noise is not read as motion. A pan moves the target; a
recomputed distance moves the position. And it clicks a **second** marker on a
different mount, because a shift that only fired on the first open would slip
past one measurement.

**Section 3 finds a dot left of centre and a dot right of centre on the real
hull**, clicks each, and requires the panel to land on that side — plus that the
two answers differ, so a rule that always said "right" fails.

## Three planted defects, and one of them nearly shipped inert

    node checks/_verify_stage_still.mjs --mutate-pan          section 2 must go red
    node checks/_verify_stage_still.mjs --mutate-alwaysright  section 3 must go red
    node checks/_verify_stage_still.mjs --mutate-opaque       section 4 must go red

**`--mutate-pan` started as two mutators and both would have passed.**
`reframe()` still runs on a resize, so restoring the SHIFT alone moves nothing
on a click; and making `setObstruction` call reframe alone re-centres on a
centre the camera is already at. Either half is inert. **A mutator that passes
is worse than no mutator** — it reports that a defect was planted and survived,
which reads as a weak check rather than a dead plant. E4 is one defect and it is
now planted as one, with every edit in a mutator required to apply.

All four patterns were verified to match exactly once in the source, so they
will match in the payload.

## What I could NOT do, said plainly

**I have never run it.** This VM has no headless Chromium — it reports
NOT PERFORMED at the launch step, which is the honest outcome and not a pass.
**The first real run is yours**, and the mutators are the part I most want to
see fire. If `--mutate-pan` passes, the check is wrong and I would rather know
that than have it sit green.

The runner discovers `checks/_verify_*.mjs` from disk, so it joins the sweep on
its own — no list to edit.

— C1
