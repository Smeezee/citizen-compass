# FINDING — the `#ivo` mesh format is decoded far enough to build a real Cutlass Black, and not far enough for the fleet

C1 (Cowork), 2026-09-05

Sleven authorised pulling the real ship models out of his own Star Citizen
install. This is what came of it, including the part that does not work.

## The headline

`DRAK_Cutlass_Black.cga` / `.cgam` out of `Data.p4k`, decoded from the bytes up:

                        the site today        from the client
    meshes                    1                     -
    materials                 1 ("Default")        19, named by CIG
    vertices            (merged blob)          326,737
    triangles           (merged blob)          273,157

It renders as a recognisable Cutlass Black. The 19 materials are CIG's own -
`Paint_Secondary`, `Paint_Pri02_Darker`, `Metal_A`, `glass_ext`, `glow_alpha` -
and the 176 subsets carry the split the merged model threw away.

**It also confirms the colour finding of the same day.** Every paint material on
this hull is `Diffuse="1,1,1"`. Rendered with CIG's own values the ship comes out
white: the colour is in textures that are not in these files. Geometry and colour
are separate problems and only the first is now open.

## What was decoded, and what tested it

**Subset table** - 176 records of 48 bytes from +168 of chunk `0xB8757777`:
`u16 node, u16 materialId, u32 indexOffset, indexCount, vertexOffset, group,
vertexCount`. Walked by its own running sums; lands exactly on the 326,737
vertices and 819,474 indices the descriptor declares, every index count divides
by three. *The first reading had the fields reversed and the totals came out
swapped - that is how it was caught.*

**Index buffer** - 16-bit at +8,620. Ten scattered subsets each have all indices
inside their own 16-bit block. `group` is the block base, and exists because the
vertex count does not fit in 16 bits.

**Vertex streams** - four, chained by 12-byte headers `[0][hash][elementSize]`,
16 + 4 + 8 + 2 = 30 bytes per vertex, the figure the file states. Strides
confirmed independently by byte-repeat measurement (stride 16 scores 0.53 where
its neighbours score 0.04). *Two earlier searches failed outright and printed
"nothing found" rather than a plausible answer.*

**Positions** - the 16-byte stream, 3 x s16 scaled over the declared bounding
box. *Containment could NOT identify it: three candidates put 100% of points
inside the box, because any 16-bit stream does once scaled to it. What worked was
TRIANGLE SIZE - median edge 0.094 m on a 34-metre hull against 3.9 m and 5.2 m
for the runners-up. Noise measures the size of the ship.*

**Materials** - `materialId` indexes the `.mtl` named for the ship's own folder.
*The first build used `..._Exterior.mtl` and got names that did not fit their
parts. `DRAK_Cutlass_Black.mtl` has 64 sub-materials whose first nineteen are the
exterior set in order; under it the 22-subset material is `Paint_Secondary` and
the white wing-tip pieces are `glow_alpha`, the navigation lights. The names
describing what they are attached to is the check.*

## What does NOT work, and this is the important half

**The Vulture fails.** Same decoder, and its subset walk passes its own
arithmetic - 624 subsets, 1,257,859 vertices, 3,613,752 indices, all matching the
declared figures - but the model renders as a shapeless blob. The container, the
subset table and the stream chain generalise; **the index base does not.** The
Vulture has 26 group bases against the Cutlass's seven and `group + value` is not
the rule for it.

**The bound I first used was over-fitted to a picture.** Bounding indices to each
subset's own vertex range removed a few long thin triangles from the Cutlass
render; on the Vulture the same rule discards **51.5%** of the ship against 0.3%
for the block bound. The general rule is the block bound, and **the long
triangles on the Cutlass are left unexplained rather than tuned away.**

**Also unresolved:** the Vulture references material ids up to 172 while its
`.mtl` holds 64, so a hull can draw on more than one material file.

**Not decoded at all:** normals, texture coordinates, tangents, vertex colours -
three of the four streams. The output carries no normals; they are generated from
the geometry and the glTF `generator` string says so.

## Where this stands

One ship, done properly. Not a pipeline.

- **Proven:** the format is readable by us with no third-party tool, and the
  per-part model with CIG's material names exists on disk for the Cutlass Black.
