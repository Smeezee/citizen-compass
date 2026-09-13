# Build update - the BOOT.md uncommitted-work line is built and proven; it is NOT live (the watcher swap is Sleven's word)

**Code (Build), 2026-09-13. Clock read at 09:29:42.** Architecture's go (`..._boot-line-go-the-844-are-not-a-chore-and-a-bounced-answer-is-invisible.md`, item 1), built exactly as scoped.

**The shape: one doc-set rule, in one language.**
- **`checks/uncommitted_receipt.py`** (new, Code's) imports `commit_guard.in_doc_set`. It runs `git status` with a 30 s timeout and writes `logs/uncommitted.json` through a temp file.
  - It records `did-not-look` with a reason, never a zero.
- **The beat runs it** (`ticker.go`) after the fetch and BEFORE the page.
  - A failed run is logged and does not stop the page.
- **`watcher-go/boot_uncommitted.go`** (new) only READS the receipt, into a new section, `## WHAT IS UNCOMMITTED`, which names its source.
  - It prints the count and the oldest age.
  - **A real zero prints as zero, in words.** Missing, unreadable, did-not-look or no-count print `NOT READ - <why>`. An old receipt says STALE.

**Proof:**
- **The Python self-test: 8 of 8,** in real throwaway git repositories:
  - a clean tree reads zero
  - untracked code and doc files land on their own sides
  - a modified code file moves the number, and committing it brings it back down
  - CLAUDE.md is outside the set
  - a non-repository is did-not-look
- **Go:** `go vet` is clean and **the whole watcher suite passes.** The new tests cover zero, many, missing, unreadable, did-not-look, no-count, stale, receipt-before-page and failed-receipt-keeps-page.
  - **The new source is in the canonical `boot_test.go` lists:** every source moves the page, and a missing one shows MISSING.
- **Rule 12: 7 of 7 Go mutations caught,** each in place, restored, and hash-checked.
  - One first ran as a BUILD FAILURE, and the runner correctly did not count it. Rewritten, it was then caught by the canonical MISSING test.
- **The real repository, both directions:**
  - **1,019 → 1,020** with an untracked code-side file, and back to **1,019** once it was moved to `_to_delete/`.
  - **My first probe was a `.tmp`,** which `.gitignore:178` ignores, so the count correctly did not move. I checked with `git check-ignore` before calling it a defect.
- **The first real receipt:** 1,019 outside the documentation set (oldest 2026-08-30 11:10), 856 doc-set.

**NOT LIVE:** the running watcher is unchanged, and the swap needs Sleven's word after this proof. **I will ask for ONE swap after the router notice for refused answers is built too,** so he is asked once, not twice.

**Next:** that router notice (the same letter, item 3). Then the cadence-commit proposal (item 2), then `## UNOWNED`.
