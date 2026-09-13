# PROCEDURE — the after-action report. One page, and the boundary that keeps it from becoming a second rule file.

    from     C1, architecture, 2026-09-12
    ordered  Sleven: "I want an AAR skill in the stack so Code, C1, Grok, Echo and
             CIC stop paying the same lesson twice."
    status   PROCEDURE. Written before any skill is installed, as ordered.

---

## WHEN AN AAR RUNS

**After a failure that cost real time or reached the live site, and after a job that went
unusually well.** Not after every letter, not on a timer, and never as a ritual attached to
closing work — a report nobody needed is the thing that makes the next one skipped.

**A desk may run one on itself. Any desk may ask another to run one. Architecture may order one.**

## THE FOUR QUESTIONS, AND NOTHING ELSE

    1  What was supposed to happen?
    2  What actually happened?
    3  Why was it different?
    4  What do we do differently, in a form somebody can check?

**Question 4 is the whole point and it is where these usually fail.** "Be more careful" is not an
answer. **"Before asking Sleven for a manual step, list what you checked" is**, because a reader
can look at a letter and tell whether it was done.

**Anything that cannot be checked by looking at an artefact does not go in.**

## THE BOUNDARY — AND THIS IS THE PART I AM ADDING, NOT RECEIVING

**A lesson that is a RULE goes in `CLAUDE.md` and nowhere else. A lesson that is NOT a rule goes in
`claude/LESSONS.md` and nowhere else.**

**They are told apart by one test: would a desk breaking it be wrong, or just slower?**

    wrong    -> a numbered rule in CLAUDE.md
    slower   -> a lesson in LESSONS.md

**Tonight's four failures split cleanly, which is the argument for the boundary:**

- **Owner-ask gate** — breaking it is wrong. **Rule 27. Already done, and the AAR would only have
  confirmed it.**
- **The mail spine uncommitted for weeks** — breaking it is wrong. Rule 2's own territory. Done.
- **CURRENT-STATE wallpaper** — that is a control change, not a rule and not a lesson. **Some AAR
  outputs are neither; they are jobs.** The report says so and orders the job.
- **"I ran three full directory listings while writing a finding about read costs"** — nobody was
  wrong. It was wasteful. **That has nowhere to go today, and it is exactly what LESSONS.md is
  for.**

**WHY THE BOUNDARY IS NOT OPTIONAL.** This project has paid three times in one week for a document
living in two places, and twice tonight I refused to create a second record on those grounds. **A
lessons file that accumulates rules IS a second rule file**, and the split proposal for
`CLAUDE.md` exists because the first one already outgrew itself. **If a line in LESSONS.md ever
reads like a rule, it is moved to CLAUDE.md and deleted from LESSONS.md the same day.**

## LESSONS.md IS FINITE, AND THAT IS ALSO NOT OPTIONAL

**An append-only lessons file becomes `NEXT.md`: 272,897 bytes nobody reads.**

- **A lesson is retired when the thing it warns about becomes impossible** — absorbed into a rule,
  a control, or a tool that cannot do the wrong thing. **Retirement is deletion of the line, with
  the AAR that raised it named in the commit.**
- **A lesson nobody has needed in three months is reviewed**, not automatically kept.
- **The file carries a stated cap.** When it is reached, the answer is retiring lessons, never
  raising the cap.

## THE HARD CONSTRAINTS, TAKEN AS ORDERED

1. **Proposal first.** An AAR never edits `CLAUDE.md`, a skill or a checklist. **It proposes, and a
   person approves.** Same rule as the auditor: flags only, never fixes.
2. **No open web.** An AAR reads this project's own record and nothing else. It does not research
   the failure, and it does not rewrite the corpus.
3. **One `claude/LESSONS.md`, pointed at from `CLAUDE.md`.** Read before similar work, not at every
   boot — a file every desk loads unconditionally is the 115,000-token defect again.
4. **The Owner-ask gate applies to AARs.** An AAR concluding "we should have asked Sleven" runs rule
   27 before it asks him anything.
5. **Echo gets the four questions as a brief section**, not a skill she cannot load. **Same four
   questions, same checkable-answer standard.**

## WHAT AN AAR IS NOT

**Not a postmortem document.** Not a narrative of the incident — the findings and memos already
hold that, and duplicating them is how this project grew 896 documents.

**Not blame, and not absolution either.** "Whoever wrote it remembered" is this project's own name
for a rule keyed to a proxy. **An AAR whose answer is that somebody should have been more careful
has not finished.**

**And not a replacement for the finding.** A finding records what was true. An AAR records what we
do differently. **They are different files and neither one substitutes.**

## THE FIRST ONE

**The last 48 hours, as ordered: the uncommitted mail spine, the Owner-ask failures, the
CURRENT-STATE wallpaper, and two design desks.**

**It runs once `LESSONS.md` exists and not before**, because an AAR with nowhere to put its output
is a memo.

**And it should expect a thin result.** Three of those four already became a rule, a commit and a
control change within hours. **If the first AAR produces one real lesson and confirms three things
we already fixed, that is the correct outcome and not a disappointment** — it is the report telling
us the machine is already converting failures, which is what we wanted to know.

*C1, 2026-09-12. Nothing installed, nothing built.*
