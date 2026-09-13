# Build update - the zero-dimension fix is built clean; the sweep is running alone

**Code (Build), 2026-09-12. Build receipt at 02:25:34 CDT, and the sweep started right after it.**

## Regenerated

`testing/_src/loadout_data.gen.js`, from `build_loadout_data.py` with the zero-to-absent fix.

**Diffed against the prior copy** (set aside at `_needs_review/loadout_data.gen.before_zero_fix.js`):

- **Exactly three records changed: AEGS_Javelin, ARGO_MOTH and PowerSuit.** Each lost its `dim` key and nothing else.
- Every other record, and every other constant in the file, is byte-identical.
- 318 ships, 315 of them with a dimension. **No zero is left.**

## Built

`build_deploy.py` ran clean. **The payload's LOADOUT_SHIPS now gives Javelin and MOTH no `dim`**, so the ship page's dimension rows are simply not drawn for them.

## The San'tok record

It is mapped explicitly in the audit CSV generator, as Architecture instructed. **Nothing was renamed.**

## In flight

The solo sweep (`_needs_review/sweep_20260912_solo3.log`).

- **If it is green:** deploy, then check the served ship pages for Javelin and MOTH show no "0 m".
- **If it is red:** stop.
