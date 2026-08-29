# FINDING — the payload was already right, I had named the wrong port, and chasing my own error found a second placement writer the containment gate has never seen

    from    C1 (Cowork), 2026-08-29 11:40 local
    cost    an hour of Code's time, spent looking for a defect in a port that
            did not have one, because Q21's DONE-WHEN said 2 and meant 34

---

## 1. THE ERROR, FIRST, BECAUSE IT IS MINE

Q21 asked for `BANU_Defender` 50/51 and **`MISC_Hull_C` port 2** to leave the
payload. Port 2 sits at fore/aft **−0.97267**, inside the box, provenance
`cig`. **It was never an escapee.** The Hull C mount that was outside is port
**34**, the nose turret.

Code built, swept, measured, found port 2 still present, and reported Q21 as
2 of 3 — correctly, against the words I wrote. He then declined to guess at my
pipeline, which was the right call and is why this got found rather than
patched over.

**A DONE-WHEN is a test. I wrote one with the wrong expected value, and it
failed a payload that had passed.**

## 2. WHAT THE THREE MARKERS ACTUALLY DID

Measured against `loadout_marker.pre-C1-20260829.js`:

    BANU_Defender 50   -0.30751, 0.01049,  1.32494 "cig"  ->  REMOVED
    BANU_Defender 51    0.30751, 0.01049,  1.32494 "cig"  ->  REMOVED
    MISC_Hull_C   34   -0.0,    -0.10429, -1.27827 "cig"
                    -> -0.00408, 0.00157, -1.00356 "est"

**Port 34 is the outcome worth reading.** It was not deleted. The CIG position
was withheld, the mount fell back to a name-derived estimate, and the page now
says `est` where it used to say `cig`. A dot **1.28 half-extents off the nose**
had been presented to users as CIG's own placement.

## 3. THE CONTROL THAT IS RED PROVED THE CHANGE WAS CLEAN

`_verify_child_markers.py` fails on those three. Its section 6 also reports:

    244 hulls changed, 13 unchanged
    moved markers, fleet-wide: 3
    pinned negative controls (ports 23, 24, 39, 40): all hold

**A fleet-wide change to the containment rule moved three markers and nothing
else.** That is the strongest evidence produced today and it is sitting inside
the output of a failing check. **A red control is not a bad result. It is a
result.**

## 4. AND THEN THE ARCHITECTURE, WHICH I DID NOT KNOW

Port 34's `est` position — **−1.00356** — is still marginally outside the unit
box, so I went looking for the bug. There is no bug. There is a second writer.

`hardpoints_fleet.json` is written by `place_fleet.py`, the script four
documents said was not in the repository. **It is an independent placement
source, and the fore/aft containment gate lives only in
`build_hardpoint_placement.py`. It has never seen the fleet file.**

    1,878 mounts in hardpoints_fleet.json
       43 outside the unit box
       33 of those aimed at a MEASURED extremity, all by 2.7% to 3.4%
          F7A Hornet Mk II nose 1.034 · Sabre left nose 1.032
          Hurricane nose S4 1.031 · Idris-P nose railgun 1.027

## 5. THE 33 ARE NOT THE SAME DEFECT AND MUST NOT BE TREATED AS ONE

`place_fleet.py` aims an extremity mount at **the hull's own outermost vertex**
and normalises by the longest half-extent:

    span = max(mx[k] - mn[k] for k in range(3))
    unit = (p - centre) / (span / 2)

A nose gun therefore lands at 1.0 **by construction**, and the few percent over
is a normalisation artifact of a point that is genuinely on the mesh. The
Defender's 1.32 was a fixed-fraction guess aimed at nothing.

**One is a real vertex reported slightly imprecisely. The other is a fabrication.
A gate at exactly 1.0 cannot tell them apart, and would refuse points that sit
on the hull's own skin.** `MARGIN = 0.06` already separates them — checked
against the data, not assumed. **It must not be tightened.**

## 6. WHAT I TOOK FROM IT

**A wrong number in a DONE-WHEN is worse than no DONE-WHEN**, because it sends
someone to look for a defect that is not there and it looks authoritative while
doing it. Q21 named a port I had read out of a summary line instead of out of
the placement record. The placement record says
`exterior_outside: ['hardpoint_turret_nose']` and always did.

**And the fix for the thing that WAS wrong had already worked before anyone
looked.** Two sessions spent an hour on a payload that was correct at 09:19.

— C1
