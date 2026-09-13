# ORDER — inspector fix. Rebuild and deploy testing.

From: C1 (Cowork), 2026-09-04
For: Code

Sleven reached ship 9 of 258 in the inspector and sent a screenshot: the 600i
Executive Edition's nose rendered in iridescent blue and magenta across half the
hull, hard-edged, the rest grey.

## Cause — my bug, in the inspector only. The site is fine.
`GLTFLoader` sets `material.vertexColors = true` on any primitive carrying `COLOR_0`.
Six of the 258 models carry one and **the 600i Executive Edition carries eight**. The
inspector reuses the file's own material and only overrode metalness, roughness,
colour and side — so the loader went on tinting the hull with whatever a third party
baked into the file.

**`cc_viewer.js` never had this.** It replaces every material with its own shader and
cannot read vertex colours. `grep -c "vColor\|vertexColors" cc_viewer.js` returns 0.
The ship page was never affected.

## Fixed in `testing/_src/_inspect.src.html` (C1)
- `m.vertexColors = false` in `dress()`, with the reasoning in the file.
- Two new reason chips: **wrong colours** and **not the right ship**. Sleven had no
  way to file what he was looking at, which is a gap in a tool whose whole job is
  letting him file things.

Verified in a real browser against the real model: hull renders uniform grey, all
eight chips present, 0 page errors. Previous source preserved at
`_to_delete/_inspect.src.html.pre_vertexcolour_*`.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

Sleven's marks are held in his browser, not in the page, so a redeploy will not lose
the ships he has already walked.

## A SEPARATE FINDING, reported not acted on
The 19 models imported from Fleetyards are **structurally unlike the other 239**.
Every one of the 239 is one mesh with one material named `Default`. The 19 are not:

    600i Executive Edition   2 meshes   2 materials   8 colour sets   'Material', 'Glass.001'
    85X                    112 meshes 113 materials   1 colour set    'orig_85x_mtl_Grey', ...
    Fury                   406 meshes  96 materials   1 colour set    'misc_fury_mtl_Decal_POM_A', ...
    Aurora Mk II, Aurora SE, Basher, Hermes, M80, MOTH, Mantis, PTV, Pitbull,
    Starlite, Tiburon, Tyilui, UTV, Merchantman, Odin, Arrastra   similar

`Glass.001` and `DefaultMaterial` are Blender's own duplicate-name conventions, so
these files have been through somebody's tool rather than coming straight out of a
holoviewer export.

**And the 85X and the Fury carry CIG's own material naming** — `orig_85x_mtl_Grey`,
`misc_fury_mtl_Decal_POM_A` — which is the same convention as the `.mtl` files inside
`Data.p4k`. That is consistent with them having been extracted from the game rather
than exported from the holoviewer.

**I registered all 23 Fleetyards models as `cig-holoviewer` earlier today. On this
evidence that label is NOT established either.** I am reporting it rather than
changing it again — I have already asserted a source I had not read once today and I
am not doing it twice. It needs Sleven, and it is the same question the image
provenance work order is about.
