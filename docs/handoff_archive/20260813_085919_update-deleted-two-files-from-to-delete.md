# Update — deleted the two files I had put in `_to_delete/`, on Sleven's instruction. The other 38 entries were not touched.

Sleven: *"delete the two files in _to_delete"*.

```
40 entries before  ->  38 after
```

Removed, and only these:

```
git_index.lock_stale_from_193856_moved_20260812_202803    0 bytes
zz_burst_focus_test.go_scratch_diagnostic_20260813      493 bytes
```

## Why I checked rather than just running rm

`_to_delete/` is not a scratch bin - it holds **40 entries going back to
2026-07-28**, including `python_handoff_path_retired_20260801`,
`models.py.bak_pre_ship_items_20260730`, `CLAUDE.md.bak.1785617770` and a
3.9 MB pre-fix `inbox_watcher.exe`. "The two files in `_to_delete`" meant the
two I added, not the directory - so I listed it first, named both targets with
their byte counts, confirmed the lock really was 0 bytes, deleted by explicit
path, and counted before and after.

Deleting that directory wholesale would have taken out months of other people's
set-asides.

## Rule 1

Rule 1 says never delete and that Sleven deletes it himself. He asked directly,
for these two, so this is his call being carried out rather than my judgement
about what is junk - which is the thing the rule actually guards against.

Both were recoverable had it been wrong: one is an empty file, and the other is
an eleven-line `go test` wrapper whose content is in the session transcript and
which calls `runHotkeyBurstSelftest` - still registered in `-selftest`, so
nothing that tests anything was lost.

## Unchanged

`_to_delete/` is gitignored, so none of this touches the repo or the push. HEAD
is still `6dde2bd`, matching origin.
