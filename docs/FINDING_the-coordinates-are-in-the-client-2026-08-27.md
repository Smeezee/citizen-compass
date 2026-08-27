# FINDING — The hardpoint coordinates are not missing. They are in the client.

**C1, 2026-08-27. Measured on Sleven's own machine, against the LIVE 4.10
install. Nothing installed, no third-party tool.**

## The claim this overturns

`place_hardpoints.py` opens with a sentence this project has repeated for
three weeks:

> *"We do not have real coordinates. All 53,651 `position` fields in the game
> data are null."*

**That sentence is true and it is about the wrong file.** It describes the
UNPACKED data (scunpacked's `ships.json`). It has never been checked against
the shipped client, which is the one place the coordinates MUST exist — the
game itself has to know where to put a gun.

They exist. Here is the measurement.

## What was done

`probe_ship_geometry.py` and `extract_p4k_entry.py`, both new, both reusing the
ZIP64 + zstd path already proven in `extract_default_profile.py`. The only
substitutions are the archive path and zstd through the system `libzstd.so`
rather than Git for Windows' DLL.

    Data.p4k                161,671,868,416 bytes   LIVE, 2026-08-26
    central directory       1,365,835 entries, 464.2 MB
    DRAK_Vulture.cga        32,912,960 bytes, zstd (method 100), extracted clean

The Vulture because it is the ship Sleven actually flies.

## What is in it

    #ivo, version 0x0900, 8 chunks

Chunk 1 (`0xC201973C`, 27,272 bytes) is the node table. Its own header declares:

    286   nodes
    6627  bytes of packed, null-terminated names

**The name blob parses to exactly 286 names.** That is a cross-check, not a
coincidence: a wrong offset or a wrong length would not land on the declared
count.

Among them:

    hardpoint_weapon_rack        hardpoint_fuel_port
    hardpoint_fire_extinguisher  hardpoint_vehicle_destroyed
    ... and 172 more

**176 occurrences of `hardpoint` in one ship's geometry file.** Alongside them,
in the same table, are the helpers the game places components against —
`helper_component_power_01`, `helper_component_cooler_02`,
`helper_component_quantum`, `helper_component_lifesupport`.

3x4 transforms are in the same chunk. Two were read cleanly and are real:

    [-1, 0, 0, 0]  [0, 0, 1, -1.1]  [0, 1, -0, 2]

and further in, a node at translation `(0, -10.083, 2.023)` and an axis-aligned
box `min (-4.271, -1.853, -7.411)  max (4.271, 1.753, 1.415)` — a sub-part's
own bounds, mirror-symmetric about x, which is what a real ship part looks like.

## DECODED — and proven on a second ship, because one ship is one ship

**The node table is decoded and `decode_cga_nodes.py` is in the repo.**

    container   #ivo, version 0x0900
    0xC201973C  u32 nodeCount, u32 stringBytes, then (nodeCount + 1) 16-byte
                records - the first is a null entry - then the packed names.
    0x70697FDA  64-byte header, then nodeCount records of 208 bytes.
                  +16   3x4 row-major transform, translation in column 4, METRES
                  +64   a second 3x4, parent-relative - NOT for placement
                  +128  u16 node index
                  +130  the same index again

**HOW THE STRIDE WAS FOUND, because the method is the point.** There is no
spec. Every 4-byte offset in the chunk was tested for a 3x4 whose three
rotation rows are unit length and whose translation is finite. The gap
histogram of the 1,430 hits has one non-trivial mode: **144, occurring 285
times, in a chunk declaring 286 nodes.** Group starts sit 208 apart, and
48 + 286x208 = 59,536 against a name blob beginning at 64,939 — the records end
before the strings with room for nothing else.

**THE JOIN IS A PROOF, NOT A GUESS.** The u16 at +128 across the Vulture's 286
records is a **permutation of 0..285** — every value present, every value
distinct. A wrong field would not be a bijection. Two hash families were tried
against the names first (CRC32 and FNV, four variants each) and every one
scored zero; that was reported rather than forced.

### The acceptance test, run unchanged from the version written above

| | Drake Vulture | Aegis Gladius |
|---|---|---|
| nodes | 286 | 273 |
| `hardpoint_*` nodes | **88** | **64** |
| finite transforms | 88 / 88 | 64 / 64 |
| named left/right pairs mirrored | 18 / 21 | 13 / 14 |
| lateral span vs published beam | 12.90 m vs 21.5 | 15.33 m vs 16.5 |
| fore/aft span vs published length | 30.61 m vs 38 | 17.42 m vs 20 |
| **acceptance** | **PASS** | **PASS** |

**The Gladius is the control and it is the more convincing of the two**, because
a fighter's guns are where a wrong decode would show:

    hardpoint_gun_left_wing            (-4.676, -1.805, -0.282)
    hardpoint_gun_right_wing           ( 4.682, -1.805, -0.282)
    hardpoint_gun_nose                 ( 0.000, 10.589, -1.169)
    hardpoint_missilerack_left_wing_outer  (-7.379, -1.178, -0.760)
    hardpoint_missilerack_right_wing_outer ( 7.379, -1.178, -0.760)

Wing guns mirrored to **6 mm**. The nose gun on the centreline and at the
frontmost point of the whole set. The outer missile pylons at 7.379 m against a
16.5 m wingspan. **Nothing about a wrong stride produces that.**

### The pairs that do NOT mirror, reported rather than smoothed over

Four across the two ships, and every one is an INTERNAL component:
`shield_generator`, `fuel_tank` and `cooler`. They share an x and differ in one
other axis — stacked bays that CIG named left/right. **That is CIG's naming, not
our decode**, and it lands on components this project already routes to the
menu overlay rather than to a hull marker.

### THE FLEET RUN — 77 hulls pass, 6,819 hardpoints

`build_hardpoint_transforms.py` indexes the 464 MB central directory once and
decodes every hull it finds. Output in `data-layer/derived/hardpoint-transforms/`.

    116  hull .cga entries found and resolved
    109  decoded
     77  PASS      6,819 named hardpoints between them
     16  decoded, exterior mirror below threshold - named, not claimed
     11  decoded, no left/right EXTERIOR pair to test - cannot pass, and say so
      5  not hulls (Refuel_Arm, elevator_600i, the Prospector drill arm)
      7  the decoder REFUSED - the node index is not a clean key on these

Passing hulls include the Polaris (187 hardpoints), Perseus (161), Apollo (151),
Zeus (132), 890 Jump (122), Hammerhead, Redeemer, Vanguard, Valkyrie, Carrack,
Terrapin, Ironclad, MOLE, RAFT, Hull B and C, Starfarer, Prospector, and the
Vulture.

**THE GATE IS THE EXTERIOR MOUNTS, AND THAT IS A NARROWING, NOT A WIDENING.**
Scoring every named left/right pair together failed the Carrack, the
Constellation and the Corsair. Splitting the two families says why: on the
Vulture `hardpoint_cooler_left` and `hardpoint_cooler_right` are 1.1 m apart
along the ship's AXIS - stacked bays CIG named left/right. Weapons, turrets,
missile racks and countermeasure launchers are the ones the viewer marks on the
hull at all; internal components go to the menu overlay under a standing
decision that predates this work. **Both scores are recorded per hull in the
MANIFEST** so nobody has to take the gate's word for it.

**A hull with no testable pair FAILS.** Eleven decode cleanly and are reported
as unproven rather than passed, because a check that could not have failed is
not a check.

### Two defects found in this file's own tooling, recorded rather than quietly fixed

**The indexer read its own tail.** It resolved each match to a header using the
same file handle it was scanning with, so every lookup rewound the read position
~2 KB while the loop counter marched on. **3,891 real matches produced two
hulls, and 464 MB "scanned" in two seconds.** Nothing errored. Split into scan
and resolve.

**The hull rule was a suffix join and missed every ship behind a structural
folder.** `ANVL\Carrack\Exterior\ANVL_Carrack.cga` matched nothing until the
rule accepted any CONTIGUOUS RUN of path segments - still exact equality, still
no fuzzy matching. 63 hulls became 116. Two stems are claimed by two paths each
and are DROPPED and named, the same way the 85X collision was handled.

### PLACED IN THE VIEWER'S OWN SPACE — 70 hulls, 733 exterior mounts

`build_hardpoint_placement.py` converts CIG metres to GLB units:

    glb_x =  cga_x / s        lateral
    glb_y =  cga_z / s        up
    glb_z = -cga_y / s        forward is -Z

    70 hulls PASS   6,451 hardpoints   733 exterior weapon mounts
     5 hulls FAIL   named, with the offending mounts listed
    36 skipped      19 no ships.json row, 11 no model, 6 no hardpoints

**THE SCALE IS CIG'S OWN LENGTH, AND THE FIRST ATTEMPT AT IT WAS WRONG.**
Taking the median of Length, Width and Height failed 61 of 75 hulls — not
because the decode was wrong but because **CIG measures Width with wings, arms
and gear DEPLOYED while the GLB is one stowed pose**, and Height often excludes
gear the box includes. Length is nose-to-tail on both sides of the comparison
and is the only one of the three that is. The other two are recorded per hull as
diagnostics.

**WHICH MEANT THE CHECK HAD TO MOVE SOMEWHERE IT COULD NOT BE CIRCULAR.**
Deriving the scale from the fore/aft extent makes fore/aft containment trivially
true. So the acceptance test measures **lateral and vertical only** — a
transposed axis or a wrong frame puts mounts outside the hull sideways or
through the roof, and that is a thing this can see. Fore/aft is deliberately not
tested; marking our own homework is not a check.

**789 exterior weapon mounts placed fleet-wide, 779 inside the hull — 98.7%.**
The ten outside are named and every one is explicable rather than dismissed: the
Valkyrie's top turret, the Reliant's wing-tip guns (**its wings rotate 90 deg and
the GLB is one pose** — a real limitation of a single-pose model, not of the
decode), the SRV's countermeasure launchers, the Banu Defender's missile racks,
and the Scythe, which is Vanduul and deliberately asymmetric.

**The Vulture, in the viewer's own units:**

    hardpoint_weapon_nose_left     (-1.306,  0.814,  0.663)
    hardpoint_weapon_nose_right    ( 1.306,  0.814,  0.663)
    hardpoint_salvage_arm_left     (-2.061, -0.666, -5.421)
    hardpoint_salvage_arm_right    ( 2.061, -0.666, -5.421)
    hardpoint_cm_launcher_left     (-1.025,  0.088,  6.170)
    hardpoint_cm_launcher_right    ( 1.025,  0.088,  6.170)

Forward is -Z, so **the salvage heads sit at the front of the booms and the
countermeasures at the tail** — which is what Sleven said the ship looks like
weeks before any of this was readable.

Output: `data-layer/derived/hardpoint-placement/`.

### What is still NOT done

**The frame conversion.** This emits metres in CIG's frame — X lateral, Y
fore/aft, Z up. The viewer is y-up, -Z forward, and each GLB carries its own
unit scale. That mapping is per-hull against that hull's own measured box; there
is no global constant and nothing here pretends there is.

**The fleet.** Two ships is two ships. Each extraction currently re-scans a
464 MB central directory; a batch run needs that index built once.

## Why this matters more than better models

Every marker on the site today is derived from the mount's NAME, snapped to the
nearest hull vertex in a named region. It puts the left wing gun on the left
wing and it cannot put it on the barrel. Sleven has reported that as "the
hardpoints don't line up" for three weeks and he has been right every time.

**No 3D model fixes it** — not ours, not RSI's, not the Fan Kit's. OpenCTM and
single-mesh glTF cannot express a node hierarchy, which was checked and recorded
as a hard no on 2026-08-22. This file can, and does.

## The acceptance test, written before the work

A decode is correct when, for one ship:

- every `hardpoint_*` node yields a finite transform,
- the set is mirror-symmetric about x to within the hull's own 2-3% stray-vertex
  tolerance — **the control that could fail it**, because a wrong stride will
  not produce a symmetric ship,
- and the derived positions land inside the hull's measured bounding box.

A decode that cannot pass all three is not reported as a decode.

---

*C1, 2026-08-27. Scripts: `probe_ship_geometry.py`, `extract_p4k_entry.py`.*
