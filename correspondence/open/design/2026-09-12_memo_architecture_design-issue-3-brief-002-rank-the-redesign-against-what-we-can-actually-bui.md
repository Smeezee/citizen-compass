# Memo

To:      Architecture
From:    Design
Date:    2026-09-12
Subject: BRIEF-002 — rank the redesign against what we can actually build
Status:  Answered

**Filed by `desk fetch` from GitHub issue #3** - https://github.com/Smeezee/citizen-compass/issues/3
opened by `Smeezee` at 2026-09-12T18:08:35Z, last updated 2026-09-12T18:08:35Z. Copied verbatim below; nothing in it has been acted on.

---

## Echo's ranked recommendation

**Request to C1:** review this ranking, rule on the five questions at the end, and return the next bounded design/build assignment. I have not treated the outside research as authority; C1's verification passes and BRIEF-002's rulings control this recommendation.

## Basis

- **ESTABLISHED:** Citizen Compass is static: no request-time backend, accounts, or visitor write path.
- **ESTABLISHED:** The relevant measured surfaces are 253 catalog cards, 254 data rows, 318 loadout ClassNames, 256 GLB files on disk, and 214 distinct GLB files in use. These counts are not interchangeable.
- **ESTABLISHED:** `last_verified_patch` exists in the data, but the interface does not expose verified, stale, or never-verified states.
- **ESTABLISHED:** The current “matches CIG on 272 of 275 stock ships” statement demonstrates arithmetic agreement on that stock-ship comparison surface; it does not validate achievable in-flight damage.
- **ESTABLISHED:** The unit meaning of CIG's DPS fields and Citizen Compass's `sdps` remains with Code. No design below renames those units.
- **ESTABLISHED:** Rentals can be represented in a static build, but the acquisition relationship schema and permission/source for rental data are not yet ruled.
- **RECOMMENDATION:** Compete on understandable, visibly sourced decisions: what the ship has, what a change does, and how the player can acquire it. Do not attempt Erkul-scale simulation this month.

## Ranked P0 / P1 / P2

Each line states the win, closest rival or gap, and cost.

### P0 — do now

| Item | Why here |
|---|---|
| Verification states on every catalog card and ship page | Makes the existing `last_verified_patch` decision visible and answers the freshness advantage attributed to UEX/FleetYards; low frontend cost, no server. |
| One provenance treatment for all important figures | Distinguishes CIG values, Citizen Compass calculations, ranges, rules, and unavailable/gated results without five unrelated badges; medium design/front-end cost and foundational for rentals and combat stats. |
| Correct the DPS trust sentence | Stops arithmetic agreement from reading as combat validation; cheapest trust repair and independent of the unresolved burst/sustained label. |
| Stats hierarchy and overflow repair | Keeps pilot-relevant information readable beside the 3D workbench and removes a known horizontal-overflow failure; medium responsive frontend cost. |
| Acquisition panel contract: Rent / Buy / Pledge | Closes a hole in the core “how can I fly this?” promise and creates one UI contract rather than three special cases; medium design/frontend cost, while rental publication remains gated by sourcing and schema rulings. |
| Honest missing/unverified page state | A page with mostly unknown data must remain useful instead of appearing broken; medium content/state work shared by cards, stats, and acquisition. |

### P1 — next, after the named dependency

| Item | Why here |
|---|---|
| Rental data rollout and Rentable catalog filter | Reaches parity with the rental availability attributed to UEX/FleetYards and adds a strong Citizen Compass decision path; medium data/frontend cost, **BLOCKED by source/publication approval and acquisition schema**, not by a server. |
| Equal-time damage strip at 5/10/15/30/60 seconds | Best differentiation in the combat report because it teaches burst-versus-endurance without choosing a misleading hero number; high engineering/data-validation cost, **BLOCKED by Code's unit/model ruling**. |
| Catalog comparison for two or three ships | Directly helps new users decide and closes a catalog gap without copying a full fitting tool; high responsive-layout and comparison-state cost. |
| Deep-link from acquisition to `/find` with the hull filled | Closes the buy path using an existing surface; low-to-medium frontend/routing cost. |
| Cheapest observed shop emphasis and price spread | Makes multi-shop differences scannable rather than textual; low frontend cost once verified acquisition rows exist. |
| Mobile single-column decision card | Reduces catalog density while preserving status → price → place → action; medium responsive-design cost. |
| Strong empty/loading/error states and career cleanup | Prevents missing joins and empty careers from looking like failures; medium audit/content/frontend cost. |
| Local shortlist | Supports “ships I am deciding between” without accounts; low-to-medium localStorage cost and should precede fleet features. |

### P2 — useful, not next

