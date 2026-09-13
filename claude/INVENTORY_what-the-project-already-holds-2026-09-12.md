# INVENTORY - what the project already holds

**Build (Code), 2026-09-12, about 03:35 CDT.** Architecture ordered it in `2026-09-12_memo_build_your-three-answers-the-clearing-is-released-and-one-new-job.md`, section 4.

**This is assembly, not research.**

- Every figure comes from a file on disk, and each line names that file and the population it was counted on.
- **Figures I had not counted myself tonight were re-counted from their files at 03:30-03:34.** Nothing is estimated.
- **Its purpose:** a desk about to research or acquire something checks here first. Five features in this project have been designed twice because nobody knew what was already held.

**The traps are marked TRAP.** Each one is a place where two honest numbers look like one thing and are not.

---

## SHIPS AND IDENTITY - three populations, not one

    254   site rows      testing/index.html SHIPS literal -> data-layer/derived/
                         main-page-concepts/frontpage_data.json   (2026-09-11 13:13)
    253   front cards    testing/_src/next.src.html const DATA    (2026-09-11 23:34)
    318   ClassNames     LOADOUT_SHIPS in testing/_src/loadout_data.gen.js
                         (2026-09-12 02:55), from the game-data snapshot

**254 rows become 253 cards** because `Valkyrie Liberator` is folded onto the Valkyrie card as an edition (`editions.json`).

**318 is a different population.** It is every vehicle in the game-data snapshot, including vehicles the site does not list.

`data-layer/ship_resolution.json` (2026-08-02) gives the counts:

- 254 site rows
- 221 matched to a game file
- 33 with no game file
- 89 game-only
- 6 tier variants

**TRAP - 221 matched, but only 219 cards carry a ClassName.** The two that fall out are **Javelin and MOTH.**

- `build_frontpage_data.py:36-40` joins against the hull keys embedded in an **older concept page**, `data-layer/derived/main-page-concepts/five-main-pages.html`. It does not join against LOADOUT_SHIPS.
- Those two are absent from that older set, so the join refuses them. They appear as `refused_join` in `frontpage_data.json`.
- **So both have working ship pages and no ClassName on their cards.**

**The 34 cards with no ClassName are the same 34 with no career.** Q63.8A list 3 proved that as a set.

## DIMENSIONS - four sources, kept apart

    game data     LOADOUT_SHIPS dim: 315 of 318 ClassNames  (loadout_data.gen.js,
                  2026-09-12 02:55). Read from Length/Width/Height in the snapshot.
    Fleetyards    sc-ships/index.json length/beam/height: reaches 219 cards by
                  exact name  (2026-07-26)
    page length   the card's L IS game-data Length (build_frontpage_data.py:88),
                  on 219 cards. Same source, not a second one
    model box     calculated from the .glb files: 217 cards, world space

**TRAP - "dim for all 318" is no longer true. It is 315.** Tonight's fix made a zero absent at import. AEGS_Javelin, ARGO_MOTH and PowerSuit were 0 x 0 x 0, and so is RSI's own ship matrix for the first two. That fix is live (Cloudflare version 0e7fff39).

**Agreement:**

- 191 cards carry both a game length and a Fleetyards length. 50 are equal, 91 differ by more than 1 m, and 58 by more than 10%. Per card in `claude/AUDIT-2026-09-12-dimension-coverage.csv`. **None was picked.**
- 277 of 318 ClassNames share an exact triple with another ClassName. This is INFERRED to be a size class, not a measured hull.

**The front page carries length only.** Its `d`/`w`/`h` fields are an outline drawing and its size. They were never dimensions.

**Phase two found figures for five more cards** (`claude/AUDIT_dimensions-phase-two-five-ships-2026-09-12.md`):

- Odin and Genesis from RSI
- MOTH from Fleetyards only
- CSV-FM and Starlancer BLD from a wiki only

## COMPONENTS

**The game-data snapshot:** `data-layer/external-sources/scunpacked-data/snapshots/20260827T225641Z/`.

- Its manifest is `data-layer/external-source-manifests/20260827T225641Z/01_scunpacked-data_manifest.json`.
- It records the upstream `StarCitizenWiki/scunpacked-data` at commit f6a2b29e, dated 2026-08-27 11:38 +02:00.
- **The manifest fields I read do not state a game build number.**

**LOADOUT_PARTS holds 3,292 parts across 35 types** (LOADOUT_TYPES). Per-type counts are in the file.

## QUANTUM DRIVES

**59 quantum drives** (type `qtm` in LOADOUT_PARTS). Alongside them: 144 quantum fuel tanks, 6 jump modules and 4 interdiction generators.

**TRAP - every one of the 59 carries the same range value:** `qt` = 340282300000000014807478566912. That is the snapshot's sentinel, which the page renders as "3.402823e+29 Gm". **The project holds no real quantum range for any drive.** The quantum-range review ruled this as corruption leaving stock.

## DAMAGE FIGURES - WHICH COLUMN, AND ONE OPEN UNKNOWN (added 2026-09-12, after the sdps question)

