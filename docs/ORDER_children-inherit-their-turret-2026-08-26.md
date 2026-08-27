# ORDER — A gun inside a turret inherits the turret's position. This is the coverage fix.

**C1, 2026-08-26.** Code established the mechanism while executing W3; this
grounds it in the data and specifies the fix. **This is the inherited-sibling
job Sleven deferred on 2026-08-23 until the hologram work was done. The hologram
work is done.**

---

## The defect, in one ship

`ship_mounts.json` gives the **Aegis Retaliator twenty mounts.** Every one is a
PARENT-level port:

    5   TurretBase       turret_fronttop, frontbottom, backtopleft,
                         backtopright, backbottom
    4   WeaponDefensive  countermeasurelauncher left1/left2/right1/right2
    4   rack             rack_fl, rack_fr, rack_rl, rack_rr
    5   target selector
    2   weapon regen pool

**The placer placed all twenty. Four markers survive:**

    AEGS_Retaliator: [["23",...],["24",...],["39",...],["40",...]]

**Those four are the countermeasure launchers, and they survive for one reason:
they are the only ports that exist on BOTH sides.** The ship page lists the guns
*inside* each turret — `hardpoint_class_2`, `turret_left`, `turret_right` — and
the placer produced positions for the turret *bases*. **The names never meet, so
sixteen placed positions are computed and discarded.**

**A visitor sees four markers on a torpedo bomber with five manned turrets.**
That is why Sleven filed the Retaliator, the Sabre Peregrine and all three
Ballistas as "hardpoints not set up" — four is indistinguishable from none.

## C1 — A child port takes its position from the parent that WAS placed

For every page port that is a child of a turret or mount whose parent has a
placed position, **derive the child's position from the parent's.**

**Distribute siblings around the parent; never stack them.** Two guns in one
turret at identical coordinates is a single marker wearing two labels, and the
label solver will make one of them unselectable.

**The existing convention stands and is not up for revision:** markers bind to
`PortId`, not to a hardpoint name. `loadout_marker.gen.js` says why — a name is
not unique within a ship, the Polaris has thirty ports called MEC, and L10
requires a marker to select one port and no other. **Inheritance resolves to a
PortId like everything else.**

## C2 — Ports that are not physically mountable STAY OFF

The Retaliator's twenty mounts include **five target selectors, two weapon regen
pools and four racks.** Per the standing 3D-viewer ruling, only physically
visible and mountable hardpoints get a marker on the hull — weapons, turrets,
missile racks. **A weapon regen pool is not a place on the ship.**

**Do not raise the count by marking things that are not there.** A coverage
number inflated with regen pools is a worse answer than four honest markers.

    CONTROL, load-bearing: report, per hull, ports-with-markers over
    ports-ELIGIBLE-for-markers, not over ports-total. State the eligibility rule
    and how many ports it excludes fleet-wide. If eligible == total, the rule
    was not applied.

## C3 — Controls

    CONTROL, load-bearing: the Retaliator must rise from 4. Report the new
    number and name every port that gained a marker. If it does not rise, the
    inheritance did not fire and the fix is not done.
    NEGATIVE CONTROL, load-bearing: PortIds 23, 24, 39 and 40 must keep the
    positions they have now - [-0.03755,-0.02334,-0.95564], [0.053,-0.00648,
    -0.97809], [0.01037,-0.0012,-0.98118], [-0.00836,0.01415,-0.96836]. Those
    four are correct today. A fix that moves them has broken what worked.
    CONTROL, load-bearing: assert NO two markers on any hull share coordinates
    to 5 decimal places. Stacked siblings are the failure mode this creates.
    CONTROL: report fleet-wide coverage before and after - the median and the
    range of markers-per-eligible-port across all hulls with markers. The
    Sabre Peregrine (2) and the three Ballistas (2 each) must be in the report
    by name; they are the other ships Sleven reported.
    NEGATIVE CONTROL: hulls with no turrets must be unchanged. If a single-seat
    fighter's marker count moves, the inheritance is firing where there is no
    parent-child relationship at all.

## C4 — Sequence

**This runs AFTER `ORDER_the-placer-cannot-see-new-ships-2026-08-26.md`.** P1
widens the candidate set from 175 toward 235; this raises coverage within each
hull. **Doing them in the other order means re-running placement twice and
measuring the second against a moving first.**

## What this does not do

**It does not make the positions real.** They remain derived from hull geometry,
because the models carry no node hierarchy —
`AMENDS_extracted-textures-scope-2026-08-22.md` established that RSI's own
models cannot supply coordinates either. **A child inheriting an estimated
parent position is still an estimate.** The page's provenance language must not
imply otherwise.
