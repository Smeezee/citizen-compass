# ORDER — craft-or-buy is built and inert. It needs one line in `deploy_pages.py` and one script tag, both yours.

**2026-08-27 23:25 local · C1** — Sleven: *"work non-stop, you have the
authority to fix it and make it work."* This is the first of the economy
features from `BRIEF_stop-being-a-better-list`.

## What exists now

**`build_crafting_demand.py`** (new, mine) reads CIG's 1,607 crafting recipes
and writes `data-layer/derived/crafting-demand/`:

    demand.json        37 materials, what each is used for, SCU and count kept apart
    recipes.json       every recipe: output, craft time, requirement tree, dismantle
    part_recipes.json  the join to THIS page's parts
    craft_data.gen.js  page-ready: const CRAFT, const CRAFT_DEMAND
    MANIFEST.json      source snapshot and the three rules below

    ship-page parts that are craftable:  452 of 3,283

**The join is CIG's own `Output.Class`, case-folded, exact.** The page keys its
parts `AMRS_LaserCannon_S1`; the blueprint says `amrs_lasercannon_s1`. Same
identifier, different capitalisation.

**The display-name route is refused and that is deliberate.** It would add 34
more, and one of them is `AMRS_AAgun_CC_S3` claiming the PyroBurst Scattergun's
recipe - a different class wearing a shared display name. **452 exact beats 486
with a wrong one in it.**

**Two units are never added together.** A `resource` is cargo in SCU; an `item`
is a count. 0.36 SCU of Agricium and 7 Hadanite are not 7.36 of anything. The
recipe COUNT is the only figure that spans both, which is why it leads.

**Tier 0 only.** Higher tiers are the same build at better quality and would
double-count every material in them.

## What it puts on the page

A quiet line under each part in the picker, where the decision is actually made:

    Craftable · 9 min · blueprint must be earned
    Agricium 0.36 SCU, Hadanite ×7, Dolivine ×7

**IT IS INERT RIGHT NOW AND THAT IS BY DESIGN.** `craftLine()` returns an empty
string when `CRAFT` is undefined - not an empty box, not an apology. The page is
shippable today whether or not you wire the data, and nothing changes visually
until you do.

## The one thing I need from you

    1. deploy_pages.py     add craft_data.gen.js to PAGES
    2. loadout.src.html    a <script src="craft_data.gen.js"> before the page
                           script  -- tell me where you want it and I will add
                           it, or add it yourself
    3. build_deploy.py     call the generator so the file regenerates:
                           python build_crafting_demand.py --emit-js=<path in _src>

**Shape is yours.** I have not touched `deploy_pages.py` or `build_deploy.py`,
and given the rule 14 question is still open I am not going to.

## And the fleet-wide half, which has no home yet

`CRAFT_DEMAND` is the mining answer nobody has:

    Aslarite        856 recipes    Iron           258
    Ouratite        495            Agricium       194
    Laranite        353            Taranite       145
    Tungsten        266            Stileron       141

Each row carries what the material is actually FOR, read off the recipe group
that consumes it - Aslarite is Min/Max Temp, Ouratite is Damage Mitigation and
Impact Force. **A miner deciding what to fill a hold with has nothing that tells
them this.** It wants a page of its own and that is a bigger conversation than
one line; the data is ready when it happens.

## Checks

`_verify_ship_page`, `_verify_part_rows`, `_verify_stage_panel`,
`_verify_look_panel`, `_verify_marker_coverage` — all exit 0.

— C1
