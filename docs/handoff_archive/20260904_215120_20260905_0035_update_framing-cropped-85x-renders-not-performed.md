# Update — three ships still cropped; the 85X renders NOT PERFORMED; section 1 blocked

**Code**

## Triage section 2 — the three framing re-checks. All three are STILL CROPPED.

Measured, not eyeballed: the eight corners of each hull's bounding box projected
through the live camera in a real browser. `worst` is the largest |NDC|; over 1.0
is outside the frame.

    ship            worstX   worstY   margin   verdict
    ATLS             0.381    1.259   -0.259   CROPPED
    ATLS GEO         0.409    1.242   -0.242   CROPPED
    Reliant Kore     0.308    1.203   -0.203   CROPPED

**All three overflow VERTICALLY and have room to spare horizontally.** That
pattern is the same on all three, which suggests the fit is being computed
against a width the stage does not have vertically, rather than three ships each
being slightly too big.

Renders kept at `docs/renders_20260905/frame_*.png`.

**Not tuning the radius.** The order is explicit that a global radius change
affects all 256 and is C1's call. Reporting the numbers, doing nothing.

## Addendum task 2 — the 85X three-way render. NOT PERFORMED.

I could not produce a trustworthy split and I am not shipping the attempt.

**Two defects in my own harness, both caught by the output rather than by an
error:**

1. **The three images came out byte-identical, 129,620 bytes each.** The
   inspector draws on demand rather than continuously, so toggling visibility
   changed the scene and the canvas never repainted. Three "different" renders
   that were the same picture.
2. **Name matching reached 26 of 985 mesh objects.** The GLB has 246 mesh-bearing
   nodes; the loaded scene has 985 mesh objects, so the loader is splitting nodes
   into primitives and the names do not carry across the way I assumed.

The three files are at `_to_delete/bogus_85x_renders_20260905/` rather than
deleted, and rather than in `docs/` where they would look like an answer.

**Reporting not performed rather than passing off three identical PNGs as a
split** - that is the whole of rule 11 and it is the second time today I have
caught my own work by looking at the numbers instead of the exit code.

## What I did establish about the 85X, which may save C1 time

**Our coordinate spaces differ by exactly the `CC_SCALE_ROOT` wrapper.** The
deployed 85X has a scene root named `CC_SCALE_ROOT` with uniform scale
**0.171213**, whose children carry **5.840674** - the two cancel to 1.0.

    my dominant pair offset  1.498 x 5.840674 = 8.747
    C1's dominant offset                        8.747

Exact. So C1's figures are mine multiplied by 5.8407, and their X=4 threshold is
0.6849 in the deployed file's own units. **Their spatial analysis was done in
un-normalised coordinates** - which does not make it wrong, but it means the
threshold cannot be applied to the deployed file as written.

Beyond that single factor our histograms still do not reconcile: theirs spans
-4..13, mine spans -37..32 after scaling, both over the same 246 mesh-bearing
nodes. I have not explained that and am not guessing at it.

## Triage section 1 — clearing the 20 stale marks. BLOCKED, and structurally.

The marks are `localStorage['cc_inspect_v1']`, in Sleven's browser. There is no
server-side or repo-side copy - I searched the tree and only the order itself and
my own updates mention the key.

**So I cannot move 20 marks to a `resolved` state.** Doing it needs either page
code in `_inspect.src.html` that migrates those specific entries on load - C1's
file, and the order names no file - or Sleven doing it himself in the browser.

Reporting rather than reaching into a page I do not own to write a migration
nobody asked for.

## Standing

Fury untouched, count 36 not 301, reported separately at 00:10. Nothing deployed.
Nothing committed.
