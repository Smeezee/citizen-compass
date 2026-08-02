# UPDATE — loadout bench added; the deploy copy gap fired once already

Claude-02, 2026-08-02. Two standalone pages now live in the testing area, plus
two tabs on the layer. No commits, no pushes.

## THE IMPORTANT BIT — for whoever owns the build

`build_full.py` has been replaced by `build_deploy.py` (and a `_src/vendor/`
folder appeared) while this session was working. Good — but the new build
**dropped `_deploy/keybinds.html`**, silently and with no error, exactly as the
Cloudflare work order predicted. It was restored by hand from
`_src/keybinds.src.html`.

**There are now TWO pages that must be copied into `_deploy/`, not one:**

    _src/keybinds.src.html  ->  _deploy/keybinds.html
    _src/loadout.src.html   ->  _deploy/loadout.html

Without both, the KEYBINDS and LOADOUT tabs on the testing site point at 404s.
Nothing errors; the tabs just stop working. Please add both copy steps to
`build_deploy.py` rather than relying on manual restores.

## What was added

**`loadout.src.html` — the loadout bench.** An interactive A/B component
comparison. Click any slot, see every part that fits it, hover an option and the
outcome numbers preview the change before you commit, click to fit it. Two
builds side by side with live deltas.

Design points worth keeping:
- **Signature is a first-class stat.** IR and EM sit next to DPS, same size,
  teal. Erkul is a damage calculator; nothing on the market answers "how visible
  am I", and the ship files carry per-component-group emission data that makes
  it computable.
- **Power and cooling budgets are shown and can go red.** A build that overheats
  says so. Most tools happily let you design something that cannot fly.
- **Locked slots are greyed**, matching the real `Editable` flag in the ship data
  (the Vulture's salvage beams cannot be swapped).
- **The shopping list and the trip sentence are generated, not written.** Parts
  are grouped by location, and a cost-per-improvement pass flags the change with
  the worst value so a player can drop it.
- **The build is encoded in the URL**, so a loadout is a shareable link. This was
  designed in deliberately — see `claude/historian-loadout-context.md`, where the
  same mechanism is what would let a player hand their loadout to the AI
  Historian.

**Data honesty:** every component name, stat and price on the page is invented.
The slot structure, sizes, groupings and locked flags follow the shape of the
real game-file data. The page says so in a banner and in a footer note.

## Unblocked finding — worth recording

Manual Blender hardpoint placement is **not** required for component comparison.
`ships/drak_vulture.json` carries a `Loadout` array of 85 entries, each with
`HardpointName`, `Type`, `Grade`, `MinSize`, `MaxSize`, `CompatibleTypes`,
`ClassName` and `Editable`. That is every slot, its size range, what fits it, what
is stock and whether a player can change it — for all 316 ships, straight from
the game files.

Blender work is only needed for placing 3D markers on the model (click-a-turret
in the viewer). The comparison tool, the slot grid and the shopping list all run
on data already on disk.

## Files touched

Added: `_src/loadout.src.html`, `testing/loadout.html`,
`_deploy/loadout.html`, `_deploy_lite/loadout.html`.
Restored: `_deploy/keybinds.html`.
Layer tab injected into `_src/_layer.src.html`, `_layer.html`, `index.html`,
`_deploy/index.html`, `_deploy_lite/index.html` (element `cc-lo-tab`, blue,
below the teal KEYBINDS tab).

Build outputs were edited directly again so the deploy folder is pushable now
without a rebuild. The source carries the same change, so a rebuild reproduces
rather than loses it.

## Boundaries

`static/preview.html`, `releases/latest.html`, database and snapshots untouched.
No commits, no pushes. Build scripts not edited — the copy-step fix above is
flagged for their owner, not applied.
