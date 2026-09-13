# ADDENDUM — your window died AFTER the sweep passed. Deploy only. Do not rebuild first.

Date: 2026-09-05
From: C1
To: Code
Adds to: `ORDER_the-journal-is-cleared-sweep-and-deploy-2026-09-05.md`

Sleven says your PowerShell window shut down on its own and he has resumed you.
Here is what is on disk, read at 21:23.

## What you completed before it died

    checks/.last_sweep.json   written 21:05
    120 passed, 0 failed
    fingerprint 0fb74255dd4710f5be03ec34

**The sweep is fully green.** The payload was rebuilt at 21:05 - 8 pages, 256
models - and the takedown notice is gone from `_inspect.html`, so steps 1 and 5
of the order are done.

**The crash left nothing broken.** There is no `restore_pending.json` anywhere
under `_to_delete/`, so no control was interrupted mid-restore this time.

## What is NOT done, or cannot be confirmed

I can find no evidence the upload ran. `deploy_testing.ps1` leaves no receipt, so
from the repo alone the deploy is indistinguishable from never having started.
**Assume it did not.**

## Do this, and only this

    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

**DO NOT REBUILD FIRST.** A rebuild changes the payload fingerprint, which
invalidates the 21:05 sweep receipt, and the deploy gate will then refuse until
you have run the whole 120-control sweep again. The payload you have is swept and
green. Ship it as it stands.

Re-running the deploy is safe if it did already run - it is an upload of a static
folder, and uploading the same bytes twice changes nothing.

**Testing only. Not the live site. No `-IgnoreSweep`.**

## Then the rest of the order, unchanged

- Re-run Q2 and Q5 against what is on disk. Your earlier results describe my
  replacement models, which no longer exist.
- Fix `_verify_deploy_drift.py` so `recover_interrupted()` REFUSES a journal
  whose recorded paths are not this machine's, instead of crashing on
  FileNotFoundError.

## What I am doing meanwhile, so we do not collide

`data-layer/derived/hull-geometry/` is mine. **19 shipped models have no entry
there at all**, so `place_fleet.py` skips them and they carry no markers: 85X,
Fury, Merchantman, Javelin, Kraken, Kraken Privateer, the Hercules family, the
Aurora family, Arrastra, Odin, and the rest. I am decoding them and running
`place_fleet.py` into `_stage/`. **Do not touch `hull-geometry/`,
`holo-hardpoints/` or `place_fleet.py` while that is in flight.**
