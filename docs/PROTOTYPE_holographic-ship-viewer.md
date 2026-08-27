# PROTOTYPE — the holographic ship viewer. Living document. Everything about it lives here.

    what      Sleven's holographic ship viewer. He likes it and it is a
              DIRECTION, not an experiment that was parked.
    status    LIVING. Add to this file; do not fork it. When something is built
              elsewhere that would make the viewer better, fold it in here.
    screens   docs/holo-viewer-prototype-screens/  - six captures from Sleven's
              own browser, 2026-08-22. LOOK AT THEM FIRST.
    data      data-layer/derived/holo-hardpoints/  - unchanged since 2026-08-10
    replaces  the dated handoff of the same subject, which framed this as
              superseded. That framing was C3's, it was wrong, and Sleven said
              so directly.

---

## 0. The correction that created this file

An earlier handoff called the prototype **"history, not a proposal."**

**Sleven:** *"I don't know why the prototype would have been suspended. I like the
prototype. This is what I want C1 to actually see."*

**Nothing was suspended.** This file exists so the prototype has a permanent home
that accumulates instead of a dated note that goes stale.

## 1. What it is today, read off the captures

**The stage.** A ship on a lit disc, dark field, optional grid and scanlines.

**Left, upper — the ship's own numbers, with provenance stated on screen:**
name, dimensions in metres, vertex and triangle counts, hardpoint count, and the
line `geometry: CIG Fan Kit .ctm · loadout: ships.json 20260801Z`. **The page tells
a visitor where its geometry and its loadout each came from.**

**Left, lower — the loadout itemised.** `PILOT HARDPOINTS — 2104.6 TOTAL DPS`, then
every mount by position: Left Body Weapon, Mantis GT-220 Gatling, 506.7 dps,
`S3 · Gallenson Tactical Systems · on a gimbal · PILOT`. Countermeasure launchers,
missile racks by pylon, manufacturer on every line.

**Right — the controls.** Four ships. Six render styles: panel lines, solid+lines,
solid holo, lit hull, wireframe, points. Five colours. Sliders for line intensity,
line detail, glow. Toggles for auto-spin, grid, scanlines, hide back faces, loadout
list. Marker filters: show markers, guns, racks, CM, turret guns, all labels,
mirror L/R, auto-frame. **And Export JSON.**

**Bottom — the instruction.** *"Hover a marker to name it · click it, or a weapon in
the list, to read its numbers."*

**Attribution, already correct:** the trademark line, the unofficial-fan-site
notice, and the Made By The Community mark.

## 2. The three things in it worth keeping exactly as they are

