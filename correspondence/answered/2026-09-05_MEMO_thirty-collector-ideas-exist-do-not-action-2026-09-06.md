# Memo

To:      Engineering
From:    Research
Date:    2026-09-06
Subject: Thirty advanced collector ideas exist as a discussion list - do not action
Status:  Answered

## Do not action this

Sleven asked C3 to imagine advanced features for the screen-reading collector.
Thirty are written up. **None is chosen, designed, costed or authorised, and
none is mandatory.** They are conversation starters.

    claude/IDEAS_thirty-advanced-features-for-the-collector-2026-09-06.md

**Sleven is bringing this to you himself** to talk through how any of it would
actually be implemented. This memo exists only so it is not a surprise when he
does. Nothing is being asked of you now.

## The one thing in it that is NOT a suggestion

His words, 2026-09-06:

> "We need to make sure that it's capable of learning with every time I use it.
> From the get go."

That is a stated requirement, not an idea. It rules out learning being added at
version four. It matches what `DESIGN_the-collector-rebuild-a-thing-that-learns-2026-08-30`
concluded independently: nothing is a fact, everything is an observation with
provenance; refusal is the learning mechanism, not the safety catch; teaching is
an operation rather than a code change and must reach backwards over everything
already kept.

## Two things worth your eye before that conversation

**The three "blockers" in the consolidated spec are not blockers.** Sleven says
the original collector already produced 700-plus screenshots that show commodity
names, show his aUEC balance on screen while at a shop kiosk, and contain plenty
of the game font. The font question, the balance question and the commodity-name
question can all be closed from material already on his disk. **C3 has not
opened those files and has not verified this** - it is his statement, recorded
here so the spec's open-questions list is read with it.

**The "no AI" constraint is worth re-deciding rather than inheriting.**
`WO-COLLECT-01 rev 5` bans calling a language model, for cost and for needing no
account or server. Small vision models now run locally on consumer hardware,
offline and free per use, which the stated reasons do not cover. It may still be
the right constraint for other reasons - it steals GPU from the game, and it
adds a component that cannot explain itself. Flagged, not proposed.

## Scope, stated plainly by him

His machine only. Prototype. Not a crew feature and not shared until he has
worked out what it is. An earlier idea about crew sharing was cut for that
reason.

## What C3 did not do

Did not open `citizen-collector/`, run anything, or assess whether any of the
thirty is buildable. Feasibility, cost and sequencing are yours, and were not
attempted here.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Filed as you asked. Nothing actioned, nothing queued, nothing designed against
it.**

Recorded here so a later session finds the disposition rather than the list and
starts building from it: **the thirty ideas are a discussion list and carry no
authority.** The collector rebuild is Sleven's and no desk closes any part of it.

If one of them ever becomes work, it arrives as its own memo with a requirement in
front of it — requirement before control, per the doctrine — not by somebody
picking an item off a list of thirty.
