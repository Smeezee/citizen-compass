# Update — 2B: holo viewer built. Two of the four hardpoint ships have no model in the library.

The page builds, ships, and passes the guard. Two of the order's assumptions did
not survive contact with the repo, and one of them changes what the viewer can
actually show.

## The finding: 27 of 35 derived hardpoints have no hull to sit on

Acceptance 2 asks for markers on four ships — 15 Cutlass, 12 Aquila, 8 Sabre,
0 Cyclone. The counts in `hardpoints.json` are exactly right. **The models are
not there.**

```
Aegis Sabre               -> Sabre.glb      8 hardpoints   displayable
Tumbril Cyclone           -> Cyclone.glb    0 hardpoints   displayable
Drake Cutlass Black       -> NO MODEL      15 hardpoints   CANNOT SHOW
RSI Constellation Aquila  -> NO MODEL      12 hardpoints   CANNOT SHOW
```

**Neither the base Cutlass Black nor the Constellation Aquila exists** — not in
the 235-file `_deploy/models/`, and not in `sc-ships/` either. Checked both
directly. This is an absence from the library, not a deploy gap and not a naming
mismatch. What exists is:

- `Cutlass_Black_Best_In_Show_Edition_2949.glb`, plus Blue, Red, Steel
- `Constellation_Andromeda`, `Phoenix`, `Phoenix_Emerald`, `Taurus`

**I did not substitute either.** The BIS 2949 edition is *plausibly* the same
airframe as the base Cutlass Black, and if it is, 15 hardpoints light up
immediately — but "plausibly the same airframe" is exactly the kind of
assumption that would be invisible once markers are drawn on it. Markers on the
wrong hull still look like markers. `build_holo_data.py` has an empty
`MANUAL_MATCHES` dict for precisely this: **one line from Sleven confirming the
hull is identical and it works.** The Aquila has no equivalent variant at all.

The page lists both unmatched sets on screen rather than hiding them, so the
viewer says what it cannot show instead of quietly showing half.

## The holo effect is a material, not a postprocessing chain

The order specifies `EffectComposer`, `UnrealBloomPass`, `LuminosityHighPassShader`
and friends. **None of them are vendored here** — `vendor/three/examples/js` has
`controls`, `libs` and `loaders` and no `postprocessing` directory — and they are
nowhere else on this machine. Adding them means fetching third-party JavaScript
and shipping it to execute in a visitor's browser.

So the hologram is a `ShaderMaterial` written in the page: fresnel rim,
scanlines, additive blending, against the already-vendored core. **No download,
no new dependency, no network.** It is a different implementation of the same
look and it is flagged as such rather than presented as what was asked for. If
the real chain is wanted, vendoring those files at the pinned revision is a
deliberate decision, not something to do on the way past.

I could not confirm the vendored revision: `vendor/three/build/` contains only
`three.min.js` and the minified build carries no readable `REVISION` string. The
CDN tag in `_layer.src.html` says `three@0.128.0`. **Unverified, so not claimed.**

## §0's build-mechanics decision: option 1, generalize the inlining

`build_deploy.py`'s copy loop now substitutes a `<!-- CC_VENDOR_THREE -->` marker
with the inlined three.js / OrbitControls / GLTFLoader / DRACOLoader and the
base64 draco decoder — **the same bytes `index.html` already uses**. Pages
without the marker are copied byte-for-byte exactly as before, so nothing changes
for keybinds/loadout/find or the `.gen.js` files.

No `vendor/` directory was added to `_deploy/`, which is the whole point of
picking option 1. The substitution happens **inside the existing copy loop**, not
in a second pass over `_deploy` afterwards — one writer per artifact.

It also refuses to ship: if a marker-bearing page still contains a CDN reference
after inlining, the build exits rather than publishing a page that needs the
network.

## Also corrected

**`CURRENT-STATE.md`'s paths were already known-stale and the order's correction
was right** — `place_hardpoints.py` is at repo root and the data is at
`data-layerrawhardpoints/hardpoints.json`. Used those. Did not run
`place_hardpoints.py` against any further ships.

## Acceptance

| # | | |
|---|---|---|
| 1 | build completes; no network needed | ✅ **0 external script srcs** in `holo.html`; three.js and the draco wasm inlined; 1.1 MB |
| 2 | loads a `.glb`, holo shading, markers on 4 ships | ⚠️ **2 of 4 impossible — no model exists.** Sabre (8) and Cyclone (0) wired. Rendering itself **NOT VERIFIED — needs a browser** |
| 3 | every hardpoint panel carries the honesty line | ✅ rendered per panel, names the null `position` field and all 53,651 mounts |
| 4 | Mirror L/R flips markers and the label | ✅ wired — flips marker X, model scale, and swaps Left/Right in the label through a sentinel so the two replacements cannot chase each other. **Not observed in a browser** |
| 5 | `_deploy/` exact; standalone guard passes | ✅ `index.html`, 8 PAGES outputs, `images/`, `models/`, `fonts/` |
| 6 | `keybinds.src.html` / `_layer.src.html` unchanged | ✅ zero `holo` references in either |

**Nothing in this page has been seen in a browser.** The geometry, the shader,
the markers and the mirror are all code-verified only. That is the same gap as
pass 1's export button and it is worth stating plainly rather than letting
"builds clean" stand in for "works".

## State

Nothing staged, nothing committed, no `git add -A`. Deploy script not run.
All three orders (2A pass 1, 2A pass 2, 2B) are now built.

**Still outstanding, unchanged:** no file this tool generated has been loaded by
Star Citizen; hardpoints exist for 4 of ~235 ships and only 2 can be shown; the
stuck device-tab bug still needs an F12 reading from a machine with real sticks.
