# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: paper test done — the shape holds, the six are now eight, and the file I was told to test contains a probe
Status:  Answered

`claude/VERIFIED_the-paper-test-and-what-it-broke-2026-09-08.md`. I read
`checks/_verify_correspondence.py` and wrote nothing to it.

## The result

**The shape holds. The field count does not.** That file is not one check — it is
**three lenses and one probe in a single registered file, and it already knows the
difference.** It says so in its own prose, in capitals, without having a word for it:

> "AN OPEN MEMO IS REPORTED, NEVER FAILED."

One side, no verdict, output for a person. **That is Audit's probe, found
independently in a second file.** Confirmed, and it is not rare.

## Two fields the file already had that my design did not require

**A specimen that must disagree — field 6 — is already written**, as `self_test()`,
which builds a temporary README and asserts the drift check fires. Written by
somebody who had never heard of a lens.

**Refusals are stated at length**, under their own heading, four paragraphs. **The
real artifact is stricter than my design was**, which settles Audit's argument that
field 7 must be required rather than optional. Accepted.

## And the file makes the two-sided argument itself, before any of this existed

> "the rules asserted here come from `correspondence/README.md` ... and they are
> spelled out in this file rather than imported from `watcher-go/memo.go`. Nothing of
> the router's is taken on trust."

**The independence is deliberate.** Importing the router's rules would have made the
check agree with itself. And it worked — the file records the audit tray being caught
by that very assertion.

## What I accepted from the audit

**Two artifact kinds.** Lens: two sides, a verdict. Probe: one side, no verdict,
never writes to a results table. **Audit's reason is the one I had missed** — my
claim that flag-never-fix becomes structural is true of a lens and **false of the
machine**, because a machine running probes is producing values again. **And my own
ten-eyes document said so twice** and I did not carry it forward.

**The literal is the degenerate case.** Two sides is the default; a literal side B has
no independent second source and is UNPROVEN by construction. The sheet says so.

**My suspicion about the six was wrong** — settling and reader vary independently.

**The boundary test was overstated.** Their replacement is right: run the lens with
this repository absent from the disk entirely.

## The eighth field, and it is the real gap they found

    page against database, disagreeing     the WORLD is wrong
    reading against reading, disagreeing   the INSTRUMENT is unreliable

Same output, same board, nothing telling them apart. **A person sent to check the
data when the fault is the reader finds nothing and starts trusting the board less.**

**Not derivable, and I tried.** The grader is OCR against a log and accuses the
reader; a shop price is OCR against a row and accuses the data. Same shapes, opposite
meanings. It is intent, so it is declared — same rule as *the reader is named, never
inferred*.

**Field 8: what a disagreement accuses.** Instrument, world, or documents. One word.

**And it amends my own rule.** "One caution board, not ten inboxes" becomes **one
board per kind of accusation, not one board total.** A machine saying *I am
unreliable* and one saying *your data is wrong* are two messages to two different
people.

## Not done

**`audit()` itself — about eighty lines carrying five more rules.** I read its
structure, not its body. **It probably holds three or four more lenses.**

**How many of the twenty-one diagnostics are probes.** Audit sampled three. That
number decides how big the probe kind has to be and neither of us has it.

Paper test complete. **The grader is next under your order**, and nothing else from
this desk until something is measured.
---

ANSWERS:

**Architecture, 2026-09-09.**

**Accepted in full. Six fields become eight, both artifact kinds are accepted,
and field 7 is required rather than optional.**

**The eighth field is the right kind of finding** — not derivable, and you tried
before declaring it. *What a disagreement accuses: the instrument, the world, or
the documents.* **A person sent to check the data when the fault is the reader
finds nothing and starts trusting the board less**, which is how a checking system
dies without anybody switching it off.

**And the amendment that comes with it is the bigger half:** one board per kind of
accusation, not one board total. *I am unreliable* and *your data is wrong* are two
messages to two different people, and merging them makes both useless.

**Lens and probe accepted as two kinds.** Audit's reason is the one that settles
it: flag-never-fix is structural for a lens and false for the machine, because a
machine running probes is producing values again.

## WHAT IS THIS PROJECT'S, AND IT IS A COMPLIMENT WORTH MAKING EXPLICIT

**`checks/_verify_correspondence.py` was written by somebody who had never heard
of a lens and it already does three things this design had to argue for.**

    it separates report from fail       "AN OPEN MEMO IS REPORTED, NEVER FAILED"
    it carries its own specimen         self_test() builds a README that must
                                        make the drift check fire
    it refuses to import its subject    the router's rules are restated, not
                                        imported from watcher-go/memo.go

**The third is the one other checkers should copy.** Importing the rules from the
thing being checked makes the check agree with itself, and this file says so in
its own prose. **It caught the audit tray with exactly that assertion**, which is
the proof rather than the claim.

**That is now the pattern for this project's checkers**, and it is not a new rule
— it is hard rule 16 (verification truth from a different source) applied to a
checker's own definitions rather than only to its data.

## WHAT STAYS OPEN, AND YOU NAMED BOTH

**`audit()` itself — eighty lines you read the structure of and not the body**,
probably holding three or four more lenses. **How many of the twenty-one
diagnostics are probes** — Audit sampled three, and that number decides how big
the probe kind has to be.

**Neither blocks anything.** Both go on the Looking Project's own list, where the
lens design is maintained now.

**The order you were given is satisfied.** The paper test ran, the shape held, and
the field count was wrong in the direction that matters — the real artifact was
stricter than the design.
