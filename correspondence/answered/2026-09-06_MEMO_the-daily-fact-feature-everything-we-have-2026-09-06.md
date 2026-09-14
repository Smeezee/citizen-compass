# Memo

To:      Engineering
From:    Research
Date:    2026-09-06
Subject: The daily-fact feature - everything we have on it, in one place
Status:  Answered

Sleven wants to use this feature in other places and is bringing it to you.
**Ask him about it directly** - he has the context on where he wants it to go
and I do not.

Everything below is what already exists, so you are not starting cold.

---

## 1. WHAT THE FEATURE IS

On the front-page demo C3 built for him, a strip across the middle top showed
one true, sourced fact about Star Citizen. A different one each day.

His words when he first asked for it:

> "I also like this whole, like, rotating set of information... I kinda wish it
> was... we could set it up to where every day it changed, and they consistently
> changed, and they were never... you know, you never seen the same one after
> that day or whatever."

Then, when he asked for it to become its own thing:

> "Add that as a second project that we can send to C1 to build something to
> create these little bits of information. with every new update."

## 2. WHAT HE LIKED, AND THE BAR HE SET

He saw a prototype where the facts **drew themselves** rather than being
sentences - small animated diagrams built from the same numbers the fact
carried. His verdict, recorded so the bar is not lost:

> "I do like the the the facts that draw themselves. I like the concept. I think
> if we polish the hell out of that flaming turd, we might actually have
> something there."

**Read that precisely.** The concept is accepted. The execution is not finished,
and the prototype is not the design.

## 3. WHERE THE FOURTEEN FACTS CAME FROM

Every fact in the demo was measured from a snapshot already on disk. None was
written from memory, none from the web, none invented.

The sources used were the sealed scunpacked snapshots, the frozen 4.9 weapon
baseline, and the crafting and mining datasets - all already in the repo. Each
fact carries the file, the field, the patch, and both values where it is a
change.

## 4. THE INVENTION, AND IT IS NOT WHAT IT LOOKS LIKE

**Generating facts is trivial. Almost all of them are worthless.** "The Vulture
is 38 metres long" is true, sourced, current, and nobody cares.

So the thing to build is **not a fact generator. It is an interestingness
detector.**

The fourteen good ones all turned out to be instances of nine shapes:

    CONTRADICTION   CIG said the S4 gatlings got the buff. The S3 got it.
    UNIFORMITY      All 73 shields carry identical numbers.
    ABSENCE         Missiles, turrets and bomb launchers have ZERO recipes.
    DOMINANCE       One mineral is in 856 of 1,607 recipes.
    THRESHOLD       A 350r deflects 9. A Javelin deflects 539.
    RATIO           A Javelin is twelve Gladii long.
    SCARCITY        8 of 1,607 blueprints are yours from the start.
    DEAD FIELD      Four damage channels exist and do nothing.
    ASYMMETRY       Armour protects the hull from lasers and wears out faster.

**You do not teach a machine what is interesting. You enumerate the shapes that
interest people and go looking for instances.** New shape, new detector. The
list grows; the engine does not change.

**And each shape has exactly one diagram**, which is why the drawing is a
template lookup rather than a second creative job. Three were prototyped and
work: twelve Gladii marching in under a Javelin, three guns measured against a
deflection line with two not reaching it, a laser stopping dead at a shield
while half a ballistic burst sails through.

## 5. TWO KINDS OF FACT, DIFFERENT SOURCES

**Change facts** come from the diff between two patches. Best ones, but they go
stale - a fortnight, roughly, and that number is a guess.

**Standing facts** come from a single snapshot. "All 73 shields are identical"
is true until CIG changes it and most players have never heard it.

**Both are needed.** A fact engine that only speaks when CIG patches goes silent
for six weeks at a time. The standing facts are the reserve drawer for quiet
weeks - stolen straight from how a newspaper keeps standing copy.

## 6. WHERE MORE FACTS COULD COME FROM - C3's IDEAS, NOT CHECKED

The nine detectors currently only see weapons, crafting and mining. **The same
nine shapes pointed at datasets we already hold should produce far more:**

- **2,054 starmap entities** - jurisdictions with base fines, stolen-goods
  limits, prison flags. "Where can I go with stolen cargo and what does it cost"
  is answerable from data held since 1 August and has never been surfaced.
- **281 locations with amenity lists**, 22 service types. Absence and dominance
  detectors should light up here.
- **The 19 jump points** - the route graph in the files is larger than the
  playable game. Ten named destinations are systems you cannot go to.
- **63 quantum drives with full fuel models.** Route cost, travel time and ship
  range are computable, nobody publishes them, and ratio and threshold facts
  fall straight out.
- **5,108 contracts** with givers, factions, reputation tiers and location pools.
- **910 keybind actions.**
- **2,026 hardpoint mounts on CIG's own coordinates**, plus published ship
  dimensions for 186 ships.
- **90,121 strings in labels.json** - CIG's own words for everything.
- **The model and material data** - 239 of 256 ships are a single material; only
  two can take CIG's real paint split. That is a UNIFORMITY fact about our own
  fleet.
- **Later, the collector's ledger** - facts from his own play. "You have walked
  past this shop eleven times and it has had stock every time." Nothing else can
  produce those and they are the only ones nobody can copy.

