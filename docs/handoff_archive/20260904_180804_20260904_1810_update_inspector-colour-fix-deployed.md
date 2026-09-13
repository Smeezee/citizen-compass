# Update — deployed: inspector colour fix and the note field

**2026-09-04 · Code**

`ORDER_inspector-colour-fix-and-note-field-rebuild-2026-09-04` (C1, 17:41),
which superseded the 17:38 vertex-colour order. One rebuild covered both; I had
not run the earlier one.

**Sweep first: 116 ok, 0 failed, 3 skipped**, payload `44e1748007f2dc09`. No
`-IgnoreSweep`.

## Verified from the served bytes, cache-busted

    /_inspect  200, 1,156,977 bytes, byte-identical to the payload

    vertexColors disabled     yes
    chip "wrong colours"      yes
    chip "two copies overlapping"  yes
    chip "not the right ship" yes
    source notice             yes
    takedown line             yes

Grew from 1,155,635 to 1,156,977 - the note box and three chips.

All three deployed-only controls pass.

**Sleven's existing marks are safe** - they live in his browser, not the page, so
the redeploy did not disturb the ships he has already walked.

## What I did NOT do, and why it is worth saying

The whole of this order was C1's work: the `dress()` fix, the note field, the
chips, all tested by them in a real browser before the order was written. My part
was build, sweep, deploy, verify. I checked the source had been still for five
minutes before building, because two orders today turned on exactly that timing -
one where a build beat an edit by ninety seconds, one where an edit beat my build
by two minutes.

## Standing findings, none of them mine, all reported by C1

- **The 85X model is broken as delivered.** 102 of 112 meshes referenced twice,
  every pair `<name>` / `<name>.001`. C1 declined to write a rule stripping
  `.001` nodes because that is name-derived inference. Correct call.
- **All 19 Fleetyards imports are structurally unlike the other 239** - named
  materials in CIG's own convention, matching the `.mtl` naming inside
  `Data.p4k`, which is consistent with extraction from the game rather than a
  holoviewer export. So the `cig-holoviewer` label applied this morning is not
  established for those 23.
- The 241 thumbnails remain unregistered pending the same provenance question.
- The glossary still marks 0 of its 31 terms.

**That is three provenance questions surfaced today and they share a shape:** a
source label applied by inference and later found to have no reading behind it.
The register is what decides which assets the takedown notice covers, so this is
not filing - it is the accuracy of a compliance claim. Sleven's call, and Part 2
of the image work order (render our own thumbnails from the 258 models) removes
the question for the images rather than arguing it.

## For Sleven

    https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html
