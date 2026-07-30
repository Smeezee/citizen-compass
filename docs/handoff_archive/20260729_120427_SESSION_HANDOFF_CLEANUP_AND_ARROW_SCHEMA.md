# CITIZEN COMPASS — SESSION HANDOFF: PROJECT CLEANUP + ARROW HARDPOINT SCHEMA

**Purpose:** compiled record of a full project-inventory-and-cleanup session,
covering duplicate removal, a new hardpoint/component data schema (built and
validated for Arrow), and the relocation of the 4.1GB `sc-ships/` 3D model
library out of `inbox/`. Written 2026-07-29.

---

## 1. Duplicate file cleanup (first pass)

Full project inventory identified 7 files that were confirmed **byte-identical**
(SHA256, not just similar) to a canonical copy elsewhere. All 7 deleted, originals
kept:

| Deleted | Duplicate of |
|---|---|
| `ccpp__20260728175427.py` | `ccpp.py` |
| `CCPP_QUICKSTART.md` (root) | `docs/CCPP_QUICKSTART.md` |
| `docs/CCPP_QUICKSTART__20260728180624.md` | `docs/CCPP_QUICKSTART.md` |
| `docs/ARCHITECTURE_DEEP_REVIEW_1.md` | `docs/ARCHITECTURE_DEEP_REVIEW.md` |
| `docs/ARCHITECTURE_DEEP_REVIEW__20260728180208.md` | `docs/ARCHITECTURE_DEEP_REVIEW.md` |
| `docs/FORMAT_COMPARISON__20260728181456.md` | `docs/FORMAT_COMPARISON.md` |
| `setup_watcher_task.ps1.txt` | *(0 bytes — empty, not a true duplicate)* |

A broader reorg plan (root `SETUP_INSTRUCTIONS.md` staleness, `tests/ships/arrow/`
vs `tests/testing-site/ships/arrow/`, the `data-layer*` flat-naming issue,
`inbox/citizen-compass-testing-ground/`, `inbox/Citizen Compass AI Brain/`) was
drafted but **paused** when priorities shifted to the Arrow hardpoint schema work
below. See "Still open" at the bottom — most of it remains unresolved by design
(explicit user decision, not an oversight).

## 2. Arrow hardpoint/component schema

Built `build_ship_component_schema.py` (new script, reuses
`hardpoint_organizer.categorize_hardpoint()` rather than reimplementing
categorization logic) to split ship data into:
- **Physical/clickable hardpoints** — `hardpoints_weapons.json`,
  `hardpoints_missiles.json`, `hardpoints_turrets.json` (from the Blender-exported
  position file, `tests/testing-site/ships/<slug>/hardpoints.json`)
- **Menu-driven components** — `components.json` (power plant, coolers, shield,
  quantum drive, etc. — from `ship_specs.json`'s `components` array, filtered to
  exclude entries whose type is itself a physical hardpoint category)

Run for Arrow only, output at `data-layer/processed/hardpoints_by_type/arrow/`:
2 weapons, 4 missiles, 1 turret, 14 components.

### Cross-checks and corrections
- Two count discrepancies surfaced between the Blender position file and
  `ship_specs.json`'s components summary (turrets: 1 vs 2; missiles: 4 vs 2).
  Investigated via a **live fetch of api.star-citizen.wiki's raw vehicle API**
  (not a cached/secondhand summary) — resolved:
  - **Missiles: 4 is correct** (matches the live API's port count exactly; the
    "2" was counting rack *models*, not physical ports).
  - **Turrets: our original 1/2 split was mechanically correct**, not the API's
    raw "3 Turret-type ports" figure. Researched Star Citizen's actual mount-type
    mechanics (RSI design-notes comm-links, RSI's own Arrow Q&A) and wrote
    `docs/HARDPOINT_MOUNT_TYPES.md` as a standing reference. Conclusion: the
    live API's `type: Turret` field is a broad internal port-classification that
    also covers ordinary gimbal mounts (evidence: the wiki files an actual
    "Gimbal Mount" item under its "Turret" category). The Arrow mechanically has
    1 true turret (top-mounted ball turret) and 2 gimbal-mounted wing guns —
    matching our original category split.
- **Size correction applied**: the two wing-gun entries in
  `hardpoints_weapons.json` were labeled Size 1; RSI's official spec, the live
  API, and third-party guides all agree they're **Size 3**. Fixed 2026-07-29,
  noted directly in the JSON file's `_corrections` field (local Blender-export
  data was stale).
- **Quick pass on other local hardpoint data**: checked
  `tests/testing-site/ships/cutlass-black/hardpoints.json` against
  `ship_specs.json`. Found but **did not fix** (flagged only, per instruction):
  - Turret size mismatch: local says S3, `ship_specs.json` says the real turret
    is a **Manned Turret, size 5**.
  - Missile data looks like a placeholder: local has 1 generic entry with no
    size; `ship_specs.json` shows 2 distinct rack types totaling 6 missile
    slots across 4 physical mounts.
  - One label typo: `hardpoint_weapon_gun_s3_ls`'s label field is missing its
    size digit ("S  LS" instead of "S3  LS").
  - `constellation-aquila` and `gladius` had no `hardpoints.json` at all to
    check.

## 3. sc-ships/ relocation and distribution

**Backup taken first**: `citizen-compass-backup-20260729/` (sibling folder),
via `robocopy /E /XD venv .cache huggingface`. Confirmed complete — 4.3GB,
1137/1137 files, 0 mismatches, 0 failures — before any of the reorg below.

`inbox/sc-ships/` (245 ship folders, ~4.1GB of `model.glb`/`model.ctm`/
`image.webp` per ship) was invisible to `inbox_watcher.py` — it only scans
top-level *files* in `inbox/`, not subfolders. Moved out entirely:

- **Relocated** `inbox/sc-ships/` → `sc-ships/` (project root), so it's fully
  out of the watcher's scan path.
- **Distributed** into the 4 ships that already had an existing viewer folder
  under `tests/testing-site/ships/` (no new folder structure created, per
  instruction):
  - **Arrow** — replaced a **broken, 0-byte `model.glb`** with the real
    12.5MB model + added `.ctm`/`.webp`. Also deleted 2 stray timestamped
    `hardpoints__*.json` duplicates left over from earlier inbox drops.
  - **Constellation Aquila** — had only `index.html` before; now has a
    complete model set.
  - **Gladius** — same as above, gap filled.
  - **Cutlass Black** — its existing `model.glb` was confirmed **byte-identical**
    (SHA256) to the `sc-ships/` copy, so it was left untouched; only the
    `.ctm`/`.webp` companions (which didn't exist locally before) were added.
    This also incidentally identified a mystery duplicate file flagged earlier
    in the session (`models/_unsorted/model__20260728174803.glb`) as an extra
    copy of this same Cutlass Black model.
- **241 ships with no existing folder** were left untouched in `sc-ships/` at
  its new root-level location, as a reference library for future ship builds —
  per instruction, no new per-ship folders were created for them.

## 4. inbox/ final state

- `Citizen Compass AI Brain/` — **left in place, untouched**. Explicitly
  flagged for future work: expanding into a proper system once dedicated
  server hardware is sorted out. Not part of this session's scope.
- `citizen-compass-testing-ground/` — **left in place, untouched**. Explicitly
  flagged for future work: needs to be brought up to date and expanded into
  the live pre-Netlify preview site. Not part of this session's scope.
- `files more/` — **fully processed and removed**. All 3 contents confirmed
  (SHA256) as exact duplicates of content already living permanently
  elsewhere — nothing new or uncovered found:
  - `FORMAT_COMPARISON.md` → identical to `docs/FORMAT_COMPARISON.md`
  - `SEARCH_COMMAND.ps1` → identical to the copy already in
    `inbox/Citizen Compass AI Brain/`
  - `SEARCH_COMMAND_SIMPLE.ps1` → identical to the copy already in
    `inbox/Citizen Compass AI Brain/`

  All 3 deleted (content fully preserved at its canonical location in both
  cases), empty `files more/` folder removed.

`inbox/` now contains exactly 2 items, both deliberately left in place:
`Citizen Compass AI Brain/` and `citizen-compass-testing-ground/`.

## 5. Still open (not done this session, by explicit decision or pending user input)

- Root `SETUP_INSTRUCTIONS.md` — stale, documents routing rules that don't
  exist in the current `inbox_watcher.py`. Not yet archived/removed.
- `tests/ships/arrow/` — an older, unreferenced duplicate viewer tree
  (superseded by `tests/testing-site/ships/arrow/`, which now also has the
  correct model). Not yet deleted.
- `data-layer*` flat-naming issue (`data-layerrawhardpoints/`,
  `data-layerprocessedhardpoints_by_type/`, `data-layerexports/` vs. the
  nested `data-layer/raw/...` structure the code actually expects) — not
  resolved. `build_ship_component_schema.py` currently reads directly from
  the flat `data-layerrawhardpoints/ship_specs.json` path as a workaround.
- Cutlass Black's real hardpoint data issues (turret size S3 vs actual S5,
  missing missile detail) — flagged, not fixed.
- `Citizen Compass AI Brain/` and `citizen-compass-testing-ground/` — both
  intentionally left in `inbox/`, each with its own stated future-work plan
  (see section 4).
- `models/_unsorted/model.glb` (the general-purpose copy, sha256
  `1c21ac34...`) is now redundant with `tests/testing-site/ships/arrow/model.glb`
  — not cleaned up this session.
