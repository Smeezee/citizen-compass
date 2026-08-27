# ORDER — every component the game has, one ship page, and no opinions. RUN CONTINUOUSLY.

    from    C1, 2026-08-22
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md.
    ruled   Sleven, 2026-08-22. Reference point is Erkul (erkul.games),
              confirmed by him. Erkul does the maths and does NOT have the ship.

---

## 0. THE PRINCIPLE, IN SLEVEN'S WORDS. Read this before the item list.

> "We don't need to name any of these builds... we just have to make it all
> available for them to build anything they want with any type of thing in mind.
> If they wanna take a Hammerhead and max it with racing and agility parts, they
> can. That's their choice if that's what they wanna do. We're just providing all
> the information for them to be able to do it."

**THE PAGE HAS NO OPINION.** No build modes. No presets. No "stealth tab". No
category the player has to pick before they can start. **Every part that fits is
offered, every number that moves is shown, and the player decides which numbers
they care about.**

This is the same rule as the mockup banner and the UEX provenance badge: **state
what is true, do not editorialise.** A page that decides for somebody what kind of
build they are making is a page that has started guessing.

**Sleven's later idea, PARKED, build nothing for it:** a "best build for this
ship" suggestion. His words: *"that can come later with much more research."*
See K10 - it gets written down, not built.

## 1. WHAT WAS MEASURED - the reason this order exists

`ship-items.json` in scunpacked snapshot `20260801T204744Z` holds **5,384 items
across 41 component types**. `loadout_data.gen.js` carries **470 parts across 5
types**. `build_loadout_data.py` trimmed the rest away, not because it does not
exist, but because the page did not render it.

    IN THE BENCH TODAY      202 WeaponGun   88 PowerPlant   81 Cooler
                             73 Shield      63 QuantumDrive

    HELD, NOT EXTRACTED     885 ManneuverThruster   381 MainThruster
                            320 WeaponAttachment    317 Turret
                            238 FlightController    210 Armor
                            188 WeaponDefensive     182 FuelTank
                            155 FuelIntake          150 QuantumFuelTank
                            145 MissileLauncher     143 CargoGrid
                             77 Radar                68 Missile
                             31 ExternalFuelTank     23 WeaponMining
                             22 Container            14 BombLauncher
                             13 LifeSupportGenerator 12 TractorBeam
                             12 JumpDrive             9 SalvageHead
                              9 SalvageModifier       7 EMP
                              7 SelfDestruct          6 QuantumInterdictionGenerator
                              3 Transponder           3 Bomb
                              2 Scanner               1 TowingBeam

`ships.json` also carries CIG's OWN `Career` and `Role` on all 316 ships - 139
Combat, 44 Transporter, 37 Exploration, 25 Industrial, 23 Support, 19
Competition, 12 Multi-Role, 10 Ground. **That is CIG's classification and it is
already in your data.** Use it to describe a ship. **Never to restrict what can
be fitted to it.** §0.

## 2. THE WORK

**K1. EXTRACT EVERY COMPONENT TYPE.** Widen `build_loadout_data.py` from 5 types
to all of them.
**EXCLUDE, and only these:** `Paints` (1,077), the four `Flair_*` types (~159),
and `GroundVehicleMissileLauncher` (8). Paints and flair are cosmetic and belong
with liveries and the acquisition layer, not the performance bench. Ground
vehicle launchers are not ship parts. **That leaves roughly 4,140 parts.**
Carry the fields each type actually needs - a cooler needs cooling and signature,
a cargo grid needs capacity and size limits, a thruster needs thrust and mass.
**Do not carry a field no readout uses.** H1's lesson: 5,566 unused UUIDs were
80% of a file, incompressible by construction.
*Acceptance:* every non-excluded item in the source has a part in the file.
Counts match exactly, asserted.
*Report the gzipped size.* Today's file is 431 KB raw for 470 parts. If the
result is wildly out of proportion, apply H1's test - **a big miss means the
shape changed** - and find out what before shipping it.

**K2. A PART IS OFFERED ONLY IF THE GAME DATA SAYS IT FITS. This is the
load-bearing item in the order.**
With 5 types, `fits` was mostly a size check. With 41 it is not. Ships carry
`PortTags`, `Loadout`, `Parts` and `CargoSizeLimits`; ports accept particular
types and sizes.
**Offering a part that cannot actually be mounted is not a small bug - it is the
page making a false claim**, which is the one thing this project does not do.
*Control, and both halves are required:* a part the data says fits **appears**;
a part the data says does not fit **is absent** - not greyed out, absent.
Assert a named example of each.
*Where the data does not say:* the part is **excluded and the uncertainty is
recorded in the ledger.** Do not guess a port rule. Do not offer it "just in
case".

**K3. THE READOUT SHOWS EVERYTHING THAT MOVES, AT ONCE.**
Not a chosen category. Every measurable output the data supports, all visible,
all showing stock-versus-current:

    damage            dps, and what fits each mount
    signature         em, ir, plus ship Emission and Distortion
    survivability     shield ehp, ShieldHp, Armor, PenetrationMultiplier
    power             pw draw against PowerPlant output and PowerPools
    heat              cool against Cooling
    speed + agility   Main and Manoeuvring thrusters, FlightController,
                      StanceSpeed, and Mass/MassTotal
    cargo             Cargo, CargoGrids, CargoSizeLimits, Container
    range             QuantumDrive, QuantumFuelTank, FuelTank, FuelIntake
    detection         Radar, Scanner
    industrial        WeaponMining, SalvageHead, SalvageModifier
    crew              Crew, Seating, Seats, LifeSupportGenerator

