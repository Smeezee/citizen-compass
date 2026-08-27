# Update - the alignment overlay is live, and the "31 pairs" were two different things

Deployed and verified by fetching back, cache-busted.

## What the 31 pairs actually were

Grouping by port set was the wrong unit. Splitting each group by MESH first -
the same 2% bounding-box bar the join uses - shows the 31 disagreements are two
populations:

**Genuinely one hull, and now aligned (10 ships, 133 markers moved):**

    Constellation Phoenix Emerald   0.602 -> 0.045
    M2 Hercules Starlifter          1.566 -> 0.051
    Guardian QI                     0.305 -> 0.045
    Cutter Scout                    0.295 -> 0.087
    Talon Shrike                    0.233 -> 0.035
    Mustang Alpha, Vindicator       0.211 -> 0.161 within its own cluster
    MISC Reliant Sen                0.205 -> 0.073
    Sabre Comet                     0.168 -> 0.073
    600i Explorer                   0.159 -> 0.159 (see below)

**Different hulls that merely share a port list, correctly left alone (32
pairs):**

    MISC Reliant Kore vs Mako       bounding boxes differ 53.9%
    L-21 Wolf vs L-22 Alpha Wolf    28.2%
    Cyclone MT vs TR                25.8%
    MISC Freelancer vs MAX          20.7%
    Glaive vs Vanduul Scythe        18.7%
    Vanguard Harbinger/Hoplite/Warden  5.9 - 12.4%
    A2 Hercules vs C2 and M2        11.8%
    Aurora LX vs the other four     14.3%

**Their markers SHOULD differ. That disagreement was never an error**, and the
first version of this - which grouped on port set alone - would have forced 15
ships onto another hull's positions. It refused them, which is how the
distinction was found.

## Result

Every same-mesh pair now agrees within 0.15 except one: 600i vs 600i Touring at
0.159, where re-snapping to its own hull cannot land closer. Reported, not
massaged.

35 same-mesh pairs agree, 32 different-hull pairs are left alone, 43 pairs could
not be checked because their geometry is not decoded (all already within
tolerance).

**The Gladius Pirate and Valiant were not touched** - 0.049 apart, inside
tolerance. The placement Sleven confirmed against RSI's art is exactly as it was.

## Guards

`hardpoints_fleet.json` and `hardpoints_join.json` are both unchanged. This is
an overlay applied by `build_holo_data.py` at read time, so each dataset keeps
its single writer.

The apply guard earned its keep immediately: three overlay keys are model stems
("M2_Hercules") while the viewer merges under real names ("M2 Hercules
Starlifter"), and the build REFUSED rather than reporting 133 markers moved when
it had moved 104. Fixed by plumbing the join's own alias map through, not by
guessing the naming rule twice.

`checks/_verify_hardpoint_alignment.py`: 7 checks - the mesh gate refuses
Kore/Mako and accepts Mako/Sen, the medoid ignores an outlier and does not
depend on dict order, the tolerance discriminates in both directions, and a
missing overlay is a no-op.

## Worth knowing

The join's own alignment pass (the one that moved the Gladius Pirate) grouped on
PORT SET, not mesh. Under the mesh rule the Pirate would not have been moved -
and the moved position is the one confirmed against the art. Flagging rather
than silently reconciling: one of the two rules is more right than I can
establish from here.

Not committed.
