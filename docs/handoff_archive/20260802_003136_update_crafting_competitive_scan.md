# Crafting category is already crowded — four live tools. 2026-08-02, C2

Full scan + eight design approaches: `claude/crafting-competitive-scan-and-approaches.md`
on claude.ai. Read-only. **C2 wrote nothing to the repository.**

## Four live competitors, all fan-made

1. **citizen-starter-guide.com/star-citizen-blueprint-finder/** — CMDR Quattro.
   Posted to RSI Community Hub (27 upvotes). Search all blueprint types; pooled
   armor sets; **gives the exact MobiGlas tab, faction and contract title per
   blueprint**; 4.8 grind-route planner that sequences contracts, respects
   reputation gates and inserts rep contracts. Stanton/Pyro/Nyx filter,
   lawful/unlawful badges, payouts.
2. **sc-craft.tools** — Norkaan / HTTPS org. 1,000+ blueprints, ownership
   tracking, filter by mission/contractor/resource/system. **Models quality
   modifiers on stats** (damage mitigation, temp resistance, fire rate, recoil).
   "Updated every patch."
3. **star-crafting.com** — 266 blueprints, 247 materials, 156 locations, 2,915
   Finder records, community submissions. States coverage openly: "0/11
   locations mapped".
4. **sccraftlab.com** — blueprints, ships, components, mining calculator,
   missions, Executive Hangar PowerCycle, universe explorer. Crafting queue,
   inventory, rep tracking, org libraries — **behind registration.** Roadmap
   includes an AI assistant, 2026-2027.

## The gap, and it is consistent

**None of the four shows a price.** No ingredient cost, no craft-vs-buy, no
market data at all. star-crafting has 156 locations and 0 of 11 mapped;
sccraftlab has a mining calculator and no prices.

Reason is structural: recipe data is static and shippable, prices need a live
feed and honest tolerance. **We already hold 23,734 item prices and a verified
UUID join to 719 craftable outputs.** This is the only defensible angle.

Two secondary gaps: no-login (sccraftlab gates its best features), and nobody
connects crafting to a specific player's ship.

## Correction to my own claim from earlier today

I said crafting quality/stat modelling was something nobody does. **Wrong.**
sc-craft.tools advertises exactly that. I claimed a differentiator from what the
data allowed without checking what competitors ship — third time this week I have
reasoned from a proxy instead of the artifact.

## Consequence for build order

Do not build a fifth recipe database. The three ideas worth pursuing (craft-vs-buy
verdict, the materials trip, resource-as-destination pages) are **all blocked on
the same single item: pulling UEX commodity prices.** That reinforces the
recommendation already filed in `inbox/update_blueprint_data_found.md`.

One idea needs no new data and is genuinely unserved: **reverse lookup** — "here
is what is in my hold, what can I make?" All four tools filter *by* resource;
none inverts it. Aslarite alone appears in 856 of 1,597 blueprints.
