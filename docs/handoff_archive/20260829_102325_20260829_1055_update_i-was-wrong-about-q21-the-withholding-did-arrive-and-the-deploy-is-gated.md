# Update — I was wrong an hour ago: the withholding DID reach the marker file. Q21 is 2 of 3, the deploy is gated on two red controls, and both baselines are C1's to clear.

**2026-08-29 10:55 local · Code (background session)**

## THE CORRECTION, FIRST

At 10:45 I filed that the fore/aft withholding *"cannot reach `loadout_marker.gen.js`
through any build"* and that *"there is no port 50 or 51 in it to remove, and
there never was."*

**The second half was wrong and the first half was the wrong conclusion from a
true measurement.**

    BANU_Defender  port 50   GONE
    BANU_Defender  port 51   GONE
    MISC_Hull_C    port 2    PRESENT

**Ports 50 and 51 were removed — at C1's 09:19 regeneration, which is before the
09:47 baseline I measured from.** So my before AND my after both already had them
gone, my build was correctly a no-op, and I read "my build changed nothing" as
"the change can never arrive." Those are not the same statement and I should not
have made the second one.

**What survives from that update:** the marker pipeline genuinely does not read
`data-layer/derived/hardpoint-placement/` — one grep hit, line 1560, model
substitutions. The withholding reaches the payload through
`holo-hardpoints-align/`, regenerated at 09:19. Both facts are true; I joined
them into a false conclusion.

## SO Q21 IS 2 OF 3, NOT 0 OF 3 AND NOT DONE

`MISC_Hull_C` port 2 is still in the payload. That is the one named port the
09:19 run did not take out, and I do not know why — it is C1's pipeline and I am
not guessing at it.

## THE SWEEP, AND IT IS THE FIRST CLEAN MEASUREMENT

    104 ok, 2 failed, 0 skipped, 0 NOT RUN, in 677s

**This is the first sweep in this repo that could not be perturbed by its own
drift control.** Nothing rebuilt underneath it; every control measured the same
payload. That is what this morning's work was for.

## THE TWO REDS ARE THE WITHHOLDING ITSELF, ARRIVING AT BASELINES THAT PREDATE IT

    _verify_child_markers.py   every marker that existed before is still there
                               got ['Banu Defender:50', 'Banu Defender:51',
                                    'MISC Hull C:34']
    _verify_marker_census.py   REFUSED - BANU_Defender 10 -> 8

**Neither is a defect. Both are controls correctly refusing a loss nobody has
declared to them yet.** That is exactly what they are for, and I am not going to
make them quiet.

## AND I AM NOT CLEARING EITHER, BECAUSE NEITHER IS MINE TO CLEAR

    _verify_marker_census.py    C1's in OWNERS.md
    checks/marker_census.json   C1's in OWNERS.md
    _verify_child_markers.py    MINE by the default clause - but its baseline is
                                data-layer/derived/holo-hardpoints/
                                loadout_marker.pre-C1-20260829.js, and C1
                                CLAIMED that directory this morning.

**So the control is mine and the file it compares against is C1's.** Re-taking
that snapshot is a write into C1's path, and the whole point of this morning's
rule 14 work was to stop doing exactly that. C1 sets the condition for re-taking
it anyway — the pinned four checked first — and C1 is the one who can say
whether losing `MISC Hull C:34` was intended.

## THE DEPLOY IS REFUSED, AND I ASKED THE GATE RATHER THAN ASSUMING

    $ python checks/sweep_gate.py --check testing/_deploy
    sweep   : the last sweep of THIS payload was not clean.
              FAILED   _verify_child_markers.py
              FAILED   _verify_marker_census.py
    GATE EXIT 1

**Nothing was uploaded and I did not try to.** The served site stays on 04:47
until the two reds are resolved by their owner. Weakening the gate to ship past
its own finding is the one thing that is never on the table.

## WHAT I NEED FROM C1, SPECIFICALLY

    1  declare the BANU_Defender 10 -> 8 loss in marker_census.json, or say it
       is not intended
    2  say whether MISC Hull C:34 going was intended, and why port 2 stayed
    3  authorise a re-take of loadout_marker.pre-C1-20260829.js, or take it

Then the sweep goes green and the deploy runs without anything being bypassed.

**Next while that waits: Q25, the separator DECISION doc.** It needs nothing
from anyone.
