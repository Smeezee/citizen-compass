# UPDATE — C1–C4 and Part D complete. Path C is done.

Committed `c88aa07`. Below is what the new auditors **found**, then the three
things confirmed by behaviour rather than by reading a registration.

## The number

**3,057 observation rows → 383 distinct findings. 27 are open DEFECTs.**

| status | | count |
|---|---|---:|
| OPEN | PASS | 260 |
| OPEN | **WARNING** | **61** |
| OPEN | **DEFECT** | **27** |
| OPEN | LIMITATION | 21 |
| CLOSED | (all results) | 14 |
| **UNKNOWN** | | **0** |

The 27 open DEFECTs: 20 `missing_encoding`, 6 `missing_or_corrupt_3d_model`
(85X, Arrastra, Fury, Mantis, Merchantman, PTV), 1 `schema_drift`.
Last full run: **24 checkers, 0 errored.**

## What the three new auditors FOUND

**`snapshot_integrity` — zero corruption, and that is a result.** All five
sealed snapshots carrying recorded hashes verify clean, including source 1's
**28,960 files / 4.5 GB**. The other eight manifests report LIMITATION,
correctly separating *"no hashes were recorded"* from *"nothing was ever
landed"*. Takes 239s, which is why the source group is weekly.

**`cross_source_disagreement` — 56 disagreements** across 117 ships shared by
scunpacked.com and the wiki API: 27 mass, 16 manufacturer, 11 cargo, 2 size.
Both values and both sources named; no winner picked.

**`uex_join_health` — the manifest confirmed from the data.** 5,566 of 7,728
UEX records carry a uuid — **exactly** the manifest's claim, now measured
rather than trusted. **3,846 of those 5,566 join to `fps-items.json`: a 69.1%
join rate**, against 5,420 distinct UUIDs on the other side. Tracked number;
UEX is Tier C and this link is the source's entire purpose.

## Picking the right field was most of the work

My first cross-source version compared scunpacked.com's numeric `Size` against
the wiki's `size` — which is a **localised label dict**. It flagged all 117
shared ships. The real counterpart is `size_class`, against which **115 of 117
agree**. The correct field turned 117 fabricated findings into 2 genuine ones.

Mass is **bracketed, not point-compared** — a measurement decision, not a
tolerance loosened until findings vanished. Median difference is 9.5% against
`mass_hull` and 7.1% against `mass_total`: a systematic offset, so these are
different quantities. Only values outside the whole hull..total range with 10%
slack are reported. That still catches the real ones — the **Anvil Carrack is
97,858 in one source and 3,275,858 in the other.**

## Two silent successes found in checkers, one of them mine

**`checker_health` had the exact bug it exists to catch.** Its first scheduled
run showed `2 new, 2 closed` on an unchanged repo — it was putting `run_id` in
`details`, and `finding_key` hashes `details`, so it minted a fresh finding
every run. The same ghosts-on-a-timer failure this order fixed in
`schema_drift`, reproduced in the checker whose whole job is noticing it. Fixed;
three consecutive runs now report `0 new, 0 reopened, 0 closed`.

**`duplicate_process` never actually looked.** It returned the same LIMITATION
unconditionally — "cannot enumerate Windows processes from this environment" —
true in the 2026-07-30 sandbox, false ever since. It could not have detected a
duplicate writer while still appearing in every run as though something had been
checked. It now enumerates processes and scheduled tasks.

**And my rewrite of it had a false negative against this very machine.** I
filtered rows with a substring test for `"disabled"`; `schtasks /v` carries that
word in unrelated columns, so the registered task was discarded and the checker
reported nothing scheduled **while a task was demonstrably running**. Now parsed
as CSV against the named `Task To Run` and `Scheduled Task State` columns, and
proven in all three directions including the disabled-task case.

## The three confirmations, by behaviour

**1. Exactly ONE task writes findings.** Enumerated every scheduled task on the
machine and inspected its action string: **2 tasks touch this repo, 1 invokes
`run_checks`** (the other is the inbox watcher, a different target).

**2. It fires unattended and writes a run record.** Triggered out of schedule
rather than waiting for 09:15. Run records went **12 → 14**, both with
`source_process=run_checks_scheduled.ps1` and `ended_at` populated.
`LastTaskResult=0`.

**3. A run that finds nothing still writes its record.** Drove the real
`_apply_lifecycle` with zero findings: **run records 14 → 15, `ended_at` set,
all counts 0, and not one finding altered** (307 before, 307 after). A dead
scheduler and a clean bill of health do not look the same.

## Part D details that are not optional

`run_checks_scheduled.ps1` sets two things, both found the hard way, neither
visible to a run with no console:

- **`PYTHONIOENCODING=utf-8`** — without it the run dies on the first non-ASCII
  ship name. The fifth cp1252 failure in this pipeline, and the first on stdout
  rather than a file open, so hard rule 14 does not cover it.
- **`venv\Scripts` on PATH** — without it `schema_drift` returns LIMITATION
  instead of DEFECT, so a **real schema drift silently stops being reported**
  while the run still looks healthy.

**Scope** was added to the lifecycle because separate daily file and db runs
would otherwise corrupt each other: a db-only run observes no file finding, so
an unscoped run marked all 289 of them UNKNOWN, and the next file run would do
the same in reverse. They would spend every day undoing each other. A db-only
run now reports `0 -> unknown`. Scope never causes a close — it only decides
what a run is entitled to have an opinion about.

## The `-WhatIf` defect, recorded in CLAUDE.md under rule 12

A dry-run flag that silently does not apply is a check that cannot fail — the
same class as `main()` returning `None` and the gate scripts returning 0
unconditionally. It is now written into rule 12 in those terms, with the
instruction to **prove the flag by behaviour**: run the dry run, then confirm
from the outside that nothing changed.

`setup_checks_task.ps1` now refuses to elevate under `-WhatIf` and forwards its
arguments. Verified: a dry run with `-TaskName 'CC Dry Run Probe' -At 03:33`
echoed those exact values and created nothing.

**`setup_watcher_task.ps1` has the same elevation flaw** — reported, not
changed; it is outside this order and its parameters are inert.

## Still open, reported not fixed

- **`schema_drift`**: 4 tables (`ship_registry`, `pipeline_check_results`, and
  the 2 I added) exist outside alembic's metadata, so
  `alembic revision --autogenerate` would generate a migration **dropping all
  four**. One schema decision covers all of them and it is yours.
- **20 `missing_encoding` DEFECTs** in `audit_ship_components.py` (3),
  `image_handling.py` (2), `rescale_all_ships.py` (4),
  `scripts/external_sources/_verify_integrity_scan.py` (1), `tests/` (10).
- **61 open WARNINGs**, mostly the cross-source disagreements above.
- The `fan_kit_compliance` warning remains untouched per rule 8.

## Rule 12 totals

91 assertions across five proofs: lifecycle 22, findings-store 36, encoding
linter 19, broken-checker end-to-end 12, source auditors 24 — plus the
duplicate_process and mutation checks run inline. **Three of them caught real
defects in my own work before I trusted it.**
