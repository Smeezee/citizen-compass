# BUILD SPEC — the crafting surfaces (D2, D3, D4)

**From C2 to C1. 2026-08-02. Spec only — C2 wrote nothing to the repository.**

Companion to `claude/build-spec-descriptions-and-blueprint-index.md`, which
specifies Build 1 (item descriptions) and Build 2 (the blueprint index). **This
document assumes the blueprint index exists.** Everything here reads it and
nothing here parses `blueprints.json` or `contracts/` again.

Three surfaces:

    D2   Blueprint page     1,597 pages
    D3   Reverse lookup     "I have this. What can I make?"
    D4   Material pages     37 pages — SCOPE CUT, see §4

Every number below is measured output from a read-only run against the sealed
snapshots, not a prediction. **Four things I had previously planned turned out
to be wrong, and one of them removes half of D4.** They are in section 1.

---

## 1. WHAT VALIDATION CHANGED

### 1a. `commodity_trade_locations.json` does NOT tell you where to buy a material

`claude/plan-crafting-build-from-data-on-hand.md` §6 says this file gives
*"where it is sold"*. It does not.

Measured: Agricium, Titanium, Gold, Tungsten, Copper, Quantainium, Borase,
Aluminum, Laranite, Beryl, Taranite, Bexalite, Corundum, Hephaestanite and
Quartz **all have exactly 468 SoldAt locations, and the location sets are
byte-identical to each other.**

The reason is in the record itself — every entry carries
`MatchedTagName: "Commodity"` or `"Metal"`. **The file matches locations by
tag, not by stock.** It says "this place trades in commodity-tagged goods," not
"this place sells Agricium."

**Consequence: the "where to get it" half of D4 has no data behind it at all.**
Not stale data, not partial data — none. Combined with the absent commodity
prices, D4 shrinks to "what this material makes," which is still worth building
but is a smaller thing than planned. Section 4 reflects that.

### 1b. No ingredient has a refined version

Same plan section promised *"what it refines into"* from
`RefinedVersionUUID` / `RefinedVersionName`. Measured across the 26 ingredients
present in `resources/commodities.json`: **0 carry a RefinedVersionUUID.** The
field exists on the schema and is null for every material we care about.

### 1c. Six blueprints have no output at all

    BP_CRAFT_COOL_S04_CNOU_Pioneer                       source_kind = none
    BP_CRAFT_cds_combat_heavy_helmet_01_02_02            source_kind = direct_reward
    BP_CRAFT_cds_combat_superheavy_backpack_01_03_01     source_kind = contract
    BP_CRAFT_cds_combat_superheavy_helmet_01_03_01       source_kind = contract
    BP_CRAFT_cds_combat_superheavy_suit_01_03_01         source_kind = contract
    BP_CRAFT_cds_undersuit_01_02_02                      source_kind = direct_reward

`Output.UUID`, `Output.Name` and `Output.Type` are all null. **These pages
cannot show what they make, cannot link to an item, and cannot show a price.**
Three of them are reachable from real contracts, so they are not dead content —
the output just does not resolve in this extraction.

**Do not let these six 404 and do not let them render blank.** They should say
what they need and where they come from, and say plainly that the item they
produce is not identified in the game data.

### 1d. Output UUID is not unique — three pairs collide

    dabd2d8d  "FullForce"  PowerPlant    BP_CRAFT_POWR_LPLT_S02_FullForce  +  BP_CRAFT_POWR_SASU_S02_DayBreak
    dadc9318  "FoxFire"    QuantumDrive  BP_CRAFT_QDRV_ACAS_S01_FoxFire    +  BP_CRAFT_QDRV_JUST_S01_Goliath
    6fc982c0  "Glacis"     Shield        BP_CRAFT_SHLD_ORIG_S04_890J       +  BP_CRAFT_SHLD_RSI_S04_Polaris

1,597 blueprints resolve to **1,588 distinct outputs**. In each pair the two
blueprint keys name different products — DayBreak is not FullForce, Goliath is
not FoxFire, the 890J shield is not the Polaris shield — yet both point at the
same output UUID.

