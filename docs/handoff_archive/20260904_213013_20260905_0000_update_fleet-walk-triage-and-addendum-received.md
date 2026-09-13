# Update — fleet-walk triage received, plus the 85X addendum

**Code**

    docs/ORDER_fleet-walk-triage-256-of-256-2026-09-04.md      (C1, 19:25)
    docs/ORDER_addendum-do-not-dedup-the-85x-by-name-2026-09-05 (C1)

Sleven has walked all 256. What I am authorised to do:

**From the triage order - sections 1 and 2 only, section 3 is report-only:**

1. Clear 20 stale marks - the 600i (vertex colours), the two Carrack C8X entries
   (removed), and seventeen "facing away" marks that all predate the
   `Math.PI + 0.9` deploy. Move them to a `resolved` state with his note text
   intact, so the count reads honestly. **Do not silently drop the notes.**
2. Re-render ATLS, ATLS GEO and Reliant Kore at the current 1.45 fit radius and
   report whether the whole hull is in frame. **Do not tune the radius** - that
   is global across 256 and C1's call.

**From the addendum:**

1. **Fury only.** Remove one node of each `<name>` / `<name>.001` pair whose
   accumulated world translations match to within 1e-6. **Exactly 301 pairs must
   qualify. If my count is not 301 I stop and report the difference rather than
   proceeding.** Displaced pairs are real parts and stay.
2. **85X - render, do not edit.** Three images on one camera: everything, then
   world X < 4, then world X >= 4.

**Section 3a is answered and closed by C1's own measurement, and the obvious fix
is a trap I am glad not to have applied.** Deleting every `.001` node on the 85X
would take pieces out of BOTH ships - the un-suffixed nodes already span the full
X range of both clusters. The meaningful split is spatial, not nominal, and even
that is unproven: 110 nodes against 136, 56 distinct offset vectors, so neither
cluster is a clean copy of the other. C1's line is the right one - a picture
decides this, not more arithmetic.

Starting with the Fury pair count, because it has a hard stop condition and
there is no point doing anything else if the number disagrees.
