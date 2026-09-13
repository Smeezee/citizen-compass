# Build update - the Status-line refusal and BOOT.md's unreadable count are built and proven; swap asked of Sleven

**Code (Build), 2026-09-12. Clock read at 20:13:33.**

- **`watcher-go/memo.go`: a memo with no `Status:` line, or a value outside {Open, Answered, Closed, Done}, is refused to `_needs_review/` at filing,** with the reason and what to add.
  - The list is the one measured on disk plus Done.
  - Before this, `readMemo` defaulted a missing Status to "open", so such letters filed silently.
- **`watcher-go/boot.go`: "WHAT IS OPEN - LETTERS" now prints an `unreadable` column per desk, and 0 is printed.**
  - It reads the router's own list, so the two cannot disagree.
- **Proof:**
  - vet is clean and the full suite passes. Every value in use still files, and the existing four-status routing test still passes.
  - **9 of 9 mutations are caught.** New: the refusal switched off, the list accepting anything, and the count removed.
- **The real tree, audit-only:** unreadable counts are owner 20, build 14, research 4, design 3, architecture 0, audit 0. The owner count includes `BOARD.md` and `OWNER-BOARD.md`, which are not letters.
- **The candidate binary is `watcher-go/inbox_watcher_pending_20260912e.exe`** (sha 3d56ffb6).
  - **The swap needs Sleven's word,** and it is asked.
  - Live test letters follow the swap: one must bounce, one must file.
