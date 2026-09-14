# Memo

To:      Owner
From:    Operations
Date:    2026-09-14
Status:  Open
Subject: RSI watcher — one elevated click when you want hourly automation
Owner-action: yes

Manual `-check` is green after reboot (all three feeds + LIVE/PTU). Proof: `docs/OPS_rsi-watcher-proof-2026-09-14.md`.

**Only ask:** when you want it on a timer, run elevated from the repo:

`.\setup_rsi_watcher_task.ps1`

`-WhatIf` already verified by Ops (would register “Citizen Compass RSI Watcher”; nothing changed).

*Operations, 2026-09-14.*