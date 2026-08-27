# Update - H7 done: the never-delete guard protects by default now

`app/preservation.py` named sixteen tables and protected those. Everything the
A-G runs built was outside it - 26,657 price rows and 2,195 hardpoint slots,
unguarded, with nothing saying so. It is inverted: protected unless named
ephemeral.

**On the ephemeral list, with a reason each:** the three `pipeline_*` auditor
tables (append-only observation logs, designed to be flushed - that is what
`checks_flush_fallback.py` is for) and `alembic_version` (a pointer to the
current revision, not a record). Plus one prefix, `cc_scratch_`, for harness
throwaways - and the code states plainly that a prefix IS a bypass, closed for
declared tables by the classification checker and not closed for raw-SQL ones.

**Both lists still exist on purpose.** The guard needs only the ephemeral one.
`PRESERVED_TABLES` is the classification, so "protected because somebody
decided" and "protected because nobody looked" are different states. 24
preserved, 4 ephemeral, 0 unclassified.

**You asked me to argue with the inversion.** I found exactly one case where
it broke something, and it was in our own controls: `_verify_never_delete_guard`
asserted "a non-preserved table is NOT blocked" using a temp table called
`scratch_notes`, which passed only because that name was off the old allowlist.
It failed the moment the inversion landed. That is the change working, not a
case against it - the assertion was asking the old question. It now asks the
right one, with a second assertion beside it proving an unclassified table is
refused.

Every importer here upserts; not one deletes rows.

## A finding, reported not fixed

The e2e harness fails at step 7, and it is not H7's doing. Steps 1-6 passed
under the inverted guard with no preservation violation - that is the answer
H7 needed. Step 7's `alembic check` fails with "Detected added table
'ship_registry'": ship_registry is declared in `app/models.py`, deliberately
not in `EXCLUDED_TABLES`, and **no migration creates it** - its DDL comes from
`registry-builder/main.go`. So on a fresh database it never gets created and
the drift check fails. Pre-existing. Whether it gets a migration or joins the
exclusion list is a schema-authority call and not in this order.

Also: `run_e2e_test.py` needs `venv/Scripts` on PATH or the alembic subprocess
raises FileNotFoundError at step 1.
