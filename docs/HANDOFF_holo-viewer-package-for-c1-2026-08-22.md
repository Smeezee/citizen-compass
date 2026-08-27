# HANDOFF — C1: OPEN THE SCREENSHOTS AND LOOK AT THIS BEFORE READING ANYTHING ELSE. Sleven likes the holographic viewer prototype and wants it seen as a DIRECTION, not as history.

    from      C3 (Cowork), 2026-08-22
    for       C1 - and this needs an actual look, not a skim
    screens   docs/holo-viewer-prototype-screens/  - six captures from Sleven's
              own browser, 2026-08-22
    status    THIS REPLACES AN EARLIER VERSION OF THIS DOCUMENT that framed the
              prototype as superseded. That framing was mine and it was wrong.
              See section 0.

---

## 0. CORRECTION, and it is the reason this document was rewritten

An earlier version of this handoff said the prototype was **"history, not a
proposal"** and that the live ship page **"has long since passed it."**

**Sleven's response, verbatim:** *"I don't know why the prototype would have been
suspended. I like the prototype. This is what I want C1 to actually see."*

**That framing was mine, it was not his, and it is withdrawn.** Nobody suspended
anything. **He likes this and he wants it looked at properly.**

## 1. What the screenshots show

Six captures, in `docs/holo-viewer-prototype-screens/`:

    01  Cutlass Black, panel-lines style, side, markers visible
    02  Cutlass Black, front three-quarter, yellow rack markers on the pylons
    03  Cutlass Black, points style - the hull as a point cloud
    04  Cutlass Black, wireframe
    05  Cyclone, wireframe - ZERO hardpoints, handled correctly
    06  Cyclone, solid holo - the glowing filled look

**Look at 01 and 06 in particular.** They are two completely different visual
registers from the same page and the same data.

## 2. What is actually in it, read off the captures

**Left panel — the ship's own numbers.** Name, dimensions in metres, vertex and
triangle counts, hardpoint count, and **a provenance line: `geometry: CIG Fan Kit
.ctm · loadout: ships.json 20260801Z`.** The page states where its geometry and
its loadout each came from, on screen, to the visitor.

**Left list — the loadout, itemised.** `PILOT HARDPOINTS — 2104.6 TOTAL DPS`, then
every mount by position: Left Body Weapon, Mantis GT-220 Gatling, 506.7 dps,
`S3 · Gallenson Tactical Systems · on a gimbal · PILOT`. Countermeasure launchers,
missile racks by pylon, manufacturer on every line.

**Right panel — the controls.** Four ships. Six render styles: panel lines,
solid + lines, solid holo, lit hull, wireframe, points. Five colours. Sliders for
line intensity, line detail and glow. Toggles for auto-spin, grid, scanlines, hide
back faces, loadout list. Marker filters: show markers, guns, racks, CM, turret
guns, all labels, mirror L/R, auto-frame. **And an Export JSON button.**

**Bottom — the instruction line.** *"Hover a marker to name it · click it, or a
weapon in the list, to read its numbers."*

**Bottom left — the attribution, already correct.** *"Star Citizen®, Roberts Space
Industries® and Cloud Imperium® are registered trademarks of Cloud Imperium Rights
LLC. Unofficial fan site. Not affiliated with Cloud Imperium Games."* Plus the
Made By The Community mark, bottom right.

## 3. The three things worth taking from it, in order

**3a. The zero-hardpoint case is handled well and it is worth copying exactly.**

Capture 05, the Cyclone, reads `0 hardpoints` and then says in plain English:

> *"This hull carries no weapon mounts in the data — nothing to mark on it."*

And underneath, a second section headed **`COMPONENTS — MENU OVERLAY, NOT
HULL-MOUNTED`** listing shields, power plant, coolers, radar, cargo grid, armor and
self destruct.

**That is the internal-versus-external distinction the project decided months ago,
rendered on screen without a word of explanation needed.** A ship with no guns does
not look broken; it looks like a ship with no guns.

