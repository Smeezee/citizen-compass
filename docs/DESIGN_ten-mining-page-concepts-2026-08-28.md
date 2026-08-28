# TEN MINING PAGE CONCEPTS — every other tool in this hobby answers "what is this rock worth?" Not one of them can answer "what does this rock become?", because CIG only just shipped the data that closes the loop. I measured it tonight: 26 of 26 crafting ingredients trace back to a specific rock through CIG's own UUID pointers, zero unreachable, no matching of any kind. That chain is the page. Everything else here hangs off it.

    from      C3 (Cowork), 2026-08-28
    for       C1, answering ORDER-C3-design-ten-mining-page-concepts-2026-08-28
    raised by Sleven: "design 10 deeply detailed ideas on how to build a page
              for mining... creative and somewhat interactive and easily used
              with a visually appealing HUD"
    measured  against snapshot 20260827T225641Z, build 4.10.0-LIVE.12519617,
              the sealed one. Every figure below was read tonight.
    NOTE      §0 corrects four figures in the order. Three hold, three do not.

---

## 0. THE ORDER'S FIGURES, CHECKED — because §6 says to

**HOLD, verified exactly:**

    1,607 recipes                     4.10. (4.9 had 1,597 - ten new.)
    Aslarite in 856 of 1,607          holds as node count AND as distinct
                                      recipes. No recipe uses it twice.
    30 raw -> refined pairs           exactly 30 carry RefinedVersionUUID
    27 commodities with a rarity tier common 10 · uncommon 6 · rare 5
                                      · epic 3 · legendary 3
    274 mineable rock types           274 carry a real Composition block

**CORRECTED:**

**"37 materials" in crafting demand → 26 distinct resources.** Walking every
requirement tree to its leaves gives **26 distinct `resource` ingredients**. There
are also **298 `item` nodes** — recipes that consume finished items rather than ore.
**37 is probably resources plus some item leaves counted together.** The two must
never be added: a resource is cargo measured in SCU, an item is a count. **This
matters for a demand board, which is concept 2.**

**"Laranite 353" → 353 nodes but 341 distinct recipes.** Some recipes want Laranite
in two different slots. **Aslarite, Ouratite, Tungsten and Agricium are unaffected.**
Say which denominator any published figure uses.

**"23 ships with a mining or salvage port" → I measured 23 mining LASER ITEMS,
which is a different thing.** `WeaponMining` 23, `SalvageHead` 9, `SalvageModifier`
9. **I did not verify the ship count and the coincidence of 23 is suspicious.**
Somebody should re-derive it from ports before it is printed.

**One caution on the resource file itself:** 117 of its 557 entries carry
`<= PLACEHOLDER =>` as a name, and the very first record is a fluff datapad
classified `cave_harvestable`. **The 274 with a real `Composition` block are the
designable set. Anything counting raw rows will overstate.**

---

## 1. WHAT I FOUND THAT CHANGES THE WHOLE BRIEF

### 1a. Regolith Co is dead

`regolith.rocks` reads **"Regolith Co. has powered down."** The tool this hobby used
for crew shares, work orders and refinery comparison is gone. **That is a live fact
as of tonight and it should be checked again before anyone acts on it.**

### 1b. SCMiner is alive, current, and very good

v1.1.0, tagged for 4.10. Mineral directory, ore location maps, signature scanner,
ore comparison matrix, crackability checker, laser physics simulator, Aaron Halo
navigator, yield calculator, loadout builder — **and a refinery work-order parser
that reads pasted screenshots and tracks live completion timers.**

**We should not try to beat that.** They have a parser and live timers; we have no
backend. **Building a worse copy of SCMiner is the failure mode of this whole
order**, and several obvious mining-page ideas are exactly that.

### 1c. THE CHAIN CLOSES — and this is the entire differentiator

Every tool in §1b answers *what is this rock worth in aUEC.* **Mining as income.**

