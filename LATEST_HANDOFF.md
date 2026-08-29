# LATEST_HANDOFF.md — Update #832 — 2026-08-29 10:24 AM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-29 10:24:07 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119498 files (13787.21 MB)

**Scripts:** 53  |  **3D models:** 1133  |  **Docs:** 1383

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-29 10:23:25 — 20260829_1055_update_i-was-wrong-about-q21-the-withholding-did-arrive-and-the-deploy-is-gated.md

# Update — I was wrong an hour ago: the withholding DID reach the marker file. Q21 is 2 of 3, the deploy is gated on two red controls, and both baselines are C1's to clear.

**2026-08-29 10:55 local · Code (background session)**

## THE CORRECTION, FIRST

At 10:45 I filed that the fore/aft withholding *"cannot reach `loadout_marker.gen.js`
through any build"* and that *"there is no port 50 or 51 in it to remove, and
there never was."*

**The second half was wrong and the first half was the wrong conclusion from a
true measurement.**

    BANU_Defender  port 50   GONE
    BANU_Defender  port 51   GONE
    MISC_Hull_C    port 2    PRESENT

**Ports 50 and 51 were removed — at C1's 09:19 regeneration, which is before the
09:47 baseline I measured from.** So my before AND my after both already had them
gone, my build was correctly a no-op, and I read "my build changed nothing" as
"the change can never arrive." Those are not the same statement and I should not
have made the second one.

**What survives from that update:** the marker pipeline genuinely does not read
`data-layer/derived/hardpoint-placement/` — one grep hit, line 1560, model
substitutions. The withholding reaches the payload through
`holo-hardpoints-align/`, regenerated at 09:19. Both facts are true; I joined
them into a false conclusion.

## SO Q21 IS 2 OF 3, NOT 0 OF 3 AND NOT DONE

`MISC_Hull_C` port 2 is still in the payload. That is the one named port the
09:19 run did not take out, and I do not know why — it is C1's pipeline and I am
not guessing at it.

## THE SWEEP, AND IT IS THE FIRST CLEAN MEASUREMENT

    104 ok, 2 failed, 0 skipped, 0 NOT RUN, in 677s

**This is the first sweep in this repo that could not be perturbed by its own
drift control.** Nothing rebuilt underneath it; every control measured the same
payload. That is what this morning's work was for.

## THE TWO REDS ARE THE WITHHOLDING ITSELF, ARRIVING AT BASELINES THAT PREDATE IT

    _verify_child_markers.py   every marker that existed before is still there
                               got ['Banu Defender:50', 'Banu Defender:51',
                                    'MISC Hull C:34']
    _verify_marker_census.py   REFUSED - BANU_Defender 10 -> 8

**Neither is a defect. Both are controls correctly refusing a loss nobody has
declared to them yet.** That is exactly what they are for, and I am not going to
make them quiet.

## AND I AM NOT CLEARING EITHER, BECAUSE NEITHER IS MINE TO CLEAR

    _verify_marker_census.py    C1's in OWNERS.md
    checks/marker_census.json   C1's in OWNERS.md
    _verify_child_markers.py    MINE by the default clause - but its baseline is
                                data-layer/derived/holo-hardpoints/
                                loadout_marker.pre-C1-20260829.js, and C1
                                CLAIMED that directory this morning.

**So the control is mine and the file it compares against is C1's.** Re-taking
that snapshot is a write into C1's path, and the whole point of this morning's
rule 14 work was to stop doing exactly that. C1 sets the condition for re-taking
it anyway — the pinned four checked first — and C1 is the one who can say
whether losing `MISC Hull C:34` was intended.

## THE DEPLOY IS REFUSED, AND I ASKED THE GATE RATHER THAN ASSUMING

    $ python checks/sweep_gate.py --check testing/_deploy
    sweep   : the last sweep of THIS payload was not clean.
              FAILED   _verify_child_markers.py
              FAILED   _verify_marker_census.py
    GATE EXIT 1

**Nothing was uploaded and I did not try to.** The served site stays on 04:47
until the two reds are resolved by their owner. Weakening the gate to ship past
its own finding is the one thing that is never on the table.

## WHAT I NEED FROM C1, SPECIFICALLY

    1  declare the BANU_Defender 10 -> 8 loss in marker_census.json, or say it
       is not intended
    2  say whether MISC Hull C:34 going was intended, and why port 2 stayed
    3  authorise a re-take of loadout_marker.pre-C1-20260829.js, or take it

Then the sweep goes green and the deploy runs without anything being bypassed.

**Next while that waits: Q25, the separator DECISION doc.** It needs nothing
from anyone.

### 2026-08-29 10:08:34 — 20260829_1045_update_q21-cannot-be-closed-by-a-build-the-withholding-does-not-reach-the-marker-file.md

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

### 2026-08-29 10:02:43 — 20260829_1030_update_q21-received-build-sweep-deploy.md

# Update — Q21 through Q26 received. Taking Q21 (rebuild and deploy) with Q24 folded into its run, as the order says.

**2026-08-29 10:30 local · Code (background session)**

Sleven relayed C1's answers and put Q21 first. Filing before I start, rule 13.

## THE FOUR ANSWERS, AND WHAT I DO WITH EACH

    Q22  the last rule-16 label      C1 did it. VERIFIED MYSELF, not taken on
                                     the line: 105 labelled, 0 unlabelled,
                                     0 malformed. I had already removed the
                                     closed baseline entry at 09:52.
    holo-hardpoints/                 claimed by C1 in OWNERS.md. Closed.
    Q25  the separator DECISION doc  MINE. I own the enforcer, so I am the only
                                     one who can write what it enforces.
    Q26  the off-hull ten            BLOCKED-BY Q21. Not measuring the old
                                     payload.

## WHAT I AM DOING NOW

    1  Q24  the false comment at build_deploy.py:1359 - my file, one line
    2       python testing/_src/build_deploy.py
    3       assert BANU_Defender 50/51 and MISC_Hull_C 2 are gone
    4       run_all_controls.py --include-deployed
    5       deploy_testing.ps1
    6       verify the served site

## ONE LINE IN Q21 IS NOW STALE, AND IT MATTERS FOR THE ORDER

Q21 ends: *"Sweep first, let it finish, then deploy — the sweep rebuilds the
payload."*

**The sweep no longer rebuilds the payload.** I removed that this morning:
`_verify_deploy_drift.py` snapshots, rebuilds, compares and puts everything back
byte for byte, mtimes included. **Q21's own command list is already right** -
build, then sweep, then deploy - so nothing about the plan changes. But the
reason given for the order is gone, and the order now matters MORE rather than
less: **a sweep will no longer quietly fix a payload somebody forgot to build.**

## AND I STOPPED A SWEEP TO DO THIS

The clean re-run I started at 09:58 was measuring the payload Q21 replaces.
Killed rather than left to finish - its drift finding is the one Q21 closes, and
a green-or-red on a superseded payload tells nobody anything. **The verification
of the drift fix does not depend on it**: that stands on the 612-file
before/after manifest, hash and mtime, which is already recorded.

## Q24 IS C1'S RULE 14 VIOLATION AND I AM NOT RE-LITIGATING IT

C1 edited `build_deploy.py:1359`, caught it, reverted it, and wrote the erratum.
`git diff` on that file is empty and it is byte-identical to `4710d30` — **I
checked rather than took the sentence.** Self-caught and self-reported is the
system working. I am making the edit because the file is mine.

### 2026-08-29 09:57:00 — 20260829_1015_update_i-did-the-thing-the-fix-is-about-to-my-own-verification.md

# Update — I perturbed my own verification the way the defect perturbs the sweep. Sweep killed, results discarded, and the mistake is recorded rather than tidied away.

**2026-08-29 10:15 local · Code (background session)**

## WHAT I DID

I started a full sweep in the background to confirm the drift fix in the place
it was built for — **and then kept editing and running
`checks/_verify_deploy_drift.py` while that sweep was executing it.**

**That is the exact defect I spent the morning fixing, done to my own
verification.** It is also the first of the three perturbations the 28th's
update lists — *"this morning I edited checks/ while a sweep executed those
files"* — so it is the second time, not the first.

## HOW IT SHOWED

An independent manifest of `testing/_deploy` and `testing/_src` came back with
content differences I could not account for:

    _deploy/holo.html               hash moved
    _deploy/loadout.html            hash moved
    _deploy/loadout_marker.gen.js   ef9be07 -> 2536dbd, in _deploy AND _src
    _src/.last_build.json           hash moved

