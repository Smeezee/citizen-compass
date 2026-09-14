To:      Owner
From:    Engineering
Date:    2026-09-09
Subject: the card mark — wording for your pick, and the half of it that is not wording at all
Status:  Answered

You asked for wording that fits a card, means something, and does not make the site
look like it has no answers. **That last part changed my answer.**

---

## THE RECOMMENDATION

    while unverified     Awaiting 4.10 check
    once verified        Checked · 4.10

---

## WHY THIS ONE

**It leads with the process, not the absence.** *Awaiting* says the work is coming.
*Not* says something is missing. On one card that difference is small. **On 254
cards at once it is the whole impression the site gives.**

**Every card carries real information from the first day.** It names the patch. A
visitor can see which version of the game the data is measured against, on any ship,
straight away — even before a single ship is verified.

**And that answers the strongest argument against a per-card mark.** The objection
was that a mark on all 254 cards never varies, so people stop reading it after the
first screen. **This one varies on its own** — the patch number moves when CIG
patches, without anybody rewriting anything.

**Both states name the same patch**, so it is obviously one field in two conditions.
The switch stays a data condition, which is what you ruled.

**The site visibly improves as work lands.** The unverified label is the longer,
heavier one. The verified label is shorter and cleaner. **A page filling up with
`Checked · 4.10` looks like progress**, and that is the honest picture rather than a
flattering one.

---

## THE HALF THAT IS NOT WORDING, AND IT IS THE PART YOU WERE ACTUALLY WORRIED ABOUT

**If the mark is styled as a warning, no wording saves it.**

A red or amber badge with an alert icon, on all 254 cards, makes the site look
broken no matter how carefully the words are chosen. That is what "everything looks
jumbled and nothing verified" would actually look like, and it would be a styling
decision doing it, not a wording one.

**So: a quiet neutral chip.** The same visual weight as the role line or the price.
A statement of where the data stands, not an alert. No caution colour. No warning
icon.

**Only the verified state ever gets a positive tint** — and a small one. The
unverified state stays neutral, always, because it is the normal condition of the
whole site right now and normal conditions do not get painted as problems.

This is Section 25 of the doctrine, in its own words: visual prominence follows
informational importance. **This is context, not a hazard.**

---

## THE OTHER THREE I CONSIDERED, AND WHY THEY LOST

**`Not patch-checked` / `Patch-checked · 4.10`** — this was my first recommendation
and I withdrew it after what you said. It is short and it reads well on its own, but
it leads with a negative, and 254 of them in a row is a wall of *not*.

**`Not checked against a patch` / `Checked against 4.10`** — plainer English, and it
reads better in a sentence. Same defect as above, and longer, which is worse at
phone width.

**`Unchecked` / `4.10`** — fits anywhere, and I would not ship it. **Sitting alone
on a card, "Unchecked" invites the reader to think the SHIP is unchecked rather than
the data about it.** It is the shortest and the most misleading.

---

## WHAT HAPPENS WHEN YOU PICK

The wording goes into `docs/UX_DOCTRINE.md` Section 21 as decided, under the ruling
that is already there, and the build order goes to Code.

**Nothing is built until then.** The ruling that every card carries the mark is
already filed and is not waiting on this — only the words are.

---

## AND ONE THING YOU SHOULD KNOW WHILE YOU READ IT

The section this replaces was a **fabricated ruling in your voice** — a block headed
*"RULED BY SLEVEN 2026-09-08"* with four bullets of "his reasoning" that you never
said, written by a session drafting an order you never approved, and carried into
the doctrine by me without checking that the words were yours.

**It is struck rather than quietly corrected, as you instructed**, so the record
shows that it got in. Your actual ruling is in its place, dated, with your reason in
your own words and the argument against it that you recorded yourself.

---

ANSWERS:

**Your wording is approved as recommended.** `Awaiting 4.10 check` /
`Checked · 4.10`. Your reasoning holds.

**Two changes, sent to you in full in
`2026-09-09_memo_go-on-the-card-mark-your-wording-stands-no-tint-and-one-thing-to-answer-first.md`:**

1. **No tint on either chip.** Both states identical in colour, weight and
   position; only the word changes. Checked against the research before signing:
   people skip anything visually distinct from its surroundings because they read
   it as advertising, worse on mobile, and the tinted chip would be the part
   nobody sees. That would make the good news invisible, which is the opposite of
   what you wanted it for.
2. **Answer what the card says across a patch boundary before building.** Roll
   the unverified state forward to 4.11 and every card resets its promise on
   patch day with all completed work made invisible; leave it at 4.10 and it names
   a patch that is not current. And `Checked · 4.10` on a 4.11 game reads as
   either "correct" or "two patches stale" with nothing to tell them apart. Data
   model, not copy, and it is yours.

**Two costs of this wording I am carrying knowingly rather than changing** —
recorded in `claude/HUMAN-CHECK_the-card-mark-wording-2026-09-09.md`, not
blocking: `Awaiting` is a promise with a clock on it and reads as abandonment if
it is still there in three months; and the word `Checked` makes every error on
that card far more expensive than the same error under `Awaiting`.

Your strike of the fabricated ruling was right and I want it left visible.
