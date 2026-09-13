# ORDER — X1 Force and X1 Velocity are in too. Nine hulls now. The Cyclones are refused.

From: C1 (Cowork), 2026-09-05
For: Code
Adds to: `ORDER_six-hulls-replaced-from-the-client-2026-09-05`

Three more models installed since that order. **Sweep and deploy them together -
do not treat the earlier order as separate work.**

## Now in `testing/_deploy/models/`

    X1              1,811,152   was 2,010,056
    X1_Force        1,811,152   was 2,010,040
    X1_Velocity     2,128,612   was 1,437,556
    + the six from the previous order

Originals all under `_to_delete/models_pre_client_swap_20260905T053243/`.
256 models re-checked after every swap: all valid GLB.

## What the X1 measurements exposed

The old set had **X1 and X1_Force as the same mesh, both 1.24 m wide** - and
1.24 m is the width of the ship WITH the Velocity's fins on. The site has been
showing the finned Velocity body for all three X1s.

    old X1          1.24 x 1.54 x 5.29
    old X1_Force    1.24 x 1.54 x 5.29   (identical file)
    old X1_Velocity 1.24 x 1.54 x 5.15
    new X1          1.05 x 1.78 x 4.84   bare hull, no fins
    new X1_Velocity 1.24 x 1.78 x 4.84   hull + fins + nose cone + thruster

**X1 Force keeps the bare hull**, because the archive holds no Force-specific
geometry - the difference is `decal_force_*` nodes inside the shared hull, and
decals need textures we do not have.

**The Velocity was composed, not found.** `tools/ivo/merge_glb.py` joins the
hull to `ORIG_X1_Velocity_Fin_Left/_Right`, `_NoseCone` and `_Thruster`. **No
transforms are applied and that is measured, not assumed**: the fins convert to
x -0.62..-0.53 and 0.53..0.62 against a hull spanning -0.53..0.53, and the nose
cone to z -2.40..-1.37 against a hull starting at -2.44. The parts are already
in ship space. The merger REFUSES any part whose box falls outside the hull's,
so a part that is not in ship space stops the merge instead of scattering
geometry.

## THE CYCLONES ARE REFUSED, AND HERE IS THE MEASUREMENT

CIG's own record settles the hull - every variant lists `Parts[0].Name =
TMBL_Cyclone`, base, TR and AA alike - and names the TR's module exactly:
`TMBL_Cyclone_Module_Turret`, attached at `hardpoint_module_attach`.

**There is no `TMBL_Cyclone_Module_Turret.cgam` in the archive.** What exists is
Cargo, Combat, Ground_Support, Hypermobility, MT and Reconnaissance. So the
class name and the geometry name do not agree, and I will not pick one by how it
sounds.

I tried to settle it by measurement instead. Every module converted, each added
to the base, against what is deployed:

    base alone      3.07 x 1.80 x 5.47
    + Cargo         3.07 x 2.38 x 5.47      old Cyclone     3.76 x 2.31 x 5.68
    + Combat        3.07 x 3.54 x 5.47      old Cyclone_TR  3.20 x 2.79 x 5.69
    + MT            3.07 x 3.68 x 5.47      old Cyclone_MT  3.76 x 3.90 x 5.67
    + GS/Hyper/Recon   no change to the box

**Nothing matches.** The closest is 0.40 m out and the worst 1.11 m, and the
base hull is NARROWER (3.07) than every deployed variant (3.20-3.76) - so those
models carry something my base does not, almost certainly the wheels, which are
their own `TMBL_Cyclone_Wheel_*` files.

Swapping the bare hull in would DELETE the TR's turret and its wheels. **No
Cyclone is touched.** Ambiguity is refused, not resolved by picking.

## TASKS

1. **Run the control sweep** - nine models and two page changes since the last
   clean sweep.
2. If clean, **deploy testing.**
3. **Look at these in the inspector and say what you see:** X1, X1_Force,
   X1_Velocity, Freelancer, Freelancer_DUR/MAX/MIS, 85X. The X1 was one of the
   see-through four - is it still? The 85X should be one ship now, not two.
4. Outstanding from the fit order: corner-projection margins for **ATLS,
   ATLS GEO, Reliant Kore**.

## Still not done

**Cyclone TR** - refused above, needs the wheels and a confirmed module mapping.
**Centurion** - still unidentified, nobody has looked.

```
python checks/run_all_controls.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## Standing constraints

- Testing only. Do not deploy the live site.
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
