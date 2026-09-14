# Owner ask — paste Ops mail-wake webhook URL (one line)

**From:** Operations  
**Need:** one paste into a local gitignored file. No chat paste of the secret key if the panel shows one — only into the file.

1. In Grok Bot → routine **Ops Architecture mail webhook wake** → copy Webhook URL.
2. Edit `ops-mail-wake/ops-mail-wake-settings.json` → set `"webhook_url"` to that URL.
3. Optional later: register logon task with `ops-mail-wake/setup_ops_mail_wake_task.ps1` (you only — hard rule 6). Ops already ran `-WhatIf`.

Prove: drop a test Architecture letter → Ops should wake without waiting for the 2h backup poll.

Related: RSI watcher still needs your `setup_rsi_watcher_task.ps1` register when you are ready (separate ask).