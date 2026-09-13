# Memo

To:      Architecture
From:    Owner
Date:    2026-09-10
Subject: FINDING — every answer you have written me today went into a folder nobody reads. This is why the system feels dead.
Status:  Answered

**Your tray is empty and you are right that it is. You have answered everything.
I could not see any of it.**

## WHAT ACTUALLY HAPPENS

`watcher-go/memo.go`, `memoDestination`:

    answered := Status == "answered" || "closed" || "done"
    if answered -> correspondence/answered/

**That test runs BEFORE the `To:` line is looked at.** So a memo answered by any desk
goes to `answered/` regardless of who it was addressed to. **A desk cannot reply to
me.** It can only reply to a folder.

**Everything you wrote me today is in there:** the Echo teardown, the chain
requirement, blocked-versus-idle, the dollar withdrawal, the brakes. **Nine letters.
My tray showed one item all afternoon.**

## WHY IT MATTERS MORE THAN IT LOOKS

**I have spent today believing nothing was coming back.** It was all coming back, into
a folder that is an archive by name and by intent. **Nobody watches an archive.**

**And it is the same defect shape as everything else this week.** Nothing went red.
The mail reported success every time. **A system that reports what it managed to do
and not what nobody read.**

**It also quietly breaks the chain I ruled this afternoon.** Work goes me → you →
Build → you → me. **That last arrow does not exist.**

## WHAT I WANT FROM YOU

**Specify the fix. Do not build it — Build is mid-brakes and this does not jump it.**

The obvious shape is that an answered memo addressed `To: Owner` lands in my tray
rather than the archive, and the archive gets its copy afterwards. **Check whether
that breaks the supersede behaviour** — `clearOpenCopy` moves the open copy aside when
an answer files, and I do not want an answer to me quietly deleting the thing it
answers.

**Say whether it is only me, or every desk.** If Build answers you, does that reply
reach your tray, or does it vanish the same way? **I suspect the second and I have not
checked.**

**And say what it costs to have a reply appear in two places** — the answer in my tray
and the record in the archive — because a copy in two places is how this project ended
up with two of everything before.

## WHAT DOES NOT CHANGE

**Your Echo verdict stands and I have read it.** Both collisions accepted, the third
correctly refused. **The number for the failed rotations is coming to you separately,
because it is mine to give and I am not giving it inside a finding.**

---

ANSWERS:

**Architecture, 2026-09-10.**

    claude/SPEC_an-answer-goes-back-to-the-sender-2026-09-10.md

**On disk. Specified, not ordered — Build stays on the brakes.**

**Your reading of the code is exact.** I read `memo.go` before writing a word of
this and the answered test does run at line 166, before `m.To` is touched at line
171. Nothing to soften.

## YOUR THREE QUESTIONS

**1. Does it break supersede? YES, and worse than you thought.**

`clearOpenCopy` loops **every** tray for the basename and moves the first hit to
`_to_delete/`. That is safe today only because the answer goes to `answered/`, which
the loop never scans. **Put the answer in a tray and the loop can move the answer it
filed two lines earlier.**

**And Go randomises map iteration order, so it would work on some runs and not
others.** A defect that works most of the time is worse than one that never does.
The fix is one argument — the loop is told which tray not to touch.

**2. Only you? No. Every desk, in every direction.** Build answering me vanishes the
same way. Audit answering Build vanishes. **New letters arrive normally and ANSWERS
vanish**, so every tray fills with fresh questions and never with replies. That is
the whole of why it reads as one-directional.

**3. A copy in two places costs exactly what you think, so there is no copy.**

The tray copy is the one that gets edited — that is what a tray is for — and the
archive copy rots beside it. **Your own `memo.go` header says this repository has
been bitten by two-of-everything three times.**

**The three status words already in the code do the whole job without duplicating
anything:**

    Open       ->  the To: desk's tray      a question going out
    Answered   ->  the FROM: desk's tray    the answer coming back
    Closed     ->  answered/                the thread is finished

**One copy at every moment. It moves; it is never copied.** And `answered/` starts
meaning what its name says — finished threads rather than threads somebody replied to
once.

## AND ONE THING YOUR LETTER GETS WRONG, WHICH CHANGES THE FIX

**"An answered memo addressed `To: Owner`" does not exist.**

The letter you wrote me says `To: Architecture, From: Owner`. **Answering it appends
a block and flips the status. The headers do not change.** Its `To:` still says
Architecture.

**So routing an answered memo on `To:` sends it back to the desk that just answered
it.** The answer travels back up the line it came down:

    an OPEN memo      goes to the tray of its To:
    an ANSWERED memo  goes to the tray of its From:

**That is the fix, and it is one lookup.**

## THE PREREQUISITE NOBODY HAS NOTICED

**`From:` has never been validated.** `To:` is lowercased and checked against the
desk list and refused to `_needs_review/` when unknown. **`From:` is free text**,
because until now nothing routed on it.

**A real letter in the archive right now says `From: Research (CIC)`.** That matches
no tray.

So `From:` gets the same treatment as `To:` — **but only on an answered memo**, where
it is load-bearing. Refusing an open letter over an odd `From:` would break working
traffic for nothing.

**And the desks write bare desk names from now on.** `From: Research`, with the CIC
identity in the signature line where it already is.

## WHAT I AM NOT DOING

**Not moving the nine letters already in `answered/`.** They are where they are, and
guessing which still need answering is a second guess about each one. **Re-open any
you want by hand — your call, not a migration.**

*C1, 2026-09-10.*
