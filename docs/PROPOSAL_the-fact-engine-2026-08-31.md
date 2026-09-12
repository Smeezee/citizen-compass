# PROPOSAL — a second project: something that reads every new patch and writes the front page's daily fact by itself. The hard part is not generating facts. It is that most facts are boring, and boring is a property you can detect.

    from      C3 (Cowork), 2026-08-31
    for       C1 to route
    raised by Sleven, after seeing the front-page demo: make this a second
              project, something that creates these little bits of information
              with every new update.
    status    design only. Nothing built, nothing queued.
    depends   on work that already exists - see §6.

---

## 1. THE QUESTION IT ANSWERS

**In the reader's voice:** *"What do I not know about this game that I would want to?"*

**And in the project's voice:** *"How does the front page stay true and interesting on a
Tuesday when nobody has touched it for three weeks?"*

The demo carries fourteen facts. **Fourteen facts is fourteen days.** Hand-writing them
is a subscription to a chore, and the day it lapses the front page starts lying about
being current.

## 2. THE ACTUAL PROBLEM, WHICH IS NOT THE ONE IT LOOKS LIKE

**Generating facts from this data is trivial and almost all of them are worthless.**
*"The Drake Vulture is 38 metres long"* is true, sourced, current, and nobody cares.

**So the engine is not a fact generator. It is an INTERESTINGNESS DETECTOR**, and that
is the whole design.

**Look at what the fourteen good ones have in common.** Every one is an instance of a
small number of shapes:

    CONTRADICTION   CIG said the S4 gatlings got the buff. The S3 got it.
    UNIFORMITY      All 73 shields carry identical numbers. Nobody expects that.
    ABSENCE         Missiles, turrets and bomb launchers have ZERO recipes.
    DOMINANCE       One mineral is in 856 of 1,607 recipes.
    THRESHOLD       A 350r deflects 9. A Javelin deflects 539.
    RATIO           A Javelin is twelve Gladii long.
    SCARCITY        8 of 1,607 blueprints are yours from the start.
    DEAD FIELD      Four damage channels exist and do nothing.
    ASYMMETRY       Armour protects the hull from lasers and wears out faster for it.

**Nine shapes. Each one is a detector somebody can write.** They run over a snapshot,
or over a diff between two snapshots, and each returns candidates with a score.

**That is the invention here, and it is worth saying plainly:** you do not teach a
machine what is interesting. **You enumerate the shapes that interest people and go
looking for instances.** New shape, new detector. The list grows; the engine does not
change.

## 3. TWO KINDS OF FACT, AND THEY COME FROM DIFFERENT PLACES

**CHANGE FACTS — from the diff between two patches.** These are the best ones and they
have a shelf life. The gatling fact is only interesting for about a fortnight.

**STANDING FACTS — from a single snapshot.** *All 73 shields are identical.* True until
CIG changes it, and most readers have never heard it. **These are the reserve** — the
engine draws on them when a patch was quiet, and a quiet patch is most of them.

**The scheduler needs both**, because a fact engine that only speaks when CIG patches
goes silent for six weeks at a time.


## 3b. THE FACT SHOULD DRAW ITSELF — added 2026-08-31 after Sleven saw it working

**The first version of this proposal assumed a fact is a sentence.** It is not. **A fact
is a shape, and the shape can draw itself.**

**And here is the part that makes it cheap: the detector already knows which shape it
found.** §2's nine shapes are not just a way of finding facts — **each one has exactly
one diagram, and the detector that emits the fact already knows which.** So the drawing
is not a second creative job. It is a template lookup.

    CONTRADICTION   two bars side by side, one marked "what CIG said"
    RATIO           the small thing repeated until it fills the big thing
    THRESHOLD       a line, and bars measured against it - some do not reach
    UNIFORMITY      many marks, all identical, and the eye does the counting
    DOMINANCE       one bar against the rest of the field
    SCARCITY        a full set, with the tiny surviving fraction lit
    ABSENCE         a row of categories with one column empty
    DEAD FIELD      six channels drawn, four of them flat
    ASYMMETRY       the same input, two outcomes, drawn in opposite directions

**Three were prototyped and they work.** Twelve Gladii marching in under a Javelin to
fill its length. Three guns measured against a deflection line, two of them not
reaching it. A laser stopping dead at a shield while half a ballistic burst sails
through. **Each runs in about four seconds and needs no reading at all.**

**Why this matters more than it looks:**

- **A sentence gets read. A picture gets shared.** The daily fact's real job is to be
  the thing somebody posts when a patch drops, and nobody posts a paragraph.
- **It is language-free.** A drawn ratio is a drawn ratio in any language, which
  matters for a game with a large non-English playerbase.
- **It is honest by construction.** A bar that does not reach a line cannot overstate
  itself the way a sentence can. **The picture is the number.**

**So the pipeline in §4 gains one step, between DRAFT and HOLD:**

    3b  RENDER   the shape picks its template, the template takes the numbers,
                 and the output is a small self-contained animation with the
                 headline and the because underneath it

**What this adds to §5's guards:** the drawing must be generated from the same numbers
the fact carries, never hand-drawn afterwards. **A diagram that is decorated rather
than derived is a lie waiting to happen** — if the re-check on the day finds the number
moved, the picture has to move with it or not run.

**Sleven's verdict on the prototype, recorded so the next session knows the bar:**
*"I like the concept. I think if we polish the hell out of that flaming turd, we might
actually have something there."* **The concept is accepted. The execution is not
finished, and nobody should treat the prototype as the design.**

