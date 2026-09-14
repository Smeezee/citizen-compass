# Build update - P15 stamp and link are BUILT and verified on the testing payload; the small-screen spot-check passes; next is a quiet full sweep, then the testing deploy so the link is actually up

**Code (Build), 2026-09-13. Clock read at 19:09:28.** Sleven's "inbox when you can": tray listed, nothing new to Build since 18:56, `inbox/` empty, and both updates filed.

**Built** (`testing/_src/build_deploy.py`, testing payload):
- **Build OK:** "deploy guard: safe to deploy", build receipt ok.
- **The build printed the derived stamp:** "Default bindings verified identical to Star Citizen 4.10.0-hotfix (change 12545750, built Aug 28 2026) - checked 1103 of 1103 actions at build."

**Verified from outside the build:**
- **`checks/_verify_keybinds_stamp.py` real run: PASS.**
  - A: the data is clean against the newest profile.
  - B: the built `keybinds.html` carries the stamp exactly once, with no leftover marker.
  - C: the source carries only the marker, and no typed version or change.
- **`checks/_verify_deploy_drift.py`: 21 passed, 0 failed,** with the new marker substitution declared.
- **Built `next.html`:** exactly one `href="keybinds.html"` (the footer link).

**Small-screen spot-check** (`checks/_diag_kb_small_screen.mjs`, Playwright, on the BUILT page; screenshots internal only, rule 21):

    375 px   105 keys, 0 overlapping pairs, narrowest key 42.8 px, stamp visible;
             the document is 5 px wider than the screen (380 vs 375) - a scroll, not a smash
    768 px   0 overlaps, no sideways scroll, stamp visible
    1440 px  (desktop reference) ONE overlap, F12 against Ins, 9 x 51 px

- **No minimal smash fix is needed:** keys neither overlap nor become unreadable at 375 or 768.
- **The 1440 overlap is an existing desktop layout defect in C1's page code.** It is reported, not fixed (not delegated).

**Open for the receipt, stated:**
- **The page shows one input per device.** Chat Window Focus shows `enter`, not also `np_enter`. The data carries both; showing it is a page-code change that was not delegated.
- **`kb_profile.py` needs an `OWNERS.md` line** (Code's), which is Architecture's edit.

**Next:**
1. a quiet full sweep (no mail filed while it runs)
2. if green, `scripts/deploy_testing.ps1` and a served-page check, so "the link is up" is true for a visitor
3. then the receipt, and STOP

**Uncommitted, Sleven's hand:**
- `kb_profile.py` (new)
- `checks/_verify_keybinds_stamp.py` (new)
- `checks/_diag_kb_small_screen.mjs` (new)
- `extract_default_profile.py`
- `data-layer/processed/keybinds_site.json`
- `testing/_src/kb_actions.gen.js`
- `testing/_src/kb_modes.gen.js`
- `testing/_src/keybinds.src.html`
- `testing/_src/next.src.html` (untracked before this session)
- `testing/_src/build_deploy.py` (it already carried an older uncommitted pile)
- `checks/_verify_deploy_drift.py`
