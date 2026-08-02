# ADDENDUM to the Go migration work order — verified 2026-08-01

Read this **with** `citizencompassgomigrationworkorder.md`, not instead of it. That order is sound and its two defects are real. Everything below was measured directly against the live repo, and it changes the execution order.

---

## 1. The work order's claims — verified, with drift noted

| claim | as written | measured now | verdict |
|---|---|---|---|
| `parseUpdateEntries()` splits on `"\n### "` | line 108 | `handoff_regen.go:108` — `strings.Split(string(raw), "\n### ")` | **confirmed, verbatim** |
| `firstRunesUpper(text, 500)` in both classifiers | lines 49, 65 | `handoff.go:49` and `handoff.go:65` | **confirmed, verbatim** |
| headers in `_updates_log.md` | 61 total / 44 timestamped → 17 phantoms | 63 total / 46 timestamped → **17 phantoms** | **confirmed** — the log grew by 2 real entries since they measured; the phantom count is identical, which independently corroborates both measurements |

The phantoms are real section headings inside update bodies — `### A1. Actual current state`, `### B2. What VerifiableMixin provides`, and so on. Exactly the failure described.

---

## 2. NEW — both writers are running *right now*, and this is measurable today

The work order describes the double-write as an observation from earlier. It is not historical. Both wrote **today**:

```
pipeline_log.txt        [2026-08-01 14:27:46] LATEST_HANDOFF.md regenerated (95526 chars)
logs/inbox_watcher.log  [2026-08-01 14:44:32] LATEST_HANDOFF.md regenerated (update #58, 65421 chars)
```

Go ran 17 minutes after Python and replaced a 95,526-character document with a 65,421-character one. **30,105 characters of the assembled handoff were discarded by the later, defective writer.**

### The damage, in the file as it stands

`LATEST_HANDOFF.md` currently contains **20 `###` headers, of which only 13 are real timestamped entries.** Seven of the twenty display slots are phantom fragments. The document is showing roughly two-thirds of the updates it is supposed to show, and the missing third is invisible rather than marked absent.

### But no data has been lost — state this plainly so nobody panics

`docs/handoff_archive/_updates_log.md` is intact at 196,713 bytes, and 72 archived update files are present. The archive is append-only and undamaged. **This is a rendering defect in a generated summary, not data loss.** Fixing the Go parser and regenerating restores the full document from sources that were never harmed.

---

## 3. NEW — the second writer is a stray process, not a scheduled one

This changes the delete step.

`setup_watcher_task.ps1` registers **only** `inbox_watcher.exe` (line 26), and its own comment at line 25 says the Go binary replaced "the old pythonw.exe inbox_watcher.py setup." So the scheduled task migrated correctly.

The Python side is still running anyway. `inbox_watcher.py` line 46 does `import generate_handoff` and calls into it at lines 130–137. Something started that process and it has never been stopped — it survives as a leftover from before the migration and is still watching `inbox/`.

**Consequence the work order does not cover:** its step 5 deletes `generate_handoff.py`. If `inbox_watcher.py` is still running when that happens, the Python watcher does not stop cleanly — it dies on `ImportError` at its next restart and fills a log with tracebacks, or keeps running on an already-imported module and continues fighting the Go watcher until something restarts it. Neither is a clean retirement.

### Required extra step, before step 5

**Stop the stray `inbox_watcher.py` process and confirm it stays stopped.** It is not registered as a scheduled task, so it will not come back on its own after a reboot — but it must be stopped explicitly rather than left to a future restart, because until it stops the two writers keep overwriting each other.

Confirm it is gone the way you would confirm anything else here: drop a test file into `inbox/`, then check that **only** `logs/inbox_watcher.log` gains a line and `pipeline_log.txt` does not. A silent process is not a stopped process — verify by observed behaviour, not by absence from a process list.

---

## 4. NEW — one more line for the CLAUDE.md additions in step 6

The work order's step 6 adds two rules. Add a third:

> **There is exactly one watcher process.** The Go `inbox_watcher.exe` registered by `setup_watcher_task.ps1` is it. The Python `inbox_watcher.py` is retired and must not be started. Two watchers on the same `inbox/` directory silently overwrite each other's output, and the only visible symptom is a handoff document that changes size for no apparent reason.

Also note that **hard rule 13** now exists (file the handoff before you move on) and postdates this work order. It applies to this task like any other: file on intake, file on completion.

---

## 5. Execution order — revised

The work order says run after Task 2 and after CC-10/CC-12. Task 2 is complete (`b017096` pushed). CC-10/CC-12 is in flight. Keep that ordering, with one change:

1. **Stop the stray Python watcher first.** This is independent of the Go fixes, takes a moment, and immediately stops the two writers from clobbering each other. Do it before or alongside the schema work — it does not need to wait.
2. Then Defect 1, Defect 2, rule-12 proofs, comparison run, delete, CLAUDE.md — exactly as written.

Rationale for splitting it: every inbox drop between now and the Go fix triggers both writers and leaves the handoff in whichever state the loser wrote. Stopping the stray process makes the record stable while the real fix is built, rather than leaving a known-corrupting process live for the duration.

---

## 6. Unchanged and endorsed

- Both defect diagnoses and both replacement implementations, as written.
- The two edge cases in the new `parseUpdateEntries()` — empty-header-set and preamble preservation. They exist to avoid silently dropping content and must not be trimmed as "defensive extras."
- Preserving the Go-only `Update #N` header.
- Step 4's stop condition: if Go and Python output still disagree after both fixes, **there is a third difference — stop and report.** Do not assume Go is correct because it was fixed twice.
- Ollama stays parked. The watcher process and its scheduled task are healthy.
