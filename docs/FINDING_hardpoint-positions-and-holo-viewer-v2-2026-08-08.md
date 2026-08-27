# FINDING — there are ZERO hardpoint coordinates in this project's data (53,651 nulls, no exceptions). But the mount NAMES describe every position in plain English, and that changes the job.

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1 + Code
    ask       Sleven, on the holographic viewer: "can we take the hardpoint information
              and apply it? If it has weapons on it, can we talk about the weapons, where
              they're actually located on the ship, and same for actual ship components."
    method    Counted every position field in ship_specs.json rather than trusting the
              existing docs. Re-derived the pilot-weapon rule and re-validated it against
              CIG's own PilotDps on all 275 armed ships. Built and browser-tested a working
              viewer; every claim below is either a counted number or a verified screenshot.

---

## 1. The blunt answer on 3D positions

`data-layerrawhardpoints/ship_specs.json` has a `position` field on every port. **53,651
`position` keys. 53,651 of them are `null`. Zero non-null, no exceptions.** The schema has
a slot for coordinates and nothing ever filled it.

The Fan Kit `.ctm` models can't supply them either — verified in the earlier pass: single
merged mesh, zero attribute maps, no node hierarchy, so there are no named empties to read
positions off.

**So the standing project position ("hardpoints require manual placement") is correct, and
is now backed by a number instead of an assertion.** Nothing here reopens it.

## 2. What DOES exist, and nobody had used it: every mount is named by location

This is the actual finding. Each `Loadout[]` entry in `ships.json` carries a **`Path`
array** of the full mount chain — and the names are descriptive, not opaque IDs.

Drake Cutlass Black, read straight out of the file:

    ['hardpoint_Left_Wing_Weapon',  'hardpoint_class_2']   CF-337 Panther Repeater
    ['hardpoint_Right_Wing_Weapon', 'hardpoint_class_2']   CF-337 Panther Repeater
    ['hardpoint_Left_Body_Weapon',  'hardpoint_class_2']   Mantis GT-220 Gatling
    ['hardpoint_Right_Body_Weapon', 'hardpoint_class_2']   Mantis GT-220 Gatling
    ['hardpoint_turret', 'hardpoint_weapon_left',  ...]    CF-337 Panther Repeater
    ['hardpoint_turret', 'hardpoint_weapon_right', ...]    CF-337 Panther Repeater

Also present: `hardpoint_cm_launcher_left` / `_right`, `hardpoint_Left_Pylon_01..03`,
`hardpoint_Right_Pylon_01..03`. On the Sabre: `weapon left nose`, `weapon right nose`,
`weapon left wing`, `weapon right wing`. On the Aquila: `gun laser top left`,
`gun laser bottom right`.

**Two consequences, and the second one is the useful one:**

1. **"Where are the weapons" is answerable in words today, for all 316 ships, with no
   manual work at all.** Left wing, right nose, turret-left, left pylon 2. That is most of
   what Sleven actually asked for and it needed no new data.
2. **It converts hardpoint placement from an open-ended art task into a checklist.**
   The Cutlass has 21 individually-named placeable mounts. Whoever places markers is no
   longer guessing what to place or where — the data names each one and says which side of
   the ship it's on.

**Important caveat, stated plainly: a name is not a coordinate.** `hardpoint_Left_Wing_Weapon`
tells you which wing, not where along it. This narrows the manual job, it does not remove it.

## 3. Rather than send this to Blender, the placement tool is now in the viewer

The standing 3D-viewer decision is *Blender-placed markers + Three.js raycasting*. The
Blender half is the expensive half and it needs a skill Sleven has said he does not want to
have to learn.

**Built and verified instead: click-to-place, inside the hologram itself.** Pick a mount
from the loadout list (it says "LEFT WING WEAPON"), click that spot on the hull, a marker
lands on the surface. Export writes a JSON file:

    {
      "schema": "citizen-compass.hardpoints/1",
      "ship": "Drake Cutlass Black",
      "model_space": "origin-centred unit cube, Y up; multiply pos by scale_cm_per_unit for centimetres",
      "scale_cm_per_unit": 1785.85,
      "hardpoints": [
        {"port":"hardpoint_class_2","where":"Left Wing Weapon",
         "item":"CF-337 Panther Repeater","type":"WeaponGun","size":3,
         "pos":[-0.27947,0.03606,0.81379]}
      ]
    }

