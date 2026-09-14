# Build update - work arrived: the local RSI firehose watcher (Architecture's go, Owner's word), filing into sc-brain/cig-firehose; reading first

**Code (Build), 2026-09-13.** The letter is `2026-09-14_memo_build_go-rsi-firehose-watcher-sc-brain.md` (filed 19:30; it is dated 2026-09-14 while the local date is 09-13).

**The order:**
- A Go package (for example `rsi-watcher/`) mirroring `roadmap-watcher/`: config JSON, `-check` taking the same path as the timer, a User-Agent, and tests.
- **A quiet hour with NO AI:**
  - GET DevTracker, the Comm-Link list and Patchbot (with a cache-bust)
  - diff post IDs against the stored set, and the LIVE build string against the stored one
  - detect staleness ("quiet is not blind")
  - write state
  - on NEW: structured JSON cards under the sc-brain shelves
  - a wake marker only on change
- **Also deliver:** `setup_rsi_watcher_task.ps1` (a duplicate guard by command line, and elevation that keeps `-WhatIf`) **for Owner to run, not Build**, plus a README, a master-plan row, and an OWNERS claim. Then build and prove one `-check` run, and STOP with a receipt.
- **Out of scope:** roadmap polling, scraping, the collector, StarBreaker, **registering the task**, headless Chromium unless plain HTTP works (otherwise PARTIAL), and any LLM.
- "Investigate real endpoints from findings / old sweep prompts - verify, don't guess."

**Binding rules noted:**
- rule 22: nothing under `/media/` on robertsspaceindustries.com
- rule 6: Task Scheduler is Owner's; Build ships the script and does not run it
- rule 12: the `-WhatIf` flag is proven by behaviour
- rule 7: no downloaded code is executed

**P15 state:** built and verified. Its receipt is filed, and its deploy waits on Architecture's `OWNERS.md` fix and a re-sweep.

**Now, read-only:**
- the master plan's watcher section and the two findings
- `roadmap-watcher/`'s shape
- the `sc-brain/` tree
