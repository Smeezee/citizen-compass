# UPDATE — `schema_drift` fixed: it was minting a new finding every run

This blocked Part D. Fixed and proven. Not yet committed.

## What was wrong, and it is worse than "unstable order"

The C0 commit flagged that `alembic check`'s operations come back in unstable
order. That is true, but it is not the main problem. **The output embeds memory
addresses.**

Every `server_default` renders as:

```
<sqlalchemy.sql.elements.TextClause object at 0x0000017059E56C10>
```

That address is different on every run. I measured it: **4 distinct addresses
across 2 consecutive runs.**

The checker put that raw dump straight into `details`, and `finding_key` hashes
a normalised `details`. So the same unchanged drift hashed to a **new key every
single run.**

**It also defeats `lifecycle.normalise_condition()`, and the reason is subtle.**
The hex normaliser is `\b[0-9a-f]{7,40}\b`. In `0x0000017059E56C10` there is no
word boundary between the `x` and the digits — both are word characters — so it
never matches. The number normaliser fails on the same boundary. A memory
address is indistinguishable from data at the normaliser's level, so **no
outside normaliser can fix this.** It had to be fixed in the checker.

Put that on a schedule and it produces one fresh ghost per run, forever — the
exact failure the lifecycle exists to prevent, delivered on a timer.

## The fix

`summarise_alembic_ops()` in `checks/db_checks.py` reduces the output to a
sorted, de-duplicated list of `op:target`. `details` becomes:

```
alembic check reports 4 drift operation(s): remove_index:ix_pipeline_check_results_check_name,
remove_index:ix_pipeline_check_results_checked_at,
remove_table:pipeline_check_results, remove_table:ship_registry
```

Byte-identical every run, and it says more than the dump did.

The operation-tuple regex carries a negative lookbehind, `(?<![A-Za-z_])\('`,
because `Column('check_name',` has the identical shape to an operation tuple and
would otherwise be parsed as one.

A non-zero exit that parses to **zero** operations now reports **WARNING —
unclassified**, not DEFECT. Failing closed: it will not describe a drift it did
not understand, and it will not echo output it cannot parse.

## Rule 12 — and my first attempt at it was a false pass

**My first verification run reported three identical keys and I nearly took it.**
It was LIMITATION on all three — `alembic` was not on PATH, so the parser never
executed. Three identical keys from a code path that never ran. That is
precisely the silent success rule 12 describes, produced by my own test.

Re-run with `venv/Scripts` on PATH so the result was **DEFECT** and the parser
genuinely ran:

| | run 1 | run 2 | stable? |
|---|---|---|---|
| **old** details | `c34b5634…` | `622a53a2…` | **NO** |
| **new** details | `053fce9c…` | `053fce9c…` | **YES** |

Old and new measured against the *same two* `alembic check` invocations, so the
comparison is like-for-like. The old path is demonstrated broken rather than
assumed broken.

## A finding this produced, and Part D must handle it

**`schema_drift` returns LIMITATION whenever `alembic` is not on PATH** — which
is the default for a non-interactive shell here. A scheduled task that does not
put `venv/Scripts` on PATH will get LIMITATION forever and **the drift will
simply stop being reported**, while the run still looks healthy.

That is a silent success waiting to happen on the schedule I am about to build.
Part D must set PATH explicitly, and `checker_health` (C4) should treat a
checker that has only ever returned LIMITATION as suspect.

## Still open, unchanged, and not mine to fix

The drift itself is real and is the DEFECT Parts A/B reported: `ship_registry`
and `pipeline_check_results` exist in the live DB but not in `app/models.py`, so
`alembic revision --autogenerate` would generate a migration **dropping both** —
295 ship rows and 890 findings. Reported, not fixed. Adding models or an alembic
exclusion is a schema decision outside this order.

## Next

The rest of C0: the `pipeline_findings` table and the 890-row backfill.