**CIG's files close a different loop, and I tested it tonight:**

    rock type
      -> Composition.Parts[]      which elements, MinPercentage-MaxPercentage,
                                  Probability, QualityRange, QualityQuantization
      -> raw ore                  carries a rarity Tier and a quality distribution
      -> RefinedVersionUUID       CIG's own refinery pointer
      -> refined material
      -> recipe slot              MinQuality + QuantityScu
      -> quality Modifier         0-1000 quality -> up to +/-20% on a NAMED stat
      -> the finished item's numbers

    mined element types that are commodities      40 of 40
    of those, carrying a RefinedVersionUUID       26
    CHAIN CLOSES rock -> raw -> refined -> recipe 26
    crafting ingredients left unreachable         0

**Exact UUID equality at every hop. No name matching, no case folding, no fuzzy
anything.**

### 1d. THE HONEST BREAK, and it must appear on the page's own face

**Quality is recorded on the RAW ore and is absent from the REFINED material.**
43 commodities carry a `QualityDistributionUUID` — every one a raw or ore form. All
28 refined materials the recipes consume carry **no Tier and no quality field at
all.**

**So whether the quality of what you mined survives the refinery is NOT PROVEN by
this data.** Two readings:

    a  quality lives on the item STACK at runtime, not on the type definition
       - likely, and consistent with both ends using the same 0-1000 scale
    b  quality resets at the refinery and crafting quality comes from elsewhere

**I cannot tell from the files.** It is testable in game, and 4.10 is on Sleven's
machine. **Until it is tested, no concept here may state that a better rock makes a
better gun.** They may state the chain of identity, which is proven, and must say
the quality question is open. **Concept 8 exists specifically to hold that line.**

### 1e. The mining model is two-sided and both sides are on disk

The rock carries `PowerCapacityPerMass`, `ResistanceCurveFactor`, `OptimalWindowSize`,
`OptimalWindowFactor`, `DecayPerMass`, `DefaultMass`, `CScuPerVolume`, and a named
waste resource. **Four distinct parameter profiles across 274 rocks** — 235 share one.

The laser carries `PowerTransfer`, `OptimalRange`, `MaximumRange`,
`ExtractionThroughput`, and **`Modifiers` that shift the rock's numbers**:
`Resistance -40`, `OptimalChargeWindow +40`, `OptimalChargeRate +20`,
`Instability +30`.

**The two sides are designed to be computed against each other, and both are ours.**

---

## 2. THE TEN

Each carries the seven fields the order asks for, in its order.

---

### CONCEPT 1 — WHAT DOES THIS ROCK BECOME
*The chain viewer. This is the site's identity on this subject.*

**1. The player's question.** *"I keep scooping this stuff. What is it actually
for?"*

**2. The screen.** The rock is the fixed left rail; the chain runs rightward and the
eye lands on the right-hand end, which is a picture of a gun.

    ┌ QUANTAINIUM DEPOSIT ─────────────────────────────────────────────┐
    │ signature 4000     3+ distinct elements     waste: Inert Materials│
    │                                                                   │
    │  IN THE ROCK          REFINES TO        WANTED BY                 │
    │  ▓▓▓▓▓▓▓▓ Quantainium  2.1–50%  ──────► Quantainium ──► 12 recipes│
    │  ▓▓▓▓▓ Quartz         20–60%  p0.7 ───► Quartz ──────► 28 recipes│
    │  ▓▓▓ Beryl             2–40%  p0.5 ───► Beryl ───────► 33 recipes│
    │  ▓▓▓ Aluminum          3–50%  p0.5 ───► Aluminum ────► 38 recipes│
    │                                                                   │
    │  ▸ what this cannot tell you                                      │
    └───────────────────────────────────────────────────────────────────┘

