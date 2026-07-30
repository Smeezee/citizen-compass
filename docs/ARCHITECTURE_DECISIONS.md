# Citizen Compass — Architecture Decisions (Phase 2)

This document records binding architecture decisions for Phase 2 and why they were made. It exists so any AI or developer picking up this project — including a different AI tool Sleven may be consulting in parallel — can understand the reasoning without re-deriving it. Do not deviate from decisions marked LOCKED without discussing it with Sleven first (per `docs/PHASE2_VISION.md`'s "architecture before features" and this project's AI RULES: "if you make an important design decision, document why").

Companion to `docs/PHASE2_VISION.md` (the long-term vision) — this doc captures the concrete decisions made to implement that vision.

---

## Standing directive (2026-07-30, governs every future recommendation)

- Design for where the project will be in 5+ years, not just current need.
- AI is a tool, not the goal — architecture must be easy for any AI or a less-experienced developer to understand, maintain, and extend.
- Prefer systems that reduce manual work, duplicated code, and opportunities for human error.
- Every major system should be modular and reusable.
- Avoid anything that paints the project into a corner or forces a large rewrite later.
- Recommendations must present multiple options with long-term tradeoffs, recommend the strongest long-term foundation (not the easiest), and actively challenge Sleven's assumptions when a better engineering approach exists.

---

## 1. Database schema — LOCKED

**Decision:** Hybrid schema using Class Table Inheritance (a shared base table holding common fields + separate 1:1 typed detail tables per category), NOT flat table-per-type and NOT pure JSONB-attributes.

**Two separate domains, not one:**
- **Ship Items** domain: ship-mountable components (weapons, shields, coolers, power plants, quantum drives, missiles) share one `components` base table (common fields: manufacturer, size, grade, price, plus the existing `VerifiableMixin` columns) with typed detail tables (`weapon_details`, `cooler_details`, etc.) joined 1:1 by PK. Ship **paints** live in the same Ship Items domain (same API section, same data-pipeline folder) but as their OWN sibling table (`ship_paints`), not the same physical table as mountable components.
- **Character Items** domain: armor, clothing, undersuits, helmets, etc. get their own separate base+detail table family entirely. Different attachment model (a character, not a ship hardpoint), no relation to Ship Items at the schema level.

**Why paints sit next to components but not inside the same table:** a ship hardpoint slot must be able to reference "whatever occupies this mount." If paints shared the exact same table as mountable components, nothing at the database level would stop a hardpoint slot from referencing a paint instead of a weapon — they'd look identical to a foreign key. Keeping paints in a sibling table removes that failure mode at zero cost to how unified the area feels to a user or an importer.

**Supporting decisions:**
- All hardpoint/loadout mount references point at the shared `components` base table's primary key — never at a type-specific detail table. This is what makes the Loadout System (Phase 2, later) tractable without a rewrite.
- `component_type` (and similarly `slot_size`/mount-size labels like S1-S5, which already appear as strings in existing ship data) should be lookup tables, not free-text or hardcoded enums. Adding a new category becomes a data insert, not a schema migration or code change.
- Paints do not need the Class Table Inheritance split themselves — their shape is uniform enough (name, manufacturer, compatible ships, release version, availability, preview, color palette, finish) for one well-normalized table plus a join table for compatible ships.

**Rejected alternatives:** flat table-per-component-type (too much duplicated structure across many tables); single table + JSONB attributes for everything (loses indexed/typed columns the Loadout System needs for compatibility queries).

---

## 2. Generic Data Pipeline — LOCKED (staged)

**Decision:** Do not build the fully generic importer yet. Build 2-3 real entity-type importers first (e.g. the next 2-3 Ship Item categories), learn the actual common patterns from real data, then generalize.

**But lock a minimal contract now, before those first importers are written**, so generalizing later is mechanical rather than a rewrite of what already exists:
- Every importer upserts on a defined natural key (matching the existing pattern already used in `seed.py`/`registry-builder`).
- Every importer stamps `verification_source` / `confidence` / `last_verified_patch` consistently, matching `VerifiableMixin`.
- Every importer logs through `pkg/pipelinelog`, matching the existing tooling.