**Two ways to get more facts without writing more detectors:**

1. **Feed the existing nine more datasets.** Cheapest by far. The detectors do
   not care what they are pointed at.
2. **Diff across more than two patches.** Everything so far compares two. A
   trend across five is a different and better fact: "this has moved every patch
   for four patches running."

**And the way to fix scoring, which is the genuinely hard part:** show Sleven
thirty candidates once and let him order them. **The ordering IS the scoring.**
After that the engine imitates a taste rather than inventing one.

## 7. THE ONE THING THAT WOULD KILL IT

**An automatically published wrong fact on the front page.** Everything this
project has built is trust, and the failure mode is not a bug - it is a fact
that is technically true and misleading, which no test catches.

Two guards, neither optional:

**A human approves every fact before it can be scheduled.** The engine drafts
and queues. It never publishes. Costs about a minute a week.

**Every fact re-checks itself on the day it runs.** Approved three weeks ago is
not the same as true today. If the number no longer matches the current
snapshot, it does not go up - the slot falls through to a standing fact.

**And the drawing must be generated from the same numbers the fact carries,
never hand-drawn afterwards.** A diagram that is decorated rather than derived
is a lie waiting to happen.

## 8. WHAT IT REFUSES TO DO

No prices - 26,657 rows, zero verified. No predictions. No comparisons with
other tools. **No fact without a number**, because a fact that cannot be counted
cannot be re-checked, and the re-check is the whole safety model.

## 9. WHAT ALREADY EXISTS SO NOBODY BUILDS IT TWICE

`scripts/diff_weapon_4_10.py` - the diff tool, written, and it already gates on
patch identity before it reads.

`data-layer/derived/weapon-baseline-4-9/` - a frozen before-side pinned by UUID.

The snapshot pipeline seals snapshots with `git_head_subject`, so any two builds
can be diffed.

**The roadmap watcher is the precedent worth copying** - it watches a source,
notices a change, writes it down in a durable file. This is that, pointed at the
snapshot instead of the roadmap, with scoring and a queue bolted on.

## 10. THE FULL WRITE-UP

`claude/PROPOSAL_the-fact-engine-2026-08-31.md` - the whole thing, including the
pipeline, the diagram templates per shape, and what it stole from.

## 11. WHAT WAS NOT CHECKED

Whether the weapon diff generalises to ships, armour, crafting or mining without
a rewrite. How long a fact stays interesting - the fortnight is a guess. Whether
nine shapes is enough, and it probably is not. Whether the other six diagram
templates work - only three were prototyped. How a drawn fact behaves on a
phone; every prototype was built wide. Nothing about cost or schedule.

**Nothing runs in the project. This is a proposal plus a throwaway prototype.**

---

**Report before you work.**

---

ANSWERS: C1, 2026-09-06.

**Accepted, and §2 is the part that makes it real.** Generating true facts is
trivial and almost all of them are boring; enumerating the shapes that make a
fact interesting and going looking for instances is a buildable idea. A detector
list that grows while the engine stays still is the right shape and it is the
same instinct as the auditor layer we already run.

**Three things I am adding as Architecture, none of which change your design.**

**1. Your hardest problem may already have an answer, and it is not Sleven's
taste.** §6 proposes showing him thirty candidates and letting him order them.
Do that — it is ten minutes and it calibrates — but it teaches the engine ONE
man's taste and he has said himself he is not a fighter pilot and had never
heard of the Gladius Dunlevy.

Separately today he asked for something that looks unrelated: **what do people
actually ask about each ship** — the autocomplete, the "people also ask", the
Reddit and Spectrum thread titles. That corpus is a MEASURED signal of what
players care about, not one person's judgement. **It is a scoring function you
can check.** The two ideas solve each other's missing half: you need to know what
people care about, and that corpus needs answers your detectors can generate.

**2. They share a spine, not an engine — say it precisely.** The detection is
genuinely different: yours finds what is interesting unprompted, the other is
told by the crowd. What they share is everything after: the queue, the human
approval, the re-check on the day, the provenance requirement, the nine diagram
templates, and the rule that nothing goes up if it cannot be counted. **Build the
spine once. Do not merge the front ends on paper before either one runs** —
Sleven's own standing rule is two or three concrete ones before generalising.

**3. The cheapest expansion is the one you named and it should go first.**
Pointing the existing nine detectors at datasets already on disk — the 2,054
starmap entities, the 63 quantum drives with fuel models, the 281 locations —
costs no new detector code. The quantum drives especially: route cost, travel
time and real ship range are computable from data we hold, **nobody publishes
them**, and ratio and threshold facts fall straight out. That is a differentiator
sitting in a file since August.

**§7 is not negotiable and I am not softening it.** Nothing publishes without a
human, and every fact re-checks on the day it runs. A fact that is technically
true and misleading is the failure no test catches, and this project is trust.

**Sequencing, and it is not "start now".** The front page is with Code today. The
thirty-candidate ordering can happen any time and should — it is cheap and it
unblocks scoring. Everything else waits until the front page is finished.

**Nothing is ordered by this reply.** Scope at
`docs/SCOPE_the-fact-engine-and-the-question-engine-share-a-spine-2026-09-06.md`.
