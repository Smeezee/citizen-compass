# Update: the restart stall found and fixed - it was not the marker

## The marker was not the cause, and the log proves it

Checked before changing anything. `collector-running.marker` is **never
consulted in any refusal path** - not in the current build and not anywhere in
the repo's history (`git log -S` across all of `citizen-collector/`). It feeds
one thing: a diagnostic line about how the previous run ended.

Sleven's own log settles it:

    23:04:10 PREVIOUS RUN DID NOT SHUT DOWN CLEANLY.
    23:04:10     It was pid 3064, started 2026-08-13T18:25:57-05:00
    23:04:10 tray: icon added ... hotkey registered: Alt+F3 ... auto mode started

**A marker was present and the collector started anyway.** The refusal also
fired once on 2026-08-14, not on every launch - 10 times total across a week,
and the build started normally at 23:17:27 afterwards.

The single-instance gate is a **kernel-owned named mutex**, which cannot go
stale: the kernel releases it when the process dies.

## What actually happened

    23:05:26 update: installed 0.3.0 - restart to use it
    23:05:29 restart: started ...collector-master.exe, this process is exiting
    23:05:29 another collector is already running ... its window could not be
             found to raise. Look for collector-master.exe in Task Manager.

Both lines in the same second. The process that had just launched its own
replacement was **still holding the lock**. The replacement looked, saw "already
running" - about the process that had just started it - found no window to raise
because the launcher's was already gone, and exited. Nothing was left running.

### The delay was backwards

```go
// A beat, so the child is past its single-instance check before this
// one releases the lock.
go func() { time.Sleep(1500 * time.Millisecond); os.Exit(0) }()
```

The child checks the lock **immediately**. Sleeping here held the lock for 1.5
seconds *longer*, across the exact moment the child was looking. The delay did
not prevent the race - it guaranteed losing it. The comment described the
correct protection; the code did the opposite.

## Fixed in four places

1. **Release before handing over.** `releaseInstanceLock()` now runs *before*
   the replacement is started. The claimed mutex handle is kept for exactly this.
2. **Looking no longer keeps the lock alive.** `CreateMutex` returns a valid
   handle even when the object already exists, and the old code kept it. Once a
   process had looked, it became a reason for the answer to stay "yes" - it could
   never observe the owner letting go. That handle is now closed.
3. **The guard waits before refusing.** A held lock is not proof of a running
   collector. It now looks for a window belonging to a live sibling, re-asks for
   up to 3 seconds, and **starts normally if the holder lets go**.
4. **The message tells the truth.** It named `collector-master.exe` regardless of
   what was running, and sent people to Task Manager to find a process that had
   already gone. It now names the actual executable and says that a lock held by
   a shutting-down process clears in a few seconds.

## The marker change Sleven asked for, applied where it is true

The report now **asks whether the pid is alive** instead of asserting a cause:

- pid alive and running our image -> "A COLLECTOR IS ALREADY RUNNING as pid N"
- pid gone -> "that process is NOT running now - checked, not assumed", and it
  says the stale marker was cleared and never blocked startup

`pidIsLiveSibling` checks the **image name** as well as liveness, so a pid
Windows has recycled for something unrelated reads as gone rather than as a
collector.

## Proven, including negative controls

New `restart_handover_selftest.go`, registered in `-selftest`. All green:

- an unheld lock reads as free / a held lock reads as taken (each is the other's
  negative control)
- **releasing the lock frees it** - the property that makes the race impossible
- live sibling: yes for this process; no for an impossible pid, pid 0, a
  negative pid, a **live non-collector pid** (recycling), and a killed process
- dead pid reported as not running, and does NOT fire the "already running"
  branch; live pid reported as already running, and does NOT fire the crash
  branch

**It immediately caught a bad fixture.** `lifecycle_selftest.go` simulated a
killed run by leaving the marker naming `os.Getpid()` - its own live process. You
cannot stage a process that died by pointing at one that did not. It now writes a
pid that cannot be running. `selftest PASS`.

## What this does NOT fix, and it matters

**The published 0.3.0 asset does not contain this.** The restarting code lives in
the build being replaced, so the friend's and wife's machines updating 0.2.0 ->
0.3.0 will still hit the stall. It is not permanent - opening the collector again
works, as Sleven's 23:17:27 start shows - but they should be told that.

The local `collector.exe` is now 0.3.0 **with different code than the published
0.3.0**. New bytes behind an old label is exactly what make-release guards
against, so this must go out as 0.4.0, not as a re-upload. Not published, and
nothing committed - awaiting a go-ahead.
