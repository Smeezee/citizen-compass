# Memo

To:      Build (Code)
From:    Owner (Sleven)
Date:    2026-09-13
Status:  Answered
Subject: BUILD NOW — static Discord/Open Graph share card on the loadout page (shape A)

**Owner go.** Architecture ruled shape A. Design copy is in:
`correspondence/open/design/2026-09-13_memo_design_discord-share-card-copy-shape-a-owner-said-build.md`
(or inbox twin if still routing)

## DO THIS

1. Add Open Graph + Twitter card meta tags to the **loadout** page (`testing/_src/loadout.src.html` or the real source of truth Build uses), using Design’s locked strings.
2. One static `og:image` (absolute URL on deploy). No per-ship stubs. No short-code server.
3. Patch suffix in description **only** if a real dataset patch field exists at build time — do not invent.
4. Prove: share a loadout link, paste into Discord (or Discord’s embed debugger / opengraph.xyz), confirm the **card** shows title + description (+ image). Also keep the Polaris packed-link paste test.
5. Deploy path as usual for testing/public per LIVE — do not invent a new pipeline.

**Out of scope:** shape B, accounts, short-code service, renaming ships in the card.

**Credit:** small change — implement, self-check, one short inbox receipt when green or blocked.

*Owner (Sleven). Design copy by Grok. Filed with Grok.*

ANSWERS:

**Green. Shape A is live on the TESTING site.** Version `d7af245e`, deployed at 08:00 on your "go", past the mail-only sweep red.

- **Checked on the served site, fetched the way Discord's crawler fetches it:**
  - `/loadout` carries Design's ten tags exactly: title `Citizen Compass — ship loadout`, the locked description plus ` · Patch 4.10`, `summary_large_image`, and absolute URLs.
  - `/og-loadout.png` serves `200 image/png`, 1200x630, byte-identical to the build.
  - No ship name. No short-code server. No per-ship stubs.
- **The patch is not typed.** It is the snapshot manifest's own (4.10), filled in at build time, so it cannot go stale.
- **The image** was drawn once, in the page's colours and Design's words. It carries no logo of anyone else's and no disclaimer text; that wording stays yours (rule 8).
- **A control now holds it:** `checks/_verify_share_card.py` checks the built page against Design's strings on every sweep.
- **NOT PERFORMED by Build: the Discord paste itself.** There is no Discord client on this machine. Everything Discord's crawler reads was checked on the served bytes. The Polaris packed-link paste test is untouched.
- **The public site is unchanged.** The loadout page is on testing only, per LIVE.md.

*Build (Code), 2026-09-13.*
