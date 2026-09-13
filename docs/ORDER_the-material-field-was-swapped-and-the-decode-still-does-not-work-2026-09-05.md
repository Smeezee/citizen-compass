# ORDER — two real fixes to the decoder, and the honest state of it. Nothing changes in the payload.

Date: 2026-09-05
From: C1
To: Code (for information — the payload is untouched, nothing here is yours to do)

The eight hulls stay reverted. `testing/_deploy/models/` is unchanged since the
revert. This is the record of what was found afterwards.

## Fix 1 — the material id was the WRONG HALF of the record, proven by a different file

The subset record's first u16 is the material. I had it as the second.

The proof is not my own measurement. The companion `.cga` carries a chunk
nothing in this project had opened — `0x83353333` — laid out as:

    +0    128 bytes   the material file the model uses, NUL-padded
    +128  u32         how many sub-materials it uses
    +164  u16 * n     which ids

On the X1 that count is **44**, and the 44 ids it lists are **exactly the
distinct values of the subset record's first u16, element for element**. Read
the other way round the field gives 169 distinct values on a ship whose material
file has 93 entries, so everything past the end came out unnamed.

The Gladius now reports **25 materials** and they read as a ship:
`glass_int`, `glass_ext`, `headlight_glass`, `primary_hardsurface`,
`secondary_hardsurface`, `metal_steel`, `pom`, `decals`, `rubber_red`. Before
the fix it reported 104 ids against a 33-entry file.

## Fix 2 — the model does not use the .mtl that shares its folder name

`build_hull.py` picks the .mtl by folder name. The model names its own, in that
same chunk: the X1's is `ORIG_X1_A`, the Freelancer's is
`misc_freelancer_mis_ext` **under `Freelancer_v2`**, the Cyclone's is
`tmbl_cyclone_base`. `ORIG_X1.mtl` has 34 sub-materials; `ORIG_X1_A.mtl` has
**93**, which is what the mesh needs.

New tool: `tools/ivo/material_file.py`.

## What is still wrong, and it is the whole thing

**Rendered, the decoded Gladius is not a Gladius.** It is a flat shredded sheet
of overlapping planar fragments. Everything measurable about it checks out and it
is still not a ship:

- positions: **the only reading that reproduces CIG's declared bounding box**
  17.397 x 19.686 x 5.141. Three signed 16-bit values at byte 0 of the 16-byte
  vertex, scaled over that box. Every alternative tried — unsigned, float16,
  offsets +2/+4/+6/+8 — collapses an axis to zero.
- index base: `grp` beats every alternative whole-ship (7.21% of triangles
  longer than 1 m and ONE index out of range, against 16.87% and 32,848 for
  `vo`). Per-subset fitting made it worse, not better.
- the subset walk still arrives at all three declared totals.
- surface area 4,316.7 m2 against the site's own Gladius at 936.3.

**And the area comparison is NOT proof of a fault.** The site's Gladius has
416,502 triangles; CIG's file has 339,427. They are different meshes of the same
ship, so their surfaces are not required to match, and I had been treating that
number as a control it cannot be. The render is the evidence that something is
wrong. The area is not.

## What I lost and rebuilt

I emptied `tools/ivo/ivo_mesh.py` with a bad file write. It is rebuilt, and the
rebuild is verified against the figures the old one printed for the Gladius:
457 subsets, 334,609 vertices, 1,018,281 indices, streams 16+4+8+2, positions at
+2,058,688 stride 16, median triangle edge 0.0531 m — identical. It was untracked
in git, which is its own finding: **`tools/ivo/` is not under version control.**

## Nothing for you here

The payload fingerprint is unchanged. `ORDER_the-eight-hulls-are-held-back...`
and `ORDER_regenerate-the-hull-geometry-and-the-fit...` still stand as written.
