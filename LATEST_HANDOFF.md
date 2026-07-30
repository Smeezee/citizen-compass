# LATEST_HANDOFF.md — Update #10 — 2026-07-30 2:06 AM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-07-30 02:06:17 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35.0/100
- Data completeness: 0.0%
- Viewer progress: 50.0%
- Documentation: 100.0%

**Ships:** 2 complete viewers / 4 total (50.0%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 7 files (0.27 MB)

**Scripts:** 13  |  **3D models:** 241  |  **Docs:** 223

---

## RECENT UPDATES (append-only, newest first)

### 2026-07-30 02:06:10 — update_overnight_queue_complete.md

# UPDATE — Overnight queue complete: real-DB status, CRUD API, auditor, E2E harness, viewer wired (2026-07-30, continued)

Full run of the approved overnight queue (Postgres real-DB proof, generic CRUD API,
data-integrity auditor, E2E test harness, Aquila/Gladius investigation), plus the two
mid-run corrections (real-DB downgrade restricted to disposable clones; don't rebuild
the already-existing viewer scaffolding). Addendum batch #2 (Cutlass Black fix + broader
auditor/checker rollout) was explicitly told to wait until this reported done here — it
has NOT been started yet, see "Next" at the bottom.

## Step 1 — Real database proof: BLOCKED, confirmed with a real network test, not skipped

The queue's premise was "`.env` has `DATABASE_URL` set, so you have direct access this
time." Tested it directly before touching anything: a raw TCP connect from the device
bridge to `127.0.0.1:5432` returned `Connection refused`, and a connect to `8.8.8.8:53`
(open internet) returned `Network is unreachable`. This is the same platform limitation
as last session, now re-confirmed with an actual test rather than assumed. Neither the
device bridge nor this cloud sandbox can reach your real local Postgres or the internet
at your machine at all.

**Consequence:** `alembic upgrade head` / `import_ship_components.py` have still never
been run against your real `citizen_compass` database. Everything below was validated
against a scratch Postgres in my own cloud sandbox (as last session), never your real DB.

**Your exact next step to close this out** (2 commands, once you're at a terminal with
real DB access):
```
alembic upgrade head
python import_ship_components.py
```
Take a backup first since you now have real access and I don't:
```
pg_dump -Fc citizen_compass > citizen_compass_backup_$(date +%Y%m%d).dump
```
Restore procedure if ever needed: `pg_restore -d citizen_compass --clean citizen_compass_backup_<date>.dump`
(only ever needed if something goes wrong - the migration is additive, it doesn't touch
existing tables).

## Step 2 — Generic CRUD/router-factory: DONE, real code committed, tested in scratch

Per `docs/ARCHITECTURE_DECISIONS.md` section 3 (LOCKED). New files:
- `app/routers/component_factory.py` - owns pagination, deterministic ordering,
  the 4 universal filters (manufacturer/size/grade/confidence), the `Page` envelope,
  id-or-class_name detail lookup with a real 404.
- `app/routers/weapons.py`, `missiles.py`, `turrets.py` - thin per-category wrappers
  with their own real, named, documented FastAPI query params for category-specific
  filters (damage_type/fire_mode, guidance_type, manned).
- `app/schemas.py` - added `Page[T]`, `ComponentBaseOut`, `WeaponOut`, `MissileOut`,
  `TurretOut` (1:1 mirror of actual model columns, no speculative fields).
- `app/main.py` - wired the 3 new routers in.

Endpoints live: `GET/{identifier} for /api/v1/weapons`, `/api/v1/missiles`, `/api/v1/turrets`.

**Real bug found by actually running it, not just import-checking:** `Component` had no
`verified_patch` relationship at all (only the raw `last_verified_patch` FK column) -
`Ship` has the equivalent relationship, this one was just missing. Crashed every
serializer the first time they ran against real data. Fixed in `app/models.py`, with a
regression test.

