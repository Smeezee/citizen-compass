# UPDATE — stale entries reconciled, manifest diagnoses corrected, CC-12 re-measured

Reconciles two stale entries, appends corrections to two published manifests,
and re-captures the CC-12 numbers. Nothing committed, nothing pushed.

## RECONCILIATION 1 — the FIX 3 entry is stale

An earlier entry describes the two pipeline gate scripts as returning 0
unconditionally. **Both already fail closed on disk.** Verified:

- `scripts/external_sources/integrity_scan.py:222` -> `return 1 if (found_something or incomplete_coverage) else 0`
- `scripts/external_sources/finalize_star_citizen_wiki.py:77` -> `return 1 if failed else 0`

And verified the way the new rule 12 requires — against known-bad input rather
than by reading the source: a JSON file containing `<script>` fed to
`integrity_scan.py` returns **exit 1**. The failure path executes.

`integrity_scan.py` additionally fails closed on *incomplete coverage* now, not
only on findings.

## RECONCILIATION 2 — the CC-16 entry is stale, and so was its replacement value

CC-16 is resolved. But the value supplied for it —
`e1d60c915cb6d31933d614f378c8fb0a7e388a50` — **was already out of date when it
was given.** Two further commits have since been pushed.

Ground truth at time of writing:

| | |
|---|---|
| HEAD | `f58a9be3728f195336f39f528e09376198c11eea` |
| origin/main | `f58a9be3728f195336f39f528e09376198c11eea` |
| in sync | YES |
| commits ahead of origin | **0** |

`e1d60c9` is now two commits back. The correct statement is: **6 commits were
pushed, then 2 more (`0ae0514`, `f58a9be`), and HEAD and origin/main are both at
`f58a9be`, fully in sync.**

## CC-12 natural key — re-measured READ-ONLY 2026-08-01

Run inside an explicit `SET TRANSACTION READ ONLY` (confirmed
`transaction_read_only = on`). No writes, no migrations, no schema changes.

| metric | value |
|---|---:|
| components rows total | 8 |
| components with `class_name` NULL | **0** |
| components with `class_name` blank (`''`) | **0** |
| duplicate non-null `class_name` values | **0** |
| ships rows total | 232 |
| duplicate `(name, manufacturer_id)` pairs | **0** |

**Blockers to applying the constraints: NONE.** Both proposed constraints
(`class_name` NOT NULL, `uq_ships_name_manufacturer_id`) would apply today with
zero data remediation. This remains the cheapest the fix will ever be — the cost
grows with every row added before it lands.

## Manifest corrections appended (APPEND ONLY)

Two published manifests state the source 3 `/vehicles` failure was a persistent
upstream fault. That diagnosis is wrong, and both are public on `origin`.

**Nothing above the new note was modified in either file.** Verified by diff:
11 and 12 lines added respectively, 1 line removed each — and that single
removed line in each case is the former last field regaining a trailing comma.
No acquisition record, count, hash or status was touched. Both files re-validate
as JSON and both keep `snapshot_status: "partial"`.

- `20260731T031754Z/03_star-citizen-wiki-api_manifest.json` — corrects
  `collections[0].failure_reason` ("a real, intermittent upstream fault at this
  page size").
- `20260731T041451Z/03_star-citizen-wiki-api_manifest.json` — corrects
  `collections[0].cross_run_significance` ("a persistent upstream fault").

Each note records: the endpoint was never down; `page[size]=200` returns HTTP
500 with an HTML body while 20 and 50 return valid JSON; and that a **single
read-only probe is the ONLY evidence** for the correction.

Two points stated deliberately rather than smoothed over:

1. **"Deterministic" is qualified.** Deterministic in every scripted run (5/5,
   5/5, 1/1 at 200), but near-deterministic across all known attempts — the
   031754Z manifest records 1 success in 3 manual curl tests at 200, making it
   1 success in ~14. Rounding that to "always fails" would misstate the record.
2. **Why the second run's reasoning failed.** Both runs held `page[size]=200`
   fixed. Repeating an identical request and seeing an identical failure cannot
   distinguish a broken endpoint from a rejected parameter. The variable that
   mattered was never varied, so run 2 added confidence without adding
   information. That is the transferable lesson, not the specific bug.

Also recorded: the claim that the `page[size]=20` citation was fabricated is
itself wrong. `scope_boundaries_hit` in the 031754Z manifest has always said
verbatim "page[size]=20 succeeded on a manual test".

## CLAUDE.md — new HARD RULE 12

**"A check that cannot fail is not a check."** Added to the HARD RULES block,
immediately after rule 11 (fail closed / never fabricate) and before the
`---` that closes the section, so it sits alongside the destructive-action
rules rather than in the advisory notes below them.

It names the pattern **SILENT SUCCESS**, cites the three instances found in this
repo, and requires that any gate be fed known-bad input and observed to fail
before it is trusted.

## BLOCKED — the session addendum was not received

`session-addendum-2026-08-01.md` is **not present**: not in `inbox/`, nowhere in
the repo, and nothing was written in the last 15 minutes. The attachment did not
arrive.

It has therefore **not** been filed to `docs/handoff_archive/`, and its Sections
1-5 have not been read. Everything above was completed from the instructions in
the request itself, which quoted rule 12's wording directly and named the two
manifests. The CC-12 numbers are captured here and are ready to be appended to
Section 2 Part A the moment the file arrives.
