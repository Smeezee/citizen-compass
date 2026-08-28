# Update — Sleven: *"the retaliator quad is right, re-baseline it"*. Starting, and saying what I am about to overwrite before I do.

**2026-08-27 21:31 local · Code (background session)** — the decision that was
blocking `_verify_child_markers.py`.

## Two things have to move, not one

1. **`PINNED`** - four Retaliator coordinates hard-coded in the control as
   "correct before this work". Sleven has now said the new mirrored quad is
   right, so these become the new four.
2. **`BEFORE`** - `data-layer/derived/holo-hardpoints/loadout_marker.pre-C1-20260826.js`,
   the snapshot taken by re-running the real build with `CC_NO_INHERIT=1`. It
   predates the CIG overlay, so today it measures the overlay rather than the
   inheritance pass, which is C1's diagnosis and I agree with it.

## The order, and the risk in it

`CC_NO_INHERIT=1` runs the REAL build, so it overwrites the shipped
`loadout_marker.gen.js` and the whole `_deploy` payload with the BEFORE state.
**A re-baseline that leaves the no-inherit build on disk would ship a page with
4,273 fewer markers.** So:

    1. copy the current shipped marker file aside
    2. move the old baseline into _to_delete/ - not overwritten, rule 1
    3. build with CC_NO_INHERIT=1, capture the BEFORE
    4. rebuild normally and CHECK the marker file is byte-identical to (1)
    5. only then update the control

**And I will record the derived-data mtimes either side.** C1 rewrote the client
overlay at 21:10:48 tonight, mid-deploy. If it moves between my two builds the
BEFORE and AFTER differ by more than the inheritance pass and the snapshot is
worthless - that has to be checked, not hoped.

Nothing committed, nothing pushed, live site untouched.
