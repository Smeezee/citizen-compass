# ORDER — the ship page. Every component shown, swappable only where the game says so. RUN CONTINUOUSLY.

    from    C1, 2026-08-22
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md.
    ruled   Sleven, 2026-08-22. Reference is Erkul (erkul.games), confirmed by
              him. Erkul does the maths and does NOT have the ship.

    SUPERSEDES, both unstarted - delete or ignore, do not work from them:
      inbox/ORDER_every-component-and-the-ship-page-2026-08-22.md
      inbox/ORDER_the-ship-page-editable-per-port-2026-08-22.md
    Each told you to extract component types that measurement later disproved.

---

## 0. THE PRINCIPLE - Sleven's words. Everything else follows from it.

> "We don't need to name any of these builds... we just have to make it all
> available for them to build anything they want with any type of thing in mind.
> If they wanna take a Hammerhead and max it with racing and agility parts, they
> can. That's their choice... We're just providing all the information for them
> to be able to do it."

**THE PAGE HAS NO OPINION.** No build modes, no presets, no category anybody picks
before they can start. Every part the game allows is offered, every number that
moves is shown, the player decides what matters.

**And its exact limit: the page offers what the GAME allows, not what the data
merely contains.** Those are different, and §1 is a list of the times confusing
them would have made the page lie.

## 1. VERIFIED FOUNDATION - measured, cross-checked, do not re-derive

Snapshot `20260801T204744Z`. 316 ships, 5,384 ship-items, 41 component types.
`loadout_data.gen.js` today: 470 parts, 5 types.

**Every `Loadout` entry states what you need:** `Editable`, `EditableChildren`,
`CompatibleTypes`, `MinSize`/`MaxSize`, and `ClassName` - the default fitted part,
which IS the stock loadout. **Read them. Never infer them, never hardcode them.**

**THE RULE: EDITABILITY IS PER PORT, PER SHIP. NEVER PER COMPONENT TYPE.**

*Why, and it is Sleven's catch:* plain `FuelTank` is 0-editable across 436 ports,
so "fuel is fixed" looks safe. **It is false.** `ExternalFuelTank` is **20
editable, 0 fixed - every one on a refueller.** Same shape for mining:
`Container` is 54 editable, on the ARGO MOLE and the ATLS - **the mining bags.**
**A by-type rule breaks the industrial ships first, which are the hulls where the
loadout IS the ship.**

**TWO CONDITIONS DECIDE SWAPPABLE, NOT ONE.** `Editable` alone is not enough:
26,182 ports are editable, but that includes **21,175 untyped** plus 3,732
Displays, 2,394 Misc, 770 Doors, 802 Seats. Cross-checked two independent ways:

    stock ClassName resolves to a real item      7,764 ports
    CompatibleTypes resolves to a real item type 8,544 ports

Two different joins, run separately, agreeing within 10%. **The non-resolving
16,289 are Misc, Display, Decal, ControlPanel, Button, Lightgroup, Sensor.**
Doors and dashboards. **A port is player-swappable when it is `Editable` AND its
type has real items in the catalogue.**

**FULL EDITABLE LISTS, so nothing is missed** (Sleven caught two of these):

    refuelling  MISC Starfarer, Starfarer Gemini, Starfarer Teach's Special,
                MISC Starlite                                        (4 hulls)
    salvage     Aegis Reclaimer x3, Argo MOTH, Drake Vulture x2,
                RSI Salvation                                        (7 hulls)
    mining      ARGO MOLE x3, Drake Golem x4, Greycat ROC,
                MISC Prospector x3                                  (11 hulls)
    containers  MOLE x3, ATLS x6, Golem x4, ROC, ROC-DS,
                Prospector x3                                       (18 hulls)
    tractor     14 hulls incl. Caterpillar, Cutlass Black, Hull B/C,
                Railen, Tyilui, 315p, MPUV Tractor

**EFFECTIVELY FIXED - build no pickers:** ManneuverThruster 32/4,683 ·
MainThruster 8/1,060 · Armor 0/305 · FuelTank 0/436 · FuelIntake 0/539 ·
QuantumFuelTank 0/261 · WeaponAttachment 35/1,162 · WeaponDefensive 4/664 ·
SalvageModifier 0/34 · TowingBeam 0/1.

**C1 WAS WRONG TWICE, corrected so you do not inherit it:** thrusters and armour
are not meaningfully swappable. An earlier draft had you extract 1,504 thruster
records to fill pickers nobody can use. **Do not.**

