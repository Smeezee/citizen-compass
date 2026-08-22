# IDEA — ten uses for ship data nothing on the site reads. PARKED.

    from    Code, 2026-08-22, written at L15 of ORDER_the-ship-page-2026-08-22-FINAL
    status  PARKED. Nothing here is built. This document is the deliverable.
    source  scunpacked snapshot 20260801T204744Z, 316 ships, 57,759 ports
    note    Every figure below was MEASURED in this repo while writing this
            file, not carried over from the order. Where a measurement
            disagreed with the order's number, mine is stated and said to be
            mine.

---

## Why write this down at all

The ship page reads 25,875 ports. The snapshot has **57,759**. The other
31,884 are not junk — they are doors, seats, fuses, relays, engineering nodes
and cargo geometry, and each one is something CIG modelled deliberately.

The risk in a dataset this size is not that something is missing. It is that
somebody rediscovers the same thing in six months and re-derives it badly. So
these are written down with their real numbers and their real limits, and
**none of them is built**.

The addendum has since ruled that the ship page is tabbed layers, and **every
idea below is a candidate tab** — one label, one generated file, loaded only
when opened. That is the shape to build any of them in, when any of them is
wanted.

---

## 1. THE CREW AND SEAT MAP — 802 seat ports

`Seat` ports across the fleet: **802**. Of those, **387 hardpoints name a pilot
seat** and **140 are bedding**. (The order says 241 pilot and 22 bedding; my
count is by hardpoint name across every record including variants, which is
why it is higher. Neither is wrong — they are counting different things, and
anyone building this should count again for their own definition.)

A ship's `Crew` figure says a number. The seat map says *where those people
sit and what they are doing* — pilot, gunner, engineering station, bunk.

**What it would answer:** "can my group of four actually all do something on
this ship, or are two of us passengers?"

**What it needs:** nothing new. The data is in `Loadout`, keyed by
`HardpointName`, and the ship page already carries `PortId` for every port.

---

## 2. THE FUSE MAP — 1,419 fuse slots on 305 hulls

Structure is **ship → relay → fuse slots**. 305 records carry relays, **692
relays**, **1,419 fuse slots**. A relay's `ClassName` states how many fuses it
holds — `RELAY_1slot` (117), `RELAY_2slot` (226), `RELAY_3slot` (184), plus
`_slim` variants — and its `HardpointName` says where on the ship it sits.

Range: **Aegis Idris-P, 15 relays / 37 fuses** down to **Drake Clipper, 1 relay
/ 1 fuse**.

**Every fuse is the same part.** What varies is how many and where.

**This one is no longer parked** — the addendum promotes it to M2, the
Engineering layer. What stays parked is everything past counts and positions;
see §11.

---

## 3. BOARDING AND ACCESS — 770 doors

**770 Door ports**, plus ramps, elevators and airlocks under their own
hardpoint names.

**What it would answer:** how many ways into this hull, and where. That is a
real question for anyone thinking about being boarded, and nothing on the site
answers it today.

---

## 4. GROUND REFUELLING — 31 ports

31 ports across the fleet accept a ground-refuelling connection. Small, and
exactly the kind of thing that is invisible until somebody needs it.

---

## 5. "WILL IT FIT" — CargoSizeLimits against hull dimensions

Every ship states `Length`, `Width` and `Height`, and cargo grids state their
own `InventoryContainer` dimensions in the game's 1.25 m unit.

**What it would answer:** will this vehicle fit in that hangar; will that
container fit in this grid. Both are asked constantly and neither is answerable
anywhere on the site.

**A warning from L6:** a cargo grid states **no SCU figure at all** —
`InventoryOccupancy` is how much room the grid itself takes up and reads 0 for
all 143 of them. Capacity is the dimensions. Anyone building this and reading
the obvious field will publish "0 SCU" everywhere.

---

## 6. SIZE COMPARISON

316 hulls with real dimensions and 235 with a 3D model, and the viewer is
already extracted into one shared module (L8). Two ships at the same scale in
one scene is a small feature on top of work that is already done.

---

## 7. REVERSE COMPONENT LOOKUP — "which ships take this shield?"

The ship page answers "what fits this port". The inverse — "where can I put
this part I already own" — is the same 124-rule fitment table read backwards,
and the table is already generated and already deduplicated.

**Cheapest idea on this list by a distance.** It is a different index over data
that already ships.

---

## 8. VARIANT DIFFING — 89 game-only variants

The fleet holds many near-identical records: `AEGS_Hammerhead` and
`AEGS_Hammerhead_GS` (226 ports / 9 crew against 224 / 8),
`DRAK_Caterpillar` and `DRAK_Caterpillar_Boarded`, four Apollo Medivac tiers,
four Grey's Shiv cosmetics.

**22 display names are shared by 51 records.** A diff view is the honest
answer to a question the shared names make unavoidable: *what is actually
different between these two?*

**And note where that lands:** the ship page had to disambiguate those names in
its own dropdown (M0). A diff view is the same problem, solved usefully instead
of defensively.

---

## 9. MODULAR BAYS — 43 Module ports, 73 Room ports

Ships whose interior is configurable at all. Small numbers, high interest —
these are the hulls people ask about.

---

## 10. THE DAMAGE MAP — `DamageMax` per part

Every fitted part carries a damage threshold. Combined with the ship's
`PenetrationMultiplier` (which reads `{Fuse: 0.7, Components: 0.4}` on many
hulls) this is the beginning of "what breaks first", which is the question
behind the whole engineering layer.

**It is a beginning and not an answer** — see §11.

---

## 11. NOT ESTABLISHED. DO NOT BUILD ON THIS.

**21,175 ports carry no `CompatibleTypes` at all**, and a large number of them
are tagged `VEN`, `MEC`, `POW` and `BAR1`. The RSI Polaris alone has thirty
ports called `MEC`, thirty called `VEN` and thirty called `POW`.

They look like engineering resource nodes. **That is a guess.** Nothing in the
snapshot says what they are, and the pattern is equally consistent with
ventilation geometry, maintenance access or an internal naming convention that
means nothing at runtime.

**So: NOT ESTABLISHED. Do not build on it, and do not let a page imply it.**

Two more, from the order and from measurement:

- **Fuse ratings and failure behaviour are not in this data.** Only counts and
  positions. Whether a blown relay disables the components near it **is not
  stated**. `PenetrationMultiplier` *suggests* damage reaches fuses before
  components. Suggests. Say so, or say nothing.
- **`WeaponPersonal` racks: 1,092 ports accept them and the catalogue to fill
  them is not in `ship-items.json`.** The racks are swappable and there is
  nothing to offer in them. That is a gap in a different dataset, not a defect
  here.

---

## What must NOT happen

- **Do not build any of these.** The order is explicit and this document is the
  whole deliverable for L15.
- **Do not build on the untyped ports.** §11.
- **Do not claim fuse behaviour the data does not state.**
- **Do not add a tab with nothing behind it.** If one of these is picked up,
  the tab arrives with the data or not at all.
