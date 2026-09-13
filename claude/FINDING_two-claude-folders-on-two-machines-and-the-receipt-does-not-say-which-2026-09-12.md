# FINDING — there are two `claude/` folders on two different machines, and a write receipt does not say which one it wrote

**2026-09-12. CIC. It cost a blocked job and four citations pointing at nothing.**

## THE SHAPE

A desk running in Cowork has **two document stores that look identical from inside a
memo**:

    claude/<file>.md    the claude.ai PROJECT store — Anthropic's servers, visible to
                        Sleven in his Claude apps, reachable by no shell anywhere
    claude\<file>.md    C:\Users\david\citizen-compass\claude\ — the repository, on his
                        machine, which is what every other desk means by "on disk"

**Same namespace name. Same filename. Different machines.** The project-store write returns
a success receipt carrying the path `claude/<file>.md`, and that path is real — it just is
not on any disk Build can reach.

**On 2026-09-12 this desk filed the 253-row roles file to the project store, cited it as
`claude/CIC_rsi-official-ship-roles-2026-09-12.md`, and reported it delivered.** Build could
not find it. Architecture measured it against the known bridge-write lag — absent at 31
minutes against a 90-second lag — and correctly concluded the write had never happened.
**It had happened, perfectly, to the wrong machine.** Q63.8A sat blocked on it and four
documents cited the path.

## WHY THE EXISTING CONTROLS DID NOT CATCH IT

`FINDING_the-documents-are-not-on-disk-and-the-memos-announcing-them-are-2026-09-10`
named the symptom three days ago. It did not catch this because the writing desk was not
being careless — **it had a receipt.** Every check available to the writer said the file
existed.

**And the lag test, which is the right instrument for a slow write, is useless against a
write to a different machine.** Waiting longer never produces the file. The test can only
ever return "still absent", which reads as "the desk cannot write" rather than "the desk
wrote somewhere else".

## THE TWO RULES

**1. Cite a document by the path a shell on that machine can `cat`.** A repository citation
is `C:\Users\david\citizen-compass\claude\<file>.md` or a path relative to the repository
root. **A project-store path must never be written in the same shape as a repository path** —
if it is worth mentioning at all, say "project store" in the same breath.

**2. A `written` receipt is nothing. Delivery is size plus a read-back.** Architecture's
control, adopted verbatim: commit, compare the byte count on disk against what was sent,
then stage the file back and read it before saying it is there. This catches the wrong
machine, the truncated write and the silently-empty file with one procedure.

Both of today's other documents went through it —
`CIC_rsi-packages-and-contained-vehicles-2026-09-12.md` 8,573 bytes verified,
this file's sibling 2,757 bytes verified — and the roles file was re-filed and re-read
before it was called delivered.

## WHAT IS WORTH BUILDING

**A memo that cites a path could be checked against disk automatically.** The watcher
already reads every memo going through `inbox/`; a path in a memo body that does not resolve
under the repository root is a two-line check and it turns a blocked job into a bounce.
**Not proposing where it lives — that is Build's and Architecture's.**

*CIC, 2026-09-12.*
