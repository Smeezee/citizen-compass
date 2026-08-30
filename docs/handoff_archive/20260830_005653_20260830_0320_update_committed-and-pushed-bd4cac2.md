# Update — committed and pushed as `bd4cac2`. Q37 and Q39 in history; tree clean.

**2026-08-30 08:20 UTC / 2026-08-30 03:20 local · Code (background session)**

    bd4cac2   18 files changed, 1,639 insertions, 367 deletions
    7cda543..bd4cac2  main -> main
    local == remote == bd4cac2      git status --porcelain   0 entries

## Verified after, not assumed

- **`_to_delete/` contributed 0 files**, and **`editability_patches.json` is not
  in the commit** - checked for both by name in the index before and in
  `git log -1 --name-only` after. The leftover plant did not enter history.
- No path outside the eight expected roots.
- Push confirmed by fetch and hash comparison.

## THE ONE JUDGEMENT CALL, REVERSED FROM LAST TIME

`testing/_src/loadout.src.html` is IN this commit. **I excluded it from
`7cda543` because no sweep had seen it.** It is included now because my Q37 fix
asserts on the markup it introduces - `data-cm-ports` and the `cm-summary` row -
so committing the control without the page would leave a control that cannot
pass. **They were verified together** by `_verify_ship_page` (237 assertions)
and `_verify_loadout_fitment`, both exit 0. **A full sweep still has not run
over it**, and that is in the commit message rather than left to be discovered.

## WHERE THINGS STAND

    Q37, Q39     done
    Q3           dry run done, list ready, NOT written - wants a verified
                 backup (rule 4) and an answer on Mule/STV sharing one stated
                 dimension triple
    Q38          not started - my _WEAPONY and C1's MARKABLE must move in the
                 same breath, 602 markers, two owners
    the deploy   still refused: _verify_marker_mesh_distance.py is NOT RUN
                 without draco3d. That is the only blocker left that is not
                 mine, and it is a one-line install away whenever Sleven says.

## OPEN AND MINE, AND IT IS THE ONE I WOULD TAKE FIRST

**`_verify_loadout_fitment.py` can leave a planted value in
`data-layer/editability_patches.json`** and therefore in the shipped data layer.
Cause not established - I guessed twice and could show neither. Until it is
fixed, **anything that builds after a sweep should check that file is absent
first.**
