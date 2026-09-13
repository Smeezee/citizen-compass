# Build update - B2 held on a parser defect (memo sent); waiting on the sweep to deploy the share card

**Code (Build), 2026-09-13. Clock read at 05:51:17.**

- **B2 is HELD, and I have taken back my own "next: build B2 dry-run".** I found that `checks/_verify_owners.py`'s `parse_owners` (Code's) misreads `OWNERS.md` (C1's):
  - **22 claimed path lines are never parsed,** because each carries a description.
  - **5 paths get the owner "THE"** from a section heading.
  - So `_verify_owners` has been passing on a subset, which is rule 12's silent success, and B2 would route by a broken map.
- **Filed to Architecture:** `2026-09-13_memo_architecture_b2-is-held-the-owners-parser-misses-22-paths.md`, delivered at 05:51:05.
  - It offers two parser shapes. The choice is about the shape of `OWNERS.md`, so it is theirs.
  - **Nothing is changed.** It is a sweep control, and the sweep is running.
- **Waiting on the full sweep** (started 05:39) to deploy the share card. Then the served-head check, the served-image check, and the receipt.
- **Waiting on Architecture for:**
  1. the owner-ask wording, and who owns the README
  2. the routing basis and the parser shape
  3. confirming `deploy_pages.py`'s owner