## 4. THE SHAPE OF THE THING

    1  DETECT     each detector runs over the newest snapshot, and over the
                  diff against the previous one. Emits candidates.
    2  SCORE      surprise, size of the number, how many players it touches,
                  and whether we have said it before.
    3  DRAFT      candidate becomes two sentences: the headline and the
                  because. Template per shape, not free prose.
    3b RENDER     the shape picks its diagram and the numbers fill it. §3b.
    4  HOLD       lands in a queue. NOBODY PUBLISHES WITHOUT A HUMAN. §5.
    5  SCHEDULE   approved facts get a date. One a day. Used ones are marked
                  and never come round again.

**Every fact carries its provenance the whole way through** — the file, the field, the
patch, and the two values if it is a change. **A fact that cannot be checked does not
get scheduled**, which also means the front page can show its own working if anyone
asks.

## 5. THE ONE THING THAT WOULD KILL IT

**An automatically published wrong fact on the front page.**

Everything this project has built is trust. The front page saying something false, in
large type, sourced and confident, does more damage than a month of saying nothing.
**And the failure mode is not a bug — it is a fact that is technically true and
misleading**, which no test catches.

**Two guards, and neither is optional:**

**A human approves every fact before it can be scheduled.** The engine drafts and
queues; it never publishes. That is the whole safety model and it costs about a minute
a week.

**Every fact re-checks itself on the day it runs.** A fact approved three weeks ago may
have been overtaken by a patch. **If the number it names no longer matches the current
snapshot, it does not go up** — the slot falls through to a standing fact and the stale
one goes back to the queue flagged.

## 6. WHAT ALREADY EXISTS, SO NOBODY BUILDS IT TWICE

**MEASURED, on disk today:**

    scripts/diff_weapon_4_10.py          the diff tool, already written, already
                                         gates on patch identity before it reads
    data-layer/derived/weapon-baseline-4-9/   a frozen before-side, subjects pinned
                                         by UUID
    the snapshot pipeline                sealed snapshots with git_head_subject,
                                         so any two builds can be diffed
    roadmap-watcher                      already writes docs/FINDING_roadmap-change-*
                                         when a card moves - the same shape of job,
                                         already solved once

**The roadmap watcher is the precedent worth copying.** It watches a source, notices a
change, and writes it down in a durable file. **This is that, pointed at the snapshot
instead of the roadmap, with a scoring step and a queue bolted on.**

**ASSUMED, not checked:** that the weapon diff generalises to ships, armour, crafting
and mining without being rewritten. **Somebody should look at it before assuming the
detectors can share one diff.**

## 7. WHAT IT REFUSES TO DO

**No prices.** 26,657 rows, zero verified. A daily fact about money would be the fastest
possible way to lose the trust the rest of it buys.

**No predictions.** *"The Idris will probably be nerfed"* is not a fact and there is no
detector for it.

**No comparisons with other tools.** *"Only we know this"* is marketing, and it ages
badly the moment somebody else works it out.

**No fact without a number.** Every shape in §2 is anchored to a countable thing. A
fact that cannot be counted cannot be re-checked, and §5 depends on re-checking.

## 8. WHAT IT STOLE FROM

**A newspaper's standing-copy desk.** Papers keep a drawer of finished, checkable
pieces that are true whenever they run, and they use them on quiet days. **The standing
facts in §3 are that drawer.** The change facts are the news, and the drawer is what
stops the front page going blank when there is none.

## 9. WHAT WOULD HAVE TO BE INVENTED

**The scoring step.** Detectors are ordinary code. **Ranking nine kinds of interesting
against each other is not**, and it is the part that decides whether this feels curated
or automatic.

**Sleven's answer would settle it faster than a formula:** show him thirty candidates
once, let him order them, and the ordering IS the scoring. **After that the engine is
imitating a taste rather than inventing one.**

## 10. WHY IT IS WORTH A PROJECT AND NOT A SCRIPT

Because it outlives the front page. **The same queue feeds a patch-notes page, a
what-changed view, a Spectrum post, and anything else that needs to say something true
and current** — all from one place that already re-checks itself.

**And it is the only part of this site that gets more valuable the longer it runs.**
Everything else is a snapshot of now. **This one accumulates.**

## 11. WHAT I CHECKED AND WHAT I DID NOT

**Checked:** that three of §3b's diagrams render correctly from real snapshot figures
in a prototype; that `scripts/diff_weapon_4_10.py` exists and gates on patch identity;
that `data-layer/derived/weapon-baseline-4-9/` holds a frozen before-side pinned by
UUID; that the roadmap watcher already writes dated finding files when a card moves;
that every one of the fourteen facts in the demo was measured from a snapshot on disk
and each is an instance of one of §2's nine shapes.

**Did NOT check:**
- **Whether the weapon diff generalises** to ships, armour, crafting or mining. §6.
- **How long a fact stays interesting.** §3 says a fortnight and that is a guess.
- **Whether nine shapes is enough**, or whether a tenth appears the moment somebody
  reads real candidate output. **It probably does.**
- **Anything about cost or schedule.** Not my desk.
- **Whether all nine diagram templates work**, or only the three prototyped. §3b.
  **The other six are asserted, not demonstrated.**
- **How a drawn fact behaves on a phone.** Every prototype was built wide.
- **I have built nothing that runs in the project.** This is a proposal, plus a
  throwaway prototype of three diagrams.
