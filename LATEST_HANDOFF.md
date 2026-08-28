# LATEST_HANDOFF.md — Update #795 — 2026-08-27 10:36 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-27 22:36:12 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119492 files (13785.50 MB)

**Scripts:** 52  |  **3D models:** 1109  |  **Docs:** 1338

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-27 22:35:29 — 20260827_2237_update_deployed-c1s-changes-and-drift-is-green-again.md

# Update — Deployed. C1's transparency and panel-side changes are live on testing, and `_verify_deploy_drift.py` is back to 12/0.

**2026-08-27 22:37 local · Code (background session)** — Sleven: *"build and
deploy it"*. Version `8589fbab-851a-4c58-ba49-936b1e77902b`.

## Exactly the two files C1 touched, and no others

    + /cc_viewer.js
    + /loadout.html
    Uploaded 2 files (522 already uploaded)

**Two uploads for two changed sources** is the correct blast radius. If a third
file had moved, that is the number that would have said so.

Build clean: seven in-process gates passed, `deploy guard: safe to deploy`,
4 browser checks GREEN, hull markers unchanged at **6,400 on 271 hulls**.

## THE DETECTOR IS GREEN AGAIN, AND THAT IS THE POINT

    _verify_deploy_drift.py    12 passed, 0 failed    exit 0

It was red at 22:18 **because** `_deploy` and `_src` disagreed after C1's write.
A deliberate build is what makes them agree, so this going back to 12/0 is the
proof that the payload is what the source says it is. **The rule 14 detector
went red on an unauthorised write and green again once the write was
acknowledged and shipped through the front door.** That is the whole mechanism
working end to end, for the first time.

## Both features confirmed in the SERVED bytes, not in the build log

    served /cc_viewer.js     hullAlpha: 0.86        13 occurrences
    served /loadout          let side = (px <= sw/2) ? "left" : "right"   present
    served /loadout          the old `let side = "right"` rule             GONE
    served /loadout          C1's rationale comment                        present

And the served page is byte-identical to what was built:

    served  sha256 6d8d2e279a6f18c6...
    local   sha256 6d8d2e279a6f18c6...

**Fetched from `/loadout`, not `/loadout.html`.** My first attempt used the
`.html` path and came back **0 bytes**, which I nearly wrote up as a missing
feature — the worker serves the extensionless route. Worth recording: a
zero-byte fetch reads exactly like a page that lost the change.

## Still green after the deploy

    _verify_deployed_links.mjs    SWEEP CLEAN, canary reporting
    Drake Buccaneer               8 dots, 8 visible, model loaded

## The provenance, stated once more so the record is complete

These two changes entered `testing/_src/` from C1 rather than through this
session — a rule 14 breach in the channel, detected at 22:18, reported at 22:28,
and authorised by Sleven at 22:33. **The content was never the objection**; every
control that touches it was green before the deploy and after.

What rule 14 asks for is that such a write be loud and immediate rather than
found later in a diff. It was.

Nothing committed since `2fc7008` — the two source files and the rebuilt payload
are in the working tree. Live site untouched; its worker still 404s.

### 2026-08-27 22:32:46 — 20260827_2233_update_building-c1s-transparency-and-panel-side.md

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

### 2026-08-27 22:26:23 — 20260827_2228_update_rule-14-fired-c1-wrote-into-testing-src.md

# Update — RULE 14 FIRED. C1 wrote directly into `testing/_src/` at 22:10 and 22:15, and the drift control caught it. Also: Q7 tranche 1 is done.

**2026-08-27 22:28 local · Code (background session)** — the rule 14 event is the
headline, so it goes first.

---

# 1. A SECOND WRITER IN `testing/_src/`

Two files were modified after my last build (21:43) and after tonight's commit
`2fc7008`. **I did not make these edits.**

    testing/_src/cc_viewer.js       22:10:29
    testing/_src/loadout.src.html   22:15:22

Both diffs name their author in their own comments: **"(C1, 2026-08-27 …)"**.

## Hard rule 14

> **`testing/` — Claude Code, and nothing else.** … **C1 does not push files into
> `testing/`** and C2 does not write to the repo at all.

The rule records two previous instances, both on this exact file family:

> a concurrent session rewrote `_layer.src.html` mid-verification, twice in one
> evening. Once it deleted a keybinds overlay and a compliance strip that were
> caught only by a marker check before deploy.

**This is the third.** It was caught the way rule 14 says it must be — *"make an
unauthorised write loud and immediate, and refuse to ship un-provenanced content.
Detect on every build, fail the deploy, name the files that moved"*:

    3. THE COPIED FILES AGAINST _src, EVERY INJECTION DECLARED
      FAIL  loadout.html no longer contains its _src text outside the declared injections
            cc_viewer.js differs from _src/cc_viewer.js
    4. THE ASSEMBLED FILE - index.html, PROVEN BY REBUILDING
      FAIL  and so is every copied file (moved: loadout.html, cc_viewer.js)

**`_verify_deploy_drift.py` is not broken. It is the detector, and this is the
first time it has fired in anger.** I green-lit it at 21:32 tonight; it went red
the moment a write it did not expect landed.

## WHAT was written, because the channel is the problem and the content is not

Both changes are substantial, well-commented, and **quote Sleven's own words**:

**`cc_viewer.js` — the hull becomes translucent.** A new `hullAlpha: 0.86` dial
and a `uAlpha` shader uniform, against *"is there any way we can make it a little
bit more see through, a little bit more transparent"*. `solid` was
`transparent: false`, so the only way to see into a ship was `xray`, a different
look entirely — there was no "a little bit".

**`loadout.src.html` — the panel opens on the side of the screen the marker is
on, and the ship stops moving.** Against *"if I'm looking straight at the ship,
and it would be the ship's right wing but it'd be on my left, it should open the
menu on the left side of the screen."* The old rule opened right and PANNED THE
SHIP to make room, which is the shifting Sleven reported.

**This is authorised work arriving through the wrong door.** I am not reverting
it and I am not going to characterise it as damage. What rule 14 exists to stop
is a write nobody notices, and the point of the detector is that this one did not
go unnoticed.

## The state of play, exactly

- **The deployed testing site (`bbd2a7d7`) does NOT carry either change.**
- **`testing/_deploy` now DOES.** The drift control's section 4 rebuilds by
  design, so at 22:22:32 it rebuilt the payload with C1's `_src` in it. The
  build directory and the served site no longer agree.
- Nothing was deployed, and I have not built since.

## C1's work is GREEN under every control I can point at it

