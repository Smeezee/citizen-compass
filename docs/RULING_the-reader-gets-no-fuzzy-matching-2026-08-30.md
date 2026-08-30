# RULING — the screen reader gets no fuzzy matching. Sleven, 2026-08-30: "I agree with you on the fuzzy matching. Let's make the reader good."

    from    C1 (Cowork), 2026-08-30, recording Sleven's decision
    about   docs/workorder-collect-01-rev3.md §3c
    status  DECIDED. Do not re-open.

---

## WHAT THE SPEC SAID

> **§3c.** Match it against the known list — 7,728 items, ~200 commodities, 479
> shops, the location set — using **Levenshtein distance, accept at ≤ 20% of
> string length.** `Ar?light Pist?l` resolves to Arclight Pistol because nothing
> else is close.

**That is fuzzy matching, in the middle of the reader, in a project whose hard
rule 2 is "NO FUZZY MATCHING, anywhere, in anything. Exact equality or refuse."**

The rule exists because this project has been bitten twice. It was written to
apply everywhere and the spec quietly carved out an exception.

## THE RULING

**Hard no. The reader is made good enough that it does not need the crutch.**

An 80%-confidence character match resolved to a real item name by edit distance
is **a guess wearing a product name.** `Ar?light Pist?l` has one plausible
neighbour today. The day a second Arclight variant ships, it has two, and the
reader will pick one silently and be wrong at 3 in the morning with nobody
watching.

## WHAT REPLACES IT

**Nothing needs to.** The accuracy mechanism is already in the spec and it is
better than the fallback it was propping up:

- **The atlas is exact on a fixed font.** One UI font, a handful of sizes,
  white on dark, no anti-alias variation between frames. Pixel comparison
  against a labelled glyph is not probabilistic.
- **Twenty reads per row.** §3d: a row visible for two seconds at 10 fps is
  read twenty times. **Take the majority, and require the majority to be an
  EXACT vocabulary hit.**
- **A string that is not an exact hit is discarded.** §3c already ends with
  *"A string matching nothing is discarded, never guessed."* That sentence now
  applies to everything, not only to the residue.

**If the reader cannot produce an exact hit twenty times out of twenty, the
reader is not finished — and that is information, not an inconvenience.** A
fuzzy fallback would have hidden exactly that signal.

## THE ONE THING THIS COSTS, STATED HONESTLY

**Coverage drops.** Rows that a fuzzy match would have recovered are now
dropped. **That is the trade and Sleven took it knowingly**: fewer rows, and
every row correct.

**The dropped rows are not lost.** A read that fails is a read that can be
retried on the next pass, and the count of failures per screen is the reader's
own quality metric. **A reader that drops 40% of a shop is telling you
something a fuzzy one would have concealed.**

— C1, recording Sleven's decision
