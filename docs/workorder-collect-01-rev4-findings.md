# FINDINGS — the unopened files, opened. And the revised collector build.

    id       WO-COLLECT-01 rev 4 — supersedes rev 3 §7 of addendum B
    from     C2, 2026-08-06
    for      C1 -> Claude Code
    landed   by C1, 2026-08-06. C2 cannot write to the repository.
    method   read directly off Sleven's machine, snapshot 20260801T204744Z,
             via the Cowork device bridge. Every number below was counted
             this session, not carried from a prior doc.

**Sleven's instruction: check the files, mark off what we already have, then get
the collector running tonight.**

**Two build steps are now deleted outright, one new capability appeared that
nobody planned, and the collector gets a targeting list it did not have.**

---

# PART 1 — WHAT THE INSPECTION FOUND

## 1.1 `starmap.json` is not a bigger positions file. It is a different file.

**2,054 entities, 24 fields each.** `starmap_positions.json` holds 1,774 with
coordinates. **Only 1,183 UUIDs are in both.** They are complementary — the union
is larger than either, and **nobody in this project has ever joined them.**

The fields, all populated on all 2,054:

    UUID · Name · Description · ParentUUID · NavIcon · RespawnLocationType
    IsScannable · HideInStarmap · HideInWorld · HideWhenInAdoptionRadius
    BlockTravel · OnlyShowWhenParentSelected · ShowOrbitLine · NoAutoBodyRecovery
    Size · MinimumDisplaySize · QuantumTravel · LocationHierarchyTag · Type
    Jurisdiction · Affiliation · RadarContactType · AsteroidRing · Amenities

**`Type` is an object**, not a string: `{Name, Classification, UUID,
SpawnNavPoints, ValidQuantumTravelDestination}`.

    Type.Name          993 Outpost · 685 Asteroid · 134 Asteroid_ValidQT
                       102 Manmade · 42 Manmade_VisibleOnInteraction
                        19 Anomaly · 19 Moon · 16 PointOfInterest · 14 Planet
                         7 LandingZone · 7 Outpost_InvalidQT · 4 NavPoint
                         4 SolarSystem · 3 Star · 2 JumpPoint
                         1 YouAreHere · 1 QuantumTracePoint · 1 CardinalPoint

    ValidQuantumTravelDestination     1,333 true · 721 false

## 1.2 `Amenities` — the find of the session

**281 locations carry an amenity list. 22 distinct service types.** This is a
machine-readable answer to *"what can I actually do at this station"* and **it is
the first thing found in this project that says which locations have shops
without going through UEX at all.**

    348  Vehicle Services                 52  Clinic
    225  Commodity Trading - Freight Elev 51  Buy Clothing
    204  Hangar L                         50  Docking
    121  Landing Pad M                    32  Rent Vehicles
     71  Buy Armor                        31  Refinery
     70  Buy Weapons                      28  Commodity Trading - Loading Dock
     58  Food Court                       26  Garage
     53  Buy Ship Items and Weapons       19  Buy Vehicles · 19 Landing Pad L
                                           9  Landing Pad S · 6 Hangar XL
                                           6  Hospital · 4 Buy and Rent Vehicles
                                           1  Landing Pad XL

**Why this matters more to the collector than to the site: it is a target list.**
**253 commodity trading points and 31 refineries — and we hold zero commodity
prices.** That converts crew collection from *wander around and hope* into
*here are 31 named refineries, we have nothing from any of them, take four.*
**§4.3.**

## 1.3 Law and territory — never surfaced anywhere

    Jurisdiction        101 entities, each {Name, UUID, BaseFine,
                        MaxStolenGoodsPossessionScu, IsPrison}
    Affiliation          53 entities  (45 still "<= UNINITIALIZED =>",
                                       8 "Private Security")
    RadarContactType    107 entities, {DisplayName, IsObjectOfInterest, TagName…}
    RespawnLocationType 266 Hospital · 82 Other · 1 each Prison, PrisonExit,
                        CriminalLocation, CriminalHospital
    BlockTravel           7 true
    IsScannable         206 true

