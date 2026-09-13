# ONE LINE FOR SLEVEN: the roadmap task still does not exist after two registration runs — next run of `setup_roadmap_task.ps1` now prints why and holds the window open; send me what it says.

**2026-08-30 11:20 UTC / 2026-08-30 06:20 local · Code (background session)**

**This is stop #4 - the same unexplained result twice - and it stops Q5b only.
The queue keeps moving; the 4.10 sweep is running underneath this.**

## WHAT I MEASURED, THREE WAYS, TWICE

    Get-ScheduledTask "Citizen Compass Roadmap Watcher"   NOT FOUND
    tasks whose ACTION mentions roadmap                   0
    schtasks /query | roadmap                             0

    total scheduled tasks visible                         226
      \Citizen Compass Auditor Checks   [Ready]
      \Citizen Compass Inbox Watcher    [Running]

**Visibility is not the explanation** - I can see this repo's other two tasks
from the same non-elevated session. And the watcher's state file was last
written at 05:04:28, which is my own manual `-check`, not a scheduled run.

## AND I PROVED IT IS NOT SOMETHING I COULD HAVE DONE MYSELF

I tried registering it directly, non-elevated:

    REGISTER FAILED: Access is denied.
    VERIFY from the scheduler: 0 task(s)

**Elevation is genuinely required.** So this is not a case of the script taking
a path it did not need.

## MY DEFECT IS PART OF WHY NOBODY CAN SEE THE CAUSE

The elevated copy runs in **its own window, which closes the instant the script
exits**. `setup_watcher_task.ps1` pauses three times for exactly that reason and
**I dropped all three.** Whatever the elevated run did, the window took the
answer with it - which is how "task registered" and "no task exists" can both be
held honestly.

**Now fixed, and more than fixed:** it pauses on every exit path, and after
registering it **asks the scheduler the same structural question the duplicate
guard asks at the top**. A pass there and a refusal here can no longer disagree.
If it silently does nothing again it will say so:

    VERIFICATION FAILED: no scheduled task runs the roadmap watcher.

**One more run and the window will name the cause.** I have stopped guessing at
it.

## WHAT IS STILL TRUE ABOUT Q5b

The script, the guards and the proof stand: `-WhatIf` refuses to elevate,
verified from outside as 0 tasks before and 0 after; the duplicate guard matches
structurally; and the exe was rebuilt first, because the one on disk was
thirteen days stale and predated the code that reads the board description.

## THE QUEUE DID NOT STOP

4.10 payload built - `last_verified_patch "4.10"`, 6,019 hull markers on 259
hulls, checksum recomputed, deploy guard green. Sweep running.
`_verify_child_markers.py` has gone red in it, which is expected: the 4.10 pull
moves markers and that control refuses an undeclared loss by design. I will read
it properly when the sweep lands rather than guess at 0.2 seconds of output.
