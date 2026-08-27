# FINDING — the 3D viewer now has fixed hardpoints. Positions are derived from mount-name vocabulary plus hull geometry, the model frame was worked out from the meshes, and left/right is the one thing still assumed.

    from      C3 (Cowork), 2026-08-09
    for       Code + C1 + Sleven
    builds on claude/FINDING_hardpoint-positions-and-holo-viewer-v2-2026-08-08.md
              claude/FINDING_mount-name-vocabulary-2026-08-08.md
    artifacts inbox/place_hardpoints.py · inbox/hardpoints.json
              Downloads/citizen-compass-holo-viewer.html

---

## 1. What was wrong and what replaced it

The old viewer had a **place mode**: arm a weapon, click the hull, a dot appears where the
mouse was. That is an authoring tool. Sleven's description of the problem was exact —
"they would go anywhere I clicked, and that wasn't how it's supposed to be."

Place mode is gone. Every hardpoint is now **fixed**, sits where its mount name says, and
opens that mount's numbers when clicked.

    Drake Cutlass Black       15 hardpoints
    RSI Constellation Aquila  12
    Aegis Sabre                8
    Tumbril Cyclone            0 — this hull carries no weapon mounts in the data,
                                   and the panel says so rather than showing nothing

## 2. Where a position comes from, said plainly

**CIG's own data has no coordinates.** All 53,651 `position` fields across every mount are
null — measured and written up yesterday. Nobody has the real numbers: not us, not Erkul,
not anyone working from the same files.

What the data does carry is the mount's **name**, and the names are locations:

    Weapon left wing          Gun laser bottom right      Left Pylon 2
    Missilerack top left rear Countermeasure launcher left Turret · weapon left

Each name is read into side / vertical / longitudinal / part, turned into a target point
in the hull's own normalised box, and then **snapped to the nearest real vertex of the
mesh** so the marker sits on geometry that exists rather than floating beside it.

It is derived. It is not CIG's. **The viewer says so on every hardpoint panel**, naming
which words placed it. Sleven accepted estimated positions; that is not a reason to let a
guess read like a measurement.

## 3. The model frame, worked out rather than assumed

| axis | meaning | how it was established |
|---|---|---|
| X | lateral | every hull is symmetric about x=0 |
| Y | up | the Cyclone's minimum Y is 0.0 — its wheels sit on the ground plane. The Aquila runs −372 to +951, more ship above the datum than below |
| Z | **forward is −Z** | at the low-Z end the Sabre is 369 cm wide; at the high-Z end 2338 cm, its full wingspan. A Sabre's nose is a point and its tail is the wings. The Aquila agrees: 1048 cm at low Z against 2072 cm wide and 1088 cm tall at high Z, which is its engine block |

**Left/right is the one thing still assumed.** With forward −Z and up +Y, a right-handed
frame puts starboard at +X. That holds only if the export preserved handedness, which is
normal but which these files do not state. The hulls are mirror-symmetric to within 2–3%
— stray vertices, not features — so **nothing in the geometry can confirm it.** I looked:
I tried to find an asymmetric feature in the Cyclone's cabin to settle it from the driver's
seat, and the Fan Kit models are exterior hull only, so there is no cabin to look at.

So the viewer has a **Mirror L/R** control, and mirroring flips the WORD as well as the
marker — otherwise the label and the dot would disagree and it would be wrong twice.

## 4. The first attempt collapsed, and how

Scoring vertices by "how far out can I get on the correct side" put **every** left-hand
mount on the same wingtip vertex. The Cutlass's left wing gun, left countermeasure
launcher and left pylon 3 all landed on one point; pylons 2 and 3 were identical.

Replaced with an explicit target per part plus a separation pass that pushes a colliding
marker along the hull until it clears, **and reports it if it cannot** rather than hiding
the overlap. Result:

    closest pair, Cutlass   327 cm   7.2% of the hull
    closest pair, Aquila    481 cm   7.1%
    closest pair, Sabre     264 cm   7.8%
    furthest any marker sits from the hull surface: 1.2% of hull size, worst case

