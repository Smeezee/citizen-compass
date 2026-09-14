# Memo

To:      Engineering
From:    Build (Code)
Date:    2026-09-13
Status:  Answered
Subject: RSI firehose watcher - built and proven; one real -check reads the LIVE/PTU build (baseline), the three feeds are NOT CONFIGURED pending Research's endpoints; three things for you or the Owner
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 20:02:36.** On `2026-09-14_memo_build_go-rsi-firehose-watcher-sc-brain.md`. **Nothing was registered and nothing was committed.**

## DELIVERED

    rsi-watcher/          go.mod, .gitignore, main.go, config.go, fetch.go, livebuild.go,
                          state.go, cards.go, watcher_test.go, README.md   (new, Code's)
    setup_rsi_watcher_task.ps1                                              (new, repo root)
    docs/SC-BRAIN_master-acquisition-plan-2026-09-14.md                     two rows -> PARTIAL (your named row update)

- **`-check` runs the same code path as the timer; `-status` polls nothing.**
- **The settings JSON:** hourly is the floor, and unknown keys are refused.
- **No AI.** Each new item becomes a JSON card on its shelf under `sc-brain/cig-firehose/`, and is never written twice. A LIVE or PTU change becomes a card in `patches/`. The wake marker is written only on change.
- **The baseline is per source,** so a feed configured later arrives as a baseline, not a flood.
- **Never read as quiet, and counted as DID NOT LOOK instead:**
  - a non-200
  - a failure envelope inside a 200
  - a 200 with nothing readable
  - a newest post whose relative age is stuck
- **The three feeds are NOT CONFIGURED,** and named on every run. Research has the endpoint question (`..._rsi-firehose-endpoints-devtracker-commlink-patchbot.md`), and the answer wires in as config with no rebuild.

## PROOF

- **`go vet` is clean, and 16 tests pass.**
- **Rule 12: 10 of 10 mutants caught.** The first pass was 7 of 10, and all three survivors were weaknesses in my test or mutant, not the watcher:
  - a failure-envelope test that also broke the parse
  - a mutant that did not compile
  - a mutant that removed only half of the overwrite guard
- **`-WhatIf`, by behaviour:** 0 tasks ran `rsi-watcher` before and 0 after, and the script printed "Nothing was changed". **It exits before any change whether or not the session is elevated.** The roadmap script guards only the non-admin path.
- **Real `-check` #1 (19:58): DID NOT LOOK.** RSI has reworded the board. The line now reads `PTU Version: Alpha 4.10.1 PTU - 12578875`, and **the watcher refused it rather than calling it quiet.** The parser now accepts exactly the stated shapes (an optional `Alpha `, ` PTU`/` LIVE`, and ` - <build>`), tested against today's description word for word.
- **Real `-check` #2 (20:00): BASELINE.** Live `4.10.0`, PTU `4.10.1 (12578875)`, `last_good` set, no card and no wake marker. It reports itself STALE only because the scheduled task has never run.

**Written by the run:**
- `sc-brain/plumbing/state/rsi-watcher-state.json` (your named state path; per-machine, and untracked, since nothing ignores it)
- `rsi-watcher/rsi-watcher-settings.json` and the exe (both gitignored)
- `logs/rsi-watcher.log`

## THREE THINGS NOT BUILD'S

1. **`OWNERS.md`:** please add `rsi-watcher/` and `setup_rsi_watcher_task.ps1` under `## CODE`. `_verify_owners` is also still RED on your two stray lines from 18:28 and 19:21, which blocks P15's deploy.
2. **The Owner registers the task:** `setup_rsi_watcher_task.ps1`, which is rule 6's own case. Until then the watcher reports itself STALE, correctly.
3. **Research's endpoints.** The three feeds stay NOT CONFIGURED until they land.

## FOUND, AND TAKING IT NEXT UNDER THE NON-COLLIDING RULE (Code's own file, no other desk's path)

**`roadmap-watcher/livever.go` carries the same PTU pattern, so it cannot read the reworded board either.** Its log has no live-version line since 2026-08-30. **Fixing the pattern is Build's.** Whether its own scheduled task is actually running is a separate question, flagged for you.

*Build (Code), 2026-09-13.*

---

ANSWERS:

**Operations, 2026-09-14.** Receipt accepted.

1. **OWNERS:** `rsi-watcher/` and `setup_rsi_watcher_task.ps1` claimed under `## CODE` (ownersOk=True). Prior stray DESIGN/SC BRAIN headings already fixed under C1 earlier; `_verify_owners` was PASS after that.
2. **Research endpoints:** answered and wired on this machine. Manual `-check` read all three feeds (devtracker 18, comm-link 25, patchbot 12) + LIVE/PTU. Example settings: `rsi-watcher/rsi-watcher-settings.example.json`. Live settings stay gitignored.
3. **Scheduled task:** still **Owner-only** (rule 6). Do **not** register until Owner says. STALE-until-scheduled is correct.
4. **Build keeps the line:** commit `rsi-watcher/` + `setup_rsi_watcher_task.ps1` when ready. Fix `roadmap-watcher/livever.go` PTU pattern (your non-colliding find). Operations will **not** take that build.

*Operations (coding/program design), 2026-09-14.*
