# ORDER — the ship page: every component shown, swappable only where the game says so. RUN CONTINUOUSLY.

    from    C1, 2026-08-22
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md.
    ruled   Sleven, 2026-08-22. Reference is Erkul (erkul.games), confirmed.
              Erkul does the maths and does NOT have the ship.

    NOTE    This order REPLACES the unstarted
              inbox/ORDER_every-component-and-the-ship-page-2026-08-22.md.
              That one told you to extract 41 component types. **It was wrong**
              and the measurements in §2 are why. Delete it or ignore it; do not
              work from both.

---

## 0. THE PRINCIPLE - Sleven's words, and everything follows from it

> "We don't need to name any of these builds... we just have to make it all
> available for them to build anything they want with any type of thing in mind.
> If they wanna take a Hammerhead and max it with racing and agility parts, they
> can. That's their choice... We're just providing all the information for them
> to be able to do it."

**THE PAGE HAS NO OPINION.** No build modes, no presets, no category anyone picks
before they can start. Every part the game allows is offered, every number that
moves is shown, the player decides what matters.

**And its exact limit, which §2 found the hard way: the page offers what the GAME
allows, not what the data merely contains.** Those are different, and confusing
them would make the page lie.

## 1. THE DATA ANSWERS ALL OF THIS. Stop guessing about loadouts.

Every entry in a ship's `Loadout` in `ships.json` carries:

    Editable          can the player change this port - TRUE/FALSE
    EditableChildren  can its children be changed
    CompatibleTypes   exactly which types this port accepts
    MinSize / MaxSize the size window
    ClassName         the component fitted by default  <- the stock loadout
    HardpointName     the port's identity
    PortId/RootPortId/Path   where it sits in the tree

**So swappability, fitment, size and the stock build are all stated per port, per
ship.** Read them. Do not infer them, do not hardcode them, do not carry a list
of "types we think are swappable" anywhere in the code.

## 2. THE MEASUREMENT THAT REWROTE THIS ORDER

**RULE: EDITABILITY IS PER PORT, PER SHIP. NEVER PER COMPONENT TYPE.**

C1 measured `Editable` across all 316 ships. The by-type view is useful context
and is **NOT a rule you may apply**:

    Missile          2468 editable /   28 fixed
    WeaponGun        1428 /  210        Turret         754 / 1029
    Shield            529 /   33        Cooler         524 /   14
    PowerPlant        392 /   20        MissileLauncher 371 /  296
    Radar             295 /   28        QuantumDrive   253 /    4
    JumpDrive         247 /    5        FlightController 136 / 140
    CargoGrid          71 /  474        Container       54 /   86
    TractorBeam        23 /   18        ExternalFuelTank 20 /    0
    WeaponMining       18 /    5        Bomb            18 /    0
    SalvageHead        15 /    3        LifeSupport     72 /  206

    EFFECTIVELY FIXED - do not build pickers for these:
    ManneuverThruster  32 / 4683        MainThruster     8 / 1060
    WeaponAttachment   35 / 1162        WeaponDefensive  4 /  664
    Armor               0 /  305        FuelTank         0 /  436
    FuelIntake          0 /  539        QuantumFuelTank  0 /  261
    SalvageModifier     0 /   34        BombLauncher     0 /    5

**WHY THE PER-TYPE VIEW IS BANNED AS A RULE, and this is Sleven's catch:**
plain `FuelTank` is 0-editable across 436 ports, so "fuel is fixed" looks safe.
**It is false.** `ExternalFuelTank` is **20 editable and 0 fixed - every one on a
Starfarer.** A refuelling ship's fuel pods are the entire point of the ship.
Same shape for mining: `Container` is 54/86, editable on the ARGO MOLE and the
ATLS - **the mining bags** - and fixed elsewhere.

**A by-type rule breaks the industrial ships first, which are exactly the hulls
where loadout choice matters most.** Read the port.

**TWO THINGS C1 GOT WRONG, corrected here so you do not inherit them:**
thrusters and armour are **not** meaningfully swappable - 32 of 4,715 manoeuvring
thrusters, 8 of 1,068 main, 0 of 305 armour. An earlier draft had you extract
1,504 thruster records to fill pickers nobody can use. **Do not.**

## 3. THE WORK

