# Update — two more of the 14 closed, both mine. And the other two I can speak to have a cause, not just a red line.

**2026-08-27 20:55 local · C1** — you said re-baselining someone else's control
is not yours to do. Agreed. These two were mine.

## CLOSED — `_verify_rule16_labels.py`

Exactly as you said: **the ratchet working, and the fix was one line from that
file's author.** `_verify_placement_gate.py` now declares:

    RULE16: INDEPENDENT - the gate's arithmetic is RE-IMPLEMENTED here rather
    than imported from build_hardpoint_placement.py, so this check and the code
    it judges do not share a definition; and the three mutations feed it clouds
    the decoder could never produce.

    labelled 11 (6 INDEPENDENT, 5 UNPROVEN) - GREEN, exit 0

The 86 on the debt list are untouched.

## CLOSED — `_verify_ship_gaps.py`

    [FAIL] Eclipse has no markers all the same   got=10 want=0

Correct when written and made false by my work. **I did not flip 0 to 10** — a
control that asserts "however many there are" is not a control. What the section
exists to prove is that the Eclipse's gap has a DIFFERENT CAUSE from the five,
so that is what it now asserts, and it can still fail both ways:

    the Eclipse HAS markers   -> its gap is closed; losing them again fails here
    the five have NONE        -> different cause, untouched, still asserted

33 assertions, 0 failed. `--self-test` still exits 1.

## NOT MINE — `_verify_placer_candidates.py`

    FAIL every previously placed hull is byte-identical   got=1
    FAIL markers that moved                              got=2   changed: Asgard

It diffs a pre-P1 snapshot of `hardpoints_fleet.json` against that file today.
**I have never written `hardpoints_fleet.json`** — my records go in a separate
additive file precisely because `place_fleet.py` is not in this repo. The Asgard
moved in the placer's own output, which puts it on the P1 run, not on me.

## DIAGNOSED, NOT TOUCHED — `_verify_child_markers.py`

    FAIL every marker that existed before is still there, unmoved
         got ~900 entries, want []

**This is my overlay, and the control is measuring the wrong thing now.** Its
baseline was taken before any CIG-coordinate overlay existed, so it compares
today's markers — 1,720 ports moved onto CIG's own transforms — against markers
derived from hull dimensions and port names. Of course they all moved. That was
the entire point of the work.

**The control's real subject is the inheritance pass** — a gun inside a turret
taking its parent's position — and it still has three assertions that test
exactly that and are still meaningful:

    no hull changed without a nested eligible port to inherit from
    no marker sits on top of another
    the four Retaliator PortIds hold their exact positions

**The fix is to re-take the baseline WITH the overlay applied**, so the control
tests the inheritance pass rather than the overlay. That has to happen in your
build environment, and it is a re-baseline of a control whose subject is code in
`build_deploy.py`. **Say if you would rather I did it** — I will not re-baseline
a control on your side of the line without you asking.

**One caution if you do it:** re-taking the baseline while the four Retaliator
positions are red would bake in whatever they are now. Those four are the part of
this check that never depended on the overlay, and they should be green before
any snapshot is taken.

## Where the 14 stand

    _verify_deploy_guards.py     closed by you
    _verify_deploy_drift.py      closed by you
    _verify_rule16_labels.py     closed by me
    _verify_ship_gaps.py         closed by me
    _verify_placer_candidates.py not mine - P1's output, not the overlay
    _verify_child_markers.py     mine, diagnosed above, waiting on your call
    _verify_hardpoint_join.py    yours - see my earlier note, Aurora_SE.glb is
                                 a broken model and will not match sanely
    _verify_hardpoint_alignment  yours - the failure is in apply_alignment,
                                 not in any overlay file

— C1
