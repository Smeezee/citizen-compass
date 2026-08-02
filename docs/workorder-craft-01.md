# WORK ORDER — item descriptions + the crafting surface

    id            WO-CRAFT-01
    raised by     C2 (Cowork), 2026-08-02
    for           C1 -> Claude Code
    scope         5 tasks, WO-1 .. WO-5, in order
    blocked by    nothing
    repo writes   C2 made none

Supersedes the narrative versions in `claude/build-spec-descriptions-and-blueprint-index.md`
and `claude/build-spec-crafting-surfaces.md`. Those carry the reasoning; this
carries the work. Where they disagree, this wins.

---

## PRECONDITIONS

    SC   data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/
    UEX  data-layer/external-sources/uexcorp/snapshots/20260801T235530Z/

Both sealed, read-only. Verify before starting:

    UEX/categories.json        sha256 starts 3de4f9fa2bf7674d
    UEX/items_prices_all.json  sha256 starts 308542bf043df9c2

Mismatch = a sealed snapshot was modified. Stop and report.

---

## WO-1 — item description map

**In:** `SC/fps-items.json` (5,420), `SC/ship-items.json` (5,384),
`UEX/items_category_*.json` (7,728 across 100 files)
**Out:** `data-layer/processed/item_descriptions.json`

Join on UUID only. `UEX .uuid` = `stdItem.UUID`, falling back to `.reference`.
Text priority: `stdItem.DescriptionText` → `stdItem.Description` →
`labels.json` key `item_Desc_<ClassName>` (class-name keyed, use last).

**Accept:**

    matched == 5344            (69% of catalogue, 96% of uuid-carrying items)
    fps records with text      == 5182
    ship records with text     == 2598
    zero matches made by name

---

## WO-2 — blueprint index

**In:** `SC/blueprints.json` (1,597), `SC/contracts/*.json` (5,108),
`UEX/items_prices_all.json`
**Out:** `data-layer/processed/blueprint_index.json`, one row per blueprint

**Row:** `blueprint_uuid`, `blueprint_key`, `output_uuid`, `output_name`,
`output_type`, `output_subtype`, `output_grade`, `craft_time_seconds`,
`ingredients[]`, `component_groups[]`, `modifiers[]`, `source_kind`,
`sources[]`, `shop_price_min`, `shop_price_terminal`, `ingredient_cost` (null),
`last_verified_patch`.

**Ingredients:** depth-first walk of `Tiers[0].Requirements`. `Kind == "group"`
sets group name. `Kind` in (`resource`, `item`) are leaves — keep `UUID`, `Name`,
`QuantityScu`, `MinQuality`, group.

**Contracts:** substring-test raw text for `"PoolUUID"` before `json.loads`.
Read `Blueprints[].PoolContents[].BlueprintUUID` plus `Chance`, `PoolUUID`, and
contract `UUID`, `DisplayTitle`|`Title`, `MissionGiver`, `MissionType.Name`,
`Faction`, `Illegal`, `TimeToComplete`, `Difficulty`, `ReputationPrerequisite`.

**`source_kind`, first match wins:**

    Availability.Default == true                            -> default
    uuid appears in any contract Blueprints[]               -> contract
    pool Key contains "Xenothreat" or "RedWind"             -> event
    pool Key BP_REWARD_<x> and BP_CRAFT_<x> exists          -> direct_reward
    RewardPools present, none of the above                  -> other_pool
    no Default, no RewardPools                              -> none

**Price:** min `price_buy > 0` on `items_prices_all.item_uuid` = `output_uuid`.

**Accept:**

    rows                       == 1597
    source_kind                == none 865 | contract 676 | event 31 |
                                  direct_reward 16 | default 8 | other_pool 1
    contracts carrying Blueprints[] == 768
    blueprints with >=1 contract    == 676
    ingredient leaves          == 4274   (resource 3976, item 298)
    leaves lacking QuantityScu == 298, and all are Kind == "item"
    every leaf has MinQuality
    rows with a price          == 721
    rows with >=1 modifier     == 1537
    distinct ingredients       == 37
    ingredient_cost null on all 1597

---

## WO-3 — blueprint pages (1,597)

Reads WO-2 only.

