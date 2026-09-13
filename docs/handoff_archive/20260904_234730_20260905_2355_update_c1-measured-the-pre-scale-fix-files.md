# Update — SOLVED: C1 measured the PRE-SCALE-FIX files. And the Fury 301 still is not there.

**Code**

Sleven asked whether there was really nothing to do. There was. I had been
handing the reconciliation back to C1 when I could measure it myself.

## Every copy of both models on disk, measured

    file                                              pairs  coin      X range  root
    testing/_deploy/models/85X.glb                      344     3   -6.2..5.4  CC_SCALE_ROOT
    sc-ships/_uvfix_all/85X.glb                         344     3   -6.2..5.4  CC_SCALE_ROOT
    _stage_scalefix_.../85X.glb                         344     3   -6.2..5.4  CC_SCALE_ROOT
    models_pre_uvfix_.../85X.glb                        344     3   -6.2..5.4  CC_SCALE_ROOT
    pre_scale_fix_20260827T172853Z/models/85X.glb       344    40   -3.2..8.7  ORIG_85X
    _stage_fleetyards_...T170938Z/85X.glb               344    40   -3.2..8.7  ORIG_85X
    _stage_fleetyards_...T171012Z/85X.glb               344    40   -3.2..8.7  ORIG_85X

    testing/_deploy/models/Fury.glb                     594    36   -3.4..3.0  CC_SCALE_ROOT
    sc-ships/_uvfix_all/Fury.glb                        594    36   -3.4..3.0  CC_SCALE_ROOT
    _stage_scalefix_.../Fury.glb                        594    36   -3.4..3.0  CC_SCALE_ROOT
    models_pre_uvfix_.../Fury.glb                       594    36   -3.4..3.0  CC_SCALE_ROOT
    pre_scale_fix_.../Fury.glb                          594    55   -1.8..1.8  MISC_Fury
    _stage_fleetyards_...T170938Z/Fury.glb              594    55   -1.8..1.8  MISC_Fury
    _stage_fleetyards_...T171012Z/Fury.glb              594    55   -1.8..1.8  MISC_Fury

Fourteen copies. Every one measured, not sampled.

## The 85X is explained completely

**C1's histogram is the PRE-SCALE-FIX file.** Its X range is **-3.2 .. 8.7** -
the two clusters at 0 and 8.75 that C1 described, with the gap between them.
Root node `ORIG_85X`.

The deployed file has been through the scale fix: root `CC_SCALE_ROOT`, range
recentred to -6.2 .. 5.4. **The two ships are still there** - the fix moved and
normalised the file, it did not merge them.

So C1's X=4 threshold maps to about **X = 0.82** in the deployed file, by the
linear map between the two ranges. **The renders I already produced split at
0.605 of the span; the correct point is 0.605.** They are right, and my earlier
caveat can be retired: the pictures do show C1's division.

One loose thread in C1's own figures: their coincident count of **3** for the
85X matches the DEPLOYED file, while their histogram matches the PRE-FIX one.
Those two numbers come from different copies.

## The Fury 301 is NOT a file-choice problem, and now that is proven

    deployed and every post-fix copy   36
    every pre-scale-fix copy           55

**No copy of the Fury that exists on this machine yields 301**, at any
tolerance from 1e-6 to a full metre, under world OR local translation
comparison. The stop condition stands and the Fury is still untouched.

Now that the 85X divergence has a cause, the Fury's does not - which makes it
more interesting, not less. If C1 got 301 from a Fury, it is not one of these
fourteen files.

## Task 1 - I cannot reach the browser, so here is the thing that can

`docs/clear_stale_marks_console_snippet.js` - paste into the console on the
inspector page.

- **Dry run by default.** Prints a table of exactly which marks it would resolve
  and why, and writes nothing until `APPLY` is set to true.
- Sets `resolved: true` and clears `bad`. **Leaves `note` and the reason chips
  untouched** - the order says preserve his note text, so nothing is deleted,
  only reclassified.
- The three named files are matched by name; the seventeen orientation marks are
  matched on what he WROTE, because the filenames were never what they had in
  common.
- Safe to run twice - an already-resolved entry is skipped.

I did not put this in `_inspect.src.html`. That is C1's file, this order names no
file, and a migration running silently on every load is a bigger thing than a
one-time paste.
