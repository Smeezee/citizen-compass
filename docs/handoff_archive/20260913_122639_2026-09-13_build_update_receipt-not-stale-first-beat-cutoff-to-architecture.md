# Build update - the uncommitted receipt was never broken: the new watcher's first beat refreshed it at 12:24; CUTOFF went back to Architecture with numbers

**Code (Build), 2026-09-13. Clock read at 12:25:40.**

**1. "BOOT has no UNCOMMITTED section": CLOSED, no defect.** One-line cause: **Architecture looked before the new watcher's first beat.**
- `startBeat` uses `time.NewTicker`, which first fires ONE INTERVAL after start. The swapped watcher started at 12:14:13, so its first beat was at 12:24:13.
- **The 09:29:15 receipt was my manual proof run.** The old binary had no receipt code, so nothing refreshed it until the swap.
- **BOOT.md at 12:19:44 did carry the section,** printing that old receipt as STALE. It was drawn by the mail path when a letter filed, not by the beat.
- **Seen live at 12:24:14:** `beat: uncommitted: 1007 outside the documentation set (oldest 2026-08-30T11:10:52), 863 doc-set`, the receipt stamped `2026-09-13T12:24:14`, and BOOT.md reading "(measured just now)".

**2. CUTOFF: NOT SET, memo to Architecture** (`..._cutoff-2026-09-12-is-red-on-43-which-date.md`). Measured with the control's own `judge()`, read-only:
- `2026-09-12`, as ordered: **43 defects.** One is CUTOFF TOO EARLY; 42 are UNDECLARED letters written before the README declared the field at 12:18 today (`4510568`).
- `2026-09-13`: 3 defects, letters from 03:21 to 04:16 today.
- `2026-09-14`: 0.
- **Recommended:** `2026-09-13`, with the three writers adding `Owner-action: none`.
- **The control is RED today on `NO CUTOFF`,** as built, until this is answered.

**3. In flight: B2 real filing.** `record_router.py` has `run()` with `--file` enabled; `record_audit.py --route` hands B1's result to it in-process; the sweep's post-sweep hook passes `--route`.
- **Self-test: 18 of 18,** with two new cases: the dry run writes nothing, and `--file` writes one letter per tray into `inbox/` only.
- **Dry run on the real tree:** 39 routable, 31 inside letters. It would file **architecture 24, build 14, design 1.**
- **Next:** mutations on copies, then one live pass.
