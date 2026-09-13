    state        WORKING
    blocked_on
    clears_by

Filed at 15:07 CDT / 20:07 UTC — `date` run at 15:05:40, this typed straight
after it.

# RECEIVED: BUILD IT. THE ANSWER-ROUTING FIX GOES AHEAD OF THE LOCK. STARTING IT
# NOW.

## WHAT ARRIVED

    15:02  Owner          BUILD IT - an answer goes back to the sender. Ahead of
                          the remaining brakes items.
    14:55  Architecture   claude/SPEC_an-answer-goes-back-to-the-sender-2026-09-10.md
    14:56  in answered/   the FINDING that started it - nine of Architecture's
                          letters to him went into a folder nobody reads

**All three read before typing this.** The brakes stop where they are: items 1
and 2 are in and tripped, item 3 (the per-desk lock) is not started and resumes
straight after this.

## WHAT I AM BUILDING, FROM THE SPEC AND NOT FROM MY OWN READING OF THE BUG

    Status: Open       ->  open/<To:>      a question travelling out
    Status: Answered   ->  open/<From:>    the answer travelling back
    Status: Closed     ->  answered/       the thread is finished
    Status: Done       ->  answered/       same as Closed

**On `From:`, not on `To:`** - an answered memo still carries the original `To:`,
so routing an answer on it sends it back to the desk that just wrote it. That is
the part the Owner's own proposed fix got wrong and Architecture caught.

**`From:` gets validated on an answered memo only** - lowercased, trimmed, looked
up, and refused to `_needs_review/` when unknown. Not on an open memo: refusing
working traffic over an odd `From:` would cost more than it saves.

**`clearOpenCopy` is told which tray not to touch**, and its gate widens from
"the destination was answered/" to "the memo is answered". Without the first, it
can move the answer it filed two lines earlier; without the second, the stale
open copy stays behind and one letter reads as waiting in one place and answered
in another.

**No second copy. No new folder. No new status word.** One copy exists at every
moment; it moves, it is never duplicated.

## THE CONDITIONS I AM WORKING UNDER, RESTATED SO THEY ARE NOT LOST

**The running watcher is not replaced today by anything I do without reporting
first.** His gate, and it is a real one - if the mail stops, nothing in this
project can tell anybody that the mail stopped.

    build and test it                            in progress
    prove each of the three cases by making it
    FAIL first                                   required
    prove an answer to Owner reaches his tray,
    ON A COPY, never the live tree                required
    keep the current binary, named, recoverable   required
    SWAP THE RUNNING WATCHER                      NOT until the above is reported

**The repeat-run requirement is the one I will not shortcut:** the supersede
failure is a randomised Go map order, so a single green run proves nothing.

Nothing committed. Nothing woken.
