# Memo

To:      Architecture
From:    Owner
Subject: Two things — the variant line goes to Echo before I answer your three questions, and here is what every ship actually has.
Status:  Answered
## 1. YOUR THREE PACKAGE QUESTIONS ARE NOT ANSWERED YET, ON PURPOSE

**I want Echo's read before I shape it, and the shape I want is wider than packages.**

My words, carried to her: a ship page should tell a visitor there are other shapes of this
ship — a package it is sold in, a paint, an edition — and let them click one to see what it
is. No functional difference is claimed, and the click goes to that exact thing's page on
the official store. **The same treatment for paints, until we can actually show a paint on
the model.**

The brief is on disk: `claude/ECHO_variants-packages-and-paints-on-a-ship-page-2026-09-12.md`.
It asks her two things: how this is presented where it has been studied, and whether paint
or livery data exists anywhere we could legitimately use.

**Your letter stays open and your recommendation is not rejected — it is waiting for one
more input. Nothing about the Carrack card moves in the meantime.**

## 2. THE SHIP INVENTORY HE ASKED FOR IS ON DISK

`claude/INVENTORY_what-every-ship-has-and-what-it-is-missing-2026-09-12.md`, with the
per-ship table as `claude/ship-coverage-2026-09-12.csv`. Counted by machine over all 253
rows in the deployed data. **Three things in it change work you already have:**

**T-003 IS NOT A FILTER DEFECT.** The 34 ships with no career are exactly — as a set — the
34 with no hull identifier, and therefore no ship page, no model, no length, no crew and no
cargo. **One missing join, six symptoms, and the filter is the only one a visitor sees.**
Fixing the filter would hide it.

**THE VARIANT PLAN HAS A HOLE IN OUR OWN DATA.** 24 rows carry no link to the official
store, and they are disproportionately the edition rows the plan depends on — Carrack
Expedition, the Executive Editions, the Emeralds, Gladius Pirate, Sabre Raven, Ursa Fortuna,
the Heartseekers. **The link that design sends people to does not exist for the rows that
need it most.**

**ONLY 63 OF 179 PURCHASABLE SHIPS CARRY A PRICE PER DEALER.** The other 116 show one
in-game price beside a list of shops, which reads as a price at those shops. That is T-011
and M-005 measured at scale.

Also: no ship has a width or height, only length; 22 models have no weapon markers; six
ships have no picture; and eight rows carry no price of any kind.

**Nothing is built and nothing is ordered by this letter.** File what is new against the
existing entries rather than opening duplicates.

---

ANSWERS:

**Architecture, 2026-09-12. Recorded against the existing entries, no duplicates opened.
Two of the three change an entry's SIZE rather than adding one, and the third changes what
the Echo design can be built on.**

## 1. T-003 — CONFIRMED FROM A SECOND DIRECTION THE SAME NIGHT

**Your inventory says the 34 careerless ships are exactly the 34 with no hull identifier.
Build measured the same thing independently on the front page's own cards and got both
difference-sets empty.** Two instruments, two surfaces, same answer.

**"One missing join, six symptoms, and the filter is the only one a visitor sees" is the
better sentence than anything in my entries** and it is now in Q63.8 in those words.
**Fixing the filter would hide it** — which is the trap, because the filter is the cheap
fix and the only visible one.

## 2. THE 24 MISSING LINKS — THIS IS THE ONE THAT CHANGES THE BUILD

**It lands exactly on Echo's correction in your other letter, and neither letter says so.**

    the design I was holding    the official store link IS the identity of an
                                edition or package
    your inventory              24 rows have no store link, and they are
                                DISPROPORTIONATELY the edition rows — Carrack
                                Expedition, the Executive Editions, the
                                Emeralds, Gladius Pirate, Sabre Raven, Ursa
                                Fortuna, the Heartseekers
    Echo's correction           the link is NOT the identity. A local record
                                with a verification status, and the link hangs
                                off it as dated evidence.

**Built my way it would have been finished and then found unbuildable on the rows it was
for.** Echo's shape is not a refinement, it is what makes the feature possible at all.
**"Not located" becomes a recorded state instead of a blank, and the feature ships without
waiting on 24 links that may never exist.**

## 3. 63 OF 179 — T-011 AND M-005 GET A SIZE, AND IT IS MUCH WORSE THAN THE ENTRIES SAID

**116 purchasable ships show one in-game price beside a list of shops, which reads as a
price at those shops.**

**This is the same defect the whole project was started to fix.** The tagline is *know
where to buy, before you fly*, and on 116 of 179 ships the page shows a number next to a
list of places and lets the visitor assume the number belongs to the places. **A price and
a copied one are different facts and this is 116 rows of the second presented as the
first.**

**Sized into T-011 and M-005 rather than opened as a new entry, as you asked.** It is now
the largest honesty defect on the board by row count.

## THE REST — RECORDED, NOT PROMOTED

    no ship has a width or height, only length
    22 models carry no weapon markers
    6 ships have no picture
    8 rows carry no price of any kind

**All four are recorded against their existing entries.** None of them is being turned into
a job by this letter.

## ONE THING I AM SAYING BECAUSE IT IS TRUE AND NOT BECAUSE IT IS PLEASANT

**Counted by machine over all 253 rows of the deployed data is the difference between this
letter and every estimate that preceded it.** Four numbers I have been carrying in entries
this week were wrong in the same direction — P20 was five times too big, Q58's count was a
character proxy, the hull gap was 35 and is 34 on the surface that matters, and the price
gap was "some ships" and is 116.

**Every one of those got smaller or sharper when somebody measured it, and every one of
them was mine.** The pattern is not that the estimates were careless; it is that an entry
written from a symptom inherits the symptom's shape. **The rider that catches it is already
in `design/ANGLES.md` and I am the one who keeps triggering it.**

*C1, 2026-09-12.*
