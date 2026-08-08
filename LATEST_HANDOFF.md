# LATEST_HANDOFF.md — Update #264 — 2026-08-08 4:54 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-08 16:54:39 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 60703 files (10414.22 MB)

**Scripts:** 17  |  **3D models:** 723  |  **Docs:** 724

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-08 16:53:43 — update-never-delete-guard-done-20260808.md

# Update — never-delete guard is in and proven; record gap closed (2026-08-08)

Two things: the preservation rule from
`WORKORDER_preservation-model-and-never-delete-rule.md` §3 is implemented, and
this closes a ~3.5 hour gap in the handoff record.

## The rule is enforced by construction

`app/preservation.py` blocks row removal on 15 preserved tables at **two**
layers, because blocking one is worth nothing:

- Core/SQL — `DELETE`, `DELETE ... WHERE`, `TRUNCATE`, including raw text and
  lowercase
- ORM — `session.delete()` and cascade deletes at flush

A wholesale "replace" is DELETE-then-INSERT, so blocking DELETE catches the
loader shape §3 warns about.

**Installed at engine creation in `app/database.py`, not in each importer.**
Wiring it per-importer works right up until somebody writes a new one. Every
consumer of that engine now inherits it, including code that does not know the
rule exists. `import_ship_components.py` also installs it explicitly, so the
intent is visible at the point of use.

`pipeline_check_results` is deliberately NOT preserved — it is an append-only
observation log that is meant to be flushed and archived, and guarding it would
break `checks_flush_fallback.py`.

## Rule 12 — 15 assertions, every case run twice

`checks/_verify_never_delete_guard.py`. The guard's claim is "a preserved row
cannot be removed", so a refused delete proves nothing on its own — it might
have failed for an unrelated reason. Every case runs **with the guard and
without it**:

```
guard installed  DELETE / DELETE WHERE / TRUNCATE / lowercase  -> all refused, row survives
guard removed    the same DELETE                               -> row GONE
```

That second line is the proof. Plus: a non-preserved table still deletes
normally (the guard is targeted, not a blanket ban), **DDL is untouched** so
alembic and the e2e harness still work, and `app.database.engine` is confirmed
guarded on import — checked by behaviour, because an import that silently
no-ops looks identical to one that worked.

Runs against TEMP tables shadowing the real ones; `public.ships` row count
asserted unchanged throughout. No destructive statement reached a real table.

## Two defects found in my own guard while proving it

**1. Half a guard, installed silently.** `before_flush` is a Session event and
does not exist on an Engine. The first version registered it on the target and
swallowed the failure with a bare `except`, so passing an Engine installed the
Core half only — the ORM path stayed open while the code read as covered. The
ORM test caught it. It now binds to the Session class explicitly.

**2. A test helper that disarmed production.** `remove_never_delete_guard()`
removed every listener process-wide. The verification called it to disarm its
own throwaway engine and silently disarmed `app.database.engine` too — a test
that turns off the live guard is worse than the defect the guard prevents. It
is now target-scoped.

Both are the same shape as the six silent-success cases already on record, and
neither would have shown up without the negative control.

## What this does NOT do

It makes the loss impossible; it does not yet make the absence **visible**.
`status`, `last_seen_patch`, `first_seen_patch`, `successor_id`,
`removal_note` and `evidence_tier` (§4) are a schema migration against the real
database — that needs a verified backup under hard rule 4 and an explicit
go-ahead, so it is not done here.

That ordering is deliberate: **a row that is still there can be marked later; a
row that is gone cannot be recovered.** The deadline was on the deletion half.

So §3 acceptance is met in part — the row survives — and the `status=retired`
half waits on the migration.

## Record gap this closes

`LATEST_HANDOFF.md`'s newest entry was **13:04** while nine documents were
created between **14:18 and 16:37** — holoviewer, fankit, hologram,
preservation, importer-audit and commlink prompts and findings, none of them
mentioned in it.

