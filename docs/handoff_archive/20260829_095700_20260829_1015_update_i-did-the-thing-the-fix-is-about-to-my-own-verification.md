# Update — I perturbed my own verification the way the defect perturbs the sweep. Sweep killed, results discarded, and the mistake is recorded rather than tidied away.

**2026-08-29 10:15 local · Code (background session)**

## WHAT I DID

I started a full sweep in the background to confirm the drift fix in the place
it was built for — **and then kept editing and running
`checks/_verify_deploy_drift.py` while that sweep was executing it.**

**That is the exact defect I spent the morning fixing, done to my own
verification.** It is also the first of the three perturbations the 28th's
update lists — *"this morning I edited checks/ while a sweep executed those
files"* — so it is the second time, not the first.

## HOW IT SHOWED

An independent manifest of `testing/_deploy` and `testing/_src` came back with
content differences I could not account for:

    _deploy/holo.html               hash moved
    _deploy/loadout.html            hash moved
    _deploy/loadout_marker.gen.js   ef9be07 -> 2536dbd, in _deploy AND _src
    _src/.last_build.json           hash moved

**None of those were my probe.** The probe left bytes intact and moved only
mtimes. The moving hashes are a concurrently-running sweep: its own copy of the
drift control planting into `_deploy` in section 5, and a rebuild landing from a
version of the file that no longer existed on disk by the time it ran.

## WHAT I DID ABOUT IT

**Killed the sweep and discarded its results.** A sweep whose controls changed
underneath it measures nothing, and reporting a number off it would be
manufacturing exactly the confidence this project calls SILENT SUCCESS.

Nothing was lost — the sweep was confirmation, not the work — and the fix's own
verification stands on its own evidence, taken before the sweep and repeated
after it:

    612 files, hash AND mtime, before and after a full run
    IDENTICAL - EVERY HASH AND EVERY MTIME

**Next: put the tree back to the state the manifest recorded before any of
this**, then re-run the sweep with nothing else touching `checks/` — which is
the only way its result means anything.

## THE RULE THAT IS MISSING, AND IT IS NOT A NEW ONE

A sweep has no lock. Nothing stopped me editing a control mid-run, and nothing
stopped C1 regenerating `data-layer/` mid-run on the 28th. **Rule 14's own
words apply: a rule that depends on remembering it is a convention, not a
guard.** The drift control was the one perturbation I could close by
construction, and it is closed. The other two are still open by design.

Not proposing a fix for that in this update. Recording it so the next session
does not rediscover it as a surprise.