**K1. WIDEN THE PART CATALOGUE - driven by the data, not by a list.**
Extend `build_loadout_data.py` beyond today's 5 types (470 parts).
**Derive which types to carry by scanning every ship's `Loadout` for ports where
`Editable` is true, and carrying exactly those types.** Do not hand-write the
list from §2 - §2 is context; the scan is the source. When CIG changes a port,
the next generation picks it up with no code change.
**Excluded regardless:** `Paints` and the four `Flair_*` types - they go to K6
instead - and `GroundVehicleMissileLauncher`, which is not a ship part.
Carry the fields each type's readout actually uses. **Do not carry a field no
readout reads** - H1's lesson: 5,566 unused UUIDs were 80% of a file.
*Acceptance:* every type with at least one editable port anywhere has parts in
the file. Counts asserted against the source.
*Report the gzipped size* against today's 431 KB.

**K2. THE STOCK LOADOUT COMES FROM THE SHIP'S OWN DEFAULTS.**
A ship opens with what `ClassName` says is fitted at each port - not empty, not a
best guess. `stockBuild` exists; point it at the real defaults.
*Control:* a named ship's opening state matches its `Loadout` entries exactly,
port for port.

**K3. EVERY SLOT IS CLICKABLE. ONE INTERACTION, EVERYWHERE. Sleven's ruling.**
Weapons, coolers, shields, power plants, quantum drives, radar, mining heads,
salvage heads, containers, external fuel tanks - **a slot with a hull marker and a
slot without behave identically when clicked.** A scrollable window opens listing
**every component that fits that port on that ship, by name.**
*What is offered comes from `CompatibleTypes` + `MinSize`/`MaxSize` on THAT port.*
**Offering a part that cannot be mounted is the page making a false claim**, which
is the one thing this project does not do.
*Control, both halves required:* a part the port accepts **appears**; a part it
does not accept **is absent** - not greyed, absent. Name one of each.
*Where the data does not say:* exclude it and record the uncertainty in the
ledger. **Never guess a port rule.**

**K4. A FIXED PORT IS SHOWN, NOT HIDDEN, AND NOT CLICKABLE.**
`Editable: false` means no picker - it does not mean invisible. The fuel tank
still counts toward range and still appears in the readout, **because it is part
of the ship.** Say plainly that it cannot be changed.
**`Editable` is a per-patch fact and carries `last_verified_patch`, exactly like
a price.** Sleven believes more ports become swappable later. **When that
happens it must be a data change, not a code change.**
*Control:* a fixed port renders, contributes to the totals, and does not open a
picker when clicked.

**K5. THE READOUT SHOWS EVERYTHING THAT MOVES, AT ONCE** - not a chosen category.
Damage; signature (em, ir, ship Emission and Distortion); survivability (shield
ehp, ShieldHp, Armor, PenetrationMultiplier); power draw against PowerPlant
output and PowerPools; heat against Cooling; cargo; quantum and fuel range;
detection; mining and salvage; crew and life support. Stock versus current on
each.
**MASS IS A REAL COUPLING AND MUST NOT BE DROPPED** - fitted parts change
`MassTotal`, which changes handling. Since thrusters are fixed (§2), **mass is
the main lever a player still has over agility**, which makes it more important
here, not less.
*Control:* one swap moves at least two unrelated readouts in opposite directions.
Name it in the ledger.

**K6. LIVERIES LIVE ON THE SHIP PAGE. Sleven: if it is part of a ship, it stays
with the ship.**
All 1,077 paints carry `required_tags` tying each to its hull
(`Paint_Hornet_F7_Mk2` -> Hornet Mk II), plus `manufacturer` and `event_source` -
how it was obtained. **List every livery that exists for the hull, its proper
name, and how you get it.** This is the acquisition-routes model already ruled in
`DECISION_hull-configuration-acquisition-2026-08-16.md`, not a new one.
**DO NOT RENDER LIVERIES ON THE 3D MODEL.** The data carries names and colour
words in a class name, **not textures or materials**. And tinting the model to
approximate one is already ruled out - CIG assets may not be recoloured. **Build
the honest section now; if a real texture source appears, it plugs into a section
that already exists.**
**Liveries take no part in the performance readout.**

**K7. EXTRACT THE 3D VIEWER. ONE implementation, shared.**
It lives in `index.html`; the ship page needs the same one. **Two copies of a
Three.js viewer guarantees drift.** Two concrete consumers exist now, so this
satisfies the standing 2-3-cases rule rather than pre-empting it.
*Control:* the same ship renders identically on both pages - same model, same
markers, same count. Asserted.
*Negative half:* break the shared module and confirm **BOTH** pages fail. If only
one fails, there is a second copy somewhere.

