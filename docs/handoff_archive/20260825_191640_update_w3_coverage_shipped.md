# Update — W3's page half shipped and deployed. Version 1be24081.

**Deployed to testing: `1be24081-3fac-489d-9dd3-f39562b79e6a`.** Not committed.

## What changed on the page

`renderMarkerNote()` now opens with the ratio. A hull with a shortfall says
**"Showing 4 of 24 weapon mounts"**, names how many have no derived position,
says they are still in the list on the left, and ends **"That is thin data, not
a broken page."** A hull with every mount marked says **"All N of this ship's
weapon mounts are marked"** and is never told it is missing any.

**Counted from the same set the generator uses.** `weaponMounts()` reads
`MARKABLE`, which is `build_deploy.py`'s `WEAPONY`. A second definition of "a
port that could carry a marker" would let the page claim coverage it does not
have.

**The five Sleven filed as "hardpoints not set up":**

    Retaliator             4 of 24
    Ballista               2 of 15
    Ballista Dunestalker   2 of 15
    Ballista Snowblind     2 of 15
    Sabre Peregrine        2 of 2   - FULL coverage in our data

**The Peregrine is a different answer and the control found it, not me.** Its
bench record lists only two weapon mounts, so its two markers are everything
there is. Asserting "showing 2 of 30" on all five would have hard-coded the
order's assumption into the check. It now says "All 2 ... are marked".

## Control

`checks/_verify_marker_coverage.mjs` — 20 assertions. Opens **all 159 marked
hulls**, reads the note the page actually rendered, and compares the printed
ratio against a count the control computes itself. Passing on the Retaliator
and printing nonsense for the other 158 would fail here.

    normal              exit 0
    --deployed          exit 0 - same assertions against testing/_deploy bytes
    --self-test         exit 1
    --mutate-silent     exit 1 - 153 hulls go silent, the state Sleven found
    --mutate-total      exit 1 - denominator taken from the markers, so every
                        hull claims full coverage. The tempting shortcut.

Negative half: the Eclipse (mounts, no markers) keeps E1's absence wording and
does NOT gain "0 of 24"; the CSV-SM (no mounts at all) is told nothing about
counts; the Peregrine is not told it is missing any.

**Served bytes proven:** `_verify_picker_deployed.mjs` reports the served page
byte-identical to the built one, and the coverage control drove those built
bytes with `--deployed`.

## Three pre-existing sweep failures found, two fixed, one reported

Sweep before this work: **72 ok, 4 failed, 3 skipped.** None of the four were
caused by the W3 change.

**1. FIXED — `missing_or_corrupt_3d_model_check` invented a seventh missing
model.** It scanned every directory under `sc-ships/` that did not start with
`.`, so the empty housekeeping folder `_corrupt_backup` was reported as a ship
with no `model.glb`. **A fabricated DEFECT hiding inside a true count** — and
it broke `_verify_broken_checker_end_to_end.py`, which pins the number of
genuinely-missing models at 6. Underscore-prefixed directories are now
excluded; that end-to-end guard is green again, 12 assertions, and the six real
ones (85X, Arrastra, Fury, Mantis, Merchantman, PTV) are unchanged.

**2. FIXED — `_verify_edge_detail.mjs` asserted a constant that G1 retired.**
It required the glow default to be 0.04. E7b chose 0.04 when the rim term was
`fres*(1.15*uGlow/0.55)` over a surface at 9% luminance; G1 replaced both
halves and the coefficient is 6.8x smaller, so the shipped default is 1.0 and
`cc_viewer.js` states the arithmetic. **The assertion was updated, not
deleted** — a drift to any other number still goes red.

**And its mutator had gone quietly half-dead.** `--mutate-hotdefaults` planted
three defects and checked only whether the whole string had changed, so its
`glow: 0.04` replacement had been matching nothing since G1 landed while the
run still claimed to have mutated. Each edit is now verified on its own and the
mutation fires all three.

**3. NOT FIXED, REPORTED — `_verify_stage_floor.mjs` cannot run.** It crashes:
`TypeError: this.camera.updateMatrixWorld is not a function`. `_fitProjected()`
in `cc_viewer.js` needs a camera with a real projection and the control's
hand-written THREE stub has `updateProjectionMatrix(){}` and nothing else.
**E5's stage-floor guarantee is currently unverified.** The fix is a real
perspective projection in that stub; bolting on a no-op `updateMatrixWorld`
would make the control pass while measuring nothing, which is the exact defect
rule 12 names. **Left red and reported rather than made green.**

**4. Still skipped — `_verify_g3_matcher_delta.py`** reports NOT PERFORMED
because `CC_GEO_DIR` is unset. It says how to regenerate. Honest skip, untouched.

**Also noted, not touched:** the encoding checker reports 28 pre-existing
`open()` calls with no `encoding=` across `audit_ship_components.py`,
`image_handling.py`, `_verify_community_mark.py` and
`_verify_turret_inheritance.py`. None in anything written today.

## Numbers from the build

    hull markers: 1210 on 159 hulls, 14 ambiguous dropped,
                  599 placed points matched NO weapon port

**That 599 is the parent/child gap quantified** — placed points naming a turret
mount that the ship page lists only as the guns hanging under it. Raising W3
coverage means closing that, which is the deferred B5 inherited-sibling job.
