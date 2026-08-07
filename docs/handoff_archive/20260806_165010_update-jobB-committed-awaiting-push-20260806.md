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
