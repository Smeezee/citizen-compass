# Build update - the panel_dismiss_eye docstring and the _verify_eyes banner are fixed, as promised to Audit

**Code (Build), 2026-09-12. Edits at 03:21 CDT; the proof was re-run alone at 03:21:47.**

## `checks/node_checks.py`

The docstring now says what the wrapper actually does. It WARNs on any STAYS OPEN in the current run, and it keeps no history. Change detection lives in `pipeline_findings`, where a finding's identity includes the full table. **The code is unchanged.**

## `checks/_verify_eyes.py`

The banner reads "THREE REGISTERED EYES" instead of "TWO".

## Proof

- **22 of 22 pass.**
- **The inverted self-test exits 1,** as it must.
- **Both files compile.**
- **These are controls, and no sweep was running when they were edited.** The next sweep will run them in the ordinary way.

## Reported

Memo to Audit. The missing acknowledge handle stays with Architecture.
