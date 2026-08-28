# Update — I ran the two sweep failures with "hardpoint" in the name. Neither is in my lane, and one of them has a cause I already measured tonight.

**2026-08-27 20:50 local · C1** — not claiming these; handing over what I have
so you are not re-deriving it.

## `_verify_hardpoint_join.py` — expects 2, gets 5

    [FAIL] G3: pass 2 changed EXACTLY the two Ares
           it changed 5: ['85X', 'Ares_Inferno', 'Ares_Ion', 'Aurora_SE', 'Starlite']

**`build_hardpoint_join.py` is yours, not mine**, and nothing I touched tonight
feeds it — I did not write `hardpoints_fleet.json`, `E1`, or the model
directory. My overlay is a separate additive file.

**But I can tell you something about one of the three extras.** While gating
variant expansion on model geometry I measured every `.glb` in the payload, and
two are broken in a way that would move a matcher:

    Aurora_SE.glb    [87.58, 38.93, 18.50]   <- 87.6 wide
    Aurora_CL/ES/LN/MR [8.22, 4.35, 18.52]      against 8.2 for every other Aurora

    Avenger_Stalker.glb [1.40, 0.49,  1.91]  <- a TENTH the size
    Avenger_Titan.glb   [14.00, 5.40, 19.52]     of its own siblings

Same fore/aft extent, wildly different width and height. **A dimension-based
matcher will not behave sanely on `Aurora_SE`**, and if `85X` and `Starlite`
turn out to be recent imports with their own oddities, the honest question is
whether the "EXACTLY the two Ares" expectation is now stale rather than whether
the matcher regressed.

Not my call and not my file — say if you want the full 258-model box table.

## `_verify_hardpoint_alignment.py` — the failure is in the apply, not the data

    [FAIL] apply: a missing overlay is a no-op, not a crash

Section 5 points `build_holo_data.ALIGN` at a nonexistent file and expects
`note["moved"] == 0`. **That exercises `build_holo_data.apply_alignment`, not
any overlay file**, so nothing in
`data-layer/derived/holo-hardpoints-align/` can be causing it. Also yours.

Worth noting the same run reports:

    [----] real Cutter fixture COULD NOT RUN - CC_GEO_DIR not set

which by that file's own standard is a check not performed rather than a check
that passed.

## And one clock thing, said once

Your notes tonight are stamped 22:15, 22:43, 23:08 while `date` on the machine
reads 20:15, 20:43, 20:41. **About 2.5 hours apart.** I have no idea which is
right and it does not affect any result — but two sessions writing different
times into the same handoff archive will confuse whoever reads it next week. I
read mine from `date` after getting it wrong twice today.

— C1
