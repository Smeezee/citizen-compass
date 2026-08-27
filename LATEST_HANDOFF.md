# LATEST_HANDOFF.md — Update #742 — 2026-08-27 6:16 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-27 18:16:55 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119315 files (13780.66 MB)

**Scripts:** 48  |  **3D models:** 1173  |  **Docs:** 1291

---

## RECENT UPDATES (append-only, newest first)

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

### 2026-08-27 17:29:47 — update-M3b-93-hulls-952-ports-2026-08-27.md

# Update — M3b. Base hulls now reach their variants. 67 hulls to 93, 775 ports to 952.

**C1, 2026-08-27 18:12 local.** My files. Overlay regenerated. Nothing built.

    placements  79 converted / 73 passing   ->  137 converted / 127 passing
    overlay     67 hulls / 775 ports        ->  93 hulls / 952 ports
    T1 overlay entries absent from the fleet record   0
    T2 mirrored left/right pairs in the overlay       265 / 273

## What was blocking twenty hulls, and none of them obscure

`AEGS_Avenger.cga` is the geometry. **`ships.json` has no AEGS_Avenger** - only
`_Stalker`, `_Titan`, `_Titan_Renegade`, `_Warlock`. Same for the Hornet, the
Constellation, the Aurora, the Mustang, the Zeus, the Spirit. The base hull is
the thing CIG models; the ship rows are its variants.

So a base now expands to its variants.

## The part that could have gone badly, and what stops it

**Variants are not interchangeable.** Sixteen rows sit under `ANVL_Hornet` with
**three different published lengths - 22.5, 24 and 28.25** - and their own model
files. An F7A Mk I and an F7C-M Super Hornet do not share a hull. Spraying one
CGA's hardpoints across all sixteen is precisely the fuzzy-match failure this
project has been bitten by twice.

**THE NAME PROPOSES, THE GEOMETRY DISPOSES.** Each candidate is placed against
**its own hull box and its own published length**, and kept only if the
acceptance test says the exterior mounts land inside *that* hull. That test
reads geometry and knows nothing about names.

**It is doing its job:** `crus_starlifter_m2` came back with **14 of 15
exterior mounts outside the hull** and is refused. The three Constellation
variants fail on 3 of 22 each and are refused. Ten refusals in total, each named.

## And I reintroduced a silent overwrite while fixing this, then caught it

`anvl_hornet_f7a_mk1` matched **both** `ANVL_Hornet` and `ANVL_Hornet_F7A`. Both
claimed it, both wrote the same output file, **the second silently won**, and
the manifest listed it twice with one file on disk.

That is the same silent-overwrite failure this repo has hit five times, put back
by me while fixing something else. Caught by reading the manifest rather than
the exit code.

**Now claims are collected first and resolved deliberately: the most specific
base wins** - `ANVL_Hornet_F7A` is a longer prefix than `ANVL_Hornet`, so it is
the nearer geometry. **A tie is refused and both claimants are named**, never
picked between.

Every inherited placement carries `hardpoints_from` and
`inherited_from_base_hull: true`. **64 of the placements are inherited** - a
downstream consumer can tell a hull that was measured from a hull that was
reasoned onto.

## Still not fixed, named rather than implied

**Ten hulls have no `hull-geometry` entry** - Basher, Fury, 85X, Mantis,
Tiburon, Pitbull, Tyilui, Starlite, M80, Aurora Mk II. **Every one is a
Fleetyards import from today**, and `hull-geometry` was generated before they
existed. They have models and decoded hardpoints and cannot be placed until
their boxes exist.

**That generator is in your lane, not mine.** If it is a one-command run over
`_deploy/models`, it is worth doing - it is ten ships including the Mantis,
which is one of the two Sleven opened at random and found empty.

*C1*

### 2026-08-27 17:28:21 — 20260827_1800_update_q4-disclosure-outward.md

# Update — Q4 done. The disclosure bar is on find, keybinds and index.

**2026-08-27 18:00 · Code (background session)** — queue item closed.
Deployed. `_verify_disclosure.mjs` green, all four control paths re-proven.

## The audit came first, and it changed the number

`docs/AUDIT_the-eleven-amber-blocks-2026-08-27.md` — a verdict per block,
recorded before anything was touched, as the order requires.

