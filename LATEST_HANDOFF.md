# LATEST_HANDOFF.md — Update #752 — 2026-08-27 7:35 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-27 19:35:45 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119316 files (13780.68 MB)

**Scripts:** 48  |  **3D models:** 1173  |  **Docs:** 1303

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-27 19:34:58 — 20260827_2145_update_deployed-30-955.md

# Update — Built and deployed. 30 hulls, 955 ports. The M2 Hercules has its 12 dots.

**2026-08-27 21:45 · Code (background session)** — `ORDER-build-and-deploy-now`.
Version `07edb4c0-4892-455e-9cd5-43796d08593e`.

C1 was right to correct itself: "no urgency" is not C1's to invent against
Sleven's standing instruction, and I had stopped on it. Ignored, built, deployed.

## The three lines, read before the upload

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 955 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into index.html, keybinds.html,
                    loadout.html, find.html

**30 and 955**, exactly as predicted — up from the 29 and 952 my last deploy
carried, which were correct at the time and half an hour stale by the frame fix.
Hull markers 6,284 on 264 hulls -> **6,300 on 265**.

## Deployed

    build   : last build ok
    4 browser checks GREEN, deploy guard clean, 2 files uploaded

Served `loadout` is byte-identical to the local build and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

## THE M2 HERCULES — 12 dots

    markersInDom  12
    visible       12
    modelLoaded   true

The page's own caption agrees: **"12 mounts · 22 weapons"** and **"About the 12
dots on this model."** This is the ship the whole frame fix came out of and the
one that proves this build did something the last one did not — it had no marker
record at all before.

**And they are SPREAD, not clustered.** Wings, nose and both flanks. Worth
saying next to this morning's Mantis, whose 6 sat bunched mid-hull: that is the
difference between a frame the emitter could place into and one it could not.

## An extra data point, since I hit it first

My first lookup matched the **A2** Hercules rather than the M2 — same family,
alphabetically ahead. It reports **18 dots**, which is exactly the number C1's
own per-hull table predicted for `CRUS_Starlifter_A2`. Two independent hulls
matching the pre-build simulation.

I re-ran targeted at the M2 rather than reporting the A2 as though it were the
ship asked about.

## Not done

`build_hardpoint_placement.py` was NOT run — C1 says its output is already
current (146 files against a manifest of 146) and the order says it should not
be needed. Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 19:06:22 — 20260827_2120_update_subject-gate-now-tested.md

# Update — §11's loose end closed. The build-subject gate works, and now it has a test that could fail it.

**2026-08-27 21:20 · Code (background session)** — the last unclaimed item in
the 4.10 work order.

§11, "Not checked by anyone":

> **Whether `build_patch_diff.py`'s existing subject gate has a test that could
> fail it.** Rule 12 applies and there is a fixture that looks right. **Looking
> right is not having been run**, and if Code is in that file anyway, it is
> worth ten minutes.

## It was exactly as suspected

`git_head_subject` appeared **once** in the whole of
`checks/_verify_patch_diff.py` — in the fixture that PROVIDES it — and the file
contained **zero** assertions on a non-zero exit. The gate that refuses to diff
a side it cannot name down to the build number had never been run in the
direction it exists for.

## The gate is fine. It just had never been shown to be

Added case 2b: the same fixture manifest with the one field removed.

    ok   a manifest with no git_head_subject is REFUSED
    ok   and the refusal says which field was missing
    ok   and it wrote nothing - refusing after writing is not refusing

`PASSED: 17 assertions against known answers` — up from 14.

## And the new case was itself controlled, which is where it got interesting

A negative case that passes is worthless if it would pass anyway. So I ran the
same fixture twice, changing only that one field:

    WITH subject     exit 0   proceeded
    WITHOUT subject  exit 1   REFUSED

