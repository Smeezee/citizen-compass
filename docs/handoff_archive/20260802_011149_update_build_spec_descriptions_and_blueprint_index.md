# BUILD SPEC — two builds, both validated against the real data

**From C2 to C1. 2026-08-02. Spec only — C2 wrote nothing to the repository.**

Two builds. Both run entirely on data already collected, gated and sealed.
Neither is blocked on the commodity price pull.

**Everything in this document was executed read-only against the real snapshots
before being written down.** Every count is measured output, not a prediction.
Where a number is asserted in section 5, a run produced it.

    BUILD 1   Item descriptions        5,344 item pages gain CIG's own prose
    BUILD 2   The blueprint index      1,597 rows, the table every crafting
                                       surface reads

**Why these two.** Build 1 is the largest visible improvement available anywhere
in the project right now and it depends on nothing. Build 2 is the foundation —
no crafting page can be built before it, and it carries zero design risk because
it is pure derivation. One visible, one structural, neither blocked.

---

## 0. READ STATE

    scunpacked-data/snapshots/20260801T204744Z/
        blueprints.json      1,597 records
        contracts/           5,108 files
        fps-items.json       5,420 records
        ship-items.json      5,384 records
        labels.json          90,121 labels

    uexcorp/snapshots/20260801T235530Z/
        items_category_*.json  7,728 records, 100 files   sha of categories.json 3de4f9fa2bf7674d
        items_prices_all.json  23,734 rows                sha 308542bf043df9c2

Both snapshots are sealed. If these hashes have moved, stop — something has
modified a sealed snapshot.

---

# BUILD 1 — ITEM DESCRIPTIONS

## 1.1 What this corrects

`claude/front-end-build-plan-2026-08-02.md` §3 states:

> **No "what it's good for" or "how to use it".** That is writing, not data.

That is wrong, and it was wrong when I wrote it. The descriptions were already on
disk in a file the project had gated a day earlier.

## 1.2 The measured coverage

    fps-items.json   records with a description      5,182 of 5,420
    ship-items.json  records with a description      2,598 of 5,384
    combined uuid -> description map                 7,780 entries

    UEX catalogue                                    7,728 items
    UEX items carrying a uuid                        5,566
    UEX items that gain a description                5,344

    = 69% of the whole catalogue
    = 96% of every item that carries a uuid

**Put that next to the other two coverage figures for the same pages:**

    description   69%
    price         36%
    image          0%

Description is the best-covered field on the item page. The doorway plan was
built around templates that must survive having almost nothing in them; this is
the single largest thing available to stop 7,728 pages reading like a database
dump.

## 1.3 The join

**UUID only. No name matching.** The UEX manifest forbids a name-matching path
and it is not needed here.

    UEX  items_category_*.json  ->  .uuid
    scunpacked  fps-items.json  ->  .stdItem.UUID   (fall back to .reference)
    scunpacked  ship-items.json ->  .stdItem.UUID   (fall back to .reference)

Both scunpacked files share the same record shape: a top-level object with
`className`, `reference`, `name`, `type`, `subType`, `size`, `grade`, `tags`,
`classification`, and a nested `stdItem` carrying `UUID`, `ClassName`, `Size`,
`Grade`, `Mass`, dimensions, `Type`, `Name`, `Description`, `DescriptionText`,
`Manufacturer`.

**Field priority, in order:**

1. `stdItem.DescriptionText`
2. `stdItem.Description`
3. `labels.json` key `item_Desc_<ClassName>`

The third path exists but keys on **class name, not UUID** — 5,805 `item_Desc_*`
keys, 5,558 with more than 20 characters of content. Use it only where the UUID
path returns nothing. `labels.json` also holds 4,749 `item_Name_*` keys if a
display name is ever needed.

**Do not merge the two ship-items and fps-items maps blindly** — build fps first,
then let ship-items overwrite, or vice versa, but pick one and record which. The
combined map is 7,780 entries against 5,420 + 5,384 inputs, so there is overlap.

## 1.4 What the descriptions actually contain

Two distinct kinds, and the page should handle both:

**Prose.** *"CDS's quest to create the ideal light armor continues with the
FBL-8a. This light armor will keep you fast on your feet with its strategic mix
of protective plating and reinforced nano-weave fabrics…"*

**Stat blocks**, newline-delimited key/value:

    Item Type: Heavy Armor
    Damage Reduction: 40%
    Temp. Rating: -80 / 105 °C
    Radiation ...

**Detect and render these differently.** A stat block rendered as a paragraph
reads as broken. Suggested test: if more than half the non-empty lines match
`^[A-Za-z][A-Za-z .'-]{2,30}:\s`, render as a definition list; otherwise render
as prose. **This heuristic is mine and is untested — validate it against a
sample before trusting it.**

