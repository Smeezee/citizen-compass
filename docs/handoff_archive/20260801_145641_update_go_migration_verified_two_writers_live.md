# Go handoff migration — work order verified, and both writers are live right now

2026-08-01. Sleven brought a Go migration work order authored by another AI. It was verified against the live repo rather than taken on report. **It is accurate.** Three things it does not cover were found and are recorded below.

Both documents are on disk: `docs/workorder-go-migration.md` and `docs/workorder-go-migration-addendum.md`. Read them together.

## Direction confirmed

The Go watcher becomes the single writer of `LATEST_HANDOFF.md`; `generate_handoff.py` is retired. Sleven restated this himself — the Python handoff generator merges into the Go system and Go becomes primary.

## Verified against the live repo

- `handoff_regen.go:108` — `strings.Split(string(raw), "\n### ")`. Confirmed verbatim.
- `handoff.go:49` and `handoff.go:65` — both call `firstRunesUpper(text, 500)`. Confirmed verbatim.
- Header counts: the order measured 61 total / 44 timestamped. Now 63 / 46. **The phantom count is 17 in both measurements** — the log grew by two real entries in between. That independently corroborates both readings rather than contradicting either.

The phantoms are genuine section headings inside update bodies (`### A1. Actual current state`, `### B2. What VerifiableMixin provides`, and similar).

## NEW — the double-write is happening today, not historically

```
pipeline_log.txt        [2026-08-01 14:27:46] regenerated (95526 chars)
logs/inbox_watcher.log  [2026-08-01 14:44:32] regenerated (update #58, 65421 chars)
```

Go ran 17 minutes after Python and replaced a 95,526-character document with a 65,421-character one — **30,105 characters of assembled handoff discarded by the later, defective writer.**

`LATEST_HANDOFF.md` as it stands holds 20 `###` headers of which only **13 are real timestamped entries**. Seven of twenty display slots are phantom fragments, so the document shows roughly two-thirds of the updates it should, with the shortfall invisible rather than flagged.

**No data was lost.** `_updates_log.md` is intact at 196,713 bytes and 72 archived update files are present. The archive is append-only and undamaged. This is a rendering defect in a generated summary. Fixing the parser and regenerating restores everything from sources that were never harmed.

## NEW — the second writer is a stray process, and this changes the delete step

`setup_watcher_task.ps1` registers **only** `inbox_watcher.exe`, and its own line 25 comment says the Go binary replaced the old `pythonw.exe inbox_watcher.py` setup. The scheduled task migrated correctly.

The Python watcher is running anyway. `inbox_watcher.py:46` does `import generate_handoff` and calls into it at lines 130-137. It is a leftover process from before the migration that was never stopped.

**The gap:** the work order's step 5 deletes `generate_handoff.py`. With `inbox_watcher.py` still running, that is not a clean retirement — the Python watcher either dies on `ImportError` at next restart and fills a log with tracebacks, or keeps running on an already-imported module and continues fighting the Go watcher.

**Required extra step, before the delete:** stop the stray `inbox_watcher.py` process and verify it stays stopped by observed behaviour — drop a test file into `inbox/` and confirm only `logs/inbox_watcher.log` gains a line while `pipeline_log.txt` does not. A silent process is not a stopped process.

**Recommended resequencing:** stop the stray watcher *first*, independent of the Go fixes. It takes a moment and immediately stops the two writers clobbering each other. Every inbox drop between now and the Go fix otherwise leaves the handoff in whichever state the loser wrote.

## NEW — a third line for the CLAUDE.md additions

> **There is exactly one watcher process.** The Go `inbox_watcher.exe` registered by `setup_watcher_task.ps1` is it. The Python `inbox_watcher.py` is retired and must not be started. Two watchers on the same `inbox/` directory silently overwrite each other, and the only visible symptom is a handoff document that changes size for no apparent reason.

Also: **hard rule 13** postdates this work order and applies to it — file on intake, file on completion.

## Endorsed unchanged

Both defect diagnoses and both replacement implementations. The two edge cases in the new `parseUpdateEntries()` (empty header set, preamble preservation) are load-bearing and must not be trimmed as defensive extras. The Go-only `Update #N` header is preserved. And step 4's stop condition stands: if Go and Python still disagree after both fixes, there is a third difference — stop and report, do not assume Go is correct because it was fixed twice.

Ollama stays parked. Sequence remains: after CC-10/CC-12, except for stopping the stray watcher, which need not wait.
