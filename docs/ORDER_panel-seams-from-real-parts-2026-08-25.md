# ORDER — Panel seams from the parts that are already there.

**C1, 2026-08-25. Built, rendered and measured before this was written.**

**The ships were never one welded lump.** Every hull in the library is already
built from thousands of physically separate pieces. Measured across all 234:

    pieces per ship, median          2,833   (range 243 to 32,261)
    ships that are a single piece         0   of 234
    largest single piece, median       3.0%   of the hull
    pieces holding 90% of the hull      838   median

**The gap between two pieces IS a panel line.** That is the thing G3 removed and
that RSI has and we do not — and it does not need detection, geometry repair or
guesswork. It is already in the file.

---

## S1 — Derive seams from connected components, not from an angle threshold

The current line pass asks "do these two triangles meet at more than 24 degrees",
which fires on the mesh's own triangulation and produces corduroy. **Instead:**

1. **Weld positions to a tolerance** of `boundingBoxDiagonal * 1e-5`. The
   exporter splits vertices for normals and UVs; without the weld every triangle
   looks like its own island. Verified: welding reduces the vertex count to a
   median of 97% of raw, so it is doing real work and not collapsing the mesh.
2. **Union-find over welded vertices**, joined by triangle edges, to label
   connected components.
3. **For each component above a triangle-count floor**, take the edges used by
   exactly ONE triangle within that component. That set is the physical rim of a
   real plate.

**Measured, at a floor of 400 to 1,500 triangles:**

| hull | pieces | drawn | seam lines | current 24-degree lines |
|---|---|---|---|---|
| Mercury Star Runner | 4,539 | 87 | **9,586** | 352,943 |
| Aegis Sabre | 5,534 | 294 | **17,499** | 361,533 |
| M2 Hercules | 1,802 | 122 | **12,544** | 278,488 |
| Origin 600i Touring | 2,310 | 59 | **8,199** | 169,283 |
| Origin Razor | 545 | 165 | **8,231** | 75,346 |

**Thirty-seven times fewer lines on the Mercury, and they are real plate edges.**

## S2 — The floor is a control, not a constant

The triangle-count floor decides how many pieces get an outline. **It must be
derived per hull, not pinned**, because piece counts run 243 to 32,261 — a
hull-independent number will draw 87 seams on one ship and 4,000 on another.

**Derive it from the target line budget**, not from a triangle count someone
liked. RSI draws roughly forty lines on a Mercury; we do not have to match that,
but the number has to be a decision rather than an accident.

    CONTROL, load-bearing: report seam-line count for all 234 hulls at the
    chosen rule. State the median, the range, and name every hull above 25,000.
    A rule that is fine on the Mercury and draws 40,000 on the Hull E has not
    been derived, it has been guessed on one ship - which is the exact mistake
    the G1 colour errata was.
    CONTROL: report the per-hull cost of computing the seams. If it cannot be
    done at build time it must be precomputed and shipped; say which.

## S3 — Seams are dark and depth-tested, never additive

They are creases in a lit surface, not glowing wires.

    dark colour, normal blending, depthWrite false, depthTest ON
    polygonOffset on the LINES, toward the camera, factor and units -1

**DO NOT put polygonOffset on the hull material.** It displaces the whole hull
backwards, the slope-scaled term explodes on steeply-angled faces, and the
background punches through the nose in speckles. I did exactly this in the first
demo pass; `_verify_hull_solid.mjs` already asserts against it.

## S4 — This is opt-in on top of `solid`, not a replacement for it

G3's default stands: the page opens on a clean lit hull. **Seams are the next
layer up**, and they must not reintroduce what G1-G5 removed.

    CONTROL, load-bearing: re-run the pure-white and mean-luminance measurement
    with seams on. Pure white must stay at the post-knee figures - ice under
    2.4%, every other colour at 0.000%. Mean luminance must not drop more than
    the knee's own 1.0-3.9%.
    NEGATIVE CONTROL: with seams OFF the render must be byte-identical to the
    current committed output. If it is not, this order has changed the default
    and it was not supposed to.

## What this does NOT do

**It does not give the pieces names.** Nothing in the file says which of the
4,539 is the canopy. Seams need no names — they are the rim of whatever the
piece is — but glass, hardpoints and part labels all still do.

`FINDING_the-models-have-one-material-2026-08-23.md` stands: one mesh, one
material called "Default", no textures, no glass, on all 234.
