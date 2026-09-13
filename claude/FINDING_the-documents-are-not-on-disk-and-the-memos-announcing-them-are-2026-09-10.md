# FINDING — the documents are not on disk, and the memos that announce them are

**Filed 2026-09-10 by the Adjutant desk. Proved by the Owner, on his own machine, with
a tool installed an hour earlier. Nothing has been changed.**

---

## WHAT WAS PROVED, AND HOW

The Owner opened the entire repository as an Obsidian vault and searched it for four
document names taken from the claude.ai project's own index.

**Every search returned hits. Not one hit was the document.** Every result was a
**memo** that *mentions* the document's path.

    disagreement-contract   3 hits   all memos quoting
                                     `claude/DESIGN_the-lens-is-a-disagreement-contract-2026-09-08.md`

    held-out-run            4 hits   all memos quoting
                                     `claude/VERIFIED_the-held-out-run-94-8-percent-2026-09-08.md`
                                     one of them: "now opens with it —"

    watch-rsi               3 hits   one of them: "`watch-rsi-state.md` is overwritten"

    keeps-reinventing       1 hit    a memo reading:
                                     "done. `claude/FINDING_this-project-keeps-reinventing-
                                      the-same-idea-2026-09-08.md`"

**THE LAST ONE IS THE WHOLE FINDING IN ONE LINE.** A desk reported *done*, named the
document it had filed, and that report is on disk today. **The document it names has
never been on disk at all.**

**Checked and not found in:** `citizen-compass\claude\`, `citizen-compass\docs\`,
`citizen-compass\design\`, `Looking Project\` (recursive), `CCDesk-logs\looking-project\`
(empty).

## THE MECHANISM, AND IT IS WRITTEN INTO THE PROJECT'S OWN INSTRUCTIONS

From the claude.ai project instructions, active today:

> "When you produce something durable — a decision, an audit, a handoff — write it to
> the project with `project_write`."

**It says write it to the project. It does not say write it to disk.**

Every session has been following that instruction correctly for months. **This desk
followed it tonight.** The document goes to the cloud; the memo announcing it goes to
the tray on disk; the two are never reconciled because nothing reconciles them.

**A desk reading the repository can see the announcements. It cannot see what was
announced.**

## WHY IT WENT UNSEEN FOR SO LONG

**Because searching the repository FINDS SOMETHING every time.** A grep for a document
name returns memos that quote it, in backticks, looking exactly like a path that
resolves. **Nothing ever comes back empty**, so nothing ever looked wrong.

**This is the project's signature defect in its purest form: the failure is real,
something plausible is returned, and nobody is told.**

## WHAT IT COST, ALREADY, TWICE

**2026-09-10.** Build sat idle nine and a half hours because the doorbell design had
been filed to the project and never to disk. It searched by exact name, by pattern,
and by content, found nothing, and correctly refused to build against memos.

**The same day.** An Architecture document cost roughly ten hours for the same reason.

**Both were treated as single incidents.** Charter rule R20 was written from the first
one — *anything a desk must execute against goes on disk*. **The rule was right and the
diagnosis was too small.** It is not an incident pattern. It is the default behaviour
of the instruction.

## THE SCALE IS NOT YET KNOWN AND SHOULD NOT BE GUESSED

    claude.ai project      850 documents
    citizen-compass\claude\ on disk    26 files

**Those two numbers are not directly comparable** — the project's paths are its own
labels, and some project documents plainly correspond to files living elsewhere on
disk under other names. **An earlier estimate of "about 820 missing" was made from
that comparison and is withdrawn as unfounded.**

**What IS established: four documents chosen at random from the project index are not
on disk anywhere, and one of them has a completion report on disk that names it.**

**The count needs an audit, not an estimate.**

## THE FIX IS TWO PARTS AND THE SECOND ONE MATTERS MORE

**1. RECOVER.** Audit the project index against the disk, produce three lists — in
both, project-only, disk-only — and pull the project-only documents down. **Nothing is
lost; every one of them is still in the project.**

**2. CHANGE THE INSTRUCTION, OR THE NEXT EIGHT HUNDRED DO THE SAME THING.** The
project instruction must say that a durable document is written to DISK, and the
project copy is a mirror of it. **Disk is the record; the project is the view.**

**Doing part one without part two is the version of this that gets done twice.**

**The instruction is the Owner's to change.** It lives in the claude.ai project
settings, not in the repository, and no desk can reach it.

## WHAT THIS DOES NOT CHANGE

Nothing built, nothing moved, nothing deleted, no instruction edited. **The switch is
out, automation is fail-closed, and the build order is untouched.** This does not delay
the brakes.
