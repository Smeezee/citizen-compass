# Build update - the live watcher is swapped to the BOOT.md build

**Code (Build), 2026-09-12. Swap completed at 06:27:52 CDT.** Sleven's word came directly in this session ("Yes, swap it").

- **Before:** PID 45220, `inbox_watcher.exe` sha256 `1dca1fde9aca383b...` (the three mail repairs).
- **After:** PID 18308, started 06:27:48, sha256 `d470f6bfaf4c1455...` (the three mail repairs plus BOOT.md). **Exactly one watcher is running.**
- **Rollback copy, verified:** `_to_delete/inbox_watcher.exe.rollback-20260912b` (1dca1fde). The older `...rollback-20260912` (f9d983b2) is still there.
- **How:** `_needs_review/swap_watcher_boot.ps1`.
  - The first run, at 06:26:43, aborted in preflight before any change. `.Count` on a single CIM object is empty in PowerShell 5.1.
  - I confirmed nothing had moved, fixed the script with `@()` at each call site, and the second run succeeded.

**This letter is also the first live test:** it should make the new watcher write `BOOT.md` at the root and put the pointer in `LATEST_HANDOFF.md`. The result follows in the next update.
