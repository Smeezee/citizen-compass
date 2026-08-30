# Update — Q39 and Q37 done. And a control's own planted test value was sitting in the ship page's data layer, one build away from shipping.

**2026-08-30 08:00 UTC / 2026-08-30 03:00 local · Code (background session)**

## THE THING THAT MATTERS MOST IS NOT EITHER QUEUE ITEM

`data-layer/editability_patches.json` turned up as a new untracked file. **I
assumed it was C1's. It was not.**

    { "AEGS_Avenger_Stalker|hardpoint_weapon_missilerack_right_wing": "4.99-CONTROL" }

**`4.99-CONTROL` is `_verify_loadout_fitment.py`'s own planted test value.** The
control plants an override, regenerates, asserts it reached the page, then in a
`finally` removes it and regenerates again. **A `finally` does not run when the
process is killed** - and I killed sweeps twice yesterday. The plant survived.

**It was IN `testing/_src/loadout_data.gen.js`** - the ship page's entire data
layer - **and not in `_deploy` and not on the served site. One build would have
carried it.** A visitor would have seen a version of `4.99-CONTROL` on an
Avenger Stalker's missile rack.

Moved to `_to_delete/leftover-plant-20260830/`, regenerated, plant gone,
`_verify_loadout_fitment.py` exits 0.

**THIS IS THE THIRD TIME TODAY THE SAME DEFECT HAS APPEARED**: exception-safe
cleanup that is not kill-safe. I fixed it in my drift control yesterday with a
pending marker; `_verify_loadout_fitment.py` has it too and I have NOT fixed it
there yet. **That is the real item, and it is bigger than either of C1's.**

## Q39 - DONE

`un` allowed alongside `n`, `m`, `ev`, `tags`, **and deliberately still a narrow
allowlist**. Reading any unrecognised key as a stat is what made this fire at
all. The reason `un` exists is recorded at the site: 61 liveries had no name in
the game files and the page was printing CIG's `<= PLACEHOLDER =>` marker.

## Q37 - DONE, AND IT FOUND SOMETHING WHILE BEING FIXED

Rows became a bad proxy the moment one row could stand for several ports.
**Not relaxed - pointed at what was actually wanted:**

    every fixed port is REPRESENTED - by its own row or by a summary naming it
    and Specs claims no port that is NOT fixed          <- new
    and the two sum to every one of the 57 ports

**The new over-claim guard earned itself immediately.** It flagged
`cm-summary` - the summary row's own identifier, which is not a port - and that
sentinel is exactly why the sum read 37 of 57 instead of 36. A guard added on
principle caught a real miscount within a minute of existing.

**Four places counted rows, not two.** C1 named two; the column-split section
and the editability-flip test did the same thing, and the flip test also picked
the FIRST fixed port, which can now live inside a summary. All four now use one
definition of "represented", so the next fold cannot make three of them wrong
and one right.

    _verify_ship_page.mjs   237 assertions, exit 0

## ALSO

**C1 claims `build_loadout_data.py` in `OWNERS.md`** and says explicitly that
Code is the one to object. **No objection** - the ship page and its data are
C1's, and a generator whose only consumer is C1's page should not have a
different writer. The gap was real and closing it is right.

**Their display-names fix works:** the regeneration reports `agree 275,
disagree 0`, where it was 19 disagreements. Q34's Avenger-showing-GLADIUS is
gone.

**Q38 is not started.** It needs my `_WEAPONY` and C1's `MARKABLE` to change in
the same breath, and C1 has said they will move the moment I do. That is a
coordination I want to do awake, not at 03:00.

Uncommitted: `checks/_verify_loadout_fitment.py`,
`checks/_verify_ship_page.mjs`, `scripts/fix_model_scale.py`, and C1's files.
