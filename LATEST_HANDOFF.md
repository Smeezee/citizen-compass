# LATEST_HANDOFF.md — Update #9 — 2026-07-30 1:04 AM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-07-30 01:04:55 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35.0/100
- Data completeness: 0.0%
- Viewer progress: 50.0%
- Documentation: 100.0%

**Ships:** 2 complete viewers / 4 total (50.0%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 7 files (0.27 MB)

**Scripts:** 11  |  **3D models:** 241  |  **Docs:** 222

---

## RECENT UPDATES (append-only, newest first)

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

