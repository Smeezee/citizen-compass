# ORDER — Build the attribution furniture and the off switch, BEFORE any RSI asset lands

    from    C1
    date    2026-08-22
    for     Code
    status  RUN THIS NOW. It does not depend on anything else and nothing else
            should start until it is done.

---

## The decision behind this order — Sleven's, taken 2026-08-22, not yours or mine

Citizen Compass will use RSI's holoviewer ship content the way the rest of this
community already does: **used and displayed, credited to Cloud Imperium Games,
with a visible "if you have a problem, contact me" notice on the page, and taken
down on request.**

His words: *"We will do the same thing that everybody else is doing... If that's
what everybody else is doing and everybody else is taking it right from RSI, then
that's good enough. And if they have a problem, then we take it down."*

**Rule 8. Do not argue it, do not caveat it in code comments, do not re-open it.**

**What this order builds is the half of that promise that has to exist first.**
The credit line and the takedown path are not paperwork that follows the
feature — they are the conditions under which the feature is allowed to exist.
Build them now, so there is never a minute in which CIG-sourced content is on
this site without them.

**Nothing in this order fetches, downloads or touches an RSI asset.** That work
is blocked on reconnaissance that has not come back yet. Do not start it, do not
scaffold for it, do not write a fetcher "ready for later".

---

## A1 — The trademark notice, verbatim and always visible

CIG's Fan Kit Guidelines specify this exactly. It is quoted here word for word
from `claude/FINDING_fankit-inventory-2026-08-08.md`, which read the PDF itself:

    Star Citizen®, Roberts Space Industries® and Cloud Imperium® are registered
    trademarks of Cloud Imperium Rights LLC.

Requirements, as CIG states them:

- **Minimum 10-point font.**
- On a website: *"displayed on the home page, on a navigation area that is
  always visible regardless of scrolling, or both."*

Put it in a navigation area that is always visible regardless of scrolling, on
**every page**, not just the home page. The ship page already scrolls its columns
internally and not the page body, so an always-visible footer strip is cheap
there — but check the other pages, which do scroll.

**Do not retype the sentence.** Define it once as a single constant, in one
place, and have every page take it from there. It carries three registered-
trademark symbols and a specific legal entity name; a typo in a required legal
notice is a defect, and six hand-copied instances is six chances at one.

    CONTROL: assert the constant appears on every built page, AND assert that a
    page built with the constant deliberately blanked FAILS the check. A check
    that passes because the string is present somewhere in a 410 KB file is not
    a check — resolve it in the rendered page and assert its computed font-size
    is >= 10pt and that it is inside the always-visible chrome, not in a
    scrolled region.

## A2 — The "Made By The Community" mark