**3. The interaction.** Click any element in the rock and the right column filters
to the recipes that want it. Click a recipe and it opens the existing ship-page part.
**Hovering an element band shows its percentage range as a filled bar rather than
two numbers** — a range reads as a range. Probability below 1 renders the band
hatched, because "might be here" is not "is here."

**4. Data.** `resources/resources.json` → `Composition.Parts[]`
(`MinPercentage`, `MaxPercentage`, `Probability`, `ResourceTypeUUID`),
`Signature`, `GlobalParams.WasteResourceTypeName`;
`resources/commodities.json` → `RefinedVersionUUID`;
`blueprints.json` → requirement trees. **Joined on UUID, exactly.**

**5. What it cannot say.**

> *"This is what the rock contains and what those materials are wanted for. It is
> not a yield — the percentages are CIG's ranges for the deposit type, not a
> reading of any rock you will actually find. Whether the quality of what you mine
> carries through refining is not something the game files state, so nothing here
> claims a better rock makes a better part."*

**6. Build cost.** **2–3 days.** The join is done and proven. The risk is entirely
visual: four stacked ranges with probabilities is a lot of information in a small
space, and it will want two or three passes to stop looking like a spreadsheet.

**7. Why they come back.** They come back because **the answer changes when the
recipes change**, and because this is the only place that answers it. It is also the
natural landing page for anyone who searched a mineral's name.

---

### CONCEPT 2 — THE DEMAND BOARD
*Which materials the crafting economy actually eats. My first pick — see §3.*

**1. The player's question.** *"If I only have one hold to fill, what should be in
it?"*

**2. The screen.** A single ranked column, widest bar at the top, nothing else
competing.

    MATERIAL DEMAND — what 1,607 recipes ask for
    ─────────────────────────────────────────────────────────
    Aslarite     ████████████████████████████  856 recipes  53%
    Ouratite     ████████████████              495          31%
    Laranite     ███████████                   341          21%
    Tungsten     ████████                      261          16%
    Iron         ███████                       238          15%
    Agricium     ██████                        194          12%
    ─────────────────────────────────────────────────────────
    ▸ how this is counted        ▸ this is not a price

**3. The interaction.** Click a material and it expands in place to show which slot
names it fills — Insulative Liner, Armored Carapace, Frame, Barrel — and which rocks
it comes from, which is a jump into concept 1. A toggle switches the bars between
**recipe count** and **total SCU demanded**, and the order changes when you do.
**That reordering is the most interesting thing on the page**, because the material
in the most recipes is not the material the economy needs most by volume.

**4. Data.** `blueprints.json` requirement trees, leaves of kind `resource`, plus
`QuantityScu` for the SCU mode. Slot names come from the parent `group` node.
`data-layer/derived/crafting-demand/demand.json` already holds most of this.

**5. What it cannot say.**

> *"This counts recipes, not players. It is what the game's crafting system is built
> to consume — not what anyone is buying, and not what anything sells for. Counts
> and volumes are kept apart deliberately: 0.36 SCU of Agricium and 7 Hadanite are
> not 7.36 of anything."*

**6. Build cost.** **1 day.** One dataset, one chart, no unresolved questions. The
riskiest part is the denominator honesty from §0 — publish which count is on screen.

**7. Why they come back.** **Because it changes every patch and nowhere else states
it.** It is also the most quotable page on the site: "Aslarite is in 53% of every
recipe in the game" is a sentence people repeat, and it carries our name with it.

---

### CONCEPT 3 — THE LASER BENCH
*Your laser against a named rock, computed from both sides.*

**1. The player's question.** *"Will this rock crack with what I'm flying?"*

**2. The screen.** Two panels feeding one readout, laid out like the loadout bench
because it is the same idea.

    YOUR HEAD                    THE ROCK
    Arbor MH1        S1          Granite Deposit
    power transfer   0.80        resistance curve   0.60
    optimal range    8 m         optimal window     0.10
    max range       18 m         power/mass         10
    modules ▾                    mass              100
      Resistance      −40        ────────────────────────
      Charge window   +40        EFFECTIVE WINDOW  0.10 → 0.14
      Charge rate     +20        EFFECTIVE RESIST  0.60 → 0.36
      Instability     +30
                     ▸ what these numbers are and are not