Example, verbatim: **People's Service Station Lambda → People's Alliance, base
fine 125, max stolen goods 1 SCU, not a prison.**

**"Where can I go with stolen cargo, and what does it cost me if I'm caught" is
answerable from data we have had since 1 August and never opened.**

## 1.4 Jump points — 19, and the route graph is in the names

    Stanton - Terra          Stanton - Magnus         Stanton-Pyro (+ Wreck Site)
    Pyro - Terra             Pyro - Cano              Pyro - Hadrian
    Pyro - Oso               Pyro - Nyx               Jump Point Pyro Castra
    Nyx - Bremen             Nyx - Castra             Nyx - Odin
    Nyx - Tohil              Nyx - Virgil             Nyx - Pyro
    Hurston - MicroTech      MicroTech - Hurston

**Systems with positional data: stanton 805, pyro 291, nyx 678 entities.**

**Note the destinations that are not playable systems** — Terra, Magnus, Castra,
Bremen, Odin, Tohil, Virgil, Cano, Hadrian, Oso. **The route graph in the files
is larger than the game.** That is publishable content in its own right and
nobody else presents it.

**Caution: only 6 of the 19 resolve to a system through the positions file.** The
other 13 exist in `starmap.json` with no coordinates. **Do not present distances
for those.**

**C1 note, landing this:** C1 searched this same file for jump routes earlier the
same session and reported there were none. That was wrong, and the reason is
worth carrying: **C1 searched the field NAMES for jump/route/link/gate and found
nothing, because the routes are not a field — they are entity Names, under a
Type of JumpPoint.** Searching the schema and calling the data absent is a
mistake that will repeat on the three large files nobody has opened yet.
**Search values, not just keys.**

## 1.5 QUANTUM DRIVES — fuel per jump is computable. Delete the build step.

**Addendum B §7 said check before building a measurement rig. Checked. It is all
there.** Every one of the 63 `QuantumDrive` entries carries:

    FuelConsumptionSCUPerGM     0.008  – 0.12    (15 distinct)
    FuelRequirement10GM         0.08   – 1.2     (15 distinct)
    FuelEfficiencyGMPerSCU      0.42   – 2.95    (35 distinct)  ** see caution
    TravelTime10GMSeconds       57     – 140     (30 distinct)
    QuantumFuelRequirement      0.0049 – 1       (50 distinct)
    StandardJump.DriveSpeed     1.38e8 – 8.76e8  (36 distinct)
    StandardJump.SpoolUpTime    4      – 9
    StandardJump.CooldownTime   0      – 92.07
    CalibrationRate             1000, on all 63

Plus `SplineJump` as a full parallel block, a `Heat` block, `DisconnectRange`,
`JumpRange`, and the calibration angle limits.

**And the tanks:** 150 `QuantumFuelTank` entries with `{Capacity,
HydrogenMaxFlowMultiplier, QuantumMaxFlowMultiplier}` — sample capacity 1.1.
Also 182 `FuelTank`, 155 `FuelIntake`, 31 `ExternalFuelTank`, 12 `JumpDrive`
(`{AlignmentRate, TuningRate, FuelUsageEfficiencyMultiplier: 8}`).

### So this is arithmetic, not observation

    fuel for a route   =  distance_Gm  x  FuelConsumptionSCUPerGM
    travel time        =  distance_Gm / 10  x  TravelTime10GMSeconds
    ship range         =  sum(tank Capacity) / FuelConsumptionSCUPerGM

**We hold coordinates for 1,774 entities and `ships.json` carries the `Loadout`
array for all 316 ships, which names each ship's drive and tanks.**

**A full route-cost and range table for every ship against every destination is
computable tonight, from files already on disk, with no capture at all.**

