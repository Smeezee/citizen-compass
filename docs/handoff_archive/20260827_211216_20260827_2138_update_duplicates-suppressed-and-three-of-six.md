# Update — Duplicates suppressed and deployed. Three of the remaining six closed, and two of them were hiding a vacuous pass.

**2026-08-27 21:38 local · Code (background session)** — Sleven: *"suppress the
duplicates, then run the remaining six"*. Version `ced3facc-e045-4eff-93ec-accfd93f3b10`.

## The suppression

    12 marker(s) gave up a position shared with a lower PortId - CIG places
    some left/right pairs at one point

    no marker sits on top of another                                 ok

C3's collision assertion is green: **271 hulls, 6,412 markers, 0 coincident.**

The rule: where two base markers land on the same coordinate, **the lower PortId
keeps CIG's exact position** and the other gives it up. Numeric ids sort as
numbers, so 9 beats 10 rather than losing to it as text.

### One thing I have to say plainly rather than let it be discovered

**The port that gives up the position does not end up with no marker.** The
inheritance pass that runs next sees a weapon port without one, places it, finds
the coordinate taken, and nudges it to the first free spot - 0.006 per step in
unit space. Measured on the Buccaneer:

    HEAD   24 at (6e-05, 0.13242, 0.64298)   25 at (6e-05,  0.13242, 0.64298)
    NOW    24 at (6e-05, 0.13242, 0.64298)   25 at (0.0043, 0.13666, 0.64298)

So both ports stay clickable and the pair is separated by about six centimetres
on a 20-metre hull. **That is the same treatment two sibling guns on one mount
already get** - `10` and `10.loadout.0` differ by 0.035 on that ship today - so
it is the established convention rather than something new.

**What is guaranteed is that no two markers share a position and that CIG's own
coordinate belongs to the lower PortId. The neighbour's offset is derived, and
the code says so.** If you would rather the second port carried NO marker at
all, that is a one-line change and I will make it - but the list reaches both
either way, and a suppressed marker is a port nobody can click from the model.

Deployed to testing, 4 browser checks GREEN, deploy guard clean, 1 file
uploaded. Served check: Drake Buccaneer, 9 dots, 9 visible, model loaded.

## Three of the six, all closed

### `_verify_broken_checker_end_to_end.py` - 11/1 -> 10 passed, exit 0

    FAIL including the 6 genuinely-missing models
         271 open findings ... (0 of them DEFECTs)

The count is stale - the model library filled up today, so nothing is genuinely
missing any more. **That is not the find.**

**The find is what the stale count was holding up.** Two assertions below it
read `all(... for k in model_defects)`, and **on an empty set those pass
vacuously**. Update the count and this control would print two green lines about
DEFECTs it never looked at — hard rule 12's silent success, inside the file whose
entire subject is a checker that silently stopped looking.

Both are now guarded and report NOT PERFORMED when there is no population:

    NOT PERFORMED - no missing-model DEFECT exists right now, so the three
    assertions about DEFECT survival cannot be exercised. Reported, never passed.

And the recovery claim is now also asserted against the 271 OPEN findings, which
always have a population, instead of resting only on a set that can empty out.

### `_verify_model_resolution.py` - 22/1 -> 23/0, exit 0

    FAIL the fleet really is mostly editions  16     (asserted len(eds) > 50)

**Both halves of that were wrong.** `resolve_ship_models.py` skips any class
already wired to a model, so `editions` is not the fleet's editions - it is the
editions STILL NEEDING RESOLUTION. It fell to 16 because the library filled in.
**The pipeline working, read as a failure.**

And a count of fleet composition is not what section 5 defends anyway. Replaced
with the assertion that keeps the five checks below it honest: they are all
`all(... for e in eds)` and would pass on an empty list, so an empty list now
FAILS here rather than sailing through. `--self-test` still exits 1.

### `_verify_g3_matcher_delta.py` - 8/1 -> 10/0, exit 0

    FAIL G3: the 25 still-refused ships are still refused, by name
         44 ships are still skipped, expected 25

**It said "by name" and checked `len(skipped_after) == 25`. It checked no name.**
44 is not a regression: models keep arriving, and a model with no ship data to
match is correctly skipped.

Now asserted by name, and **the list is imported from
`_verify_hardpoint_join.py` rather than copied** - one must-not-match list in the
repo instead of two that drift (rule 14). That file checks the 25 against the
RULE; this one checks them against the join REPORT.

Proved it can fail: swapped one entry for `Ares_Ion`, which IS matched, and only
that assertion failed. Probe moved to `_to_delete/probes-2026-08-27/`.

## Still running

`_verify_dim.mjs`, `_verify_ship_page.mjs`, `_verify_stage_panel.mjs` - the three
browser ones. Results next.

## Still on hold

`_verify_child_markers.py`'s re-baseline. One of its two blockers is gone; the
other stands - nobody has said the Retaliator's new mirrored quad is right rather
than tidier.

Nothing committed, nothing pushed, live site untouched.
