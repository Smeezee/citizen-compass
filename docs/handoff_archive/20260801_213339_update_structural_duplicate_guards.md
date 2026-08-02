# UPDATE — structural duplicate-writer guards, proven by a decoy

You were right that this was still open: I made `-TaskName` forward correctly
and left the door it opens unguarded. `-TaskName "Watcher 2"` would reliably
have produced a second watcher — the ~37,000-characters-per-regeneration
failure, reachable *through the parameter I had just made work*.

## What changed

Both setup scripts now refuse to register when something else already does the
job, and both match **structurally — on what a task EXECUTES**, not on what it
is called.

- `setup_watcher_task.ps1` — refuses if any task's action runs
  `inbox_watcher`.
- `setup_checks_task.ps1` — its old `*Auditor*` / `*Citizen Compass Checks*`
  name patterns are **gone**, replaced by a match on any action running
  `run_checks`.

Tasks with the **same name** as the target are excluded, because replacing the
canonical task is exactly what a legitimate re-run does. A second writer under a
*different* name is the failure.

**Both guards run BEFORE the elevation check.** Detecting a duplicate needs no
privileges, a dry run has to be able to report the refusal, and a run that is
going to refuse should not raise a UAC prompt first. With the guard after the
elevation branch it would have been unreachable from a non-admin dry run — the
check would have existed without ever being able to run.

## Rule 12 — the decoy

Registered `Nightly Media Sync`, a task whose action runs `inbox_watcher.exe`.
The name is deliberately unrelated: **no name pattern would ever match it.**
Second decoy `Quarterly Report Builder` running `run_checks.py`.

| stage | watcher script | checks script |
|---|---|---|
| **baseline**, no decoy | exit 0, reached "would register" | exit 0, reached "would register" |
| **decoy present** | **exit 1, REFUSED** | **exit 1, REFUSED** |
| reached register stage? | **No** | **No** |
| **decoy removed** | exit 0, reached "would register" | exit 0, reached "would register" |

The baseline matters: without it a refusal proves nothing, because a guard that
refuses unconditionally is as broken as one that never refuses.

## The direct comparison, which is the whole point

At the moment both decoys were live:

| guard | tasks matched |
|---|---:|
| **old, name-based** (`*Auditor*`, `*Citizen Compass Checks*`, `*Watcher*`) | **0** |
| **new, structural** (action runs `inbox_watcher` / `run_checks`) | **4** |

**The old guard matched nothing.** It would have let both decoys through and
registered a second watcher alongside them. This is not a hypothetical about
naming conventions — it is measured, against the exact scenario the parameter
makes reachable.

## A flaw in my own test, corrected

My first assertion reported `REFUSING=False` even though the console plainly
showed the refusal. Cause: the guard uses `Write-Host`, which goes to the
**information stream**, and `2>&1` does not capture it — so the captured string
was empty and every `-match` was trivially false. A test that reads an empty
buffer and reports "not found" is a check that cannot fail. Re-run with `6>&1`
and the assertions are real.

## Machine state afterwards

Decoys removed; nothing left behind.

```
total scheduled tasks       : 226   (unchanged from before the test)
tasks running inbox_watcher : 1     Citizen Compass Inbox Watcher
tasks running run_checks    : 1     Citizen Compass Auditor Checks
watcher process PID         : 21764 (unchanged throughout - never restarted)
```

Both scripts parse with 0 errors.
