# ORDER — six hulls replaced from the game client. Sweep, deploy, and look at them.

From: C1 (Cowork), 2026-09-05
For: Code

Sleven's instruction: the ships we fixed go on the test site, in the same
holographic style as everything else. Six are in. **Models only - I have touched
no page source in this order.**

## What changed in `testing/_deploy/models/`

    X1                1,811,152   was 2,010,056
    Freelancer          783,336   was 4,638,900
    Freelancer_DUR    1,170,728   was 1,172,016
    Freelancer_MAX      909,624   was 1,087,284
    Freelancer_MIS      936,128   was 1,155,148
    85X                 724,288   was 3,107,272

Originals preserved at
`_to_delete/models_pre_client_swap_20260905T053243/`. All 256 models re-checked
after the swap: every one is a valid GLB.

## Why these six, and why they are drop-ins

Built from `Data.p4k` with `tools/ivo/ivo_mesh.py`, then Draco-compressed with
the existing `testing/_tools/cc-uvfix-compress.cjs`.

**They need no rescaling and that is measured, not assumed.** The Cutlass Black
converted from the client comes out at 26.146 x 10.035 x 35.722 against the
deployed model's 26.146 x 10.236 x 35.717 - the same space, the same axis order,
metres for metres. Four of the six match their old extents to within 0.5%:

    Freelancer_DUR   old 22.59 8.80 37.17   new 22.58 7.92 37.17   ratio 1.000
    Freelancer_MAX   old 31.39 8.80 36.71   new 31.39 7.92 36.77   ratio 0.999
    Freelancer_MIS   old 22.58 8.80 37.17   new 22.58 7.87 37.36   ratio 0.995
    85X              old 10.10 5.28 13.09   new 10.10 2.66 13.09   ratio 1.000

**The two that do NOT match are the two that were wrong**, and the numbers say
how:

- **Freelancer** old 24.89 x 8.10 x 32.17, new 22.58 x 7.81 x 36.71. The old one
  is four and a half metres too short and two too wide. Note the three variants
  above already matched v2 - only the BASE Freelancer was still the old airframe,
  which is exactly the one Sleven noticed.
- **85X** old height 5.28, new 2.66 - **exactly twice**. That is the duplicate
  copy, measured. Width and length were already correct and are unchanged.

## The compressor had a bug and it is fixed

`cc-uvfix-compress.cjs` wrote its temp file as `dst + '.part'`, and
gltf-transform picks its output FORMAT from the extension - so it wrote glTF
JSON plus an orphaned sidecar `.bin`, then renamed the JSON to `.glb`. Six hulls
came out at 32 KB for 164,000 triangles, which is the only reason it was looked
at. Temp name now keeps the `.glb` suffix.

**The 256 shipped models were checked and all are real GLBs - nothing live was
damaged by this.**

## And the 40% triangle drop in compression is correct

Every hull lost ~40% of its triangles to Draco and that is right, not a loss:

    X1 source triangles           333,088
      two indices identical       147,519  (44.3%)
      distinct indices, same XYZ    4,025  ( 1.2%)
      degenerate total            151,544  (45.5%)
      compressor kept             181,544  (54.5%)

The compressor removed the degenerates and nothing else - the kept count is
exactly the non-degenerate count. CIG's index buffers carry degenerate padding
and my reader passes it through; the compressor drops it. Worth filtering at
conversion so the intermediate counts stop being misleading, but it changes
nothing visible.

## TASKS

1. **Run the control sweep.** The payload has changed again since the last
   order - the six models are new on top of the two page changes.
2. If clean, **deploy testing.**
3. **Load these six in the inspector and look at them.** X1 was one of the
   see-through four - report whether it still is. The 85X should now be one
   ship, not two. Say what you see; a picture is the only thing that settles it.
4. Still outstanding from the fit order: the corner-projection margins for
   **ATLS, ATLS GEO and Reliant Kore** after the deploy.

## NOT done, and not to be started here

**X1 Force, X1 Velocity and Cyclone TR** are not single files in the archive -
they are a base hull plus swapped parts (`ORIG_X1_Velocity_Fin_Left`,
`TMBL_Cyclone_Module_Combat` and so on) that have to be composed and placed.
That is mine. **Centurion** is still unidentified.

```
python checks/run_all_controls.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## Standing constraints

- Testing only. Do not deploy the live site.
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