- **Not proven:** that it generalises. One of the two ships tried came out wrong,
  and wrong in a way the arithmetic did not catch - every total agreed and the
  model was still rubbish. Worth remembering before anyone runs this over 256.
- **Not started:** normals, UVs, textures, and the merge back into the site.

**Nothing deployed, committed, or put in front of a visitor.**

    tools/ivo/ivo_mesh.py                      the decoder, reads only
    _work/paint/Cutlass_Black_from_client.glb   7.2 MB   good
    _work/paint/cutlass_from_client.png                  the render
    _work/paint/Vulture_from_client.glb        29.6 MB   WRONG - do not use

## The next real question

Whether the remaining three streams are worth decoding by hand, or whether the
Vulture failure says the sensible path is still an existing converter. This
proves the data is reachable and that we can read it; it does not prove that
hand-decoding the rest is the cheapest way to 256 ships.

---

# UPDATE, same day — the Vulture is fixed, and the decoder now works on six ships

## What was actually wrong

Not the index base, and not `group`. **The stream header is 8 bytes, not 12.**

The first decoder looked for `[0][hash][elementSize]` and hard-coded the offsets
it found on the Cutlass Black. That leading zero was never part of the header -
it was padding that happened to sit there on that one ship. On the Vulture the
preceding word is the tail of the index buffer, so the scan found no chain, the
build read the wrong region as positions, and out came a blob.

The real shape is `[u32 typeHash][u32 elementSize]`, the first one at the next
4-byte boundary after the index buffer, each following one after any padding.

**The Cutlass's own position stream sits at +1,647,584 and the Vulture's at
+7,257,640.** Nothing about the first ship's offsets was ever going to
generalise, and carrying them was the mistake underneath the visible one.

## The decoder no longer knows anything about a particular ship

Everything is read from the file: counts, both bounding boxes, the subset table,
the index buffer, the stream chain. And the position stream is now **chosen by
geometry rather than by its place in the chain** - every candidate is read
through the index buffer and the one with the smallest median triangle edge
wins, and it must come in under 0.5 m or the run refuses.

That last part matters, because it is the only gate here that the file cannot
satisfy by being internally consistent. The Vulture passed every declared total
while producing rubbish.

## Six hulls, measured

```
                      subsets   vertices   triangles   median edge   streams
Cutlass Black             176    326,737     273,157      0.084 m    16+4+8+2
Vulture                   624  1,257,859   1,204,583      0.029 m    16+4+8+2
Gladius                   457    334,609     339,426      0.053 m    16+4+8+2
Prospector                419    371,900     402,646      0.045 m    16+4+8+2
Arrow                     180    146,658     138,088      0.034 m    16+4+8+2
300i                      220    145,955     128,003      0.038 m    16+4+8+2
```

Every one: 30 bytes per vertex, positions on the 16-byte stream, at most one
triangle dropped. Four were rendered and are recognisably the right ship - the
Vulture with its arms out, the Prospector's rounded hull, the Gladius's swept
wings and twin tails.

**The Prospector is worth noting: it is the ship that measured worst for
see-through hull in the whole fleet.** From the client it comes out solid.

## What is still not right

**Materials are only partly named.** Every hull past the Cutlass draws on more
than one `.mtl` - the Gladius uses 104 materials against 33 named, the Vulture
173 against 64. The unnamed ones come out as `material_71` and take a default
grey. The decoder reports the count rather than guessing a file, and finding the
other `.mtl` files is not started.

**Two ships were not reached at all** - the Aurora MR and the Constellation
Andromeda, whose hull files are not named for their folder the way the rule
expects, and the Freelancer, whose entry failed extraction with "no local
header". Three of nine. Those are lookup problems, not decode problems, and they
are written down rather than worked around.

**Still not decoded:** normals, texture coordinates, tangents, vertex colours -
three of the four streams. And the colour is still in textures we do not have,
so these hulls are all grey.

## Where it stands now

Six ships in, six out, on a decoder that carries no ship-specific constants. That
is a different position from this morning's one-ship result, and it is enough to
say the format is read rather than that one file was cracked. It is **not** yet
enough to run over 256 hulls: a third of the ships tried could not even be
located by name, and no check yet exists that would catch a bad model without a
human looking at it.
