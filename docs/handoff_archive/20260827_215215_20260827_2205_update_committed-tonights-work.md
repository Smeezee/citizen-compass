# Update — Committed. `2fc7008`, 395 files. Not pushed.

**2026-08-27 22:05 local · Code (background session)** — Sleven: *"not yet,
commit everything from tonight"*.

    2fc7008  Thirteen of the sweep's fourteen close, and the live deploy stops
             being the unguarded one

    395 files changed, 341,378 insertions(+), 18,624 deletions(-)
    working tree after: clean

**Committed, NOT pushed.** He said commit. The live site is untouched and its
worker still 404s.

## What went in

Everything from tonight, both sides of it:

    data-layer/   328   C1's placement, transforms and client overlay - the
                        ground vehicles, the blind-folder hulls, the origin fix
    docs/          40   the findings, the orders, the whole handoff archive
    checks/        16   ten controls closed, plus the shared loadout harness
    testing/        3   build_deploy.py, loadout.src.html, the marker table
    scripts/        1   deploy_live.ps1 - both gates
    root            5   the three hardpoint builders and C1's two probes

## Checked before staging, not after

    .env                      gitignored
    data-layer/external-sources/  gitignored
    _to_delete/               gitignored
    testing/_deploy/          gitignored
    staged files matching env/secret/token/credential/.glb/.p4k:  none

## Two judgement calls, named rather than buried

**C1's `probe_join_by_hardpoint_names.py` and `probe_vehicle_entity_records.py`
are in.** They are throwaway probes at the repo root and I would normally leave
them out - but "everything from tonight" is explicit, and dropping files is the
riskier deviation. Say if you want them out; they come out cleanly.

**The old marker baseline is committed as a DELETE.** It was moved to
`_to_delete/child-marker-rebaseline-2026-08-27/` under rule 1, not deleted, and
`loadout_marker.pre-C1-20260827.js` replaces it in the same commit.

## One order I had not read until now, and it is already done

`ORDER-build-again-a-real-defect-was-in-the-markers-2026-08-27.md` (21:12) - C1
found markers sitting at the dead hull origin, which is CIG's never-set identity
value rather than a gun at the centre of the ship, and withheld 27 overlay ports
plus 318 record ports. That is the **1,720 -> 1,693** I recorded at 21:43 as
"a number that moved and is not mine".

**The build that carries it is already deployed** - version
`bbd2a7d7-7979-4980-8984-7f1e9dec042c`, built at 21:32, reporting exactly
`1693 port(s) moved onto CIG positions`. Nothing further to run for it.

Worth repeating C1's own note on it, because it is the same lesson twice in one
night: its first attempt tested the raw `pos` for exact zero and eleven ports
still came out at the origin, because `unit` is `pos / H0` rounded to five
decimals. **Testing the input to a rounding step tells you nothing about its
output** - the same shape as a gate that never ran and a flag that never applied.

## Still open

- `_verify_placer_candidates.py` - belongs to `place_fleet.py`, which is not in
  this repo.
- Going live. Four commands, and the first one creates the worker. Sleven's.

Nothing pushed.
