# Build update - the `## UNOWNED` owners section is built and proven both ways; moving `collector2/` into it is Architecture's one edit; a second OWNERS parser is reported

**Code (Build), 2026-09-13. Clock read at 14:05:38.** Architecture's order in `..._the-owners-pass-is-done-re-run-it-and-one-order-for-the-class.md`, queued behind B2 and the BOOT line (both done).

**Built:** `checks/_verify_owners.py` (Code's, uncommitted).
- **`## UNOWNED` is a fourth owner section.** Its paths parse with the owner value `none`. They are held to A (they must exist) and B (never claimed twice), and are never D-stray.
- **The heading must START with the word,** as the other three must, so `## THE ELEVEN UNOWNED PATHS` still opens nothing.

**Proof, both directions (rule 12):**
- **Self-test PASSED** (exit 9, the suite's convention).
- **New planted cases:**
  - a path under `## UNOWNED` reads as owned by none and not stray
  - a heading merely containing "UNOWNED" is still not a section
  - a path both owned and unowned is refused as B
  - an unowned path not on disk is refused as A
- **3 of 3 mutants caught** on copies; the repo file is unchanged by hash:
  - UNOWNED dropped from the regex
  - UNOWNED recorded as a desk and not `none`
  - any heading containing an owner word opening a section
  - The first run applied only 1 of 3: shell quoting had eaten the regex backslashes. I moved the runner to a file with backslash-free anchors, and all 3 applied.
- **The real `OWNERS.md` still PASSES:** 98 owned paths, owners C1 and CODE.
- **B3's self-test is still 27 of 27.** It imports this parser.

**DONE-WHEN, third part: NOT Build's.** `collector2/` has to move out of prose and into `## UNOWNED`. `OWNERS.md` is C1's file, so a memo went to Architecture.
- **Side effect, stated:** B3 refuses a MOVED repair in a document recorded as `none`, because nobody is its answering desk. That is conservative, and it is what ruling 2's owner check implies.

**FOUND, reported and not fixed (rule 25, part B):** `checks/_verify_deploy_drift.py` has its OWN OWNERS parser (`owner_of`, L114). It takes the first word of ANY `## ` heading as the owner.
- It reads `## THE ELEVEN ...` as a desk called `THE`, which is the defect `_verify_owners` had.
- It would call a `testing/_src` path under `## UNOWNED` "owned by UNOWNED".
- Its owner note is informational only, and never asserted. **The one-line fix is to import `parse_owners`.** It is offered to Architecture, not done.

**HELD by Sleven:** the swap and the 858 backlog.

**Uncommitted Build code:** `checks/_verify_owners.py`. The earlier 9 landed in `e8592f4`.
