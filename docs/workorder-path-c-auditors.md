# WORK ORDER — Path C: put the auditors to work

**Approved by Sleven 2026-08-02.** Chosen over "schedule the collectors" (Path A) and "build Stage 2 first" (Path B).

Hard rule 13 applies: file an `inbox/` update on intake, on completion, and on any stop.

---

## Read this before planning: most of this is already built

Path C was scoped as "build the auditor layer." **It largely exists.** Verified on disk 2026-08-02:

```
checks/framework.py       101 lines   Finding dataclass, four-value vocabulary,
                                      write_findings -> pipeline_check_results
checks/file_checks.py     459 lines   13 checkers, stdlib + git only
checks/db_checks.py       184 lines   4 checkers, needs real Postgres
checks/network_checks.py  138 lines   1 wired, 1 deliberately held back
run_checks.py             125 lines   CLI, --group file|db|network|all
```

`pipeline_check_results` already exists in the schema. The vocabulary is already fixed at DEFECT / WARNING / LIMITATION / PASS. Findings-only is already locked in `ARCHITECTURE_DECISIONS.md` §4.

**Do not rebuild any of this.** The job is to make it run, make it trustworthy, and make it run by itself.

---

## PART A — the 874 findings nobody has read

`logs/pipeline_check_results_fallback.jsonl` holds **874 findings from three runs, last written 2026-07-31**, queued because no database connection was available.

**`checks_flush_fallback.py` — the script `framework.py` tells you to run — does not exist.** It was described in a docstring and never written. So every finding the auditors have ever produced has been sitting in a log file with no path into the table.

That is the single highest-value thing in this order: the system already works and has been talking to an empty room.

### A1. Write `checks_flush_fallback.py`

- Reads the JSONL, inserts into `pipeline_check_results`, and **does not double-insert on a second run.** Findings carry `check_name`, `subject`, `result`, `details`, `source_process`, `checked_at` — dedupe on the full tuple.
- On success, move the log aside with a timestamp rather than deleting it. Nothing here is worth losing to a partial load.
- **Rule 12:** run it twice and prove the row count does not change on the second run. An idempotence claim that has never been tested is a guess.

### A2. What the queued findings already say

Counts: **780 PASS, 43 LIMITATION, 33 DEFECT, 18 WARNING.** Two DEFECT groups, and **both look like checker bugs rather than data bugs** — confirm before acting:

**`missing_or_corrupt_3d_model` — 32 rows, ~11 unique subjects across three runs.** Ships flagged: 85X, Arrastra, Fury, Mantis, Merchantman, PTV, Pulse, Ursa Fortuna, P-72 Archimedes Emerald, Caterpillar Pirate Edition — plus `.cache`.

- **Independently corroborated.** `build_full.py` reports `unmatched: 6` naming 85X, Arrastra, Fury, Mantis, Merchantman, PTV. Two unrelated tools reached the same list. **These ships genuinely have no model.** Real finding — record it, do not "fix" it by deleting the check.
- **`.cache` is a false positive.** The checker walks every directory under `sc-ships/` and treats each as a ship. Skip dotfile directories. Noise in a findings table is not harmless — it teaches everyone to skim, which is how the real one gets missed.
- Four of these ships have a `MODEL_SOURCE.txt` explaining a shared-chassis copy. The checker should read that file and downgrade those to LIMITATION with the note's reason, not DEFECT.

**`registry_sync` — 1 row:** `ship_registry.json is not valid JSON: 'charmap' codec can't decode byte 0x81 at position 56616`.

**`charmap` means the file was opened without an encoding and Windows defaulted to cp1252.** The file is very likely fine and the *checker* is broken. **Verify by opening it explicitly as UTF-8 before changing anything** — if it parses, fix the checker; if it does not, the file is genuinely corrupt and that is a much bigger deal. Either way, audit every `open()` in `checks/` for a missing `encoding=` and fix them all, not just this one.

**7 `fan_kit_compliance` WARNINGs** — read these now. They bear directly on the open image-provenance question, and they were produced two days ago.

