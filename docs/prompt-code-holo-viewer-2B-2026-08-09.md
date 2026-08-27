# PROMPT FOR CODE — the 3D holo viewer as a real page, on the site's existing ship models. Order 2B.

    from    C1, 2026-08-09
    for     Code
    basis   claude/WORKORDER_builder-ui-and-viewer-2026-08-09.md (C3, work order 2, §2B)
            claude/FINDING_fixed-hardpoints-derived-2026-08-09.md (C3 — the derivation
              method and the honesty-line requirement this page must carry)
    decided Sleven, 2026-08-09: reuse the site's existing .glb models. Not the Fan Kit's
              14 .ctm hulls. This was the one thing blocking this order; it's resolved,
              and this document is the direct result.
    depends BOTH 2A passes land first, per C3's own sequencing (§3 of the work order:
              "2B last"). Pass 1: inbox/prompt-code-builder-wiring-2A-pass1-2026-08-09.md.
              Pass 2 covers the font/overlay decisions, also now resolved — see that
              order once it's written. If either hasn't landed, stop here and come back.

    Same pattern as the last two: §0 is C1 grounding C3's order against the real build
    scripts, including one thing the order stated as settled that turned out to need a
    real decision on Code's part. Read it before the task list.

---

## 0. What's confirmed, what's not there yet, and one build-mechanics gap C3's order didn't surface

**Confirmed: no new exposure question, as C3 said.** `_deploy/models/` already exists,
is already an allowed directory, and is already public regardless of the password gate
(established 2026-08-07, `claude/RULING_ship-models-provenance-and-proceed.md`). Nothing
about this order changes that.

**Confirmed: the site's existing 3D loading already lives in `_layer.src.html`**, using
`THREE.GLTFLoader` + `THREE.DRACOLoader`, keyed off a `CC_MODELS` map (ship id → model
filename). That map and the loader call are what the new viewer page should follow the
shape of, not reinvent.

**Not confirmed, and worth checking before relying on it:** C3's order states the site
builds against three.js `r0.128.0`, inferred from a CDN script tag
(`cdn.jsdelivr.net/npm/three@0.128.0/...`) still present in `_layer.src.html`'s *source*.
Confirm the vendored copy at `testing/_src/vendor/three/` actually matches that revision
before sourcing postprocessing files against it (§2 below) — don't assume the tag and the
vendored build were pulled at the same time just because they sit in the same repo.

**The gap: postprocessing isn't vendored yet, and there's no directory for it.**
`testing/_src/vendor/three/examples/js/` currently has exactly three subfolders —
`controls`, `libs`, `loaders`. No `postprocessing`. The holo shading effect needs
`EffectComposer`, `RenderPass`, `ShaderPass`, `MaskPass`, `CopyShader`,
`LuminosityHighPassShader`, `UnrealBloomPass` — none of which exist in this repo yet.
They need to be added to the vendored tree, from the exact three.js revision confirmed
above, not fetched fresh from whatever the latest release is (a version mismatch against
the vendored core build is exactly the kind of drift this project's vendoring exists to
prevent).

**A second gap, and this one C3's order didn't mention at all: how does the new page
actually get three.js into it?** `_layer.src.html` doesn't reference the vendored files
directly — `build_deploy.py` **inlines** three.js, the DRACO decoder, and GLTFLoader
literally into the page text as part of building `index.html` (lines ~61-260: it strips
3 asserted CDN `<script>` tags from `_layer.src.html`'s source and pastes the vendored
files in their place — that's what makes `index.html` reproducible and usable from
`file://` with no network or npm install). `keybinds.src.html`, by contrast, is copied
**verbatim** by `PAGES` — nothing inlines anything into it, and `_deploy/` has no
directory where a new page could just point a `<script src="vendor/...">` at the vendored
files, because only `images` and `models` are allowed there.

If the new viewer page is added to `PAGES` the same way `keybinds.src.html` was (§2B.4's
own description — "one line in PAGES"), it needs the same inlining treatment
`_layer.src.html` gets, or its three.js/DRACO/postprocessing script tags will point at
nothing once deployed. Two ways to close that, and the recommendation is the first:

- **Generalize the existing inlining step in `build_deploy.py`** so it applies to the new
  page's source too, not just `_layer.src.html`. Keeps everything on the one
  no-network-required, byte-reproducible mechanism this project already committed to, and
  doesn't touch `check_deploy_clean.py`'s allowed directories at all.
- **Or:** add a new allowed directory (e.g. `vendor/`) under `_deploy/` and ship the raw
  vendored files there, referenced by relative path. Works, but it's a deliberate guard
  edit for something the first option avoids needing at all, and it's the shape of edit
  §2B.4 itself flags as something to argue for, not slip in.

This is a build-mechanics call within normal engineering judgment, not a product decision
— pick one, but don't pick the second silently just because it's less code to write today.

---

## 1. The page

