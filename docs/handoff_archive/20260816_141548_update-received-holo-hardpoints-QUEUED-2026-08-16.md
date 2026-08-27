# Update: received the holo hardpoint order. QUEUED, not started.

The order says "Queued behind the collector rebuild. Do not start until that is
done." **The collector rebuild is items 1, 2, 3, 5, 6, 7 and 8 of Version One,
and none of them are started.** So this sits behind roughly a fortnight of work
and I have not begun it.

## Premise verified, read-only, because three have been wrong this week

Every fact in the order checks out:

    hardpoints_fleet.json     present, 0.6 MB
    ships                     167          (as stated)
    hardpoints                1,798        (as stated)

    'hardpoints_fleet' in testing/_deploy/holo.html : 0
    'pos_model'                                     : 0
    'pilot_dps'                                     : 0

**The data is real, complete, and completely unreferenced.** The order's
diagnosis is correct: it was built, it was reported, and the last step never
happened.

That is the third instance this week and the pattern is worth naming, because it
is the same one that produced the console build and the unreachable loadout
page: **the artifact was never asked whether it had the property.** Nobody
grepped the deployed page. One command would have shown it.

## Two things I would want settled before this starts

1. **The scale problem (§2) is the actual job**, and it is not a wiring task.
   `pos_model` is in each model's own units and those units differ across the
   library, so a marker tuned on one hull lands wrong on another. `build_holo_data.py`
   already solves a version of this - it computes `world = unit * (max(bbox size)/2)`
   per model, which is how the 167-ship fleet placement was done in the first
   place. Whether that same normalisation is correct for hardpoints is the
   question worth answering first, and it is answerable in an afternoon of
   measurement rather than guessed at during a rewrite.

2. **Acceptance 1 requires checking all 167, not a sample.** That means a
   programmatic check that renders or at least projects every hull, not eyeballing
   three. Worth building the checker before the feature, because it is also how
   the "renders correctly vs does not, summing to 167" number gets produced
   honestly rather than estimated.

Neither is started. Recorded so the next session knows the shape of it.

## The queue, as I understand it

    1. Version One collector - items 1,2,3,5,6,7,8   NOT STARTED
    2. This order                                    QUEUED behind it

If that priority is wrong - if Sleven would rather have the 3D viewer working
than the installer - it is one sentence to reorder, and I would rather be told
than assume. The holo job is days; V1 is a fortnight.
