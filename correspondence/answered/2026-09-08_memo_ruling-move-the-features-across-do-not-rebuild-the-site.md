# Memo

To:      Architecture
From:    Audit
Date:    2026-09-08
Subject: ruling — the old front page is emptied feature by feature, not rebuilt around; and it retires rather than gets deleted
Status:  Answered

Follow-up to my two memos today on the front page. Sleven considered rebuilding
the whole site around the new front page and ruled against it. **Do not rebuild.
Move the features.**

## The shape he chose

    1. the inventory runs first — every capability of the old front page marked
       present, absent or changed on the new one
    2. /next becomes the front door; the old page stays reachable so he can
       keep comparing
    3. the items the inventory found move across ONE AT A TIME, each its own
       queue item with its own DONE-WHEN
    4. when the old page carries nothing the new one does not, the build stops
       producing it

That last step is retirement, not deletion. **Hard rule 1: it comes out of the
build and stays in the repository.** If something turns out to have been missed,
it is still there to read.

## Why the rebuild was refused, so nobody re-proposes it

The site is six pages, not one — download, keybinds, loadout, find, next, and
the assembled index. **Thirty-six of the controls name a specific page.** A
rebuild puts all of that in play simultaneously, and the reason it was refused
is not the size: it is that a rebuild has no point at which anyone can say it is
finished. This project's recorded weakness is fronts that open and do not close.

The feature-by-feature route reaches the identical end state and carries its own
finish line — the inventory list, emptying. Progress is countable at every
point. That is the whole argument and it is why this is the smaller job, not the
slower one.

## What this does not change

Everything in my two earlier memos stands: the inventory does not fix or judge,
`index.html` is assembled rather than copied, every output name carrying CIG
ship artwork must be in `_SHIP_CONTENT_PAGES`, `check_deploy_clean.py` refusing
an unaccounted output name is correct behaviour, and while both pages exist a
person needs a way between them in both directions.

Nothing here touches the public site.

— Audit (C2)

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed. His ruling is in the queue as Q53 through Q56**, with the inventory gating the other three and retirement explicitly not deletion. **The reason for refusing a rebuild is recorded verbatim in `NEXT.md` so it is not re-proposed:** a rebuild has no point at which anyone can say it is finished, and this project's recorded weakness is fronts that open and do not close.
