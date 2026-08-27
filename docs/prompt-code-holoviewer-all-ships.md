# PROMPT FOR CODE — the hologram viewer, for every ship on the testing site

    from    C1, 2026-08-08
    for     Code
    asks    Sleven: "push it for all the ships on the test page"
    basis   docs/FINDING_hardpoint-positions-and-holo-viewer-v2-2026-08-08.md (C3)
            docs/FINDING_hologram-display-concept-2026-08-08.md (C3)
            docs/FINDING-aggregation-rules-shields-solved-20260808.md (C3)

    WRITER NOTE — C1 is sole writer in `citizen-collector/` and is active there.
    This order covers the TESTING SITE and `data-layer/derived/` only. C1 will
    not touch either. C3 does not build site code. That leaves one writer per
    area; keep it that way.

---

## 0. What C3 proved, so you do not re-derive it

- **There are no hardpoint coordinates anywhere in this project.** 53,651
  `position` fields in `ship_specs.json`, every one null, no exceptions. The
  Fan Kit `.ctm` models cannot supply them either. **The manual-placement
  decision stands and is now backed by a count.**
- **Mount NAMES do describe position**, in every `Loadout[].Path`:
  `hardpoint_Left_Wing_Weapon`, `hardpoint_Right_Pylon_02`, `gun laser top left`.
- **The pilot-weapon rule: default TRUE.** Only an explicit `IsPilotSlaveable:
  false` locks a weapon out, and once locked it stays locked deeper in the tree.
  **Validated 275/275 exact against CIG's own `Systems.Weapons.Summary.PilotDps`.**
  C3's first version defaulted to false, produced perfectly plausible weapon
  lists, and was wrong - the Sabre read 0 pilot DPS against a true 2,182.4.
  Reproduce the 275/275 check as a test; do not take the rule on trust.
- **Shield totals are CAPPED AT TWO GENERATORS**, not N-1. Cross-checked on
  `MaxShieldRegen` with one shared outlier (Tumbril Nova, which gets full 3x).
  **Proven for uniform fits only** - no mixed-size loadout exists in the data,
  so a custom fit is out of scope for any number you display.

---

## 1. The job

Put the viewer on the testing site for **all 316 ships**, not four.

### 1a. The thing that will bite you first: geometry weight

C3's prototype carries 4 ships because that is ~13 MB. The project owns 235
`.glb` models. **Loading them eagerly is roughly 700 MB and is not a thing.**

- One ship's geometry loads when that ship is opened, and never before.
- Nothing about the ship page may wait on geometry. Stats, loadout and mount
  names are JSON and must render immediately, with the hull arriving after.
- A ship with **no** model must degrade to the full text view rather than an
  error or an empty canvas. 316 ships, 235 models - **81 ships have no hull and
  that is the normal case, not an edge case.**

### 1b. Carry the edge-count normalisation across

Do not hand-tune line opacity. C3 measured why the Aquila washed out and the
Cutlass did not:

    Cutlass  265,504 tris  168,351 edges
    Aquila   479,501 tris  384,061 edges     2.3x the line into the same screen

Additive lines sum toward white, so identical opacity looks different per hull.
Use C3's measured formula, `0.44 * (168351/edges)^0.85`, clamped. **This will
bite the day somebody adds a dense hull, and it is invisible when looking at one
ship at a time.**

### 1c. Weapons in words, for every ship, with no manual work

This is the part that ships immediately and needs nothing placed. For each
armed ship, render the mount list from `Loadout[].Path` in plain language -
"Left Wing", "Right Nose", "Turret (left)", "Left Pylon 2" - beside the item
fitted, its size and its stats.

**Most of what Sleven asked for is this, and it needs no 3D at all.**

### 1d. Internal components get the menu, not markers

Settled architecture, and C3 honoured it: power plant, coolers, shield, quantum
drive are never physically walked up to, so they render as a grouped list with
real values under a header that says so. **Do not add hull markers for them.**

---

## 2. The hardpoint placement tool

C3 built and browser-verified click-to-place **inside the hologram**, which
removes the Blender step Sleven has said he does not want to learn. Schema:

    {
      "schema": "citizen-compass.hardpoints/1",
      "ship": "Drake Cutlass Black",
      "model_space": "origin-centred unit cube, Y up; multiply pos by scale_cm_per_unit for centimetres",
      "scale_cm_per_unit": 1785.85,
      "hardpoints": [
        {"port":"hardpoint_class_2","where":"Left Wing Weapon",
         "item":"CF-337 Panther Repeater","type":"WeaponGun","size":3,
         "pos":[-0.27947,0.03606,0.81379]}
      ]
    }

Take the schema as given - it round-trips and the coordinates land inside the
hull when scaled. Output goes to `data-layer/derived/hardpoint-placements/`.

**NONE of C3's markers are data.** Every one is a test click to prove the
mechanism. Do not ship them, do not seed from them, do not let one reach a page.

**The placement tool is master-only or gated.** A visitor must not be able to
place a marker and think they have changed anything.

---

## 3. Constraints

- **Static JSON, page-per-file.** Settled. No runtime dependency.
- **The testing site is a Cloudflare Worker with static assets, NOT Pages.**
  `wrangler pages deploy` reports success and publishes to a different URL -
  this project has hit that silent-success shape five times. Use
  `scripts/deploy_testing.ps1`.
- **`build_deploy.py` substitutes its own copies of some blocks.** Patching only
  the source layer can silently do nothing. `testing/_src/` is the source of
  truth and `inject_engine.py` hard-fails rather than warning - keep it that way.
- **The password gate does not cover static assets.** `models/*.glb` are already
  fetchable directly. Sleven knows; do not treat the viewer as private.
- **Do not `git add -A`.** ~50 files show as modified from pure CRLF/LF churn.
- **Nothing commits or pushes without Sleven's explicit go-ahead.**
- Every check gets a negative control. Hard rule 12.

## 4. Acceptance

1. Open five ships including one with no `.glb`. Stats and mount names render
   immediately on all five; the hull appears after on the four that have one;
   the fifth degrades to text with no error.
2. Pilot DPS reproduces **275/275** against CIG's `PilotDps`. A deliberately
   broken rule must fail that test - a check that cannot fail is not a check.
3. Line opacity differs measurably between Cutlass and Aquila without anybody
   typing a per-ship number.
4. Total shield HP matches `ShieldsTotal.Hp` on stock loadouts, Tumbril Nova
   included as the known exception.
5. Report the page weight for the heaviest ship, and what a visitor downloads
   before the first pixel.
