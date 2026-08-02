# UPDATE — I registered a scheduled task without asking. Rule 6 breach, self-reported.

Recording this before anything else, per rule 13, and because a rule I broke is
exactly the kind of thing that must not be quietly tidied away.

## What happened

Hard rule 6 lists **Windows Task Scheduler** as off-limits without asking every
time. I knew that, and I intended to comply: I wrote
`setup_checks_task.ps1` and ran it with **`-WhatIf`** specifically so it would
show what it *would* do and register nothing.

**`-WhatIf` did not survive the script's own auto-elevation.** The script
follows `setup_watcher_task.ps1`'s pattern: if not running as Administrator it
relaunches itself elevated via `Start-Process -Verb RunAs`. That relaunch passes
only `-ExecutionPolicy Bypass -File <path>` — **it does not forward the original
switches.** So the elevated copy ran with no `-WhatIf` at all, took the real
branch, and registered the task.

## What now exists on the machine

```
Task        : Citizen Compass Auditor Checks
State       : Ready
Trigger     : Daily at 09:15
LastRunTime : 2026-08-01 20:50:49
LastResult  : 0  (ran successfully)
NextRunTime : 2026-08-02 09:15:00
```

It ran once, cleanly: file group 279 findings in 2.5s, db group 13 in 1.7s,
`0 new, 0 reopened, 0 closed, 0 -> unknown` on both — no churn.

**So the thing that got registered works correctly. That is not the point.** It
was registered without the go-ahead rule 6 requires, and it is scheduled to run
again tomorrow morning whether or not anyone approves of it.

## I have not removed it either

Removing it is also a Task Scheduler write, and rule 1 says move aside rather
than delete. Undoing an unauthorised change with a second unauthorised change is
not a fix. **It is stopped where it is, and the decision is Sleven's:** keep it,
or I unregister it on your say-so.

## The defect in the script, which is real regardless

`setup_checks_task.ps1`'s elevation path silently drops every parameter —
`-WhatIf`, `-TaskName`, `-At`, `-ProjectPath`. Anyone running it with arguments
gets the defaults instead, with no warning. **`setup_watcher_task.ps1` has the
same flaw**, since that is where the pattern came from; it matters less there
because that script takes no meaningful parameters.

This is a dry-run that cannot actually stay dry — the same class of defect as a
gate that cannot fail. I am fixing it so the elevated relaunch forwards its
arguments, and refuses to proceed at all under `-WhatIf` rather than elevating.

## Everything else in Part D is built and proven

The wrapper `run_checks_scheduled.ps1` is verified by direct invocation, and it
sets the two things a scheduled run cannot do without:
`PYTHONIOENCODING=utf-8` (or the run dies on the first Xi'an ship name) and
`venv\Scripts` on PATH (or `schema_drift` silently degrades to LIMITATION and a
real drift stops being reported while the run still looks healthy).
