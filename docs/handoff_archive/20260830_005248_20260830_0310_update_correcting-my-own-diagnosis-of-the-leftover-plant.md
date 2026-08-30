# Correction — I gave a confident cause for the leftover plant twice and neither is established. Here is only what I can show.

**2026-08-30 08:10 UTC / 2026-08-30 03:10 local · Code (background session)**

Twenty minutes ago I filed that `_verify_loadout_fitment.py`'s plant survived
because *"a `finally` does not run when the process is killed"*. Then I said it
**leaks on every run**. **I have not established either.**

## WHAT IS ACTUALLY MEASURED

    the file        data-layer/editability_patches.json
    its content     {"AEGS_Avenger_Stalker|...missilerack_right_wing":
                     "4.99-CONTROL"}
    who writes it   _verify_loadout_fitment.py, and nothing else.
                    build_loadout_data.py only READS it, lines 1282-1283, and
                    C1's change today does not touch those lines.
    where it got to testing/_src/loadout_data.gen.js - the ship page's data
                    layer - and NOT testing/_deploy, and NOT the served site.
    now             absent from all three. Verified after regenerating.

**A build would have carried it.** That part I stand behind and it is why this
was worth stopping for: a visitor would have seen `4.99-CONTROL` as a version on
an Avenger Stalker's missile rack.

## WHAT I COULD NOT REPRODUCE CLEANLY

    run A   file absent before -> exit 0 -> file PRESENT after, plant in gen.js
    run B   file absent before -> exit 1 -> file absent after
    run C   file absent before -> exit 1 -> file PRESENT after

**Three runs, three outcomes, from the same starting state.** That is not a
mechanism I can name, and naming one anyway is what I did twice tonight. The
control also has more than one plant section and I have only read one of them.

## WHY I AM STOPPING RATHER THAN CHASING IT

It is 03:10. The control mutates a real data file and re-runs a generator that
C1 claimed today, and I have already twice asserted a cause I could not show.
**A third guess would be worse than the defect.**

**The tree is clean** - no plant file, `4.99-CONTROL` in neither `_src` nor
`_deploy`, and `loadout_data.gen.js` differs from HEAD by three lines that are
C1's livery and display-name work, not mine.

**The item for whoever takes it**, and it is mine: `_verify_loadout_fitment.py`
can leave a planted value in `data-layer/editability_patches.json` and therefore
in the shipped data layer. Reproduce by running it repeatedly from a clean
state and watching that path. **Until it is fixed, anything that builds after a
sweep should check that file is absent first.**

## Q39 AND Q37 ARE UNAFFECTED AND STILL DONE

Both were verified after the plant was cleared:
`_verify_loadout_fitment.py` and `_verify_ship_page.mjs` (237 assertions) both
exit 0 on a clean tree.