**Most likely a copy-paste error in CIG's data**, alongside the missing-`c`
reward key already recorded. **Not certain.** Treat item → blueprint as
many-to-many, show "2 blueprints make this" on the item page rather than picking
one, and do not silently deduplicate.

---

## 2. D2 — THE BLUEPRINT PAGE

1,597 pages. Reads the index only.

### 2.1 The problem that shapes the page

**Sources per blueprint, measured across the 676 contract-sourced ones:**

    min 1   median 6   p90 33   max 127

    1 source        135 blueprints
    2-5 sources     166
    6-20 sources    273
    21-50 sources    62
    51+ sources      40

**A page that renders one row per source produces a 127-row table to answer one
question.** Grouping is not a nicety here, it is the design.

Also measured: **22 distinct mission givers** overall, and **68 blueprints are
awarded by more than one giver** (max 9 different givers for a single
blueprint).

    Shubin Interstellar  2,760      Eckhart Security       291
    Headhunters          1,361      Bit Zeros              280
    Citizens for Prosperity 792     Recco Battaglia        269
    Foxwell Enforcement    761      InterSec Defense Sol.  207
    United Wayfarers Club  656      FTL Courier            156

    Mission types: Mercenary 3,179 · Ship Mining 2,658 · Refueling 656 ·
    Bounty Hunter 456 · Delivery 335 · Hauling 172 · Salvage 150 · Hand Mining 102

**Worth noticing:** Ship Mining is the second-largest source of blueprints.
Crafting is not a combat-only loop, and the page should not read as though it is.

### 2.2 Page structure

1. **Answer line.** *"Crafts an Omnisky III Cannon in 9 minutes. Most easily
   from Shubin Interstellar mining contracts."*

2. **What it makes.** Name, type, grade, link to the item page. If a shop price
   exists: *"Or buy it outright for 14,845 aUEC at Ship Weapons CRU-L5."*
   Measured: **721 of 1,597 blueprint rows carry a price.**
   **If `output_uuid` is null (6 pages) this whole block is replaced by a plain
   statement that the output is not identified in the data.**

3. **What it needs.** Ingredients grouped by component group. Group names are
   real and readable — Frame, Emitter, Aperture Iris, Insulative Liner, Armored
   Carapace, Shell, Barrel.
   - `resource` leaves show a quantity in SCU.
   - **`item` leaves show no quantity — `QuantityScu` is null on all 298 of
     them.** Render the name alone. Never print "null SCU".
   - Every leaf has `MinQuality`; show it where it is above the floor.
   - **No cost column. No total.** See §5.

4. **What quality does.** The `modifiers` table — stat, value at minimum
   quality, value at maximum. Measured: **1,537 of 1,597 carry at least one
   modifier; 60 carry none** (36 WeaponAttachment, 17 Char_Armor_Backpack,
   3 Misc, 3 Char_Armor_Legs, 1 Cargo). The section must disappear cleanly on
   those 60 rather than render an empty table.

5. **Where the blueprint comes from** — by `source_kind`:

   - **`contract` (676).** Lead with the *best* source: highest `Chance`, then
     lowest `MinReputation`. Then a grouped summary — *"Also awarded by 126
     other Mercenary and Ship Mining contracts from Shubin Interstellar and 3
     others."* Full list behind a disclosure, never inline.

     Each source shows: contract title, giver, mission type, lawful or unlawful
     (`Illegal` — measured 7,571 false, 776 true), drop chance
     (**measured 8,283 at 1, 53 at 0.25, 11 at 0.75**), and the reputation gate
     rendered from `ReputationPrerequisite`:

         "Needs Sr. Contractor standing with InterSec Defense Solutions."

     built from `MinStanding.Name` and `Faction`. The raw numbers
     (`MinReputation: 5800`) are available if wanted but the name is the answer.

     **There is no payout to show.** `CalculatedReward` is a boolean — measured
     8,260 true, 87 null, no numbers anywhere in the field.

   - **`event` (31).** *"Reward from the XenoThreat event"* — and for the 25
     XenoThreat entries the pool key carries the contribution tier
     (`_15_`, `_25_`, `_50_`, `_60_`, `_85_`, `_100_`), so say which.
     The 6 RedWind entries: *"Reward from RedWind Linehaul."*
     **Caveat on record: whether RedWind's contracts carry a `Blueprints` array
     was never checked.** If they do, those 6 are misclassified.

   - **`direct_reward` (16) and `default` (8).** Stated plainly.

   - **`other_pool` (1).** The Microsatellite probe. It exists so nothing falls
     through silently.

   - **`none` (865).** ***"We don't know how you get this blueprint."***
     Verified against all 5,108 contracts, so this is a finding, not a hedge.
     **54% of all blueprint pages say this.** It has to read as confident.
     Suggested wording, and the reason for it: *"Nothing in the game files says
     how this blueprint is obtained. It may come from an event, or it may not be
     available yet."* — states what we checked, offers the two live
     possibilities, claims nothing.

