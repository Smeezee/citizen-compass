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