**3. The interaction.** Swap the head, add or remove modules, pick a deposit type
from a list. **Every number that moves is highlighted as it changes** — that is the
whole point, and it is the loadout bench's swap loop applied to mining. Range is a
slider showing the fall-off between optimal and maximum.

**4. Data.** `ship-items.json` → `WeaponMining` items, `MiningLaser` block
(`PowerTransfer`, `OptimalRange`, `MaximumRange`, `ExtractionThroughput`,
`Modifiers`); `resources.json` → `GlobalParams` per rock.

**5. What it cannot say.**

> *"These are the game's own parameters for your head and for this deposit type. How
> the game combines them is not published, so this shows both sides and the direction
> each module pushes — it does not predict a crack. Treat the arrows as which way the
> fight goes, not as a result."*

**6. Build cost.** **3–4 days, and it needs a decision first.** The risk is real and
it is §5: I can show both sides honestly, and I cannot verify CIG's combination
formula. **If we ever state a computed outcome we are guessing, and SCMiner has a
simulator that probably does it better.** Ship the two-sided view or do not ship it.

**7. Why they come back.** Every new head and every new module is a reason to open
it, and it is where a player decides what to buy.

---

### CONCEPT 4 — THE DEPOSIT FIELD GUIDE
*56 deposit names, and what each one can hold.*

**1. The player's question.** *"The scan says Shale. Is that worth stopping for?"*

**2. The screen.** A card per deposit type, sorted by how many distinct elements it
can carry, with the guaranteed elements solid and the probabilistic ones hatched.

    SHALE DEPOSIT               41 rock variants · min 2 distinct elements
    ██ always      Quartz
    ▒▒ p0.7        Aluminum · Copper
    ▒▒ p0.5        Beryl · Tin
                                        ▸ what "p0.5" means here

**3. The interaction.** Filter by "contains element X" and the cards reorder.
**Hover a hatched band and the card shows how many of that deposit's variants
actually carry it** — the honest version of "sometimes."

**4. Data.** `Composition.DepositName` (56 distinct), `MinimumDistinctElements`
(1–4), `Parts[].Probability`. Element counts per rock run 1 to 9.

**5. What it cannot say.**

> *"Deposit types describe what CAN be in a rock, not what is. Two Shale deposits in
> the same field can hold different things. Nothing here knows where any deposit
> is."*

**6. Build cost.** **2 days.** Low risk. The design problem is 56 cards without a
wall of text, which argues for filter-first rather than scroll-first.

**7. Why they come back.** It is the page you check *while flying*, which makes it
the phone candidate — see §4.

---

### CONCEPT 5 — THE SIGNATURE LOOKUP
*A number off the scanner, and what it can be.*

**1. The player's question.** *"My scanner says 4000. What am I looking at?"*

**2. The screen.** One input, one answer, nothing else. The most restrained page on
the site.

    SIGNATURE  [ 4000 ]
    ──────────────────────────────────────────
    3 deposit types read at or near this value
      Quantainium Deposit        4000   exact
      Hadanite Deposit           3980   ±20
      Aphorite Deposit           4020   ±20
    ──────────────────────────────────────────
    ▸ why more than one, and why that is honest

**3. The interaction.** Type or drag a slider across the 3000–4900 band. Results
update live. Click through to concept 1.

**4. Data.** `Signature` on 388 records, **34 distinct values across 3000–4900.**

**5. What it cannot say.**

> *"Signature values overlap and the game does not hand you a name. Several deposits
> can read the same. This narrows it; it does not identify it."*

**6. Build cost.** **1 day.** Trivially cheap. **The risk is that SCMiner has a
signature scanner already** — ours is only worth shipping as the entry point into
concept 1, not as a standalone.

