# Build update - Q55.P15 GO received: the three decisions are answered and the delegation is complete; building stamp and link on the deployed keybinds page

**Code (Build), 2026-09-13. Clock read at 18:29:46.** Sleven's message: "go". Tray listed: `2026-09-13_memo_build_go-p15-three-decisions-answered.md` (18:28). Both Build memos are now `Answered` in `open/architecture/` (`12725a6`).

**DELEGATION, recorded as `OWNERS.md` requires:**
- **The order:** Architecture's answers on `..._p15-stopped-stamp-not-derivable-as-ruled-three-decisions.md`, with Sleven's "go".
- **`testing/_src/keybinds.src.html` (C1's):** one stamp marker, `__CC_KEYBINDS_STAMP__`.
- **`testing/_src/next.src.html` (C1's):** ONE link to the keybinds page.
- **`testing/_src/build_deploy.py` (Code's):** computes and fills the stamp.
- **Not claimed:** `build_kb_actions.py` and the profile readers. Helpers may sit next to them.
- **The stamp wording is Architecture's:** "Default bindings verified identical to Star Citizen 4.10.0-hotfix (change 12545750, built Aug 28 2026) - checked N of N actions at build." It is read from the newest MANIFEST plus an action-level compare re-run each build. **No typed build number.** If the compare fails, the page shows "not verified against the latest default profile".
- **Page:** the DEPLOYED `keybinds.src.html`, not the C3 mock.
- **Out of scope:** the competitive P0 list. Small screens are a spot-check at about 375 and 768 px, with a minimal fix only if keys overlap.

**Order:**
1. read the formats (profile XML against `keybinds_site.json`)
2. the compare and stamp, plus a control with self-test and mutations
3. the marker and the fill, plus the drift declaration
4. the link
5. build
6. the spot-check
7. the receipt, then STOP
