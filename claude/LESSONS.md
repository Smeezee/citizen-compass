# LESSONS.md — checkable habits that are not rules

    owner     Architecture (C1) maintains; any desk may append via an AAR
    procedure claude/PROCEDURE_the-after-action-report-2026-09-12.md
    skill     skills/aar-loop/SKILL.md (mirrored at .claude/skills/aar-loop/)
    helper    scripts/append_lesson.py

**This is NOT a second CLAUDE.md.** Project-local. Do not export this file as a universal skill.

- Breaking a **rule** is wrong → numbered entry in `CLAUDE.md` (AAR proposes; apply only on approval).
- Being **slower / wasteful** without being wrong → a lesson here.
- A **control or job** → order the job; do not park it here as a fake lesson.

**Read before similar work**, not at every boot. `BOOT.md` stays the boot page.

## Cap (not optional)

- Soft cap: **40 active lessons** or ~12,000 bytes of lesson body, whichever comes first.
- When reached: **retire**, never raise the cap.
- Retire when the failure becomes impossible (rule, control, or tool). Name the AAR/ruling in the commit or letter.
- Unused for **three months** → review (keep, retire, or promote to a rule proposal).

## Active lessons

_None yet. First AAR (last 48 hours) may add a few — expect most of that night to already be rules/jobs._

## How this file is written - ONE APPENDER, ruled 2026-09-12

**`scripts/append_lesson.py` is the ONLY thing that appends a lesson.** Not "preferred" - the only
one. If it cannot write what an AAR needs, that is a defect in the helper and it gets fixed; it is
never a reason to hand-write an entry.

**Retiring a lesson is a hand edit, and it is the only hand edit this file takes.**

**Two writers appending to one file is how its format diverges until nothing can read it** - rule
14, applied here.

## Template - for reading the format, NOT for writing by hand

Fields the helper writes:

- date + short title
- expected / actual / why / next time / tags
- fix-proposed / fix-applied


## Retired

_None._
