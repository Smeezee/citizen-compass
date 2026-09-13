# Update — order received: inspector colour fix + note field

**2026-09-04 · Code**

`ORDER_inspector-colour-fix-and-note-field-rebuild-2026-09-04` (C1, 17:41),
which supersedes `ORDER_inspector-vertex-colour-fix-rebuild-and-deploy` (17:38).
I had not run the earlier one, so this is a single rebuild covering both.

**Sleven is walking the 258 ships and found two things in the first twelve.**

1. The 600i Executive Edition rendered iridescent blue and magenta.
   `GLTFLoader` sets `material.vertexColors = true` on any primitive carrying
   `COLOR_0`; six of the 258 do and the 600i carries eight colour sets. C1 has
   fixed it in `dress()`. **The site itself was never affected** - `cc_viewer.js`
   replaces every material with its own shader and reads no vertex colours.
2. He had no way to tell C1 what he was seeing. A free-text note per ship, which
   auto-marks the ship as broken, persists per ship and appears in the report;
   plus three new chips.

**My part is the rebuild and deploy, nothing else.** Both changes are C1's, in
C1's files, already tested by them in a real browser.

His marks live in his browser rather than the page, so redeploying will not lose
the ships he has already walked.

**Checking the source has settled before building.** Two orders today turned on
exactly that - one where a build beat an edit by ninety seconds, one where an
edit beat my build by two minutes.

## Noted, not acted on

C1 reports the **85X model is broken as delivered** - 102 of its 112 meshes
referenced twice, every pair `<name>` and `<name>.001`, Blender's duplicate
convention. Two ships crossed in an X. They explicitly declined to write a rule
stripping `.001` nodes because that is name-derived inference.

And that **all 19 Fleetyards imports are structurally unlike the other 239**, with
CIG's own material naming, consistent with extraction from the game rather than a
holoviewer export - so the `cig-holoviewer` label C1 applied this morning is "not
established either". Reported by them, not changed. Not mine to touch either way.
