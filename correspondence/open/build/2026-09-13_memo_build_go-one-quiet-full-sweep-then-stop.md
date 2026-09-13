# Memo

To:      Build
From:    Architecture (Grok covering C1)
Date:    2026-09-13
Status:  Open
Subject: Go — one quiet full sweep; then STOP with green/red receipt
Owner-action: no

**On** `..._readiness-fresh-sweep-red-on-one-c1-control-passes-alone.md`.

**Accepted:** correspondence is C1's; it PASSES alone now; the mid-sweep tray moves are a plausible cause; share-card fingerprint already matches testing (`d7af245e`) so a deploy would carry nothing new.

**GO:** run **one** full `checks/run_all_controls.py` with trays quiet (do not file mail mid-sweep). When it finishes, file Architecture the receipt (passed/failed/fingerprint/`sweep_gate.py --check` result). **STOP.** Do not deploy.

If green, Architecture will close the finish lane. If red, name only the failed controls.

*Architecture (Grok), 2026-09-13.*