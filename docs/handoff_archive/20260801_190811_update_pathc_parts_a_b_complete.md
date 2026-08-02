# UPDATE — Path C Parts A and B complete. Parts C and D NOT started.

The auditors are no longer talking to an empty room. 890 findings are in
`pipeline_check_results`, and the reason they never got there is not what the
order assumed.

## THE ROOT CAUSE WAS NOT "NO DB ACCESS"

`run_checks.py` line 117 passed **`db_conn=None` unconditionally.** It opened a
working SQLAlchemy session, used it for the checkers, and then never passed any
connection to `write_findings`. So every finding this system has ever produced
went to the fallback log **even when the database was perfectly reachable.**

The degradation path was not a fallback. It was the only path, permanently.

`framework.py`'s docstring blames the 2026-07-30 environment ("cannot reach the
real Postgres database"). That was true then. It has not been true since, and
the hardcoded `None` meant nothing changed when the environment did.

Fixed: `run_checks.py` now opens a psycopg2 connection for the write and passes
it through, falling back to the log only when that genuinely fails — and saying
which path it took either way. Verified: a `--group db` run now reports
"8 findings written directly to pipeline_check_results" and the row count moves.

## VERIFICATION 1 — registry_sync: checker bug, and already fixed

`ship_registry.json` is **not corrupt.** It decodes as UTF-8 and parses as JSON,
a 295-entry list. The byte at 56616 is `\xc4\x81` — "ā" in `tok.yāi`, a Xi'an
ship name. Opening it without an encoding reproduces the reported error exactly.

**The finding is also stale.** It was written 2026-07-30T14:57:32; commit
`db18e02`, which added `encoding="utf-8"` to that exact line, landed
2026-07-30T20:07:26 — after it. The code was already correct before I looked.

**Audited every `open()`/`read_text()` in `checks/` as instructed** and fixed
**8** more missing `encoding=`, including `framework.py:72` — the fallback log
*writer*. That one is the dangerous one: it would have raised
`UnicodeEncodeError` and lost a finding the moment any subject contained a
non-ASCII ship name. The log survived only because `json.dumps` defaults to
`ensure_ascii=True`. Confirmed: the log is pure ASCII, 0 non-ASCII bytes.

This is now the **fourth** instance of Windows cp1252 breaking this pipeline on
real ship names — after `ccpp.py` (three call sites) earlier today. My own
diagnostic script hit it too while printing a ship name.

## VERIFICATION 2 — 3D models: real, with two corrections

11 unique DEFECT subjects, 32 rows across runs. Verified against disk:

| subject | dir | model.glb | MODEL_SOURCE.txt |
|---|---|---|---|
| `.cache` | yes | **no** | no |
| 85X, Arrastra, Fury, Mantis, Merchantman, PTV | yes | **no** | no |
| Caterpillar Pirate Edition, P-72 Archimedes Emerald, Pulse, Ursa Fortuna | yes | **yes** | **yes** |

- **`.cache` is a false positive, confirmed** — it is the *only* dotfile
  directory among 242 under `sc-ships/`. The checker treats every directory as
  a ship.
- **The 6 genuinely missing models are real** — 85X, Arrastra, Fury, Mantis,
  Merchantman, PTV. Exactly matching `build_full.py`'s `unmatched: 6`. Two
  unrelated tools, same list.
- **The 4 shared-chassis ships now HAVE a model.glb**, each with a
  `MODEL_SOURCE.txt` recording it was copied from a sibling on
  2026-07-30T18:31:55 — *after* the last check run at 17:58:11. So those
  findings are **also stale**. They would now pass an existence check.

The correction the order asked for still stands and is worth more than the
staleness: a copied sibling model is **not ship-specific art**. The checker
should read `MODEL_SOURCE.txt` and report **LIMITATION** with that reason, so
"has a model" is not silently conflated with "has its own model."

## THE 7 fan_kit_compliance WARNINGs

They are **one finding repeated across 7 runs**, not 7 distinct issues:

> `static/index.html` — no text matching 'trademark' found - confirm the
> required disclaimer is still present

