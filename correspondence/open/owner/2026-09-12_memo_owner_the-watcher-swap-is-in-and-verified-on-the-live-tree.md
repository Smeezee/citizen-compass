# Memo

To:      Owner
From:    Build
Subject: The watcher swap is in and verified on the live tree. The three mail repairs are live. Here are the evidence and the rollback, and I am stopping here.
Status:  Open

**Your go, in this session:** "Yes, swap it", after tonight's zero-dimension deploy. **That deploy went out at 03:06 and was verified first.**

## THE SWAP

    rollback copy   _to_delete/inbox_watcher.exe.rollback-20260912
                    sha256 f9d983b2ea7c8541...  (the binary that ran since 09-10)
    installed       inbox_watcher.exe
                    sha256 1dca1fde9aca383b...  (verified on disk after the copy)
    process         exactly one watcher: PID 45220, started 03:17:02
    task            Citizen Compass Inbox Watcher, Running

**The order, as your procedure asks:**

1. Rollback copy written and verified first.
2. Stop.
3. Zero watcher processes within 1.0 s.
4. Copy.
5. Hash check.
6. Start.
7. One process.

**This session cannot disable the task** ("Access is denied", the same as last time), so the swap ran inside the task's one-minute restart window, as last time.

**To roll back:** stop the task, copy the rollback file over `inbox_watcher.exe`, start the task.

## THE LIVE TEST - TEST LETTERS ONLY, ALL USING MY OWN TRAY

    1  a Closed letter ending in a bare "CLOSED."      REFUSED to _needs_review/ with the
                                                       reason - never reached answered/
    2  a Closed letter WITH its CLOSED: record         filed to answered/
    3  an Open letter to "Build (Code)"                reached the build tray
    4  an answer "From: Build (Code)"                  came home to the build tray; the log
                                                       says "(From: signature (Code) kept,
                                                       not used as an address)"
    5  case 4's answer dropped back, byte-identical    CLEARED to answered/, the tray copy
                                                       moved to _to_delete/, the tray empty

**Normal mail is unaffected.** My later letters routed on the new watcher as usual.

**The handoff is unchanged in size across the swap.** The last regeneration before the swap and the first after it are both 51,859 characters.

**The mail check passes, run on its own, with every test letter gone.**

## CLOSED OUT, AND NAMED

Every test letter is in `_to_delete/`, and no test letter remains in any tray:

- the five routed copies, in `_to_delete/swaptest_20260912_closed_out/`
- the tray copy superseded by case 5
- the four drafts, in `_to_delete/swaptest_20260912_drafts/`

## WHAT WENT WRONG ON THE WAY, BOTH MINE, BOTH HARMLESS

**Two attempts aborted at their first check, before anything was stopped, copied or moved.**

- **First attempt:** I named a helper `H`, which PowerShell already uses for its command history.
- **Second attempt:** I used `$NEW` and `$new` as if they were different. PowerShell treats them as the same variable.

**Both times I verified afterwards that nothing had changed** before trying again. Separately, **the test drafts I had left under `_needs_review/` turned the mail check red.** I moved them aside, and it passed.

## ONE OBSERVATION, NOT A CONCLUSION

**Most letters route within seconds.** Two of the six filed after the swap waited 40 to 60 seconds, for the watcher's next handoff cycle. **My change does not touch that loop.** I am timing further drops, and I will say so if it turns out to be new.

**Stopping here, as your procedure says.**

*Build (Code), 2026-09-12.*
