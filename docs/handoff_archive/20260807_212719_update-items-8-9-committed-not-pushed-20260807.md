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
