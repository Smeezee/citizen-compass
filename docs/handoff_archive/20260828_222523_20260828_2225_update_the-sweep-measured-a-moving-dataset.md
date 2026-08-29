# Update — That sweep measured a moving dataset. C1 regenerated the overlay while it ran, and three marker controls disagree with themselves ten minutes apart.

**2026-08-28 22:25 local · Code (background session)**

    103 ok, 3 failed, 0 skipped, 0 NOT RUN, in 683s

    FAIL  _verify_marker_census.py
    FAIL  _verify_marker_provenance.py
    FAIL  _verify_marker_spread.py

**Do not read those three as findings. The sweep was measuring something that
was being rewritten underneath it.**

## The evidence

    sweep ran                              22:12 - 22:23
    data-layer/hardpoint-placement/        written 22:18:56
    data-layer/holo-hardpoints-align/      written 22:19:08
    testing/_src/loadout_marker.gen.js     written 22:23:24

**C1 regenerated the placement and the client overlay in the middle of the
run**, and the sweep's own `_verify_deploy_drift.py` then rebuilt the marker
file from the new data. Controls that ran before that point read one dataset and
controls that ran after read another.

The count says it plainly:

    markers carrying a label, during the sweep    6,133
    markers carrying a label, ten minutes later   6,060

And re-running the same three now:

    _verify_marker_provenance.py   FAILED in the sweep -> passes now
    _verify_marker_spread.py       FAILED in the sweep -> passes now
    _verify_marker_census.py       passed in the sweep -> FAILS now (ORIG_m80)

**Three controls, all disagreeing with their own result from ten minutes
earlier, in both directions.** That is not three defects; it is one measurement
taken during a write.

## The structural half, which is mine

This is the third time today a sweep has been perturbed, and twice it was
avoidable:

    this morning   I edited checks/ while a sweep executed those files
    this evening   C1 regenerated data-layer/ while a sweep read it
    all day        the sweep's OWN _verify_deploy_drift.py rebuilds the
                   artifacts that later controls read, so a control's result
                   depends on where its name sorts relative to "d"

**The third one is a real defect in the sweep and it is mine.** A control that
rebuilds shared artifacts mid-run makes every control after it a measurement of
a different state from every control before it. It has not bitten on its own
because the rebuild is normally byte-identical - but "normally" is doing all the
work in that sentence, and tonight the data moved underneath it.

**I am not fixing it in this pass**, because the fix is a design decision rather
than a repair: either the sweep refuses to run controls that mutate shared
state, or it snapshots the payload first, or the drift control stops rebuilding
and reports instead. That belongs in a `docs/DECISION_*` with C1, not in a
20-minute edit at 22:30.

## What I am NOT doing

**Re-running the sweep now.** The data settled at 22:19 and has not moved in six
minutes, but a receipt taken while C1 may still be mid-run is worth nothing, and
I have already spent one 683-second sweep finding that out.

The gate is refusing on the stale receipt, which is correct: the payload
fingerprint moved to `9ccd3bbf` and nothing has vouched for it.

## What is true regardless

    Q13, Q14, Q15   done and verified individually, not by the sweep
    Q7              81 of 104
    served site     f278ca37; its ship page still matches the last build
    live site       404, never deployed

`_verify_marker_census.py`'s current failure on `ORIG_m80` may be real or may be
the same moving target. **It is C1's control and C1's data.** I will look at it
when the dataset has been still for long enough to mean something, and say which
it was.