6. **Provenance line.** Patch stamp and source, same as every page.

---

## 3. D3 — REVERSE LOOKUP

The cheapest genuinely-new thing in the crafting area. **Needs no data beyond
the index.** None of the four competing tools inverts the question.

### 3.1 The inverted index — all 37 ingredients, measured

    856  resource  Aslarite            83  resource  Borase
    495  resource  Ouratite            82  resource  Torite
    341  resource  Laranite            75  resource  Silicon
    261  resource  Tungsten            73  resource  Corundum
    228  resource  Iron                71  item      Dolivine
    194  resource  Agricium            63  resource  Gold
    145  resource  Taranite            58  item      Hadanite
    137  resource  Stileron            51  resource  Tin
    122  resource  Hephaestanite       38  resource  Aluminum
    113  resource  Lindinium           37  item      Sadaryx
    101  resource  Titanium            34  item      Beradom
     96  resource  Copper              33  resource  Beryl
     92  resource  Pressurized Ice     32  item      Aphorite
     88  resource  Savrilium           28  resource  Quartz
     84  resource  Riccite             25  resource  Bexalite
                                       25  item      Glacosite
                                       16  item      Janalite
                                        9  item      Feynmaline
                                        8  item      Carinite
                                        7  item      Saldynium (Ore)
                                        3  resource  Quantainium
                                        1  item      Yormandi Eye

**37 total. A plain multi-select covers the entire space** — no search box, no
autocomplete, no infrastructure.

### 3.2 Behaviour

- Tick what you are carrying. 26 resources and 11 hand-mined gems, visually
  separated because they are acquired completely differently.
- Two result lists, and **the second is the more useful one**:
  - **"You have everything for these."**
  - **"You're one short."** — with the missing ingredient named. This is what
    turns the page from a lookup into a plan.
- Sort by the output's shop price, descending, so the most valuable thing the
  pile makes is at the top. **Only 721 of 1,597 have a price** — unpriced rows
  sort last, never interleaved with a blank.
- Quantities are deliberately ignored. The data gives `QuantityScu` per recipe
  but the player's hold size is unknown and 298 leaves have no quantity at all.
  **Match on presence, not amount, and say so on the page.**
- Every row links to its blueprint page.

### 3.3 Why it works

Aslarite is in **856 of 1,597 blueprints** — 54%. Ouratite 495, Laranite 341.
A player who just finished a mining run is holding common ore and has hundreds
of answers. The value is not the list, it is the ranking and the "one short"
column.

**State the scope limit plainly on the page:** this matches ingredients, not
whether you have the blueprint. A player can be shown something they cannot yet
craft. That is still useful — it tells them which blueprint to go get — but it
must not pretend otherwise.

---

## 4. D4 — MATERIAL PAGES (scope cut)

37 pages. **Reduced by §1a and §1b to essentially one good section.** Build it
anyway — it is the only surface in the project that speaks to miners, and it is
the bridge between the mining audience and the gear audience.

**What is real:**