Both logo variants (black-ring / white-ring) are in the Fan Kit already on the
machine at `Downloads\Fankit_2025_11_19\`. CIG's stated requirement:

- **In the corner** of any images.
- **No less than 50% opacity.**
- **A reasonably legible size** — CIG names legibility, not a pixel figure.

And the hard prohibitions, which CIG applies to *all images and assets*: **no
recolouring, no flipping or reversing, no distorting, no outlines or drop
shadows, no patterns/textures/effects applied on top.**

`claude/FINDING_hologram-display-concept-2026-08-08.md` already did this once
correctly on a real render at 70% opacity. **Follow that precedent; do not invent
a second approach.**

    CONTROL: the negative control is the load-bearing one. Assert that an image
    composited WITHOUT the mark is REFUSED by the build. Without that, "the mark
    is applied" also passes on a build that applies nothing.

## A3 — The source and contact notice — the part that is Sleven's own commitment

A short, plainly-worded block, visible on any page that displays ship content:

- **What it is** — ship models and imagery from Cloud Imperium Games' own
  holoviewer.
- **Who owns it** — Cloud Imperium Games. This site is an unofficial fan site,
  not affiliated with or endorsed by CIG.
- **How to complain** — a real, working contact route, stated in plain English:
  if Cloud Imperium Games would like any of this removed, here is where to say
  so, and it will be removed.

**Do not invent the contact address.** Read it from configuration. If the config
value is absent, **the build fails loudly** — it does not ship a page that
promises a contact route and does not have one. Sleven supplies the real address;
your job is to make its absence impossible to miss.

Write the wording in the plain-language register the ship page already uses.
Sleven's standing instruction: the user has to understand what they are looking
at. That applies to a legal notice more than to a stat tile, not less.

    CONTROL: build with the config value removed and assert the build FAILS.
    A notice that silently renders "contact: " with nothing after it is the exact
    failure this control exists to catch.

## A4 — THE OFF SWITCH. This is the item that matters most.

Sleven's commitment was *"if they have a problem, then we take it down."*

**A promise you cannot execute in ten minutes is not a promise.** Build the
mechanism that makes it true:

1. **Every CIG-sourced asset is tagged as such at the data layer**, from the
   moment the first one arrives — a real field on the record, not a filename
   convention and not a folder. Folders get reorganised; a field survives.
2. **One command removes every asset carrying that tag** from the built site and
   rebuilds it, leaving the site working — degraded, honest about what is
   missing, not broken. A page whose model has been pulled says the model was
   removed at the rights holder's request. It does not show a broken canvas and
   it does not silently render an empty box.
3. **The command is exercised in the test suite as a real run**, not documented
   as a procedure. A takedown script nobody has ever executed is a script that
   fails the first time it is needed, which is the worst possible time.
4. **Document it in one page** — `docs/TAKEDOWN.md` — written for somebody who is
   stressed and in a hurry. One command, at the top, in a plain code block.
   Explanation below it, not above it.

Note for your own reasoning: this is the same discipline as the preservation
guard and the checker lifecycle. **A control that has never been observed to fire
is an assumption.**

    CONTROL: run the takedown against a fixture set containing both tagged and
    untagged assets. Assert every tagged asset is gone, assert every UNTAGGED
    asset SURVIVES, and assert the site still builds and serves. The second of
    those three is the one that catches a script that just deletes everything.

## A5 — Measure and report the current static-asset exposure. Do NOT fix it blind.

**A real difference between what this site does and what the rest of the
community does, and it needs to be on the record before more assets arrive.**

Every project in this space renders models and refuses to hand out the files.
myfleet.gg's own repository states it: *"Issues asking for 3D model files (or
links to them) will be closed or removed without comment. Models will not be
provided, shared, or pointed to."*

`CURRENT-STATE.md` already records that our testing site does not have that
property: the password gate does not cover static assets, and `models/100i.glb`
was fetched directly on 2026-08-07 and returned binary. **Anything under
`_deploy/` that is not HTML is on the open internet.**

**Measure it, do not fix it.** Report:

- Exactly which asset types are directly fetchable on the deployed testing site,
  verified by fetching them, not by reading config.
- What it would actually take to serve model bytes through a Worker route that
  checks `Referer` or `Origin` — and **state honestly how weak that is**, because
  it is trivially bypassed and every project using it knows that.
- What it would cost in bandwidth and complexity.
- Whether the live Netlify site has the same property.

**Then stop.** Whether to do anything about it is Sleven's call, and it is a
different call from the one he already made. Give him a measurement, three
options with real trade-offs, and a recommendation. Do not implement one.

## A6 — Sweep, deploy to testing, verify from the served bytes

The standing rule applies: **testing deploys are automatic and need no
permission** (`RULING_testing-deploys-are-automatic-2026-08-22.md`). The live
site is not touched.

Verify from the **deployed bytes**, not from source and not from a successful
deploy — this project has been caught five times by a deploy that reported
success and published elsewhere. Resolve the notice in the served HTML, resolve
the contact block, and state the version ID.

---

## Run rules

Unchanged from `ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md` and
every order since. Restating the two that get forgotten:

- **No decision gates.** Everything above is pre-ruled. If you hit a genuine
  ambiguity, pick the option that is easier to reverse, write down that you
  picked it and why, and keep going. Do not stop and wait.
- **Append to the ledger as you go**, one entry per item, with the commit sha.
  The ledger is what survives your context being compacted.

**And the honest limit, stated up front so you do not have to discover it:** the
question of whether CIG minds is not answerable by anything in this repository.
This order does not try to answer it. It makes the answer cheap to act on when it
comes.
