# FINDING — the 3D viewer and the loadout bench can be one page. The join is 100%, with zero misses, and every stat a swap tool needs is already on disk.

    from    C1, 2026-08-13
    status  MEASURED, not argued. Every number below came out of
              `hardpoints_fleet.json`, `ships.json` and `ship-items.json` on
              Sleven's machine, this session.
    asked   Sleven: "are you gonna put the ship components into the 3D modeled
              section to where we'll be able to swap components and weapons and
              be able to see the performance gain or loss or DPS gain or loss...
              kinda like how the other DPS calculator tool is"

    ANSWER: yes, and it is cheaper than anyone assumed. The expensive part —
    proving the two datasets describe the same mounts — is done and it is exact.

---

## 1. The headline

```
holo ships  ->  ships.json          167 / 167   100%
holo ports  ->  Loadout HardpointName   1798 / 1798   100%   ZERO misses
```

**Every hardpoint marker on every hull in the viewer resolves to a real slot in
that ship's loadout tree.** Not 94%, not "with a long tail" — exact, across the
whole fleet.

This was the open risk. `hardpoints_fleet.json` positions are *derived* (mount
name vocabulary + hull geometry, because CIG's own `position` field is null for
all 53,651 mounts), while `Loadout[]` comes straight from the game files. They
had no shared provenance and nobody had checked whether they agreed on which
mount is which. **They agree completely.**

**So the merge is plumbing, not research.** Click a marker on the hull → you
already know exactly which loadout slot that is.

### One methodology note, because it nearly produced a false answer

The first ship-key pass matched only 138/167 and reported 29 "unmatched" — the
Hornet variants, the Spirits, the Dragonfly. That was **not** a data problem:
`hardpoints_fleet.json` keys some ships by display name ("F7A Hornet Mk I") and
others by class stem ("100i"). Adding a lookup on `ships.json`'s own `Name`
field took it to 167/167. **Anyone re-running this must index on ClassName,
ClassName-minus-manufacturer, Name, AND Name-minus-manufacturer**, or they will
conclude 29 ships are missing when none are.

## 2. What the loadout tree actually is

`Loadout[]` is **nested, not flat.** This is the thing that will trip up the
next person, because it tripped up this session:

```
depth 0   14099    the root ports on the hull
depth 1   11289    what is fitted INTO them
depth 2    2511
depth 3    1448
--------------------
total     29347 entries over the 167 holo ships
          18537 fitted (carry a ClassName)
          10810 empty ports
```

**A shallow read of `Loadout[]` finds 14 pilot guns and 260 turrets and looks
wrong.** It is not wrong — it is incomplete. The guns hang *inside* the gimbal
mounts. Worked example, Origin 100i:

```
hardpoint_weapon_gun_right      Mount_Gimbal_S3   "VariPuck S3 Gimbal Mount"   Turret.GunTurret
  \]_ hardpoint_class_2        KLWE_LaserRepeater_S3   "CF-337 Panther Repeater"   WeaponGun.Gun
         |- BAR1   (barrel,     not editable)
         |- MEC    (mechanism,  not editable)
         |- POW    (power,      not editable)
         \\- VEN    (ventilation, not editable)
```

The holo marker points at the **mount**. The swappable gun is **one level down**.
Recurse, or you will build a weapon picker that cannot see any weapons.

## 3. What is swappable, and where it lives

**13,300 editable slots** across the 167 ships. **12,601 of them (94.7%) carry
`CompatibleTypes`**, which is what lets a picker say "this slot takes an S3
WeaponGun" rather than offering the player everything. Every single entry
carries `MinSize` and `MaxSize` — 14,099 of 14,099, no exceptions.

Split by whether a hull marker can reach them:

**REACHABLE FROM A 3D CLICK — 3,324 editable slots**

```
1245  Missile
 702  WeaponGun          <- the pilot guns. This is the DPS tool.
 636  (empty port)
 359  Turret
 157  MissileLauncher
 131  Display
  34  Usable
  13  TractorBeam
```

**NOT ON THE HULL, needs the menu overlay — 9,976 editable slots**

```
5419  (empty port)
1589  Display
 958  Misc
 291  ControlPanel
 284  Shield
 284  Cooler
 209  PowerPlant
 160  Radar
 131  QuantumDrive
 131  JumpDrive
  77  FlightController
```

