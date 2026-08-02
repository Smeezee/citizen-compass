# UPDATE — C0 lifecycle: identity and transitions built and proven. Schema and backfill NOT done.

Partial C0. What is done is proven; what is not is named. Stopping here rather
than half-landing a schema change.

## Done — `checks/lifecycle.py`

**Identity.** `finding_key` = sha256 of `check_name` + `subject` + a
**normalised** condition. Normalisation strips what varies between runs while
the condition stays the same: ISO timestamps, bare dates, Windows and POSIX
paths, hex ids and UUIDs, and drifting counts.

**Transitions**, with the load-bearing rule encoded rather than remembered:

| previous | seen this run? | its checker ran cleanly? | result |
|---|---|---|---|
| any | yes | — | OPEN (ACKNOWLEDGED stays acknowledged) |
| OPEN | no | **yes** | **CLOSED** |
| OPEN | no | **no** | **UNKNOWN** |
| CLOSED/UNKNOWN | yes | — | reopens, clearing acknowledgement |

**A finding is CLOSED only by a run that looked for it and did not find it.**
Nothing closes by human, session, or inference.

## Where the state lives, and why — the call the addendum asked me to make

**A companion table, `pipeline_findings`, not extra columns on
`pipeline_check_results`.**

`pipeline_check_results` is an append-only *observation* log — one row per
thing-a-run-saw. That history is not redundant: it is precisely what made the
staleness diagnosis possible, by letting finding timestamps be compared against
commit times. Lifecycle state is a different thing — one row per condition,
describing what is true *now*. Collapsing them would destroy the observation
history to gain a status column.

## Rule 12 — 22 assertions, all passing

`checks/_verify_lifecycle.py`. The critical case is tested directly: **with no
checker having run, nothing may CLOSE** — every previously-open finding goes to
UNKNOWN. Also proven: a relative and an absolute path for the same condition
produce the same key; a count drifting by one does not create a new finding;
different subject, different checker, and genuinely different conditions all
produce different keys; a reappearing CLOSED or UNKNOWN finding reopens; and the
mass-close alarm fires at 40-of-50 but not 2-of-50.

**The proof caught a real bug in my own normaliser.** The Windows path pattern
required a drive letter, so `sc-ships\85X\model.glb` and
`C:\...\sc-ships\85X\model.glb` were *different* findings — reproducing the
exact near-duplicate problem this module exists to stop. Fixed, then re-proven.

## Measured on the real 890 rows

| | |
|---|---:|
| rows in `pipeline_check_results` | 890 |
| **distinct findings after collapse** | **274** |
| collapse ratio | **3.2x** |
| DEFECT rows -> distinct DEFECT findings | **35 -> 14** |

Distinct by result: PASS 247, DEFECT 14, LIMITATION 8, WARNING 5.

The 11 model subjects collapse correctly, each seen 3x (`.cache` 2x).

## FINDING — `schema_drift` would multiply ghosts on a timer

Two `schema_drift` DEFECTs produced **different** finding keys despite being the
same condition. Cause: `alembic check`'s output lists drift operations in
**unstable order** — one run leads with `remove_index`, the other with
`remove_table` — and the checker puts that raw dump straight into `details`.

**Consequence if Part D schedules this as-is: every single run creates a brand
new `schema_drift` finding.** That is precisely the ghost-multiplication the
addendum exists to prevent, and no amount of normalisation fixes it, because a
normaliser cannot reorder arbitrary text.

**The fix belongs in the checker, not the normaliser:** `schema_drift` should
emit a stable, sorted summary — the sorted set of `(operation, object_name)`
pairs — instead of alembic's raw dump. That is a change to an existing checker
and I have not made it. **It should land before Part D schedules anything.**

Two further notes on that finding, unchanged from Part B: the drift itself is
real, and it is a latent data-loss risk — `alembic check` proposes
`remove_table` for `ship_registry` (295 rows) and `pipeline_check_results` (890
rows), because both exist in the database and neither is in `app/models.py`.

## NOT done

- **The `pipeline_findings` table.** Needs a model plus an alembic migration,
  and therefore a fresh verified backup first (rule 4) — the last one predates
  today's 890-row load.
- **Backfilling the 890 rows** as UNKNOWN, then one full run to decide what is
  genuinely open. The collapse number above is computed read-only; nothing has
  been written.
- **C1-C3** (`snapshot_integrity`, `cross_source_disagreement`,
  `uex_join_health`), **C4** (`checker_health`), the **standing rule**
  (CLAUDE.md hard rule + `missing_encoding` checker), and **Part D**.

**Path C is not complete.** What exists is the identity and transition logic,
proven, plus a measured answer to "how many of the 890 are actually distinct":
**274, of which 14 are DEFECTs.** How many are genuinely *open* is not yet
known, because that requires the lifecycle-aware run that the table does not yet
exist to support.
