To:      Architecture
From:    Sleven
Date:    2026-09-08
Subject: ruling — the mark goes on every card, and the doctrine currently says the opposite in my name
Status:  Answered

**Every card carries the mark. Not a single line at the top of the page.**

I was shown both, drawn with real card shapes, and I picked the per-card mark.

## FIRST, FIX THE DOCUMENT — THIS IS THE URGENT HALF

`docs/UX_DOCTRINE.md` carries a section headed **"RULED BY SLEVEN 2026-09-08 —
SAY IT ONCE, LOUDLY, NOT 254 TIMES QUIETLY"**, followed by bullets introduced as
*"His reasoning, recorded so it can be applied to cases he has not named."*

**I never said any of that.** It was written in my voice by a session drafting an
order I never approved, and it reached the document anyway. It is now not only
misattributed but **backwards** — it rules against what I have actually decided.

Strike it. Put this ruling in its place, dated today, and say plainly in the
replacement that the earlier text was never mine. Do not quietly edit it into
agreement — the record should show that a fabricated ruling got in, or nobody
learns anything from it.

Sections are frozen; amend in place, do not renumber.

## THE RULING

**Every ship card carries a mark saying its data has not been checked against a
game patch.** All of them, while all of them are unverified.

**The mark is per-card and stays per-card.** When ships start getting verified,
the mark keeps its place and starts distinguishing checked from unchecked —
which is when it begins carrying real information. **Build it so that switch is
a data condition, not a rewrite.** That part of the earlier text was sound and
it is the only part worth keeping.

Hard rule 20 is untouched and not in play. Every row still carries
`last_verified_patch`.

## WHAT I HAVE NOT DECIDED

**The words on the badge.** I was shown wording written for a page-level bar and
it does not fit a card. Propose the card wording yourself and show me before it
ships. Short enough to sit on a card and still mean something.

## WHAT WAS ARGUED AGAINST IT, SO YOU HAVE IT

A mark on all 254 cards never varies, so it stops being read after the first
screen, and it cannot tell one ship from another.

**I went with it anyway and the reason is worth writing down:** a person landing
on a single ship from a search never sees the top of the ship list, and on a
phone a line at the top of the page scrolls away in one flick. The mark travels
with the card. The bar does not.
---

ANSWERS:

**Architecture, 2026-09-09.**

**Done. The fabricated section is struck and your ruling is in its place, dated
today, saying plainly that the earlier text was never yours.**

## WHAT THE DOCUMENT NOW SAYS

Section 21, `docs/UX_DOCTRINE.md`, amended in place. Nothing renumbered.

Two subsections where there was one. The first is headed **STRUCK 2026-09-08 —
THE TEXT THAT STOOD HERE WAS NEVER SLEVEN'S**, and it says what stood there, that
you never said it, that it was written in your voice by a session drafting an
order you never approved, and **that C1 carried it into a frozen document without
checking that the words were yours.** Your reason for striking rather than
correcting is quoted in your own words.

The second is your ruling: **the mark goes on every card**, per-card and staying
per-card, the switch built as a data condition rather than a rewrite, with your
reason about a person landing on a single ship from a search and a bar that
scrolls away in one flick on a phone. **The argument against it is recorded too**,
because you recorded it yourself.

**The one sentence kept from the struck text** is the data-condition sentence, and
the document says that is the only thing carried over.

## THE CARD WORDING — PROPOSED, NOT SHIPPED

You asked for wording that fits a card and still means something. **The test I
used: it has to read as the same field in both states, so that the day ships start
getting verified nothing on the card has to be redesigned.**

**RECOMMENDED**

    unverified   Not patch-checked
    verified     Patch-checked · 4.10

Two words, one negation between the states, and **"patch" is the player's own
word** — nobody who plays this game needs it explained. It says what is missing
rather than passing judgement on the ship, which matters when it is sitting on
all 254 cards at once.

**ALTERNATIVE — plainer, one word longer**

    unverified   Not checked against a patch
    verified     Checked against 4.10

Reads better in a sentence, harder to fit on a card at phone width.

**ALTERNATIVE — shortest**

    unverified   Unchecked
    verified     4.10

Fits anywhere. **I would not ship it**: alone on a card, "Unchecked" invites the
reader to think the ship is unchecked, not the data about it.

**Nothing is built until you pick one.**

---

# REVISED 2026-09-09 — HE PUSHED BACK AND THE RECOMMENDATION CHANGES

**His constraint, and it is the one I under-weighted:** the mark must not make the
site look like *"nothing verified and nothing checked and, like, it doesn't need to
look like we don't actually have answers."*

**He is right, and it kills my own recommendation.** `Not patch-checked` leads with
a negative. Printed on all 254 cards at once it is a wall of *not*, and a visitor
reads that as **the site has nothing**, when the truth is that the site has the data
and has not yet confirmed it against the current game patch. **Those are very
different messages and the wording was sending the wrong one.**

## THE REVISED RECOMMENDATION

    unverified   Awaiting 4.10 check
    verified     Checked · 4.10

**Why this one.**

**It leads with the process, not the absence.** *Awaiting* says work is coming.
*Not* says something is missing.

**It carries real information from day one, which answers the strongest argument
against a per-card mark.** The objection was that a mark on 254 cards never varies
and stops being read. **This one names the patch**, so every card tells a visitor
which game version is the reference point — and that changes when CIG patches, on
its own, without anybody rewriting anything.

**Both states name the same patch**, so it is obviously one field in two conditions,
and the switch stays a data condition rather than a rewrite.

**And the site visibly improves as work lands.** The unverified label is the longer,
heavier one; the verified label is shorter and cleaner. **A page filling up with
`Checked · 4.10` looks like progress**, which is the honest picture.

## THE PART THAT WORDING CANNOT FIX, AND IT IS A DESIGN RULING

**If the mark is styled as a warning, no wording saves it.** A red or amber alert
badge on all 254 cards makes the site look broken no matter what it says.

**It is a quiet neutral chip, carrying the same visual weight as the role line or
the price.** A statement of where the data stands — not an alert, not a caution
colour, not an icon that reads as a problem. **Doctrine Section 25: visual
prominence follows informational importance**, and this is context, not a hazard.

When a ship becomes verified the label may gain the smallest positive signal it can
carry. **The unverified state stays neutral, always.**

## THE EARLIER PROPOSALS, KEPT SO THE THINKING IS ON THE RECORD

    Not patch-checked / Patch-checked · 4.10      withdrawn — leads with a negative
    Not checked against a patch / Checked ...     same defect, longer
    Unchecked / 4.10                              worst — alone on a card,
                                                  "Unchecked" reads as though the
                                                  SHIP is unchecked, not the data

**Still nothing is built until he picks.**

