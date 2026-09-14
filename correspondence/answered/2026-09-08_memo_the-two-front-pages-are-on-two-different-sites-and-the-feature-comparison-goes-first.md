# Memo

To:      Engineering
From:    Audit
Date:    2026-09-08
Subject: Sleven wants the new front page to replace the old one — the feature comparison goes first, and the two pages are not on the same site
Status:  Answered

Sleven's words today: he wants the new front page put in place of the current
one, both still viewable, and — the condition that matters — **"I just wanna
make sure that all the features from the first one do end up on the page before
we get rid of it."**

He has said plainly he wants to go with the new page. He has not authorised the
swap yet, because of something he did not know when he said it.

## The thing that changes the question

The two pages are not on the same site.

    public site      citizencompass.netlify.app
                     front page is static/preview.html, mirrored to
                     releases/latest.html. LIVE.md records the public site at
                     v0.3.9, 254 ships, page text "Compiled/updated:
                     2026-07-30".

    new front page   testing/_src/next.src.html -> next.html, published beside
                     index.html on the PASSWORD-GATED testing site per
                     ORDER_put-the-new-front-page-up-beside-the-old-one-2026-09-06.
                     253 cards, one height, grouped by manufacturer.

So "replace the front page and keep both viewable" means two very different jobs
depending on which site he means, and one of them is a publication event on a
site strangers can already load. **I have asked him which. Do not act on the
swap until he answers, and do not assume the public one.**

## What is NOT ambiguous, and should start now

The feature comparison. It is required before either version of the swap, it
cannot be wasted work, and it is the condition he actually stated.

**Proposed queue item — WHAT THE OLD FRONT PAGE DOES THAT THE NEW ONE DOES NOT**

A feature-by-feature inventory of the CURRENT public front page
(static/preview.html) against the new one (next.src.html / next.html), listing
for every capability on the old page whether it is present, absent, or changed
on the new page. Capabilities, not appearance — search and its behaviour,
filters, sort, links out, the price and buy-location fields, provenance and
currentness signals, the trademark strip and takedown contact, glossary, any
keyboard behaviour, any URL that a person may have bookmarked.

Three things this must not do:

- do not fix anything it finds. This is an inventory. A gap found here is a
  queue item of its own, with its own DONE-WHEN.
- do not judge whether a missing feature should be carried over. Several may be
  deliberately dropped. Say present / absent / changed and stop; the keep-or-
  drop call is Sleven's.
- do not compare rendered screenshots and call that a feature list. A feature
  that exists but is not visible above the fold still exists.

DONE-WHEN: a single list Sleven can read straight through, every capability of
the old front page marked present, absent or changed on the new one, with
nothing on it that is a recommendation.

One thing already known and already on your board: the old page links to the new
one nowhere. That is one of the four defects your adoption assessment found, and
it belongs to this same job — whatever the swap turns out to be, a person needs
a way between the two pages while both exist.

## What a good answer looks like

Confirmation that the inventory is queued, and who runs it. It reads two files;
it does not need the database or a browser.

— Audit (C2)

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** Both points are in `NEXT.md`: the feature inventory gates the swap as Q53, and the inventory is read off the **served** pages of each site rather than off either source file, because the two pages do not share a generator and a textual comparison would answer nothing.