**2a. The zero-hardpoint case.** Capture 05, the Cyclone: `0 hardpoints`, then in
plain English *"This hull carries no weapon mounts in the data — nothing to mark on
it."* Underneath, a second section headed **`COMPONENTS — MENU OVERLAY, NOT
HULL-MOUNTED`** listing shields, power plant, coolers, radar, cargo grid, armor,
self destruct.

**That is the internal-versus-external ruling rendered on screen with no
explanation required.** A ship with no guns does not look broken; it looks like a
ship with no guns. **It is also exactly what B3 of the picker order specifies** —
the prototype already solved it.

**2b. Six render styles from one dataset.** Same geometry drawn six ways, no extra
data. The Cyclone reads beautifully in solid holo and clinically in wireframe.

**2c. Provenance on screen.** The geometry/loadout source line. Most tools state
nothing.

## 2d. THE LOOK IS PINNED — Sleven, 2026-08-23

He sent one capture of the **Aegis Sabre** and said: *"this is what I'm talking
about, this is how I want all of the ships, this is the key to it all."*

**The combination is specific. It is not "the holographic style" in general:**

    STYLE    Solid + lines      not Panel lines, not Wireframe
    COLOUR   amber / gold       not the default cyan
    LABELS   All labels ON      a leader line out from every hardpoint
    VIEW     grid on, lit disc, scanlines off

**`Solid + lines` in amber with every label showing is now the ship page's
default state**, carried into `ORDER_every-ship-is-a-hologram-2026-08-22.md` H1.
The other styles and colours stay as controls.

**The labels are the part that matters most, and they are also the answer to a
standing problem.** Each one names the part AND the port — `CF-337 Panther
Repeater / Weapon left nose`. A derived position will never be exact; the exports
are one welded mesh with no mount data and RSI's are no better. **A labelled
leader line is what makes an approximate position useful anyway.** A dot two
metres out that names itself is informative; the same dot bare is a guess nobody
can check.

**2d-i. AND THE PROTOTYPE HAS NOT SOLVED LABEL COLLISION.** In that very capture,
on eight hardpoints, `MSD-423 Missile Rack` and `CF-337 Panther Repeater` overlap
into an unreadable stack and `Weapon left wing` is drawn twice on itself. The
Polaris has 24 markers and the Perseus 35. **A naive port of this to the fleet is
unreadable on exactly the ships where knowing what is where matters most.**
Ordered as H1b: deconflict the LABELS and not the markers, since only one of the
two is a claim about the hull.

**2d-ii. Missiles group under their rack.** The prototype's list reads
`MISSILES — CARRIED ON THE RACKS ABOVE / 2x Arrester III Missile`. The live page
renders the same thing as eight separate `Missile 0N attach` rows — Sleven
photographed that on the Gladius Valiant. Ordered as H1c.

## 3. FOLD IN — already built elsewhere, belongs here

**This section is the point of the living document. Add to it.**

**3a. Real port binding, from the live ship page.** The live page binds each marker
to its `PortId` and clicking opens the component picker. The prototype's markers
name and read out; they do not select. **Adopt the binding.**

**3b. `selectPort()` as the single selection path.** The picker order documents it
as *"THE ONE PLACE A PORT GETS SELECTED. Both routes come here."* Clicking a marker
and clicking its list row must land in the same place with the same content.
**One selection path, two entrances — keep that true here too.**

**3c. The picker as a panel over the stage, anchored near the marker.** B3: it must
not cover its own marker, flips side when there is no room, Escape closes it,
clicking the background closes it. **Choosing a gun happens where the gun is.**

**3d. Two-stage mount then weapon.** From the Erkul teardown: a gimbal mount goes
into the hardpoint, then a weapon into the mount. Our data has `WeaponAttachment`
(320 items, 35 editable ports) and the schema has `GimbalMountDetail`. **The
prototype's list is single-stage. Erkul's is not.**

**3e. Swap-panel affordances worth copying**, also from Erkul: a search box, a size
badge on every row, an explicit EQUIPPED marker, a count of what fits, and a Remove
option — **an empty port is a legal state, not an error.**

**3f. Spin off by default.** B4, from Sleven directly: *"the ship just constantly
spins."* A stop control is not the same as opening calm. Default to still, remember
the choice for the session.

**3g. Turret guns inherit their turret's position.** B5. The prototype filters
turret guns as a category; B5 says where they go.

**3h. Place against the hull's measured extremity, not a fixed fraction.** B6.

**3i. Liveries.** 279 of 316 hulls carry one editable `hardpoint_paint` port, empty
by default. Erkul shows *"No paint · factory hull."* The prototype has a colour
picker for the hologram; **that is a different thing from a ship's paint.**

**3j. CIG-asset tagging.** The prototype's geometry is Fan Kit `.ctm`. Every
CIG-sourced asset now carries a `source` field in `data-layer/cig_assets.json` and
`scripts/takedown.py --yes` strips them. **The prototype's models must carry that
tag or the takedown misses them.**

**3k. Hull-change detection, available and unused.** All 235 models have a
fingerprint — hash, vertex count, bounding box. The viewer already displays vertex
and triangle counts. **It is one step from saying "this hull has not changed since
14 August."**

**3l. B0 — a marker that does nothing must stop existing in that form.** ADDED
BY C1, 2026-08-22, and it is a CONDITION ON 3a rather than a separate item.
Measured on the live page: **782 of 1,200 hull markers do nothing when clicked —
65.2% — and on 61 hulls EVERY marker is dead.** Cause: `selectPort()` refuses a
non-swappable port, clears the selection, and re-renders the same empty prompt.
The prototype does not have this defect today because its markers only name and
read out. **The moment 3a adopts the live page's port binding, it inherits the
defect unless B0 comes with it.** A fixed port keeps its marker, looks different
before it is clicked, and opens a panel naming the part and why the game locks
it.

**3m. One attribution implementation, not two.** ADDED BY C1, 2026-08-22. The
prototype already renders the trademark line, the unofficial-fan-site notice and
the Made By The Community mark correctly. The live site now does too, as of
`ORDER_the-attribution-and-the-off-switch-2026-08-22.md` A1-A3, where the
trademark sentence is **a single constant** because it carries three registered-
trademark symbols and a specific legal entity name. **The prototype must take the
constant rather than keep its own copy.** Two hand-maintained copies of a required
legal notice is the same defect shape as `keybinds.src.html` being a second
standalone page.

## 4. The data underneath

    hardpoints_fleet.json     167 ships, 1,798 hardpoints
    place_fleet.py            the derivation, reasoning in comments
    placement_report.json     167 placed, 7 skipped with reasons, 17 crowded
    MANIFEST.json             what the dataset is and is NOT

**These are NOT CIG's coordinates.** All 25,150 ports in `ship_specs.json` carry
`position: null`. **Nobody has the real numbers.** Positions are derived from the
mount NAME plus the hull's own geometry — close, not exact, and the viewer must
keep saying so.

**The field is `pos_model`, not `pos_m`.** The library uses three scales: 158 ships
in metres, 8 normalised, 1 in centimetres. An earlier file called it `pos`, a viewer
read it as metres, it was centimetres, and every marker landed fifty ship-lengths
off the hull. **The unit belongs in the name.**

## 5. Two defects already found and fixed here — do not reintroduce them

Measured, not described:

    pure white pixels    63.7%  ->  0.0%
    markers on screen      0    ->  8
    lit pixels          48,581  ->  49,544   (ship unchanged in size)

**The white-out was `DoubleSide` plus additive blending with no depth pre-pass** on
a 353,731-vertex mesh — every surface behind every other adding light until the hull
saturated. Fixed with a depth-only pre-pass and `FrontSide`. **Anything rebuilt from
scratch hits this again if the pre-pass is left out.**

**DRACO-compressed `.glb` needs a worker to decode, and workers are blocked over
`file://`.** A viewer that "does not render" locally may simply need serving over
http. That cost a rebuild once already.

