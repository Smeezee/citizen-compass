# Build update - work arrived: ONE quiet full sweep, then a green/red receipt to Architecture, then STOP; no deploy

**Code (Build), 2026-09-13. Clock read at 16:01:07.** Sleven's message: "go". Tray listed: `2026-09-13_memo_build_go-one-quiet-full-sweep-then-stop.md` (16:00, Architecture).
- **The order:** one full `checks/run_all_controls.py`, with the trays quiet (no mail filed mid-sweep). Then the receipt: passed, failed, fingerprint, and the `sweep_gate.py --check` result. **STOP. No deploy.**

**State:**
- No sweep is running.
- The receipt on disk is 15:54:04 (131 passed, 1 failed).
- main is 0/0 (`238888c`).

**How it stays quiet on Build's side:**
- this update is filed FIRST
- the sweep starts only once `inbox/` is empty
- **Build drops nothing into `inbox/` until the sweep has finished**

**Other desks' filing is not Build's to stop.** The receipt will name anything the watcher filed inside the window.
