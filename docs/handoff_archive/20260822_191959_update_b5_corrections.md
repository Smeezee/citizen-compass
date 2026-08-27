# Update - three corrections to the promotion. All three confirmed, one worse than reported.

Sweep after the work: **54 ok, 0 failed, 3 skipped, 0 NOT RUN, 268s.** Nothing
committed yet - I said I would hold for the children/crowding call.

## 1. B5 did not fire, and the cause is upstream of everywhere I looked

Not the record write, not `place_fleet` reading it. **The child ports were never
in the placement input at all.**

    ships.json        2,555 top-level weapon ports, 2,374 CHILDREN
    ship_mounts.json  3,011 mounts, 0 of them children

The Hammerhead's 24 `hardpoint_class_2` guns were not on the hull-centre
default - they were absent. `turretOf` was null on all 1,798 records because no
port that HAD a turret ever reached the file. My earlier "the premise does not
hold" was the same miss from the other side.

**Proven on the Hammerhead**, children on: 24 guns present, all carrying
`turretOf`, all `placed_from: inherited` from that turret, none at hull centre.

"One level" would have been actively wrong. The chain is
`turret_side_back_right -> hardpoint_weapon_left_upper -> hardpoint_class_2`,
and one level up yields *left, upper* - putting a back-RIGHT turret's gun on the
LEFT of the ship. A port inside a turret now takes the outermost `TurretBase` in
its own recorded chain.

### And it is NOT fit to ship. My control caught why.

After inheritance, the hull-scale sibling spread plus the collision walk
scatters them: **12 of 24 guns land nearer a different turret than their own.**
A front-left gun beside the rear turret is a confident wrong position - worse
than hull centre, which at least looks wrong.

The fix is spreading an inherited sibling around ITS TURRET rather than across
the hull, and not letting the collision pass walk it arbitrarily far. **Not
done.** So `--with-children` is off by default, and the control asserts the
shipped dataset holds **0 inherited and 0 child points** - it fails if anyone
turns the flag on before the scatter is fixed.

The trade, measured, so the call is somebody's to make with numbers:

    with children:  +160 markers on 5 more hulls
                    crowding 60->216 markers, 9->21 hulls (proximity)
                             117->451 markers, 19->34 hulls (report)

## 2. You were right about the crowding figure, and it is worse than you said

I quoted the half that improved. Both, on two independent metrics:

                      report metric      proximity metric
                      markers  hulls     markers  hulls
    B6 alone BEFORE     118     19         60      9
             AFTER      117     19         60      9

B6 alone is clean on all four. But **the promotion as a whole is not**:

    sandbox (this morning) -> shipped     50 -> 60 markers,  8 -> 9 hulls

**+10 markers and +1 hull, worse**, from the vertex resample rather than from
B5 or B6. I did not report that. The control now asserts all four numbers and
fires on a rise in any of them.

## 3. The gate had nothing left to refuse

`matched.json` was built from `hardpoints_fleet.json` - the 167 hulls that had
**already been placed**, a set with every refusal already removed. That is why
it said `skipped: 0`. A gate that cannot refuse anything is not a gate.

Candidate set is now every hull with mount data and decoded geometry:

    placed 169, skipped 6
      Clipper, Defender, Eclipse, Nova, Pulse   proportions do not match dims
      Javelin                                    no published dimensions

Not loosened - the control drives it with proportions that must fail and a hull
that must pass. **Six, not seven.** Which hull the seventh was cannot be stated,
because I overwrote that report before reading it.

Side effect worth naming: 2 more hulls now place, so markers went 1,200 on 157
hulls to **1,210 on 159**.

## Held

Not committed. The children/crowding trade is the one decision I did not want to
make silently by default.
