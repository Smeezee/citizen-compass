# UPDATE — work-order batch committed and pushed

Completes the record for the previous entry
(`update_workorder_source2_reland_task2_blocked`), which was written before the
commit and therefore did not record its outcome.

## Commit

`cf57eee` — "Re-land source 2 verified, correct two manifest diagnoses, add hard
rule 12". 13 files, 1,138 insertions, 35 deletions.

## Push

```
f58a9be..cf57eee  main -> main
```

| | |
|---|---|
| HEAD | `cf57eeed05f4b6d3c86a0a2063a0952a22ba49cb` |
| origin/main | `cf57eeed05f4b6d3c86a0a2063a0952a22ba49cb` |
| in sync | YES |
| ahead of origin | 0 |

## What went public

- Source 2 snapshot `20260801T171748Z` manifest, gate report, pre/post-scan hash
  sets, and its `_build_manifest.py`
- `20260801T042157Z` marked `superseded` (append-only, +19/-2)
- Correction notes appended to both published source 3 manifests
  (`20260731T031754Z`, `20260731T041451Z`) — diagnosis only, no acquisition
  record altered
- `CLAUDE.md` hard rule 12, "a check that cannot fail is not a check"
- `docs/EXTERNAL_SOURCE_STATUS_VOCABULARY.md` amendment
- Two handoff archive entries

Largest staged blob 16 KB. Zero raw snapshot data, zero handoff aggregates.

## Unchanged and still open

- **Task 2 remains STOPPED** — the work order defining it has still not been
  received, and neither has `session-addendum-2026-08-01.md`. Source 1 was not
  touched. The Git LFS trap documented in the previous entry stands: any
  re-acquisition that does not resolve LFS returns pointer stubs that look like
  data and report success.
- Tasks 1 and 3 skipped as instructed, not started.
- CC-10 and CC-12 untouched, per boundaries. CC-12's numbers remain measured and
  clean (0 NULLs, 0 duplicates, no blockers) if that work is ever picked up.
