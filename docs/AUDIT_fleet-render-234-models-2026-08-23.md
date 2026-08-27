# AUDIT — 234 models, ten categories. The render holds; the data does not.

**Run by C1, 2026-08-23.** Every `model_scaled.glb` in `sc-ships` loaded once into
a headless Chromium (WebGL2, 24-bit depth) and measured ten ways. **234 measured,
0 failed to load, 0 hand-entered numbers, no model modified.**

Full report with per-model table: `fleet-audit.html` (delivered to Sleven).

---

## The headline

**The proposed render holds on all 234.** Tuned against ten hulls, then run
against the whole library without adjustment:

- **Zero clipping.** Not one hull puts a single pixel above 90% luminance, at
  any of three angles. The white-out is gone fleet-wide, not sample-wide.
- **near:far ratio median 12.9, worst 16.7.** Today every hull runs 30,000:1.
- **No hull under 5,000 rendered pixels** at any angle. Framing works on
  everything from the San'tok.yai at 0.23 units to the Javelin at 469.
- **Mean luminance median 124**, range 78-158.

## The ten categories, and what each found

**1. Structure.** 234 of 234 are ONE mesh, ONE primitive, ONE material named
"Default", alphaMode OPAQUE. Zero textures. Zero transparent materials. Zero
glTF extensions. **This settles the glass question fleet-wide** — there is no
canopy to make transparent on any ship in the library.

**2. Watertightness.** Front-face vs double-sided silhouette, three angles.
Median gap 0.035%, nine models over 1%, none over 5%. Worst: X1 / X1 Force
3.15%, Ranger RC 3.08%. **No reported see-through was ever a hole in a model.**

**3./4. Normals.** Present on all 234, zero zero-length. But agreement between
vertex normal and own face winding: **median 0.986, floor 0.541.** 54 models
below 0.95, **27 below 0.90.** Worst: Cutter Rambler 0.541, F8C Lightning and
Executive Edition 0.544, Zeus Mk II MR 0.674. On the Cutter Rambler **46% of
triangles are lit from the wrong side.** Fixable offline. Most common real
defect in the library.

**5. Scale.** Largest dimension runs 0.23 to 469 units — a factor of 2,000.
**Four models are under one unit** and cannot be metres: San'tok.yai 0.23,
Genesis 0.43, Starlancer TAC 0.84, Crucible 0.89. Nothing over 1,000, so nothing
is in centimetres. Any world-unit measurement on those four is wrong.

**6. Orientation.** Five taller than long or wide: ATLS, ATLS GEO, Khartu-Al,
Railen, Reliant Kore. **Two are false positives and are reported as such** — the
ATLS pair are walking loaders and upright is correct. A flag is not a defect
until someone looks.

**7. Stray geometry.** Max vertex radius vs 95th percentile: median 1.16, only
one model over 2.0 (Khartu-Al 2.10x, its own wings). **No runaway geometry
anywhere.**

**8. Occlusion and framing.** Covered in the headline.

**9. Luminance.** Zero clipping. Nine models outside 95-150 flagged for a look.

**10. Degenerate geometry.** **2,650,600 zero-area triangles** across the fleet,
in 233 of 234 models. Median 0.22%, but Ranger RC 23.8%, Galaxy 22.0%, X1 /
X1 Force 19.6%, SRV 18.3%. Zero non-finite positions.

## 72 of 234 carry at least one flag

normals 54 · degenerate 11 · silhouette 9 · luminance 9 · orientation 5 · scale 4.
**None carry three or more. None break the render.** All twenty worst offenders
were rendered and every one reads as a solid, correctly-framed object.

## A story I checked and dropped

Models with bad normals render darker on average — mean luminance 109 below 0.90
agreement against 124 above 0.98. **But fleet-wide correlation is r = 0.13.**
That is weak, so bad normals do NOT explain the brightness spread and no claim
is made that they do. Recorded because the subgroup difference is real and
someone will otherwise find it and over-read it.

## What this audit cannot do

- **It cannot tell a stylistic choice from a defect.** The ATLS flag proves it.
- It measures one export of one loadout of each hull.
- **It says nothing about whether these are the right models to be using.**
  That is `FINDING_the-models-have-one-material-2026-08-23.md`, and it is a
  separate question with a separate answer.
