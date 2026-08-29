# Update — Q7 tranche 7: the viewer family. 71 of 104, and five of these nine earned INDEPENDENT.

**2026-08-28 11:22 local · Code (background session)**

    labelled     71  (31 INDEPENDENT, 40 UNPROVEN)     was 62
    unlabelled   33                                    was 42

Nine rendering controls. **All nine green after labelling.**

## THE FIVE INDEPENDENT ONES, AND WHY THIS FAMILY EARNS MORE OF THEM

Rendering is where independence is easiest to get, because there is somewhere
else to look:

**`_verify_camera_framing.mjs`** serves the real payload over HTTP and drives a
real browser. Its own header calls itself *"the first control in this repo that
sees what a visitor sees"*. **It does not ask the viewer anything; it looks at
the result.**

**`_verify_colour_headroom.mjs`** RE-IMPLEMENTS the shader's arithmetic. The
constants are pulled out of the viewer by regex and the multiplier and knee are
computed in the control, so the two implementations must agree - the same shape
as `_verify_placement_gate.py`, this repo's exemplar for the pattern.

**`_verify_palette.mjs`** implements the dichromacy transform itself **and proves
its own instrument before using it**: white must stay white, blue must stay blue
under protanopia, red must land on a known value. *A control whose measuring
device is unverified is measuring nothing*, and this one checks the device first.

**`_verify_shared_viewer.mjs`** breaks the shared module and requires both pages
to fail. A page can load `cc_viewer.js`, ignore it entirely, and satisfy every
positive assertion about sharing - it cannot survive the module being broken.

**`_verify_edge_detail.mjs`** compares the shipped constants against the
prototype's own captures - a number the viewer did not produce. Its risk is
staleness rather than circularity, **and it has already been paid once**: the
header marks the glow figure SUPERSEDED after G1 rebuilt the rim term and 0.04
stopped describing anything.

## THE FOUR UNPROVEN, AND ONE OF THEM SAID SO FIRST

**`_verify_hull_solid.mjs` labelled itself before rule 16 existed.** Its opening
paragraph is titled *"WHAT THIS CONTROL CANNOT DO, FIRST, BECAUSE IT BOUNDS
EVERYTHING BELOW"* and explains that the order's load-bearing control is a pixel
measurement of an eroded silhouette, which C1 produced from a headless browser
and this file cannot. The rule 16 label had almost nothing to add.

`_verify_holo_render.mjs` reads the viewer's own uniforms before and after, so a
viewer reporting a change it did not make would pass - **but the label names
where that question IS answered**: whether a moved value reaches a pixel is
`_verify_camera_framing.mjs`'s subject, and that one is independent.

`_verify_stage_floor.mjs` drives the viewer's own `frame()` and `_fitTable()`;
its independent half is the population - every hull, not a chosen few.
`_verify_spin_default.mjs`'s independent half is the SEQUENCE it imposes: open
cold, stop, reload, open a different ship.

## A THIRD COMMA, AND THE GATE I JUST FIXED IS WHY IT COST NOTHING

I wrote `RULE16: UNPROVEN, and this file already said so...` - the same malformed
shape as C1's and as my own an hour ago. **Third time.** The verdict wants a
separator and the natural English sentence wants a comma.

It cost one dry-run cycle instead of an hour, because the applier's report
column showed the whole run-on where a one-word verdict belongs. The gate would
also have named it correctly now, which it would not have this morning.

**Three occurrences in two people in twelve hours is a format problem, not three
careless mistakes.** The gate accepting a comma would be the wrong fix - the
separator is what makes the reason machine-readable - but it is worth saying
that the trap is in the format rather than in the typing.

## Where Q7 stands

    71 of 104 labelled       33 to go
    31 INDEPENDENT           40 UNPROVEN

Nothing committed since `1a1b4b7`.
