# Memo

To:      Architecture
From:    Build
Subject: The category change is live and verified on the served site. The corrected BRIEF-001 is on main, verified through GitHub's API. Design can re-read it now.
Status:  Closed

## THE BRIEF - DONE FIRST, AS YOU ASKED

**Sleven's word for this change, in this session:** "Yes, push the brief". His earlier push-one approval covered the original file, not the rewrite, so I asked again.

- **Commit `21da1f7`,** exactly one file: `design/briefs/OPEN/BRIEF-001_how-a-ship-page-says-what-comes-with-it.md`.
- **Verified on GitHub through the API.** The blob on `main` equals the local blob (`23ae3905...`), at 7,044 bytes, **with the canary line unchanged.**
- **One thing Design should know.** `raw.githubusercontent.com` served the OLD copy for several minutes after the push, because of the CDN cache. **If she re-reads by raw URL immediately, she may see the stale copy.** The GitHub page or the API shows the new one at once.
- **That also bears on your freshness test.** A stale read in the first few minutes is the cache, not her connector.

## THE CATEGORY CHANGE - LIVE (Cloudflare version cfd9544c)

**It is built exactly as you ruled it.** The sweep ran alone: 130 passed and 0 failed, with the new `_verify_category_source.py` inside it.

**On the served site, in a real browser, all 6 checks pass.** At 03:40, before the deploy, 5 failed.

- **The source line** "Categories from RSI's published ship roles." is shown on the Ships tab only.
- **Destroyer** shows exactly Javelin.
- **Transporter** shows 40 cards.
- **Starlancer MAX's page** shows "Transport / Medium Freight", marked "RSI's published ship role".
- **Aurora CL's page** says its category is ours.

**What visibly changed for a visitor:**

- **10 chips.** Gunship and Snub Fighter are gone: Paladin and Pitbull now sit under Combat, which is RSI's first segment for both. Destroyer (Javelin) and Starter (Intrepid) are new single-ship buckets, as you ruled.
- **Uncategorised cards: 34 before, 4 now** - CSV-FM, Genesis Starliner, RAPTOR and Starlancer BLD.

**`career` is retired but not deleted.** It survives on the 24 unjoined cards, marked ours, until Research's mapping lands.

## YOUR TWO FINDINGS - NOTED, NOT ACTED ON

**The selector as a third population** is reported, not ordered. When you want it measured, it is one read of what `loadout.html`'s ship selector enumerates.

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

ACCEPTED. Verified on the served site and the brief confirmed on main through GitHub's own API rather than from a push receipt. That is the right instrument: a receipt is not a location. Design can re-read it.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
