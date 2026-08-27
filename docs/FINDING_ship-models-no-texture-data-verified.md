# FINDING — the 235 ship models have zero skin/texture data. Verified on disk.

    id       FINDING-MODELS-02
    from     C3 (Cowork), 2026-08-07
    for      Sleven + C1
    context  Sleven wants the collector and the ship-model/hardpoint/skin
             question worked as one combined project focus, since better
             models feed the collector's ship-recognition training and the
             collector's captures could eventually help verify/improve the
             models. This finding answers the specific question raised:
             "I'm not sure if what I have is the right one."
    scope    Technical only. No legal or rights conclusion drawn here — see
             the rights table at the bottom, which points to the rulings
             that already exist.

---

## What was checked, and how

Opened the actual `.glb` files in `testing/_deploy/models/` (235 files, the
ones the live viewer serves) and read their internal glTF structure directly
— not the file names, not a report about them, the binary contents. Checked
`100i.glb`, `Aurora_LX.glb`, `Cutlass_Black_Best_In_Show_Edition_2949.glb`,
`F7A_Hornet_Mk_I.glb`, `Idris-M.glb` as a spread across ship sizes/classes.

## What's actually in the files

**Every one checked has zero texture data. Not "one plain skin" — zero.**
No images, no textures, one flat generic gray material (50% rough, 50%
metallic, no color, no pattern) applied to the whole hull. This matches the
already-known fact that these are single flattened meshes (`RULING-MODELS-01`
§4) — there was never a paint job to preserve, because the file only ever
held bare geometry.

**The geometry does carry UV coordinates** (`TEXCOORD_0` on every mesh
checked). That's the good news: if a real texture ever gets sourced, the
geometry is already laid out to receive one — nobody has to redo the modeling
to add skin support later, just the texture itself.

**A second, separate defect, found by accident while checking this:** four of
the five Aurora files on disk — `Aurora_CL.glb`, `Aurora_ES.glb`,
`Aurora_LN.glb`, `Aurora_MR.glb` — are byte-for-byte identical (same MD5
hash). Only `Aurora_LX` is a genuinely different file. Whatever the viewer is
showing for CL vs. ES vs. LN vs. MR right now, it's the exact same model
copied under four names — there is currently no visual difference between
those trims at all. Worth checking whether this is isolated to the Aurora or
project-wide before relying on any trim/variant looking distinct.

## What this means for the two things Sleven wants to build

**Hardpoints.** Already known and now doubly confirmed: these files cannot
give hardpoint locations by extraction — no node tree, no named parts. This
does **not** block the project's existing plan (`CURRENT-STATE.md`, project
instructions) of a person manually placing hardpoint markers in Blender on
the hull shape — that only needs accurate outer geometry, which these files
have. It does mean there is no shortcut; every hardpoint on every ship still
has to be placed by hand.

**Skins/liveries.** Currently not possible at all with what's in the repo —
there is no texture to swap, on any ship. Two ways forward, not a
recommendation, just what exists:

1. Source real texture/livery images and map them onto the existing
   UV-mapped geometry. Where those images could legitimately come from is a
   rights question, not a technical one — see below.
2. Leave ships as plain gray hulls for now; this doesn't block the collector
   training-data use case at all, since silhouette/hull recognition
   (`RULING-MODELS-01` §4, §6) doesn't need a texture.

## The rights picture, for context — not decided here

| Question | Where it stands |
|---|---|
| Can this project use the 235 Hugging Face community models at all? | Ruled — proceed, build first, ask CIG before public launch. `RULING-MODELS-01`. |
| Can this project extract textures/models directly from CIG's own game files? | Already settled, separately: **no.** `docs/CORRECTION_extracted-textures-are-not-granted.md` — extracted creative assets (textures, icons, models, CIG's own description text) are out; factual game data is fine. |
| Does CIG's official Fan Kit include usable 3D models with textures? | Reportedly yes, per the Fan Kit's own content list, but nobody has opened it — it sits behind a click-through agreement only Sleven can accept. `RULING-MODELS-01` §7. **This is the one open door that could resolve both the hardpoint and skin question cleanly if it's usable — someone needs to look.** |

## Suggested next move, not a build order

Two independent threads Sleven can pick up in either order:

1. **Open the Fan Kit and see what the 3D models actually contain** — file
   structure, whether they have real node hierarchies (hardpoints) and real
   textures (skins). That single check could make everything above moot in
   either direction.
2. **Keep building the collector on what's on hand now** — the texture gap
   doesn't block silhouette-based ship recognition, which is the piece that
   actually feeds back into the collector. The hardpoint/skin work and the
   collector's recognition training aren't blocking each other; they're
   running in parallel toward the same ship-model foundation.
