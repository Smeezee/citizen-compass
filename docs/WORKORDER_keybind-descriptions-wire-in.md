# WORK ORDER — wire plain-language descriptions into the keybind page

    from      C3 (Cowork), 2026-08-07
    for       C1 -> Claude Code
    status    238 draft descriptions written and in the repo. Not yet wired into
              the page. That's the one gap between what's built and what Sleven
              asked for: "show what the key will do in game and be helpful."
    data      data-layer/processed/keybind_descriptions_draft.json (238 rows) +
              .MANIFEST.json (methodology, confidence key, two flagged rows)

---

## 1. WHERE THE KEYBIND PAGE ACTUALLY STANDS — more built than the planning docs suggest

The project docs (`claude/plan-keybind-newplayer.md`, `claude/workorder-keybind-extraction.md`,
`claude/workorder-device-visual-map.md`) describe planning from 2026-08-02/05. **The repo has
moved well past that** — recent commits not reflected in those docs:

    232cac2  Device panel rev 2: fix the lag, and stop inventing axis names
    2f435ce  Make the keybind page look like a keyboard, and capture the keys Windows steals
    8ee5cdd  Give the page back to the mouse: the wheel was being swallowed everywhere
    0c25997  keybinds: make the Gamepad and Joystick/HOTAS tabs read real hardware
    3254dea  Split the keybind page into six modes, generated from the actionmap

**In plain terms: the device-panel bug list (D1/D2 at least) and Product A's core structure
(Flight/On Foot/E.V.A./Vehicle/Camera/Social, built from real `keybinds_site.json` data via
`build_keybind_modes.py` -> `kb_modes.gen.js`) are already done.** This work order does not
re-litigate any of that. `claude/CURRENT-STATE.md` has been updated to point at this instead
of the stale 2026-08-05 build status.

**What's still missing, confirmed by reading the build script and the page source directly:**
`build_keybind_modes.py` never reads or emits a `desc` field, and `testing/_src/keybinds.src.html`
has no reference to `desc` anywhere. **The page shows key -> action name. It does not show what
the action does.** That's the exact gap between what exists and "be helpful."

---

## 2. WHAT'S NEW THIS SESSION

**238 plain-language descriptions, drafted and in the repo**, covering every keyboard-bound,
labeled action that doesn't already have a real CIG description (86 of those already exist and
need no drafting - see `docs/finding-keybind-descriptions-closed.md`, closed, don't re-chase).

    data-layer/processed/keybind_descriptions_draft.json           238 rows
    data-layer/processed/keybind_descriptions_draft.MANIFEST.json  methodology + flags

**These are drafts, not facts.** Every row carries `source: "cc_draft"` and a `confidence`
(169 high, 64 medium, 5 low) so the page - and Sleven - can tell a CIG-written description
from one this session wrote from the label, group, actionmap, and binding context alone.
**Per `claude/plan-writing-keybind-descriptions.md` §6: draft first, Sleven corrects rather
than authors from scratch.** That review has not happened yet - these should not go live
un-reviewed.

**One real bug caught and fixed before it shipped:** `v_yaw_left`/`v_yaw_right` mean "yaw the
ship's nose" under `spaceship_movement` but "turn the ground vehicle" under `vehicle_driver` -
same action name, different meaning, different actionmap. A description keyed by action name
alone would have silently mislabeled one of them. **Every row in the draft file carries both
`action` and `map` for this reason - join on the pair, never on `action` alone.** The join
script asserts this (checks every action name across the 238 rows for a second, different
label under a different map) and found exactly this one collision, nothing else. Re-run that
check any time this file is regenerated for a future patch.

**Five rows flagged for an actual look in-game, not just a read**, listed with reasoning in
the MANIFEST: the four "reactor power throttle" F9/F10 actions (labeled just "Increase/Decrease
Throttle" but grouped with power-triangle controls, not the flight-throttle controls - the
description is a plausible guess from the grouping, not confirmed), and `view_switch_to_alternative`
vs `view_enable_camview_mode` (identically labeled, different keys, unclear real distinction).

---

## 3. THE BUILD STEP

1. Extend `build_keybind_modes.py` to also load `keybind_descriptions_draft.json`, joined to
   `keybinds_site.json` on `(action, map)`.
2. For each action: use `keybinds_site.json`'s own `desc` if it's real (non-null, not a
   duplicate of the label - `build_keybind_modes.py` doesn't currently check this, it should).
   Otherwise fall back to the draft file's `desc`.
3. Carry `confidence` and `source` through into `kb_modes.gen.js` so the page can render a CIG
   description and a cc_draft description differently - e.g. no marker for CIG-sourced text,
   a small "draft" tag for cc_draft ones until Sleven has reviewed them. Do not present a
   cc_draft description with the same visual weight as a CIG one; that would misrepresent
   what's verified.
4. An action with neither a real CIG desc nor a drafted one should show nothing rather than a
   placeholder - same standard the project already applies everywhere else (no invented data).

## 4. NOT THIS WORK ORDER'S CALL

- **Reviewing the 238 drafts.** That's Sleven's pass, same shape as the shop-capture review
  screen - machine drafts, human confirms, nothing publishes as "confirmed" unreviewed. The
  five specifically-flagged rows are the highest-value place to start.
- **The five items still open in `claude/workorder-device-visual-map.md`** (D3 data model,
  D4 layout, D5 guided mapping) - unclear from the repo alone which of these landed in the
  "Device panel rev 2" commit and which are still open. Worth a direct status check against
  that commit's diff before assuming any of D3/D4/D5 still need doing.
- **`claude/workorder-device-facts.md`** (vendor-sourced button numbering for VKB/VIRPIL/
Thrustmaster/etc.) - status of the actual research unclear from the repo; not touched this
  session.
- **Whether the 238 cc_draft descriptions are covered by the same rights hold as the 130
  CIG-written keybind descriptions in `labels.json`.** `CURRENT-STATE.md` says to ship the
  keys and hold CIG's description text until `claude/finding-description-rights-correction.md`
  is settled. The 238 rows this session added are original text - written by C3 from the
  action name, label, group, actionmap and binding context, not copied or paraphrased from
  any CIG source - which is a different situation than reproducing CIG's own Comm-Link-style
  prose. That distinction is noted here as a fact, not a ruling; whether it actually clears
  these 238 rows to ship is a legal call and stays Sleven's, not this work order's.