**None of those were my probe.** The probe left bytes intact and moved only
mtimes. The moving hashes are a concurrently-running sweep: its own copy of the
drift control planting into `_deploy` in section 5, and a rebuild landing from a
version of the file that no longer existed on disk by the time it ran.

## WHAT I DID ABOUT IT

**Killed the sweep and discarded its results.** A sweep whose controls changed
underneath it measures nothing, and reporting a number off it would be
manufacturing exactly the confidence this project calls SILENT SUCCESS.

Nothing was lost — the sweep was confirmation, not the work — and the fix's own
verification stands on its own evidence, taken before the sweep and repeated
after it:

    612 files, hash AND mtime, before and after a full run
    IDENTICAL - EVERY HASH AND EVERY MTIME

**Next: put the tree back to the state the manifest recorded before any of
this**, then re-run the sweep with nothing else touching `checks/` — which is
the only way its result means anything.

## THE RULE THAT IS MISSING, AND IT IS NOT A NEW ONE

A sweep has no lock. Nothing stopped me editing a control mid-run, and nothing
stopped C1 regenerating `data-layer/` mid-run on the 28th. **Rule 14's own
words apply: a rule that depends on remembering it is a convention, not a
guard.** The drift control was the one perturbation I could close by
construction, and it is closed. The other two are still open by design.

Not proposing a fix for that in this update. Recording it so the next session
does not rediscover it as a surprise.

### 2026-08-29 09:53:15 — 20260829_1010_update_the-drift-control-no-longer-writes-to-what-it-audits.md

# Update — the deploy-drift defect is fixed: the control no longer writes to the artifact it audits, and the guard was proven by disabling it. Q7 is 105 of 105.

**2026-08-29 10:10 local · Code (background session)**

## THE RULING

**A checker is not a writer of the artifact it audits.** `testing/_deploy` has
one writer — `build_deploy.py` — and `_verify_deploy_drift.py` is not it. That is
rule 14 applied to the one artifact where nobody had applied it.

I named three options on the 28th. **I took none of them.** Not "the sweep
refuses mutating controls" (fixes ordering only, not the evidence loss), not
"snapshot the payload first" (moves the problem to whoever remembers to), and
not "stop rebuilding and report" — **that one would have thrown away the only
honest proof an assembled file has.** `index.html` is built from
`releases/latest.html` plus a dozen substitutions; there is no source to compare
it to. Rebuild-and-compare is the whole proof.

**So: SNAPSHOT, REBUILD, COMPARE, RESTORE.** The comparison is untouched and
nothing is exempted from it. Afterwards every file the rebuild wrote is put back
byte for byte.

## WHAT IT COST BEFORE, FOR THE RECORD

    ORDERING      a control's result depended on where its name sorted
                  relative to "d"
    EVIDENCE      a "before" copy taken at 23:37 on the 28th was an "after"
    A REAL ABORT  the deploy gate refused an upload because this control moved
                  the payload between two of Sleven's commands

## THE FILES IT WAS WRITING, WHICH WERE MORE THAN I THOUGHT

`build_deploy.py` writes **four generated files into `testing/_src`** as well as
the payload — `loadout_model`, `loadout_marker`, `loadout_eng`, `craft_data` —
**and its own receipt**, `.last_build.json`, which `deploy_testing.ps1` reads to
decide whether a build succeeded.

**That last one is a defect on its own.** A rebuild run for AUDIT was leaving
behind a receipt saying a build had completed ok. The receipt is now restored
with everything else.

The watched set is **discovered, not listed** — 77 files this run. A hand-written
list would go stale the day a fifth generated file appears, and it would fail
silently, which is the exact shape of thing this control exists against.

## THE GUARD IS PROVEN BY BEHAVIOUR, BOTH WAYS

Every other assertion in section 4 is measured BEFORE the restore runs, so all
of them would still pass if the restore quietly did nothing. **So the restore
has its own assertion, and I made it fail on purpose.**

    PROBE: a copy with restore() replaced by a no-op

    FAIL  and _deploy and _src are byte for byte as this control found them
          (still moved: testing\_deploy\loadout_marker.gen.js,
           testing\_src\.last_build.json, testing\_src\loadout_marker.gen.js)

Named all three. The probe is in `_to_delete/probes-20260829/`, never deleted.

**And verified from OUTSIDE the control**, because a manifest built by the code
under test proves nothing: an independent script hashed all 612 files under
`_deploy` and `_src` before and after — assets by size and mtime, 445 MB of
models not worth hashing.

    612 file(s) recorded ... IDENTICAL - the control left nothing moved

Twice, on two consecutive runs. `--self-test` still inverts and exits 1.

## IT IMMEDIATELY FOUND SOMETHING THE OLD BEHAVIOUR HID

    FAIL  and so is every copied file (moved: loadout_marker.gen.js)
    -   259 hulls, 6060 markers.
    +   259 hulls, 6058 markers.

**The deployed testing payload is two markers behind its sources.** Real drift,
not non-determinism — `index.html` rebuilt byte-identical beside it.

**The old behaviour would have reported this once and then buried it.** Run one
rebuilt the file, so run two found the payload already matching and went green.
A finding that disappears when you look again is worse than no finding. It now
stays red until somebody runs the build deliberately.

**I have not run that build.** It is a payload change and it wants a deploy
behind it; that is a separate decision and it is Sleven's, not something to
staple onto a checker fix.

## AND Q7 CLOSED WHILE I WAS IN THERE

C1 labelled `_verify_panel_dismiss.mjs` INDEPENDENT. The gate asked for the
baseline line to come out, so it came out:

    labelled 105  (56 INDEPENDENT, 49 UNPROVEN)   unlabelled 0   malformed 0
    0 gap(s) still on the list

`rule16_baseline.txt` is now empty of entries and says why. **Q7 is 105 of 105.**

## STANDING

Files changed: `checks/_verify_deploy_drift.py`, `checks/rule16_baseline.txt`.
Nothing committed. A full sweep is running to confirm the fix in the place it
was built for — the first sweep in this repo that cannot be perturbed by its own
drift control.

### 2026-08-29 09:41:56 — 20260829_1000_update_taking-the-deploy-drift-decision.md

# Update — taking the deploy-drift decision. Sleven said go; I am ruling on it rather than filing another flag.

**2026-08-29 10:00 local · Code (background session)**

I flagged this twice and did not rule. Sleven has now told me to go ahead, so
this is the third mention and the last one.

## THE DEFECT, STATED ONCE

`_verify_deploy_drift.py` proves `testing/_deploy/index.html` the only honest way
available — **it REBUILDS and requires the bytes not to move.** The rebuild
writes into the real `testing/_deploy`, and that is a shared artifact the rest of
the sweep reads.

**It has cost three separate things, none of them theoretical:**

    ordering       a control's result depends on where its name sorts
                   relative to "d". Controls before the rebuild measure one
                   state; controls after measure another.
    evidence       22:23 on the 28th - it rebuilt the payload after C1's 22:19
                   data fix, so the "before" copy I took at 23:37 was an
                   "after". I nearly reported 0 hulls lost markers when the
                   Tiburon had gone from seventeen to none.
    a real abort   Q10's gate refused a deploy because the payload hash moved
                   between Sleven's two commands. The thing that moved it was
                   the sweep's own drift control.

The one measurement that made it undeniable: `_verify_marker_provenance.py` and
`_verify_marker_spread.py` FAILED in the sweep and passed ten minutes later,
while `_verify_marker_census.py` passed in the sweep and failed after. **Three
controls disagreeing with themselves in both directions is one measurement taken
during a write, not three defects.**

## WHAT I AM ABOUT TO DO

I named three options on the 28th and said the choice was a design decision.
Having read the checker again, **I think there is a fourth that gives up
nothing**, and I am checking it before I commit to it: rebuild into a scratch
directory and compare there, so the proof survives and the mutation does not
happen at all.

If `build_deploy.py` cannot be pointed at an output directory, that option dies
and I will take one of the original three and say which.

**Ownership checked first:** `_verify_deploy_drift.py` is not in C1's list in
`OWNERS.md`, so it is Code's by the default clause. `testing/_src/build_deploy.py`
is explicitly Code's. Nothing here touches a C1 path.

Rule 12 applies to the result: whatever I build, the failure path gets exercised
on purpose before I call it working.

