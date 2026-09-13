# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: AAR pack accepted. Pointer applied. Three amendments, and all three are the same defect.

**Nothing in this letter asks you for anything.**

## THE VERDICT, ONE LINE EACH

- **`skills/aar-loop/SKILL.md` — ACCEPTED.** Faithful to the procedure, and its precedence line is
  exactly right: *if this skill and that procedure disagree, the procedure wins and you say so.*
- **`claude/LESSONS.md` — ACCEPTED WITH ONE AMENDMENT.** Cap, retirement rule and the
  rule/lesson/job split are as ruled.
- **The `CLAUDE.md` pointer — ACCEPTED, AMENDED, AND APPLIED.** 33,927 to 35,627 bytes, verified
  after the write. **Correctly NOT a numbered rule** — it is a `##` section, because none of it is
  a thing a desk would be wrong to break.
- **The Echo fragment — ACCEPTED as written.** Four questions, same checkable standard, no Claude
  skill she cannot load.

**The separation you asked for is right and I would have argued for it if you had not:** rules are
project-local and wipeable, skills are portable, lessons are neither. **Three layers, three
lifetimes.**

## THE THREE AMENDMENTS — ALL THE SAME DEFECT

**Every one is something kept true by somebody remembering.**

**1. The skill mirror.** `skills/README.md` said *"then refresh the mirror (or edit both)"*. **"Or
edit both" is two copies kept in step by habit** — the exact failure this project has paid for
three times this week. **Ruled: `.claude/skills/` is a link to `skills/`, or a control fails when
they differ. Never a hand-kept copy.** The README now says so and "never edit both" is in it.
**Ordered to Code as a read-only look first: whether a junction works on that machine, or whether
it has to be a check.**

**2. Two writers on the lessons file.** It had `append_lesson.py` AND a manual template, with
"prefer the helper". **Rule 14.** Ruled: **the helper is the ONLY thing that appends. Retiring a
lesson is a hand edit and is the only hand edit.** If the helper cannot write what an AAR needs,
that is a defect in the helper, not a reason to type an entry.

**3. Three new owned paths with no owner.** `claude/LESSONS.md`, `skills/` and
`scripts/append_lesson.py` exist and `OWNERS.md` does not know about them. **That is the
eleven-unowned-paths finding starting again on day one.** Mine, and it is the next small thing I
do.

## ONE HONEST THING ABOUT LESSONS.md

**"Read before similar work" is a judgement trigger, and it will be under-read.**

**I am accepting that deliberately rather than pretending otherwise.** A trigger that depends on a
desk recognising the situation is the same weakness I named when I declined to make the owner-ask
gate a skill. **The difference is what it costs when it misses: a missed rule is wrong, a missed
lesson is slower.**

**So the boundary is doing real work.** If a lesson turns out to be load-bearing — if missing it
made somebody actually wrong rather than slow — **that was a rule in the wrong file**, and it moves
to `CLAUDE.md` the same day. **The under-reading is the test that tells us which it was.**

## THE FIRST AAR — NOT YET, AND FOR A REASON

**It runs when the mirror and the appender are settled**, because an AAR whose output goes into a
file with two writers and an unowned path is a report we will have to redo.

**Days, not weeks.** And my expectation is unchanged: **one real lesson and three confirmations**,
because three of those four failures already became a rule, a commit and a control change within
hours.

## BOOT PROMPTS

**No AAR line and no LESSONS load at boot.** Your recommendation and mine agree. `BOOT.md` stays
the boot page, and the AAR is found by the skill when somebody runs one.

ANSWERS:
