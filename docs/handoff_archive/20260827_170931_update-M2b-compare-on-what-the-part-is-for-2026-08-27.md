# Update — M2b. The picker compares on what the part is FOR, and says what the number means.

**C1, 2026-08-27 17:34 local.** `loadout.src.html`. `node --check` clean.
Not built — yours.

Three changes, all from the brief's own words.

## 1. `gn` becomes an axis — the missile-rack complaint, fixed at the root

The brief named this defect exactly: *"A missile rack shows Mass 20 · IR 0 ·
EM 0 — not how many missiles it holds or what size. The next option reads Mass
3,000 with nothing explaining the 150x difference."*

**The cause: `CC_AXIS_ORDER` had no entry for how many things a part carries.**
So on a missile rack every key in that list missed, it fell through to SIZE,
and the row led with mass because mass came first in a fixed sequence.

`["gn","carried"]` is now in the order. The word is **"carried"** rather than
"missiles" because the same field is a turret's gun count — **one field, one
honest word for both**, rather than a label that is right on one port type and
wrong on the other.

## 2. The row leads with the PORT'S headline stat, not a fixed sequence

`partRow` emitted DPS, HP, Range, Power, Cooling, SCU, Mass, then the facts of
a different kind — the same order on every port. **So mass was the first thing
the eye met on a part where mass is a footnote.**

It now leads with the axis `sortRow` **already derives from the parts on
offer**, and marks it. No new machinery: the thing you are sorting by is now
the thing you read first, so the row and the control above it agree.

Guarded so the lead is never printed twice — `seen()` on every fixed-order
push.

## 3. Every number carries a plain sentence

The brief: *"every number carries a plain sentence saying what it means, the
way the right rail already does."* You have said repeatedly that the right-hand
column is the one you prefer, **and the reason you give is that it explains
itself. The picker never has.**

`CC_MEANS` uses **the rail's own words** where the rail has a line for the same
measurement, so the two halves of the page do not invent separate vocabularies
for one number.

**And it is on the page, not only in a tooltip:**

    Compared on carried — how many it carries, and at what size.

A tooltip is not an explanation to somebody on a touchscreen, and it is not an
explanation to somebody who does not know there is anything to hover.

## What to check, and the control that matters

    open a missile-rack port
    assert the first stat on each row is the carried count, not Mass
    assert the axis note is present and names "carried"

**The control: remove `["gn","carried"]` from CC_AXIS_ORDER in the served
bytes.** The rows must go back to leading with Mass and the assertion must go
red. Without that, a check that simply found *some* stat first would pass on
the broken page.

Second control worth having: **a port whose parts carry no `gn` must still lead
with its own correct axis** — a shield on HP, a cooler on cooling. If the fix
only ever leads with `gn`, it has replaced one fixed order with another.

*C1*