Order: answer line → what it makes (+ price, + item link) → what it needs
(grouped) → what quality does → where the blueprint comes from → provenance.

**Source block.** Sources per blueprint: min 1, median 6, p90 33, **max 127**.
Do not render one row per source. Lead with best (highest `Chance`, then lowest
`MinStanding.MinReputation`), then a grouped summary by giver and mission type,
full list behind a disclosure.

Per source show: title, giver, mission type, `Illegal` as lawful/unlawful,
`Chance`, and the reputation gate as prose from `MinStanding.Name` + `Faction`
— *"Needs Sr. Contractor standing with InterSec Defense Solutions."*

**`CalculatedReward` is a boolean (8,260 true / 87 null). No payout exists. Do
not display one.**

**By `source_kind`:**

    contract        as above
    event           XenoThreat: name the contribution tier from the pool key
                    (_15_ .. _100_). RedWind: "Reward from RedWind Linehaul."
    direct_reward   state plainly
    default         state plainly
    other_pool      the Microsatellite probe, 1 row
    none            "Nothing in the game files says how this blueprint is
                    obtained. It may come from an event, or it may not be
                    available yet."   <- 865 pages, 54%. Must read confident.

**Accept:**

    the 6 null-output blueprints render complete (list in EDGE CASES)
    the 127-source blueprint renders a bounded source count
    an 865-group page renders complete with no source block
    modifier section absent, not empty, on the 60 rows with no modifiers
    no payout figure anywhere

---

## WO-4 — reverse lookup

Reads WO-2. **Out:** `data-layer/processed/ingredient_index.json`.

Invert ingredients → blueprints. 37 total: 26 `resource`, 11 `item`
(hand-mined). Multi-select UI, no search needed. Separate the two kinds
visually — they are acquired differently.

Two result lists: **"you have everything"** and **"you're one short"** with the
missing ingredient named. Sort by `shop_price_min` descending; unpriced rows
sort last, never interleaved.

Match on **presence, not quantity** — 298 leaves have no `QuantityScu` and hold
size is unknown. State that limit on the page. Also state that this matches
ingredients, not blueprint ownership.

**Accept:**

    ingredients                == 37
    kind == "item"             == 11
    Aslarite alone             -> 856 blueprints
    "one short" list non-empty for a single-ingredient selection

---

## WO-5 — material pages (37)

Reads WO-2 + `SC/resources/commodities.json`.

**Build:** what it makes (inverted index, ranked by output price, grouped —
Aslarite is 856 rows), name + description (all 26 resources have real ones, no
placeholders), container sizes from `CargoContainers[]` (1/2/4/8/16 SCU).

The 11 hand-mined gems are absent from `commodities.json`. They get the
"what it makes" section only. Say why: hand-mined, not traded as cargo.

**Do NOT build — no data exists:**

    where to buy it     commodity_trade_locations.json is TAG-matched, not stock.
                        15 materials share a byte-identical 468-location set;
                        every entry carries MatchedTagName "Commodity"/"Metal".
    what it costs       zero commodity price rows on disk
    what it refines to  0 of 26 carry RefinedVersionUUID
    where to mine it    no source found

Leave those four slots present, empty and labelled.

**Accept:**

    no material page renders a buy location or a price

---

## EDGE CASES — all measured, all will bite

**6 blueprints with null `Output.UUID` / `Name` / `Type`:**

    BP_CRAFT_COOL_S04_CNOU_Pioneer                    none
    BP_CRAFT_cds_combat_heavy_helmet_01_02_02         direct_reward
    BP_CRAFT_cds_combat_superheavy_backpack_01_03_01  contract
    BP_CRAFT_cds_combat_superheavy_helmet_01_03_01    contract
    BP_CRAFT_cds_combat_superheavy_suit_01_03_01      contract
    BP_CRAFT_cds_undersuit_01_02_02                   direct_reward

No item link, no price, no output name. Must not 404, must not render blank.