Descriptions contain literal `\n`. Preserve line breaks.

## 1.5 Where it goes on the page

Slot 3 of the item page defined in `front-end-build-plan-2026-08-02.md` §A2 —
under the header, above the answer line. The answer line ("Sold at 4 shops,
cheapest is…") stays the most important element; the description is context, not
the answer.

**Where a stat block exists, it also belongs beside the price**, because it is
the thing that tells someone whether the cheaper item is the worse item.

## 1.6 Verification — hard rule 12

- **Assert the join returns exactly 5,344.** Fewer means the fallback chain is
  broken; more means something matched by name.
- **Assert the 2,384 items with no description still render a complete page.**
  That is 31% of the catalogue. This is the empty-state test the doorway plan
  already requires, now with a real number attached.
- **Assert no name-based match occurs.** Log any item that gained a description
  without a UUID match — the count must be zero unless the `labels.json`
  fallback is deliberately enabled, in which case count it separately.
- **Assert a stat-block description renders as a list and a prose description
  renders as a paragraph**, using one known example of each.

---

# BUILD 2 — THE BLUEPRINT INDEX

One derived table. 1,597 rows. Everything crafting reads it and nothing else
parses `blueprints.json` or `contracts/` again.

## 2.1 Row shape

| field | source |
|---|---|
| `blueprint_uuid` | `blueprints.json[].UUID` |
| `blueprint_key` | `.Key` |
| `output_uuid` `output_name` `output_type` `output_subtype` `output_grade` | `.Output.*` |
| `craft_time_seconds` | `.Tiers[0].CraftTimeSeconds` |
| `ingredients[]` | flattened `.Tiers[0].Requirements` |
| `component_groups[]` | `.Tiers[0].Requirements.Children[]` — `Key`, `Name`, `RequiredCount` |
| `modifiers[]` | each group's `Modifiers[]` |
| `source_kind` | derived, see 2.3 |
| `sources[]` | contract records, or pool keys |
| `shop_price_min` `shop_price_terminal` | UEX join on `output_uuid` |
| `last_verified_patch` | snapshot patch stamp |

Every blueprint has exactly **one** tier. Do not build for many.

## 2.2 Ingredient flattening — and the trap in it

Walk `Requirements` depth-first. `Kind == "group"` sets the current group name.
`Kind == "resource"` and `Kind == "item"` are leaves. Keep `UUID`, `Name`,
`QuantityScu`, `MinQuality`, and the enclosing group name.

**Measured across all 1,597 blueprints — 4,274 leaves:**

    Kind == "resource"    3,976    all 3,976 carry QuantityScu
    Kind == "item"          298    NONE carry QuantityScu
    all 4,274 carry MinQuality

**`QuantityScu` is null on every `item` leaf.** Those 298 are the hand-mined
gems — Dolivine, Hadanite, Sadaryx, Beradom, Aphorite, Glacosite, Janalite,
Feynmaline, Carinite, Saldynium (Ore), Yormandi Eye. A template that assumes a
quantity will print "null SCU of Hadanite" on roughly one recipe in five.
**Render those as a name with no quantity.**

37 distinct ingredients total. 1–4 leaves per blueprint, average 2.7.

## 2.3 `source_kind` — derivation and measured distribution

Evaluate in this order, first match wins:

    Availability.Default == true                              -> default
    blueprint_uuid appears in any contract's Blueprints[]     -> contract
    any pool Key contains "Xenothreat" or "RedWind"           -> event
    any pool Key is BP_REWARD_<x> where BP_CRAFT_<x> exists   -> direct_reward
    RewardPools present but none of the above                 -> other_pool
    no Default, no RewardPools                                -> none

**Measured result — this is the assertion:**

    none            865
    contract        676
    event            31
    direct_reward    16
    default           8
    other_pool        1
    -------------------
    total         1,597

The single `other_pool` row is `BP_CRAFT_Carryable_2H_FL_MissionItem_Microsatellite_a`
("Probe"), pointing at `BP_MISSIONREWARD_Carryable_2H_FL_MissionItem_Microsatellite_a`.
**It exists so nothing falls through silently.** If that bucket ever grows past 1,
a new reward mechanism has appeared and someone should look.

## 2.4 Contract extraction — what each contract gives, and one correction

For each of the 5,108 files, read `Blueprints[]`. Each entry:
`Chance`, `PoolUUID`, `PoolContents[]` of `{ItemName, ItemUUID, BlueprintUUID}`.

Alongside, capture from the contract: `UUID`, `DisplayTitle` (fall back to
`Title`), `MissionGiver`, `MissionType.Name`, `Faction`, `TimeToComplete`,
`Difficulty`, `Illegal`, `ReputationPrerequisite`,
`LocationPools[].ResolvedLocations[].Name`.

**Correction to `claude/plan-crafting-build-from-data-on-hand.md` §3.** That plan
lists `CalculatedReward` as the payout. **It is a boolean, not an amount** —
measured 8,260 `true`, 87 `null`, no numbers. It means the reward is computed at
runtime. **There is no payout figure in this data.** Do not display one.

**What is genuinely there and is better than expected — `ReputationPrerequisite`
is a full object:**

    { "Faction": "InterSec Defense Solutions",
      "Scope": "FactionReputation",
      "MinStanding": { "Name": "Sr. Contractor",   "MinReputation": 5800 },
      "MaxStanding": { "Name": "Elite Contractor", "MinReputation": 95250 } }

That gives the reputation gate in human words — *"needs Sr. Contractor standing
with InterSec Defense Solutions"* — which is exactly the question a player has.

**`Illegal`** — measured 7,571 false, 776 true. Lawful/unlawful badge, free.

**`Chance`** — measured 8,283 at 1, 53 at 0.25, 11 at 0.75. Real and varied.
Show it. Nobody else does.

## 2.5 The thing that will break the page if it is not handled

**Sources per blueprint: minimum 1, maximum 127.**

One blueprint is awarded by 127 different contracts. A blueprint page that
renders a row per source will produce a 127-row table for a single answer.

**Group by `MissionGiver` and `MissionType` and summarise**: *"Awarded by 127
Mercenary contracts from Headhunters and 4 others."* Offer the full list behind
a disclosure. Show the **best** source first — highest `Chance`, then lowest
reputation requirement.

## 2.6 Price join

`output_uuid` = `items_prices_all.json[].item_uuid`, taking rows where
`price_buy > 0`, keeping the minimum and its `terminal_name`.

**Measured: 721 of 1,597 blueprint rows gain a price.** (The earlier figure of
719 counted distinct *items*; 1,597 blueprints resolve to 1,588 distinct outputs,
so the row count differs slightly. Both are correct for what they count.)

**No ingredient cost. No total. No craft-vs-buy verdict.** There are zero
commodity price rows on disk. Leave the slot in the schema, leave it null, and
do not let anything populate it before the commodity pull lands.

## 2.7 Modifiers

Each component group carries `Modifiers[]` with `Key`, `Name`, `QualityRange`
(min/max, observed 0–1000), `ModifierRange` (`AtMinQuality`/`AtMaxQuality`),
`ValueRangeType` (observed `linear`), `UnitFormat`.

**Measured: 1,537 of 1,597 blueprints carry at least one modifier.**
The 60 without are mostly `WeaponAttachment` (36) and `Char_Armor_Backpack` (17).
The template must not assume a quality curve exists.

## 2.8 Performance — two runs timed out getting this wrong

Scanning 5,108 contract files naively exceeds 45 seconds.

- One pass over the directory.
- **Substring-test the raw text for `"PoolUUID"` before calling `json.loads`.**
  Only ~15% of contracts award blueprints; parsing the other 85% is wasted.
- **Do not loop 146 pool keys against every file.** That is 745,000 substring
  searches and it is what timed out. Invert it: extract from the file, then look
  up.

On a machine without a 45-second cap this is a non-issue, but the wasted work is
real either way.

## 2.9 Verification — hard rule 12

- **Assert 1,597 rows out.** Same as in.
- **Assert `source_kind` partitions to 865 / 676 / 31 / 16 / 8 / 1.** These are
  measured. Any drift means the data or the derivation changed, and both are
  worth knowing about.
- **Assert 676 blueprints have at least one contract source**, and that the
  scan found **768** contracts carrying a `Blueprints` array. A run finding fewer
  has silently skipped files.
- **Assert all 4,274 ingredient leaves carry `MinQuality`, and that exactly the
  298 `item`-kind leaves lack `QuantityScu`.** If a `resource` leaf ever lacks a
  quantity, the flattening is wrong.
- **Assert 721 rows carry a price and 0 rows carry an ingredient cost.** The
  second is the important one — a cost appearing means something invented it.
- **Assert an `865`-group page renders complete with no source.** That is 54% of
  all blueprint pages.
- **Assert no name-based join exists.** 35 of the 37 ingredient names happen to
  match UEX commodity names exactly. It will work. **It is still forbidden** —
  use the UUIDs in `resources/commodities.json`, which cover 26 of 37 properly,
  and leave the other 11 unjoined rather than matching on a string.

---

## 3. WHAT I DID NOT VERIFY

- **The stat-block detection heuristic in 1.4 is mine and untested.**
- **Whether RedWind's contracts carry a `Blueprints` array.** Its 6 blueprints
  are classed `event` on the strength of the pool key alone.
- **`CategoryUUID` on blueprints** — never resolved to a name.
- **Description coverage per doorway.** I have the total (69%) but not the split,
  so I cannot say whether Ship parts is better or worse covered than Clothing.
- **Whether `labels.json item_Desc_*` adds anything beyond the UUID path.** It may
  be entirely redundant. Worth measuring before wiring the third fallback.

---

## 4. REFERENCE IMPLEMENTATION

Read-only. Writes one JSON file each. Neither touches a snapshot.
Both were executed against the real data to produce the counts asserted above.

Paths assume `C:\Users\david\citizen-compass`. Adjust `ROOT` if that changes.

### 4.1 Build 1 — the description map

```python
import json, glob, os

ROOT = r"C:\Users\david\citizen-compass"
SC   = os.path.join(ROOT, r"data-layer\external-sources\scunpacked-data\snapshots\20260801T204744Z")
UEX  = os.path.join(ROOT, r"data-layer\external-sources\uexcorp\snapshots\20260801T235530Z")
OUT  = os.path.join(ROOT, r"data-layer\processed\item_descriptions.json")

def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

desc, src = {}, {}
for fname in ("fps-items.json", "ship-items.json"):
    for rec in load(os.path.join(SC, fname)):
        std = rec.get("stdItem") or {}
        uuid = std.get("UUID") or rec.get("reference")
        if not uuid:
            continue
        text = (std.get("DescriptionText") or std.get("Description") or "").strip()
        if text:
            desc[uuid] = text
            src[uuid] = fname

uex = []
for path in glob.glob(os.path.join(UEX, "items_category_*.json")):
    uex += (load(path).get("data") or [])

out, hit = {}, 0
for item in uex:
    uuid = item.get("uuid")
    if uuid and uuid in desc:
        hit += 1
        out[str(item["id"])] = {
            "uuid": uuid,
            "name": item.get("name"),
            "description": desc[uuid],
            "source_file": src[uuid],
        }

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print("uex items:", len(uex), "with uuid:", sum(1 for i in uex if i.get("uuid")))
print("descriptions matched:", hit)
assert hit == 5344, f"expected 5344, got {hit}"
print("OK ->", OUT)
```

### 4.2 Build 2 — the blueprint index

```python
import json, glob, os, collections

ROOT = r"C:\Users\david\citizen-compass"
SC   = os.path.join(ROOT, r"data-layer\external-sources\scunpacked-data\snapshots\20260801T204744Z")
UEX  = os.path.join(ROOT, r"data-layer\external-sources\uexcorp\snapshots\20260801T235530Z")
OUT  = os.path.join(ROOT, r"data-layer\processed\blueprint_index.json")
PATCH = "4.9"   # snapshot patch stamp - set from the manifest, do not hard-code blindly

def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

# ---- contracts: only parse files that can possibly matter -------------------
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
    meta = {
        "contract_uuid": c.get("UUID"),
        "title":         c.get("DisplayTitle") or c.get("Title"),
        "giver":         c.get("MissionGiver"),
        "mission_type":  (c.get("MissionType") or {}).get("Name"),
        "faction":       c.get("Faction"),
        "illegal":       c.get("Illegal"),
        "time_to_complete": c.get("TimeToComplete"),
        "difficulty":    c.get("Difficulty"),
        "reputation":    c.get("ReputationPrerequisite"),
    }
    for pool in pools:
        for entry in (pool.get("PoolContents") or []):
            bp_uuid = entry.get("BlueprintUUID")
            if bp_uuid:
                sources.setdefault(bp_uuid, []).append(
                    dict(meta, chance=pool.get("Chance"), pool_uuid=pool.get("PoolUUID")))

# ---- prices ----------------------------------------------------------------
cheapest = {}
for row in load(os.path.join(UEX, "items_prices_all.json"))["data"]:
    uuid, buy = row.get("item_uuid"), (row.get("price_buy") or 0)
    if uuid and buy > 0 and (uuid not in cheapest or buy < cheapest[uuid][0]):
        cheapest[uuid] = (buy, row.get("terminal_name"))

# ---- blueprints ------------------------------------------------------------
blueprints = load(os.path.join(SC, "blueprints.json"))
keys = {b.get("Key") for b in blueprints}

def flatten(node, acc, group=None):
    kind = node.get("Kind")
    if kind == "group":
        group = node.get("Name")
    if kind in ("resource", "item"):
        acc.append({
            "kind": kind,
            "uuid": node.get("UUID"),
            "name": node.get("Name"),
            "quantity_scu": node.get("QuantityScu"),   # null on every 'item'
            "min_quality": node.get("MinQuality"),
            "group": group,
        })
    for child in (node.get("Children") or []):
        flatten(child, acc, group)

rows, kinds = [], collections.Counter()
for b in blueprints:
    tier  = (b.get("Tiers") or [{}])[0]
    req   = tier.get("Requirements") or {}
    avail = b.get("Availability") or {}
    pools = avail.get("RewardPools") or []
    pool_keys = [p.get("Key") or "" for p in pools]

    ingredients = []
    flatten(req, ingredients)

    groups, modifiers = [], []
    for g in (req.get("Children") or []):
        groups.append({"key": g.get("Key"), "name": g.get("Name"),
                       "required_count": g.get("RequiredCount")})
        for m in (g.get("Modifiers") or []):
            modifiers.append({
                "group": g.get("Name"), "key": m.get("Key"), "name": m.get("Name"),
                "quality_range": m.get("QualityRange"),
                "modifier_range": m.get("ModifierRange"),
                "value_range_type": m.get("ValueRangeType"),
                "unit_format": m.get("UnitFormat"),
            })

    uuid = b["UUID"]
    if avail.get("Default"):
        kind = "default"
    elif uuid in sources:
        kind = "contract"
    elif any("Xenothreat" in k or "RedWind" in k for k in pool_keys):
        kind = "event"
    elif any(k.startswith("BP_REWARD_") and "BP_CRAFT_" + k[len("BP_REWARD_"):] in keys
             for k in pool_keys):
        kind = "direct_reward"
    elif pools:
        kind = "other_pool"
    else:
        kind = "none"
    kinds[kind] += 1

    out = b.get("Output") or {}
    price = cheapest.get(out.get("UUID"))
    rows.append({
        "blueprint_uuid": uuid,
        "blueprint_key": b.get("Key"),
        "output_uuid": out.get("UUID"),
        "output_name": out.get("Name"),
        "output_type": out.get("Type"),
        "output_subtype": out.get("Subtype"),
        "output_grade": out.get("Grade"),
        "craft_time_seconds": tier.get("CraftTimeSeconds"),
        "ingredients": ingredients,
        "component_groups": groups,
        "modifiers": modifiers,
        "source_kind": kind,
        "sources": sources.get(uuid, []) if kind == "contract" else pool_keys,
        "shop_price_min": price[0] if price else None,
        "shop_price_terminal": price[1] if price else None,
        "ingredient_cost": None,          # stays null until commodity prices land
        "last_verified_patch": PATCH,
    })

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)

# ---- hard rule 12: assert, do not report ----------------------------------
leaves = [i for r in rows for i in r["ingredients"]]
expected = {"none": 865, "contract": 676, "event": 31,
            "direct_reward": 16, "default": 8, "other_pool": 1}

assert len(rows) == 1597,                     f"rows {len(rows)}"
assert dict(kinds) == expected,               f"source_kind {dict(kinds)}"
assert contracts_with_bp == 768,              f"contracts {contracts_with_bp}"
assert len(sources) == 676,                   f"sourced blueprints {len(sources)}"
assert len(leaves) == 4274,                   f"leaves {len(leaves)}"
assert all(i["min_quality"] is not None for i in leaves), "a leaf lacks MinQuality"
assert sum(1 for i in leaves if i["quantity_scu"] is None) == 298, "quantity nulls moved"
assert all(i["kind"] == "item" for i in leaves if i["quantity_scu"] is None), \
       "a 'resource' leaf lacks a quantity - flattening is wrong"
assert sum(1 for r in rows if r["shop_price_min"]) == 721, "price join moved"
assert all(r["ingredient_cost"] is None for r in rows),  "something invented a cost"
assert sum(1 for r in rows if r["modifiers"]) == 1537,   "modifier count moved"

print("rows:", len(rows))
print("source_kind:", dict(kinds))
print("priced:", sum(1 for r in rows if r["shop_price_min"]))
print("max sources on one blueprint:",
      max((len(r["sources"]) for r in rows if r["source_kind"] == "contract"), default=0))
print("OK ->", OUT)
```

**On the assertions.** They are deliberately exact rather than
greater-than-zero, because a check that cannot fail is not a check. They will
break when the game patches — **that is the point.** A failing assertion after a
patch is the signal that the data moved and someone should look, not a bug in
the script. Update the numbers deliberately, with a note saying which patch
changed them.