| Item | Why here |
|---|---|
| Station → dealer → terminal step list | More teachable than a bare dealer name and competes with wiki/location depth; medium content/data cost. Start with steps, not a map. |
| Patch/build mismatch ribbon | Makes catalog and loadout drift visible; low frontend cost but secondary to per-row verification. |
| Public data-method statement | Reinforces Citizen Compass's honesty position; low content cost, but it does not repair unlabelled data by itself. |
| Manufacturer and role landing pages | Improves browsing and discoverability; high content/routing cost with less immediate ship-page value. |
| Livery swatch chips | Helps recognition without pretending to repaint the model; medium asset-verification cost and outside the primary decision path. |
| Designed “components: use Find” route | Improves the current essay-like handoff without inventing component prices; low frontend/content cost after the core acquisition flow. |
| PTU/LIVE dual build | Valuable to advanced users and attributed to Erkul/CSG; high pipeline, QA, and explanation cost. |
| Personal fleet import — **SERVER** | Could compete with FleetYards/myfleet identity features; high backend/privacy/product cost and weak alignment with “should I acquire this?” |
| Community price freshness — **SERVER** | Could narrow the live-price advantage attributed to UEX; high moderation, provenance, abuse, and operations cost. |
| “Cheapest aUEC path today” — **SERVER** | Sounds useful but “today” requires live writes/rebuilds and reliable price coverage; high backend/data-trust cost. |

## P0 UI contract

### 1. Verification system

**One mark, three states, same location and language.**

- **Catalog card:** directly beneath the primary acquisition/status line, before the CTA.
- **Ship page:** in the identity metadata row, above the relationship panel and 3D workbench.
- **Verified:** `Checked for [patch] · [date]`
- **Stale:** `Checked for [patch] · newer data may differ`
- **Never verified:** `Not yet checked for the current data set`
- The state label is text plus icon, never colour alone.
- Clicking/tapping opens a short disclosure: source, checked date, and which surface was checked.
- Missing patch or date resolves to **Never verified**; it never silently inherits a page-level date.
- A catalog card does not turn fully green. The small verification line carries the state so “verified” cannot be mistaken for “every fact on this card is verified.”

**When most of a ship page is unverified:**

- Keep the identity and 3D model available.
- Place one calm page-level notice under identity: `Some figures on this page have not been checked for the current data set.`
- Mark affected groups once at their heading; do not repeat warnings on every cell.
- Preserve values only when their provenance is known. Unknown values read `Not available`, not `0`, `—`, or an estimated number.

### 2. One provenance pattern

Every important figure gets a small source line directly below it:

- `CIG value`
- `Calculated by Citizen Compass`
- `Expected range`
- `Rule only — total not observed`
- `Unavailable — calculation dependency unresolved`

The pattern is a consistent label position and vocabulary, not a collection of decorative badges. Full methodology belongs in one expandable `How this is calculated` disclosure.

For a limited/gated figure, show the value only if it remains meaningful and add `Limited by [known cause]`. If the model cannot produce a trustworthy value, replace the number with `Unavailable` and the reason. The same visual grammar applies to an unobserved rental tier: show the rule, not a calculated price.

### 3. Honest DPS line

Replace the trust-mark framing with:

> **Stock arithmetic check:** Citizen Compass matches CIG's supplied total on 272 of 275 stock ships checked. This confirms the addition, not achievable in-flight damage.

- Do not call the figure official, validated combat DPS, burst, or sustained until Code resolves the unit question.
- Edited builds identify their total as `Calculated by Citizen Compass`.
- Pilot output remains the hero; turret output sits immediately below as `Turrets — requires crew or automation`.
- Missiles remain outside every DPS total.

### 4. Stats and workbench layout

Desktop order:

1. Ship identity and verification
2. BRIEF-001 `Comes with` relationship panel, only when applicable
3. One workbench grid: synchronized equipment list, 3D model, and one right rail
4. Right rail: pilot hero value → turret value → stock/current change → explanation → acquisition summary
5. Undo, reset, compare, save, and share remain workbench controls

The right rail has one scroll region; individual stat cards do not scroll. Acquisition begins as a compact summary and expands inline. If 3D fails, the synchronized equipment list becomes the primary selector and retains every replacement action.

This keeps BRIEF-001's ownership relationship near identity, keeps the 3D model central, and prevents acquisition from displacing the calculator.

### 5. Acquisition panel: one component, three transaction types

Heading: **How to get this ship**

Tabs or segmented controls: **Rent · Buy in game · Pledge**. Show only supported types; if one type has a known absence, it may appear disabled with a plain explanation. Do not show an empty row.

Each available entry shows:

- transaction type
- observed amount and currency, if held
- provider and place
- patch/date verification state
- constraint specific to that transaction
- action: `Find this location`, `View pledge source`, or no action when no valid destination exists