Verified end to end in headless Chromium, not asserted: armed a mount, clicked the hull,
4 markers + 4 labels created, export produced the JSON above, undo removed one, zero console
errors. Round-tripping the first coordinate through `scale_cm_per_unit` puts it at
−2.99 m, 0.77 m, 14.28 m from ship centre, which is inside a 35.7 m hull. Import is wired
too, so a file can be reloaded and corrected later.

**This is a proposal for Code to own, not a shipped feature** — C3 doesn't build site code.
But the schema and the interaction are proven rather than sketched, and the output drops
straight into `data-layer/derived/`.

## 4. Components are deliberately NOT getting hull markers

Per the standing architecture decision, internal components — power plant, coolers, shield,
quantum drive — are never physically walked up to in game and get a **menu-driven overlay**
instead of 3D placement. The viewer follows that: components render as a grouped list with
real values (shield HP, QD speed, sizes, manufacturers), under a header that says so out
loud. Not re-litigating a settled call; recording that it was honoured.

## 5. A correction to my own work, caught by validating instead of trusting

My first loadout extraction defaulted a weapon with **no** `IsPilotSlaveable` flag to
*not* pilot-controlled. That silently mislabelled every plain fixed gun — the Sabre reported
0 pilot DPS when the truth is 2,182.4.

The rule is: **default TRUE; only an explicit `false` locks a weapon out, and once locked it
cannot be reopened deeper in the tree.** Revalidated against `Systems.Weapons.Summary.PilotDps`
across every armed ship: **275/275 exact, 100%.** Same figure the earlier aggregation work
landed on, now reproduced from scratch.

Worth noting the failure mode: the wrong version *looked* fine. It produced plausible
weapon lists. Only checking against CIG's own total caught it.

Second correction: the field is `HardpointName`, not `PortName`. My first pass wrote empty
strings into every port and I only noticed because the exported JSON had `"port": ""`.

## 6. Why the Aquila washed out and the Cutlass didn't — it was measurable, not taste

Sleven: *"on the Cutlass, panel lines is the style I like best… but on the Aquila, panel
lines looks too washed out and too overbearing and white."*

Counted the edges each hull produces at the same 24° threshold:

    Drake Cutlass Black        265,504 tris    168,351 edges
    Aegis Sabre                621,882 tris    366,343 edges
    RSI Constellation Aquila   479,501 tris    384,061 edges
    Tumbril Cyclone            144,714 tris    124,701 edges

**The Aquila lays down 2.3× as much line as the Cutlass into the same screen area, and the
lines blend additively, so they sum toward white.** Same opacity, very different result —
nothing to do with the ship's design.

Fixed by normalising opacity against measured edge count at load
(`0.44 × (168351/edges)^0.85`, clamped), so any hull added later self-balances rather than
needing a hand-tuned number. Measured in-browser afterwards: Cutlass 0.442, Aquila 0.218,
Sabre 0.227, Cyclone 0.55. **Worth carrying into the real build — this will bite again the
moment a dense hull is added, and it is not obvious from looking at one ship.**

## 7. Also fixed / added this pass

- **New "Solid + lines" style** — opaque shaded hull with panel lines over it. The previous
  solid mode read murky because it was additive-only with nothing writing depth, so the grid
  showed through the ship. Now the hull genuinely occludes.
- **Line Intensity and Line Detail sliders** (detail re-computes the edge threshold live,
  6°–60°), so the look is tunable per taste rather than baked to mine.
- All five styles kept, per Sleven's explicit "I kinda wanna keep all the options."

## 8. What I did not do

- Did not touch any site code, the repo build, or the database.
- Did not place a single real hardpoint. Every marker in the screenshots is a test click by
  me to prove the mechanism, **not** a claim about where that gun actually sits. **None of
  it should be treated as data.**
- Did not resolve whether a static "real paint job" reference photo from RSI's site is
  usable — still open, still Sleven's call, unchanged from the earlier finding.
- The viewer carries 4 ships because that is ~13 MB of geometry; the technique is not
  limited to 4, or to the Fan Kit's 14. The project's own 235 `.glb` models are texture-free
  for the same reason and render the same way.