## 5b. A defect visible in the captures, not yet fixed

**`<= PLACEHOLDER =>` is on screen.** Captures 05 and 06, the Cyclone, under
**CARGO GRID** and **ARMOR** — the component list renders the literal string
`<= PLACEHOLDER =>` where a part name belongs, with a real size badge (`S1`) and
a real manufacturer (`Tumbril Land Systems`) beside it.

**It is not a rendering bug; it is upstream data reaching the page unfiltered.**
The size and manufacturer are right, so the record exists and only its name is a
placeholder.

**Two candidate behaviours, and the choice is not obvious:** suppress the row, or
show the row and say the game files carry no name for this part. **The second is
more in keeping with this project's standard** — the Cyclone's own
zero-hardpoint message is exactly that move — but a decision needs making rather
than defaulting. **Either way, the literal placeholder string must never render.**

    CONTROL: assert no rendered page contains the substring "PLACEHOLDER".
    NEGATIVE CONTROL: a part WITH a real name still renders its name - otherwise
    a build that suppresses every component row also passes.

## 6. Coverage — reaching every ship

**42 of the 68 unmarkered ships are reachable with data already on this machine**
(`FINDING_reaching-every-ship-2026-08-22.md`). **Not 29 — that figure was
understated and corrected on 2026-08-22.**

Twelve are CIG's longer name against our short one — `Aurora_CL` against
`Aurora Mk I CL`, `A2_Hercules` against `A2 Hercules Starlifter`. Sixteen are paint
and edition variants covered by the shared-hull ruling. One is a capital letter,
`Khartu-Al` against `Khartu-al`.

**The seven rejected by the placement guard, in full: Clipper, Defender, Eclipse,
Javelin, Nova, Pulse, Pulse LX.** Six need corrected dimensions and their mount data
is already available. **Pulse LX is the exception — 8 ports, zero weapon mounts** —
so a dimension fix changes nothing visible. It belongs with the correctly-empty
ships, exactly like the Cyclone in capture 05.

