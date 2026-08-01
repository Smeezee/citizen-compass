# WORK ORDER — CC-12 and CC-10 schema fixes

**Sleven gave explicit approval on 2026-08-01.** This is the "explicit yes" these two have been waiting on. It covers commit and push for this scope only.

**Run this AFTER source 1 re-acquisition (Task 2) completes.** Do not interleave.

---

## Approval covers, specifically

1. **CC-12** — make `components.class_name` NOT NULL, and add a unique constraint on `ships(name, manufacturer_id)`.
2. **CC-10** — add provenance columns to the five detail tables.
3. **The visible consequence, accepted in advance:** `confidence` NOT NULL defaulting to `unverified` flips all 8 existing detail rows to "unverified" and that will show on the site. Sleven's call, made knowingly. Those rows genuinely are unverified and the site currently implies otherwise. Do not soften this by defaulting to something friendlier — that reintroduces the exact false confidence CC-10 exists to remove.

---

## Measured state (read-only, 2026-08-01)

| metric | value |
|---|---|
| `components` rows | 8 |
| `class_name` NULL | 0 |
| `class_name` blank | 0 |
| duplicate `class_name` | 0 |
| `ships` rows | 232 |
| duplicate `(name, manufacturer_id)` | 0 |

**Both constraints would apply today with zero data remediation.** This is a schema change against a nearly-empty table, not a data migration.

**Re-measure before you migrate.** Those figures are from 2026-08-01 and source 1 work has happened since. If any count is non-zero now, stop and report — do not clean data to make a constraint fit without saying so first.

---

## CC-12

`components.class_name` is nullable while sitting under a UniqueConstraint. Postgres permits unlimited NULLs, so the constraint allows unlimited duplicate rows on the field a comment three lines above calls "the natural key importers upsert on." `ships` has no unique on `(name, manufacturer_id)` at all.

Consequence: **nothing in the pipeline is idempotent.** Run an importer twice, get two rows. Every importer written before this fix inherits the flaw, which is why this blocks Stage 2 rather than merely annoying it.

- `components.class_name` → NOT NULL, keep the existing UniqueConstraint.
- `ships` → add a unique constraint on `(name, manufacturer_id)`.
- If a natural-key fallback is needed where `class_name` is genuinely absent upstream, define it explicitly in the migration and document it. Do not let NULL be the fallback.

## CC-10

`WeaponDetail`, `MissileDetail`, `MissileRackDetail`, `GimbalMountDetail` and `TurretDetail` subclass bare `Base` — no confidence, no verification source, no `last_verified_patch`, no timestamps. These are exactly the tables that receive promoted stats, so verification performed on them is lost the moment it is written.

**`VerifiableMixin` does not apply cleanly and this was tested, not assumed:** its `id` lands alongside `component_id`, producing a composite primary key `['component_id', 'id']`, and `create_all()` succeeds silently rather than raising. That silent success is itself a rule 12 instance — `db_checks.py` never touches these tables, so nothing catches it.

**Fix:** split out a `ProvenanceMixin` containing everything in `VerifiableMixin` except `id`. Additive — changes no existing table, leaves `VerifiableMixin` alone for whatever already uses it. Apply `ProvenanceMixin` to the five detail tables.

---

## Required sequence

Hard rules 3, 4, 5 and 12 all apply here. None is optional.

1. **File an `inbox/` update that you received this work order and are starting** — hard rule 13.
2. **Take a verified backup first** (rule 4). Verified means restore-tested or hash-checked, not "the command exited 0."
3. **Re-measure** the six counts above against the live database, read-only. Any non-zero → stop and report.
4. **Write the alembic migration.** Include a working downgrade; do not leave it as a stub.
5. **Dry run first** (rule 5) — against a throwaway database via the guarded harness in `run_e2e_test.py`, never against production. That harness refuses hosted/managed servers and an unset `DATABASE_URL`; do not bypass it.
6. **Prove the new constraints actually bite** (rule 12). A constraint that has never rejected anything is an untested constraint. Explicitly attempt, and confirm each fails:
   - inserting a second `components` row with the same `class_name`
   - inserting a `components` row with NULL `class_name`
   - inserting a second `ships` row with the same `(name, manufacturer_id)`
   Record these three attempts and their rejections. If any *succeeds*, the migration did not do what it claims — stop.
7. **Confirm the composite-PK problem is gone** — assert each of the five detail tables has a single-column primary key after the change. That was the specific trap; test for it directly.
8. Apply to the real database only after all of the above pass.
9. **Verify after:** row counts unchanged (8 components, 232 ships), all five detail tables carry the new columns, all 8 detail rows read `unverified`.
10. **File an `inbox/` update** with what changed, the three rejection tests and their results, and the before/after counts.
11. Commit and push.

---

## Boundaries

- Nothing outside CC-12 and CC-10. If you find a third defect, write it to `inbox/` and leave it.
- Do not touch the live site or anything under `testing/` except `_layer.html` and `build.py`.
- Do not "fix" the 254-vs-232 site/database ship gap. It is a known, deliberately deferred item and is not in scope.
- No data is deleted or rewritten to make a constraint fit. If data blocks a constraint, that is a finding to report, not an obstacle to clear.
- If the backup cannot be verified, stop before step 4. An unverified backup is not a backup.

---

## Why this matters more than its size suggests

This is small now — 8 rows and 232 rows — and gets expensive with every row and every importer added. Stage 2 is the thing that will add both. Landing it first means the validation work Sleven wants to build next has a floor that can dedupe and can record its own provenance. Landing it after means rewriting every importer built in between.
