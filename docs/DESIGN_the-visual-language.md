# DESIGN — the visual language. LIVING DOCUMENT. Add to it; do not fork it.

    what     The site's shared visual and layout vocabulary, and a running list of
             places it should replace what is there now.
    status   LIVING. When something is found, it goes in section 3 with what is
             wrong, what it becomes, and where else it applies.
    why      Sleven, 2026-08-23: "it's these type of things that I need help
             looking for and locating, so we can utilize making the entire site
             more visually appealing and usable."
    rule     This is a standing job, not a one-off pass. Nobody has to be asked
             to look.

---

## 1. What is settled

**1a. THE ROW NEVER CRUSHES ITS OWN NAME. Approved 2026-08-23, applies site-wide.**

Sleven, on seeing a component list at narrow width: *"there's empty space that
could be filled up... make it skinnier, but hold the same length."*

    The name holds ONE line. It truncates politely; it never wraps and never
    stacks.
    When the row runs out of width, the DATA drops to its own line underneath
    and uses the space that was going begging.

**This is not a ship-page fix. It is how every list on the site behaves** — the
component picker, the ship list, FIND's results, the keybind tables, anywhere a
label and some figures share a row. **Sleven's own scoping:** the reflow goes
everywhere; the pip graphics go only where they earn it.

**1b. A NUMBER GETS A GRAPHIC ONLY WHEN IT HAS A REAL RANGE.**

Three inputs, always: **a value, a range, and a sentence naming the range.**
Nothing about ships is baked in — a price behaves exactly like a DPS figure.

**No range, no graphic.** It falls back to the plain number. **A bar against an
invented scale would be the most confident lie on the page.**

**1c. THE VALUE IS CARRIED BY POSITION OR COUNT, NEVER BY COLOUR.**

How far the bar runs, how many pips are lit. Recolour it with the colour picker,
dim it to Blackout, print it in grey — it still reads. This satisfies H1g's
colourblind requirement by construction rather than by remembering.

**1d. THE NUMBER IS NEVER INSIDE THE GRAPHIC.**

Learned by getting it wrong: radial gauges with the value in the middle were
rejected because shrinking the ring shrinks the text. **Text stays ordinary text
at ordinary size; the graphic sits beside it and carries no text of its own.**
That is the only reason the compact forms survive being made small.

## 2. The forms, and what each is for

    PIPS        5 blocks, countable          dense lists. Degrades best - at half
                                             size still five countable blocks.
    BAR         position in a range, with a  where the row has room and precision
                pale tick for what is fitted matters
    BULLET      position + comparison mark   between the two, narrower than the bar
    RING        a share of a known whole     ONLY where the whole is real. Rings
                                             read worse than bars for comparison.
    SEG RING    one tick per real object     small countable sets you can verify
    PLAIN       no range exists              the honest fallback

## 3. FOUND — candidates, oldest first. ADD TO THIS.

**Each entry: what is wrong, what it becomes, where else it applies.**

**3a. Every list row on the site, at narrow width.** Names wrap and stack while
space sits empty below. → 1a. **Applies: component picker, ship list, FIND
results, keybind tables, Where-to-buy.**

**3b. `EVERYTHING THAT MOVES` is sixteen boxes of plain text.** Every tile has
equal visual weight, so nothing leads and a visitor reads all sixteen or none.
And the CIG-vs-computed distinction — the thing the whole honesty layer rests on
— is carried by a small badge that is easy to miss. → stat + compact graphic
against the fleet; make provenance structural rather than a badge.

**3c. The orange footnote paragraph at the foot of the ship page.** A wall of
small text carrying real information nobody will read at that length. → needs a
form, not a paragraph.

**3d. The left column's group headings** (`WEAPONS`, `SHIELDS`, `POWER &
COOLING`) are plain text with no hierarchy, so a 117-port hull reads as one long
undifferentiated list. → grouping needs visual weight, and probably a count.

**3e. The ship selector is a native `<select>`.** On a site whose whole pitch is
that it looks good, the single most-used control is the browser default. → this
is also where Fleetyards' card grid is genuinely better than ours.

**3f. The tab row** (`Loadout / Engineering / Liveries / Where to buy / Specs`)
is plain text with an underline. Functional, invisible, and it is the page's
primary navigation.

**3g. The `?` help markers** are small and easy to miss, which defeats the point
of writing plain-language explanations at all.

## 3z. HELD — the first batch, and why it is waiting

**Sleven, 2026-08-23: hold the order, remember it, check periodically.**

**The batch: 3a (row reflow) + 3b (stat tiles) + 3d (group headings).** They are
one page and one design language; a language changes as a set or it does not
change at all.

**Why held:** Code is mid-run on the errata queue — E6, E8, E9 and E10 remain —
and every one of them writes `testing/_src/loadout.src.html` and
`cc_viewer.js`, which is exactly where this batch lands. **Rule 14, one writer
per artifact.** This project has been bitten by that five times and does not
need a sixth.

**The trigger to release it:** Code records E6, E8, E9 and E10 in the ledger and
the run is quiet. C1 holds a scheduled check; if that check is ever lost, this
paragraph is the record.

**Use the wait.** Build the demos for 3b and 3d now, so the order is proven
before it is handed over. That is section 4's method, applied to itself.

## 4. Standing instruction to C1

**Look for these without being asked.** When Sleven sends a screenshot, read it
for layout and legibility as well as for the defect he reported. When a page is
built, ask what it looks like at 400px and at Blackout. **Add findings here with
the same three parts, and propose them in batches rather than one at a time** —
a design language changes as a set or it does not change at all.

**And build the demo before writing the order.** Three passes on the compact
stat happened because Sleven could click each one; none of it would have survived
being described in prose.