**MASS IS A REAL COUPLING AND MUST NOT BE DROPPED.** Fitting heavier parts
changes `MassTotal`, which changes agility. **That coupling is exactly what makes
Sleven's Hammerhead-full-of-racing-thrusters example interesting**, and a readout
that ignores it would quietly lie about the result.
*Control:* one swap moves at least two unrelated readouts in opposite directions,
observed and named in the ledger.

**K4. EXTRACT THE 3D VIEWER. ONE implementation, shared.**
It lives in `index.html`; the ship page needs the same one. **Two copies of a
Three.js viewer guarantees drift** - one gets a fix, the other does not, nobody
notices for months. Two concrete consumers exist now, so this satisfies the
standing 2-3-cases rule rather than pre-empting it.
*Control:* the same ship renders identically on both pages - same model, same
markers, same count, asserted not eyeballed.
*Negative half:* break the shared module deliberately and confirm **BOTH** pages
fail. If only one fails, there is a second copy somewhere.

**K5. THE SHIP PAGE = THE BENCH PLUS THE MODEL. Do not build a third page.**
`loadout.html` is already per-ship, already does A/B, already shares by URL. It
is missing the model. **Add the model to it.**
*Rejected - a new `ship.html`:* three places rendering ships instead of two.
*Rejected - merging into `index.html`:* it is already ~10,000 lines and the ship
would still have no URL of its own.
*Control:* swap a part; the model stays loaded and the readout changes.

**K6. CLICK A HARDPOINT ON THE HULL, SWAP THAT MOUNT. This is the item Erkul
cannot copy.** A marker selects the hardpoint it belongs to and opens the picker
for that mount, filtered by K2.
*Control:* clicking marker N selects hardpoint N and no other - assert by
identity, never by screen position.
**Markers stay weapons-only.** Physically visible and mountable - weapons,
turrets, missile racks. Internal components use the menu overlay. **Settled
design, do not re-litigate.**
*25 ships have no mount data.* Those say so plainly and menu swapping still
works. **Never a spinner. Never an empty hull shown as a complete one.**

**K7. THE SHIP NAME LINKS TO THE SHIP PAGE**, not to RSI. **The RSI link moves
ONTO the ship page and stays clearly available.** It does not disappear.
Sending somebody off-site the moment they click a name means they never see what
was built for them.
*Control:* every ship name in the list resolves to a page that loads.

**K8. THE SHARE LINK CARRIES THE WHOLE BUILD.** `writeHash`/`readHash` already
share a build; it must survive and now cover the ship and every fitted type.
*Control:* paste a shared URL into a clean session and get the same build back,
model and all.

**K9. PROVENANCE SURVIVES.** `loadout_data.gen.js` distinguishes **CIG's own
precomputed stock aggregate** from **anything summed from parts**, and says which
is which. **That distinction must not be lost when the layout changes** - it is
the difference between reporting and asserting. Same for `last_verified_patch`
4.9 and the 33 unreleased ships.
*Control:* a CIG-sourced stat and a computed stat are visibly different on the
rendered page.

**K10. WRITE THE PARKED IDEA DOWN. BUILD NOTHING FOR IT.**
`docs/IDEA_recommended-builds.md`. Sleven's "best build for this ship" idea, why
it is parked, and **what it would require** - a defined objective per build type,
a source for what "best" means, and a way to keep it current across patches.
**Note the tension plainly: a recommendation is an opinion, and §0 says this page
does not have opinions.** That is not a reason to refuse it later; it is the
thing to design around when it is picked up.

**K11. THE PRE-LIVE PUNCH LIST.** `docs/PRE-LIVE-PUNCH-LIST.md`, maintained, not
a one-off. Every page, every dataset, every place the site says "not yet" or
shows an empty state, **with a number**, and whether it blocks going live.
Measured starting points: **25 ships with no mount data, 8 refused by the
alignment gate, 21 `unchecked_hull`** (was 7 - the G3 geometry rebuild recovered
twelve models now borrowing base-ship mount data nothing verified), **9 price
categories with items and no prices**, keybind modes and devices the page dims,
**and the four careers with no component behind them** - Medical (16 ships),
Passenger, Repair, Construction. Those are hull properties, not builds. **The
site should say so rather than offer a control that does nothing.**
**Then bring `docs/CURRENT-STATE.md` back in line.** It was last written
2026-08-16 and predates the shop layer, FIND, the guard inversion and the
collector build. **A five-day-stale state document is why nobody could say what
was left.**

**K12. SWEEP.** Every control in `checks/`.

## 3. WHAT MUST NOT HAPPEN

- **Do not add build modes, presets, or categories.** §0.
- **Do not restrict what fits a hull by its CIG Career or Role.** §1.
- **Do not offer a part the data does not say fits.** K2.
- **Do not drop mass from the agility maths.** K3.
- **Do not build a second 3D viewer.** K4.
- **Do not build a third ship page.** K5.
- **Do not put 3D markers on internal components.** K6.
- **Do not remove the RSI link.** K7. It moves.
- **Do not lose the CIG-versus-ours distinction.** K9.
- **Do not build recommended builds.** K10.
- **Do not deploy the live site. Do not cut a release.**
- **Do not `git add -A`. Push at the end.**

## 4. REPORT

- Part count and gzipped size after K1, against today's 470 / 431 KB.
- The K2 examples: one part proven to fit, one proven absent, both named.
- The K3 case in words: one swap, two readouts moving opposite ways.
- Whether breaking the shared viewer module broke both pages.
- The punch list, and what on it you think actually blocks going live.
- Anything here you think is wrong. **K2 is the part most worth arguing with** -
  if the game data turns out not to express port rules cleanly enough to decide
  what fits, **say so early and loudly**, because everything the page claims
  rests on it.
