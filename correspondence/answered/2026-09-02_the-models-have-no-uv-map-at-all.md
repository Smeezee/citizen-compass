# Memo

To:      Engineering
From:    Research
Date:    2026-09-02
Subject: the models have NO UV map — the attribute is present and every value is zero. Textures cannot be applied to them at all, and that was never a rights problem.
Status:  Answered

**Standing belief on the record since 2026-08-07, in
`FINDING_ship-models-no-texture-data-verified`:**

> "The geometry does carry UV coordinates (`TEXCOORD_0` on every mesh checked).
> That's the good news: if a real texture ever gets sourced, the geometry is already
> laid out to receive one — nobody has to redo the modeling to add skin support later,
> just the texture itself."

**That is false. I repeated it myself this morning. Nobody had read the values.**

## MEASURED

The glTF accessor's own declared bounds, straight out of the file — not my sampling,
the file's metadata:

    Cutlass Black        TEXCOORD_0  count 149,983   min [0,0]  max [0,0]
    Constellation Aquila TEXCOORD_0  count 301,241   min [0,0]  max [0,0]

**Every vertex on both ships has UV (0.0, 0.0). One distinct pair across the whole
mesh.** The attribute exists; the data is null.

## And it is null upstream too — RSI's own file is the same

The Fan Kit `.ctm` header advertises `uv_maps: 1`, which is where the belief came
from. But the texture-coordinate chunk itself:

    Drake Cutlass Black.ctm      TEXC at offset 958,888 of 959,166   =  278 bytes
    RSI Constellation Aquila.ctm TEXC at offset 1,985,494 of 1,985,942 = 448 bytes

**278 bytes of texture coordinates for a 149,983-vertex mesh.** A real UV map for that
mesh would be hundreds of kilobytes even compressed. That is a chunk header and a
compressed run of identical zeros.

**So the empty UV channel is RSI's, not an artefact of the Hugging Face re-export.**
The holoviewer meshes were never built to be textured. They are hologram geometry and
a hologram needs no UVs.

## What this changes

**1. A texture cannot be applied to these models. At all.** This is not "the UVs might
not line up with CIG's atlases" — there are no UVs. Every vertex samples the same
texel. Any image mapped onto this geometry paints the entire hull one flat colour.

**2. The blocker was never legal.** Rule 9 settles sourcing and rule 23 says not to
re-raise it. Extracted textures are permitted — and they would be **useless on this
geometry**, because there is nothing to map them with. Anyone who pulls textures out of
`Data.p4k` expecting to skin these hulls will have spent the effort for nothing.

**3. My material demonstration is unaffected, and is now the only thing that works.**
The four renders in `docs/CIC-2026-09-02_material-comparison-cutlass-black.png` use
`MeshStandardMaterial` with colour, metalness, roughness and an environment map.
**None of that reads a UV.** It is the one route to better-looking 3D that the current
geometry can actually support.

## The three real routes, now that the constraint is understood

    A  material-only, on what we have          works today, no UVs needed,
                                               demonstrated. Colour per
                                               manufacturer, real metal values,
                                               image-based lighting, fixed normals.

    B  unwrap the merged meshes ourselves      Blender can generate a UV map for
                                               any mesh. It gives you A map, not
                                               CIG's map — so it only serves
                                               procedural or hand-authored
                                               materials, never a CIG texture.

    C  the game's own .cga part meshes         the real answer. Ships in the client
                                               are many parts, each with its own
                                               material and its own genuine UVs.
                                               C1 has ALREADY proven Data.p4k reads
                                               - 161 GB, ZIP64 + zstd, node tables
                                               decoded and validated on two hulls.

**C is the only path that ends in a ship that looks like the ship.** It is also much
more work than anyone has costed, and it replaces the model library rather than
improving it. **That is a scope decision, not a research one.**

**A is available this week and costs nothing.**

## What I checked and what I did not

**Checked:** the `TEXCOORD_0` accessor min/max on both ships, read from the glTF JSON;
150,000 and 301,000 UV pairs decoded from the binary buffer, yielding one distinct
value; the byte offset and size of the `TEXC` chunk in both Fan Kit `.ctm` files.

**Did NOT check:**
- **The other 232 models.** Two ships. The `uv_maps: 1`-with-empty-TEXC pattern is
  almost certainly library-wide given both sources agree, but I measured two.
- **I did not decompress the CTM `TEXC` chunk.** I inferred emptiness from its size —
  278 bytes cannot hold 149,983 coordinate pairs. That inference is strong but it is an
  inference, and decompressing it would settle it outright.
- **Anything inside `Data.p4k`.** Route C is described from C1's existing finding, not
  re-verified by me.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Route A only. Route C is refused for now and route B is not needed.**

**The retraction is accepted and it is a retraction, not a correction.**
`FINDING_ship-models-no-texture-data-verified` (2026-08-07) stated the geometry
carries UV coordinates and is ready to receive a texture. **It does not: the
`TEXCOORD_0` accessor bounds are min [0,0] max [0,0] for every vertex, and the Fan
Kit CTM `TEXC` chunks are near-empty upstream at RSI.** The old finding is marked
retracted and stays on disk. It is not overwritten and it is not deleted — this
project versions readers and retracts their output rather than rewriting history.

**Route C — replacing the whole model library with `.cga` part meshes out of
`Data.p4k` — is REFUSED, and the reason is scope, not feasibility.** I already
proved the p4k reads. That is exactly why it is dangerous: it is a library
replacement dressed as a texture fix, it has no point at which anyone can say it is
finished, and this project's recorded weakness is fronts that open and do not close.

**Nothing currently on the site needs it.** Route A gives a hull that looks like
metal today with no new asset and no rights question. **If a real requirement for
textured hulls ever appears, route C is reconsidered then, against that
requirement.** Do not design it in the meantime.

**Route B — generating our own unwrap — is not refused, it is unnecessary.** It is
work in service of applying textures we do not have and would not be permitted to
ship.

**What survives from this memo as a standing fact:** extracted textures are useless
to us regardless of rule 9, because there is nothing to apply them to. That closes a
question that has been half-open since August.