- **What it makes.** The inverted index from §3.1, ranked by output shop price.
  For Aslarite that is 856 blueprints, so it needs the same grouping discipline
  as D2 — summarise by output type, disclose the full list.
- **Name and description.** Measured: **all 26 resource ingredients present in
  `resources/commodities.json` carry a real Name and Description** — no
  placeholders. `labels.json` holds 552 `items_commodities_*` keys as a
  secondary source. **My name-match against those labels was fuzzy and I do not
  trust the 37-of-37 hit rate it reported — verify per material before relying
  on it.**
- **Container sizes.** All 26 carry `CargoContainers[]` — 1 / 2 / 4 / 8 / 16 SCU.
- **The 11 hand-mined gems are not in `commodities.json` at all.** Those pages
  get the "what it makes" section and nothing else. Say why: they are hand-mined,
  not traded as cargo.

**What is NOT available and must not be faked:**

- Where to buy it — §1a. The tag-matched location list is not stock data.
- What it costs — no commodity price rows exist on disk.
- What it refines into — §1b, zero coverage.
- Where to mine it — not in any file examined.

**Leave those four slots in the template, empty and labelled.** Three of them
open up the moment commodity prices land; the mining-location one needs a source
that does not currently exist and should be recorded as an open data gap.

---

## 5. STILL FENCED OFF

**Anything requiring an ingredient cost.** Zero commodity price rows on disk,
verified twice. That fences off the craft-vs-buy verdict, any total-cost figure,
the materials shopping trip, and cost-per-improvement ranking.

Keep `ingredient_cost` in the schema, keep it null, and assert it stays null
(§6). **Do not ship an estimate.**

**Grind-route planning stays out of scope by decision.** CmdrQuattro's tool owns
it. Link out.

---

## 6. VERIFICATION — HARD RULE 12

Exact, not greater-than-zero. A check that cannot fail is not a check.

- **D2: assert the six null-output blueprints render a complete page.** Named in
  §1c. This is the empty-state test that matters most, because three of them are
  reachable from real contracts and will get traffic.
- **D2: assert a 127-source blueprint renders without a 127-row table.** Take
  the max-source blueprint from the index and assert the rendered source count
  is bounded.
- **D2: assert an `865`-group page renders complete with no source block.**
  54% of pages.
- **D2: assert the modifier section is absent, not empty, on all 60 rows that
  carry no modifiers.**
- **D2: assert no payout figure appears anywhere.** `CalculatedReward` is
  boolean; a number on screen means something invented it.
- **D3: assert the ingredient list is exactly 37**, and that ticking Aslarite
  alone returns 856 blueprints.
- **D3: assert the "one short" list is non-empty for a single-ingredient
  selection** — otherwise the logic has collapsed into the "have everything"
  case.
- **D4: assert no material page renders a buy location or a price.** This is the
  §1a guard. The tag-matched data is present and will look plausible if someone
  wires it up by mistake.
- **All: assert `ingredient_cost` is null on all 1,597 rows.**
- **All: assert no name-based join exists.** 35 of 37 ingredient names match UEX
  commodity names exactly. It will work. It is still forbidden — use the
  `resources/commodities.json` UUIDs, which cover 26 of 37 properly, and leave
  the other 11 unjoined rather than matching on a string.

---

## 7. WHAT I DID NOT VERIFY

- **Whether RedWind's contracts carry a `Blueprints` array.** Six blueprints are
  classed `event` on the pool key alone.
- **Whether the three colliding output UUIDs are a CIG error or intentional.**
- **Whether the six null outputs resolve in a newer extraction.** The snapshot is
  from 2026-08-01; the game is on 4.9.
- **`CategoryUUID` on blueprints** — never resolved to a name. It may give a
  better grouping for D2 than `output_type`.
- **The `items_commodities_*` label match** — fuzzy, see §4.
- **Whether mining locations exist in any file** — the `Kind: cave_harvestable`
  entries in `resources/resources.json` (557 records) were seen but not opened.
  **That is the most likely home for the missing mining-location data and is
  worth ten minutes before D4 is called complete.**

---

