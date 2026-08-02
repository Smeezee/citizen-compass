# ADDENDUM to `workorder-path-c-auditors.md` — finding lifecycle, and one standing rule

Written 2026-08-02 after Parts A and B landed (`562880a`). **Read this before starting Parts C and D.** It changes what those parts have to build.

---

## Why this exists

Parts A and B loaded 890 findings and then established that **most of them described problems that no longer existed:**

- `registry_sync` reported a corrupt file. The file was fine, the checker was broken, **and the checker had already been fixed six hours before the finding was ever read.**
- Four ships flagged as missing 3D models had models copied in **after** the last check run.
- The 7 `fan_kit_compliance` warnings were **one finding repeated across 7 runs.**
- 32 `missing_or_corrupt_3d_model` rows described **11 subjects**, of which **6 were real.**

So of 33 DEFECTs, roughly 6 were live. The rest were ghosts and duplicates.

**A findings table that is mostly ghosts is worse than no table**, because the only rational response is to skim it — and skimming is how the real one gets missed. Parts C and D add three more auditors and put them on a schedule. Without a lifecycle that multiplies the noise on a timer.

---

## PART C0 — finding lifecycle (do this BEFORE C1–C3)

### Identity

A finding needs a stable key so the same condition seen twice is one finding, not two rows.

`finding_key` = a hash of `check_name` + `subject` + a **normalised** description of the condition.

**Normalised means the varying parts are stripped** — timestamps, absolute paths, run ids, counts that drift. Key off "this ship has no model," never off "checked at 14:57 and this ship has no model." Getting this wrong reproduces the 32-rows-for-11-problems result exactly.

### Columns

Add to `pipeline_check_results` (or a companion table — your call, but say which and why): `finding_key`, `status`, `first_seen`, `last_seen`, `closed_at`, `closed_by_run`, `run_id`, `acknowledged`, `acknowledged_reason`.

`status` ∈ **OPEN / CLOSED / UNKNOWN / ACKNOWLEDGED**.

### The transition rules — this is the load-bearing part

**A finding is CLOSED only by a run that looked for it and did not find it.**

- Seen this run → OPEN, `last_seen` updated. **Do not insert a second row.**
- Previously OPEN, its checker ran successfully, not seen → **CLOSED**, with `closed_at` and `closed_by_run`.
- Previously OPEN, but its checker **errored, was skipped, or is no longer registered** → **UNKNOWN**. Never CLOSED.

**That last rule is the whole point.** A checker that stopped running must never look like a problem that went away. This project has already had a scheduled process stop with nobody noticing, and has already had a status brief claim something stopped when it was still running. Silence is not evidence of absence — encode that, don't rely on remembering it.

**Nothing is ever closed by a human, by a session, or by inference.** Not by "I fixed that," not by editing the row. If it is fixed, the next run proves it. Same principle as auditors flagging and never fixing.

### ACKNOWLEDGED

Some findings are real, known and accepted — the 6 ships with genuinely no model are the obvious case.

- Requires a reason and who set it. Sleven's call, not a tool's.
- **Still counted, just sorted down. Never hidden.** A suppression mechanism that removes things from view is how a real finding disappears for six months.
- Cleared automatically if the finding CLOSES and later reopens — the world changed, look again.

### Backfilling the 890 rows already loaded

They are historical and mostly stale. Do not try to reconstruct their history.

1. Assign `finding_key` to every existing row.
2. Collapse duplicates into one row per key, `first_seen` = earliest, `last_seen` = latest.
3. Mark them all **UNKNOWN**, not OPEN. Nothing has verified them today.
4. Run the full check suite once. Whatever reappears becomes OPEN; whatever does not becomes CLOSED with a note that it was closed by the first lifecycle-aware run.

**Report the before and after counts.** "890 rows became N findings, of which M are actually open" is the single most useful number this order will produce.

---

## PART C4 — one more auditor, added by this addendum

**`checker_health`** — the auditors watching themselves.

- Reports any registered checker that **errored** in the last run, and any that has not produced a result in longer than its schedule allows.
- Reports if a single run closed an implausible share of open findings at once. **A mass close is far more often a broken checker than a productive afternoon.**
- Reports any finding in UNKNOWN for more than a week.

Without this, Part D's schedule can quietly stop and the table just looks calm.

---

## STANDING RULE — every file open specifies its encoding

Parts A and B found **8 more missing `encoding=`** in `checks/`, including `framework.py:72` — the fallback log's own *writer*, which would have destroyed a finding the moment any subject contained a non-ASCII ship name. It survived only because `json.dumps` escapes to ASCII by default.

**That is the fourth time Windows cp1252 has broken this pipeline on real ship names**, after three call sites in `ccpp.py`. Xi'an and Banu names are not edge cases in a Star Citizen database — `tok.yāi` is a shipping product.

Add to `CLAUDE.md` as a hard rule: **every `open()`, `read_text()` and `write_text()` in this project specifies `encoding="utf-8"` explicitly. No exceptions, including in throwaway diagnostic scripts** — one of those hit it too.

Then make it self-enforcing: add a **`missing_encoding`** checker that scans the repo for file opens without an explicit encoding and reports each one. Cheap, mechanical, and it stops this being a thing anyone has to remember.

**Rule 12 on that checker:** plant a call site without an encoding and confirm it is caught, then confirm a correct one is not flagged. A linter with a false-negative is worse than none.

---

## Amendments to C1–C3 as already specced

- **`.cache` and every dotfile directory** is skipped by any checker walking `sc-ships/`. Confirmed as the only such directory among 242.
- **`MODEL_SOURCE.txt` is read.** A ship whose model was copied from a sibling reports **LIMITATION** with that reason, not PASS. "Has a model" must not silently mean "has its own model" — four ships are currently in exactly that state.
- The 6 ships with genuinely no model — 85X, Arrastra, Fury, Mantis, Merchantman, PTV — are a real, confirmed finding, corroborated independently by `build_full.py`'s `unmatched: 6`. Candidates for ACKNOWLEDGED once Sleven decides, not for deletion.

## Amendments to Part D

- Every run writes a run record: `run_id`, start, end, checkers attempted, checkers errored, findings opened, closed, unchanged.
- **A run that finds nothing still writes that record.** A dead scheduler and a clean bill of health must never look the same.
- `duplicate_process` and the new `checker_health` both point at this system. One scheduled task, confirmed by behaviour, not by reading the task list.

## Done means

The count of genuinely open findings is a number you can say out loud and defend, the schedule has run unattended more than once, and a deliberately broken checker has been shown to produce UNKNOWN rather than a wave of CLOSED.
