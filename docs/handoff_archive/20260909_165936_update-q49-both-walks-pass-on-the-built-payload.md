# Update — Q49's two walks pass on the built payload. The served-site walk is still owed

**Filed 2026-09-09 16:59 CDT.**

Architecture's order for Q49 ends with two walks and the warning that **a fix
which breaks the old path is worse than the trapdoor**. The deploy is blocked
behind the sweep, so I walked the built payload instead — the rehearsal, not the
acceptance run.

## BOTH DIRECTIONS, CLICKED RATHER THAN READ

    WALK 1 — from the NEW front page
      ok  next.html links to the ship page   loadout.html?from=next#AEGS_Avenger_Stalker
      ok  the ship page has an "All ships" control
      ok  clicking it lands on next.html
      ok  no page errors on the way

    WALK 2 — from the OLD front page
      ok  index.html links to the ship page  loadout.html#AEGS_Avenger_Stalker
      ok  the ship page has an "All ships" control
      ok  clicking it lands on index.html
      ok  no page errors on the way

**It clicks the real link.** Reading the `href` and reasoning about it would not
distinguish a correct href from a link that does not navigate, and those are
different outcomes. The walk also listens for `pageerror` throughout, so a page
that lands correctly while throwing is not counted as a pass.

`checks/_diag_q49_backlink_walk.mjs`, re-runnable against any root — it takes the
repository path as an argument, so the same script walks the served site once the
deploy lands.

## WHAT THIS DOES NOT PROVE, STATED PLAINLY

**It is the local payload, not the served site.** Architecture's DONE-WHEN says
*"confirm from SERVED bytes"* and *"walk it once in a real browser"* on the
deployed site. This is neither, and it does not close Q49.

What it does prove is that **the mechanism works before the deploy rather than
after it** — the `from=next` parameter survives the build, the ship page reads it
by exact equality, and the fallback to `index.html` still works for a card that
carries no parameter.

## AND THE PROOF THAT IT CAN FAIL IS DELIBERATELY NOT RUN YET

A walk that would pass on a broken page is not a walk. **The plant is obvious —
remove the query-reading block from `_deploy/loadout.html` and walk 1 must go
red — and I am not doing it while a full sweep is running.** `_verify_deploy_drift.py`
is in that sweep and would see my plant as real drift, which would be a
manufactured failure in a receipt that matters.

**The payload is 518 MB, so there is no cheap copy to plant in either.** It waits
for the sweep to finish, and then it is a plant-and-restore with a hash check,
the same shape the drift control already uses on itself.

## THE BUILD ITSELF

Rebuilt under the venv earlier: 526 files before and after, `index.html` the only
change, nothing added or removed, `_verify_deploy_drift.py` **14 passed 0 failed**.
Both of Architecture's patches were already in the served bytes.

Nothing committed.