**This maps exactly onto the standing design decision** — physically visible
mounts get hull markers, internal components get a menu-driven overlay. That
decision was made on gameplay grounds ("you don't walk up to a power plant") and
the data independently agrees with it: the internals are precisely the slots no
hardpoint marker reaches. **Nothing needs re-litigating.**

## 4. Every stat a swap tool needs is present

`ship-items.json`, 5,384 records. Candidate pools and stat coverage:

| slot type | items | with usable stats | source key |
|---|---|---|---|
| WeaponGun | 202 | **197** | `Weapon` |
| Turret | 317 | **306** | `Turret` |
| WeaponDefensive | 188 | **188** | `Weapon` |
| Shield | 73 | **73** | `Shield` |
| QuantumDrive | 63 | **63** | `QuantumDrive` |
| Radar | 77 | **77** | `Radar` |
| Missile | 68 | **67** | `Missile` |
| PowerPlant | 88 | **84** | `ResourceNetwork` |
| Cooler | 81 | **81** | `ResourceNetwork` + `Emission` |
| MissileLauncher | 145 | **145** | `MissileRack` |

### The three that looked like gaps and are not

A first pass reported PowerPlant, Cooler and MissileLauncher at **zero**. That
was wrong and it is worth writing down why, because the same shape will recur:
**those three do not carry a stat block named after themselves.**

- **PowerPlant** → `ResourceNetwork`, e.g. `Generation / Power / Rate: 32`.
  84 of 88 (the 4 misses are literal `<= PLACEHOLDER =>` records).
- **Cooler** → `ResourceNetwork` as a *conversion*: `Power 3 -> Coolant 38`, plus
  `Emission` (`Em.Maximum 1490`, `Ir 7920`). 81 of 81.
- **MissileLauncher** -> `MissileRack { MissileCount }`. 145 of 145.

**Nothing is missing.** Anyone auditing coverage by "does it have a block named
after its type" will report three false gaps.

Weapon records carry `RateOfFire`, `EffectiveRange`, `Capacity`, firing `Modes`,
and an `Attachments` list (barrel, mechanism, power array, ventilation). The
attachment ports exist and are marked **not editable**, so the tool should show
them and not offer to change them.

## 5. Do not invent the maths

`docs/FINDING_ship-aggregation-rules-proven-2026-08-08.md` already proves the
formulas against CIG's own precomputed values:

- **Shields** — top-2-generator redundancy cap, **267/267 exact**
- **DPS** — the `IsPilotSlaveable` outermost-lock rule, **275/275 exact** against
  CIG's own `PilotDps`
- **Power** — 10 of 11 categories at 100%

And `ships.json` publishes `ShieldsTotal`, `Power`, `Cooling`, `Emission` by
contributing group, and `Distortion.Pool` for the stock fit. **The stock numbers
are free; only the deltas from a swap need computing, with rules that are already
proven.** `hardpoints_fleet.json` even carries `pilot_dps` and `pilot_alpha`
per ship already (100i: 1091.2 / 87.4).

Still open from that finding and therefore still open here: WeaponGun's power
residual, Cooling in Quantum mode, and Emission/Distortion. Report them as
unknown rather than guessing.

## 6. What this means for the build

**The merge is not a research project.** In order:

1. **Tonight's loadout order lands first** — it wires the bench to real data and
   proves the swap/compare maths across 316 ships. Nothing here changes it.
2. **Then the merge is: hull marker -> loadout slot -> picker.** The join key is
   `HardpointName`, already exact. The A/B compare, ghost preview and delta
   display already exist on the loadout page and do not need rebuilding.
3. **Internals stay a menu**, as already decided — and the data confirms that is
   the only option, since no marker reaches them.

**What Citizen Compass would have that the existing DPS calculators do not:**
they have the numbers; nobody has the numbers *on the hull*. Clicking the actual
wing mount on the actual model and watching DPS move is the differentiator, and
the measurement above says it is reachable.

## 7. Honest limits

- **167 ships have hardpoints, 235 models are deployed.** ~68 models have no
  hardpoint data yet — the merge covers 167 until that gap closes.
- **Positions remain derived**, not CIG's. Left/right handedness is still an
  assumption with a Mirror control, because the hulls are mirror-symmetric and
  nothing in them confirms it. The panel says so and must keep saying so.
- **699 editable slots have no `CompatibleTypes`** (5.3%). A picker cannot be
  populated for those from this data alone. Small, but it should say "we don't
  know what fits here" rather than showing an empty list.
- **This proves the data supports the feature. It does not prove the feature is
  built.** Nobody has rendered a swap through this path yet.
