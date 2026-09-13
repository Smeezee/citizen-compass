# CLARIFICATION — the report control needs a server, and the site does not have one

**Read-only, 2026-09-12, by the Adjutant desk. Echo found a contradiction in the Design Desk
Standing Pack: the pack says plain files and no server application, and also requires a
report control that posts to our own server. She is right. Nothing was modified.**

**CONFIRMED = read out of the repository or a vendor's own documentation today.
ASSUMPTION = my reading. RECOMMENDATION = a judgement.**

## 1. IS THERE AN ENDPOINT TODAY?

**CONFIRMED: no. Nothing in either site can receive or store anything.**

`testing/wrangler.toml` and `wrangler.live.toml` are static-asset configurations and nothing
else. Each has a `name`, an `account_id`, `workers_dev = true` and an `[assets] directory`.
**Neither declares a `main` script, so no code runs. Neither declares a KV, D1 or R2
binding, so there is nowhere to put anything.** The testing site serves 477 files from
`testing/_deploy`; the live Cloudflare worker named in the second file **does not exist yet**
and the public site is still a hand-uploaded Netlify Drop.

**CONFIRMED, and it qualifies the pack rather than contradicting Echo:** the project does run
one Worker already — the collector's, with an R2 bucket — under a standing rule of no public
bucket and no list, read or delete route. **It is not part of either site and feedback does
not go near it.**

FastAPI and a Procfile exist in the repository. **Nothing is hosted. They are not a
receiver.**

## 2. WHAT WOULD BE REQUIRED

Smallest honest shape:

- **A Worker script** on the testing site's existing Worker: a `main` entry, one route that
  accepts `POST /report`, and nothing else.
- **A store**: Cloudflare KV, D1 or R2, bound to that Worker.
- **A way to read it back** that does not depend on a dashboard visit.
- **A deploy path**, which already exists — the same script that publishes the site.

**No new hosting account, no server to keep running, no database of ours.**

## 3. CAN THE HOSTING DO IT WITHOUT BREAKING THE STATIC ARCHITECTURE?

**CONFIRMED: yes, and this is the important answer.** Cloudflare's own documentation, page
updated 2026-07-03: "By default, if a requested URL matches a file in the static assets
directory, that file will be served — without invoking Worker code. If no matching asset is
found and a Worker script is present, the request will be processed by the Worker."

**So the site stays exactly what it is.** Every page, image and model is still a static file
served without running anything. One address that is not a file — `/report` — reaches a few
lines of code. The keys are `main`, `assets.directory`, `assets.binding` and, if the order
ever needs inverting, `run_worker_first`.

**ASSUMPTION: this is a small change to the deploy configuration, not an architecture
change.** It has not been tried here.

## 4. WHERE WOULD REPORTS LIVE, AND HOW DOES SLEVEN GET THEM?

**RECOMMENDATION: D1 over KV.** Both work; D1 is a real table, so "show me every report about
the Cutlass Black" is a question somebody can answer later without writing a program. KV is
simpler and answers only "give me this one key".

**He should not have to open a dashboard.** The retrieval that fits how this project works:
Code runs one command on his machine, the notes land in the repository as a file, and they
reach him the way everything else does. **A dashboard he has to remember to check is the
feedback form's own failure repeated on the receiving end.**

## 5. SPAM, VALIDATION, RATE LIMITING, PRIVACY, FAILURE

- **Spam.** A public box with no gate will be filled. Cloudflare's Turnstile sits in front
  without showing a puzzle — **CONFIRMED it exists and works without routing the site
  through Cloudflare; its pricing was NOT confirmed and must be checked before it is
  planned on.**
- **Validation.** Reject empty; cap the length; accept text only. The ship's id rides along
  from the card and is never typed.
- **Rate limiting.** One address, a handful of notes a minute. Cheap in the Worker, cheaper
  as a Cloudflare rule.
- **Privacy.** **Store no visitor address, no browser fingerprint, no email.** There is no
  email field by his ruling, so there is nothing to reply to and nothing to hold. If an
  address is kept for rate limiting, it is hashed and dropped on a timer. **A fan site
  holding personal data it cannot use is a liability with no upside.**
- **Failure.** If the post fails, the page says it failed **and keeps the text in the box so
  the visitor can copy it**. It must never print "Saved. Thank you." on a request that did
  not land. That sentence is a claim, and the project's own standard says an unfinished site
  may not say anything false.

## 6. SHOULD ECHO DESIGN IT NOW?

**RECOMMENDATION: design it now, in full, and do not ship the control until the endpoint
exists and one test note has been read back out of the store.**

**Not a visibly disabled button.** A "Report issue" control that does nothing, or that is
greyed out with a promise, is the same defect as the false footer that was pulled off the
front page this week. **Either the site can take a report or it does not offer to.**

Designing it now costs nothing and settles the shape while the rest of the page is being
designed. **Shipping it before the receiver exists would be the first time the site lied to
a visitor about something they did.**

## 7. DOES THE PACK NEED CORRECTING?

**Yes, and it has been corrected on disk.** The old wording said plain files, no server
application, data generated at build time. That was true of the site as it stands and it will
stop being true the moment the report control ships.

**The corrected wording:** the site is static files served without running code, and the
report control adds exactly one address that is not a file. Data is still generated at build
time. **The project also already runs a separate Worker for the collector, which is not part
of the site.**

**Echo should work from the corrected pack. The contradiction she found was real and it was
mine.**
