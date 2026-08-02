# UPDATE — alembic drop hazard CLOSED, and the class closed with it

All four items done. Uncommitted pending a go-ahead (rule 2).

## A correction to the ruling's premise, found before acting on it

The ruling said to retire **schema-init's** creation of `ship_registry`.
**schema-init never created it.** It creates only the three `pipeline_*` tables.

`ship_registry` is created by **`registry-builder/main.go`** (`ensureSchema()`,
line 331). So there were **three** schema authorities, not two — which is itself
the argument for building the control rather than fixing the instance.

## 1. `ship_registry` declared — and it matches exactly

Added to `app/models.py`, mirroring `registry-builder`'s DDL column for column:
`ship_code` varchar(20) unique, `manufacturer_code` varchar(10),
`manufacturer_name` varchar(150), `ship_name` varchar(150), `source_slug`
varchar(150) unique, `folder_slug` varchar(150) nullable, `created_at` timestamp
default now().

**The match was verified, not assumed.** After declaring it, `alembic check`
dropped `remove_table:ship_registry` and proposed **no ALTERs in its place** —
which was the sharper half of the concern. A near-miss model would have been
quieter and equally wrong.

Deliberately not a `VerifiableMixin` table: it is a generated cross-index
rebuilt from source, not community-sourced data with its own provenance story.

## 2. The three `pipeline_*` tables excluded, by name

`alembic/env.py` gains `EXCLUDED_TABLES` and an `include_object` hook, wired
into **both** `configure()` calls (offline and online — one would have been a
silent half-fix).

Held to the conditions:

- **Named explicitly.** No pattern match. A `pipeline_*` prefix rule would
  silently adopt the next table someone adds, which is precisely the failure
  being closed.
- **Commented** with who owns the DDL (`schema-init/main.go`) and why:
  subsystem telemetry, written only by `findings_store.py` and `framework.py`,
  read by nothing in `app/`, schema moving with the checker layer.
- Records that this is the **one-writer-per-artifact** rule applied to schema —
  two authorities over one table being the same defect as two watchers on one
  handoff file.
- Notes explicitly that `ship_registry` is *not* in the list, and why.

**Result: `alembic check` now reports "No new upgrade operations detected."**
The hazard is closed — autogenerate would emit nothing.

## 3. The control — `checks/schema_checks.py`

`schema_ownership`: every live table must be claimed by **exactly one**
authority.

- claimed by **neither** -> DEFECT (an unregistered table; autogenerate will
  propose dropping it and the proposal will look ordinary)
- claimed by **both** -> DEFECT (ambiguous ownership)
- named but absent -> WARNING (a boundary pointing at nothing)
- `alembic_version` handled as legitimately neither

It parses `EXCLUDED_TABLES` from source rather than importing `env.py`, because
importing it runs alembic's configuration machinery and needs a live
connection — a checker that requires the thing it checks to be healthy is not
much of a checker.

### Rule 12 — the guard was made to fire

| case | result |
|---|---|
| table claimed by **neither** | **DEFECT, names the table** |
| table claimed by **both** | **DEFECT, "BOTH"** |
| declared table | not flagged |
| excluded table | not flagged as unclaimed |
| offenders removed | **PASS** |
| no session | **LIMITATION**, never a false PASS |

`env.py` was tampered with to force the double-claim case and **restored
byte-identical**, asserted.

**The proof caught a design flaw in my own checker.** PASS was keyed on *no
findings at all*, so a stale-exclusion WARNING suppressed it — meaning a run
that verified the invariant would look identical to one that never checked.
That is the exact failure this layer exists to catch, in the layer itself. PASS
is now keyed on the absence of DEFECTs.

Registered in `db_checks.py`. Live run against the real database:

```
14 findings: DEFECT=0  WARNING=3  LIMITATION=0  PASS=11
[schema_ownership] all 19 tables claimed by exactly one authority
                   (15 declared in models.py, 3 externally owned, 1 alembic-internal)
```

**DEFECT count is now 0** — the schema_drift DEFECT is gone.

## 4. The 22,988 flip recorded

Written into `docs/order-front-end-build.md` beside the ruling, with both
numbers, why 21,849 is real, why the non-recursive glob produced "items/ is
empty", and the note that the ruling rests on the zero-runtime-dependency
reason precisely because a decision resting on the file count would have
flipped on a definition.

## One thing NOT done, and it is a judgement call

**`registry-builder/main.go` still contains `CREATE TABLE IF NOT EXISTS
ship_registry`.** So `ship_registry` currently has two creators: alembic (via
the model) and registry-builder.

I did not retire it, for a reason worth stating: **no alembic migration creates
`ship_registry`.** The model matches the existing table, so autogenerate
proposes nothing — correct for this database, but it means a **fresh** database
would never get the table if registry-builder stopped creating it. Retiring the
Go DDL therefore needs a migration that creates it, written as a no-op where it
already exists, applied under a fresh verified backup.

That is a real change to a tool's bootstrap behaviour, on a premise that turned
out to be different from the ruling's. Flagging rather than doing it.

**The new checker does not currently catch this**, because it compares against
`models.py` and `EXCLUDED_TABLES`, not against Go source. Detecting "two things
create this table" is a different check — worth having, not built.

## Uncommitted

`app/models.py`, `alembic/env.py`, `checks/schema_checks.py`,
`checks/_verify_schema_checks.py`, `checks/db_checks.py`,
`docs/order-front-end-build.md`. No commit go-ahead was given for this change.