Both numbers are checked in the test rather than eyeballed. A marker on top of another
marker is unclickable, which is a silent failure, which is this project's recurring shape.

## 5. One physical hardpoint, one marker

The data lists a gimbal mount and the gun sitting in it as two rows sharing a `where`.
They are the same place on the hull, so they are merged into one hardpoint carrying both —
otherwise every wing sprouts two markers on top of each other. Clicking "Left Wing Weapon"
shows the CF-337 Panther Repeater **and** the VariPuck S3 Gimbal Mount it sits in, with
545.6 DPS and 43.7 alpha read straight out of the data.

Turret guns — `Turret · weapon left` — are marked separately in blue and labelled
**NOT PILOT-CONTROLLED**, because a Cutlass owner reading a DPS total needs to know which
half of it needs a second person.

## 6. Internal components still get a menu, not a marker

Unchanged and deliberate: the standing decision is that anything you never physically walk
up to belongs in a menu overlay. Power plant, coolers, shield, quantum drive stay in the
list under "COMPONENTS — MENU OVERLAY, NOT HULL-MOUNTED". Not re-litigated.

## 7. Also fixed while in there

**Labels.** Fifteen labels at once was a wall of unreadable text on the Cutlass — every
marker correct, none of them legible. A label now appears only for the marker you are
pointing at or have opened, with an "All labels" toggle for the full set. Markers on the
far side of the hull fade to 30% instead of reading as if they were on the near side.

**Framing.** Each hull is now framed to fill the view, fitted to the tighter of the
horizontal and vertical field of view. Fitting only to the vertical left the 61 m
Constellation looking distant beside the 24 m Sabre.

**Drag versus click.** Orbiting used to close the detail panel, because a drag ended in a
click. A pointer that moves more than 5 px is an orbit now.

**A "Lit hull" finish**, since Sleven asked about material swapping. It is procedural
shading, not a skin — **the Fan Kit .ctm files carry geometry and one EMPTY UV map, checked
file by file**, so there is no texture to apply and the code says so where someone will
read it. The panel banding is shading standing in for plating. It should never be described
to a user as a paint.

## 8. Tested in a real browser

32 checks, all passing, including the ones that could have caught a plausible-looking
mistake:

    the two wing guns are symmetric to within a hair
    a wing gun is further outboard than a body gun
    the top turret gun is above the body guns
    the three left pylons are spread along the ship, in order, not stacked
    every hardpoint in the data has a marker, on all four hulls
    no marker floats off the hull  (worst 0.053 of 2.0 units)
    clicking a marker opens the hardpoint it names, with real DPS
    the panel says the position is derived and that CIG's field is null
    dragging to orbit does not close the panel
    mirror flips the marker AND the left/right word together
    turning racks off removes exactly the 6 pylon markers

Screenshots were taken of every ship and looked at, not just asserted — which is how the
label pile and the too-dark hull finish were caught, since both passed every check.

## 9. What I checked and what I did not

**Checked:** the model frame against four hulls; the unit-cube packing decoded from the
payload rather than trusted from the packing code (the Aquila comes back spanning
0.870 × 0.435 × 2.000 against real dimensions of 2649.7 × 1323.8 × 6090.2 cm, the same
ratios); every mount name parsed; marker separation and distance-to-hull measured on all
four ships; the full viewer driven in headless Chromium.

**Did NOT check:**
- **No position here is CIG's.** They are derived, every one, and the accuracy is "about
  where that gun is", not a coordinate.
- **Left and right are assumed**, per §3, and nothing available can confirm them.
- Only four hulls. The rules are name-driven and should generalise, but 312 other ships
  have not been run through this and the vocabulary work showed 63.6% of mounts sit in
  within-ship name collisions — those hulls will need the separation pass to do more work,
  and some will hit the "cannot separate" report.
- Missile counts are the ship total, not per rack; the data gives a total and does not
  split it. The panel says that where a rack is opened rather than dividing it and
  implying precision that is not there.