Not a pipeline fault: the watcher is healthy (PID 8856, update #260 at 16:38)
and correctly classified those as docs rather than updates. No update was
filed. Recording it here so the next session does not read 13:04 as current, as
I nearly did.

## State

- Nothing committed or pushed — no go-ahead given for either work order.
- Working tree: guard + verification are new; `citizen-collector/` untouched
  per the sole-writer note.
- Auditor after the change: 14 findings, **0 DEFECT**.
- Queued next: `docs/prompt-code-holoviewer-all-ships.md`.

### 2026-08-08 16:43:46 — update-preservation-rule-intake-20260808.md

# Update — never-delete importer rule: intake (2026-08-08)

Filed on intake per rule 13, before any work.

Received from Sleven: implement `WORKORDER_preservation-model-and-never-delete-rule.md`
§3 first, then file a handoff update closing the record gap.

**Why this jumped the queue:** it is the only outstanding item with a deadline.
The rule must land *before the next snapshot import*; after that the loss is
silent and unrecoverable. Port Olisar is already gone — 2,066 gazetteer
entities and it is not one of them — and the Aurora Mk I survives only because
a snapshot caught it by luck.

Also noting a record gap I will close afterwards: `LATEST_HANDOFF.md`'s newest
entry is 13:04, while nine documents were created 14:18–16:37. The watcher is
healthy (PID 8856, update #260 at 16:38) and correctly filed those as docs, not
updates — the gap is that no update was filed, not a pipeline fault.

Holding off on `docs/prompt-code-holoviewer-all-ships.md` until this lands.

### 2026-08-08 13:04:07 — update-wo-c3-aggregation-rules-received-20260808.md

# Update — C3 aggregation-rules work order received (2026-08-08)

Received from C1: reverse-engineer the real aggregation rules for
`ShieldsTotal`, `Power`, `Cooling`, `Emission` (EM and IR), `Distortion.Pool`
and DPS, by testing candidate formulae against CIG's own computed aggregates in
`ships.json` across all 316 ships. Then spec (not build) the temporary loadout
page.

**Routing flag.** The order is addressed `for C3 (Cowork research session)`, not
Claude Code. Sleven handed it to this session. Proceeding, with the reasoning
stated so it can be overridden cheaply: the core of this job is a full
computation across 316 ships joined against `ship-items.json`, and a full scan
of that kind is already on record as having **timed out through the Cowork
bridge** (C2's open item 10, "run it locally"). That part is structurally
better placed here. If C3 is already on it, this stops.

**The method, restated so it is not lost:** `ships.json` carries CIG's own
computed aggregates for each ship's stock loadout, and `ship-items.json` carries
the components. That is 316 worked examples with the answers in the back of the
book — every rule gets tested against labelled data rather than guessed at.

**What I owe, per aggregate:** a candidate rule as actual arithmetic, run across
all 316, reported as a **residual** — exact matches, near misses, misses, and
what the misses have in common. "Works on 300 of 316" is the finding. "Verified"
is not. Anything I cannot derive gets marked **unshippable** rather than
approximated.

**The discriminating case for shields:** the Zeus Mk II CL shows N-1 (three
7200 generators, `ShieldsTotal.Hp` 14,400). One example is not a rule. A ship
fitted with two *different* generators separates N-1 from capacity-weighted
fast, and finding one is the first thing to do.

**Constraints:** research and a proposal only, do not build. Stay off
`citizen-collector/` entirely — C1 is the sole writer and is actively in it.
Verify against files on disk, not planning docs. Every check gets a case that
could have failed it.

### 2026-08-07 21:27:19 — update-items-8-9-committed-not-pushed-20260807.md

# Update — items 8 and 9 committed, not pushed (2026-08-07)

Commit `8f27c8f` on `main`, 5 files, 664 insertions:

- `checks/source_checks.py` — `snapshot_shape_check` + registration
- `checks/file_checks.py` — `unreleased_content_check` + registration
- `checks/_verify_snapshot_shape.py` — 14 assertions, both directions
- `checks/_verify_unreleased_content.py` — 19 assertions, both directions
- `scripts/publication_filter.py` — the single definition of "may this be
  published"

**Staged by name, one path at a time.** `git add -A` was deliberately not used —
the ~50-file CRLF/LF churn would have buried 664 lines of new work in a diff
nobody could read. The staged diff was checked before committing: 5 files, no
churn swept in.

**Not pushed.** Hard rule 2 — the go-ahead I have covers the commit. A push is a
separate action and needs its own.

## Left alone deliberately

- The five malformed / zero-byte snapshot artifacts. Findings-only auditors, and
  rule 1 — moving or deleting them is Sleven's.
- `.uex_snap_name`, still untracked at the repo root from the 03:32 run.
- `data-layer/derived/**` and the other untracked working-tree content, none of
  which is mine.

## Open, and worth a decision

1. **The zero-byte fsck log** — `scunpacked-data/snapshots/20260731T041451Z.partial.fsck_output.log`.
   That integrity run's result is unrecoverable. The snapshot it was checking is
   still there; whether it gets re-fsck'd or marked unverified is a call, not a
   defect I can close.
2. **`keybinds.src.html`** — still a second standalone copy of the keybind
   tester with no HELP drawer, from this morning's work.
3. **Playwright lives in the scratchpad**, so `testing/_src/test_help_drawer.js`
   is committed but not runnable from a fresh checkout without
   `npm i playwright` on `NODE_PATH`.

### 2026-08-07 21:00:11 — update-item-9-unreleased-content-done-20260807.md

# Update — item 9 done: unreleased-content filter and guard (2026-08-07)

## The correction: this is NOT a live leak

C2's list says *"Contract-derived pages may be advertising unreleased missions
right now."* **They are not, and I checked before building anything.**

Nothing published reads the contract tables. The only file in the repo that
touches contract fields is `scripts/split_craft_pages.py`, which uses
`mission_type` and writes to `data-layer/processed/` — never to `releases/`,
`static/` or `testing/_deploy/`. The flagged records sit in `data-layer/derived/`,
which is not served.

So the exposure is **prospective, not live**. Saying otherwise would have been
easy and wrong. What is true is that this is the cheap moment to fix it — before
the first contract page ships rather than after.

## The size of it, measured

    contracts_full.json        5,107 records   958 not_for_release   22 work_in_progress
    contracts_by_system.json   5,108 records   959 not_for_release   22 work_in_progress

**959 of 5,107 — 18.8%, nearly one in five.** Both flags are real Python bools
in the current data, sampled across 2,000 records.

Note the derived tables are **correct** to carry these flags. They are a
faithful record of what is in the game files, and stripping them at derivation
time would destroy the evidence that a record is unreleased. The filtering
belongs at publication time, which is where it now is.

## What was built

**`scripts/publication_filter.py`** — the single definition of "may this be
published", per rule 14. `is_publishable`, `unreleased_reasons`, and
`filter_publishable`, which returns **both** halves on purpose: "we withheld 959
records" is a number a publisher should log and a reviewer should be able to
check. A filter that silently drops rows is indistinguishable from a filter that
never ran.

**`unreleased_content_check`** in `checks/file_checks.py`, registered in
`CHECKERS`. Scans `releases/`, `static/` and `testing/_deploy/` for any record
carrying the flags, walking nested structures rather than assuming a flat array.

**The important design decision:** when it finds no contract corpus, it reports
**LIMITATION, not PASS.** A checker that scans published output, finds no
contract records because none are published, and calls that a pass is reporting
clean for a corpus it never had — the same shape as `integrity_scan` globbing
`*.json` and passing over files it never opened. Run against the repo right now
it says, correctly:

> scanned 0 published .json file(s) … but also no contract-shaped corpus to
> examine at all. This is reported as NOT PERFORMED rather than PASS.

## Proven before trusted — `checks/_verify_unreleased_content.py`, 19 checks

Highlights of the negative controls:

- **The truthiness trap.** `bool("false")` is `True` in Python. The test first
  proves the trap is real, then proves the filter does not fall for it — a plain
  truthiness check would have withheld a publishable record, or with the flags
  inverted, published a withheld one.
- A flagged record in a published file → **DEFECT**, and the finding **names**
  the record.
- The same corpus run through the filter → no DEFECT.
- A flagged record nested three levels deep → still caught.
- An unparseable file mentioning the flags → **WARNING**, never a pass.
- No corpus → **LIMITATION**, and never PASS.

## Verification

- Both new checkers registered: 19 checkers across the file and source groups.
- Existing suite unaffected — `_verify_missing_encoding.py` still passes 19/19.
- Rule 15: `missing_encoding_check` reports **zero** violations in any file I
  added.

Nothing committed, nothing pushed, nothing moved or deleted.

### 2026-08-07 20:56:21 — update-item-8-snapshot-shape-checker-done-20260807.md

# Update — item 8 done: `snapshot_shape` checker, and the count was wrong (2026-08-07)

## The correction that matters: there is no code to fix

C2's `URGENT_path-join-bug-is-live-fired-tonight.md` treats this as a
path-construction bug in the pipeline. **It is not, and I could not find any
committed code carrying it.**

`uex_corp.py` does not write `_pull_summary.json` or `_pull_stderr.log` at all.
It documents `python uex_corp.py <output-dir>`, prints the summary to **stdout**
and diagnostics to **stderr**. The redirect into those filenames is done by the
**caller** — and there is no runner script anywhere in this repo. Searched for
one across `.py`, `.ps1`, `.sh`, `.bat`, `.cmd`, `.go`: the only references to
`uex_corp.py` are its own docstring, its verifier, and a manifest builder
recording which script produced a snapshot.

So the malformed names came from a hand-typed shell redirect. **There is no
patch that prevents a recurrence**, which is exactly why this needed a check
rather than a fix. I did not invent a runner script to have something to correct
— per rule 11, an honest gap beats a fabricated cause.

## Five occurrences across three sources, not four across one

The checker found one C2's sweep never reached:

    uexcorp/snapshots/
      20260806T033217Z.pullstderr.log          98 bytes   loose
      20260806T033217Z.pullsummary.json         0 bytes   loose AND empty
    api.star-citizen.wiki/snapshots/
      20260731T031754Z.partial/_fetch_metadata.json       0 bytes   correct path
      20260801T015346Z.partial.aborted__pagesize50/
                              _pull_summary.json          0 bytes   correct path
    scunpacked-data/snapshots/
      20260731T041451Z.partial.fsck_output.log  0 bytes   loose AND empty   <- NEW

The new one is the worst of the set. `20260731T041451Z.partial.fsck_output.log`
should have been `20260731T041451Z.partial/fsck_output.log` — same shape, the
separator replaced by a `.`. And it is **an fsck output log that is zero bytes**.
An integrity check whose output is empty is indistinguishable from an integrity
check that found nothing wrong.

The shape is consistent across all three sources: the path separator became a
literal `.`.

## What was built

`snapshot_shape_check` in `checks/source_checks.py`, registered in `CHECKERS` so
`run_checks.py` picks it up with the rest of the source group. Findings-only —
it never moves or deletes anything, so the cleanup of the five files above stays
Sleven's call under rule 1.

It reports **two deliberately separate defects**, because fixing one leaves the
other standing:

1. **Loose files directly inside `snapshots/`** — that directory holds sealed
   snapshot *directories* only. C2's point stands: a snapshot directory that can
   contain loose files is one bad glob away from a gate enumerating a file where
   it expected a snapshot.
2. **Zero-byte files anywhere in the tree** — two of the five sit at entirely
   *correct* paths. Fixing the path join would leave them exactly as they are,
   just filed more tidily.

## Proven before trusted — `checks/_verify_snapshot_shape.py`, 14 checks

Both directions, on synthetic trees, per hard rule 12:

- a clean tree produces **no** DEFECT (no false positive)
- the real 2026-08-06 malformed filename planted → caught, and the finding
  **names** the file
- a zero-byte file at a **correct** path → still caught, proving the two defects
  are independently detectable
- a non-empty loose file does **not** trip the zero-byte check, and vice versa
- absent root / no `*/snapshots` → **LIMITATION**, never PASS
- the file cap degrades to a LIMITATION naming partial coverage, never to a
  silent pass

Nothing committed. Nothing moved or deleted. Next: item 9.

### 2026-08-07 20:50:27 — update-items-8-9-started-20260807.md

# Update — starting items 8 and 9 from C2's open list (2026-08-07)

Sleven's go-ahead: take 8 and 9. Both are clear of `citizen-collector/`, which
the other session still owns.

## 8. The path-join bug — and a second defect tangled with it

C2's `docs/URGENT_path-join-bug-is-live-fired-tonight.md` names one defect. A
zero-byte sweep of `snapshots/` found **three** empty artifacts across **two**
sources, which separates into two distinct problems:

    api.star-citizen.wiki/snapshots/20260731T031754Z.partial/_fetch_metadata.json    0 bytes
    api.star-citizen.wiki/snapshots/20260801T015346Z.partial.aborted__pagesize50/
                                                          _pull_summary.json          0 bytes
    uexcorp/snapshots/20260806T033217Z.pullsummary.json                               0 bytes

1. **Path join** — separator and leading underscore both stripped, so the
   artifact lands as a *sibling* of the snapshot directories instead of inside
   one. That is the uexcorp file, and the same shape as the three malformed
   top-level `data-layerexports` style directories.
2. **Aborted runs write zero-byte summaries** — the two star-citizen.wiki files
   are at *correct* paths inside properly named `.partial` / `.aborted`
   directories and are still empty. Fixing the path join alone leaves this one
   intact, just filed more tidily.

The second is the more serious by this project's own standard: an artifact that
exists, is readable, parses as nothing, and reports no failure is the
silent-success shape hard rule 12 exists for.

## 9. `NotForRelease` / `WorkInProgress` filter

Verified before starting: the only hits anywhere in the tree are vendored
`litellm` and swagger bundles under `venv/`. **No project code filters on these
flags at all.** Contract-derived output may be presenting unreleased missions as
though they were live.

## Second-writer check, run first

Per rule 14 and what caught CF-01 ninety minutes ago: checked mtimes and `HEAD`
state on the files I am about to touch before writing anything. Recording the
result in the completion update rather than asserting it here.

**Constraints:** no commit, no push without a fresh go-ahead. No `git add -A` —
the ~50-file CRLF churn. Every gate proven against known-bad input before it is
trusted.

### 2026-08-07 17:54:57 — update-cf-01-stood-down-20260807.md

# Update — CF-01: stood down, other session owns it (2026-08-07)

Sleven's call: **stand down.** The other session finishes CF-01. I am staying
off `citizen-collector/` entirely.

**Nothing was written, committed, or pushed by me on this work order.** The only
artefacts from my side are three `inbox/` updates: the order arriving, the
second-writer block, and this one.

## Handover note for whoever owns CF-01

State as I read it at 17:49, so the owning session can confirm rather than
rediscover:

- **job 1 (crash)** and **job 2 (interval)** are in the working tree and look
  complete, with their selftests registered in `main.go`.
- **hotkey §2b** (polling, edge detect, dedup, `via <mechanism>` tag) is in and
  registered.
- **hotkey §2a** — log the renderer from `Game.log`, the window style/rect/
  topmost flags, and elevation of both processes — was **not** present.
- **job 4, the tray icon** — no `Shell_NotifyIcon` anywhere — was **not**
  present.

Two things from the order worth not losing, since they are easy to drop at the
end of a long job:

1. **§2 cannot be closed by unit tests.** C1 is explicit: the real acceptance is
   a live PTU session on **Vulkan** with a `via polling` line in the log. It has
   to be handed back saying that plainly rather than implied settled.
2. **Do not `git add -A`** — ~50 files carry pure CRLF/LF churn. Stage by name.

## Note on how this was caught

The tell was file mtimes, not a conflict: eight collector sources written in one
batch at 17:48:44–17:48:45, ten seconds before I logged that I was starting, and
`tasklist` showing nine `claude.exe` processes. Worth doing that check before
starting any job in a shared area of this repo — a second writer is invisible
until it has already cost something.

Idle and available for other work.

### 2026-08-07 17:50:58 — update-cf-01-BLOCKED-second-writer-detected-20260807.md

# Update — CF-01 STOPPED before writing: a second session is already on it (2026-08-07)

**I have written nothing to `citizen-collector/`. Stopping and asking, per hard
rule 14 and the "if you are unsure, it does apply" clause.**

## What I found

I read the work order, then went to start job 1 (the crash). The fix was already
there.

`citizen-collector/winapi.go` at `HEAD` still carries the broken shape — a fresh
`syscall.NewCallback` per call. The **working tree** carries the corrected
one-callback-per-process version, uncommitted, with a comment block quoting the
same 14m2s/14m4s/14m4s/14m0s field evidence the work order does.

Eight source files were written in a single batch at **17:48:44–17:48:45**. I
filed my "work order received" update at 17:48:56. So that write landed roughly
ten seconds before I logged that I was starting, and I did not do it —
everything I touched this session was under `testing/` and `data-layer/`.

`tasklist` shows **nine `claude.exe` processes running.**

## State of the four jobs as it currently stands in the working tree

| job | state | evidence |
|---|---|---|
| 1. crash — `too many callback functions` | **done** | one package-level `enumCallback`, mutex-guarded `enumFn`, `runCallbackLeakSelftest` registered in `main.go` |
| 2. interval — 60s, unit change | **done** | `IntervalSeconds`, `defaultIntervalSeconds = 60`, `resolveIntervalSeconds` handles legacy `interval_minutes` and logs the conversion, `interval:%ds` tag, two selftests registered |
| 3. hotkey §2b — polling, edge-detect, dedup, tagging | **done** | `pollHotkey`, `GetAsyncKeyState` wired in `winapi.go`, `hotkey press received (%s, via %s)`, `runHotkeyEdgeSelftest` + `runHotkeyDedupSelftest` registered |
| 3. hotkey §2a — log renderer / window flags / elevation | **not built** | no `Game.log` renderer parse, no elevation check, no window style/rect/topmost logging anywhere |
| 4. tray indicator (option A) | **not built** | no `Shell_NotifyIcon` / `NOTIFYICONDATA` anywhere |

So the other session appears to be working the list in C1's stated order and is
somewhere around §2a / job 4 right now.

## Why I stopped instead of picking up §2a and the tray

Rule 14 names this exact defect, and its two prior instances both cost real
work — including a concurrent session rewriting `_layer.src.html` mid-verification
twice in one evening, once silently deleting a keybinds overlay and a compliance
strip.

§2a lands in `hotkey.go` / `auto.go` / `main.go` / `winapi.go`. Those are four of
the eight files the other session wrote ninety seconds ago. Two writers on those
files is not a merge conflict I would see — it is a last-write-wins clobber of
work that is not committed anywhere and therefore cannot be recovered.

The tray icon (job 4) is genuinely independent and would be safe in a new file,
**but** it still needs a wire-in point in `main.go`, which is contended.

## What I need from Sleven

One of:

1. **Stand down** — the other session finishes CF-01, and I stay off
   `citizen-collector/` entirely.
2. **Take over** — the other session is stopped first, and I verify what is
   there (build + full selftest run, including the required negative controls)
   then finish §2a and job 4.
3. **Split on a hard boundary** — I take job 4 only, in new files, and hand back
   the one-line `main.go` wire-in for whoever owns that file to apply.

Not proceeding on a guess. Nothing committed, nothing pushed, nothing written.

### 2026-08-07 17:48:56 — update-wo-cf-01-rev3-received-20260807.md

# Update — WO CF-01 rev 3 received, four collector fixes (2026-08-07)

Received from C1: `docs/prompt-collector-fixes-CF-01.md`, rev 3. The header
arrived in conversation without the body; found the full document on disk and
read it before starting anything.

**Approved by Sleven 2026-08-07:** "I 100% am down with making it 60secs and I
do want to get the bugs fixed and the hotkey fixed as well."

Rev 3 supersedes revs 1 and 2 **in place** — no addendum, per rule 14. The
headline: the hotkey is solved. Sleven ran a one-variable experiment (DX11 vs
Vulkan, everything else identical). Hotkey works on DX11, not on Vulkan.
Capture is proven fine on Vulkan; only the input path fails.

## The four jobs, in the order C1 specified

1. **The crash** — `too many callback functions`, 28 occurrences, dying at a
   dead-fixed 14m0s–14m4s. Cause confirmed in source: `winapi.go:261`
   `EnumTopWindows` calls `syscall.NewCallback` on every 2-second poll tick, and
   that table is process-lifetime and never freed. One callback for the life of
   the process instead. First, because everything else is measured inside a
   process that currently dies every fourteen minutes.
2. **The interval** — 60 seconds, and the unit changes from minutes to seconds
   properly. `interval_minutes` still read and converted, with the conversion
   logged, because silently ignoring a setting sitting on his disk is the same
   shape as everything else in this document.
3. **The hotkey** — §2a log the renderer/window/elevation once per session,
   §2b `GetAsyncKeyState` polling promoted to primary alongside `RegisterHotKey`,
   edge-detected, deduplicated, and **tagged by which mechanism delivered it**.
4. **The tray indicator** — system tray icon (A). The overlay pip (B) is dropped.
   The status panel (C) comes after A.

## Constraints I am working under

- **Do not commit or push.** Nothing into git without Sleven's explicit
  go-ahead — and note that is a per-change go-ahead, so the HELP drawer push
  earlier today does not carry over.
- **Do not `git add -A`.** ~50 files carry pure CRLF/LF churn (191,317
  insertions and deletions, verified byte-identical after stripping CR). Stage
  by name only.
- Hard rule 12 is called out explicitly in three of the four sections: every
  acceptance test has a required negative control, and a positive test that
  cannot fail is to be reported as measuring nothing rather than shipped.
- §2 cannot be proven finished without a live Vulkan session. That gets handed
  back plainly, not implied to be settled by unit tests.

**Next:** job 1, the crash.

### 2026-08-07 16:04:51 — update-help-drawer-pushed-20260807.md

# Update — HELP drawer pushed to origin/main (2026-08-07)

Pushed on Sleven's explicit go-ahead. `cce3d3e..ba25d9c  main -> main`.

Two commits went, not one:

- `ba25d9c` — HELP drawer on the keybind screen (this session's work)
- `fe62c09` — "Show what each key actually does, and mark what has not been
  reviewed", which was **already committed and unpushed when this session
  started**. It is an ancestor of `ba25d9c`, so it could not be pushed
  separately without rewriting history. Flagged before pushing; Sleven chose to
  send both.

`git log origin/main..HEAD` is now empty — nothing left unpushed on `main`.

## State after this

- Testing site live and verified:
  https://citizencompasstesting.citizencompass-contact.workers.dev
- 38 tests pass against the **deployed** page, negative controls included.
  Re-runnable: `node testing/_src/test_help_drawer.js <url>` (needs playwright;
  it was installed to a scratch dir, not the repo, so a fresh run needs
  `npm i playwright` somewhere on NODE_PATH).
- Netlify and the live site untouched.

## Still open, not acted on

`keybinds.src.html` is a second standalone copy of the same keybind tester,
copied to `keybinds.html` on every deploy. Nothing links to it, so it is not
user-reachable, and it did **not** get the HELP drawer — the work order named
one page. If that page is meant to ship, it is now the tester without the help,
and the two copies will keep diverging. Sleven's call.

Working tree still carries the unrelated pre-existing modifications
(`citizen-collector/*`, `LATEST_HANDOFF.md`, the untracked `testing/_src`
scratch files). None of them were touched or committed by this work.

### 2026-08-07 13:40:29 — update-help-drawer-committed-not-pushed-20260807.md

# Update — HELP drawer committed, not pushed (2026-08-07)

Commit `ba25d9c` on `main`, 6 files, 1042 insertions:

- `testing/_src/_layer.src.html` — the drawer, the reflow, the hint line
- `testing/_src/build_deploy.py` — build-time JSON substitution + its guards
- `data-layer/processed/keybind_troubleshooting.json` (now tracked)
- `data-layer/processed/vendor_support.json` (now tracked)
- `testing/_src/test_help_drawer.js` — 38 tests with negative controls
- `testing/_src/shot_help_drawer.js` — screenshot harness

**Not pushed.** Hard rule 2 — no go-ahead given for this change. The work is
committed locally and waiting.

Deliberately left out of the commit: `testing/_src/_modelfolders.txt` and
`testing/_src/_scunpacked_names.json`, which were already untracked before this
work and are nothing to do with it.

## Open item for Sleven, not acted on

`keybinds.src.html` is a **second, standalone copy** of the same keybind tester,
built and copied to `keybinds.html` on every deploy. Nothing on the site links
to it, so it is not user-reachable today, and the work order named one page — so
it did **not** get the HELP drawer. If it is meant to stay a shipped page, it is
currently the tester without the help, and that divergence will only widen. Two
copies of one screen is the shape rule 14 exists about. Flagging it rather than
expanding scope unasked.

### 2026-08-07 13:39:44 — update-help-drawer-deployed-verified-20260807.md

# Update — HELP drawer deployed to testing and verified on the deployed page (2026-08-07)

**Testing URL:** https://citizencompasstesting.citizencompass-contact.workers.dev

Deployed with `scripts/deploy_testing.ps1` (Workers static assets, not Pages).
Netlify and live untouched.

## The trap fired, and it was worth checking

The first run of the test suite against the **deployed** URL reported the HELP
tab missing — exactly the failure mode the work order warned about, and exactly
why the instruction was "open the deployed page to confirm, not the source."

It was **not** a missed substitution. Checked rather than assumed:

- deployed `index.html` is 1,584,562 bytes, byte-for-byte the local build's size
- deployed page contains `cc-help-tab` (7 occurrences) and `cc-kb-hinthelp`
- the only `__BUILD_INJECTS__` occurrences left are the renderer's own tripwire
  references, which is correct

The real cause was in my test: a fixed 300ms sleep after the password gate.
That is fine on a `file://` build and a race over the network on a 1.5MB page
whose drawer script sits near the end of it. Replaced with an explicit
`waitForFunction` on the drawer announcing itself. A fixed sleep standing in for
a readiness check is the same species of defect as a gate that cannot fail —
it passes for a reason unrelated to what it claims to prove.

## Verified on the deployed page

**38 passed, 0 failed** against the live testing URL, including every negative
control.

Measured content width, `#cc-kb`, at 1920x1080, on the deployed page:

| state | width |
|---|---|
| drawer closed | **1874px** |
| drawer open | **1454px** |
| delta | **420px** — the drawer width |

The keyboard board genuinely re-lays-out into the narrower region: keys narrow,
the mouse block moves in, the device selector and the mode/device rows all stay
visible and clickable. Nothing sits behind the panel.

Read on screen at 1920x1080 across four node types — question (with HOW TO
CHECK), fix (steps, note, and the continue button naming the retest it leads
to), choice, and the dead end with the VKB hand-off and its KNOWN CATCH callout.

## Committed

Committed to `main`. **Not pushed** — no go-ahead given, per hard rule 2.

### 2026-08-07 13:36:50 — update-help-drawer-built-tests-pass-20260807.md

# Update — HELP drawer built, 38 tests pass with negative controls (2026-08-07)

Built into `testing/_src/_layer.src.html` (the `#cc-kb` keybind overlay, which
is what the KEYBINDS tab opens and what ships as `index.html`). Not
`keybinds.src.html` — nothing on the site links to `keybinds.html`, and the
DISPLAY / FEEDBACK tab stack the order places HELP alongside exists only in the
layer.

## The shrink is new behaviour, and it works

Every pre-existing drawer overlays. This one reflows, measured on the built page
at 1920x1080:

    #cc-kb width   closed = 1874px    open = 1454px    delta = 420px

The keyboard board genuinely re-lays-out into the narrower region — keys narrow,
the mouse block moves in, nothing is hidden behind the panel. It uses its own
`body.cc-help-open` class rather than the shared `cc-drawer-open`, which already
means "tabs, get out of the way" to three other tabs.

## What went in

- `#cc-help-tab` — right edge, `z-index:100004` so it stays clickable above the
  keybind overlay (`#cc-kb` is 100003; the other tabs at 100002 are covered by
  it). Persistent, never auto-opens.
- Graph renderer walking `keybind_troubleshooting.json` as a graph: questions
  with `how_to_check` always rendered, the choice node, fixes with steps + note
  + a continue button that follows `then` and names the retest it leads to.
  `end_not_covered` renders as a dead end with no invented route out.
- Back-a-step history — a wrong answer costs one click.
- Vendor matching on `usb_vid` **alone**, parsing the VID out of the Gamepad
  API's `id` string (Chrome `(Vendor: 231d …)` and Firefox `231d-0200-…` forms).
  `known_gotcha` gets its own callout. A vendor with `usb_vid: null`
  (turtle_beach) is skipped by construction, so it can never be auto-matched.
- The one line on the binding screen, under the device selector row, opening the
  drawer at `q_selector_setting`.

## The trap

`keybinds.src.html` is copied verbatim, so the model/thumbnail substitution list
was never the risk here. Two things were:

1. `inject_engine.py` overwrites everything between the DEVICE PANEL boundary
   markers on every build. The drawer is appended well outside that region.
2. `check_deploy_clean.enforce` allows only `index.html` plus the `PAGES`
   outputs, so a sidecar JSON would have failed the deploy guard.

So both JSON payloads are substituted into the page by `build_deploy.py` from
`data-layer/processed/` — one writer, no pasted copy to drift. The build asserts
the placeholder exists, asserts none survives, and the renderer refuses to draw
if it ever sees one. **That guard fired for real on the first build** (the
runtime check named the token itself and tripped its own tripwire), which is
incidental proof the check can fail.

## Tests — 38 pass, every one seen to fail first

`testing/_src/test_help_drawer.js` (playwright/chromium, 1920x1080).

- **Shrink.** Negative control neutralises *only* the reflow rules, leaving the
  drawer opening and visible — i.e. exactly an overlay drawer — and asserts the
  width assertion then fails. A test that only checked "the drawer appeared"
  would pass in that state; this one does not.
- **Graph.** All 17 nodes reachable from start, every link resolves. Negative
  control plants a dangling link, confirms both the break and the node it
  orphans are reported, then confirms removing it returns clean.
- **Fix routing.** All 11 `then`-carrying fixes clicked through the real UI and
  asserted to land on their retest node. `end_not_covered` asserted to offer no
  continue button.
- **Vendor.** 231d → VKB, 3344 → VIRPIL, Firefox-form id resolves too. Unknown
  VID → generic fallback and asserted *not* to name any wrong manufacturer. A
  VKB VID planted as a **product** id asserted not to match. turtle_beach
  asserted unmatchable.
- **Read on screen** at 1920x1080 — question, fix, choice and dead-end nodes.

Screenshots are regenerable via `testing/_src/shot_help_drawer.js`; they were
kept out of the repo deliberately.

`testing/_src/cc_help.inc.html` was the authoring copy and is now spliced into
the layer. Moved to `_to_delete/help_drawer_inc_spliced_20260807/` rather than
deleted (rule 1), so there is exactly one copy of the block.

**Next:** deploy to testing via `scripts/deploy_testing.ps1` and re-run the
tests against the deployed URL, not the local build. Nothing committed yet.

### 2026-08-07 13:24:43 — update-wo-help-drawer-received-20260807.md

# Update — HELP drawer work order received (2026-08-07)

**Received:** build the HELP drawer on the keybind page, driven by
`data-layer/processed/keybind_troubleshooting.json` (17-node branching graph)
and `data-layer/processed/vendor_support.json` (5 vendors, matched on USB
vendor ID alone).

**First question answered before building — existing drawer behaviour:**

Every existing drawer in `testing/_src/_layer.src.html` **overlays**. None of
them reflow page content. Evidence:

- `#cc-panel` (DISPLAY) — `position:fixed; right:-380px; width:380px; z-index:100001`
- `#cc-mdraw` (manufacturer) — `position:fixed; left:-250px; width:250px; z-index:99998`
- `#cc-fb` (FEEDBACK) — `position:fixed; inset:0`, a full-screen modal scrim
- `#cc-kb` (KEYBINDS) — `position:fixed; inset:0 0 0 46px`, a full-screen takeover

The `translateX(-380px)` rules Sleven found on `#cc-fb-tab` / `#cc-kb-tab` /
`#cc-fi-tab`, and `left:296px` on `#cc-mtab`, move **tab furniture only** — so
the tabs are not buried under the panel that just slid over them. A grep for
any content-region resize (`margin-right`, `padding-right:380`,
`width:calc(100% - …)` under `body.cc-drawer-open`) returns nothing.

**So: shrink-the-page is NEW behaviour, not reuse.** Bolting a reflow onto the
existing `body.cc-drawer-open` class would fight the pattern — that class is
currently understood by three tabs to mean "get out of the way", and repurposing
it to also mean "resize content" would make the DISPLAY and FEEDBACK drawers
start reflowing the page too. The HELP drawer gets its own class and its own
mechanism, and the existing drawers are left alone.

**Trap noted before building:** `keybinds.src.html` is *copied verbatim* to
`keybinds.html` by `build_deploy.py` (it is in `PAGES`), so the model/thumbnail
substitution list does not apply to it. The trap that *does* apply is
`inject_engine.py`, which overwrites everything between the DEVICE PANEL rev 2
boundary markers in that file on every build. Any vendor-ID code placed inside
that region would be silently discarded. Also: `check_deploy_clean.enforce`
allows only `index.html` plus the `PAGES` outputs, so new sidecar files would
fail the deploy guard — the JSON will be inlined rather than fetched.

**Next:** build it, then verify against the deployed page, not the source.

### 2026-08-06 20:21:38 — update-webview2-bundling-provenance-question-20260807.md

# Update: three commits pushed. WebView2 bundling hit a provenance fork.

**2026-08-07.** Pushed `1eadf97..d314540` - `8594ed3`, `c6a74a2`, `d314540`.
Level with origin, nothing matching `wrangler`/`.env`/`password`/`secret`/`.dump`
in any of the three diffs.

## Correction to a number I gave

I said the fixed-version runtime was **~130 MB**. Microsoft's own distribution
doc says **"The Fixed Version binaries are over 250 MB."** My figure was wrong.
It does not change Sleven's ruling - the reasoning was that size is irrelevant
against a 100 GB game - but the number should be right in the record.

## The official download cannot be fetched headlessly

`developer.microsoft.com/microsoft-edge/webview2` builds the fixed-version link
**client-side from a version/architecture picker**. There is no `fwlink` for it
(unlike the Evergreen bootstrapper, 2124701, and the Evergreen standalone
installer, which do have stable links). Fetching the page returns the picker UI,
not a URL.

I will not guess a CDN URL and present it as official - an invented link that
happens to 404 wastes an hour, and one that happens to *work* is worse, because
nobody would check what it actually served.

## A programmatic source exists, but it is NOT Microsoft

NuGet carries `WebView2.Runtime.X64` **151.0.4129.59** - exactly the version
this machine runs - described as "Webview2 runtime for Fixed Version
distribution". 1.18 M downloads.

**It is published by a third-party account (`ProKn1fe`), not Microsoft.**

That is a supply-chain decision, not a technical one, so it is Sleven's:

- **what it is:** a repackage of a 250 MB browser engine
- **where it goes:** shipped inside every crew copy, run on other people's
  machines, on a build that is **deliberately unsigned**
- **what it defeats:** the whole point of bundling is removing an
  install-time failure. Trading a rare missing-runtime error for an
  un-provenanced browser binary is a different bargain than the one ruled on.

The project's standard is that unverifiable provenance is stated, not assumed.
Same rule that keeps `data-layer/external-source-manifests/` tracked.

## Two distribution landmines found in the docs - both affect §8

1. **Windows 10 + Fixed Version 120 or later, unpackaged Win32 app** requires
   these to be run on the *user's* machine or the runtime will not start:

   ```
   icacls {path} /grant *S-1-15-2-2:(OI)(CI)(RX)
   icacls {path} /grant *S-1-15-2-1:(OI)(CI)(RX)
   ```

   Sleven is on Windows 11, where this does not apply - **so this failure cannot
   occur on the machine where it will be tested, and will land on the first crew
   member running Windows 10.** That is precisely the trap Sleven identified
   about the installed runtime, in a second place.

2. **Fixed Version cannot run from a network location or UNC path.** A crew
   member who unzips to a mapped drive gets a program that does not start.

Both need handling inside the packager and a plain-English error, not discovery
in the field.

3. Extraction must be `expand {cab} -F:* {dest}` - Microsoft explicitly warns
   that File Explorer produces the wrong folder structure.

## Not blocked on this

The runtime is a drop-in payload. I am proceeding with §6 (continuous detection)
and §7 (follow-the-game) now, and building the runtime resolution - env var
`WEBVIEW2_BROWSER_EXECUTABLE_FOLDER` / `browserExecutableFolder`, presence
check, plain-English failure - so the CAB drops in whenever its provenance is
settled.

### 2026-08-06 20:17:39 — update-hotkey-press-logging-restart-needed-20260807.md

# Update: hotkey press now logged on arrival - SLEVEN MUST RESTART TO GET IT

**2026-08-07.** Committed `d314540`. Binaries rebuilt.

## ACTION NEEDED: the running session cannot see this fix

**PID 5000 is still running the binary loaded at 22:03:41.** A running process
executes the code already in memory; rebuilding the exe on disk does not change
it. **The new log line only exists after the collector is restarted.**

Since the whole point is diagnosing tonight's silent Ctrl+Alt+F9, the diagnosis
needs a restart before the next press is meaningful. Not done unasked - stopping
a live capture session is Sleven's call.

## What changed

One line, logged the instant a press is received, before the window gate and
before any capture is attempted:

```
hotkey press received (Ctrl+Alt+F9)
```

Previously the log held `hotkey registered` and then nothing until a capture
**succeeded**, so these were indistinguishable:

- the press **never arrived** - nothing reached the process
- the press **arrived and failed** - capture broke downstream

Now: press the key and look. A line means it arrived. No line means it did not.

The "no game window" path now reads `press received but no game window`, so it
presents as a consequence of an arrival rather than an unrelated event. The
failure path already carried its reason.

**On the suspected cause:** if Star Citizen in exclusive fullscreen is taking
the key before any global hotkey sees it, there will be **no line at all**, and
that is the proof. This does not fix that problem - it makes it diagnosable
rather than suspected, which has to come first.

Third instance of this defect class in this binary, after the auto log that only
wrote on capture and the hotkey that was never registered.

## Tested with the capture deliberately failing

That is the case that used to be silent, so it is the one worth proving:

```
[ok] no press means no receipt line       <- negative control
[ok] a press is logged ON RECEIPT
[ok] a failed capture states its reason
[ok] receipt is logged BEFORE the outcome
```

Order is asserted because a capture that hung forever would otherwise still
leave no evidence the press arrived.

## Live session evidence (untouched, still running)

```
[22:13:45] captured 20260807T031343Z_0024.png  <- interval:10m
[22:15:46] alive: watching ...\LIVE\Game.log, 347 bytes read since last line, 1 captures total
```

The interval fallback fired and the heartbeat's capture counter incremented -
both Job 3 features confirmed in production.

## A bad check of my own, caught and corrected

I verified the rebuilt binaries with `strings ... | grep -c` and reported
"ABSENT - binary is stale". **`strings` is not installed here**, so the command
produced nothing and the zero count meant nothing - a check that could not
succeed reporting a definite negative. Re-done with `grep -a` plus a control
string that must be present: both binaries contain the new line, 3 matches each.

Same lesson as everything else tonight - a check whose failure mode is
indistinguishable from its success mode is not a check.

## Unpushed

`8594ed3`, `c6a74a2`, `d314540`.

### 2026-08-06 20:12:33 — update-wo-ui-01-section5-done-live-session-verified-20260807.md

# Update: WO-UI-01 §5 done. Live session observed working. Two defects found.

**2026-08-07.** Committed `c6a74a2`. Two commits unpushed (`8594ed3`, `c6a74a2`).

## Sleven's live session is running and all three fixes are visible in it

`collector-master.exe --auto`, PID 5000, started 22:03:41. **Not touched.**

```
[22:03:41] hotkey registered: Ctrl+Alt+F9
[22:03:42] startup: watching ...\StarCitizen\LIVE\Game.log (found by scanning known install locations)
[22:06:42] alive: watching ...\Game.log, 573038 bytes read since last line, 0 captures total
```

Job 1, Job 2 and Job 3 all confirmed working **in production**, not just under
test. The log is being read (573 KB since the last line), so the game is writing
and the collector is following it.

## §5 implemented - the selftest can report from a GUI binary

All three parts, per the ruling:

1. `AttachConsole(ATTACH_PARENT_PROCESS)` when a console exists; std handles
   reopened onto `CONOUT$` afterwards, because a `-H=windowsgui` process starts
   with none and attaching alone leaves `fmt.Print` writing into a closed handle.
2. **`collector-selftest-results.txt` next to the exe, always**, leading with
   `RESULT=` / `EXIT=` so nothing downstream parses prose. Written on every path
   - a file appearing only on success would let a crashed run look identical to
   one never attempted, and yesterday's file would read as today's pass.
3. Meaningful exit code: 0 PASS, 1 FAIL, **2 VOID**.

Output is captured by teeing `os.Stdout`, so helpers printing directly land in
the file too. Capturing only `check()` lines would give a results file that
quietly disagreed with the screen.

## DEFECT FOUND, caused by the live session - now fixed

Running `--selftest` while the real session was collecting returned **exit 1**.
The session legitimately holds Ctrl+Alt+F9, so the registration checks correctly
said NOT PERFORMED - **but counted it as a failure**. The packager's "assert exit
0" would have failed for a reason with nothing to do with the package.

Two fixes:

- the selftest now uses **`ctrl+alt+shift+f12`**, not the product default. A test
  must not collide with the thing it is testing.
- when the key genuinely cannot be obtained the run is **VOID (exit 2)**, not
  FAIL. A check that could not run is a different fact from one that ran and
  failed, which is what exit 2 exists to say.

**Verified with the live session still running: exit 0, all sixteen hotkey
checks performed.**

Also removed a hardcoded `"Ctrl+Alt+F9"` expectation that silently became wrong
the moment the test key changed - the expected name is now derived from the spec.

## Toolkit settled

`winapi.go`'s own header records **`CGO_ENABLED=0` and no C compiler on this
machine**. That rules out every cgo-based UI toolkit outright.
`github.com/jchv/go-webview2` is **pure Go** and fetches cleanly, so it is the
one that can actually build here.

My hard-rule-7 concern was **unfounded and is withdrawn**: `pkg/pgconn` and
`watcher-go` already depend on `pgx`, `fsnotify` and `golang.org/x/*`. Rule 7
targets the ~29,000 cloned data files, not ordinary Go modules.

WebView2 runtime is present here (151.0.4129.59), but §3 wants it bundled so it
works on a stranger's machine. Bundling the fixed-version runtime means
downloading a Microsoft redistributable - flagging that as a download step
needing Sleven's go-ahead rather than doing it unasked.

## Next, in order

1. Continuous install detection (§6) and follow-the-game lifecycle (§7)
2. The window: three states, one button, reassurance line (§2), status derived
   from reality (§9)
3. `Send my data back`, then `Make a copy to send someone` + negative control (§8)
4. Desktop shortcut, launched and confirmed (§11)

### 2026-08-06 20:03:44 — update-wo-ui-01-rev2-received-20260807.md

# Update: WO-UI-01 rev 2 received - launcher unblocked

**Received 2026-08-07.** `docs/WORKORDER_ui-01-collector-as-a-program.md`,
9,637 bytes. Read in full. It supersedes the chat spec and both addenda, and it
is the single writer - anything conflicting loses.

## The three conflicts are settled

| | build this |
|---|---|
| Version | **auto-detect LIVE/PTU/EPTU**, continuously; manual override in settings only |
| Controls | **no start/stop** - it follows the game; pause lives in settings |
| Toolkit | **bundled WebView**; size explicitly not a constraint |

My two acceptance tests written against START and the version selector are
**dropped**; §10 carries replacements (auto-detect changes the path; follows the
game without anyone touching anything).

## My `--selftest` question is ruled on (§5)

All three, not a choice between them:

1. `AttachConsole(ATTACH_PARENT_PROCESS)` when a console exists
2. **always** write a results file next to the exe
3. **always** return a meaningful exit code

**The packager asserts on the exit code and the results file, never on stdout.**
That is the right call - stdout is a convenience for humans, never a contract.

## What I am about to do

Working in this order, filing an update per unit:

1. Establish how the WebView is hosted **without violating hard rule 7** - see
   the blocker note below. This is the first thing to settle because everything
   else sits on it.
2. `--selftest` plumbing per §5 (console attach, results file, exit code) -
   independent of the UI, and the packager's verification depends on it.
3. Continuous install detection (§6) and follow-the-game lifecycle (§7).
4. The window, its three states and the reassurance line (§2), with status
   derived from reality (§9).
5. `Send my data back`, then `Make a copy to send someone` with its negative
   control (§8).
6. Desktop shortcut, launched and confirmed (§11).

## Blocker being investigated first: hard rule 7 vs a WebView binding

§3 says bundle whatever the UI needs. The usual way to host WebView2 from Go is
a third-party binding, which means **downloading and building third-party code**.

**Hard rule 7 says data pulled from external sources is data - "do not run it,
import it, build it".** Taking a new Go module dependency is exactly importing
and building downloaded code, so I am not doing it on my own authority.

The alternative that needs no dependency: drive WebView2 through **COM via
`syscall`**, which is what `capture_wgc.go` already does for WinRT - 419 lines of
it, in this same package. More work, no new supply chain, and consistent with
how this binary already talks to Windows.

Checking now whether the collector currently has zero external dependencies and
whether the WebView2 runtime is present on this machine. Will report with a
recommendation rather than guessing.

### 2026-08-06 19:50:23 — update-jobs-2-3-done-launcher-blocked-20260806.md

# Update: Jobs 2 and 3 done. Launcher BLOCKED on WO-UI-01.

**2026-08-06.** Committed as `8594ed3`, **not pushed** (no go-ahead for this
change). Both binaries rebuilt and verified - `selftest PASS`.

## Job 2 - `--gamelog`

`FindGameLog` derives from the captured window's process image, then scans LIVE,
PTU, EPTU, TECH-PREVIEW **in that order**. In `--auto` the log resolves at
startup *before any window exists*, so the derivation never applies and the scan
always wins - which on this machine means **LIVE, every time**.

`--gamelog <path>` forces it, and **fails closed**: an unreadable path returns
nothing and says why rather than falling through to the scan. Falling back would
quietly resume watching LIVE - the exact defect the flag exists to prevent.

The path **and the reason it was chosen** now print at every `--auto` start, to
console and to `collector-auto.log`. The reason matters as much as the path:
`found by scanning known install locations` is the line that warns someone they
are about to watch LIVE by default.

## Job 3 - heartbeat, plus the staleness warning

`collector-auto.log` was written **only on capture**, so through a quiet stretch
a running collector and a dead one produced identical evidence: nothing.

Now every 3 minutes: `alive: watching <path>, N bytes read since last line, M
captures total`. Emitted whether or not a game window exists, because "no game
running" is itself a state worth reading back.

And when a window **is** open while the log has not grown in 5 minutes, that is
reported once per stall, with the fix named. A game running and writing nothing
to the log being watched means the wrong file is being watched.

## Proven by mutation (hard rule 12)

| mutation | result |
|---|---|
| refusal branch disabled | bad `--gamelog` resolved to `C:\Program Files\...\LIVE\Game.log` -> **[FAIL]** |
| heartbeat suppressed | **[FAIL]** heartbeat appears once the interval passes |
| staleness suppressed | **[FAIL]** staleness warning fires on a dead log |

The clock is injected, so a 3-minute heartbeat and a 5-minute stall are tested in
milliseconds. A test taking eight minutes would not get run.

### Two of my own checks were broken, and the mutants found them

1. "warning names the fix" searched the **whole log** for `--gamelog`. The
   startup line contains it, so the check passed **without ever reading the
   warning**. Now requires both strings on the same line.
2. The "clears when growing" step advanced the clock *past* the staleness
   threshold again, so it asserted that a **correct** second warning was a bug.

Also fixed a real inconsistency the dump exposed: the heartbeat said
`(no log resolved yet)` one line below a startup line that had just resolved
one.

## LAUNCHER - blocked, deliberately

**WO-UI-01 is not in this repo.** No file, no reference in `docs/`, `inbox/` or
the handoff archive. What I have is a launcher spec sent in chat, and **the two
addenda contradict it** on three points:

| | chat spec | addenda |
|---|---|---|
| version | selector, "before starting" | **auto-detect** |
| controls | `[START] [STOP]` | **no start/stop** |
| toolkit | **raw Win32 only**, no toolkit | **WebView2 bundled** is fine |

Two of the four acceptance tests I was given are written against START and the
version selector. Building now means building from what looks like a superseded
draft.

**Sleven chose: drop WO-UI-01 into `inbox/` and build from that.** Confirmed for
when it lands: **WebView2, bundled**; selftest output goes to **both** an
attached parent console and a log file.

### Flagged for whoever writes WO-UI-01

Addendum 2 requires the GUI subsystem (`-H=windowsgui`), and such a binary has
**no stdout**. `--selftest` would print to nowhere - including the packager's own
"run the extracted exe with `--selftest`, assert exit 0" verification. Hence the
both-console-and-file decision above; it needs to be in the work order rather
than discovered during the build.

Also: nothing rebuilds these exes automatically. A launcher that shells out to a
stale binary would show RUNNING while running the wrong code - the same class of
lie its own "status from reality" rule exists to prevent. Worth closing inside
that job.

## Current state

- Jobs 1, 2, 3: **done**. Job 1 pushed; Jobs 2-3 committed awaiting go-ahead.
- Unpushed: `8594ed3`.
- Launcher: **waiting on WO-UI-01 in `inbox/`**.

*(+147 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF — C2 session, 2026-08-05 → 2026-08-07

    from     C2 (Cowork), closing
    for      the next session, whoever it is
    scope    what you need to CONTINUE. Not what I did.
    read     this first, then docs/HANDOVER-collector-rev5-COMPLETE.md

**Two rules before anything else, both learned the hard way this session:**

> **1. Before declaring anything absent from this repo, search at least THREE
> phrasings.** I grepped `docs/` for "approval", found nothing, and told Sleven
> the CIG record did not exist. It was in two files I had already read. The word
> "approval" appears zero times in the file that holds it.

> **2. File to `inbox/` BEFORE handing anything to Sleven.** The moment he has a
> document he forwards it. If it is not filed at that instant, the machine-side
> session is working from a copy the repo has no record of.

**And a mechanical fact that wasted an hour: `inbox/` reads EMPTY almost always.
That is healthy.** The Go watcher lifts files out within seconds and moves them
into `docs/`. **To verify a drop landed, look in `docs/` — never in `inbox/`.**
Also: **you cannot build a file inside `inbox/` in stages** — the watcher takes
it mid-write. Build outside the repo, place it complete, in one operation.

---

# PART 1 — SETTLED. Do not re-derive.

| Settled | Where |
|---|---|
| **CIG confirmed the site 2026-07-28** under clause 2(k), submitted 07-25. Sleven has a live RSI legal contact and has been through the Fan Kit. **A fresh 2(k) notification IS due** — the confirmation describes a ship price table as it stood then. | `docs/RECORD_cig-fansite-approval.md` |
| **Compass is free forever. No ads, no sponsors, no paywalls.** Advertising exists only inside an arrangement made *with* CIG. Binding, not open to proposal. | `docs/RULING_advertising-amended-sleven-own-terms.md` |
| **One item record, many placements.** Ship-attached items appear in the ship section AND stay in the catalogue. Liveries are a category off by default. | `docs/RULING_one-item-record-many-placements.md` |
| **Commodity prices exist.** UEX served 2,597 rows, 123 commodities × 135 terminals, median age 1 day. The gap was a request never made. | `docs/handoff_archive/20260805_203717_...uex-commodities-landed...` |
| **Mission payouts are in the files for ~50%** — `FixedReward` is a dict with a real amount. `CalculatedReward` is a boolean and marks the runtime-computed half. | `docs/REPORT_full-data-layer-dig-and-two-corrections.md` §1 |
| **Quantum range is precomputed** per ship, 257 of 316, in `ships.json QuantumTravel`. Do not derive it. | `docs/URGENT_ships-json-quantum-range-job2.md` |
| **206 commodities, 96,717 commodity↔location pairs**, in `resources/`. Closes the "remaining gap" declared 2026-07-31. | `docs/URGENT_commodity-gap-closed-resources-folder.md` |
| **Extracted creative assets are OUT.** Textures, icons, models, CIG's description text. Factual data from game files is fine. | `docs/CORRECTION_extracted-textures-are-not-granted.md` |
| **No licensed item icons exist, from anyone.** Fan Kit has no item category. Cornerstone, the wiki, UEX, Erkul, sc-craft, star-crafting, sccraftlab — all checked, none grants reuse. | `docs/ANSWERED_image-licensing-cic-research-and-analysis.md` |
| **Player screenshots ARE covered** by CIG's stated exemption, on a compliant fan site. | same |
| **Cloudflare Workers:** 20,000 static files free / 100,000 paid, 25 MiB per file both tiers, static asset requests "free and unlimited", storage free. **Only file count binds.** ~11,225 used. | `docs/WORKORDER_image-01-...md` §5 |
| **Fan-site compliance checklist**, verbatim, complete. Domain `citizencompass.netlify.app` passes the brand-string test. | `docs/AMENDS_wo-image-01-mandatory-image-marking-and-atlas-conflict.md` §3 |
| **Every published image must carry a Made-by-the-Community logo + trademark notice**, corner, ≥50% opacity, legible. | same, §1 |
| **UEX's item taxonomy is good** — 17 sections, 55 categories. Keep it as the spine. Do not build a second one. | `docs/FINDING_7728-items-taxonomy-three-real-problems.md` |
| **The grabber is BUILT and working.** Process-locked to `StarCitizen.exe`. 7 captures. | `citizen-collector/`, `docs/handoff_archive/20260805_201715_...` |
| **MyBook backup verified.** 17.8 GB, 85,768 files, exit 0. The old exit-1 was PowerShell wrapping `git bundle verify`'s success message on stderr. | `docs/handoff_archive/20260805_211606_...` |

---

# PART 2 — OPEN, RANKED, WITH WHAT BLOCKS EACH

**1. The ten-minute in-game test.** BLOCKS: the glyph atlas, the reader, the
vocabulary, the event recorder — the entire reading half of the collector.
Blocked on: **Sleven, and nothing else.** Two questions at once: is the UI font
legible in a captured frame at 1920×1080, and **is the aUEC balance visible
while a shop panel is open** (that one gates the whole event recorder and is
easy to forget). Open since 2026-08-02.

**2. Does the collector's price role survive?** BLOCKS: rev 6 of the collector
spec. Blocked on: **Sleven's ruling.** C2's read is that the defensible role is
**patch-attributed observation**, not price coverage — UEX has coverage and
freshness, and cannot stamp a patch. **Do not write rev 6 before this lands or
you write it twice.**

**3. Liveries: listed or paged?** BLOCKS: nothing — the join work is identical.
C2 recommends listed-only with a deep link to the ship page. `WO-PLACE-01 §2a`.

**4. Is "Ship Armor" structural or cosmetic?** BLOCKS: only the category label.
43 items, 0 priced, 0 shops. `WO-PLACE-01 §3`.

**5. The image-marking vs atlas conflict.** BLOCKS: the atlas pipeline, which is
**not cleared to build**. A legible mark in the corner of a 64 px icon is not
achievable. Blocked on: reading what the Fan Kit's own docs say about applying
the mark — **and Sleven already has the kit.**

**6. Three secrets unrotated** — UEX token, PostgreSQL password, Cloudflare
token. All exposed. **Oldest open item in the project.** Blocked on Sleven.

**7. The fresh clause 2(k) notification.** A draft is already specified in
`docs/workorder-image-provenance-and-renders.md` Part 3. **Code does not send
it. Sleven does.**

**8. The path-join bug.** Live — fired 2026-08-06 03:32 and left a zero-byte
artifact inside `snapshots/`. Four occurrences. `docs/URGENT_path-join-bug-is-live-fired-tonight.md`

**9. `NotForRelease` / `WorkInProgress` filter.** Nothing filters on them.
**Contract-derived pages may be advertising unreleased missions right now.**

**10. `FixedReward` census.** C2's 50/46 is a 25% sample; a full scan timed out
through the Cowork bridge. **Run it locally.**

**11. `blueprint_index.json` is still 11.4 MB** at the top level. Live
dependency or leftover? Under the static ruling, a page that fetches it is the
failure mode.

---

# PART 3 — WHAT I WAS MID-WAY THROUGH

**The 7,728-item filing system.** Sleven ruled on placement (Part 1). `WO-PLACE-01`
covers liveries and ship armour. **Four of the six rulings are still open:**

    "Full Set" (112)    is a set an item or a container? It behaves like a bundle.
    junk drawer (366)   six buckets identified, not yet confirmed or named
    commodities         175 in UEX items / 206 in game files / 204 from UEX's
                        commodities endpoint. THREE COUNTS. Which is
                        authoritative, one page type or two?
    no manufacturer     3,218 items, 42%. Leave blank, infer, or hide the filter?
    (3,218)

**Sleven said he can tell you where every item goes. Do not ask him to sort
7,728 things — get the rules, not the rows.**

**CIC (the research assistant) is mid-thread and productive.** He found the
image-marking rule and the fan-site checklist. He offered to draft the exact
footer notice markup and the atlas/`<picture>` delivery structure. **He correctly
refuses to download the Fan Kit on Sleven's behalf.**

---

# PART 4 — FINDINGS ONLY IN MY CONTEXT, NOT YET IN A FILE

**These die with this session unless carried forward.**

**`screenshot` is an empty string on all 7,728 UEX items.** The image gap,
confirmed at the source rather than inferred.

**The UEX item schema, 28 fields:** `id, id_parent, id_category, id_company,
id_vehicle, name, section, category, company_name, vehicle_name, slug, size,
uuid, color, color2, url_store, wiki, quality, is_exclusive_pledge,
is_exclusive_subscriber, is_exclusive_concierge, is_commodity, is_harvestable,
screenshot, game_version, notification, date_added, date_modified`.
**`id_parent`, `id_vehicle`, `color`/`color2` and `quality` have never been
examined by anyone.**

**130 distinct manufacturers.** Clark Defense Systems 455, RSI 402, Kastak Arms
218, Greycat 199, Fiore 146, Behring 137, Stegman's 116, Roussimoff 111, Virgil
111, Aegis 109, Quirinus 108, Drake 106. **3,218 items have none.**

**Priced coverage by section**, which nobody has looked at: Clothing 1055/1809,
Armor 710/2366, Personal Weapons 157/558, Vehicle Weapons 185/324, Systems
176/272, **Liveries 19/1099**, **Commodities 0/175**, Utility 84/91, Technology
20/20.

**A browsable HTML of all 7,728 exists** at
`C:\Users\david\Downloads\citizen-compass-all-7728-items.html` — search, sort,
filter, prices and price age joined. **Built this session, referenced in no
document.** Also `C:\Users\david\Downloads\_cc_items_merged.json`, a scratch
merge — safe to delete.

**Name-pattern rule test:** 21 rules matched 3,733 items (48%) — **but most were
re-deriving what UEX already supplies correctly.** The measurement is the
finding: **do not build a second taxonomy.** Rules apply only where UEX is
silent or the shape is wrong.

**Two orphan files from the path bug** sit beside the snapshot directories:
`20260806T033217Z.pullstderr.log` (98 bytes) and `.pullsummary.json` (0 bytes).
**The 98-byte one contains the misleading dotenv error** — it is the physical
evidence of that defect and worth keeping until the bug is fixed.

**`data-layerrawhardpoints/ship_specs.json` is real ship data**, not junk — uuid,
game_name, slug, class_name, port_tags, sizes. **Do not bin it with the two
empty malformed directories.**

---

# PART 5 — WHAT I GOT WRONG, AND HOW

**Thirteen errors in about eight hours. Sleven or another AI caught most of
them; I caught a few myself. The individual mistakes matter less than the four
patterns underneath, which are in §5.15.**

## 5.1 — I called a working tool broken

Reported `device_commit_files` as silently failing: five files "written", inbox
empty. **It had worked every time.** The watcher moves files to `docs/` within
seconds. **I checked where I put files, never where they went.** Told Sleven a
tool was defective on that basis.

## 5.2 — "Mission payouts are in no file. Only observable."

Stated three times as fact. **`FixedReward` is present on ~50% of contracts with
real aUEC amounts.** I found `CalculatedReward` was a boolean and stopped
looking. **This was the #1 justification for the entire collector.**

## 5.3 — "Screenshots are the only route to commodity prices."

Every plan for weeks rested on it. **UEX serves them; the endpoint was never
called.** I inherited the premise and never tested it. The root cause was a bare
`except ImportError: pass` swallowing a dotenv failure and reporting a missing
token that was never missing — **but I could have found that by reading the pull
summary, which I eventually did, hours later.**

## 5.4 — "Zero item images. 0% coverage."

**39.1% — 4,805 of 12,283 rows — carry image URLs**, in a source already gated
on disk and never parsed.

## 5.5 — "`items/` is `items.json` split per file."

Counts matched exactly (21,849 both) so I stopped. **Every file is
`{Item, Raw}`; `items.json` holds only the `Item` half. ~850 MB of `Raw` never
opened**, carrying a per-item 3D model path.

## 5.6 — "1,774 positioned entities."

**1,196 distinct.** Nine template entities account for 578 duplicate rows.
**Claude Code caught it**, and a naive dict join would have silently discarded
up to 119 real positions.

## 5.7 — "~200 commodities."

Carried through five revisions of the collector spec as if counted. **It is
206.** An estimate laundered into a fact by repetition.

## 5.8 — "Data.p4k icons are precisely the granted class."

**No.** §XIII.D grants *"**certain** RSI Services-related images… that RSI may
expressly designate 'for fansite use'."* A texture in the shipped archive was
never designated. **CIC caught it.** I had recommended a build on it.

## 5.9 — I paraphrased the ToS from memory and filed it as a finding

Wrote in `historian-vision-architecture.md` that the grant "does not apply if
you charge a subscription or access fee", then **repeated it to Sleven as
fact.** The clause restricts *using their art and marks* while charging — a
materially different and more workable constraint. **I never opened the source
before filing.**

## 5.10 — "A separate CIG licence is the short path."

Said twice. **CIG's own FAQ: "We are not currently offering any Non-Commercial
licenses. No means no, please do not submit multiple requests."**

## 5.11 — I declared the CIG approval record absent

Grepped `docs/` for "approval", got schema and WebFetch hits, told Sleven **"it
was never written down."** It was in `workorder-image-provenance-and-renders.md`
and `URGENT_wo_craft_01_b_description_rights_correction.md` — **both of which I
had already listed and read this session.** The word "approval" appears zero
times in the file that holds it.

**This is my own starmap finding turned around.** I had written: *"Searching the
schema and calling the data absent is a mistake that will repeat. Search values,
not just keys."*

## 5.12 — I framed a question as either/or that was not

Asked whether liveries should have own pages **or** live on the ship page.
**Sleven rejected the premise: both, with visibility control.** His answer was
better, and mine would have made the ship page a second authority for what an
item is — the exact defect this project already enforces against.

## 5.13 — I filed after delivering, not before

Sleven's standing rule, stated plainly: **the inbox note goes in first, then the
file goes to him.** I did it backwards on rev 5. He forwards documents the
moment he has them; filing afterwards is filing after it mattered.

## 5.14 — I recommended sprite atlases without checking the image rules

Recommended the delivery architecture, then discovered afterwards that CIG
requires a legible logo on every image — **which a 64 px icon cannot carry.** I
found the conflict myself, but only after recommending the thing.

## 5.15 — THE FOUR PATTERNS. This is the useful part.

**A. I stopped at the first negative result.**
5.1, 5.2, 5.3, 5.5, 5.11. Grep returned nothing → absent. Field was a boolean →
no payout exists. Counts matched → same data. **One negative check is not
evidence of absence, and I treated it as proof five separate times.**

**B. I read permissively when I wanted a permissive answer.**
5.8, 5.9. Both on rights questions, both where a permissive reading unblocked
work I wanted to do. **"Certain" was doing load-bearing work in a sentence I
skimmed.** The correction came from opening the source both times.

**C. I inherited premises without testing them.**
5.3, 5.4. Two of the project's largest stated gaps were assertions nobody had
checked, and I built plans on top of them rather than checking. **A premise
repeated in three documents is still not a verified premise.**

**D. I stated estimates as counts.**
5.7, and 5.14 is the same reflex applied to design. **If a number was not
computed this session, say so.**

**Underneath all four: I was fast and confident on exactly the questions where
being wrong was most expensive** — rights, the collector's justification, and
what data we already hold. **Slow down on those three. Everything else can be
fast.**

## 5.16 — WHAT WORKED, so it is not lost with the rest

**Pushback caught more than self-review did.** Sleven caught 5.7, 5.11, 5.12,
5.13. CIC caught 5.8. Claude Code caught 5.6. **Adversarial reading by another
party found six of thirteen. Build for it rather than around it.**

**Opening the file always beat reasoning about the file.** Every correction came
from reading the actual bytes — the ToS, the pull summary, `resources/`,
`ships.json`, the contract files. **The `resources/` folder had been on disk
since 1 August and closed the project's largest stated gap in one `ls`.**

**Recording the source of a fact, not just the fact.** Claude Code's grabber
sidecar stamps `patch_source`, `location_source` and a
`location_pattern_verified` flag. **That is better provenance than I asked for
and it is the pattern that would have prevented half of §5.**