**Deliberately NOT done:** did not retrofit the new `Page`/pagination envelope onto the
existing `/api/v1/ships`, `/api/v1/dealers`, `/api/v1/manufacturers` endpoints, even
though the architecture doc mentions eventually doing so - that's already-live behavior
outside tonight's explicit scope. **Flagging this for your call**, not deciding it
myself: do you want those three retrofitted to the same envelope, and if so, on what
timeline (it's a breaking response-shape change for anything already consuming them)?

**Tests:** `tests/test_component_routers.py` (17 tests: envelope shape, category
isolation, deterministic ordering, pagination bounds, all filter types, 404s including
cross-category and huge-integer identifiers, 422 validation, existing endpoints
unaffected, OpenAPI). All passing against scratch Postgres.

## Step 3 — Data-integrity auditor: DONE, real code committed, tested in scratch

`audit_ship_components.py`. Findings-only (never repairs data), per
`docs/ARCHITECTURE_DECISIONS.md` section 4 (LOCKED). Checks source-vs-processed-vs-DB
coverage, relational integrity (broken FKs, cross-category detail mismatches, missing
detail rows, duplicate natural keys, invalid confidence/size values), and re-runs the
importer twice to catch drift. Every finding is exactly one of `DEFECT` / `WARNING` /
`LIMITATION` / `PASS`. Outputs both JSON and a human-readable .txt to `logs/` (gitignored
- only the script is committed).

**Real result against the actual imported Arrow data:** 0 DEFECTs, 5 LIMITATIONs (all
expected: unresolved manufacturer prefixes GATS/FSKI/TALN, partial port-tree coverage -
8 of 53 port entries imported so far, by design per the staged-pipeline decision), 2
PASSes.

**Tests:** `tests/test_audit_ship_components.py` - verifies the auditor actually flags
an injected cross-category-detail-mismatch and a missing-detail-row as DEFECTs, and
does NOT flag a well-formed component. (A findings-only tool that never finds anything
real is worse than useless - it looks like a safety net that isn't one.)

## Step 4 — E2E test harness: DONE, real code committed, passes clean

`run_e2e_test.py`. Creates its own throwaway Postgres database (name derived from
whatever `DATABASE_URL` is configured, credentials never hardcoded - so this can't
silently target the wrong server when it's eventually run in your real environment),
applies all migrations, seeds a small deterministic 5-category fixture (independent of
the real Arrow data), runs the auditor, exercises 8 representative endpoint calls via
FastAPI's TestClient, re-seeds to prove idempotency, downgrades to base and back to head
to prove reversibility, runs `alembic check`, drops the database. **Full run passed
clean this session.**

This is also where tonight's addendum #1 correction now lives structurally: destructive
migration testing (downgrade/re-upgrade) only ever happens against this disposable
per-run database going forward - never the real one, and it never did this session
anyway since the real DB was unreachable.

`requirements-dev.txt` added (pytest, httpx) - separate from `requirements.txt` so
Railway's production install doesn't pull test tooling.

## Step 5 — Viewer parity + Aquila/Gladius: DONE (parity), investigated + honestly blocked (data)

**Viewer parity (per the mid-run addendum):** confirmed `64f2ee6`'s shared module
(`tests/testing-site/shared/hardpoint-viewer.js`) already existed - did not rebuild it.
Verified real behavioral parity before wiring it in, using headless Chromium
(Playwright, available in my sandbox) with mouse coordinates computed from the actual
camera projection matrix - a genuine simulated user interaction, not a code-reading
guess. Compared hover-highlight, click-to-open popup, rack-configuration swap,
missile-total recompute, and the turret/gun popup path field-by-field between the
original inline-script Arrow page and a copy wired to the shared module.

**This caught 2 real regressions** from the original extraction: two hardcoded
provenance-note strings had been reworded - one silently dropped
"(arrow_api_raw.json)", the other dropped a trailing sentence about buy-location data.
Fixed both; while fixing the first, also generalized it (`rackSourceLabel` option
instead of a hardcoded Arrow filename - a "shared" module hardcoding one ship's
filename would have been wrong for the next ship). Re-ran the full comparison after the
fix: **PARITY CONFIRMED**, zero differences, zero console errors either page. Wired the
shared module into `arrow/index.html` for real (commit `367ea74`) - HTML/CSS unchanged,
only the ~230-line inline scene script replaced with a ~20-line call into the engine.

**Aquila/Gladius real data:** confirmed (again) neither ship has any raw port-tree data.
Investigated the source: `arrow_api_raw.json`'s own embedded metadata reveals exactly
where Arrow's data came from - `api.star-citizen.wiki`, resource type "vehicle", the
open-source `StarCitizenWiki/API` project (confirmed via `WebSearch`, which works fine
in this session). The URL pattern is `https://api.star-citizen.wiki/api/vehicles/{slug}`
(Arrow's slug: `anvl-arrow`) - likely slugs for the other two are `aegs-gladius` and
something like `crus-constellation-aquila`, not yet confirmed.

**Real, precise blocker (not a data-sourcing question, a tool-availability one):**
`WebFetch` itself requires a live per-request approval prompt in this session that
nobody was there to answer - tried 3 times against 2 different domains
(`api.star-citizen.wiki` and `starcitizen.tools`), all timed out identically. This isn't
domain-specific and isn't something more retries would fix. **This needs you present**:
either (a) approve the `WebFetch` prompt once when you're at the session live so I can
pull both ships' data the same way Arrow's was pulled, or (b) you pull
`https://api.star-citizen.wiki/api/vehicles/aegs-gladius` and the Aquila's equivalent
yourself (browser or curl) and drop the JSON into `data-layer/raw/<ship>/`, same
convention as Arrow - either path, no data was invented in the meantime.

## Commits this run (all local, none pushed)

```
367ea74 Wire shared hardpoint-viewer engine into Arrow, verified byte-for-byte
2515fc8 Add Ship Items data-integrity auditor + isolated E2E test harness
3fcd75f Add generic CRUD router factory for Ship Items (weapons/missiles/turrets)
```
(on top of the 11 commits already local from earlier tonight). **14 commits ahead of
`origin/main` now, still all local** - flagging again since it's been sitting a while,
not something I'll push without you saying so.

`git status`: clean working tree.

One cosmetic note: the router-factory commit's message has a small gap where a
backtick-quoted phrase got eaten by an unescaped-backtick shell quoting mistake on my
end (bash command substitution) - message reads "Component had no relationship at all"
instead of "no `verified_patch` relationship". Content is otherwise intact and not
misleading; didn't amend it since amending isn't something I do without you asking.

## Test results summary

23 pytest tests, all passing (17 router tests + 3 auditor tests + 3 schema/importer
regression tests) - against scratch Postgres, not your real DB (see Step 1). Full
`run_e2e_test.py` pass: clean. Auditor run against real imported Arrow data: 0 defects.

## Decisions that need you

1. Should `/api/v1/ships`, `/dealers`, `/manufacturers` get retrofitted to the new
   `Page` envelope (the architecture doc mentions it eventually)? Left alone tonight,
   your call on timing since it's a breaking shape change.
2. `ARCHITECTURE_DEEP_REVIEW.md` scope question - still untouched, exactly as flagged,
   not decided by me.
3. Aquila/Gladius real data - needs you present for one `WebFetch` approval, or a
   manual pull, per Step 5 above.

## Next / addendum #2 status

Addendum #2 (Cutlass Black slug/label/turret-size/rack-data fix + broader
auditor/checker rollout across data-integrity, ops-health, security, code-quality,
external-reachability categories) was received mid-run with explicit instructions to
**hold until this queue reported done here** - which is now. **Not started yet.** Will
begin it next, working in the same small-validated-stages/git-lock-workaround pattern,
starting with the Cutlass Black fix (needs the same real-source-data verification
approach as Arrow for the turret-size question - same `WebFetch` limitation above may
apply there too, will report honestly if so rather than guess S5 from the unverified
note).

### 2026-07-29 21:47:41 — update_audit_complete.md

# UPDATE — Full audit queue closed out (2026-07-30)

All items from the 2026-07-29 "exact next step to resume from" list are now resolved:

1. ~~Run setup_watcher_task.ps1~~ — done (twice; first pass had a bug, fixed, second pass succeeded).
2. ~~Confirm it registers and starts~~ — confirmed both times via log.
3. ~~Re-test auto-restart for real~~ — confirmed: killed `inbox_watcher.exe`, it came back on its own within ~1 minute (fresh full re-init in the log at 21:45:19 after being killed post-21:41:20 start). Required a real bug fix first — see `update_watcher_autorestart_bug_and_fix.md` / `update_watcher_autorestart_confirmed.md` in this archive.
4. ~~Confirm schema-init/registry-builder stay on-demand~~ — confirmed by reading their actual Go source: both are plain single-run `main()` functions, no loops/tickers/schedulers. Only one Task Scheduler entry exists on the machine (the watcher itself).
5. ~~Confirm CLAUDE.md headless-operation standing rule is in place~~ — confirmed: the "keep LATEST_HANDOFF.md current, always" rule in CLAUDE.md is written to cover unattended/headless operation specifically (denied permissions, idle stops, section completions), not just interactive sessions.

Phase 1 wrap-up is done. Next natural step per the 2026-07-29 handoff notes: move on to Phase 3 (per PHASE2_VISION.md), or pick up the queued "AI Brain" knowledge-base project per the 2026-07-30 documentation-system decision — Sleven's call on which to prioritize.

### 2026-07-29 21:46:13 — update_watcher_autorestart_confirmed.md

# UPDATE — Auto-restart fix CONFIRMED working (2026-07-30)

## Result
The Daily-trigger-with-repetition fix works. Live test:
- Sleven re-ran `setup_watcher_task.ps1` (fixed version) — registered successfully, no XML error this time (previous attempt failed with "Duration:PT0S ... incorrectly formatted or out of range" from trying to use `[TimeSpan]::Zero` as an "indefinite" sentinel — reverted that piece to the original 10-year finite duration, kept the Daily-trigger-instead-of-AtLogOn fix).
- Watcher started 21:41:20.
- Sleven ended `inbox_watcher.exe` via Task Manager.
- Confirmed via `logs/inbox_watcher.log` (read directly through the device-side mount, bypassing a stale-cache issue in the file-staging bridge): a fresh "Watcher started (Go)" sequence at 21:45:19 — full re-init (protected folders reloaded, etc.), not a stale/limping process. Came back on its own within ~1 minute of being killed.

## Status: this closes out the watcher self-healing item from the 2026-07-29 handoff.

## Remaining from the original audit queue
1. Confirm `schema-init`/`registry-builder` stay on-demand tools (not continuously running) — not yet checked this session.
2. Confirm the CLAUDE.md headless-operation standing rule is in place — CLAUDE.md already read this session; it does contain the "keep LATEST_HANDOFF.md current" standing rule. Worth a final check of whether anything else was meant by "headless-operation standing rule" specifically.
3. "AI Brain" numbered-folder knowledge base — queued as a future project per 2026-07-30 decision, not urgent.

## Note for future sessions
Reading files through the file-staging bridge (`device_stage_files` + Read/Bash) can silently return stale cached content for a path that's been staged before, even when the tool reports updated size/mtime. Workaround: use `device_bash` to `cat`/`tail` the file directly from its mount at `/sessions/<session-id>/mnt/<folder-name>/...` — that reads live, no cache issue.

### 2026-07-29 21:41:23 — update_watcher_autorestart_bug_and_fix.md

# UPDATE — Auto-restart bug found and fixed (2026-07-30)

## Bug
`setup_watcher_task.ps1` registered successfully and the watcher started fine, but the self-healing behavior did not actually work: killed `inbox_watcher.exe` via Task Manager, waited well past 90 seconds, it did not come back. Confirmed via Task Manager (no matching process) — not just a slow log read.

## Root cause (best diagnosis — could not get full Task Scheduler UI confirmation; its window would not accept clicks through the computer-use bridge, likely running at a different privilege level)
The previous trigger design attached a 1-minute repetition pattern directly to an `AtLogOn` trigger (`$trigger.Repetition = $repeatingOnce.Repetition` on a trigger created via `-AtLogOn`). `AtLogOn` is an event-based trigger with no fixed clock StartBoundary of its own. Repetition patterns combined with event-based triggers (AtLogOn/AtStartup) are a widely-reported unreliable combination in Windows Task Scheduler — the engine's repetition polling is anchored to a trigger's StartBoundary, which event triggers don't meaningfully have outside the moment the event fires once.

Also worth noting for the record: the previous `RepetitionDuration (New-TimeSpan -Days 3650)` was a large but *finite* duration, not the documented "indefinite" sentinel (`[TimeSpan]::Zero`). Not believed to be today's actual failure (10 years hasn't elapsed), but corrected anyway since it's the technically correct way to express "repeat forever."

## Fix applied
Rewrote the trigger section of `setup_watcher_task.ps1`:
- New primary trigger: `New-ScheduledTaskTrigger -Daily -At (Get-Date)` — a genuine calendar-based trigger with a real StartBoundary the engine actively polls.
- Repetition attached to that Daily trigger: 1-minute interval, `RepetitionDuration = [TimeSpan]::Zero` (the documented "repeat indefinitely" sentinel).
- Kept `AtLogOn` as a second trigger in the same task (array of two triggers), purely so it also comes up immediately on reboot instead of waiting up to a minute for the first repeat tick.
- Everything else in the script (admin elevation check, exe path check, RestartCount/RestartInterval settings, IgnoreNew, description) left unchanged.

Delivered the updated script directly onto Sleven's machine (overwriting the old `setup_watcher_task.ps1`), per his explicit standing instruction that Claude should always attempt the actual work itself before asking him to do anything manually.

## Still needs
Sleven to re-run the updated `setup_watcher_task.ps1` (right-click → Run with PowerShell → Yes on UAC) so the corrected trigger gets registered, then re-test: kill `inbox_watcher.exe`, wait ~90s, confirm it comes back on its own this time.

### 2026-07-29 21:23:59 — update_power_outage_checkpoint.md

# UPDATE

Emergency checkpoint before possible power outage. Everything below is
confirmed stable — no process running, no file mid-write.

**Verified complete this session:**
- Phase 1: ship ID registry (295 ships in Postgres `ship_registry` table +
  `data-layer/ship_registry.json` export), shared `pipeline_check_results`
  table (verified via fresh independent query: 7 columns, correct types,
  both indexes, 0 rows as expected), `pkg/pipelinelog` + `pkg/pgconn` shared
  Go packages, watcher retrofitted to use `logs/inbox_watcher.log`.
- Fixed real bug: `tesseract.exe` OCR subprocess call in
  `watcher-go/ocr.go` had no `HideWindow` flag, which would flash a visible
  console window since the parent watcher has none. Fixed with
  `cmd.SysProcAttr = &syscall.SysProcAttr{HideWindow: true}`.
- Rebuilt release binary with the fix, copied to
  `C:\Users\david\citizen-compass\inbox_watcher.exe` — confirmed on disk,
  matches `watcher-go\inbox_watcher_release.exe` exactly (same size/timestamp).

**Verified NOT working, root-caused, fix prepared but NOT YET APPLIED:**
- Task Scheduler's `RestartCount`/`RestartInterval` auto-restart was tested
  empirically (killed the tracked process, waited 2.5+ minutes past the
  1-minute interval) — confirmed it does NOT recover the watcher on its own.
  `Last Result: 1`, `Next Run Time: N/A` after the kill.
- Root cause: this mechanism is unreliable for a process that's externally
  terminated/crashes outright, rather than exiting through its own normal
  completion path.
- Fix already written into `C:\Users\david\citizen-compass\setup_watcher_task.ps1`:
  adds a 1-minute repetition trigger (on top of "at logon") combined with
  `MultipleInstances=IgnoreNew`, so Task Scheduler itself re-attempts to
  start the task every minute forever — a no-op while already running,
  self-healing within a minute if it's ever down.
- **This script has NOT been run yet** — I cannot self-elevate (no
  interactive UAC access). It needs to be run manually (double-click,
  accept the UAC prompt) to actually take effect.

**Exact next step to resume from:**
1. Run `C:\Users\david\citizen-compass\setup_watcher_task.ps1` (double-click,
   accept the Administrator prompt).
2. Confirm the task re-registers and starts (script prints the tail of
   `logs\inbox_watcher.log`, should show "Watcher started (Go)").
3. Re-run the empirical auto-restart test: kill the tracked
   `inbox_watcher.exe` PID via `taskkill /PID <pid> /F`, wait ~90 seconds,
   confirm a new instance appears on its own and Task Scheduler shows
   `Status: Running` again.
4. Once confirmed, finish the remaining audit items: confirm `schema-init`
   and `registry-builder` are correctly left as on-demand (not
   continuously-running) tools per the new CLAUDE.md rule, and add that
   rule to CLAUDE.md if not already there.

Nothing else was in progress. Safe to stop here.

### 2026-07-29 19:05:05 — update_phase1_progress.md

# UPDATE

Phase 1 progress checkpoint.

**Completed and verified:**
- Ship ID registry: built (`registry-builder`), dry-run tested against the real
  `citizen_compass` Postgres DB, then run for real — all 295 ships from
  `ship_specs.json` registered with permanent codes (manufacturer + sequential
  number). Confirmed idempotent on re-run (0 new added, 295 already registered).
  Exported to `data-layer/ship_registry.json`. Manufacturer-code edge cases
  (Mirai vs MISC collision, Banu Souli mis-tagged Argo ships) resolved by
  coding from actual manufacturer name, not legacy class-name prefix, per
  your decision.
- Shared Go packages: `pkg/pipelinelog` (standardized `logs/<tool>.log`
  logging, one file per tool) and `pkg/pgconn` (shared Postgres connection
  boilerplate: find project root, read `.env`, connect) — both built, both
  used by `registry-builder` and `schema-init`.
- `watcher-go` retrofitted to use `pkg/pipelinelog` instead of its own inline
  logger — built and scratch-tested successfully.

**In progress / blocked:**
- `schema-init` (creates the shared `pipeline_check_results` table) is built
  and compiles, but the actual run against the real database was interrupted
  by a denied tool permission before it executed. Not yet confirmed against
  the real DB.
- The retrofitted watcher (using `pkg/pipelinelog`) has **not yet been
  redeployed** to the real project — the currently-running `inbox_watcher.exe`
  is still the pre-retrofit build, still logging to `pipeline_log.txt` at
  root rather than `logs/inbox_watcher.log`.

**Next steps:** run `schema-init` for real, redeploy the retrofitted watcher,
then continue Phase 1 wrap-up before moving to Phase 3.

---

## PROJECT NOTES (from most recent full handoff doc)

# UPDATE — Ship Items schema + importer shipped, viewer generalization scoped (2026-07-30, overnight)

Resumed from the 2026-07-29 handoff's three open items. Sleven was asleep; proceeded on
judgment per his standing instruction, did not decide the one item he flagged as his call.

## 1. Postgres schema + importer for weapons/missiles/turrets (PRIMARY — done, locally verified)

Built the "Ship Items" domain locked in `docs/ARCHITECTURE_DECISIONS.md` (Class Table
Inheritance): `component_types` lookup table + `components` base table + 5 typed detail
tables (`weapon_details`, `missile_details`, `missile_rack_details`, `gimbal_mount_details`,
`turret_details`), all wired to the existing `VerifiableMixin` provenance pattern
(verification_source/confidence).

- `app/models.py` — new `ComponentType`, `Component`, `WeaponDetail`, `MissileDetail`,
  `MissileRackDetail`, `GimbalMountDetail`, `TurretDetail` classes.
- `alembic/versions/219446ebce6a_*.py` — migration creating all 6 new tables + indexes,
  seeding `component_types` with the 5 categories.
- `import_ship_components.py` — hand-curated importer (per the "2-3 real importers before
  generalizing" staged-pipeline decision), populating 8 real Arrow components sourced from
  `data-layer/raw/arrow/arrow_api_raw.json`'s actual port tree, cross-checked against
  `docs/HARDPOINT_MOUNT_TYPES.md`. Upserts on `class_name`, idempotent on re-run.
- Commit: `bf22494`.

**Honesty note on verification:** all of this was tested against a scratch PostgreSQL
instance in my own cloud sandbox (upgrade/downgrade/re-upgrade cycle, `alembic check` clean,
importer dry-run + real + re-run, full `app.main` import with routers still boots clean). It
has **NOT** been run against the real project database — this session's tools can't reach
`localhost:5432` on your machine from the cloud container, and the device bridge has no
network access at all. First real run against your actual dev DB is the first thing to do
when you're back: `alembic upgrade head` then `python import_ship_components.py`. Read the
importer's inline notes before trusting it blind — 3 manufacturer prefixes (GATS, FSKI,
TALN) and a couple of stat fields were deliberately left `None` because I couldn't confidently
identify them, not because they don't matter.

## 2. Viewer pattern generalization (SECONDARY — scoped down, real blocker found)

Checked `constellation-aquila` and `gladius` before touching anything: neither has a
`hardpoints.json`, and `data-layer/raw/` only has `arrow` and `misc` — there is no raw
port-tree data for either ship. Wiring the Arrow's hover/rack-selector pattern into them
tonight would mean inventing hardpoint positions, which is exactly the kind of guess this
project's evidence standard rules out. Did not do that.

What I did instead: extracted the reusable engine (scene setup, hover/click raycasting,
rack-config popup, missile-total calculator) out of `arrow/index.html` into
`tests/testing-site/shared/hardpoint-viewer.js` (`createHardpointViewer()`, parameterized).
Commit: `64f2ee6`.

**Deliberately left undone, for good reason:** did NOT wire this into `arrow/index.html`
itself, and did NOT touch that file at all. This session has no way to render WebGL or take
a screenshot to visually confirm the swap is behaviorally identical — the working Arrow demo
was judged not worth risking on a blind refactor. `arrow/index.html` is untouched and still
the known-good reference.

**Real next step for this task** (not done tonight, needs you or a session with browser
verification): (a) wire the shared module into `arrow/index.html`, look at it in a browser,
confirm parity; (b) pull real port-tree data for constellation-aquila and gladius the same
way it was done for the Arrow (their raw API pull → `data-layer/raw/<ship>/`), then the
shared engine can actually be used on them.

## 3. ARCHITECTURE_DEEP_REVIEW.md scope question

Left exactly as flagged, per explicit instruction. Not touched, not decided.

## Also worth knowing

- 9 commits are now sitting local-only, ahead of `origin/main` (was 8, +1 tonight). Not
  pushed — wasn't asked to, flagging again since it's been sitting a while.
- Could not confirm whether `inbox_watcher.exe` is currently running from this session (no
  Windows process/task-scheduler visibility from the device bridge) — if it's down, this
  update file will just sit in `inbox/` until it's restarted; check `logs/inbox_watcher.log`
  for the last "Watcher started" line when you're back.

