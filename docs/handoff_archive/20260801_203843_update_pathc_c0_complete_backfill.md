# UPDATE — C0 complete: 890 observation rows are 274 findings, 27 are open DEFECTs

The number the addendum asked for, and it is defensible rather than asserted.

## The headline

| | |
|---|---:|
| `pipeline_check_results` observation rows | **890** |
| distinct findings after collapsing | **274** (3.2x) |
| findings after one run that actually looked | **299** |
| **OPEN DEFECTs** | **27** |
| OPEN non-PASS (DEFECT + LIMITATION + WARNING) | **42** |
| OPEN PASS (checked, nothing wrong) | 247 |
| CLOSED by a run that looked and did not find it | 10 |
| UNKNOWN | **0** |

274 independently matches the read-only figure in the C0 commit — two
different code paths, same answer.

**The 27 open DEFECTs:** 20 `missing_encoding`, 6 `missing_or_corrupt_3d_model`,
1 `schema_drift`. The 6 are exactly 85X, Arrastra, Fury, Mantis, Merchantman and
PTV — the list Parts A/B confirmed against `build_full.py`, now reached a third
time by a different mechanism.

## The 10 CLOSED are the ghosts, and they closed for the right reason

Not deleted, not suppressed — **closed by a run that ran their checker and did
not find them.** Every one is a ghost Parts A/B predicted:

- `registry_sync` charmap DEFECT — the stale one. A run opened the file as
  UTF-8, parsed it fine, did not report it. Closed.
- `.cache` missing model — the false positive. Checker skips dotfile dirs.
- Caterpillar Pirate Edition, P-72 Archimedes Emerald, Pulse, Ursa Fortuna —
  the four that had sibling models copied in after the last run.
- **2 old-format `schema_drift` DEFECTs** — the memory-address ones, replaced by
  the single stable finding. The fix visibly retiring its own ghosts.
- `schema_drift` "alembic not on PATH" LIMITATION.
- `missing_preview_image` for `.cache`.

**A repeat run produces `0 new, 0 reopened, 289 unchanged`.** Zero churn on an
unchanged repo — the 32-rows-for-11-problems behaviour is gone.

## THE DEMONSTRATION THIS ORDER ASKED FOR

`checks/_verify_broken_checker_end_to_end.py` sabotages a real checker inside
the real `run_checks.py` pipeline. `missing_or_corrupt_3d_model` was chosen
because it owns **241 open findings, 6 of them the genuinely-missing models** —
so an unguarded failure would be large, specific and silent.

```
of 241 findings owned by the broken checker:
  -> UNKNOWN : 241
  -> CLOSED  : 0
```

**Zero false closures.** The 6 real DEFECTs stayed visible, and came back as
OPEN once the checker was repaired.

And the mutation test that proves the guard is load-bearing rather than
decorative — same scenario, guard removed:

| | closed | unknown |
|---|---:|---:|
| with the guard | **0** | 3 |
| guard removed | **3** | 0 |

Without it, a dead checker reports a wave of CLOSED. That is the failure the
design exists to prevent, demonstrated rather than reasoned about.

## Two real bugs the first lifecycle run found by itself

**1. A finding that could never close.** The single UNKNOWN after the first run
was `missing_preview_image`. That name is emitted by
`missing_or_corrupt_3d_model_check` but **is not a registered checker**, so
nothing could ever vouch for having looked — pinned at UNKNOWN forever. Fixed
with an explicit `CHECKER_EMITS` map. Declared statically on purpose: inferring
emitted names from what a run produced would mean a condition that genuinely
went away drops out of "what ran" and goes UNKNOWN instead of CLOSED. It now
closes correctly, and UNKNOWN is 0.

**2. A FIFTH cp1252 failure, and my new rule does not cover it.** The first full
run crashed:

```
UnicodeEncodeError: 'charmap' codec can't encode character 'ā'
```

That is the `ā` in `tok.yāi` — **on stdout, not on a file open.** Hard rule 14
and the `missing_encoding` checker both address `open()`/`read_text()`/
`write_text()` and neither catches this. The run only completed with
`PYTHONIOENCODING=utf-8`.

**Part D must set `PYTHONIOENCODING=utf-8` in the scheduled task**, or the
schedule dies on the first Xi'an ship name with no console to show the error.

## Rule 4 — backup taken and verified before the backfill

`Backup-CitizenCompass.ps1`: **0 failures**, 997.9 MB, mirrored to E: and
**all 3,970 files hash-verified** against SHA256SUMS.txt.

One warning, which I checked rather than waved through: *"Restore returned 232
ships, expected 254"*. That is the already-recorded DB/live-site gap (DB 232,
registry 295, site 254), not a bad dump. The script's expectation of 254 is what
is stale.

Sequencing I got wrong and am recording rather than glossing: I ran the
additive `CREATE TABLE IF NOT EXISTS` DDL **before** taking the backup. It is
non-destructive and idempotent, but rule 4 puts the backup first and I should
have.

## What was built

- `pipeline_findings` — lifecycle state, one row per condition, `status`
  CHECK-constrained in the database. Proven able to reject an invalid status and
  to accept a valid one.
- `pipeline_check_runs` — one row per run, written **before** checkers execute,
  so a crashed run leaves a NULL `ended_at` rather than looking like it never
  started.
- Both added to `schema-init` (idempotent, re-ran clean), matching how
  `pipeline_check_results` was created.
- `checks/findings_store.py` — `apply_run` **requires** `checkers_ran_ok` and
  raises without it. A caller that cannot say which checkers succeeded is not
  allowed to close anything.
- `run_checks.py` — `_run_group` now reports which checkers completed. It
  previously returned findings only, which made a crashed checker
  indistinguishable from a clean one that found nothing.
- Hard rule 14 added to `CLAUDE.md`.
- `missing_encoding` checker, and the `MODEL_SOURCE.txt` → LIMITATION amendment.

## Rule 12 status

| proof | assertions |
|---|---|
| `_verify_findings_store.py` | 36 |
| `_verify_missing_encoding.py` | 19 (both directions) |
| `_verify_broken_checker_end_to_end.py` | 12 |

**Two of these caught real defects in my own work before I trusted them.** The
findings-store proof failed 4 assertions on first run — my test was wrong, not
the code, and I checked which before changing anything. The encoding linter
passed a 16-case fixture and then produced false positives against the real
repo: it flagged **its own docstring and its own fixture table**. Regex could
not tell a call site from text describing one, so it was rewritten on
`tokenize`, and those two cases are now regression tests.

Worth stating plainly: **the fixture passing did not mean the linter worked.**
It took real input to show that.

## Adding two tables makes `schema_drift` report more, and that is correct

`pipeline_findings` and `pipeline_check_runs` are outside alembic's metadata,
exactly like the two tables already flagged. `schema_drift` will now report 4
tables at risk of being dropped by an autogenerated migration instead of 2.
That is a true statement about a real risk, not a regression. Still reported,
not fixed — one schema decision covers all four and it is yours.

## Not done

C1–C3 (`snapshot_integrity`, `cross_source_disagreement`, `uex_join_health`),
C4 (`checker_health`), Part D. Path C is **not** complete.

## Also open, reported not fixed

The 20 `missing_encoding` DEFECTs are real call sites in
`audit_ship_components.py` (3), `image_handling.py` (2), `rescale_all_ships.py`
(4), `scripts/external_sources/_verify_integrity_scan.py` (1) and `tests/` (10).
Findings-only is locked and fixing them is outside this order — say the word and
they are a short, separate job.