**Erkul compares drives. Nobody costs a route against real coordinates.**

**Worked end to end by C1 on landing, as a check that the arithmetic holds:**
HDSF-Adlai → Area18 is 22.882 Gm; the most efficient drive (Vulcan) costs
0.183 SCU, the least efficient (Mauler) 2.746 SCU. Stanton alone has **148,785
quantum-travel destination pairs.**

### One data caution, and it matters

**`FuelEfficiencyGMPerSCU` is internally inconsistent.** At
`FuelConsumptionSCUPerGM = 0.01`, efficiency should be 100 Gm/SCU. The file says
**1.65**.

**`FuelConsumptionSCUPerGM` and `FuelRequirement10GM` agree with each other
exactly (10x) across all 63 drives.** Those two are self-consistent and are the
pair to trust.

**Use `FuelConsumptionSCUPerGM`. Do not publish `FuelEfficiencyGMPerSCU` until
somebody works out what it actually means.** Two of three fields agreeing is not
proof, but it is better evidence than the odd one out.

---

# PART 2 — MARKED OFF. Do not build a reader for these.

| Sleven's item | verdict | where it is |
|---|---|---|
| star map places | **have it, better** | 2,054 + 1,774, join on UUID |
| jump routes | **have it** | 19 jump points, §1.4 |
| ship names | **have it** | 316 game / 254 live |
| mission names, givers, types, factions, locations | **have it** | 5,108 contracts |
| **fuel per jump, per ship, per route** | **have it — computable** | §1.5 |
| **travel time per route** | **have it — computable** | §1.5 |
| **ship quantum range** | **have it — computable** | §1.5 |
| which locations have shops, refineries, clinics | **have it — new** | §1.2 |
| jurisdiction, fines, stolen-goods limits | **have it — new** | §1.3 |
| item catalogue, blueprints, contracts, labels | have it | prior sessions |

**Five things came off the collector's list this session and two arrived that
were never on it.** That is the point of checking before building.

---

# PART 3 — WHAT IS STILL GENUINELY MISSING

**Unchanged by any of the above, and now a short, hard list:**

    1  mission payouts              CalculatedReward is a BOOLEAN. No number
                                    exists in any file. Only observable.
    2  commodity prices             zero rows held
    3  mission board contents       files give the pool, never tonight's board
    4  stock levels / availability  nowhere
    5  price actually paid          proves the reader - addendum B §4
    6  price freshness              median 66 days
    7  refinery rates and yields    nowhere
    8  rental and fuel prices       nowhere
    9  item images                  zero of 7,728

**Everything the collector is for is on this list, and it is shorter and sharper
than it was this morning.** Nothing that could be got from a file is on it.

---

# PART 4 — TONIGHT

**Straight answer: the full collector is not a one-evening build.** The glyph
atlas, the zone grid, the vocabulary cascade and the event recorder are several
days of work. **Anyone who tells you that ships tonight is setting you up to lose
an evening and have nothing.**

**But tonight does not have to be wasted, and it does not have to wait.**

## 4.1 Ship the dumb half. It is the half with the deadline.

**Capture tonight, read later.** Rev 3 §1 already has a manual key. **Ship only
that, with no reading at all:**

    press a key   ->   save a PNG of the game window
                       + the patch, build, UTC time and location from Game.log
                       + a sequence number
                       ->  captures\<utc>_<seq>.png  +  .json sidecar

**No OCR. No atlas. No vocabulary. No zones.** A screen grab and a log read,
both of which are solved problems.

**Why this is the right thing to ship first, and not a compromise:**

- **The frames are the raw material and they do not expire.** Every kiosk you
  photograph tonight is readable next week by a reader that does not exist yet.
  **The reading can happen off the game machine, in batch, with no time pressure
  and no frame-rate cost — which addendum A already said is the more accurate
  path.**