### 2026-08-29 09:39:19 — 20260829_0950_update_check-in-with-c1-four-things-and-an-empty-queue.md

# Update — check-in with C1: Q20 is pushed, Code's queue is empty, and four things are waiting on C1. One of them is a single line.

**2026-08-29 09:50 local · Code (background session) · addressed to C1**

Sleven asked me to check in with you. I have no channel to you that I own —
`NEXT.md` is yours and I do not write it — so this is the handoff, which is the
path `OWNERS.md` leaves open.

**Everything below was measured this morning, not read off the board.**

## 1. HISTORY MOVED. `4710d30` IS PUSHED.

    4710d30   383 files changed, 14,043 insertions, 17,912 deletions
    1a1b4b7..4710d30  main -> main
    working tree      clean, 0 entries

Sleven gave the go-ahead in session, so rule 2 is satisfied. Staged by path,
never `git add -A`; `_to_delete/` contributed 0 files, checked in the index
before and in `git log -1 --name-only` after. **Nothing went to the live site.**

Your `data-layer/derived/hardpoint-placement/` (285 files),
`holo-hardpoints-align/` (3) and `crafting-demand/` (1) are all in it, along
with `build_hardpoint_placement.py` and `build_hardpoint_overlay.py`. **If you
have uncommitted work on the Cowork mount, it is not in this commit and I did
not go looking for it.**

## 2. Q7's LAST LABEL IS YOURS, AND IT IS ONE LINE

Run just now rather than quoted:

    RULE 16 LABELS - 105 check(s)
      labelled            104  (55 INDEPENDENT, 49 UNPROVEN)
      unlabelled          1
      malformed label     0

    $ grep -c RULE16 checks/_verify_panel_dismiss.mjs
    0

`_verify_panel_dismiss.mjs` is yours in `OWNERS.md`. **I am not writing a line
into your file to close my own queue item** — that is the exact move rule 14
exists against. One `RULE16: <INDEPENDENT|UNPROVEN> - <reason>` line from you
and Q7 is 105 of 105.

**Mind the separator.** `malformed label 0` is true today and the gate now tells
the two apart, but the fourth comma was two hours after the third.

## 3. AN OWNERSHIP GAP, IN THE DIRECTORY WHERE A FILE WENT MISSING

    data-layer/derived/holo-hardpoints-align/    yours
    data-layer/derived/holo-hardpoints/          NOBODY'S

`_verify_owners.py` passes — A, B and C all green — because it validates the
paths that are listed. **It cannot see a path nobody claimed.** Your own words:
*"a path that is not in this file has no declared owner. That is not permission;
it is a gap, and finding one is worth reporting."*

**And it is the directory where rule 1 was not followed.**
`loadout_marker.pre-C1-20260828.js` was **deleted** from the working tree rather
than moved to `_to_delete/`, and `pre-C1-20260829.js` replaced it. Content is
safe in `1a1b4b7` and both the delete and the replacement are recorded in
`4710d30`'s message rather than quietly absorbed. **I did not do it and I cannot
tell which session did** — which is itself the argument for the directory having
a name against it. `OWNERS.md` is yours; the assignment is your call.

## 4. THE FOURTH COMMA WANTS A `docs/DECISION_*`

Your note says it plainly — *worth a `docs/DECISION_*` rather than a fifth
occurrence* — and it has now cost you an hour and me three dry-run cycles. I
have not written it: the format is the shared contract and I did not want to
rule on it alone. **Yours or mine?** I will write it today if you say mine.

## 5. YOUR OFF-HULL TEN ARE ON NOBODY'S QUEUE

`FINDING_four-hulls-draw-a-dot-in-empty-space-2026-08-29.md` — 2,193 dots, 87.2%
exactly on the hull, ten that are not:

    BANU_Defender   port 50 @19px, port 51 @38px      DRAK_Corsair  3 of 15
    TMBL_Storm_AA   port 4 @15px                      VNCL_Glaive   port 43 @16px

It is committed and it is real, and **it is not an item on any queue.** The
Defender is also a client-record hull, which is the set I drove through a browser
at 08:40 — that control proves the dots DRAW; it cannot say they draw in the
right place, and the label says so.

## WHAT I NEED FROM C1

    the one line in _verify_panel_dismiss.mjs     closes Q7 at 105 of 105
    an owner for data-layer/derived/holo-hardpoints/
    the DECISION doc on the separator             yours or mine
    whether the off-hull ten become Q21
    what is next                                  Code's queue is empty

**One thing is mine and I am not passing it to you:** the sweep's own
`_verify_deploy_drift.py` rebuilds the artifacts other controls read, which
perturbs the measurement and destroyed a "before" copy I needed on the 28th. I
have flagged it twice and not ruled. I will rule on it rather than ask.

Going live is Sleven's and stays off the queue.

### 2026-08-29 09:22:26 — 20260829_0940_update_q20-done-committed-and-pushed-4710d30.md

# Update — Q20 done. 383 files committed and pushed as `4710d30`; working tree is clean and nothing went to the live site.

**2026-08-29 09:40 local · Code (background session)**

Sleven gave the go-ahead in this session, so rule 2 is satisfied for this change.

    4710d30   383 files changed, 14,043 insertions, 17,912 deletions
    1a1b4b7..4710d30  main -> main
    local HEAD == origin/main == 4710d30
    git status --porcelain    0 entries

## Staged by path, never `git add -A`

    data-layer/derived/hardpoint-placement     285
    data-layer/derived/holo-hardpoints-align     3
    data-layer/derived/holo-hardpoints           2
    data-layer/derived/crafting-demand           1
    checks/                                     65
    docs/                                       20
    testing/_src/loadout_marker.gen.js           1
    build_hardpoint_placement.py, build_hardpoint_overlay.py,
    OWNERS.md, NEXT.md, LATEST_HANDOFF.md        5

## Verified after, not assumed

- **`_to_delete/` contributed 0 files** - checked in the index before the commit
  and again in `git log -1 --name-only` after it. The 5.2 GB of C1 tarballs did
  not enter history.
- **No path outside the expected set.** I filtered the commit's file list against
  the eight roots above and it came back empty.
- **No `.git/index.lock` trouble.** It was already absent; C1's stale lock is in
  `_to_delete/git-locks/`.
- **Nothing binary or oversized.** Largest entry is `_updates_log.md` at 2.0 MB,
  text, already tracked.
- **The push landed** - `git fetch` then a hash comparison, not the push's own
  output.

Line-ending warnings (LF to CRLF) appeared on the 285 placement JSONs. Cosmetic,
Windows-normal, no content change.

## What went in, and one thing that did not

NEXT.md left the backup to my judgement, so:
`loadout_marker.pre-C1-20260829.js` **is in history**. The matching deletion of
`pre-C1-20260828.js` went in with it, so the tree is coherent rather than
carrying a dangling delete. **That deletion was not mine** - the file was removed
instead of moved to `_to_delete/`, against rule 1, and I do not know which
session did it. Content survives in `1a1b4b7`. It is recorded in the commit
message rather than quietly absorbed.

**Nothing reached the live site.** GitHub only, as the go-ahead covered. Going
live remains off the queue until Sleven raises it.

## Standing

**Code's queue is now empty.** Q7's last label is C1's file. The three
outstanding items are unchanged and none are queue work: the
`_verify_deploy_drift.py` rebuild-during-sweep decision (mine to make and I have
deferred it twice), the RULE16 separator trap, and going live.

### 2026-08-29 09:19:03 — 20260829_0930_update_asked-whats-next-queue-is-empty-except-q20.md

# Update — asked "what's next": Code's queue is empty except Q20, which needs Sleven's word in this session.

**2026-08-29 09:30 local · Code (background session)**

Sleven asked what is next. I checked the DONE-WHENs rather than reading the
board, per NEXT.md's own instruction.

## What I checked, not remembered

    git status --porcelain      382 entries: 363 M, 18 ??, 1 D
    last commit                 1a1b4b7, 2026-08-28 10:52
    staged                      0
    _to_delete/                 gitignored, .gitignore:46 - confirmed, 0 entries
    .git/index.lock             absent; C1's stale lock is already moved aside

NEXT.md's Q20 quotes 504 files. It is 382 now. The number moved; the item did
not.

## The state

**Q1-Q6, Q8-Q19 and Q12 (ORIGINAL) are closed.** Q7 stands at 104 of 105, and
the last one is C1's file, not mine. **Q20 - commit and push - is the only
thing at the head of the queue.**

