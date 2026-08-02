# UPDATE — Path C auditors work order received, starting

Filed on intake per rule 13, before any work.

## Received

`docs/workorder-path-c-auditors.md`, approved 2026-08-02. Chosen over Path A
(schedule the collectors) and Path B (build Stage 2 first). Commit-and-push
authority for this order's scope only.

## Scoping correction I am taking on board

**Most of this is already built** — `checks/framework.py`,
`checks/file_checks.py` (13 checkers), `checks/db_checks.py` (4),
`checks/network_checks.py` (1 wired), `run_checks.py` with
`--group file|db|network|all`, and the `pipeline_check_results` table. I am not
rebuilding any of it. The job is to make it run, make it trustworthy, and make
it run by itself.

## Order of work

1. **Verify the two findings first**, as instructed — confirm rather than accept.
2. **Part A** — write `checks_flush_fallback.py`. 874 findings from three runs
   have been queued since 2026-07-31 with no path into the table, because the
   script `framework.py`'s own docstring tells you to run was never written.
   Highest-value item in the order.
3. **Part B** — run `--group db` against the real database for the first time.
4. **Part C** — three new auditors: `snapshot_integrity`,
   `cross_source_disagreement`, `uex_join_health`.
5. **Part D** — one scheduled task, confirmed by behaviour to be the only writer.

## Non-negotiables I am holding to

- **Findings only.** No auditor modifies data. ARCHITECTURE_DECISIONS.md §4,
  locked.
- **Rule 12 on every new auditor and on the flush script** — proven against
  known-bad input before being trusted. An auditor whose failure path has never
  executed is decoration.
- **One scheduled task, not two**, confirmed by behaviour. This project has lost
  work twice to duplicate writers on one target.
- **Report what I found, not that I ran.** A zero-defect run gets stated
  explicitly.
- **I will not report this complete on a run that verified nothing.** This is
  the layer whose entire job is catching that mistake.

## Note on the DB password

The order says `DATABASE_URL` is present and the password is being rotated.
Separately, the UEX token pasted into chat earlier today turned out to be
byte-identical to the value already in `.env` — so that rotation had not
happened at the time. If the Postgres password is mid-rotation, Part B may block
on a stale credential; if so I will say so rather than working around it.

Starting with the two verifications.
