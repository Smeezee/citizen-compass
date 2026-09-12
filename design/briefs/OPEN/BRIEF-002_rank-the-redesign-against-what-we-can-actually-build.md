# BRIEF-002 — rank the redesign against what we can actually build

    from      C1, architecture
    to        Design (Echo)
    opened    2026-09-12
    REVISED   2026-09-12, three times. The first version told you a competitive
              landscape document was YOURS. IT IS NOT. C1 assumed that and was
              wrong. The second added a rentals proposal; the third adds a DPS
              and combat-math report. All three arrived the same evening.
    answer    a GitHub issue on this repository titled
              "BRIEF-002 — rank the redesign against what we can actually build"
    canary    quote the CANARY LINE at the bottom back in your answer, exactly.

---

# WHAT THIS BRIEF IS ABOUT, AND WHOSE WORK IT IS NOT

**Sleven is running a competitive search of his own, separately from the Design desk.** It has
produced three documents. **None of them is yours. You have not seen them before.**

    claude/RESEARCH_the-competitive-landscape-and-where-we-win-2026-09-12.md
    claude/RESEARCH_rentals-the-third-acquisition-path-2026-09-12.md
    claude/RESEARCH_how-dps-is-calculated-and-what-we-are-actually-matching-2026-09-12.md

**Read all three.** Each opens with a verification pass by this desk marking what was checked, what
was wrong, and what is not to be published. **Those passes bind you; the documents themselves do
not.** They are an outside opinion, and your job is to rank and design against them, not to
adopt them.

**This brief asks for ONE ranked P0/P1/P2 covering all three documents together.**

**A warning about scale, and it shapes your answer:** the three together propose more than this
project can build in a year. **A ranking that puts everything somewhere is not the deliverable.**
The deliverable includes what you would NOT do, and why — see item 8.

---

# WHAT WE ALREADY HAVE — six things the outside search did not

## 1. THE MODEL COUNT. THE LANDSCAPE DOCUMENT SAYS ~295. THERE ARE 256 FILES.

Measured in `claude/AUDIT_images-models-dimensions-phase-one-2026-09-12.md`, section 4:

    256    GLB files that exist on disk
    214    distinct files actually in use
    295    ClassNames that map onto those 214 files
    318    ClassNames in the loadout data in total
     42    files referenced by no ClassName at all

**295 is a count of ClassNames, not of models.**

**The rule this earns, and it binds you: every number carries the surface it was measured on.**
This project has four populations that all look like a ship count — 253 catalog cards, 254 data
rows, 318 ClassNames, 253 RSI role rows — and **only 225 of the two 253s even join by name.** A
figure without its surface is not a figure here.

## 2. THERE IS NO SERVER

**Citizen Compass is a static site.** No backend, no database at request time, no user accounts,
no write path from a visitor. Ruled in
`claude/CLARIFICATION_the-report-control-needs-a-server-and-we-do-not-have-one-2026-09-12.md`.

**So these cannot be built today, at any priority:** community-sourced dealer price freshness;
"cheapest aUEC path today" if "today" means without a rebuild; any per-user stored fleet import.

**Do not drop them. Rank them and mark each SERVER.** The list of things blocked only by having
no backend is itself the argument for building one, and nobody has assembled it.

**A localStorage shortlist is fine** and is not in this group. **Rentals are also NOT in this
group** — rental prices bake at build time and stamp like our dealer prices already do.

## 3. THE VERIFICATION BADGE IS NOT A NEW IDEA. IT IS OUR OLDEST UNBUILT DECISION.

The landscape document ranks *per-ship "checked against patch X on date Y"* first. **We decided
that already**: *"Every data row carries `last_verified_patch`; front end flags unverified data."*
The field exists in the data. **The front end does not flag it.**

**An outside reviewer who could not see our architecture decisions named our unbuilt decision as
our largest competitive gap.** It is not up for ranking. **It is P0 and you design it:** the
states (verified, stale, never verified), the words, where the mark sits on a card and on a ship
page, and **what a whole page looks like when most of it is unverified** — which is the real
question, because that is the honest state of a lot of our data and an honest page that reads as
broken helps nobody.

## 4. A RENTAL PRICE WE CALCULATED IS AN INVENTED PRICE

**Binding, and the rentals document gets this wrong in its own mockup.**

Every multi-day figure in it is computed from the day rate via the wiki discount table — I
re-derived all of them and they are exact — **and its mockup prints them in the same column as
the observed day rate with no mark.** A reader cannot tell which number was seen and which was
multiplied.

**The rule:**

1. **An observed day rate displays as a price.**
2. **An unobserved 3-day or 7-day total does not display as a price at all.** It displays as the
   RULE — *"3 days: 10% off the daily rate"* — which is true, is CIG's, and is what the visitor
   needs to decide.
3. **An observed tier displays as a price, stamped, like any other.** Both states can sit on one
   panel; they cannot look the same.

**Designing those two states so they read as clearly different is part of what this brief is
asking for.**

## 5. RENTALS ARE A RELATIONSHIP, NOT A FIELD

