# UPDATE — PART C COMPLETE: Go is the sole writer, Python path retired

Ruling actioned in the order given. Formatting fixed before deploy, comparison
re-run, binary deployed and verified by behaviour, Python path retired.

## 1. Formatting fixed — before the deploy, which was the point

`watcher-go/handoff_regen.go`: `%.1f` replaced with `trimNum()`, which uses
`strconv.FormatFloat(f, 'f', -1, 64)` — the shortest representation that
round-trips, so 35 prints as `35` and a genuinely fractional score keeps its
decimals. Matches Python exactly.

Doing this first is what stopped `35.0/100` being baked into the deployed
binary.

## 2. Comparison re-run — clean

| | Go (fixed) | Python |
|---|---:|---:|
| `###` headers | 35 | 35 |
| timestamped entries | 20 | 20 |

Diff after normalising line endings: **7 lines**, exactly the two expected
differences and nothing else —

1. the Go-only version-marker block (the KEEP feature)
2. Python's Ollama-fallback footer, which Go is correct to omit

The number formatting difference is **gone**.

**One correction to my own method:** my first re-diff reported 3,610 differing
lines and I nearly treated that as a new problem. It was my error — I had
dropped the trailing-whitespace normalisation used in the original comparison,
so CRLF/LF made every line differ. The fix was to the diff invocation, not the
code. Worth recording because a 3,610-line diff looks alarming and would have
triggered a spurious second stop.

## 3. Deployed — and the verification caught a real failure first

Old binary preserved at `_to_delete/inbox_watcher_PRE_GOFIX_20260801.exe`
(rule 1: replaced, not destroyed). Task stopped, binary swapped, task restarted.

**The first behavioural check FAILED, and it mattered.** The probe produced
70,680 chars, 7 phantom-looking headers, and `35.0/100` — the old behaviour —
even though the deployed file's SHA-256 matched the fixed build. Running the
deployed exe directly emitted `35/100` correctly, which proved the binary was
fine and a *stale process* was answering: the instance serving that probe
(PID 34800) predated the file swap.

A clean stop-kill-start left exactly one process (PID 21764), and the re-probe
passed:

| check | result |
|---|---|
| `**Project health score:**` | **`35/100`** — correct formatting live |
| completeness / viewers / docs | `0%` / `50%` / `100%` |
| timestamped entries in RECENT UPDATES | **20** — full display cap, zero phantoms |
| `pipeline_log.txt` delta | **0** — single writer |
| regeneration size | 85,986 chars |

**On the size:** the work order expected "the 100k range". Observed fixed runs
were 102,901 / 98,961 / 91,730 / 85,986. It fluctuates because every probe I
drop pushes an older entry out of the 20-entry window, so total length tracks
whichever 20 entries are current. All are far above the ~65,000 the defective
binary produced. The load-bearing evidence is structural, not size: **20 real
timestamped entries where the old binary filled the same 20 slots with roughly
7 fragments.**

Had I verified by process list or by hash alone, I would have reported a
successful deploy that was serving old output. Behavioural verification is what
caught it.

## 4. Python path retired

Checked first: **`generate_ai_brief.py` imports only `json`, `pathlib` and
`datetime`** — no dependency on anything being retired. The only importers of
`generate_handoff` were `inbox_watcher.py` and `_verify_generate_handoff.py`,
both retired in the same pass, so nothing is left importing a missing module.

Moved to `_to_delete/python_handoff_path_retired_20260801/` — **not deleted**,
per rule 1:

- `generate_handoff.py` (15,010 bytes)
- `inbox_watcher.py` (17,166 bytes)
- `_verify_generate_handoff.py` (4,362 bytes)

`inbox_watcher.py` in particular did `import generate_handoff`, so leaving it
behind meant a file that crashes on import if anything ever started it. Nothing
had deliberately stopped it earlier and nobody established what started it, so
removing it is what actually closes that hole.

## 5. CLAUDE.md additions

New section "How the handoff pipeline works (post Go migration, 2026-08-01)",
after the standing rule and before "What's here". Four items:

- the Go watcher is the **only** writer; `inbox/` is the sole supported path
- there is **exactly one** watcher process; the Python one must not be started
- the watcher logs to `logs/inbox_watcher.log`; `pipeline_log.txt` belongs to
  the retired path, and its growing again is the signal something revived Python
- **handoff compression no longer exists in any form** — retiring the Python
  generator removed the only implementation; if wanted again it is a new Go
  feature to build, not a flag to flip

## Finding, reported not acted on (out of scope)

**`image_handling.py` is now orphaned.** It documents itself as "import into
`inbox_watcher.py`", and nothing imports it any more. Its capability is not
lost — the Go watcher handles images natively (`classify.go`, `ocr.go`) — so
this is dead code rather than a functional gap. Left in place; boundaries say
nothing outside the three parts.

## Status

- **PART A** — condition met and verified; I did not stop the process, it had
  already stopped.
- **PART B** — script written and proven; **pull still BLOCKED**, the UEX token
  value does not exist on disk.
- **PART C** — complete.

**Phase 1 is NOT complete.** Source 6 has never been pulled.
