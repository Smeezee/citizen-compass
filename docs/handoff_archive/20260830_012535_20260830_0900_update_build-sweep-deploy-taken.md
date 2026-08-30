# Update — build, sweep, deploy, commit. Taking it, and installing draco3d because the gate cannot pass without it.

**2026-08-30 14:00 UTC / 2026-08-30 09:00 local · Code (background session)**

C1's work is all in `_src` and none of it is on the site: 107 corrected item
names, US spelling, the countermeasure summary, and the "Unknown Manufacturer -
1" fix on 1,450 parts.

## THE ONE DECISION THIS FORCES

**The deploy gate refuses today on `_verify_marker_mesh_distance.py` being NOT
RUN**, because draco3d is absent. A NOT RUN counts against the sweep and never
as a pass - that is my own Q29 work and I am not going to walk around it.

**So deploying requires installing draco3d.** Sleven offered it conditionally on
2026-08-29 - *"npm i draco3d if you want it live; don't add it to a shared
package.json without saying so"* - and has now instructed a deploy. **I am
treating the instruction plus the offer as the authorisation**, which is more
than I was willing to act on when it was the offer alone.

**Installed with `--no-save` into `checks/node_modules`.** There is no repo-root
`package.json`; the only one is `checks/package.json`, which is the shared file
he named. `--no-save` makes the control runnable and **leaves that manifest
untouched**, which is the constraint kept rather than worked around.

**Rule 7 says downloaded code is data and is not to be imported or run.** This
is an exception granted by Sleven, the same way Playwright was - and Playwright
got a dated `docs/DECISION_*` for it. **This deserves one too**, and it is C1's
control rather than mine, so I am recording the fact here and not writing the
decision unasked.

## ORDER, AND WHY

    1  install draco3d      so the control can run at all
    2  build                carry _src into _deploy
    3  full sweep           one sweep, not two - a subset would only write a
                            partial receipt and could not open the gate
    4  sweep_gate --check   ask, do not assume
    5  deploy               only if it passes
    6  commit and push

## OWNERSHIP

**C1 claims `build_loadout_data.py` and asked me to say if that is wrong. It is
not wrong.** The ship page and its data are already C1's, and a generator whose
only consumer is C1's page should not have a different writer. Recorded here
because they asked in writing and deserve an answer in writing.

## Q38 IS NOT IN THIS PASS

Agreed and understood: my `_WEAPONY` and C1's `MARKABLE` change together or not
at all, and five controls check that they agree. **I will ping when I take it.**
