# Update — CC-12 and CC-10 investigated (read-only, no changes made)

Investigation and written proposal only. `app/models.py` was not modified, no
migration was run, and every database query ran inside an explicit
`SET TRANSACTION READ ONLY` (confirmed `transaction_read_only = on`).

Both audit findings are **accurate as described** and still current.

## PART A — CC-12, the natural key

### A1. Actual current state (verified, not assumed)

`app/models.py` and the live database **agree** — no drift.

| table | column | nullable | constraint |
|---|---|:--:|---|
| components | `class_name` | **YES** | `uq_components_class_name` UNIQUE (`class_name`) |
| components | `name` | NO | none |
| components | `component_type_id` | NO | FK + index |
| ships | `name` | NO | **none** |
| ships | `manufacturer_id` | NO | FK + index |

Live DB constraints on these two tables: `components_pkey`,
`uq_components_class_name`, `ships_pkey`. **That is all.** `ships` has no unique
constraint on `(name, manufacturer_id)` — confirmed, the audit is right.

The nullable-unique problem is real: Postgres treats NULLs as distinct, so
`uq_components_class_name` permits unlimited rows with `class_name IS NULL` —
on the field the comment at `app/models.py:206-209` calls "the natural key
importers upsert on."

### A2. Data state — clean

| metric | value |
|---|---:|
| components rows | 8 |
| `class_name IS NULL` | **0** |
| `class_name = ''` | **0** |
| duplicate non-null `class_name` | **0** |
| ships rows | 232 |
| duplicate `(name, manufacturer_id)` | **0** |

### A3. Duplicates to resolve — NONE

Nothing needs merging or deleting. Nothing was merged or deleted.

**This is the cheapest this fix will ever be.** 8 component rows and no
violations: the constraints can be applied today with zero data remediation.
Every row added before this lands raises the cost.

### A4. Proposed fix (NOT applied)

**Becomes NOT NULL:** `components.class_name`.

**Constraints added:**
1. `components.class_name` -> `SET NOT NULL` (makes the existing
   `uq_components_class_name` actually enforce one row per class name)
2. `ships` -> `UniqueConstraint("name", "manufacturer_id", name="uq_ships_name_manufacturer_id")`

**Fallback for an entity with genuinely no natural key.** This is the part that
needs a decision, because "make it NOT NULL" alone would block legitimate
inserts for components whose in-game class name is not yet known — the exact
case the current comment says is expected ("not always known yet").

Proposed: a deterministic synthetic key plus an explicit flag.
- `class_name` = `CC_SYNTH_<component_type_key>_<slugified name>` when the real
  one is unknown
- new column `class_name_is_synthetic BOOLEAN NOT NULL DEFAULT false`

This keeps the column NOT NULL and unique while making synthetic keys
queryable and replaceable — an importer that later learns the real class name
updates the row and clears the flag. It never silently presents a made-up
identifier as real, which matters under CLAUDE.md rule 11.

**Migration order:**
1. Verify zero NULL/blank/duplicate `class_name` (currently true — re-verify at
   migration time, do not assume)
2. Add `class_name_is_synthetic` with a default
3. Backfill synthetic keys for any NULL `class_name` (currently zero rows)
4. `ALTER COLUMN class_name SET NOT NULL`
5. Add `uq_ships_name_manufacturer_id`
6. Verify both constraints exist

**What would break if run against current data:** nothing at the schema level —
zero violations exist, so steps 4 and 5 succeed. The real breakage is
**behavioural, after the migration**: any importer that currently inserts a
component without a `class_name` starts raising `NotNullViolation`. Every
importer write path must be checked for that before step 4 ships. That is the
work item, not the ALTER itself.

## PART B — CC-10, provenance on detail tables

### B1. Confirmed

All five — `WeaponDetail`, `MissileDetail`, `MissileRackDetail`,
`GimbalMountDetail`, `TurretDetail` — subclass bare `Base`. Confirmed in the
live database too: **all five tables have zero provenance columns.** No
`confidence`, no `verification_source`, no `last_verified_patch`, no
`created_at`/`updated_at`.

Current row counts: weapon 2, missile 2, missile_rack 2, gimbal_mount 1,
turret 1.

### B2. What VerifiableMixin provides

`app/models.py:22-42`:
- `id` — **`primary_key=True`**
- `created_at`, `updated_at` (`server_default=func.now()`, `onupdate`)
- `verification_source` — `String(255)`, nullable
- `confidence` — `String(20)`, NOT NULL, `server_default="unverified"`
- `confidence_check(table_name)` — a static method returning
  `CheckConstraint("confidence IN (...)", name=f"ck_{table}_confidence_valid")`,
  which each table must add to its own `__table_args__` (it is not automatic)

**`last_verified_patch` is NOT part of the mixin.** Every table that has it
declares its own `ForeignKey("patches.id")` column. Any fix for CC-10 must add
that column per class explicitly — inheriting the mixin alone will not supply
the field that the described failure mode actually turns on.

### B3. The mixin does NOT apply cleanly — demonstrated

Tested in isolation (separate `Base`, in-memory SQLite, `app/models.py`
untouched). Naively adding `VerifiableMixin` to a detail table produces:

```
primary key columns: ['component_id', 'id']
is composite PK?     True
all columns:         ['component_id', 'id', 'created_at', 'updated_at',
                      'verification_source', 'confidence']
create_all():        SUCCEEDED (no exception)
```

The mixin's `id` is added **alongside** `component_id`, producing a composite
primary key. The detail table stops being a true 1:1 extension of `components`.

**Proposed instead:** split the mixin rather than reuse it as-is.

- Extract a `ProvenanceMixin` with `created_at`, `updated_at`,
  `verification_source`, `confidence` and the `confidence_check` helper — but
  **no `id`**.
- `VerifiableMixin` becomes `ProvenanceMixin` + `id`, so every existing table is
  unchanged.
- The five detail classes take `ProvenanceMixin`, keep `component_id` as sole
  PK, and each adds its own `last_verified_patch` FK and
  `ProvenanceMixin.confidence_check("<table>")` in `__table_args__`.

This is additive for the nine existing VerifiableMixin tables — none of their
schemas change.

### B4. Does it break create_all() or any checker?

**`Base.metadata.create_all()`: NO — and that is the concerning part.** The
naive version does not raise. It silently produces a composite PK. This defect
would ship without an error, which is why it needs deciding deliberately rather
than being discovered later.

**Checkers: NO.** `checks/db_checks.py` imports only `CONFIDENCE_LEVELS`,
`Dealer`, `Manufacturer`, `Ship`, `ShipDealerListing`. It never touches the five
detail tables, so nothing there breaks either way.

**Routers: not broken, but worth noting.** `app/routers/weapons.py`,
`missiles.py` and `turrets.py` join the detail tables and filter on their
columns. Joins are unaffected by an extra PK column, but the
`uselist=False, cascade="all, delete-orphan"` 1:1 relationships on `Component`
assume one detail row per component — a composite PK removes the guarantee that
enforces it. Under the proposed `ProvenanceMixin` split, none of this changes.

**One consequence to decide separately:** adding `confidence` NOT NULL with
`server_default="unverified"` means all 8 existing detail rows become
`unverified` on migration. That is the honest default and matches rule 11, but
it will visibly change what the front end reports for those rows.

## Status

Nothing implemented. `app/models.py` unchanged. No migration run, no writes, no
schema changes. Both parts are proposals awaiting a decision.