Run after the 22:15 edit, against the current source:

    _verify_stage_panel.mjs      ok   (the panel's own control)
    _verify_ship_page.mjs        ok   242 assertions
    _verify_panel_dismiss.mjs    ok
    _verify_settings_revision.mjs ok
    _verify_disclosure.mjs       ok
    _verify_armour_naming.mjs    ok
    _verify_look_panel.mjs       ok

**So the objection is procedural, not substantive.**

## THE DECISION I AM NOT TAKING ON MY OWN

Sleven's standing instruction is that the day's work reaches the test page the
same day, and this is his own request implemented. Against that, rule 14 says
**refuse to ship un-provenanced content**, and this session neither wrote nor was
handed these changes.

**Say build-and-deploy and I will**, in the next message — the payload is already
rebuilt, the checks are green, and it is one command plus verification. I am not
going to infer it.

---

# 2. Q7, TRANCHE 1 — 11 files labelled

    labelled     22  (7 INDEPENDENT, 15 UNPROVEN)
    unlabelled   75     (was 86)
    malformed     0     GREEN, exit 0

The baseline shrank by exactly 11. The gate fails if a line names a file that no
longer needs it, so the debt list cannot rot into fiction.

**One INDEPENDENT, and it had to earn it:** `_verify_deploy_guards.py` runs the
REAL scripts as subprocesses and reads only their exit codes and printed
refusals. Nothing is imported from them, the payload markers are spelled out
here rather than copied from them, and every input is one the control built — an
absent check file, a check that genuinely exits 1, a receipt planted as failed, a
receipt that is not JSON.

**Ten UNPROVEN, each naming what it could not reach.** The pattern that decided
most of them: `_verify_hardpoint_join.py` and `_verify_hardpoint_alignment.py`
**import the very functions they judge**, so a wrong rule is applied identically
on both sides and cannot be caught by asking it. `_verify_child_markers.py`'s
BEFORE state is the same builder with a switch flipped. `_verify_g3_matcher_delta.py`
diffs the subject's own report against itself. `_verify_dim.mjs` proves the
stylesheet and the theme engine agree with EACH OTHER, which cannot catch both
being wrong together.

**Verified by running all 11.** Ten pass unchanged; the eleventh is
`_verify_deploy_drift.py`, red for the reason in part 1 and not because of its
label.

**Tranche 2** is the seven label and marker controls. Groundwork done:
`_verify_label_threshold.mjs` re-measures its threshold from the fleet each run
and shrinks the stage to make the answer move — that reads INDEPENDENT.
`_verify_marker_absence.mjs` judges the page's ABSENCE MESSAGE against the
generated marker and slot data, which the message logic did not produce.

Nothing committed since `2fc7008`. Nothing deployed. Live site untouched.

### 2026-08-27 22:11:48 — 20260827_2218_update_whats-next-measured-q7-is-the-only-one-left.md

# Update — Checked every DONE-WHEN on Code's queue by running it. Q1–Q6 are satisfied. Q7 is the only one left, and it is 86 files.

**2026-08-27 22:18 local · Code (background session)** — Sleven: *"whats next"*.

`NEXT.md` says to check the DONE-WHEN myself rather than assume the file is
current. So I did, one at a time, by running the thing that decides it.

## Q1 — ARMOUR NAMING — **DONE**

`_verify_armour_naming.mjs` is GREEN, and it is in the deploy's own gate list, so
it has run before every upload tonight.

## Q2 — A FAILED BUILD MUST NOT REACH A DEPLOY — **DONE**

Proven on BOTH scripts and now asserted on every run, `_verify_deploy_guards.py`
section 10: refuses a failed receipt, names the exit code, never reaches the dry
run, `-IgnoreFailedBuild` gets past it loudly, and an unreadable receipt is
refused. 83 passed, 0 failed.

## Q3 — SCALE THE 12 FROM `model_scaled.glb` — **DONE**

Both halves of the DONE-WHEN, measured:

    _verify_model_scale.mjs        GREEN - every imported ship is the size its
                                   own record says it is
    _verify_holo_placement.py      ALL 8 CHECKS PASSED
                                   (178 ships, 5,634 axis placements)

## Q4 — THE DISCLOSURE BAR ON THE OTHER THREE PAGES — **DONE**

`_verify_disclosure.mjs` exit 0, GREEN. The build shares `_disc.css` into
`index`, `keybinds`, `loadout` and `find` on every run.

## Q5 — THE ROADMAP WATCHER, PAST R0 — **DONE**

    _verify_roadmap_board.py   GREEN - board 1 is the live release view
    _verify_roadmap_watch.py   9 checks, 0 failed - the watcher refuses a board
                               that is not the release view

R1 is built, not just specified: `scripts/roadmap_watch.py:141 write_finding()`
writes `docs/FINDING_roadmap-change-<date>.md`, and `--dry-run` explicitly does
not. R2 and R3 are stances and are carried in the module's own docstring. The
state is real rather than empty: **board 1, 828 cards, with a fetch time**.

## Q6 — RUN THE COLLECTOR SELFTEST — **DONE**

`FINDING_the-collector-selftest-runs-and-4-10-is-on-this-machine`:
**575 checks, 0 failed, 0 void** — and the order's estimate of ~190 was low by a
factor of three. Written down, which was the deliverable.

## Q7 — LABEL EVERY CHECK THAT CANNOT MEET RULE 16 — **THE ONLY ONE LEFT**

    labelled            11  (6 INDEPENDENT, 5 UNPROVEN)
    unlabelled          86
    malformed label     0

    GREEN - every check either declares its rule 16 status or was already on the
    baseline. 86 gap(s) still on the list.

**The control passing is not the item being done.** It is a ratchet: the 86 sit
in `checks/rule16_baseline.txt` as recorded DEBT, the baseline can only shrink,
and Q7's DONE-WHEN is *"every check in `checks/` either draws its truth from a
real source or carries an UNPROVEN label naming what it could not reach"*.

### What the work actually is, per file

Read the check, decide honestly which of two things is true, and write one line
in the first few lines of the file:

    RULE16: INDEPENDENT - <where the truth comes from, and why the thing under
                          test could not have produced it>
    RULE16: UNPROVEN    - <what it could not reach>

**INDEPENDENT means EVERY assertion in the file draws on a source the code under
test did not produce.** If one assertion does not, the file is UNPROVEN. So this
is not a labelling pass — it is 86 honest re-readings, and the expected outcome
is that **the board looks worse before it looks better**, which `NEXT.md` already
says is the point.

It is also the one queue item with no dependency and no decision waiting on
anyone.

## Not on Code's queue, and not mine to start

- **`_verify_placer_candidates.py`** — the last of the sweep's 14. It diffs
  `place_fleet.py`'s output and **`place_fleet.py` is not in this repo.**
  Unowned rather than open.
- **`PROPOSAL_the-marker-pipeline-is-four-layers-deep...`** (21:00) — wants a
  decision from Sleven, not work from me.
- **Going live** — four commands, the first creates the worker, and Sleven has
  said not yet.

**Unless told otherwise I will start Q7**, in tranches, filing as I go rather
than in one lump at the end.

### 2026-08-27 22:04:09 — 20260827_2212_update_recycled-160-items-2-89-gb.md

# Update — Recycled. 160 of 160 items, 2.89 GB freed, 0 failures, and confirmed from the Recycle Bin's side.

**2026-08-27 22:12 local · Code (background session)** — Sleven: *"run it with
the corrected filter"*.

    recycled : 160 of 160 items
    failures : none
    _to_delete now: 31 items, 4.72 GB   (was 191 items, 7.61 GB)
    freed: 2.89 GB

Exactly the 160 / 2.89 GB reported at 22:02, to the item.

## The guard fired the way a guard should — by not firing

The script recomputed the selection immediately before touching anything and
was set to **throw without recycling a single item** if it did not still come to
160 / 2.89 GB. It matched, so it proceeded. Had a control written a new attic in
the four minutes between the report and the run, this would have stopped instead.

**The cutoff was not widened.** The one mis-sorted folder was held by name:

    20260827T030607Z_source1_git   still present   LastWriteTime 2026-08-26

That is the 1.31 GB same-day backup the order listed as HOLD and its own filter
would have binned.

## Confirmed from the OUTSIDE, because exit 0 is not proof

    recycle bin holds 160 top-level items

and the three largest are there by name — `20260801T204744Z_source1_git`
(1.55 GB), `collector_deadweight_20260809` (1.00 GB),
`starmap-routes-pyro-testrun-20260805` (0.27 GB). **Nothing was permanently
deleted; everything is one restore away and Sleven empties the bin.**

## And the three controls that read `_to_delete` still pass

The order claimed nothing reads it; I found three that do, and said the
conclusion held anyway. That was a prediction until now:

    _verify_model_scale.mjs      exit 0   GREEN - every imported ship is the
                                          size its own record says it is
    _verify_marker_positions.mjs exit 0   GREEN - the markers are on CIG's own
                                          coordinates
    _verify_takedown.py          exit 0   PASSED: 19 assertions

**Measured after the sweep, not argued before it.**

## What is left in the attic

31 items, 4.72 GB, every one of them dated today except the held backup — the
three `pre_scale_fix_*`, `pre_holo_regen`, `pre_overlay_regen`, both
`*_source1_git` snapshots, tonight's drift plants and probes, and
`child-marker-rebaseline-2026-08-27`.

Per the order, the 4.3 GB of git folders can go with the next sweep once 4.10
has settled. **They are the before-state of everything that landed today.**

Nothing committed since `2fc7008`; `_to_delete/` is gitignored, so nothing about
this touches the repository's contents.

### 2026-08-27 22:01:56 — 20260827_2206_update_running-the-recycle-with-the-corrected-filter.md

# Update — Sleven: *"run it with the corrected filter"*. Running it, and writing down the authority before I do.

**2026-08-27 22:06 local · Code (background session)**

## Why I am running a rule 1 action

Hard rule 1 says **"Sleven deletes it himself"**, and at 22:02 I reported rather
than ran, on exactly that basis.

**He has now told me to run it, in this session, in this message, for this
specific action, with the corrected filter I proposed.** That is the same
standard rule 2 sets for a commit — *"Sleven saying so, in that message, for that
change"* — and it is met. The rule exists so that Code does not decide what goes;
Sleven has decided.

## The guard I am adding on top of the order's

The order's own stop condition is a count and a size. Mine is stricter: the
script **recomputes the selection and refuses to touch anything** unless it
matches what I measured and reported at 22:02 —

    160 items, 2.89 GB, holding 20260827T030607Z_source1_git by name

If the disk has moved since (a control writing a new attic, C1 moving something
aside), the numbers change and it stops without recycling a single item. **The
cutoff is not widened and is not a parameter.**

## Rule 4, and why there is no backup step

*"Take a verified backup before anything destructive or irreversible."* This is
neither. Every item goes to the Recycle Bin, `NukeOnDelete = 0` on every volume,
bin capacity 13–192 GB against a largest item of 1.55 GB, 495 GB free — all
measured at 22:00. **The Recycle Bin IS the backup**, and backing up the attic
would be backing up a backup.

## Rule 5, and the list

Bulk work gets a report-only pass first, and it had one — the 22:02 note carried
the count and the size and Sleven has seen it. The run below prints **every item
by name, size and date before it touches anything**, so the record of what went
is itemised rather than a total.

### 2026-08-27 21:59:34 — 20260827_2202_update_the-recycle-order-stops-on-its-own-condition.md

# Update — Verified the recycle order. It fails its OWN stop condition, and the command would bin a backup the order says to hold.

**2026-08-27 22:02 local · Code (background session)** — follow-on to 21:58.
**Nothing has been moved, recycled or deleted.**

`docs/FINDING_the-recycle-order-would-bin-a-backup-it-said-to-hold-2026-08-27.md`

## The measurement

    ORDER says                       MEASURED
    SEND   157 items   3.10 GB       161 items   4.20 GB
    HOLD    32 items   5.07 GB        30 items   3.41 GB

The order says: *"If it does not move roughly 157 items and ~3.1 GB, stop and
say so rather than re-running it with a wider date."* **It does not. Stopping.**

## The gigabyte has a name

    20260827T030607Z_source1_git   1.31 GB   LastWriteTime 2026-08-26

**The order HOLDS that folder** — it is one of the five same-day backups, listed
at 1.40 GB as "dated TODAY". Its LastWriteTime is yesterday. The order judged it
by the run id in its NAME; the command filters on `LastWriteTime`. Where those
disagree the command wins, silently, and it bins a same-day backup — the one
trade the order itself says this project should never make.

**The split is sound. The filter does not implement it.**

## A correction to the order, conclusion unchanged

*"Nothing in the repo READS from `_to_delete`"* is not so — `_verify_model_scale.mjs`,
`_verify_marker_positions.mjs` and `_verify_takedown.py` all read it. **All three
are safe under this sweep** and I checked each rather than assuming: their inputs
are either dated today and held, or scratch directories the controls recreate.

Worth correcting anyway, because "nothing reads it" is a premise that gets reused
next month against a different cutoff.

## And one worry I can retire

A too-large item would be permanently deleted rather than binned, with
`OnlyErrorDialogs` hiding the prompt. Checked: `NukeOnDelete = 0` on every
volume, bin capacity 13–192 GB, 495 GB free, largest item 1.55 GB. **No
silent-permanent-delete risk.**

## Rule 1

I am not running it. *"Sleven deletes it himself."* The order uses the VisualBasic
Recycle Bin API rather than `Remove-Item`, which is not on rule 1's list by
name — and the rule's answer to that is *"if you are ever unsure, it is."* The
go-ahead quoted in the order is also Sleven speaking to C1, not here.

The finding carries the corrected command, holding the one mis-sorted folder by
name: **160 items / 2.89 GB**, every same-day backup untouched. Sleven runs it.

## Also unactioned, and neither needs me tonight

- `PROPOSAL_the-marker-pipeline-is-four-layers-deep...` (21:00) — a proposal,
  wants a decision rather than work.
- `FINDING_the-economy-data-we-never-opened...` (21:50) — C1's, informational.

### 2026-08-27 21:56:40 — 20260827_2158_update_the-recycle-bin-order-is-rule-1.md

# Update — `ORDER-send-the-old-attic-to-the-recycle-bin` is outstanding, and it is the one kind of order I do not execute. Verifying it instead.

**2026-08-27 21:58 local · Code (background session)** — checked the updates.
Inbox empty, no new C1 handoff notes since 20:47, but three C1 documents are
unactioned and one of them is an ORDER.

## The order

`ORDER-send-the-old-attic-to-the-recycle-bin-2026-08-27.md` (21:18) asks me to
send **157 items / 3.10 GB** of `_to_delete/` to the Recycle Bin, holding back
32 items / 5.07 GB dated today.

**HARD RULE 1: "Sleven deletes it himself."** The rule names `rm`, `del`,
`Remove-Item`, `rmdir` and `shutil.rmtree`; the order uses
`[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(...,'SendToRecycleBin')`,
which is not on that list by name. The rule also says: *"If you are ever unsure
whether an action falls under one of these, it does. Ask. Do not guess."*

I am not unsure, as it happens - removing 3.1 GB from the repo directory is the
thing rule 1 exists to stop, whatever the API is called. And the quote in the
order is **Sleven speaking to C1**, not to me in this session.

## So I am doing the half that IS mine

Sleven's actual words in the order are *"verify that it's just old stuff we
don't need anymore"*. That verification is exactly my job and does not touch a
byte:

  1. re-measure C1's split independently - counts and sizes, either side of the
     cutoff
  2. re-check the claim that nothing in the repo READS from `_to_delete`
  3. check one thing the order does not mention, which I think matters

Findings next. Nothing has been moved, recycled or deleted.

### 2026-08-27 21:55:10 — 20260827_2210_update_pushed.md

# Update — Pushed. `575d38b..2fc7008` on `origin/main`, verified from the remote's side.

**2026-08-27 22:10 local · Code (background session)** — Sleven: *"push it"*.

    git push origin main
    To https://github.com/Smeezee/citizen-compass.git
       575d38b..2fc7008  main -> main

## Verified against the remote, not against the push output

A push that printed a ref update is not the same as a remote that has it, so I
fetched and compared:

    local  HEAD         2fc7008131fbc7b58ecceeddec87149d3432e5d9
    origin/main         2fc7008131fbc7b58ecceeddec87149d3432e5d9
    ahead / behind      0 / 0

Fast-forward, no force, nothing rewritten. `main` was 1 ahead and 0 behind
before the push, so there was nothing on the remote to rebase onto or clobber.

## What is now public

**The repository is public** - `github.com/Smeezee/citizen-compass` - so those
395 files are readable by anyone from this moment. Said plainly rather than
assumed: it is the same repo the download page already links to, and the staged
set was checked for `.env`, secrets, tokens, credentials, `.glb` and `.p4k`
before the commit, all of which are gitignored or absent.

**This is the CODE going public, not the SITE.** The live worker still returns
404 and `deploy_live.ps1` has still never been run for real.

## Working tree after

Four entries, all of them the watcher doing its job on the note above:

    M  LATEST_HANDOFF.md
    M  docs/handoff_archive/.handoff_update_counter
    M  docs/handoff_archive/_updates_log.md
    ?? docs/handoff_archive/20260827_215215_..._committed-tonights-work.md

That is the handoff pipeline recording the commit, which by definition lands
after it. Nothing from tonight's work is unpushed.

## Still open, unchanged by this

- `_verify_placer_candidates.py` - `place_fleet.py` is not in this repo.
- Going live. Four commands, the first creates the worker, and they are Sleven's.

### 2026-08-27 21:52:15 — 20260827_2205_update_committed-tonights-work.md

# Update — Committed. `2fc7008`, 395 files. Not pushed.

**2026-08-27 22:05 local · Code (background session)** — Sleven: *"not yet,
commit everything from tonight"*.

    2fc7008  Thirteen of the sweep's fourteen close, and the live deploy stops
             being the unguarded one

    395 files changed, 341,378 insertions(+), 18,624 deletions(-)
    working tree after: clean

**Committed, NOT pushed.** He said commit. The live site is untouched and its
worker still 404s.

## What went in

Everything from tonight, both sides of it:

    data-layer/   328   C1's placement, transforms and client overlay - the
                        ground vehicles, the blind-folder hulls, the origin fix
    docs/          40   the findings, the orders, the whole handoff archive
    checks/        16   ten controls closed, plus the shared loadout harness
    testing/        3   build_deploy.py, loadout.src.html, the marker table
    scripts/        1   deploy_live.ps1 - both gates
    root            5   the three hardpoint builders and C1's two probes

## Checked before staging, not after

    .env                      gitignored
    data-layer/external-sources/  gitignored
    _to_delete/               gitignored
    testing/_deploy/          gitignored
    staged files matching env/secret/token/credential/.glb/.p4k:  none

## Two judgement calls, named rather than buried

**C1's `probe_join_by_hardpoint_names.py` and `probe_vehicle_entity_records.py`
are in.** They are throwaway probes at the repo root and I would normally leave
them out - but "everything from tonight" is explicit, and dropping files is the
riskier deviation. Say if you want them out; they come out cleanly.

**The old marker baseline is committed as a DELETE.** It was moved to
`_to_delete/child-marker-rebaseline-2026-08-27/` under rule 1, not deleted, and
`loadout_marker.pre-C1-20260827.js` replaces it in the same commit.

## One order I had not read until now, and it is already done

`ORDER-build-again-a-real-defect-was-in-the-markers-2026-08-27.md` (21:12) - C1
found markers sitting at the dead hull origin, which is CIG's never-set identity
value rather than a gun at the centre of the ship, and withheld 27 overlay ports
plus 318 record ports. That is the **1,720 -> 1,693** I recorded at 21:43 as
"a number that moved and is not mine".

**The build that carries it is already deployed** - version
`bbd2a7d7-7979-4980-8984-7f1e9dec042c`, built at 21:32, reporting exactly
`1693 port(s) moved onto CIG positions`. Nothing further to run for it.

Worth repeating C1's own note on it, because it is the same lesson twice in one
night: its first attempt tested the raw `pos` for exact zero and eleven ports
still came out at the origin, because `unit` is `pos / H0` rounded to five
decimals. **Testing the input to a rounding step tells you nothing about its
output** - the same shape as a gate that never ran and a flag that never applied.

## Still open

- `_verify_placer_candidates.py` - belongs to `place_fleet.py`, which is not in
  this repo.
- Going live. Four commands, and the first one creates the worker. Sleven's.

Nothing pushed.

### 2026-08-27 21:46:02 — 20260827_2159_update_the-live-dry-run-and-a-clean-round-trip.md

# Update — The live dry run, in full. All gates green, nothing published, and the testing payload came back byte for byte.

**2026-08-27 21:59 local · Code (background session)** — Sleven chose the dry
run. Testing version `bbd2a7d7-7979-4980-8984-7f1e9dec042c`.

## What the live script says with a real LIVE payload in front of it

    === LIVE SITE DEPLOY ===
    build   : last build ok (2026-08-27T21:43:00)
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    version : v0.4.0   (from the payload itself, not from a note)
    payload : LIVE - no password gate, no testing stamp
    guard   : _deploy contains only known assets
    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN
    check   : _verify_armour_naming.mjs ... GREEN
    checks  : all browser checks green
    payload : 524 files, 456.7 MB
    models  : 258 .glb files
    largest : Tyilui.glb (17.19 MB)
    auth    : scoped token loaded from .env (length 53, not shown)

    -WhatIf: WOULD PUBLISH THE LIVE SITE.
    -WhatIf:   worker    citizencompass
    -WhatIf:   payload   524 files, 456.7 MB, 258 models
    Nothing was uploaded.

**Both gates I added an hour ago ran on the live path for the first time, on the
real payload, and both passed** - the receipt read and accepted, four browser
checks driven against the very bytes that would have gone out. Two hours ago
this script ran neither.

## Confirmed from the OUTSIDE, which is what the script itself insists on

    https://citizencompass.citizencompass-contact.workers.dev/   ->  HTTP 404

**The worker still does not exist. Nothing was published.** The public site is
exactly as it was.

## The round trip, measured rather than assumed

`--live` rewrites the same directory the testing site publishes, so the risk was
never the dry run - it was leaving the public build sitting in `testing/_deploy`.
I hashed every non-model file before starting and compared after the rebuild:

    files before 266 | now 266 | identical 266
    DIFFERENT: none - the testing payload is byte-for-byte what it was

Redeployed testing to prove the path still works after the round trip:
**"No updated asset files to upload"** - exactly right, because the payload never
actually changed. The served page carries its password gate, and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

## What this told us that the control could not

`_verify_deploy_guards.py` proves the gates refuse bad input against throwaway
trees. **This is the first time the live script has been driven end to end
against the real 456 MB payload**, and the useful new fact is that it gets all
the way through - the guard, four real browser checks, the file and size
ceilings, the credential load - and stops exactly where it is supposed to.

**The version it reports, `v0.4.0`, it read out of the payload itself.** Worth
saying because a version taken from a note is the kind of thing that is right
until the day it is not.

## Where it leaves going live

One command away, and that command is Sleven's:

    python testing\_src\build_deploy.py --live
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1
    python testing\_src\build_deploy.py          <- put testing back
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

**The first real run CREATES the worker** rather than updating one, since the
name 404s today. That remains his to do, and nothing about tonight changes it.

Probe files moved to `_to_delete/probes-2026-08-27/`, never deleted. Nothing
committed, nothing pushed, live site untouched.

### 2026-08-27 21:42:52 — 20260827_2156_update_dry-run-only-doing-it-now.md

# Update — Sleven chose the dry run. Doing it, and recording what has to come back afterwards.

**2026-08-27 21:56 local · Code (background session)**

    python testing/_src/build_deploy.py --live
    deploy_live.ps1 -WhatIf
    python testing/_src/build_deploy.py
    deploy_testing.ps1

**PUBLIC SITE: untouched. The worker stays 404.**

The step that needs proving is the last two: `--live` rewrites the same
directory the testing site publishes, so the testing payload has to come back
**byte for byte**, not approximately. Hashing every non-model file in
`testing/_deploy` before I start so the restore is a measurement rather than an
assumption.

### 2026-08-27 21:41:00 — 20260827_2154_update_the-live-deploy-refuses-and-the-worker-does-not-exist.md

# Update — I ran it. It refused, correctly, and the live worker returns 404. Stopping to ask before the two steps that would change that.

**2026-08-27 21:54 local · Code (background session)** — Sleven: *"well run it"*.

## I ran it. Here is what it said

    powershell -File .\scripts\deploy_live.ps1 -WhatIf

    === LIVE SITE DEPLOY ===
    build   : last build ok (2026-08-27T21:32:11)
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    LIVE DEPLOY ABORTED: THIS PAYLOAD CARRIES THE PRIVATE-PREVIEW PASSWORD GATE.

**The gate I added an hour ago is working**: `build : last build ok` is the new
receipt gate reading the receipt and passing it. What stopped the run is the
payload-identity refusal that has been there since 2026-08-21.

**Nothing was published. The dry run never reached the point of trying.**

## Two facts that stand between here and a live site

**1. `testing/_deploy` is the TESTING payload.** It carries the private-preview
password gate and the `testing 2026-08-28` stamp. Publishing it would lock every
visitor out behind a password they were never given, which from outside reads as
an outage rather than a mistake. The script says so and refuses.

To publish I would first have to run:

    python testing\_src\build_deploy.py --live

That **strips the password gate and the testing stamp**, and it rewrites the
same directory the testing site publishes. Until it is rebuilt without `--live`,
`deploy_testing.ps1` will refuse - deliberately, each script refuses the other's
payload. So it is not one command, it is: build live, publish, rebuild testing,
redeploy testing.

**2. The live worker does not exist.**

    https://citizencompass.citizencompass-contact.workers.dev/   ->  HTTP 404

`deploy_live.ps1`'s own header says only Sleven creates it. A `wrangler deploy`
against a name that does not exist would **create the public site**, which is
the one thing that file reserves to him by name.

## So I have stopped, and this is why rather than an excuse

*"Run it"* cannot execute as given: the script refuses, correctly. Getting past
that needs a step Sleven did not name (`--live`), which disables the testing
deploy until reverted, and a `wrangler deploy` that would **create** the public
site rather than update it.

**This is the only action in this repo that cannot be taken back**, and Sleven's
recorded position at 14:10 today was that the site is not ready. He may well
have changed his mind - that is entirely his to change - but I am not going to
infer it from three words when the cost of being wrong is a public site nobody
meant to publish.

Asking now, with the exact sequence written out, rather than after.

Nothing built, nothing published, nothing committed, live site untouched.

### 2026-08-27 21:39:55 — 20260827_2152_update_asked-to-run-the-live-deploy.md

# Update — Asked to run `deploy_live.ps1` for real. Gathering the facts before touching anything.

**2026-08-27 21:52 local · Code (background session)** — Sleven: *"well run it"*,
straight after I said the script has never been run for real.

This is the one action in this repo that cannot be taken back, so I am writing
down what I check before I do anything, not after.

**Nothing has been published. Nothing has been built. This note is the pause.**

### 2026-08-27 21:38:42 — 20260827_2148_update_the-live-deploy-script-has-both-gates.md

# Update — `deploy_live.ps1` has both gates, and the control that proves them went in with them. 56 -> 83 assertions.

**2026-08-27 21:48 local · Code (background session)** — Sleven: *"add the gates
to deploy_live.ps1"*. The finding from 20:34 is closed.

## What went in

**1. The build receipt gate**, checked first, before the payload identity checks
and long before the browser checks, so a refusal is immediate rather than four
minutes in:

    missing     no build to judge. Allowed, and SAID so rather than assumed.
    ok          the build reached its last statement.
    anything    refused, naming the status and the exit code.
    unreadable  refused. An unreadable receipt is not a passing one.

Override: `-IgnoreFailedBuild`, which prints a banner saying it is publishing to
the PUBLIC SITE from a build that did not succeed.

**2. The browser-check gate**, the same four checks on the same bytes - both
scripts publish `testing\_deploy`, so a check that passed before Sleven reviewed
the testing site is a check against the very payload going public. A missing
check FILE is refused as NOT CHECKED. Override: `-IgnoreRedCheck '<name>'`,
which names one check rather than waving the gate through.

**Both escape hatches came across, and so did the reason they are not `-Force`.**
A gate with no documented way past it gets bypassed by editing the script, and
then the bypass is invisible.

**And the `-File` normalisation came with them.** Under `powershell -File`,
`-IgnoreRedCheck 'a.mjs','b.mjs'` arrives as the single string `"a.mjs,b.mjs"`
and a `-contains` test is false for both names. That defect was found in the
testing script by RUNNING the three paths; it is not repeated here.

## The control went in at the same time, which was the whole point

Section 9 (**the live gates**) and section 10 (**the receipt, on BOTH scripts**).
**56 -> 83 assertions, 0 failed**, `--self-test` still exits 1.

    9.  deploy_live.ps1 REFUSES a missing browser check FILE / names it /
        never said it would publish
        REFUSES a RED check / names it / quotes the LIVE override / never
        said it would publish
        -IgnoreRedCheck publishes past it / says OVERRIDE and PUBLIC SITE /
        reaches the dry run
        but a DIFFERENT check name does not wave the red one through

    10. BOTH scripts REFUSE a failed build / name the exit code / never reach
        the dry run / -IgnoreFailedBuild gets past it, loudly / then reaches it
        BOTH scripts REFUSE an UNREADABLE receipt

**Section 10 covers the testing script too.** Q2's DONE-WHEN was satisfied there
this evening but only ever proven by me typing it at a prompt. It is now
asserted on every run, on both sides.

## Proven by behaviour, including against the gate's own absence

Every assertion drives the REAL script with `-WhatIf` against throwaway trees -
a genuinely absent check file, a check that genuinely exits 1, a planted failed
receipt, a receipt that is not JSON.

And the load-bearing one, because "it refused" is not the same as "the gate is
what refused". I copied the live script with the browser-check block cut out and
ran the same RED-check fixture through both:

    WITHOUT the gate: exit=0   reached the dry run=True
    WITH    the gate: exit=1   reached the dry run=False

**Without it, a red check publishes to the public site and reports success.**
That is the defect the finding described, measured rather than argued - and it
means section 9 would catch the gate being removed again. The probe copy went to
`_to_delete/probes-2026-08-27/`, never deleted.

## One more thing, in the file's own header

The header claimed this script was a mirror of the testing one, *"and every one
of those differences is a refusal"*. That sentence was untrue for a day. It now
lists both gates - **and says the gap existed**, rather than tidying it away:

> THE LAST TWO IN THAT LIST ARRIVED LATE ... for a day the rehearsal ran four
> browser checks and read the build receipt while the performance did neither.

## What I did NOT do

**`deploy_live.ps1` has still never been run for real, and I did not run it.**
Everything above is `-WhatIf` against temp directories with an obviously fake
token. The live worker was never contacted. Only Sleven publishes the public
site.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:34:29 — 20260827_2140_update_adding-the-gates-to-deploy-live.md

# Update — Sleven: *"add the gates to deploy_live.ps1"*. Starting, with the constraint that matters written down first.

**2026-08-27 21:40 local · Code (background session)** — the go-ahead I asked for
at 22:55 in `docs/FINDING_the-live-deploy-script-has-neither-gate-...`.

## What I am adding

Both blocks, lifted from `deploy_testing.ps1` with their escape hatches:

1. **The build receipt gate** plus `-IgnoreFailedBuild`. Refuses when the last
   build did not succeed, and names the status and the exit code.
2. **The browser-check gate** plus `-IgnoreRedCheck '<name>'`. Refuses a RED
   check and refuses a MISSING check file, and the override names one check
   rather than waving the gate through.

**Every escape hatch comes across with them.** A gate with no documented way past
it gets bypassed by editing the script, and then the bypass is invisible.

## And the control comes with them, in the same sitting

`_verify_deploy_guards.py` asserts these behaviours for the testing script only.
**Adding the gates without extending the control would give the live script a
guard nobody has ever seen fail** - rule 12's untested gate wearing a reassuring
name, which is the exact defect I wrote the finding about. Section 8 gets the
live script alongside the testing one, driven with a missing check, a red check
and a failed receipt.

## What I will NOT do

**I will not run `deploy_live.ps1` for real.** Its own header says it never has
been, the worker may not exist, and only Sleven publishes the public site.
Everything below is `-WhatIf` against throwaway project trees in a temp
directory - nothing uploaded, nothing in the repo touched, an obviously fake
token in the fixture's `.env`.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:33:36 — 20260827_2135_update_child-markers-rebaselined-and-suppression-made-final.md

# Update — `_verify_child_markers.py` is green: 16 assertions, 0 failed. And it caught my own suppression within the hour.

**2026-08-27 21:35 local · Code (background session)** — Sleven: *"the retaliator
quad is right, re-baseline it"*. Version `bca57a21-70c0-4354-99a4-fcc624941b53`.

## Done, and here is exactly what moved

**The pin.** The old four are kept in the file next to the new four, because a
pin nobody can audit is not a pin:

    was  23 [-0.03755, -0.02334, -0.95564]   now  23 [-0.15708, -0.06014, 0.55639]
         24 [ 0.053,   -0.00648, -0.97809]        24 [-0.17993, -0.06014, 0.55639]
         39 [ 0.01037, -0.0012,  -0.98118]        39 [ 0.15711, -0.06014, 0.55639]
         40 [-0.00836,  0.01415, -0.96836]        40 [ 0.1799,  -0.06014, 0.55639]

The comment records that **the symmetry is evidence, not proof, and is not what
authorised this** - Sleven's word is, quoted in the file.

**The baseline.** `loadout_marker.pre-C1-20260827.js`, taken by re-running the
real build with `CC_NO_INHERIT=1`. The old `pre-C1-20260826` snapshot went to
`_to_delete/child-marker-rebaseline-2026-08-27/`, not overwritten.

**The dangerous step, and how it was checked.** `CC_NO_INHERIT=1` runs the REAL
build, so it overwrote the shipped marker file with the 2,139-marker BEFORE
state. I copied the shipped file aside first and confirmed the normal rebuild
restored it **byte for byte**:

    57e30d97f4c0b45f3ead22028583648edf52b7aecb4b3a70663de3c8178ebb8b   before
    57e30d97f4c0b45f3ead22028583648edf52b7aecb4b3a70663de3c8178ebb8b   after

Derived-data mtimes were read either side. C1 did not write during it, so the
BEFORE and AFTER differ by the inheritance pass and nothing else - which is the
whole point of the snapshot.

## THE CONTROL CAUGHT MY OWN CHANGE, AND IT WAS RIGHT

First run after re-baselining, two failures left:

    no hull changed without having a nested eligible port to inherit from
      got ['C.O. HoverQuad', 'Mirai Pulse LX']

**That is the marker suppression I shipped an hour ago.** I dropped the upper
port of each coincident pair and let the inheritance pass put it back, nudged
0.006 aside - and I said so in the 21:38 note and offered to change it.

The control's objection is the better argument, and it is two arguments:

- **A re-placed TOP-LEVEL port is not an inherited child.** The inheritance pass
  is for a gun inside a turret taking its turret's position. Using it to
  re-place a port that had its own position is a different mechanism wearing the
  same counter.
- **The nudged dot claims a position CIG does not give.** It says "this port is
  six centimetres that way" when two independent sources say the two mounts are
  in one place. Every other marker on that page is CIG's own coordinate or an
  honestly-derived child of one.

**So the suppression is now final: the upper PortId gets no marker at all.** Same
answer this build already gives for an ambiguous name, and the list still
reaches every port.

    hull markers  6412 -> 6400 on 271 hulls      (exactly the 12)
    inherited     4273 -> 4261
    Drake Buccaneer on the served page: 9 dots -> 8

**Sleven: this is the change I said would be one line if you preferred it. I
made it because the control disagreed with the other reading, not because you
asked - say if you would rather have the nudged dot back.**

## Proven it can still fail - all four, on demand

    --mutate-drop-children   exit 1   the Retaliator gained markers: FAIL
    --mutate-stack           exit 1   two markers share a position: FAIL
    --mutate-move-pinned     exit 1   PortId 23 got [-0.15707,...] want [-0.15708,...]
    --self-test              exit 1

`--mutate-move-pinned` is the one that matters here: it nudges by 0.00001 and is
caught **against the NEW pin**, so the re-baselined values are genuinely what is
being defended and not a comment.

## Re-verified after the change

    _verify_deploy_drift.py     12 passed, 0 failed
    _verify_marker_absence.mjs  ok      _verify_marker_coverage.mjs  ok
    _verify_marker_response.mjs ok      _verify_stage_panel.mjs      ok
    _verify_ship_page.mjs       ok

Deployed to testing, 4 browser checks GREEN, deploy guard clean, 1 file uploaded.

## THE SWEEP'S 14 IS NOW 13 CLOSED

The only one left is `_verify_placer_candidates.py`, which C1 says belongs to
`place_fleet.py`'s own output rather than to the overlay - **and place_fleet.py
is not in this repo**, so I cannot close it and will not claim to.

Still outstanding and not mine to decide: `deploy_live.ps1` has neither the
build-receipt gate nor the browser-check gate
(`docs/FINDING_the-live-deploy-script-has-neither-gate-...`).

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:28:16 — 20260827_2131_update_rebaselining-child-markers.md

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

### 2026-08-27 21:20:36 — 20260827_2121_update_all-six-closed-harness-proven-inert-deployed.md

# Update — All six closed. The harness change is measured inert across 19 controls, and it is deployed.

**2026-08-27 21:21 local · Code (background session)** — closing out
*"suppress the duplicates, then run the remaining six"*.
Version `6c31ef0c-bf32-48e9-acb3-0bffcb294245`.

## The harness change, measured rather than argued

I said the deferred-timer change was designed to be inert unless a control calls
`flushTimers()`. **Designed to be is not measured to be**, so I ran every control
that imports `checks/_loadout_harness.mjs`:

    19 ok, 0 failed, 1 skipped (_verify_picker_deployed.mjs - network, opt-in)

    column_split · damage_readout · flight_blades · inline_picker ·
    label_cold_start · label_threshold · label_tracking · labels · look_panel ·
    marker_absence · marker_coverage · marker_response · palette ·
    panel_findable · part_rows · ship_page · sorts · spin_default · stage_panel

## Built and deployed

    gate passed: _verify_holo_placement.py (checks) and (self-proof)
    inline JS parses: _layer.src.html (13 blocks), keybinds.src.html (4 blocks)
    12 marker(s) gave up a position shared with a lower PortId
    disclosure CSS: ... index.html, keybinds.html, loadout.html, find.html
    deploy guard: safe to deploy

4 browser checks GREEN, **2 files uploaded** - `loadout.html` this time as well
as the markers, which is the theme tokens and the `setSel` refactor reaching the
page. Served check: Drake Buccaneer 9 dots, 9 visible, model loaded.
`_verify_deployed_links.mjs` SWEEP CLEAN with its canary.

## One number moved that is not mine

    client hardpoint overlay: 1720 -> 1693 port(s) moved onto CIG positions
    matched no weapon port:   3927 -> 3609

**C1 rewrote the client overlay at 21:10:48**, between my last deploy and this
build. Fewer ports are moved by the overlay and far more of them now match a
weapon port, which reads as the overlay getting more selective rather than
smaller. Recorded because a number changing under a deploy should never be
found later in a diff - it is C1's change, not the suppression's. Hull markers
are unchanged at **6,412 on 271 hulls**.

## THE SWEEP'S 14, FINAL

    _verify_deploy_guards.py        40/3  -> 56/0     me
    _verify_deploy_drift.py         11/1  -> 12/0     me
    _verify_hardpoint_alignment.py  FAIL  -> exit 0   me - and 4b ran for the first time ever
    _verify_hardpoint_join.py       FAIL  -> exit 0   me
    _verify_broken_checker_e2e.py   11/1  -> 10/0     me - and two vacuous passes closed
    _verify_model_resolution.py     22/1  -> 23/0     me
    _verify_g3_matcher_delta.py      8/1  -> 10/0     me
    _verify_dim.mjs                 42/1  -> 43/0     me
    _verify_ship_page.mjs          241/1  -> 242/0    me
    _verify_stage_panel.mjs         51/1  -> 54/0     me
    _verify_rule16_labels.py        closed by C1
    _verify_ship_gaps.py            closed by C1
    _verify_placer_candidates.py    C1: P1's output, not the overlay - unclaimed
    _verify_child_markers.py        BLOCKED, below

**Twelve of fourteen closed. Not one was a regression in shipped behaviour** -
they were stale expectations, a fixture that predated a gate, an env var nobody
set, a harness that discarded deferred work, and two genuine page defects the
controls were right about (two theme tokens that never dimmed, three places
building one selection object).

## Still blocked, and it is the same blocker

`_verify_child_markers.py`. The coincident-marker half is closed - **section 3
is green, 0 markers on top of another.** What remains is the baseline: nobody
has said the Retaliator's new mirrored quad is RIGHT rather than tidier, and
re-taking the snapshot now bakes those four in. **One word and it is done in
the same sitting.**

## Also outstanding, from earlier

`docs/FINDING_the-live-deploy-script-has-neither-gate-...` - `deploy_live.ps1`
still has neither the build-receipt gate nor the browser-check gate. Waiting on
a go-ahead, not on me.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:18:14 — 20260827_2126_update_the-three-browser-controls-and-a-harness-that-ate-deferred-work.md

# Update — The last three of the six are green, and one of them was the harness lying to every control that uses it.

**2026-08-27 21:26 local · Code (background session)** — the browser half of
*"run the remaining six"*.

## `_verify_dim.mjs` — 42/1 -> 43/43, exit 0

    FAILED: and neither side declares a token the other does not  css 58 vs engine 56

Named the two, rather than accepting a count:

    in CSS, NOT in palette():  ['bracket', 'panelglass']
    in palette(), NOT in CSS:  []

**A token the theme engine does not know about is never re-emitted, so it keeps
its Day value at every preset.** `--panelglass` is the stage panel's ground and
`--bracket` is its corner brackets - **the two things sitting directly over the
render, which is the exact place the dim exists for.** They stayed at full
brightness in Blackout.

Both are the SCRIMS shape and were simply never registered when they were added.
Their literals gave the base and the alpha, read rather than chosen:

    --bracket     rgba( 34,211,238,0.30)  = accent2 (#22D3EE) at 0.30
    --panelglass  rgba( 14, 27, 46,0.80)  = panel   (#0E1B2E) at 0.80

The CSS literals also carried a trailing zero the engine does not emit
(`0.30` vs `0.3`), so the value assertion caught them a second time. Written to
match.

**The control still fails on demand:** `--mutate-nofloor` exits 1 with the body
text sitting ON the floor at Blackout.

## `_verify_ship_page.mjs` — 241/1 -> 242/242, exit 0

    FAILED: there is exactly ONE place in the page that selects a port
            3 assignments to sel={...}

**The control was right and the page was wrong.** Three sites built the
selection object: `selectPort()`, `undoSwap()` and the ledger's revert handler.
Its stated reason holds - *"the marker and the list open the IDENTICAL window"*
is only true BY CONSTRUCTION while one place decides what a selection is.

And the two extras built it **without the `fixed` key**, so a port selected by
undo or revert carried a different shape from the same port selected by a click.
Both are guarded to swappable ports today, which is why nothing had gone
visibly wrong yet.

Added `setSel(slot)` as the one place the object is built. `selectPort` still
owns what opens and the `editing` decision; undo and revert now get the flag
**without gaining a render they did not ask for** - both their callers already
render. The behavioural counts are unchanged: still *"2 geometry loads across
two ships, three showModel() calls and three tab switches"*.

## `_verify_stage_panel.mjs` — 51/1 -> 54/54, exit 0. And this is the one worth reading

    FAILED: and it closes the panel

The page was not broken. **`checks/_loadout_harness.mjs` had
`setTimeout: () => 0`.** Every callback the page deferred was thrown away, and
nothing said so.

P1e clears the selection during the click and calls `setTimeout(renderAll, 0)`
deliberately - rendering inline would rebuild the DOM underneath the branches
that have not run yet. So in this harness the panel never closed, and the
control has been reporting a page defect that does not exist **for as long as
P1e has existed**.

**Twenty controls import that harness.** Any behaviour the page defers was
invisible to all of them - and the dangerous direction is not this one, it is an
assertion that some deferred cleanup did NOT happen passing because it never
could have.

Deferred callbacks are now QUEUED and `flushTimers()` runs them. **Not
auto-flushed**: running them inline would change the ordering every existing
control was written against, and a control that wants a deferred effect should
have to say so.

The assertion was also split, so it says which half failed:

    the click clears the selection during the event, before any render   (synchronous)
    and it DEFERRED a render rather than doing nothing   1 deferred callback(s) ran
    and it closes the panel

**A flush that runs nothing is now a failure**, so this cannot go green on a
page that has stopped deferring anything.

## Re-running all 20 harness users before I call this done

The harness change is designed to be inert unless `flushTimers()` is called, but
"designed to be" is not "measured to be". Result in the next note, then a build
and deploy - `loadout.src.html` changed, so the page has to reach testing.

Nothing committed, nothing pushed, live site untouched.

*(+534 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

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

