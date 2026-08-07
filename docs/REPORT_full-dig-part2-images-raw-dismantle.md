# FULL DIG PART 2 — every remaining unopened and uncategorised file

    from    C2, 2026-08-06
    for     C1 -> Claude Code
    follows docs/REPORT_full-data-layer-dig-and-two-corrections.md
    method  read off the machine, snapshot 20260801T204744Z and the other three
            sources. SAMPLE is marked where a full scan timed out on the bridge.

**The dig is finished. Nothing in `data-layer/` is now unopened except what is
listed in §11.**

**Two more standing claims are wrong — §1 and §2.**

---

# 1. CORRECTION — item images exist. Coverage is 39%, not 0%.

**Every plan says "no item images. Zero. All 7,728 UEX items have an empty
`screenshot` field." That is true of UEX and false of the project.**

`api.star-citizen.wiki/snapshots/20260801T021731Z` — **62 pages, 12,283 item
rows, never parsed by anyone.**

    rows with a non-empty `images` array     4,805  (39.1%)

Each entry is a full record, not a bare link:

    {"source": "cstone.space",
     "original_url": "https://cstone.space/uifimages/<uuid>.png",
     "thumbnail_url": "...",
     "original_width": 3440, "original_height": 1440,
     "thumbnail_width": ..., "thumbnail_height": ...}

**Dimensions are included, so a layout can be built before a single byte is
fetched.**

### The catch, and it is a real one

**The images are hosted by `cstone.space` — Cornerstone, a third-party
community tool.** They are not CIG assets served by CIG, and they are not ours.

**Two separate questions, and neither is answered:**

1. **May we display them at all** — that is Cornerstone's call, not RSI's.
2. **May we hotlink them** — serving traffic off somebody else's host without
   asking is its own problem regardless of the answer to 1.

**Do not wire these in.** But **stop designing on the premise that coverage is
zero** — the honest figure is *39% of items have a known image that we do not
yet have permission to use*, which is a completely different problem from *no
image exists.* **It is a permission problem now, not a data problem.**

`claude/plan-build-a-static.md` and `claude/finding-coverage-and-the-newbie-standard.md`
both need this correction.

### Also in the same rows, never used

    is_craftable       1,585
    is_lootable        3,683
    is_base_variant    present
    event_source       present    (Concierge, Subscriber, IAE, Luminalia...)

**`is_lootable` on 3,683 items answers "can I just find this" — a question the
site cannot currently answer at all**, and it is a boolean, not writing, so the
text-rights hold does not touch it.

---

# 2. CORRECTION — `items/` is not the same data as `items.json`

**Counts match exactly, so this looked settled. It is not.**

    ships/      316 files  ==  ships.json      316 rows   same data
    blueprints/ 1,597      ==  blueprints.json 1,597      same data
    items/      21,849     ==  items.json      21,849     DIFFERENT SHAPE

**Every file in `items/` is `{Item, Raw}`.** `items.json` contains only the
`Item` half. **The `Raw` half has never been opened by anyone.**

    mean Raw size            ~38,792 bytes per item   (SAMPLE, 25 files)
    items/ total on disk     ~3.8 GB                  (SAMPLE, every 200th)
    so Raw is roughly        ~850 MB of unexamined data

`Raw.Entity` carries `ClassName`, `Category`, `Icon`, `tags`, `BBoxSelection`,
`Invisible`, `entityDensityClass`, `StaticEntityClassData`, `__path`, `__type`,
and **`Components`**.

### What is actually in there

**`Icon` is an editor icon, not artwork.** 97% of sampled items have one and the
values are `Default.bmp` and `Usable.bmp` — CryEngine viewport icons. **This does
not help the image gap. Closing it so nobody chases it again.**

