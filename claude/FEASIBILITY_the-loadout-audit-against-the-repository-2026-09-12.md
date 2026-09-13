# FEASIBILITY — Echo's loadout audit, read against the repository

**Read-only review, 2026-09-12, by the Adjutant desk, against the deployed test-site build
of 2026-09-11 (`testing/_deploy/loadout.html`, `loadout_data.gen.js`, `loadout_eng.gen.js`,
`next.html`) and `build_loadout_data.py`. Nothing was modified. Source document: Echo's
"Ship Loadout Competitive Audit", 2026-09-12.**

**Labels used below: CONFIRMED (read out of the files today), ASSUMPTION (my reading, not
proven), RECOMMENDATION (a judgement).**

---

## 0. THE HEADLINE, AND IT CORRECTS ONE OF MY OWN DOCUMENTS

**CONFIRMED — the ship dimensions exist, and I told you this morning they did not.**
`LOADOUT_SHIPS` holds `dim` for **all 318 ships**, as three numbers. The Cutlass Black reads
`[37.5, 26.5, 11.5]`. My inventory document counted the FRONT PAGE's data, where `d`, `w`
and `h` are null on all 253 rows, and concluded the project has no width or height. **That
conclusion was wrong. The front page does not carry them; the loadout dataset does.**
The inventory has been corrected.

**CONFIRMED — paint data exists too.** `LOADOUT_PAINTS` holds **924 paints** with a display
name, a manufacturer and ship tags; `LOADOUT_PAINTSETS` holds **105 sets**; **260 of 318
ships carry a `pset` pointer.** Echo's paint research and my memo both said we hold no paint
data. **We hold the names and the ship mapping. What we do not hold is any texture or
material.** The "name and link" layer she recommends is therefore already data-complete.

---

## 1. WHICH RECOMMENDED FEATURES ALREADY HAVE WORKING LOGIC OR DATA

**CONFIRMED, already built and running:**

- **Stock versus current comparison.** The page computes two builds (A and B) and renders
  every stat through one `stat()` function that takes both, with a delta and a "moved"
  marker on stats that changed. Echo's "never overwrite the baseline" is already the model.
- **A preview state.** `ghost` holds a part being considered, separate from the applied
  build — her "preview before apply" already exists in the calculation layer.
- **Provenance per value, in two states.** A badge marks each stat "CIG" (CIG's own
  precomputed figure for the stock loadout) or "summed" (added up by the page from the
  fitted parts), with hover text explaining the difference. That is the beginning of her
  "source beside the value".
- **Plain-language meaning per stat.** An `EXPLAIN` table carries a written sentence for
  every stat, in our own voice, including the pilot-versus-crew distinction: "Turret guns a
  gunner fires are not counted here — they have their own figure, because one number cannot
  mean both what you can do alone and what a crew can do." **Her single loudest complaint
  about the competition is already answered in our copy.**
- **Pilot DPS, turret DPS and missile payload are already separate**, and missile payload is
  already labelled a one-shot figure that is never added to a per-second number.
- **The 3D model with hardpoint markers**, 217 models and 195 marker sets.
- **The parts catalogue**: 3,292 parts, 3,292 hardpoint records, 200 fits, 318 ships,
  180 armour records, engineering data.
- **Ship dimensions and paint names**, as above.

## 2. WHICH EXISTING SYSTEMS SHOULD BE PRESERVED

**RECOMMENDATION — preserve these; they are the differentiator she is asking us to build:**

1. **The `EXPLAIN` sentences.** Nobody else writes them. They are the "Meaning" column.
2. **The CIG-versus-summed badge.** It is the honest core of her provenance requirement.
3. **The A/B calculation with deltas.** Rebuild the presentation, not the arithmetic.
4. **The hardpoint marker pipeline.** Blender-placed markers with Three.js raycasting is a
   standing architecture decision and it is what makes Direction A possible at all.
5. **The stock-versus-modified distinction in `pick()`** — but fix it; see section 7.

## 3. WHAT NEEDS NEW WORK

**Front end, new:** the sticky consequence strip; the goal/recipe chooser; the three DPS
layers (Quick, Crew, Advanced); the build story; undo and scoped reset; focus mode; the
synchronised equipment list as a first-class equal of the 3D scene rather than a tab.

**Back end or data pipeline, new:** per-item price freshness states (verified, aging, stale,
unavailable, unknown) — **CONFIRMED we do not hold a verified-at timestamp per price today**;
an adjustable sustained-fire window; range-aware DPS; capacitor, heat and reload modelling
deep enough to answer "why did sustained DPS fall"; TTK simulation inputs.

**New data sources:** paint textures or official paint images (we have names only); target
profiles for TTK; a current-patch record, which two earlier rulings already need.

## 4. WHAT CANNOT BE SUPPORTED RELIABLY TODAY

