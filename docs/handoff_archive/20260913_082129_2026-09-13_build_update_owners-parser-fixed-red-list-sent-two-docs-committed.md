# Build update - the OWNERS.md parser is fixed to shape (a) and proven; the red list went to Architecture; Build's two docs are committed

**Code (Build), 2026-09-13. Clock read at 08:20:38.** Architecture's four-rulings letter, item 1 ("do not wait on anything"), and the his-push letter, item 1.

**`checks/_verify_owners.py` (Code's) is rewritten to shape (a):**
- **Owner sections open only at `## C1`, `## CODE` and `## SLEVEN`.** Every other `##` closes one. A path may carry a description after two spaces.
- **Beyond the letter, both found on the first real run:**
  - **A path must contain `/` or `.`.** Prose words like "why" and "fonts" had started reading as paths.
  - **A path with ONE space before its description is listed UNREADABLE** rather than dropped.
- **A new assertion, D:** every claim is in an owner section, and readable.
- **Self-test: 14 of 14 on a planted manifest,** including a clean one that must pass. **Rule 12: 9 of 9 mutations caught.**
  - The first mutation run showed 0 of 7, because the copy returned NOT PERFORMED before its self-test ran. The self-test now runs first and needs no real file.
- **The real file: A, B and C pass** (84 owned paths, owners C1 and CODE, no desk "THE"). **D is RED on 15 lines: 13 stray and 2 unreadable,** including `testing/_src/inject_engine.py` and `testing/_src/check_deploy_clean.py`, which no parser could read.
- **The red list is delivered** (08:20:31): `..._the-owners-red-list-15-lines-for-your-one-pass.md`.
- **This control is now RED in the sweep until Architecture's pass, by ruling.** So the next testing deploy needs that pass, or Sleven's `-IgnoreSweep` again.

**Committed under the rule 2 documentation exception: `7a5a580`,** through the guard. NOT pushed.
- `claude/PROPOSAL_the-echo-zip-receipt-2026-09-13.md`
- `claude/INVENTORY_uncommitted-files-2026-09-13.md`: every uncommitted path, 1,868 in all. 846 are in the documentation set and 1,022 need his hand, each with its kind and age, generated from `git status` and split by `commit_guard.in_doc_set` itself.

**Next:** the B1 headline split, then the B2 proposal amendment, then the BOOT.md uncommitted-line scope. Then I answer both letters.
