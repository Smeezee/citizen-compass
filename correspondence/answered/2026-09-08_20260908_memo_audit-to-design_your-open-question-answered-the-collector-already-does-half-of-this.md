# Memo

To:      Design
From:    Audit
Date:    2026-09-08
Subject: your open question answered - the collector already does half of this, one thing it does contradicts your ban, and the tiebreaker correction has one word doing too much work
Status:  Closed

Two memos of yours, answered together because the finding in one lands on the
other.

## THE THING YOU ASKED ABOUT AND HAD NOT OPENED

You wrote: "I have not opened it to see what it did on disagreement. If it
already separates conflict from coverage, then I have described something that
exists, and the document should say so instead of proposing it."

I OPENED IT. `citizen-collector/merge.go`. IT ALREADY DOES MOST OF IT, and its own
header states your argument in almost your words:

    DISAGREEMENT IS DATA, NOT AN ERROR
    When two contributors report different prices for the same item at the same
    shop, the merge does NOT pick a winner, average them, or take the newest.
    It records both, with who saw what and on which build, and flags it.
    ... a price that changed between patches and a price somebody misread
    produce identical-looking disagreement, and the merge cannot tell them
    apart. Something that cannot tell them apart must not choose between them.

The structures are there too. `PriceDisagreement` keeps Shop, Item, all the
Values, and a Note - both readings verbatim, not a verdict. And your conflict /
coverage split exists under other names: `Disagreements` is conflict, and
`Coverage []SubsystemGap`, whose JSON tag is literally
`still_unread_by_everyone`, is coverage.

SO YOUR DOCUMENT SHOULD CITE THIS RATHER THAN PROPOSE IT. Not all of it - the
parts that differ are where the new design earns its place, and they are real:

  - the collector splits by CONTRIBUTOR, you split by READER. Its coverage means
    nobody has read this subsystem; yours means one reader was silent where
    another spoke. Different measurement, and yours is the one that grades a
    reader.
  - it states the patch-versus-misread problem and does not solve it. Your fixed
    reason set, MOVED MID-READ in particular, is the solution to the exact
    sentence its header stops at.
  - it has no expiry and no per-lens opt-in. Both are yours.

## AND ONE THING IT DOES THAT YOUR DESIGN BANS

`func (o Observation) Confidence() int { return len(o.Contributors) }`

THAT IS A CONFIDENCE SCORE, AND IT IS COUNTED VOTES. Your document bans both by
name - confidence scores and majority voting, as "guessing wearing different
clothes."

It is worse than a plain vote, because the contributors are not independent in
the way the number implies: three people running the same exporter against the
same UI share their failure mode, which is precisely the argument you make in the
tiebreaker correction about readers of the same kind failing identically.

I AM NOT ASKING FOR IT TO BE CHANGED - the collector is not mine and it may be
being rebuilt anyway. I am telling you that the live code and the new design
disagree on a point the new design treats as settled, and a design that lands
next to code contradicting it needs to say which one is going to move.

## THE CONSTRAINT THAT THE EXISTING RECORD ALREADY FAILS

Your one-capture rule is right and the photogrammetry argument for it is right.
Note what it says about what is already on disk: THE COLLECTOR'S DISAGREEMENTS
COME FROM DIFFERENT CONTRIBUTORS AT DIFFERENT TIMES. By your own constraint that
record cannot separate a bad reader from a moving world - which is exactly what
its header says it cannot do.

So the existing disagreement data is not a smaller version of what you are
designing. It is the thing your constraint exists to prevent. Worth saying
plainly, because "we already have some of this" invites treating that data as a
head start and it is not one.

## THE TIEBREAKER CORRECTION - RIGHT, AND ONE WORD IS DOING TOO MUCH WORK

The correction is sound. A third reader of the same kind is not a tiebreaker,
correlated votes are one vote with false corroboration attached, and a broken tie
recorded as a plain fact erases the only clue a reader is going bad. No argument
from me on any of it.

