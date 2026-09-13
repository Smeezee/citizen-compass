# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: The skill pack you built to be portable has never been committed. One ask, and one thing that can wait.

## ALREADY CHECKED

**Asked of Build, read-only, answered today. Nothing was staged, created or committed to find out.**

- **Does the documentation exception cover `skills/`?** **No.** The guard hard-codes it to tracked
  `.md` under `docs/`, `claude/`, `design/` and `correspondence/`. `skills/` is none of those, and
  it is untracked — never committed at all.
- **Does an existing order of yours cover it?** **No.** This morning's commit ruling named
  `watcher-go`, `pkg/apikeyguard` and `go.work` exactly.
- **Can Architecture order it instead?** **No.** Same guard, same answer as this morning: the only
  route past the hook is `--no-verify`, reserved for your hand.

## THE ASK

**Commit `skills/` so the portable pack survives the disk it lives on. No push.**

## WHY IT IS WORTH ONE MINUTE

**You built `skills/` specifically so a rewrite of `CLAUDE.md` could not destroy it, and so you
could carry it to other projects.** It currently exists in one place on one machine and in no
history. **Same shape as the mail spine this morning: the thing designed to be durable is the thing
with no copy.**

**Small — one folder, two files.**

---

## SEPARATELY, AND IT CAN WAIT

**The `.claude/skills/` mirror.** Code checked and could not establish from Microsoft's own pages
whether a directory junction needs administrator rights — the reference pages are silent, and he
declined to count forum threads as established, which was correct. **He could only settle it by
creating one, which I had told him not to do.**

**But the technical question turned out not to be the blocker.** **Rule 6 makes `.claude/` your
word regardless**, since it is Claude's own configuration.

**So: a control gets built now** — it checks the two copies are byte-identical and reports when they
are not. **It stays correct if a junction ever replaces the copy, because then it simply passes.**

**The junction itself is yours, and there is no hurry:** the two copies are identical today,
verified, and the control will say so the moment they are not.

---

## ONE THING WORTH THIRTY SECONDS OF YOUR ATTENTION

**The record auditor — the thing you ordered this morning as B1 — ran on today's tree and its first
finding was in `CLAUDE.md`.**

**Rule 27, written this morning, cited a letter path that does not exist.** Corrected, verified.

**A tool built to find dead citations found one on its first run, in a rule written hours earlier,
in the file that governs every desk.** That is the argument for building it, and nobody had to
make it.

ANSWERS:
