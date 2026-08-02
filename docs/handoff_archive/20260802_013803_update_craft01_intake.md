# UPDATE — WO-CRAFT-01 received, starting

Filed on intake per rule 13.

**Filename note:** the order was given as
`docs/workorder-crafting-and-descriptions.md`, which does not exist. It is
`docs/workorder-craft-01.md` (plus `workorder-craft-01-addendum.md`). WO-CRAFT-01
matches unambiguously so I am proceeding, flagging rather than guessing silently.

## Taken as verified, not re-derived

C1 independently measured and matched: preconditions hashes, file counts
(blueprints 1597, contracts 5108, fps-items 5420, ship-items 5384), WO-1
(7728/5344), and the WO-2 numbers derivable from `blueprints.json` alone.

## The three numbers C1 could NOT verify

768 contracts with `Blueprints[]`, 676 blueprints with a contract, max 127
sources — the scan exceeded C1's 45-second window. They reconcile arithmetically
(693 either way, and the no-pool bucket of 865 matches exactly), but the scan has
not been run.

**My first run is their verification. If any differ, that is the finding — I
stop and report rather than adjusting the assertion.**

## Before WO-2

Reconciling C2's `source_kind` with the acquisition routes in
`docs/finding-editions-paints-acquisition.md` into one vocabulary, and reporting
it rather than picking silently.

## Holding

- Assertions stay exact. Not softened to ranges. A break is the signal.
- No name-based joins; UUID only.
- No estimates, no placeholders, no ingredient cost.
- Reporting WO-2's output file size — it bears on the static-JSON ruling.
