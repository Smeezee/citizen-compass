# Memo

To:      Design
From:    Grok (Design / CIC)
Date:    2026-09-13
Status:  Open
Subject: Discord share card copy — shape A (static). Owner said build it.

**Ruling:** `claude/RULING_the-share-card-is-one-static-card-2026-09-13.md` (shape A).  
**Owner:** “I want it built” (2026-09-13).

## CARD COPY (LOCKED FOR BUILD)

One set of tags on the loadout page. Same for every build. No ship name.

| Tag | Value |
| --- | ----- |
| `og:title` | `Citizen Compass — ship loadout` |
| `og:description` | `Fit a ship, see what changes, know where to buy — before you fly. Shared builds open ready to tweak.` |
| `twitter:title` | same as og:title |
| `twitter:description` | same as og:description |
| `og:type` | `website` |
| `og:site_name` | `Citizen Compass` |
| `twitter:card` | `summary_large_image` |

**Patch line:** append to description when the dataset exposes a single build-time patch (e.g. ` · Patch 4.x` from `LOADOUT_META.last_verified_patch` or the generator’s declared patch — whichever already ships). If no patch field exists yet, ship without it; do not invent a number.

**Image:** one static `og:image` / `twitter:image` — site brand card (not per-ship). Prefer an existing Compass asset under testing/static if one is share-sized (~1200×630); otherwise generate one simple static PNG once and commit it. Absolute HTTPS URL on the deployed host.

**Also:** `og:url` = canonical loadout page URL (no hash).

## WHY THIS COPY

Stranger in Discord only sees a friend’s message + our card. Friend already named the ship. Card must say **what we are** and **that the link is a working bench**, not an article.

*Grok (Design / CIC), 2026-09-13.*