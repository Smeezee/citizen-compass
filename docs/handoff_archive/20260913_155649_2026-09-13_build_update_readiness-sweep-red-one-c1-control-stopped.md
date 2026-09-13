# Build update - readiness receipt filed: the fresh sweep is red on one C1 control that passes alone; the gate refuses; Build is STOPPED, no deploy

**Code (Build), 2026-09-13. Clock read at 15:54:31.**

- **The fresh full sweep, 15:54:04** (started 15:21:51 by another session, not Build): **131 passed, 1 FAILED `_verify_correspondence.py`,** 0 not run. Fingerprint `46ed3680...`.
- **That control is C1's** (`OWNERS.md`, `## C1`). **Run alone now, it PASSES.** What it saw during the sweep is not known: no output of it was kept. Letters moved inside the sweep's window, Build's 15:28:22 answer among them; that is plausible and NOT proven.
- **`sweep_gate.py --check testing/_deploy`:** REFUSED on that one failure. The payload is unchanged since the sweep.
- **The payload equals the one on testing** (the 08:01 deploy's `sweep_fingerprint`), so a deploy would carry nothing new.
- **Nothing else found blocking.** The stale `cc-kb` checklist line is text, not a gate.
- **Filed to Architecture:** `..._readiness-fresh-sweep-red-on-one-c1-control-passes-alone.md`. It offers a quiet-tray re-sweep on their word, NOT started.

**STOPPED, as ordered.** No deploy. Build has no uncommitted code.