**KNOWN CAVEAT:** 1,092 ports accept `WeaponPersonal` - gun racks - but personal
weapons are NOT in `ship-items.json`; that catalogue is the UEX data. **Racks are
swappable, the catalogue to fill them is elsewhere.** Out of scope here. Log it.

## 2. WHAT CIC ESTABLISHED FROM CIG'S OWN SOURCES, 2026-08-22

- **4.10 is NOT Live. Live is 4.9.0.** RC1 (4.10.0-PTU.12497254) posted
  2026-08-21. No CIG-stated Live date. **So the 4.9 snapshot is CORRECT for the
  live game and needs no emergency refresh.**
- **Component swappability has NOT changed and nothing is announced to change
  it** - confirmed negative across all 22 PTU threads and every roadmap column.
  **Every measurement in §1 holds.**
- **A "Vehicle Armor" feature now governs per-hull damage resistance by weapon
  type**, and 4.10 does a balance pass on it. See L5.
- **Kruger S-65 Stingray** exists but is PTU-only, unpledgeable, absent from the
  Ship Matrix, with no published specs. **Held. See L14.**
- **Aegis Vulcan** is still `in-concept`. Our record is correct.
- Grey's Shiv, Grey's Basher, Kruger L-21/L-22 Wolf, Mirai Guardian MX are all
  **already matched in `ship_resolution.json`.** No gap.
- **Wikelo reward variants are already ruled** by
  `DECISION_hull-configuration-acquisition-2026-08-16.md`. `Drake Clipper Wikelo
  War Special` is already in the game files. **Do not re-open that decision.**

## 3. THE WORK

**L1. WIDEN THE CATALOGUE - derived, not hand-written.**
Extend `build_loadout_data.py` past today's 5 types. **Derive the type list by
scanning every ship's `Loadout` for ports satisfying BOTH conditions in §1.**
Do NOT transcribe the lists in §1 - those are context; the scan is the source.
When CIG changes a port, the next generation picks it up with no code change.
**Excluded regardless:** the four `Flair_*` types and
`GroundVehicleMissileLauncher`. **`Paints` are NOT excluded** - they go to L7.
Carry only fields a readout reads. *H1's lesson: 5,566 unused UUIDs were 80% of
a file.*
*Acceptance:* counts asserted against source. *Report the gzipped size* against
today's 431 KB.

**L2. THE STOCK LOADOUT IS THE SHIP'S OWN DEFAULTS.** A ship opens with what
`ClassName` says is fitted at each port. Not empty, not a guess.
*Control:* a named ship's opening state matches its `Loadout` port for port.

**L3. EVERY SLOT IS CLICKABLE. ONE INTERACTION EVERYWHERE.** Sleven's ruling.
A slot with a hull marker and a slot without **behave identically when clicked**.
A scrollable window lists **every component that fits that port on that ship**.
What is offered comes from `CompatibleTypes` + `MinSize`/`MaxSize` **on that
port**. **Offering an unmountable part is the page making a false claim.**
*Control, both halves:* a part the port accepts **appears**; a part it does not
**is absent** - not greyed, absent. Name one of each.
*Where the data does not say:* exclude and log it. **Never guess a port rule.**

**L4. A FIXED PORT IS SHOWN, NOT HIDDEN, AND NOT CLICKABLE.**
`Editable: false` means no picker, not invisible. The fuel tank still counts
toward range **because it is part of the ship.** Say plainly it cannot be changed.
**`Editable` carries `last_verified_patch`** - Sleven expects more ports to open
up later, and **that must be a data change, not a code change.**
*Control:* a fixed port renders, contributes to totals, opens no picker.

**L5. ARMOUR - fixed, not swappable, and it changes TWO things people care
about. NEW ITEM, and do not skip it because it has no picker.**
Every hull's armour carries, under `stdItem.Armor`:

    DamageMultipliers    Physical, Energy, Distortion, Thermal,
                         Biochemical, Stun  (+ *Change deltas)
    SignalMultipliers    CrossSection, Infrared, Electromagnetic
    PenetrationResistance / Deflection

The Drake Vulture's armour takes **Energy at 0.5 and Physical at 0.7**, with
Deflection 18 physical / 16 energy. **So "survivability" is not one number** - a
hull can be tough against ballistics and soft against lasers, and the readout must
say which. **And armour carries SIGNAL multipliers, so it moves stealth too.**
133 of 210 armour items are tagged to a hull; **the other 77 are not, and how
they attach must be established, not assumed.**
`app/models.py` has `damage_type` on weapons (the attacking side) and **nothing
for hull resistance.** This dimension does not exist in the schema yet.
*Also note* `PenetrationMultiplier` on the ship: `{Fuse: 0.7, Components: 0.4}` -
damage passes through to fuses and components at those rates.
*Control:* two hulls with different armour show different resistance, and a
weapon strong against one is visibly weaker against the other.

