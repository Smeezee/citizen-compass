# BUILD AND DEPLOY. 167 hulls / 1,720 ports, 245 ships fully on CIG coordinates. This is the end of my run tonight.

**2026-08-27 20:35 local · C1** — read from `date`.

    client marker records added for 41 hull(s) the dataset had none for
    client hardpoint overlay: 1720 port(s) moved onto CIG positions

**The manifests on disk beat any number in this note.** The rule that does not
change: none of those may be zero, and `loadout.html` must appear in the
disclosure-CSS line.

## THE BIG ONE — CIG'S OWN RECORD SAYS WHICH HULL A SHIP IS BUILT ON

I wrote earlier tonight, in a finding, that *"ships.json carries no geometry
path — I checked every field on the row."* **I checked the top-level fields for
a PATH. The answer is a NAME, one level down, and it was there all along:**

    anvl_c8_pisces  ->  Parts[0].Name == "ANVL_Pisces"

The root of CIG's own part tree names the hull. 309 of 318 classes carry one;
183 name a hull other than themselves. **It reaches every variant a name rule
never could** — `ANVL_C8_Pisces -> ANVL_Pisces`, `RSI_Ursa_Medivac ->
RSI_Ursa_Rover`, `GRIN_MDC -> GRIN_MXC`, none of which share a prefix.

This **replaced** the `cls + "_"` prefix expansion. That was a pattern standing
in for exactly this fact. And it is safe where my earlier name-expansion
experiment was not: only ports whose `HardpointName` exists as a node in that
hull are placed, so a module-specific mount gets **no** position rather than a
wrong one. The record decides membership; the geometry decides placement.

## AND HALF THE FLEET WAS PARKED IN A TREE NOBODY LOOKED AT

Every hull the decoder had ever seen lives under
`Data\Objects\Spaceships\Ships\`. **Ground vehicles do not.** They sit in
`Data\Objects\Vehicles\` — 1,762 `.cga` entries, never scanned:

    Vehicles\TMBL\storm\TMBL_Storm.cga        Vehicles\TMBL\Nova\TMBL_Nova.cga
    Vehicles\ANVL\Ballista\ANVL_Ballista.cga  Vehicles\ANVL\Atlas\Centurion\...

The Cyclones, Storm, Nova, Ursa, Ballista, Centurion, Spartan and Lynx were all
"no `.cga` anywhere" for that one reason.

`Spaceships` is still narrowed to its `Ships` subtree — the same tree also holds
Turrets, Seats and Derelicts, and those are parts.

## Numbers across tonight

    transforms   116 hulls -> 153
    placement    146 converted -> 284 · 137 passed -> 277
    overlay      93 hulls / 955 ports -> 167 hulls / 1,720 ports
    ship page    165 classes fully on CIG coordinates -> 245, and 91 with
                 none -> 20

## The 20 still with nothing, each for a stated reason

    ARGO_ATLS family (8)   it is a POWER SUIT, under Characters\PowerSuit -
                           not a vehicle hull and not in either tree
    GRIN MDC/MTC/ROC (4)   decoded, but no exterior mount at all - nothing
                           there could have failed a check
    TMBL_Cyclone AA/MT/TR  variants whose own records name no decoded root
    AEGS_Javelin           two paths claim the name with equal evidence,
                           one under `dmg` - refused, not picked
    VNCL_Glaive, _Scythe   ASYMMETRIC SHIPS, not a bug - the Glaive's "right"
                           missile rack sits at negative X, on the left side,
                           while VNCL_Blade mirrors perfectly from the same
                           decoder in the same run
    MOTH, Starfarer Gemini

## Verified before sending

    placement directory vs manifest      284 / 284, zero stale
    overlay entries matching nothing                       0
    client records colliding with existing                 0
    checks/_verify_placement_gate.py               exits 0

Testing only. Nothing to the live site without Sleven's go-ahead.

— C1
