# Build update - work arrived: the tray-noise dry-run list (then hold); the watcher swap and the 873-file backlog commit both landed, and neither was run by Build

**Code (Build), 2026-09-13. Clock read at 15:05:29.** Sleven's message: "go". Tray listed: `2026-09-13_memo_build_next-tray-noise-dry-run-list-only.md` (14:57, Architecture).
- **The order:** list each stale open letter in Build's tray against what closed it. **A dry-run list only, and nothing is edited.** File it to Architecture, then STOP and wait.

**WHAT CHANGED, checked from the record, not taken:**
- **The watcher swap happened at 13:57:14.** The running `inbox_watcher.exe` (PID 10384) hashes `1278201c...`, the candidate.
- **The bulk gate worked as built.** The 14:07:15 beat logged `mail commit: bulk - 866 path(s) ... --approve 225016d03711eefc` and committed nothing.
- **`24ce797`, 14:49:45:** 873 files (543 `correspondence/`, 330 `docs/handoff_archive/`), author and committer `Citizen Compass Watcher <watcher@local>`.
  - Its receipt: `committed`, until `2026-09-13 14:39:39`, batch `564731e77d28e8e1`.
  - **So it was a hand-run `--commit --until ... --approve`,** not the beat, which was gated to the next hour. **Build did not run it, and the receipt does not record who did.**
  - It has since been pushed: main is 0/0 with origin. The script itself never pushes.
- **`6ae6791` (Sleven):** `Owner-action:` added to the three owner letters. **`_verify_owner_asks` now PASSES** (real run, exit 0), so the sweep's owner-ask red is gone.

**Now:** the read-only tray triage.