NEXT.md records that Sleven said yes to Q20 on 2026-08-29. **I have not acted
on it.** Hard rule 2 wants the go-ahead in the message, for the change, and
what I have is C1's record of one. I asked rather than assumed. It costs a
minute; the alternative is a push nobody authorised in this session.

## One thing I found while scoping it

    D  data-layer/derived/holo-hardpoints/loadout_marker.pre-C1-20260828.js
    ?? data-layer/derived/holo-hardpoints/loadout_marker.pre-C1-20260829.js

Yesterday's backup was **deleted from the working tree**, not moved to
`_to_delete/`, and today's replaced it. It is tracked, so the content is safe in
`1a1b4b7` and recoverable. Flagging it rather than fixing it: I did not do it,
and I do not know which session did. **Rule 1 was not followed on that file.**

## Standing

Waiting on Sleven for Q20. Nothing else on Code's queue is open. The three
outstanding non-queue items are unchanged: the `_verify_deploy_drift.py`
rebuild-during-sweep decision, the RULE16 separator trap (four occurrences,
two people), and going live - his.

### 2026-08-29 08:30:40 — 20260829_0840_update_q12-original-the-client-record-hulls-are-through-the-browser.md

# Update — Q12 (ORIGINAL) done: all 27 client-record hulls driven through a real browser, 27 of 27 draw their markers. And C1's newest finding says why it mattered.

**2026-08-29 08:40 local · Code (background session)**

    ---- 27 client-record hull(s), drawn on screen ----
    27 hull(s) driven; 0 have no ship row, 0 carry no marker
    ok   the client-record hulls were actually driven  (27 of 27)
    ok   and every one of them draws its markers  (27 of 27)

    GREEN - the markers on the page are on CIG's own coordinates.

**The 41 are 27 now** - the orientation refusal withdrew the rest overnight -
and the DONE-WHEN asks for the result by name, so: every one of
`AEGS_Eclipse`, `BANU_Defender`, `CRUS_Star_Runner`, `DRAK_Dragonfly`,
`MISC_Fury`, `ORIG_600i`, `ORIG_85x`, `TMBL_Nova`, `gama_tyilui`, `mrai_pulse`,
`mrai_pulse_lx`, the five `rsi_aurora_gs_*`, the four `crus_starfighter_*`, the
four `crus_starlifter_*`, `aegs_eclipse_bis2950`, `aegs_gladius_pir` and
`orig_600i_bis2951` was loaded in Chromium and asserted to draw.

## Why this was worth doing rather than declaring answered

`_verify_marker_provenance.py` proves every dot the page calls `cig` sits on its
own hull's CIG coordinate. **It cannot say whether that coordinate renders where
the mount is**, and no browser control had ever looked at these hulls.

**C1's off-hull audit, filed at 23:49 last night, makes that concrete.** Ten dots
float in empty space across four hulls - and the worst in the entire fleet, port
51 on the **Banu Defender at 38px clear of its own silhouette**, is a
client-record hull. These are also the hulls whose provenance was wrong for a
day.

## What it adds, and what it deliberately does not

It asserts the markers exist and are DRAWN. **It does not assert they are on the
hull** - that needs a silhouette and a second screenshot, which is what
`offhull.py` does in fifty minutes and a sweep cannot. A dot in the wrong place
still passes here; a hull that draws nothing does not. The label says so.

Cost: the control goes from 8.6s to **77s**. That is real and it is the price of
27 model loads in a browser. Still half of `_verify_broken_checker_end_to_end`'s
126s, which is the sweep's current ceiling.

## THE SECTION CAUGHT ITSELF TWICE BEFORE IT CAUGHT ANYTHING ELSE

I wrote a `check(checked > 0, ...)` guard - *"a section that drove nothing is not
a section that passed"* - and it earned its place immediately:

    FAIL the client-record hulls were actually driven  (0 of 27)
    ok   and every one of them draws its markers  (0 of 0)

**Twice.** Both times my key lookup went through `SHIPS[k].cls`, and the second
assertion sat there reporting green on an empty set beside it.

**`SHIPS` rows carry no `cls` field at all.** MARKS and SHIPS share a key
directly - the page itself reads `MARKS[shipId]`. Without the guard this section
would have shipped as two green lines that had looked at nothing, which is the
exact defect the whole suite exists against.

**It also explains something I had seen and not chased.** Every
`_diag_served_ship.mjs` run all week printed `"marksForClass": null`, because my
diagnostic used the same wrong indirection. The number was always null and I read
past it for two days.

And the Gladius block above it finds its own ship by a NAME SUBSTRING for the
same reason - its `SHIPS[k].cls === c` term has never matched anything. Not
touched: it works, and changing a passing control's lookup at 08:40 to tidy it is
how a green suite becomes a red one.

## Standing

    Q1-Q6, Q8-Q19 and Q12 (ORIGINAL)   done
    Q7                                 104 of 105; the last is C1's file

**Nothing on Code's queue is open.** What is outstanding is not queue work:

- **a very large uncommitted tree** - two days of it, since `1a1b4b7`
- **the decision I have flagged twice and not made**: the sweep's own
  `_verify_deploy_drift.py` rebuilds the artifacts other controls read, which
  perturbs measurements AND destroyed a "before" copy I needed last night
- **the RULE16 separator trap** - four occurrences, two people
- **going live** - Sleven's, and the worker still 404s

### 2026-08-28 23:50:48 — 20260828_2352_update_q19-done-the-heap-is-off-the-site.md

# Update — Q19 done. The heap is off the served site, 106 controls green, and I lost a piece of my own evidence on the way.

**2026-08-28 23:52 local · Code (background session)**
Version `588f1f6c-50a4-45a5-9b70-9c5a91a7b833`.

---

# THE HEAP IS GONE FROM WHAT A VISITOR GETS

    106 ok, 0 failed, 0 skipped, 0 NOT RUN, in 616s
    2 files uploaded

Verified from the SERVED bytes, not the build log:

    served 283,031 bytes  ef9be078c18f8de5
    provenance: 1,875 cig / 141 est / 4,044 anc = 6,060

    AEGS_Tiburon                     0 markers, 0 labelled cig
    RSI_Mantis                       0 markers, 0 labelled cig
    RSI_Hermes                       0 markers, 0 labelled cig
    MISC_Starlite                    0 markers, 0 labelled cig
    ORIG_m80                         0 markers, 0 labelled cig
    GLSN_Basher                      0 markers, 0 labelled cig
    ORIG_600i_Executive_Edition      0 markers, 0 labelled cig
    RSI_Aurora_Mk2                   0 markers, 0 labelled cig

And on the served page itself: **the Tiburon renders its model and draws zero
dots**, where until this deploy it drew seventeen in a clump and called them
CIG's own. The Buccaneer is unaffected - 337px of spread, dots where they belong.

**Absent beats confidently wrong**, and that trade is now made on the live
testing site rather than in the tree.

## The fleet-level cost, stated rather than buried

    markers   6,326 -> 6,060    (-266)
    cig       2,006 -> 1,875    (-131)

Fourteen hulls lost their CIG markers. That is the correct outcome - they were
never CIG's positions, the scale came off the wrong axis on models that measure
taller than they are long - but it IS a visible reduction and Sleven should hear
it as one rather than discover it.

## The baseline, re-taken with C1's condition checked FIRST

C1 asked that the list be read before the snapshot, and that any name outside the
orientation-refused set be treated as the finding rather than the baseline.

    14 distinct hulls: Tiburon, Khartu-al, San'tok.yai, Pitbull, Basher, Railen,
    Reliant Kore, Starlite, 600i Executive, M80, Aurora GS SE, Aurora Mk2,
    Hermes, Mantis

**Every one is from that set. No stranger appeared.** Restore verified
byte-identical (`ef9be078` both sides), control 16/0, all four known-bad inputs
still exiting 1.

---

# A MISTAKE IN MY OWN EVIDENCE, AND IT IS WORTH THE PARAGRAPH

I tried to measure exactly what the page lost by diffing the marker file I had
saved aside against the new one. It reported **0 hulls lost markers and 0 hulls
had fewer** - which is plainly false, since the Tiburon went from seventeen to
none.

**The copy I saved as "SHIPPED" was already the fixed build.** The sweep's own
`_verify_deploy_drift.py` rebuilt the payload at 22:23, after C1's 22:19 data
fix, so by the time I copied it aside at 23:37 the heap was already out of it.
My "before" was an "after".

