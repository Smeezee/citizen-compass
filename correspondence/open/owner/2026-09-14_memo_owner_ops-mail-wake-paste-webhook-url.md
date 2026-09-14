# Memo

To:      Owner
From:    Engineering
Date:    2026-09-14
Status:  Open
Subject: Ops mail-wake webhook URL — settings file (optional; backup cron live)
Owner-action: no

## Already checked
Wake tool built (ops-mail-wake), webhook routine created (ops-architecture-mail-webhook-wake), backup cron coarsened. Webhook URL is host-controlled in the routine panel (agent filesystem does not store it). Marker path correspondence/_ops_state/wake.json works without POST. Owner GO: Ops may finish wiring when the URL is available in-panel; not a blocking Owner ask.

If you open the routine panel, the URL can still be pasted into ops-mail-wake/ops-mail-wake-settings.json for true push wakes.

*Engineering, 2026-09-14.*