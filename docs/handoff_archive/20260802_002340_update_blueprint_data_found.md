# Blueprint/crafting data found — and the one pull that unblocks it. 2026-08-02, C2

Full detail: `claude/finding-blueprints-crafting-data.md` on claude.ai.
Read-only investigation. **C2 wrote nothing to the repository.**

## What is on disk

`scunpacked-data/snapshots/20260801T204744Z/blueprints.json` — **1,597
blueprints**, plus a `blueprints/` folder with one file each. All
`Kind: "creation"`, all single-tier.

Per blueprint: `Output` (UUID/Class/Type/Subtype/Grade/Name), `CraftTimeSeconds`,
`Availability` (`Default` + `RewardPools[]`), and a `Requirements` tree of
`root → group → resource|item` with `QuantityScu` and `MinQuality` per leaf.

Groups are named parts — Insulative Liner (853), Armored Carapace (451),
Frame (272), Shell (233), Barrel (98). Each group carries stat `Modifiers` with a
`QualityRange` 0–1000 mapped to a `ModifierRange`: craft quality shifts real
stats, e.g. `health_maxhealth` 0.9×–1.1×, `weapon_damage` 0.95×–1.05×.

Craftable output: armor 684, personal weapons 174, ship guns 96, power plants 75,
coolers 74, shields 62, radar 60, quantum drives 57, plus attachments and tools.

Ingredients: **37 distinct**. 26 join by UUID to `resources/commodities.json`
(Aslarite alone appears in 856 blueprints). The other 11 are `Kind: "item"`
hand-mined gems — Hadanite, Dolivine, Aphorite, Sadaryx and so on — **not** in
`commodities.json`.

Acquisition: **8** blueprints are `Default: true`. **724** come from named
reward pools. **865 have neither** — the data does not say how you get them.

## The join works — 719 items

`Output.UUID` → `items_prices_all.json.item_uuid` matches on **719 of 1,588
craftable items.** Proper UUID join, no name matching. Spot-checked:
`BP_CRAFT_AMRS_LaserCannon_S1` → `26838ca7-...` "Omnisky III Cannon" →
`id_item 1`, 15,461 aUEC at CenterMass Area 18.

That supports craft-vs-buy on 719 items, which nothing else on the market does.

## THE BLOCKER — no commodity prices exist anywhere on disk

Verified twice:

- `items_prices_all.json` has **zero** rows in the Commodities section. All
  23,734 rows are gear/component sections.
- `resources/commodity_trade_locations.json` (41 MB, 109 commodities) lists
  **where** commodities are sold, with **no price field**.

The 2026-08-01 UEX pull covered `/items/` and vehicle purchase prices and did not
include commodity prices. **Recommend pulling them.** It is the highest-value
single data addition found so far: it completes craft-vs-buy AND fills the
"how much does RMC sell for" intent that the item-page plan currently cannot serve
(only 171 of 7,728 items have a sell price).

Second, smaller gap: the 11 hand-mined gems are not commodities and would still
be unpriced. ~30% of recipes would remain partially costed — state that on the
page rather than estimating.

## Worth testing, cheap

**`RewardPools` → `contracts/` join.** Pool keys look mission-related
(`BP_REWARDS_FullStrikeOnStationB`). If it resolves, "where do I get this
blueprint" becomes answerable. Not attempted.

## Not verified

- Whether 4.9 changed crafting. Confirmed by search that crafting/blueprints are
  live since 4.8; did not read 4.9 notes in detail. Snapshot is from 2026-08-01.
- **A community blueprint-finder tool already exists**, posted on RSI's Community
  Hub. Not evaluated. Look before building — same call as Star Binder.
- What the 865 no-default-no-pool blueprints mean.
- `CategoryUUID` not resolved to names.

## Closing an open item: `tags.json` checked, does not help

Flagged as unopened in `claude/plan-doorways-and-browse-layer.md` §2.
It is a dict of **18,844** UUID → {name, parent_uuid}, 70 roots — the engine's
internal tag tree, not a consumer taxonomy. Largest branches: `ItemPorts` 809,
`SpawnCloset` 247, `DefendArea` 246. Roots include `Subsumption`,
`PopulationManager`, `EntitySpawner_Printing`.

**It does not replace the proposed tag model** — that section of the doorway plan
stands. Four subtrees worth mining later: `LocationType` 147, `MissionType` 101,
`Series` 96, `Manufacturer` 90.
