# UPDATE — working tree committed and pushed in three commits

`383a8ba` on `origin/main`, 0 ahead / 0 behind. Filed per rule 13 before
starting the next unit of work.

The brief said 96 files. `git status --porcelain` said **56**. All 56 are
accounted for below: 55 committed, 1 deliberately left.

## `7c0c59e` — the testing layer source, and this is the one that mattered

`testing/_src/` held the **only** copy of the testing layer source and its three
build scripts. They existed nowhere but an ephemeral cloud session — that
session ending would have taken the source with it, leaving only a built
artifact and no way back to it.

In: `_layer.src.html`, `build_full.py`, `build_machine_layer.py`,
`build_portable.py`, plus `testing/_layer.html` and `testing/build.py`.
3,991 lines across 7 files.

The reason `testing/` was untracked wholesale is that `testing/_deploy` alone is
**344 MB** of compressed ship models. That filter is now written into
`.gitignore` rather than enforced by leaving the whole directory out:
`testing/index.html`, `_deploy/`, `_models/`, `_tools/` stay out; source stays
in. I confirmed with `git ls-files --others --exclude-standard testing/` that
exactly 6 files were in scope before staging — a plain `find` over that
directory times out, which is itself the point.

Same commit ignores `data-layer/external-sources/` while leaving
`data-layer/external-source-manifests/` tracked, per the caveat in `CLAUDE.md`.

## `90fee81` — safety tooling that the hard rules already assume exists

Hard rule 4 says run `Backup-CitizenCompass.ps1` before anything destructive.
Hard rule 3 names `run_e2e_test.py` as the only sanctioned destructive path.
**Neither was committed.** Both are now.

I reviewed the `run_e2e_test.py` diff specifically to confirm it *strengthens*
the guards rather than weakening them, because rule 3 forbids the opposite. It
strengthens them, and it is worth being exact about what it fixes:

The harness was **already** sound about *which database* it drops — `DB_NAME` is
a fixed prefix plus a fresh random suffix, never derived from `DATABASE_URL`, so
`DROP DATABASE` could only ever name a database the process had just created.
Nothing to fix there.

The hole was **which server**. The connection inherits host and credentials from
`DATABASE_URL`, and an unset `DATABASE_URL` silently fell back to
`RAILWAY_DATABASE_URL` — production. A missing environment variable was enough
to aim `CREATE DATABASE`, `DROP DATABASE` and `alembic downgrade base` at the
live server. `assert_safe_target()` now refuses to start on any of: a
non-throwaway name, collision with the configured database, a non-local host
without `CC_E2E_ALLOW_REMOTE`, or `DATABASE_URL` unset. `assert_disposable()`
re-checks immediately before each destructive call rather than trusting one
import-time check. Fails closed — exits 2 having touched nothing.

## `383a8ba` — the record

40 handoff archive files spanning 2026-07-30 to today; the archive had drifted
that far behind. 6 work orders, `docs/testing-feature-inventory.md`,
`docs/design-daily-handout.md`.

Data, each following an existing tracked convention rather than inventing one:
two ship captures (`constellation-aquila`, `gladius`) under
`data-layer/raw/<ship>/`; `buccaneer_hardpoints.json` alongside the tracked
`cutlass_black` equivalent; release snapshot `v0.3.9` alongside the other
tracked releases.

`model_rescale_report__20260730183923.json` **in, deliberately.** It is the only
per-file record of the 234-file in-place mutation that hard rule 5 exists
because of — before/after scale and dimensions for every ship touched.
Structured evidence of an irreversible bulk operation is worth keeping even
though it is a run artifact.

## LEFT OUT — one file, stated plainly

`rescale_run_output.log`, 183 KB of console output from that same run. Its only
unique content is four `[chassis cross-ref]` lines recording byte-identical
sibling copies, and that is already on disk in each ship's `MODEL_SOURCE.txt`
and in the archived handoff entry. Superseded, not lost. **It is still in the
working tree** — nothing was deleted, per rule 1. Say the word and it goes in.

## Note on the three commit messages

The first commit's message came out with a stray `@` as its subject line — I
used PowerShell here-string syntax in a bash call. Amended before pushing;
`7c0c59e` is the corrected commit and the malformed one never left this machine.

## Next

`schema_drift`'s unstable `details` first — it must land before Part D schedules
anything, or the same condition hashes to a new key every run and the schedule
manufactures ghosts on a timer. Then the rest of C0: the `pipeline_findings`
table and the 890-row backfill.
