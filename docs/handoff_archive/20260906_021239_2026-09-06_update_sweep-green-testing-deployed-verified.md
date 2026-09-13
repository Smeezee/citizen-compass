# Update - THE SWEEP IS GREEN AND TESTING IS DEPLOYED AND VERIFIED FROM SERVED BYTES.

    120 ok, 0 failed, 3 skipped, 0 NOT RUN, in 1885s
    receipt 2026-09-06T02:09:38   fingerprint 53676ee77da95f1f
    exit 0

Zero failed and zero NOT RUN. The three skipped are the deployed-only controls,
as always.

## Deployed - TESTING ONLY

    https://citizencompasstesting.citizencompass-contact.workers.dev
    Version ID de3a43f1-f3cd-4b5b-bba5-ea408f992337
    524 files, 517.9 MB, 256 models

**I did NOT rebuild first**, deliberately. The 2026-09-05 addendum's lesson is
that a rebuild changes the payload fingerprint and invalidates the receipt, so
the gate would then refuse. The sweep ran against this exact payload and the
script confirmed it: *"120 control(s) green against this exact payload"*.

**One file changed on the wire: `/loadout_marker.gen.js`.** 523 of 524 were
already uploaded. That single file IS tonight's work reaching the site - the
markers re-fitted by C1's `hull_box()` correction on the seven hulls.

No `-IgnoreSweep`. The live Netlify site was not touched and this script cannot
touch it.

## Verified from SERVED BYTES, not from exit code 0

The script says in its own words that exit 0 is not proof. So:

    /                       200, 396,153 bytes
    title                   "Citizen Compass v0.4.0 - testing 2026-09-06"
                            - the testing stamp, dated today
    id="cc-kb"              present in the served HTML
    id="cc-panel"           present in the served HTML
    /models/Hammerhead.glb  200, 4,153,816 bytes, model/gltf-binary
    /index.html             307 -> /  (the gate normalising, not a failure)
    private-preview gate    present in the served markup

**And the file this deploy existed to ship, byte for byte:**

    served sha256  a6cf733fa0584764   289,793 bytes
    local  sha256  a6cf733fa0584764   289,793 bytes
    IDENTICAL

## The whole night, closed out

    DONE   exit-2 relabelling            19 sites, 12 files, 18 proven by firing
    DONE   _verify_g3_matcher_delta.py   re-pinned to names
    DONE   _verify_stage_floor.mjs       both tails pinned by name
    DONE   _verify_hardpoint_join.py     split in two, mutation-proven
    DONE   _verify_placer_candidates.py  7 declared by name, proven both ways
    DONE   _verify_holo_render.mjs       Step B on the Liberator + ratio control
    C1's   _verify_marker_census.py      green, hers
    C1's   _verify_child_markers.py      green, hers
    DONE   sweep green, TESTING deployed and verified

## Nothing committed, nothing pushed

Rule 2. The work is in the working tree and reported. No `git add -A` was run.
Sleven's explicit go-ahead is what commits this, and he has not given one.

## Still open, for the queue - none of it touched tonight

1. **14 hulls over the 5% pure-white threshold** in section 5's own model, max
   9.21% (Dragonfly Yellowjacket), confirmed through the control's own code
   path. Real or a sampling artefact of the 80,000-point cap - unanswered.
2. **Section 5 tests one hull and reads as if it tested the fleet.**
3. **C1's ordering finding** - a control reading a build artefact it does not
   rebuild reports on whatever the last build left. Queued by her, not mine to
   close.
4. `_verify_placer_candidates.py` raises a bare `FileNotFoundError` where a NOT
   PERFORMED belongs.
