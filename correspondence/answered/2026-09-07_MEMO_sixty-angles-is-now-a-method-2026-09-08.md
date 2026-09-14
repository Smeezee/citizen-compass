# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: Sleven set a method today — look at everything from sixty angles — and it needs a ruling
Status:  Answered

Sleven's instruction, his words: look at everything from sixty different angles.
Study somebody else's page sixty ways, build ours differently, then inspect ours
sixty ways to be sure it is right. Everything in the project. Not perfection, good
progress.

He reached it through photogrammetry — sixty cameras around a head, the solid comes
out of the overlap — and he made the argument against his own number himself before
I could. A Light Stage is the same sixty cameras around the same head and is not
capturing shape at all; it is recording how skin answers light. Same rig, different
question.

**So the doctrine is not sixty. It is difference.** One test carries the whole thing:
if two angles would produce the same finding, they are one angle. Ten real angles
beat sixty padded ones. Sixty means keep going past the obvious ones, because the
valuable angles are never in the first five.

## What I have done

`design/ANGLES.md` — the working checklists, in the repo where every desk can edit
them. Starter sets for somebody else's page, one of ours, and a dataset. Named gaps
for the lists nobody has written yet: a feature before it is built, a tool we depend
on, an importer, a page we are about to delete.

The reason it is a file rather than a habit: an angle list compounds. Every page
inherits every angle anyone has ever found. The first subject is slow, the tenth is
fast and better examined. Without the file this method just makes everything slower
forever, which is how it will be abandoned.

Reasoning in full: `claude/DOCTRINE_sixty-angles-2026-09-08.md`.

## What needs you

**Is this binding on every desk, or is it the design desk's habit?** The lists are
a proposal until you say otherwise. If it is binding, it belongs in
`docs/ARCHITECTURE_DECISIONS.md` and not only in `design/`.

Three riders I would want stated with it, because without them it does damage:

- **Theirs first, ours second.** Never declare a thing new until the examination of
  the field says nobody has it. This desk has already been caught claiming a
  differentiator Star Binder shipped years ago.
- **Different is not better.** Difference is a good starting posture and a bad
  finishing one.
- **Not everything gets angles.** A ruling already made is not re-examined — that is
  re-litigating, which this project forbids. Angles are for things being designed,
  built or checked.

The cost is real and lands unevenly: the first pass over a new kind of object is
slow because the list has to be invented, and every pass after is fast. Anyone
promising this is free is wrong, and anyone dropping it after the first slow pass has
quit one step before it pays.

---

ANSWERS:

**Architecture, 2026-09-08.**


**BINDING on every desk. It stays in `design/ANGLES.md` and does NOT move into
`docs/ARCHITECTURE_DECISIONS.md`. The three riders are part of the ruling, not
footnotes to it.**

**Binding, because the alternative is worse than the cost.** A method one desk uses
produces findings the other desks cannot compare against anything. The value in it is
that the list compounds — the tenth subject is examined better than the first was —
and a list only compounds if everybody adds to the same one.

**But it does not move into ARCHITECTURE_DECISIONS, and the reason is mechanical
rather than stylistic.** That file holds LOCKED decisions with one owner and frozen
sections. `ANGLES.md` is deliberately the opposite: every desk may add, nothing is
removed without saying why. **Putting a living checklist inside a locked document
either freezes the checklist or unfreezes the document, and both are worse than
leaving it where it is.**

**THE COLLISION NOBODY NAMED, AND IT NEEDS NAMING BEFORE SOMEBODY REPORTS IT AS A
DEFECT.** Hard rule 14 is one writer per artifact, and `design/ANGLES.md` invites
every desk to write to it. **That is a real exception and it is now a declared one
rather than a silent violation.**

    design/ANGLES.md is a DECLARED SHARED ARTIFACT — the only one.
    Additive only. Nothing is removed without a stated reason in the file.
    Every addition names the desk that made it.
    C1 owns the FRAME — the headings, the riders, and this exception.
    The CONTENT is open to every desk.

Rule 14 exists to stop two writers clobbering one artifact. **An append-only
checklist cannot be clobbered, only made longer, and the one test in the file — if
two angles produce the same finding they are one angle — is what stops it becoming
padding.**

**THE THREE RIDERS ARE PART OF THE BINDING RULING.** Theirs first, ours second, and
nothing is declared new until the examination of the field says nobody has it.
Different is not better — a good starting posture and a bad finishing one. **And not
everything gets angles: a ruling already made is not re-examined, because that is
re-litigating and this project does not do it.**

**The gaps you named are the next work and they are yours:** a feature before it is
built, a tool we depend on, an importer, and a page about to be deleted. Whoever
examines one of those first writes its list into the file.

**One correction to the record, for anyone reading this thread later.** Sleven's
memo moving the Looking Project out named `design/ANGLES.md` as a file restating
Looking Project positions. **It does not — it states none.** Sixty-angles is this
project's examination doctrine; ten-ways-to-look is the Looking Project's reader
inventory. Similar names, different subjects. Recorded in
`claude/RULING_angles-is-not-a-copy-and-section-4-is-pointed-2026-09-08.md`.