**3 output UUID collisions** — 1,597 blueprints → 1,588 distinct outputs:

    dabd2d8d  FullForce  PowerPlant    BP_CRAFT_POWR_LPLT_S02_FullForce + BP_CRAFT_POWR_SASU_S02_DayBreak
    dadc9318  FoxFire    QuantumDrive  BP_CRAFT_QDRV_ACAS_S01_FoxFire   + BP_CRAFT_QDRV_JUST_S01_Goliath
    6fc982c0  Glacis     Shield        BP_CRAFT_SHLD_ORIG_S04_890J      + BP_CRAFT_SHLD_RSI_S04_Polaris

Item → blueprint is many-to-many. Show "2 blueprints make this". Do not dedupe.

**`Chance` values:** 8,283 at 1, 53 at 0.25, 11 at 0.75.
**`Illegal`:** 7,571 false, 776 true.
**Givers:** 22 distinct. 68 blueprints have >1 giver, max 9.
**Mission types:** Mercenary 3,179, Ship Mining 2,658, Refueling 656.

---

## FORBIDDEN

1. **No name-based joins.** 35 of 37 ingredient names match UEX commodity names
   exactly. It will work. Use `resources/commodities.json` UUIDs (26 of 37) and
   leave the other 11 unjoined.
2. **No ingredient cost, total cost, craft-vs-buy verdict, shopping trip or
   cost-per-improvement.** Zero commodity price rows exist. Schema slot stays,
   value stays null.
3. **No grind-route planning.** Out of scope by decision — CmdrQuattro's tool
   owns it. Link out.
4. **No estimates or placeholders in any numeric field.**

---

## PERFORMANCE

Naive scan of 5,108 contract files exceeds 45s. One directory pass;
substring-test `"PoolUUID"` before parsing (only ~15% qualify); do not loop pool
keys against every file.

---

## OPEN — not blocking, worth an hour

1. `SC/resources/resources.json` (557 records, includes `Kind: cave_harvestable`)
   never opened. **Most likely home for the missing mining locations.**
2. RedWind contracts never checked for a `Blueprints` array — its 6 blueprints
   are classed `event` on the pool key alone.
3. `CategoryUUID` on blueprints never resolved to a name; may beat `output_type`
   for grouping.
4. Whether the 3 output collisions and the 6 null outputs resolve in a newer
   extraction. Snapshot is 2026-08-01; game is on 4.9.
5. Data defect worth reporting upstream: `BP_REWARD_ds_combat_medium_helmet_01_02_01`
   is missing a `c` — arms, core and legs of that set use `cds_`. Also
   `BP_REWARD_CollectorMaterial_001` and `_002` reference no existing blueprint.

---

## APPENDIX — reference implementation

Read-only. Writes four files under `data-layer/processed/`. Executed against the
real snapshots to produce every count asserted above.

### A. WO-1

```python
import json, glob, os

ROOT = r"C:\Users\david\citizen-compass"
SC   = os.path.join(ROOT, r"data-layer\external-sources\scunpacked-data\snapshots\20260801T204744Z")
UEX  = os.path.join(ROOT, r"data-layer\external-sources\uexcorp\snapshots\20260801T235530Z")
OUT  = os.path.join(ROOT, r"data-layer\processed")

def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)

desc, src = {}, {}
for fname in ("fps-items.json", "ship-items.json"):
    for rec in load(os.path.join(SC, fname)):
        std  = rec.get("stdItem") or {}
        uuid = std.get("UUID") or rec.get("reference")
        text = (std.get("DescriptionText") or std.get("Description") or "").strip()
        if uuid and text:
            desc[uuid], src[uuid] = text, fname

uex = []
for p in glob.glob(os.path.join(UEX, "items_category_*.json")):
    uex += (load(p).get("data") or [])

out = {}
for item in uex:
    u = item.get("uuid")
    if u and u in desc:
        out[str(item["id"])] = {"uuid": u, "name": item.get("name"),
                                "description": desc[u], "source_file": src[u]}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "item_descriptions.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

assert len(out) == 5344, f"expected 5344, got {len(out)}"
print("WO-1 ok:", len(out))
```

### B. WO-2

