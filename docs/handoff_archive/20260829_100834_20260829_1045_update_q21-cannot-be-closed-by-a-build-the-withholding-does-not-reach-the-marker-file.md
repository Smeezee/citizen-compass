# Update — Q21's DONE-WHEN cannot be reached by a build. The fore/aft withholding lands in a directory the marker pipeline never reads. Measured, not inferred.

**2026-08-29 10:45 local · Code (background session)**

I ran the build. **It exited 0 and produced a payload BYTE-IDENTICAL to the one
already in `testing/_deploy`.** Not one marker moved.

    hulls    259 -> 259        markers  6058 -> 6058
    every hull that lost a marker:  none
    BANU_Defender  before 8  after 8   removed: none
    MISC_Hull_C    before 23 after 23  removed: none

## WHY, AND IT IS NOT THAT THE BUILD FAILED

**The fore/aft change is real and it IS in C1's script.** `build_hardpoint_placement.py:580`
now loops `for i in (0, 1, 2)`, and `BANU_Defender.json` records the result:
*"4 of 11 exterior mounts withheld"*. That work is done and I am not disputing it.

**It lands in `data-layer/derived/hardpoint-placement/`. The marker file is not
built from that directory.**

    build_deploy.py:1309   data-layer/derived/holo-hardpoints/hardpoints_fleet.json
    build_deploy.py:1398   data-layer/derived/holo-hardpoints-align/fleet_records_client.json
    build_deploy.py:1413   data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json

    grep hardpoint-placement testing/_src/build_deploy.py
      -> one hit, line 1560, about model substitutions. Nothing else.

`hardpoints_fleet.json` is dated **2026-08-26** and is the file that decides
which hulls get markers. **A withholding written into `hardpoint-placement/`
cannot reach `loadout_marker.gen.js` through any build.**

The port numbering says the same thing out loud: the marker file's
`BANU_Defender` carries ports **0, 1, 58, 62**. There is no port 50 or 51 in it
to remove, and there never was.

## SO Q21'S PREMISE IS WRONG, NOT ITS GOAL

*"only the deployed marker file is behind"* — it is not behind. It is built from
a different source than the one that was fixed. **Re-running the build is not
the missing step, and I could run it a hundred times.**

I checked the two obvious alternatives before saying this:

    build_hardpoint_overlay.py   edited 09:45, AFTER its 09:19 output - but the
                                 change is a COMMENT ONLY (the place_fleet
                                 erratum). Re-running it changes no numbers.
                                 It also landed with a typo: "So. So".
    a stale MANIFEST.json        still carries the old "marking our own
                                 homework" sentence at 09:19, while the script
                                 that wrote it no longer believes it.

**This is C1's call, not mine.** `hardpoints_fleet.json` and the align
directory are C1's in `OWNERS.md`, and the question — whether the withholding
should propagate into the marker pipeline, or whether the marker pipeline should
read the placement directory at all — is a data-model decision, not a build step.

**Q26 inherits this.** Its line *"seven of the ten are the fore/aft escapees Q21
removes"* does not hold: Q21 as written removes none of them.

## WHAT I AM STILL DOING

The served site is on 04:47 and the local payload is genuinely newer — today's
client overlay regeneration is in it. **So I am sweeping and deploying anyway**,
which fixes the staleness Sleven actually named. **It will not remove the three
dots**, and I would rather say that before the deploy than have it discovered
after.

## AND ONE DEFECT IN MY OWN MORNING'S FIX, FOUND BY THIS

The deployed marker file changed from `ef9be07` to `2536dbd` without a
deliberate build. **I killed a sweep mid-run, and a killed process does not run
`finally`** — so the drift control's rebuild survived and its restore never
happened. My restore is exception-safe and **not** kill-safe, and I described it
this morning as if it were both. Fixing that before the sweep, not after.
