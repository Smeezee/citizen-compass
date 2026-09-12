# Angles — Citizen Compass

**THE METHOD IS NOT IN THIS FILE. IT MOVED UP, NOT ACROSS.**

Sleven's sixty-angles method, its one test, and the general checklists — a
dataset, a reader, a page — live in the company folder at **`CCDesk-logs/ANGLES.md`**,
because the method is his, it predates this site, and more than one project uses
it now. **Read that first. Anything here is in addition to it, never instead of
it.**

Moved 2026-09-08 on his order. Nothing was deleted. The reasoning that used to
sit here is in the company copy word for word, and a second copy in this
repository would drift — which is what this project has already paid for three
times with its state documents.

> **Why a pointer and not a copy.** The next project that wants the method would
> copy this file, and then there would be three. The company folder is not this
> project; it serves all of them, which is exactly what the method is.

---

## What this file is now

**The extra questions Citizen Compass asks on top of the company lists.** Every
one of them exists because of something specific to this project — its data, its
sources, or a mistake it has already made. A question that would apply to any
project belongs upstairs, not here.

**Any desk may add. Nothing is removed without saying why.** Same rule as the
company file.

---

## One of our pages — on top of the company `A page` list

 1. **Does it show which patch the data was verified against?** Hard rule 20 says
    every row carries `last_verified_patch`, and as of 2026-09-08 every one of
    the 254 ship rows carries nothing. A page that does not surface that is
    hiding a gap the whole project is built to admit.
 2. **Colour drained.** It is on the company list too, and it matters more here
    than in most places, because **we tell people what things are by colouring
    them.** Drain it and check the page still says what it means.
 3. **Is our different way actually better, or only different?** Aimed at the
    instruction itself. See the rider below.
 4. **Does the page name the manufacturer, or only the group header it scrolled
    past?** Sleven hit this on the new front page while gathering data.
 5. **Draw the longest note the data contains, in the real card.** A clamp that
    truncates can reverse a meaning — the Heartseeker's note loses the words
    marking a price conflict as *disputed*, and prints a contested number as
    settled.
 6. **Can every tab be reached at phone width?** The credits tab exists because
    of hard rule 9, and it is the one that falls off the edge at 451px.

## Somebody else's page — on top of the company lists

 1. What does it do that we do not?
 2. What does it refuse to do — gap, or decision?
 3. **Is its data right? Check its numbers against ours and say who is wrong.**
 4. Where does its data come from, and how old is the oldest thing on the page?
 5. How many actions to the single most common task?
 6. **What happens to it when the game patches?**
 7. What does it cost them to run, and what pays for that?
 8. What do its own users complain about, in their own words?
 9. Who is it for, and how can you tell in one second?

## Our own data — on top of the company `A dataset` list

 1. **Which rows have no hull key?** 35 ships as of 2026-09-08, and it is the
    join gap this project keeps rediscovering under different names.
 2. **Is a real zero being read as a missing value?** `if not x` treats 0 as
    blank, and it turned 121 real cargo values into holes.
 3. **Is the source CIG, or somebody reading CIG?** A community aggregator does
    not overwrite the maker's own number, however current its patch stamp looks.
 4. **Are two different products being compared as one?** The Retaliator against
    the Retaliator-Bomber looked like a $100 price disagreement and was not.

## Standing riders specific to this project

**Theirs first, ours second.** On the company list, and it is here because this
desk has already been caught by it: it claimed a differentiator that Star Binder
had shipped years earlier — `claude/CIC_survey-keybind-tools-and-the-gap-2026-09-06.md`.

**Ask what the set you counted actually contains, before you explain a gap.**
Four times in one week a number came from the wrong population and was explained
instead of interrogated — the payout count, the "forty questions", the 75
price-less ships, and the first reading of the frame grader.