**I nearly reported 0/0 as though nothing had changed.** The numbers above come
from the fleet totals and the served bytes instead, which I can actually stand
behind. The true pre-fix marker file is the one that was being served until
tonight and I no longer have it locally.

Two things follow: **the drift control rebuilding mid-sweep destroys evidence as
well as perturbing measurements**, which is another entry for the decision I
flagged at 22:25 and have not made; and a "before" copy is worth taking before
the first rebuild rather than after the third.

---

# Q19'S OPTIONAL PART: NOT TAKEN, WITH A REASON

C1 offered an emitter-side rule - group by `PortId.split(".")[0]`, take the
shallowest, drop a hull's CIG markers if its drawn dots span under 0.47 while the
model measures taller than long.

**`_verify_marker_spread.py` exits 0 right now.** C1's placement fix already
covers the M80 and the Starlite, so the rule would have nothing to catch today.
Adding a guard with no work to do is inventing one rather than needing one, and
the control will say if that changes. **Taken if it goes red.**

---

    Q1-Q6, Q8-Q19    done
    Q7               104 of 105 labelled; the last is _verify_panel_dismiss.mjs,
                     which OWNERS.md names as C1's
    testing site     588f1f6c, served bytes match the build
    live site        404, never run for real

Nothing committed since `1a1b4b7` - and that is now a very large tree.

### 2026-08-28 22:42:02 — 20260828_2245_update_q7-is-done-except-c1s-one-file.md

# Update — Q7 is done except for one file, and that one is C1's. 104 labelled, 1 left, and the debt list is a single line.

**2026-08-28 22:45 local · Code (background session)**

    labelled     104  (55 INDEPENDENT, 49 UNPROVEN)     was 81
    unlabelled     1
    malformed      0

    rule16_baseline.txt now contains exactly one entry:
        _verify_panel_dismiss.mjs

**`OWNERS.md` names that file as C1's, so it is C1's to label.** Every other
control in `checks/` now declares where its truth comes from, or names what it
could not reach.

Twenty-two controls in this pass, in two tranches. **All twenty-two green
afterwards**, including the two that go over the network.

## The strongest labels came from the same three shapes

**Run it as a subprocess with input you built.** `_verify_patch_diff`,
`_verify_takedown`, `_verify_hardpoint_data`, `_verify_community_mark`,
`_verify_extremity_placement`, `_verify_turret_inheritance` - nothing imported,
the expectation decided here, the verdict read from an exit code and what was
left on disk.

**Perturb it and require the answer to move, or not to.**
`_verify_placer_candidates` empties the fleet file and requires the candidate
count NOT to fall - 186 either way. **If the placer were reading its own output,
emptying that output would change the answer.** No assertion about the source
could have established that.

**Go and look at the served bytes.** `_verify_deployed_links` and
`_verify_picker_deployed` fetch the deployed origin. A build exiting 0 is not
accepted as evidence about what a visitor receives.

## And one UNPROVEN that is a requirement rather than a shortfall

`_verify_attribution.mjs` takes the expected wording from
`testing/_src/attribution.py` - **the build's own constant** - so the pages are
compared against the same definition that produced them.

**That is required, not convenient.** Hard rule 8 makes the legal text Sleven's
alone and rule 14 forbids a second writer for it. A control carrying its own
copy would be a rule violation AND the worse kind of useless: it would keep
passing while the page said something different, because both sides would be
reading the checker's copy. `_verify_deploy_drift.py` makes the same trade for
the same reason, and both labels say so.

**UNPROVEN is not a grade.** Nineteen of the forty-nine are files whose subject
is a checker, and proving a checker fires on planted input is rule 12's job
rather than rule 16's.

## THE FOURTH COMMA

`RULE16: UNPROVEN, deliberately, and this is...` - the separator again, fourth
time across two sessions.

The format wants `VERDICT - reason` and English wants a comma after the verdict.
It has now cost C1 an hour and me three dry-run cycles. **The gate accepting a
comma would be the wrong fix** - the separator is what makes the reason
machine-readable - but the trap is in the format and it will catch the next
person too. Worth a `docs/DECISION_*` rather than a fifth occurrence.

## What Q7 actually produced, beyond the labels

Writing one forces the question *"what would this check fail to notice"*, and
five answers were specific enough to act on:

    _verify_label_cold_start   asserts a source STRING, not a behaviour
    _verify_labels             counts the page against the page
    _verify_ship_page_fits     models a browser's layout rather than measuring it
    _verify_hull_solid         already said so itself, before rule 16 existed
    _verify_ship_page N9       duplicated a sentence another control asserts
                               better - deleted under Q14

Nothing committed since `1a1b4b7`.

### 2026-08-28 22:25:23 — 20260828_2225_update_the-sweep-measured-a-moving-dataset.md

# Update — That sweep measured a moving dataset. C1 regenerated the overlay while it ran, and three marker controls disagree with themselves ten minutes apart.

**2026-08-28 22:25 local · Code (background session)**

    103 ok, 3 failed, 0 skipped, 0 NOT RUN, in 683s

    FAIL  _verify_marker_census.py
    FAIL  _verify_marker_provenance.py
    FAIL  _verify_marker_spread.py

**Do not read those three as findings. The sweep was measuring something that
was being rewritten underneath it.**

## The evidence

    sweep ran                              22:12 - 22:23
    data-layer/hardpoint-placement/        written 22:18:56
    data-layer/holo-hardpoints-align/      written 22:19:08
    testing/_src/loadout_marker.gen.js     written 22:23:24

**C1 regenerated the placement and the client overlay in the middle of the
run**, and the sweep's own `_verify_deploy_drift.py` then rebuilt the marker
file from the new data. Controls that ran before that point read one dataset and
controls that ran after read another.

The count says it plainly:

    markers carrying a label, during the sweep    6,133
    markers carrying a label, ten minutes later   6,060

And re-running the same three now:

    _verify_marker_provenance.py   FAILED in the sweep -> passes now
    _verify_marker_spread.py       FAILED in the sweep -> passes now
    _verify_marker_census.py       passed in the sweep -> FAILS now (ORIG_m80)

**Three controls, all disagreeing with their own result from ten minutes
earlier, in both directions.** That is not three defects; it is one measurement
taken during a write.

## The structural half, which is mine

This is the third time today a sweep has been perturbed, and twice it was
avoidable:

    this morning   I edited checks/ while a sweep executed those files
    this evening   C1 regenerated data-layer/ while a sweep read it
    all day        the sweep's OWN _verify_deploy_drift.py rebuilds the
                   artifacts that later controls read, so a control's result
                   depends on where its name sorts relative to "d"

**The third one is a real defect in the sweep and it is mine.** A control that
rebuilds shared artifacts mid-run makes every control after it a measurement of
a different state from every control before it. It has not bitten on its own
because the rebuild is normally byte-identical - but "normally" is doing all the
work in that sentence, and tonight the data moved underneath it.

**I am not fixing it in this pass**, because the fix is a design decision rather
than a repair: either the sweep refuses to run controls that mutate shared
state, or it snapshots the payload first, or the drift control stops rebuilding
and reports instead. That belongs in a `docs/DECISION_*` with C1, not in a
20-minute edit at 22:30.

## What I am NOT doing

**Re-running the sweep now.** The data settled at 22:19 and has not moved in six
minutes, but a receipt taken while C1 may still be mid-run is worth nothing, and
I have already spent one 683-second sweep finding that out.

The gate is refusing on the stale receipt, which is correct: the payload
fingerprint moved to `9ccd3bbf` and nothing has vouched for it.

## What is true regardless

    Q13, Q14, Q15   done and verified individually, not by the sweep
    Q7              81 of 104
    served site     f278ca37; its ship page still matches the last build
    live site       404, never deployed

`_verify_marker_census.py`'s current failure on `ORIG_m80` may be real or may be
the same moving target. **It is C1's control and C1's data.** I will look at it
when the dataset has been still for long enough to mean something, and say which
it was.

### 2026-08-28 22:12:32 — 20260828_2215_update_q15-q14-q13-done.md

# Update — Q15, Q14 and Q13 done. And the `%s` fix printed a real refusal correctly for the first time.

**2026-08-28 22:15 local · Code (background session)**

---

# Q15 — `clearTimeout`, AND I TOOK THE HARDER OPTION

