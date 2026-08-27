# Update — Scale fixed on disk and proven. NOT built, NOT deployed.

**2026-08-27 13:45 · Code (background session)** — unit of work finished.
Sleven interrupted before the rebuild, so the state is worth stating exactly.

## All 19 are now the size their own record says

`checks/_verify_model_scale.mjs` — **GREEN, ratio 1.000 on every one.**

    Odin      752.00 m     Merchantman 193.50 m    Arrastra 124.00 m
    Tiburon   121.00 m     600i Exec    91.50 m    Tyilui    69.00 m
    Hermes     65.00 m     MOTH         45.00 m    M80/Starlite 32.00 m
    Mantis     30.00 m     Aurora Mk II 27.50 m    Aurora SE 18.50 m
    Basher     16.75 m     85X          14.00 m    Fury       7.00 m
    Pitbull     5.90 m     UTV           4.00 m    PTV        3.00 m

The rule: largest model dimension equals largest published dimension, both
axis-independent. The published figures come from the SAME Fleetyards record the
model came from, so there is no join to get wrong.

**Validated before it was applied**, against five ships already known correct —
measured over published: Caterpillar 1.001, Hammerhead 1.011, Arrow 1.031,
Gladius 0.941, 100i 0.920. So the target is good to about 8%, and that number is
stated rather than implied.

## The control is the real defect, not a simulated one

    node checks/_verify_model_scale.mjs --control-old

serves the actual pre-fix models out of `_to_delete/` and every assertion must go
red. It does: **16 of 19 fail**. The three that pass are 600i Executive Edition,
85X and Mantis — **the three that were already correct before the fix**. So the
check discriminates rather than simply failing everything it is shown, which is
the difference between a control and a formality.

## Two things went wrong on the way, both caught by guards rather than by luck

**1. The 85X missed its target on the first attempt** — 19.13 m against 14.00.
The Blender step scaled every parentless object; that is right for a flat scene
and landed 18 of 19 exactly, but the 85X has 985 objects in a hierarchy where it
does not hold. **The run refused to install ANY ship** rather than 18 good ones
and one wrong one, which is why nothing had to be unpicked.

Fixed by parenting everything to a single new empty at the origin and scaling
that. One transform, above every object, applied once — it cannot compound
through a hierarchy and it cannot miss a branch, whatever the source looks like.
Re-run: all 19 exact, 85X included.

**2. A `*/` inside a block comment** — the path `pre_scale_fix_*/models/` closed
the comment early and the check would not parse. Caught immediately because the
check was run rather than assumed to work.

## WHERE THIS LEAVES THE LIVE SITE

**The testing site still serves the WRONG-SCALE models.** The fix is on disk in
`testing/_deploy/models/` but `build_deploy.py` has not been re-run and nothing
has been uploaded. Until it is, Sleven is looking at the 13:20 deploy.

Nothing is broken by that — the viewer frames the camera to whatever it loads, so
the old models still render correctly, just in the wrong space.

## Rule 1 observed

Every replaced file was MOVED to `_to_delete/pre_scale_fix_20260827T173231Z/`,
not deleted. That directory is also what the control reads, so deleting it would
disarm the control.

Nothing committed.
