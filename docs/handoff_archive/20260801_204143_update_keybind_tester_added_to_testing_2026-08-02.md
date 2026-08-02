# UPDATE — keybinding tester page added to the testing area

Claude-02, Cowork brainstorming session, 2026-08-02. One new page in three
locations. **The layer was not touched.** No commits, no pushes.

## What was added

A standalone prototype page: an interactive keyboard that responds to real key
and mouse input, shows what each binding does in Star Citizen Flight mode,
switches modifier layers live, and reports whether a press registered as a tap,
a hold or a double tap with timing in milliseconds.

Written to three places, identical content:

| path | role |
|---|---|
| `testing/_src/keybinds.src.html` | **source of truth** |
| `testing/keybinds.html` | served by the local dev server |
| `testing/_deploy/keybinds.html` | so it ships with the next Netlify Drop |

## Deliberately NOT integrated into the layer

`testing/_layer.html` and `testing/_src/_layer.src.html` were left alone.

Reason: two sessions overwrote each other's work in this repo twice on
2026-08-01 — the dual handoff writer, and a blurred-backdrop change to
`_layer.html` that was destroyed by a push fifteen minutes later because that
file is a build output. A standalone page cannot be wiped by a layer rebuild,
so this one survives regardless of who builds next.

If it is later folded into the layer, that work belongs in
`testing/_src/_layer.src.html` and goes through whoever owns the build scripts.

## ACTION NEEDED — one line in a build script

`build_full.py` produces `testing/_deploy/`. It does not currently copy this
page, so the next full build will drop `_deploy/keybinds.html` and the page will
vanish from the deploy bundle without any error being raised.

Add a copy step for `keybinds.src.html` -> `_deploy/keybinds.html`, or the
manual copy has to be repeated after every build. Flagging rather than editing
the build scripts, since they are owned elsewhere.

Same applies to `testing/keybinds.html` if `build.py` ever cleans that folder.

## What the page currently does

- Reads physical key position, not the typed character, so it behaves correctly
  on non-US keyboard layouts. This matters: Star Citizen binds by position.
- Mouse buttons 1-5 and the wheel.
- Left Alt / Left Shift / Right Alt switch modifier layers live. Star Citizen
  distinguishes left from right modifiers and so does this.
- Press timing: under 400ms is a tap, 400ms or more is a hold, two taps inside
  320ms is a double tap. If the bound action is a hold and the user tapped it,
  the page says so.
- Click any key to see everything bound to it across all layers.
- Search box.

## Honest limits, stated on the page itself

- **The data is transcribed by eye from in-game screenshots and is not
  verified.** Entries the transcriber could not read confidently are marked with
  an orange `?`. This is Flight mode, keyboard and mouse only. On Foot, EVA,
  Camera, gamepad and joystick are not entered.
- Alt+F4, Ctrl+Alt+Del and the Windows key cannot be captured by any web page —
  Windows takes them before the browser sees them.
- Ctrl+W, Ctrl+T and Escape need the Keyboard Lock API, which requires
  JavaScript-initiated fullscreen. Not implemented in this prototype.

## What replaces the transcribed data

`defaultProfile.xml` from inside `Data.p4k`. It carries every action, its
default binding, the modifier definitions, and the link from an action's
internal name to its display label. The display names, descriptions, mode names
and category names are **already on disk** in `labels.json` in the source-1
snapshot — 910 `ui_CI*` action names, 53 `ui_CC*` modes, 42 `ui_CG*` categories.
Only the bindings themselves are missing.

Checked and rejected as shortcuts: three GitHub repos previously reported as
holding extracted default profiles do not (`SC-VRse` is a VR PowerShell tool,
`VectorSigma` is a VoiceAttack profile, `StarCitizenDiff` is unverifiable from
outside and unlicensed). The only public dump found is for 3.0.0 and is years
stale. Extraction from the local install remains the path.
`GlebYaltchik/sc-keybind-extract` is a purpose-built tool worth looking at
before writing one.

## Boundaries

`static/preview.html`, `releases/latest.html`, `_layer.html`,
`_src/_layer.src.html` and all build scripts untouched. Database, snapshots and
live site untouched. No commits, no pushes.