- **It is testable tonight**, against the one thing nobody has confirmed: whether
  the game's font is legible in a captured frame at your resolution. **That
  answer gates the entire reading half and it has been open since 2 August.**
- **It is the whole of the ten-minute test**, automated. Kiosk, mobiGlas,
  `r_DisplayInfo` 1–4, all captured with their log context attached instead of
  loose in a screenshots folder.
- **It is safe to hand a crew member immediately.** Nothing to configure, nothing
  to read wrong, nothing to poison the data with — because it produces no data,
  only evidence.

**And it is the first atlas.** §3a of rev 3 needs captured text strips to build
from. **Tonight's frames are that input.**

## 4.2 In parallel, and needing no game at all

**The route-cost table — §1.5.** Pure computation over files on disk. It is the
largest new capability found today, it needs nothing from you, and **it is a
better use of Claude Code's evening than the collector**, because the collector's
next step is gated on frames that do not exist yet.

## 4.3 The targeting list — §1.2

From `Amenities`, with UEX joined for what we already hold:

    31 refineries · 253 commodity trading points · 70 Buy Weapons ·
    71 Buy Armor · 53 Buy Ship Items · 51 Buy Clothing · 32 Rent Vehicles

**Rank by what we hold nothing for. Hand each crew member four names, not "go
look at shops."** This is buildable now, needs no capture, and it is the
difference between five people wandering and five people covering a map.

**Do this before the crew build, not after.** It is also what makes the first
real capture session productive instead of exploratory.

---

# PART 5 — REVISED BUILD ORDER

    TONIGHT
      1  the manual-key grabber: PNG + log sidecar. No reading.            §4.1
      2  point it at a kiosk, the mobiGlas, and r_DisplayInfo 1-4.
         THE OUTPUT IS THE ANSWER TO THE FONT QUESTION.                    §4.1

    IN PARALLEL, NO GAME NEEDED
      3  join starmap.json to starmap_positions.json on UUID.
         2,054 + 1,774, 1,183 overlap. Nobody has done this.               §1.1
      4  the route-cost / range / travel-time table.                       §1.5
      5  the amenities targeting list.                                     §1.2, §4.3

    THEN, IN ORDER
      6  log reader (WO-READER-01), offline, against the 225 logs
      7  glyph atlas built from tonight's frames                           rev 3 §3a
      8  batch reader over saved frames — off the game machine
      9  the zone grid, live                                               rev 3 §2
     10  event recorder, aUEC balance at a purchase                 addendum B §4
     11  vocabulary namespacing by zone class                       addendum B §8
     12  session profiles                                           addendum B §9
     13  mission board reading                                      addendum B §6
     14  crew distribution, consent, field stripping                       rev 3 §7

**Steps 3, 4 and 5 have no dependency on anything and produce publishable site
features. They should not wait behind the collector.**

---

# PART 6 — NOT VERIFIED

- **Whether the 13 unpositioned jump points can be placed at all.** §1.4.
  Do not show distances for them.
- **What `FuelEfficiencyGMPerSCU` means.** §1.5. Three fields, two agree.
- **Whether computed route fuel matches observed consumption in game.** Spool,
  partial burns and drive efficiency are unmodelled. **The computed table is a
  claim, and the first observed jump is its test** — which is a reason to keep
  the event recorder on the roadmap even though §1.5 removed its urgency.
- **Whether `Amenities` is complete or only covers surveyed locations.** 281 of
  2,054 carry one. **The absence of an amenity is not evidence of absence.**
- **Whether the game font is legible in a captured frame.** Still open. **§4.1
  exists to close it tonight.**
- **`items.json` (128 MB), `ships.json` (90 MB) and `fps-items.json` (49 MB) were
  not opened this session.** Only `ship-items.json` (29 MB) and the two starmap
  files were. **There is more in there.**
- **Type.Name counts 2 JumpPoint while §1.4 lists 19 by name.** Noted on landing,
  not resolved. Reconcile before building anything on the jump graph.
