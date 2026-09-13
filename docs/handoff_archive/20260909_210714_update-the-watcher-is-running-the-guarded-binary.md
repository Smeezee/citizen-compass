# Update — the inbox watcher now runs the guarded binary, and the swap is verified

**Filed 2026-09-09 21:07 CDT.** Authorised in the terminal.

## PROVEN BEFORE THE SWAP, NOT AFTER

Built a **test** binary first and tripped its guard, so nothing about the live
watcher depended on hoping:

    ANTHROPIC_API_KEY=<planted marker> ./inbox_watcher_guardtest.exe
    -> REFUSING TO START: ANTHROPIC_API_KEY is set in this environment, and
       inbox_watcher.exe will not run while it is.
    -> exit 78

**It reached `logs/inbox_watcher.log`, not just stderr** — which is the whole
point, since a Task Scheduler process's stderr goes nowhere anybody looks. **And
the log does not contain the marker:** `grep -c` returns 0.

## THE SWAP

    old binary copied aside   _to_delete/2026-09-09_inbox_watcher_before_guard/
                              (rule 1 - moved, never deleted)
    old sha256                1ebbcdbe7d5563eb...
    task stopped              process confirmed gone before rebuilding
    rebuilt                   go build -o ../inbox_watcher.exe .
    new sha256                3c15544f15b62964...

**The live binary is byte-identical to the test binary whose guard I tripped.**
That is the proof the guard is in what is actually running, rather than in what
was compiled from the same source and hoped to be the same.

## RUNNING, AND EXACTLY ONE OF IT

    task state   Running
    process      one pid, 26084, started 2026-09-09 21:06:19
    log          "Now watching for new files. Leave this running."
                 protected folders loaded, both skipped as designed

**One process, checked** — rule 14, and two watchers on one inbox is a failure
this project has already paid for.

The handoff pipeline was deaf for **about 25 seconds**, between the task
terminating and the new process reporting it was watching. This file arriving in
`LATEST_HANDOFF.md` is the end-to-end proof that the pipeline works.

## AND THE SWEEP-TIME LETTER IS SETTLED

Sleven's memo: Architecture corrected `Status: Answered` on
`2026-09-08_where-the-sweep-time-goes.md` — *"an error of mine, not a decision"*,
caused by a tray disposition flipping the status on every letter including one
deliberately left open. **The letter is open on purpose and the second of my two
readings was the right one.**

**"Build found it, refused to guess which of the two was meant, and was right
to."** Rule 19 earned its keep.

**What it actually waits on is two more ordinary sweep receipts** so the 42.7%
figure can be read across three runs. The clean 42.2-minute run tonight is the
second. Nothing needs running specially.

He also noted that my 16:59 report named a blocker that had been fixed at about
17:27 and nobody told me — **the third time in one day, to three different
desks**, which makes it the system rather than anybody's mistake. Not mine to fix
and not asked of me; recorded.

Nothing committed.
