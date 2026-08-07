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
