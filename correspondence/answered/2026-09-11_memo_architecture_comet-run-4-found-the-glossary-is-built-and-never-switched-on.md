# Memo

To:      Engineering
From:    Owner
Subject: The phone review is in. The glossary is built and never switched on, and the ship page scrolls sideways.
Status:  Closed

The full review is on disk, with Comet's findings word for word:
`claude/RESULT_comet-run-4-phone-2026-09-11.md`. 16 findings, 14 CONFIRMED, measured at
390 px. It follows the run 3 memo; the Cutlass Black price and the lost list position came
up again and are not repeated here.

## CHECKED AGAINST THE DEPLOYED FILES BEFORE SENDING

**1. The glossary exists and is never used on the front page (M-014).** `next.html` already
carries definitions for "aUEC" and "SCU", with the tap, hover and keyboard tooltip code.
Nothing on the front page ever calls it, so visitors see jargon on every card with no
definition anywhere. The ship page calls it for part names only. This looks like the
cheapest real fix on the list.

**2. The ship page cannot say where a ship is sold (M-005).** Neither "New Deal" nor
"Lorville" appears in `loadout.html` or `loadout_data.gen.js`. The front page card says
"at New Deal · Lorville"; the ship page, which is where a visitor goes to learn more,
shows less. Same class as run 3's T-011.

**3. The ship page scrolls sideways on a phone (M-007).** Comet measured the ship dropdown
at 425 px in a 390 px screen, so the whole page slides and labels are cut ("FACTURER").
The dropdown has no width rule that I could find.

## FROM THE REVIEW, NOT RE-CHECKED BY ME

- M-001 and M-002: the category-chip row scrolls sideways with no cue; the currency selector
  sits at the far end of it, entirely off-screen.
- M-003: the "Legend & Sources" tab, the one that explains trust, is clipped off-screen on
  the first view.
- M-006: the ship page heading is cut to "Drake Cutlass …".
- M-009 and M-010: tabs, chips and ship-page buttons measure 27 to 35 px tall, under 44 px.
- M-012: the "aUEC" label is 9.5 px at 4.34:1 contrast.
- M-013: forward Tab never reaches the section tabs; only Shift+Tab does.
- M-016 (opinion): the loadout list is a scroll box inside the page, which catches swipes.

## ALSO

- M-011: the testing stamp is 2.89:1 contrast. I recomputed it from the colours. The stamp is
  now visible on a phone, so the hidden-stamp item Code took at 14:08 is fixed as far as a
  visitor can see.

## WHAT I WANT

Same as the run 3 memo: queue entries for what is new, one per item, with the three above at
the top in that order. They are defects, not features, so none of them needs my keep-or-drop.

---

ANSWERS:

**Architecture, 2026-09-11. Filed into Q62 with the run 3 findings, your three at the
top in your order. M-011 is closed and M-005 was merged rather than duplicated.**

## THE GLOSSARY IS THE ONE TO READ TWICE, AND YOU ARE RIGHT THAT IT IS CHEAPEST

**`next.html` already carries the definitions AND the tap, hover and keyboard tooltip
code. Nothing calls it.** Built, deployed, working, switched off.

**This is the fourth instance of one shape in this project and it should be read as a
pattern rather than four items:**

    thirty ships      a model built, shipped, and reachable by no visitor
    /keybinds         94,082 bytes serving today, no link from the front door
    /find             31,387 bytes serving today, no link from the front door
    the glossary      definitions and tooltip code shipped, never invoked

**Work that was paid for, finished, and is sitting inside the product doing nothing.**
The first three you are being asked to keep-or-drop; this one nobody has to decide,
which is what makes it the cheapest real fix on the list.

## M-005 IS FILED WITH RUN 3's T-011 AS ONE ENTRY

Two reviewers found the same defect from two directions — **the desktop one saw two bare
dealer names where the data has prices; the phone one found that "New Deal" and
"Lorville" are not in `loadout.html` or `loadout_data.gen.js` at all.** Same entry, both
measurements cited. **I would rather it be one item that is certainly true than two that
half-overlap.**

## M-007 CARRIES M-006 WITH IT

**A 425 px dropdown in a 390 px screen is the cause; the cut heading is the symptom.**
They close together, and if the heading is still clipped after the width rule lands then
there is a second cause and it gets its own entry.

## M-011 IS CLOSED AND YOU CLOSED IT

**You recomputed the stamp's contrast from the colours yourself and the stamp is now
visible on a phone.** Recorded as closed rather than left on the list — a finding that
is fixed and still listed is the same defect as a stale queue.

## M-016 IS FILED AS AN OPINION AND LABELLED ONE

Comet marked the loadout scroll box an opinion. **It is in the queue as one, and it must
not be worked as if it were measured.** A decision either way in a dated line closes it.

## THE REST

M-001, M-002 and M-003 are filed as one entry — **all three are things the first phone
view hides**, including the Legend & Sources tab, which is the one that explains trust.
M-009, M-010, M-012 and M-013 are filed as one reach-and-legibility entry, including the
one that costs a keyboard user the most: **forward Tab never reaches the section tabs.**

**Nothing here needed your keep-or-drop and nothing is coming back to you.**

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.** Run 5, the last of the review, went to you separately.
