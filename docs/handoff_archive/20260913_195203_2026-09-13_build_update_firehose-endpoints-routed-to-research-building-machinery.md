# Build update - RSI firehose watcher: three of four endpoints are not on this machine and are routed to Research; the watcher's machinery is being built with those sources loudly NOT CONFIGURED until verified

**Code (Build), 2026-09-13.**

**Read:**
- the master plan's watcher section
- both findings (`..._pays-an-ai-to-do-a-diff-2026-09-09.md`, `..._is-blind-and-the-knowledge-base-is-at-82-percent-2026-09-14.md`)
- `roadmap-watcher/` (main, board, livever, config, store, `.gitignore`, `go.mod`)
- `setup_roadmap_task.ps1`
- the `sc-brain/` tree

**The endpoint gap, measured:**
- **No DevTracker, Comm-Link-list or Patchbot endpoint is recorded anywhere in the repository.** The old Claude sweep's prompt lived in the deleted claude.ai scheduled task, and the findings quote its RESULTS, not its URLs.
- Its last state: all four sources returned `PROVENANCE_REQUIRED` for 27 runs. **That was its fetch tool being refused, which says nothing either way about a local HTTP client.**
- **Discovery is FIND OUT (rule 28), so a memo went to Research:** `..._rsi-firehose-endpoints-devtracker-commlink-patchbot.md` (exact URL, method, shape, plain-HTTP or not, stale-looking-fine traps). Build will CHECK each returned endpoint once before wiring it.
- **The LIVE build string is already solved:** the roadmap board's `data.description`, verified and parsed by `roadmap-watcher/livever.go`.

**Building now (ordered deliverables that do not need the URLs):**
- the `rsi-watcher/` Go package, mirroring `roadmap-watcher`:
  - `-check` on the same code path as the timer
  - a settings JSON (unsafe cadences refused; unknown keys refused)
  - a User-Agent
  - state in `sc-brain/plumbing/state/`
  - a baseline that is never news
  - three states: new, nothing new, and **did not look**
  - stuck-age staleness
  - cards in `sc-brain/cig-firehose/<shelf>/`
  - a wake marker only on a new CIG ID or build
- **tests on planted payloads,** and `setup_rsi_watcher_task.ps1` (a duplicate guard by command line; `-WhatIf` never elevated) **for Owner to run**
- **Sources without a verified endpoint are NOT CONFIGURED,** and every run says so; that is the order's PARTIAL. **Nothing is guessed.**

**P15:** still waiting on Architecture's `OWNERS.md` fix, then a re-sweep and the testing deploy.
