# FINDING — JOB 2. The mount-name vocabulary across all 316 ships. The names are better than expected and the checklist is still not safe, for a reason that is measurable.

    from      C3 (Cowork), 2026-08-08
    for       C1 + Sleven (→ Code)
    ask       C1: "walk every Loadout[].Path across all 316 and produce the vocabulary...
              The ambiguous tail is the deliverable."
    method    Walked every Loadout[] entry in ships.json 20260801T204744Z. 57,759 entries
              carry a Path; zero lack one. Narrowed to externally-mounted hardware, then
              measured rather than eyeballed. Placed no hardpoints and produced no data.

---

## 0. Headline

**Every placeable mount has a real name. Not one is nameless.** The "0 · no name at all"
bucket came back empty — there is no mount whose only identity is its size.

**But 63.6% of placeable mounts sit in a group where two or more mounts on the SAME ship
share one name.** A checklist built on names alone would, for most ships, show the operator
several identical rows and no way to tell which is which. **That is the finding.** The problem
is not that names are missing or vague — it is that they are not unique within a hull.

## 1. Scope — what counts, and what got excluded

    57,759   Loadout[] entries carrying a Path (0 without)
     5,087   distinct path segments across all of them
     4,878   externally-mounted hardware = 8.4% of the above
     1,436   distinct full paths among those
       727   distinct segments among those
     1,043   distinct EFFECTIVE names (path minus generic hardpoint_class_N segments)

The other 91.6% is seats, dashboards, displays, doors, relays, decals, fuses, light groups and
thruster ports — real data, but not things anyone walks up to and points at. Excluded per the
standing decision that only physically visible/mountable hardware gets hull markers.

Included types: WeaponGun, Turret, MissileLauncher, WeaponDefensive, WeaponMining,
BombLauncher, GroundVehicleMissileLauncher, TractorBeam, SalvageHead, EMP,
QuantumInterdictionGenerator, Scanner.

**`hardpoint_class_2` alone occurs 1,323 times among placeable mounts** — it states size, never
place, and is always the innermost segment. It is the reason the parent Path matters: strip it
and the segment above almost always carries the location.

## 2. How well do the names state a position? Measured, not guessed

    161  ( 3.3%)  no position and no part named
    235  ( 4.8%)  a part only  — "turret", "remote turret", "mining arm"
  1,359  (27.9%)  one axis only, no part — "left", "top", "rear"
  1,395  (28.6%)  one axis + a part — "left wing weapon", "gunmount left"
  1,728  (35.4%)  two or more axes — "turret lower left", "left aft countermeasure"

**Roughly two thirds (64%) name a part or two axes and are genuinely actionable.** The 27.9%
one-axis-only band is the awkward middle: `hardpoint_weapon_left` tells you which side and
nothing else — left wing, left nose or left body are all consistent with it.

## 3. THE AMBIGUOUS TAIL — three distinct kinds, and only one is fatal

### 3a. Within-ship collisions — this is the one that breaks a checklist

**1,311 colliding name-groups across 228 of the 275 armed ships. 3,104 of 4,878 mounts
(63.6%) sit in one.** Worst cases:

    8x  RSI Apollo Medivac    hardpoint_turret / hardpoint_weapon_left
    8x  RSI Apollo Medivac    hardpoint_weapon_left
    8x  Grey's Shiv           hardpoint_Right_Body_Weapon
    8x  Grey's Shiv           hardpoint_turret / hardpoint_weapon_top_left

Eight mounts on one hull, one name between them. **The data does not distinguish them at all** —
not by index, not by suffix, nothing. A placement tool cannot ask "place the left turret gun"
when there are eight and the file cannot tell them apart.

**This is not solvable from the names, ever.** It has to be solved by the tool: present the
group, let the operator place N markers against it, and record which is which by placement
order. **The names are a guide to the region, not a unique key.** Anyone building the checklist
on the assumption that name ⇒ one position will produce a tool that silently mislabels most
multi-turret ships.

### 3b. Cross-ship reuse — looks alarming, is mostly fine

    71 ships  hardpoint_countermeasure_launcher_left / _right
    56 ships  hardpoint_weapon_left / _right
    53 ships  hardpoint_countermeasures_left / _right
    25 ships  hardpoint_missile_rack_left / _right

One name meaning a different physical place on 71 different hulls. **This is only a problem if
positions are ever shared between ships — and they must not be**, since each hull's geometry is
its own. Recorded so nobody later tries to build a cross-ship position library keyed on mount
name. Positions belong to (ship, mount), never to mount alone.

### 3c. Names that carry a part but no side — the quiet 4.8%

`hardpoint_turret` appearing 26 times, `hardpoint_remote_turret` 5, `hardpoint_turret_mount` 5.
On a single-turret ship this is unambiguous. On a multi-turret ship it collapses into 3a. Not
separately fatal, but it is where 3a comes from.

## 4. Normalisation — and a correction to my own first attempt

