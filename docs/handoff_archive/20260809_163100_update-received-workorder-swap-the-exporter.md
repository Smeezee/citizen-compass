# Update — received C1's work order: land the round-tripping exporter

Received from C1, 2026-08-09: *land the round-tripping exporter and its two test
harnesses. Nothing else.* Based on C3's
`WORKORDER_swap-the-exporter-2026-08-09.md` and
`FINDING_exporter-round-trip-passes-2026-08-09.md`, with four corrections C1
made against the real repo.

Logging receipt before starting, per rule 13.

## What I am about to do

1. Read the five input files from **`_needs_review/`** (not `inbox/` — C1's first
   correction).
2. `testing/_src/sc_export.js` ← contents of `_needs_review/sc_export2.js`, with
   `SCX2` → `SCX` as the only body edit.
3. Delete `testing/_src/test_sc_export.js` — **as a move to `_to_delete/`, not an
   actual delete**, per rule 1. The order says "delete"; rule 1 outranks that
   wording and the effect C1 wants (point 7.4, `grep` returns nothing) is
   identical either way. Flagging rather than silently reinterpreting.
4. Add `roundtrip.js` and `mutate.js` with all six path literals rewritten
   relative to `__dirname` using `path.join`, plus the
   `require('./sc_export2.js')` → `./sc_export.js` fix.
5. Add both XML fixtures under `testing/_src/fixtures/`.
6. Wire both harnesses into `checks/` — **not** GitHub Actions, which this repo
   does not have.
7. `@xmldom/xmldom` dependency, and close the missing `node_modules` gitignore gap.

## Expectations recorded up front, so they cannot drift

- `roundtrip.js` must print **ALL CHECKS PASSED**, exit 0.
- `mutate.js` must report **19/20 with M18 the sole survivor**. 20/20 means the
  check is broken, not that the code improved. That expectation goes into the
  checker's label by name.
- `verified` stays hard-coded **false**. No generated file has ever been loaded
  by Star Citizen.
- `testing/_deploy/` must be untouched. Verifying with
  `git --no-optional-locks status --short testing/_deploy/` at the end.
- Original copies stay in `_needs_review/` — Sleven's to clear.

## Note on rule 14

Another session was writing `citizen-collector/` at 15:35 today. This order is
entirely in `testing/`, which rule 14 assigns to Claude Code — a different area,
so the collision risk is lower, but I will check mtimes under `testing/` before
writing anything and report anything that moves under me.