**3b. Six render styles from one dataset.** Panel lines, wireframe, points and solid
holo are the same geometry drawn four ways, and they suit different ships. The
Cyclone reads beautifully in solid holo (06) and clinically in wireframe (05).
**That is a lot of visual range for no extra data.**

**3c. Export JSON.** The page can hand back what it is showing. Worth knowing that
existed before anyone designs the equivalent from scratch.

## 4. Where the data under it comes from

    hardpoints_fleet.json     167 ships, 1,798 hardpoints
    place_fleet.py            the derivation, reasoning in comments
    placement_report.json     167 placed, 7 skipped with stated reasons, 17 crowded
    MANIFEST.json             what the dataset is and is NOT

All four sit in `data-layer/derived/holo-hardpoints/` and have since 2026-08-10.

**These are NOT CIG's coordinates.** All 25,150 ports in `ship_specs.json` carry
`position: null`. **Nobody has the real numbers.** Positions are derived from the
mount NAME plus the hull's own geometry — close, not exact, and the viewer must
keep saying so.

**One naming decision to carry forward.** The field is `pos_model`, not `pos_m`,
because the library uses three scales — 158 ships in metres, 8 normalised, 1 in
centimetres. An earlier file called it `pos`, a viewer read it as metres, it was
centimetres, and every marker landed fifty ship-lengths off the hull. **The unit
belongs in the name.**

## 5. Two defects that were found and fixed in this prototype

Measured, not described:

    pure white pixels    63.7%  ->  0.0%
    markers on screen      0    ->  8
    lit pixels          48,581  ->  49,544   (ship unchanged in size)

The white-out was `DoubleSide` plus additive blending with **no depth pre-pass** on
a 353,731-vertex mesh — every surface behind every other surface adding light until
the hull saturated. Fixed with a depth-only pre-pass and `FrontSide`. **Anything
rebuilt from scratch will hit this again if the pre-pass is left out.**

Also worth knowing: DRACO-compressed `.glb` needs a worker to decode, and workers
are blocked over `file://`. **A viewer that "does not render" locally may simply
need serving over http.** That cost a rebuild once already.

## 6. Reaching every ship — the ships not yet covered

**42 of the 68 unmarkered ships are reachable with data already on this machine**,
per `FINDING_reaching-every-ship-2026-08-22.md`. **Not 29 — that figure was
understated and was corrected today.**

The seven rejected by the placement guard, named in full: **Clipper, Defender,
Eclipse, Javelin, Nova, Pulse, Pulse LX.** Six need corrected dimensions and their
mount data is already available. **Pulse LX is the exception — 8 ports, zero weapon
mounts** — so fixing its dimensions changes nothing visible. It belongs with the
correctly-empty ships, exactly like the Cyclone in capture 05.

**And RSI's own models cannot help here.** Per `AMENDS_extracted-textures-scope-2026-08-22.md`,
they are OpenCTM — one mesh, exterior only, and **OpenCTM cannot express a node
hierarchy by format definition.** Derived markers are not a stopgap waiting for
something better. They are the only approach available.

## 7. What I checked and what I did not

**Checked:** every feature listed in section 2 is read off the six captures, not
recalled; the dataset files are unchanged on disk since 2026-08-10; the 68-ship
breakdown ship by ship against four data files.

**Did NOT check:**
- **Which build produced these captures.** The window title is
  `citizen-compass-holo-viewer_1.html` and the four ships match the 2026-08-09
  prototype, but the control panel is considerably richer than what I built.
  **Somebody has developed it further and I do not know who or when.** Establish
  that before anyone rebuilds anything.
- **Whether the 42 would PLACE once joined.** Their ports exist. The placement step
  must still accept the geometry. **Nobody should promise 42 until a run proves it.**
- **Whether `place_fleet.py`'s port-name vocabulary matches the wiki dataset's.** It
  derives position from the mount NAME. If the names differ, the mapping is a second
  job. **This is the biggest unknown in section 6 and it is checkable in an hour.**