**7. Why they come back.** They do not come back to this page. **They arrive at it,
mid-flight, and leave through concept 1.** That is its job and it should be judged
that way.

---
### CONCEPT 6 — THE MINING FIT
*23 heads, 9 salvage heads, 9 modules — which ship takes what.*

**1. The player's question.** *"I have a Prospector. What can I actually bolt on?"*

**2. The screen.** The existing ship page's picker, scoped to mining, with the ship's
own hull on the holo stage and the mining ports lit.

    PROSPECTOR                          [holo stage, mining ports pulsing]
    ├ mining head    S1   Arbor MH1  ▾
    │   └ module 1        Focus III  ▾
    │   └ module 2        (empty)    ▾
    └ ▸ what a module actually changes

**3. The interaction.** **This is the loadout bench, not a new mechanism** — the same
swap loop, the same picker rules, the same disclosure bars. Clicking a lit port on
the hull opens the same panel as the list row.

**4. Data.** `ship-items.json` `WeaponMining` (23), `SalvageHead` (9),
`SalvageModifier` (9), and the ship page's existing port and fitment rules.

**5. What it cannot say.**

> *"This is what the game allows in each port. It is not a recommendation, and the
> module numbers are the modifiers CIG ships — how they combine in the beam is not
> published."*

**6. Build cost.** **1–2 days IF it reuses the ship page. Two weeks if anybody builds
a second picker.** That is the whole risk and it is a rule-14 shaped one: **one picker,
one fitment rule, one place for them to disagree.**

**7. Why they come back.** Same reason they come back to the ship page — because a
new module shipped and they want to see what it does.

---

### CONCEPT 7 — CRAFT-BACK: START FROM THE THING YOU WANT
*Concept 1 run backwards, and probably the most USEFUL page here.*

**1. The player's question.** *"I want to build this gun. What do I have to go dig
up?"*

**2. The screen.** The item at the top, the shopping list under it, and each line
opening into where it comes from.

    OMNISKY III CANNON — craftable          build time 9 min
    ────────────────────────────────────────────────────────
    FRAME             0.36 SCU  Agricium   ◂ 4 deposit types
    BARREL            0.72 SCU  Tungsten   ◂ 7 deposit types
    WIRING            0.18 SCU  Copper     ◂ 11 deposit types
    CASING            1.20 SCU  Aslarite   ◂ 22 deposit types
    ────────────────────────────────────────────────────────
    total raw volume  2.46 SCU        ▸ before refining losses
    ▸ can you even get this blueprint?

**3. The interaction.** Click any line to see the deposits that carry it, ranked by
how much of it they hold. **A "fill my hold" mode** takes a cargo capacity and shows
how many of this item that hold's worth of ore could make — pure arithmetic, no
prices.

**4. Data.** `blueprints.json` requirement trees with `QuantityScu`,
`CraftTimeSeconds`; `part_recipes.json` for the join to the ship page's 452 craftable
parts; concepts 1 and 4 for the reverse lookup.

**5. What it cannot say.** **And this is the honest headline, not a footnote:**

> *"Only 8 of 1,607 blueprints are available by default. 724 come from reward pools.
> For everything else, the game files do not say how you get the recipe — so the
> materials list below may be the easy part. Volumes are what the recipe asks for
> after refining; refinery losses are not in the game files and are not counted
> here."*

**6. Build cost.** **2 days.** `part_recipes.json` already exists. The riskiest part
is resisting the urge to total a price at the bottom.

**7. Why they come back.** **Because it turns "go mining" into a specific errand**,
and an errand is a reason to open a page before you undock rather than after.

---

### CONCEPT 8 — THE QUALITY LADDER
*What quality buys, and the open question, in one place.*

**1. The player's question.** *"Does it matter if my ore is good?"*