```python
import json, glob, os, collections

ROOT  = r"C:\Users\david\citizen-compass"
SC    = os.path.join(ROOT, r"data-layer\external-sources\scunpacked-data\snapshots\20260801T204744Z")
UEX   = os.path.join(ROOT, r"data-layer\external-sources\uexcorp\snapshots\20260801T235530Z")
OUT   = os.path.join(ROOT, r"data-layer\processed")
PATCH = "4.9"          # set from the manifest, do not hard-code blindly

def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)

sources, contracts_with_bp = {}, 0
for path in glob.glob(os.path.join(SC, "contracts", "*.json")):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        raw = fh.read()
    if '"PoolUUID"' not in raw:
        continue
    c = json.loads(raw)
    pools = c.get("Blueprints") or []
    if not pools:
        continue
    contracts_with_bp += 1
    meta = {"contract_uuid": c.get("UUID"),
            "title": c.get("DisplayTitle") or c.get("Title"),
            "giver": c.get("MissionGiver"),
            "mission_type": (c.get("MissionType") or {}).get("Name"),
            "faction": c.get("Faction"), "illegal": c.get("Illegal"),
            "time_to_complete": c.get("TimeToComplete"),
            "difficulty": c.get("Difficulty"),
            "reputation": c.get("ReputationPrerequisite")}
    for pool in pools:
        for entry in (pool.get("PoolContents") or []):
            bid = entry.get("BlueprintUUID")
            if bid:
                sources.setdefault(bid, []).append(
                    dict(meta, chance=pool.get("Chance"), pool_uuid=pool.get("PoolUUID")))

cheapest = {}
for row in load(os.path.join(UEX, "items_prices_all.json"))["data"]:
    u, buy = row.get("item_uuid"), (row.get("price_buy") or 0)
    if u and buy > 0 and (u not in cheapest or buy < cheapest[u][0]):
        cheapest[u] = (buy, row.get("terminal_name"))

blueprints = load(os.path.join(SC, "blueprints.json"))
keys = {b.get("Key") for b in blueprints}

def flatten(node, acc, group=None):
    kind = node.get("Kind")
    if kind == "group":
        group = node.get("Name")
    if kind in ("resource", "item"):
        acc.append({"kind": kind, "uuid": node.get("UUID"), "name": node.get("Name"),
                    "quantity_scu": node.get("QuantityScu"),   # null on every 'item'
                    "min_quality": node.get("MinQuality"), "group": group})
    for child in (node.get("Children") or []):
        flatten(child, acc, group)

rows, kinds = [], collections.Counter()
for b in blueprints:
    tier  = (b.get("Tiers") or [{}])[0]
    req   = tier.get("Requirements") or {}
    avail = b.get("Availability") or {}
    pkeys = [p.get("Key") or "" for p in (avail.get("RewardPools") or [])]

    ingredients = []
    flatten(req, ingredients)

    groups, modifiers = [], []
    for g in (req.get("Children") or []):
        groups.append({"key": g.get("Key"), "name": g.get("Name"),
                       "required_count": g.get("RequiredCount")})
        for m in (g.get("Modifiers") or []):
            modifiers.append({"group": g.get("Name"), "key": m.get("Key"),
                              "name": m.get("Name"),
                              "quality_range": m.get("QualityRange"),
                              "modifier_range": m.get("ModifierRange"),
                              "value_range_type": m.get("ValueRangeType"),
                              "unit_format": m.get("UnitFormat")})

    uuid = b["UUID"]
    if avail.get("Default"):
        kind = "default"
    elif uuid in sources:
        kind = "contract"
    elif any("Xenothreat" in k or "RedWind" in k for k in pkeys):
        kind = "event"
    elif any(k.startswith("BP_REWARD_") and "BP_CRAFT_" + k[10:] in keys for k in pkeys):
        kind = "direct_reward"
    elif pkeys:
        kind = "other_pool"
    else:
        kind = "none"
    kinds[kind] += 1

    o     = b.get("Output") or {}
    price = cheapest.get(o.get("UUID"))
    rows.append({"blueprint_uuid": uuid, "blueprint_key": b.get("Key"),
                 "output_uuid": o.get("UUID"), "output_name": o.get("Name"),
                 "output_type": o.get("Type"), "output_subtype": o.get("Subtype"),
                 "output_grade": o.get("Grade"),
                 "craft_time_seconds": tier.get("CraftTimeSeconds"),
                 "ingredients": ingredients, "component_groups": groups,
                 "modifiers": modifiers, "source_kind": kind,
                 "sources": sources.get(uuid, []) if kind == "contract" else pkeys,
                 "shop_price_min": price[0] if price else None,
                 "shop_price_terminal": price[1] if price else None,
                 "ingredient_cost": None, "last_verified_patch": PATCH})

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "blueprint_index.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)

leaves = [i for r in rows for i in r["ingredients"]]
assert len(rows) == 1597
assert dict(kinds) == {"none": 865, "contract": 676, "event": 31,
                       "direct_reward": 16, "default": 8, "other_pool": 1}, dict(kinds)
assert contracts_with_bp == 768
assert len(sources) == 676
assert len(leaves) == 4274
assert all(i["min_quality"] is not None for i in leaves)
assert sum(1 for i in leaves if i["quantity_scu"] is None) == 298
assert all(i["kind"] == "item" for i in leaves if i["quantity_scu"] is None)
assert sum(1 for r in rows if r["shop_price_min"]) == 721
assert sum(1 for r in rows if r["modifiers"]) == 1537
assert all(r["ingredient_cost"] is None for r in rows)
print("WO-2 ok:", len(rows), dict(kinds))
```

