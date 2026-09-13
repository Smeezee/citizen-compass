# Memo

To:      Architecture
From:    Owner (Sleven)
Date:    2026-09-13
Status:  Answered
Subject: Reply — Discord binding: packed link is enough; add a simple preview card; short-code stays on the shelf

**Your measure on Polaris (~250 chars vs Discord’s 2000) is accepted.** The Discord binding is met by a compact packed link. No short-code server for now.

## SETTLED

1. **Share format:** packed loadout link (what you measured). Pre-ship test remains: fit a Polaris, paste into a **real Discord message**, open from there.
2. **Short-code / server fallback:** **not required** unless a real Discord paste ever fails. Keep it on the shelf.
3. **Look:** add a **simple Discord preview card** (Open Graph / same tags for every build — ship name + “Citizen Compass loadout” + patch if present). Not per-build custom art. Design owns the card copy/layout; cheap page tags, no accounts.

Grok recommended this; I agree. Still nothing ordered to Build until the broader loadout talk is stamped.

*Owner (Sleven). Filed with Grok.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-13. 1 AND 2 TAKEN AS SETTLED. 3 HAS A CONTRADICTION IN IT AND IT IS MINE TO HAVE CAUGHT EARLIER.

**1 and 2 are settled and I am not reopening them.** Packed link, Discord paste test before ship,
short-code on the shelf unless a real paste fails.

## 3 - THE CARD CANNOT SAY THE SHIP NAME AND BE THE SAME TAGS FOR EVERY BUILD. THOSE ARE TWO
## DIFFERENT CARDS.

**Why, in one sentence: the payload lives after the `#`, and a `#` is never sent to any server, so
Discord's crawler cannot see which ship the link is for.** That is not a limitation to work around
- **it is the thing that makes the link serverless in the first place.**

**The crawler fetches the page, reads whatever tags are baked into that file, and draws the card.
It never runs our code and never sees the build.**

**So there are two shapes and they cost differently:**

    SHAPE A - TRULY STATIC, ONE CARD FOREVER
      "Citizen Compass - ship loadout" plus the dataset's patch. No ship name, because
      the page cannot know it.
      COST: a handful of tags in one file. Hours. Nothing else changes.

    SHAPE B - THE CARD NAMES THE SHIP
      The ship has to be somewhere the crawler CAN see - the path - so the share URL
      becomes something like /l/polaris#b=<payload>, and the build generates one small
      stub page per ship, each with its own tags, each handing off to the loadout page
      with the fragment intact.
      COST: 318 generated stubs, a new URL shape, and a build-pipeline step.
      STILL NO SERVER AND STILL NO ACCOUNTS.

**The patch can be in either.** The dataset carries one - `last_verified_patch: "4.10"` in
`LOADOUT_META` - so it is a build-time value, not a per-build one.

**What can never be in the card, in either shape, is the loadout itself.** Per-build art or
per-build text needs something running per request, and that is a service to keep alive - the exact
thing the packed link exists to avoid. **You already ruled that out and nothing here reopens it.**

**MY ERROR, NAMED.** I told you a card "is a tag on the page, not a short code" and that one static
card costs nothing. **True, and I skipped the part where a static card cannot name the ship.** You
and Grok then specified ship name AND same-tags-for-every-build, which is not a mistake either of
you made - it is the gap in what I told you.

## THE ONE LINE BACK

**Shape A or shape B.** A is hours and says nothing about the ship; B is a build step and 318 stubs
and says "RSI Polaris - Citizen Compass loadout".

**Design has the constraint so the card copy is written against what is actually possible rather
than against my summary of it.**

*C1 (Claude-09), 2026-09-13.*
