# Update — Q49 is on the served site. Sweep green, deploy done, three walks passed

**Filed 2026-09-09 18:05 CDT.**

## THE SWEEP WENT GREEN

    127 ok, 0 failed, 3 skipped, 0 NOT RUN, in 4025s
    receipt 2026-09-09T17:58:44, payload 95912315762859de

**Zero failures, zero NOT RUN.** The three skipped are the `_deployed` controls
that need a live site, which is the normal skip.

**And the working-figure line I built this afternoon fired for real on its first
opportunity:**

    OVER THE WORKING FIGURE: 4025s (67.1 min) against 3600s (60 min), 425s over.
    REPORTED, NOT GATED - this does not stop a deploy and is not a failure.

It did not stop the deploy, which is exactly what it was built not to do.

**Its per-control timings are still contaminated by my own concurrent work and
must not be counted as one of Sleven's three receipts.** The pass/fail is sound;
the seconds are not.

## DEPLOYED

    sweep    127 control(s) green against this exact payload
    upload   2 new or modified assets, 524 already uploaded
    version  53bfd496-91d9-4ccc-ae84-8b2477a989eb

Standing ruling, 2026-08-22: *"Every run that changes anything the site serves
ENDS BY DEPLOYING TO TESTING. No permission, no asking, no waiting."* The live
site was not touched and `deploy_live.ps1` was not run.

## CONFIRMED FROM SERVED BYTES, NOT FROM THE BUILD

    /loadout  URLSearchParams(location.search).get("from")==="next")
              {a.setAttribute("href","next.html")}
    /next     carries loadout.html?from=next
    /         cc-kb, cc-panel, and the preview gate all present
    /models/Hammerhead.glb   200, 4,153,816 bytes

`_verify_deployed_links.mjs` against the live site: **SWEEP CLEAN** — 19 internal
references across 11 pages plus 15 external, canary 404 proving it can report.
**Eleven pages because `next.html` is now in the list**; yesterday it was four.

## THE WALK — THREE, AND THE THIRD IS THE ONE THAT MATTERS

    inspector  Code, 2026-09-09, against the served site, in a real browser

    WALK 1  /next  -> ship -> "All ships"  ->  landed /next          ok
    WALK 2  /      -> ship -> "All ships"  ->  landed /              ok
    WALK 3  ship page with NO parameter    ->  landed /              ok

**Walks 1 and 2 would both pass on a patch that always pointed one way**, given
each front page linked the matching direction. Only a page reached with **no
parameter** tests that the parameter is what decides. That is walk 3 and I added
it because the two ordered walks prove less than they look like they prove.

Every walk clicks the real control rather than reading its href — a correct href
and a link that does not navigate are different outcomes — and watches for
`pageerror` throughout, so a page that lands correctly while throwing is not a
pass.

## THE FIRST SERVED WALK FAILED AND THE SITE WAS RIGHT

Walk 1 went red: *"landed on next"* against an expected `next.html`. **The
deployment 307s `/next.html` to `/next`.** My assertion was too literal.

Both sides are now reduced the same way, with the normalisation written into the
file per rule 17 — an exact rewrite of two spellings of one resource that the
server's own redirect says are the same, not a similarity match. `/next` and
`/nextish` stay different and landing on the wrong page still fails.

## WHAT I COULD NOT DO

Architecture asked for the walk recorded in **Q49's closure**. `NEXT.md` is C1's,
so the closure entry is theirs; the record is in the memo answer, formatted to
paste.

## STILL BLOCKED

**The Stop hook.** Authorised by Sleven twice in writing, refused by this
session's own permission layer on `.claude/settings.json`. Backup taken, every
claim verified, exact change written out.

**Build tray: 9 open** (counted at filing; the watcher is still filing tonight's closures). Nothing committed.
