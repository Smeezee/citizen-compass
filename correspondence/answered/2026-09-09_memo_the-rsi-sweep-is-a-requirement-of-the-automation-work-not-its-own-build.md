# Memo

To:      Architecture
From:    Owner
Date:    2026-09-09
Subject: the RSI sweep is a requirement of the automation work, not a build job of its own
Status:  Answered

**Do not build a replacement RSI watcher as a separate thing. It goes into the
automation design as its first real workload.**

I asked why an hourly Claude session is doing work a program could do. The answer
was worse than the question. This memo is the ruling that comes out of it.

## WHAT IS ACTUALLY WRONG WITH IT

From the watcher's own records, not from an opinion:

- **Twenty-two consecutive fully-blocked runs** in one stretch in August.
- **The devtracker returns frozen snapshots** — identical top post at "51 minutes
  ago" across three fetches spanning two hours. Confirmed, not suspected. It is
  the source the runbook checks first.
- **The status page serves content about seven weeks old**, still calling 4.9.0
  current.
- **The roadmap and the ship pages have never been read.** Not degraded — never
  worked, the whole month, because they are JavaScript-rendered and a WebFetch
  cannot run them.
- Its one real roadmap recovery came from a third-party mirror its own state file
  now lists under DO NOT USE.

**Tonight's classified finding in full: a roadmap post exists, its body could not
be read, and I should go and read it myself.** That is a link in an email, and it
runs for twenty-two minutes.

**Four of five sources blind. That is a correctness problem, not a cost one.**

## WHY IT IS NOT ITS OWN BUILD

I ruled this morning that the automation proposal comes before the queue. **A
bespoke watcher built now is something that work then has to swallow or throw
away**, and this project has a documented habit of solving the same problem in a
new place. **It is the same problem: something happens outside, a program notices,
a session gets woken only if there is something to think about.**

**So the sweep becomes the first workload the automation design has to satisfy.**
It is a good one — small, real, already specified, and it either works or visibly
does not.

## WHAT IT MUST BE ABLE TO DO — carry these into the design

    hourly, locally, no model      fetch, diff post IDs against a stored set,
                                   compare build strings, run the staleness
                                   test, write state, and stop
    a real browser                 the roadmap and pledge/ships pages need one.
                                   Whatever runs this must drive a headless
                                   browser, or it inherits the blindness
    wake on a real change only     hand the woken session the specific new item,
                                   get the classification, stop
    the wake cannot self-trigger   the trigger is a post ID published by CIG.
                                   Nothing a woken session can produce

**The judgement that stays with a model, and only when something new appears:** new
hull or livery; **is it a RENAME**, which silently breaks 316 name joins; which of
BUILD / DEVPOST / SHIP / ROADMAP / ECONOMY / EVENT; and what a post actually says.

**The current prompt's hard-won rules are not thrown away — they move into the
spec.** The planted-control rule, the livery trap, the rename trap, the write
budget, the staleness test, cache-busting every URL, and CONFIRMED against
REPORTED. Every one of those exists because something went wrong once.

## ONE PIECE IS CARVED OUT AND STAYS WITH CODE NOW

**Which patch the game is on.** Your own card-mark decision ends on it: if that
value is stale on patch day, every verified card goes on claiming to be current.
You have already asked Code for a real source and a control that proves it fresh.

**Leave that where it is.** It is small, the card mark needs it, and it is the one
part of the sweep that has worked reliably all month — a patchbot fetch and a
string comparison, correct even through the weeks everything else was blocked.

## TWO THINGS CHECKED TODAY THAT CHANGE THE DESIGN AROUND THIS

**Temporal runs a real server on Windows.** Their own page: *"The CLI is available
for macOS, Linux, and Windows"*, and it *"includes a local Temporal development
service"*, started with `temporal server start-dev`. **The limit: that is the
DEVELOPMENT server and it uses an in-memory database.** For a system whose product
is surviving restarts, in-memory is not a footnote. Production-server support on
Windows is unconfirmed and is now the open question.

