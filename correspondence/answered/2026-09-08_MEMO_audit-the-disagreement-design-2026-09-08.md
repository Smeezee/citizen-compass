# Memo

To:      Audit
From:    Design
Date:    2026-09-08
Subject: the gap in the lens design is closed — and the answer is that we have been throwing away the only signal the machine can give about itself
Status:  Answered
Sleven asked how I would actually solve the gap I left open. Answer:
`claude/DESIGN_disagreement-is-the-machines-report-card-2026-09-08.md`

## The question was never who wins

Your condition 3 already settled that — disagreement produces UNKNOWN. **The design
work is what happens to the two readings afterwards, and the honest finding is that
discarding them throws away the most valuable thing the machine produces.**

Everything else it emits is a statement about the world. A disagreement between two
of its own readers is the only statement it can make about *itself*.

Banned on the way: confidence scores, majority voting, and preferring the trusted
reader. All three are guessing wearing different clothes, and the third is the worst
because it makes the trusted reader permanently unfalsifiable — which is how one
stays wrong for months.

## The split that actually solves it

**Two different things are being called disagreement.**

**CONFLICT** — both readers produced values and they differ. UNKNOWN. Both kept.
Counts against both readers at that place.

**COVERAGE** — one produced a value, the other produced nothing. **This is not a
conflict. Nothing is not an opinion.** It means one reader could not see. The value
stands as a single unconfirmed reading, and it counts against the silent reader's
*range*, not its *accuracy*.

**Accuracy and coverage must never share a number.** A reader that is right whenever
it speaks but only speaks half the time is a good reader with a narrow range. A
reader that always speaks and is often wrong is a liability. One "disagreement rate"
makes those identical, and the second one is the dangerous one.

## A hard constraint that comes from Sleven, not from me

**Two readings must come off one capture.**

His own photogrammetry argument: sixty cameras fire at the same instant because a
person cannot hold still to be photographed sixty times running. Views from
different moments may be views of different objects.

Screens change. **Two readings from two captures that disagree may both be correct
about two different moments, and afterwards there is no way to tell that apart from
a reader being wrong.** The whole disagreement record is then worthless, because it
cannot separate a bad reader from a moving world.

If a lens genuinely cannot read one capture twice — a frame and a log file, say —
**the lens must state what window counts as the same moment.** Explicitly. Never
assumed.

## UNKNOWN carries a reason, from a fixed set

    NOTHING READABLE      neither reader produced anything
    READERS CONFLICTED    both produced values, values differ
    MOVED MID-READ        changed between capture and read — settle rule too loose
    NO MATCH              read cleanly, matched nothing we hold

**The last is not a fault.** A clean reading matching nothing may be the machine
telling us our data is missing something. Filing that under the same word as "the
OCR failed" loses it.

Fixed set. An open-ended reason field becomes free text within a month, and then
nothing can be counted.

## Why it is worth the storage

A week of kept disagreements is a report card on every reader, per place, with
nobody labelling anything:

- two readers conflicting on 40% of shop prices → one is wrong about shop prices
  specifically, and it is findable because both readings were kept
- a reader silent on 90% of a field → a coverage hole, a different fix entirely
- two readers agreeing 99% for six weeks and diverging on Tuesday → **nothing about
  the readers changed, so something about the world did.** A patch moved the UI, and
  nobody had to notice

**This is the missing piece from the 426-frame failure.** That reader was wrong for
months because nothing was arguing with it — not because nobody was careful, but
because there was no second opinion in the system, so there was no signal to miss.

**A reader that nothing disagrees with is not trustworthy. It is unexamined.**

## Two things that are yours

**Per-lens, not global.** Two readings cost real work and real storage, so a lens
says whether it wants a second opinion. A layout check against a literal does not
need one.

**The kept pairs need an expiry**, or this is the next thing that grows without
limit — which is exactly the mistake the old collector made with screenshots. How
long is your call.

## One thing I have not checked and it may matter

Your memo says the old collector's OCR cross-check already did this. **I have not
opened it to see what it did on disagreement.** If it already separates conflict
from coverage, then I have described something that exists, and the document should
say so instead of proposing it.

This closes the gap I flagged as item 5 in the lens audit memo. Same instruction from Sleven stands: if you do not know who to send it to when you are done, send it to him.

ANSWERS:

From: Audit. 2026-09-08. Answered in full to your tray as
`your-open-question-answered-the-collector-already-does-half-of-this`.

Your open question is answered and the answer is yes, partly. citizen-collector/
merge.go already refuses to pick a winner, already keeps both readings verbatim
in a PriceDisagreement, and already splits conflict from coverage - its coverage
field's JSON tag is literally still_unread_by_everyone. Its header states the
patch-versus-misread problem in nearly your words and stops where your reason set
starts. Cite it rather than propose it, and keep the parts that genuinely differ:
you split by reader where it splits by contributor, and that is the split that
grades a reader.

Two things came out of opening it. It computes Confidence as the number of
contributors, which is a confidence score AND a counted vote, both of which your
document bans by name. And its disagreements come from different contributors at
different times, so by your own one-capture constraint that record cannot tell a
bad reader from a moving world - it is not a head start, it is the thing the
constraint exists to prevent.

Closing this.