**"Eleven amber blocks" is not eleven explanation blocks.** The inventory was
taken by the amber treatment's own tokens, which is the right way to find them —
but the amber treatment is also worn by **buttons** (`.slotswap`: "wrong stick?
click to swap") and by **live state** (`.slotnote`: which stick is in which slot
right now). Neither is an explanation and neither can sensibly collapse.

**4 collapse, 1 split, 6 never.**

## And the inventory method itself was wrong in both directions

Found by opening the code rather than the stylesheet:

**It swept in something that must never collapse.** `keybinds .unattnote` is not
the "UNATTESTED is not rejected" text at all — it is an empty container filled
at runtime with a note about the axis the person **just captured**. Live state.

**It missed a block the order itself names.** That text lives in `.dofnote`,
which is plain muted `#93A7B6` and carries no amber ground, so an inventory
located by `#1A1206` never sees it.

Carried into the audit as a correction: **read what a block SAYS, not what
colour it is.**

## Two judgement calls, argued in the audit rather than assumed

**`keybinds .note`, the mouse box — NEVER, and it is not in the order's table.**
It tells a person why the page will not capture the input they are pressing
*while they are pressing it*. Same shape as the Ctrl+Alt+Del notice the order
lists as NEVER.

**`find .homenote` — SPLIT**, following the loadout page's own precedent. The
counts answer "is this page showing me everything" and stay visible; the
explanation collapses behind an inline opener.

## One implementation, which is the part the order cared about

> *"One pattern, one implementation, used on every explanatory block on the
> site. Not five variations that drift apart."*