**Data-layer folder reconciliation (rolled into this decision):** the existing flat vs. nested `data-layer*` naming mess (open caveat since before this session) gets resolved as part of this work, using a folder structure organized by domain and by data direction:
- `data-layer/specs/ship-items/...` and `data-layer/specs/character-items/...` — human-authored/community-sourced *input* specs (what `seed.py`'s hardcoded `SHIPS` list should become).
- `data-layer/processed/...` — intermediate pipeline output (already exists, keep).
- `data-layer/exports/...` — generated output derived FROM Postgres (e.g. `ship_registry.json`'s pattern), never hand-edited.

This gives any importer, watcher, or future AI session one predictable place to look for "ship stuff" vs. "character stuff," and one predictable distinction between editable input and generated output.

---

## 3. API Expansion — LOCKED

**Decision:**
- Generic CRUD/list router factory for simple list+filter+detail entities (the Ship Items and Character Items encyclopedia endpoints as they're added).
- Custom hand-written routers kept only where logic is genuinely bespoke — `ships` already has multi-table price aggregation (dealer listings + pledge links) and should stay custom.
- Response envelope and pagination standard locked now, before more endpoints are added — including retrofitting the existing `/api/v1/ships` endpoint, so nothing already live has to change format later.
- New endpoints organized under the same Ship Items / Character Items domain split as the schema and data-layer.

---

## 4. Automated Validation — LOCKED

**Decision:** Both layers, not one:
- Database constraints (FKs, unique constraints, CHECKs) catch hard integrity issues for free — already partly true in the existing schema.
- A pluggable auditor (many small independent checkers: duplicate detection, missing-field detection, broken-reference detection) writes findings to the already-built `pipeline_check_results` table.
- Findings-only — validation tools never automatically modify data. Matches the already-decided supervisor pattern (periodic review of the results table, flag only).

---

## 5. Viewer Generator — RECOMMENDED (pending final sign-off)

**Decision:** Hybrid — static per-ship shell pages (for SEO and shareable direct links, e.g. social/Discord previews) that fetch live data client-side from the API for the actual interactive 3D content. Not a single fully dynamic viewer page, and not fully pre-baked static content — this is a public reference site whose value is discoverability, so per-object pages matter (`docs/PHASE2_VISION.md` already calls for "each object should become an interactive page").

## 6. Interactive 3D Viewer — RECOMMENDED (pending final sign-off)

**Decision:** three.js (or babylon.js) directly, not the `<model-viewer>` web component. The existing Phase 2 wishlist (toggle doors/gear/interior visibility, per-hardpoint highlighting, component swap previews) requires real scene-graph access that `<model-viewer>` doesn't expose. Starting on `<model-viewer>` as an MVP and swapping later would be exactly the kind of throwaway rework this project's standing directive says to avoid.

## 7. 3D Pipeline — RECOMMENDED (pending final sign-off)

**Decision:** Manual-but-consistent convention for now (`models/<ship-slug>/model.glb` + `hardpoints.json` + `metadata.json`), automate the intake/optimization step later once enough ships are in the pipeline to justify the tooling investment.

---

## Future projects — folded into existing plans

`documentation_expansion`, `architecture_history`, `engineering_decisions`, and `ai_coordination` (from the Phase 2 discussion) are not separate new systems — they fold into the already-queued "Citizen Compass AI Brain" knowledge-base project (which already has `03 architecturs` and `07 decisions` folder slots reserved for exactly this).

---

## Still open / not yet decided

- **Component Database (Priority 8) data sourcing** — where canonical weapon/shield/cooler/etc. specs actually come from (community data-mining sources vs. manual entry, same as ships today). Not a schema question — a content-sourcing question.
- **Loadout System (Priority 9) rule placement** — compatibility rules in application code vs. a compatibility table in the database. Deliberately deferred until Priority 8 (component data) actually exists to design against.
