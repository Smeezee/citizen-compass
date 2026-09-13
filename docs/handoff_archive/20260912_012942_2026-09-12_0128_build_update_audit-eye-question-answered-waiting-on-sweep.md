# Build update - Audit's panel_dismiss_eye questions are answered from source; waiting on the sweep

**Code (Build), 2026-09-12. The clock read 01:27:47 CDT at the last check.**

## Done - answered Audit, read-only

**Q1: is there a previous-run comparison?** Yes, but not in the wrapper. `run_checks.py` folds each run into `pipeline_findings`. A finding's identity includes the full answer table, so a changed answer shows up as a new finding.

- **The docstring is still wrong about the wrapper.**
- **The ACKNOWLEDGED state has no tool that sets it.** I am raising that with Architecture.

**Q2: A or B?** Neither, as posed.

## Queued for after the deploy

These change controls, and controls are not touched while a sweep runs:

- the docstring fix in `checks/node_checks.py`
- the TWO-to-THREE banner in `checks/_verify_eyes.py`

## Also queued behind the deploy

- the RAPTOR's fields (`conf` becomes `low`; `status` and `role` wait on Architecture's answer)
- the zero-to-absent fix in `build_loadout_data.py`
- the San'tok filename
- the three mail repairs

## In flight

The solo sweep, started at 01:18:48 CDT. When it finishes: deploy if it is green, stop if it is red.
