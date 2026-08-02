# UPDATE — PART C: both Go defects fixed and proven; STOPPED at step 4's stop condition

Defects 1 and 2 are fixed and proven against known-bad input. Step 4's
comparison found a **third difference**, so per the work order I have stopped
and am reporting rather than proceeding to delete `generate_handoff.py`.

## Defect 1 — invented entries — FIXED

`watcher-go/handoff_regen.go`. `strings.Split(string(raw), "\n### ")` replaced
with `updateEntryHeaderRe`, matching only the headers `appendUpdate()` writes.
Both required edge cases preserved: an empty header set returns the whole file
as one entry, and preamble before the first header is kept.

Also extracted `parseUpdateEntriesFrom(path)` so the parser can be exercised
against fixtures rather than only whatever the live log happens to hold.
`parseUpdateEntries()` calls it with `updatesLogPath()` — behaviour unchanged.

## Defect 2 — classification by prose — FIXED

`watcher-go/handoff.go`. `titleLine()` added; both `isHandoffDoc()` and
`isUpdateDoc()` now use it instead of `firstRunesUpper(text, 500)`.
**Evaluation order unchanged** — filename hints first, `isHandoffDoc()` before
`isUpdateDoc()`, a doc matching both is a full handoff. `firstRunesUpper` had no
remaining callers and was removed, with a comment recording what it was and why
it went.

## Rule 12 — proven, not asserted

`watcher-go/handoff_defects_test.go` and `handoff_livelog_test.go`. `go build`,
`go vet` and `go test ./...` all clean.

| test | asserts |
|---|---|
| subheadings stay inside their entry | a body with two `###` subheadings yields **1** entry, not 3, and keeps both |
| no headers returns whole file | content is not dropped |
| preamble preserved | text before the first header survives |
| hyphen separator parses | `-` works as well as `—` |
| update mentioning "handoff" in BODY | classified as **update**, not handoff |
| genuine handoff title | still detected (`CITIZEN COMPASS HANDOFF`, `SESSION ARCHIVE`) |
| filename hint still wins | evaluation order intact |
| `titleLine` | first heading, else first non-blank line |
| **live `_updates_log.md`** | **70 total `###` headers -> 50 parsed entries, 0 phantoms** |

Python (fixed) on the same live log: **50 entries, 0 phantoms.** Identical.

## Step 4 — the comparison, and the STOP

Built the fixed binary and regenerated via `--once`, then regenerated with
`generate_handoff.py`, and diffed.

**The improvement is real and large:** fixed Go emitted **102,901 chars** where
the deployed binary was emitting ~65,000. That recovers almost exactly the
~37,000 characters the addendum measured as discarded.

**Both defects are confirmed fixed by structural comparison:**

| | Go (fixed) | Python (fixed) |
|---|---:|---:|
| `###` headers in output | 40 | 40 |
| timestamped entries shown | 20 | 20 |

Identical. No phantoms, no classification divergence.

### But the outputs still disagree — third difference found

Beyond the Go-only version-marker block (which is the KEEP feature and is
expected), the diff is 21 lines in two groups:

**1. Number formatting — 5 lines.**

| Go | Python |
|---|---|
| `**Project health score:** 35.0/100` | `**Project health score:** 35/100` |
| `- Data completeness: 0.0%` | `- Data completeness: 0%` |
| `- Viewer progress: 50.0%` | `- Viewer progress: 50%` |
| `- Documentation: 100.0%` | `- Documentation: 100%` |
| `**Ships:** ... (50.0%)` | `**Ships:** ... (50%)` |

**2. Python emits a trailing line Go has no equivalent for:**

```
*(raw text of the most recently adopted handoff doc — local AI compression
unavailable right now, showing it unmodified)*
```

That is Python's Ollama-fallback footer. Ollama is disabled and parked, so
Python takes the fallback path and says so; Go never compresses at all, so it
has nothing to report.

### Why I am stopping rather than judging

The work order is explicit: *"If they still disagree there is a third difference
— stop and report, do not assume Go is correct because it was fixed twice."*

They disagree. I can characterise both differences and neither touches entry
content or classification — but "I can explain it" is not "it matches", and this
is precisely the reasoning the stop condition exists to prevent. **Not
executed:** step 5 (delete `generate_handoff.py` and `_verify_generate_handoff.py`)
and step 6 (the CLAUDE.md additions).

### The decision these need

- **Number formatting:** which is correct? Python's `35/100` reads better;
  Go's `35.0/100` is what the live document will show. One of them should
  change so the two agree, or Python's retirement makes it moot.
- **The Ollama footer:** Go is arguably right to omit it, since it never
  attempts compression. If so, this difference is expected rather than a defect
  — but that is a call to make explicitly, not to assume.

## Deployment state — the fix is NOT live

`inbox_watcher_fixed.exe` (5,735,424 bytes, built from fixed source) sits in the
repo root. `inbox_watcher.exe` (3,884,032 bytes, 29 July) is still the binary
the scheduled task runs.

**So the live watcher is still the defective one**, still emitting ~65k with
phantoms. Replacing it means stopping the scheduled task to unlock the file, and
I have not done that — deploying while an unexplained third difference stands
would bake in whichever formatting Go happens to use. Say the word and it is a
two-minute change.

Nothing deleted. `generate_handoff.py`, `_verify_generate_handoff.py` and
`inbox_watcher.py` are all still on disk. Comparison artifacts moved to
`_to_delete/go_migration_comparison_20260801/`.
