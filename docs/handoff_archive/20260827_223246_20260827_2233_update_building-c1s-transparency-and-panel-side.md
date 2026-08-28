# Update — Sleven: *"build and deploy it"*. Building C1's two changes, with the provenance recorded rather than waved through.

**2026-08-27 22:33 local · Code (background session)**

## What is being shipped, and where it came from

Two changes written directly into `testing/_src/` by C1 at 22:10:29 and
22:15:22 — a rule 14 breach in the channel, caught by
`_verify_deploy_drift.py`, reported at 22:28, and **now authorised by Sleven in
this session**:

    cc_viewer.js       hullAlpha 0.86 and a uAlpha shader uniform - the hull
                       reads translucent instead of solid
    loadout.src.html   the panel opens on the side of the SCREEN the marker is
                       on, and the viewer no longer pans the ship to make room

**Rule 14's requirement was "make an unauthorised write loud and immediate, and
refuse to ship un-provenanced content."** It was made loud, it was reported, and
it is no longer un-provenanced: Sleven has now looked at it and said ship it.
That is the rule working, not the rule being bypassed.

## Checked before building

Nothing has been written since **22:22:32**, which was the drift control's own
rebuild. C1's source edits are the newest hand-made change and the derived data
has not moved since 21:10:48, so this is a stable snapshot rather than a moving
one.

## After the deploy I will re-run `_verify_deploy_drift.py`

It is red right now **because** `_deploy` and `_src` disagree. A deliberate build
is what makes them agree again, so that control going back to 12/0 is the proof
that the payload is what the source says it is — not a separate errand.

Nothing committed since `2fc7008`. Live site untouched.
