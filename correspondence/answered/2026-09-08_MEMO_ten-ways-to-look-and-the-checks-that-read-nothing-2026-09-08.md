# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: ten reader types, and the group nobody builds — checks that catch a wrong reading without reading anything
Status:  Answered

Sleven asked whether readers could work by genuinely different rules. Catalogue:
`claude/DESIGN_ten-ways-to-look-and-the-ones-that-never-read-a-word-2026-09-08.md`

## The constraint that makes it interesting

Every reader receives the same thing: a grid of dots carrying red, green and blue.
**There is no hidden layer in a captured frame.** So a genuinely different reader is
not one with more access — it is one that **discards different information on the
way in**, and therefore fails on different things.

Banned first: two different OCR engines. Same kind of looking, different branding,
correlated failures. That is the false-corroboration trap wearing a second logo.

## The group worth your attention

Five of the ten are variations on looking at pixels — shape without colour, colour
without shape, template matching, inverted, multi-scale. All useful, all still
reading content.

**Four are not, and they are the ones almost nothing anywhere builds:**

**Layout.** Where are the boxes, how many, how arranged — *what kind of screen is
this*, answered before anything on it is read. **This is exactly the question that
was got wrong 426 times.** `terminal_open` on frames with no shop panel is a content
answer given to a layout question.

**Count, do not read.** A reader returns twelve items; the picture geometrically
contains fourteen rows. **The reader missed two, and nothing was read to find that
out.**

**Measure the width.** Evenly-spaced digits mean the pixel width of a number states
how many digits it has. A reader says "4320" and the space is five digits wide —
something is wrong. **Caught by arithmetic on a rectangle.**

**Read the frame, not the fill.** Is the region I am reading actually the region I
think it is? Catches the failure where recognition is working perfectly on the wrong
rectangle — which better recognition can never catch.

## Why this sharpens the third-witness rule

    WEAKEST    a second reader of the same kind on the same pixels
    BETTER     a reader that discards different information
    STRONGEST  a check that never reads the content at all, or an exact
               source that had nothing to recognise

**A checker that re-reads shares the evidence. A checker that measures something the
reader never looked at shares almost nothing.** These are cheap, nearly independent,
and they feel like they are not doing the real work — which is why they do not get
built. They are not doing the reading. They are doing the checking, and the checking
is what this project has historically had none of.

## Two things to verify before anyone builds

**The width check is ASSUMED, not measured.** It needs Star Citizen's UI to space
digits evenly, and **I have not measured that on a single frame.** True of most game
interfaces, not all. **Measure it on the 628 first.** If the font is proportional,
that check is worthless as written and needs rebuilding around character cells.

**Some of this may already exist.** `_diag_cover_threshold.mjs` and
`_diag_q5_contact_sheet.mjs` both measure coverage in pixels rather than reading
content — that is group B behaviour. **I have read their opening comments only, so I
may be proposing back something already written.** Worth opening before treating any
of this as new.

## What it does not change

**Nothing here needs a seventh field.** A lens wanting one of these writes it as side
B being a different reader on the same capture. The shape already expresses it.

That is the second time this week something new fitted the six fields without a
special case — the first was your boundary lens. Taking that as evidence the shape
is right rather than as a coincidence.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Closed as MOVED.** Looking Project material and maintained there. **One correction is preserved on this side because it kept getting confused:** *ten ways to look* is the Looking Project's reader inventory. *Sixty angles* is this project's own examination doctrine in `design/ANGLES.md`. Similar names, different subjects, and one of them nearly got deleted for resembling the other.
