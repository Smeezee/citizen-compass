# Memo

To:      Engineering
From:    Design
Date:    2026-09-12
Subject: BRIEF-003 — the provenance system and the verification mark as one piece
Status:  Open

**Filed by `desk fetch` from GitHub issue #4** - https://github.com/Smeezee/citizen-compass/issues/4
opened by `Smeezee` at 2026-09-12T22:00:25Z, last updated 2026-09-12T22:00:25Z. Copied verbatim below; nothing in it has been acted on.

---

## Echo's implementation design

**Status:** recommendation for C1 ruling. This specifies one provenance grammar that includes verification; it does not redesign the surrounding workbench.

## Core rule

Every displayed value has two separate questions:

1. **How was this value obtained?** — the provenance label.
2. **When was its source last checked?** — the verification state.

They render as one compact source line in one fixed position. Verification is not a second badge system.

## Component anatomy

For every value-bearing component:

1. **Figure name** — what the number means, including the correct measurement type.
2. **Figure value** — or an explicit absence/withheld state.
3. **Provenance line** — source/method first, verification second.
4. **Plain-language meaning** — the existing short explanation, where space permits.
5. **Disclosure trigger** — `How this is calculated` opens the shared detail format.

### One position rule at both densities

> The provenance line sits immediately below the value it qualifies, left-aligned with that value, before explanatory or action text.

This rule does not change between catalog cards and workbench stats.

- **Catalog card:** name/price → value → provenance line → action.
- **Workbench stat row:** stat name → value → provenance line → plain-language meaning.
- If a compact card cannot fit the full verification date, it may shorten the visible line to source/method + state. The accessible name and disclosure retain the complete patch/date information.
- The provenance line never shares the figure-name line. On the current Avenger Stalker page, the cramped `CIG` or `summed` token beside the heading moves beneath the value.
- The entire card or stat row does not change colour. State is communicated by text plus a small repeated icon; colour may reinforce it but never carry it alone.
- Labels wrap to a second line rather than truncate the source or verification state.
- The disclosure trigger is keyboard reachable and uses an actual button with `aria-expanded` and `aria-controls`.

## Approved provenance vocabulary

Use these exact primary labels:

- `CIG value`
- `Calculated by Citizen Compass`
- `Expected range`
- `Rule only — total not observed`
- `Unavailable — calculation dependency unresolved`

Verification joins the same line as a secondary clause:

- `Checked for [patch] · [date]`
- `Checked for [patch] · newer data may differ`
- `Never verified`

Example structure, with values supplied by data rather than copy:

> `CIG value · Checked for [patch] · [date]`

No count, percentage, date, patch, price, or total is typed into interface copy. All variable facts come from the data/generator.

## Figure-class mapping

| Figure class held by Citizen Compass | Primary provenance label | Required qualification |
|---|---|---|
| CIG ship totals used for stock values | `CIG value` | Verification reflects that exact row; never inherit a page/build date. |
| Edited-build values summed from fitted parts | `Calculated by Citizen Compass` | Disclosure names the input class and aggregation method. |
| Stock alpha or another part-derived sum | `Calculated by Citizen Compass` | Do not call it CIG merely because its inputs originated in CIG files. |
| Armour matchup output | `Calculated by Citizen Compass` | The figure name must say `burst`; the disclosure says no sustained damage-type split is supplied, so none is computed. |
| Honest lower/upper armour or effectiveness interval | `Expected range` | Both endpoints come from data; neither becomes a single “best” result. |
| Rental duration rule without a terminal-observed total | `Rule only — total not observed` | Show the rule as words. Do not calculate or display a price. |
| Rental day rate | **No universally honest approved label exists yet.** | Use `CIG value` only if the approved source contract establishes it as a direct CIG value. Otherwise withhold publication until C1 supplies the acquisition/source contract; do not relabel an aggregator report as CIG. |
| Observed rental tier total | **No universally honest approved label exists yet.** | Same dependency as the day rate. A verification stamp cannot substitute for source identity. |
| In-game purchase price | `CIG value` only when directly sourced from CIG/game data | If its source chain is unknown, use the unknown-provenance state and withhold the value. |
| RSI pledge price | `CIG value` | Availability is a separate fact; a historical price must not imply current availability. |
| Official published dimension | `CIG value` | Disclosure names the specific CIG surface. |
| Dimension measured from a GLB/model | `Calculated by Citizen Compass` | Figure name must say `model measurement`; it must not appear as an official ship dimension. |
| Dimension expressed as a defensible interval | `Expected range` | Disclosure names the endpoints and method. |
| A gated combat or engineering figure whose trustworthy calculation cannot run | `Unavailable — calculation dependency unresolved` | Replace the number; never show a fantasy value with a warning beside it. |
| Image credit | **No honest label exists inside this numeric provenance grammar.** | An image is an asset, not a figure. Keep the existing CIG ownership/source credit in the viewer disclosure; forcing it into `CIG value` would be false. |
| Unknown or unattributed value | No primary label; use the unknown-provenance state below | Suppress the value until its source is repaired. |

## Verification states

### Verified

Visible line:

> `[Provenance] · Checked for [patch] · [date]`

Use only when both patch and date exist for that exact row.

### Stale

Visible line:

> `[Provenance] · Checked for [patch] · newer data may differ`

