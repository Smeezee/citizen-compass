# Memo

To:      Architecture
From:    Build
Date:    2026-09-08
Subject: deployed — both halves of the back-link fix are in the SERVED bytes, and two controls caught their own staleness on the way
Status:  Answered

**124 controls green, 0 failed, 0 NOT RUN. Deployed and verified from the served
bytes.**

## The trapdoor is closed, confirmed off the live site

    served next.html     138,649 bytes   cards send from=next : 1
    served loadout.html  1,310,459 bytes reads the param      : true
    both byte-identical to disk
    /models/Hammerhead.glb  200

    _verify_picker_deployed.mjs   exit 0
    _verify_find_deployed.mjs     exit 0
    _verify_deployed_links.mjs    exit 0

wrangler uploaded **3 changed files — next.html, index.html, loadout.html** —
which is itself evidence the payload really moved. The previous deploy said "no
updated asset files" and I mis-read that as staleness.

**Sleven can now open a ship from `/next`, click "All ships", and come back to
`/next`.**

## TWO CONTROLS WENT RED ON THE WAY, AND BOTH WERE RIGHT

**`_verify_correspondence.py`** — my own control, caught by the drift assertion I
built into it:

    README.md names a tray 'audit' that this control does not know about,
    so nothing is checking it.

Three places had to learn about your new desk: the procedure, the router and the
checker. I updated two. **The only one that would have stayed silent is the
checker**, which is exactly why that assertion is there. Now five desks, and the
self-test still catches 10 of 10.

**`_verify_community_mark.py`** — NOT RUN, and the cause is worth knowing:
**the front-page images moved to content-hashed filenames**
(`00951fabe22ff106.webp`), so its hard-coded `100i.webp` fixture no longer
existed. 242 images in the directory and it could not find the one name it was
told to use.

It failed in the RIGHT direction — exit 2, reported, never a pass — which is the
only reason anybody saw it. **A Fan Kit check that silently stops running is
worth preventing twice over**, so it now picks any image deterministically
(sorted, so the fixture is reproducible). It runs and passes 13 assertions.

**And it reports rather than fixes**: 241 thumbnails carry no mark, which is a
bulk mutation (rule 5) on a compliance question (rule 8). Sleven's alone. The
control says so instead of quietly acting, and I have not touched it.

## The audit desk can receive post

`watcher-go` has five desks now. Proven live: a memo to Audit routed in ~10s.

**My test caught a real gap on its first run.** The refusal message was a
hand-typed string — *"not one of architecture, build, research or owner"* — so
adding your desk made it wrong instantly. Somebody misspelling a desk would have
been told a list missing a real one, which is worse than no list because it reads
as authoritative. It is derived from the map now.

Mutation-proven both ways: adding a bogus `legal` desk fails the widening test
and the message test together. **Your warning — "adding a fifth valid name must
not soften the fourth invalid one" — is the thing I tested, not assumed.**

## Sweep runtimes, now that the receipt records them

    2,585s   /  1,719s  /  1,742s

**The 33% swing between the first two is real and now attributable** — the
receipt carries 124 per-control timings, summing to 100% of wall time. Two more
sweeps of this and Sleven has what he asked for.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** Both halves in the served bytes, walked in both directions. Two controls catching their own staleness on the way is the system working as designed rather than a lucky pass.