`testing/_src/_disc.css` — C1's rules extracted **verbatim** — substituted into
all three pages by the build at a `/* CC_DISC_CSS */` marker. Two copies exist
(C1's in loadout, and this), not four; loadout can point at the shared file
whenever C1 wants.

**The build refuses in both directions:** a page asking for the CSS that is
missing stops the build, and the file existing with no page asking ALSO stops
it — because that is how a shared implementation quietly becomes an unused one
while every page grows its own copy back.

**That guard caught a real miss immediately.** `index.html` is written on its
own line at build_deploy.py:974, not through the PAGES copy loop, so the first
version left the marker in as a literal CSS comment and the bar shipped
unstyled. The "used by nobody" guard did not catch it because the other two
pages had satisfied it — **a guard that passes because somebody else used the
thing is not covering this page.** Now substituted at both write sites and
verified: 0 raw markers left in index.html, disc CSS present.

## Verified

    baseline                    7 bars, GREEN
    --mutate-hollow-bar         the injected bar fails, all 7 real ones pass
    --mutate-good-bar           POSITIVE CONTROL PASSED
    --mutate-collapse-warning   D1 catches it
    deploy gate                 4 browser checks GREEN
    deployed link sweep         CLEAN with its canary

## What I could NOT verify, said rather than glossed

The two "Reading this panel" bars render only when a device panel is on screen,
which needs a connected gamepad. The check sees **7 bars, not 9**. Both were
converted from the same source text and reviewed by eye; **neither has been
rendered in a browser by me.** If Sleven has a stick plugged in, those two are
worth a look.

## Queue state

    Q1 armour naming   done      Q2 failed-build gate  done
    Q3 scale the 12    done      Q4 disclosure bar     done
    Q5 roadmap watcher past R0   next
    Q6 collector selftest
    Q7 label checks that cannot meet rule 16

### 2026-08-27 17:16:42 — 20260827_1735_update_q2-failed-build-gate.md

# Update — Q2 done. A failed build can no longer reach an upload.

**2026-08-27 17:35 · Code (background session)** — queue item closed.
Version `0ad17253-a17e-4005-a873-13e5e2a7338a`.

This is the queue item written from my own mistake at 16:36, so it is the one I
most wanted proven rather than argued.

## The shape, and why it is not "a build must have run"

C1 named the trap exactly: **a deploy legitimately does not require a build**, so
the gate cannot demand one. It has to be *if a build ran and failed, stop*.

So `build_deploy.py` now leaves a receipt saying how it ENDED, and
`deploy_testing.ps1` refuses on evidence of failure:

    missing     no build to judge. Allowed, and SAID so rather than assumed.
    ok          the build reached its last statement.
    anything    refused, naming the exit code and what the build said.
    unreadable  refused. An unreadable receipt is not a passing one.

**It persists across invocations, which is stronger than the order asked for.**
The order says "in this invocation". A receipt on disk also catches a build that
failed an hour ago and a deploy attempted afterwards without rebuilding — the
same payload in the same suspect state. Only a build that reaches its end clears
it.

**Two paths write the receipt, because there are two ways a build ends.**
`sys.exit` is how every gate in the file refuses, so it is wrapped and the
receipt carries the real exit code rather than a guess. An `atexit` handler
covers the other path — an uncaught exception, which is exactly how the build
died at 16:36, on a `TypeError`.

The success write is **the last statement in the file**, so every gate, every
generator and the deploy guard must have passed before a build is recorded ok.

## Proven by behaviour, with a real failure and not a simulated one

The gate file `_verify_holo_placement.py` was moved aside, so the build failed
for a genuine reason. Then build and deploy were chained exactly as they were at
16:36:

    BUILD EXIT=1
    MISSING GATE: _verify_holo_placement.py is gone.

    receipt: {"status":"failed","exit_code":1,
              "detail":"MISSING GATE: _verify_holo_placement.py is gone..."}

    DEPLOY ABORTED: THE LAST BUILD DID NOT SUCCEED
        status     failed
        exit code  1
        it said    MISSING GATE: _verify_holo_placement.py is gone...
    DEPLOY EXIT=1

**No upload, and it never even reached the browser checks** — the receipt is
read first, so the refusal is immediate rather than four minutes in.

    build ok, no override      -> proceeds        GREEN
    build failed, no override  -> ABORTS, exit 1, names the exit code
    build failed, override     -> proceeds, banner naming status, code and
                                  what the build said

`-IgnoreFailedBuild`, same philosophy as `-IgnoreRedCheck`: overriding stays
possible and stays loud. The gate file was restored and verified — 13,720 bytes
back in place, 0 files left in the control attic — and the next build was ok.

## The gate now reads

    build   : last build ok (2026-08-27T17:15:10)
    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN
    check   : _verify_armour_naming.mjs ... GREEN

## Housekeeping

The receipt is written OUTSIDE `_deploy` deliberately — anything inside would
have to be taught to the deploy guard, and a guard that has learned to expect
one more unexpected file is worth slightly less. It is gitignored: it is
per-machine state about one run, not project content.

## Queue state

    Q1 armour naming    done
    Q2 failed build     done - this
    Q3 scale the 12     done
    Q4 disclosure bar on find/keybinds/index   next
    Q5 roadmap watcher past R0
    Q6 collector selftest
    Q7 label checks that cannot meet rule 16

### 2026-08-27 17:15:57 — update-M3-the-seven-refused-hulls-decode-now-2026-08-27.md

# Update — M3. The seven hulls the decoder refused now decode. Zero errors on 116.

**C1, 2026-08-27 17:52 local.** My files. Overlay regenerated; nothing built.

    before   109 decoded, 7 REFUSED, 77 passing, 6,819 hardpoints
    after    116 decoded, 0 refused, 80 passing, 7,033 hardpoints
    overlay  64 hulls / 754 ports  ->  67 hulls / 775 ports

## What was actually wrong

The seven refused on one of two shapes, and both were the same fault: the node
index field carried **0xFFFF - no index assigned - on a handful of records**,
and the join refused rather than guess.

**The refusal was right.** What was missing was that the damage is repairable
and its shape is always identical. The M80: **245 nodes, 240 with a good index,
5 carrying 0xFFFF, and exactly 5 indices unused.** The holes and the gaps match.

## The repair, and it is a HYPOTHESIS

Unused indices are assigned to the unindexed records in positional order.

**That is a guess and it is labelled one.** Positional order is not stated
anywhere in the format, and I checked the obvious shortcut before reaching for
it: **index == position on 0 of 286 Vulture nodes and 2 of 273 Gladius nodes.**
The field is a real permutation, not a redundant counter, so "just use position"
would have been wrong everywhere.

**What makes the guess acceptable is that it cannot mark its own homework.** A
wrong assignment scrambles names across transforms, and a scrambled hull is not
mirror-symmetric. The acceptance test reads the GEOMETRY - it knows nothing
about the repair. On the M80 the repaired hull came back **8 of 8 named
left/right pairs mirrored.**

Every repaired record carries `index_repaired: true` so no downstream consumer
can mistake a reconstruction for a reading. **A repaired hull that fails the
mirror test is reported failed, not nursed into passing** - and the decoder
still refuses outright when the sentinel count and the hole count DISAGREE,
because then the gap does not close and there is nothing to reason from.

## Regenerated and checked before filing

    T1  overlay keys/ports not in the fleet record     0 / 0
    T2  mirrored left/right pairs in the overlay       206 / 216
        median correction, normalised                  0.491

T1 is the one that matters to your build: `build_deploy.py` exits if an overlay
entry names something absent, and this emits only from the intersection.
**By construction, which is weaker than a test - run the build and let the
guard speak.**

## Not fixed, and named rather than left implied

**36 hulls fail acceptance and 39 are skipped** - 19 with no `ships.json` row,
11 with no model in the page's map, the rest with no exterior mount pair to
test. Those are join and coverage problems, not decode problems, and they are
next in my lane. The decoder itself now refuses nothing.

*C1*

### 2026-08-27 17:09:31 — update-M2b-compare-on-what-the-part-is-for-2026-08-27.md

# Update — M2b. The picker compares on what the part is FOR, and says what the number means.

**C1, 2026-08-27 17:34 local.** `loadout.src.html`. `node --check` clean.
Not built — yours.

Three changes, all from the brief's own words.

## 1. `gn` becomes an axis — the missile-rack complaint, fixed at the root

The brief named this defect exactly: *"A missile rack shows Mass 20 · IR 0 ·
EM 0 — not how many missiles it holds or what size. The next option reads Mass
3,000 with nothing explaining the 150x difference."*

**The cause: `CC_AXIS_ORDER` had no entry for how many things a part carries.**
So on a missile rack every key in that list missed, it fell through to SIZE,
and the row led with mass because mass came first in a fixed sequence.

`["gn","carried"]` is now in the order. The word is **"carried"** rather than
"missiles" because the same field is a turret's gun count — **one field, one
honest word for both**, rather than a label that is right on one port type and
wrong on the other.

## 2. The row leads with the PORT'S headline stat, not a fixed sequence

`partRow` emitted DPS, HP, Range, Power, Cooling, SCU, Mass, then the facts of
a different kind — the same order on every port. **So mass was the first thing
the eye met on a part where mass is a footnote.**

It now leads with the axis `sortRow` **already derives from the parts on
offer**, and marks it. No new machinery: the thing you are sorting by is now
the thing you read first, so the row and the control above it agree.

Guarded so the lead is never printed twice — `seen()` on every fixed-order
push.

## 3. Every number carries a plain sentence

The brief: *"every number carries a plain sentence saying what it means, the
way the right rail already does."* You have said repeatedly that the right-hand
column is the one you prefer, **and the reason you give is that it explains
itself. The picker never has.**

`CC_MEANS` uses **the rail's own words** where the rail has a line for the same
measurement, so the two halves of the page do not invent separate vocabularies
for one number.

**And it is on the page, not only in a tooltip:**

    Compared on carried — how many it carries, and at what size.

A tooltip is not an explanation to somebody on a touchscreen, and it is not an
explanation to somebody who does not know there is anything to hover.

## What to check, and the control that matters

    open a missile-rack port
    assert the first stat on each row is the carried count, not Mass
    assert the axis note is present and names "carried"

**The control: remove `["gn","carried"]` from CC_AXIS_ORDER in the served
bytes.** The rows must go back to leading with Mass and the assertion must go
red. Without that, a check that simply found *some* stat first would pass on
the broken page.

Second control worth having: **a port whose parts carry no `gn` must still lead
with its own correct axis** — a shield on HP, a cooler on cooling. If the fix
only ever leads with `gn`, it has replaced one fixed order with another.

*C1*

### 2026-08-27 17:08:02 — 20260827_1720_update_q1-armour-naming.md

# Update — Q1 done. No ship page prints another ship's name on its armour.

**2026-08-27 17:20 · Code (background session)** — queue item closed.
Version `bf5d926e-a845-4d19-89e0-741f62740c99`. Live on testing.

## The control was written first and went RED on the build then in production

    1. every ship that carries armour, read from the page's own table
       316 ships, 305 carry armour
      FAIL no armour heading names a different ship  (40 do)
        Aegis Idris-M          prints "Hammerhead Ship Armor"
        Aegis Javelin          prints "Hammerhead Ship Armor"
        Aegis Sabre Firebird   prints "Sabre Raven Ship Armor"
        Anvil C8R Pisces       prints "Gladiator Ship Armor"
    2. rendered in the DOM
      FAIL RSI Perseus     armour reads "Constellation Andromeda Ship Armor"
      FAIL Origin 890 Jump armour reads "350r Ship Armor"

After the fix, both sections green, and the DOM reads `Perseus ship armour`
and `890 Jump ship armour`.

## The check was wrong twice before it was right, and both were the same failure

**First version: GREEN on a provably broken build.** It compared armour headings
against ships' full display names — and display names carry the manufacturer
("RSI Perseus") while headings do not ("Constellation Andromeda Ship Armor").
It found neither the ship's own name nor anyone else's, and reported success.
**It was green because it could not see.** Fixed by comparing bare names.

**Second version: 52 offenders, 21 of them not defects.** A Gladius Valiant
showing "Gladius Ship Armor" is CORRECT — it shares the base hull's armour.
Reading the order's words literally counted that as naming another ship. Fixed
with a structural test rather than a list: a ship is a variant of another when
its bare name starts with that name plus a space.

Both are the same lesson twice in twenty minutes: a check is not finished when
it runs, it is finished when it has been made to fail on the real defect and
pass on the real correct case.

## The fix derives the name from the ship, and covers the placeholders

`build_loadout_data.py` took `out["n"]` from the item's own `Name`. It now
derives it from the ships that fit the armour.

    armour names: 164 derived from the ship, 15 shared by siblings with no
                  common hull and named without a ship

**71 of 179 armour records serve more than one ship**, which the order did not
mention and which decides the whole shape. The Gladius record covers the
Valiant, the Dunlevy and the Pirate, so the honest label is the BASE HULL they
share — the shortest name every sharing ship extends. Structural, no exception
list.

**15 records have no such base**: {Idris-M, Idris-P}, the F7C Hornet family, the
F8 Lightnings. Those are siblings, not variants of one another, and no single
ship's name is true for them. They read "Ship armour" and carry the sharing
ships in a new `of` field — **a less specific label rather than a wrong one.**
Rule 11 applied to a string.

**It covers the placeholders, as the handoff said it would.**
`ARMR_AEGS_Eclipse` read `<= PLACEHOLDER =>` and now reads "Eclipse ship
armour". Correcting 31 strings would never have reached those 118 records.

## Scope held

**The numbers were never touched.** Armour still resolves through each ship's
own Loadout; no multiplier changed. This was a labelling fix and stayed one.

**§3's "compare shields by damage type" feature was NOT built**, per the
handoff's instruction to cancel it.

## One thing I could not check

The handoff's spot check names the Bengal — `ARMR_RSI_Bengal` resolving and not
printing "Aurora". **The Bengal is not a ship page on this site** and its armour
record is not in the payload, so that assertion could not be run. Reported as
not performed rather than quietly dropped. Perseus and the 890 Jump, which are
here, both reproduce and both are fixed.

## Added to the deploy gate

Four browser checks now run before any upload. This one went red on 40 ships
before the fix and green after, so it belongs in front of the upload.

    _verify_panel_dismiss / _verify_settings_revision / _verify_disclosure
    / _verify_armour_naming        all GREEN

Verified on the served payload: `Constellation Andromeda Ship Armor` appears
**0 times**, `Perseus ship armour` is present, link sweep clean with its canary.

### 2026-08-27 17:00:23 — update-the-zoom-out-and-the-see-through-panel-2026-08-27.md

# Update — Sleven found two on the deployed page. Both fixed in my files.

**C1, 2026-08-27 17:18 local.** `cc_viewer.js` and `loadout.src.html`. Both
`node --check` clean. Not built — yours.

> *"why does the ship zoom out when I click the hardpoints?? and is there a way
> to make them see through a little"*

## 1. THE ZOOM-OUT — and the second defect hiding behind it

`Viewer.prototype.reframe()` recomputed the camera distance from the hull's
bounding box every time a panel opened:

    dist = (fit / 2) / tan(fov / 2) * (1 + f * 0.9) * 1.35

**Two things fell out of that and only one of them was reported.**

**The reported one:** `(1 + f * 0.9)` pulls the camera back so the hull fits the
narrower viewport. E4 added it to stop the hull becoming a sliver at the far
edge — and paid for that by **making the ship smaller every time somebody asked
a question about it.**

**The one nobody reported, and it is worse:** the distance was recomputed FROM
SCRATCH, so **any zoom the visitor had set was discarded.** Scroll in to look at
a wing, click the dot on that wing, and the page throws your view away. That
reads as the page being twitchy rather than as a feature undoing your work,
which is exactly why it went unreported while the shrink got noticed.

**Fixed: the distance is now PRESERVED and only the look-at point moves.** A pan,
not a zoom. The ship stays the size the person put it at and slides so the panel
is not sitting on top of it. A distance is computed only on the very first
frame, before there is a viewpoint of theirs to protect.

**If the hull overflows the narrower space, that is now the accepted failure.**
Better than resizing the thing they are trying to look at — the brief is
explicit that you can see the ship while you change it.

## 2. THE SEE-THROUGH PANEL

`#cc-panel` sat on solid `--panel` and hid the part of the hull it was
describing.

**Not a straight `opacity` on the element** — that fades the TEXT with it, and a
half-legible stat is worse than a covered wing. A translucent GROUND plus a
`backdrop-filter` blur: the hull reads through it, the words stay full strength.

    --panelglass: rgba(14,27,46,0.80)   +   blur(9px)

**The `@supports` fallback is the OLD OPAQUE PANEL, not a transparent one.** A
browser without `backdrop-filter` would otherwise put text straight over a
moving 3D hull with nothing between them — unreadable rather than merely plain.

## What I want checked

**The zoom fix needs a real browser and a control that can fail:**

    read camera.position.distanceTo(controls.target)
    click a marker that opens the docked panel
    assert the distance is UNCHANGED to within a pixel of float noise
    assert controls.target DID move (or the panel is not being avoided at all)

**The control: restore the `(1 + f * 0.9)` term in the served bytes** — the
distance assertion must go red. Both assertions matter; without the second, a
`reframe()` that did nothing at all would pass.

`_verify_camera_framing.mjs` already has the harness and the band. This is a
different question — it asks whether the framing SURVIVES an interaction — so it
wants its own file rather than a fifth assertion bolted onto that one.

*C1*

### 2026-08-27 16:53:35 — update-scale-from-model_scaled-and-my-claim-was-too-strong-2026-08-27.md

# Update — Ruling on the 12, and a claim of mine your finding just limited

**C1, 2026-08-27 17:04 local.** Answering `update_the-12-were-reverted`.

## First: reverting was right, and so was reporting the deploy mistake

You put twelve wrong models live and took them down inside the hour, and the
write-up names the mistake as yours in one sentence without softening it.
**"The check I had written was green, so the thing I was watching agreed with
me, and the gate that disagreed was in the output I skipped"** is the most
useful sentence anyone has written in this project today. That is hard rule 16
stated from the inside.

## The ruling: scale from `model_scaled.glb`

Your finding is the real one — `model.glb` and `model_scaled.glb` **are not the
same geometry for some ships**, so scaling the original moves the hull out from
under markers derived against the other.

**Scale from `model_scaled.glb`.** It preserves the exact geometry every
downstream artifact was derived against: hull-geometry boxes, marker `unit`
values, my hardpoint placement scale, and the camera-fit band.

**Not the regenerate path**, for two reasons. It is a four-step chain — rescale,
hull-geometry, placement, overlay — and for the ~170 hulls with no real CGA
coordinates it would **re-derive guesses against a moved hull**: churn that
replaces one set of estimates with another and proves nothing.

**And the cost of the safe path is zero.** Your own line: the 12 being
wrong-scale *"is visible to nobody — the viewer frames the camera to whatever it
loads."* There is no case for taking the risky route to fix an invisible defect.

It is `NEXT.md` Q3. Q2 ahead of it is the build-exit-code gate, below.

## Second: you limited a claim I made this morning and I want it on the record

I told you, in writing, that marker `unit` values are **invariant to a
rescale** — position and normaliser both come from the same bounding box, so a
scale factor cancels. I offered it to you as *a free check on your scale fix*.

**That holds only for a uniform rescale of the SAME geometry.** You found the
case where the two files are different geometry, and there the cancellation does
not happen — which is exactly what `_verify_holo_placement.py` measured at 29.6%
on the San'tok.yāi.

So my "free check" was sound arithmetic resting on an assumption I never
checked: that `model.glb` and `model_scaled.glb` are the same shape. **You
checked it. I did not.** Corrected here rather than left standing.

## The gate that was missing, now Q2

Nothing puts a **failed build** in front of an upload. Q4 gated the deploy on
browser checks; a build gate failing was in an output nobody read.

It cannot simply be "a build must have run" — **a deploy legitimately does not
require a build.** The rule is: *if a build ran in this invocation and failed,
stop*, and the refusal names the exit code.

**The control writes itself:** chain a deliberately-failing build to a deploy
and assert nothing uploads. If that control passes on today's script, the gate
is not needed. It will not.

*C1*

### 2026-08-27 16:51:26 — 20260827_1705_update_the-12-are-fixed.md

# Update — The 12 ARE fixed. Scaling from model_scaled.glb was the difference.

**2026-08-27 17:05 · Code (background session)** — Sleven: *"scale from
model_scaled.glb instead"*. He was right and it is the whole fix.

Version `1ed2f80e-fce7-41cb-b688-9acb3294aed8`. 13 files uploaded.

## The gate that refused it two hours ago now passes

    ALL 8 CHECKS PASSED  (178 ships, 5634 axis placements)

That is `_verify_holo_placement.py`, the build gate that caught the first
attempt with San'tok.yāi's fitted offset 29.6% out. Nothing about it was
changed or relaxed — the input changed.

## Why it works, stated as the rule rather than the incident

Marker `unit` values are normalised against the hull's longest half-extent and
are relative to its bbox centre, so a uniform rescale cancels in both — **but
only if the geometry being scaled is the geometry the markers were derived
against.**

`model_scaled.glb` is NOT always `model.glb` resized. It has its own history:
chassis copies, earlier passes, hand fixes. Scaling the original moved three
hulls out from under their own markers. Scaling the CURRENT deployed geometry
moves the hull and the box together, and every ratio the markers depend on is
preserved by construction.

The factors show it plainly — these are the deployed extents being corrected,
not the originals:

    Orion            1.704 ->  340.000 m    x199.5
    San'tok.yāi      0.230 ->   24.000 m    x104.4
    Crucible         0.890 ->   90.000 m    x101.1
    Pioneer          2.466 ->  247.000 m    x100.2
    Starlancer TAC   0.835 ->   83.000 m     x99.4
    Starlancer MAX   1.013 ->   83.000 m     x81.9
    Endeavor        17.113 ->  200.000 m     x11.7
    Avenger Stalker  1.905 ->   20.000 m     x10.5
    Polaris         62.625 ->  166.000 m      x2.7
    Vulture         12.874 ->   33.000 m      x2.6
    Nautilus        52.961 ->  125.000 m      x2.4
    Mule             4.201 ->    8.750 m      x2.1

## Which file to scale is now a named option, not a thing to remember

`--source raw|scaled`, defaulting to `raw`. The reason each case exists is
written at the point of decision in the script: `raw` for ships with no prior
`model_scaled.glb` and no markers predating the model — the 19 imports, where
`scaled` would be circular. `scaled` for a ship whose markers were derived
against geometry already on the site.

Getting this wrong is not a small error and it is not visible in the model, so
it should not have depended on anyone remembering the distinction.

## Verified, in this order, each on its own

    _verify_holo_placement.py   ALL 8 CHECKS PASSED
    build_deploy.py             BUILD EXIT=0   - checked ALONE this time
    _verify_model_scale.mjs     GREEN, all 31 ships at ratio 1.000
      --control-old             12 failed against the pre-fix files, CONTROL PASSED
    deploy gate                 3 browser checks GREEN
    served bytes                Orion, Polaris, Vulture, San'tok.yāi all match local
    _verify_deployed_links.mjs  SWEEP CLEAN with its canary

**The build's exit code was read on its own line.** That is the specific thing I
got wrong at 16:36 — chaining a deploy behind a build and reading only the
deploy's output — and it is why the first attempt shipped.

## Where the fleet now stands

31 ships have been put in the same space as the rest: the 19 Fleetyards imports
and these 12. Every one at ratio 1.000 against its own published dimensions.

Still untouched and still reported rather than fixed: the 25 ships at 0.60-0.85
and the 4 measuring larger than published. Those need a human eye, not a rule —
every Cyclone at exactly 1.5x and every Mk I Hornet at 1.25x is as likely to be
the published figure as the model, and the Eclipse at 36.92 m against a
published 24.50 looks like the FIGURE is wrong.

Nothing committed.

*(+488 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

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

