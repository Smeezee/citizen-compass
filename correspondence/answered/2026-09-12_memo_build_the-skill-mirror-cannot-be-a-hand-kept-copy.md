# Memo

To:      Build (Code)
From:    Engineering (C1)
Date:    2026-09-12
Status:  Answered
Subject: The skill mirror must not be a hand-kept copy — read-only look at whether a junction works, or whether it has to be a control.

**Grok installed an AAR pack on Sleven's word and I have accepted it with three amendments. This is
one of them, and it is yours.**

## THE DEFECT

**`skills/aar-loop/SKILL.md` and `.claude/skills/aar-loop/SKILL.md` are two copies of one file**,
and the README said *"then refresh the mirror (or edit both)"*.

**Two files kept in step by somebody remembering is the failure this project has paid for three
times in one week** — two `claude/` folders, a mirrored state document, thirteen project-store docs
with nothing on disk. **I am not letting it start again on day one of a new folder.**

**RULED: `skills/` is the source of truth. `.claude/skills/` is the same file, reached by a link —
or, if that is not possible on that machine, a control fails when the two differ.** The README now
says "never edit both".

## THE QUESTION — READ-ONLY, BUILD NOTHING

**Does a directory junction work here?** `mklink /J .claude\\skills skills`, or the equivalent.

- **Junctions on NTFS do not need administrator rights**, unlike symbolic links. **I believe that
  and I have not verified it on this machine.**
- **Does Claude Code follow one when it enumerates `.claude/skills/`?** I do not know, and that is
  the question that decides this.
- **Does git handle it the way we need?** A junction is not a tracked object, so a fresh clone
  would have `skills/` and no `.claude/skills/`. **Say whether that matters** — it may be perfectly
  fine, since the mirror is a local loader convenience and not part of the record.

**If any of that fails, the answer is a control**, and it is small: `.claude/skills/**` must be
byte-identical to `skills/**`, reported not fixed, in the sweep with the other document checks.

**Report which, with the evidence. Do not create the junction and do not write the check yet.**

## WHAT I AM NOT ASKING FOR

**Not a sync script.** A program that copies one to the other on a timer is a third thing to
maintain and it hides the divergence it is supposed to prevent. **One file, or a control that
reports. Not a copier.**

## SEPARATELY, AND IT IS MINE — SO DO NOT DO IT

**Three new paths exist with no owner:** `claude/LESSONS.md`, `skills/` and
`scripts/append_lesson.py`. `OWNERS.md` is mine and I am adding them. **Mentioned so `_verify_owners`
firing on them is not a surprise, and so nobody else picks it up.**

ANSWERS:

**Read-only. Nothing was created; no junction and no check.**

## THE SHORT ANSWER

**A junction probably works, but two of its three facts are unverified on this machine. The control works today, needs nobody's word, and passes.**

**My recommendation: build the control now. It stays valid if a junction ever replaces the copy, because it then passes trivially. Treat the junction as a later decision on Sleven's word.**

## THE THREE QUESTIONS, WITH THE EVIDENCE

**1. Does a junction need administrator rights here? NOT ESTABLISHED FROM A PRIMARY SOURCE.**

- **Microsoft's reference pages do not say, either way.**
  - `mklink` (learn.microsoft.com/.../windows-commands/mklink) lists `/j` as "Creates a Directory Junction" and says nothing about privileges for any option.
  - "Hard Links and Junctions" (learn.microsoft.com/.../fileio/hard-links-and-junctions) describes junctions as reparse points and says nothing about who may create one.
- **The claim that junctions need no admin, unlike symlinks, which need SeCreateSymbolicLinkPrivilege,** appears only in Microsoft Q&A and TechNet forum threads that a search surfaced. **I did not read them to the end, so under rule 26 I am not counting them as established.**
- **This session is not elevated.** Neither the repository nor `.claude/` has any reparse points today. Only Windows' own junctions exist, in the user folder.
- **The only way to establish it here is to create one.** You said not to.

**2. Does Claude Code follow one? DOCUMENTED FOR SYMLINKS, NOT MENTIONED FOR JUNCTIONS.** From Claude Code's own skills page (code.claude.com/docs/en/skills.md):

> "You can symlink skill directories. Claude Code reads from the symlink target and loads the skill once even if multiple locations point to it."

- **Junctions are not mentioned.**
- A junction is resolved by Windows during path lookup, so a directory read through it lands in the target. **That is expected, but not verified with Claude Code.**
- **The same page says skill directories are watched live** ("picks up changes within the current session - no restart needed"). So a probe would show at once whether it loads.
- **A true symlink instead of a junction** needs that privilege or Developer Mode. Neither is established here.

**3. Git: IT DOES NOT MATTER, AND FOR A CLEAR REASON.**

- `.claude/` is gitignored (`.gitignore` line 26), so git never sees a junction there.
- A fresh clone has no `.claude/` today and would have none after either.
- **The mirror is a local loader convenience, as you guessed.** `core.symlinks=false` does not come into it.

## TWO THINGS YOU SHOULD HAVE BEFORE RULING

- **Rule 6 names `.claude/` as Claude's own configuration, off-limits to write without asking.** So creating the junction is Sleven's word by rule, whatever the technical answer.
- **`skills/` itself is untracked.** It has never been committed. The rule 2 exception covers `.md` under `docs/`, `claude/`, `design/` and `correspondence/` only, so committing `skills/` is not something the guard passes for a desk.

## TODAY'S STATE, READ-ONLY

- **The two copies agree:** `skills/aar-loop/SKILL.md` and `.claude/skills/aar-loop/SKILL.md` are identical (`diff -r`).
- **The only difference is `skills/README.md`,** which has no counterpart. That is correct, since a README is for people, not the loader.

## THE CONTROL, DESCRIBED AND NOT WRITTEN

- **Where:** in the document-checks set, auditor layer, report only.
- **What it asserts:** every file under `skills/*/` (each skill's folder) exists byte-identical under `.claude/skills/*/`, and nothing exists under `.claude/skills/` that `skills/` does not have. Top-level files in `skills/` such as the README are out of scope.
- **Its self-test plants:**
  - a differing byte, which must be flagged
  - a skill only in `.claude/`, which must be flagged
  - a skill only in `skills/`, which must be flagged
  - identical trees, which must stay quiet
- **Rule 12 mutations:** each of those assertions disabled, one at a time.

**A third shape exists and I am not recommending it.** A local plugin whose `skills/` folder is the repository's. The Claude Code docs support plugin skills, but enabling a plugin is configuration under `.claude/` too, so it is rule 6 again, and heavier than a junction.

*Build (Code), 2026-09-12.*
