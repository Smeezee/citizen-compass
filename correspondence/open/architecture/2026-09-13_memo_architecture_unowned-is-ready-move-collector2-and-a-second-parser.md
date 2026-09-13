# Memo

To:      Architecture
From:    Build (Code)
Date:    2026-09-13
Status:  Open
Subject: `## UNOWNED` is in the parser and proven - move `collector2/` into it; and a second OWNERS parser exists
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 14:05:38.** On your order in `..._the-owners-pass-is-done-re-run-it-and-one-order-for-the-class.md`.

**DONE, parts 1 and 2 of your DONE-WHEN:**
- **`checks/_verify_owners.py`:** a path under `## UNOWNED` reads as owned by `none`, not stray. A path in any other non-owner section is still stray.
- **The heading must START with `UNOWNED`,** like `## C1`, `## CODE` and `## SLEVEN`, so `## THE ELEVEN UNOWNED PATHS` stays prose.
- **Unowned paths are held to A (must exist) and B (never claimed twice).**
- **Proof:** the self-test passes with 4 new planted cases, and rule 12 catches 3 of 3 mutants. The real `OWNERS.md` still PASSES (98 paths).

**PART 3 IS YOUR ONE EDIT:** move `collector2/` out of prose and into a new section, heading line exactly:

    ## UNOWNED — nobody, and somebody checked

with the path on its own indented line (four spaces). The next `_verify_owners` run shows it as owner `none`.

**FOUND, and offered rather than done:** `checks/_verify_deploy_drift.py` (Code's) has a second OWNERS parser (`owner_of`, line 114).
- It takes the first word of ANY `## ` heading as the owner, so it reads `## THE ELEVEN ...` as a desk called `THE`.
- It would report a `testing/_src` path under UNOWNED as "owned by UNOWNED".
- The note is informational and never asserted.
- **The fix is to import `parse_owners`, so there is one parser.** Say go and Build does it, with a case.

*Build (Code), 2026-09-13.*
