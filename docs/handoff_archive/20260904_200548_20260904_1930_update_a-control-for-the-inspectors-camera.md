# Update — the inspector now has a control, and it caught a defect in itself first

**2026-09-04 · Code**

Written: `checks/_verify_inspector_nose.mjs`. **RULE16: INDEPENDENT.**

## Why

Nothing anywhere asserted anything about `_inspect.html` - `grep -l _inspect
checks/_verify_*` returned nothing. A page that now ships 256 CIG models, that
Sleven is walking one ship at a time, with two defects found in it today by him
looking at it, had no control at all.

**And the orientation bug was the second instance of the same defect.**
`cc_viewer.js` opened at +Z until this morning; `_verify_camera_framing.mjs`
section 3 holds the site to -Z now, with a `--mutate-behind` mutator, and I
confirmed it still fires. `_inspect.src.html` was written separately and made the
identical assumption independently. The site's copy was caught by a control. The
inspector's was caught by **Sleven walking ninety-three ships and writing "shows
facing away from the user" on twenty of them before he stopped bothering.**

The convention is measured in `place_hardpoints.py` lines 28-34 and was enforced
in exactly one place. Now two.

## What it does

Serves the built `testing/_deploy` over a local static server, loads the real
`_inspect.html` in a real headless Chromium, drives the page's own `go(n)` for a
sample spread across the list, waits for the real GLB to decode, and reads
`cam.position.z` against the loaded model's own bounding-box centre.

It asks **which side**, not which angle. A control that pinned the angle would go
red on any legitimate reframing, and that is how a control gets relaxed in a
hurry and stops meaning anything.

    100i             camZ -16.47   radius 10.53   nose
    Caterpillar      camZ -93.10   radius 59.54   nose
    Freelancer MIS   camZ -34.69   radius 22.19   nose
    MPUV Cargo       camZ -10.37   radius  6.63   nose
    Reliant Kore     camZ -27.39   radius 17.52   nose

**Proven against known-bad input.** `--mutate-behind` restores `0.9` in the bytes
the browser parses - the exact defect - and every camZ flips sign:

    100i  +16.47 TAIL   Caterpillar +93.10 TAIL   Freelancer MIS +34.69 TAIL
    MPUV Cargo +10.37 TAIL   Reliant Kore +27.39 TAIL       FAILED 5 of 6

## It passed for the wrong reason first, and that is worth recording

The first version waited on `while (!current)` before measuring. `current` still
holds the PREVIOUS ship, so that returns instantly: it measured the last hull
over and over and reported five green assertions.

**What gave it away was the data, not the exit code.** 100i and Caterpillar both
came back camZ -16.47 radius 10.53, and Freelancer MIS and MPUV Cargo both
-93.10 / 59.54. Two different ships cannot frame identically. It now waits for
`current.uuid` to CHANGE, and every hull reports its own numbers.

A control that measures the ship before the one it names would pass with the
named ship loaded backwards - which is the entire defect it exists to catch. It
would have been a green control over nothing, written the same afternoon I spent
an hour arguing with a control that was right.

The reasoning is written into the file at the point of the fix, not tidied away.

## Scope

`checks/` is Code's by default under OWNERS.md and this file is not in C1's list.
It asserts behaviour of a page C1 owns, which is the normal arrangement - Code
writes the suite, C1 contributes controls and names them there when it does. No
C1-owned file was touched.

Not added to any deploy gate by hand: `run_all_controls.py` discovers
`checks/_verify_*.mjs` by glob, so it is swept from the next run without being
listed anywhere.
