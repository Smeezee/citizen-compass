# Build update - started: a zero dimension becomes absent at import (Architecture's order)

**Code (Build), 2026-09-12, around 02:04 to 02:10 CDT.**

## The order

It is in `2026-09-12_memo_build_phase-two-is-five-ships-and-two-bigger-jobs-go-first`, section 4.

> "the repaired value is ABSENT, not zero ... `build_loadout_data.py` is this desk's file. This is the order."

That wording is the delegation. The file is C1's.

## Why it is visible, not only a data fix

The ship page prints Length, Width and Height whenever `dim` exists (`loadout.src.html:4934`). **So Javelin and MOTH have been showing "0 m" for all three.**

## The edit

`build_loadout_data.py:1299`. A dimension is kept only if all three figures are present and greater than zero. The reason is in a comment beside it.

## In flight

- The generator is running in the background. It is slow: it parses a 41 MB snapshot.
- The prior `loadout_data.gen.js` is set aside in `_needs_review/` so the regenerated file can be diffed against it.
- **Expected result:** exactly three records lose `dim` (AEGS_Javelin, ARGO_MOTH and PowerSuit), and nothing else changes. **If anything else changes, it stops there.**

## Then

Build, run the sweep alone, deploy, and verify on the served ship page that Javelin and MOTH show no dimensions rather than 0 m.
