# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: the shape of a lens — it is a disagreement contract, six required parts, and one existing diagnostic should be rewritten as one before anything is built
Status:  Answered

Answering your ask. Full design:
`claude/DESIGN_the-lens-is-a-disagreement-contract-2026-09-08.md`

## The shape

**A lens names two things that ought to say the same thing, and what to do when they
do not.**

That falls straight out of your condition 1 taken literally — *the reading is never
the source, it is the challenger.* A challenger has to be challenging something. So
the comparison is not bolted onto the end of a lookup. **The comparison is the whole
object**, and the reading is one of its two halves.

Every case collapses into it with no special cases: the frame and that night's log,
the page and the database row, the game screen and what we hold, a rendered box and
"inside its parent", an image's own history and where we filed it from, and an HTML
file and a literal string.

**And it makes flag-never-fix structural rather than a rule somebody remembers.** A
thing whose only output is *these two disagree* has nowhere to put a value. It
cannot write into the data because it does not produce data.

I banned my first instinct — a settings file with target, selector and expected
value. Not because it is ugly. Because it describes a lookup, a lookup produces a
value, and a thing that produces values eventually writes one down.

## Six required parts

1. **Name and version.** `shop-price@2`. Your own `gamelog@1`→`@3` retraction is the
   argument; an unversioned reading is unrecoverable.
2. **The claim in one plain sentence.** If it cannot be written in one, the lens is
   doing two jobs.
3. **Side A — the observation.** Where to look, when it is ready, and which reader.
   **The reader is named, never inferred.** That is the socket: a new kind of
   reading is a new reader plus a lens naming it, never surgery on the machine.
4. **Side B — what it should agree with.** A row, a file the game wrote, a second
   reading of side A, or **a literal.** The literal is not a convenience. Without
   it, no lens can exist that does not need our database, and the boundary breaks on
   day one.
5. **What counts as agreement.** Exact unless a tolerance is written into the lens.
   **Never a default tolerance** — a default is where wrongness hides.
6. **A specimen that must disagree.** Kept with the lens. **A lens never shown to
   fail is a claim, not a check.**

Two optional: what it refuses to claim, and when it goes stale. One thing that is
not a field because it must never be configurable: **zero is an ordinary answer.**
UNKNOWN is permanent and normal. The moment it is configurable, somebody configures
it away.

## The boundary test fits the same six fields

Your non-project lens: side A is a local HTML file shipped with the machine, side B
is a literal string, agreement is exact, and the specimen is the same file with the
heading changed. **Rename the Citizen Compass folder and it still runs.**

That it needs no extra machinery to express is the strongest evidence the shape is
right. If your boundary test had needed a special case, the shape would be wrong.

## What I need from you before anyone builds

**Take one existing `_diag_` script and write it as a lens.** On paper, not in code.

That is the cheapest possible way to find out this design is wrong, and it is
cheaper than my opinion. I have read those scripts' opening comments and not their
bodies, so **I do not know whether their structure fits these six fields or fights
them.** If a real one will not fit, I would rather learn it from a sheet of paper
than from a half-built machine.

I also have not read `docs/ARCHITECTURE_DECISIONS.md` section 4, which you cite as
LOCKED and governing this framework. If anything above contradicts it, it loses.

## One real gap I am not hiding

Condition 3 — two readings that must agree — is expressible as side B being a second
reading of side A. **The shape holds it. I have not designed what the machine does
when they disagree**, and that is not the same as designing it away.

The collector's screen half is untouched, as instructed.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Closed as MOVED, with one item extracted and ruled.** The lens shape is maintained in the Looking Project. **The paper test you asked for is accepted and goes ahead of the grader**, as you yourself later recommended: rewrite `_verify_correspondence` as a lens **on paper** and report whether the six fields hold. **Nobody edits that file.** If the fields do not hold, the shape is wrong and the grader would be built on it.
