# ORDER — the build is right, the deploy is correctly refusing. Run the sweep, then deploy.

From: C1 (Cowork), 2026-09-05
For: Code

Sleven asked why the fixes had not reached the test site. **They were built and
never uploaded, and the reason is your own gate doing its job.**

## What I measured

Both changes ARE in the built payload:

    testing/_deploy/_inspect.html      camera fit         present
                                       CC_FIT_MARGIN      present
                                       retireStaleMarks   present
                                       old orbit.set(r*1.45)   gone

And the payload no longer matches what was last swept:

    current payload   7aaee030d513ea4c7488b08d513266bdb6802a99a992b91f320db110a496ed6d
    last swept        446a772a82a876997e1c007c7c73acf662b0af4629f5d138f1f42cd6806f330b
    match             NO

`checks/.last_sweep.json` reads 117 passed / 0 failed / 0 not run - a clean
sweep, of the **previous** payload. `deploy_testing.ps1` refuses to upload a
payload the sweep has not passed, so it stopped. `.wrangler/tmp` has been empty
since 00:00, which is the confirmation that no upload was attempted.

**This is the gate working, not a fault.** Nothing needs overriding and
`-IgnoreSweep` should not be used.

One loose end, low priority: `testing/_src/.last_build.json` still reads
`at 2026-09-05T00:17:51` while `_deploy/` was written at 05:14. The receipt did
not move with the build. Worth a look - a stale build receipt is the kind of
thing the deploy gate reads.

## TASKS, in this order

1. **Run the full control sweep against the current payload.**
2. If it is clean, **deploy testing.**
3. If anything is red, report which control and what it says. Do not deploy
   past it and do not use `-IgnoreSweep`.
4. After the deploy, the outstanding measurement from the fit order: re-run your
   corner projection on **ATLS, ATLS GEO and Reliant Kore** and report the three
   margins. If any is still negative, say so - do not raise `CC_FIT_MARGIN`.
5. Confirm the page loads with 0 console errors and the ship list reads 256.

```
python checks/run_all_controls.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## Standing constraints

- Testing only. Do not deploy the live site.
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
