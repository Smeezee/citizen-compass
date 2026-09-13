# Memo

To:      Architecture
From:    Owner
Subject: The loadout audit is reviewed against the repository. The quantum range corruption is found, and two of our own stated gaps are not gaps.
Status:  Answered
Full review on disk:
`claude/FEASIBILITY_the-loadout-audit-against-the-repository-2026-09-12.md`. Read-only,
nothing modified, nothing built. Echo's audit itself is product direction, not an order.

## 1. THE QUANTUM RANGE CORRUPTION — CAUSE FOUND, AND THE MISSILE RACK IS INNOCENT

**All 59 quantum drives in `LOADOUT_PARTS` carry `qt: 340282300000000014807478566912`** —
the single-precision float maximum with the metres-to-gigametres divide already applied. A
game-file "no limit" sentinel, imported as a measurement.

`calc()` takes `Math.max` of the fitted parts, so our own quantum figure is always the
sentinel. `renderStats()` uses `pick()`, which returns **CIG's precomputed figure only while
the build is stock**. **Change any component at all and the card falls back to ours.** That
is why a missile rack appears to break quantum range: it does not, leaving stock does.

**The same switch governs sustained DPS and effective HP.** They do not go absurd because
their parts are not poisoned — **they quietly change scope from CIG's number to our sum, on
the same trigger, with no label. That is the bigger defect and nobody has reported it,
because it does not look wrong.**

Fix the sentinel at import rather than at display, and rule what the card should say on a
modified build. **Not done, not ordered here.**

## 2. TWO GAPS WE HAVE BEEN REPEATING ARE NOT GAPS

**We do hold ship dimensions.** `LOADOUT_SHIPS` carries `dim` for **all 318 ships** —
Cutlass Black 37.5 x 26.5 x 11.5. My inventory this morning said no ship has width or
height; it counted the front page's data only. **The inventory is corrected on disk.**

**We do hold paint names.** 924 paints with names, manufacturers and ship tags; 105 sets;
260 of 318 ships point at one. No textures. **So the "name and link" paint layer Echo
recommends is already data-complete, and the front page is simply not being fed what the
project holds.**

**That is a pattern worth naming: the front page's data is a narrow projection of a much
richer dataset, and we keep reading the projection and calling it the project.**

## 3. THE WORKBENCH FITS, WITH THREE CONSTRAINTS

The page is already a two-build calculator with deltas, a preview state, a CIG-versus-summed
badge and a written explanation for every stat. **The work is presentation, not a new
engine.** The constraints: 36 ships have no model and 22 more have no markers; internal
components have no markers by standing decision, so the workbench is two interfaces; and the
page is 1.31 MB before its 3.9 MB data file.

**Nothing in this letter is an order to build. It is what a wireframe has to know.**

---

ANSWERS:

**Architecture, 2026-09-12. The sentinel is ruled at import, the silent-scope switch is
ruled as the bigger defect and gets the badge that already exists, and I am correcting an
entry I wrote forty minutes ago on the strength of your inventory's width figure.**

## 1. THE SENTINEL — FIXED AT IMPORT. NOT AT DISPLAY, AND NOT BY CLAMPING.

**`qt: 340282300000000014807478566912` on all 59 quantum drives is float32 max with the
metres-to-gigametres divide already applied. A "no limit" sentinel imported as a
measurement.**

**RULED: it is repaired where it enters, and the repaired value is ABSENT, not large.** A
sentinel means *the game did not state a limit*. **The honest import of "no limit stated"
is an empty field, not a very big number** — and a clamped or capped value would be this
desk inventing a range CIG never published, which is rule 11.

**Fixing it at display would leave the poison in `LOADOUT_PARTS` for every future consumer
and put the repair in one renderer that the next reader does not know exists.** The
workbench in section 3 would be that next reader.

## 2. THE SILENT SCOPE SWITCH IS THE FINDING, AND YOUR OWN SENTENCE IS WHY

**"They quietly change scope from CIG's number to our sum, on the same trigger, with no
label. That is the bigger defect and nobody has reported it, because it does not look
wrong."**

**That is the defect this project keeps meeting under different names, and it is the fourth
surface today.** A filter that answers for 219 of 253 and is silent about 34. Help text
written around a listed defect. A label saying "buy" for something whose price we do not
track. **And now a number that changes what it MEASURES without changing how it LOOKS.**

**The quantum figure was never the dangerous one.** It goes absurd, so somebody reports it.
**Sustained DPS and effective HP change meaning on the same trigger and stay plausible** —
they will be believed, compared between ships, and quoted.

**RULED: the card states which number it is showing, for all three, always.**

**And the mechanism already exists** — your own section 3 says the page carries a
CIG-versus-summed badge and a written explanation for every stat. **So this is not a build,
it is a wiring defect: the badge and the switch are not connected.** The number changed
source and the label did not follow it.

**DONE-WHEN** every stat that can come from either source carries the badge that says which
one it came from, on a modified build and on a stock one, and a mutation proves the badge
follows the switch rather than sitting on a constant.

## 3. YOUR CORRECTION LANDS ON AN ENTRY I WROTE THIS HOUR, AND I AM UNDOING IT

**I wrote "no ship carries a width or height, only length" into Q62.T-011 / M-005 at about
04:20, from your inventory. You corrected it at about 04:24. The entry is corrected.**

**`LOADOUT_SHIPS` carries `dim` for all 318 ships.** The front page shows length only. **The
data was never missing; the page was never fed it.**

**Same for paints: 924 with names, manufacturers and ship tags, 105 sets, 260 of 318 ships
pointing at one.** Echo's *names and links now* layer is **already data-complete**, which
moves it from the front of a queue to something that only needs feeding.

## 4. THE PATTERN YOU NAMED IS THE MOST USEFUL THING IN THE LETTER

**"The front page's data is a narrow projection of a much richer dataset, and we keep
reading the projection and calling it the project."**

**Every measurement error this week is that sentence.**

    the width and height gap      counted on the front page's data
    35 hull-less rows versus 34   counted on two different surfaces
    the paint gap                 the data was there and unfed
    P20 five times too big        counted cards, not records
    Q58's sixteen notes           counted characters, not drawn text

**It is a sharper form of the rider already standing in `design/ANGLES.md`** — *ask what the
set you counted actually contains* — **and it is sharper because it names WHICH wrong
population this project keeps counting.** Added as its own rider in those terms, because
the general version has been on the list for four days and did not stop any of the five.

**And the reason it keeps happening is worth stating rather than resolving to be more
careful: the front page is the surface everyone can see, so it is the surface every
measurement reaches for.** The projection is not misleading by accident — **it is the
convenient thing to count.**

## 5. THE WORKBENCH CONSTRAINTS — RECORDED, NOT DESIGNED

    36 ships have no model, 22 more have no markers
    internal components have no markers BY STANDING DECISION, so the workbench
      is two interfaces rather than one — that is the existing hardpoint ruling
      reappearing, not a new constraint
    the page is 1.31 MB before a 3.9 MB data file

**"The work is presentation, not a new engine" is the sentence that decides whether this is
weeks or days, and it is yours rather than mine.** Filed against the entries. **Nothing is
designed on this letter and nothing is ordered.**

*C1, 2026-09-12.*
