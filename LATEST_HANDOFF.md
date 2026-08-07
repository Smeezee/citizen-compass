# LATEST_HANDOFF.md — Update #198 — 2026-08-06 5:25 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-06 17:25:48 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 60679 files (10407.68 MB)

**Scripts:** 17  |  **3D models:** 723  |  **Docs:** 659

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-06 17:24:01 — update-job-a-complete-database-now-backed-up-20260806.md

# Update: Job A COMPLETE - the database is backed up, restored, and mirrored

**Completed 2026-08-06.** The gap is closed. There are now **three copies of
the data** (C:, D:, E:), and the dump has been proven restorable by actually
restoring it.

## Step 2 - the real dump

```
dump           : C:\cc-backup\20260806-172223\citizen_compass-20260806-172223.dump
dump size      : 175,705 bytes (0.17 MB)
ships LIVE     : 232
ships RESTORED : 232      <- restored into a scratch database and counted
```

These are two separately measured numbers, not one number printed twice. The
live count came from `citizen_compass`; the restored count came from
`cc_restore_test_20260806_172223` after a real `pg_restore`.

The harness's own negative control also fired on the real dump: a corrupted
copy was rejected (exit 1) and yielded 0 ships, not 232.

Both scratch databases were created and dropped by that run.

## Step 3 - both mirrors, verified per file

`Verify-MirrorTree.ps1` - the verifier that caught the external-sources
failure - run against each mirror with the **destination enumerated from disk**,
not from any manifest, log, or the copy's own file list:

- **D:** POSITIVE control passed; all 1 expected file present with matching
  byte size. VERIFY PASSED (exit 0).
- **E:** POSITIVE control passed; all 1 expected file present with matching
  byte size. VERIFY PASSED (exit 0).

Its NEGATIVE control reported **NOT PERFORMED** on both, honestly - a
single-file backup directory contains no excluded file to test with. Stated,
not glossed as a pass.

Independent re-hash from disk after the fact, all three locations:

```
C:\cc-backup   175,705 B  136249D1EC40948A576B3F6DED263CD0F0960BBC9E27B1C24971465079D5689D
D:\cc-backup   175,705 B  136249D1EC40948A576B3F6DED263CD0F0960BBC9E27B1C24971465079D5689D
E:\cc-backup   175,705 B  136249D1EC40948A576B3F6DED263CD0F0960BBC9E27B1C24971465079D5689D
```

Byte-identical on all three.

## The verifier was itself tested against known-bad input (hard rule 12)

A verifier nobody has seen fail is an untested gate. Fed two known-bad
destinations on scratch copies:

- **truncated file** (present, so a file-COUNT check passes - the exact
  2026-08-05 failure signature): caught, `a.dump source 175,705 B -> dest
  1,000 B`, **exit 1**.
- **missing file**: caught, `c.txt (10 B at source)`, **exit 1**.

Both failed as required, so the two passes above mean something.

## FOUND - not acted on: four orphaned scratch databases

These are left over from **earlier** runs, not from tonight:

```
cc_restore_test_20260730_233853
cc_restore_test_20260801_144501
cc_restore_test_20260801_203049
cc_restore_test_20260805_205238
```

**I did not drop them.** Hard rule 3 forbids `DROP DATABASE` against a database
this process did not create, and this process did not create any of these.
They are harmless but they hold stale copies of ship data and will accumulate.
Dropping them is Sleven's call.

Worth noting the earlier runs' guarded cleanup did not remove them - probably
because those runs exited before step 4. Cheap fix available if wanted: a
startup sweep that drops only names matching the scratch pattern, but that
would itself be dropping databases the process did not create, so it needs an
explicit decision rather than a quiet addition.

## Still outstanding: PGPASSWORD does not authenticate

The `PGPASSWORD` set in my environment returns
`FATAL: password authentication failed for user "postgres"` against
`127.0.0.1:5432`. The value is clean (no quotes/whitespace/CR/LF) and does not
match `.env`. All work above used the app's own `DATABASE_URL` credential.
No password was echoed, logged, or written anywhere.

