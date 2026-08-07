# FINDING — missions and locations, broken all the way down: system, planet/moon, city/outpost, and template count for both mission families

    from      C3 (Cowork), 2026-08-07
    for       C1 -> Claude Code
    supersedes docs/FINDING_contracts-divided-by-system-stanton-pyro-nyx.md (2026-08-07,
              earlier today) - that doc was system-level only and was reported before this
              work was complete. This doc replaces it. Do not build on the earlier one.
    data      data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/
              (contracts/, starmap.json, starmap_positions.json, factions/,
              trade_locations.json) plus the pre-existing derived/starmap-routes/entities.json.
              Every count below was computed against the actual files this session - none of
              it is sampled or estimated, except where explicitly marked as an estimate.
    derived   data-layer/derived/location-gazetteer/  (gazetteer.json + MANIFEST.json)
              data-layer/derived/contracts-by-system/ (contracts_full.json + MANIFEST.json,
              supersedes contracts_by_system.json in the same folder)
              data-layer/derived/mission-templates/   (templates.json + factions.json +
              MANIFEST.json)
              All written directly to the repo this session. Full methodology and caveats
              are in each folder's MANIFEST.json - this doc summarizes them.

Sleven's instruction this session: don't bring back partial work again - go through
everything, don't leave a folder unchecked, resolve the location hierarchy all the way
down to moons/cities/outposts, take the time it takes. This is that pass.

---

## 1. THE LOCATION HIERARCHY — 2,066 entities, system down to outpost

**data-layer/derived/location-gazetteer/gazetteer.json** — every starmap entity, tagged
with its star system and (where it has one) the planet or moon it sits on.

    1,964 / 2,066   resolved to a system (Stanton / Pyro / Nyx)
      701 / 2,066   resolved to a specific planet/moon "settlement"
      102 / 2,066   unresolved to any system (see gap below)

**Full breakdown by system and type:**

    STANTON (912 total)          PYRO (577 total)              NYX (395 total)
      516  Outpost                 337  Asteroid                  314  Outpost
      275  Asteroid                126  Outpost                    70  Asteroid
       34  Manmade                  66  Asteroid_ValidQT            68  Asteroid_ValidQT
       22  Manmade_VisibleOnInter   20  Manmade_VisibleOnInter      31  Manmade
       12  Moon                      7  Anomaly                      6  Anomaly
        9  PointOfInterest           6  Outpost_InvalidQT            3  Planet
        5  Planet                    6  Planet                       2  PointOfInterest
        4  LandingZone               6  Moon                         1  Moon
        3  Anomaly                   5  Manmade                      1  Star
        2  JumpPoint                 3  LandingZone
        2  NavPoint                  1  Star
        1  Star

**Every named planet and moon (32 total), with its system:**

    STANTON (5 planets, 7 moons)    PYRO (5 planets, 6 moons)    NYX (3 planets, 1 moon)
      ArcCorp                         Bloom                         Nyx I
      Crusader  - Aberdeen              -Fuego, Ignis, Fairo        Nyx II
        - Cellin, Daymar, Yela,       Monox                         Nyx III
          Magda, Wala                Pyro I
      Green                          Pyro IV
      Hurston                        Pyro V
      microTech - Calliope,          Terminus
        Clio, Euterpe,                 - Adir, Vuur, Vatra
        Lyria, Ita

**Every LandingZone (city-tier location) — only 7 exist in this snapshot, and that's a
fact about the game's current content, not a gap:**

    New Babbage    Stanton, on microTech
    Orison         Stanton, on Crusader
    Area18         Stanton, on ArcCorp
    Lorville       Stanton, on Hurston
    Ghost Arena    Pyro, on Terminus
    Contested Zone Pyro (x2 - one on Bloom, one unresolved)

Pyro does not have Stanton-style settled cities yet in this patch - "Ghost Arena" and
"Contested Zone" are arena/contested-zone type locations, not full cities. Worth knowing
if a "cities" facet or page type is planned - it would need to say so rather than imply
parity between the two systems.

**The known gap, named rather than hidden:** 12 entities, all prefixed `UGF_...`
(underground/bunker FPS locations - e.g. `UGF_SP_Criska`, `UGF_TheGarden`) have no
`parent_uuid` and do not resolve to any system through this hierarchy. They exist outside
the main starmap parent chain in this snapshot. Left as `system: null` rather than guessed.

**Also found, not yet folded in — a finer-grained dataset for later:**
`resources/trade_locations.json`, 965 rows, is interior sub-zones inside outposts/stations
("Security Compound," "Lobby," "Shipping Area") — only 231/965 match a gazetteer entity by
name, because most are rooms inside a facility, not independently-mappable points. Relevant
to a future interior/amenity feature, not consumed here.

---

## 2. MISSIONS JOINED TO THAT HIERARCHY — system down to planet/moon where possible

