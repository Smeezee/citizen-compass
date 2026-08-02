# UPDATE — Parts C/D intake; three briefed premises did not match disk

Filed on intake per rule 13, before any work. New session. I verified the
brief's stated starting conditions against disk rather than accepting them,
and **three of them are wrong.** Recording that before doing anything, because
two of the three asked me to take an action that would have damaged the record.

## 1. There is no `.git/index.lock`. Nothing is blocking commits.

The brief says a stale `.git/index.lock` is present and will block the first
commit. It is not there. `Test-Path` says no; no `git`, `git-lfs`, `gitk` or
`git-gui` process is running.

The only `.lock` anywhere under `.git/` is `.git/objects/maintenance.lock`,
0 bytes, dated 2026-07-29. That is git's background-maintenance lock. It does
**not** block `git commit`, and it is not the file the brief described.

**I have not removed it.** It is unrelated to the stated problem, rule 1 says
move aside rather than delete, and nothing currently needs it gone. If git
maintenance turns out to be wedged that is a separate call for Sleven.

## 2. The "false entry" is not false, and it has already been superseded.

The brief says `LATEST_HANDOFF.md` line 214 carries a fabricated entry — "UPDATE
— Path C auditors work order received, starting" — filed by an aborted session
that did not know Parts A and B were done, sitting *after* the completion entry,
and asks me to mark it retracted.

**I am not doing that, because the entry is truthful and correctly placed.**

- It is not at line 214. Line 214 is body text of the Parts A/B completion entry.
  The real entry is at **line 388**, `update_pathc_intake.md`.
- Its timestamp is **19:00:06**. The Parts A/B completion entry is **19:08:11**.
  The intake was filed **eight minutes before** the completion — a normal rule-13
  intake, filed before the work, exactly as required.
- It only *appears* below the completion entry because the section is headed
  **"RECENT UPDATES (append-only, newest first)"** (line 31). Later in the file
  means older, not newer. Reading it as a restart is a misreading of that
  ordering, not a defect in the record.
- It is **already explicitly superseded**. `update_pathc_cd_intake_corrected.md`
  at **20:02:20** (line 139) opens: *"Supersedes `update_pathc_intake.md`, which
  described the original order before the addendum existed and before Parts A and
  B were done."* The correction was appended, not substituted — which is what
  append-only requires.

Marking a truthful, correctly-ordered, already-superseded entry as "retracted"
would put a false statement into the record in the name of protecting it. The
next session is better served by the ordering note above than by a retraction of
something that was never wrong.

**Reported, not acted on.** If Sleven still wants an annotation there after
reading this, that is a one-line change and I will make it.

## 3. Part C0 is not pending. It is done, committed, and pushed.

The brief places me at `562880a` with C0 ahead of me. `HEAD` is **`329f437`**,
*"Path C0: finding lifecycle identity and transitions, proven"*, and
`origin/main` is the same commit — 0 ahead, 0 behind. A session got further than
the brief knew.

`checks/lifecycle.py` (166 lines) exists: stable `finding_key` over
`check_name` + `subject` + a normalised condition, the four statuses, and the
transition rules. 22 rule-12 assertions in `checks/_verify_lifecycle.py`,
including the critical one — with no checker having run, nothing may close and
every open finding goes to UNKNOWN. Measured read-only against the real data:
**890 rows collapse to 274 distinct findings (3.2x); 35 DEFECT rows to 14
distinct DEFECTs.**

**I am not re-deriving any of that.** But C0 is only *partly* landed. Its own
commit message says so: the `pipeline_findings` table, the backfill, C1–C4, the
standing rule and Part D are **not** done.

Also carried forward from that commit, and it matters before Part D:
`schema_drift` puts `alembic check`'s raw output into `details`, and that output
lists drift operations in **unstable order** — so the same condition hashes to a
different key every run. No normaliser can fix that from the outside; the
checker must emit a sorted summary. **Scheduling anything before that fix would
multiply ghosts on a timer**, which is the precise failure the addendum exists to
prevent. It goes before Part D.

## 4. 56 files uncommitted, not 96.

`git status --porcelain` reports **56**. I will review and commit what belongs
and state explicitly what I leave out. `testing/_src/` is present and holds
`_layer.src.html` plus the three build scripts (`build_full.py`,
`build_machine_layer.py`, `build_portable.py`) — going in, as instructed.

## What I am doing, in order

1. Commit the working tree (56 files), `testing/_src/` included.
2. Fix `schema_drift`'s unstable `details` — blocks Part D.
3. Finish C0: `pipeline_findings` table + backfill the 890 rows as UNKNOWN, then
   one full run decides what is genuinely open. Report before/after counts.
4. Standing rule: `encoding="utf-8"` as a CLAUDE.md hard rule + a self-enforcing
   `missing_encoding` checker, rule-12 proven **both** directions.
5. C1–C3, then C4 `checker_health`.
6. Part D — one scheduled task, run records written even on a clean run.
7. The rule-12 demonstration this order names specifically: **deliberately break
   a checker and prove it yields UNKNOWN, not a wave of CLOSED.**

Filing an update as each lands. I will not report Path C complete on a run that
verified nothing.
