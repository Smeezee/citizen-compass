# Update — `_verify_hardpoint_join.py` is green. Three models imported at 12:31 today, not a matcher regression.

**2026-08-27 21:14 local · Code (background session)** — the third of the sweep
failures C1 handed me. Exit 0, 1 assertion became 6.

## What it was

    [FAIL] G3: pass 2 changed EXACTLY the two Ares
           it changed 5: ['85X', 'Ares_Inferno', 'Ares_Ion', 'Aurora_SE', 'Starlite']

Measured, all five, before and after:

    85X           None -> '85X Limited'
    Starlite      None -> 'MISC Starlite'
    Aurora_SE     None -> 'Aurora Mk I SE'
    Ares_Inferno  None -> 'Ares Star Fighter Inferno'
    Ares_Ion      None -> 'Ares Star Fighter Ion'

**Every one goes from NOTHING to a correct full name**, by the same rule, and
none goes from one hull to another. That is pass 2 doing exactly what it was
loosened to do.

The cause is on disk, not in the matcher:

    85X.glb        2026-08-27 12:31
    Starlite.glb   2026-08-27 12:31
    Aurora_SE.glb  2026-08-27 12:31
    Ares_Ion.glb   2026-08-01 14:33

**Three models were imported this lunchtime, hours after the assertion was
written.** The expectation was right when made and stale by 12:31. The
25-entry `STILL_REFUSED` trap — the thing that would catch the loosening
catching too much — passes untouched.

## A correction to C1's steer, and it matters for the right reason

C1 handed this over with the `Aurora_SE.glb` measurement: 87.6 wide against 8.2
for every other Aurora, and the reasonable suggestion that a dimension-based
matcher would not behave sanely on it.

**This assertion is not dimension-based.** The rule that resolves `Aurora_SE` is
pure name matching — *"words of the model name appear in order inside the longer
mount-data key"* — and it returns `'Aurora Mk I SE'`, which is right whatever
shape the mesh is. The proportion and `hull_matches` gates in the same file
belong to the ALIGN step, not to this resolution.

**So the broken geometry is real and is not this.** C1's box table is still
worth having; it just does not bear on this failure, and matching it to this one
would have fixed the wrong thing.

## The assertion was replaced, not re-baselined

A bare name list could tell you the SET had grown and never that a member had
resolved to the **wrong hull** — which is the failure that actually matters when
a matcher is loosened. Each entry now records its answer:

    G3: pass 2 changed exactly the 5 recorded below
    G3: and '85X' resolves to '85X Limited'
    G3: and 'Ares_Inferno' resolves to 'Ares Star Fighter Inferno'
    G3: and 'Ares_Ion' resolves to 'Ares Star Fighter Ion'
    G3: and 'Aurora_SE' resolves to 'Aurora Mk I SE'
    G3: and 'Starlite' resolves to 'MISC Starlite'

A future import now fails **by name**, with added/missing spelled out, rather
than by a count that says nothing about which.

## Proven it can fail, by behaviour

Copied the control, changed one expected target to `'Aegis Hammerhead'`, ran it:

    [FAIL] G3: and 'Starlite' resolves to 'Aegis Hammerhead'
           it resolved to 'MISC Starlite' - a matched hull that is not this
           ship's is worse than no match at all

**Exactly that one assertion failed**, exit 1. The probe was moved to
`_to_delete/probes-2026-08-27/`, not deleted.

## Where the 14 stand

    _verify_deploy_guards.py       closed by me
    _verify_deploy_drift.py        closed by me
    _verify_hardpoint_alignment.py closed by me
    _verify_hardpoint_join.py      closed by me
    _verify_rule16_labels.py       closed by C1
    _verify_ship_gaps.py           closed by C1
    _verify_child_markers.py       diagnosed - blocked on a decision about the
                                   six coincident CIG pairs, see 21:01
    _verify_placer_candidates.py   C1: P1's output, not the overlay

**Six of fourteen closed.** The six remaining are `_verify_broken_checker_end_to_end`,
`_verify_dim.mjs`, `_verify_g3_matcher_delta`, `_verify_model_resolution`,
`_verify_ship_page.mjs` and `_verify_stage_panel.mjs` — none of them looked at
yet, and I am not going to call them anything until I have run them.

Nothing committed, nothing pushed, live site untouched.
