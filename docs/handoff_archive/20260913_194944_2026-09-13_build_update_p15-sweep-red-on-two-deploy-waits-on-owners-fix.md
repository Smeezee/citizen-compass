# Build update - P15 sweep (19:11 to 19:47) is RED on two controls: the OWNERS.md lines are Architecture's; the three answered letters are being closed by Build; the testing deploy waits

**Code (Build), 2026-09-13. Clock read at 19:47:22.**

- **Sweep:** 131 passed, **2 failed** (`_verify_owners.py`, `_verify_correspondence.py`), 0 not run, fingerprint `fb3f7ca0...`. The watcher filed nothing inside the window. **`_verify_keybinds_stamp` (PASS) and `_verify_deploy_drift` (21 of 21) are green in it.**
- **`sweep_gate.py --check`:** refuses on both.
- **`_verify_owners` D:** two stray claims Architecture added to `OWNERS.md` (C1's):
  - `design/keybindings/` under a DESIGN heading (18:28)
  - `sc-brain/` under an SC BRAIN heading (19:21, mid-sweep)
  - Neither heading is an owner section under shape (a). **The fix is Architecture's:** move the lines, or rule a new heading.
- **`_verify_correspondence`:** three of Build's P15 letters are Answered but left in `open/architecture/` (answered in place, never routed). **Build is closing them now** (Closed plus a `CLOSED:` record, through `inbox/`, to `answered/`). Rule 5 does not apply: 3 letters.
- **Receipt to Architecture:** `..._p15-built-sweep-red-on-two-owners-lines-and-these-letters.md`.
- **Next:**
  1. after the OWNERS fix: a quiet sweep, then the testing deploy, then the served check (unless Architecture says hold)
  2. meanwhile, **the RSI firehose watcher** (Architecture's go with Owner's word, 19:30) starts next, as a separate unit
