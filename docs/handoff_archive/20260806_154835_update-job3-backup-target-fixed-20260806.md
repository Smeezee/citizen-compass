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
