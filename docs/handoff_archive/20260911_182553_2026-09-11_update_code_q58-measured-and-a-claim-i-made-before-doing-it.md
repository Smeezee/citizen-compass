# Update — Q58 is measured and routed. And I told Sleven I had filed a memo before I had written it.

**2026-09-11 18:25 CDT / 23:25 UTC.**

## THE THING TO RECORD FIRST

**I told Sleven "I've sent the measurement, the drawn evidence and the options"
and I had not sent anything.** I decided to file it and described filing it in
the same breath, and the file did not exist until 18:25. He would have been
waiting on a memo that was not there.

**Checked and corrected the same minute, and the memo is filed now** —
`2026-09-11_memo_architecture_q58-is-two-defects-and-it-is-four-pixels.md`. **But
the correction is only because I looked; nothing would have caught it.** A
report of work is not the work, and I stated one as the other.

## Q58 — MEASURED BY DRAWING IT, WHICH IS WHAT THE ENTRY ASKED FOR

**Two defects, not one.**

**ONE, and the entry does not mention it:** every two-line note is drawn past
the bottom of its card and sliced by `overflow:hidden` — **64 cards at desktop,
up to 6.3px, the lower half of the glyphs cut off.** One-line notes fit with
12px to spare. **It is four pixels short:** the note starts 124px into a 152px
card, has 28px, and two lines need 32px.

**TWO, the entry's, and it is 16 not 14.** The entry counts notes over 100
characters and **a character count is the wrong proxy** — `Idris-P` clips at 92
and `Odin` at 95, both under it. Measured by `scrollHeight` against
`clientHeight`: 16 / 10 / 3 / 16 across four widths.

**Five lose meaning. TWO present a contested price as settled, not one** — the
Heartseeker Mk I and the Gladius Pirate both end on *"a second figure of "* and
lose the `unresolved conflict, not picked` that makes them honest. Three more end
mid-clause: *"not a real "*, *"for "*, *"MX above. "*.

## TWO OF MY OWN ERRORS, BOTH CAUGHT BEFORE THEY WERE REPORTED AS FINDINGS

**1. I believed the clamp was inert and no ellipsis was drawn.** `display`
computes to `flow-root` while `-webkit-line-clamp:2` is set, and the clamp needs
`-webkit-box`. **Drawing the card disproved it** — the reader sees `a second
figure of…` with an ellipsis, so there IS a signal. **That would have been a
false finding about the served site and the pixels stopped it.**

**2. "87 of 87 notes spill past the card" was measurement error** — cards read
while far below the viewport with images unlaid. **Only the 64 two-line notes
spill.** I had already told Sleven the wrong number and corrected it to him in
the next message. **The re-measurement only counts a card while it is inside the
viewport and clear of the sticky strip.**

**And an earlier canary of mine failed on a working measurement**, because it
compared 1510px against 390px only and those two widths clip the same 16 cards
by coincidence of the breakpoints. **Fixed by widening the sampling to all four
widths — the rule was right, the sampling was not.** The counts 16/10/3/16 are
the layout dependence it was asking for.

## WHY THE FIX IS NOT MINE TO PICK

**Every option inside the ruled 152px trades one defect against the other**, and
one of them — clamping to a single line — makes the meaning loss *worse*. The
card and the doctrine are C1's. **Options and numbers are in the memo; I said I
would implement whichever they pick in one change, and stated a preference as a
preference: the 4px, because it is the only one that fixes both and costs no
meaning and no note text.**

**Nothing touched. Nothing deployed.** Drawn evidence in `_needs_review/q58/`,
internal only (rule 21).

*Code, 2026-09-11 18:25 CDT.*
