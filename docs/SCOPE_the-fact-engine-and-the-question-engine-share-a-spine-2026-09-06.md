# SCOPE — the daily fact and "what people ask" are two front ends on one spine

    from      C1, 2026-09-06
    about     C3's fact-engine proposal, and Sleven's question-corpus idea
    status    SCOPE ONLY. Nothing is ordered, nothing is built, nothing is
              scheduled. The front page is with Code and comes first.

---

## The one sentence

**C3 built a machine that finds what is interesting. Sleven asked for a list of
what people actually want to know. Each one is the other's missing half.**

## What C3 got right, and it is the whole idea

Generating true facts is trivial. *"The Vulture is 38 metres long"* is true,
sourced, current, and nobody cares. **So the thing to build is not a fact
generator, it is an interestingness detector** — nine shapes (contradiction,
uniformity, absence, dominance, threshold, ratio, scarcity, dead field,
asymmetry), and you go looking for instances of them.

A detector list that grows while the engine stays still is the right shape. It is
the same instinct as the auditor layer this project already runs: pluggable
checkers writing to a shared results table, flagging only, never fixing.

**And each shape already knows its own diagram**, so drawing the fact is a
template lookup rather than a second creative job. Three templates are prototyped
and work.

## The problem C3 named as hardest

**Scoring.** What makes one true fact worth the front page and another worthless?
C3's answer: show Sleven thirty candidates once and let him order them; the
ordering is the scoring.

**Do that. It is ten minutes and it calibrates.** But be honest about what it
teaches — **one man's taste.** He said himself today he is not much of a fighter
pilot and had never heard of the Gladius Dunlevy. A scoring function trained on
him will be blind wherever he is.

## Sleven's other idea, which arrived the same day and looked unrelated

**What do people actually ask about each ship.** Not search volume — that number
is not publicly available and anything claiming it would be a guess in a data
costume. What IS gettable and citable: autocomplete completions, "people also
ask" boxes, Reddit and Spectrum thread titles, video titles.

**That corpus is a measured signal of what players care about.** It is not
somebody's judgement, it can be re-gathered, and it can be checked.

**So it is a scoring function with a source.** The fact engine needs to know what
people care about; the question corpus needs answers that a detector can
generate. Neither is complete alone.

## They share a spine. They do not share an engine.

**Say it precisely, because the loose version leads to building one thing that
does neither job.**

**Genuinely different — the detection.** The fact engine finds what is
interesting unprompted, from our own data. The question engine is told what is
interesting by the crowd, from outside.

**Genuinely shared — everything downstream:**

    the queue, and a human approving before anything publishes
    the re-check on the day it runs
    provenance on every row: file, field, patch, both values on a change
    the nine diagram templates
    the rule that nothing goes up if it cannot be counted

**Build the spine once. Do not merge the front ends on paper before either one
runs.** Sleven's own standing rule: two or three concrete ones before
generalising into a shared pipeline.

## What is cheapest and should go first

**Point the existing nine detectors at data already on disk.** No new detector
code. Nothing to gather. C3 named the candidates and they are sitting in the repo:

    2,054 starmap entities   jurisdictions, fines, stolen-goods limits
    63 quantum drives        full fuel models
    281 locations            amenity lists, 22 service types
    19 jump points           a route graph larger than the playable game

**The quantum drives are the standout.** Route cost, real travel time and actual
ship range are computable from data we have held since August, **nobody publishes
them**, and ratio and threshold facts fall straight out. That is a differentiator
sitting in a file, unread.

## The guard that is not negotiable

**Nothing publishes without a human, and every fact re-checks itself on the day it
runs.** A fact that is technically true and misleading is the failure no test
catches, and everything this project has is trust.

**The drawing must be generated from the same numbers the fact carries.** A
diagram decorated afterwards rather than derived is a lie waiting to happen.

## Sequence, and none of it starts today

    1  the front page finishes            with Code now
    2  the thirty-candidate ordering      Sleven, ~10 minutes, any time
    3  nine detectors -> data on disk     cheapest, no new code
    4  question harvest, 10 ships only    a pilot, not 253
    5  decide whether the spine merges    only after 3 and 4 have run

## What C1 checked and what C1 did not

**Checked:** C3's memo and the full proposal of 2026-08-31, including the diagram
templates and the pipeline; that the datasets named in §6 of the memo are real
counts from files in this repo, not estimates.

**Did NOT check:** whether the weapon diff generalises to ships, armour, crafting
or mining without a rewrite — C3 flagged that as unknown and it stays unknown.
Whether nine shapes is enough; probably not. How any of it behaves on a phone —
every prototype was built wide, and Sleven reads on a phone.

*C1, 2026-09-06. Scope only. Report before work stands.*
