# UPDATE — corrected intake: starting Path C Parts C0-C4 and D

Supersedes `update_pathc_intake.md`, which described the original order before
the addendum existed and before Parts A and B were done.

## Correction to my own previous note

Parts A and B are **complete and pushed** as `562880a`. I was about to re-run
both verifications that commit already answered. I am not repeating them. For
the record, they are settled:

- `registry_sync` — checker bug, not corruption, and stale: `db18e02` fixed that
  line six hours before the finding was read. 8 further missing `encoding=`
  fixed across `checks/`, including `framework.py:72`, the fallback log writer.
- 3D models — `.cache` is the only dotfile dir of 242. 6 ships genuinely have no
  model (85X, Arrastra, Fury, Mantis, Merchantman, PTV), corroborated by
  `build_full.py`'s `unmatched: 6`. The other 4 had sibling models copied in
  after the last run.
- fan_kit_compliance — one warning across 7 runs, about `static/index.html`,
  which is not the deployed page.
- `run_checks.py` passed `db_conn=None` unconditionally; fixed. 890 findings are
  in `pipeline_check_results`.

## What I am starting now

`docs/workorder-path-c-addendum-lifecycle.md`, then Parts C and D of
`docs/workorder-path-c-auditors.md` as amended by it.

**The addendum exists because of what Parts A and B found:** of 33 DEFECTs,
roughly 6 were live. The rest were ghosts and duplicates. Adding three auditors
and a schedule on top of that multiplies ghosts on a timer.

Order of work, as the addendum requires:

1. **C0 — finding lifecycle, before C1-C3.** Stable `finding_key` off a
   *normalised* condition, `status` in OPEN/CLOSED/UNKNOWN/ACKNOWLEDGED, and the
   transition rules. The load-bearing rule: **a finding is CLOSED only by a run
   that looked for it and did not find it.** A checker that errored, was skipped
   or is no longer registered yields **UNKNOWN**, never CLOSED — a checker that
   stopped running must never look like a problem that went away. Backfill the
   890 rows as UNKNOWN, then one full run decides what is really open, and
   report before/after counts.
2. **Standing rule** — `encoding="utf-8"` everywhere as a CLAUDE.md hard rule,
   plus a self-enforcing `missing_encoding` checker with rule-12 proof both ways
   (planted bad call site caught; correct one not flagged).
3. **C1-C3** — `snapshot_integrity`, `cross_source_disagreement`,
   `uex_join_health`, each proven against known-bad input.
4. **C4** — `checker_health`, the auditors watching themselves, including the
   mass-close alarm.
5. **Part D** — one scheduled task, run records written even on a clean run,
   confirmed by behaviour.

## Constraints I am holding to

- **Findings only.** No auditor modifies data. Locked.
- **Nothing is ever closed by a human, a session, or by inference.** If it is
  fixed, the next run proves it.
- **ACKNOWLEDGED is sorted down, never hidden.**
- **Rule 12 on every new auditor**, including the false-negative direction — a
  linter that misses things is worse than none.
- I will not report Path C complete on a run that verified nothing.

## Realistic scope note

This is five distinct pieces of work. I will file an update as each lands and
stop cleanly with a note rather than half-finishing several. C0 first, because
everything after it is worth less without it.