C1 offered `clearTimeout: () => {}` and noted the alternative would be "closer to
a browser". **The stub really cancels now.**

    setTimeout   returns a SLOT INDEX rather than timers.length. Two pending
                 timers could otherwise share an id the moment one was
                 cancelled, and the id identified nothing.
    clearTimeout empties that slot.
    flushTimers  skips an emptied slot and does NOT count it - `ran` is what a
                 control asserts on, and counting a callback that never fired
                 would report deferred work that did not happen.

**And the flush uses a cursor rather than `shift()`.** A callback may cancel a
later one, and `shift()` renumbers everything behind it - so `clearTimeout(4)`
would have emptied whatever had moved into slot 4. That would have been a bug
introduced by the fix for a bug.

    node checks/_verify_swap_loop.mjs    28/28, and no NOT PERFORMED lines

**All 22 harness-using controls re-run: 0 failing.**

---

# Q14 — DELETED, AFTER CHECKING THE REPLACEMENT WAS BETTER

I said this morning that deleting would leave nothing checking the per-ship
claim. **That was wrong, and Q14 answers it directly**: the five assertions live
in `checks/_verify_marker_note.mjs`, which asserts MORE than N9 did.

**Verified before deleting rather than after:**

    node checks/_verify_marker_note.mjs                     17 pass
    node checks/_verify_marker_note.mjs --mutate-fleetwide  exit 1
    node checks/_verify_marker_note.mjs --mutate-blind      exit 1
    node checks/_verify_marker_note.mjs --self-test         exit 1

and its own closing line is the reason it is better than what I wrote:

> The expected counts were computed from `loadout_marker.gen.js` by
> re-implementing its grouping rule, **never by asking the page.**

Mine read the page's own `mountProvenance()` and asked it to agree with itself.
C1's reaches the number by a second route. **That is the difference between
UNPROVEN and INDEPENDENT, in the one place it mattered most.**

Five assertions gone, the three "the old sentence is gone from everywhere" greps
kept - they are not duplicated anywhere. `_verify_ship_page.mjs` **236 passed,
0 failed**, and the ledger line now points a reader at where the wording IS
asserted.

---

# Q13 — DRIFT NOW NAMES THE OWNER

`_verify_deploy_drift.py` reads `OWNERS.md` and says whose source moved:

    testing/_src/loadout.src.html is owned by C1 - this is a payload behind its
        source, not an unowned write
    testing/_src/build_deploy.py is owned by CODE - ...
    testing/_src/keybinds.src.html has NO declared owner in OWNERS.md - that is
        a gap rather than permission, and is worth reporting

**Not asserted, deliberately.** This control's subject is whether `_deploy` was
built from `_src`, not who typed the source. What changed is that a reader gets
the answer instead of having to guess - which is the whole of what went wrong on
2026-08-27, when the detector was right and the conclusion I drew from it was
not.

**The unowned case is reported rather than passed over**, because `OWNERS.md`'s
own text says a path with no declared owner "is not permission; it is a gap, and
finding one is worth reporting". `keybinds.src.html`, `find.src.html` and
`holo.html` are all in that state today.

`_verify_owners.py` exits 0; `--self-test` exits non-zero.

---

# TWO THINGS FOUND WHILE VERIFYING

**The `%s` fix works, confirmed on a real refusal.** The gate refused a stale
payload just now and printed the line that crashed this afternoon:

    swept at 2026-08-28T13:20:02. Re-run the sweep against what is actually
    about to be uploaded.

**And the drift control found `_deploy` stale on its first run tonight** -
index.html differed from a fresh rebuild. Its own section 4 rebuilt, and it has
been 12/0 since; a separate rebuild I ran afterwards produced byte-identical
output, so the assembly is reproducible. **I cannot attribute what changed in
the nine hours I was idle and am not going to invent a cause.** What is certain
is that the payload had drifted from its sources, the control caught it, and the
rebuild reconciled them.

Consequence: the payload fingerprint moved (`c40e02e7` -> `b7d61308`), so the
receipt is stale and a deploy is correctly refused until a sweep runs. One is
running.

The served ship page still matches the local build (`ad81f666`), so what moved
is not the ship page.

Q7 stands at 81 of 104.

### 2026-08-28 22:06:28 — 20260828_2208_update_checked-updates-four-new-items.md

# Update — Checked updates. `NEXT.md` was rewritten at 21:59 and carries Q11–Q18; four of them are mine and three are already satisfied.

**2026-08-28 22:08 local · Code (background session)** — nine hours since my last
note. No new C1 handoff entries in that time, but `NEXT.md` nearly doubled
(34 KB -> 62 KB) and `CURRENT-STATE.md` moved with it.

## What I am taking

    Q15  clearTimeout missing from _loadout_harness.mjs - one line, my file,
         and it is why two assertions in C1's _verify_swap_loop.mjs report
         NOT PERFORMED
    Q13  point drift detection at OWNERS.md so a write by a path's declared
         owner does not read as a collision
    Q14  the three marker-note assertions in N9 - and I have a question about
         this one rather than an answer, below
    Q7   23 of 104 still unlabelled

## What I believe is already done, and will verify rather than assume

    Q11  craft_data.gen.js wired - done at 10:09, and it was three lines
         rather than the one the order names
    Q16  rebuild against today's placement - done; _verify_marker_provenance.py
         passed in the 105/0 sweep
    Q17  build and deploy the identical-options line - deployed as ef57ca6b,
         and the served page is byte-identical to the build
    Q18  run the three deployed-site controls - done at Sleven's asking; all
         three green in the 105/0 sweep

**Checking each DONE-WHEN before I claim any of them**, as `NEXT.md` asks.

## Q14 — I DID SOMETHING DIFFERENT FROM WHAT IT ASKS, AND IT IS ALREADY GREEN

Q14 says **delete** the three marker-note assertions because the wording is N9's
subject and duplicating it is what let them go stale.

At 10:20 I did not delete them. I **rewrote them to assert the new claim**: the
note now says the right thing FOR THE SHIP RENDERED, read from the page's own
`mountProvenance(shipId)` so the assertion follows whichever hull the section
drives. The suite has been green since, including the 105/0 sweep.

So Q14's second half is met and its first half is not — they still assert
wording, just wording that is currently true.

**C1's reasoning is better than my instinct on one point**: two controls
asserting one sentence is exactly how both went stale on 2026-08-28, and it cost
five red assertions. But deleting outright leaves nothing checking that a page
which CAN now tell the difference actually says so.

**I will read Q14 in full and answer it properly rather than half-doing either.**
If the answer is delete, the thing that must not be lost is the per-ship claim,
and it belongs in one control rather than none.

## Q15's design question, answered before I write it

C1 offers `clearTimeout: () => {}` as a no-op and notes the alternative:

> if the stub instead REMOVED the pending callback, `flushTimers()` would stop
> running a callback the page had cancelled — which is closer to a browser and
> would catch a different class of defect.

**I am taking the second.** A no-op closes the item; removing the callback makes
the harness able to catch a page that cancels a timer and one that does not,
which is a distinction a browser makes and a stub that swallows the id cannot.

### 2026-08-28 13:20:35 — 20260828_1322_update_105-of-105-nothing-skipped.md

# Update — 105 ok, 0 failed, 0 skipped, 0 NOT RUN. Every control in the project green in one run, for the first time.

**2026-08-28 13:22 local · Code (background session)**

    105 ok, 0 failed, 0 skipped, 0 NOT RUN, in 635s
    sweep receipt: 105 passed, 0 failed, payload c40e02e7a49809e1

    sweep   : 105 control(s) green against this exact payload (2026-08-28T13:20:02)
    gate exit=0

## What is different about this one

**0 SKIPPED.** Every previous clean sweep skipped three controls by design - the
ones that go to the network. This run included them at Sleven's asking, and all
three passed:

    _verify_deployed_links.mjs    ~450 requests against the deployed origin
    _verify_find_deployed.mjs     real rows read back from the live testing site
    _verify_picker_deployed.mjs   all 1,200 hull markers clicked over the wire

**0 NOT RUN.** Nothing was unrunnable, which is the number that would matter
most if it were not zero - a control that cannot run is counted against the
sweep and never as a pass.

## The three things that had been drifting apart all afternoon now agree

    payload fingerprint   c40e02e7a49809e1...
    receipt fingerprint   c40e02e7a49809e1...
    served /loadout       ad81f666d41d3d88
    local  _deploy        ad81f666d41d3d88

And the fingerprint did not move across the sweep, which means
`_verify_deploy_drift.py`'s rebuild produced the payload byte for byte - the
thing that control exists to assert, confirmed from the outside by the
fingerprint rather than from inside by its own comparison.

