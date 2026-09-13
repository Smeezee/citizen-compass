# Update — first job on boot accepted: the two halves of the API-key guard

**Filed 2026-09-09 21:45 CDT.** Rule 13, on arrival, before starting.

## WHAT ARRIVED

Owner memo timestamped 21:42,
`correspondence/open/build/2026-09-09_memo_first-job-on-boot-the-two-halves-of-the-guard-disagree.md`.
Read on boot together with the rest of the tray (rule 24).

## WHAT IT SAYS IS WRONG

    pkg/apikeyguard              AMENDED - refuses a MISMATCH
    Assert-DeclaredBilling.ps1   AMENDED - refuses a MISMATCH
    run_checks_scheduled.ps1     calls the amended one. LIVE.
    inbox_watcher.exe            built 21:06 from the PRE-amendment package.
                                 Refuses on PRESENCE. LIVE.

The binary I swapped in at 21:06 and proved is the one that is now out of date.
**One guard, two behaviours, both running** — and a control whose behaviour
cannot be stated is not a control.

## WHAT I AM ABOUT TO DO

1. Rebuild `inbox_watcher.exe` from the amended package, proven the same way the
   first swap was proven: trip the guard on a TEST binary first, confirm the
   refusal reaches `logs/inbox_watcher.log`, confirm the log does not contain the
   planted value, confirm the live binary is byte-identical to the one tripped.
   Old binary moved aside, never deleted.
2. Then the red case in `checks/_verify_api_key_guard.py` — 27 passed, 1 failed,
   the empty-but-present variable. **Prove whether Windows can hold that state at
   all** before calling it NOT PERFORMED. "PowerShell cannot" is not "Windows
   cannot". Not a way to ship: `failed` and `not_run` both refuse a deploy.

Then the tray order he gave: the six old letters, the card mark build order, the
small import, the RAPTOR and family_id work.

Nothing committed.
