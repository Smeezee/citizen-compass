# ONE LINE FOR SLEVEN: run `powershell -ExecutionPolicy Bypass -File .\setup_roadmap_task.ps1` and click Yes on the UAC prompt. That is all Q5b needs.

**2026-08-30 11:10 UTC / 2026-08-30 06:10 local · Code (background session)**

Adopting the stop discipline: the ask is the first line, and I did not wait for
it - Q46's sweep is running underneath this.

## Q5b IS BUILT AND PROVEN. IT NEEDS ADMINISTRATOR, WHICH I DO NOT HAVE.

    setup_roadmap_task.ps1        committed 835413a
    running as Administrator      False
    -WhatIf, proven from outside  0 matching tasks before, 0 after

**I cannot complete the registration.** It needs elevation, elevation raises a
UAC prompt, and this session is non-interactive - a GUI prompt here blocks until
timeout rather than appearing. **The script is the whole of the work; the click
is the only part left.**

**Both of the older script's scars are carried:**

- the duplicate guard matches **structurally, on what a task executes**, not on
  its name - a name pattern fails the moment somebody passes a different one
- **`-WhatIf` refuses to elevate** rather than elevating without itself, which is
  the 2026-08-01 defect where an elevated relaunch forwarded only `-File` and a
  dry run registered a task for real

**And it is proven by behaviour, not by reading it.** I ran `-WhatIf` and counted
scheduled tasks matching "roadmap" from OUTSIDE the script: **0 before, 0 after.**

## AND THE EXE WAS THIRTEEN DAYS STALE

`roadmap-watcher.exe` was built 17 August - **before Q5c taught it to read the
board description.** Registering the task against it would have scheduled the
version that throws the answer away, and it would have looked like it was
working. Rebuilt before writing the script.

## WHERE IT DIFFERS FROM THE INBOX WATCHER, DELIBERATELY

    -check, not the resident loop   the scheduler owns the interval, so a reboot
                                    is survived by the scheduler rather than by
                                    the process, and a crashed poll costs one
                                    cycle instead of every cycle
    1-hour execution limit, not 0   the inbox watcher is resident and zero is
                                    right for it; this is a bounded job and a
                                    hung HTTP read should be killed. Copying
                                    zero would have been the wrong consistency.
    Daily trigger carries the       AtLogOn+repetition was tested in the other
    repetition                      script and found dead

## Q46 IS UNDERWAY

`last_verified_patch` reads **4.10** and the build is clean on it - 6,019 hull
markers on 259 hulls, checksum recomputed, deploy guard green. Full sweep
running; redeploy follows if it is clean.