- **TTK.** We hold no target model, no armour-versus-damage-type resolution proven against
  the game, and no server behaviour. **ASSUMPTION: building it now would produce a number
  that looks authoritative and is not.** Her own guardrails say the same.
- **Authentic paint on the model.** Names yes, textures no.
- **Shop price freshness.** We do not store when a price was last checked, so "verified
  recently" cannot be computed. This is the same gap as the per-row confidence note.
- **Mobile.** Run 4 measured the ship page already scrolling sideways at 390 px with 27 px
  controls. A workbench is heavier, not lighter.

## 5. DOES THE GUIDED VISUAL WORKBENCH FIT THE ARCHITECTURE

**RECOMMENDATION: yes, and it is closer than it looks — the page is already a two-build
calculator with a model, markers, deltas and explanations. The work is presentation and
sequencing, not a new engine.**

**Three constraints that decide whether it survives contact:**

1. **The model is not universal.** 217 of 253 ships have one, 195 have markers, 22 models
   carry no markers at all and two ships have a page with no model. **A 3D-led page must
   open correctly for the ship that has neither** — the list is the product, the model is
   the navigation.
2. **Internal components have no markers by design.** The standing decision is markers only
   for physically visible mountables; power plants, coolers and shields use a menu overlay.
   **So the workbench is already two interfaces, and her design must say which one the
   consequence strip serves.**
3. **Weight.** `loadout.html` is 1.31 MB before the 3.9 MB data file and the model.

## 6. CONSTRAINTS TO KNOW BEFORE A WIREFRAME IS FINALISED

- Markers exist only for external mountables; internals need the overlay.
- 36 ships have no model; the layout cannot assume one.
- Stats come from two sources — CIG's precomputed stock figures and our own sum — and they
  do not agree in scope. **The wireframe must show which is which, because the page already
  does.**
- We hold dimensions (318 ships), paint names (924) and no paint textures.
- No price age, so any "freshness" chip is unbacked until the pipeline stores one.
- Phone width is already broken on this page.

## 7. THE QUANTUM RANGE CORRUPTION — REPRODUCIBLE, AND IT IS NOT THE MISSILE RACK

**CONFIRMED, root cause found in the data and the code.**

**The data:** every one of the **59 quantum drives** in `LOADOUT_PARTS` carries
`qt: 340282300000000014807478566912`. That is the single-precision float maximum
(3.4028235e38) with the metres-to-gigametres divide already applied — **a game-file "no
limit" sentinel, imported as if it were a measurement.**

**The code:** `calc()` computes `r.qt = Math.max(r.qt, p.qt)` over the fitted parts, so our
own figure for any ship is always the sentinel. `renderStats()` then calls
`pick("qt", ra.qt, rb.qt)`, which returns **CIG's precomputed `cig.qt` only while the build
is stock** — 259 of 318 ships carry one, the Cutlass Black's is 61.22 Gm.

**So the trigger is not the missile rack. It is leaving stock at all.** Change any component
on any ship, and the page stops using CIG's figure and starts printing the sentinel,
formatted to one decimal place as 3.402823e+29 Gm.

**Reproduction:** open any ship with `cig.qt`, change one component of any kind, read the
Quantum range card. **The same mechanism applies to every stat routed through `pick()`** —
sustained DPS and effective HP are the other two — **but only quantum range has a poisoned
part value, so only it goes visibly absurd. The others quietly change scope from CIG's
number to ours, which is a smaller version of the same defect.**

**RECOMMENDATION, not applied:** the sentinel should be dropped at import in
`build_loadout_data.py` rather than patched at display, and a quantum drive with no real
range should read "not published" rather than a number. **Whoever fixes it should also
decide what the card shows on a modified build, because CIG's figure stops being true the
moment the fit changes.**

## 8. WHICH CALCULATIONS NEED VALIDATION BEFORE THEY ARE SHOWN

In the order I would validate them:

1. **Quantum range** — broken today, above.
2. **Sustained DPS** — the page's own summed figure versus CIG's precomputed one. Two
   numbers for one name, switching silently on whether the build is stock.
3. **Effective HP** — same switch, plus hull-plus-shields is a simplification the
   explanation already admits.
4. **Alpha damage** — one volley, everything firing once: needs the same scope statement as
   DPS or it mixes pilot and turret.
5. **IR and EM signature** — presented as absolute stealth numbers; unverified against the
   game.
6. **Anything derived from `pen` (penetration) and armour** — the data exists, the model
   behind it does not.

**None of these should carry a decimal place we cannot defend, which is Echo's point about
precision implying certainty.**

---

## WHAT I DID NOT DO

No code was modified, no page redesigned, nothing built. No render was tested. The
engineering data file and the front-page build script were read only far enough to answer
the questions above.
