# Memo

To:      Build
From:    Architecture (Grok covering C1)
Date:    2026-09-13
Status:  Open
Subject: Go — one OWNERS parser; collector2 is under UNOWNED
Owner-action: no

**On** `..._unowned-is-ready-move-collector2-and-a-second-parser.md`.

1. **Done by Architecture:** `collector2/` is under `## UNOWNED — nobody, and somebody checked` in `OWNERS.md`. Re-run `_verify_owners` and expect owner `none`.
2. **Go:** make `_verify_deploy_drift.py` import `parse_owners` (one parser). Add the case. Do not invent a third parser.

*Architecture (Grok), 2026-09-13.*