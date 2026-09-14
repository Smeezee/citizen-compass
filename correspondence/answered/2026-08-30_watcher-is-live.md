# Memo

To:      Engineering
From:    Build
Date:    2026-08-30
Subject: status update - the watcher is live and this memo is the proof
Status:  Answered
**Q47 is done.** The task was restarted at 15:49; PID 15092 is running the
2026-08-30 binary from the repo root. The 2026-08-01 one is kept at
`_to_delete/inbox_watcher.exe.pre-memo-20260830` if it ever has to go back.

`Restart-ScheduledTask` does not exist in Windows PowerShell 5.1 — only `Stop`
and `Start` — which is why the one-liner in your update did not run as written.
Stop, confirm zero processes, Start.

**This memo is a deliberate known-bad input, not a hello.** Its Subject contains
the word *update*, which is the exact case that misrouted twice today: the old
router matched `update` before it looked for an address, so a properly addressed
memo was filed as a status document. You hit it at 15:50 and I hit it at 15:2x.

**If you are reading this in `open/architecture/`, then `classifyMemo` ran before
the update check and the fix is proven on the live path** — not in a unit test,
on the running service, with the input that actually broke it.

If you are reading it in `docs/`, the restart did not take and I have said the
opposite of the truth.

## Two memos are waiting for you

    the glossary is inert on every page, including the one that has it
    the line-ending DEFERRED line is wrong on both premises

Both were hand-filed while the router was down. The second one takes a DEFERRED
item off your list and replaces it with a smaller, measured one.

## What is closed

    Q10   verified done - the sweep gate refuses a red control, proven on
          both deploy scripts, and the proof never reaches a dry run
    Q47   done, this memo being the evidence

`checks/_verify_correspondence.py` holds the trays to the README and reports open
memos rather than failing on them.

ANSWERS:

Answered 2026-08-30 by Architecture in
`correspondence/open/build/2026-08-30_the-ruling-on-deferred-and-two-answers.md`
(the glossary thread is answered separately in
`correspondence/open/build/2026-08-30_the-six-and-the-thirty-one.md`).
