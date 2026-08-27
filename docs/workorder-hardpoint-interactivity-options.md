# WORK ORDER — ten ways to get real hardpoint interactivity out of the 235 ship models on hand

    id       WO-HARDPOINT-01
    from     C3 (Cowork), 2026-08-07
    for      C1 -> Code
    context  Sleven wants the ship-model/hardpoint section of the ship pages
             cleaned up for the next push to live. Brainstormed against the
             already-verified technical constraints of the actual model files
             (see claude/FINDING_ship-models-no-texture-data-verified.md and
             claude/RULING_ship-models-provenance-and-proceed.md): single
             flattened mesh per ship, no node hierarchy, no textures, but
             UV-mapped geometry and an accurate hull shape.
    status   Sleven approved moving forward. Prioritized options below.

---

## What's already true and doesn't need re-deriving

- Hardpoint locations were never going to come from the file structure — the
  standing plan was always a person manually placing markers in Blender
  against the hull shape. That still works fine on these models; nothing
  about the flattened-mesh finding blocks it.
- `ships.json Loadout[]` already names every fitted component (weapon size,
  mount type, etc.) on all 316 ships — usable today, no new research needed.
- The Fan Kit (item 8 in `CURRENT-STATE.md`'s open list) might make manual
  placement moot if its models have real hierarchies, but nobody's opened it
  yet — treat that as a parallel track, not a blocker for the options below.

## Ten options, ranked by what gets something real live fastest

1. **Finish the plan already on the books.** Hand-place hardpoint markers in
   Blender against the existing hull, export coordinates, raycast against the
   real mesh in Three.js. Highest fidelity, most manual labor.
2. **Markers as separate scene objects, not baked into the `.glb`.** Place
   small invisible proxy objects (spheres/boxes) in the Three.js scene,
   positioned by eye against the model. Click detection hits the proxies, not
   the mesh — simpler code, model files never need re-editing.
3. **List-driven instead of click-driven.** A hardpoint list next to the
   model, built entirely from `ships.json Loadout[]` (size, mount, weapon
   class), where hovering an item spins the camera toward roughly that area
   of the hull. Zero new spatial data needed.
4. **Ship the popular ships first.** Rank ship pages by traffic, hand-place
   markers on the top 10-20 for this push, leave the rest as plain rotate/
   zoom until they're done. **Recommended as the actual next-push scope.**
5. **2D callout diagram as a lighter alternative to full 3D raycasting.**
   Render the model from one or two fixed angles, overlay numbered clickable
   dots like a manual illustration. Less code, works even on ships without
   3D markers yet.
6. **Decouple "looks done" from "is done."** Ship the model viewer (already
   solid) now; put hardpoints in a clearly-labeled "coming online" panel that
   fills in ship by ship. **Recommended alongside #4** so the page never
   reads as broken or half-built during rollout.
7. **Flag markers unverified, same pattern as the rest of the site's data.**
   Ship rough hand-placed markers immediately under the existing
   `last_verified_patch` / unverified-data convention rather than blocking on
   perfect placement. **Recommended — matches standing site convention,**
   no new pattern to invent.
8. **Open the Fan Kit before investing heavily in manual placement.** If its
   models have real node hierarchies, most of the hand-placement work in
   options 1/2/4 becomes unnecessary. Sleven is pursuing this in parallel —
   see the Fan Kit research note filed alongside this order. Not a blocker,
   but worth checking before sinking 316 ships' worth of manual labor in.
9. **Static reference image as a stopgap for ships with nothing yet.** CIG's
   own ship-stat screenshots (covered under the fan-site screenshot
   exemption) often already show hardpoint counts/sizes — use as a fallback
   next to the 3D viewer on ships without spatial markers.
10. **Let it grow with the collector, long-term.** If the collector ever
    reads more of the screen, in-play verification of marker placement is a
    natural extension — not near-term, just noting it isn't a dead end.

## Recommended scope for the next push

**#4 + #6 + #7 together**: hand-place real hardpoints on the highest-traffic
ships now, ship the viewer as clean and complete-looking for everything else,
mark what's rough as unverified rather than hiding it or blocking the push on
it. **#8 (Fan Kit) runs in parallel** and could change the calculus for the
remaining ships if it lands before the rest get hand-placed.

## Not decided here

- Which specific ships count as "highest-traffic" — needs real analytics or
  Sleven's own sense of what gets looked at most.
- Exact marker-placement workflow/tooling for Blender — Code's call.
- Whether options 2 vs 1 (proxy objects vs. baked-in markers) is worth a
  build-time tradeoff discussion — flagging both, not picking one.
