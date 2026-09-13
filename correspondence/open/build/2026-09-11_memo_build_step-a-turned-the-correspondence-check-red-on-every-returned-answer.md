# Memo

To:      Build
From:    Owner
Date:    2026-09-11
Subject: Step A turned the correspondence check red on every returned answer. It is not pre-existing - it is step A's.
Status:  Open

**Not urgent. Do not stop Q54 for it. Take it when Q54 is done.**

---

## WHAT IS WRONG

Your 2026-09-11 day page says `checks/_verify_correspondence.py` is RED on memos in
`open/owner/` addressed to Architecture and marked Answered, and calls it
pre-existing. **It is not pre-existing. Step A caused it, and it will go red on every
answer the router returns from now on.**

The router, `watcher-go/memo.go`, in its own table:

    Status: Open      ->  open/<To:>     a question travelling out
    Status: Answered  ->  open/<From:>   the answer travelling back
    Status: Closed    ->  answered/      the thread is finished

The check, in the open-tray loop, fails a memo two ways that the router now does on
purpose:

    m["to"] != desk                    "sits in open/owner/ but is addressed to 'architecture'"
    m["status"] in ANSWERED_WORDS      "marked 'answered' but is still in an OPEN tray"

**So every returned answer is two failures, and it stays red until the sender
closes the letter.** A letter waiting to be read is not a failure - the check's own
header already says a control that goes red on an unanswered letter trains everyone
to ignore red. This is the same thing from the other side.

## WHAT THE CHECK SHOULD SAY

Take it from the router, not from a new rule:

    in open/<desk>/, Status Answered is correct when From: is <desk>,
      whatever To: says - that is an answer delivered to its sender.
      Report it as waiting to be read, like an open letter. Do not fail it.
    Status Answered in any other tray is still a failure.
    Status Closed or Done in any open tray is still a failure.
    Open letters keep today's To: == tray rule, unchanged.

**Prove it against the real tray, not a planted one.**
`open/owner/2026-09-10_memo_architecture_your-three-corrections-hold-and-the-refusals-have-a-hole.md`
is a returned answer I am deliberately keeping open - it still holds a question for me.
With the fix, that letter reports as waiting and the suite goes green on it. Without
the fix, it fails twice. Add a planted case for each of the four lines above.

## WHAT I DID ON MY SIDE

I closed eight letters in my own tray today - read and spent. That clears most of
the red, which is **why this memo exists: the red going away is not the fix.** The
next answer the router returns turns it red again.

**Do not touch anything in `open/owner/`.** That tray is mine.
