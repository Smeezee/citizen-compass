# DESIGN â€” Ops wake-on-new Architecture letter
**Date:** 2026-09-14  
**Status:** MARKER-FIRST DONE. Webhook POST PARTIAL — URL is host-controlled in routine panel; agent cannot read it from disk. Backup cron live.

## Goal
Wake Operations when a NEW letter lands in `correspondence/open/architecture`, instead of relying only on a blind `*/20` poll (credit thrash).

## Shape
```
Claude / desks  --write-->  correspondence/open/architecture/*.md
                                    |
                                    v
                         ops-mail-wake.exe  (fsnotify)
                           |            |
                           v            v
                    wake.json marker   POST webhook
                           |            |
                           +-----> Operations routine
                                   (mail-bridge process)
```

## Pieces landed
1. **Local tool** `ops-mail-wake/` â€” Go + fsnotify; `-check`, `-dry-run`, `-once`; anti-runaway: debounce, `.md` only, max 6 wakes/hour, fired-path set in `correspondence/_ops_state/mail_wake_state.json`.
2. **Webhook routine** â€” `ops-architecture-mail-webhook-wake` (fires on POST).
3. **Backup cron** â€” `operations-code-architecture-mail-bridge` coarsened to `0 9,11,13,15,17 * * 1-5` (weekdays).
4. **Settings** â€” `ops-mail-wake-settings.example.json`; live `ops-mail-wake-settings.json` gitignored.
5. **Task script** â€” `setup_ops_mail_wake_task.ps1` (`-WhatIf` OK; Owner registers for real â€” hard rule 6).

## Owner steps (one-time)
1. Open routine **Ops Architecture mail webhook wake** â†’ copy **Webhook URL** (+ sender key if the panel shows one â€” paste only into local settings, never into chat).
2. Set `"webhook_url"` in `ops-mail-wake/ops-mail-wake-settings.json`.
3. Optional: elevated/logon task via `ops-mail-wake/setup_ops_mail_wake_task.ps1` (Owner only). Or leave a terminal running `ops-mail-wake.exe` while testing.

## Anti-runaway (same house rules)
- Cap per hour on local tool + max 3 letters per Ops wake
- Empty tray = silence
- No self-mail storms
- Do not touch `rsi-watcher/` mid-edit

## Done when
New Architecture `.md` â†’ webhook fires Ops within ~2s debounce â†’ letter stamped without waiting for next 2h backup poll.