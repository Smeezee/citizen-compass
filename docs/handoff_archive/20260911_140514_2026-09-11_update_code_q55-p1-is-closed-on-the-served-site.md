# Update — Q55.P1 is closed. The four dead addresses land again on the served site.

**2026-09-11 14:08 CDT / 19:08 UTC. Deployed and verified.**

    #matrix     -> ships tab     "AEGIS DYNAMICS · 28 ships · 19 buyable in game…"
    #dev        -> dev tab       "DEVELOPMENT PROGRESS…"
    #calendar   -> cal tab       "SALE CALENDAR…"
    #legend     -> legend tab    "LEGEND & SOURCES…"

**Walked in a real browser against the deployed origin**, reading what a visitor
ends up looking at rather than what the page source says. Both canaries hold: a
bare load lands on the default tab, and an address no mapping covers does not
move the page — so the walk can tell a mapped address from an unmapped one.
`checks/_diag_q55_p1_addresses.mjs`.

**The front-door walk is still green** — gate, `/classic`, `/next`, and the
404 canary all unchanged.

**Version ID `80b59f0b-da46-4c98-9dad-d10f8462e0ce`. Sweep 129 green against
this exact payload (`988edd0334304d69`), 0 failed, 0 not run.**

## SCOPE HELD

The names are the OLD page's and they are **mapped, not renamed** — nobody's
bookmark gets rewritten. **The hash is deliberately not written back on a tab
click and the back button is not handled: that is P3**, and riding it along
would give a failure two possible causes.

The tab switch became a named function because the hash path and the click path
must not be two copies of the same logic.

## A MISTAKE OF MINE THAT COULD HAVE SHIPPED A FALSE GREEN

**I chained the pre-checks and the sweep in one command, and the sweep started
while `_verify_deploy_drift.py` was planting hand edits into the payload.** A
sweep measuring a payload another control is actively mutating proves nothing —
and it would have gone green, and I would have deployed on it.

**Caught by checking whether the sweep log existed while drift was still
running.** Killed it, re-ran drift alone (16 passed, payload restored byte for
byte, hash handler and stamp and gate all present), then ran the sweep alone
with nothing else touching the payload. **The 129-green receipt above is from
that clean run, not the contaminated one.**

## NEXT, AND IT IS OWNER'S 13:55 LETTER

**On a phone the front door hides the testing stamp.** `#ver` computes to
`display:none` at 386 px, so the marker is in the bytes and invisible on screen.
**My guard reads the bytes, so it passes** — the same shape as P24 itself: a
check that holds while the thing it protects is defeated, one screen width down.

His instruction: *"Treat it as P24's own unfinished edge, not a new feature.
File it where it belongs, fix it when P1 is done, and prove the fix at phone
width on the served page, not from the build."*

**P1 is done, so I am taking it now.** I will reproduce it at phone width
myself before changing anything — he used a same-origin iframe because Chrome
refused to resize the real window, and I would rather confirm it with a real
mobile viewport than inherit a measurement I did not take.

*Code, 2026-09-11 14:08 CDT.*