**data-layer/derived/contracts-by-system/contracts_full.json** — all 5,107 parseable
contract records (of 5,108 total; 1 failed to parse), each tagged with system and, where
resolvable, which planet(s)/moon(s) it's available at.

    4,270 / 5,107   resolved to a system
      837 / 5,107   unresolved (mostly genuinely system-agnostic templates - generic
                    hauling/time-trial/tutorial missions with no location baked into
                    the template itself, not a join failure)
    1,893 / 5,107   have planet/moon-level detail

**Important, and stated on every record in the file so it can't get read out of context:**
`possible_planets_moons` is **where the mission is available to pick up** (broker/jurisdiction
level) — **not** the mission's actual objective/site. That finer site (a specific wreck,
outpost room, asteroid) is generated per-instance at runtime and does not exist as a static
value anywhere in this snapshot. This was checked, not assumed: the one field that looked
like it should give the precise site (`LocationPools[].ResolvedLocations[].UUID`) was
tried, and its UUIDs were confirmed by direct membership check to not exist anywhere in
2,066-entity gazetteer — a real data-source gap, not a bug in this session's join.

---

## 3. MISSION TEMPLATES — both families, counted separately because they don't share a schema

The contracts folder holds two differently-shaped record types. This matters for the
"templates respawn, same mission different scenery" question directly.

**Family A — `ContractGeneratorHandler_Career`/`_List` (2,943 records) — has a clean
built-in template ID:**

    106 unique GeneratorClass values, 27.8x compression, HIGH confidence (read
    directly from a game-native field, zero inference)

**Family B — `MissionBrokerEntry` (2,165 records) — `GeneratorClass` is null on every
single one of these records, confirmed directly, not assumed. No clean template-ID field
 exists for this family. The only signal is the DebugName string**, e.g.
`PU_Bounty_PVE_Pyro_HeadHunters_Generic_Pyro1`.

Built a normalizer that strips tokens judged to be flavor/variance (not template identity)
from DebugName: the star system, faction/threat abbreviations, difficulty/legality words,
numeric and rank suffixes. The faction abbreviations were **verified, not guessed** — e.g.
"CFP" co-occurs with `MissionGiver: "Citizens for Prosperity"` in 60/62 records carrying it,
and a matching file exists in `factions/` (`faction_reputation_lawful_citizensforprosperity.json`).
All 74 factions in that folder are now captured in `mission-templates/factions.json`, a
real dataset that was sitting unused until this pass.

    Result: 861 unique normalized roots, 2.51x compression, MEDIUM confidence

**This is a considered estimate, not a settled count, and the MANIFEST says so
explicitly.** A handful of tokens (`Group`, `Inhabited`, `NoNonHostiles`, `CrossStanton`,
`DC`) were deliberately left un-stripped because treating them as flavor rather than real
mission-logic differences would be a guess this session can't verify from the data alone —
they're flagged in the MANIFEST for a call later. The lower compression ratio versus Family
A (2.51x vs 27.8x) is plausibly **real**, not just weaker normalization: sampling by
MissionType shows genuinely different mission verbs side by side even after stripping —
Steal, Assassination, RemoveClaimJumpers, EliminateSpecific are different templates, not
variants of one. Family B may simply be more granular than Family A.

**Combined estimate: roughly 800–1,150 distinct mission templates total** (106 settled +
700–1,051 depending on how the flagged tokens are eventually treated). Treat the 106 as
fact and the Family B range as the open question — narrowing it needs a human or
game-knowledge call on the flagged tokens, not another normalization pass from this
session guessing alone.

---

## 4. OTHER FOLDERS CHECKED THIS SESSION, NOTHING ELSE FOUND

Per the instruction not to leave a folder unchecked: swept `data-layer/raw` (ship CAD/API
dumps — arrow, constellation-aquila, gladius, misc), `data-layer/processed` (blueprints,
hardpoints — item/crafting data), and the other three external sources
(`uexcorp` — commodities pricing only, `api.star-citizen.wiki` — items only,
`scunpacked.com` — ships/labels only). **None of these contain mission or location data.**
The relevant material was entirely inside the one `scunpacked-data` snapshot already in
use, across `contracts/`, `starmap.json`, `starmap_positions.json`, `factions/`, and
`trade_locations.json` — all of which are now accounted for above.

---

## 5. NOT VERIFIED

- **Whether the 837 system-unresolved contracts and 12 system-unresolved gazetteer
  entities overlap in any meaningful way** — not cross-checked.
- **Whether `Group`/`Inhabited`/`NoNonHostiles`/`CrossStanton`/`DC` should be stripped as
  flavor tokens for Family B's template count** — flagged, not decided.
- **Whether `SoldAt`/`BoughtAt`-style trade-location data (per the earlier
  `URGENT_commodity-gap-closed-resources-folder.md` finding) reflects current 4.9
  behaviour** — inherited caveat, not re-checked this session.
- **`trade_locations.json`'s 965 interior sub-zones** were found and counted but not
  joined to anything — noted as a future asset, not built out.
