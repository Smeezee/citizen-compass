    state        IDLE
    blocked_on   step B authorisation, which I must write and he must grant
    clears_by    OWNER

Filed at 19:56 CDT / 00:56 UTC — `date` run at 19:52:18, this typed after it.

# STEP A IS DONE. THE LIVE MAIL SYSTEM RUNS THE ANSWER-ROUTING BUILD.

**Full report in his tray:
`2026-09-11_memo_owner_step-a-is-done-the-swap-is-in-and-verified-on-the-live-tree.md`.**
This is the working record.

## THE SWAP

    rollback   inbox_watcher.ROLLBACK-20260910-1948.exe   5,768,192 B
               sha256 6b22ec29...e46d20   taken and hash-verified FIRST
    installed  inbox_watcher.exe                          5,770,752 B
               sha256 f9d983b2...f84868   the artefact proved yesterday,
                                          not a rebuild
    running    pid 19112, started 19:47:49; "Now watching" at 19:47:50

**The task cannot be disabled from an unelevated shell** — `Disable-ScheduledTask`
returns Access denied — **and it restarts itself after one minute**, so the first
stop just produced a new process while I watched. The swap went through as one
uninterrupted sequence inside that window: stop, poll until the process was
really gone (1.0s), copy, verify the hash on disk, start.

**And my own command lied to me while I did it.** It printed "disabled" on a line
that ran unconditionally, after the disable had failed. **A silent success in my
tooling, in the middle of the one change I was told to be careful with.** Caught
by the next command. Worth writing down.

## THE FOUR CONDITIONS, ON THE LIVE TREE, SYNTHETIC LETTERS ONLY

    1  an answered letter returns to the SENDER'S tray          PASS
    2  the open copy survives a routing FAILURE                 PASS
    3  invalid From: -> _needs_review with the reason           PASS
       absent From:  -> not a memo at all, filed as a document  PASS
    4  the Looking Project not accessed, not affected           PASS

**Condition 2 was caused, not simulated.** The destination filename was occupied
by a file held open by another process; `routeTo` must move an existing
destination aside before writing, a locked file cannot be renamed, so it returned
its error and the supersede — gated on that error being nil — never ran.

**The open copy sat there for the whole fifty-five seconds routing was failing.
When I released the lock the system finished the job itself and superseded it
then.** Both halves, in the right order, on the real system.

## THE FINDING THAT CAME OUT OF IT

**During those fifty-five seconds the watcher logged NOTHING.** No error, no
retry line. It silently re-attempted until the lock cleared.

**Had the blocker been permanent the letter would have sat in `inbox/` forever
and the only trace would have been its continued presence there.** Same shape as
the `fsnotify` defect Architecture filed at 13:40 — the failure is real, recovery
is attempted, nobody is told. **Reported, not touched.**

## TWO OF MY ASSERTIONS FAILED AND THE SYSTEM WAS RIGHT BOTH TIMES

The harness reported 11 passed, 2 failed. **Both failures were my timing.**

The unknown-`From:` letter was given forty seconds to reach `_needs_review`; the
watcher was still clearing the queue behind the letter I had deliberately jammed
and filed it **eight seconds after my check gave up**. And the missing error line
is the finding above, not a failed condition.

**Checked before writing the report rather than after.** "The test said FAIL and
I decided it was fine" is the reasoning that should never go unwritten.

## EVERY TEST LETTER CLOSED OUT

`_to_delete\SYNTH_step_a_verification_20260910\` — six files, each renamed to
carry its original path, plus the two supersede records left where the system
wrote them as evidence of the run. **Moved, not deleted. Nothing matching
`SYNTH-*` exists anywhere outside `_to_delete\`.**

## HIS EIGHT QUESTIONS, ANSWERED IN THE MEMO

The two worth repeating here:

**Q3 — the 16:43:55 wake had NO `--tools` and NO `--allowedTools`.** Read from
the log's own argv: `--restricted`, `--permission-prompts none`, and a deny-list
of six tools. **No allow-list at all, so writes were not path-restricted.** The
wake that "worked" carried no containment.

**Q2 — `wake_log.jsonl` still carries not one token count.** The code writes them
now; **no wake has run since the change**, so the only usage-bearing record in
the file is still `"usage_parsed": true` from 16:45:18. Saying otherwise would be
quoting a record that does not exist.

## WHAT IS NOT DONE

**Step B not begun** — containment returns to him as its own authorisation
request, which I write. **Switch still absent, so still OFF and still his to
activate.** Watcher not connected to the launcher. **Tray reconciliation and the
descendant ACL scan unstarted, in that order.** Nothing committed, nothing
pushed, no ACL changed.
