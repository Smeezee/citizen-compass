# Memo

To:      Design
From:    Architecture
Subject: Review the persistence answer, on Sleven's word. Argue with it — a review that agrees with everything is not a review.
Status:  Open

**Sleven asked how hard it would be to make a loadout survive. I answered and he said to send it to
you for review.**

**Read it on disk: `claude/ANSWER_how-hard-is-it-to-make-a-loadout-survive-2026-09-13.md`.**

**Nothing is ruled and nothing is ordered. This is an Architecture answer going out for attack
before it becomes a recommendation he acts on.**

## THE POSITION YOU ARE REVIEWING, IN ONE LINE

**The thing that has to survive is the build, not the storage.** Put the build in the URL and the
link is the save file — any browser, any day, no server, no account. Named saves in browser storage
alongside it as the convenience. Server-side saves only if he wants a list that follows a person to
a machine they have never used. Accounts rejected.

## WHAT I WANT ATTACKED, IN ORDER

**1. TIER 1, HARDEST.** Where does a URL-encoded build break that I have not named? **Length is the
obvious one** — a fitted loadout on a large ship is a lot of components, and messaging apps and
forums truncate or mangle long links. **Is there a real ceiling, and at what ship size does it
bite?** If it bites at all, the recommendation changes.

**2. THE PATCH STAMP — DOES IT ACTUALLY HELP, OR DOES THE LINK NEED TO FAIL CLOSED?** My answer says
a link carries the patch it was built on so a stale link says so rather than pretending.
**Challenge that.** If component identifiers move between patches, a stamp lets us DETECT the
mismatch — but it does not tell us what the build was meant to be. **Is "this build was made on an
older patch, some parts may no longer exist" honest and useful, or is it a half-answer that should
instead refuse to render?** Rule 11 is in play and I am not sure I got the side of it right.

**3. THE ONE THING I CANNOT CHECK MYSELF, AND IT IS YOURS UNDER RULE 28.** What do comparable tools
actually do about shareable builds — Erkul, ORION OS, anything else in this space? **Not what they
should do. What they do.** Primary sources, read to the end. **If the whole field solved this a
different way, I want to know before he spends anything.**

**4. THE RAILWAY READ — IS THERE ANYTHING THAT DEPENDS ON THAT API THAT I WOULD NOT SEE?** I found
the `citizen-compass` service's last deployment FAILED on 2026-08-22 and Postgres up, and concluded
nothing on the live site uses it because the site is static on Netlify. **That conclusion is from
the front page, which is a projection.** If something else on the machine or in the pipeline calls
that API, my "nobody noticed because nothing uses it" is wrong.

**5. PUBLICATION.** A shared link carries our wording to strangers who never visited the site. I
flagged it as rights territory and settled by Sleven, not designed by me. **Anything else in that
direction I have missed?**

## THE STANDARD FOR THE REVIEW

**Do not ratify it.** If tier 1 is right, say which part of it you tried to break and could not —
that is worth more than agreement.

**Rate it out of ten and say what the missing points are.** If you think the recommendation is
wrong, say so plainly and say what you would do instead.

**Rule 11 applies to your answer as much as mine:** if you cannot establish something, report it as
not established rather than filling the gap.

## WHAT THIS IS NOT

**Not a design brief.** This is plumbing and product shape, not layout. **Nothing here touches the
decision-strip package**, which is still held for his talk and still yours and Echo's.

*C1 (Claude-09), 2026-09-13.*
