# Crafting build plan filed + 48 dangling pools resolved + item descriptions found
2026-08-02, C2. Read-only. **C2 wrote nothing to the repository.**

Plan: `claude/plan-crafting-build-from-data-on-hand.md` on claude.ai.
Everything in it runs on data already collected, gated and sealed. No new
acquisition needed.

## BIGGEST ITEM — item descriptions exist, 69% coverage

`claude/front-end-build-plan-2026-08-02.md` §3 says *"No 'what it's good for' or
'how to use it'. That is writing, not data."* **Wrong.**

`fps-items.json` and `ship-items.json` carry `stdItem.Description` and
`stdItem.DescriptionText`:

    fps-items with a description       5,182 of 5,420
    ship-items with a description      2,598 of 5,384
    combined uuid -> description       7,780
    UEX items that gain one            5,344 = 69% of catalogue, 96% of uuid-carrying

`labels.json` separately holds 5,805 `item_Desc_*` keys (5,558 with content) and
4,749 `item_Name_*`, some with stat blocks ("Damage Reduction: 40%, Temp. Rating
-80/105 °C").

**Description coverage (69%) beats price coverage (36%) and images (0%).** This
is the cheapest large improvement available in the project right now and it
benefits 5,344 item pages. Priority order: `stdItem.DescriptionText` →
`Description` → `labels.json item_Desc_*` (label path keys on class name, not
UUID — prefer UUID).

## The 48 dangling pools — resolved, and not broken

    25  XenoThreat event rewards  (BP_REWARDS_Xenothreat2_15_01 ... _100_03)
        XenoThreat is a real faction, 357 labels. Numbers are contribution
        tiers. Event rewards, not contracts — hence no contract awards them.
    16  1:1 mirror keys — BP_REWARD_<x> mirrors BP_CRAFT_<x> exactly.
        All "SecondWind" / "Purgatory Camo" cosmetic variants.
     6  RedWind — RedWind Linehaul delivery contractor, 118 labels.
        NOT CHECKED whether its contracts carry a Blueprints array.
     1  Microsatellite probe mission item.

**"Dangling" was the wrong word — these are obtainable by non-contract routes.**
Site wording should be "event reward" / "special reward", never "unobtainable".

**The 865 no-pool-no-default group remains genuinely sourceless** — zero
reachable across all 5,108 contracts.

## Defect in CIG's own data — worth a bug report

Three reward keys reference blueprints that do not exist under the mirrored name:

    BP_REWARD_ds_combat_medium_helmet_01_02_01   <- missing a 'c'
        actual blueprint: BP_CRAFT_cds_combat_medium_helmet_01_02_01
    BP_REWARD_CollectorMaterial_001
    BP_REWARD_CollectorMaterial_002

Arms, core and legs of that ORC-mkX SecondWind set all use the correct `cds_`
prefix; only the helmet is misspelled. If rewards resolve by this key, that
helmet cannot drop while the rest of its set can. **Not certain enough to
publish. Certain enough to report.**

## Build order in the plan

1. **D1 blueprint index** — one derived table, 1,597 rows, everything reads it.
2. **Wire item descriptions into the item template** — 5,344 pages, independent
   of crafting.
3. **D2 blueprint pages** — 1,597 pages, source/ingredients/quality curve.
4. **D3 reverse lookup** — "I have this, what can I make?" 37 materials, no new
   data, and none of the four competing tools inverts the question.
5. **D4 material pages** — 37 pages, better after prices land.

## Fenced off until commodity prices land

Zero commodity price rows exist on disk (verified twice). No craft-vs-buy
verdict, no total cost, no shopping trip, no cost-per-improvement. **Build the
templates with the slot present and empty** so it stays a data change, not a
redesign. Do not ship an estimate.

Also out of scope by decision: grind-route planning — CmdrQuattro's tool owns it.

## Performance warning for whoever implements D1

Scanning 5,108 contract files naively exceeds 45s. One pass; substring-test for
`"PoolUUID"` before parsing JSON; do not loop the 146 pool keys against every
file. That approach timed out twice here.

## Parked, not actioned

Contacting CmdrQuattro and the other three maintainers about a mutual link or
data exchange. Revisit only after commodity prices land — until then we have
nothing to offer. Terms of use to be read by a person first.
