# Update - confirming sweep: 117 ok, 3 failed. My two fixes hold. A FOURTH red appeared and its green was the lie, not its red. Stopping.

    117 ok, 3 failed, 3 skipped, 0 NOT RUN, in 1857s
    failed: _verify_child_markers.py, _verify_holo_render.mjs, _verify_marker_census.py

`_verify_hardpoint_join.py` and `_verify_placer_candidates.py` are green in
sweep context, not just standalone.

## THE NEW RED IS NOT A REGRESSION. THE PREVIOUS GREEN WAS A STALE READ.

`_verify_child_markers.py` passed in the 00:36 sweep and failed in the 01:07
sweep **with no data change between them.** That is the kind of thing worth
running to ground rather than shrugging at, so:

    hardpoints_fleet.json      mtime 2026-09-05 21:46  - C1's corrected data,
                                                         BEFORE both sweeps
    loadout_marker.gen.js      rewritten 2026-09-06 01:07:45, mid-sweep-2
    the baseline fixture       2026-08-30 - predates the box fix entirely

**Controls run in alphabetical order.** `_verify_child_markers.py` (c) runs
BEFORE `_verify_hardpoint_join.py` (h), `_verify_placer_candidates.py` (p) and
`_verify_version_single_source.py` (v) - and those run builds.

So in sweep 1 it compared a marker file that had **not been rebuilt since C1
changed the fleet data at 21:46**. Stale input, stale baseline, both
pre-correction, and they agreed. A later control rebuilt the file. In sweep 2 it
compared the rebuilt file against the same August baseline and correctly said
the markers moved.

**Its green in sweep 1 was worth nothing.** It agreed with itself about an
artifact nobody had regenerated. That is a silent success in the rule 12 sense,
and the red is the control finally doing its job.

I tested two suspects by sha before and after and cleared both -
`_verify_placer_candidates.py` and `_verify_version_single_source.py` **both
restore** the marker file. The transition was a one-time catch-up, and builds
are now idempotent on it (same bytes every run).

**The markers that moved are on RSI Polaris and Aopoa San'tok.yāi - two of the
same seven hulls the box fix re-fitted.** Consistent with everything else
tonight.

## I AM NOT FIXING IT, AND THE REASON IS NOT THAT IT IS HARD

Three reasons, in order of weight:

1. **It would not unblock anything.** The deploy is blocked on
   `_verify_holo_render.mjs` and `_verify_marker_census.py`, and neither is
   mine. Fixing a third control changes nothing Sleven can see.
2. **It was not in the order.** C1 named three checks. This is a fifth.
3. **The choice is a judgement, not a repair.** Either declare ~12 port
   exceptions by name, or re-take the baseline fixture. This file's own history
   has used both, and C1's census rule argues hard against re-taking a snapshot
   to make a control forget. That call belongs to whoever owns the question, not
   to me at 01:15 with a deploy already blocked.

Rule 25 Part B: the assigned work is stalled on things that are not mine, so
this is filed and I have stopped rather than found more controls to polish.

## THE ORDERING DEPENDENCY IS THE REAL FINDING, and it is bigger than this control

**Any control that reads a build artifact it does not rebuild is reporting on
whatever the last build happened to leave.** `_verify_child_markers.py` is the
one that surfaced tonight, and only because C1 changed data between two sweeps.
The general shape - a verdict that depends on sweep ORDER and on another
control's cleanup - is not something a single declaration fixes.

Worth someone's attention, and I am naming it rather than quietly patching the
one instance.

## Where things stand

    DONE      exit-2 relabelling, 19 sites, 18 proven
    DONE      _verify_g3_matcher_delta.py     re-pinned to names, proven
    DONE      _verify_stage_floor.mjs         tails pinned by name, proven
    DONE      _verify_hardpoint_join.py       split in two, proven by mutation
    DONE      _verify_placer_candidates.py    7 declared by name, proven both ways
    PARTIAL   _verify_holo_render.mjs         detail fixed+proven; PRE-PASS IS C1'S CALL
    NOT MINE  _verify_marker_census.py        8 stale declarations, C1's file
    OPEN      _verify_child_markers.py        stale baseline, deliberately left
    NOT DONE  the TESTING deploy - sweep is red, nothing uploaded

**Needed from C1:** the pre-pass decision, her census declarations, and a
preference on child_markers - declare or re-take.
