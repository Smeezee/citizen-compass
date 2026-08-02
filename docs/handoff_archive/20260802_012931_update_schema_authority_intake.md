# UPDATE — closing the alembic drop hazard, and building the control

Filed on intake per rule 13.

## Ruling received

- `ship_registry` -> declare in `app/models.py`, and **retire schema-init's
  creation of it in the same change** so one table has one authority.
- The three `pipeline_*` tables -> `include_object` exclusion that **names them
  explicitly**, with a comment recording that `schema-init/main.go` owns their
  DDL and why.
- **Build the control**: a checker asserting every table is claimed by exactly
  one authority. Claimed by neither = an unregistered table. Claimed by both =
  drift. Either is a finding.
- Record the 22,988 flip in the front-end order.

## One consequence I need to handle carefully

Retiring schema-init's creation of `ship_registry` leaves **nothing** creating
it on a fresh database unless alembic does. So the change is not just "delete
the Go DDL" - it needs a migration that creates the table, written so it is a
no-op where the table already exists.

That means `alembic upgrade head` against the real database, which means
**rule 4: verified backup first.** The last one predates tonight's 3,751 rows.

## Order

1. Read schema-init's DDL and the live table definition, and match the model to
   both exactly - a mismatch produces ALTERs instead of drops, which is quieter
   and still wrong.
2. `include_object` exclusion, naming the three tables.
3. Conditional migration for `ship_registry`.
4. Verified backup.
5. Apply, then confirm `alembic check` is clean.
6. Build the ownership checker, with rule 12 proof: create a table in neither
   place and confirm it is reported. A guard that has never fired is not a
   guard.
7. Record the 22,988 flip.

Not committing without a go-ahead per rule 2.