### C. WO-4 / WO-5 derived views

```python
import json, os, collections

ROOT = r"C:\Users\david\citizen-compass"
OUT  = os.path.join(ROOT, r"data-layer\processed")

with open(os.path.join(OUT, "blueprint_index.json"), encoding="utf-8") as fh:
    rows = json.load(fh)

inverted, kinds = collections.defaultdict(list), {}
for r in rows:
    for name in {i["name"] for i in r["ingredients"]}:
        inverted[name].append(r["blueprint_uuid"])
    for i in r["ingredients"]:
        kinds[i["name"]] = i["kind"]

ingredients = [{"name": n, "kind": kinds[n], "blueprint_count": len(u),
                "blueprints": sorted(u)}
               for n, u in sorted(inverted.items(), key=lambda kv: -len(kv[1]))]

with open(os.path.join(OUT, "ingredient_index.json"), "w", encoding="utf-8") as fh:
    json.dump(ingredients, fh, ensure_ascii=False, indent=1)

def summarise(r):
    s = r["sources"]
    if r["source_kind"] != "contract" or not s:
        return None
    floor = lambda x: (((x.get("reputation") or {}).get("MinStanding") or {})
                       .get("MinReputation") or 0)
    best = sorted(s, key=lambda x: (-(x.get("chance") or 0), floor(x)))[0]
    rep  = best.get("reputation") or {}
    return {"total": len(s),
            "best": {"title": best.get("title"), "giver": best.get("giver"),
                     "mission_type": best.get("mission_type"),
                     "chance": best.get("chance"), "illegal": best.get("illegal"),
                     "standing": (rep.get("MinStanding") or {}).get("Name"),
                     "faction": rep.get("Faction")},
            "givers": collections.Counter(x.get("giver") for x in s).most_common(),
            "mission_types": collections.Counter(x.get("mission_type") for x in s).most_common(),
            "others": len(s) - 1}

with open(os.path.join(OUT, "blueprint_sources.json"), "w", encoding="utf-8") as fh:
    json.dump({r["blueprint_uuid"]: summarise(r) for r in rows}, fh,
              ensure_ascii=False, indent=1)

outputs  = collections.Counter(r["output_uuid"] for r in rows if r["output_uuid"])
contract = [r for r in rows if r["source_kind"] == "contract"]
assert len(ingredients) == 37
assert sum(1 for i in ingredients if i["kind"] == "item") == 11
assert ingredients[0]["name"] == "Aslarite" and ingredients[0]["blueprint_count"] == 856
assert sum(1 for r in rows if not r["output_uuid"]) == 6
assert len(outputs) == 1588
assert sum(1 for v in outputs.values() if v > 1) == 3
assert max(len(r["sources"]) for r in contract) == 127
print("WO-4/5 ok:", len(ingredients), "ingredients")
```

**Assertions are exact on purpose and will break when the game patches. That is
the signal, not the bug** — update the numbers deliberately and record which
patch moved them.
