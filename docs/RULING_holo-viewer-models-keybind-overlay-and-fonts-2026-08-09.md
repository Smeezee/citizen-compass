# RULING — holo viewer model source, keybind overlay scope, and builder fonts

    from      Sleven, 2026-08-09
    recorded  Claude Code
    status    DECIDED. These three were open; they are not open any more.

Three decisions, each with what it unblocks and what it costs, checked against
the repo rather than restated from the question.

---

## 1. Holo viewer — reuse the existing 235 `.glb`. Not the Fan Kit hulls.

**Verified on disk:** 235 `.glb` in `testing/_deploy/models`, which is exactly the
figure the decision was framed against. The Fan Kit's 14 `.ctm` holoviewer models
are at `C:\Users\david\Downloads\Fankit_2025_11_19\02_HOLOVIEWERS\` — **outside
this repo**, per `FINDING_fankit-inventory-2026-08-08.md`.

(The 234 `.ctm` inside the repo are a *different* set — one per ship folder under
`sc-ships/`, alongside `model.glb` and `model_scaled.glb`. They are not the Fan
Kit's 14. Worth stating so the next person counting `.ctm` files does not
conclude the Fan Kit is already vendored here.)

**This does not deviate from anything — it confirms it.**
`ARCHITECTURE_DECISIONS.md` §7 already specifies the convention
`models/<ship-slug>/model.glb` + `hardpoints.json` + `metadata.json`. §7 is
marked *RECOMMENDED (pending final sign-off)*; this ruling is that sign-off for
the model-source half of it.

**Cost accepted:** the Fan Kit geometry is cleaner. Coverage wins anyway —
235 hulls against 14, on a pipeline that already exists, versus a second
permanent pipeline serving 6% of the fleet.

**What it unblocks:** the previous work order listed "the 3D viewer /
model-serving question" as *blocked on a decision that's Sleven's, not on code*.
It is no longer blocked.

**Flagged, not decided (rule 8):** using our own `.glb` rather than Fan Kit
assets also avoids taking on the Fan Kit's redistribution terms for 3D models.
That is a licensing consequence and licensing is Sleven's alone — noting it as a
benefit to confirm, not a claim I am making.

**Recommend:** flip §7 (and §6, three.js) from RECOMMENDED to **LOCKED**. Not
doing that myself — changing a status to LOCKED on Sleven's behalf is his call,
and the standing instruction is to ask rather than assume.

---

## 2. Keybind overlay stays lightweight and links out to the full page.

The index page's overlay does **not** get the 691-action browser or the DOF
reference. It stays a verifier and links to `keybinds.src.html`.

**Verified:** 691 is exact, not approximate — it is the number of rows in
`keybinds_site.json` carrying a `label` (1103 rows total, 1025 distinct actions,
691 labelled). `WORKORDER_builder-ui-and-viewer-2026-08-09.md` already framed
both options at line 166 and called both defensible.

**The strongest argument for this one is rule 14, and it is worth stating
explicitly.** Duplicating the 691-action browser into the overlay would create a
**second copy of the same artifact** — two places rendering one action list, free
to drift, discovered later in a diff. This project has had five artifacts with
two writers and every one of them drifted. Linking out keeps exactly one browser,
in `keybinds.src.html`, and makes the second copy impossible rather than merely
discouraged.

It also keeps ~40 KB off the index page.

---

## 3. Builder fonts — match Star Citizen's UI type.

Saira Condensed, Rajdhani, Chakra Petch.

**This one has a real interaction that the decision as posed does not cover, and
it needs a deliberate answer before anyone implements it.**

`_layer.src.html` already ships a **user-facing accessibility font switcher** —
five modes, applied with `!important`:

```
cc-f-system   Segoe UI
cc-f-legible  Atkinson Hyperlegible   <- Braille Institute, low-vision
cc-f-lexend   Lexend                  <- reading proficiency
cc-f-serif    Source Serif 4
cc-f-mono     ui-monospace
```

Each rule is scoped `*:not(.cc-ui):not(.cc-ui *)` — so `.cc-ui` is an existing,
deliberate escape hatch for chrome that should keep its own type. **The mechanism
this ruling needs already exists**, which is the good news.

**The trap:** if the builder's *content* — the action rows, key names, the dense
reference text — is marked `.cc-ui` to pick up the SC fonts, that content becomes
permanently exempt from the accessibility switcher. Someone using Atkinson
Hyperlegible because they need it would find the one screen densest in small text
is the one screen that ignores their setting. Saira Condensed makes that worse
than average: condensed faces are harder to read at low vision, not easier.

**Recommended split, for Sleven to confirm:**

- **SC fonts on chrome only** — headings, tab labels, panel titles, buttons.
  Marked `.cc-ui`. This is what carries the Star Citizen feel.
- **Action table content NOT marked `.cc-ui`** — so it keeps following whatever
  font the reader chose.

That delivers the decision as made while leaving the accessibility feature
working. If Sleven wants SC type across the content too, that is his call to
make knowingly — but it should be made knowingly, not arrived at by marking the
whole panel `.cc-ui` and not noticing.

**Also noted:** the site already loads fonts from `fonts.googleapis.com` /
`fonts.gstatic.com` (Atkinson Hyperlegible, Lexend, Source Serif 4), so adding
families follows an existing pattern rather than introducing a new dependency.
All three named faces are, to my knowledge, available on Google Fonts under the
SIL Open Font License — **confirm the licence before shipping rather than taking
that from me**, since font licensing sits in the class of thing I report and do
not decide.

---

## Status

Decisions 1 and 2 are directly actionable and need no further input.
**Decision 3 needs one more answer from Sleven: the chrome-only split above, or
SC type across the content as well.**

Nothing has been implemented from any of these — no order has been given to
build the builder UI, and `WORKORDER_builder-ui-and-viewer-2026-08-09.md`
remains the place that work is specified.
