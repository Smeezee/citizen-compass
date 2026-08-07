# FINDING — device panel D3/D4/D5 status, and device-facts research status

    from      C3 (Cowork), 2026-08-07
    for       C1 / Sleven — status only, verified against the actual repo, not assumed
    checked   commit 232cac2 ("Device panel rev 2"), testing/_src/device_engine.js,
              testing/_src/patch_two_sticks.py, testing/_src/patch_btn_limit.py,
              data-layer/raw/devices/ (does not exist)

---

Sleven asked to verify, not assume, what actually landed from
`claude/workorder-device-visual-map.md` (D3/D4/D5) and `claude/workorder-device-facts.md`
before doing anything else. Checked both against the real repo — commit diffs and current
source, not the planning docs. Here's what's actually true.

## D1 (lag) and D2 (hats) — DONE, confirmed in code

Not asked about, confirmed anyway since they're in the same commit. `device_engine.js`
builds the device DOM once and only mutates text/classes/width after that — no `innerHTML`
after first build, matching the D1 fix exactly. Hat detection uses the sevenths rule
(`HAT_CENTRE=1.2857`) and names hats `hat1_up/down/left/right` — matching D2 exactly.

## D3 (one control, two identities) — PARTIALLY done

The work order asked for a real data model: `control: {id, label, x, y, inputs: [...]}`,
so the Gladiator's two-stage Main Trigger is one thing with two inputs, not two things in
one spot. **That specific data model does not exist in the repo.** What exists is a code
comment and a design principle: `device_engine.js` explicitly notes "a physical control
can be an axis AND a button at once, and nothing here may assume the two sets are
exclusive" — so the *processing* no longer breaks on a dual-identity control. But buttons
and axes still render through separate paths (a button grid, a separate axis list) — there
is no unified `control` object grouping them, and no `x, y` positioning data at all. That
positioning data is what D5's guided wizard and any future photo-map would need, and nothing
here produces it.

**Status: the bug D3 was protecting against (crashing or double-counting a dual-identity
control) is avoided. The data model D3 actually asked for is not built.**

## D4 (layout) — MOSTLY done, one piece missing, one piece off-spec

- **Both devices visible side by side, without scrolling** — done. `patch_two_sticks.py`
  gives each device its own column, side by side on a normal screen, stacking only when
  there's no room (`dvcols.pair` CSS). This part matches the work order exactly.
- **Show only controls that have fired, collapse the rest to one expandable line** — built,
  but not to spec by default. `patch_btn_limit.py` caps the *default* display at the first
  40 buttons (not the "0 at rest" the acceptance criteria asked for) and reveals any button
  the moment it's pressed, wherever its index falls. A **"Hide unused buttons" toggle
  exists** and does implement the literal ask — but it defaults to **off**
  (`hideUnused=false`), so out of the box you still see up to 40 tiles that have never
  fired, not zero. One line to flip if you want the strict spec instead of the 40-tile
  compromise.
- **Add-on devices (pedals, throttle quadrants) behind a separate toggle** — not found
  anywhere in the code. Every connected device currently gets the same column treatment;
  there's no secondary/primary distinction.

## D5 (guided mapping wizard) — NOT done

Searched `testing/_src/*.js`, `*.html`, and `*.py` for anything resembling a wizard, a
checklist, or the 34-control VKB Gladiator template (A1 Ministick, A2 Red Button, Main
Trigger stage 1/2, etc.) from the work order. **Nothing exists.** The current device panel
is purely a live telemetry readout — press a control, see which raw index lit up. There is
no "press A3 Center Hat — up" walkthrough, no known-device checklist, no completion state.
This is a real feature, not a small addition, and it's fully unbuilt.

## Device-facts research (`claude/workorder-device-facts.md`) — NOT STARTED

`data-layer/raw/devices/` does not exist in the repo at all — not `device_facts.json`, not
`device_facts_findings.md`, nothing. This work order (filed by C1, 2026-08-06: sourced USB
identity, button numbering, axis order, and geometry for VKB/VIRPIL/Thrustmaster/etc, with
mandatory source URLs per field) has zero output so far. Nothing to report beyond "not
begun" — worth knowing before assuming it's in progress somewhere.

## Bottom line, in order of what's actually missing

1. **D5 — guided mapping wizard.** Entirely unbuilt. The biggest gap of the five.
2. **Device-facts research.** Entirely unstarted — and D5 depends on it for any device
   beyond a freeform-photo fallback, since the wizard needs a known control list to walk.
3. **D3's actual data model.** The crash/double-count risk is defused, but the `control`
   object with positioned `inputs[]` that D5 (and any future visual map) would consume
   doesn't exist yet.
4. **D4's add-on-device toggle.** Missing; low effort relative to the other three.
5. **D4's "0 tiles at rest" default.** A toggle exists but isn't the default — a one-line
   fix if the strict spec matters more than the 40-tile compromise.

D1 and D2 are the only two of the five items that are fully done and match their
acceptance criteria exactly.
