# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: BUILD IT — an answer must reach the desk that asked. Spec is on disk. The watcher does not get swapped until it is proved.
Status:  Open

    claude/SPEC_an-answer-goes-back-to-the-sender-2026-09-10.md

**Architecture has specified it. Build it.**

## THE DEFECT, IN ONE LINE

**A desk cannot reply to anybody.** `memoDestination` tests `Status: Answered` before
it looks at the `To:` line, so every answer goes to `correspondence/answered/`
regardless of who asked the question. **Nine of Architecture's letters to me landed
there today and I saw none of them.**

**It also breaks the chain I ruled this afternoon** — me → Architecture → Build →
Architecture → me. **That last arrow does not exist.**

## THREE THINGS ARCHITECTURE FOUND THAT ARE NOT OPTIONAL

**1. Route on `From:`, not on `To:`.** An answered memo still carries the original
`To:`, so routing on it sends the answer back to the desk that just wrote it. **My own
proposed fix was wrong and Architecture caught it.**

**2. `From:` has never been validated.** `To:` is checked against the tray list and an
unknown addressee goes to `_needs_review`. **`From:` gets no such check and is about
to become a routing decision.** Give it the same treatment, and the same refusal — an
unknown sender is not guessed at.

**3. `clearOpenCopy` will delete the answer it just filed.** Architecture's words, and
it is worse than I understood: **on some runs and not others.** Fix it as part of this
or do not ship it.

## THE CONDITIONS ON THE SWAP

**The running watcher moves every letter in this project. It does not get replaced on
the strength of a clean build.**

    build it and test it                        yes
    prove the three cases above by TEST         yes, and by making each one fail first
    prove an answer to Owner reaches my tray    on a copy, not on the live tree
    keep the current binary, named, recoverable yes
    REPLACE THE RUNNING WATCHER                 NOT UNTIL YOU HAVE REPORTED THE ABOVE

**Report before the swap. That is the only gate on this one and it is a real one** —
if the mail stops, nothing in this project can tell anybody that the mail stopped.

## WHERE IT SITS IN YOUR QUEUE

**Ahead of the remaining brakes items.** The brakes make automation safe; this makes
the system able to answer me at all, and I have spent a day believing desks were idle
when they were writing to a folder nobody reads.

**The per-desk lock and the rest of the brakes resume straight after.**
