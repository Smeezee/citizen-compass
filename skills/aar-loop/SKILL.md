---
name: aar-loop
description: Run a Citizen Compass after-action review (AAR) after friction, failure, or unusually good work. Four Army-style questions, checkable lessons only, propose rule/skill edits never silent apply. Use when the user or desk says aar, after action, retro, what did we learn, debrief this session, or after a costly mistake.
---

# AAR loop

Portable skill. On Citizen Compass, follow `claude/PROCEDURE_the-after-action-report-2026-09-12.md` when that file exists. **If this skill and that procedure disagree, the procedure wins** and you say so.

On a fresh project without that procedure, use the workflow below alone; keep the hard constraints.

## When to run

- After a failure that cost real time or touched a live/testing surface.
- After a job that went unusually well (lock in what worked).
- When ordered by architecture/owner, or another desk asks for one.
- **Not** after every task. **Not** on a timer. **Not** as a closing ritual.

## Hard constraints (fail closed)

1. **Propose only.** Never edit rules files (`CLAUDE.md` / `AGENTS.md`), skills, or checklists unless the user already said apply/fix for **this** AAR.
2. **No open-web self-heal.** Use the project's own record. Do not rewrite a corpus from the internet.
3. **Lessons file is separate from rules.** Project-local lessons (on CC: `claude/LESSONS.md`). Never turn LESSONS into a second rule file.
4. **Owner/human-ask gate still applies** if the project has one: check approved paths before dumping chores on the human.
5. **Not a finding substitute.** Findings = what was true. AAR = what we do differently.
6. **Not a second brain.** Does not replace auditors, routers, boot digests, or mail.

## The four questions (in order)

1. What was supposed to happen?
2. What actually happened?
3. Why was it different? (mechanism, not mood)
4. What do we do differently, in a form somebody can check?

Question 4 fails if the answer is "be more careful." Passes if a reader can look at an artefact and tell whether it was done.

## Classify each output

| Test | Destination |
|------|-------------|
| Breaking it would be **wrong** | Propose a rule edit — do not only journal it |
| Breaking it would only be **slower** | Append to the project's LESSONS file |
| It is a **control/tool/job** | Name the job — do not fake a lesson |

## Workflow

1. Answer the four questions briefly.
2. Extract 0–3 checkable lessons. Zero is valid.
3. Dedup against existing lessons.
4. Present a numbered **FIX PLAN** before any edit. Wait for approval unless invoke said apply/fix.
5. Append lessons (on CC: `python scripts/append_lesson.py` or the template in `claude/LESSONS.md`).
6. Report: four answers, lessons written, fix plan status, paths.

## Citizen Compass paths

- Procedure: `claude/PROCEDURE_the-after-action-report-2026-09-12.md`
- Lessons: `claude/LESSONS.md`
- Helper: `scripts/append_lesson.py`
- Echo (no Claude skills): `claude/PROMPT_aar-four-questions-for-echo.md`