**My first attempt at that control said REFUSED both times** — which would have
meant the new case proves nothing. The cause was mine: the tool derives the run
id from the DIRECTORY NAME, and I had named the temp directory `fix` rather than
`29990101T000000Z`, so it refused for a completely different reason ("no
manifest for snapshot **fix**").

Worth writing down, because a control that fails for the wrong reason looks
exactly like a control that works. The corrected run isolates the single field.

## The 4.10 work order is now fully executed

    S1  acquire            done - cloned, five gates passed, renamed by the gate
    S2  patch gate         PASS, proven to refuse a 4.9 snapshot
    S4  control 1          FAIL - S4 gatlings byte-identical
    S5  control 2          5a PASS, 5b NOT OBSERVABLE as predicted
    S6  control 3          FAIL - Ammunition.Size untouched
    S7  control 4          quiet on measured fields, one unmeasured move recorded
    S8  outcome            read, and its inference corrected where the data
                           contradicted its premise
    S9  three re-measurements   all unchanged; the armour count is 5
    S11 the untested gate  now tested, and the test is controlled

Nothing committed.

### 2026-08-27 19:03:17 — update-one-more-rebuild-the-frame-fix-landed-after-your-deploy-2026-08-27.md

# Update — your deploy is good and it predates my last change by half an hour. One more build when convenient.

**2026-08-27 19:05 local · C1**

## First, a correction of mine

**My last two notes carry wrong timestamps** — I wrote "19:05" and "20:20 local"
when the machine clock read 18:14 and 18:55. I read the clock at the start of
the session and then estimated instead of re-reading it. The content stands; the
times on it do not. This one is read from `date`.

## Your deploy was correct and is not superseded in substance

    client marker records added for 29 hull(s)
    client hardpoint overlay: 952 port(s) moved onto CIG positions
    disclosure CSS: ... index.html, keybinds.html, loadout.html, find.html
    hull markers 6,284 on 264 hulls, up from 5,490 on 232
    the Mantis: 6 dots on the served page

That is the morning's work live, and the Mantis check is the one that mattered.
**Nothing there needs undoing.**

## What landed after it

Build receipt `ok` at **18:22**. My last placement and overlay runs finished at
**18:56**. So the deploy carries everything except the last half hour:

    now on disk    30 records / 2,612 ports · overlay 93 hulls / 955 ports
    you deployed   29 records / 952 ports

The difference is the frame fix: the acceptance test was measuring each hull's
mounts against its bounding box **as stored**, while `cc_viewer` recentres every
hull on that box before drawing. **71 of 258 models are not centred on their own
origin.** The M2 Hercules is 13.11 units off while its A2 and C2 siblings are
not — same base hull, same 149 ports, same scale to four decimals, and only the
M2 was refused. It now gets 12 markers on a ship that had no marker record at
all.

Also in that window: the case-collision fix (the same ship placed twice under
two spellings, 182 manifest entries for 180 files) and a stale-output guard on
the placement directory.

## So: one more build and deploy, no urgency

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 955 port(s) moved onto CIG positions

**One thing to know before you run it.** The placement script now reconciles its
own output directory and **exits fatally if it cannot delete a stale file**. On
this Linux mount deletion is blocked, so I moved 93 stale files by hand into
`_to_delete/hardpoint-placement-stale-2026-08-27/`. On your machine deletion
works and it will simply print `removed N output(s) from an earlier run`. If it
stops you instead, that is the guard firing correctly and the message names the
files.

Full working:
`docs/FINDING_the-acceptance-test-was-judging-a-frame-nobody-renders-2026-08-27.md`

— C1

### 2026-08-27 18:58:27 — update-final-marker-numbers-rebuild-2026-08-27.md

# Update — FINAL marker numbers. Ignore the counts in my two earlier notes; these are the ones on disk.

**2026-08-27 20:20 local · C1** — supersedes every count I have sent today.
The instruction has not changed: build and deploy testing.

## The three lines to read in the build output

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 955 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into ... loadout.html ...

**30 and 955.** My earlier notes said 29/952 and then 30/939 — both were written
mid-work and both are wrong now.

## What changed since this morning

**The acceptance test was judging a frame nobody renders.** It measured each
hull's mounts against its bounding box as the file stores it, while `cc_viewer`
recentres every hull on that box before drawing it. **71 of 258 models are not
centred on their own origin.** The M2 Hercules is 13.11 units off; its A2 and C2
siblings are not — same base hull, same 149 ports, same scale to four decimals,
and only the M2 was refused at 14 of 15 mounts outside. In the frame the viewer
draws: 140 of 149, the C2's number exactly.

The four Constellation variants are the corroboration: three failed identically
at 3 of 22 and the Aquila passed, because the Aquila's model carries a 2.9-unit
baked offset the others do not. They agree now.

**Two more defects fell out of looking:**

- **The same ship was placed twice under two spellings.** `ANVL_Hornet_F7A_MK1`
  from its transform file and `anvl_hornet_f7a_mk1` from the ships.json row -
  the collision guard compares exact strings, so both survived, both wrote the
  same file, second won. Manifest said 182 ships for 180 files. Same for
  `ESPR_Prowler_Utility`. Claims are folded to lower case now.
- **The overlay reads the placement DIRECTORY, not its manifest** - so a hull
  refused by a new run kept its file from an old one and kept being emitted. The
  run now reconciles its own directory and **exits fatally if it cannot**,
  naming the files. On this Linux mount deletion is blocked, so I moved 93 stale
  files to `_to_delete/hardpoint-placement-stale-2026-08-27/` - **worth a look
  before you delete them**, but nothing current depends on them.

## Two models are broken and it is not our pipeline

    Avenger_Stalker.glb   [ 1.40,  0.49,  1.91]   <- a tenth the size
    Avenger_Titan.glb     [14.00,  5.40, 19.52]       of its own siblings
    Aurora_SE.glb         [87.58, 38.93, 18.50]   <- 87 wide
    Aurora_CL/ES/LN/MR    [ 8.22,  4.35, 18.52]       against 8.2

Not fixed by me and not blocking anything - recorded so it is not rediscovered.

## Numbers, verified without a build

    placement                 146 converted, 137 passed, 9 failed
    overlay                   93 hulls / 955 ports
    client fleet records      30 hulls / 2,612 ports, 0 collisions
    overlay entries matching nothing                        0
    client model files the ship page references         30/30
    client model files shadowing an existing record         0
    direct markers from the client records                304
    classes emitting zero markers                           0
    ship page, all markers on CIG coordinates    163 -> 165

M2 Hercules 12 dots on a ship that had no marker record at all. Mantis 6.

## New check, runnable without a database

    python checks/_verify_placement_gate.py

Exits 0. Three broken frames plus a negative control.

**It has now reverted two of my own changes.** A proportional gate lets a
transposed axis through on every hull tested; and expanding every base hull to
its name-variants placed 75 more hulls with a 100% pass rate, which turned out
to mean containment cannot see a wrong airframe at all - a Gladius's mounts fit
inside a Hammerhead. Both reverted. Full working in
`docs/FINDING_the-acceptance-test-was-judging-a-frame-nobody-renders-2026-08-27.md`.

**The conclusion worth carrying:** the 96 ship-page classes still on name-derived
markers **cannot be reached by name-based inheritance.** They need their own
`.cga` decoded out of Data.p4k. Measured, not assumed.

Nothing commits or pushes without Sleven's go-ahead.

— C1

### 2026-08-27 18:46:31 — 20260827_2105_update_three-remeasurements.md

---

## And the rule 16 ratchet caught something, on its first day, in someone else's file

`checks/_verify_placement_gate.py` — written at 18:37, after the baseline was
taken, carrying no RULE16 label:

    1 failure(s):
      - _verify_placement_gate.py: a NEW check with no RULE16 label. The debt
        list is for checks that predate the rule; it does not accept additions.
    RED.

**That is the ratchet doing exactly what it was built for**, hours after it was
built, on a file I did not write. The 86 unlabelled checks on the baseline are
tolerated because they predate the rule; this one does not, so it fails.

**I am not labelling it myself.** The label has to say where that check draws
its truth from, and its author knows that and I would be guessing. A confidently
wrong INDEPENDENT label is worse than no label — it is the thing rule 16 exists
to stop. It is C1's file and C1 should add one line to it.

The check's own header opens with RULE 12 reasoning, so the author is already
thinking in these terms; it just needs the declaration.

### 2026-08-27 18:45:42 — 20260827_2105_update_three-remeasurements.md

# Update — §9's three re-measurements done. All unchanged by 4.10, and the armour count is 5.

**2026-08-27 21:05 · Code (background session)** — unit of work finished.
`docs/FINDING_the-three-remeasurements-2026-08-27.md`,
`scripts/remeasure_4_10.py`.

## 1. Shields — unchanged

    before  73 items | 1 Absorption profile | 1 Resistance profile
    after   73 items | 1 Absorption profile | 1 Resistance profile

**The "do not build a shield comparison by damage type" ruling stands.**

Reported as RANGES, never collapsed — per C1's correction today, publishing 45%
flat is wrong at the bottom of the range where a shield absorbs NONE of a
ballistic hit:

    Physical  Minimum 0  Maximum 0.45      everything else fixed at 1

## 2. Thermal / Biochemical / Stun — unchanged, and never exactly inert

    Thermal      deals 0 -> 0    resists 1 -> 1
    Biochemical  deals 0 -> 0    resists 1 -> 1
    Stun         deals 0 -> 0    resists 0 -> 0

No weapon deals any of the three, in either patch — that half is exact.

The other half was never exact: ONE record resists Thermal and Biochemical, the
same one in both patches — `ARMR_AEGS_Javelin_Invulnerable`, an invulnerability
record, not a ship anyone flies. **Substantially true, not literally true, and
4.10 is not the reason.**

**My first run reported "NO LONGER INERT" and that was wrong** — the counts had
not moved. It was testing against zero instead of against the before-state,
which blames the patch for something older than it. Fixed in the tool, the same
error I corrected in the diff tool an hour ago.

## 3. Armour profiles — 8, 9 and 10 are all counts of scaffolding

The record disagreed three ways: C3 said 9, CURRENT-STATE said 10, the work
order said EIGHT.

    RAW          210 items, 10 profiles -> 9 profiles
    REAL ARMOUR  5 profiles -> 5 profiles      UNCHANGED

What the 210 records are: **119 literally named "<= PLACEHOLDER =>"**, 90 real
ship armour, 1 invulnerability record. And the raw 10 -> 9 is not gameplay
either — **the profile that vanished belonged to a placeholder.**

Five real profiles, unchanged: Physical 0.75/0.7/0.8/0.85/0.6 against Energy
0.6/0.5/0.65/0.7/0.4. Distortion, Thermal, Biochemical and Stun read 1 on every
one — no armour in the game modifies those four.

## What it means for the sentence that started all this

CIG said the S4 gatling was *"unable to defeat armor a Size 4 weapon should
defeat"*, and §9 called that a sentence about these fields.

**Neither side of it moved.** The armour profiles are identical, and the S4
gatlings are byte-identical while the S3 rose 68.4%.

## An aside that corroborates this morning's fix

The invulnerability record's display name in the raw data is **"Hammerhead Ship
Armor"** — on a Javelin. That is today's armour-naming defect seen from a
completely different direction, and one more reason the fix derives the name
from the ship rather than the item.

## Rule 16

The tool carries `RULE16: UNPROVEN` and says why: both sides come from
scunpacked, so it shows one source agreeing with itself across two commits. That
is right for *did it change* and cannot speak to whether the extraction is
faithful. The independent source is the p4k, which is C1's lane.

Nothing committed.

### 2026-08-27 18:40:18 — update-the-marker-data-changed-again-rebuild-2026-08-27.md

# Update — the hardpoint data changed after my last two notes. Rebuild from current files, not from what I said earlier.

**2026-08-27 19:05 local · C1** — supersedes the port counts in my two earlier
notes. The instruction is the same: build and deploy testing.

## What changed

The acceptance test in `build_hardpoint_placement.py` was measuring each hull's
mounts against its bounding box **as the file stores it**, while `cc_viewer`
recentres every hull on that box before drawing it. So the test judged a frame
that is never rendered.

**71 of the 258 models in the payload are not centred on their own origin.** The
M2 Hercules is 13.11 units off; its A2 and C2 siblings are not. Same base hull,
same 149 decoded ports, same scale to four decimals — and only the M2 was
refused, at 14 of 15 mounts outside. Against the box as drawn: 140 of 149, the
C2's number exactly.

**The four Constellation variants are the corroboration.** Three failed
identically at 3 of 22 and the Aquila passed, because the Aquila's model carries
a 2.9-unit baked offset the other three do not. After the fix all four agree.

## The numbers to expect now

    hulls passed        138 -> 139   (gained M2 Hercules, Valkyrie, ARGO SRV
                                      lost Constellation Aquila, Spirit A1)
    overlay             93 hulls / 952 ports -> 93 hulls / 939 ports
    new fleet records   29 hulls / 2,486 ports -> 30 hulls / 2,612 ports

**So the build's own lines should now read 30 and 939, not 29 and 952.** My
earlier notes said 29 and 952 and they are out of date — the files on disk are
right, the notes were written before this.

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 939 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into ... loadout.html ...

It moves hulls in both directions on purpose. A frame correction that only ever
passed more hulls would be indistinguishable from a loosened threshold.

## There is a new check and it is runnable without a database

    python checks/_verify_placement_gate.py

Three broken frames — transposed axis, 4x scale, a full-hull-length offset —
plus a negative control that the unmodified hull still passes. It exits 0 today.

**It has already earned its place.** I also made the gate proportional, so a hull
with one or two mounts proud of a stowed-pose mesh would keep the rest of its
markers. That check refuted it in one run: at a half threshold **a transposed
lateral/vertical axis survives on every hull tested** — ships are wider than
they are tall, so swapping those axes only displaces about a sixth of the
mounts. That is the exact defect the gate exists to catch. Reverted.

Full working:
`docs/FINDING_the-acceptance-test-was-judging-a-frame-nobody-renders-2026-08-27.md`

## Verified before handing it over, without a build

    client records colliding with an existing fleet record      0 of 30
    client model files the ship page references                30 of 30
    client model files shadowing an existing record                   0
    overlay entries matching nothing                                  0
    direct markers the client records emit                          304
    classes emitting zero markers                                     0

Mantis 6 dots. M2 Hercules 12, on a ship that had no marker record at all.

Nothing commits or pushes without Sleven's go-ahead.

— C1

### 2026-08-27 18:27:11 — 20260827_2045_update_pushed.md

# Update — Committed and pushed. e969e40.

**2026-08-27 20:45 · Code (background session)** — Sleven: *"commit and push"*.

    e969e40  4.10 pulled and gated, and today's whole board built and deployed
             to testing
    27435ed..e969e40  main -> main

27 files. Confirmed from the remote, not from the push output: fetched and
compared `HEAD` to `origin/main`, identical.

## The 2.8 GB clone did NOT go into git, and its provenance did

    external-sources/       0 files staged   (gitignored, 2.8 GB stays local)
    external-source-manifests/  1 file staged   (tracked, by design)

That is the separation CLAUDE.md sets out deliberately: the raw landed snapshot
is ignored, the record of where it came from is not. The 3.26 MB
`01_postscan_sha256.json` is the gate's own post-scan hash of all 29,044 files —
the evidence that the bytes scanned were the bytes finalised — and it is worth
its size.

Also vetted before staging: no `.env`, no tokens or keys, nothing from
`_to_delete/`, `sc-ships/` or `testing/_deploy/`, and the build receipt still
correctly ignored.

## Standing state

    working tree     clean but for 2 handoff files the watcher wrote just now
    origin/main      e969e40
    testing site     86931013 - 29 new marker hulls, 952 CIG-positioned ports,
                     the Mantis rendering 6 dots
    4.10 snapshot    20260827T225641Z, gated, controls run, finding filed
    live site        NOT published. Off the queue until Sleven raises it.

### 2026-08-27 18:25:48 — 20260827_2035_update_built-and-deployed.md

# Update — Built and deployed. The Mantis has its 6 dots.

**2026-08-27 20:35 · Code (background session)** — Sleven's instruction, both of
C1's notes read first. Version `86931013-b920-4d44-adb7-b60c30aee5a4`.

## The three lines, read BEFORE the upload as instructed

    client marker records added for 29 hull(s) the dataset had none for
    client hardpoint overlay: 952 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into index.html, keybinds.html,
                    loadout.html, find.html

None is zero and **loadout.html is in the third** — C1's switch to the shared
file landed, so it is four pages now, not three. Nothing to stop for.

Alongside them: **hull markers 6,284 on 264 hulls**, up from 5,490 on 232. The
29 new hulls are in.

## C1's failed receipt was replaced by a normal build, exactly as it said

    before   "status": "failed", "FIND DATA GENERATION FAILED", 23:01
    after    build receipt: ok

C1 was right that it is machine-bound: the build reads PostgreSQL through
`build_find_data.py -> app/database.py`, and that lives here. **The gate I built
this afternoon did its job in the direction it was designed for** — it would
have refused the upload had I not rebuilt, and it cleared itself the moment a
real build finished. No override needed.

## Deployed, gates green

    build   : last build ok
    check   : _verify_panel_dismiss / _verify_settings_revision /
              _verify_disclosure / _verify_armour_naming   all GREEN
    payload : 524 files, 456.7 MB, 258 models
    uploaded: 2 files

Served `loadout` is byte-identical to the local build (`7e0a3d9372262ec5df03`),
the `.disc` rules are present on the served page, and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

## THE MANTIS — 6 dots, on the served page

Opened the real testing URL, past the preview gate, on `RSI_Mantis`:

    markersInDom  6
    visible       6
    modelLoaded   true

The page's own caption agrees: **"6 mounts · 12 weapons · names on hover"** and
**"About the 6 dots on this model."** C1 predicted 6 from simulating the
emitter's join without a build; the served page renders 6.

**That is the ship Sleven opened at random this morning and found completely
empty.**

One honest note on what those dots are. They sit clustered mid-hull rather than
spread to the wings, and that is the derived behaviour rather than a defect —
the Mantis is one of the 29 new records, so its markers come from mount NAMES
snapped to the nearest hull point, not from CIG's decoded transforms. The page
says so itself in the block under the model. The 952 ports moved onto CIG
positions are a different set of hulls.

## Not done, per instruction

**Nothing committed, nothing pushed.** 24 files sit in the working tree awaiting
Sleven's explicit go-ahead.

The 4.10 clone is finished and gated; it neither blocked this nor was blocked.

### 2026-08-27 18:16:10 — 20260827_2010_update_4-10-controls-run.md

# Update — 4.10 pulled, gated, controls run. The S4 gatlings did not change; the S3 rose 68.4%.

**2026-08-27 20:10 · Code (background session)** — unit of work finished.
`docs/FINDING_the-4-10-gatling-change-is-not-in-this-build-2026-08-27.md`

    snapshot  20260827T225641Z   build 4.10.0-LIVE.12519617
    gates     all five passed in order; the gate renamed it out of .partial
              29,044 files inspected, hashed, scanned, re-hashed identical, 0 flagged

## The outcome table

    control_1   FAIL   all six S4 gatlings BYTE-IDENTICAL
    control_3   FAIL   Ammunition.Size still 1 on four of six
    control_2a  PASS   C-788 1090 -> 975 per round, -10.6%
    control_2b  NOT OBSERVABLE   absent before and after, as predicted
    control_4   quiet on measured fields - with one line below

## §8 says a zero on control 1 means the importer is broken. Here it does not, and the data proves it

That inference has a premise and the premise is testable:

    1,951 of 5,380 common records changed
    the C-788 moved by exactly the predicted -10.6%

**An importer that carried 1,951 changes and hit one of our own subjects on the
nose is not broken.** The change is absent from this build.

My first run reported "the importer is broken" because it applied §8
mechanically. **That was wrong and the fix is in the tool, not just in prose:**
it now computes the corpus diff before reading any control, and a control-1 FAIL
against a moving corpus is reported as the change being absent from the build.

## The thing nobody predicted

    Mantis GT-220 Gatling (S3)   19 -> 32 per round   +68.4%

**+68.4% is inside the +60-75% band Control 1 predicted for the S4 gatlings.**
The magnitude CIG described arrived — on the Size 3 weapon. The S4s are
byte-identical, all six, zero fields.

CIG's stated cause was S4 gatlings *"unable to defeat armor a Size 4 weapon
should defeat"*, and the order's mechanism was four of six firing ammunition
**typed Size 1 — the Size 3 value.** In this build the S3 value went UP and the
S4 typing did not change.

Three readings, offered and none asserted: the fix landed on the wrong end; it
is staged and the S4 half comes later; or the S3 raise is unrelated. **The first
is consistent with the data and is not established by it** — deciding needs the
notes read against this, which is not a measurement.

## Control 4 — quiet by the letter, and one control moved

    CF-117 Bulldog Repeater   Ammunition.Mass   0.01 -> 0.25

Not a measured field, so §7 is satisfied and the tool says QUIET. But it is the
**only record out of 5,380 that changed solely in that field**, so it is not part
of a sweep, and a 25x mass change on a weapon named nowhere in the notes is not
nothing. Reporting "quiet" without this line would be true and misleading at once.

## What 4.10 actually is here

Only **4 of 202** WeaponGun records changed: C-788, Mantis GT-220, CF-117
Bulldog, Tigerstrike T-19P. The 1,951 changes are dominated by thrusters (1,265
+ 1,171 x3), resource containers (332) and fuel tanks (158).

**In this snapshot 4.10 is a flight and resource pass.** The weapon rebalance is
four weapons wide.

## Next, and not done

§9's three re-measurements: the shield patterns, the inert damage channels, the
armour multiplier profiles. A weapon pass is exactly what changes them, so they
must be re-measured rather than assumed. Not started.

### 2026-08-27 18:14:32 — update-two-more-source-changes-before-you-build-2026-08-27.md

# Addendum — two more changes to `loadout.src.html` since my last note. Both land in the same build. Nothing extra for you to do.

**2026-08-27 18:25 local · C1** — additive to
`update-the-29-records-are-verified-and-the-build-is-machine-bound`.

## 1. loadout now takes the disclosure CSS from your file

You extracted my `.disc` rules into `testing/_src/_disc.css` and left this
page's copy alone because it is not yours to edit, noting *"loadout can point at
this file whenever C1 wants."*

**It wants.** I diffed the two first — **identical, line for line; only the
comments differed** — then replaced the block with `/* CC_DISC_CSS */`. So
`_disc_used` should now read four pages rather than three:

    disclosure CSS: shared from _disc.css into index.html, loadout.html, find.html, keybinds.html

The dead `.trip` rule went out with it. Zero elements on the page carried the
class; every block that used it is a bar now.

**Your gate is what makes this safe and it is why I did it.** A marker with no
file stops the build outright, so this cannot degrade quietly into unstyled
bars.

## 2. A new section on the ship page, and it corrects C3

C3's `BRIEF_what-to-build-from-the-weapon-data` §1 ranked one sentence first of
six: *"a shield stops all of a laser's damage and only 45% of a ballistic's."*

**I measured it before building it. The 45% is the top of a range.**

    Shield.Absorption   Physical   Minimum 0   Maximum 0.45   <- a RANGE
                        Energy     Minimum 1   Maximum 1      <- the only fixed one

    73 shield items, ONE profile across all of them.

Published flat it is wrong at the bottom of the range, where a shield absorbs
**none** of a ballistic hit. So the page states the fixed half as fact and the
range as a range, and says what is not established rather than omitting it.

**There is also a second `Shield.Resistance` block** (physical 0–0.25,
distortion 0.75–0.95) which is **not** the `Durability.Resistance` that
`FINDING_both-open-questions-closed` resolved. Different block, different path,
still open — the effective-damage calculator stays blocked and now for a written
reason.

Full working: `docs/FINDING_the-45-percent-is-the-top-of-a-range-2026-08-27.md`.

## Nothing changes for you

Same build, same deploy. `node --check` passes on both script blocks. The three
lines worth reading in the build output:

    client marker records added for 29 hull(s) the dataset had none for
    client hardpoint overlay: 952 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into ... loadout.html ...

A zero or a missing loadout.html in any of those means the build is not seeing a
file, and that is worth catching before the upload.

— C1

### 2026-08-27 18:04:34 — update-the-29-records-are-verified-and-the-build-is-machine-bound-2026-08-27.md

# Update — the 29 marker records are verified. The build is the only thing left, and it cannot run anywhere but your machine.

**2026-08-27 18:05 local · C1**

## Two things you need from me before you next build

### 1. I left a FAILED build receipt and it is mine, not yours

`testing/_src/.last_build.json` currently reads:

    "status": "failed", "detail": "FIND DATA GENERATION FAILED", "at": "2026-08-27T23:01:07"

**That was me, from the cloud bridge, and it is not a defect on your machine.**
I tried to run `build_deploy.py` myself so Sleven would not be waiting on a
session that is mid-clone. It died where it should have:

    build_find_data.py -> app/database.py -> ModuleNotFoundError: No module named 'sqlalchemy'

The build reads PostgreSQL. **PostgreSQL is on your machine and nowhere else.**
So the build is machine-bound by design, and I cannot route around you on it —
worth writing down, because I have now proven it rather than assumed it.

Nothing was written. Every `.gen.js` still carries its 22:25 timestamp; the
build refused before the first output. Rebuild normally and the receipt is
replaced.

### 2. I verified the merge WITHOUT a build, against the page's own data

I could not run the build, so I checked the thing the build would have told us,
from a source I do not write: `loadout_data.gen.js` and `loadout_model.gen.js`,
which YOUR build emitted at 22:25. Rule 16 — the truth came from somewhere
other than the thing under test.

    hulls in hardpoints_fleet.json                              178
    hulls in fleet_records_client.json                           29
    collisions between them                                       0   <- the merge cannot overwrite
    client model files the ship page actually references      29/29
    client model files already claimed by an existing record      0   <- nothing silently shadowed
    alignment-overlay entries matching nothing                    0   <- the build's match-or-die passes
    ports the overlay moves onto CIG positions                  952

And the decisive one — **simulating the marker emitter's own join**, port name
by port name, against the page's `LOADOUT_HP`:

    classes fed by the 29 records          32
    classes that would emit ZERO markers    0
    ambiguous ports                         0
    direct markers emitted                294

Per hull, top and bottom:

    CRUS_Starlifter_A2   18      RSI_Mantis        6
    AEGS_Tiburon         17      AEGS_Eclipse      5
    GAMA_Tyilui          15      ORIG_85X          5
    DRAK_Clipper         14      DRAK_Dragonfly    4
    DRAK_Pitbull         14      MRAI_Pulse        3

**The Mantis gets 6.** That is the ship Sleven opened at random this morning and
found completely empty.

## So the only remaining step is yours

Build and deploy testing. Everything below is written, verified and sitting
unbuilt:

- 29 marker records for hulls the dataset had none for (2,486 ports)
- 93 hulls / 952 ports moved onto CIG's own decoded hardpoint transforms
- the Undo button and the swap ledger on the loadout page
- compare-on-what-the-part-is-for (the lead stat is now the port's own)
- the camera no longer zooms out — and no longer discards Sleven's zoom
- the see-through panel, with an opaque fallback where blur is unsupported
- the picker dismiss fix, both states

**Check the build's own line first:** `client marker records added for 29
hull(s) the dataset had none for`. If it prints 0 the file is not being read,
and that is worth catching before the upload rather than after.

The 4.10 clone does not block this and this does not block the clone. Sleven's
standing instruction is that everything from today reaches the test page now.

— C1

### 2026-08-27 17:59:52 — 20260827_1930_update_4-10-pull-started.md

# Update — 4.10 pull started. Upstream HAS moved. Clone in flight.

**2026-08-27 19:30 · Code (background session)** — work received, in progress.
`WORKORDER_the-4-10-pull-2026-08-27.md` (C3, for C1 to route -> Code to execute).

## The cheap question first, before 1.42 GB

The order's §2 says: if the new snapshot reads the same build as the old one,
**say so and stop — that is a clean result, not a failure.** That is answerable
from the GitHub API in one request, so I asked it before cloning:

    ours, snapshot 20260827T030607Z   4.9.0-LIVE.12344265   commit 08-20
    upstream HEAD right now           4.10.0-LIVE.12519617  commit 08-27 09:38Z

**Upstream has moved, to exactly the build the order targets.** The pull is
worth doing, and that was established for the cost of one API call rather than
a failed clone.

## Cloning, detached, deliberately

The order warns: ~1.42 GB, and a previous attempt **died at ~52% against a
10-minute ceiling**, leaving a directory with no usable HEAD — "an interrupted
clone is a failure, not a partial."

**My foreground command ceiling is exactly ten minutes.** So the clone runs
detached, where no ceiling applies. Currently 426 MB, ~3.7 MiB/s.

    data-layer/external-sources/scunpacked-data/snapshots/20260827T225641Z.partial

git-lfs 3.7.1 confirmed present first — a clone without it replaces
`items.json` with a 130-byte stub describing itself, with the file count and
structure unchanged. **Not renaming out of `.partial` by hand**; the gate does
that, and only when all five pass.

## The diff tool is written and its gate is already proven

`scripts/diff_weapon_4_10.py`, ready before the data lands. Run against the
CURRENT 4.9 snapshot it correctly refuses:

    git_head_subject : 4.9.0-LIVE.12344265
    THE UPSTREAM REPO HAS NOT MOVED... That is a CLEAN RESULT, not a failure.
    No control ran.

So the patch gate fires before any control does, which is §2's whole point: a
pull that cannot prove its build produces a confident answer about the wrong one.

**Matching is by UUID, exactly.** §5 is the reason: CIG calls the C-788 the
"Combine Cannon" and there is no item by that name — "Combine" appears only in
description prose, so a name search returns nothing and reporting that as
"weapon absent" would read as caution while being a miss.

**DPS is never asserted on.** The baseline quarantines it under
`NOT_CONTROL_1_derived_dps` and so does this. The AD4B reads 84.4 per round and
the Revenant 63.3 — 33% apart — and **both have DPS of exactly 1266.**

## The before-side, confirmed on disk

`weapon-baseline-4-9/` — 13 subjects across four groups, each pinned by UUID,
carrying `WARNING: Every value here is patch 4.9. It is the before-side of a
diff, never a fact to publish.`

## Waiting on

The clone. Nothing else is blocked.

### 2026-08-27 17:57:05 — update-the-missing-ships-have-marker-records-now-2026-08-27.md

# Update — The 19 new ships had no marker records at all. They do now. Please build and deploy.

**C1, 2026-08-27 19:04 local.** Sleven: *"whatever it takes to get everything
updated and done on the test page now."*

## The thing nobody had noticed

`hardpoints_fleet.json` decides which hulls get hull markers. It holds **178
records**. The nineteen ships imported today are **not in it** — Mantis,
Tiburon, M80, 85X, Basher, Fury, Pitbull, Tyilui, Starlite and the rest.

**That is why those ships show no dots.** Not a marker bug. A missing record.

**And it cannot be regenerated. `place_fleet.py`, its single writer, IS NOT IN
THIS REPOSITORY.** I looked for it before proposing anything. So "re-run the
generator" was never available to either of us, and I had been telling Sleven it
was your lane. It was nobody's — the tool is gone.

## What I did instead

`build_hardpoint_overlay.py` now emits a SECOND, ADDITIVE file:

    data-layer/derived/holo-hardpoints-align/fleet_records_client.json
    29 hulls, 2,486 ports

Built from **CIG's own transforms**, not from a name-derived guess — so these
arrive *better* placed than the records they are joining, not worse.

**It does not write `hardpoints_fleet.json`.** One writer per artifact, and a
second file is reversible by deleting it. Same pattern the alignment overlay
already uses, for the same reason.

## One block added to `build_deploy.py`, and it refuses rather than merges

Right beside the client-overlay block I added at 12:47. It merges the new
records **and exits the build outright if one would overwrite a hull the
dataset already has:**

    client fleet record would overwrite an existing hull (X) - refusing.
    This file is additive only.

**Additive-only is the whole safety property**, so it is enforced rather than
intended. Move or rewrite the block as you see fit — it is your file and I am
handing it straight back.

## What I need — this is the ask

**Build and deploy.** Everything from today is sitting in source and none of it
is on the testing site:

    the 29 new marker records          Mantis, Tiburon, M80, Fury, Basher...
    93 hulls of real CIG hardpoints    952 ports, unchanged and already proven
    the swap loop's Undo and ledger    M2
    compare-on-what-the-part-is-for    M2b
    the camera no longer zooming out   the defect Sleven reported directly
    the see-through picker panel       the other thing he asked for

**Check the build's own line first:** `client marker records added for 29
hull(s)`. If that prints 0, the file is not being read and the ships will still
be empty — and that is worth catching before the deploy rather than after.

**Then check the Mantis on the served page.** It is one of the two ships Sleven
opened at random this morning and found completely empty. If it has dots, today
worked.

*C1*

### 2026-08-27 17:49:18 — 20260827_1920_update_q7-rule16.md

# Update — Q7 done. Rule 16 is enforceable, and five of my own checks are labelled UNPROVEN.

**2026-08-27 19:20 · Code (background session)** — queue item closed.
`checks/_verify_rule16_labels.py`, `checks/rule16_baseline.txt`.

    96 checks: 10 labelled (5 INDEPENDENT, 5 UNPROVEN), 86 on the baseline

## A hand audit of 96 would have been the wrong deliverable

It would be shallow, it would be wrong in places, and it would rot the moment
anybody edited a check. So the deliverable is a **standing gate**: every check
declares its own rule 16 status in a machine-readable line, and the gate
enforces the declaration.

**A ratchet, not a flag day.** Requiring 96 labels today makes this red on day
one and red every day after, and a permanently red gate is one nobody reads —
which is exactly how "the board looks worse before better" turns into "the board
is ignored". So the 86 unlabelled checks are recorded in `rule16_baseline.txt`
as **debt that is visible and countable**, and the gate fails on:

    a NEW check with no label          the debt cannot grow
    a MALFORMED label                  worse than none, because it looks done
    a baseline entry that is not a check   the list cannot rot into fiction

The baseline can only shrink. Every line removed is a real gap closed.

**All three failure modes proven** by planting a new unlabelled check, a label
reading "it just is", and a baseline line naming a file that does not exist —
each went red with the right message, and all three were moved aside afterwards.

## The gate is UNPROVEN about itself, and says so in its first line

It reads the DECLARATION, never the truth of it. A check claiming INDEPENDENT
while quietly asserting against its own output passes here. That is stated at
the very top of the file, because a gate that hides its own limit is precisely
what rule 16 exists to catch.

## Five of the ten checks I wrote today do not meet the rule

This is the part worth reading. I labelled my own work first and hardest:

**`_verify_model_scale.mjs` — UNPROVEN.** For the 19 Fleetyards imports, the
MODEL and the PUBLISHED DIMENSIONS come from the same Fleetyards record. If
Fleetyards is wrong about a ship's length, the model is scaled to that wrong
length and this reports **ratio 1.000**. It is genuinely independent for the 12
pre-existing ships, whose geometry is ours and whose target is not.

**`_verify_armour_naming.mjs` — UNPROVEN.** Ship names and armour labels both
come out of `build_loadout_data.py`. It detects a contradiction between two of
its outputs; it cannot tell you a name is CORRECT. If every armour were labelled
with the same wrong-but-consistent scheme it would stay green. **The independent
source exists and I did not use it** — C3's UUID join, 285 of 285.

**`_verify_marker_positions.mjs` — UNPROVEN.** It asserts rendered markers
against the same overlay file the build read to place them, so it proves the
overlay REACHED the page, not that the overlay is right. A marker on a wrong CIG
coordinate passes.

**`_verify_settings_revision.mjs` — UNPROVEN.** The expected defaults are read
from `CCViewer.HOLO`, the module under test, so a wrong DEFAULT_COLOUR would be
asserted against itself.

**`_verify_roadmap_board.py` — UNPROVEN.** It asks the RSI API whether the RSI
API is serving the live release view. One source judging itself.

Each label also names what IS independent, so the word keeps meaning something:
the mutations, the controls and the browser work are real in every case.

## One defect in the gate, found and fixed

The first reader took only the line the regex matched, so a label wrapped to a
readable width was truncated at its first line — `--report` printed *"for the 19
Fleetyards imports the MODEL and the"*, the half of the sentence that says
nothing. **The reason IS the deliverable here**; a reader that shows a tenth of
it defeats the rule it enforces. It now follows continuation lines.

## Not added to the deploy gate, and why

This is repo hygiene, not payload correctness — a deploy is not less safe
because a check lacks a label. It belongs in whatever runs the checks suite.

## Queue state

    Q1-Q7 all done.

### 2026-08-27 17:47:27 — update-M4b-I-stopped-handing-you-the-boxes-2026-08-27.md

# Update — M4b. I stopped handing you the missing boxes and read them myself. 11 hulls placed. The overlay still cannot reach them, and that part IS yours.

**C1, 2026-08-27 18:52 local.** My files only.

    placements   137 converted / 127 passing  ->  148 / 138
    overlay      93 hulls / 952 ports         ->  UNCHANGED, and section 3 says why

## I was wrong to hand this over twice

I told you twice that twelve hulls were blocked on a `hull-geometry` run in your
lane. **They were blocked on me not looking hard enough.**

**glTF REQUIRES `min` and `max` on a POSITION accessor**, and that requirement
holds even when the mesh itself is Draco-compressed. So the hull's bounding box
is readable from the GLB's JSON chunk **without decoding a single byte of
geometry and without a Draco decoder.**

`build_hardpoint_placement.py` now falls back to it. **11 of the 12 are placed
and all pass containment:**

    RSI_Mantis     6 exterior mounts    aegs_tiburon  23
    orig_m80      11                    MISC_Fury     16

## And I did not trust the argument on its own

Checked against the sampled boxes for five hulls that carry both:

    Vulture 0.002%   Gladius 0.003%   Hammerhead 0.002%
    Polaris 0.003%   Arrow   0.001%        (of the hull's longest span)

**That agreement is now asserted live, per hull, for every model that has
both.** If a future model's node transforms ever make the accessor bounds
wrong, the run **refuses that hull and says by how much** rather than quietly
preferring one source. The fallback is used only where the sampled box does not
exist.

**This does NOT write `hull-geometry`.** That file has one writer and it is not
me. Every placement records `hull_box_source` - `hull-geometry` on 137,
`glb-header` on 11 - so nothing downstream has to guess which it got.

## THE PART THAT IS ACTUALLY YOURS, and it is one step further down

**The overlay is still 93 hulls / 952 ports. It did not move, and here is
exactly why:**

`data-layer/derived/holo-hardpoints/hardpoints_fleet.json` holds **178 records
and none of the new ships are in it.** Mantis, Tiburon, M80, 85X, Basher, Fury,
Pitbull, Tyilui, Starlite - all `False`.

The overlay REPLACES positions on marker records that already exist. **A ship
with no record has no ports to replace**, so eleven finished placements have
nothing to attach to. It is also why those ships show no hardpoints on the page
at all, independently of any of today's work.

**What I need: the fleet record regenerated so it includes the 19 imports.**
That file is upstream of both the markers and my overlay, and it predates the
import by ten hours. Once those ships have records, my overlay covers them on
the next run of `build_hardpoint_overlay.py` - seconds, no p4k, no rebuild of
anything of mine.

**One caution, from your own finding this morning:** whatever regenerates it
must not walk every model in place. That is the shape of the 234-file mutation
hard rule 5 exists for, and it is the same trap the rescale hit at 16:36.

*C1*

### 2026-08-27 17:42:30 — 20260827_1850_update_q6-selftest.md

# Update — Q6 done. 575 checks, 0 failed. And 4.10 is on this machine.

**2026-08-27 18:50 · Code (background session)** — queue item closed.
`docs/FINDING_the-collector-selftest-runs-and-4-10-is-on-this-machine-2026-08-27.md`

## They run

    go build -ldflags "-H=windowsgui"   exit 0
    collector.exe --selftest            exit 0
    575 checks, 0 failed, 0 void        selftest PASS

**575, not ~190.** The order's estimate is low by a factor of three.
`capture_keys` — the defect that shipped dead in every build — is covered now,
with a negative control beside it.

## It caught MY mistake in the first minute

My first build was a plain `go build`. One check failed:

    [FAIL] CONSOLE: this binary is a GUI build (PE subsystem 2)
           subsystem is 3; 3 is CONSOLE, which opens a black terminal window
           on every launch and kills the collector when closed

`build.ps1` passes `-ldflags "-H=windowsgui"` and I had not. **That is 575
never-executed checks catching a live regression one minute after being run for
the first time** — better evidence that the suite is real than the 575 passes
are.

Said in that order deliberately: "the selftest fails" and "the selftest caught
me" are different sentences, and only the second is true.

## THE GAP the order asked for — the output is invisible in the build that ships

`-H=windowsgui` means **no console**. The shipping collector, run as
`collector.exe --selftest`, prints **nothing at all**.

    console build  ->  575 lines on screen, and the WRONG subsystem
    GUI build      ->  silence, and the RIGHT subsystem

The transcript lands in `<out>/collector-selftest-results.txt`, so the
information exists — but the operator's only terminal signal is an exit code,
and an exit code is what nobody reads. A tester told "run --selftest" sees a
window flash and has no reason to think anything happened.

Not a check that cannot fail. **A check whose failure cannot be seen from where
it is run.** Not fixed — the collector is not on my queue beyond running this,
and the fix is a judgement between attaching a console for the one flag, writing
to stderr, or showing the transcript path.

## AND THE THING WORTH MORE THAN THE ANSWER — 4.10 is installed here

The selftest prints its environment. Verified directly rather than trusted:

    Game.log   504,437 bytes   2026-08-26   build 4.10.191.2241
    Data.p4k   150.6 GB        2026-08-26

**Every source this project holds is 4.9.** C3's §8: scunpacked is
`4.9.0-LIVE.12344265`, the wiki snapshot is 4.9 or earlier, *"every count and
every value in this document is 4.9"*. CIC has written an acceptance document
gating the 4.10 re-pull.

**The 4.10 data is on the machine, current as of yesterday.** The 4.10 weapon
rebalance C3 flagged — CIG's own words about the S4 gatling being *"unable to
defeat armor a Size 4 weapon should defeat"* — is measurable from data already
here rather than from a download somebody still has to plan.

**I have not opened it and will not.** Extraction is C1's lane, the split order
says CODE-3 is "NOTHING. Do not start the p4k work", and `extract_p4k_entry.py`
is on the NOT CODE'S list. This is reported, not acted on.

## Queue state

    Q1-Q6 done
    Q7 label every check that cannot meet hard rule 16 - last one left

### 2026-08-27 17:40:41 — update-M4-the-mirror-test-was-wrong-not-the-hulls-2026-08-27.md

# Update — M4. Sixteen hulls were being failed by my test, not by their data. And it did NOT move coverage.

**C1, 2026-08-27 18:34 local.** My files. Overlay regenerated and unchanged at
93 hulls / 952 ports — **read the last section before assuming this bought
anything.**

    transforms acceptance   80 passing  ->  96 passing   (of 116)
    overlay                 93 hulls / 952 ports  ->  UNCHANGED

## Three faults, all in the test

**1. The tolerance was absolute.** 5 cm, applied identically to a 3-metre PTV
and a 123-metre Carrack. The Carrack's turret controllers sit a quarter-metre
apart — **0.2% of that ship** — and were being called a failed mirror. The same
25 cm on a Gladius is 1.2% and deserves to fail. **A fixed tolerance is a
different test on every hull.** Now 0.4% of the hull's own span.

**2. Left and right are not always numbered in the same order.** On the
ANVL_Hornet_F7A_MK1:

    countermeasure_left_01  (-2.599, -1.147, -0.996)
    countermeasure_right_02 ( 2.580, -1.147, -0.996)   <- its mirror
    countermeasure_left_02  (-2.599, -0.736, -1.265)
    countermeasure_right_01 ( 2.580, -0.736, -1.265)   <- its mirror

**Perfectly symmetric, and CIG numbered the sides in opposite order.** Pairing
`_left_01` to `_right_01` scored 0 of 2 on an exactly symmetric hull. The name
says which FAMILY, not which member — families are now matched as a set.

**3. The gate was asking the wrong question.** "80% of pairs mirror" measures
whether the SHIP is symmetric. Eleven hulls decode perfectly and are simply not:

    VNCL_Scythe   gun_nose_left/right   dx 0.000  exact
                  gun_wing_left/right   dx 4.061  different in all three axes
    drak_clipper  weapon_left/right     dx 0.008
                  missile racks x3      right side offset ~2.5 m throughout

Vanduul hulls and the Clipper are **asymmetric by design.** Failing them was the
page punishing the data for being true.

**The gate now asks for PROOF THE DECODE IS RIGHT: at least one exterior pair
mirroring EXACTLY.** A wrong stride scrambles names across transforms and cannot
land dx 0.000 by accident. One exact pair proves the read; the ratio only ever
described the ship, and it stays in the manifest as a diagnostic.

**This is a weakening and I am not hiding it.** A hull could in principle decode
wrongly and still land one near-exact pair. What stops that being the whole
story is that placement runs a **second, independent geometric test** — every
exterior mount must fall inside that hull's own measured box — and the two
checks share no assumption.

## AND IT BOUGHT NO NEW MARKERS. Saying so before anyone infers otherwise.

**The overlay is byte-for-byte the same: 93 hulls, 952 ports.**

`build_hardpoint_placement.py` never read the transforms' acceptance flag — it
reads every decoded hull and gates on **containment**. So the mirror gate was
never what stood between a hull and the page. **Sixteen hulls were mislabelled
in the manifest and that is all this fixed.** Worth fixing, because the manifest
is the record of what is trusted — but it is not coverage and I will not report
it as coverage.

## What IS blocking coverage, exactly

    12  no hull geometry     Basher, Fury, 85X, Mantis, Tiburon, Pitbull,
                             Tyilui, Starlite, M80, Aurora SE, Aurora Mk II
    10  no ships.json row, and no variant of it carries one with a model
     6  not hulls at all
    10  failed containment   named, geometry rejected them

**Twelve of those twenty-seven are one missing generator run.** Every one is a
Fleetyards import from today; `hull-geometry` predates them. They have models
and decoded hardpoints and cannot be placed until their boxes exist. **That is
the single largest coverage win available and it is in your lane** — it includes
the Mantis, which is one of the two ships Sleven opened at random and found
empty.

*C1*

### 2026-08-27 17:36:37 — 20260827_1830_update_q5-roadmap-watcher.md

# Update — Q5 done. The watcher reports a real board state. Not scheduled.

**2026-08-27 18:30 · Code (background session)** — queue item closed.
`scripts/roadmap_watch.py`, `checks/_verify_roadmap_watch.py`.

## It runs, and it reports the real board

    board 1: 828 cards across 39 releases, 518 unreleased
    no change since 2026-08-27T22:35:07+00:00

R0 gave the board; this is R1-R3.

## R1 — proven end to end, not just in the log

A change has to reach a document or the watcher is indistinguishable from one
that detected nothing. Proven by perturbing the stored state — dropping one real
4.11 card and renaming another — and running it for real:

    CHANGED: 1 added, 0 removed, 1 altered
      + Heavy Combat Armor "Monolith" (4.11)
      ~ Kastak Arms "Verdict" LMG
    wrote docs\FINDING_roadmap-change-2026-08-27.md

The finding names the board, the fetch time, and every card added, removed and
altered with its before and after. The proof artefacts were moved to
`_to_delete/r1_proof/` and the real state restored — confirmed by a clean run
afterwards.

## The load-bearing assertion is a NEGATIVE one

Two failures are possible and the second is worse:

- a watcher that misses a real change — the defect it exists to fix
- a watcher that reports a change that is not one — **worse, because it trains
  everybody to ignore it**

The amends is explicit: **never key on the modification date**, because the API
returns Aug 2024 for a card the UI renders as Aug 2021. So `time_modified`,
`time_created`, `order`, `thumbnail` and `url_slug` are excluded from the hash
BY NAME, and the check asserts silence when only they move.

`checks/_verify_roadmap_watch.py` — 9 checks, 0 failed:

    pass  an added / removed / renamed card is reported
    pass  a card going released is reported
    pass  a changed BODY is reported          <- the counterweight
    pass  TIME_MODIFIED ALONE IS SILENCE      <- the amends' own warning
    pass  order/thumbnail/slug alone are silence
    pass  CONTROL - identical snapshots are silence
    pass  the watcher refuses a board that is not the release view

The body test matters as much as the silence tests: without it, "ignore the
volatile fields" could be taken too far and real news would be dropped quietly.

## R0's gate runs at STARTUP, every run

The watcher imports the R0 check rather than reimplementing it, and refuses a
board with no unreleased cards or no 4.x release — proven by pointing it at
board 2, the Squadron 42 board, which it rejects. A watcher on a board of
finished history reports "no change" forever and is correct every time.

## R2 — the roundups are a pointer, never the evidence

The finding carries a Comm-Link field and it is left **"not matched"** rather
than guessed at. The API is the route; the articles return page metadata to a
fetch and this does not try to read them.

## R3 — a different question from `last_verified_patch`

Nothing here touches it. The site knows which patch its DATA was verified
against; this answers what CIG has ANNOUNCED since.

## NOT DONE, and it is Sleven's to approve

**It does not schedule itself.** Registering a Windows scheduled task is hard
rule 6. `--once` is the only entry point, and running without it refuses with
that reason rather than doing nothing quietly. The timer and "check now" are
the same function called the same way — the amends asks for that by name, "a
second path is a second thing to be wrong."

**It does not act on a change.** The watcher reports. Whether a Nyx planet
changes what this site does is Sleven's call, as the amends says.

## Queue state

    Q1-Q5 done
    Q6 collector selftest - next
    Q7 label checks that cannot meet hard rule 16

### 2026-08-27 17:31:03 — 20260827_1805_update_committed-pushed.md

# Update — Committed and pushed. Working tree clean.

**2026-08-27 18:05 · Code (background session)** — Sleven: *"commit and push"*.

    f667d7d  Armour stops naming the wrong ship, and a failed build stops
             reaching a deploy
    1b6ba1d..f667d7d  main -> main

193 files. Confirmed from the remote rather than from the push output: fetched
and compared `HEAD` to `origin/main`, identical. Working tree clean.

## A stale git lock had to be cleared first, and it is worth recording

`git add -A` failed with:

    fatal: Unable to create '.git/index.lock': File exists.

**Checked before touching it**, because that file existing usually means another
process is mid-write and removing it corrupts the index: 0 bytes, created
17:28:18, and `Get-Process git` returned nothing. Stale, left by my own
interrupted `git add`.

**Moved to `_to_delete/stale_git_locks/index.lock.20260827T172945`, not
deleted** — rule 1 does not carve out an exception for files that look like
scaffolding, and "obviously junk" has been wrong in this repo before.

## Vetted before staging, as last time

    .env / tokens / keys    none in the change set
    sc-ships/               0 files (gitignored - the models stay out)
    testing/_deploy/        0 files
    _to_delete/             0 files
    .last_build.json        0 files (gitignored - per-machine build state)
    largest staged          3.73 MB, testing/_src/loadout_data.gen.js

The commit also carries C1's uncommitted work in its own lane -
`loadout.src.html`, `decode_cga_nodes.py`, `build_hardpoint_placement.py` and
the hardpoint-transforms data - which was sitting in the tree alongside mine.

## Standing state

    working tree     clean
    origin/main      current - f667d7d
    testing site     current, 4 browser checks green at the gate
    live site        NOT published. Off the queue until Sleven raises it.

Next on the queue: Q5 the roadmap watcher past R0, Q6 the collector selftest,
Q7 labelling checks that cannot meet hard rule 16.

*(+497 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF to C1 — the whole weapon/armour/shield picture in one document. One live defect with a one-line cause and a zero-guesswork fix, one feature to cancel before somebody builds it, one thing I got wrong, and a schema gap. Everything here was measured on disk and every claim names the file it came from.

    from      C3 (Cowork), 2026-08-27
    for       C1, to route. Code owns every file named here; I wrote to none of them.
    method    measured on disk in this repo. Nothing fetched. No live source touched.
    replaces  nothing. This CONSOLIDATES five documents so you do not have to open
              five documents. They are listed in §9 if you want the working.
    PATCH     4.9 THROUGHOUT. Read §8 before quoting a number to anyone.

---

## 0. The four things that matter, in the order I would act on them

    1  ARMOUR NAMES ARE WRONG ON 31 SHIPS AND THE PAGE SHOWS IT   live, visible
    2  the fix is a UUID join that is exact 285/285                no matching
    3  cancel any "compare shields by damage type" feature         nothing to show
    4  Deflection was already built - I said it was not            my error, §7

Everything else is context for those.

---

## 1. THE DEFECT — one line, 31 ships, visible on the live ship page

`build_loadout_data.py`, line 740:

    "n": (it.get("stdItem") or {}).get("Name") or it.get("name")

That value renders in `loadout.src.html` as the hull-armour heading, `${a.n}`.

**Both of those source fields carry the wrong ship's name on 31 records.** Verified
directly in `ship-items.json`:

    className                    stdItem.Name (what the page prints)
    ARMR_ORIG_890J               "350r Ship Armor"
    ARMR_RSI_Perseus             "Constellation Andromeda Ship Armor"
    ARMR_RSI_Bengal              "Aurora Mk I MR Ship Armor"
    ARMR_AEGS_Idris_P            "Hammerhead Ship Armor"
    ARMR_AEGS_Idris_M            "Hammerhead Ship Armor"
    ARMR_ANVL_C8R_Pisces         "Gladiator Ship Armor"
    ARMR_ORIG_X1                 "M50 Ship Armor"
    ARMR_ANVL_Hornet_F7CS        "Anvil Void Ship Armor"
    ARMR_CNOU_Mustang_Delta      "Consolidated Outland Cavalry Ship Armor"
    ARMR_RSI_Zeus_ES             "Constellation Andromeda Ship Armor"

    209 armour items
    118 are "<= PLACEHOLDER =>"
     91 carry a name
     31 of those 91 name a ship other than the one in the className   -> 34%

**The className is right every time. Only the label is wrong.** So the defect lives in
whatever resolves a display name upstream of us, not in the numbers.

**Scope it honestly:** the ship page resolves armour through each ship's own `Loadout`,
so **no ship is showing another ship's multipliers.** The numbers on the page are
correct. It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud** — which is worse
than it sounds for a reference site.

**Do not fix this by correcting 31 strings.** §2.

## 2. THE FIX — an exact UUID join, 285 of 285, no matching of any kind

Each wiki vehicle record carries an `armor` block whose first field is a UUID that is
our armour item's UUID.

    wiki    vehicle -> armor.uuid
    ours    ship-items.json -> stdItem.UUID -> Armor block

    vehicles carrying armor.uuid                285
    joining to a scunpacked armour item         285
    join rate                                   100%

**Checked with a literal dictionary lookup on the UUID string.** No normalisation, no
lowercasing, no token containment, no fuzzy anything. **This project has been burned by
fuzzy matching twice this month and I did not do it a third time.**

    sources
      data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T021731Z/vehicles_page_*.json
      data-layer/external-sources/scunpacked-data/snapshots/20260827T030607Z/ship-items.json

**End-to-end spot check.** Avenger Stalker → `b3b23908-e9ab-4c46-93ed-ecd20aaf65c3`
→ `ARMR_AEGS_Avenger_Stalker` → Deflection Physical 11 / Energy 9, DamageMultipliers
Physical 0.8 / Energy 0.65. **Both sources agree on every value.**

**Why this beats fixing the labels:** deriving the armour's display name from the SHIP
rather than from the item's own broken `Name` removes the class of bug instead of
correcting 31 instances of it. It also covers the 118 placeholder records, which no
amount of label-fixing would. **Generic infrastructure over hard-coded exceptions —
the standing rule, applied to a naming bug.**

**Rule 12 for whoever implements it:** the check that matters is one that would FAIL if
the join fell back to name matching. Assert the Bengal's armour resolves to
`ARMR_RSI_Bengal` and that its printed name does not contain "Aurora".

**Whoever owns `build_loadout_data.py` decides the shape. I am not writing to it.**

## 3. CANCEL THIS FEATURE — every shield in the game is identical by damage type

Measured across all 73 shield items:

    distinct Absorption patterns    1   of 73
    distinct Resistance patterns    1   of 73

**One. Not one per grade, not one per class — one, for every shield in the game.**

    Absorption   Physical 0 to 0.45   Energy 1.0   Distortion 1.0
                 Thermal 1.0   Biochemical 1.0   Stun 1.0

    Resistance   Physical 0 to 0.25   Energy 0     Distortion 0.75 to 0.95
                 Thermal 0     Biochemical 0     Stun 0

**A grade A military shield and a grade D stealth shield absorb ballistics
identically.** Any brief proposing "pick a shield for the damage type you expect"
should be closed by pointing here — **it would be inventing a decision the player does
not have**, which is a worse failure than omitting a feature.

**Checked against the build, not just the data:** `loadout.src.html` shows shields as
HP and regen only. There is no absorption or resistance display anywhere in it. **So
this is not a rediscovery of something built — it is a reason not to build one.**

**It also shrinks a blocker I raised earlier.** `FINDING_the-interaction-is-computable`
said absorption and resistance may stack and I had not established how. Still true.
**But because the shield term is a constant, it cancels out of every comparison** — so
it blocks publishing an absolute damage number and blocks nothing else. Amend that
finding rather than withdrawing it.

**The one sentence this supports, for the weapon page:** shields stop all of an energy
shot and at most 45% of a ballistic one, and no shield you can buy changes that.

## 4. THERE ARE TWO DAMAGE TYPES IN SHIP COMBAT, NOT SIX — and both sides prove it

Across all 212 weapon damage blocks in the snapshot, against all 209 armour items and
73 shields:

    channel        weapons dealing it     defences that touch it
    Energy               114              shield absorbs 100%; armour 0.4-1.1;
                                          deflection varies by hull
    Physical              66              shield absorbs at most 45%; armour
                                          0.6-0.85; deflection varies by hull
    Distortion             3              shield resists 75-95%; armour ignores
                                          it completely
    Thermal                0              every multiplier 1.0, every deflection 0
    Biochemical            0              every multiplier 1.0, every deflection 0
    Stun                   0              every multiplier 1.0, every deflection 0

**Thermal, Biochemical and Stun are inert on BOTH sides simultaneously.** No ship
weapon deals them; no ship defence resists them.

**The consequence for the UI is concrete:** a six-channel damage display prints four
columns of 1.0 and 0 forever and teaches a new player that four mechanics exist which
do not. **Show two, plus distortion as a labelled special case.**

**Distortion is the interesting one and it is worth a sentence on the weapon page:**

    at the shield   heavily resisted    Resistance 0.75 to 0.95
    at the armour   ignored             DamageMultiplier 1.0 on 208 of 209
    deflection      ignored             0 on all 209
    penetration     ignored             PenetrationResistance.Distortion = 0, all 209

**Shields are the only thing that stops distortion, and armour does not slow it at
all.** Four fields agreeing. That is the kind of true, useful, non-obvious line
`BRIEF_the-weapon-features` asked for — woven into the weapon page, not printed
standalone.

## 5. THE SCHEMA GAP

`Armor.Deflection` and `Armor.PenetrationResistance` are six-channel per-ship fields
with **57 distinct Deflection value sets across 209 items**. They are rendered by the
ship page today (§7) but they have no home in the model.

**They belong on the armour side of the hybrid schema as real indexed columns, not
JSONB.** Six numeric channels, read on every ship page, compared across ships — that is
precisely the case the standing hybrid-schema decision reserves columns for. **JSONB
here would make the most-queried numbers on the page the slowest ones.**

Deflection tracks hull size cleanly when read by `className`:

    ARMR_ORIG_350r            Physical   9    Energy   7
    ARMR_RSI_Aurora_MR        Physical  11    Energy   9
    ARMR_AEGS_Hammerhead      Physical 531    Energy 380
    ARMR_AEGS_Idris_P         Physical 528    Energy 462
    ARMR_RSI_Bengal           Physical 550    Energy 479

## 6. TWO OPEN QUESTIONS — nobody should build on either yet

**6a. What Min and Max mean on the shield blocks.** Physical absorption runs 0 to 0.45
and the endpoints are not labelled. Almost certainly a function of shield charge.
**Not established. Do not publish a number that depends on it.**

**6b. What the wiki's `resistance_multiplier` is.** The wiki armour block carries it;
our canonical snapshot's `Armor` block has exactly four keys on all 209 items —
`DamageMultipliers`, `SignalMultipliers`, `PenetrationResistance`, `Deflection` — and
none of them is it.

They are not the same numbers. `damage_multipliers` has 9 distinct patterns with round
values; `resistance_multipliers` has 32 distinct patterns with values like 0.81, 1.08,
1.22, 1.35 — **and several exceed 1.0, meaning more damage taken.**

**I do not know what it is.** Derived by the wiki, dropped by our extractor, or the
same quantity at a different stage. **This is the first case I have found where the
non-canonical source carries something canonical does not**, which is worth someone's
attention given `canonical-source-decision.md`.

## 7. WHAT I GOT WRONG, stated plainly because you will read the finding

**I claimed Deflection was not on the site, not in the schema, and in no brief. False
on two of three.** `build_loadout_data.py` line 743 extracts it and
`loadout.src.html` renders it, with better framing than mine:

> *"Damage below these values is deflected outright."*

Penetration resistance, the damage multipliers and a "what gets through" block for
internals are all built too. **CURRENT-STATE has said since 08-22 that armour is a real
dimension.** I did not read it before writing.

**Root cause, and it is the same one as the shared-models erratum on 08-14: I measured
a source file and reported what the project does with it without opening what the
project does with it.** Measuring the input is not measuring the system. Worth naming
because it is now twice.

**One live discrepancy from that reconciliation:** I count **9** distinct
DamageMultiplier profiles across 209 items; CURRENT-STATE says **ten**. Probably the
template or placeholder records. **Somebody should close that gap rather than assume
it** — it is small, and small unexplained gaps are how the 4.9-as-4.10 error started.

## 8. THE PATCH CAVEAT — this is not a footnote

**Neither source is 4.10.**

    scunpacked   snapshot 20260827T030607Z, commit dated 2026-08-20
                 commit subject 4.9.0-LIVE.12344265           -> 4.9
    wiki         snapshot 20260801T021731Z, 01 August 2026     -> 4.9 or earlier

**Every count and every value in this document is 4.9.**

**The structural claims survive a patch:** the fields exist, the join is by UUID, the
labels are broken, shields carry one pattern each. **The values do not**, and neither
does §4's "inert on both sides."

4.10 contains a vehicle weapon rebalance that mentions armour explicitly — CIG wrote
that the S4 gatling was *"unable to defeat armor a Size 4 weapon should defeat."*
**That sentence is about exactly these fields.** So §3's "one pattern for all 73
shields" and §4's dead channels must be **re-measured after the 4.10 pull, not
assumed.** They are precisely what a balance pass exists to change.

**The gate before any of that:** the snapshot manifest records `git_head_commit` and
`git_commit_date` but **not the commit subject**, and the subject is the only place the
patch version appears. That one missing field is why two snapshots looked like progress
and neither said 4.9. **Add `git_commit_subject` to the manifest before the 4.10 pull**
— CIC's acceptance document makes it a hard gate and it should be.

## 9. The working, if you want it

    docs/FINDING_the-damage-multiplier-fields-exist-and-armour-is-mislabelled-2026-08-27.md
        the measurements, in full
    docs/ERRATUM_deflection-was-already-built-2026-08-27.md
        §7 above, at length. Read it WITH the finding or read neither.
    docs/RESPONSE_to-cic-three-questions-2026-08-27.md
        §4 above, plus the source-tier proposal for the claim register
    docs/ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md
        CIC's four controls and the manifest gate in §8. Delivered by me on his
        behalf - he has no device bridge.
    docs/CURRENT-STATE.md
        new top section dated 2026-08-27 carrying §1, §2, §3 in short form

## 10. What I checked and what I did not

**Checked, by measurement:** 73 shield items and both their blocks; 209 armour items
and all four of theirs; 57 distinct Deflection sets; 9 distinct DamageMultiplier sets;
the 31 mislabelled records; 212 weapon damage blocks across all six channels; the
285/285 UUID join across all six wiki vehicle pages; the Avenger Stalker end to end in
both sources. **Then, after the erratum, `build_loadout_data.py` and
`loadout.src.html` for what the project already does with all of it.**

**Did NOT check:**
- The order of operations between absorption and resistance. **Open. No absolute
  damage number should be published yet.**
- Whether Deflection subtracts, gates or scales. The page asserts it subtracts; I have
  the shape and the size correlation only.
- What Min/Max mean on the shield blocks. §6a.
- What `resistance_multiplier` is. §6b.
- Whether the deployed site matches the source I read.
- What the page renders for the 118 placeholder-named armour records.
- The 82 MB wiki items file. Not needed for any question answered here.
- **I built nothing and changed no code.** The only files I wrote are the documents in
  §9 and the new section in CURRENT-STATE.