---

## PART B — run `--group db` for the first time ever

`checks/db_checks.py` was written, unit-tested against a scratch Postgres, and **has never been run against the real database.** `referential_integrity`, `duplicate_identifier`, `registry_sync`, `schema_drift`.

`DATABASE_URL` is present in `.env` and the password is being rotated — coordinate, then run.

- Run it. Flush the findings. **Report what it found rather than that it ran.**
- `schema_drift` and `registry_sync` are the two most likely to surface something real: the live site shows 254 ships and Postgres holds 232, and that gap has never been examined by a tool.
- **A run that produces zero DEFECTs is a result worth stating explicitly**, not silence.

---

## PART C — three new auditors, now that Phase 1 is done

Phase 1 completed 2026-08-01 (`afe00dc`). Five sources landed, two correctly ruled out. Nothing yet checks them *against each other*, and that is where the value is.

**C1. `snapshot_integrity`** — for every sealed snapshot, re-verify the hash manifest and report drift. Sealed snapshots are never modified, so **any** difference is either corruption or a broken rule. Must distinguish "file changed" from "file missing" from "manifest unreadable" — three different problems.

**C2. `cross_source_disagreement`** — where two sources describe the same ship, compare. Names, dimensions, manufacturer. Report disagreements with both values and both sources named. **Never pick a winner** — that is Stage 2's job and this layer flags only. Use the canonical-source decision's tiers to set severity, not to resolve.

**C3. `uex_join_health`** — UEX is Tier C and the whole point of the source is the item→shop→price link. Check: what fraction of `items.uuid` values actually join to `fps-items.json`? The manifest records 5,566 of 7,728 records carrying a UUID — **confirm that from the data rather than trusting the manifest**, and report the join rate as a tracked number. Flag prices outside plausible bounds given UEX's own stated ±20% commodity / ±100% item tolerance.

**All three: findings only. No writes outside `pipeline_check_results`.**

**Rule 12 for each:** feed each auditor input that must fail — a tampered hash, a planted disagreement, a broken join key — and confirm it reports. An auditor whose failure path has never executed is decoration.

---

## PART D — make it run by itself

This is the part that makes it Path C rather than a one-off.

Follow the pattern already proven by `inbox_watcher.exe`: real background service, auto-start, silent, no console window, survives reboot, registered the way `setup_watcher_task.ps1` registers the watcher.

- `--group file` **daily**. Cheap, no dependencies, runs anywhere.
- `--group db` **daily**, after the file group.
- `--group network` **weekly**. It runs `pip-audit`; that does not need to be daily.
- Findings go to `pipeline_check_results` directly when the DB is up, to the fallback log when it is not — the existing degradation path. **Now that a flush script exists, schedule the flush too**, or the fallback silently accumulates again exactly as it just did for two days.
- Log every run: what ran, how long, how many findings by result. **A run that finds nothing must still log that it ran** — otherwise a scheduler that quietly stopped looks identical to a clean bill of health.

**One process, one schedule.** This project has already lost ~37,000 characters per regeneration to two writers on one file, and again today to two sessions on one layer. Register exactly one scheduled task and confirm by behaviour that only one is writing.

`duplicate_process` is already a registered checker. **Point it at this** so the auditor system watches for its own duplication.

---

## What "done" looks like

1. The 874 queued findings are in the table and the two DEFECT groups are characterised as data problems or checker problems, with evidence either way.
2. `--group db` has run against the real database at least once and its result is written down.
3. Three new auditors exist, each proven against known-bad input.
4. One scheduled task runs the whole thing and its log shows more than one successful unattended run.

**Do not report this complete on a run that verified nothing.** That is the exact failure that let source 2 be marked complete, and this is the layer whose entire job is catching that class of mistake.

## Boundaries

- **Findings only.** No auditor modifies data, ever. Locked decision, not up for revisiting.
- Live site, sealed snapshots and `releases/latest.html` untouched.
- Nothing under `testing/` except what other orders cover.
- If a part blocks, write to `inbox/`, stop that part, move to the next.
