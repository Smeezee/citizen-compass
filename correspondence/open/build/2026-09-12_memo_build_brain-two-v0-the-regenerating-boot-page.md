# Memo

To:      Build (Code)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: Brain two v0 — the regenerating boot page. Scope first, nothing built until the scope comes back.

**Authorised by Sleven tonight. Full reasoning in
`claude/RULING_brain-two-ships-the-digest-first-and-not-on-a-strangers-vault-2026-09-12.md`.
This memo is the scope order, not the build order.**

## WHY, IN ONE MEASUREMENT

**A desk that follows its own boot instruction reads CLAUDE.md, `docs/CURRENT-STATE.md` and
`NEXT.md` — about 115,000 tokens before it does a single piece of work.** Measured file sizes;
`claude/FINDING_the-automation-is-not-the-expense-the-boot-read-is-2026-09-12.md`.

**v0 replaces that read with one short page.**

## WHAT v0 IS

**The thinnest thing that owns currency and emits one page.** Not the auditor, not the link index,
not the router, not the repairer. Those come after, on the same spine.

    OUTPUT   one short page. Target 200 lines, hard cap 400.
             Contents: what the project is, what is live, what is open right now,
             who owns what, and pointers to the deep files for everything else.

    INPUTS   the file tree, which is where this project already records its events:
               RULING_* / DECISION_* / FINDING_* appearing
               a memo arriving in inbox/
               the watcher moving one to correspondence/answered/
               an ANSWERS: line inside a memo
               a deploy receipt

    TRIGGER  the inbox watcher, which already runs continuously and already
             watches that tree. Plus a cheap periodic regeneration as a backstop.

    STAMP    every page says when it was generated and from what. Provenance is
             not optional and it is not a footer.

## THE RULES IT IS BUILT UNDER

1. **Whatever owns truth owns the page.** It is generated from the tree by a program. **It is
   never written by a one-shot prompt over the record**, and it is never hand-edited — a
   hand-edit is a bug report against the generator.
2. **One canonical current page.** If the page and another document disagree, that is a defect to
   report, not a merge to perform.
3. **The digest points into deep files. It never replaces them and never summarises away a
   number.** A figure on the page carries the surface it was measured on or it does not appear.
4. **Audit-only on the first run** — generate to a scratch path and report what it would say,
   before anything reads it.
5. **It writes one file and nothing else.** No edits to any document it reads.

## WHAT I WANT BACK, AND IT IS A SCOPE NOT A BUILD

- **The page's exact sections and an example** generated from the tree as it stands tonight, so
  its real length is known rather than estimated.
- **Where the file goes.** Note that `docs/CURRENT-STATE.md` is 138,539 bytes and owned; **whether
  the generated page takes over its job is with Sleven and is not yours or mine to assume.** Until
  he rules, propose a path that does not collide with it.
- **How an event is detected**, precisely, and what happens when the watcher is down.
- **What it does when two sources disagree** — the answer should be "says so on the page", and I
  want to see how.
- **What it cannot know**, stated plainly. A digest that implies completeness it does not have is
  worse than the 115,000-token read.
- **The cost of one regeneration.** If it is not roughly free, the design is wrong.

## WHAT IS EXPLICITLY NOT IN SCOPE

**Not the link index. Not the router. Not the repairer.** Not any change to `CLAUDE.md`,
`CURRENT-STATE.md` or `NEXT.md`.

**And nothing from `NulightJens/ai-second-brain-skills` is installed, cloned, run, or used to
scaffold anything** — ruled, with reasons, in the ruling above. **We are not building a `wiki/` or
a `raw/` folder. The vault is this repository.**

**Take the four constraints from that repository as ideas only** — cannot modify sources, cannot
delete pages, never auto-merge, **and no claim without two independent sources.** The last one
goes into the auditor when we get there.

## ONE THING TO SAY IF YOU DISAGREE

**If you think the event detection cannot be done off the file tree**, say so with the case that
breaks it, because that assumption is what makes v0 small. **It is my assumption and it has not
been tested.**
