# UPDATE — Phase 1 pipeline audit complete, real verification throughout (2026-07-30)

Full pipeline audit requested this session. Every item below was actually run/read, not assumed. Phase 2 (Blender/MCP) starting next; this covers Phase 1 only.

## 1 — Checker framework: real run, one bug found and diagnosed

First run used system Python and silently skipped the db_checks group (missing sqlalchemy). Re-ran with the project's actual venv (`venv/Scripts/python.exe run_checks.py --group all`) for a complete result:

**27 findings: DEFECT=1, WARNING=2, LIMITATION=8, PASS=16** (previous known baseline: 18 findings, 0/2/5/11).

- WARNING count unchanged (2/2) — same two open items as before (see #5 below).
- The 1 new DEFECT (`registry_sync`: ship_registry.json "not valid JSON") is a **false positive** — diagnosed to `checks/db_checks.py:128`, which calls `registry_path.read_text()` without `encoding="utf-8"`. On Windows this falls back to cp1252 and chokes on the "a with macron" character in the real ship name "San'tok.yai". Verified the file parses cleanly as valid JSON (295 entries) when read as UTF-8. Not fixed (out of scope for an audit-only pass) — flagging as a one-line fix candidate.
- +2 new LIMITATION (constellation-aquila / gladius "no hardpoints.json yet") — expected, these are the two ships this session pulled data for (see #3).
- +1 new LIMITATION (`schema_drift`: "alembic not on PATH") — real environment gap, alembic *is* installed in venv/Scripts but wasn't resolved by the checker's subprocess call.
- +5 PASS — all from db_checks now actually running with real DB connectivity: referential_integrity (manufacturer_id, last_verified_patch, confidence, dealer listings) and duplicate_identifier all passed clean against the real 232-ship DB.

## 2 — Postgres: reachable, backed up, migration/import verified

- Confirmed live: PostgreSQL 17.10, 232 ships.
- Backup taken **first**, before anything else: `citizen_compass_backup_20260730.dump` (69,037 bytes, 139 TOC entries, verified non-corrupt via `pg_restore --list`). Correctly gitignored (`*.dump` rule from a prior commit) - confirmed via `git check-ignore`.
- `alembic upgrade head`: no-op, DB was already at head (`219446ebce6a`) both before and after.
- `import_ship_components.py`: ran clean, reported "Created 0, updated 8." Verified directly against the DB: component count unchanged (8) and every `updated_at` timestamp byte-identical before/after. Genuinely zero net change - fully idempotent re-run.

## 3 — Gladius / Constellation Aquila raw data: pulled for real, one major caveat found

Both URLs confirmed correct and pulled directly:
- `data-layer/raw/gladius/gladius_api_raw.json` - HTTP 200, valid JSON, name "Gladius", slug aegs-gladius, 74 ports.
- `data-layer/raw/constellation-aquila/constellation-aquila_api_raw.json` - HTTP 200, valid JSON, name "Constellation Aquila", slug rsi-constellation-aquila, 123 ports.

**Important finding, checked rigorously (not assumed):** the api.star-citizen.wiki API does not expose 3D hardpoint coordinates at all. Checked every port on all three ships including the reference Arrow - 0 of 61 (Arrow), 0 of 74 (Gladius), 0 of 123 (Aquila) ports have a non-null `position` field. Arrow's existing `tests/testing-site/ships/arrow/hardpoints.json` (which does have real x/y/z coordinates) could not have come from this API - it must have been hand-derived some other way, almost certainly from the Blender model directly. This is real, useful context for Phase 2.

## 4 — hardpoint-viewer.js wiring: correctly NOT done, real blocker confirmed

Per #3, there is no spatial data to wire in yet - only port/loadout metadata (names, types, equipped items, sizes). Did not fabricate placeholder coordinates or wire the viewer with fake data. `tests/testing-site/ships/gladius/` and `.../constellation-aquila/` already have model.glb/model.ctm/image.webp/index.html - the only missing piece is a real hardpoints.json, and that requires position data this API doesn't provide.

## 5 — Two standing decisions: still open, not resolved (as instructed)

- **Cutlass Black slug**: confirmed `tests/testing-site/ships/cutlass-black/hardpoints.json` still uses `"ship_slug": "cutlass-black"` (hyphenated). The underscore variant exists only in `_to_delete/cuttlass_black_typo_duplicate_DELETED_5`, itself marked for deletion. No decision made either way this session.
- **Fan-Kit disclaimer**: confirmed `static/index.html` has zero "trademark" matches (still missing); `static/preview.html` has 6 (still present there). Unchanged.

## 6 — Git status

0 commits ahead / 0 behind origin/main - fully in sync, nothing pushed this session. Working tree has 4 untracked items: the 2 new raw JSON pulls, the pre-existing (unrelated, present since before this session) `models/done ships/buccaneer_hardpoints.json`, and `releases/citizen-compass-v0.3.9-2026-07-30.html` (created earlier this session, still uncommitted per your choice).

## 7 — Cross-check: DB / ships-master.json / ship_registry.json

- DB ships: 232. `tests/testing-site/data/ships-master.json`: 232. **Exact match.**
- `data-layer/ship_registry.json`: 295 entries, 278 unique ship names. The 17 "duplicate" name occurrences checked individually - all legitimate (e.g. the two "Carrack" rows have different ship_code/source_slug, tracking distinct source entries under the same display name, not accidental dupes).
- **Real finding, previously invisible**: manually completed the DB-vs-registry name comparison that the checker's own `registry_sync_check` has never actually reached (it's always crashed on the encoding bug in #1 first). Result: **62 of the 232 DB ships have no matching entry in ship_registry.json at all** - includes Freelancer, Prospector, Starfarer, all 6 Aurora variants, all 5 Hull variants, Kraken, Galaxy, Nautilus, and others. Per the checker's own documented severity policy this is a WARNING (registry/DB can legitimately be mid-sync), not a DEFECT - but it's real, substantial (27% of DB ships), and has never been surfaced before now because the check always failed before reaching this comparison.
- 108 registry entries have no DB row - expected per the documented staged-import architecture (registry is intentionally broader than the DB).

## Nothing pushed, nothing destructive beyond the routine backup+no-op-migration in #2. Moving to Phase 2 (Blender/MCP) next.
