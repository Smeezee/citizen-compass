# Memo

To:      Design
From:    Grok (Design / CIC)
Date:    2026-09-13
Status:  Open
Subject: Loadout workbench — decision-strip pass (builds on Echo second pass; needs C1 before Build)

**Bounce base:** Echo / Design second pass (Sleven pasted 2026-09-13) — direction holds; layout revised so replacement choice and consequences stay together. Echo could not inspect live files; quantum-range stays previously reported, not re-proven in that pass.

**This letter:** Grok’s tightened Design package for the same job. Explicit comparison to Echo below. **Do not implement until C1 rules** (Echo owns the bounce thread; overlapping Grok work needs Architecture stamp).

---

## ONE JOB

Change one fitted part, know what it does **before** you commit, keep your place after.

---

## LAYOUT — DECISION STRIP

| Zone | Role |
| ---- | ---- |
| Main / left | Ship viewer — look, don’t decide. Not a third permanent decision panel. |
| Right rail | **Decision strip** (always where the act happens): (1) fitted-component list → (2) this hardpoint → (3) **preview strip** → (4) Fit / Cancel preview. |
| Details | Replace the list **in the same rail**; clear return to list. |
| Mobile | Same sequence, single column; viewer collapses above the strip. |

**Do not** put the important deltas under a large viewer where selective attention will miss them (Echo’s correction — kept).

---

## PREVIEW STRIP (ALWAYS BESIDE FIT)

Show together, immediately above **Fit component**:

**Fitted / Candidate / Difference / Meaning**

- Previewing a candidate does **not** silently install it.
- Preview ≠ installed. **Fit** commits. **Cancel preview** backs out with no change.

---

## TWO COMPARISON MODES (NAMED IN THE UI)

| Mode | When | Meaning |
| ---- | ---- | ------- |
| **vs fitted** | Default on a swap | What this change does to the *current* build |
| **vs stock** | Whole-loadout review only | Stock / Current / Difference / Meaning for the complete build |

Mode chip always visible. **Never mix** the two in one table. Component replacement compares against what is currently fitted; whole-loadout review is the stock pass.

Build A vs Build B: one comparison surface, identical stat rows, no independently scrolling columns.

---

## AFTER FITTING

- Keep selection and camera position.
- Persistent **Changed** label on that hardpoint.
- Resulting differences + **Undo** nearby.
- **This pass:** one-step Undo on that hardpoint. Multi-undo stack = later, not now.

---

## HEADER

Ship name · loadout name · patch · verification status **only if** `last_verified_patch` (or equal) is actually present — otherwise do not imply the page is verified-live.

Save and Share stay separate.

---

## SHOPPING

Purchase plan stays inside Citizen Compass. Unknown prices stay **unknown** — never invent a number.

---

## VISUAL TREATMENT

Quiet surfaces, readable text, restrained borders. Emphasis only for selection, next action, and meaningful warnings. Pair color with words/symbols; an increase is not automatically better. Label burst and sustained separately. Recommendations, not palette psychology claims.

---

## ACCEPTANCE (HARD)

Keyboard-only and with 3D unavailable: **select → preview → read Δ + Meaning → Fit → Undo** without losing place or needing the viewer. Mobile preserves the same sequence in one column. Crowded model markers must have equivalent list controls (target size: aim ~44px rows/controls; meet WCAG minimums at least).

---

## VS ECHO (EXPLICIT)

| Keep from Echo | Add / harden here |
| -------------- | ----------------- |
| Consequences next to Fit | Named **decision strip** as the only decision chrome |
| Candidate vs stock distinction | **Mode chip** in UI; never mix tables |
| Research framing (attention, cognitive, target size) | Hard acceptance path + verification honesty |
| Echo owns Design bounce | C1 must rule before Build; no silent implement |

**Quantum-range:** out of scope for this UX pass — leave as open defect pointer; do not imply this letter fixes it.

---

## ASK

**C1 (Architecture):** rule this package (or name holds) so Build has one Design target.  
**Echo:** bounce/amend if the strip or mode chip fights the second pass — reply on Design tray.  
**Build:** wait for C1. No code from this letter alone.

*Grok (Design / CIC), 2026-09-13. On Sleven’s word.*