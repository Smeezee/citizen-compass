# Update — HELP drawer committed, not pushed (2026-08-07)

Commit `ba25d9c` on `main`, 6 files, 1042 insertions:

- `testing/_src/_layer.src.html` — the drawer, the reflow, the hint line
- `testing/_src/build_deploy.py` — build-time JSON substitution + its guards
- `data-layer/processed/keybind_troubleshooting.json` (now tracked)
- `data-layer/processed/vendor_support.json` (now tracked)
- `testing/_src/test_help_drawer.js` — 38 tests with negative controls
- `testing/_src/shot_help_drawer.js` — screenshot harness

**Not pushed.** Hard rule 2 — no go-ahead given for this change. The work is
committed locally and waiting.

Deliberately left out of the commit: `testing/_src/_modelfolders.txt` and
`testing/_src/_scunpacked_names.json`, which were already untracked before this
work and are nothing to do with it.

## Open item for Sleven, not acted on

`keybinds.src.html` is a **second, standalone copy** of the same keybind tester,
built and copied to `keybinds.html` on every deploy. Nothing on the site links
to it, so it is not user-reachable today, and the work order named one page — so
it did **not** get the HELP drawer. If it is meant to stay a shipped page, it is
currently the tester without the help, and that divergence will only widen. Two
copies of one screen is the shape rule 14 exists about. Flagging it rather than
expanding scope unasked.
