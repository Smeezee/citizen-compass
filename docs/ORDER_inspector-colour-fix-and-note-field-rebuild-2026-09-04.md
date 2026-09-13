# ORDER — inspector: colour fix + a free-text note. Rebuild and deploy testing.

From: C1 (Cowork), 2026-09-04
For: Code

**This supersedes `ORDER_inspector-vertex-colour-fix-rebuild-and-deploy-2026-09-04`
if you have not run it yet.** Same rebuild, one more change folded in. If you already
ran it, this is a second pass — the note field is new.

Sleven is walking the 258 ships and found two things in the first twelve.

## 1. The 600i Executive Edition rendered iridescent blue and magenta — MY BUG
`GLTFLoader` sets `material.vertexColors = true` on any primitive carrying `COLOR_0`.
Six of the 258 do; the 600i Executive Edition carries **eight** colour sets. The
inspector reused the file's own material and only overrode metalness, roughness,
colour and side, so the loader went on tinting the hull with whatever a third party
baked in.

**The site was never affected.** `cc_viewer.js` replaces every material with its own
shader and cannot read vertex colours — `grep -c "vColor\|vertexColors"` returns 0.

Fixed: `m.vertexColors = false` in `dress()`. Verified in a real browser against the
real model — uniform grey hull, 0 page errors.

## 2. He had no way to tell me what he was seeing
The chips only cover what I thought of in advance, and he hit two things in twelve
ships that none of them named. That is a defect in a tool whose entire job is letting
him record what he finds.

Added to `testing/_src/_inspect.src.html`:
- **A free-text note box per ship.** Typing in it marks the ship broken by itself —
  if he bothered to type, it is a finding. Saved per ship, restored on return,
  included in the Report output under the ship's name.
- `keydown` is stopped inside the box so typing cannot steal the arrow keys or the
  spacebar shortcut.
- Three new chips: **wrong colours**, **two copies overlapping**, **not the right ship**.

Tested end to end: note persists per ship, comes back on return, auto-marks, arrow
keys still navigate, report renders it. 0 page errors. Previous source preserved at
`_to_delete/_inspect.src.html.pre_vertexcolour_*`.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

His marks live in his browser, not the page, so a redeploy will not lose the ships he
has already walked.

## SEPARATE FINDING — the 85X model is broken as delivered. Reported, not fixed.
It renders as two ships crossed in an X. That is not our viewer:

    scenes 2   nodes 939   meshes 112   materials 113
    246 node references to 112 meshes - 102 meshes are referenced TWICE
    every pair is `<name>` and `<name>.001`, Blender's duplicate-name convention
      0588c4_body_internals / 0588c4_body_internals.001
      0588c4_glass_int      / 0588c4_glass_int.001

Whoever prepared this file duplicated the whole ship in Blender and left both copies
in the scene, one rotated. **I am not writing a rule that strips `.001` nodes** — that
is name-derived inference and rule 2 forbids it. This wants a replacement model or a
real import pass, and it is on the same pile as the 19 Fleetyards files generally.

Related, from the same scan: **all 19 Fleetyards imports are structurally unlike the
other 239.** Each of the 239 is one mesh with one material named `Default`. The 19 are
2 to 406 meshes with named materials. The 85X and the Fury carry CIG's own naming —
`orig_85x_mtl_Grey`, `misc_fury_mtl_Decal_POM_A` — the same convention as the `.mtl`
files inside `Data.p4k`, which is consistent with extraction from the game rather
than a holoviewer export. I registered all 23 as `cig-holoviewer` this morning; **on
this evidence that label is not established either.** Reported, not changed — I have
already asserted an unread source once today.