**L6. THE READOUT SHOWS EVERYTHING THAT MOVES, AT ONCE** - not a chosen category.
Damage; signature (em, ir, ship Emission/Distortion, **and armour's signal
multipliers**); survivability (shield ehp, ShieldHp, **armour resistance per
damage type**, Deflection); power draw against PowerPlant output and PowerPools;
heat against Cooling; cargo; quantum and fuel range; detection; mining and
salvage; crew, seats and life support. **Stock versus current on each.**
**MASS IS A REAL COUPLING AND MUST NOT BE DROPPED** - fitted parts change
`MassTotal`, which changes handling. **Since thrusters are fixed, mass is the main
lever a player has left over agility**, which makes it more important, not less.
*Control:* one swap moves at least two unrelated readouts in **opposite**
directions. Name it in the ledger.

**L7. LIVERIES LIVE ON THE SHIP PAGE.** Sleven: *if it is part of a ship, it
stays with the ship.*
**279 of 316 ships have exactly one `hardpoint_paint` port** - editable, empty by
default. **A livery is a real fitted slot**, like a shield. 302 are spelled
`hardpoint_paint` and **6 are `Hardpoint_Paint`** - CIG's own inconsistency;
**match case-insensitively or you silently lose six ships.**
All 1,077 paints carry `required_tags` tying them to a hull
(`Paint_Hornet_F7_Mk2` -> Hornet Mk II), plus `manufacturer` and `event_source` -
how it was obtained. This is the acquisition-routes model already ruled, not a
new one.
**DO NOT RENDER LIVERIES ON THE 3D MODEL.** The data has names and colour words
in a class name, **not textures**. Tinting to approximate is already ruled out.
**Build the honest section; a texture source can plug into it later.**
**Liveries take no part in the performance readout.**

**L8. EXTRACT THE 3D VIEWER. ONE implementation, shared.**
It lives in `index.html`; the ship page needs the same one. **Two copies of a
Three.js viewer guarantees drift.** Two concrete consumers exist, so this
satisfies the standing 2-3-cases rule.
*Control:* the same ship renders identically on both pages - same model, same
markers, same count. Asserted.
*Negative half:* break the shared module and confirm **BOTH** pages fail. If only
one fails, there is a second copy somewhere.

**L9. THE SHIP PAGE = THE BENCH PLUS THE MODEL. No third page.**
`loadout.html` is already per-ship, already does A/B, already shares by URL. Add
the model to it.
*Rejected - a new `ship.html`:* three places rendering ships instead of two.
*Rejected - merging into `index.html`:* ~10,000 lines already, and the ship still
gets no URL of its own.
*Control:* swap a part; the model stays loaded and the readout changes.

**L10. A HULL MARKER IS A SECOND ROUTE TO THE SAME PICKER**, not a second
mechanism. Clicking the gun on the model and clicking it in the list open the
identical window. **This is the item Erkul cannot copy.**
*Control:* marker N selects port N and no other - by identity, never by screen
position.
**Markers stay weapons-only.** Internal ports are reached from the list. Settled.

**L11. THE SHIP NAME LINKS TO THE SHIP PAGE**, not to RSI. **The RSI link moves
ONTO the page and stays clearly available.** Sending somebody off-site the moment
they click a name means they never see what was built for them.
*Control:* every ship name in the list resolves to a page that loads.

**L12. THE SHARE LINK CARRIES THE WHOLE BUILD** - ship and every fitted port.
*Control:* paste a shared URL into a clean session; same build back, model and all.

**L13. PROVENANCE SURVIVES.** The generated data separates **CIG's own
precomputed stock aggregate** from **anything summed from parts**, and says
which is which. **That must not be lost when the layout changes** - it is the
difference between reporting and asserting. Same for `last_verified_patch` and
the 33 unreleased ships.
*Control:* a CIG-sourced stat and a computed stat are visibly different on the page.

**L14. THE THREE KINDS OF INCOMPLETE SHIP, each handled honestly.**
1. **Has a game file, no 3D model.** `Origin M80` - full stats, `has_model:
   false`. Full readout and swapping; an honest "no model available" where the
   viewer goes. **Not a broken viewer, not a spinner.**