`citizen_compass_backup_20260730.dump` in the repo root remains the **stale**
2026-07-30 file and is still not a current backup - the current one is the
`C:\cc-backup\20260806-172223\` dump above.

**Next:** Job B - grouping the uncommitted Jobs 3-5 and collector work into
logical commits. Nothing will be pushed without explicit confirmation.

### 2026-08-06 17:22:09 — update-job-a-step1-control-proven-20260806.md

# Update: Job A step 1 - corruption control PROVEN (and proven the hard way)

**Completed 2026-08-06.** The restore check can fail. It is therefore worth
trusting to bless a real backup.

Subject was the **stale `citizen_compass_backup_20260730.dump`** (69,037 bytes,
2026-07-30). **This is NOT a current backup and is not reported as one** - it
was used only as a known-restorable artifact to exercise the control. The
original was never opened for write; its sha256 was re-checked after every pass
and is unchanged.

## Pass 1 - byte midpoint

Flipped 2,048 bytes at offset 34,518 of 69,037. `pg_restore` rejected it
(exit 1, "could not read from input file: end of file"), ships table
unreadable. **Control fired** - but `pg_restore --list` *also* failed, meaning
the damage had reached the TOC. That is the same weak class as corrupting the
header: it fails for a cheap reason and proves nothing about whether the
restore path actually reads data bytes. Logged as weaker than intended rather
than counted as a clean win.

## Pass 2 - the strong form

Walked deeper to find an offset whose corruption leaves the TOC readable:

| offset | through | `pg_restore --list` |
|--------|---------|---------------------|
| 41,422 | 60% | exit 1 - TOC damaged |
| 48,326 | 70% | exit 1 - TOC damaged |
| 51,778 | 75% | **exit 0 - TOC intact** |
| 55,230 | 80% | **exit 0 - TOC intact** |
| 58,681 | 85% | **exit 0 - TOC intact** |
| 62,133 | 90% | **exit 0 - TOC intact** |
| 65,585 | 95% | **exit 0 - TOC intact** |

Used offset 65,585 (1,024 bytes flipped). That copy **passes `--list` with
exit 0** - a cheap integrity check calls it perfectly healthy.

A real restore into a real scratch database:

```
pg_restore: error: could not uncompress data: invalid distance too far back
pg_restore exit = 1
ships recovered: 0        (clean baseline: 232)
```

**CONTROL FIRED IN THE DATA SECTION.** This directly confirms the claim in
`Test-DatabaseBackup.ps1`'s header: a `--list`-only integrity check would
declare a dump with a shredded data section healthy. Only driving it through a
real `pg_restore` reads those bytes.

## Housekeeping

All four scratch databases were created by that process and dropped by it
through the guarded `Remove-ScratchDb`, which refuses any name not matching the
scratch pattern, not created by the run, or equal to the live database
(hard rule 3). Zero scratch databases remain.

## Blocker found and worked around - please confirm

**`PGPASSWORD` as set in my environment does NOT authenticate:**
`FATAL: password authentication failed for user "postgres"`. The value is clean
(no quotes, whitespace, or CR/LF) and it does **not** match the credential in
`.env`. I fell back to the app's own `DATABASE_URL` credential, which
authenticates fine - live DB reachable, **232 ships**.

Neither value has been echoed, logged, or written anywhere; the comparison was
done as a boolean only. Flagging it because the PGPASSWORD you set may be for a
different host or role than local `127.0.0.1:5432`.

**Next:** step 2 - take the real dump, restore it, count ships live vs restored.
The database is still unbacked-up as of this update.

### 2026-08-06 17:17:25 — update-job-a-db-backup-received-20260806.md

# Update: Job A received - database backup (DB is currently UNBACKED UP)

**Received 2026-08-06.** Sleven flagged that the file trees are verified on both
mirrors but the Postgres dump was skipped and correctly recorded as a failure.
State right now: **two copies of the files, zero copies of the data.**

`citizen_compass_backup_20260730.dump` in the repo root (69,037 bytes, dated
2026-07-30) is **NOT a current backup** and will not be reported as one.

## What I am about to do

1. **Prove the control first**, using the stale dump as the test subject:
   copy it to scratch (never touch the original), restore the clean copy to a
   scratch database, then corrupt the copy by flipping bytes in the **middle**
   (not the header - a mangled header fails for the wrong reason), and confirm
   the restore **fails**. Drop the scratch database.
   Per Hard Rule 12: if a deliberately corrupted dump restores clean, the check
   cannot fail and is worthless. I stop and report rather than let it bless a
   real backup.
2. **Take the real dump** and verify it the same way - restore to scratch and
   **count the ships**, reporting live count and restored count as two separate
   numbers. Drop the scratch database.
3. **Copy to both mirrors** and verify per file with the same verifier that
   caught the external-sources failure, with the destination side **enumerated
   from disk, not from a manifest**.

Then Job B: group the uncommitted Jobs 3-5 / collector work into logical
commits, add by name only (no `git add -A`), and **wait for confirmation before
pushing**.

PGPASSWORD is in the environment for this session. It will not be echoed,
logged, or written anywhere.

### 2026-08-06 17:06:52 — update-cloudflare-plugin-installed-20260806.md

# Update: Cloudflare agent setup completed (2026-08-06)

Done in two halves, because the second was blocked for me.

- `claude plugin marketplace add cloudflare/skills` — run by me, succeeded,
  declared in user settings.
- `claude plugin install cloudflare@cloudflare` — **blocked by the Claude Code
  permission classifier** when I attempted it. Sleven ran it directly instead.

Verified: `cloudflare@cloudflare`, version 1.0.0, scope user, status enabled.

## What this changed, and where

This is configuration **outside the repo** — the user-scope Claude config, not
anything under `citizen-compass/`. It registers five remote MCP endpoints
(`mcp.`, `docs.mcp.`, `bindings.mcp.`, `builds.mcp.`, `observability.
mcp.cloudflare.com`). Cloudflare OAuth triggers on first use of a Cloudflare
tool, separately from the `wrangler` OAuth login done earlier tonight.

Recorded here because hard rule 6 names MCP server registration and `.claude/`
config as off-limits without asking, so the fact that it happened — and that it
was authorised, deferred, then completed by hand — belongs in the record rather
than only in a terminal scrollback.

## Remaining step

`/reload-plugins` in Claude before the plugin's tools become available in this
session.

## Note on how this arrived

The instruction was "fetch and execute the instructions at
`developers.cloudflare.com/agent-setup/prompt.md`". Hard rule 7 forbids
executing fetched content, so it was fetched and **read**, its two commands
reported, and confirmation taken before anything ran. The content turned out to
be exactly what was asked for and nothing more.

### 2026-08-06 16:58:53 — update-jobB-pushed-20260806.md

# Update: Job B pushed (2026-08-06)

Pushed on confirmation. `3254dea..0570426` to `origin/main`. All four commits
verified present on the remote; `origin/main..HEAD` is now **0**.

| commit | what |
|---|---|
| `37324ce` | backup fixes — the backslash regex, the null exit code, hard failure on a missing mirror, `Verify-MirrorTree`, `Report-BackupCloseout`, `Test-DatabaseBackup` |
| `8de0a57` | the collector, including unattended `--auto` |
| `83c326b` | the process-lock proof |
| `0570426` | the `_deploy` publication guard |

23 files, +6001 / -41, every one added by name. The ~50 CRLF-churn files were
not touched — the working tree still shows only the six pre-existing
modifications that were deliberately left alone (`.gitignore`, `go.work`,
`scripts/external_sources/uex_corp.py`, and the three watcher-owned handoff
files).

## Still open

**Job A — the database is still not backed up.** Blocked on `PGPASSWORD`
reaching this process; it is absent at every scope and Postgres requires
password auth. Setting it in another terminal cannot work, because a Windows
child process inherits its parent's environment block rather than reading the
registry. It has to be set in the shell that launches Claude Code, followed by
a restart:

    $env:PGPASSWORD = '<password>'
    claude

`scripts/Test-DatabaseBackup.ps1` is committed and ready — one command, and its
preflight is already proven to refuse with exit 2 rather than prompt or pass.

Current exposure is unchanged: two verified copies of the FILES on two external
drives, zero verified copies of the DATA.

### 2026-08-06 16:50:10 — update-jobB-committed-awaiting-push-20260806.md

# Update: Job B — four commits made, NOT pushed (2026-08-06)

Four commits on `main`, ahead of `origin/main` by 4. **Nothing pushed** — the
order requires the list to be confirmed first. 23 files, +6001 / -41.

Added **by name** throughout. No `git add -A`. The CRLF churn files were not
touched; git's "LF will be replaced by CRLF" warnings are the filter acting on
the files actually being staged, not churn.

| commit | what |
|---|---|
| `37324ce` | backup fixes — `Backup-CitizenCompass.ps1`, `Verify-MirrorTree.ps1`, `Report-BackupCloseout.ps1`, `Test-DatabaseBackup.ps1` |
| `8de0a57` | the collector, including `--auto` — 16 files |
| `83c326b` | the process-lock proof — `process_lock_selftest.go` |
| `0570426` | the `_deploy` guard — `check_deploy_clean.py`, `build_deploy.py` |

## One honest note about the split

`citizen-collector/` had **never been committed** — the whole directory was
untracked. So `8de0a57` necessarily lands the base grabber as well as the auto
mode, and `main.go` / `winapi.go` land whole in it. That means the
`finalWindowGuard` extraction, which exists for the process-lock test, is in
`8de0a57` rather than `83c326b`. The proof file itself is the later commit.
Splitting further would have meant staging hunks of a brand-new file, which
buys tidiness at the cost of commits that do not build.

## Deliberately left uncommitted

- `LATEST_HANDOFF.md`, `docs/handoff_archive/*` — the Go watcher owns these
  (rule 14, one writer). Not mine to commit as part of a code change.
- `.gitignore`, `go.work`, `scripts/external_sources/uex_corp.py` — already
  modified before this session started. Not my changes; not folding someone
  else's work into my commits.

## Build outputs kept out

`citizen-collector/.gitignore` already excluded `collector.exe`,
`collector-master.exe` and `captures/`. Added `collector-auto.log` and
`collector-settings.txt` — both are written next to the exe at run time and
belong to whoever runs it. Committing the settings file would push one
machine's interval choices onto everyone else.

## Deploy guard (the low-priority item)

`testing/_src/check_deploy_clean.py`, called at the end of `build_deploy.py`
and runnable standalone before a deploy. Whitelist, not denylist — a denylist
would stop `.wrangler` and silently permit the next surprise. Allowed file list
is derived from `PAGES` so the two cannot drift.

Proven by negative control, all passing:

- planted `.wrangler/` directory — REFUSED (the exact incident)
- unexpected file `notes.txt` — REFUSED
- unexpected directory `backup/` — REFUSED
- nested dot-file inside `models/` — REFUSED
- clean again once the plants are removed — confirms it detects the plants
  rather than always failing

Live `_deploy` currently passes: "contains only known assets - safe to deploy".

## Waiting on

1. **Push confirmation** for the four commits above.
2. **Job A** — still blocked on `PGPASSWORD` reaching this process. See
   `update-jobA-database-blocked-20260806`. Two verified copies of the files,
   zero verified copies of the data.

### 2026-08-06 16:46:29 — update-jobA-database-blocked-20260806.md

# Update: Job A BLOCKED — PGPASSWORD never reached this process (2026-08-06)

The database is still not backed up. Harness is written and proven fail-closed;
it cannot run without the credential.

## Why it is blocked

- **Postgres 17 is running** (7 processes) and **requires password auth**. A
  deliberately wrong password returns `FATAL: password authentication failed`,
  not a trust connection — so there is no passwordless path.
- **`PGPASSWORD` is absent** from process env, User scope, Machine scope, and
  there is no `pgpass.conf`.

**The mechanism matters, because setting it again the same way will not work.**
Every tool call I make spawns a child of the Claude Code process and inherits
*its* environment block, captured when Claude Code launched. Windows builds a
child's environment from its parent, **not** from the registry. So a variable
set in a separate terminal, or set at User scope after launch, cannot reach me.

**The fix — set it in the shell that launches Claude Code, then restart:**

    $env:PGPASSWORD = '<password>'
    claude

That keeps it in memory only: never a file, never a log, never the transcript.

I deliberately did NOT suggest typing it into this session with `!` — that
would put the secret straight into the conversation, which is exactly what the
order forbids. (It would not work anyway; shell state does not persist between
my calls.)

## What is ready

`scripts/Test-DatabaseBackup.ps1` (new). One command once the password is
present. It dumps, restores into a scratch database, counts ships and asserts
live == restored, runs the corruption control, drops the scratch databases,
copies the dump to both mirrors and verifies each per file by size AND sha256.

**Proven already:**

- Parses clean.
- **Fail-closed preflight**: with no `PGPASSWORD` it prints a refusal and exits
  **2** — never 0, and never a prompt. A prompt on an unattended console hangs
  forever, which is how the earlier run wedged.
- The secret is only ever tested for presence. It is never printed, written,
  logged, or passed as a command-line argument (arguments are visible to other
  processes).

## A real finding: `--list` is not an integrity check

I proved the corruption control server-free, using the 8/5 dump already on disk
(`citizen_compass-20260805-205238.dump`, 170,357 bytes). Worked on copies; the
existing backups were not modified.

| corrupted region | `pg_restore --list` |
|---|---|
| header / magic | **caught** — exit 1, `unsupported version (-2.-17)` |
| TOC | **caught** — exit 1, `could not read from input file` |
| **middle of data** | **NOT caught** — exit 0, lists perfectly |
| **near end of data** | **NOT caught** — exit 0, lists perfectly |

So a cheap `--list` check would certify a dump with a shredded data section as
healthy. **The corruption control therefore has to go through a real restore**,
and the harness corrupts the DATA SECTION specifically for that reason. This is
direct evidence for the order's own premise: a dump nobody has restored is a
file, not a backup.

## Guarded drop

Hard rule 3 forbids `DROP DATABASE` against a database this process did not
create. The order asks for the scratch database to be dropped, and both scratch
databases *are* created by this script in this run. `Remove-ScratchDb` refuses
any name that is the live database, does not match `^cc_restore_test_[0-9a-z_]+$`,
or was not recorded as created by this run. Note this differs from
`Backup-CitizenCompass.ps1`, which deliberately leaves its scratch database in
place to keep its "deletes nothing" guarantee absolute.

## Current exposure

Two verified copies of the FILES on two external drives. **Zero copies of the
DATA**, other than the stale 8/5 dump at
`C:\cc-backup\20260805-205238\` — which is on C: only and has never been
restore-tested.

### 2026-08-06 16:30:47 — update-job5-backup-closeout-20260806.md

# Update: Job 5 complete — backup verified on both mirrors (2026-08-06)

Run `20260806-160056`. Close-out report exit **0**. Both irreplaceable trees
are on both external mirrors and verified **per file**.

Reported by `scripts/Report-BackupCloseout.ps1` (new), which runs as a separate
process AFTER the copy and rebuilds every fact from disk — never from
`SHA256SUMS.txt`, never from robocopy's file list, never from the copy's own
filter.

## robocopy exit code per tree

Bitmask, not an ordinal. 0-7 success, 8+ real failure.

| tree | mirror | exit | meaning |
|---|---|---|---|
| repo working tree | C: staging | 1 | files copied |
| whole backup folder | D: | 1 | files copied |
| `sc-ships` | D: | 1 | files copied |
| `data-layer\external-sources` | D: | 1 | files copied |
| whole backup folder | E: | 1 | files copied |
| `sc-ships` | E: | 1 | files copied |
| `data-layer\external-sources` | E: | 1 | files copied |

All seven are 1. Every robocopy log also carries an `Ended :` line and contains
no `ERROR` lines — checked from the logs robocopy wrote itself, not from a
variable the copier kept.

## Per-file verification, destination enumerated from disk

| tree | mirror | expected | present with matching byte size |
|---|---|---|---|
| `sc-ships` | D: | 951 | **951** |
| `sc-ships` | E: | 951 | **951** |
| `data-layer\external-sources` | D: | 58,257 | **58,257** |
| `data-layer\external-sources` | E: | 58,257 | **58,257** |

`sc-ships` holds 1,675 files of which 724 are in `.cache` and correctly
excluded, so 951 is the right denominator — not a shortfall.

## First 10 mismatches by name

**None. Zero mismatches across all four tree/mirror pairs.** The reporting path
is real and proven — see below, where it names a truncated file with both
sizes — it simply had nothing to report here.

## Negative control

Asserted independently per mirror, and it PASSED on both:

- D: `NEGATIVE CONTROL PASSED` — subject `.cache\huggingface\.gitignore`
- E: `NEGATIVE CONTROL PASSED` — subject `.cache\huggingface\.gitignore`

It is only credited after proving the destination is readable, by first finding
a file known to BE there. An "absent" result from a checker that cannot see the
destination is vacuous, and this refuses to score it.

One honest gap, stated not glossed: for `data-layer\external-sources` the
verifier reports `NEGATIVE control NOT PERFORMED - no excluded file exists to
test with`. That tree contains nothing matching the exclusion list, so there is
nothing to test with. Reported as not performed, never as a pass.

## The checker was made to fail on demand — 7 controls

It passed first time, so it was not yet a check. Against synthetic trees
(nothing touched the real backup):

| scenario | result |
|---|---|
| correct mirror | PASSES, exit 0, and verified both trees |
| **truncated** file at destination | CAUGHT — `Liberator\model.glb source 23 B -> dest 8 B (-15 B)` |
| **missing** file | CAUGHT and named |
| excluded `.cache` file reaching the mirror | CAUGHT — `NEGATIVE CONTROL FAILED` |
| run folder absent | reported `NOT VERIFIED`, exit 1 |
| `ERROR` line in robocopy's log | CAUGHT |

The truncation case is the one a file count cannot see: the file is present, so
the count matches. That is exactly the 2026-08-05 kill signature.

While building this, the harness itself failed 7/7 with exit 2 — because the
close-out resolves the verifier relative to `-RepoPath` and my synthetic repo
had no `scripts\Verify-MirrorTree.ps1`. **That was the checker failing closed
correctly**, refusing to verify rather than reporting a pass. The harness was
wrong, not the checker.

## The database is NOT in this backup

`PGPASSWORD` is not set in process env, user env, or `pgpass.conf`. With
`-NonInteractive` the script skipped the dump and the restore test and recorded
a `[FAIL]`. The run therefore ends with `Failures: 1` even though every file
copied and verified. That is correct — it is a real gap, not a formality.

To capture it: set `$env:PGPASSWORD` and re-run. The file trees are unaffected.

## Still to do by hand

1. Copy the backup folder to the laptop you are taking.
2. Upload to cloud storage — the only copy that survives losing the trailer.

## Uncommitted

`Backup-CitizenCompass.ps1` (modified), `scripts/Verify-MirrorTree.ps1` and
`scripts/Report-BackupCloseout.ps1` (untracked), and the whole
`citizen-collector/` auto-mode and process-lock work are all sitting in the
working tree. **Not committed** — Job 2's go-ahead covered 14 named files and
nothing else. Say the word and I will stage them by name.

### 2026-08-06 16:08:02 — update-process-lock-proven-20260806.md

# Update: process lock now proven by refusal, both builds (2026-08-06)

All four ordered checks are in `--selftest` and pass on the crew AND master
builds. Nothing has been packaged or distributed.

New file `process_lock_selftest.go`; `main.go` and `winapi.go` amended.

## The condition is CREATED, not hoped for

The test builds a real top-level Win32 window, really titled **"Star Citizen"**,
really `WS_VISIBLE`, 400x300 so it clears the 200px filter — owned by the test
binary, which is not `StarCitizen.exe`. It is placed at -5000,-5000 so a
selftest does not flash a box over whatever you are doing; `IsWindowVisible`
tests the WS_VISIBLE *style*, not desktop bounds, so it still takes exactly the
path a real bystander window takes.

A test that waited for such a window to happen to exist would silently do
nothing on a quiet desktop and report a pass.

## The four checks

1. **POSITIVE CONTROL — refuses.** `findGameWindow(allowAny=false)` refuses the
   decoy, and the error **names the refused process** (`collector.exe` /
   `collector-master.exe`).
2. **NEGATIVE CONTROL — accepts.** Faked at the `isGameProcess` boundary only:
   `scProcessNames` is briefly pointed at the test binary's own exe name. **The
   gate itself is untouched and still runs** — same call, same path, same
   guard. A further check confirms the whitelist was restored afterwards, so no
   later check runs against a permanently widened list.
3. **SECOND GUARD, independently.** The inline `if` at the old `main.go:187` is
   now a named `finalWindowGuard(win, allowAny)`, called from exactly one place
   so no logic is duplicated. It is fed a crafted window (`claude.exe`) that
   "passed selection" and must refuse, naming it; must admit a genuine game
   window; and must stand aside under `--allow-any-window`.
4. **CREW VARIANT — cannot set it.** Asserts `flag.Lookup("allow-any-window")
   is nil` **and** the bench closure returns false. Master asserts the
   opposite, so the check cannot pass by accident in both.

Measured directly, not inferred:

- crew `--allow-any-window` -> `flag provided but not defined`, **exit 2**
- master `--allow-any-window` -> accepted, listed in `--help`
- master `--allow-any-window --auto` -> **exit 2**, combination refused

## My own test had the exact defect you warned about, inverted

Mutation testing found it. **Deleting layer 1 outright turned nothing red** —
layer 2 caught the decoy, `findGameWindow` still returned an error, and every
check still passed. "It refused" is true of both layers, so asking only "did it
refuse" proves *neither* individually. That is the same hole as testing layer 1
alone, pointing the other way.

Fixed by pinning the layer from the error wording — layer 1 says
`Refused N other process(es)`, layer 2 says `internal guard:` — and adding
**`lock: refusal came from LAYER 1, the process gate`**. That check fails the
moment layer 1 is removed.

## Every check seen to fail. Seven mutations, all caught:

| mutation | check that went red |
|---|---|
| layer 1 gate never refuses | `refusal came from LAYER 1` |
| refusal error stops naming the process | `refusal NAMES the refused process` |
| `finalWindowGuard` always allows | `second guard refuses a non-game window` |
| `isGameProcess` never matches | `NEGATIVE CONTROL accepts the real game process` |
| crew bench closure leaks `allowAny=true` | `CREW build cannot set allow-any-window` |
| crew build registers the flag | `CREW build cannot set allow-any-window` |
| master build loses the flag | `MASTER build does offer allow-any-window` |

Source restored from a pristine copy; both baselines re-confirmed exit 0.

One incidental proof: calling `registerBenchFlags()` a second time is harmless
in crew (it registers nothing) but panics the master build with
`flag redefined`. That panic is itself evidence the two variants genuinely
differ, so the second call is made only in the crew branch, with a comment
saying why.

## Full verbatim output — CREW

```
citizen-collector 0.1.0 (crew) selftest
  [ok  ] captures dir writable              ...
  [ok  ] blank detector rejects blank       every one of 4096 sampled pixels is rgb(0,0,0)
  [ok  ] blank detector accepts content     accepted as real content
  [ok  ] png encode                         ...
  [ok  ] win32 reachable                    primary display 1920x1080
  -- process lock --
  [ok  ] lock: decoy is a real visible 'Star Citizen' window title="Star Citizen" visible=true size=400x300 owner=collector.exe
  [ok  ] lock: POSITIVE CONTROL refuses a non-game 'Star Citizen' refused, error names collector.exe: true
  [ok  ] lock: refusal NAMES the refused process refused, error names collector.exe: true
  [ok  ] lock: refusal came from LAYER 1, the process gate the process gate refused it before any title was consulted
  [ok  ] lock: NEGATIVE CONTROL accepts the real game process accepted the window once its process counted as the game
  [ok  ] lock: whitelist restored after the fake scProcessNames=[starcitizen.exe]
  [ok  ] lock: second guard refuses a non-game window internal guard: selected a window from "claude.exe", which is not starcitizen.exe - refusing
  [ok  ] lock: second guard admits the game a genuine game window is not blocked by the guard
  [ok  ] lock: second guard defers to --allow-any-window master-only bypass still works, by design
  [ok  ] lock: CREW build cannot set allow-any-window flag registered=false benchAllow=false hint="" (all must be empty/false)
  -- auto mode --   (16 checks, see the Job 4 update)
  -- environment --
  [note] Game.log  ...LIVE\Game.log (776 lines, patch 4.9.188.23497)
selftest PASS   exit 0
```

## MASTER — identical except the last lock line

```
  [ok  ] lock: MASTER build does offer allow-any-window flag registered=true
selftest PASS   exit 0
```

**Which checks are new:** everything under `-- process lock --` (10 checks) and
everything under `-- auto mode --` (16 checks). The five above `-- process
lock --` are the pre-existing ones.

## Standing gap

The lock is proven against a decoy. It has **not** been exercised against a
real running Star Citizen — the game is not running, so the "accepts the actual
game" path is proven only via the `isGameProcess` boundary fake. Stating it
rather than implying coverage I do not have.

### 2026-08-06 16:01:26 — update-job4-collector-auto-mode-20260806.md

# Update: Job 4 complete — collector --auto mode (2026-08-06)

`citizen-collector` gains `--auto`. Builds clean, `--selftest` passes, and every
new check has been **seen to fail** before being trusted.

## What was added

New files `auto.go` and `auto_selftest.go`; `main.go` and `winapi.go` amended.

- **Tails Game.log**, polling every 2s (`--poll`). Reads only APPENDED bytes,
  carrying a partial trailing line to the next poll so a line split across two
  polls is not parsed as two broken ones.
- **Captures on state change**, reusing the parsers already in `gamelog.go` —
  `reGameRules`, `reMap`, `reLoadingScreen`, and the `OnClientSpawned-zone`
  pattern, which is looked up **by name** so a rename in `gamelog.go` breaks
  loudly instead of silently binding to nothing.
  - state: `gamerules`, `map`, `zone`, `location`
  - events: `loading_screen`, `client_spawned`
- **Debounce** 3s (`--debounce`).
- **Interval fallback** every N minutes with no change, default 10, `0` = off
  (`--interval`).
- **Window gate**: captures only while a `StarCitizen.exe` window exists.
- **Trigger recorded in every sidecar**, e.g.
  `{"kind":"state_change","field":"gamerules","from":"SC_Frontend","to":"SC_Default"}`.
  Interval captures say `{"kind":"interval","minutes":10}`; manual ones now say
  `hotkey` or `once` rather than nothing.
- **No console**: `--auto` hides the console window and logs to
  `collector-auto.log` next to the exe. Every recoverable problem is logged and
  the loop continues, so it survives being left running.
- **Settings** from `collector-settings.txt` next to the exe, written with
  commented defaults on first run and never overwritten. Command-line flags win
  over the file.

No OCR, no database routing, no ZIP packager — as instructed.

## Three design points worth recording

1. **The first poll never fires.** Game.log already holds a whole session when
   the tool starts; feeding that backlog through the detector would fire a
   burst of captures for state changes that happened before launch, stamped
   now. The first read primes silently. Same on log rotation — a new session
   truncates Game.log, and that re-primes rather than replaying.
2. **`--allow-any-window` cannot combine with `--auto`.** The flag only exists
   in the master build at all, but a master build left running unattended with
   the process restriction lifted would photograph whatever was on screen for
   hours into a corpus meant to be shared. The combination is refused at
   startup, and the auto loop passes a literal `false` — there is no variable
   to get wrong.
3. **`doCapture` takes a `Trigger`, not a `*Trigger`,** and refuses an empty
   `Kind`. A capture with no stated reason is a bug, so it cannot be written.

## Checks — and the mutation testing that proves them

`--selftest` gained 16 checks. The negative control runs **first**: a synthetic
log with no state changes must produce **exactly zero** triggers, and if it
fires the whole group is reported **VOID** (exit 2) rather than as a set of
passes.

Known sequence asserts count **and** exact reasons:

    event:loading_screen "Frontend_Main : SC_Frontend"
    state_change:gamerules "SC_Frontend"->"SC_Default"
    state_change:map "megamap"->"pyro"
    state_change:zone ""->"Stanton_1_Hurston"
    event:client_spawned "Stanton_1_Hurston"
    event:client_spawned "Stanton_1_Hurston"

**All checks passed first time, so per rule 12 I broke each one deliberately
and confirmed it failed.** Six mutations, all caught:

| mutation | caught by |
|---|---|
| tailer starts primed | `priming fires nothing` — 2 triggers from backlog |
| detector fires on every line | **NEGATIVE CONTROL fired -> VOID, exit 2** |
| debounce ignored | `debounce holds to 1 per 3s` |
| `interval 0` no longer means off | `interval 0 never fires` |
| BOM no longer stripped | `settings reads first line despite BOM` |
| zone parser renamed in `gamelog.go` | `shared zone parser found` |

**Two of those mutations initially escaped, and both revealed a weak test:**

- The BOM fixture had a **comment** on line 1, so an unstripped BOM corrupted a
  comment and changed nothing. The check was passing vacuously. Fixture now
  puts a live setting first, and the check fails properly.
- The zone-parser mutation was applied to the call site in `auto.go` rather
  than to the pattern name in `gamelog.go`, so the selftest's own lookup was
  untouched. Retargeted at the real thing.

Source restored byte-for-byte from a pristine copy afterwards and the baseline
re-confirmed clean; no mutation residue remains.

## Not done in this job

The `--auto` loop has not been exercised against a **live** Star Citizen
session — the game is not running. Every trigger path is proven against a
synthetic log, but the window gate and the capture path under real conditions
are untested. That is a real gap and I am stating it rather than implying
coverage I do not have.

### 2026-08-06 15:54:43 — update-process-lock-test-job-received-20260806.md

# Update: process-lock refusal test ordered (2026-08-06)

Received mid-session, logged on arrival before starting.

**The finding is correct and I accept it.** `--selftest` currently has four
checks — captures dir writable, blank detector in both directions, png encode,
win32 reachable. **None of them touch the process gate.** The gate at
`main.go:119` and the second guard at `main.go:187` read correctly, but reading
is not testing, and there is no artifact on disk showing a refusal was ever
exercised.

Capture 0007 is not evidence, also correct: it was taken **with**
`--allow-any-window`, so it proves the door opens when unlocked, not that it
stays shut when it is not.

Four checks to add to `--selftest`:

1. **Positive control** — `findGameWindow(allowAny=false)` must REFUSE a window
   titled "Star Citizen" whose process is not `StarCitizen.exe`. Create the
   condition rather than hoping for it. The error must NAME the refused process.
2. **Negative control** — the same call must ACCEPT a window whose process IS
   the game. Fake it at the `isGameProcess` boundary, without stubbing out the
   gate itself.
3. **The second guard** — `main.go:187` must be shown to fire independently.
   Two layers means two tests.
4. **Crew variant** — the crew build must be unable to set `allowAny` at all,
   not merely refuse it.

Then run `--selftest` on both builds and report output verbatim, marking which
checks are new. Any check that passes first time without having been seen to
fail gets broken deliberately, confirmed failing, and put back.

**No crew build is to be built, packaged or distributed until all four pass.**

## Sequencing

Job 4 (`--auto`) is in flight: `auto.go` and `auto_selftest.go` are written, and
`main.go` wiring is next. Both jobs modify `selftest()`, so I am finishing and
filing Job 4's wiring first rather than interleaving two sets of edits into the
same function. Starting this immediately after — nothing else comes between.

### 2026-08-06 15:48:35 — update-job3-backup-target-fixed-20260806.md

# Update: Job 3 complete — backup repointed to D: and launched (2026-08-06)

`Backup-CitizenCompass.ps1` changed and running detached. **PID 11824**, log
`logs/backup-run-20260806-154735.log`, args `-FullMirror -NonInteractive`.

## (a) D: primary, E: second mirror

Was `$MirrorRoot = 'E:\cc-backup'`, a single target. Now:

    [string]   $MirrorRoot       = 'D:\cc-backup'      # My Book, external
    [string[]] $SecondMirrorRoot = @('E:\cc-backup')   # secondary, kept

Step 7 is now a loop over both, and neither is best-effort. Recorded in the
parameter comment why D: must be primary: **E: is internal**, in the same box
as C:, so it does not survive losing the machine. D: is exFAT, which is why the
copies use neither `/COPYALL` nor `/SEC` — that was already handled and is left
alone. `-MirrorRoot` kept its name so the invocation in
`docs/workorder-backup-01-external-drive.md` still works.

## (b) A missing mirror drive is now fatal

It previously warned, set `$SkipMirror`, and the run still printed
`Failures: 0` and exited 0 — a backup that never left C: reporting success.
That is the SILENT SUCCESS pattern. Now every drive in the list is checked and
any absence exits 1 before a single byte is written.

`-SkipMirror` remains the one way out, deliberately: an operator saying "skip
it" and a drive quietly not being plugged in are different events and are no
longer collapsed into the same outcome.

**Proven by behaviour, not by reading the code — three controls:**

| control | result |
|---|---|
| primary mirror missing (`-MirrorRoot Z:\cc-backup`) | `[FAIL] MIRROR DRIVE(S) NOT PRESENT: Z:` — **exit 1**, no backup folder created |
| **second** mirror missing (`-SecondMirrorRoot Z:\cc-backup`) | D: passed, Z: failed — **exit 1**. The secondary is not treated as optional |
| `-SkipMirror` | `[WARN] MIRRORS SKIPPED BY REQUEST` and the run proceeds — opt-out still works |

The old code would have passed the first two. This gate has now failed on
demand, so it is a real check.

## (c) -FullMirror

Used on the launch, so `sc-ships` and `data-layer\external-sources` reach the
external drive. With two mirrors those trees are now written to D: **and** E:.

## (d) robocopy detached, logging to a file

New `Invoke-Robocopy` runs robocopy via `Start-Process -PassThru` with `/LOG:`,
and every call site now uses it (repo copy, Blender addons, mirror copy, and
the two full-mirror trees). It returns the exit code from the **process
object** rather than `$LASTEXITCODE`, which any intervening pipeline can
clobber.

`WaitForExit()` is deliberate: the copy must finish before the verifier reads
the destination, or the verifier races the writer and reports truncation that
is merely incompleteness. What must not block is the **tool call**, so the
whole script is launched detached instead — which is the actual fix for the
2026-08-05 kill.

Exit-code decoding moved into one `Show-RoboCode` helper so every call site
reports the bitmask identically instead of only 7b doing it.

Quoting is handled explicitly — `Start-Process` does not quote for you, and
both `Blender Foundation` and `done ships` contain spaces. Trailing
backslashes are trimmed before quoting because robocopy reads `"C:\path\"` as
an escaped quote.

## Checks

- Script parses clean (`Parser::ParseFile`, 0 errors).
- Destructive-operation scan: every `/MIR`, `Remove-Item`, `rmdir`, `del` hit
  in the file is **inside a comment**. No delete operation exists. `/E` only.

## Two things to note

1. **The database is NOT captured in this run.** No `PGPASSWORD` in process
   env, user env, or `pgpass.conf`. With `-NonInteractive` the script skips the
   dump and restore test and records it as a `[FAIL]` — correctly, since it is
   a real gap. The run will therefore exit 1 even if every file copies
   perfectly. Re-run with `$env:PGPASSWORD` set to capture it; the file trees
   are unaffected.
2. **A stray backup folder exists at `C:\cc-backup\20260806-154521`.** My
   `-SkipMirror` control test ran a full C:-only backup as a side effect. It is
   complete and harmless, and it is useful evidence that the new detached
   robocopy works (both `robocopy-*.log` files were written). Left in place —
   nothing is ever deleted here. Remove it yourself if you want it gone.

Job 5 will report per-tree exit codes and per-file verification. Continuing to
Job 4 while the copy runs.

### 2026-08-06 15:39:58 — update-job2-push-20260806.md

# Update: Job 2 complete — 14 files pushed (2026-08-06)

Commit `3254dea`, "Split the keybind page into six modes, generated from the
actionmap". Pushed `8ee5cdd..3254dea` to `origin/main`.

The push carried **two** commits: the branch was already ahead by one
(`a7118c7`, the WO-COLLECT-01 rev 4 landing) before I started.

## Staging

Added the 14 files by name. No `git add -A`. `git diff --cached` confirmed
exactly 14 entries before committing — none of the ~50 CRLF/LF phantom-churn
files were pulled in. Git printed its usual "LF will be replaced by CRLF"
warnings for the staged files themselves; that is the filter, not churn.

Five modified, nine new:

- M `testing/_src/_layer.src.html`, `build_deploy.py`, `device_engine.js`,
  `keybinds.src.html`
- A `build_keybind_modes.py`, `data-layer/processed/actionmap_categories.json`,
  and `testing/_src/`: `check_modes.py`, `inject_engine.py`, `kb_modes.gen.js`,
  `patch_btn_limit.py`, `patch_modes_wire.py`, `patch_two_sticks.py`,
  `sc_export.js`, `test_sc_export.js`

## Two things to flag

1. **`data-layer/processed/actionmap_categories.json`** — the order's closing
   line says do not touch `data-layer\processed\`, but Job 2 explicitly lists
   this file to stage. Treated the specific instruction as authoritative and
   staged it. Its content was not modified or regenerated; it was only added to
   the commit. Say if that was not intended — it is one file to revert.

2. **A stale `.git/HEAD.lock` blocked the first commit attempt.** Zero bytes,
   dated 2026-08-05 19:55, no git process running — left by a crashed git
   process, most likely the concurrent session noted in CLAUDE.md rule 14.
   Moved to `_to_delete/stale_git_locks_20260806/` per rule 1 rather than
   deleted, then the commit succeeded.

   **`.git/objects/maintenance.lock` is also stale**, dated 2026-07-29. It is
   not blocking me so I left it, but it is probably blocking background git
   maintenance. Reporting, not fixing.

Note `kb_modes.gen.js` is a generated artifact committed alongside its
generator. Its header states one writer and it is `build_keybind_modes.py`.
Edit the generator, never the output.

### 2026-08-06 15:39:31 — update-job1-keybind-deploy-20260806.md

# Update: Job 1 complete, but not by the commanded route (2026-08-06)

Keybind page is live at
`https://citizencompasstesting.citizencompass-contact.workers.dev` —
version `81494202-f92c-4169-ad19-1389b2b3bd29`.

## The order's deploy command was wrong and would have looked successful

The order said:

    npx wrangler pages deploy . --project-name citizen-compass-testing

Three things were wrong with it.

1. **There is no Pages project.** `wrangler pages project list` returns empty.
   The testing site is a **Worker with static assets**, configured in
   `testing/wrangler.toml`. Cloudflare moved static hosting off Pages.
2. **The project name is the known trap.** `testing/wrangler.toml` carries a
   comment written on 2026-08-01 warning that the hyphenated name
   `citizen-compass-testing` publishes to a *second* URL and leaves the live
   testing site untouched "while looking like a complete success". The worker
   name is `citizencompasstesting`, unhyphenated, and the name IS the subdomain.
3. Had I forced it by running `wrangler pages project create`, the result would
   have been exactly the two-URLs-in-circulation failure the repo already
   documents.

Deployed with `npx wrangler deploy` from `testing/` instead, which targets the
existing worker name. Same intent, correct mechanism, updates the site actually
in circulation. **`testing/wrangler.toml` was not modified.**

## Authentication

The order said wrangler was not authenticated. It was, partly: a
`CLOUDFLARE_API_TOKEN` in the repo-root `.env`, which wrangler 4 auto-loads
**from the current working directory**. That is why `whoami` worked from the
repo root and the deploy failed from `testing/_deploy` — no `.env` there. The
token also lacked Pages/Workers write permission (API error 10000). Ran
`npx wrangler login` as instructed; OAuth succeeded and that is what the deploy
used. `.env` remains gitignored and its contents were never printed.

## Self-inflicted defect, found and fixed

My first failed `pages deploy` attempt, run from inside `testing/_deploy`,
created a `.wrangler/cache/` folder there. The next deploy **published it as a
public asset** — `/.wrangler/cache/wrangler-account.json` and `pages.json`,
containing the account ID and account name. No tokens. Moved to
`_to_delete/stray_wrangler_cache_in_deploy_20260806/` per rule 1 and
redeployed; both now 404 at origin (one briefly served 200 from edge cache
until cache-busted). Asset count went 487 → 483.

**Worth a permanent guard:** anything that lands in `testing/_deploy/` gets
published. An `.assetsignore` or a build-time check for dot-directories would
close this. Not doing it in this job — reporting it.

## Acceptance checks — all three pass, against the DEPLOYED file

Verified against the deployed `kb_modes.gen.js` fetched back over HTTP, not the
local copy.

- six modes — PASS, 6/6: FLIGHT, ONFOOT, EVA, VEHICLE, CAMERA, SOCIAL
- Social 6 numpad + 34 keyless emotes — PASS, keys=6, all Np1..Np6, emotes=34
- On Foot, Left Alt, H — PASS, `m=1` resolves to `Helmet (Equip)`
  (`build_keybind_modes.py:59` sets `MODS={"lalt":1,...}`, and the page labels
  layer 1 "M1 (Left Alt)", so `m:1` is Left Alt by construction, not assumption)

**Negative control:** the same three checks were re-run against a deliberately
corrupted copy — one mode renamed away, one emote removed, the H binding
relabelled. All three FAILED as required. A check that cannot fail is not a
check; these were proven able to fail.

`kb_modes.gen.js` returns **200**, so `PAGES` in `build_deploy.py` did copy it.
Nothing to report there.

Also confirmed: `/keybinds.html` and `/index.html` return 307 to their
extensionless forms and resolve 200. That is wrangler's normal html handling,
not a fault.

### 2026-08-06 15:30:38 — update-five-jobs-received-20260806.md

# Update: five-job work order received (2026-08-06)

Received a five-job order. Logging on arrival per hard rule 13, before starting.

1. **Deploy the keybind page** — `npx wrangler login`, then deploy
   `testing\_deploy` to Cloudflare Pages project `citizen-compass-testing`.
   Verify six modes, Social numpad + 34 folded emotes, On Foot Left-Alt
   "Helmet (Equip)" on H. If `kb_modes.gen.js` 404s, report the PAGES list in
   `build_deploy.py` — do not patch around it.
2. **Push** — 14 named files only. No `git add -A` (about 50 tracked files
   carry phantom CRLF/LF churn).
3. **Fix the backup target** — `Backup-CitizenCompass.ps1` currently mirrors to
   `E:\cc-backup`. Primary becomes `D:\cc-backup` (My Book, 3.63 TB external);
   `E:` stays as a second mirror. Missing mirror drive becomes a hard failure,
   not a warning. Use `-FullMirror`. Launch detached via `Start-Process
   -PassThru` so a 7.5 GB copy is not killed by a tool-call timeout.
4. **Collector `--auto` mode** (main job) — tail Game.log, capture on state
   change, 3s debounce, interval fallback (default 10 min, 0 = off), only while
   a StarCitizen.exe window exists, record the trigger reason in the JSON
   sidecar. Extend `--selftest` with a synthetic Game.log, exact trigger counts
   and reasons, plus a negative control that must produce zero triggers.
5. **Close out the backup** — robocopy exit code per tree, per-file
   verification enumerated from the destination disk, first 10 mismatches, and
   a negative control asserting `sc-ships\.cache\` is absent from the
   destination.

Standing constraints for this order: never delete (robocopy `/E`, never
`/MIR`), add files by name only, one writer per artifact, every check needs a
negative control, no secrets in chat or files, encoding stated on every file
open. `data-layer\processed\` and `viewer\profiles.js` are off-limits.

Starting Job 1.

### 2026-08-05 21:22:38 — update-mirror-verify-per-file-20260805.md

# Update — mirror check rebuilt: per-file, non-tautological, proven against real known-bad data

**When:** 2026-08-05

New: `scripts/Verify-MirrorTree.ps1`. Step 7b of `Backup-CitizenCompass.ps1` now
calls it instead of comparing aggregates.

## Why the old check was not a check

Two independent defects, both now fixed:

1. **Aggregates cancel.** A file count plus an MB total can both match while the
   contents are wrong — two files differing by +2 MB and −2 MB sum to a pass.
2. **A truncated file is invisible to a count.** It is *present*, so the count
   matches.

## Not tautological — enforced structurally

The verifier is a **separate script run as a separate process**. It shares no
filter state with the copy, so it cannot compare the copy to itself. It:

- enumerates the **destination from disk** — never from `SHA256SUMS.txt`, never
  from robocopy's log, never from the copy's own file list;
- compares **per file, on relative path AND byte size**;
- **names the first 10 mismatches** with both sizes and the delta, not just a
  count.

## Two controls, because a checker that reads nothing passes everything

- **POSITIVE** — a known-*included* file must be found at the destination. If
  this fails, the enumeration is empty or aimed at the wrong path and no verdict
  below it means anything.
- **NEGATIVE** — a known-*excluded* file (something under `.cache`) must be
  **absent**.

The negative control is **only credited when the positive control passed**,
otherwise "absent" is vacuous. Where no excluded file exists to test with, it is
reported **NOT PERFORMED** — never as a pass.

## Proven to fail, on real data rather than a fixture

The killed run left genuine known-bad input, which is better evidence than
anything synthetic:

| Target | Result |
|---|---|
| **Killed run** `20260805-204113` external-sources | **FAIL, exit 1** — `MISSING from destination: 44428` of 58,257, first 10 named. Positive control passed, so it demonstrably *was* reading the destination. |
| **Good run** `20260805-205238` sc-ships | **PASS** — all **951** files present, byte sizes matching. **Both controls fired:** positive `Liberator\model.glb` present; negative `.cache\huggingface\trees\aed8d04c…json` **absent** — proving `.cache` was genuinely excluded rather than assumed. |
| **Good run** external-sources | **PASS** — all **58,257** files present with matching byte sizes. Negative control honestly reported *not performed* (that tree contains no excluded dirs). |

**One honest correction to the prediction.** The expectation was that the killed
run would leave a *truncated* file. It did not — it left 44,428 files **missing**
and **zero** size mismatches. robocopy evidently does not leave partials behind
in this mode. The per-file size comparison is still the right check and stays,
but I did not catch a truncation, and I am not going to claim I did. What the
check actually caught was mass absence that the old aggregate check would have
flagged too — the size dimension remains **unproven against a real partial**,
and is recorded as such rather than as demonstrated.

## `/MIR` — not used, and why

The instruction specified `/MIR`. I used **`/E`** and am flagging it rather than
silently substituting.

`/MIR` deletes anything at the destination that is not at the source. This
script's header states as a **guarantee** that it "contains no delete operation
of any kind… robocopy is called with /E, never /MIR", and CLAUDE.md hard rule 1
is never delete. Using `/MIR` would break both.

**The stated reason for `/MIR` was resumability, and `/E` already has it.**
Measured, not assumed — re-running `/E` against the completed mirror:

```
elapsed: 1.1s   exit code: 0
Files :  951   Copied: 0   Skipped: 951   Bytes: 7.392 g skipped
```

It re-scanned 7.4 GB and copied nothing in about a second. A killed run restarts
cheaply. Nothing is gained by `/MIR` except the ability to destroy. Say the word
and I will switch it.

## robocopy's exit code is now reported and decoded

It is a bitmask, and it is printed in full: 1 = files copied, 2 = extra at
destination, 4 = **mismatched**, 8 = **some files could not be copied**, 16 =
**serious error**; 0 = nothing to do. **Anything ≥ 8 is FATAL regardless of what
the file counts say**, and the copy is abandoned for that tree before
verification even runs.

If the verifier cannot run at all (script missing) that is reported as **not
verified**, never as passed.

## The timeout was structural

7.5 GB will not finish inside a 10-minute tool call and never will. The copy no
longer runs inside a tool call — it is launched detached (`Start-Process
-PassThru -WindowStyle Hidden`) with `/LOG:` to a durable per-tree log, and each
tool call only polls exit state and tails the log. That is how the completed run
above was driven.

**Nothing staged or committed.**

**Next:** the flight-stick device-facts job, then the unreleased-content filter
and the FixedReward census.

### 2026-08-05 21:16:06 — update-backup-mybook-complete-20260805.md

# Update — MyBook backup complete and verified. Exit 0, 0 failures, 1 known warning.

**When:** 2026-08-05
**Backup:** `C:\cc-backup\20260805-205238` → `D:\cc-backup\20260805-205238`

## 1. The drive

**D: is the MyBook** — WD My Book 25EE, USB, 3726 GB, Healthy, 3726 GB free.

**Filesystem is exFAT, not NTFS.** That matters and I checked the script for it:
exFAT carries no NTFS ACLs and supports no junctions or hardlinks, so any
robocopy `/COPYALL` or `/SEC` would have errored on every file. The script uses
`/E /R:2 /W:5` with no ACL flags, and the `-FullMirror` code I added
deliberately does the same.

## 2. The 2026-07-30 failure — diagnosed, and the premise needs correcting

**It was already diagnosed at the time, and it was already fixed.** Two runs
exist, not one:

- **`20260730-231753`** — the one that **exited 1**. It contains exactly **one
  file**, the git bundle. Cause, recorded in
  `docs/handoff_archive/20260730_231828_...backup_script_failed.md`:
  `git bundle verify` writes its success message to **stderr**, and Windows
  PowerShell 5.1 wraps native stderr into a `NativeCommandError` under
  `$ErrorActionPreference = 'Stop'` — so the script **aborted on a passing
  verification**.
- **`20260730-233853`** — v2, which fixed exactly that via `Invoke-Native`, ran
  **all 7 steps, exit 0**, 599 files.

The directory the work order pointed me at (`20260730-233853`) is the
**successful** run, which is why grepping its logs found only noise — repo logs
copied *into* the backup, not backup logs. The failed run left no log at all.

This is the same native-stderr bug `deploy_testing.ps1` documents in its own
header. Third appearance in this repo.

## 3. Measurement

Repo: **17.8 GB across 85,768 files.**

## 4. `-FullMirror` added

New `[switch] $FullMirror`. **Defaults unchanged** — without it the script
behaves exactly as before.

The mirror copies `$BackupDir`, which step 2 already stripped, so the two
irreplaceable trees cannot come from there. Step **7b** copies them from the
repo straight into the mirror with only the four rebuildable exclusions
(`venv`, `__pycache__`, `.cache`, `node_modules`), then verifies by **file count
and bytes**.

I also corrected the script's own comment: "external-sources → re-pullable" is
simply **wrong** (re-pulling UEX returns *today's* prices, not the sealed
snapshot's), and "sc-ships → re-downloadable" overstates a pack whose
redistribution rights are on record as unestablished.

**A missing mirror drive is now fatal when `-FullMirror` is set** rather than a
warning, because that is the precise failure this switch exists to prevent.

## Three defects I introduced and caught before they mattered

1. **A false FAIL.** First run reported *"sc-ships: only 951 of 1675 files
   reached the mirror"*. Wrong — **724 of those 1,675 live in `.cache`**, a
   HuggingFace cache correctly excluded. All 951 eligible files and every one of
   their 7,570.0 MB had arrived. My check compared an *unfiltered* source count
   against a *filtered* destination. Now both sides apply the same exclusions,
   and bytes are compared too (equal counts with unequal bytes = truncation).
   **A false failure is as corrosive as a false pass** — it trains the reader to
   disbelieve the check.
2. **A silently truncated message.** I wrote the loudest `Write-Fail` in the
   script as `"a" + "b" + "c"` across lines. PowerShell parses that as **five
   positional arguments**, not concatenation — `$m` would bind only the first
   fragment and the rest would vanish into `$args`. It "parsed clean". Wrapped
   in parentheses.
3. **PGPASSWORD not set on the first run**, so the dump and restore test were
   skipped. My regex `^[a-z]+://` could not match `postgresql+psycopg2://` — the
   `+`. Fixed; the second run captured the database properly.

The first run was also killed by my own 10-minute tool timeout mid-copy, not by
the script. Re-run in the background. Its partial output is left in place at
`20260805-204113` per hard rule 1 — moved aside for Sleven, never deleted.

## 6. Verification — every check reported explicitly

| | Check | Result |
|---|---|---|
| **a** | `git fsck` **exit code** | **0 — PASS.** Judged by exit code only. It printed "dangling blob/commit" lines to stderr; those are normal unreferenced objects, not errors, and judging by text would get this backwards. |
| **b** | Restore ran, ship count | **PASS — the dump is usable.** Restored into a throwaway DB and returned **232 ships**. Script expected 254 and warned. **232 is reported as the actual number rather than treated as a failure**, per instruction. |
| **c** | File counts | Literal: **C: 28,153 / D: 90,810** (spans all runs per drive). This run: **C: 8,412 / D: 67,620** — D: is higher **by design**, since `-FullMirror` adds 59,208 files C: never had. |
| **d** | `.env` in the mirror | **PASS** — `D:\cc-backup\20260805-205238\repo\.env`, 223 bytes. |
| **e** | Sealed snapshots | **PASS** — uexcorp `20260801T235530Z` holds **exactly 114 files**; scunpacked `20260801T204744Z\blueprints.json` present at 9.8 MB. The new commodity snapshot `20260806T033315Z` also mirrored. |

**The mirror step was NOT skipped.** Both trees verified: `sc-ships` 951 files /
7,570.0 MB and `external-sources` 58,257 files / 10,262.8 MB, source and
destination equal on both counts.

## Two things for Sleven

1. **232 vs 254.** The 2026-07-30 note already recorded that every DB check that
   session read 232, so `$ExpectedShipCount = 254` looks like a **stale
   hardcoded baseline** rather than a bad dump. I have **not** changed it — it
   is a default and I was told not to change defaults. Worth correcting
   deliberately.
2. **`.env` is now on an external drive**, as instructed. That compounds the
   standing exposure: the UEX token inside it was exposed in a screenshot and
   **still has not been rotated**. Back it up, then rotate — the rotation is
   still outstanding.

A throwaway restore database was left in place (the script never deletes):
`cc_restore_test_20260805_205238`.

**Nothing staged or committed.**

**Next:** the flight-stick device-facts job, then the two outstanding jobs from
the earlier batch (unreleased-content filter, FixedReward census).

### 2026-08-05 20:53:04 — update-device-facts-job-received-20260805.md

# Update — received: sourced flight-stick fact file for the keybind page

**When:** 2026-08-05

Logging on arrival per hard rule 13. **Not started** — the MyBook backup is in
flight and was explicitly "stop at the first failure", so this queues behind it.

## The job

Build `data-layer/raw/devices/device_facts.json` plus
`device_facts_findings.md`, so the keybind page can recognise a stick from its
browser gamepad id, name each control correctly, and draw it in the right place.

Seven devices in priority order: VKB Gladiator NXT EVO (**every** variant —
Standard, SCE, Omni Throttle, Premium, left and right hand), VIRPIL
Constellation ALPHA Prime, VIRPIL CDT-AEROMAX, Thrustmaster T.16000M,
Thrustmaster SOL-R 2, Turtle Beach VelocityOne Flightstick II, Winctrl Ursa
Minor.

Five fact classes each: **A** USB identity (VID/PID hex per variant and firmware
mode, plus verbatim `navigator.getGamepads()[i].id` strings — the exact wording
matters more than the numbers because that string is what we match on), **B**
default button numbering with an explicit statement of 1-based (VKB docs) vs
0-based (browser) and which firmware/VKBDevCfg profile it belongs to, **C** axis
order including whether each hat is an HID hat switch or four buttons, **D**
plain-words control inventory, **E** geometry as 0–1 fractions of each face from
the vendor's own layout template.

## The governing rule, noted

**Blank beats wrong.** Every field carries a source URL; anything unsourceable
is `null` with a `_missing` note recording what was looked for and where. A
blank renders as "press it to identify" and is harmless; a wrong number
silently mislabels a control and nobody ever finds out.

That is the same standard already applied to the collector's Game.log parser
(verified vs unverified patterns, null plus a reason rather than a plausible
default) and to job 2's `range_gm`. Consistent with hard rule 11.

## Constraints I will observe

- **No vendor images, 3D models or manuals downloaded into the repo.** Facts and
  coordinates only — we are not licensed to republish their artwork. Geometry is
  to be read from published templates and recorded as fractions, describing the
  positions in JSON without pulling the image.
- **Do not touch `viewer/profiles.js`, anything under `testing/`, or any built
  HTML.** One writer per artifact — hard rule 14. `testing/` is explicitly
  Claude-Code-only-via-C1 in CLAUDE.md, and this job is not that path.
- Primary sources preferred; community sources allowed but that entry is marked
  `confidence: "community"`.
- If a fetch is blocked, that is the answer — hard rule 9. I will not route
  around it via a mirror, cache or archive; I will record it as not found and
  say where I looked.

**Next:** finish and verify the backup, then start this.

### 2026-08-05 20:37:46 — update-backup-mybook-received-20260805.md

# Update — received: run the backup to the WD MyBook on D:

**When:** 2026-08-05

Logging on arrival per hard rule 13. Jobs 3 and 4 of the previous batch (the
unreleased-content filter and the FixedReward census) are **not started** and
are now queued behind this.

Six steps, **stop at the first failure**:

1. Confirm D: is the MyBook — filesystem (NTFS vs exFAT changes robocopy long-path
   handling) and free space.
2. Diagnose the 2026-07-30 backup that exited 1 and was never explained. Do not
   run a bigger one without knowing why.
3. Measure the repo size.
4. Add `-FullMirror` to `Backup-CitizenCompass.ps1`. When set, the **mirror**
   copy excludes only the four genuinely rebuildable things (venv, `__pycache__`,
   `.cache`, `node_modules`). `sc-ships` (~7.3 GB, redistribution rights on
   record as unestablished) and `data-layer\external-sources` (the sealed
   snapshots — re-pulling UEX gives *today's* prices, not 1 August's) go **in**.
   The C: copy keeps existing exclusions for speed. **Defaults unchanged.**
5. Run it against `D:\cc-backup` with `-FullMirror`.
6. Verify — exit 0 is not proof. Five explicit checks: `git fsck` **exit code**
   (not its text — git writes "is okay" to stderr on success), a database
   restore reporting an actual ship count, file counts C: vs D:, `.env` present
   in the mirror, and the sealed snapshots spot-checked.

**A skipped mirror step is a FAILURE, not a warning.** The script currently
treats a missing mirror drive as non-fatal; if that fires I am to say so loudly.

`.env` is included deliberately — Sleven's call, back it up then rotate. Noting
that this compounds the standing exposure: the UEX token in that file was
exposed in a screenshot and still has not been rotated, and it will now exist on
an external drive as well.

**Next:** step 1.

### 2026-08-05 20:37:17 — update-job2-uex-commodities-landed-20260805.md

# Update — job 2 of 4: UEX commodity endpoints called. "Screenshots are the only route" is REFUTED.

**When:** 2026-08-05

## The headline

**UEX serves commodity prices, and it always would have.** The 1 Aug pull never
asked. Searching that snapshot's `_pull_summary.json` for `commodit` returns
nothing — the gap was in the **request list**, not in the API. Every plan since
has rested on an assertion that was never tested.

New sealed snapshot: `data-layer/external-sources/uexcorp/snapshots/20260806T033315Z`

## Row counts per endpoint

| Endpoint | Result | Rows |
|---|---|---|
| `/commodities/` | **200** | **204** |
| `/commodities_prices_all/` | **200** | **2,597** |
| `/commodities_raw_prices_all/` | **200** | **335** |
| `/commodities_status/` | **200** | legend dict (buy/sell status codes) |
| `/commodities_averages/` | **400** | requires `id_commodity` |
| `/commodities_prices_history/` | **400** | requires `id_terminal` |

The two 400s are **parameter requirements, not permission failures** —
`{"status":"missing_id_commodity","message":"Commodity not provided"}` and
`{"status":"missing_id_terminal","message":"Terminal not specified"}`. The
credential was verified against `/game_versions/` before the run and the other
four returned 200. Same shape as the bare `/items/` endpoint this source already
documents. Neither body was written to disk — write-before-status held.

Coverage: **2,597 price rows across 123 commodities × 135 terminals.**

## The freshness question — timestamp, NOT game_version

**Prices carry `date_added` and `date_modified` (Unix epoch). There is no
`game_version`, `patch` or `build` field on any commodity price row.**

| | days |
|---|---|
| min / p25 / median | 0 / 0 / **1** |
| p75 / p90 | 4 / 9 |
| max | 509 |

Buckets: **1,389 rows ≤1 day**, 883 ≤7d, 320 ≤30d, 3 ≤90d, 2 >365d.
Newest row `2026-08-06T03:07:17Z` — **eight minutes before the pull**. Oldest
`2025-03-14`.

**So coverage and freshness are both genuinely good — but they are not patch
provenance.** Without a game_version a price cannot be attributed to a patch. A
row nine days old may straddle a patch boundary and nothing in the data says so.
That is the distinction the work order asked for, and it cuts both ways:

- **Against the collector's price role:** UEX already has broad, near-live
  commodity prices. Screenshotting shops to obtain a number UEX refreshed an
  hour ago is redundant.
- **For it:** the collector can stamp `patch` and `build` on every observation —
  the grabber already does, read from `Game.log`. That is precisely what UEX
  cannot supply. The defensible role is **patch-attributed** observation, not
  price coverage.

I am reporting that trade-off rather than deciding it — "may delete a build" is
Sleven's call.

## Gating, as source 6 was gated

`verify_snapshot_v2.py 2.0.0`, **inspection_complete: true** — 6 files, 0 JSON
parse failures, 0 ext/content mismatches, 0 active-content hits, 0 read errors,
0 walk errors, 0 duplicate hashes, 0 changed during run. SHA256 for every file.

Two "unexpected domain" flags: `api.uexcorp.uk` appearing in `_pull_summary.json`
and `_pull_stderr.log` — files **this pull wrote itself**, not downloaded
payload. Benign, and recorded in the manifest rather than suppressed.

Manifest:
`data-layer/external-source-manifests/20260806T033315Z/06_uex-corp_commodities_manifest.json`
— **data_tier C**, UEX's own ±20% commodity tolerance stated.
**Nothing promoted to the database.**

## A silent failure found and fixed in uex_corp.py

The script's docstring said the token was "loaded from .env". The
`python-dotenv` import was wrapped in `try/except ImportError` with a **bare
pass** — and python-dotenv is **not installed** in this interpreter. So `.env`
was never read, and the script reported *"UEX_API_TOKEN is not set. Refusing to
run."* while the token sat in `.env` the whole time.

That is a silent failure reported as a different, plausible failure: the message
sent a reader hunting for a missing credential that was never missing, while the
real cause was swallowed by the bare `pass`.

Fixed by parsing `.env` directly — removing the dependency rather than adding
one, which also avoids installing a package outside the repo (hard rule 6) — and
by making the failure name which step failed and whether `.env` exists. The
existing `_verify_uex_corp.py` fixture suite still passes.

## Credential handling

Token went from `.env` into the request header and nowhere else. **Not printed,
logged, echoed, or written into any snapshot or manifest file.** I confirmed its
presence by length only (40 chars).

**Standing warning, repeated because it is independent of this job: that token
was exposed in a screenshot and has still not been rotated.** It should be
rotated at UEX regardless of this work order — I cannot do that from here.

## Not done

`/commodities_averages/` and `/commodities_prices_history/` need per-commodity
and per-terminal parameterisation — 123 and 135+ requests respectively. The
precedent exists (`fetch_items_by_category`). Not attempted in this run; flagged
rather than silently skipped.

**Nothing staged or committed.**

**Next:** job 3 — the unreleased-content filter, which the work order flags as a
possible live defect.

*(+121 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# UPDATE — PART C: both Go defects fixed and proven; STOPPED at step 4's stop condition

Defects 1 and 2 are fixed and proven against known-bad input. Step 4's
comparison found a **third difference**, so per the work order I have stopped
and am reporting rather than proceeding to delete `generate_handoff.py`.

## Defect 1 — invented entries — FIXED

`watcher-go/handoff_regen.go`. `strings.Split(string(raw), "\n### ")` replaced
with `updateEntryHeaderRe`, matching only the headers `appendUpdate()` writes.
Both required edge cases preserved: an empty header set returns the whole file
as one entry, and preamble before the first header is kept.

Also extracted `parseUpdateEntriesFrom(path)` so the parser can be exercised
against fixtures rather than only whatever the live log happens to hold.
`parseUpdateEntries()` calls it with `updatesLogPath()` — behaviour unchanged.

## Defect 2 — classification by prose — FIXED

`watcher-go/handoff.go`. `titleLine()` added; both `isHandoffDoc()` and
`isUpdateDoc()` now use it instead of `firstRunesUpper(text, 500)`.
**Evaluation order unchanged** — filename hints first, `isHandoffDoc()` before
`isUpdateDoc()`, a doc matching both is a full handoff. `firstRunesUpper` had no
remaining callers and was removed, with a comment recording what it was and why
it went.

## Rule 12 — proven, not asserted

`watcher-go/handoff_defects_test.go` and `handoff_livelog_test.go`. `go build`,
`go vet` and `go test ./...` all clean.

| test | asserts |
|---|---|
| subheadings stay inside their entry | a body with two `###` subheadings yields **1** entry, not 3, and keeps both |
| no headers returns whole file | content is not dropped |
| preamble preserved | text before the first header survives |
| hyphen separator parses | `-` works as well as `—` |
| update mentioning "handoff" in BODY | classified as **update**, not handoff |
| genuine handoff title | still detected (`CITIZEN COMPASS HANDOFF`, `SESSION ARCHIVE`) |
| filename hint still wins | evaluation order intact |
| `titleLine` | first heading, else first non-blank line |
| **live `_updates_log.md`** | **70 total `###` headers -> 50 parsed entries, 0 phantoms** |

Python (fixed) on the same live log: **50 entries, 0 phantoms.** Identical.

## Step 4 — the comparison, and the STOP

Built the fixed binary and regenerated via `--once`, then regenerated with
`generate_handoff.py`, and diffed.

**The improvement is real and large:** fixed Go emitted **102,901 chars** where
the deployed binary was emitting ~65,000. That recovers almost exactly the
~37,000 characters the addendum measured as discarded.

**Both defects are confirmed fixed by structural comparison:**

| | Go (fixed) | Python (fixed) |
|---|---:|---:|
| `###` headers in output | 40 | 40 |
| timestamped entries shown | 20 | 20 |

Identical. No phantoms, no classification divergence.

### But the outputs still disagree — third difference found

Beyond the Go-only version-marker block (which is the KEEP feature and is
expected), the diff is 21 lines in two groups:

**1. Number formatting — 5 lines.**

| Go | Python |
|---|---|
| `**Project health score:** 35.0/100` | `**Project health score:** 35/100` |
| `- Data completeness: 0.0%` | `- Data completeness: 0%` |
| `- Viewer progress: 50.0%` | `- Viewer progress: 50%` |
| `- Documentation: 100.0%` | `- Documentation: 100%` |
| `**Ships:** ... (50.0%)` | `**Ships:** ... (50%)` |

**2. Python emits a trailing line Go has no equivalent for:**

```
*(raw text of the most recently adopted handoff doc — local AI compression
unavailable right now, showing it unmodified)*
```

That is Python's Ollama-fallback footer. Ollama is disabled and parked, so
Python takes the fallback path and says so; Go never compresses at all, so it
has nothing to report.

### Why I am stopping rather than judging

The work order is explicit: *"If they still disagree there is a third difference
— stop and report, do not assume Go is correct because it was fixed twice."*

They disagree. I can characterise both differences and neither touches entry
content or classification — but "I can explain it" is not "it matches", and this
is precisely the reasoning the stop condition exists to prevent. **Not
executed:** step 5 (delete `generate_handoff.py` and `_verify_generate_handoff.py`)
and step 6 (the CLAUDE.md additions).

### The decision these need

- **Number formatting:** which is correct? Python's `35/100` reads better;
  Go's `35.0/100` is what the live document will show. One of them should
  change so the two agree, or Python's retirement makes it moot.
- **The Ollama footer:** Go is arguably right to omit it, since it never
  attempts compression. If so, this difference is expected rather than a defect
  — but that is a call to make explicitly, not to assume.

## Deployment state — the fix is NOT live

`inbox_watcher_fixed.exe` (5,735,424 bytes, built from fixed source) sits in the
repo root. `inbox_watcher.exe` (3,884,032 bytes, 29 July) is still the binary
the scheduled task runs.

**So the live watcher is still the defective one**, still emitting ~65k with
phantoms. Replacing it means stopping the scheduled task to unlock the file, and
I have not done that — deploying while an unexplained third difference stands
would bake in whichever formatting Go happens to use. Say the word and it is a
two-minute change.

Nothing deleted. `generate_handoff.py`, `_verify_generate_handoff.py` and
`inbox_watcher.py` are all still on disk. Comparison artifacts moved to
`_to_delete/go_migration_comparison_20260801/`.

