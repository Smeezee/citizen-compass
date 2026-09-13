# Build update - the category change is live and verified on the served site; the corrected BRIEF-001 is pushed and verified on GitHub

**Code (Build), 2026-09-12. The clock read 04:23:39 to 04:24:01 CDT across the served checks.**

## The category change - DEPLOYED AND VERIFIED

**Sweep, run alone:** 03:39:25 to 04:18:58. **130 passed, 0 failed, 3 skipped, 0 not run.** Receipt fingerprint 3bf0160c. **The new `_verify_category_source.py` ran inside it and passed.**

- **No control timed out.** The heavy measurement script I stopped at 03:47 did not affect the sweep.

**The deploy:** `deploy_testing.ps1`, no override. **Three files changed:** `next.html`, `loadout.html` and `loadout_model.gen.js`. Cloudflare version cfd9544c-3b90-42d2-8689-f156f49a9a4f.

**Served, in a real browser** (`_needs_review/served_category.mjs`). **All 6 pass.** At 03:40, before the deploy, 5 of 6 failed, which proves the check can fail.

- The source line is shown on the Ships tab and hidden on the Development tab.
- The Destroyer chip shows exactly Javelin.
- The Transporter chip shows 40 cards.
- Starlancer MAX shows "Transport / Medium Freight", marked "RSI's published ship role".
- Aurora CL shows its category marked "our own category, from game data - no RSI role joined for this ship".

**Served bytes:** `/`, `/next.html`, `/loadout.html` and `/loadout_model.gen.js` are all identical to the payload.

## The corrected BRIEF-001 - PUSHED AND VERIFIED (Sleven: "Yes, push the brief")

- **Commit `21da1f7`,** one file. Pushed `26e5c43..21da1f7`. Ahead/behind 0/0.
- **Verified through GitHub's API, not the cached raw address.** The blob on `main` is `23ae3905...`, which equals the local HEAD blob. It is 7,044 bytes, and the canary line is present.
- **The raw address still served the old copy for a few minutes.** That was the CDN cache, not a failed push.

## Not acted on

Architecture's finding that the ship-page selector lists ships that are not cards. It was reported, not ordered.
