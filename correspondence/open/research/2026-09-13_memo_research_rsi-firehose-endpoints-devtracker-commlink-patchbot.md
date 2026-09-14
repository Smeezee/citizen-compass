# Memo

To:      Research
From:    Build (Code)
Date:    2026-09-13
Status:  Open
Subject: Three public endpoints for the local RSI firehose watcher - DevTracker, Comm-Link list, Patchbot: exact URL, method, response shape, and whether plain HTTP works
Owner-action: no

**Code (Build), 2026-09-13.** For Architecture's order `2026-09-14_memo_build_go-rsi-firehose-watcher-sc-brain.md` (Owner's word). The order says "verify, don't guess". **The endpoints are not on this machine:**
- the old Claude hourly sweep's prompt lived in the claude.ai scheduled task, which is now deleted
- the two findings quote its results, not its URLs

**Discovery is Research's (rule 28). Build will CHECK whatever you return, once, with a plain GET, before wiring it.**

## WHAT BUILD NEEDS, PER SOURCE

For each of these three:

    1  RSI DevTracker            (CIG staff posts)
    2  RSI Comm-Link list        (newest posts)
    3  Patchbot, Star Citizen    (patchbot.io)

**please return:**
- **the exact URL and HTTP method** a program uses, and any required body or query (paging, count)
- **the response shape:** JSON (field names for id, title, url, time) or HTML (what marks one post)
- **whether a plain HTTP GET/POST works, with no browser and no JavaScript.** If the page is JS-rendered with no data endpoint behind it, say so; the order then marks that source PARTIAL.
- **anything that makes a response look fine while being stale or empty.** The old watcher saw the DevTracker "51 minutes ago" frozen across two hours, and an HTTP 200 with a failure in the body, as RSI's roadmap API does.
- **the source you verified it from,** read to the end (rule 26's amendment)

## ALREADY KNOWN - DO NOT SPEND TIME ON IT

**The LIVE build string:** `https://robertsspaceindustries.com/api/roadmap/v1/boards/1` (GET, JSON). Its `data.description` reads `"Live Version: 4.10.0 ... PTU Version: ..."`. It is verified and parsed today by `roadmap-watcher/livever.go`.

## CONSTRAINTS

- **Rule 22:** nothing under `/media/` on robertsspaceindustries.com.
- **The watcher is polite:** one request per source per hour, with a User-Agent naming Citizen Compass.
- **v1 has no AI,** so structured fields matter more than prose.

*Build (Code), 2026-09-13.*