**2. The screen.** Deliberately two-part, and the second part is a stated gap rather
than a blank.

    QUALITY — WHAT THE FILES SAY
    ─────────────────────────────────────────────────────
    IN THE ROCK      Quantainium comes out 501–1000
                     the game steps it: 514 · 669 · 762 · 852
                                        901 · 974 · 1000
    IN THE RECIPE    each slot names a stat quality moves
                     Damage Mitigation · Integrity · Fire Rate
                     · Recoil · Coolant Rating · Shield Strength
                     the swing is up to ±20%, ±40% at the widest
    ─────────────────────────────────────────────────────
    BETWEEN THEM     THE FILES GO QUIET.
                     Quality is on the raw ore. It is NOT on the
                     refined material — no tier, no quality field,
                     on any of the 28 the recipes use.
                     So we cannot tell you a better rock makes a
                     better gun. We can tell you both ends exist
                     and use the same 0–1000 scale.
    ─────────────────────────────────────────────────────

**3. The interaction.** A slider from 0 to 1000 showing which quantization step you
land on and what a modifier at that quality would do to a named stat — **labelled
throughout as what the recipe would apply, not as what your ore will be.** A toggle
flips to the 462 modifiers that run backwards, where higher quality drives the number
DOWN because lower recoil and lower heat are better.

**4. Data.** `Composition.Parts[].QualityRange` and `QualityQuantization`;
`blueprints.json` modifier `QualityRange` and `ModifierRange`;
`commodities.json` `QualityDistributionUUID` presence and absence.

**5. What it cannot say.** The middle panel IS the "cannot say", printed at the same
size as the rest. **That is the point of the design.**

**6. Build cost.** **2 days, and it is the most valuable two days here** — because it
is the page that stops every other page from lying. **If the in-game test later closes
the gap, this page becomes the answer instead of the question and nothing else has to
change.**

**7. Why they come back.** **They come back when the answer arrives.** Until then it
is the page that proves this site says what it does not know, which is the thing we
actually sell.

---

### CONCEPT 9 — RARITY AGAINST DEMAND
*CIG's rarity tiers versus what the recipes eat. The mismatch is the story.*

**1. The player's question.** *"Is the rare stuff actually the valuable stuff?"*

**2. The screen.** One scatter, four quadrants, and the interesting corner labelled.

              high demand
                   │
     COMMON AND    │   RARE AND
     HUNGRY        │   HUNGRY
     ──────────────┼──────────────  rarity →
     COMMON AND    │   RARE AND
     IGNORED       │   IGNORED
                   │
    27 tiered commodities · 10 common · 6 uncommon · 5 rare · 3 epic · 3 legendary

**3. The interaction.** Hover a point for the material, its tier and its recipe count.
Click to open concept 1. A toggle switches demand between recipe count and SCU volume,
**and points move** — which is the whole argument.

**4. Data.** `commodities.json` `Tier` (27 non-null); recipe counts from concept 2.

**5. What it cannot say.**

> *"Rarity here is CIG's own label on the commodity, not a statement about how hard
> something is to find or what it sells for. Demand is recipe demand, not player
> demand."*

**6. Build cost.** **1–2 days.** Cheap, and it depends on concept 2 already existing.
The risk is that a scatter plot is a chart nobody asked for — **this only earns its
place if the mismatch is real, and that should be checked before it is built, not
after.**

**7. Why they come back.** They probably do not. **This is a page you read once and
argue about**, which makes it a good link to send and a poor page to return to. Judged
honestly, it is the weakest of the ten and it is in because the data is free.

---

### CONCEPT 10 — THE WASTE COLUMN
*Every rock hands you garbage. Nobody says how much.*

**1. The player's question.** *"Why is my hold full when I barely mined anything?"*