**`claude --bare` cannot use the subscription.** Anthropic's own words: *"Set
`ANTHROPIC_API_KEY` before running it, because bare mode doesn't use your
subscription login"*. And on the same page, *"`--bare` ... will become the default
for `-p` in a future release."* **So the cheap-startup mode and subscription
billing are mutually exclusive, and the default may move.** Anything designed
around `claude -p` being subscription-billed has to survive that.

Both are recorded with sources in
`claude/VERIFIED_the-automation-proposal-first-four-claims-2026-09-09.md`. The
watcher analysis is in
`claude/FINDING_the-rsi-watcher-pays-an-ai-to-do-a-diff-2026-09-09.md`.

## WHAT I AM NOT ASKING FOR

**Not a schedule.** Not a decision on Temporal against something simpler — that is
still being checked and I have not ruled on it.

**And do not switch the current watcher off.** It is blind on four sources and
still the only thing watching. It runs until the replacement is proved, not until
the replacement is designed.

---

ANSWERS:

**Architecture, 2026-09-09. Ruling recorded. No replacement watcher is being built,
the five requirements are now binding on the automation design, and the patch
carve-out stays with Code exactly as you left it.**

## WHAT I AM NOT DOING

No bespoke watcher. No schedule. No ruling on Temporal against anything simpler —
you have not ruled and I am not filling the gap. **And the current watcher stays
running**, blind on four sources, because it is still the only thing watching.

## THE FOUR BLIND SOURCES ARE ONE FAILURE, NOT FOUR

Worth stating because it changes what the requirement is: **the roadmap and ship
pages were never readable, and the devtracker and status page serve stale
snapshots. What the current watcher can read is exactly the static content.**

**So it is one capability gap wearing four faces — no browser** — which is why your
second requirement is the one everything else rests on. A design that satisfies the
other four and not that one inherits the blindness whole.

## THE PATTERN UNDERNEATH IT HAPPENED TWICE TODAY, IN TWO UNRELATED SYSTEMS

**The watcher reported results for a month while four of five sources returned
nothing, and nothing said four sources were blind.**

**Today the deployed-links control printed SWEEP CLEAN for ten days while never
fetching the new front page** — its page list was typed and had gone stale, so it
kept passing over a smaller world.

    a system that reports what it managed to read,
    without reporting what it failed to read,
    will look healthy while going blind

**That is now a requirement on the automation design as well as the check suite:
report coverage, not only results.** *Four of five sources unreadable* has to be a
number on the face of it, not something somebody works out a month later from the
records. It is also the cheapest of the requirements to build and the one most
likely to be dropped as a nicety.

## THE FIVE REQUIREMENTS ARE CARRIED AS WRITTEN

Hourly, locally, no model, for fetch-diff-compare-write-stop. A real browser. Wake
on a real change only. **A trigger that cannot be self-produced** — a post ID CIG
published, never anything a woken session can write. And the model judgement kept to
new items only: rename against new hull, the livery trap, and the classification.

**The hard-won prompt rules move into the spec rather than being rewritten** — the
planted control, the rename trap, the write budget, the staleness test,
cache-busting, CONFIRMED against REPORTED. Each of those is a scar and none of them
get re-derived from scratch.

## THE PATCH VALUE — CONFIRMED, AND IT WAS ALREADY WHERE YOU PUT IT

Code has the order: read the current patch from a real source and prove it fresh
with a control. **The card mark ends on that value** — stale on patch day and every
verified card keeps claiming to be current.

**Recorded here so the automation work does not later absorb it back** as "part of
the sweep." It is small, it works, the card mark depends on it, and it is the one
piece of the sweep that stayed correct through the weeks everything else was
blocked. **It stays out.**

## THE TWO CHECKS THAT CHANGE THE GROUND

Both carried into the design and neither is mine to rule on.

**The Temporal development server is in-memory.** For a system whose entire product
is surviving restarts, that is not a footnote — it is the requirement failing at the
first hurdle. Production-server support on Windows is the open question and it
should be answered before anything is built on it, not after.

**`--bare` and subscription billing are mutually exclusive, and `--bare` may become
the default for `-p`.** So anything designed around `claude -p` being
subscription-billed has to survive that default moving. **A design that only works
under today's default is a design with a clock on it**, and this project has just
spent a day on a label with the same problem.
