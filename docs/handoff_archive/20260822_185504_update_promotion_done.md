# Update - B5/B6 promoted, ef4cf29. 1,193 of 1,200 markers moved.

Ledger `afcd2a3`. Old dataset moved aside to
`_to_delete/hardpoints_fleet_pre_B5B6_20260822185204.json` (656,401 bytes), not
overwritten.

## The delta, decomposed - because two different changes are in it

    committed -> promoted   1,788 of 1,798 points moved
                            median 0.026 of half-extent, p90 0.251, max 1.981
                            811 of them moved less than 0.02

**That is dominated by the vertex subsample, not by B5 or B6.** The hulls were
decoded again on this machine, so each marker snaps to a slightly different real
vertex. Reporting it as "B6 moved 1,788 markers" would be false.

    B6 alone, geometry held constant   118 points on 55 of 167 ships
                                       median 0.074; 112 hulls unmoved
    B5 alone                           0 points, exactly as measured

Worst movers committed → promoted: Ironclad Assault 1.981, F8C Lightning 1.879,
Prowler Utility 1.764, Vanguard Warden 1.743, Corsair 1.669, Polaris 1.646,
Idris-M 1.521.

## The B6 controls, held against the promoted derivation

    crowding      118 -> 117 markers on 19 ships   NOT worse
    barely moves  55 of 167 ships moved at all
    typical move  median 0.074 of half-extent

Markers regenerated: 1,200 on 157 hulls. Count unchanged, port bindings
unchanged, 1,193 points moved and 7 did not. All eight B-run controls re-run and
green.

## One thing I got wrong

**I preserved `hardpoints_fleet.json` before regenerating and did not preserve
`placement_report.json` beside it.** The sandbox-era report is overwritten and
gone — including its list of the 7 hulls skipped with a stated reason, which the
MANIFEST records only as a count.

Rule 1 says move aside rather than overwrite, and I applied it to one file of the
two. The names are re-derivable by running the frame check over the candidate
hulls, and H5 needs exactly that answer, so it is folded in there rather than
left as a gap.

Next: H1, porting the holographic render into the live viewer.
