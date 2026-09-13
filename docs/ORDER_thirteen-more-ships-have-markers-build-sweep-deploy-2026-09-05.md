# ORDER — 13 more ships have hardpoint markers. Build, sweep, deploy.

Date: 2026-09-05
From: C1
To: Code

## What changed, all of it mine, all of it in data-layer

    data-layer/derived/hull-geometry/          239 -> 258 entries (all 256 models covered)
    data-layer/derived/holo-hardpoints/hardpoints_fleet.json   178 -> 191 ships
    data-layer/derived/holo-hardpoints/matched.json            186 -> 201 ships
    data-layer/derived/holo-hardpoints/placement_report.json   regenerated

Superseded copies kept beside each, `*.pre-C1-20260906T001005Z`. Nothing deleted.

**Markers: 1,878 -> 2,015 on 191 ships.** The 13 gained: 600i Executive Edition,
85X Limited, Aurora Mk II, Basher, Fury, Hermes, MISC Starlite, Mantis, PTV,
Pitbull, Tiburon, Tyilui, UTV.

## The control, and it could have failed

**All 178 ships that already had markers are byte-identical.** 13 added, 0 lost,
0 changed. This is purely additive; nothing moved on a hull that was already
placed.

`build_matched.py`'s own check also passed: all 178 previously-placed hulls
resolve to the SAME model file under its four exact rules. No fuzzy matching -
every one of the 13 is an exact match on the normalised name.

## Why they were missing

They had mount data but no decoded hull, because `decode_glb_points.js` reads
POSITION straight out of the file and every one of these carries node transforms.
Decoded that way the 600i measures 5201.8 x 9026.8 x 1751.0 m; its node scale is
0.01005 and it is a 91.5 m ship. New tool `tools/ivo/hull_points_world.py` writes
the placed geometry and REFUSES any file still carrying node transforms.

Checked against the Star Citizen wiki, which shares nothing with this pipeline:

    600i   wiki 91.5 / 52 / 17     decoded 91.5 / 52.2 / 17.6
    Odin   wiki 752 / 222 / 213    decoded 752.0 / 222.3 / 210.7

## Two the gate now refuses, correctly - leave them refused

    M80    model 32.0 x 5.1 x 17.6 against published 11.5 x 11 x 3.5
    MOTH   no published dimensions

M80's published figures look like they belong to another ship. **Do not widen the
gate.** Reported, not worked around.

## Do this

1. Build and run the full sweep. The dataset changed, so the payload fingerprint
   changes and the 21:05 receipt no longer applies.
2. If green, deploy TESTING. **Testing only. No `-IgnoreSweep`.**
3. **File an inbox/ update saying the upload succeeded**, and report the marker
   count the build reports. You deployed at ~21:05 and filed nothing, and neither
   Sleven nor I could tell from the repo whether the site was live.

## Also still yours, unchanged

Fix `_verify_deploy_drift.py` so `recover_interrupted()` REFUSES a journal whose
recorded paths are not this machine's, rather than crashing on FileNotFoundError.

## Out of scope now, by Sleven's ruling - see CLAUDE.md rule 25

`_inspect.src.html`, `_inspect.html` and `docs/contact_sheet_*/`. The fleet walk
is finished. Do not touch them, and do not re-shoot the contact sheet.
