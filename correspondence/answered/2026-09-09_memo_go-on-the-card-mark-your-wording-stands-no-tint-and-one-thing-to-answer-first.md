# Memo

To:      Architecture
From:    Owner
Date:    2026-09-09
Subject: GO on the card mark — your wording stands, one change to the styling, one thing to answer first
Status:  Answered

**Your wording is approved as you recommended it.**

    while unverified     Awaiting 4.10 check
    once verified        Checked · 4.10

Your reasoning holds and I am not going to restate it back at you. Two changes,
and only one of them touches the design.

---

## 1. NO COLOUR ON EITHER CHIP. THEY LOOK IDENTICAL.

You wanted the unverified chip neutral and a small positive tint on the verified
one. **Drop the tint. Both states get the same chip — same colour, same weight,
same position. The only thing that changes is the word.**

I had this checked against the research before signing off, and the tint is the
part that fails.

Nielsen Norman Group, *Banner Blindness Revisited*: people skip content that
"stands out from immediate surrounding context" because they have learned that
anything visually distinct is an advert. In their measurement, **one fixation out
of 132 landed in a region occupying 25% of the content area — a 33-fold drop
against the space it took up.** They call it hot-potato scanning: the eye touches
it, decides it is not for them, and then avoids that area for the rest of the
session. **The effect is worse on mobile, which is how I read this site.**

So a tinted chip sitting where a badge sits is the one thing on the card most
likely to go unread. **The tint would make the good news the part nobody sees**,
which is the exact opposite of what you wanted it for.

Identical chips also make the mark one field in two conditions, visually as well as
structurally — which is what you said you were after.

## 2. ANSWER THIS BEFORE ANYTHING IS BUILT — WHAT DOES THE CARD SAY WHEN 4.11 SHIPS?

**Your strongest argument for this wording is that the patch number moves on its
own so the mark never goes stale. Follow it through and it breaks both ways.**

**If the unverified cards roll forward to `Awaiting 4.11 check`:** every card resets
its promise on patch day, and every ship verified up to that point looks
unverified again. The site would show no progress no matter how much work landed.

**If they stay at `Awaiting 4.10 check`:** they are now naming a patch that is not
current, which is the abandoned-project reading arriving on a schedule.

**And `Checked · 4.10` on a 4.11 game means two different things that look
identical:** *checked and correct*, or *checked two patches ago and nobody has
looked since.* A visitor cannot tell which, and the second one is what gets a site
called wrong.

**This is a data-model question, not a copy question, and it is yours.** Work out
what each state says across a patch boundary, then build.

---

## ONE MORE THING TO READ, NOT TO ACTION

`claude/HUMAN-CHECK_the-card-mark-wording-2026-09-09.md` — the full check behind
this, including two costs of the wording I decided to carry knowingly rather than
change. The one worth your attention: **`Awaiting` is a promise with a clock on
it.** It reads as diligence now and as abandonment if it is still sitting there in
three months, and that is a fact about how fast verification actually moves, not
about the words.

**Related, and it is the reason the second condition above is not optional:** the
word `Checked` makes every error on that card far more expensive than the same
error under `Awaiting`. Nothing carries `Checked` until the check behind it is real
and can be re-run.

## WHAT HAPPENS NOW

Wording into `docs/UX_DOCTRINE.md` Section 21 as decided, with the no-tint change
recorded as part of the decision. Answer the patch-boundary question. Then the
build order to Code.

---

ANSWERS:

**Architecture, 2026-09-09. The tint is dropped, and the patch-boundary question
has an answer: there are three states, not two, and the third is created by CIG
shipping rather than by anyone here doing anything.**

## 1. NO COLOUR — TAKEN, AND IT TIGHTENS THE WORDS

Every state gets the identical chip. **Your ruling, and it makes the word carry
the whole signal**, which means each label now has to be distinguishable from the
others at a glance without colour. That is a constraint on the wording rather than
a preference about it, and it changed one of my three labels below.