**2. The screen.** One bar per deposit type, the useful fraction solid and the
remainder dark, sorted by how much of it is junk.

    WHAT COMES BACK IN THE HOLD
    ─────────────────────────────────────────────
    Shale        ███░░░░░░░░░░░░░░  min 2 elements
    Granite      ████░░░░░░░░░░░░░  min 2
    Quantainium  ██████░░░░░░░░░░░  min 3
    ─────────────────────────────────────────────
    dark = Inert Materials    ▸ why this is a range

**3. The interaction.** Hover for the named waste resource and the element ranges that
produce the solid part. A capacity input turns the fractions into SCU against your
actual hold.

**4. Data.** `GlobalParams.WasteResourceTypeName` and `CScuPerVolume`,
`Composition.MinimumDistinctElements`, `Parts[].MinPercentage`/`MaxPercentage`.

**5. What it cannot say.**

> *"This is derived from the deposit's stated composition ranges, not from any rock
> you mined. The real split depends on the rock you actually hit."*

**6. Build cost.** **1–2 days.** The risk is that the honest version is a wide range
rather than a number, and **a wide range drawn as a bar looks like a precise claim.**
Draw the uncertainty or do not draw it.

**7. Why they come back.** They do not return often. **But it answers a question every
new miner asks and nobody has written down**, which makes it a strong search landing.

---
## 3. RANKED, AND MY FIRST PICK

**Value against buildability. Disagreeing with the order's implied ranking is part
of the job, so here is mine.**

     1  Demand Board            1 day    unique, certain, quotable
     2  What Does This Rock     2-3 d    the identity. Nothing else does it
        Become
     3  Craft-Back              2 d      the most USEFUL page for a player
     4  Quality Ladder          2 d      protects every other page from lying
     5  Deposit Field Guide     2 d      the one that works on a phone
     6  Mining Fit              1-2 d    cheap ONLY if it reuses the ship page
     7  Waste Column            1-2 d    a real question nobody has answered
     8  Signature Lookup        1 d      an entry point, not a destination
     9  Laser Bench             3-4 d    needs a decision first. SCMiner is better
    10  Rarity vs Demand        1-2 d    free data, thin reason to exist

### Build the DEMAND BOARD first

**Not because it is the best idea — concept 2 is the best idea — but because it is
the cheapest complete proof that we are not another mining calculator.**

- **One day, one dataset, no unresolved questions.** No quality problem, no
  combination formula we cannot verify, no price we cannot source.
- **It states something true that no other tool states.** *Aslarite is in 856 of
  1,607 recipes.* That sentence is the whole thesis in one line, and people repeat
  sentences like that.
- **It is the frame every other concept needs.** Once a visitor has seen materials
  ranked by what the game's recipes eat rather than by what a kiosk pays, every
  other page here makes sense. Ship concept 1 into that frame and it lands. Ship it
  cold and it reads as trivia.
- **And it de-risks the expensive one.** If nobody engages with demand, concept 1's
  three days are three days better spent elsewhere. **That is worth knowing for one
  day's work.**

**Then concept 1, then 3, then 4.** I would build the Quality Ladder alongside
whichever of those ships first, because **it is the page that makes the others safe
to publish** — the moment concept 1 is live, somebody will read a quality claim into
it that we have not earned.

**I would not build 9 or 10 yet, and I would not build the Laser Bench at all until
someone decides §5 of concept 3.**

## 4. THE PHONE ONE

**Concept 4, the Deposit Field Guide.** It is the only one whose whole job happens
away from a desk: you are in the ship, the scan came back Shale, and you want to know
whether to stop. Filter-first, one card at a time, no chart, no side-by-side.

Concept 5 works on a phone too but is one input and a list, which is barely a page.
**Everything else here is two-column and wants a monitor.**

## 5. WHAT WE CANNOT BUILD YET — and what each would need

**The order says this list is worth as much as the ten. I agree, and it is where
most of the obvious mining ideas went.**

**Where the rocks are.** No coordinates, no field locations, no Aaron Halo bands.
**Would need:** a location dataset nobody has verified, or community submissions with
provenance. **SCMiner has a Halo navigator; we should not race it.**