The disclosure includes the recorded date. “Stale” requires a defined comparison against the current relevant dataset; age alone is not silently treated as patch drift.

### Never verified

Visible line:

> `[Provenance] · Never verified`

A missing patch **or** missing date produces this state. It never inherits a page date, neighbouring-row date, compile date, or dataset timestamp.

## Unknown provenance versus known absence

These are different states and must use different words and behavior.

### Unknown provenance — Citizen Compass defect

Visible value:

> `Value withheld`

Visible source line:

> `Source unknown — verification required`

Behavior:

- Suppress the untraceable number.
- Keep the row visible so the defect is not hidden.
- Disclosure says: `Citizen Compass has a value for this field but cannot currently verify where it came from. The value is withheld until its source is repaired.`
- This state is attention-bearing because it describes our data failure.
- It must be included in audit/report output if such output exists; the UI does not offer visitors a write path.

### Known absent — source/game does not provide the fact

Visible value:

> `Not provided`

Visible source line:

> `CIG does not provide this value for this ship`

Behavior:

- Do not display `0`, a dash, or an estimate.
- Disclosure identifies the checked source surface and verification state.
- This is neutral, not an error state; the row may be omitted only when the product decision says the fact is irrelevant to that ship class.
- If the source is not CIG, replace `CIG` with the named approved source. Do not use generic “not available” when the absence is known.

### Calculation dependency unresolved — known reason, different from both

Visible value:

> `Unavailable`

Visible provenance line:

> `Unavailable — calculation dependency unresolved`

Disclosure names the missing model/input. This state means the source is understood but the calculation cannot honestly run.

## Shared disclosure

Heading and trigger:

> **How this is calculated**

The same disclosure template is used for CIG values, calculated values, ranges, rules, and unavailable values. It contains:

1. **Meaning** — what the figure measures in plain language.
2. **Source or method** — exact source surface, or the calculation performed.
3. **Inputs** — named input classes; values are populated from data.
4. **Verification** — state, patch, and date for the exact row.
5. **Limits** — what the result does not prove.
6. **Why unavailable**, only when applicable.

### Disclosure copy by class

**CIG value**

> `This value is supplied by CIG for the stock ship. Citizen Compass displays it without treating it as a simulation. Source: [surface]. Verification: [state generated from this row].`

**Calculated by Citizen Compass**

> `Citizen Compass calculates this value from the currently fitted parts using [method]. Inputs: [input classes]. It is not a CIG ship total. Verification: [state of each required input group].`

If required inputs have mixed verification states, the displayed calculation inherits the least-trusted input state and the disclosure lists the groups separately. It does not inherit the newest input's state.

**Expected range**

> `Citizen Compass shows a range because the available data supports more than one defensible outcome. The endpoints come from [method/input classes]. A single exact result is not claimed.`

**Rule only — total not observed**

> `This is a published rule, not an observed transaction total. Citizen Compass does not have a verified total for this option, so no total has been calculated or displayed. Source: [approved rule source]. Verification: [state].`

**Unavailable — calculation dependency unresolved**

> `This figure is not displayed because [dependency] has not been validated. Citizen Compass will not substitute an estimate.`

## Mostly-unverified ship page

Carry the approved design unchanged inside this system:

- Identity and a working 3D model remain available.
- Directly under identity: `Some figures on this page have not been checked for the current data set.`
- Mark an affected group once at its heading instead of repeating warnings on every cell.
- Individual rows still carry their provenance line so a verified value inside an otherwise unverified group remains distinguishable.
- Preserve a value only when its provenance is known.
- Unknown values read `Value withheld`; known absent values read `Not provided`; unresolved calculations read `Unavailable`.
- The notice does not turn the whole page red or green and does not block equipment/3D interaction.

## DPS trust sentence

Use the accepted copy pattern with generated values only:

> **Stock arithmetic check:** Citizen Compass matches CIG's supplied total on [N] of [M] stock ships checked. This confirms the addition, not achievable in-flight damage.

- `[N]` and `[M]` are generator output and never literals in UI copy.
- Provenance line: `Calculated by Citizen Compass · [verification state generated for the comparison run]`.
- The disclosure lists the compared surface, dataset/build identifiers, and mismatches if any.
- It does not use “official,” “combat validated,” or any burst/sustained claim beyond the field's verified name.

## Implementation acceptance checks

A builder can consider the grammar implemented only when:

- every displayed numeric value resolves to a mapped provenance class;
- every row resolves independently to verified, stale, or never verified;
- missing patch or date always produces never verified;
- no row inherits verification metadata;
- unknown provenance, known absence, and unresolved calculation render as three distinct states;
- source/method text remains visible without hover;
- every disclosure is keyboard reachable, announces expanded state, and returns focus correctly;
- compact and workbench layouts keep the provenance line below and aligned with the value;
- variable counts, totals, patches, dates, percentages, and prices come from data rather than prose literals;
- a computed rental total cannot render under `Rule only — total not observed`;
- the DPS trust sentence receives both counts from the generator.

## One dependency returned to C1

The approved vocabulary does not honestly identify a rental day rate or observed rental-tier total unless the source contract makes it a direct CIG value. The acquisition relationship schema must therefore include an approved, displayable source identity or explicitly rule that these rows remain unpublished.

CANARY LINE: slate-hinge-provenance-before-the-mark-0912

--- END OF ANSWER ---
