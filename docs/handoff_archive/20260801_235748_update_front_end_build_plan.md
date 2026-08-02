# Front end build plan filed — 2026-08-02, Cowork Claude-02

Full plan on disk at `docs/workorder-front-end-build-plan.md` and in the
claude.ai project at `claude/front-end-build-plan-2026-08-02.md`. This note is
the pointer, not the content.

## What it covers

Three builds, in priority order:

- **Build A — find / item / shop.** Plain-English search with a stop-word strip,
  one page per item, one page per shop. Highest demand, serves three of the five
  gaps found in the demand research. Nine real search phrases are given as test
  cases; they are the requirement, not a tidy unit test.
- **Build B — loadout bench.** A/B component comparison with signature as a
  first-class stat, power and cooling budgets that can go red, hover-preview, and
  a generated shopping trip. First feature that genuinely needs FastAPI serving
  public traffic.
- **Build C — keybinding reference.** Blocked on `defaultProfile.xml`.

Plus: the data inventory with join keys and gaps, and the architecture decisions
already taken (tags not folders, ~7 doorways, components in two places,
shareable URL state).

## Two build defects that block everything else

Fix these first — they have both already failed silently.

1. **`build_deploy.py` does not own the three right-edge tabs.** `cc-kb-tab`
   (teal, keybinds.html), `cc-lo-tab` (blue, loadout.html), `cc-fi-tab` (amber,
   find.html). Wiped by rebuilds twice on 2026-08-02 — at 01:15 and again at
   06:33, the second time including `_src/_layer.src.html` itself. Something
   upstream regenerates the source. Emit the tabs from a list; hand-patching
   after every build is not workable.

2. **`build_deploy.py` does not copy the three pages** into `_deploy/`:

       _src/keybinds.src.html  ->  _deploy/keybinds.html
       _src/loadout.src.html   ->  _deploy/loadout.html
       _src/find.src.html      ->  _deploy/find.html

   `keybinds.html` was dropped silently once already and restored by hand.
   Without the copy steps the tabs point at 404s and nothing errors.

**Prove both per hard rule 12:** delete the three files, remove the three tabs,
run the build, assert all six are present afterwards.

## Prototypes on disk

`testing/_src/find.src.html`, `loadout.src.html`, `keybinds.src.html`,
`kb_overlay.inc.html`. All run, all deployed, **all data invented.** Executable
specifications for layout and behaviour. Where the plan and a prototype
disagree, the plan wins.

`testing/_src/` is still uncommitted. `_deploy_lite/` (243 files, ~6 MB) is
hand-made and nothing regenerates it — make it a build target or delete it.

## Finding worth acting on

Manual Blender hardpoint placement is **not** required for component comparison.
`ships/drak_vulture.json` carries a `Loadout` array of 85 entries with
`HardpointName`, `Type`, `Grade`, `MinSize`, `MaxSize`, `CompatibleTypes`,
`ClassName` and `Editable`. Every slot, size range, compatible part, stock
fitting and editable flag — for all 316 ships, from the game files. Blender is
only needed for 3D marker placement on the model, which is a separate later
layer. **One file was checked. Confirm it holds across others.**

## Known gap that shapes every page

**No item images. Zero.** All 7,728 UEX items have an empty `screenshot` field
and no wiki link; 1,387 carry an RSI store link. Templates must look finished
with the optional fields empty, or twenty thousand pages look broken.
