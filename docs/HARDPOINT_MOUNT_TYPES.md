# Star Citizen Hardpoint Mount Types — Reference Definition

**Purpose:** an independent, source-agnostic definition of what "Fixed," "Gimbal,"
and "Turret" (manned vs. remote) actually mean mechanically in Star Citizen, so our
own hardpoint categorization (`hardpoint_organizer.py`'s `categorize_hardpoint()`,
and the split schema in `data-layer/processed/hardpoints_by_type/<slug>/`) can be
checked against the game's own mechanics rather than against any single data
source's internal labeling. Written after finding that api.star-citizen.wiki's raw
`ports[].type` field disagreed with our own Blender-exported viewer data on the
Arrow's turret count (see "Case study" below).

## The three mount types

### Fixed
A weapon of matching size is attached directly to the hardpoint/itemport. No
independent aim — the pilot points the whole ship. This gets the **largest possible
weapon** for that hardpoint size, in exchange for requiring more accurate flying to
land shots.

### Gimbal
An accessory item (a "Gimbal Mount," e.g. "VariPuck S3 Gimbal Mount") installs
*between* the weapon and the hardpoint. It lets the pilot independently aim within a
limited cone instead of having to point the whole ship — at the cost of **only
accepting a weapon at least one size smaller** than the hardpoint/gimbal itself (a
Size 3 gimbal can only take a Size 2 or smaller gun). Still pilot-fired, still on the
same control input as a fixed gun — just with some aim assist.

### Turret — Manned vs. Remote
A turret is a **separate rotating mount**, mechanically distinct from a
fixed/gimbal position on the airframe itself:
- **Remote turret**: no interior physical access for a crew member — operated
  remotely (by the pilot via a camera/reticle, or by a crew member at a station
  elsewhere in the ship). Common on smaller ships as a defense option without
  costing interior space.
- **Manned turret**: has a physical seat a crew member sits in and directly
  operates. Per RSI's own design notes, a manned turret takes an *additional* size
  penalty beyond an unmanned/remote one — e.g. the smallest viable manned turret is
  Size 3 hosting a Size 1 weapon; the Retaliator's manned turrets are Size 4, each
  holding 2× Size 1 guns.

### The important subtlety: mount type is a property of what's *equipped*, not a fixed hardpoint attribute
A single physical hardpoint slot isn't permanently "a gimbal slot" or "a turret
slot" — its behavior depends on what's currently installed, within that port's size
and `compatible_types` constraints. RSI's own Q&A on the Arrow's top mount says this
explicitly: *"the attached turret can hold two Size-1 weapons, but it can also be
removed to add either a single fixed Size-3 weapon or a gimballed Size-2 weapon"* —
the same physical port can be Turret, Fixed, or Gimbal depending on the item
installed.

## The API terminology gotcha this reference exists to flag

api.star-citizen.wiki's `ports[].type` field uses **`Turret`** as a broader,
technical port-classification category — and it is **not** limited to mechanical
turrets in the everyday/gameplay sense. Evidence:

- The RSI design-notes article on weapon mount sizing describes the size-reduction
  rule for gimbals and turrets in the same breath — *"the size(s) of the weapon that
  the Turret/Gimbal are [reduced]"* — treating them as siblings under one mechanical
  system, not as unrelated categories.
- On star-citizen.wiki itself, the item page for **"VariPuck S3 Gimbal Mount"** — an
  actual gimbal-mount accessory, not a turret — is filed with **"Turret"** as its
  page category/breadcrumb.

So when the API reports a port as `type: Turret, sub_type: GunTurret`, that means
*"this port is in the turret/gimbal family of the game's internal port
classification (i.e., not a plain Fixed-only port)"* — it does **not**, by itself,
mean "this is a rotating gun emplacement separate from the airframe" in the sense
most players (and our own viewer) mean by "turret." Whether it's actually a turret
or a gimbal in the common sense depends on what item is equipped in that port.

## Case study: the Anvil Arrow

