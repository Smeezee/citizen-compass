# UPDATE — WO-1 and WO-2 complete. All assertions hold, including C1's three unverified numbers.

## Preconditions

`categories.json` `3de4f9fa2bf7674d`, `items_prices_all.json` `308542bf043df9c2`
— both match. Sealed snapshots intact. blueprints 1597, contracts 5108.

## WO-1 — PASS

| assertion | got | want |
|---|---:|---:|
| matched | **5344** | 5344 |
| fps records with text | **5182** | 5182 |
| ship records with text | **2598** | 2598 |
| UEX items | **7728** | 7728 |

Join is UUID-only by construction; no name match is possible in that code path.
Output 2.05 MB.

## WO-2 — PASS. The three unverified numbers CONFIRM.

**This was C2's verification and it holds:**

| assertion | got | want |
|---|---:|---:|
| contracts carrying `Blueprints[]` | **768** | 768 |
| blueprints with >=1 contract | **676** | 676 |
| **max sources on one blueprint** | **127** | 127 |

C1's reconciliation arithmetic was right: the numbers only closed if these were
correct, and they are.

Every remaining assertion also holds — rows 1597, the full `source_kind`
distribution, 4274 leaves, 298 lacking QuantityScu and all `item`, every leaf
with MinQuality, 721 priced, 1537 with modifiers, `ingredient_cost` null
throughout.

**Performance:** the contract scan took **1.5 seconds**, not the 45+ a naive
scan costs. The substring pre-filter cut 5,108 files to 768 — and 768 qualifying
on `"PoolUUID"` is exactly the count that carry `Blueprints[]`, so the filter is
lossless here rather than merely fast.

## FILE SIZE — this bears on the static-JSON ruling

**`blueprint_index.json` is 11,439,463 bytes — 10.91 MB.**

The ruling assumed page-sized payloads. This is one file, and the `sources[]`
arrays are why: 676 blueprints carry contract sources, up to 127 each.

It does not reverse the ruling — the ruling rests on zero runtime dependency,
not on payload size — but **10.91 MB is not a page payload.** WO-3 reads WO-2,
and if a blueprint page fetches this file to render one row, that is 10.91 MB to
show one blueprint. The shape that works is per-blueprint shards or an index
plus lazy source fetch. Flagging now because it is cheaper to decide before 1,597
pages are built on it than after.

Not tracked in git: `data-layer/processed/.gitignore` added, on the same
reasoning as `journal.jsonl` and `*_perfile.json` — large, fully reproducible
from tracked sealed snapshots, with exact assertions recorded in the work order.

## OPEN ITEM 1 — SETTLED. `resources.json` does NOT hold mining locations.

Opened all 557 records. **The union of every key across every record is:**

```
AdditionalWaitForNearbyPlayersSeconds, Composition, DespawnTimeSeconds,
GlobalParams, HarvestableKey, HarvestableUUID, Key, Kind, Name, Parts,
RespawnInSlotTime, Signature, Tier, UUID
```

**No planet, moon, system, body, region, deposit or site field exists.** The
hypothesis is disproven. "Where to mine it" stays empty in WO-5 — but now for a
*verified* reason rather than "no source found", which is a materially better
thing to be able to say on 37 pages.

### But it is not a dead end — it answers a different question

`Kind` distribution: **cave_harvestable 244, mineable 274, salvageable 25,
harvestable 14.**

That is *how* a material is obtained, which is precisely the distinction WO-5
needs for the 11 hand-mined gems ("hand-mined, not traded as cargo"). Currently
that split is asserted from their absence in `commodities.json` — an argument
from silence. `Kind` would make it positive evidence.

14 of the 37 ingredients appear here by name. **I did not join on name** —
FORBIDDEN 1. Records carry `UUID` and `HarvestableUUID`, so a UUID join is
available and is the only one I would use.

**Data-quality note:** many `cave_harvestable` records carry
`Name: "<= PLACEHOLDER =>"`. Any page reading `Name` from this file must handle
that, or placeholder text ships to users.

## VOCABULARY RECONCILIATION — reporting, not picking

C2's `source_kind` (blueprints) and the acquisition routes (ships, paints,
editions) are the same question — *how do you get this* — arriving from two
directions.

**Proposed: two levels. Level 1 is the honest one-line answer; level 2 keeps the
precision neither side should lose.**

| L1 | L2 | covers |
|---|---|---|
| **bought** | `shop` | aUEC at a named terminal — UEX prices, dealer columns |
| | `pledge` | real money on the RSI store |
| | `trade` | exchanged for goods, not currency — Wikelo Emporium |
| **awarded** | `mission` | completing contracted work — C2 `contract`, 676 |
| | `event` | time-limited event — C2 `event`, 31 (XenoThreat, RedWind) |
| | `reward` | status or standing, no specific action — C2 `direct_reward` 16, `other_pool` 1, plus Subscriber/Concierge |
| **included** | `factory` | arrives fitted, never separately obtained — War/Sneak Specials |
| | `default` | available without acquisition — C2 `default`, 8 |
| **unknown** | `unknown` | the files do not say — C2 `none`, **865** |

**Why two levels rather than one flat list.** Your point was that a
contract blueprint and a Subscriber livery are both "awarded, not bought". At L1
that is one word and the site can say it once. At L2 they stay distinguishable,
because *how* you earn them differs completely. A single flat vocabulary forces
a choice between losing the shared idea and losing the distinction.

**Mapping is total and lossless in one direction:** every C2 value and every
acquisition route maps to exactly one L2 term, and no L2 term is unreachable.
`other_pool` folds into `reward` — it is one row, the Microsatellite probe, and
"awarded by some pool we cannot classify" is a `reward` with low confidence, not
a category.

**`unknown` deliberately keeps its own L1.** Folding it under any of the other
three would assert something the files do not support — 865 blueprints, 54%, is
far too much to guess about.

**Not implemented.** WO-2's output currently carries C2's `source_kind` verbatim
so the assertions could be verified exactly as written. Remapping is a
mechanical pass once the vocabulary is ruled — and it must happen before WO-3
renders any of it, or the two taxonomies ship.

## Stopping here

WO-3 (1,597 pages), WO-4 and WO-5 are not started. WO-3 renders `source_kind`
prose, so it is downstream of the vocabulary ruling, and the 10.91 MB payload
shape should be settled before pages are built against it.