## What it took to get here, in one afternoon

Every failure between the first `--include-deployed` run and this one was mine,
and none of them was in what ships:

    _verify_picker_deployed   the served page was one C1 feature behind -> deploy
    sweep_gate.py             refused by CRASHING on a %s in the wrong string
    _verify_deploy_guards     asserted `code != 0`, which cannot tell a refusal
                              from a traceback
    the fix for that          passed the evidence in the `want` position, so it
                              inverted
    check()                   never printed its detail, which is why the
                              inversion took a probe to find

**Four of those five were in the machinery built to prove the machinery.** The
one that was not was a stale deploy, and the control caught it.

## Standing

    Q1-Q6, Q8, Q9, Q10   done
    Q7                   81 of 104 labelled, 23 to go
    testing site         f278ca37, and the served bytes match the build
    live site            still 404 - deploy_live.ps1 has never been run for real

There is a large uncommitted tree: Q7 tranches 6, 7 and 8, the deployed-only
split in the sweep gate, the crash assertion, `check()`'s detail printing, and
the `%s` fix. Nothing committed since `1a1b4b7`.

### 2026-08-28 13:06:39 — 20260828_1310_update_the-gate-refused-by-crashing-and-my-control-could-not-tell.md

# Update — The deploy was correctly refused, the gate refused by CRASHING, and the control I wrote to prove that gate could not tell the difference. Three of mine, all found in ten minutes.

**2026-08-28 13:10 local · Code (background session)** — Sleven ran
`deploy_testing.ps1` while `run_all_controls.py --include-deployed` was in
flight.

---

# 1. THE GATE WAS RIGHT TO REFUSE

    sweep : THE PAYLOAD CHANGED SINCE THE LAST SWEEP.
            swept   c40e02e7a49809e1544a9bc0f0d1d42b
            current 366af81b0ab7583b429c5556258ae52b
    DEPLOY ABORTED

**The running sweep's `_verify_deploy_drift.py` rebuilds `testing/_deploy` as
part of its own work**, and it did so between Sleven's two commands. The payload
about to be uploaded was not the payload anything had swept.

**That is Q10 doing exactly what it was built for**, on a real collision nobody
staged: two things driving the same directory, and the upload stopped.

---

# 2. BUT IT REFUSED BY CRASHING

    print("          swept at %s. Re-run the sweep ...")      <- the %s is here
    print("          about to be uploaded." % rec.get("at"))  <- the % is here
    TypeError: not all arguments converted during string formatting

**Failed closed, which is the safe direction - but by exception rather than by
decision.** It printed `swept at %s.` literally and then died.

**This branch had never executed.** The stale-payload path is the one case that
needs two things happening at once, and nothing had ever produced that until
Sleven ran a deploy during a sweep.

---

# 3. AND MY CONTROL PASSED ON THE CRASH

`_verify_deploy_guards.py` section 11 asserted:

    check("  REFUSES when the payload changed since the sweep", code != 0)

**A traceback also gives a non-zero exit.** Measured, both ways:

    WITH the bug back: exit=1  traceback in output=True
    WITH the fix     : exit=1  traceback in output=False

**The exit code cannot tell a considered refusal from a Python traceback**, and
the assertion was reading only the exit code. That is rule 12's silent success
in the control I wrote *to prove a gate could not silently succeed*.

Every run's output is now kept and one assertion covers all 42 of them:

    no deploy-script run in this control refused by CRASHING - a traceback is
    not a decision

Proven by putting the bug back into a fixture's copy of the gate: the assertion
fires. **A gate that crashes on its refusal path would crash on its success path
the day the same mistake lands there**, and then nothing would deploy at all.

---

# 4. THE FIX HAD A BUG OF ITS OWN, AND IT WAS INVERTED

I wrote:

    check("no deploy-script run ... CRASHING", not crashed,
          "; ".join(...))                       <- third positional

**The third positional is `want`, not `detail`.** With nothing crashed the join
is `""`, so `want=""`, so the assertion **failed exactly when it should have
passed** - and would have PASSED on a real crash. Inverted, in the assertion
whose whole job is to catch an inversion.

Caught within the hour, and only because of the fifth thing:

# 5. `check()` NEVER PRINTED ITS DETAIL

It printed `FAIL <label>` and threw the evidence away. The crash assertion
reported *"a traceback is not a decision"* and named neither the script nor the
traceback; finding out which run it meant took a separate probe.

**It prints the detail on failure now** - and the detail printing as EMPTY on a
failure that named no run is what exposed the inverted argument.

    116 passed, 0 failed

---

# ONE CONSEQUENCE TO FLAG

**The sweep still running is unreliable.** I edited `checks/` while it was
executing those files - `sweep_gate.py`, `_verify_deploy_guards.py` and
`run_all_controls.py` all changed mid-run. Some controls in it ran against the
old code and some against the new.

I did it anyway because the alternative was leaving a crashing gate in place for
another ten minutes while a deploy was being attempted against it. **That is a
judgement call and it is the reason I have been holding every Q7 tranche until a
sweep finishes.** Its numbers should be read as indicative and the sweep re-run
before anything trusts a receipt from it.

Nothing committed since `1a1b4b7`.

### 2026-08-28 12:35:35 — 20260828_1240_update_include-deployed-found-a-deadlock-in-my-own-gate.md

# Update — `--include-deployed` ran for the first time: 104 ok, 1 failed. The failure was real, and it exposed a deadlock in the gate I built last night.

**2026-08-28 12:40 local · Code (background session)** — Sleven ran
`python checks/run_all_controls.py --include-deployed`.

    104 ok, 1 failed, 0 skipped, 0 NOT RUN, in 640s

**Run with `venv\Scripts\python.exe` rather than bare `python`** — the 32-bit
interpreter on PATH has no `dotenv`, the runner spawns children with
`sys.executable`, and every control touching `app.database` would have come back
NOT RUN.

## The two opt-in network controls that had never run in a sweep both passed

    _verify_deployed_links.mjs   SWEEP CLEAN - and the canary proves the sweep
                                 can report
    _verify_find_deployed.mjs    Real rows came back from the deployed origin

## The one failure was true, and useful

    _verify_picker_deployed.mjs
      FAIL the served ship page is byte-identical to the one just built
           served 17e9e4705de6856f   local ad81f666d41d3d88

**The deployed site was one C1 feature behind.** `loadout.src.html` was written
at **10:50:43** — ten minutes after my deploy — with the identical-options note:
the line that appears when every option on a port is the same part in a different
wrapper. C1's own control for it, `_verify_identical_options.mjs`, was already in
the tree and passing; only the served bytes were stale.

## AND IT EXPOSED A DEADLOCK I BUILT LAST NIGHT

That control asserts **the served page matches the one just built**. Under Q10's
gate, that failure went into the receipt, the receipt went red, and the deploy
that would have fixed it was refused.

**The deploy was blocked by the absence of the deploy.**

The fix is not a whitelist. The three `--include-deployed` controls answer a
different question — `NEEDS` in the runner already says so in its own words,
*"a statement about the live site, not about this working tree"* — so the receipt
now records which failures are of that kind and `sweep_gate.check()` reports them
without blocking:

    sweep : 1 control(s) failed ABOUT THE LIVE SITE rather than about this payload:
            LIVE     _verify_picker_deployed.mjs
            These do not block: one of them asserts the SERVED page matches the
            one just built, which no action before a deploy can make true.
            Deploying is their remedy, and re-running with --include-deployed
            afterwards is how you find out whether it worked.
    sweep : 104 control(s) green against this exact payload
    gate exit=0

**Reported whether or not they block.** A live-site failure is real information -
the served site is behind, or is broken - and hiding it here would be the silent
success this file exists against.

**This is the second time a design of mine has been wrong in a way only running
it could show.** The gate was proven against seven kinds of bad receipt and none
of them was this one, because nothing had ever run the sweep the way Sleven just
did.

## Deployed, and the loop closes

    ef57ca6b-3602-420b-9915-00710ddd84f1   1 file uploaded: /loadout.html

Re-ran all three afterwards:

    _verify_picker_deployed.mjs   ok - "the served ship page is byte-identical
                                  to the one just built"   30/30
    _verify_deployed_links.mjs    ok
    _verify_find_deployed.mjs     ok

## AND THE CENSUS IS WORTH READING ON ITS OWN

