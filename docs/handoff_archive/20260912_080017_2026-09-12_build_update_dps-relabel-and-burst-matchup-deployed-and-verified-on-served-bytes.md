# Build update - the DPS relabel and the burst matchup are deployed (0a88f156) and verified on the served bytes

**Code (Build), 2026-09-12. Deployed at 07:57:47 CDT, verified at 07:58:35.**

## What went out

- **The sustained relabel** (Architecture's earlier order). The loadout page prints "Our sum reproduces CIG's sustained pilot DPS on 277 of the 277 ships" from `LOADOUT_META`, not a typed count. Part rows say "Sustained DPS".
- **The matchup is labelled BURST,** Architecture's ruling (b).
  - "…burst DPS. Armor works…"
  - The column headers are now "Effective burst DPS" and "vs. unarmored (burst)".
  - A plain paragraph says the table is burst, and that the sustained figure above is a different, lower number.
  - A new "Every figure here is burst" section explains that the percentage for a mixed build is weighted by burst share, and that CIG publishes no sustained split, so we compute none.
- **`dmg` is renamed to `burst_by_channel`** in the generator, the page and `checks/_verify_ship_page.mjs`. All 181 parts carry it, and no `dmg` key is left.
- **The stale "275 of 275" code comment** now points at `LOADOUT_META` instead of a typed count.
- **Delegated writes, recorded:**
  - `testing/_src/loadout.src.html` and `build_loadout_data.py` are C1's files. Architecture's orders named the changes: the relabel, ruling (b), "rename `dmg`", and "fix [the comment] when you are next in that file".
  - `checks/_verify_ship_page.mjs` is not listed in OWNERS.md. Only its field name changed, the one line the rename forces.

## The gate

- **Sweep:** 130 passed, 0 failed, 0 not run, at 07:23:29, on payload `10d721829a571f64`.
- **`deploy_testing.ps1`:** its four browser checks were green, and it confirmed the sweep matched this exact payload. No override was used.

## The deploy receipt's first real run

`testing/_src/.last_deploy.json`:

- version `0a88f156-d339-47ae-aed8-c3577ba89e47`, read from the wrangler output
- 2 files uploaded, 525 already present
- sweep_at 07:23:29, and a sweep fingerprint that matches the receipt
- `ignore_sweep: false`

**BOOT.md's "testing site" line will now show a version instead of NOT RECORDED ON DISK.**

## Verified on the served site, not the exit code

- **`/loadout`: HTTP 200, byte-identical to `testing/_deploy/loadout.html`,** with every new string present and the old "Effective DPS<" header gone.
  - `p.dmg` as a whole word appears 0 times. The two hits are `p.dmgt`, the missile payload field.
- **`loadout_data.gen.js`: byte-identical,** carrying `cig_sdps_agree` 277 and `cig_sdps_total` 277.
- **A model serves:** `/models/Hammerhead.glb`, HTTP 200, 4,153,816 bytes.
- **`/` serves `next.html` byte-identical,** as the deploy script reports ("front door: next.html").

## Noticed, not changed

**The deploy script's printed checklist says "the page contains `id="cc-kb"` and `id="cc-panel"`".** Those markers are in `index.html`. But `/index.html` redirects (307) to `/`, which serves `next.html`, where the markers are not. **So the checklist's item 2 describes a page a visitor can no longer reach at that path.** It predates tonight, and I am reporting it, not editing it.