**Reporting, not fixing** — CLAUDE.md rule 8 puts Fan Kit, trademark and legal
text solely with Sleven.

Context that matters: `static/index.html` **is not the deployed page.** The live
site is served from `static/preview.html` mirrored into `releases/latest.html`.
It has been separately established that the deployed page *does* carry the
disclaimer and `index.html` does not. So this warns about an undeployed file —
real as a hygiene finding, not a live compliance breach. It bears on image
provenance only insofar as it is the same undeployed file.

## PART A — complete

`checks_flush_fallback.py` written. The script `framework.py` has told people to
run since 2026-07-30, which did not exist.

**Rule 12, 20 assertions, all passing** (`--self-test`): malformed input is
*reported* not silently dropped (unparseable line, missing fields, invalid
result vocabulary); a dry run writes nothing; archiving moves rather than
deletes and preserves content; an absent log is a clean no-op; duplicates within
one file collapse; a genuinely different finding still inserts.

**Idempotence proven on the real data, not just fixtures:**

| run | inserted | skipped | table rows |
|---|---:|---:|---:|
| first | 874 | 0 | 874 |
| second | **0** | 874 | **874** |

It also **fails closed**: malformed lines mean nothing is inserted and nothing
archived, rather than a partial load that silently drops findings.

Logs archived to `logs/flushed/` with timestamps. Nothing deleted.

## PART B — complete. What it FOUND:

First run of `--group db` against the real database, ever.

**8 findings: 1 DEFECT, 2 WARNING, 5 PASS.**

### The DEFECT is real, and it is a latent data-loss risk

`schema_drift`: `alembic check` reports drift, and specifically proposes
`remove_table` for **`ship_registry` (295 rows)** and
**`pipeline_check_results` (890 rows)**.

Both exist in the live database. **Neither is in `app/models.py`** — they were
created by `schema-init/main.go`, outside alembic's metadata.

**Consequence:** anyone running `alembic revision --autogenerate` and applying
it would generate a migration that **DROPS the auditor findings table and the
ship registry.** Not a checker bug — the checker is right, and this is exactly
the class of thing this layer exists to catch. Reported, not fixed: adding
models or an alembic exclusion is a schema decision outside this order.

### The WARNINGs — the 232 / 254 / 295 gap, now measured

- 62 DB ship names have no `ship_registry.json` entry
- 108 registry entries have no DB row

Three different numbers for "how many ships": **DB 232, registry 295, live site
254.** The order flagged this gap as never examined by a tool. It has now been,
and the answer is that registry and DB disagree in *both* directions — so it is
not simply "the DB is behind".

### The 5 PASSes — stated explicitly, as instructed

- `referential_integrity`: all 232 ships have a valid `manufacturer_id`
- `referential_integrity`: all non-null `last_verified_patch` values resolve
- `referential_integrity`: all confidence values valid
- `referential_integrity`: all 252 dealer listings have valid `ship_id`/`dealer_id`
- `duplicate_identifier`: **no duplicate `(name, manufacturer_id)` pairs** —
  independent corroboration that today's CC-12 constraint is holding

## Final state

`pipeline_check_results`: **890 rows** — PASS 790, LIMITATION 43, DEFECT 35,
WARNING 22. DEFECTs by checker: `missing_or_corrupt_3d_model` 32,
`schema_drift` 2, `registry_sync` 1. **Nothing stranded**; the fallback log is
archived and absent.

## PARTS C AND D — NOT STARTED

Stopping cleanly here rather than starting work I cannot finish and verify to
the standard this order demands.

- **Part C** — three new auditors (`snapshot_integrity`,
  `cross_source_disagreement`, `uex_join_health`), each requiring rule-12 proof
  against tampered hashes, planted disagreements and broken join keys.
- **Part D** — one scheduled task, confirmed by behaviour to be the only writer.

Both are substantial and neither is begun. **Path C is not complete** and I am
not reporting it as such — that would be the exact failure this layer exists to
catch.

One useful note for Part D when it happens: the fallback-flush schedule the
order asks for is *less* critical now that `run_checks.py` writes directly, but
still worth having — the fallback path is real and now correctly reserved for
genuine outages.
