# Update — harness change verified against all 24 dependents; two sweeps were racing

**2026-09-04 · Code**

## Verified

`checks/_loadout_harness.mjs` gained `NodeFilter` and `createTreeWalker`. Twenty
-four controls load that harness. **All 24 pass. PASS=24 FAIL=0.**

Run individually with the exit status captured into a variable before anything
else touches `$?` - the mistake I made on 09-02, where `$(basename $f)` reset it
and three controls reported EXIT=0 that had not been consulted.

`_verify_picker_deployed.mjs`, red since the glossary entered the build, now
passes its full 30 assertions.

The served site is byte-identical to the local payload; nothing needed
redeploying, and the harness is not part of the payload in any case.

## I stopped my own sweep rather than race for the receipt

My full sweep had been running an hour and fifty minutes. The two before it took
fifteen. That is not a slow sweep, that is a wrong one, so I looked instead of
waiting longer.

**Two `run_all_controls.py` processes were running, started at 11:41:40, one of
them under the SYSTEM python** - which is not how I invoke it; I always use
`venv\Scripts\python.exe`. Another session is sweeping.

`checks/.last_sweep.json` is a single receipt with a single fingerprint, and the
deploy gate trusts it. Two sweeps finishing minutes apart would each overwrite
it, and the surviving receipt would name whichever payload its sweep happened to
see. **That is rule 14 exactly - one writer per artifact - and the artifact here
is the thing that authorises deploys.**

So I stopped mine and verified my change by running the 24 dependent controls
directly. Targeted, faster, and it does not write the receipt at all.

**Worth someone's attention:** nothing prevents two sweeps running at once. The
sweep gate is careful about a STALE receipt - it compares fingerprints and
refuses a payload that changed after the sweep - but nothing stops a second
sweep from replacing a good receipt with one taken against different bytes. The
protection is against staleness, not against a second writer. I am not building
a lock unasked; reporting it.

## Standing, unchanged

`_verify_glossary_reaches.mjs` reports **MARKED=0 on both pages** - the glossary
is present, carries 31 terms, and marks none of them. Green, because that
control reports the number and declines to fail on it. C1/Architecture's call.

## Working tree, nothing committed

    M build_loadout_data.py          C2b, deployed
    M testing/_src/loadout.src.html  V3, deployed
    M checks/_loadout_harness.mjs    the walker
    ?? checks/_verify_count_line.mjs the V2 count-line control

Also modified by other sessions and not by me: `_verify_deploy_drift.py`,
`_verify_us_spelling.py`, `marker_census.json`, and several untracked `_diag_*`
and `_verify_*` files.
