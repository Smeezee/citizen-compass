# Update — absence pass / lifecycle columns: intake (2026-08-08)

Filed on intake per rule 13, before any work.
Order: "the guard stops deletion. Now stop the lie." (C1, for Code, 2026-08-08).

**Holoviewer is PAUSED at survey stage**, not abandoned — data located and
verified (316 ships, 275 with `PilotDps`, sealed snapshot `20260801T204744Z`),
nothing written. `update-holoviewer-intake-20260808.md` stands; this order
supersedes it for now.

## Why this is the right inversion

The guard (`77623fa`) stops the row disappearing. C3's point is that stopping
the loss is not the same as telling the truth: because nothing deletes AND
nothing marks absence, a removed ship survives still flagged purchasable, still
stamped `last_verified_patch = 4.9`, and indistinguishable from one that still
exists.

Losing a fact is recoverable from a snapshot. **Publishing "you can buy this"
about a ship CIG removed is not** — and it lands on the page a newcomer trusts
most. Agreed, and it changes the priority.

## Hard rules that bind this one

This is a **schema migration against the real database**, so:

- **Rule 4** — a verified backup before the migration, and I confirm it
  reported success rather than assuming it ran.
- **Rule 3** — forward-only `alembic upgrade head`. No downgrade, no
  destructive path outside the guarded harness.
- **Rule 12** — the acceptance list is five negative controls, and item 2 is
  the one that matters: break the absence pass and confirm the row stays
  `live`. Its failure shape is *a row that looks perfectly fine*.

## Order of work

1. Survey: current `Ship` schema, the liveries/paints data, alembic state.
2. **Backup, verified**, before any migration.
3. Migration: 6 lifecycle columns, `status` and `evidence_tier` **indexed**.
4. Absence pass **inside the import transaction** — an absence pass that can be
   skipped is one an interrupted import silently omits, and that looks exactly
   like success.
5. Backfill `first_seen_patch`/`last_seen_patch` from sealed snapshots, with an
   explicit note that the earliest snapshot is a floor, not an observed first
   appearance. Snapshots begin 2026-07-31.
6. Generated disclaimer from `status` + `last_seen_patch` + `evidence_tier`.
7. Pilot on retired paints — 498 of 1,099 liveries already have no store URL.

## Holding to

- `unknown` is load-bearing, not a placeholder. An entity that vanished before
  we started sealing is **not** `retired` — we do not know it was not renamed.
  Guessing manufactures false history.
- A row already `retired` is never re-stamped: `last_seen_patch` records when it
  was last **seen**, not last looked for.
- `pipeline_check_results` stays unpreserved.
- Out of `citizen-collector/` entirely — C1 is sole writer and active.
- No `git add -A`. Nothing pushes without a go-ahead.