Our model is ships to dealers to places and assumes a sale. **Renting shops are not dealers**,
and a rental has a duration, a discount tier, an included insurance window and a stock-only
constraint that a sale does not.

**Do not design around the `rn`/`rd` bolt-on fields the document proposes.** Design against
**one acquisition panel with three types — rent, buy, pledge** — which is also what makes its own
"acquisition ladder" idea trivial rather than a fourth special case. **The data shape is mine and
is not settled; the panel is yours.**

## 6. THE COMBAT MATH IS SPLIT, AND HALF OF IT IS NOT YOURS

**Not yours, and do not rank it:** whether we build a shared-capacitor pool model, the model
itself, and the unit question now with Code — whether CIG's figure sums burst or sustained values,
and what our own `sdps` field actually holds. **That is engineering, it is unresolved, and nothing
downstream of it is designed until it comes back.**

**Yours, and this is the valuable half:**

- **The page currently claims our DPS "matches CIG on 272 of 275 stock ships" and shows it as a
  trust mark.** If CIG's own number is an isolated per-gun sum — which the arithmetic supports —
  then that claim proves our addition matches their addition and nothing more, while reading to a
  visitor as validation. **Design the honest version of that line.** It is a label, not a model,
  and it may be the cheapest P0 in all three documents.
- **The provenance labels** — which figures came from CIG, which we computed, which are a range.
  **One visual system, not five badges.**
- **The equal-time strip** — damage delivered at 5, 10, 15, 30 and 60 seconds. **This desk rates it
  the best single idea in the three documents**, because it ends the burst-versus-sustained
  argument instead of taking a side in it. Design how it reads.
- **What the default hero number is**, and where turret DPS sits relative to it.
- **How a GATED figure shows that it is gated.** This desk has ruled that a power control which
  does not move the printed number must not sit beside it. **You design what "this number is
  limited" looks like** — and it is the same problem as the unobserved rental tier in item 4, so
  solve them with one pattern, not two.

## 7. IN FLIGHT, DO NOT DUPLICATE

- **BRIEF-001** is open with you and owns the "comes with" panel. **The acquisition panel must
  not redesign it**, and you should say how the two sit together on one page.
- **We carry no packages.** Nothing may assume a package section exists.
- **Two items in the landscape document are the owner's and are with him:** the "Open in Erkul /
  CSG" handoff, and dropping the preview gate. **Do not rank or design either.**
- **Do not cite "~452 craft recipes", any UEX figure, or any claim about Erkul's internals as
  fact.** None of it is verified by this desk. The Erkul material is a useful map of what the
  problem contains; it is not evidence and does not go on our page.
- **Do not add missiles into any DPS figure.**

---

# WHAT IS BEING ASKED

1. **One ranked P0/P1/P2 across both documents** — the landscape list in sections 5.1 to 5.6, and
   the rentals proposal.
2. **One line per item on why it sits where it does** — what it wins, against which rival, what
   it costs.
3. **SERVER marked on every item that cannot exist without a backend**, gathered into one short
   section.
4. **For every P0, enough UI detail that a builder could start**: where it sits, what it says,
   its states, and what it does when the underlying data is missing.
5. **The acquisition panel designed as one thing** — rent, buy and pledge as three types, with
   the observed-versus-rule distinction visible without a legend.
6. **The break-even idea judged.** "About 36 days of rental equals the buy price" — I checked the
   arithmetic and it holds, and it is the strongest idea in either document. **But a break-even
   in days implies the two purchases are the same purchase, and they are not:** a rental is
   stock-only, cannot be modified, and ends. **Design the framing that keeps the number and
   tells that truth**, or argue it should not ship.
7. **The acquisition panel and the stats panel judged against each other.** Both are being
   redesigned at once on the same page. **Say how they coexist**, or say one should wait.
8. **A NOT NOW section, and it is not optional.** Name what you would explicitly not build in the
   next month and why. **An item you would drop entirely is more useful to this desk than an item
   ranked P2**, and a ranking in which nothing is refused will be sent back.

# WHAT IS NOT BEING ASKED

**Not mocks.** Not colour, not type. A ranked brief in words with enough UI detail to build from.

**Not the two owner items. Not the "comes with" panel. Not the front page selector defect.**
Nothing about rights, the Fan Kit, trademark, credentials or money.

**Do not propose displaying data we do not hold, and do not assume a number you have not been
given.** If you need a figure, **ask for it in the issue rather than estimating it** — that is
exactly what went wrong with the model count, and asking would have cost nothing.

**Do not decide anything.** This desk rules; you recommend.

# HOW THE ANSWER IS JUDGED

**Accepted if every P0 could be started by a builder without a further question; if no item
assumes a server without being marked SERVER; if no computed price is shown as a price; if no
figure is presented as validated when it is only arithmetically consistent; and if every number
in it carries the surface it was measured on.**

**Sent back without a NOT NOW section.**

**End your issue with `--- END OF ANSWER ---`.**

---

    CANARY LINE: cobalt-ledger-two-surfaces-one-count-0912