**Do not loosen the proportion guard.** The Defender and the Eclipse are both
published at 24.5 x 24.5 x 5, confirmed in two independent datasets. Different
ships, identical figures. The guard is right and the source is wrong.

**One rule for the mapping table: no fuzzy matching.** It produced four confident
wrong pairs on 2026-08-16 — Dragonfly Black to Yellowjacket, E1 Spirit to C1 Spirit,
G12a to 125a, Zeus MR to Zeus ES. **In the real pipeline that bolts the wrong
hardpoints onto four ships and nothing catches it.**

## 7. RSI's own models cannot help here

Per `AMENDS_extracted-textures-scope-2026-08-22.md`, from CIC's live capture: they
are OpenCTM — one mesh, exterior hull only, and **OpenCTM cannot express a node
hierarchy by format definition.** No named parts, no hardpoint nodes.

**Derived markers are not a stopgap waiting for something better. They are the only
approach available.** Nobody should plan around real coordinates arriving.

## 8. Open, and worth settling early

- ~~**Which build produced the 2026-08-22 captures.**~~ **SETTLED by C1,
  2026-08-22, with a hash rather than an argument. NOBODY DEVELOPED IT FURTHER.**

      Downloads/citizen-compass-holo-viewer.html     13,314,680 B   Aug  9 20:49
      Downloads/citizen-compass-holo-viewer_1.html   13,314,680 B   Aug 22 23:02

      sha256  5e91d8e41cb250ca8acd795a81759b9234fa565fa2cec181cd9323fcbe6eac1a
      sha256  5e91d8e41cb250ca8acd795a81759b9234fa565fa2cec181cd9323fcbe6eac1a

  **Byte-identical.** The `_1` is Chrome's duplicate-name suffix from Sleven
  re-downloading the same file on 22 August to take the captures. **The rich
  control panel IS C3's 2026-08-09 build** — six render styles, five colours,
  three sliders, the marker filters and Export JSON were all there on day one.
  The earlier reading of it as "considerably richer than C3 built" was wrong.

  **The lesson is the one this project keeps relearning: a filename is not a
  fact about a file.** Two minutes of `sha256sum` closed a question that was
  about to send somebody hunting for a developer who does not exist. Same shape
  as `collector-master.exe` silently being the crew build.
- **Whether the 42 would PLACE once joined.** Their ports exist; the placement step
  must still accept the geometry. **Nobody should promise 42 until a run proves it.**
- ~~**Whether `place_fleet.py`'s port-name vocabulary matches the wiki
  dataset's.**~~ **SETTLED by C1, 2026-08-22. IT IS THE SAME VOCABULARY — there
  is no mapping to build.** Measured across 29 comparable hulls, 333 port names:
  **263 found verbatim in the wiki data, 79.0%.** The 70 misses are almost
  entirely not mounts — 47 are `hardpoint_weapon_regen_pool` / `_regen_pool_turrets`
  ammo-pool pseudo-ports, 13 are `hardpoint_weapon_rack` / `_locker` FPS storage
  inside the hull. **Strip the non-mounts and agreement is roughly 97%**; the
  remaining ~10 real misses (`animated_turret_*`, `hardpoint_mountedgun_*`,
  `hardpoint_manned_turret_airlock_*`) are an hour of work, not a build.

  **Why it was always going to be the same:** both sources read the same CIG game
  files. The wiki publishes CIG's port names, exactly as scunpacked does.
  `hardpoint_controller_flight` is identical on both sides.

  **Bigger thing found while checking, and it changes what this dataset is for:**
  the wiki record carries **roughly double the ports per ship on hulls we already
  cover** — Freelancer ours 11 / theirs 22, Fortune ours 6 / theirs 16 — and each
  port carries `type`, `sizes{min,max}`, `compatible_types[]`, the equipped item,
  and **`editable`**, the same per-port flag the whole swappability model rests
  on. `position` is null, consistent with everything else. **Treat it as a second
  independent source to cross-check against, not only as a patch for 68 gaps.**
  Full detail: `FINDING_reaching-every-ship-2026-08-22.md`.
- **The prototype is four ships. The dataset is 167.** Nobody has run the prototype
  against the full set.