**`SGeometryResourceParams` — present on ~92% of sampled items — carries the
exact model path inside `Data.p4k`:**

    "Geometry": { "path": "objects/spaceships/ships/rsi/constellation/
                           constellation_base/rsi_constellation_int_neck_bench.cga" }

**That is the missing link for the 3D viewer.** The hardpoint plan
(`claude/plan-device-map-visual.md`, and the viewer work in CURRENT-STATE)
assumes Blender-placed markers on models obtained by hand. **This gives a
machine-readable model path per item, straight into the archive we already know
how to open** — `unp4k` plus the ZIP64/ZStandard route proven for
`defaultProfile.xml`.

**Component types present (SAMPLE, 183 items):**

    SAttachableComponentParams 183 · SGeometryResourceParams 168
    SEntityPhysicsControllerParams 141 · SEntityInteractableParams 124
    SInteractionStateMachineParams 105 · SItemPortContainerComponentParams 101
    SCItemPurchasableParams 92 · ItemControlComponentParams 78
    SARDataComponentParams 70 · SHealthComponentParams 57
    SEntityComponentCarryableParams 56 · SCItemClothingParams 37
    SCItemInspectableParams 32 · SDegradationParams 21
    SCItemSuitArmorParams 20 · ResourceContainer 19

**`SCItemPurchasableParams` on ~50% is worth a look on its own** — a
purchasability flag straight from the game files, independent of UEX.

**Do not ingest 850 MB of `Raw`.** Extract the two or three fields that matter —
the model path first — and leave the rest on disk.

---

# 3. `Dismantle` — on all 1,597 blueprints, never opened

    {"TimeSeconds": 15, "Efficiency": 0.5,
     "Returns": [ {"Kind":"resource","Name":"Agricium","QuantityScu":0.18},
                  {"Kind":"item","Name":"Hadanite","Quantity":3},
                  {"Kind":"item","Name":"Dolivine","Quantity":3} ]}

**"What do I get back if I break this down, and how long does it take" — for
every craftable item in the game.** None of the four competing crafting tools
shows this.

**It also completes the crafting loop.** The build specs model craft-in only;
this is craft-out, and `Efficiency` is the number that makes salvage-vs-sell a
real calculation.

**Two structural facts that validate existing specs:**

    Kind        "creation" on all 1,597 — one value, no branching needed
    Tiers       exactly 1 on all 1,597 — Tiers[0] is safe, as assumed
    Availability {Default, RewardPools} on all 1,597 — shape is uniform
    CategoryUUID 14 distinct; largest holds 916 of 1,597

---

# 4. COMMODITIES — a real taxonomy, and hauling maths

From `resources/commodities.json`, 206 rows:

    CommodityGroups   ProcessedGoods 71 · Organic 37 · Metal 37 · Mineral 33
                      UnrefinedOres 16 · Vice 16 · SyntheticMaterials 12
                      Food 11 · Bulk_Supplies 11 · Gas 10 · Raw_Minerals 10
                      Nonmetal 9
    DensityGPerCc     on ALL 206, 33 distinct values (0.25 – ...)
    Tier              on 27 only: common / uncommon / rare / epic / legendary
    Instability       on 42, 17 distinct
    Volatility        on 1 only

**`CommodityGroups` is a genuine consumer taxonomy** — unlike `tags.json`, which
was examined on 2 August and found to be the engine's internal tree. **This is
the grouping a commodity browse page should use, and it already exists.**

**`DensityGPerCc` on all 206 makes cargo mass computable** — SCU is volume, and
mass drives ship handling. **Nobody publishes cargo mass by commodity.**

---

# 5. CONTRACTS — the blocks nobody opened

**SAMPLE, every 7th file, 730 of 5,108.**

    MissionTokens                1,100   more than one per contract
    Lifetime                       730   on every one
    CrimeStat                      458
    ObjectiveTokens                366
    Deadline                       364
    BrokerReputationPrerequisites  364
    HaulingOrders                  298
    PropertyOverrides              253
    Prerequisites                  198
    CombatSummary                  162
    ItemCounts                     116
    CompletionTags                  84
    NpcNames                        69
    RewardItems                     55
    RequiredMissions                48
    EntitySpawns                    20
    JournalEntries                  11
    BadgeAward                      11

**`HaulingOrders` — 41% of contracts — is a real cargo manifest:**

    [{"Kind":"Resource","Name":"Tin","MinScu":228,"MaxScu":228,
      "MaxContainerSize":-1}, {"Name":"Pressurized Ice","MinScu":228,...}]

**What a hauling mission actually asks you to carry, by commodity, in SCU.**
It joins straight to the 206 commodity names. **Nobody publishes it, and it is
exactly the "can my ship even take this job" question** — cross it with the
`Cargo` figure now known for 149 ships and `CargoSizeLimits`.

**`Lifetime` on every contract — how many can exist at once:**

    {"InstanceLifeTime":5, "InstanceLifeTimeVariation":2, "RespawnTime":5,
     "RespawnTimeVariation":2, "MaxInstances":8, "MaxInstancesPerPlayer":1}

**This is the mission board's own spawn model.** `rev 5` Part 3 row 3 says board
contents are unobtainable from files. **Partly wrong — the *capacity and
refresh* are in the files.** What is offered right now still is not.

**`CombatSummary`** `{"Total":{"Min":2,"Max":2},"ByGroup":[...]}` — **how many
enemies, by group.** A difficulty signal that is a number, not opinion.

**`Prerequisites` is a mission chain graph** — `RequiredMissions` by UUID and
DebugName, plus required/excluded tags and counts. **Mission chains are
reconstructable.**

**`ItemCounts`** — the pool a delivery mission draws from (Processed Food,
Medical Supplies, Probe, Astatine, Ammunition Crate...).
**`RewardItems`** — item payouts, e.g. `Council Scrip ×6, SendToHome true`.
**`CrimeStat`** `{Min,Max}` — the crime-stat window a mission is offered in.
**`CompletionTags`** — difficulty labels, e.g. `Easy`.
**`BadgeAward`** — e.g. `WelcomeToPyro_Firesale`.
**`MissionTokens`** — **the full mission briefing text**, keyed
(`Contractor|PrisonerBreakTitle`, `...Description`). **This is CIG-written prose
and falls squarely under the parked text-rights question. Extract the structure,
hold the text.**

---

# 6. FACTIONS — the law model, complete

`factions/`, 74 files, **55 with a real name.**

    FactionType       Lawful 36 · Unlawful 28 · PrivateSecurity 7 ·
                      LawEnforcement 3
    DefaultReaction   Neutral 57 · Hostile 15 · Friendly 2
    AbleToArrest      9
    also              PolicesCriminality · PolicesLawfulTrespass · NoLegalRights

Named: ArcCorp, Hurston Dynamics, Hurston Security, Crusader Industries,
Crusader Security, Covalex, Headhunters, Dusters, Fire Rats, Dead Saints,
BlacJac, Bit Zeros, Adagio Holdings, Citizens For Prosperity, FTL Courier,
InterSec Defense Solutions, Klescher Rehabilitation Facilities, Frontier
Fighters, Civilian Defense Force, MT Protection Services, Clovus Darneely...

**Pair this with the `Jurisdiction` block from `starmap.json`** — base fine,
max stolen-goods SCU, prison flag on 101 locations. **Together: who polices
this place, will they arrest me, are they hostile on sight, and what does it
cost. That is a page nobody has built.**

---

# 7. `trade_locations.json` — the `Negative` arrays, opened

**670 negative entries across 965 locations.** Both `ProducesTags` and
`ConsumesTags` are `{Positive[], Negative[]}`.

    ConsumesTags Negative   Luxury 217 · BodyRemains 70 · Research 49 · Maze 28
    ProducesTags Negative   BodyRemains 110 · Luxury 90 · Research 44 · Maze 8
    Positive (for scale)    ProducesTags Waste 1,048 · ConsumesTags Supplies 913
                            ConsumesTags Common 679 · ProducesTags Common 660

**What `Negative` means is not established.** Most likely an explicit exclusion —
*this place will not take Luxury* — but it could be a demand modifier.
**Do not publish an interpretation. It is testable at a kiosk**, which is another
question for the first real capture session.

**`Disabled` is false on all 965** — nothing is switched off.

---

# 8. UEX `categories.json` — 100 rows, and it is not just items

    type       item 66 · service 23 · contract 11
    section    General 33 · Utility 11 · Clothing 10 · Vehicle Weapons 8
               Systems 7 · Armor 6 · Miscellaneous 5 · Data 3
               Personal Weapons 2 · Commodities 2 · Avionics 2 · Other 2
    is_mining  4 of 100

**UEX categorises services and contracts, not only items** — 34 of its 100
categories are non-item. **Nothing in this project has looked at what sits
behind them**, and it is another route to the mission/service side.

**A `Commodities` section exists in UEX's own taxonomy** — further support for
§2 of the previous report: the commodity side of UEX was simply never requested.

---

# 9. THE REPO'S OWN DIRECTORIES — all accounted for

    checks/            the auditor layer + 6 _verify_*.py files
    pkg/               pgconn · pipelinelog
    registry-builder/  Go, with a compiled test binary checked in
    watcher-go/        the handoff watcher
    schema-init/       DDL ownership
    sc-ships/          per-ship model folders — 100i, 125a, 135c, 300i ...
    logs/              inbox_watcher · registry_builder · schema_init ·
                       checks_scheduled · ship_components_audit (json + txt)
    releases/          v0.3.0 .. v0.3.9 html
    _zip_archive/      8+ zips incl. "auto handoffs.zip", "bigboys.zip"
    _needs_review/ _to_delete/   quarantine, working as designed
    exports/           EMPTY

**Two things to flag, both small:**

**`registry-builder/registry_builder_test.exe` is a compiled test binary in
version control.** It will rot and it bloats clones. **Should be gitignored.**

**`data-layerrawhardpoints/ship_specs.json` is real data, not junk.** It is a
proper ship spec array — `uuid`, `name`, `game_name`, `slug`, `class_name`,
`port_tags`, `sizes {length, beam, height}`. **Do not delete it with the two
empty malformed directories.** Check whether its content is duplicated in
`data-layer/raw/` before moving it, then fix the path-join bug that put it
there.

---

# 10. WHAT ALL THIS CHANGES

**Corrections to standing project claims, all three from these two reports:**

    "no item images, zero"          -> 39.1% have a known image.
                                       It is a PERMISSION problem now, not a
                                       data problem.  §1
    "items/ is items.json split"    -> ~850 MB of Raw never opened, carrying
                                       the 3D model path per item.  §2
    "board contents unobtainable"   -> capacity and refresh ARE in the files.
                                       Only tonight's offers are not.  §5

**New capabilities that need no capture and no external source:**

    dismantle / salvage returns for every craftable        §3
    cargo mass by commodity, and a real commodity taxonomy §4
    hauling manifests in SCU, joined to commodities        §5
    mission chains, enemy counts, crime-stat gates         §5
    the law model - who polices where, and the fine        §6
    per-item 3D model paths into Data.p4k                  §2

---

# 11. WHAT IS STILL UNOPENED — the honest remainder

    items/ Raw blocks       ~850 MB. Sampled, not swept. §2
    ObjectiveTokens · EntitySpawns · PropertyOverrides · BrokerReputation*
                            seen but not decoded
    tags.json               18,844 rows, examined 2 August, engine tree,
                            not re-examined
    labels.json             90,121 keys, counted, never mined for anything
                            except keybinds and item descriptions
    UEX items_category_*    56 files with data, never compared against
                            items_prices_all
    wiki description/       present on the 12,283 rows; under the parked
    description_data        text-rights question, deliberately not read
    _zip_archive/           8+ zips, contents unknown

**Everything else in `data-layer/` has now been opened at least once.**

---

# 12. NOT VERIFIED

- **Whether Cornerstone permits use or hotlinking of `cstone.space` images.**
  §1. **Nobody has asked. Do not use them.**
- **Whether the 4,805 image rows join cleanly to our UUIDs.** Not tested.
- **Whether every `SGeometryResourceParams` path resolves inside `Data.p4k`.**
  §2. One sample checked, not swept.
- **What `Negative` means in the tag arrays.** §7.
- **What `SCItemPurchasableParams` contains.** §2. Present on ~50%, never opened.
- **The contract block counts are a 1-in-7 sample.** §5.
- **Whether `ship_specs.json` duplicates `data-layer/raw/`.** §9.
- **`Instability`, `Volatility` and `Tier` on commodities** are present on 42,
  1 and 27 rows respectively. **Sparse enough that they may be abandoned
  fields.** Do not build on them.
