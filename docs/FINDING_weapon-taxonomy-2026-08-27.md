# FINDING — the weapon taxonomy was already on the machine, in CIG's own files. 948 items, measured. And three of the six damage channels have never been used by anything.

    from      C3 (Cowork), 2026-08-27
    for       C1 + Sleven
    ask       Sleven: "a dive on all the different weapon types, all the different
              weapon sizes, and everything to do with the components and the
              weapons... energy, laser, plasma, ballistic and a whole slew"
    dataset   data-layer/derived/weapon-taxonomy/
    source    scunpacked 20260801T204744Z, ship-items.json. CIG's shipped values.
              Nothing from a wiki. Nothing typed by hand.

---

## 1. This did not need a research job

**The ask was to send CIC out to research weapon types. It should not go.** Every
weapon in the game ships with its own type label, its own class tags, its own
damage channels and its own firing numbers, and all of it is on Sleven's disk
already.

**948 weapon-family items with a real name.** A wiki would be a worse copy of
this, one patch behind, typed by a volunteer.

**One thing genuinely does need an outside source** and it is named in §6.

## 2. CIG's own weapon-class labels — the answer to "what types are there"

Read off `DescriptionData.Item Type`, which is what the game itself shows:

    Laser Cannon 42 · Laser Repeater 38 · Laser Turret 3 · Laser Scattergun 3
    Laser Beam 1 · Laser Gatling 1
    Ballistic Cannon 22 · Ballistic Gatling 20 · Ballistic Scattergun 6
    Ballistic Repeater 4 · Ballistic Gatling Turret 2 · Ballistic Cannon Turret 1
    Distortion Cannon 4 · Distortion Repeater 4 · Distortion Scattergun 3
    Neutron Cannon 4 · Neutron Repeater 3
    Plasma Cannon 1 · Plasma Canon 2   <- see §5, that is CIG's typo, not ours
    Tachyon Cannon 5 · Mass Driver Cannon 6
    Mining Laser 23 · Scraper Module 5 · Salvage Head 2 · Tractor Beam 17
    Missile Rack 106 · Missile Launcher 7 · Missile Turret 1 · Torpedo Rack 8
    Torpedo Launcher 1 · Bomb Rack 10 · Rocket Pod 9
    Anti-Aircraft Turret 48 · Turret 10 · Ball Turret 1 · PDC 1
    Weapon Mount 46 · Gimbal Mount 1

**So the shape is: a damage family, then an action.** Laser, Ballistic,
Distortion, Neutron, Plasma, Tachyon and Mass Driver are the families. Cannon,
Repeater, Gatling, Scattergun and Beam are how they fire. **Most combinations
exist; not all do.**

**465 of the 948 carry no Item Type at all.** Mostly turrets and mounts. Anything
that groups by that field must handle the blank, and 465 is not a rounding error.

## 3. THE FINDING WORTH READING TWICE — three damage channels are dead

Every gun carrying an `ImpactDamage` block declares **six** channels. Measured
across all 185:

    Physical       non-zero on  65 guns
    Energy         non-zero on 107 guns
    Distortion     non-zero on   3 guns
    Thermal        non-zero on   0
    Biochemical    non-zero on   0
    Stun           non-zero on   0

**Thermal, Biochemical and Stun are present on every single gun and used by
none.** They are schema that CIG has not filled in.

**A weapon panel that renders all six channels shows three empty columns
forever** and looks broken on every ship in the game. **Render the three that
carry values.** This is exactly the shape of thing that ships, then gets reported
as a bug, then takes an afternoon to trace.

**And Distortion is nearly as thin** — three guns out of 193. A "distortion
damage" column is technically correct and visually empty 98% of the time.

## 4. Sizes, and what actually exists

Across the whole weapon family:

    size 0    6      size 1  288      size 2  122      size 3  109
    size 4  129      size 5  141      size 6   38      size 7   25
    size 8   16      size 9   35      size 10  30      size 12   9

**There is no size 11.** A size picker built as a range 0-12 offers an empty
slot. Build it from the values present, not from a range.

**Grade is not a differentiator here.** 947 of 948 are grade 1. Whatever grade
means on components, it is not carrying information on weapons.

## 5. A defect in CIG's own data, reported not fixed

`DescriptionData.Item Type` carries **both spellings**:

    "Plasma Canon"    2 items
    "Plasma Cannon"   1 item

**Grouping on that field produces two categories for one weapon class.** It is
CIG's typo in CIG's shipped data. **Do not silently correct it in the pipeline** —
normalise it at display time and record that the raw value differs, so the day CIG
fixes it nothing here breaks.

The `Tags` field is the more reliable key: `PlasmaCannon` is spelled one way on
all four. **Group on tags, label from Item Type.**

## 6. Fire modes, and what is NOT in the files

Four modes exist across 193 guns: **Single 153, Rapid 25, Charge 9, Beam 5.**

**What the files do not contain, and this is the only part of the ask that needs
an outside source:** what the damage types actually DO. The data says a weapon
deals 65 Physical and 0 Energy. It does not say whether Physical is better against
shields or hull, why a pilot picks a repeater over a cannon, or what Distortion is
for.

**That is gameplay meaning, and it belongs to Sleven or to a researched source —
not to this file.** Everything measurable is here; everything interpretive is not.

## 7. What I checked and what I did not

**Checked:** all 5,384 ship-item records, filtering to the 3,137 with a real name
and the 948 in the weapon family; the six damage channels counted across every gun
carrying the block; the size and grade distributions; the two Plasma spellings
confirmed as distinct strings in the source.

**Did NOT check:**
- **Whether the 82 MB star-citizen.wiki items file adds anything.** It is on disk
  and I did not open it for this. If it carries damage-versus-shield multipliers,
  that would answer §6 from data rather than from a wiki article. **Worth an hour
  before anyone is sent to research.**
- **Personal weapons and armour.** The ask said weapons; this covers SHIP weapons
  only. FPS items are a separate 5,420-record file.
- **Whether any of these 948 are actually purchasable.** The price join covers
  55% of ship weapons by distinct name — see `FINDING_uex-price-join-2026-08-16.md`.
- Nothing was built into the site and no page was touched.
