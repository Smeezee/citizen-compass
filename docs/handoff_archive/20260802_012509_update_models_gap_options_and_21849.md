# UPDATE — the alembic drop hazard: options and consequences. Plus 21,849 solved.

Reporting, not choosing, as instructed.

## THE HAZARD, measured

`alembic check` proposes **10 operations — 4 table drops and 6 index drops**:

```
remove_table:pipeline_check_results     remove_index:ix_pipeline_check_results_check_name
remove_table:pipeline_check_runs        remove_index:ix_pipeline_check_results_checked_at
remove_table:pipeline_findings          remove_index:ix_pipeline_check_runs_started_at
remove_table:ship_registry              remove_index:ix_pipeline_findings_check_name
                                        remove_index:ix_pipeline_findings_last_seen
                                        remove_index:ix_pipeline_findings_status
```

**3,751 rows at risk:** `pipeline_check_results` 3,057, `pipeline_findings` 383,
`ship_registry` 295, `pipeline_check_runs` 16.

Confirmed: **zero** occurrences of any of the four in `app/models.py`.

**Root cause is two schema authorities.** `schema-init/main.go` creates
`pipeline_check_results`, `pipeline_findings` and `pipeline_check_runs` with
`CREATE TABLE IF NOT EXISTS`. Alembic has never heard of any of them, so
autogenerate reads them as tables that should not exist. `ship_registry` is in
the same position.

The danger is specifically `alembic revision --autogenerate`. Its output looks
like ordinary work — a migration file full of plausible operations — and nothing
in it announces that it is about to drop a night's findings.

## OPTION A — declare the models in `app/models.py`

**Consequence:** autogenerate stops proposing the drops. Alembic becomes the
single authority.

**Cost, and it is not zero:** the models must match `schema-init`'s DDL
*exactly* — column types, nullability, server defaults, index names. Any
mismatch and autogenerate proposes ALTERs instead of drops, which is quieter but
still wrong. And `schema-init/main.go` would then be creating tables alembic
also manages: harmless while it stays `IF NOT EXISTS`, but two things creating
one table is the condition that produced this hazard in the first place. Closing
it properly means retiring schema-init's table creation, which is a second
change.

## OPTION B — exclude them via `include_object` in `alembic/env.py`

**Consequence:** autogenerate ignores those tables. No drops proposed.

**Cost:** they stay outside alembic permanently, so every future change to them
is manual. It silences the symptom while keeping two authorities.

**But it is not purely a workaround, and this is the part worth weighing:**
`include_object` exists precisely to say "these objects are owned elsewhere."
For the three `pipeline_*` tables that is arguably *true* — they are the checker
subsystem's operational telemetry, not application domain models, and keeping
subsystem tables out of the app's ORM is defensible separation rather than
evasion.

## What I find, since you asked

**The two groups are not the same case, and I would not treat them the same.**

- **`ship_registry` is domain data** — 295 ships, the same registry
  `registry_sync` compares the database against. That belongs in `models.py`.
  Option A.
- **The three `pipeline_*` tables are subsystem telemetry.** They are written
  only by `checks/findings_store.py` and `framework.py`, read by nothing in
  `app/`, and their schema moves with the checker layer rather than the
  application. Option B is honest for these *if* the exclusion is explicit and
  commented — naming them, saying schema-init owns them, and saying why.

Your read was that declaring is correct and excluding is a workaround. I agree
for `ship_registry`. For the `pipeline_*` tables I think it is closer to a
genuine ownership boundary than a dodge — but that is a judgement about where
the boundary *should* sit, which is yours.

**Either way the hazard must close before anything else touches alembic.** A
mixed answer still closes it: all four stop appearing in autogenerate output.

**One thing neither option gives you:** a control. Both rely on the drift being
absent. Neither stops someone applying a hand-written migration that drops a
table. If that matters, it is a separate ask.

## 21,849 — SOLVED, and it corrects both the order and the hypothesis

It is the **file count of `items/` in the scunpacked-data (source 1) snapshot.**

| snapshot | `items/` files |
|---|---:|
| `20260731T041451Z` (superseded) | **21,849** |
| `20260801T204744Z` (current) | **21,849** |

**Both are populated.** The order's "the snapshot's `items/` directory is empty"
is wrong, and the hypothesis that the number came from the superseded snapshot
*because* the current one is empty is wrong too — they are identical, which is
expected, since both snapshots are the same upstream commit `4764726`. The files
are per-item JSON (`3_seat_bench_constellation.json`,
`987_hat_01_01_01.json`, …).

So C2 conflated **source 1's game-file item count (21,849)** with **UEX's priced
item records (7,728)**. Two different things: everything in the game files
versus only what UEX has a price for.

**This is worth carrying into the backend decision even though it is already
ruled.** If "a page per item" ever means source 1's game items rather than UEX's
priced ones, the arithmetic is **21,849 + 823 + 316 = 22,988 — over the 20,000
cap.** The static ruling holds regardless, and for the stronger reason, but the
file-count argument flips depending on which "items" is meant. Recorded so the
next person to reach for it has both numbers.

## Corrections to my own stale context

`schema_drift` **was already fixed** at 20:23 and I should have read
`20260801_202307_update_schema_drift_stable_key.md` before listing it as open.
The archive entry is also sharper than my diagnosis: the real culprit was
**memory addresses** in `server_default` renders
(`<TextClause object at 0x0000017059E56C10>`, 4 distinct across 2 runs), not
merely unstable ordering — and that is why my hex normaliser missed them.

I have not touched `findings_store.py`, `source_checks.py` or
`pipeline_findings`. I read enough to answer this question and nothing more.

## Committed

`8f46e69` — `find.src.html` added to `build_deploy.py` PAGES, per the go-ahead.
