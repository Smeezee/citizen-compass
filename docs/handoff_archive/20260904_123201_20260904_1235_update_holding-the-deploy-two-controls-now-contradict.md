# Update — holding the inspector deploy. Two controls now assert opposite things.

**2026-09-04 · Code**

Sleven said go. **I have not deployed, because the gate will not pass this and
should not.** Reporting rather than reaching for `-IgnoreSweep`.

## The sweep

    114 passed, 2 failed, 3 skipped, payload adad57991845bc71

    FAILED  _verify_holo_render.mjs
    FAILED  _verify_rule16_labels.py

Neither is mine and neither is the inspector.

## 1. Two controls now disagree about DoubleSide

Another session is fixing see-through hulls - `docs/see-through-ships-2026-09-04.html`,
and a new control `checks/_verify_hull_is_solid.mjs` created at 12:11:23. Its own
header states the case well: glTF defaults `doubleSided:false`, nothing set
`material.side`, and **3,287,114 of 139,487,571 triangles across 258 models are
wound backwards, visible on 32 hulls.**

`testing/_src/cc_viewer.js` was rewritten at **12:10:37** and now carries ten
`DoubleSide` references where it carried five.

**`_verify_holo_render.mjs` asserts the opposite** and is now red on six styles
at once:

    FAIL solid uses no DoubleSide pass
    FAIL panel / solidlines / hull / wire / points - same

So one control requires DoubleSide and another forbids it, on the same property,
in the same file. `_verify_hull_is_solid.mjs` passes; `_verify_holo_render.mjs`
fails; both are green-or-red about a deliberate change.

**This is not mine to settle.** `cc_viewer.js` is C1's, the see-through fix is
C1's work in flight, and whether the holo styles should now be double-sided is a
rendering decision. `_verify_holo_render.mjs` is Code's by default, so if the
answer is "the old control is wrong now", I will change it - **on an order that
says so.** I am not going to relax an assertion to make a red suite green,
which is the one move that turns a control into decoration.

## 2. A new control with no RULE16 label, again

`_verify_hull_is_solid.mjs` opens `RULE 12 + RULE 16 control`, which is prose,
not the label. The gate wants `RULE16: INDEPENDENT` or `RULE16: UNPROVEN`
followed by a reason.

**I labelled the last one of these myself this morning and said so loudly.** I
am not doing it twice unasked - two in one day is a pattern, and the pattern is
better fixed by whoever is writing the controls than by me relabelling their
work behind them.

## 3. My payload is stale, and I would not deploy it even if the sweep were green

I built at 12:08:18. `cc_viewer.js` changed at 12:10:37 - **two minutes later.**

    testing/_deploy/cc_viewer.js    5 DoubleSide references
    testing/_src/cc_viewer.js      10

So the built payload predates the viewer change and does not match the source it
came from. Rebuilding would bake another session's in-progress rendering work
into a deploy while the control that governs it is red.

**This is the ninety-second race from this morning's order, running the other
way.** That order was written because a build beat an edit; this time an edit
beat the build. I checked the source had settled for three minutes before
building, and it moved anyway.

Also: `testing/_deploy/cc_viewer.js` has an mtime of 12:30:12, during my sweep,
which means something rebuilt part of the payload while it was being swept.

## What is actually ready

The inspector work itself is done and clean:

    _inspect.html built, 1,154,730 bytes, trademark bar present
    258 .glb models on disk, matching what the page expects
    _verify_no_leaked_comments.py   23 pages, clean
    check_deploy_clean.py           safe to deploy

**It needs one clean moment to go out in.** When the viewer work lands and its
two controls agree, I rebuild and deploy in two commands.

The source-notice gap from my 12:15 update is unchanged and separate:
`data-layer/cig_assets.json` does not exist, so no page carries the source and
takedown notice. Reported, not touched (rule 8).