2. **No game file at all** - 33 of them: Vulcan, Galaxy, Kraken, Liberator,
   Orion, Pioneer, Nautilus, the Rangers, Hull D/E and the rest. **Announced or
   pledgeable, not built.** Show the ship, say it is not flyable yet, **say
   nothing about its loadout.**
3. **No mount data** - 25 ships. List-driven swapping still works; say so plainly.
**Never an empty hull presented as a complete one.**
*Control:* one named example of each renders correctly.
**DO NOT ADD the Kruger S-65 Stingray.** PTU-only, no Ship Matrix entry, no
published specs. **A ship with no verifiable specs is the opposite of what this
site is for.** It comes in when it reaches Live.

**L15. WRITE THE PARKED IDEAS DOWN. BUILD NOTHING FOR THEM.**
`docs/IDEA_recommended-builds.md` - Sleven's "best build for this ship", why it is
parked (*"that can come later with much more research"*), and what it needs.
**Name the tension: a recommendation is an opinion and §0 says this page has
none.** That is what to design around, not a reason to refuse it.
`docs/IDEA_unused-ship-data.md` - ten uses C1 measured for data nobody reads:
**crew and seat map (802 seat ports, 241 pilot, 22 bedding); the fuse map (1,416
`$slot_fuse_*` - engineering); boarding and access (770 doors, ramps, elevators);
ground refuelling (31 ports); "will it fit" (CargoSizeLimits + hull dimensions);
size comparison; reverse component lookup (which ships take this shield);
variant diffing (89 game-only variants); modular bays (39 Module, 73 Room ports);
damage map (`DamageMax` per part).** **Unresolved: 21,175 untyped ports tagged
VEN / MEC / POW / BAR1 - possibly engineering resource nodes. NOT established.
Do not build on it.**

**L16. THE PRE-LIVE PUNCH LIST.** `docs/PRE-LIVE-PUNCH-LIST.md`, maintained.
Every page, dataset and empty state, **with a number**, and whether it blocks
going live. Measured starts: **25 ships with no mount data, 8 refused by the
alignment gate, 21 `unchecked_hull`** (was 7 - the G3 geometry rebuild recovered
twelve models now borrowing base-ship mount data nothing verified), **9 price
categories with items and no prices**, keybind modes and devices the page dims,
**armour resistance absent from the schema (L5)**, **`WeaponPersonal` racks with
no catalogue**, **the Stingray pending Live**, and **the four careers with no
component behind them** - Medical (16 ships), Passenger, Repair, Construction.
**Those are hull properties, not builds - say so rather than offer a dead
control.**
**Then bring `docs/CURRENT-STATE.md` back in line.** Last written 2026-08-16,
predating the shop layer, FIND, the guard inversion and the collector build.
**A five-day-stale state document is why nobody could say what was left.**

**L17. SWEEP.** Every control in `checks/`.

## 4. WHAT MUST NOT HAPPEN

- **Do not apply editability by component type.** §1. Read the port.
- **Do not use `Editable` alone.** §1. Both conditions.
- **Do not build pickers for thrusters, armour, fuel tanks or intakes.** §1.
- **Do not hide fixed components.** L4. They are part of the ship.
- **Do not offer a part the port does not accept.** L3.
- **Do not treat survivability as one number.** L5.
- **Do not drop mass from the handling maths.** L6.
- **Do not render liveries on the model.** L7. And match `hardpoint_paint`
  case-insensitively.
- **Do not build a second 3D viewer.** L8. Or a third ship page. L9.
- **Do not remove the RSI link.** L11. It moves.
- **Do not add the Stingray.** L14.
- **Do not re-open the Wikelo variant decision.** §2.
- **Do not add build modes, presets or categories.** §0.
- **Do not restrict what fits by a ship's CIG Career or Role.**
- **Do not build recommended builds or any L15 idea.**
- **Do not deploy the live site. Do not cut a release.**
- **Do not `git add -A`. Push at the end.**

## 5. REPORT

- Which types the L1 scan selected, and the gzipped size against 431 KB.
- L3's two named examples: one part proven offered, one proven absent.
- L5: how the 77 untagged armour items attach, and whether a hull's resistance
  can be resolved for every ship or only some.
- The L6 case in words: one swap, two readouts moving opposite ways.
- Whether breaking the shared viewer module broke both pages.
- The punch list, and what on it you think actually blocks going live.
- Anything here you think is wrong. **L3 is the part most worth arguing with** -
  if `CompatibleTypes` and the size window do not decide fitment cleanly for every
  port, **say so early and loudly**, because everything this page claims rests on
  it.