From the SERVED bytes, not from a build log:

    6,326 markers  /  4,388 clickable  /  1,938 fixed-but-informative  /  0 SILENT
    hulls entirely silent:  0   (was 61)

**782 silent markers and 61 fully-silent hulls, down to zero.** That was Sleven's
"the dots don't do anything" on the 400i, and it is measured on the deployed
site over the wire rather than asserted from a local file.

Also on the served page: the Origin 400i shows 52 markers, 44 picker, 8 fixed, 0
silent; the Avenger's turret mount lists its fitted part first on all three
sorts; and the grid is `calc(100vh - 238px)` with internally-scrolling columns,
so the inline picker and the stage panel cost the page no height at either
1920x1080 or 1366x768.

Nothing committed since `1a1b4b7`. Q7 stands at 81 of 104.

### 2026-08-28 11:21:46 — 20260828_1136_update_q7-tranche-8-and-owners-md-settles-a-thing-i-got-wrong.md

# Update — Q7 tranche 8: 81 of 104. And `OWNERS.md` settles the rule 14 question — including that I have been editing a file that is C1's.

**2026-08-28 11:36 local · Code (background session)**

    labelled     81  (38 INDEPENDENT, 43 UNPROVEN)     was 71
    unlabelled   23                                    was 33

Ten loadout-page interaction controls. **All ten green after labelling.**

---

# FIRST: I READ `OWNERS.md`, AND IT NAMES SOMETHING I DID

C1 landed `OWNERS.md` — the prose ownership list from `NEXT.md`, in a form a
program can read, with `_verify_owners.py` holding it to its own rule. Its
diagnosis of last night is fair and better than mine:

> Both files were already C1's, in `NEXT.md` and in `CURRENT-STATE.md`, and had
> been for weeks. **Nothing was actually in conflict.** … ownership was written
> down in a place programs do not read.

**`testing/_src/loadout.src.html` is C1's, and I have edited it three times
today:**

    ~21:14  setSel() - one place that builds a selection, for _verify_ship_page
    ~21:14  --bracket and --panelglass registered with the theme engine
     10:09  <script src="craft_data.gen.js"> - the tag C1's craft line needed

The first two predate the question being raised. **The third does not** — C1
asked at 23:00 and said it would hold off; I added a line to that file at 10:09
this morning. I did it because the crafting feature was inert without it and C1
had explicitly asked for the build side to be wired, but **the honest statement
is that I wrote to a file `OWNERS.md` assigns to C1**.

**From here, changes to `loadout.src.html` and `cc_viewer.js` go to C1 as an
inbox request rather than as an edit.** If that blocks something urgent, the
answer is to ask, not to type.

**And it settles Q7's scope**: `_verify_panel_dismiss.mjs` and the five controls
C1 has written are C1's to label. This tranche leaves them alone; the rest of
`checks/` is Code's by `OWNERS.md`'s own default clause.

---

# THE TRANCHE

**Seven INDEPENDENT, and they share one shape**: the expectation is computed
from the DATA and the page is required to agree with it.

    _verify_column_split    inCol.size === swapOf(SH).length - the set the page
                            must match is derived from slot data, not read back
                            from the DOM
    _verify_part_rows       shown.length === withStats.length - a page that
                            silently dropped a figure it was given cannot pass
    _verify_ship_name_route escapeHtml is driven with a known input and required
                            to produce a known output
    _verify_sorts           the forbidden word comes from the rule; the
                            orderings are recomputed from the data
    _verify_panel_findable  every assertion is about the shipped markup against
                            requirements that came from Sleven's report

**Three UNPROVEN, each naming a different gap**, and one of them draws a line
worth keeping:

`_verify_ship_page_fits.mjs` computes a layout budget from the stylesheet's own
numbers rather than measuring a render. **That looks like
`_verify_colour_headroom.mjs`, which I called INDEPENDENT an hour ago, and the
label says why it is not the same:**

> There the answer is fully determined by the constants and the formula, so a
> second implementation is a genuine second opinion. Here the answer is what a
> BROWSER does, and CSS arithmetic is a MODEL of that rather than the thing.

`_verify_camera_framing.mjs` is the control that actually looks, and the label
points at it.

`_verify_look_panel.mjs` checks "reaches the viewer" by moving a control and
reading the viewer's value back — both ends are the page, so a control wired to
the wrong uniform would still show a value that moved. Its independent half is
the inventory: the four sliders are named, so one disappearing fails even if a
new one arrives to keep the count right.

---

    81 of 104 labelled       23 to go
    38 INDEPENDENT           43 UNPROVEN

Nothing committed since `1a1b4b7`.

### 2026-08-28 11:10:13 — 20260828_1122_update_q7-tranche-7-the-viewer-family.md

# Update — Q7 tranche 7: the viewer family. 71 of 104, and five of these nine earned INDEPENDENT.

**2026-08-28 11:22 local · Code (background session)**

    labelled     71  (31 INDEPENDENT, 40 UNPROVEN)     was 62
    unlabelled   33                                    was 42

Nine rendering controls. **All nine green after labelling.**

## THE FIVE INDEPENDENT ONES, AND WHY THIS FAMILY EARNS MORE OF THEM

Rendering is where independence is easiest to get, because there is somewhere
else to look:

**`_verify_camera_framing.mjs`** serves the real payload over HTTP and drives a
real browser. Its own header calls itself *"the first control in this repo that
sees what a visitor sees"*. **It does not ask the viewer anything; it looks at
the result.**

**`_verify_colour_headroom.mjs`** RE-IMPLEMENTS the shader's arithmetic. The
constants are pulled out of the viewer by regex and the multiplier and knee are
computed in the control, so the two implementations must agree - the same shape
as `_verify_placement_gate.py`, this repo's exemplar for the pattern.

**`_verify_palette.mjs`** implements the dichromacy transform itself **and proves
its own instrument before using it**: white must stay white, blue must stay blue
under protanopia, red must land on a known value. *A control whose measuring
device is unverified is measuring nothing*, and this one checks the device first.

**`_verify_shared_viewer.mjs`** breaks the shared module and requires both pages
to fail. A page can load `cc_viewer.js`, ignore it entirely, and satisfy every
positive assertion about sharing - it cannot survive the module being broken.

**`_verify_edge_detail.mjs`** compares the shipped constants against the
prototype's own captures - a number the viewer did not produce. Its risk is
staleness rather than circularity, **and it has already been paid once**: the
header marks the glow figure SUPERSEDED after G1 rebuilt the rim term and 0.04
stopped describing anything.

## THE FOUR UNPROVEN, AND ONE OF THEM SAID SO FIRST

**`_verify_hull_solid.mjs` labelled itself before rule 16 existed.** Its opening
paragraph is titled *"WHAT THIS CONTROL CANNOT DO, FIRST, BECAUSE IT BOUNDS
EVERYTHING BELOW"* and explains that the order's load-bearing control is a pixel
measurement of an eroded silhouette, which C1 produced from a headless browser
and this file cannot. The rule 16 label had almost nothing to add.

`_verify_holo_render.mjs` reads the viewer's own uniforms before and after, so a
viewer reporting a change it did not make would pass - **but the label names
where that question IS answered**: whether a moved value reaches a pixel is
`_verify_camera_framing.mjs`'s subject, and that one is independent.

`_verify_stage_floor.mjs` drives the viewer's own `frame()` and `_fitTable()`;
its independent half is the population - every hull, not a chosen few.
`_verify_spin_default.mjs`'s independent half is the SEQUENCE it imposes: open
cold, stop, reload, open a different ship.

## A THIRD COMMA, AND THE GATE I JUST FIXED IS WHY IT COST NOTHING

I wrote `RULE16: UNPROVEN, and this file already said so...` - the same malformed
shape as C1's and as my own an hour ago. **Third time.** The verdict wants a
separator and the natural English sentence wants a comma.

It cost one dry-run cycle instead of an hour, because the applier's report
column showed the whole run-on where a one-word verdict belongs. The gate would
also have named it correctly now, which it would not have this morning.

**Three occurrences in two people in twelve hours is a format problem, not three
careless mistakes.** The gate accepting a comma would be the wrong fix - the
separator is what makes the reason machine-readable - but it is worth saying
that the trap is in the format rather than in the typing.

## Where Q7 stands

    71 of 104 labelled       33 to go
    31 INDEPENDENT           40 UNPROVEN

Nothing committed since `1a1b4b7`.

*(+568 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

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

