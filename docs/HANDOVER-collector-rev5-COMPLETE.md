# THE CREW COLLECTOR — complete handover

    id        WO-COLLECT-01 rev 5 — SUPERSEDES rev 1, 2, 3, addendum A,
              addendum B, and the rev 4 findings note. One document. Read only this.
    from      C2, 2026-08-06
    to        C1 -> Claude Code
    repo      C2 wrote nothing except inbox/*.md
    contains  what is in the data folders (verified this session, on the machine),
              what that deletes from the build, and the full collector spec.

**C1 — your judgement is wanted, not just your execution.** Points marked
**[C1]** are open calls where you have context I do not: what Code can actually
land in an evening, what the repo will tolerate, and what has already been tried.
**If a design decision here is wrong, say so and change it.** They are collected
again in Part 8 so nothing has to be hunted for.

---

# PART 0 — WHAT THIS IS FOR

**A small Windows program Sleven and a handful of crew run while playing, that
collects Star Citizen data the game files do not contain.**

**Hard constraint, first because it shapes everything: nothing in this tool may
call a language model or any paid service.** It runs offline, costs nothing per
use, and has no account, no server and no API. The AI Historian is a separate
product and its vision work is filed separately in
`claude/historian-vision-architecture.md`. **Do not merge them.**

---

# PART 1 — WHAT IS ACTUALLY IN THE DATA FOLDERS

**Read directly off Sleven's machine this session, snapshot
`20260801T204744Z`, via the Cowork device bridge. Every number below was counted
this session. Nothing here is carried from an older document.**

Snapshot contents and sizes:

    items.json          128,570,490      ships.json           90,706,055
    fps-items.json       49,454,254      ship-items.json      29,278,707
    labels.json          11,380,772      blueprints.json      10,239,541
    trade_locations.json  3,624,811      starmap.json          3,161,905
    tags.json             2,848,050      starmap_positions.json  759,576
    manufacturers.json       48,392
    + directories: blueprints/ contracts/ factions/ items/ resources/ ships/

## 1.1 `starmap.json` is a different file from the positions file

**2,054 entities, 24 fields, all populated.** `starmap_positions.json` holds
1,774 entities with x/y/z. **Only 1,183 UUIDs appear in both.**

**They are complementary and nobody in this project has ever joined them.** The
union is larger than either, and the metadata lives in one file while the
coordinates live in the other.

Fields on all 2,054:

    UUID · Name · Description · ParentUUID · NavIcon · RespawnLocationType
    IsScannable · HideInStarmap · HideInWorld · HideWhenInAdoptionRadius
    BlockTravel · OnlyShowWhenParentSelected · ShowOrbitLine · NoAutoBodyRecovery
    Size · MinimumDisplaySize · QuantumTravel · LocationHierarchyTag · Type
    Jurisdiction · Affiliation · RadarContactType · AsteroidRing · Amenities

**`Type` is an object, not a string:** `{Name, Classification, UUID,
SpawnNavPoints, ValidQuantumTravelDestination}`.

    Type.Name    993 Outpost · 685 Asteroid · 134 Asteroid_ValidQT · 102 Manmade
                  42 Manmade_VisibleOnInteraction · 19 Anomaly · 19 Moon
                  16 PointOfInterest · 14 Planet · 7 LandingZone
                   7 Outpost_InvalidQT · 4 NavPoint · 4 SolarSystem · 3 Star
                   2 JumpPoint · 1 YouAreHere · 1 QuantumTracePoint
                   1 CardinalPoint

    ValidQuantumTravelDestination      1,333 true · 721 false
    QuantumTravel                      1,561 carry {AdoptionRadius, ArrivalRadius,
                                       ObstructionRadius, ArrivalPointDetectionOffset,
                                       SubPointRadiusMultiplier} · 493 null
    LocationHierarchyTag               599 carry {Name, UUID}
    NavIcon                            1,296 Default · 611 Outpost · 105 Station
                                       19 Moon · 14 Planet · 6 LandingZone · 3 Star

## 1.2 `Amenities` — the most useful thing found this session

**281 locations carry an amenity list. 22 distinct service types.**

    348  Vehicle Services                    52  Clinic
    225  Commodity Trading - Freight Elev.   51  Buy Clothing
    204  Hangar L                            50  Docking
    121  Landing Pad M                       32  Rent Vehicles
     71  Buy Armor                           31  Refinery
     70  Buy Weapons                         28  Commodity Trading - Loading Dock
     58  Food Court                          26  Garage
     53  Buy Ship Items and Weapons          19  Buy Vehicles
     19  Landing Pad L                        9  Landing Pad S
      6  Hangar XL                            6  Hospital
      4  Buy and Rent Vehicles                1  Landing Pad XL

**This is a machine-readable answer to "what can I do at this station", and it is
the first thing in this project that identifies which locations have shops
without going through UEX at all.**

**For the collector it is a targeting list.** 253 commodity trading points and 31
refineries exist, and **we hold zero commodity prices.** See §5.3.

## 1.3 Law and territory — present, never surfaced

    Jurisdiction         101 entities, each {Name, UUID, BaseFine,
                         MaxStolenGoodsPossessionScu, IsPrison}
    Affiliation           53 entities (45 "<= UNINITIALIZED =>",
                                       8 "Private Security")
    RadarContactType     107 entities {DisplayName, IsObjectOfInterest,
                                       TagName, TagUUID, UUID}
    RespawnLocationType  266 Hospital · 82 Other · 1 each Prison, PrisonExit,
                         CriminalLocation, CriminalHospital · 1,702 None
    BlockTravel            7 true
    IsScannable          206 true
    AsteroidRing           2 entities {DensityScale, Depth, InnerRadius,
                                       OuterRadius, SizeScale}

Verbatim example: **People's Service Station Lambda → People's Alliance, base
fine 125, max stolen goods 1 SCU, not a prison.**

**"Where can I go with stolen cargo and what does it cost if I'm caught" is
answerable from data we have held since 1 August.**

## 1.4 Jump points — 19, route graph readable from the names

    Stanton - Terra          Stanton - Magnus        Stanton-Pyro
    Stanton-Pyro Wreck Site  Pyro - Terra            Pyro - Cano
    Pyro - Hadrian           Pyro - Oso              Pyro - Nyx
    Jump Point Pyro Castra   Nyx - Bremen            Nyx - Castra
    Nyx - Odin               Nyx - Tohil             Nyx - Virgil
    Nyx - Pyro               Hurston - MicroTech     MicroTech - Hurston

Positional entities by system: **stanton 805 · nyx 678 · pyro 291.**

**The destinations include systems that are not playable** — Terra, Magnus,
Castra, Bremen, Odin, Tohil, Virgil, Cano, Hadrian, Oso. **The route graph in the
files is larger than the game**, which is publishable content in its own right.

**Caution: only 6 of the 19 resolve to a system through the positions file.** The
other 13 have no coordinates. **Do not show distances for those.**

## 1.5 `ship-items.json` — 5,384 rows, and fuel per jump is computable

Type distribution:

    1077 Paints          885 ManneuverThruster   381 MainThruster
     320 WeaponAttachment 317 Turret             238 FlightController
     210 Armor            202 WeaponGun          188 WeaponDefensive
     182 FuelTank         155 FuelIntake         150 QuantumFuelTank
     145 MissileLauncher  143 CargoGrid           94 Flair_Surface
      88 PowerPlant        81 Cooler              77 Radar
      73 Shield            68 Missile             63 QuantumDrive
      31 ExternalFuelTank  23 WeaponMining        22 Container
      14 BombLauncher      13 LifeSupportGenerator 12 JumpDrive
      12 TractorBeam        9 SalvageHead          9 SalvageModifier
       7 SelfDestruct       7 EMP                  6 QuantumInterdictionGenerator
       3 Transponder        3 Bomb                 2 Scanner

**Every one of the 63 `QuantumDrive` entries carries a full fuel and travel
model.** Measured ranges across all 63:

    FuelConsumptionSCUPerGM      0.008  – 0.12      15 distinct
    FuelRequirement10GM          0.08   – 1.2       15 distinct
    FuelEfficiencyGMPerSCU       0.42   – 2.95      35 distinct   ** see caution
    TravelTime10GMSeconds        57     – 140       30 distinct
    QuantumFuelRequirement       0.0049 – 1         50 distinct
    StandardJump.DriveSpeed      1.38e8 – 8.76e8    36 distinct
    StandardJump.SpoolUpTime     4      – 9
    StandardJump.CooldownTime    0      – 92.07
    CalibrationRate              1000 on all 63

Plus a parallel `SplineJump` block, a `Heat` block, `DisconnectRange`,
`JumpRange`, and calibration angle limits.

**Tanks:** 150 `QuantumFuelTank` with `{Capacity, HydrogenMaxFlowMultiplier,
QuantumMaxFlowMultiplier}`. 12 `JumpDrive` with `{AlignmentRate,
AlignmentDecayRate, TuningRate, TuningDecayRate, FuelUsageEfficiencyMultiplier}`.

### This makes it arithmetic, not observation

    fuel for a route  =  distance_Gm x FuelConsumptionSCUPerGM
    travel time       =  distance_Gm / 10 x TravelTime10GMSeconds
    ship range        =  sum(tank Capacity) / FuelConsumptionSCUPerGM

**We hold coordinates for 1,774 entities, and `ships.json` carries the `Loadout`
array for all 316 ships naming each ship's drive and tanks.**

**A full route-cost and range table, every ship against every destination, is
computable from files on disk with no capture at all.**

**Erkul compares drives. Nobody costs a route against real coordinates.**

### One data caution that must not be skipped

**`FuelEfficiencyGMPerSCU` is internally inconsistent.** At
`FuelConsumptionSCUPerGM = 0.01`, efficiency should be 100 Gm/SCU. The file says
**1.65**.

**`FuelConsumptionSCUPerGM` and `FuelRequirement10GM` agree with each other
exactly — 10x — across all 63 drives.** Those two are self-consistent and are the
pair to trust.

**Use `FuelConsumptionSCUPerGM`. Do not publish `FuelEfficiencyGMPerSCU` until
somebody works out what it means.** Two of three agreeing is not proof, but it is
better evidence than the odd one out.

---

# PART 2 — MARKED OFF. Build no reader for these.

| asked for | verdict | where it already is |
|---|---|---|
| star map places | **have it, better** | 2,054 + 1,774, join on UUID — §1.1 |
| jump routes | **have it** | 19 jump points — §1.4 |
| ship names | **have it** | 316 game / 254 live, `ship_resolution.json` |
| mission names, givers, types, factions, locations | **have it** | 5,108 contracts |
| **fuel per jump, per ship, per route** | **have it — computable** | §1.5 |
| **travel time per route** | **have it — computable** | §1.5 |
| **ship quantum range** | **have it — computable** | §1.5 |
| which locations have shops / refineries / clinics | **have it — new** | §1.2 |
| jurisdiction, fines, stolen-goods limits | **have it — new** | §1.3 |
| item catalogue, blueprints, contracts, labels | have it | prior sessions |

**Reading something off a screen when it is already in a file produces worse data
at higher cost.** Five items came off the collector's list this session and two
capabilities arrived that were never on it.

---

# PART 3 — WHAT IS STILL GENUINELY MISSING

**This is now the entire justification for the collector, and it is short:**

    1  mission payouts             CalculatedReward is a BOOLEAN - 8,260 true,
                                   87 null, no numbers. Computed at runtime.
                                   NO FILE CONTAINS IT. Only observable.
    2  commodity prices            zero rows of 23,734
    3  mission board contents      files give the pool a mission comes from,
                                   never what is offered tonight
    4  stock levels / availability nowhere
    5  price actually paid         and it proves the reader - §4.7
    6  shop identity per visit     halves every other target's metadata
    7  price freshness             median 66 days, 75% over 30
    8  refinery rates and yields   nowhere
    9  rental and fuel prices      nowhere
    10 item images                 zero of 7,728

**Rows 1–3 are the build. Nothing obtainable from a file is on this list.**

---

# PART 4 — THE COLLECTOR

## 4.0 What it is

**One Windows folder. No installer.**

    citizen-collector\
      collector.exe          Go, statically linked, single binary
      atlas\                 glyph atlases, one per resolution      §4.3
      names.dat              vocabulary pack                        §4.4
      zones.json             zone grid + learned content classes    §4.2
      profiles.json          session profiles                       §4.9
      config.json            written on first run
      captures\              output

**Unzip, double-click. Uninstall = delete the folder.** No registry, no service,
no admin rights, no OBS, no Python, no AI, no API, no tokens.

**Capture: `Windows.Graphics.Capture`, DXGI Desktop Duplication as fallback.**
OS-level, the same class Snip & Sketch and Xbox Game Bar use. **No injection, no
hooking** — the boundary from `WO-READER-01` is unchanged and non-negotiable.

**Go, not Python** — single binary, no runtime to install, no "install Python
first" conversation with a non-technical friend. Matches the project's existing
move to Go for background components.

## 4.1 The three inputs

    the game log     patch, build, UTC time, gear worn, rough location.
                     Free, no reading required. WO-READER-01.
    the screen       zone watchers - §4.2
    a manual key     grabs and reads the current frame in full.
                     For anything transient.

## 4.2 Zone watchers — a grid, not fixed regions

**Fixed region definitions break every patch and cannot catch anything we did not
anticipate. A grid does neither.**

**Divide the client area into a 6 × 4 grid — 24 zones.** Stored in `zones.json`
**as fractions of the window, never pixels**, so it survives any resolution.

Each zone runs independently and holds a small state machine:

    IDLE      sample 16 pixels, 10x/sec, hash them.  Cost: negligible.
    CHANGED   hash differs from last -> something appeared or moved
    SETTLING  hash changed again -> still moving, do not read yet
    STABLE    hash unchanged for 150 ms after a change -> READ NOW
    READING   full-region read, then back to IDLE

**Reading only ever happens on STABLE.** A panel sliding open, a scene load or a
camera pan never triggers a read — they never settle. **This is what makes 24
zones affordable.**

### How they work in harmony

**Neighbour merging.** Zones going STABLE within the same 150 ms window that
share an edge are **one panel**. Merge and read as a single region. A shop list
spanning six zones is read once, not six times.

**Whole-screen suppression.** More than 14 of 24 zones changing at once is a scene
load or a camera cut. **Read nothing. Reset all zones to IDLE.**

**A read budget.** At most **4 region reads per second**, going to whichever zones
have the largest change area. Everything else waits. **The budget is the ceiling
on cost and it is fixed regardless of what is on screen.**

**Zone learning.** Each zone keeps a running tally of what has been successfully
matched in it. After a session or two, `zones.json` records that zone 3,1 usually
holds prices and zone 0,0 usually holds the info panel. **Learned zones get
budget priority and a tighter expected-content filter, and their content class
selects which vocabularies are live — §4.8.** Nothing hardcoded; learned per
player, per resolution, per UI layout.

**This is why it survives a patch.** CIG moves a panel, the zones relearn. No
region file to update, no silent breakage.

**Each zone reports:** zone id · change area · settle time · extracted text ·
matched entities · confidence.

**[C1] 6×4, 150 ms and 4 reads/sec are my guesses. Make all three config values
and tune on the first real session.** If Code's first capture test says otherwise,
believe the test over this document.

## 4.3 Reading the font — glyph atlas, specified

**This is the answer to "Tesseract may not read the game's font." It is not a
fallback. It is the design.**

**Why not general OCR:** Tesseract's strength is arbitrary unknown fonts. **We do
not have that problem.** Star Citizen renders one UI font, at a handful of sizes,
white-on-dark, with no anti-alias variation between frames. Tesseract's weakness
— thin stylised faces — is exactly our case. **We would pay its cost and get none
of its benefit.**

### Building the atlas — once, by the player, guided

1. Player opens a shop or the info panel and presses the calibrate key.
2. The tool captures the region and **segments it into text lines**, then into
   **character cells** — threshold to binary, find columns of background between
   glyphs.
3. The tool shows the captured strip and asks: **"type exactly what this says."**
4. Character count is matched to cell count. **Each cell is now a labelled
   bitmap.**
5. Repeat over 3–4 strips until the alphabet, digits and punctuation are covered.
   **Ten minutes, once.**
6. Write `atlas\<width>x<height>_<fontsize>.atlas`.

**Ship Sleven's atlas with the tool.** Most players run 1920×1080 or 2560×1440 at
default UI scale, so **most people never calibrate at all.**

### Matching at runtime

1. Threshold the region to binary. **The UI is high-contrast; a fixed threshold
   at ~60% luminance works and is one operation.**
2. Segment into lines by horizontal projection, into cells by vertical.
3. Compare each cell against every atlas glyph of that height.
   **Score = matching pixels / total pixels.**
4. Best score wins. **Below 0.80, emit `?`.**
5. Assemble the string.

**Pure integer comparison. No libraries, no DLL, no model.** Faster than
Tesseract by a wide margin and **exact on a fixed font** rather than
probabilistic.

### Voting

A row visible for two seconds at 10 fps is read twenty times. **Take the majority
string per row.** Twenty-eight to two settles it.

**This is the accuracy mechanism, and it is why scrolling slowly matters** — and
why a single screenshot was always the wrong tool.

## 4.4 The vocabulary pack — `names.dat`

**Everything below is already on disk, collected and gated.**

| list | count | source | use |
|---|---|---|---|
| item names (priced) | 7,728 | UEX | the main match target |
| item files (all) | 21,849 | scunpacked `items/` | catches what UEX lacks |
| FPS gear records | 5,420 | `fps-items.json` | gear shops |
| ship names — game | 316 | scunpacked `ships/` | ship kiosks, spawn menus |
| ship names — live | 254 | `ship_resolution.json` | what we publish |
| shops / terminals | 823 terminals, 479 item shops | UEX | shop identity |
| trade locations | 965 | `trade_locations.json` | stations, refineries |
| starmap entities | 2,054 | `starmap.json` | any place name — §1.1 |
| positioned entities | 1,774 | `starmap_positions.json` | with coordinates |
| systems / planets / moons | 96 / 324 / 73 | source 1 | location |
| stations / cities / outposts | 60 / 5 / 117 | source 1 | location |
| manufacturers | 152 | sources 1/3/6 | disambiguates similar names |
| companies | 311 | sources 1/3/6 | shop branding |
| factions | 74 | sources 1/3/6 | mission and reputation UI |
| blueprints | 1,597 | scunpacked | crafting UI |
| contracts | 5,108 | scunpacked | mission board |
| amenity types | 22 | `starmap.json` — §1.2 | station service panels |
| labels | 90,121 | `labels.json` | **the catch-all, below** |
| keybind actions | 910 | `defaultProfile.xml` | settings screens |

**`labels.json` is the sleeper entry.** 90,121 strings is effectively every piece
of text CIG puts on screen. **Matching against it will not say what a thing is,
but it will say that a string is real game text and not a misread** — exactly the
signal that separates "the OCR failed" from "we found something we have no list
for." **Lowest-priority tier of the cascade.**

### The one list we do not have

**Commodity names.** All 23,734 price rows are gear and components; not one is a
commodity. **The `~200 commodities` figure carried in earlier revisions is mine
and unverified.** `trade_locations.json` records category tags — "Luxury",
"Commodity" — **not item names.**

**Commodity kiosks are the first real target and we would be matching against a
list we do not hold.**

**Action, one request, before build step 5:** UEX publishes a commodities
endpoint separately from prices. **Pull the catalogue even though the prices are
absent.** If it does not exist, commodity names must be collected
open-vocabulary and confirmed by hand the first time — workable, slower, and
better known now than discovered mid-build.

**[C1] This is the one genuine blocker in Part 4. Worth doing before anything
else in the collector.**

## 4.5 The three recognizer classes

Every read passes through three, in order. **A read producing nothing in any of
them is discarded, not stored.**

**Class A — vocabulary.** §4.4. Most of the value, and why no AI is needed.

**Class B — shape.** No list needed; works on the first run, including on screens
never anticipated:

    aUEC price          digits, thousands separators, optional aUEC suffix
    quantity            number + SCU / cSCU / uSCU / units
    percentage          number + %
    duration            mm:ss and hh:mm:ss
    distance            number + km / Gm / AU
    patch / build       N.N.N.NNNNN
    UTC timestamp       from r_DisplayInfo and the log
    stock state         "In Stock" / "Out of Stock" / "No Stock" / "N available"
    column headers      "Buy" / "Sell" / "Price" / "Qty"  -> gives class C
    rate / stat units   dps, m/s, rpm, HP, kW

**Prices and quantities are digit strings — ten glyphs rather than sixty — which
makes them the most reliable thing on the screen, not the least.**

**A price that fails to parse is dropped. Never rounded, never inferred, never
carried from an adjacent row.**

**Class C — structure.** Not the text, the layout. One panel, a two-column table,
or a scrolling list? **Determines whether a name and a number on the same row
belong together — the single most important thing to get right, because a name
paired with the wrong row's price is worse than no price at all.**

Read from the segmentation §4.3 already performs: line positions give rows, a
consistent column gap across ≥3 lines gives columns. **No extra machinery.**

### Then the vocabulary does the rest

**RULED 2026-08-30 BY SLEVEN: EXACT HITS ONLY.** Match against the known list
and **accept only an exact hit. Anything else is discarded.**

This section specified Levenshtein distance at ≤ 20% of string length, with
`Ar?light Pist?l` resolving to Arclight Pistol as the example. Against a
7,728-entry list a 20% edit distance does not resolve a misread - **it picks the
nearest thing, and the output is indistinguishable from a correct read.**

The accuracy mechanism was always the atlas and the twenty-read vote. A glyph
below threshold already emits `?`; a string carrying `?` is not an exact hit and
is discarded. **A discard is a labelled gap, which is worth more than a guess
because a guess never reports one.**

Full reasoning in `workorder-collect-01-rev3.md` §3c and
`docs/RULING_the-reader-gets-no-fuzzy-matching-2026-08-30.md`.

## 4.6 The priors — what we hand each zone

**Zone learning records where things appear. These are the other half: what we
already know, handed in, so a match starts from a short list instead of 7,728.**

**The shop's own inventory, once shop identity resolves.** The strongest prior by
a wide margin. Standing in Casaba Outlet the candidate set drops from 7,728 to
that shop's known stock. **A 20-way match is near-certain where a 7,728-way match
is merely probable.** Unmatched strings then become the interesting result — they
are new stock, which is what we most want to know.

**The patch's known item set.** A name resolving to an item not in this patch is
either a misread or genuinely new. **We can tell which:** matching nothing now but
matching last patch is almost certainly a misread of a familiar name. Matching
nothing anywhere goes to review.

**The player's own loadout, from the log.** Proven — 249 of 298 ClassNames join
across 225 sessions. **The inventory and character panels are predictable before
being read**, making them the ideal calibration target: we know the answer, so a
wrong read is measurable rather than invisible.

**The location's amenities — §1.2.** Standing at a location whose amenity list
says *Refinery* and *Commodity Trading*, the tool knows which panels to expect
**before it sees one.** This is new this session and it did not exist in any
earlier revision.

**Resolution and UI scale** — selects the atlas, read once at startup.
**Current system** — narrows place names.

## 4.7 The event recorder — the second mechanism

**Some of what we need is not text on a screen. It is a value's change across an
event.** *"How much fuel does a jump take"* is never displayed — §1.5 now answers
that from files, but the mechanism is still needed for everything below.

**Build it as its own component.** It shares the atlas, the capture and the zone
grid, and nothing else. **Roughly a tenth of the reader's code.**

| watch | across | gives | held elsewhere? |
|---|---|---|---|
| **aUEC balance** | mission turn-in | **actual payout** | **no — Part 3 row 1** |
| **aUEC balance** | a purchase | **price actually paid** | proves the reader |
| aUEC balance | a sale | actual sell price | 171 of 7,728 items only |
| cargo hold | loading | what was loaded, in SCU | no |
| reputation | turn-in | rep gained per mission | partly |
| wall clock | A to B | real travel time | computable — §1.5, worth checking |
| quantum fuel | a jump | observed vs computed | **computed — §1.5. Validate it** |

### The delta that proves the reader — rule 12, properly

**The strongest reason to build this is not the data. It is that it makes the OCR
falsifiable.**

The kiosk says 4,050. You buy it. The balance drops by 4,050. **The read is
confirmed by arithmetic, not by a confidence score.**

If the balance drops by 4,650, the reader misread a digit and we know it, exactly,
on that row. **That is a check that can genuinely fail and names its own cause —
which is the standing bar, and no confidence threshold ever meets it.**

**Every confirmed purchase is a free labelled example for the atlas.** Drift in
the agreement rate is early warning that CIG changed the font.

**[C1] This rests on one untested assumption: that the aUEC balance is on screen
often enough to catch both sides of a transaction.** It is a mobiGlas element and
may not be visible at a kiosk. **If it is not, §4.7 does not work.** Worth
checking in the same session as the font test.

## 4.8 The self-checks

**Standing rule 12: a check that cannot fail is not a check.** Each of these can
fail, and each names its own cause.

**Known-shop agreement rate.** At a shop whose stock we hold, record what fraction
of read rows match. **A drop has two meanings and they are distinguishable:** if
the unmatched strings match *some* catalogue item, the shop changed — a finding
worth having. If they match nothing at all, reading broke.

**Price plausibility.** More than 10x or less than 1/10 of the last known price is
**held for review, not published and not discarded.** Either a misread digit or a
genuine repricing, and both deserve a look.

**Patch agreement.** The patch read off screen must equal the patch from the log.
**A mismatch means a stale frame or the wrong window** — the failure most likely
to poison data silently, caught by one comparison.

**Dead zone report.** A zone with no match in ten sessions is covering nothing or
sized wrong. **Report it. Do not silently keep polling** — that is the shape of
the handoff-watcher defect this project has hit three times.

**Atlas confidence drift.** Falling mean per-glyph score means CIG changed the
font or the UI scale moved. **Surface it before the data degrades.**

### Vocabulary namespacing — cheap now, a rewrite later

**Adding 5,108 mission titles to the same match pool as 7,728 item names makes
them compete.** A mission titled *"Arclight"* competes with the pistol, and every
list added makes every other list slightly less accurate.

**Namespace the vocabulary by the zone's learned content class.** A zone classed
*shop list* matches items and prices only; *mission board* matches titles, givers
and factions only. **Zone learning already produces the classification — this
just uses it.**

**Do this from the start.** Retrofitting after the vocabulary is one flat file is
a rewrite.

## 4.9 Session profiles — how "collect everything" actually works

**The read budget is fixed at 4 regions/sec, and that cap is what makes 24 zones
affordable. Adding targets does not add capacity — it divides it.** Forty things
watched at once means each is watched a fortieth as often, and a scrolling list
read at a fortieth rate misses most rows.

**The resolution is that everything does not have to happen at once.**

**A selector at startup:** `shopping · missions · hauling · mining · exploring ·
everything`. The profile sets which vocabularies are live and which zones get
budget priority. **Nothing is disabled — the budget is aimed.**

**Run a shop session tonight and a mission-board session tomorrow and inside a
week the whole list is covered at full accuracy, instead of everything at once at
a fortieth of it.**

**This is the generic version the project's architecture rules ask for.**
Recognizers generic, vocabularies as data files, profiles as a list. **Adding a
target later costs a list entry, not a code change.** That is "collect everything
we possibly can" as a design property rather than a switch, and it is the
difference between a tool that survives a new game system and one that gets
rewritten when CIG ships something we did not anticipate.

**`everything` stays as a profile** — right for a long session where nothing
specific is being hunted, and honest about the trade.

## 4.10 Feedback — sound first, screen optional

**Default: sound.** Works on one monitor, in any display mode, including
exclusive fullscreen.

    short tone     matched something new
    lower tone     read text, matched nothing
    silence        nothing being read

**The beep rate is the scroll-speed gauge.** Tones stopping while still scrolling
means going too fast. **Learned in one session without looking away from the
game.**

**Optional: a ~200×40 top-most status chip** — *"watching · 47 captured"*.
**A top-most window is not injection** — SCOverlay is exactly this and is posted
on RSI's Community Hub. It will not draw over exclusive fullscreen, which is why
sound is the default.

## 4.11 Output

**There is no video. Frames are read and discarded.**

    captures\session_<patch>_<utc>.json
    captures\crops\<row-id>.png          ~200x40 strip per row

    { "captured_at": "...", "patch": "4.9.188.23497",
      "install_id": "<random per install, NOT a person>",
      "profile": "shopping",
      "location": {"system":"Stanton","place":"reststop","shop":"Casaba Outlet"},
      "rows": [ {"name":"Arclight Pistol","matched_id":1234,"price":4050,
                 "confidence":0.93,"frames":28,"zone":"3,1","crop":"r001.png"} ] }

**A session is kilobytes of JSON and a few hundred KB of crops. It fits in a
Discord message.**

**The crops are why it is reviewable.** Every row carries the strip of screen it
came from, so a claim can be checked without anyone sending gigabytes. **Better
provenance than UEX has.**

**Stripped before the file exists, never written:** player handle, session id,
shard id, machine specs, GPU, CPU, `[Social]` / `[Login]` / `[Network]` content,
chat, other players' names.

## 4.12 The anti-dictionary — what it must refuse to look at

**Hard exclusion, not filtering. A filter can fail open; an excluded zone is
never read, so there is nothing to leak.**

**Zones overlapping the chat region are never sampled.** Not read and discarded —
**never read.** Set at first run, part of consent.

**A zone whose text matches the chat shape** — timestamp, name, colon — **has its
entire output dropped and is muted for the rest of the session.** Not just the
offending line.

**Any string matching a player-handle shape and no vocabulary entry is
discarded**, never held for review, never written to a crop.

**Never recognised at all, by design:** other players' names, party and org
lists, friend lists, shard ids, session ids, `[Social]`, `[Login]`, `[Network]`.

**This is the section to hand a friend when they ask what it does.**

**[C1] Is the chat region at a fixed position across UI scales?** If not, the
exclusion must be drawn by the player at first run. I do not know the answer.

## 4.13 Getting the data back

**"Export session" → one zip → they send it however you already talk.** No server,
no account, no upload endpoint. **Do not build infrastructure for five people.**

**It lands in a holding pen. Sleven approves before anything reaches the data.**
A misconfigured install must not be able to quietly poison prices. **Auditors
flag, they never auto-fix — an OCR pass is an auditor.**

**If it ever outgrows that**, a shared cloud folder is next and an upload endpoint
after that. **Building either now solves a problem that does not exist**, and the
project's own rule is two or three concrete cases before generalising.

## 4.14 First run

One consent page. **Nothing runs until they click yes.**

- reads: the game log, and the screen while the game is focused
- never reads: chat, other players, anything outside the game window
- sends: **nothing, automatically, ever.** Export is manual.
- stopping: a key, or close it. **Off means off.**
- removing: delete the folder

**Audible or visible indicator whenever it is watching. No silent operation.**

## 4.15 What it will not do

- **No stock quantities** unless they are on screen.
- **No precise position.** Location resolves to "a reststop in Stanton", not a
  floor.
- **No other players.** It knows only the session it runs in.
- **No AI.** It does not answer questions, explain anything, or reason. It reads a
  list and matches it. **That is the point.**

---

# PART 5 — TONIGHT

**Straight answer: the full collector is not a one-evening build.** Atlas, zone
grid, vocabulary cascade and event recorder are several days. **Promising it
tonight costs an evening and delivers nothing.**

**But tonight does not have to be wasted.**

## 5.1 Ship the dumb half — the manual-key grabber

**Capture tonight, read later.** §4.1 already has a manual key. **Ship only that,
with no reading at all:**

    press a key  ->  save a PNG of the game window
                     + patch, build, UTC time and location from Game.log
                     + a sequence number
                     ->  captures\<utc>_<seq>.png  +  .json sidecar

**No OCR. No atlas. No vocabulary. No zones.** A screen grab and a log read, both
solved problems.

**Why this is the right first thing and not a compromise:**

- **The frames are the raw material and they do not expire.** Every kiosk
  photographed tonight is readable next week by a reader that does not exist yet.
  **Reading in batch, off the game machine, is the more accurate path anyway.**
- **It closes the font question tonight.** Whether the UI font is legible in a
  captured frame at Sleven's resolution has been open since 2 August and gates
  the entire reading half.
- **It is the ten-minute test, automated.** Kiosk, mobiGlas, `r_DisplayInfo` 1–4,
  captured with log context attached instead of loose in a screenshots folder.
- **It is safe to hand a crew member immediately** — it produces no data, only
  evidence, so it cannot poison anything.
- **It is the atlas input.** §4.3 needs captured text strips to build from.

**[C1] This is the piece with the deadline. If Code can only land one thing
tonight, land this.**

## 5.2 In parallel, no game needed

**The route-cost table — §1.5.** Pure computation over files on disk. The largest
new capability found today, needs nothing from Sleven, and **a better use of
Code's evening than the collector**, because the collector's next step is gated on
frames that do not exist yet.

**And the starmap join — §1.1.** 2,054 + 1,774 on UUID, 1,183 overlap. Nobody has
done it. It is the input the route table needs anyway.

## 5.3 The targeting list — §1.2

From `Amenities`, joined to what UEX already gives us:

    31 refineries · 253 commodity trading points · 70 Buy Weapons ·
    71 Buy Armor · 53 Buy Ship Items · 51 Buy Clothing · 32 Rent Vehicles

**Rank by what we hold nothing for. Hand each crew member four named places, not
"go look at shops."**

**Do this before the crew build, not after.** It is what makes the first real
capture session productive instead of exploratory, and it is the difference
between five people wandering and five people covering a map.

---

# PART 6 — BUILD ORDER

    TONIGHT
      1  the manual-key grabber: PNG + log sidecar. No reading.          §5.1
      2  point it at a kiosk, the mobiGlas, and r_DisplayInfo 1-4.
         THE OUTPUT IS THE ANSWER TO THE FONT QUESTION.                  §5.1

    IN PARALLEL, NO GAME NEEDED, NO DEPENDENCIES
      3  join starmap.json to starmap_positions.json on UUID             §1.1
      4  route-cost / range / travel-time table                          §1.5
      5  the amenities targeting list                                    §1.2, §5.3

    BLOCKER, ONE REQUEST
      6  pull the UEX commodity catalogue                                §4.4

    THEN, IN ORDER
      7  log reader (WO-READER-01), offline, against the 225 logs
      8  glyph atlas built from tonight's frames                         §4.3
      9  batch reader over saved frames, off the game machine
     10  the zone grid, live, reporting change events only - prove
         24 zones cost nothing and STABLE fires where expected           §4.2
     11  glyph matching + vocabulary on the info panel only              §4.3-4.5
     12  commodity kiosks                                                Part 3 row 2
     13  event recorder, aUEC balance at a purchase                      §4.7
     14  vocabulary namespacing by zone class                            §4.8
     15  voting, sound, export                                           §4.3, 4.10, 4.13
     16  session profiles                                                §4.9
     17  review pen                                                      §4.13
     18  mission board reading                                           Part 3 row 3
     19  the crew, with consent and field stripping                      §4.12, 4.14

**Sleven runs 1–17 himself before anyone else installs anything.**

**Steps 3, 4 and 5 produce publishable site features and have no dependency on
anything. They should not wait behind the collector.**

---

# PART 7 — ACCEPTANCE

    24 zones idle                    < 1% of one CPU core
    read budget                      never exceeds 4 regions/sec
    scene load                       >14 zones changing triggers zero reads
    atlas match                      >= 0.80 per glyph or emit '?'
    vocabulary match                 EXACT hit or discard - no edit distance
    price parse failure              dropped, never inferred
    known-shop agreement             reported every session, both failure modes
                                     distinguished
    purchase delta                   read price == balance delta, or the row
                                     is flagged
    output                           contains no handle, no chat, no other player
    chat zones                       never sampled, not merely filtered
    export                           one zip, sends in a chat message
    nothing publishes                without passing the review pen

---

# PART 8 — [C1] OPEN CALLS, COLLECTED

**These are yours. I do not have the context to close them.**

1. **The UEX commodity catalogue pull — §4.4.** The one genuine blocker in the
   collector. Worth doing ahead of everything else in Part 4.
2. **Can Code land the grabber tonight — §5.1?** If only one thing ships, this is
   it. If it cannot, say so and Sleven should know before he sits down to play.
3. **6×4 grid, 150 ms settle, 4 reads/sec — §4.2.** My guesses. Config values.
   Believe the first capture test over this document.
4. **Is the aUEC balance visible at a kiosk — §4.7?** Untested, and §4.7 does not
   work without it. Same session as the font test.
5. **Is the chat region fixed across UI scales — §4.12?** If not, the exclusion
   must be player-drawn at first run.
6. **Where do CmdrQuattro's mission payout figures come from?** He publishes
   payouts. Look before building the mission board — same discipline that stopped
   us rebuilding Star Binder. **Do not contact him; Sleven has parked that.**
7. **`FuelEfficiencyGMPerSCU` — §1.5.** Three fields, two agree. Someone should
   work out what the third means before anything publishes it.
8. **Ordering of steps 3–5 against the grabber.** They are independent; you know
   what Code's evening actually holds.

---

# PART 9 — NOT VERIFIED

- **Whether WGC captures Star Citizen in exclusive fullscreen.** Generally yes;
  untested. DXGI fallback exists for this.
- **Whether the game font is legible in a captured frame.** Open since 2 August.
  **§5.1 exists to close it tonight.**
- **Whether the aUEC balance is on screen at a kiosk.** §4.7 rests on it.
- **Whether column detection survives a scrolling list**, rows entering and
  leaving mid-frame. Class C is the least tested idea in this document.
- **Whether shop stock is stable enough for the §4.6 prior to help.** Heavy
  rotation weakens it.
- **Whether `labels.json` matching is fast enough at 90,121 entries** to sit in
  the read path. If not, it moves to the review step where time is free.
- **Whether the game's UI anti-aliases differently at different scales**, which
  would need one atlas per UI scale as well as per resolution.
- **Whether computed route fuel matches observed consumption.** Spool, partial
  burns and drive efficiency are unmodelled. **The computed table is a claim and
  the first observed jump is its test** — a reason to keep §4.7 on the roadmap
  even though §1.5 removed its urgency.
- **Whether `Amenities` is complete or only covers surveyed locations.** 281 of
  2,054 carry one. **Absence of an amenity is not evidence of absence.**
- **Whether payouts vary by player** — reputation, org, insurance, shard state.
  **If they do, an observed payout is one player's number and must publish as a
  range across observations, never as a fact.** Nobody has checked.
- **Whether the 13 unpositioned jump points can be placed at all.** §1.4.
- **Antivirus.** A small unsigned binary that reads game files and captures the
  screen is exactly that shape. **Expect it. Do not tell friends to add
  exclusions.** Plan for signing or accept the friction.
- **`items.json` (128 MB), `ships.json` (90 MB) and `fps-items.json` (49 MB) were
  not opened this session.** Only `ship-items.json` and the two starmap files
  were. **There is more in there.**