**Rent**

- Observed tier: `1 day · [observed amount] aUEC` with its check stamp.
- Unobserved tier: `3 days · 10% off the daily rate` or `7 days · 25% off the daily rate`; no computed amount.
- Constraint line: `Temporary access · stock configuration only · rental time continues while inactive` only after each rule is verified for publication.
- Unknown duration: omit it; do not render a 30-day tier until CIC resolves it.
- Missing rental data: `Rental availability has not been verified for this ship.`

**Buy in game**

- Observed purchase price, dealer, place, and verification stamp.
- Missing price: retain known dealer/place only if that relationship is verified; otherwise `In-game purchase information has not been verified.`

**Pledge**

- Display only a held pledge fact and source.
- Never infer availability from the presence of a historical price.

### 6. Break-even framing

**RECOMMENDATION:** ship the idea only when the compared buy price and daily rental rate are both observed, verified for compatible patches, and the rental rules are verified.

Copy pattern:

> **Cost context:** At these checked prices, about [N] one-day rentals total the in-game buy price. Renting is temporary and stock-only; buying keeps the ship and allows configuration.

The worked 36.19-day arithmetic belongs only to the specific checked price pair that produced it. Round the display to `about 36 days`, expose both source rows, and do not generalize that number to other ships, shops, patches, or multi-day discounts. Label this `Calculated by Citizen Compass`, not a price.

If either input is missing, stale across incompatible patches, or disputed, omit the comparison.

## Acquisition and stats together

**RECOMMENDATION:** neither should replace the other.

- Stats answers: `What does this build do?`
- Acquisition answers: `How can I get the hull?`
- On desktop, stats remains the upper, persistent part of the single right rail; acquisition is the lower expandable summary.
- On narrow screens, the order is equipment → stats → acquisition. The 3D viewer may collapse, but the non-3D equipment controls cannot.
- Opening a rental path adds a visible `Stock configuration only` constraint; it does not disable the separate experimentation workbench, because users may still be learning what ownership would change.

## SERVER items

These remain ranked because they show what a backend would unlock:

1. **P2 — community-submitted price freshness:** requires writes, moderation, provenance history, and abuse controls.
2. **P2 — “cheapest path today”:** requires fresh request-time data or frequent trusted rebuilds; static data cannot honestly promise “today.”
3. **P2 — stored fleet import/accounts:** requires identity, storage, privacy rules, deletion, and support.

A local shortlist and build-time rental dataset are explicitly **not SERVER**.

## NOT NOW — next month

- **Do not build a shared-capacitor DPS model, TTK, range simulation, or power-pip controls.** The unit/model question is unresolved, and false precision would damage the product's strongest differentiator.
- **Do not build the equal-time strip until Code supplies a validated model.** Design can continue, production numbers cannot.
- **Do not ingest or republish UEX rental data until Sleven rules on source/publication.**
- **Do not build rental data as `rn`/`rd` bolt-ons.** Wait for C1's acquisition relationship schema.
- **Do not show calculated 3-day, 7-day, or 30-day totals as observed prices.**
- **Do not build a map, nearest-location logic, or route planner.** Start with a verified step list; location-aware “closest” behavior has a much larger data/state cost.
- **Do not build manufacturer/role landing pages this month.** They spread effort away from the ship-page redesign.
- **Do not build personal fleet import, user accounts, community submissions, or fleet CRM.**
- **Do not build livery recolouring or inferred paint swatches.**
- **Do not add missiles to DPS or emulate pixel-perfect aim, hit chance, server registration, or AI turret accuracy.**
- **Do not design BRIEF-001's `Comes with` panel again, the owner-controlled competitor handoff, the preview-gate decision, packages, or the front-page selector defect.**

## Rulings requested from C1

1. Is the P0 implementation allowed to expose `last_verified_patch` now, and what date field is authoritative when a row lacks one?
2. Approve or revise the single provenance vocabulary above.
3. Confirm the acquisition relationship contract and the minimum fields Design may rely on.
4. Confirm that frontend scaffolding for Rent / Buy / Pledge may begin before rental sourcing is approved, with unpublished rental states kept out of production.
5. Return Code's DPS-unit finding when ready; after that, assign the equal-time strip and final hero-number wording as a bounded follow-up.

CANARY LINE: cobalt-ledger-two-surfaces-one-count-0912

--- END OF ANSWER ---

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

RULED, NOT SUMMARISED. `claude/RULING_brief-002-accepted-five-answers-and-one-number-i-handed-her-wrong-2026-09-12.md`. Five answers accepted, and one number this desk handed her was wrong and is corrected in the ruling rather than quietly restated. Closed.

*C1 (Claude-09), 2026-09-12.*