## 8. REFERENCE IMPLEMENTATION — the derived views

Read-only. Reads `blueprint_index.json` from Build 2 and writes two small
lookup files. Neither touches a snapshot.

```python
import json, os, collections

ROOT  = r"C:\Users\david\citizen-compass"
INDEX = os.path.join(ROOT, r"data-layer\processed\blueprint_index.json")
OUT   = os.path.join(ROOT, r"data-layer\processed")

with open(INDEX, encoding="utf-8") as fh:
    rows = json.load(fh)

# ---- D3: ingredient -> blueprints -----------------------------------------
inverted = collections.defaultdict(list)
kinds    = {}
for r in rows:
    for name in {i["name"] for i in r["ingredients"]}:
        inverted[name].append(r["blueprint_uuid"])
    for i in r["ingredients"]:
        kinds[i["name"]] = i["kind"]

ingredients = [
    {
        "name": name,
        "kind": kinds[name],                    # resource | item (hand-mined)
        "blueprint_count": len(uuids),
        "blueprints": sorted(uuids),
    }
    for name, uuids in sorted(inverted.items(), key=lambda kv: -len(kv[1]))
]

with open(os.path.join(OUT, "ingredient_index.json"), "w", encoding="utf-8") as fh:
    json.dump(ingredients, fh, ensure_ascii=False, indent=1)

# ---- D2: source summary per blueprint -------------------------------------
def summarise(r):
    """Collapse up to 127 contract sources into one displayable block."""
    srcs = r["sources"]
    if r["source_kind"] != "contract" or not srcs:
        return None

    def rep_floor(s):
        rep = s.get("reputation") or {}
        return ((rep.get("MinStanding") or {}).get("MinReputation") or 0)

    best = sorted(srcs, key=lambda s: (-(s.get("chance") or 0), rep_floor(s)))[0]
    givers = collections.Counter(s.get("giver") for s in srcs)
    types  = collections.Counter(s.get("mission_type") for s in srcs)
    rep    = (best.get("reputation") or {})
    standing = (rep.get("MinStanding") or {}).get("Name")

    return {
        "total": len(srcs),
        "best": {
            "title":        best.get("title"),
            "giver":        best.get("giver"),
            "mission_type": best.get("mission_type"),
            "chance":       best.get("chance"),
            "illegal":      best.get("illegal"),
            "standing":     standing,
            "faction":      rep.get("Faction"),
        },
        "givers":        givers.most_common(),
        "mission_types": types.most_common(),
        "others":        len(srcs) - 1,
    }

summary = {r["blueprint_uuid"]: summarise(r) for r in rows}
with open(os.path.join(OUT, "blueprint_sources.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=1)

# ---- hard rule 12 ----------------------------------------------------------
NULL_OUTPUT = 6
assert len(ingredients) == 37, f"ingredients {len(ingredients)}"
assert ingredients[0]["name"] == "Aslarite" and ingredients[0]["blueprint_count"] == 856
assert sum(1 for i in ingredients if i["kind"] == "item") == 11, "hand-mined count moved"
assert sum(1 for r in rows if not r["output_uuid"]) == NULL_OUTPUT, "null-output count moved"

outputs = collections.Counter(r["output_uuid"] for r in rows if r["output_uuid"])
assert len(outputs) == 1588, f"distinct outputs {len(outputs)}"
assert sum(1 for v in outputs.values() if v > 1) == 3, "output collisions moved"

contract_rows = [r for r in rows if r["source_kind"] == "contract"]
assert max(len(r["sources"]) for r in contract_rows) == 127, "max sources moved"
assert all(r["ingredient_cost"] is None for r in rows), "something invented a cost"

print("ingredients:", len(ingredients))
print("null-output blueprints:", NULL_OUTPUT, "| output collisions: 3")
print("max sources on one blueprint:", max(len(r["sources"]) for r in contract_rows))
print("OK ->", OUT)
```

**On the assertions.** They are exact on purpose and they will break when the
game patches. **That is the signal, not the bug.** Update the numbers
deliberately, with a note recording which patch moved them.
