# rsi-watcher

The local, free, no-AI replacement for the Claude hourly RSI sweep. Architecture's order, with the Owner's word, 2026-09-14: `2026-09-14_memo_build_go-rsi-firehose-watcher-sc-brain.md`. The reasoning is in `claude/FINDING_the-rsi-watcher-pays-an-ai-to-do-a-diff-2026-09-09.md`.

**A quiet hour is a diff, not a thought.** Each hour:
1. Read each configured feed and the roadmap board's `Live Version` / `PTU Version` line.
2. Diff post ids and the build against what `sc-brain/plumbing/state/rsi-watcher-state.json` already holds.
3. For each **new** CIG item, write one JSON card to its shelf under `sc-brain/cig-firehose/`.
4. Only when something changed, write `sc-brain/plumbing/state/rsi-watcher-wake.json`.

No model runs. The trigger is a CIG id or a build string, which nothing a woken session writes can produce.

    rsi-watcher.exe            run on the configured cadence (hourly)
    rsi-watcher.exe -check     one pass now - the same code path as the timer
    rsi-watcher.exe -status    what is known; polls nothing

## Every pass ends in one of these, never confused

| Outcome | Meaning |
|---|---|
| `BASELINE` | The first read of a source or the build. Recorded as known, **never news**. It is per source, so a feed configured later arrives as a baseline. |
| `NEW` | Cards written, plus the wake marker. |
| `CHECKED, NOTHING NEW` | Every surface is named: which were read, which failed, which were stale, which are not configured. |
| `DID NOT LOOK` | Nothing could be read. `last_good` does not move. |

**Per source, these are also "did not look", never quiet:**
- a non-200
- a 200 carrying a failure envelope
- a 200 with zero readable items
- a newest post whose relative age ("51 minutes ago") has not moved in `stale_age_minutes`

## Endpoints: NOT CONFIGURED until verified

**On 2026-09-13 no DevTracker, Comm-Link-list or Patchbot endpoint was recorded on this machine.** Discovery was routed to Research: `2026-09-13_memo_research_rsi-firehose-endpoints-devtracker-commlink-patchbot.md`.

Each feed is plain config in `rsi-watcher-settings.json`. It is written with defaults on first run, and unknown keys are refused:

```json
{ "name": "devtracker", "shelf": "devtracker", "url": "", "method": "GET",
  "format": "json", "items_path": "data.items", "id_field": "id",
  "title_field": "title", "url_field": "url", "time_field": "time",
  "success_field": "success", "success_value": "1",
  "cache_bust_param": "cb", "url_prefix": "https://robertsspaceindustries.com" }
```

- **An empty `url` is NOT CONFIGURED:** named on every run, never polled.
- **HTML feeds** use `"format": "html"` and an `item_regex` with named groups `id` (required), `title`, `url` and `time`.
- **The build line** comes from `https://robertsspaceindustries.com/api/roadmap/v1/boards/1`. It is the same field `roadmap-watcher/livever.go` parses. `livebuild.go` is a stated twin, to be folded into one package later.

## Build and test

    cd rsi-watcher
    $env:GOWORK = "off"; go vet .; go test .; go build -o rsi-watcher.exe .

## Scheduling is Owner's (hard rule 6)

`setup_rsi_watcher_task.ps1`, at the repo root:
- It registers an hourly `-check`.
- **It refuses** if any other task already runs `rsi-watcher`, matched on the command line, not the name.
- **`-WhatIf` prints what it would do and exits before touching anything**, elevated or not.

Build ships the script; the Owner runs it.

## Rules it keeps

- **Rule 22:** it never requests anything under `/media/` on robertsspaceindustries.com.
- **Politeness:** hourly is the floor, and every request carries a User-Agent naming Citizen Compass.
- **A card is never written twice.** An id cannot name a path outside its shelf.