**Collapsing spelling variants works and is worth doing.** 1,043 distinct effective names
reduce to **869 canonical families; 128 families hold more than one spelling, covering 49.4%
of all placeable mounts.** The largest families:

    "countermeasure, right"   211 mounts, SIX spellings:
        hardpoint_countermeasure_launcher_right   76
        hardpoint_countermeasures_right           57
        hardpoint_countermeasure_right            49
        hardpoint_cm_launcher_right               20
        Hardpoint_Countermeasure_Right             6
    "weapon, left"            154 mounts: hardpoint_weapon_left 124 · hardpoint_gun_left 30
    "weapon, left wing"        96 mounts, FIVE spellings:
        hardpoint_weapon_wing_left 34 · hardpoint_weapon_left_wing 30
        hardpoint_Left_Wing_Weapon 18 · hardpoint_gun_left_wing 8 · hardpoint_gun_wing_left 6

**Safe collapses, and why:** `countermeasures`→`countermeasure`→`cm`; `gun`→`weapon`;
`upper`→`top`, `lower`→`bottom`; case differences (`Hardpoint_Countermeasure_Right` is the same
place as its lowercase twin); zero-padding (`_01`→`_1`); and word-order variants within a single
segment (`wing_left` = `left_wing`).

### The collapse I got wrong, found by testing it

My first canonical form **sorted tokens across the whole path**. That merges two genuinely
different places:

    hardpoint_turret / hardpoint_gunmount_left        the LEFT GUN of one turret
    hardpoint_remote_turret / turret_lower_left       the gun of the LOWER-LEFT TURRET
    hardpoint_turret_nose_left_lower / hardpoint_weapon_left   BOTH at once (Aegis Javelin)

Measured across the data:

      863 mounts  the side is on the TURRET segment      (which turret)
      429 mounts  the side is on the WEAPON segment      (which gun within a turret)
      316 mounts  BOTH segments carry a side

**So 429 mounts would be mislocated by cross-segment sorting, and 316 more would lose half
their meaning.** The fix is simple and must be stated: **normalise within each path segment,
never across segments, and keep segment order.** A canonical form that flattens
`turret → weapon_left` into one bag of words is wrong, and it is wrong on 745 real mounts.

I am reporting this rather than quietly fixing it because the flawed version produced a
perfectly plausible-looking family list — the same failure shape as the pilot-weapon default
earlier today.

### One collapse checked and proven safe by absence

`port`→`left` / `starboard`→`right` is standard nautical, but `port` also means "item port" in
this data (`RightHandWeapon_ItemPort`). **Checked: zero segments contain a standalone `port`
token. The collapse never fires.** Safe, and safe for a verifiable reason rather than a hopeful
one.

## 5. Mounts per ship — and the worst case, which is worth knowing before starting

    ships with at least one placeable mount   275 of 316
    median                                     12
    mean                                       17.7
    maximum                                   214

    Aegis Idris-P              214        Grey's Shiv                 84
    RSI Polaris                154        Aegis Idris-P Wikelo        80
    Aegis Hammerhead           120        Aegis Idris-M               78
    Vanduul Mauler Destroyer    91        RSI Perseus                 65

**The Cutlass Black's 21 is not typical — it is nearly double the median.** Most ships are a
12-mount job. **The Idris-P is 214 and will take as long as roughly eighteen median ships.**

**41 of 316 ships have no placeable mounts at all** — the ATLS variants and similar. The
placement tool needs a defined empty state for those; several are paint variants that differ
from their base only cosmetically.

## 6. Recommendation

1. **Do not build the checklist on the assumption that a name identifies one position.** It
   does so for barely a third of mounts. Group by name, place N markers per group, record
   order.
2. **Normalise within segments, never across them.** §4 gives the safe list and the count of
   mounts that cross-segment sorting would break.
3. **Key positions on (ship, mount), never on mount name alone** — §3b.
4. **Show mount count before the operator starts.** "This hull has 214" is information someone
   needs in advance, not after twenty minutes.
5. **Start with median ships to prove the tool**, not the Cutlass and certainly not the Idris.
6. Worth considering: sort the checklist so unambiguous mounts come first, so the easy 36%
   is done before anyone meets a collision group.

## 7. What I checked and what I did not

**Checked:** all 316 ships; every `Loadout[]` entry with a `Path`; segment and family counts
computed, not sampled; both risky collapses tested against the data rather than assumed;
mount-per-ship distribution computed across all 275 armed hulls.

**Did NOT check, and these are real gaps:**

- **Whether mount names correspond to anything in the 3D geometry.** They almost certainly do
  in CIG's own source, but our `.ctm`/`.glb` models are merged meshes with no node hierarchy
  (verified earlier today), so **there is no way to confirm a name against the model from data
  we hold.** The names remain unvalidated against physical reality.
- **The 41 unarmed ships** were counted but not examined; I did not confirm every one is
  legitimately unarmed rather than a parsing miss on my side.
- **Non-weapon mounts** (thrusters, intakes, coolers) were excluded by the standing decision,
  not because their names are bad. If internal components ever want markers, that vocabulary
  is unmeasured.
- Did not verify my `PLACEABLE` type list against anyone else's definition — if Code's viewer
  includes a type I excluded, the counts shift.
- Placed no hardpoints. Produced no position data. Nothing in this document is a coordinate.
