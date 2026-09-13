# Build update - work arrived: wait for a fresh green sweep, then a deploy-readiness receipt to Architecture; NO deploy

**Code (Build), 2026-09-13. Clock read at 15:39:41.** Sleven's message: "Go". Tray listed: `2026-09-13_memo_build_next-wait-green-sweep-then-deploy-readiness.md` (15:36, Architecture).
- **The order:**
  - When `checks/.last_sweep.json` shows a FRESH full sweep with `failed: []`, file a receipt: passed, failed, fingerprint, and anything else blocking the share card or a testing deploy.
  - If it is red: fix only what Build owns, or name the blockers.
  - **Do not deploy.** Then STOP.

**State, read, not assumed:**
- Polish landed: `e799077` (git-busy) and `0fa85e4` (the 13 orphans). main is 0/0. **Build has no uncommitted code.**
- **A full sweep is RUNNING,** started 15:21:51 (`run_all_controls.py`, venv). The receipt on disk is still 09:20:54: 132 passed, 0 failed, fingerprint `46ed3680...`.
- `testing/_src/.last_build.json`: ok at 15:35:57, written during this sweep.
- `.last_deploy.json`: testing `d7af245e`, 08:01:58, `ignore_sweep: true`.

**Waiting for the sweep to finish,** by a background wait on the receipt, not by polling.
