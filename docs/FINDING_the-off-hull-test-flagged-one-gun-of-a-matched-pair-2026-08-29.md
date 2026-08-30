# FINDING — the off-hull test flagged one gun of a symmetric pair and missed its twin sitting the same distance away. Measured against the mesh instead of the screen, three of the five flagged dots are fine and two unflagged ones are not.

    from    C1 (Cowork), 2026-08-29 14:10 local
    method  Draco-decoded hull geometry, distance from each marker to the
            nearest real vertex, in the ship's own units. No camera.
    scope   corrects docs/FINDING_four-hulls-draw-a-dot-in-empty-space-2026-08-29

---

## 1. THE INSTRUMENT WAS A PHOTOGRAPH, AND A PHOTOGRAPH CANNOT SEE A NOTCH

`offhull.py` decides a dot is adrift when no hull pixel is within 14px of it in
a clean silhouette. **A concave hull shows the background through its own gaps.**
A mount sitting in a recess, a wing root, or between two arms is photographed
against empty space and reported as floating, and there is no camera angle that
fixes it — the gap is real geometry.

I described those ten dots as *"individual mounts, not broken ships"* and said
**"no population-level check can see a single mount in the wrong place."** The
second half was right. The first half named the wrong mounts.

## 2. WHAT THE MESH SAYS, FULL RESOLUTION, EVERY VERTEX

    TMBL_Storm_AA      4 markers   median 0.522   p90 0.564
      port 4    FLAGGED    0.560 units    rank 2 of 4
      port 2    not flagged 0.566 units   rank 1 of 4  - FARTHER, and passed

**The Storm AA dot is the second-closest of four.** It is indistinguishable from
every other marker on that vehicle. **A clean false positive.**

    DRAK_Corsair      38 markers   median 2.561   p75 6.145   p90 7.231
      port 80   FLAGGED    6.291    rank  7 of 38   "Weapon wing top"
      port 93   FLAGGED    6.004    rank 12 of 38   "Wing right missile mount c"
      port 94   FLAGGED    8.138    rank  2 of 38   "Wing right missile mount d"
      port 67   not flagged 7.518   rank  4 of 38   "Cheek weapon right"

**Port 93 is mid-table.** Port 67 is worse than two of the three flagged and was
never reported. **The Corsair's real problem is that its median marker sits 2.56
units — 4.7% of hull length — from the nearest surface.** The screen test
sampled that spread and returned an arbitrary three.

    VNCL_Glaive       16 markers   median 0.369   p90 3.628
      port 43   FLAGGED    5.488    rank 1 of 16   "Gun nose left"
      port 44   not flagged 5.481   rank 2 of 16   "Gun nose right"

## 3. THIS IS THE ONE THAT SHOULD NOT HAVE SURVIVED REVIEW

**`Gun nose left` and `Gun nose right` are a mirrored pair.** They are 5.488 and
5.481 units adrift — a difference of seven thousandths of a unit on a 30-unit
hull. **The test flagged one and passed the other.**

Nothing about the data distinguishes them. The only thing that differed was
which side of the ship happened to face the camera. **A test whose verdict
depends on the viewing angle, applied to a symmetric pair, will disagree with
itself — and this one did, in a repository whose whole mirror machinery exists
because left and right must match.**

## 4. WHAT IS ACTUALLY WRONG, THEN

**Sixty markers on twenty hulls, not ten on four** — see 4b. The Glaive's nose
pair is real and so is a great deal the photograph never saw.

**One hull is broadly imprecise rather than individually broken:** the Corsair,
whose whole marker set sits farther out than any other hull measured. That is a
hull-level question — likely its articulated wings sitting in a different pose
in the Fan Kit export than in CIG's transforms — and it should be asked about
all 38 markers, not about three of them.

**Everything else flagged was fine.**

## 4b. THEN IT WAS RUN ON THE WHOLE FLEET, AND THE OLD LIST LOOKS SMALL

    5,800 markers - 256 hulls - 60 flagged on 20 hulls

**The photograph found 10 dots on 4 hulls. Three of its five worst were fine,
and it had never mentioned sixteen of the twenty hulls the mesh reports.**

    GAMA_Tyilui              15 flagged   worst 28.0% of hull length
    VNCL_Glaive               3 flagged   worst 17.8%
    ESPR_Talon_Shrike         6 flagged   worst  9.0%
    CRUS_Starlifter_A2        2 flagged   worst  7.6%
    ANVL_Gladiator            4 flagged   worst  6.2%
    DRAK_Cutlass_Black x4     2 each      worst  4.3%
    RSI_Constellation_Phoenix 3 flagged   worst  5.1%
    ...20 hulls in total

**`GAMA_Tyilui` has fifteen markers adrift and one of them sits 28% of the
hull's own length from any surface of it.** It was photographed like every other
ship and reported clean, because its mounts are adrift into places the camera
sees hull behind. Nothing in this repository has ever mentioned it.

**AND THE CORSAIR IS NOT ON THE LIST AT ALL.** Its 38 markers are uniformly
loose — median 2.56 units — but not one is an outlier against its own hull.
The three the photograph flagged are ordinary members of a wide distribution.
Its wide spread is still a real question, and it is a question about the whole
hull rather than about three mounts.

## 5. THE CONTROL

`checks/_verify_marker_mesh_distance.py` — distance to the nearest real vertex,
per hull, flagging a marker only when it is an outlier **against its own hull's
distribution**. **RULE16: INDEPENDENT** — its truth comes from the decoded GLB,
which is not the file the markers are written to.

It needs `draco3d` to read the compressed meshes. Where the decoder is absent it
exits **2, NOT PERFORMED**, naming what it could not reach — which is only a
distinguishable answer once Q29 lands, and is filed that way regardless.

**`offhull.py` is not deleted.** It answers a real question — *is a dot visible
against the hull from the default view* — and that is worth knowing. It is no
longer evidence that a mount is misplaced.

## 6. THE LESSON

**I built a measuring instrument, got a number, and reported the number as the
thing.** The photograph measured visibility. I wrote it down as position. They
agree on a convex hull and part company on every ship with a gap in it — which
is most of them.

The tell was in the output the whole time: **a symmetric pair split across the
verdict.** I read the ten names, recognised none of them as pairs, and moved on.

— C1
