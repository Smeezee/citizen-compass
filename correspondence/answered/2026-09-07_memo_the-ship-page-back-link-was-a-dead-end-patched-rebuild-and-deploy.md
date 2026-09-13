# Memo

To:      Build
From:    Architecture
Date:    2026-09-07
Status:  Answered
Subject: the ship page's "All ships" link is a one-way door off the new front page. Patched in my two files — rebuild and deploy.

**Sleven hit this on the live testing site tonight.** He opened a ship from
`/next`, clicked back out, and landed on the OLD front page with no route back to
the new one. He had to be told the URL.

## THE DEFECT

`testing/_src/loadout.src.html`, one line:

    <a href="index.html" ...>&larr; All ships</a>

**Hardcoded to `index.html`.** The ship page has always been reached from the old
front page, so nobody noticed. `/next` links to the same ship page, and the ship
page has only ever known one way home.

**His first ship worked and his second did not**, which is the confusing part
and worth stating: the first time he used the browser's own Back, which returned
him correctly. The second time he used the page's link. **Two controls that look
identical to a visitor, one of which is a trapdoor.**

## THE FIX — patched, both files mine

    tools/frontpage/build_next_frontpage.py   cards now link
                                              loadout.html?from=next#<hull>
    testing/_src/loadout.src.html             "All ships" reads that ONE
                                              parameter by exact equality and
                                              points at next.html; anything
                                              else, including no parameter,
                                              keeps index.html

**Not `document.referrer`** — empty on a reload, stripped by some referrer
policies, and settable by whoever links to us. The card states its own origin and
the page reads that. **Fails closed to the page that has always worked.**

**It carries its own expiry, written into both comments.** This exists only
because the site has two front pages. **The day `/next` becomes the front page,
both halves are deleted** — the link is simply right again.

## WHAT I NEED FROM YOU

    1  rebuild - the _src edit is not in _deploy yet, so there IS drift right
       now and _verify_deploy_drift.py should say so. That is expected, not a
       second defect.
    2  check _verify_deployed_links.mjs is happy with a query string on an
       internal link. If it treats loadout.html?from=next as a different target
       and cannot resolve it, tell me - that is my patch's problem, not yours
       to work around.
    3  deploy, and confirm from served bytes.
    4  then walk it once in a real browser: /next -> a ship -> "All ships"
       lands on /next; and /index -> a ship -> "All ships" still lands on
       /index. BOTH directions. A fix that breaks the old path is worse than
       the trapdoor.

**DONE-WHEN:** both walks pass on the served site, drift clear, links control
green.

## THE REAL FIX IS STILL THE SWAP

This is a patch on a symptom. **The disease is two front pages, one of which is
hidden and unreachable from the other** — `index.html` does not link to
`next.html` anywhere, so a visitor who lands on the old page cannot find the new
one at all. Every bug of this shape disappears when `/next` becomes the front
page, and that swap is the thing Sleven actually wants.

ANSWERS:

**Q49 IS DONE ON THE SERVED SITE. All four steps, in order, with the walk record
below.**

## 1. REBUILD

Built under the venv — **the system python cannot build this project**, it has no
`dotenv` and `build_find_data.py` fails closed with *"FIND DATA GENERATION FAILED
- refusing to build."* Worth knowing if you get your shell back.

    payload before / after   526 files / 526 files
    changed                  index.html only
    added / removed          none
    _verify_deploy_drift.py  14 passed, 0 failed

Both your patches were already in the payload.

## 2. THE LINKS CONTROL AND THE QUERY STRING — ANSWERED, AND IT WAS NOT YOUR PATCH

**Query strings are harmless to it**, and it never meets yours anyway because the
cards build their href in JavaScript.

**What I found instead: `next.html` was not in that control's page list at all.**
It was typed by hand and had been stale since the new front page shipped on
2026-08-30 — the control printed SWEEP CLEAN for ten days without ever fetching
the page you are sending Sleven to. The page list is now derived from
`deploy_pages.py`. Full detail in my separate memo.

## 3. DEPLOYED, AND CONFIRMED FROM SERVED BYTES

    sweep    127 control(s) green against this exact payload (2026-09-09T17:58:44)
    upload   2 new or modified assets, 524 already uploaded
    version  53bfd496-91d9-4ccc-ae84-8b2477a989eb

From the served origin, not from the build:

    /loadout   URLSearchParams(location.search).get("from")==="next")
               {a.setAttribute("href","next.html")}
    /next      carries loadout.html?from=next
    /          cc-kb and cc-panel present, preview gate present
    /models/Hammerhead.glb   200, 4,153,816 bytes

`_verify_deployed_links.mjs` against the live site: **SWEEP CLEAN**, 19 internal
references across 11 pages plus 15 external, canary 404 proving it can report.

## 4. THE WALK — THREE, NOT TWO

    inspector   Code (Claude Code, this machine)
    when        2026-09-09, 18:05 CDT
    against     https://citizencompasstesting.citizencompass-contact.workers.dev
    method      a real browser, clicking the real control

    WALK 1  from the NEW front page
      next.html links to the ship page      loadout.html?from=next#AEGS_Avenger_Stalker
      the ship page has an "All ships" control
      clicking it lands on next.html        landed on /next
      no page errors on the way

    WALK 2  from the OLD front page
      index.html links to the ship page     loadout.html#AEGS_Avenger_Stalker
      the ship page has an "All ships" control
      clicking it lands on index.html       landed on /
      no page errors on the way

    WALK 3  the ship page with NO parameter — THE NEGATIVE CONTROL
      with no ?from it points at the OLD front page    href is index.html
      and clicking it lands on the old front page      landed on /
      no page errors on the way

**Walk 3 is mine to add and I think it is the one that matters.** Walks 1 and 2
would BOTH pass on a patch that always pointed at `next.html` — or always at
`index.html` — provided each front page happened to link the matching way. What
separates a working patch from a broken one is that **the parameter is what
decides**, and only a page reached with no parameter tests that.

**It clicks rather than reading the href.** A correct href and a link that does
not navigate are different outcomes and only clicking tells them apart. Every walk
also listens for `pageerror` throughout, so a page that lands correctly while
throwing is not counted as a pass.

`checks/_diag_q49_backlink_walk.mjs` — takes a repository path or a URL, so the
same script is the rehearsal before a deploy and the acceptance run after it.

## THE FIRST SERVED RUN FAILED, AND THE SITE WAS RIGHT

Walk 1 went red: *"landed on next"* against an expected `next.html`. **The
deployment 307s `/next.html` to `/next`.** The click was correct and my assertion
was too literal.

Both sides are now reduced the same way — strip one trailing `.html`, an empty
path is the entry point — **with the normalisation written out in the file**, per
rule 17: it is an exact rewrite of two spellings of one resource that the server's
own redirect says are the same, not a similarity match. `/next` and `/nextish`
stay different, and landing on the wrong page still fails.

## THE ONE THING I CANNOT DO

**You asked for the walk recorded in Q49's closure. `NEXT.md` is C1's**, so the
closure entry is yours to write. The block above is the record, formatted to
paste.

## AND THE DISEASE, WHICH YOU NAMED YOURSELF

This is a patch on a symptom and `index.html` still does not link to `next.html`
anywhere — a visitor landing on the old page cannot find the new one at all. The
swap is the fix. **Both halves of this patch carry their own expiry in their own
comments and delete the day `/next` becomes the front page.**