**THE FRONT PAGE'S DATA IS A NARROW PROJECTION. DO NOT MEASURE IT AND REPORT THE
PROJECT.** His words, 2026-09-12, and it is the specific form of the rider below —
here as its own line because the general version had been on this list for four
days and did not stop any of the five errors it names.

    the width and height gap      counted the front page's data. LOADOUT_SHIPS
                                  carries dim for all 318 ships.
    the paint gap                 counted the front page. 924 paint records
                                  with names, manufacturers and ship tags
                                  already exist.
    35 hull-less rows vs 34       two surfaces, one folded card between them
    P20 five times too big        counted cards, not records
    Q58's sixteen notes           counted characters, not drawn text

**And the reason it recurs is not carelessness: the front page is the surface
everyone can see, so it is the surface every measurement reaches for.** The
projection is the convenient thing to count. **Name the surface in the number,
every time — "253 cards" and "318 ships" are both true and they are not the same
measurement.**

**A paginated sweep is not finished until it is reconciled against a known list.**
Added 2026-09-12, and it was caught rather than theorised: sweeping RSI's store
by `sortField=weight` returned duplicate pages and silently dropped 38 of 253
ships. The page count looked right. **Alphabetical paginated cleanly.** The
defect is invisible without a list to check against — so the reconciliation is
the measurement, not a formality after it.

**Split by day or by session, never at random.** Frames captured seconds apart
are near-copies; a random split scores a reader on pictures it has already seen.
Measured 2026-09-08: random 96.0%, split by day 82.4%. **The honest number is
always the smaller one**, and this trap is available in every future measurement
on this material.

## Pairs — a different unit, and not an angle list

**Added by Audit, 2026-09-08; taken by Design, 2026-09-12.**

Every list above examines ONE THING from many positions. **This one examines
PAIRS**, and it is here because three collisions in a single day were invisible
from either document alone and obvious with both open. C1's summary: *"None of
them was a defect in either document. All three were the absence of somebody
reading both at once."*

Two questions per pair, and **the second is the one that gets skipped**:

    1  do these two still agree?
    2  if one of them is right, is it right about the thing that matters?

Question 2 catches a rule that is correct, followed, and policing the wrong half.

    CLAUDE.md               x  the repository
    docs/CURRENT-STATE      x  OWNERS.md
    docs/CURRENT-STATE      x  claude/CURRENT-STATE
    OWNERS.md               x  the repository
    LIVE.md                 x  the public site
    NEXT.md                 x  correspondence/answered
    a ruling or an order    x  the thing it ruled on
    a doctrine section      x  the measurement it assumes
    correspondence/README   x  the router and the checker
    ARCHITECTURE_DECISIONS  x  any new design
    a document              x  its own correction elsewhere
    a file's own HEADER     x  what the file actually does

**Twelve, not sixty, and every one earned by something that has already gone
wrong.** The file's own rule applies: a pair joins only with an incident behind
it.

**The twelfth is C1's, 2026-09-12, and it has three live examples on the day it
was added.** A header states what a file does; nothing checks it, so the file and
its own claim drift apart in the same document.

    citizen-collector/merge.go    header: "it does NOT pick a winner, average
                                  them, or take the newest". Twelve lines later
                                  it ships Confidence() = len(Contributors),
                                  which is a tally.
    checks/_verify_              docstring: "Status: ANSWERED with nothing under
    correspondence.py            an ANSWERS: line". The code requires ANSWERS:
                                  for EVERYTHING in answered/ and treats
                                  answered, closed and done alike. The code is
                                  broader than its own docstring.
    the help design              its premise sentence about third-party help
                                  was withdrawn the same week the design was
                                  written, by somebody reading the sites.

**Question 1 passes on all three** — a header and its code do not contradict each
other until somebody reads both. **Only question 2 finds them**, and the reader
has to be looking at behaviour rather than at prose.

**The eleventh is Design's, 2026-09-12.**
`FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08` was
corrected in a second document and left standing in the first with its wrong
sentence; another desk read the standing one and tripped on it. **Question 1
passes on that pair** — a document and its correction do not contradict each
other. Only question 2 finds it.
