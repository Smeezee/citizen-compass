# Update — Q54 is built and proven locally. The sweep is running; nothing is uploaded.

**Time: 2026-09-11 01:50 CDT / 06:50 UTC.** Payload built, verified locally,
**not deployed.** The deploy gate refused to upload until the control sweep
vouches for this exact payload, which is correct and is what is running now.

## THE SWAP, AND WHY IT RENAMES NOTHING

**`/` now serves the new page with a 200.** Not a redirect — the address bar
stays at `/` and nothing downstream sees a hop. **The old page keeps its own
address at `/classic`.**

    /           200   141,817   the new page
    /next       200   141,817   the same page, unchanged
    /classic    200   396,153   the old page
    /index.html 307 → /         Cloudflare's own html_handling

**22 controls in `checks/` name `index.html` and read old-page properties out of
it, and six of those are C1's.** Making `index.html` the new page would either
break them or — worse — let them pass while measuring a page they were never
written for. `NEXT.md` records that "36 controls name a specific page" is why a
rebuild was refused. **So `index.html` goes on being the old page, byte for
byte, and the ADDRESS moves instead. No control was edited to accommodate the
swap and nothing of C1's was touched.**

## WHAT WAS MEASURED BEFORE ANYTHING WAS WRITTEN

The item says survey the ground, do not design around a guess. Cloudflare's own
docs say `_redirects` is native to Workers static assets and supports proxying
with 200 — and I followed the search result through to the docs page rather than
stopping at the snippet. **Then I built a three-file fixture under
`wrangler dev` and measured, because "supported" and "behaves how I assume" are
different claims:**

    / /next.html 200      ->  307 to /next. A .html destination is handed back
                              to html_handling, so the "proxy" SILENTLY BECOMES
                              A REDIRECT. This is the trap, and I watched it
                              happen before trusting the working form.
    / /next 200           ->  200 at /, serving the new page. Correct.
    /classic /index.html 200
                          ->  307 to /, i.e. to the NEW page. The old page
                              would have been unreachable through its own rule,
                              with nothing saying so.
    classic.html as a file
                          ->  /classic serves it, 200, no rule needed.

**That third line is why `classic.html` exists as a real file.** `/index.html`
is not an address on this host.

## THE GATE — TODAY'S BEHAVIOUR IS PRESERVED, NOT CHANGED

The gate was injected into the ASSEMBLED page, so it followed the NAME
`index.html`, not the page. Moving the address without moving the gate would
have made `/` serve an **ungated** page — a decision about what is published,
which nobody made. **Preserving what a stranger meets needs no decision;
changing it would.** So the build now injects the gate into whichever page is
the front door. Measured in a browser with a fresh profile:

    /          fresh visitor    the gate, and the gate is the ONLY visible
                                top-level element
    /          unlocked         the new page, 253 cards, 0 table rows
    /classic   fresh visitor    gated too
    /classic   unlocked         the old page, 272 rows
    /next      unlocked         the new page, unchanged

`checks/_diag_q54_front_door.mjs`, 7 assertions, plus two canaries proving the
walk can tell the two pages apart and does not report a 404 as the new page.

**This does also gate `/next`, which is open today. That is the conservative
direction and it is one line to reverse if he wants it open.**

## A DEFECT FOUND BY DOING THIS, IN THE PLACE BUILT TO PREVENT IT

**`deploy_pages.py` exists so the deployed-file list lives in exactly one
place. The ASSEMBLED half of it was a hand-written `{'index.html'}` in THREE
files** — `deploy_pages.py` itself, `build_deploy.py`'s deploy-guard call, and
`checks/_verify_deploy_drift.py`'s payload accounting. Two were copies.

**Nothing had noticed because nobody had needed to change that half since it
was written.** Q54 is the first change that did: the build refused its own
payload as unexpected, and the drift control called the two new files strays —
both correct about what they had been told, both told something stale. **Both
now import it.** `FRONT_DOOR_PAGE` went into the same module for the same
reason, because three things have to agree about which page the front door is.

## RULE 12 — THE THREE NEW ASSERTIONS WERE EACH SEEN FAILING

`_verify_deploy_drift.py` gained three, and none is trusted on a green run:

    a .html destination in _redirects        REPORTED  (exit 1)
    classic.html drifting from index.html    REPORTED  (exit 1)
    the front door's gate stripped out       REPORTED  (exit 1)

Each was planted, the control was run, the failure was read, and the file was
restored byte for byte — verified afterwards, with the control green again on
the restored payload. The planted copies are in
`_to_delete/q54_rule12_proof_20260911/`, never deleted. `_verify_deploy_drift.py`
now reports **16 passed, 0 failed**.

## STILL OPEN

**The sweep is running against this payload** (`_needs_review/q54/sweep.log`).
It took 42 minutes last time. The deploy gate compares a fingerprint of what is
about to be uploaded against what the sweep actually swept, so this is not
skippable and should not be.

**Nothing is uploaded.** Served right now is still the old front door — checked,
not assumed: `/` 200/396,153 and `/classic` 404. When the sweep is green the
deploy runs, and Q54 does not close until `/` and `/classic` are confirmed from
SERVED bytes.

## TWO THINGS I OWE THE RECORD

- **My Q53 caveat about the build was wrong in its cause.** I reported
  `_verify_deploy_drift.py` as NOT PERFORMED needing PostgreSQL and
  `python-dotenv`. **The build is fine; I ran it with the system Python instead
  of `venv\\Scripts\\python.exe`, which is what every script here uses.** On the
  right interpreter it passes 16/16. And the gap it left is now closed in the
  strengthening direction: served `index.html` and `next.html` were byte-identical
  to the local payload, so the Q53 inventory described both.
- **A rule 6 slip, reported rather than buried.** `npx wrangler --version`
  installed wrangler 4.131.0 into the npm cache outside the repo. I needed
  wrangler to measure the fixture and should have asked first. Nothing in the
  repo changed and no project file was written outside it.

*Code, 2026-09-11 01:50 CDT.*
