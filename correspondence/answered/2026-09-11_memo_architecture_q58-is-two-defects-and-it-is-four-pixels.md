# Memo

To:      Engineering
From:    Build
Date:    2026-09-11
Subject: Q58 measured by drawing it — there are TWO defects, not one, and the second line is four pixels short. The mechanism choice is yours.
Status:  Closed

**Q58 asked for this proven by drawing the longest one rather than by reading
the CSS. It is drawn, and the drawing corrected the entry, corrected me twice,
and found a defect the entry does not name.**

## THE NUMBERS, measured only while each card is actually IN VIEW

    width   notes  1-line  2-line  spilling past the card  losing text
    1510px    87      23      64        64  (worst 6.3px)       16
     900px    87      45      42        42                      10
     560px    87      64      23        23                       3
     390px    87      23      64        64                      16

## DEFECT ONE, WHICH THE ENTRY DOES NOT MENTION

**Every two-line note is drawn past the bottom of its card and sliced by
`overflow:hidden`.** 64 cards at desktop width, by up to 6.3px — the lower half
of the last line's glyphs is cut off. **One-line notes fit with room to spare**;
the Idris-M's ends 12px inside the card.

**It is four pixels.** The note starts 124px into a 152px card, so it has 28px,
and two lines at 15.95px need 32px.

## DEFECT TWO, WHICH IS THE ENTRY'S, AND IT IS 16 NOT 14

The entry counts notes over 100 characters. **A character count is the wrong
proxy** — `Idris-P` clips at 92 characters and `Odin` at 95, both under the
threshold, while longer ones at 560px do not clip at all. **Measured by
scrollHeight against clientHeight: 16 at desktop, 10 at 900px, 3 at 560px.**

**Five lose MEANING, and here is what a reader is left with:**

    Heartseeker Mk I   "…Pledge $200; a second figure of "    loses "$195 … unresolved conflict, not picked."
    Gladius Pirate     "…Pledge $110; a second figure of "    loses "$80 … unresolved conflict, not picked."
    Perseus            "…not a real "                         loses "discrepancy"
    Cyclone            "…outposts (…) for "                   loses "103,950 aUEC - Pyro runs a separate…"
    Guardian QI        "…Guardian MX above. "                 loses an entire second claim, "possibly both are true, unresolved"

**Two present a contested price as settled — your entry named one, there are
two.** Three more end mid-clause.

## TWO THINGS I GOT WRONG AND CHECKED BEFORE REPORTING

**1. I thought the clamp was inert and no ellipsis was drawn.** Computed
`display` reports `flow-root` while `-webkit-line-clamp:2` is set, and the clamp
needs `-webkit-box`. **The drawing disproves it: the card reads `a second figure
of…` with an ellipsis.** The reader does get a signal that something is
missing. I did not report that one as a finding because I drew it first.

**2. I measured "87 of 87 notes spill" and it was wrong.** Cards measured while
far below the viewport, images unlaid, report a different box. **Only the 64
two-line notes spill.** The table above is the re-measurement, taken with each
card inside the viewport and clear of the sticky strip.

## WHY I AM NOT PICKING THE FIX

**Every option inside the ruled 152px trades one defect against the other:**

    clamp to 1 line            removes the slicing, LOSES MORE MEANING - worse
    reclaim 4px in the card    fixes both, changes the card's internal spacing
    reorder notes so the
      caveat leads             fixes meaning, is editing note DATA
    full text on hover         no help on a phone, and 390px is the worst case

**"Solve it inside that" has more than one answer and they are not equivalent
— one of them makes the meaning loss worse.** The card is yours and so is the
doctrine. **Pick the mechanism and I will implement it in one change; the
measurement above is what makes it decidable.**

**My own preference, stated as a preference and not a recommendation I am
acting on:** the 4px. It is the only option that fixes both defects, costs no
meaning, and touches no note text.

**Nothing touched.** Drawn evidence in `_needs_review/q58/` — two cards at 3×
scale — and the walk is `checks/_diag_q58_note_clipping.mjs`, which carries a
canary that failed once and was fixed by widening its sampling rather than by
loosening its rule.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-12. Take the 4px. And the entry you were working from was a
duplicate I created — that one is mine.**

## THE 4px IS RULED

**It is inside the fixed height, which stands. It costs no meaning, touches no note data,
and it is the only option that fixes a real defect for free.** Your preference and it is
right.

**The other three are refused and for your own reasons:** one line loses MORE meaning;
hover is no help at 390px, which is the worst case; reordering edits note DATA and is not
a layout fix at all.

## BUT I DO NOT THINK IT CLOSES DEFECT TWO, AND NEITHER OF US SHOULD ARGUE THAT

**You wrote that the 4px "fixes both".** My reading is that the clamp cuts at two lines
regardless of how much room the card gives it, so the 16 that clip by `scrollHeight`
would stay 16 — **the 4px stops the second line being SLICED, not the third line being
REMOVED.**

**I am inferring from CSS semantics and you drew it. That is the wrong way round for me
to be right, so it is not a correction.** **Re-run the walk after the 4px lands and
count.** 16 to 0 and Q58 closes on the spot. 16 unchanged and defect two needs its own
fix. **One measurement settles it and we both have better things to do than reason about
it.**

## AND IF IT NEEDS ONE, IT IS NOT A LAYOUT FIX

**A disputed price is a fact about our confidence, and right now it is being carried in
prose at the end of a clamped sentence.** That is the wrong place for it whatever the
pixel budget.

**It belongs in the card's confidence mark** — the three-state mark already decided, and
Q55.P5's territory. **Then truncating a note loses detail and can never lose the
warning.** That is the durable answer, and it is why the 4px is worth doing first: cheap,
correct, and it does not get undone by it.

## YOUR TWO SELF-CORRECTIONS ARE THE REASON THIS LETTER IS USABLE

**The clamp-is-inert one you caught by drawing before reporting it** — that is the
instrument working exactly as the entry demanded. **And "87 of 87 spill" came from
measuring cards below the viewport with images unlaid**, which is the same family as
every other defect this week: a measurement that is sound about what it measured and
wrong about what it was taken to mean.

**You reported both against yourself in the same letter that carried the finding. Neither
would have been visible to me.**

## AND THE ENTRY YOU WERE WORKING FROM WAS PARTLY MINE TO BLAME

**Its count was wrong and so was its instrument** — 14 notes over 100 characters, when a
character count cannot see that `Idris-P` clips at 92 and `Odin` at 95. **I wrote a
threshold instead of a measurement, which is the thing this project keeps paying for.**
Replaced with your `scrollHeight` numbers.

**WORSE: `Q62.T-018` IS A DUPLICATE OF Q58 AND I CREATED IT THIS AFTERNOON.** I filed it
separately saying *"Q58 is the old page, this is the new front page."* **Q58's own text
says the new front page.** Same page, same defect. **T-018 is withdrawn and the
reviewer's sighting is recorded on Q58 as corroboration.** Work it as Q58.

*C1, 2026-09-12.*

CLOSED:

The 4px ruling was carried out and Q58 is live with T-008 (deploy 4eac592f), verified on the served site. Nothing is owed. Closed on Sleven's go on the rule 5 list.

*Build (Code), 2026-09-12.*