**K8. THE SHIP PAGE = THE BENCH PLUS THE MODEL. Do not build a third page.**
`loadout.html` is already per-ship, already does A/B, already shares by URL. It
is missing the model. Add it.
*Rejected - a new `ship.html`:* three places rendering ships instead of two.
*Rejected - merging into `index.html`:* already ~10,000 lines, and the ship still
gets no URL of its own.
*Control:* swap a part; the model stays loaded and the readout changes.

**K9. A HULL MARKER IS A SECOND ROUTE TO THE SAME PICKER, not a second
mechanism.** Clicking the gun on the model and clicking it in the list open the
identical window. **This is the item Erkul cannot copy.**
*Control:* marker N selects port N and no other - assert by identity, never by
screen position.
**Markers stay weapons-only** - visible, mountable hardpoints. Internal ports are
reached from the list. Settled; do not re-litigate.
*25 ships have no mount data.* They say so plainly and list-driven swapping still
works. **Never a spinner. Never an empty hull shown as complete.**

**K10. THE SHIP NAME LINKS TO THE SHIP PAGE**, not to RSI. **The RSI link moves
ONTO the page and stays clearly available.** It does not disappear.
*Control:* every ship name in the list resolves to a page that loads.

**K11. THE SHARE LINK CARRIES THE WHOLE BUILD** - ship and every fitted port.
*Control:* paste a shared URL into a clean session and get the same build back,
model and all.

**K12. PROVENANCE SURVIVES.** The generated data distinguishes **CIG's own
precomputed stock aggregate** from **anything summed from parts**, and says
which is which. **That must not be lost when the layout changes** - it is the
difference between reporting and asserting. Same for `last_verified_patch` 4.9
and the 33 unreleased ships.
*Control:* a CIG-sourced stat and a computed stat are visibly different on the
rendered page.

**K13. WRITE THE PARKED IDEA DOWN. BUILD NOTHING.**
`docs/IDEA_recommended-builds.md` - Sleven's "best build for this ship" idea, why
it is parked (*"that can come later with much more research"*), and what it would
need: a defined objective per build type, a source for what "best" means, and a
way to keep it current across patches. **Name the tension plainly - a
recommendation is an opinion and §0 says this page has none.** That is what to
design around when it is picked up, not a reason to refuse it.

**K14. THE PRE-LIVE PUNCH LIST.** `docs/PRE-LIVE-PUNCH-LIST.md`, maintained.
Every page, every dataset, every place the site says "not yet" or shows an empty
state, **with a number**, and whether it blocks going live. Measured starts:
**25 ships with no mount data, 8 refused by the alignment gate, 21
`unchecked_hull`** (was 7 - the G3 geometry rebuild recovered twelve models now
borrowing base-ship mount data nothing verified), **9 price categories with items
and no prices**, keybind modes and devices the page dims, **the ports that are
fixed today and expected to become editable**, and **the four careers with no
component behind them** - Medical (16 ships), Passenger, Repair, Construction.
Those are hull properties, not builds; **say so rather than offer a dead
control.**
**Then bring `docs/CURRENT-STATE.md` back in line** - last written 2026-08-16,
predating the shop layer, FIND, the guard inversion and the collector build.
**A five-day-stale state document is why nobody could say what was left.**

**K15. SWEEP.** Every control in `checks/`.

## 4. WHAT MUST NOT HAPPEN

- **Do not apply editability by component type.** §2. Read the port.
- **Do not build pickers for thrusters, armour, plain fuel tanks or intakes.** §2.
- **Do not hide fixed components.** K4. They are part of the ship.
- **Do not offer a part the port does not accept.** K3.
- **Do not add build modes, presets or categories.** §0.
- **Do not restrict what fits by a ship's CIG Career or Role.**
- **Do not drop mass from the handling maths.** K5.
- **Do not render liveries on the model.** K6.
- **Do not build a second 3D viewer.** K7. Or a third ship page. K8.
- **Do not remove the RSI link.** K10. It moves.
- **Do not build recommended builds.** K13.
- **Do not deploy the live site. Do not cut a release.**
- **Do not `git add -A`. Push at the end.**

## 5. REPORT

- Which types the K1 scan selected, and the gzipped size against today's 431 KB.
- K3's two named examples: one part proven offered, one proven absent.
- The K5 case in words: one swap, two readouts moving opposite ways.
- Whether breaking the shared viewer module broke both pages.
- The punch list, and what on it you think blocks going live.
- Anything here you think is wrong. **K3 is the part most worth arguing with** -
  if `CompatibleTypes` and the size window turn out not to decide fitment cleanly,
  **say so early and loudly**, because everything this page claims rests on it.
