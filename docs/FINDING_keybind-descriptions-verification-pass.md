# FINDING — keybind description accuracy pass against outside CIG-adjacent sources

    from      C3 (Cowork), 2026-08-07 (same day as the original 238-row draft)
    for       C1 / Sleven — informational, no action required unless flagged below
    touches   data-layer/processed/keybind_descriptions_draft.json (in place, still 238 rows)
              data-layer/processed/keybind_descriptions_draft.MANIFEST.json (in place)

---

Sleven asked for a pass to make sure the 238 drafted keybind descriptions are as accurate
against CIG's own information as possible. This is that pass. **Nothing about the build
plan in `docs/WORKORDER_keybind-descriptions-wire-in.md` changes** — same file, same path,
same schema, same join key. This finding documents what was checked and what moved.

## What was checked

CIG's own site (robertsspaceindustries.com/community-hub) was checked first — a camera
controls tutorial post and the 3.20 keybind-changes guide. Both are video-first landing
pages; neither had usable description text in the page itself, so they contributed
nothing this pass. **No CIG-written text was found, copied, or added anywhere in this
pass** — everything below is this session cross-checking its own drafted text against an
independent third-party reference, not sourcing new CIG text.

The most useful source was **scfocus.org**, a fan-run keybind reference that's actively
maintained through the current Alpha 4.8 build. It isn't CIG, and its exact wording was
never copied — it was used to sanity-check category and mechanic, the same way a second
technical reviewer would.

## What changed

All 5 of the original `confidence:low` rows moved up, none moved down:

- **The four "reactor power throttle" rows (F9/F10)**, originally flagged because they
  were labeled just "Decrease/Increase Throttle" and it wasn't clear whether that meant
  ship speed or reactor power. scfocus.org's own keybind list places these same four
  actions inside its "Power Distribution" section, directly after the weapons/engines/
  shields triangle controls — not inside its separate flight-speed section. That matches
  this repo's own actionmap grouping (`spaceship_power`, group "Flight - Power") and
  confirms the category. **Moved low → medium.** The exact step-size mechanic is still
  not confirmed in-game, which is why this stopped at medium and not high.
- **`view_switch_to_alternative` (Z) vs `view_enable_camview_mode` (F4)** — both carried
  the identical label "Advanced Camera Controls Modifier (Hold)" with no way to tell them
  apart from the data alone. scfocus.org's camera-controls page describes Z (held) +
  mouse movement as orbiting the third-person camera around a fixed focal point, and F4
  as the separate modifier that unlocks the full offset/zoom/field-of-view/depth-of-field/
  preset adjustment set. Both descriptions were rewritten to say that. `view_switch_to_
  alternative` **moved low → medium**; `view_enable_camview_mode`'s text was tightened,
  confidence held at medium.

Two more rows were corroborated closely enough to move up a full tier:

- `v_mgv_switch_brake_on_idle` — scfocus.org's description of the auto-brake toggle
  matches this draft's wording almost exactly. **Moved medium → high.**
- `eva_boost` — scfocus.org confirms Boost increases EVA movement speed, matching the
  draft. **Moved medium → high.**

New confidence counts: **171 high / 67 medium / 0 low** (was 169/64/5).

The remaining medium-confidence rows (the bulk of the 64, now 67) were reviewed
structurally against known game mechanics rather than individually web-checked — nothing
else stood out as genuinely ambiguous the way the two camera modifiers and the power-
throttle group were. If Sleven's review pass turns up something in that set worth a
second look, flag it and it'll get the same treatment.

## What this doesn't resolve

This is still not CIG's own words, and it's still not Sleven's in-game confirmation — it's
a second independent read from a currently-maintained fan source, used to check the
original draft rather than replace it. Every row still carries `source: "cc_draft"`.
**The review pass called for in `claude/plan-writing-keybind-descriptions.md` §6 — Sleven
corrects rather than authors — still has not happened**, and this pass doesn't substitute
for it.

The description-rights question flagged in `docs/WORKORDER_keybind-descriptions-wire-in.md`
§4 is unrelated and still open. This pass improved the factual accuracy of text this
session already wrote in its own words; it did not touch, and does not resolve, whether
that text is clear to publish. That's still Sleven's call.