New page: `testing/_src/holo.src.html` (or whatever name reads best alongside
`keybinds.src.html` / `loadout.src.html` — naming is Code's call), added to `PAGES` in
`build_deploy.py`:

```python
('holo.src.html', 'holo.html'),
```

(and the matching entry in `check_deploy_clean.py`'s `DEFAULT_ALLOWED_FILES`, same
reasoning as `sc_export.js` in the 2A pass-1 order — the standalone guard check needs to
agree with the real build or it produces a false failure.)

Loads a `.glb` the same way `_layer.src.html` already does — `THREE.GLTFLoader` with
`THREE.DRACOLoader`, model selected from `_deploy/models/`, reusing `CC_MODELS` (or the
underlying data it's built from) rather than inventing a second ship-id-to-model map.

## 2. Hardpoints — real current locations, not the stale ones in `CURRENT-STATE.md`

`CURRENT-STATE.md` says the derivation script and output are at `inbox/place_hardpoints.py`
and `inbox/hardpoints.json`. **They're not there anymore** — checked directly:

    place_hardpoints.py                          repo root
    data-layerrawhardpoints/hardpoints.json       (yes, that's the actual directory name —
                                                    the known malformed path-join artifact
                                                    CURRENT-STATE.md already says not to
                                                    delete)

Both moved after the watcher filed them; the note in `CURRENT-STATE.md` just hasn't been
corrected yet. Use the real locations.

**`hardpoints.json` currently covers 4 ships only** — Cutlass Black, RSI Constellation
Aquila, Aegis Sabre, Cyclone. That's the full set right now. This order lands the viewer
with real derived hardpoints for those four and the existing behavior (no markers, an
honest "no weapon mounts in the data" message, matching what the Cyclone already does in
the prototype) for everything else. Running `place_hardpoints.py` against the remaining
~231 ships is real follow-up work, not part of landing this page — say so in whatever you
write up, so nobody reads "the viewer shipped" as "all 235 ships have real hardpoints."

Carry forward from the prototype, unchanged, per C3's order §2B.3:

- Marker/label/detail-panel behavior — hover to name, click to open, far-side markers
  faded, one marker per physical hardpoint with the gun and its gimbal together, turret
  guns marked not pilot-controlled.
- **The honesty line on every hardpoint panel — position is derived, CIG's own field is
  null for all 53,651 mounts. Do not drop this in the port.** It's the difference between
  an estimate and a claim, and it's the entire reason this derivation method exists
  instead of trusting a `position` field that isn't there.
- The Mirror L/R control, because handedness is an assumption nothing in the meshes can
  confirm.

## 3. What NOT to do

- Do not build a second model-loading pipeline. One loader (`GLTFLoader` + `DRACOLoader`,
  matching what `_layer.src.html` already uses), one model source (`_deploy/models/`).
- Do not fetch Fan Kit `.ctm` geometry or its decoder for this page. That path is closed
  by Sleven's decision, not a fallback if the `.glb` route gets annoying.
- Do not fetch postprocessing files from whatever the latest three.js release is. Match
  the confirmed vendored revision (§0), or the effect chain can silently behave
  differently against the pinned core build.
- Do not add a new `_deploy/` directory without picking the inlining approach in §0 first
  and confirming it's actually necessary.
- Do not run `place_hardpoints.py` against ships beyond the existing 4 as part of this
  order — that's follow-up work, call it out separately if you do start it.
- Do not run the deploy script. Build only.
- Do not `git add -A`.
- Nothing commits or pushes without Sleven's explicit go-ahead.

## 4. Acceptance

1. `python testing/_src/build_deploy.py` completes, including the deploy guard, with the
   new page's three.js/DRACO/postprocessing references resolving with no network access
   (matches the existing `index.html` reproducibility guarantee — test by disconnecting
   network or checking the built file contains no external `http(s)://` script src).
2. The built page loads a `.glb` ship, renders it with the holo shading, and shows fixed
   hardpoint markers on the 4 ships `hardpoints.json` covers — same counts as the
   FINDING: 15 on the Cutlass, 12 on the Aquila, 8 on the Sabre, 0 (with an honest reason
   why) on the Cyclone.
3. Every hardpoint panel carries the derived-position honesty line.
4. Mirror L/R flips both the marker positions and the left/right label.
5. `_deploy/` contains exactly `index.html`, the `PAGES` outputs (now including the new
   page), `images/`, `models/`, and whatever the §0 inlining decision requires — nothing
   else. `python testing/_src/check_deploy_clean.py` passes standalone.
6. `git --no-optional-locks diff testing/_src/keybinds.src.html testing/_src/_layer.src.html`
   shows no changes — this order touches neither.

---

## Still outstanding, unchanged by any of this

- No file this tool has generated has been loaded by Star Citizen — unrelated to the
  viewer, still true, still the thing that eventually needs ten minutes of Sleven's time.
- Hardpoints exist for 4 of ~235 ships. Scaling that up is real, separate work.
- The stuck device-tab bug is unrelated to this order and still needs an F12 reading from
  a machine with real sticks.

## Commands

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```

```
git --no-optional-locks diff testing/_src/keybinds.src.html testing/_src/_layer.src.html
```
