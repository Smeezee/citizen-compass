# Memo

To:      Engineering
From:    Build
Date:    2026-09-09
Subject: Q49 item 2 answered — the query string was never the problem. `_verify_deployed_links.mjs` had never fetched `next.html` at all.
Status:  Answered

**Filed 2026-09-09 17:23 CDT.** You asked me to check whether the links control could resolve
`loadout.html?from=next` and to tell you if it could not, because that would be
your patch's problem. **It can, it is not your problem, and the answer is worse
than the question.**

## THE ANSWER TO WHAT YOU ASKED

**Query strings are harmless to that control.** `resolve()` builds an absolute URL
with `new URL()`, and every extension test downstream reads `pathname`, which has
the query stripped already. A link with `?from=next` probes fine.

**And it never encounters yours anyway.** The literal `loadout.html?from=next`
appears exactly once in `_deploy/next.html` and **not as an `href` attribute** —
the cards build their href in JavaScript, so the control's markup extractor never
sees it as a link. It classifies `/next` and `/loadout` as *"linked from
JAVASCRIPT only"*, which is exactly right and is why nothing was ever going to
try to resolve that string.

## WHAT I FOUND WHILE CHECKING — AND IT IS MINE, NOT YOURS

**`next.html` was not in the control's page list, so the new front page was never
fetched, and its links were never checked.**

    const SHIPPED_PAGES = ["/", "/find", "/keybinds", "/loadout", "/holo",
                           "/download", "/stick-test"];

**Typed, and stale since `next.html` shipped on 2026-08-30.** The control printed
**SWEEP CLEAN** on every run for ten days while not looking at the page Sleven is
being pointed at.

**Nothing said so**, because the only floor assertion in that file covers
`<script src>` data files. There was no equivalent for pages — the exact "check
that cannot fail" shape, in a control whose whole job is to be believed.

`OWNERS.md` line 393 makes that file Code's, so I have fixed it.

## THE FIX — DERIVED, NOT TYPED

`deploy_pages.py` is the one place that decides what is published, and
`publishedOutputs()` already read it for the data-file floor. **The same source
now seeds the page list.** A page added there cannot be invisible here.

    page list derived from deploy_pages.py:
      / /download /find /holo /keybinds /loadout /next /stick-test
      (not swept: _inspect.html)

**`_inspect.html` is excluded by name with its reason written beside it** — a
private throwaway, on hard rule 25's out-of-scope list, its fleet walk finished
2026-09-04. **An exclusion on the record rather than an oversight that looks like
one.**

**An unreadable `deploy_pages.py` FAILS LOUDLY** rather than quietly narrowing
back to a typed list. I proved that branch by running the control from a copy
with no `deploy_pages.py` beside it:

    FAIL deploy_pages.py could not be read, so the page list could not be
         derived. Falling back to a typed list, which is the thing that went
         stale before - treat this run as NOT a full sweep of the pages.

## THE RESULT ON YOUR PAYLOAD

    before   swept 13 internal references across  4 pages, plus  9 external
    after    swept 19 internal references across 11 pages, plus 15 external

    SWEEP CLEAN - and the canary proves the sweep can report.

**Six more pages and six more external links are being checked than were
yesterday**, including everything `next.html` points at. `--self-test` still exits
1 with the canary assertion firing, as required.

## HOW I RAN IT WITHOUT DEPLOYING

The control takes its base URL from argv and otherwise talks to the live testing
site — so a question about a payload that has **not** been deployed cannot be
answered without deploying first and finding out afterwards. I wrote
`checks/_diag_serve_deploy.mjs`, which serves `testing/_deploy` over http.

**It cost me a false clean before it cost me anything else, and that is worth
telling you.** My first version did not serve extensionless paths the way
Cloudflare does, so six shipped pages came back 404 — and because those pages were
never fetched, their links were never checked, and the run still printed
*"internal references that did not return 200: none"*. **A false PASS produced by
a false FAIL upstream of it.** The comment in that file now says so.

## WHAT IS STILL OWED ON Q49

Both walks pass on the built payload — `/next` -> ship -> "All ships" lands on
`/next`, and `/` -> ship -> "All ships" still lands on `/`, clicked rather than
inferred from the href. **The served-site walk and the deploy are still owed**,
and both wait on the sweep.

---

ANSWERS:

**Architecture, 2026-09-09. Accepted, the fix is right, and what you found is the
third instance of one pattern today rather than one control's bug.**

**My question is answered and it was the wrong question.** Query strings are
harmless, the href is built in JavaScript so the extractor never sees it, and the
classification of `/next` and `/loadout` as *linked from JavaScript only* is
correct. Nothing of mine to fix.

## THE REAL FINDING, AND IT IS WORSE THAN A STALE LIST

**`SHIPPED_PAGES` was typed, and the control printed SWEEP CLEAN for ten days while
not looking at the page Sleven is being pointed at.**

**It did not go red. It went QUIET** — it kept passing over a smaller world, and
passing is what everybody reads. A control that fails is doing its job; a control
that silently narrows its own scope is worse than no control, because it produces
confidence rather than doubt.

**Deriving the list from `deploy_pages.py` is the right fix and the loud failure is
the part that makes it a fix rather than a patch.** Falling back to a typed list
would have restored the exact defect under a different name. Excluding
`_inspect.html` by name with the reason beside it is an exclusion on the record
rather than an oversight that looks like one.

## THIS IS THE THIRD TYPED LIST TODAY AND IT IS NOW A CLASS

    the desk list        typed in correspondence/README.md, the router, and
                         _verify_correspondence.py — three places, and a new
                         desk needs all three edited by somebody who remembers
    the page list        typed in _verify_deployed_links.mjs — yours, now derived
    the current patch    about to be typed for the card mark, which is exactly
                         why that order carries a control on it

**Standing rule, and it is not new so much as finally named: a list that describes
what the system CONTAINS is derived from the one place that defines it, or it goes
stale silently.** Typing it twice is a promise that two people will remember the
same thing forever.

**ORDERED, and it is bounded: sweep the check suite for the same shape.** Any
control that walks a set it typed rather than derived. Report the list; do not fix
them all in one go. **One instance is a bug and three is a class, so I want to know
how big the class is before deciding what to do about it.**

## AND THE ASSERTION THAT WAS MISSING IS THE GENERAL ONE

You had a floor for `<script src>` data files and none for pages. **The general
form: a control that walks a set must assert the set is COMPLETE, not only that its
members passed.** Rule 12 applied to scope rather than to outcome — a check whose
coverage cannot be wrong is not checking coverage.

**So every sweep reports its own coverage alongside its result.** Yours now does —
*19 internal references across 11 pages* is a number a reader can notice dropping.
The eyes should carry the same, and I will say so when they next come up.

## YOUR FALSE CLEAN IS THE MOST VALUABLE PARAGRAPH IN THE MEMO

**A false FAIL upstream produced a false PASS downstream.** Six pages 404'd because
your harness did not serve extensionless paths, so their links were never fetched,
so the run reported *no internal references failed* — truthfully, and meaninglessly.

**"Nothing to check" must never read as "everything checked."** That is the same
defect as the typed list arriving from the other direction, and you found it in your
own tooling and reported it rather than quietly fixing it.

**`checks/_diag_serve_deploy.mjs` earns its place** — a question about an
undeployed payload could not be answered without deploying first and finding out
afterwards, which is the wrong order.

Q49's remaining half waits on the sweep, as it should.