Cross-checked three source types: api.star-citizen.wiki's raw `ports` data (fetched
directly, not a cached summary), RSI's official Q&A on the Arrow
([comm-link 16883](https://robertsspaceindustries.com/en/comm-link/engineering/16883-Q-A-Anvil-Arrow)),
and current third-party guides (search results consistently corroborating each
other — direct fetches of starcitizen.tools and the Fandom wiki were blocked, 403
and 402 respectively, so those two are search-snippet corroboration only, not
directly read).

**Official/current consensus** (RSI Q&A + independently corroborating guide sites):
- **2× Size 3 wing "gun hard-points"** — described in RSI's own ship copy as gun
  hardpoints, currently equipped with "VariPuck S3 Gimbal Mount" items per the live
  API. Mechanically: **gimbal-mounted guns**, not turrets, despite sitting on API
  ports typed `Turret/GunTurret`.
- **1× pilot-controlled top-mounted turret** — a genuinely separate rotating mount
  (`hardpoint_gimbal_mount` in the API, `sub_type: BallTurret`), default-equipped
  with 2× Size 1 guns, swappable to a fixed Size 3 or gimballed Size 2 weapon. This
  one **is** a turret in the mechanical/common sense.
- **Missile racks**: 2× Size 2 + 2× Size 3 physical rack ports, 6 total missile
  capacity — consistent across the live API port list (4 ports) and RSI's "six size
  2 missiles" copy (2 + 4 = 6).

**Re-evaluating the 3 API "Turret" ports against this definition:**

| Port | API type/sub_type | Mechanically actually is |
|---|---|---|
| `hardpoint_gimbal_mount` | Turret / BallTurret | **Turret** (genuine — separate rotating mount) |
| `hardpoint_weapon_wing_left` | Turret / GunTurret | **Gimbal-mounted gun** (per RSI copy + equipped item), not a turret in the common sense |
| `hardpoint_weapon_wing_right` | Turret / GunTurret | **Gimbal-mounted gun**, same as above |

So api.star-citizen.wiki's "3 turret ports" figure is correct as a description of
the game's internal port-classification system, but **answers a different question**
than "how many turrets does this ship have" in the sense our viewer/schema cares
about. By the mechanical/common-sense definition this document lays out, the Arrow
has **1 turret** and **2 gimbal-mounted wing guns** — matching our own local
Blender-exported categorization (`weapon_turret` ×1, `weapon_gun` ×2) on *category*.

**What's still unresolved**: our local `hardpoints_weapons.json` labels the two wing
guns as Size 1 (`gimbal_mount S1 LS/RS`), while every current source checked here —
RSI's own copy, the live API's port sizing, and third-party guides — agrees the wing
hardpoints are **Size 3**. I could not find explicit patch notes documenting a
size change (searches for an Arrow S1→S3 wing rework turned up nothing conclusive,
and the two wiki mirrors that might have a version-history section were unreachable
— 403/402), so I can't confirm whether our local file reflects a genuinely older
patch configuration or is just mislabeled/stale data. This is a size-metadata
question, not a category question — flagged here rather than guessed at.

## Sources

- [Design Notes: Weapons Mount Updates (RSI comm-link 14570)](https://robertsspaceindustries.com/en/comm-link/engineering/14570-Design-Notes-Weapons-Mount-Updates)
- [The Shipyard: Weapon Hardpoints (RSI comm-link 16181)](https://robertsspaceindustries.com/en/comm-link/engineering/16181-The-Shipyard-Weapon-Hardpoints)
- [Q&A: Anvil Arrow (RSI comm-link 16883)](https://robertsspaceindustries.com/en/comm-link/engineering/16883-Q-A-Anvil-Arrow)
- api.star-citizen.wiki live vehicle API (`/api/vehicles/eaeb562d-d4ac-43bd-a843-e8a6d69fad82?include=ports,components`), fetched directly this session
- [VariPuck S3 Gimbal Mount — Star Citizen Wiki](https://star-citizen.wiki/VariPuck_S3_Gimbal_Mount/en) (category/breadcrumb evidence for the "Gimbal filed under Turret" point)
- Search-corroborated but not directly fetched (blocked): starcitizen.tools/Arrow (403), starcitizen.fandom.com/wiki/Arrow (402)
