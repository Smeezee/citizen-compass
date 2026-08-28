# Update — Sleven: *"add the gates to deploy_live.ps1"*. Starting, with the constraint that matters written down first.

**2026-08-27 21:40 local · Code (background session)** — the go-ahead I asked for
at 22:55 in `docs/FINDING_the-live-deploy-script-has-neither-gate-...`.

## What I am adding

Both blocks, lifted from `deploy_testing.ps1` with their escape hatches:

1. **The build receipt gate** plus `-IgnoreFailedBuild`. Refuses when the last
   build did not succeed, and names the status and the exit code.
2. **The browser-check gate** plus `-IgnoreRedCheck '<name>'`. Refuses a RED
   check and refuses a MISSING check file, and the override names one check
   rather than waving the gate through.

**Every escape hatch comes across with them.** A gate with no documented way past
it gets bypassed by editing the script, and then the bypass is invisible.

## And the control comes with them, in the same sitting

`_verify_deploy_guards.py` asserts these behaviours for the testing script only.
**Adding the gates without extending the control would give the live script a
guard nobody has ever seen fail** - rule 12's untested gate wearing a reassuring
name, which is the exact defect I wrote the finding about. Section 8 gets the
live script alongside the testing one, driven with a missing check, a red check
and a failed receipt.

## What I will NOT do

**I will not run `deploy_live.ps1` for real.** Its own header says it never has
been, the worker may not exist, and only Sleven publishes the public site.
Everything below is `-WhatIf` against throwaway project trees in a temp
directory - nothing uploaded, nothing in the repo touched, an obviously fake
token in the fixture's `.env`.

Nothing committed, nothing pushed, live site untouched.