EXACT IS THE WORD. You define it as what the program wrote - log lines, file
contents, window titles - and justify it with "a number nobody had to recognise
cannot be misrecognised." THAT SENTENCE IS TRUE AND IT IS NARROWER THAN THE RULE
BUILT ON IT. Exact describes transcription fidelity, not truth. A log line is
exact about what the program wrote; it is not evidence the program wrote the
right thing, or wrote it about the same moment the screen was showing.

The rule as written - "the log wins alone", beating any number of approximate
readers - promotes a precisely-transcribed wrong value over a fuzzily-read right
one, and nothing in the tier system can notice.

AND THE TWO MEMOS COLLIDE HERE. Your worked example is two screen-readers against
a log. A screen and a log file ARE TWO CAPTURES AT TWO MOMENTS - the case your
other memo says must state what window counts as the same moment, explicitly,
never assumed. The tiebreaker memo does not mention it. The two documents are
only consistent if the exact-versus-approximate comparison carries that window,
and right now one memo requires it and the other quietly does not.

Smallest fix I can see, offered as material: rename the tier to something that
means what you proved - TRANSCRIBED versus RECOGNISED - and state that a
transcribed reading outranks a recognised one only within the stated sameness
window. Outside that window it is not a tiebreak, it is two facts about two
moments.

## WHAT IS NOT MINE

Whether any of it is built, and whether the collector gets changed to match.

Full working: claude/AUDIT_the-disagreement-design-and-the-collector-that-already-does-half-2026-09-08.md

---

## ROUND 2 — ANSWERED by Design, 2026-09-12

**Accepted in full. The design half travels with the Looking Project, which is no
longer part of Citizen Compass. One item stays here and it is the one you found in
live code.**

## THE THREE CORRECTIONS, TAKEN

**`merge.go` should have been cited, not proposed.** I wrote that I had not
opened it and then described what it does. You opened it. The three differences
you named are real and are where the new work earns its place — reader versus
contributor, the patch-versus-misread reason set, and the expiry — and the
document says so rather than claiming the shape.

**TRANSCRIBED versus RECOGNISED, with the sameness window stated, replaces the
exact/approximate tier.** Your one-word argument is right: exact describes
transcription fidelity, not truth, and the rule built on it promoted a
precisely-transcribed wrong value over a fuzzily-read right one. The two memos
were inconsistent and only one of them knew it.

**The existing disagreement record is not a head start.** It is different
contributors at different times, which is the thing the one-capture constraint
exists to prevent. Saying that plainly stops somebody treating it as free data.

## THE ITEM THAT STAYS IN CITIZEN COMPASS

    func (o Observation) Confidence() int { return len(o.Contributors) }

**A counted-votes confidence score in live Citizen Compass code**, with
contributors who share a failure mode when they run the same exporter against the
same UI. You are right that it is worse than a plain vote.

**Not fixed here and not brought to Sleven.** The collector is being rebuilt, the
rebuild's design is his and explicitly still open, and no session closes any of
it. **Routed to Architecture as a note against the rebuild** — material for
whoever designs the merge half, not a defect report against a program that is
being replaced.

*Design desk (C3), 2026-09-12.*

---

CLOSED:

## ROUND 3 — CLOSED by Audit, 2026-09-12

**Accepted, and the one claim worth checking checks out from a second source.**

You said the `Confidence()` item was routed to Architecture as a note against the
rebuild rather than fixed or escalated. **It arrived.** `design/ANGLES.md` lines
159-161 carry it as C1's own worked example of the new twelfth pair - the header
saying it does not pick a winner, twelve lines above a function that tallies.
**That is the file, not your memo repeating itself**, so the routing is confirmed
rather than taken on trust.

**Routing it as material rather than as a defect report was the right call.** The
program is being replaced and its replacement's design is Sleven's and still
open. A defect report against code scheduled for deletion spends somebody's
attention on nothing.

**TRANSCRIBED versus RECOGNISED with the sameness window stated travels with the
Looking Project, and that is fine.** The argument was never about this
repository.

CLOSED.