## 2. THE PATCH BOUNDARY — YOU FOUND THE HOLE IN MY OWN BEST ARGUMENT

**Both of your readings are wrong for the same reason, and it is not the one I
was defending.** Rolling forward resets the promise and hides every ship already
verified. Freezing names a dead patch. **Neither works because the number should
never have been in that state at all.**

**A row that has never been checked has no relationship to any patch.** Naming one
states a fact that does not exist — which is the defect this whole section of the
doctrine was written to prevent, arriving through my own recommendation.

**So I withdraw the patch number from the unverified label**, and with it the
argument that the mark carries information from day one. It was buying an
appearance, not a fact.

### The three states

    NEVER CHECKED        last_verified_patch IS NULL
    CHECKED, CURRENT     last_verified_patch == the patch the game is on
    CHECKED, OVERTAKEN   last_verified_patch is behind the patch the game is on

**The third is the one you named** — *checked and correct* against *checked two
patches ago and nobody has looked since* — and the two-state design printed them
identically because it had no way to tell them apart.

### The labels

    Awaiting check          never checked against anything
    Checked · 4.10          checked, and 4.10 is what the game is on
    Needs re-check · 4.9    checked, and the game has moved past it

**The third label is new and you have not seen it, so it is a proposal.** I chose
`Needs re-check` over `Last checked` deliberately: with no colour anywhere,
`Checked · 4.10` and `Last checked · 4.9` differ by one word and one digit and are
easy to confuse at a glance. **This is the dangerous state — the one where the site
could be wrong and look right — so it gets the label that cannot be mistaken for
the good one**, even though it is longer. It will also never be on all 254 cards
the way `Awaiting check` is today.

**Nothing is blocked on your answer**, because no row can currently reach either
verified state.

## 3. THE STATE IS DERIVED, NEVER STORED — THIS IS THE ACTUAL ANSWER

Computed where the page is built, from the row's `last_verified_patch` against
**one** current-patch value. **No per-row state column and no data migration on
patch day.**

**When 4.11 ships, every `Checked · 4.10` becomes `Needs re-check · 4.10` by
itself.** Nothing on the site can go on quietly claiming to be current, because the
comparison happens in the build rather than in the visitor's head — which is the
part of your objection that mattered. A visitor never has to know which patch is
current to read the card correctly.

**And it is what makes the switch a data condition rather than a rewrite**, which
was your own condition from the ruling.

## 4. ONE THING NEITHER OF US HAD, AND IT IS WHERE THIS WOULD ROT

**Every label depends on one value: which patch the game is on.** If that value is
typed by hand and somebody forgets it on patch day, **every verified card keeps
saying `Checked` about a patch the game has left** — and the mark built to prevent
exactly that becomes the thing asserting it.

**So the current-patch value is read from a source and a control asserts it is
current.** Hard rule 12: without it nothing about this mark can ever fail, and a
mark that cannot be wrong is decoration.

That control is part of the build order, not a follow-up.

## 5. `Checked` DOES NOT GET USED UNTIL THE CHECK IS REAL

Accepted without qualification. **As of today no row qualifies** — all 254 carry no
`last_verified_patch` at all — **so the site shows `Awaiting check` and nothing
else.** That is the honest picture rather than a defect in the mark.

## 6. THE COST YOU ARE CARRYING KNOWINGLY IS IN THE DOCTRINE

`Awaiting` is a promise with a clock on it, and it reads as abandonment if it is
still on 254 cards in three months. **Written into Section 21 as a choice made with
its cost known**, so that nobody later reads it as a mistake and quietly changes it.

**It also turns the wording into a fact about the pipeline.** The label is only
safe while verification is actually moving, and right now the number of rows that
have ever been verified is zero — which makes Q61 the item this label depends on
rather than a queue entry.

## WHAT IS DONE AND WHAT IS MOVING

`docs/UX_DOCTRINE.md` Section 21 carries all of it, dated, with the no-tint change
recorded as yours and the research attributed to the check you commissioned rather
than restated here. Sections frozen, nothing renumbered. Build order to Code.
