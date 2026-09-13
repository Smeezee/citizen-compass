# Memo

To:      Architecture
From:    Owner
Subject: Propose the split of CLAUDE.md. Nothing is deleted and nothing is edited without my word.
Status:  Answered
Sleven asked what to do about the 624-line rules file, and mentioned advice he read that a
rules file should be wiped every six months. **We are not wiping it. Hard rule 1 stands and
the rules in it were paid for by incidents.** The answer is a split, not a deletion.

## WHAT I WANT PROPOSED

**A core that every session must carry, and a reference set it reads only when it is
relevant.** Anthropic's own guidance is under 200 lines; ours is 624 and it is re-read on
every request, which is the multiplier in
`claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`.

**The test for the core, borrowed from C5's charter and it is the right one:** a rule stays
in the core if breaking it costs something no check would catch. Everything else keeps its
words, in a referenced document, reachable when a desk needs it.

**Build already wrote a six-bullet version of the core for a woken desk.** Start from that
rather than from a blank page — it has been in use and nothing broke.

## CONDITIONS

1. **No line is deleted.** Everything that leaves the core lands somewhere, with the pointer
   in place before the line moves.
2. **No edit to `CLAUDE.md` until Sleven sees the proposed core in full.** It is his file and
   this is the second edit to it in a day.
3. **Measure before and after.** The usage logging is authorised and Build has it. A
   before-and-after number on the same wake is what proves this was worth doing.

**Bring me the proposed core and the map of where everything else goes. Nothing is built or
edited on this letter.**

---

ANSWERS:

**Architecture, 2026-09-12. Proposal on disk with the core in full, as you required:
`claude/PROPOSAL_the-rules-file-split-2026-09-12.md`. Nothing edited. Three things here
that you should see before you open it.**

## THE FILE ALREADY BROKE ITS OWN STRUCTURE AND SAYS SO

**Its first instruction is "Read the Hard Rules below." That block does not contain rules
24, 25 and 26** — they are filed 118 lines further down as subsections of `## Known
caveats`, past four other sections.

**Those three are the ones about dealing with you:** read the mail before you answer him;
scope is a list, not a memory; an unknown is researched, not returned. **A session obeying
line 3 literally never reaches them.**

**And the file states the discipline it broke, twice** — *"the ONLY numbered rule list"*
and *"add it here and nowhere else"*. The rules were added to the file and not to the list.
**Nobody had to argue for the split; the file grew past its own structure and then
documented the growth.**

## THE TEST DOES NOT CUT WHAT YOU OR I EXPECTED

**Applied honestly, it cuts no rules.** I cannot find one that a check reliably catches —
not a deletion, not a fabrication, not a missing backup, not a question handed to you that
a search would have answered.

**So it does not separate rules from rules. It separates rules from their EVIDENCE.** The
624 lines are about 370 lines of rule and 230-to-250 lines of incident, rationale and
repo inventory — near 40%.

**Which is why the advice you read is wrong for this file, and worth saying plainly.**
*Wipe it every six months* assumes a rules file accumulates guesses. **Yours accumulates
receipts** — the 234-file mutation, three generators fighting over one handoff, the April
Fools ship ordered onto the front page as fact. **Wiping it deletes the receipts, and a
rule with no receipt is a rule the next session argues with.**

**The core comes out at 26 rules in about 95 lines. Nothing is dropped and no number
moves** — your own L27-29 constraint, and about a hundred check files depend on it.

## AND FOUR CONTRADICTIONS THAT ARE IN THE FILE NOW, NOT CAUSED BY ANY SPLIT

**They are worth something on their own and one of them has already cost a queue item.**

`generate_handoff.py` is described as a live pipeline component in one section, as retired
and nowhere on disk in another, and as never-to-be-invoked in a third. Rule 14 keeps a
stale `testing/` assignment inside the same paragraph that argues for deleting stale rules
rather than leaving them to be reconciled by whoever trips on them. Rule 1's promise about
`_to_delete/` sits 400 lines from the file's own record that the folder never existed. And
the single-list discipline, above.

**Full detail in the proposal rather than here.**

---

**THE QUESTION:**

1. Do you want the core as proposed, or do you want to see it after the evidence file is
   drafted so you can read a rule and its receipt side by side before deciding?

*C1, 2026-09-12. Nothing edited.*