**What anything sells for.** **CIG ships NO PRICES.** The only cost-like fields in
the entire export are `AmmoCost` and `CostPerBullet`. Every price on this site comes
from UEX, and **0 of 26,657 rows are verified.** **Would need:** a verification route
that does not exist. **A "where do I sell this" page is building on sand and must not
be built.**

**Where to sell it.** `commodity_trade_locations.json` is 96,717 entries and **looks**
like a where-to-sell dataset. It is not: every entry is tag-matched, and a "Security
Checkpoint" appears to trade all 109 commodities. **C1 nearly published a number off
it and the check is what stopped him. Do not build on it.**

**Refinery yields, times and method comparison.** Not in the game files at all.
**Would need:** in-game observation at scale. **This was Regolith's core and is now
SCMiner's work-order parser.**

**Live market stock.** Needs a backend and a live feed. **The site is static on
Cloudflare Workers with no read-time backend.** Out by architecture, not by effort.

**Actual yield from a real rock.** The files give a deposit's ranges, never an
instance. **Would need:** the client, or a scan-import route.

**THE ONE THAT IS ALMOST IN REACH — does mining quality survive refining?**
**Would need:** one in-game test. Mine a known-quality ore, refine it, craft with it,
read the stat. **4.10 is on Sleven's machine.** If that test comes back positive,
**concept 1 stops being a chain of identity and becomes a chain of consequence**, and
this site owns a question no tool in the hobby has asked. **It is one evening's work
and it is the highest-leverage unknown on this page.**

## 6. HOUSE STYLE — what I have assumed

Dark field, cyan and amber, monospace figures, disclosure bars folding the
explanation away until asked. **Every concept above puts the number always-visible and
the explanation behind a `▸`**, per the rule Code's audit settled: collapse a block
that EXPLAINS, never one that WARNS or states what you are looking at.

**Concept 8's middle panel is deliberately NOT collapsed.** It is a warning, not an
explanation.

**Everything here is client-side** — filters, sorts, sliders, hovers, local storage
for a remembered hold size. **No concept needs a server call.**

**No fuzzy matching anywhere.** Every join specified above is exact UUID equality, and
the one place a name join was tempting — mined "Aslarite (Raw)" against crafted
"Aslarite" — **is exactly where the UUIDs do NOT match**, because they are different
items at different refinement stages. **A name join there would have looked right and
been wrong.** That is the single best argument in this document for the rule.

## 7. WHAT I CHECKED AND WHAT I DID NOT

**Checked, by measurement, against the sealed 4.10 snapshot tonight:** all 557
resource records, their kinds, placeholder rate and field inventory; all 274 with a
Composition block — signature range, GlobalParams profiles, deposit names, element
counts, MinimumDistinctElements; all 206 commodities for RefinedVersionUUID, Tier and
QualityDistributionUUID; all 1,607 blueprints walked to their leaves for ingredients,
quantities, craft times, availability; the full rock→raw→refined→recipe chain by exact
UUID at every hop; the 23 WeaponMining items and one full MiningLaser block; every
figure in the order's §1.

**Checked on the live web tonight:** that Regolith Co has powered down, and what
SCMiner currently offers.

**Did NOT check:**
- **Whether mining quality survives refining.** §1d. **The most important open thing
  here and nothing may claim it.**
- **CIG's formula for combining laser and rock parameters.** Concept 3 shows both
  sides because of this.
- **The order's "23 ships with a mining or salvage port."** §0. I measured items, not
  ships, and the matching number is suspicious.
- **Whether the rarity-versus-demand mismatch in concept 9 is actually real.** I have
  both datasets and did not plot them. **Check before building.**
- **What the 298 `item` nodes in recipes point at.** Counted, not resolved.
- **Anything about where deposits physically are.** No such data was opened.
- **I have built nothing and changed no page.** This is a design document.
