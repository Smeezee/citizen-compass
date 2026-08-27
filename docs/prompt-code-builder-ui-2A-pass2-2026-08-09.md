# PROMPT FOR CODE — the 691-action browser, DOF reference, fonts, and the overlay link-out. Pass 2 of 2A.

    from    C1, 2026-08-09
    for     Code
    basis   claude/WORKORDER_builder-ui-and-viewer-2026-08-09.md (C3, work order 2, §2A)
    depends inbox/prompt-code-builder-wiring-2A-pass1-2026-08-09.md lands first — this
              pass adds browsing UI on top of the import/export wiring pass 1 builds; it
              doesn't replace it. If pass 1's acceptance criteria haven't all passed, stop
              here and come back.
    decided Sleven, 2026-08-09, both of the open questions from C3's order:
              - the index-page overlay stays a lightweight verifier and links out, it does
                NOT get the full builder duplicated into it
              - fonts should match Star Citizen's real UI type (Saira Condensed, Rajdhani,
                Chakra Petch), not the site's existing stack

---

## 1. The 691-action browser and DOF reference — generate the data, don't paste it

The prototype inlines 127 KB of action data directly into the HTML (`data.json`, pasted
in). Don't repeat that here — it creates a second copy of information that already has an
owner in `data-layer/processed/keybinds_site.json` and `actionmap_categories.json`, and it
will drift the first time either changes.

**Follow the pattern `build_keybind_modes.py` already established** for `kb_modes.gen.js`:
a generator script at repo root, reading from `data-layer/processed/*.json`, writing a
`.gen.js` file into `testing/_src/` with `encoding="utf-8", newline="\n"` (rule 15), added
to `PAGES` in `build_deploy.py` and loaded in `keybinds.src.html` the same way
`kb_modes.gen.js` and `sc_export.js` (pass 1) already are — `<script src="...gen.js">`.

Write a matching generator (name it consistently with the existing one — e.g.
`build_kb_actions.py`) that produces the 691-action, 9-category, 35-section browsing
structure with the plain-English section descriptions.

**The DOF reference table doesn't exist as repo data yet — it's currently only inside the
prototype.** Use the corrected version from
`claude/FINDING_exporter-round-trip-passes-2026-08-09.md` §8, not whatever the prototype
currently ships, since the prototype predates that correction in at least one case
(`z` was wrongly UNPROVEN there and is now PROVEN):

    x  y  z  rotz     PROVEN — appear in real player profiles
    slider1           PROVEN — in the game's own shipped defaults only
    rotx roty slider2 UNATTESTED — absent from every file read so far; not the same
                                    as rejected, just never seen

Ship this alongside the action data, generated rather than hand-typed into the page, same
reasoning.

## 2. Fonts — serve as files, not inlined

Sleven's call: match Star Citizen's actual type (Saira Condensed, Rajdhani, Chakra
Petch). Recommend serving them as real font files under a new `_deploy/fonts/` directory
rather than the prototype's ~115 KB base64-inlined approach — matches how this project
already handles other large binary assets (`images/`, `models/` are served files, not
inlined), and keeps `keybinds.html` from growing by six figures of base64 text for
something that doesn't need to change per-build.

This needs a **deliberate edit** to `check_deploy_clean.py`'s `DEFAULT_ALLOWED_DIRS`
(currently `{"images", "models"}`) — that's the guard §2B.4 already flagged as something
to argue for, not slip in. The argument is above; make the edit and note it plainly in
whatever you write up, since a new top-level allowed directory is exactly the kind of
change future sessions need to know was deliberate.

`build_deploy.py` will need a copy step for `fonts/` into `_deploy/`, matching however
`images/`/`models/` already get there (check the existing copy logic for those — mirror
it, don't invent a second mechanism).

## 3. The overlay — link out, don't duplicate

`_layer.src.html`'s existing "keybinding tester overlay" section (confirmed present,
independent of `keybinds.src.html`, not covered by the device-panel single-writer guard)
stays a lightweight verifier. Add a link from it to the full `keybinds.html` page for
anyone who wants the action browser, DOF reference, or import/export.

Do not add the 691-action browser, DOF page, or import/export UI into `_layer.src.html`
or anything it includes. That was the option Sleven didn't pick — don't build it as a
hedge.

## 4. Acceptance

1. `python testing/_src/build_deploy.py` completes, including the deploy guard.
2. `_deploy/fonts/` exists, contains the three typefaces, and `check_deploy_clean.py`
   accepts it as a deliberately-allowed directory (not by disabling the guard — by adding
   `fonts` to `DEFAULT_ALLOWED_DIRS`).
3. The built keybind page renders in the Star Citizen typefaces and browses all 691
   actions across 9 categories / 35 sections, each with its plain-English description.
4. The DOF reference page shows the corrected evidence table from §1, not the prototype's
   pre-correction version.
5. `git --no-optional-locks diff testing/_src/_layer.src.html` shows a link added to the
   overlay section and nothing else — no action-browser or DOF content duplicated in.
6. `git --no-optional-locks diff testing/_src/device_engine.js` shows no changes — this
   pass doesn't touch device identity, that landed in pass 1.
7. `_deploy/` contains exactly: `index.html`, the `PAGES` outputs, `images/`, `models/`,
   `fonts/` — nothing else.

## What NOT to do

- Do not inline `data.json` or the DOF table into any HTML file.
- Do not duplicate the action browser into the index-page overlay.
- Do not touch `device_engine.js` or the stick-identity logic — pass 1's job, done.
- Do not touch the 3D viewer.
- Do not run the deploy script. Build only.
- Do not `git add -A`.
- Nothing commits or pushes without Sleven's explicit go-ahead.

## Commands

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```

```
git --no-optional-locks diff testing/_src/_layer.src.html testing/_src/device_engine.js
```
