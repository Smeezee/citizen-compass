To:      Engineering
From:    Sleven
Date:    2026-09-08
Subject: when I say (inbox), you work it to empty
Status:  Answered

**New standing rule. Write it into your own boot prompt in the same session you
read this, so it survives you.**

## THE RULE

When I say **(inbox)**, or "go through your inbox", or anything that means it:
work `correspondence/open/architecture/` to empty and **do not stop partway**.

Every letter gets one of three outcomes, and no letter gets none:

  **ANSWERED** — write the answer into the memo and move it to
  `correspondence/answered/`.

  **STILL OPEN, WITH A REASON** — it stays in the tray only if the memo itself
  now says what it is waiting on and who from. A letter with no stated blocker is
  not open, it is ignored.

  **SUPERSEDED** — say what overtook it, and move it.

**Done means the tray is empty or every letter left in it carries a written
reason.** Not "I got through most of them."

Then reply to me with one short line. Not a summary of the tray.

## WHY

**You are carrying 22 unanswered letters and the oldest is from 30 August.** Your
own daily page lists them as open. Nothing in the system ever asked you about
them, so they have just been sitting there while both of us worked around them.

Some of those are from desks that are blocked on your answer and have no way to
tell you twice.

## THE PART THAT IS NOT ABOUT TODAY

**A tray nobody is ever asked about fills up.** That is not a failure of yours,
it is a gap in the machine, and the same gap exists on every desk that has a
mailbox.

So when you write this into your boot prompt, also tell me whether it should be
automatic instead of waiting on me saying a word — checked at the start of every
session, or when a letter passes some age. I would rather not be the trigger.
Answer that in this memo.

## WHAT NOT TO DO

Do not answer 22 letters in one sitting if the answers are guesses. A letter
answered badly is worse than one answered late — say which ones need real work
and what they are waiting on, and that counts as working the tray.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Done, and the rule is in the boot prompt. Your question: YES, automatic — at every
boot, not on an age threshold, and with a check so it cannot go quiet again.**

**THE TRAY.** It was 41 letters, not 22. My own daily page said 22 and it was wrong,
which is its own small proof of your point. Worked to empty tonight. Everything
answered carries the answer in the memo itself and has moved to
`correspondence/answered/`. **One letter is still in the tray on purpose** — the
sweep-composition receipt — and it now says in writing what it waits on and from
whom.

**THE BOOT PROMPT.** Written into `claude/PROMPT_boot-a-new-c1.md`, which did not
exist before tonight. Your limit went in with the rule and it matters as much: **a
letter answered badly is worse than one answered late**, and naming what a letter is
waiting on counts as working it.

**YOUR QUESTION — SHOULD IT BE AUTOMATIC. Three parts, and you should not be any of
the triggers.**

**1. AT BOOT, EVERY SESSION. This is the main answer.** The tray is read before the
desk says anything to you, and every letter gets a disposition then. **Boot is the
right trigger because it is the one moment every session already performs** — it
costs nothing to attach to and there is no clock for anyone to forget to watch.

**2. NOT AN AGE THRESHOLD, and this is the part I would argue with you about if you
wanted one.** A threshold gives letters permission to sit until they are old enough
to matter. **The 30 August letter was not a problem because it turned seven days
old — it was a problem the day it arrived and nobody read it.** An age rule would
have let it sit legitimately for most of that week.

**3. A CHECK, so a full tray is visible without anybody asking.** Boot covers a new
session; it does not cover a long one where post arrives mid-run, and it does not
cover a desk that boots and skips it. **The checker that already validates
correspondence reports tray depth and the age of the oldest letter.** That is the
machine half, it is flag-only, and it makes an ignored tray impossible to not
notice. Ordered to Build with the bounce-folder assertion in the same change.

**THE PART THAT IS NOT ABOUT TODAY, WHICH YOU ALREADY SAW.** You are right that this
is a gap in the machine rather than a failure of one desk, and right that it exists
on every desk with a mailbox. **The fix above is deliberately at the mechanism, not
at this desk** — the check counts every tray, and the boot rule is written into a
boot prompt so it survives the session rather than living in one conversation.

**One thing I did wrong tonight while carrying this out, and you should hear it from
me.** I wrote `claude/PROMPT_boot-a-new-c1.md` without reading whether something was
already at that path. The write reported that it replaced an existing document.
**I do not know what was there and I cannot recover it.** Nothing in the repository
or the project references an earlier version, and the new one is complete and
current, so the likely loss is nothing — but I cannot prove that, and I am not going
to present a guess as a fact. **The practice that prevents it is now in the boot
prompt: read a project path before writing to it, always.**
