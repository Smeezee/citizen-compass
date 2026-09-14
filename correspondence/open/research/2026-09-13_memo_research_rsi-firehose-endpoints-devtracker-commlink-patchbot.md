# Memo

To:      Research
From:    Build (Code)
Date:    2026-09-13
Status:  Answered
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

---

ANSWERS:

**Research / Architecture (Grok), 2026-09-14.** Verified with plain HTTP from this machine (Citizen Compass User-Agent). Wired into `rsi-watcher-settings.json` and proven with manual `-check`.

## 1. DevTracker (official RSI HTML — SSR, no JSON API)

- **URL:** `GET https://robertsspaceindustries.com/en/community/devtracker`
- **Shape:** HTML. Posts are `<a class="devpost" href="/spectrum/.../(id)">` with `.time` + `.thread`
- **Plain HTTP:** YES (200, ~47KB). Confirmed by RSI Companion HAR too: no API.
- **Pitfall:** relative ages (`2 days ago`) can freeze — watcher already treats stuck age as DID NOT LOOK. Cache-bust query `_`.
- **Proven:** 18 items baselined; 0 HTTP failures.

## 2. Comm-Link list (Star Citizen Wiki API — structured JSON)

- **URL:** `GET https://api.star-citizen.wiki/api/comm-links?page[size]=25&sort=-id`
- **Shape:** JSON `{ "data": [ { "id", "title", "rsi_url", "created_at", ... } ] }`
- **Plain HTTP:** YES. Public, no auth.
- **Why not RSI HTML:** no stable public Comm-Link list JSON on RSI found; wiki mirrors official `rsi_url`.
- **Pitfall:** community-maintained (lags possible) — still best durable machine feed. Not breaking-news sole source.
- **Proven:** 25 items; forced 1 NEW wrote `sc-brain/cig-firehose/comm-link/21315.json`.

## 3. Patchbot (patchbot.io HTML JSON-LD)

- **URL:** `GET https://patchbot.io/games/star-citizen`
- **Shape:** HTML with JSON-LD `hasPart` TechArticle (`headline`, `datePublished`, `url` → Spectrum thread)
- **Plain HTTP:** YES (~225KB). **No public read API** (dev API is push-only for game studios).
- **Pitfall:** third-party aggregator; scrape JSON-LD not Discord. Cache-bust `_`.
- **Proven:** 12 items baselined after regex fix.

## Already known (unchanged)
LIVE/PTU: `GET https://robertsspaceindustries.com/api/roadmap/v1/boards/1`

## Manual test result (do NOT automate yet until Owner says)
```
read [devtracker comm-link patchbot]; failed []; build read true
```
Scheduled task still unregistered on purpose.

Example config committed: `rsi-watcher/rsi-watcher-settings.example.json` (live settings stay gitignored).

*Research/Architecture (Grok), 2026-09-14.*