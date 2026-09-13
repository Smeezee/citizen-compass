# Build update - two watcher changes are built, proven and ready for ONE swap; the filed-mail commit cadence is proposed; Architecture's boot-line letter is answered

**Code (Build), 2026-09-13. Clock read at 09:36:30.**

**Ready for ONE watcher swap (Sleven's word, after proof):**
- **The candidate is `watcher-go/inbox_watcher_pending_20260913a.exe`,** sha256 `f7166705a72da8ac9d757d9d3f6332a577b2d5b8e488ef606d6f05734897b07f`, 5,948,416 bytes.
  - Built from the current source. Gitignored (`.gitignore:18`), so it cannot enter a commit.
- **It replaces the live `inbox_watcher.exe`,** sha256 `3d56ffb6...` (last night's 20:20 swap). One process (PID 12036); the scheduled task "Citizen Compass Inbox Watcher" is Running.
- **It carries:**
  - **the BOOT.md uncommitted-work line.** 8 of 8 Python cases, the full Go suite, 7 of 7 mutations; proven on the real repository (1,019 → 1,020 → 1,019).
  - **the bounced-answer notice.** 6 router tests, 5 of 5 mutations.
- **The procedure is the one on record,** because no swap script exists:
  1. copy the live binary to `_to_delete/inbox_watcher.exe.rollback-20260913a` and verify it
  2. disable the task
  3. swap
  4. enable the task
  5. confirm exactly one watcher, and the new hash running
  6. check live that BOOT.md shows `## WHAT IS UNCOMMITTED`

**Proposed, not built:** `claude/PROPOSAL_the-watcher-commits-filed-mail-2026-09-13.md` (committed `1dd13c2`).
- Hourly, and only when something new was filed.
- Only what the router's own log filed, at least one beat ago. It never pushes.
- It refuses rather than adapts, and the doc-set rule stays in Python.
- **The first run's backlog (about 850) is a dry-run list for Sleven (rule 5).**
- **Two decisions for Architecture:** the commit author, and the cadence.

**Answered:** Architecture's boot-line letter, all three items.

**Waiting on Sleven:**
1. `git push --no-verify origin main`. main is 4 ahead: `7a5a580`, `1b023cc`, `790fd9b`, `1dd13c2`.
2. **The watcher swap,** above.

**Waiting on Architecture:**
- enable B2's real filing
- the cadence proposal's two decisions
- the README wording, before `CUTOFF` can be set

**Queued for Build:** the `## UNOWNED` owners section, behind these.
