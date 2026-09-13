# Memo

To:      Architecture
From:    Owner
Subject: Echo found a real contradiction — the report control posts to a server that does not exist. Answered, pack corrected.
Status:  Answered

Full answer on disk:
`claude/CLARIFICATION_the-report-control-needs-a-server-and-we-do-not-have-one-2026-09-12.md`.
Read-only, nothing modified.

## THE FACTS, OFF THE CONFIGURATION FILES

**Neither site can receive anything.** `testing/wrangler.toml` and `wrangler.live.toml` are
static-asset configurations: a name, an account, `workers_dev`, an `[assets] directory`.
**No `main` script, so no code runs. No KV, D1 or R2 binding, so there is nowhere to put a
note.** The live Cloudflare worker still does not exist and the public site is a hand
upload. FastAPI and the Procfile are in the repository and host nothing.

## THE PART THAT KEEPS YOUR RECOMMENDATION ALIVE

**Cloudflare serves the static files without invoking code, and only runs a Worker when the
requested URL is not a file** — their documentation, page updated 2026-07-03. So one address
becomes a receiver and every page, image and model stays exactly as static as it is today.
**Your on-page form posting to the testing site's own Worker is still the right shape; it
just needs `main`, a binding and a store, and none of those exist yet.**

**D1 over KV**, so "every report about this ship" is answerable later without writing a
program. **And the notes come out by a command Code runs into the repository, not by
somebody remembering to open a dashboard** — a dashboard nobody checks is the feedback
form's own failure moved to the other end.

## WHAT I WANT HELD

**The control does not ship until a test note has been stored and read back.** Not a greyed
button, not a promise. A "Report issue" control that cannot receive is the false footer
again, and the page may not say anything false.

**Turnstile is the likely spam gate and I have not confirmed its price.** Do not plan on free
until somebody reads the plan page.

## AND THE PACK WAS WRONG

The standing pack said plain files, no server application. **Corrected on disk and reissued
to Echo**, with the exception written into it and the collector's Worker named so nobody
reads "no server" as "no Workers anywhere".


---

ANSWERS:

**Architecture, 2026-09-12. The hold is right and it is now written as the entry's
DONE-WHEN rather than as an instruction somebody has to remember. Nothing is built.**

## THE HOLD, AS A CONDITION A MACHINE CAN CHECK

**The control does not ship until a note has been stored and read back out.** Not a greyed
button, not a promise, not a form that posts into nothing.

**DONE-WHEN:** a test note submitted from the served page is retrievable from the store by
the command Code runs into the repository, and the retrieval is shown. Until that exists the
control is not on any page.

**A "Report issue" button that cannot receive is the false footer wearing a new hat**, and it
is the fifth surface of that one rule this week — the filter that answers for 219 of 253 and
is silent about 34, help text written around a listed defect, a "buy" label for a price we do
not track, a stat that changes what it measures without changing how it looks, and now a
control that says it is listening.

## THE SHAPE IS ACCEPTED AND SO IS THE STORE

**A Worker only runs when the requested URL is not a file**, so one address becomes a
receiver and every page, image and model stays exactly as static as it is today. **D1 over
KV**, so *every report about this ship* is answerable later without writing a program.

**And the notes come out by a command into the repository, not by somebody opening a
dashboard.** A dashboard nobody checks is the feedback form's own failure moved to the far
end.

## TURNSTILE IS AN UNKNOWN AND IT IS NOT HIS TO GO AND FIND

**Nobody plans on free until somebody reads the plan page.** That is a research task on a
vendor's own published pricing, and it is ordered rather than carried.

## WHAT IS NOT ACCEPTED YET

**`main`, the binding and the store do not exist**, so this is a build with three parts that
have never been stood up on this project. It gets a proposal with its own DONE-WHEN before
anything is written, and it does not jump the front page.

*C1, 2026-09-12.*
