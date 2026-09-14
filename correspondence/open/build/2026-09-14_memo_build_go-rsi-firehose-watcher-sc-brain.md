# Memo

To:      Build
From:    Architecture (Grok covering C1)
Date:    2026-09-14
Status:  Open
Subject: GO — build local RSI firehose watcher (Claude hourly replacement) filing into sc-brain/cig-firehose
Owner-action: no

**Owner word:** Sleven 2026-09-14 in Architecture chat — "Yeah, go ahead and build the watcher."

## WHY
Claude RSI hourly sweep is being shut down / is blind. Quiet hours need a **local free diff** (pattern: `roadmap-watcher/`). AI wakes only on real new IDs later (v1 = no AI).

## READ FIRST
- `docs/SC-BRAIN_master-acquisition-plan-2026-09-14.md` (A + RSI local watcher)
- `claude/FINDING_the-rsi-watcher-pays-an-ai-to-do-a-diff-2026-09-09.md`
- `claude/FINDING_the-rsi-watcher-is-blind-and-the-knowledge-base-is-at-82-percent-2026-09-14.md`
- Mirror: `roadmap-watcher/`, `setup_roadmap_task.ps1`, `setup_watcher_task.ps1`
- File into: `sc-brain/cig-firehose/{devtracker,comm-link,patchbot,patches}/`
- State: `sc-brain/plumbing/state/` (+ local state next to exe if needed)

## QUIET HOUR (NO AI)
1. GET DevTracker, Comm-Link list, Patchbot (cache-bust query)
2. Diff post IDs vs stored set
3. Diff LIVE build string vs stored
4. Detect staleness (stuck relative-age; unreachable sources) — quiet ≠ blind
5. Write state
6. On NEW: structured JSON/cards (id, url, title, time) under sc-brain shelves — no model summaries
7. Notify / wake-marker only on change (trigger = CIG IDs/build only)

## OUT OF SCOPE (v1)
- Roadmap polling (`roadmap-watcher` owns it)
- Erkul/SPViewer scrape, citizen-collector, StarBreaker
- Registering the Scheduled Task yourself — ship `setup_rsi_watcher_task.ps1`; Owner runs it
- Headless Chromium unless a plain HTTP endpoint already works (document PARTIAL)
- LLM classify/summarize

## DELIVER
1. Go package e.g. `rsi-watcher/` (config JSON, `-check` = same path as timer, User-Agent, tests)
2. `setup_rsi_watcher_task.ps1` (duplicate-guard by cmdline; elevation keeps -WhatIf)
3. README + master-plan row update (HAVE/PARTIAL)
4. OWNERS claim for the new dir
5. Build + prove one `-check` run; STOP with receipt (paths written, quiet vs change)

Investigate real endpoints from findings / old sweep prompts — verify, don’t guess.

*Architecture (Grok covering C1), 2026-09-14.*