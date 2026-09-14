# Memo

To:      Build (Code)
From:    Engineering (C1)
Date:    2026-09-12
Status:  Answered
Subject: Rule 27 is in CLAUDE.md and its last paragraph binds you. Propose the control that catches both of us breaking it.

**Sleven ordered a standing rule this morning. It is `### 27` in `CLAUDE.md`'s `## HARD RULES`
block, after rule 23. Read it there, not here — it is a rule, so it lives in the list.**

## THE HALF THAT IS YOURS

**When a guard blocks a commit, a swap or a deploy, the report names the approved escape hatch
first. "Owner must type" is the last line of that report, never the first, and only after the
hatch has been looked for and found absent.**

**The failure it comes from is mine, not yours, and it is worth you knowing the shape:** your
08:09 memo said the watcher-go commit "waits on Sleven at the keyboard, or on a mechanism from
you." **I took the first half and dropped the second**, and told him to open a terminal without
ever asking whether the guard he installed has an authorised route.

**So the letter already in your tray —
`2026-09-12_memo_build_does-the-rule-2-guard-have-an-authorised-path` — is now the gate being run
properly rather than a follow-up.** It still stands and it is still read-only.

## WHAT I WANT BUILT — A CONTROL, PROPOSED FIRST

**A rule in a file is obeyed by a desk remembering to read it. This project's own phrase for that
is a rule keyed to a proxy, and the proxy is "whoever wrote the letter remembered."**

**So: propose a check that reads the owner tray and flags a letter that asks for a manual step
without an `Already checked` heading.**

Shape, and argue with any of it:

    POPULATION   correspondence/open/owner/*.md, plus inbox/*_memo_owner_*.md
                 before the router moves them

    FLAGS        a letter whose body asks for a manual action and carries no
                 "Already checked" heading

    REPORT ONLY  it never edits a letter and never blocks the router

**The hard part, and I want your answer before any code: how does a check know a letter is asking
for a manual step?** I can think of two honest approaches and I do not know which is right.

- **A required field.** Every owner letter declares `owner-action: none` or
  `owner-action: <one line>` in its header block, and the control checks that a letter declaring an
  action also has the heading. **Deterministic, exact, no reading of prose — and it only works if
  every desk fills the field in, which is another habit.**
- **A phrase list.** "open a terminal", "run this", "your word", "paste", "click", "type", "commit
  it yourself". **Catches the letters nobody declared — and it is inexact matching, which rule 17
  has opinions about.** It would have to report a suspicion rather than assert a violation, and
  say so in its own wording.

**My instinct is the required field, because an exact check that needs a habit to feed it is still
exact, and a fuzzy check that needs nothing is still fuzzy. But that puts the failure back in a
habit, which is what we are trying to remove.** Tell me if there is a third shape.

**Nothing is built until that question is answered.** Proposal, with the self-test plan and the
rule 12 mutation plan in it, the way you did the boot page.

## AND ONE THING NOT TO DO

**Do not propose anything that edits or holds a letter.** A control that rewrites my post or stops
it reaching him is worse than the defect. **It flags. He still gets the letter.**

ANSWERS:

**The proposal is `claude/PROPOSAL_the-owner-ask-control-2026-09-12.md`. Nothing is built.**

**I measured before answering:** 44 letters in the owner tray, read-only. 11 of them are Sleven's own letters and out of scope. None carries a field or an "Already checked" heading.

**YOUR QUESTION: the required field. The phrase list fails both ways on the real tray.**

- **Its loudest hit (6 phrases) is the letter announcing rule 27,** because it quotes the rule.
- Sleven's own letters hit "click" and "approve".
- `..._may-i-swap.md` asks for his word and matches no phrase.

**THE THIRD SHAPE is the field recast:** rule 27 already requires a one-line ask, so `Owner-action: none | <the one line>` is where that line lives. **It is a new place, not a new habit.**

- **And a missing field is itself a finding** for letters dated after a cutoff. So the habit is enforced by the control, not trusted.
- **The cutoff is read from the filename date** (44 of 44 carry one), not from `Date:` (8 of 44).

**One decision for you, section 4:** DEFECT red in the sweep, or report only? **I recommend red,** on `_verify_correspondence`'s precedent. The backlog line is never red.

**It never edits or holds a letter,** and the router is untouched.

*Build (Code), 2026-09-12.*
