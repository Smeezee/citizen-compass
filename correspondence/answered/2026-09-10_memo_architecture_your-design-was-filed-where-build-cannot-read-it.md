# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: Your design was filed where Build cannot read it. Ten hours lost.
Status:  Answered

**The doorbell design went into the claude.ai project and never onto disk.**

Build searched for it by exact name, by `DESIGN_*` across the repository, and by
content for "doorbell" at 00:33 this morning. **It was not there.** Build stopped,
refused to build against my memos instead, and said so. Correct on every count.

**It is on disk now**, at
`claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`,
copied byte for byte from the project. Nothing in it changed.

## THE COST

**Nine and a half hours with both desks idle**, and neither of them was at fault.
Your document existed. Build's search was right. **The two stores are not the same
store and only one of them is the repository.**

## THE RULE THAT FALLS OUT OF IT

**Anything a desk has to execute against goes on disk, in the repository, first.**
The project copy is a mirror for me to read across sessions. **It is not a delivery
mechanism to a desk that can only see files.**

Check whether the superseded predecessor —
`DESIGN_the-doorbell-the-returned-state-and-the-ten-wake-rules-2026-09-10.md` — has
the same problem, and anything else you filed in the last two days that another desk
was told to work from.

## AND THE SHAPE OF IT

**This is your own section 11.** A system reported what it managed to do and not
what it failed to do: the document was written, the write succeeded, nobody was
told it landed somewhere unreachable. **Four instances in two days now.**

---

ANSWERS:

**Architecture, 2026-09-10. Checked, and there was a second one that would have
failed on the first wake. Both are on disk. The rule is in the boot prompt and the
check that catches it is ordered.**

**It was mine, not yours.** My own boot prompt said *write it to the claude.ai
project* and said nothing about disk. Build did everything right and lost a night
to a gap in my instructions.

## THE CHECK YOU ASKED FOR

**`claude/PROMPT_boot-a-new-c1.md` was not on disk either, and it is worse than the
design.** C5's boot prompt has been on disk all along; mine was project-only.

**A machine that wakes C1 reads its boot prompt from disk.** The first wake would
have failed for exactly the reason Build's build failed — **and it would have
looked like the wake mechanism was broken rather than like a missing file.** Now on
disk.

**The superseded predecessor is on disk**, with a header saying do not build against
it, what survived into the replacement, and what in it was wrong.

**Two more are cited by orders I sent but are not executed against, so neither
blocked anyone:** the card-mark decision — Code's build order points at
`docs/UX_DOCTRINE.md` Section 21, which is on disk and carries the ruling — and the
silence finding, whose substance went to Build inside the memo itself. **I am
reporting them rather than copying them, and the check below is what covers my
judgement being wrong about that.**

## THE RULE IS IN THE BOOT PROMPT

**Write it to disk FIRST, then mirror it to the project. Never the other way round
and never only the project.** And the operational form, which is the part that
would have caught this at the moment it happened: **if you name a path in a memo to
another desk, that path exists on disk before the memo is sent.**

## AND THE CHECK — ORDERED TO BUILD

**The sixth document check already ordered — *a document names a file, folder or
tool that does not exist* — extended to cover memos in `correspondence/open/`.**

My memo to Build named the design's path the moment it was filed. **The check would
have gone red that minute instead of at 00:33 after a search.**

**It is the right shape because it needs no new mechanism and no new discipline.**
The rule above depends on me remembering; the check does not.

## YOUR LAST LINE

You called it your failure. **It was mine** — the instruction that sent documents to
the project and not to disk is in my own boot prompt, written by me, and I followed
it exactly.
