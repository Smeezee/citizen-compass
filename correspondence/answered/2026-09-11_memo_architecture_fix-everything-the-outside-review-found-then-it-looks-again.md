# Memo

To:      Engineering
From:    Owner
Subject: Fix everything the outside review found. When it is all fixed, the review runs again.
Status:  Closed

## MY WORDS

> "It has caught a few things more than I did myself. So those things need to get fixed.
> And then once we fix all of them, we will have it go back through and look."

## WHAT THAT MEANS

**1. Every confirmed finding from the five Comet runs gets fixed.** That is Q62 as you filed
it from runs 3 and 4, plus the run 5 items when you file them. OPINION findings, such as
M-016, get a dated decision line either way, as you already said.

**2. Scope is the test site.** The public site is frozen. Its false claims (the RAPTOR
sentence, and the "LIVE 4.9.0" banner) are a separate question already in my tray. This
letter does not reach it.

**3. My reading of "fix all of them", so you do not have to ask:** it includes the two
findings you said were waiting on my keep-or-drop. T-002 (no link to /find, Q55.P16) and
T-007 (no patch attached to a price, Q55.P5 / Q61) are **keep**. The review found them as
problems, and I said the problems get fixed. The other Q55 keep-or-drops that the review did
not touch are still mine and still open.

**4. The feedback route is the one fix that still needs a pick from me: where the notes go.**
Everything else about it is ruled. Do not let it hold up the rest.

## ORDER

You own the order. My preference, for you to overrule with a reason:
1. Anything that says something false: T-008, T-012 and their kind.
2. Anything that gives a wrong answer about the ships: T-003 (the filter), T-009 (two
   prices), T-010 (roles), T-011 / M-005 (the ship page with no shop).
3. The cheap wiring of work that is already built: the glossary first.
4. Phone layout, then reach and legibility.
5. The run 5 gaps against the public site.

## DONE, AND THEN THE SECOND LOOK

**Done means every entry from the review is closed with its evidence, and the fixes are live
on the test site.** Not "fixed in the file". Deployed and read back.

**When that is true, tell me in one letter.** The Adjutant desk then runs the review again:
the same five runs, the same rules, a freshly checked answer key, and every old finding ID
marked fixed, still there, or changed. New findings get new IDs.

**Nothing in this letter grants a commit, a push, a public-site change or any new
permission.** The usual rules stand.

---

ANSWERS:

**Architecture, 2026-09-11. Taken whole, order accepted as you wrote it, and one problem
with the instruction that is arithmetic rather than an opinion.**

## YOUR ORDER STANDS AND I AM NOT INVENTING A DISAGREEMENT

**You offered it for overruling with a reason. There is no real reason, so it goes in as
written.** Correctness before cheap wins is the right call and it is your own standard
from this morning — the site may be unfinished, it may not say anything false.

**Two adjustments inside it, neither of which moves a category:**

**T-009 must not be fixed at the display.** The seven RSI price corrections already queued
put the Cutlass Black at **$110** — so of the two numbers the site is showing, one is
already known stale. **Fixing the template first gives you a page that agrees with itself
and is still wrong.** The entry now says to read that one first.

**C-002 comes off the top of group 5 — it is closed.** No ship is missing; it was the
`editions.json` fold and I traced it against the public site's own data before filing.

## THE TWO YOU RESOLVED ARE CLOSED

**T-002 (Q55.P16) and T-007 (Q55.P5) are KEEP**, recorded in both entries with your
reason: the review found them as problems and the problems get fixed. **The Q55
keep-or-drops the review did not touch are untouched and still yours.**

## THE FEEDBACK ROUTE — YOUR LATER LETTER SUPERSEDES THIS ONE

This letter says the destination *"still needs a pick from me."* **Your later letter says
the destination stands and is not reopened** — the on-page form posting to the testing
site's own Worker, away from the collector's bucket. **I am taking the later one.** Only
placement and wording are open, they are with the research, and nothing is held for
them.

---

## THE ONE PROBLEM, AND IT IS IN THE ARITHMETIC RATHER THAN THE INTENT

**"Every confirmed finding" is about sixty entries. "One item at a time" and "done means
deployed and read back" cannot both be taken literally at that count.**

    the sweep                     1,885 seconds — 31 minutes — for 120 controls
    the deploy gate               refuses a payload whose fingerprint does not match
                                  the sweep receipt
    a rebuild                     changes the fingerprint and invalidates the receipt
    so, per DEPLOYED item         one build + one 31-minute sweep + one deploy
    sixty items deployed singly   OVER THIRTY HOURS of sweep time alone

**Those are our own measured numbers, not an estimate.**

**The fix is not to batch the fixes.** One commit per item is what makes a failure have
one possible cause, and that property is worth every minute it costs. **You have been
right about that twice this week.**

**It is to separate the two things your sentence joins: FIX one at a time, DEPLOY in
groups.** Each entry gets its own commit and its own evidence; a deploy carries whatever
has landed since the last one. **The one-cause property lives in the commit, not in the
deploy** — and "closed with its evidence" does not require a deploy cycle per entry.

**Recorded in Q62 as my reading, marked as mine, and work proceeds that way until you say
otherwise.** If you meant one deploy per item literally, say so and I will plan around
thirty hours of sweep rather than discover it in a week.

## WHAT DONE WILL LOOK LIKE

**One letter, when every entry from all five runs is closed with its evidence and live on
the test site.** Not before, and not a partial one. **Then the Adjutant re-runs all five
with a freshly checked answer key, every old ID marked fixed / still there / changed, and
new findings on new IDs.**

**Nothing in this grants a commit, a push, a public-site change or any new permission,
and none has been taken.**

*C1, 2026-09-11.*

## QUESTIONS

1. Deploy cadence: fix one at a time and deploy in groups, or did you mean one deploy per
   item?
2. The feedback destination — your later letter closed it; confirm I read the two letters
   the right way round.

---

**Owner, 2026-09-11. Read. Closed.** Deploy cadence answered in its own letter: fix one at a time, deploy in groups. Your reading was right.
