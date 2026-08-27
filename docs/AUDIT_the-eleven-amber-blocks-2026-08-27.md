# AUDIT — the amber blocks on find, keybinds and index, one verdict each

**Written by Code, 2026-08-27. Q4 of `NEXT.md`.**
**`ORDER_the-disclosure-bar-2026-08-27.md`: "Audit every one against the rule
above before changing any of them, and record the verdict per block."**

The rule being applied, in the order's own words:

> **Collapse a block that EXPLAINS.**
> **Never collapse a block that WARNS, that reports an ERROR, or that states
> WHAT THE VISITOR IS LOOKING AT RIGHT NOW.**

---

## The count of eleven is not eleven explanation blocks

The inventory was taken by the amber treatment's own tokens, which is the right
way to find them — but the amber treatment is also worn by **buttons** and by
**runtime state notes**, and neither is an explanation.

Located by CSS carrying `#1A1206` in each source, then every element using
those classes:

| page | class | what it is | verdict |
|---|---|---|---|
| index | `.dvwarn` | "Reading this panel. The name in the left column is what Star Citizen calls that input…" | **COLLAPSE** — explanation, and named in the order's table |
| index | `.slotnote` | runtime text, `esc(slotNote)` — which stick is in which slot right now | **NEVER** — states what the visitor is looking at |
| index | `.slotswap` ×2 | *buttons*: "only one stick", "wrong stick? click to swap" | **NEVER** — a control, not a block. Collapsing it is meaningless |
| find | `.warn` | "Where these numbers come from. Star Citizen does not publish its prices. Players do…" | **COLLAPSE** — explanation, named in the order's table |
| find | `.homenote` | "26,657 price rows, read from a file. The invented items and shops that used to be here are gone…" | **SPLIT** — see below |
| keybinds | `.dvwarn` | same "Reading this panel" block as index | **COLLAPSE** |
| keybinds | `.note` | "Mouse buttons and the wheel are only read inside the dashed mouse box. Everywhere else the page scrolls normally." | **NEVER** — see below |
| keybinds | `.unattnote` | "Joystick axes — what the evidence actually supports. UNATTESTED is not rejected…" | **COLLAPSE** — named in the order's table |
| keybinds | `.slotnote` | as index | **NEVER** |
| keybinds | `.slotswap` ×2 | as index | **NEVER** |

**So: 4 collapse, 1 split, 6 never.** Not eleven explanation blocks — eleven
elements wearing the amber treatment, of which five are buttons or live state.

## The two judgement calls, argued rather than asserted

**`keybinds .note` — the mouse box. NEVER, and this one is not in the order's
table.** It reads as an explanation and it is not: it tells a person why the
page will not capture the input they are pressing *while they are pressing it*.
That is the same shape as the `Ctrl+Alt+Del` and `Windows key` notices the
order lists as NEVER — "they explain why a control will not work while the
person is trying to use it". A visitor who has to click to discover why their
mouse wheel did nothing has been failed by the layout.

**`find .homenote` — SPLIT, following the loadout page's own precedent.** It
opens with a count of the price rows and then explains what was removed and
why. The count is the answer to *is this page showing me everything*; the rest
explains. Same treatment as `Showing 14 of 15 weapon mounts`: **the count stays
in the sentence, the reasoning collapses behind it.**

## What is NOT in this audit

`download.html` carries no amber block at all — its antivirus warning uses a
different treatment. It was listed in the order's table as NEVER, and it is
NEVER, but anyone sweeping "all amber blocks" would never have reached it. Said
here so the gap is recorded rather than discovered.

`.trip` blocks on the loadout page are C1's, and three of them are still to be
converted — C1 said so itself.

---

*Code, 2026-08-27. Verdicts recorded before any block was touched.*

---

## CORRECTION, made while implementing — the amber inventory is not the right list

Two errors in the table above, both found by opening the code rather than the
stylesheet, and both in the same direction: **an inventory taken by the amber
treatment is not an inventory of explanation blocks.**

**`keybinds .unattnote` is NOT the "UNATTESTED is not rejected" block.** It is an
empty container, `id="kbbunatt"`, filled at runtime with a note about the axis
the person **just captured** (`unattestedNote  /* {input, note} for the last
captured axis */`). That is live state about what the visitor is doing right
now. **NEVER**, and for a stronger reason than the table gave.

**The block the order actually names is `.dofnote`, and it is not amber at all.**
Plain muted text, `#93A7B6`, so an inventory located by `#1A1206` never sees it.
It EXPLAINS what a label means. **COLLAPSED**, as the order's table says.

So the corrected verdicts are **4 collapse, 1 split, 6 never** — the same
counts, but `.dofnote` takes `.unattnote`'s place in the collapse column.

**Worth carrying forward:** the order's own inventory method (locate by the
amber tokens) both over-counts and under-counts. It swept in two buttons and a
live-state container, and it missed a block the order itself names. Anyone
extending this pattern should read what a block SAYS, not what colour it is.

## What was built

    find     "Where these numbers come from"   -> bar, stamp PLAYER-REPORTED
    find     the home counts                    -> SPLIT, counts stay visible
    keybinds "What UNATTESTED means"            -> bar, stamp UNATTESTED != REJECTED
    keybinds "Reading this panel"               -> bar, stamp 2 LINES PER INPUT
    index    "Reading this panel"               -> bar, same

One implementation: `testing/_src/_disc.css`, C1's rules extracted verbatim and
substituted into all three pages by the build at a `/* CC_DISC_CSS */` marker.
The build refuses if a page asks for it and the file is missing, and refuses if
the file exists and no page asks — the second because that is how a shared
implementation quietly becomes an unused one while pages grow copies again.

**Not verifiable by the check, and said rather than glossed:** the two "Reading
this panel" bars render only when a device panel is on screen, which needs a
connected gamepad. `_verify_disclosure.mjs` sees 7 bars, not 9. Those two were
converted from the same source text as each other and reviewed by eye; they have
not been rendered in a browser by me.
