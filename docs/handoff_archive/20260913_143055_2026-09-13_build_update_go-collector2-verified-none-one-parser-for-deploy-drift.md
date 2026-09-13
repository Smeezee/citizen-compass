# Build update - "go": collector2 verified as owner `none`; taking Architecture's go on ONE OWNERS parser for deploy drift

**Code (Build), 2026-09-13. Clock read at 14:30:13.** Sleven's message: "go". Tray listed: `2026-09-13_memo_build_go-one-owners-parser-and-unowned-done.md` (14:23, Architecture).

**Checked, not taken:**
- **`a399e72`:** `OWNERS.md` has `## UNOWNED — nobody, and somebody checked` at L469, with `collector2/` under it. main is 0/0.
- **The real `_verify_owners` run: PASS.** 99 owned paths, owners `['C1', 'CODE', 'none']`. `parse_owners` gives `[('collector2/', 'none')]`, and `collector2/` exists on disk.
- **So the order's DONE-WHEN holds, all three parts,** on the real file.

**Taking:** item 2. `checks/_verify_deploy_drift.py` (Code's) imports `parse_owners` and drops its own heading-first-word parser, with a planted case. No third parser.

**Still uncommitted:** `checks/_verify_owners.py`. **HELD by Sleven:** the swap and the 858 backlog.
