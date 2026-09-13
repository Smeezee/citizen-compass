# Build update - the watcher's 10-minute beat is built, proven, and swapped in; first beat due about 08:08

**Code (Build), 2026-09-12. Swap completed at 07:58:19 CDT.** This is Architecture's ruling on the beat. Sleven's word on the swap came directly in this session ("Yes, swap it").

## Built

- **`watcher-go/ticker.go`:** every 10 minutes it execs `venv\Scripts\python.exe scripts\desk.py fetch`, with a 2-minute timeout and no console window. Then it rewrites BOOT.md.
  - A failed fetch is logged, and the page is written anyway.
  - The 70-second rescan and the handoff are not touched by the beat.
- **`watcher-go/boot_poller.go`:** BOOT.md's `echo poller` line shows the last run's time, outcome, counts or reason, and its age.
  - It shows MISSING, UNREADABLE or NOT FOUND when the record is absent or bad, and STALE after three missed ticks.
- **A lock on BOOT.md's writes.** The mail path and the beat are now two writers inside one process, so `handoff_regen.go` also writes through the lock.
- **`scripts/desk.py`:** every fetch is recorded in `logs/desk_fetch_runs.json` (attempted_at, outcome ok / did-not-look / error, reason, counts, the last 50 runs).
  - **"Never ran" and "nothing to refuse" can no longer look alike.**

## Proven

- **Go:** `go vet` clean, the whole suite passes, and 8 new tests.
- **Beat mutations:** 5 of 5 caught (`_needs_review/beat_mutations.py`):
  - STALE check disabled
  - a missing record printing nothing
  - the beat stopping on a failed fetch
  - a failed run showing counts
  - the lock removed (the race test, run 5 times)

  One mutation first came back as a Go build failure, which is a flaw in the mutation, not a catch. I fixed it and reran.
- **`desk.py --self-test`:** PASS, with 6 new checks.
- **`desk.py` mutations:** 2 of 2 caught (`_needs_review/desk_run_mutations.py`).
  - The first run showed a no-op `record_run` crashing the self-test rather than failing a named check. I fixed the self-test so it fails by name.
- **Every self-test and mutation used temp paths.** The real `logs/desk_fetch_runs.json` did not exist until the live beat.

## Swapped

- **Before:** PID 18308, sha `d470f6bf...`.
- **After:** PID 44956, sha `74b08843...`, started 07:58:15, with exactly one watcher running.
- **Rollback copy, verified:** `_to_delete/inbox_watcher.exe.rollback-20260912c`.
- **The log says "Beat started: desk fetch + BOOT.md every 10m0s".**

**The first beat's result follows in the next update.**

**Not committed.** The watcher-go commit is still refused by the rule 2 hook for Code.
