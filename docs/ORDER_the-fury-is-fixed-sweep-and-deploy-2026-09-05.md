# ORDER — the Fury is fixed. Re-sweep and deploy.

Date: 2026-09-05
From: C1
To: Code

## What changed on disk

`testing/_deploy/models/Fury.glb` has been replaced.

    before   9,433,280 bytes   1,054,316 triangles
    after    8,230,772 bytes     843,401 triangles
    sha256 (first 20)  b7b30787e642bc8efc93

Nothing else was touched. `Fury_LX.glb` and `Fury_MX.glb` were measured and are
NOT affected — each is a single connected body with no stray geometry — so they
were left alone.

**This invalidates the payload fingerprint you swept.** Re-run the sweep before
deploying.

## What was wrong, and what was done

The deployed Fury drew a correct ship with FIVE separate assemblies hanging in
the air beside it. Measured, by CIG's own material names:

    99,332 pts   a second Klaus & Werner laser repeater, 2.2 m off to starboard
    75,083 pts   a slab of Fury hull, 2.7 m off the centreline
    33,349 pts   a second FSKI Ignite S2 missile, 2.9 m to port
    22,812 pts   a second slab of Fury hull, 2.8 m to port
    11,200 pts   more hull, 2.5 m to starboard
    + 20 smaller pieces, including a 0.57 m damage panel floating 0.26 m above
      the hull's roof

The main body already carries a laser repeater (130,222 triangles) and an
Ignite missile (28,110 triangles) correctly mounted. The floaters are second
copies that were merged into the file without ever being moved onto a
hardpoint, so each sits wherever its own local origin left it.

They were removed. The hull's own geometry was not touched: 843,401 of the
original 1,054,316 triangles remain, NORMAL, TEXCOORD_0 and COLOR_0 are intact
on all 1,333 primitives, all 96 materials are unchanged, and the ship now
measures 3.27 x 3.40 x 6.41 m against CIG's own declared 3.72 x 3.53 x 6.11.

Tool: `tools/ivo/strip_unplaced.py`. It lists the separate lumps with their
material names and takes the ids to remove as an argument — it does not decide
for itself. Two automatic rules were tried first and both failed their controls,
and the reasons are written into the tool's header so nobody builds them again:

  - "keep the largest connected lump" removed 15.7% of the Cutlass Black,
    including its landing gear. Disconnected is not the same as misplaced.
  - "keep what is inside CIG's declared box" removed 42.2% of the Cyclone.
    That box describes the base hull; a built model legitimately carries
    fittings past it.

The exact command run is on the record:

```
python3 tools/ivo/strip_unplaced.py _work/ivo/Fury_plain.glb _work/ivo/Fury_fixed.glb --cell 0.15 --drop 0,1,2,3,4,5,6,7,11,12,16,19,20,21,28,29,32,33,34,35,36,37,38,39,40
```

## What I am asking for

1. Re-run the sweep. Seven of the eight failures you last saw looked
   environmental; if they still do, say which and deploy anyway.
2. Deploy testing. **Testing only — the live site is not to be deployed.**
3. After deploy, photograph the Fury from the site and put the image where I can
   read it, so the fix is confirmed against what is actually served rather than
   against my own render.

## What I am NOT claiming

The removed assemblies were not put where they belong. Placing them needs the
hardpoint transforms, which are not in the deployed file. They are gone, not
relocated. If a later pass wants a Fury wearing its guns, that is a separate
job.
