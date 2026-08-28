# BUILD AND DEPLOY AGAIN. 112 hulls / 1,164 ports. This is the last one from me tonight.

**2026-08-27 19:58 local · C1** — read from `date`.

    client marker records added for 31 hull(s) the dataset had none for
    client hardpoint overlay: 1164 port(s) moved onto CIG positions

**Same rule as before: none of those may be zero, loadout.html must be in the
disclosure-CSS line, and the manifests on disk beat any number in this note.**

## What moved since your 30/955 deploy

Two changes, and the second one is the interesting half.

**1. The hull rule was blind to fifteen ships.** It takes the `.cga` whose stem
equals a contiguous run of its own folders — 120 of 18,891 entries, and right
about all 120. But CIG does not always name a folder for the ship inside it:
`AEGS\Sabre\AEGS_Sabre_Raven.cga`, `MISC\Freelancer_v2\MISC_Freelancer.cga`,
`ORIG\300_Series\ORIG_300I.cga`. Second rule added — **exact equality against
CIG's own ClassName list in ships.json.** An authority, not a pattern: it cannot
admit a prop because there is no ship class called `aegs_hab_bunkbed_sq_player`.
Javelin and Basher are ambiguous and are dropped and named.

**2. Nine of the ten remaining refusals were a stowed pose, not a bad frame.**
The Constellation's three offenders are the top-turret mounts, 0.53–0.71 above a
13.2-unit hull. The Reliant's are its wing-tip guns; its wings move and the GLB
is one pose. Refusing the whole hull threw away nineteen good Constellation
ports to avoid three arguable ones — and left the reader with name-derived
markers instead, which sit a median 0.488 of a half-extent out. **The refusal
was worse than what it refused.**

**The gate did not loosen.** A second, independent signal was added: exterior
left/right pairs must all mirror in the converted frame. A transpose destroys
that completely — 0 of N on every hull — and a uniform scale does not touch it,
which is precisely the complement of what containment can see.

## The check refuted me twice while I built this, and both are in the code

- **A proportional gate is not viable.** At "more than half outside", a
  transposed axis survives on every hull tested — ships are wider than they are
  tall, so the swap only displaces about a sixth of the mounts.
- **A proven frame is not a licence to ignore containment.** Mirroring survives
  a uniform scale and a uniform offset, so "proven" on its own let a 4x scale
  and a full-hull-length offset through on the Eclipse and the Sabre. The
  withholding is now bounded by an absolute count of 4 — pose mismatches run
  1 to 3, the smallest frame error observed is 23.

    python checks/_verify_placement_gate.py        exits 0

## Numbers

    transforms   116 hulls -> 135
    placement    146 -> 160 converted · 137 -> 157 passed · 3 failed
    overlay      93/955 -> 112 hulls / 1,164 ports
    ship page    165 -> 182 classes fully on CIG coordinates, 84 with none

The three that still fail, each with a reason anyone can check:

    ARGO_MPUV_Transport   no exterior mount at all - nothing could have failed
    VNCL_Glaive           2 of 4 exterior pairs mirror - frame not proven
    VNCL_Scythe           1 of 4 exterior pairs mirror - frame not proven

Nine hulls withhold individual mounts and every one has a perfect mirror except
the two Vanduul, which are refused whole for that reason.

## Verified

    placement directory vs manifest        160 / 160, zero stale
    overlay entries matching nothing                        0
    client records colliding with existing                  0
    client model files the page references              31/31

Testing only. Nothing to the live site without Sleven's go-ahead.

— C1