**Settled from our own data.** Part `dps` is the snapshot's `Weapon.Damage.Sustained`, and so is the ship's `cig.sdps` (`PilotSustainedDps`). Ship `cig.dps` is the burst column (`PilotDps`). **Part `dmg` is BURST DPS split by damage channel,** and the armour matchup on the ship page uses it. That is reported to Architecture as a unit bug.

**OPEN UNKNOWN - 9 of 190 weapon parts carry no `dps` value.** They are recorded here, on Architecture's instruction, and not guessed at:

    BEHR_JavelinBallisticCannon_S7_Dummy / _S7_LowPoly, BEHR_LaserCannon_S7_Idris_M_Dummy
                                                   M9A Cannon  (placeholder copies)
    HRST_LaserBeam_Bespoke, Vanduul_LaserBeam_S12_TSG   Exodus-10 Laser Beam
    HRST_LaserBeam_Tiburon                         Supremacy-10T Laser Beam
    VNCL_Gen2_LaserBeam_S9                         Vanduul Mauler 'IGNITER' Beam
    VNCL_Gen2_TachyonBeam_S10                      Vanduul Mauler 'ANNIHILATOR' Cannon
    RSI_Constellation_Taurus_Tractor_Beam          SureGrip TH2 Tractor Beam

**OBSERVED, NOT PROVEN:** every one is a continuous beam, a tractor beam, or a Dummy/LowPoly placeholder, and none carries a `Damage.Sustained` figure in the snapshot. **Why the snapshot has none is not established.**

## HARDPOINTS

**6,252 markers on 267 ClassNames** (`testing/_src/loadout_marker.gen.js`, recounted 03:32), by provenance:

    from CIG data                   1,852
    inherited from a sibling hull   4,176
    estimated from part names         224

**These are the project's placements, not the model files' own.** Only two model files name hardpoint nodes themselves: 85X (199) and Fury (182).

## MODELS

**256 `.glb` files** in `testing/_deploy/models/`, 504.2 MiB. All glTF 2.0 with Draco.

- **217 cards reach a model.**
- **42 files are referenced by no ClassName.** 28 of them are exact-name candidates for hull-less cards.
- **Paint:** zero textures anywhere, and 239 files have a single material. **No model can take a paint as a texture swap today.**

Full detail is in `claude/AUDIT_images-models-dimensions-phase-one-2026-09-12.md` and its CSVs.

## PICTURES

**247 cards have a picture and 6 do not.** All 247 files exist and are WebP.

**The 6 are:** CSV-FM, F7C-M Hornet Heartseeker Mk II, Genesis Starliner, MOTH, RAPTOR and Starlancer BLD.

**The RAPTOR is a kept joke card.** Its picture is Sleven's one save.

## PAINTS

- **924 paints,** with names, manufacturers and ship tags (LOADOUT_PAINTS).
- **105 paint sets** (LOADOUT_PAINTSETS).
- Both are in `loadout_data.gen.js`.

**TRAP - these are names and tags, with no textures.** The earlier claim that "we hold no paint data" was wrong (the Adjutant inventory's correction), and so is "we can show paints". **We hold the list, not the look.**

## ROLES

**253 official roles from RSI's own store:** `claude/CIC_rsi-official-ship-roles-2026-09-12.md`, read 2026-09-12. Verbatim and unnormalised.

**TRAP - its 253 is RSI's store population, not our 253 cards.**

- Joined on exact name, 225 cards match. 28 of ours have no roles row, and 28 of RSI's rows have no card.
- The mapping for the 28 is ordered to Research.
- Q63.8A (`claude/Q63-8A_career-against-the-official-role-2026-09-12.md`): on the 225, `career` equals RSI's first segment on 192 of 195. **Architecture has ruled that RSI's role replaces career.** The build is in progress.

**RSI's ship matrix** (`robertsspaceindustries.com/ship-matrix/index`) is RSI's own JSON: 253 records with length, beam, height and status. It was read tonight and **is not stored in the repository.**

## PRICES

    in-game price      179 purchasable cards carry one (frontpage_data.json)
    per-dealer price    63 of those 179  (data-layer/derived/ship-prices/
                        ship_dealer_prices.json, C1 2026-08-31, from Fleetyards,
                        marked UNPROVEN in game; 47 of the 63 vary by shop)
    pledge price       237 of 253 cards

**TRAP - the other 116 purchasable cards show one price beside a list of shops.** That reads as "this price at these shops", and the data does not say that. This is run 3's T-011 and run 4's M-005.

---

## WHAT THIS DOCUMENT DID NOT DO

- **Take a new measurement.** Every figure was already on disk. It was only re-counted, where named, to confirm the file still says it.
- **Reconcile any two sources.** The traps above are the places where that would be a decision.
- **Read the claude.ai project store.** Documents that exist only there are invisible to this inventory, and to every desk with file access. See `claude/ACCESS-MAP_design-desk-files-for-echo-2026-09-12.md`.

*Build (Code), 2026-09-12.*
