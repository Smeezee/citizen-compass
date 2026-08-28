# Update — Sleven: *"suppress the duplicates, then run the remaining six"*. Starting.

**2026-08-27 21:18 local · Code (background session)** — the decision I asked
for at 21:01, answered.

## What I am about to do

1. **Suppress coincident markers in the emitter.** Where two markers on one hull
   would land on the same coordinate, emit one. The six pairs are CIG's own
   left/right channels of a single physical rack or launcher, measured and named
   in the 21:01 note. The build already drops ambiguous points and says how
   many; this will be reported the same way rather than done quietly.
2. **Rebuild, re-verify, deploy to testing** - the standing instruction is that
   the day's work reaches the test page the same day.
3. **Run the remaining six sweep failures**: `_verify_broken_checker_end_to_end`,
   `_verify_dim.mjs`, `_verify_g3_matcher_delta`, `_verify_model_resolution`,
   `_verify_ship_page.mjs`, `_verify_stage_panel.mjs`.

## What this does NOT unblock

`_verify_child_markers.py`'s **re-baseline is still on hold.** Suppressing the
duplicates closes one of the two blockers I named. The other stands: nobody has
said the Retaliator's new mirrored quad is RIGHT rather than merely tidier, and
a snapshot taken now would bake those four in. I will not take it on my own
reading of the geometry.

Nothing committed, nothing pushed, live site untouched.
