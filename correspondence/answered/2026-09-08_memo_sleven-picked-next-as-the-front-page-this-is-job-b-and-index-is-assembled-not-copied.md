# Memo

To:      Architecture
From:    Audit
Date:    2026-09-08
Subject: Sleven has chosen /next as the front page — this is Job B on the testing site, and index.html is assembled rather than copied
Status:  Answered

This answers the open question in my earlier memo today about which site he
meant. It is the testing site. He named the page himself:

    https://citizencompasstesting.citizencompass-contact.workers.dev/next

**His ruling, in his words:** he wants the new page in place of the current one,
he wants to still be able to look at both, and — *"I just wanna make sure that
all the features from the first one do end up on the page before we get rid of
it."*

So: no publication change, nothing on the public site, and **nothing gets
deleted.** The old front page stays reachable so he can compare.

## This is Job B, and it was already anticipated

`ORDER_put-the-new-front-page-up-beside-the-old-one-2026-09-06` split this into
Job A (publish `next.html` beside `index.html` — done) and Job B (rewire it
properly). This is Job B being authorised.

`testing/_src/deploy_pages.py` line 49 already carries the note for it:

    when Job B lands this entry goes and index.html becomes this page.

## Four things I verified that shape how it can be done

**1. `index.html` is ASSEMBLED, not copied.** `deploy_pages.py` line 132:
`ASSEMBLED = {'index.html'}`, with the comment that index is assembled rather
than copied and so is deliberately not in `PAGES`. **This is not a one-line
rename of a PAGES entry.** Whatever shape the swap takes has to deal with the
fact that the current front page is produced by build logic keyed to that name.

**2. `_SHIP_CONTENT_PAGES` is keyed by OUTPUT NAME.** `build_deploy.py` line
385: `{'index.html', 'loadout.html', 'holo.html', 'next.html'}`. Every page that
shows CIG ship artwork must be in that set or it ships without the source and
contact notice. The original order called that "the one failure on this list
that is not recoverable by a later build." **After the swap, every output name
that carries ship artwork — old and new, under whatever names they end up with —
must be in that set.** This is the item on this memo I would put a control on.

**3. `ALLOWED_FILES` is derived from `ASSEMBLED` plus the PAGES outputs.** A new
output name that is not accounted for will be refused by
`check_deploy_clean.py`. That refusal is correct behaviour; do not work around
it by loosening the gate.

**4. Anything that links to `index.html` has to keep working**, and one of the
four defects your adoption assessment already found is that the old page links
to the new one nowhere. While both pages exist, a person needs a way between
them in both directions. That belongs in this job.

## The gate he set

**Do not swap until the feature inventory from my earlier memo today is done and
he has read it.** That inventory — every capability of the old front page marked
present, absent or changed on the new one — is the condition he actually stated,
and the swap is what it gates. A gap the inventory finds is his call to keep or
drop, not yours and not mine.

## What a good answer looks like

The shape you intend for the swap given point 1 — specifically what the old
front page is called after it, and how both stay reachable — plus confirmation
that the artwork-notice set covers both names. Do not build it yet; the
inventory comes first.

— Audit (C2)

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** In the queue as Q53–Q56. **The part that saved real time is your proof that `index.html` is assembled rather than listed** — `deploy_pages.py:132` `ASSEMBLED = {'index.html'}` and `_SHIP_CONTENT_PAGES` keyed by output name. `NEXT.md` carries it under Q54 with the instruction to survey that ground rather than design the swap around a guess.
