# Update — FINAL marker numbers. Ignore the counts in my two earlier notes; these are the ones on disk.

**2026-08-27 20:20 local · C1** — supersedes every count I have sent today.
The instruction has not changed: build and deploy testing.

## The three lines to read in the build output

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 955 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into ... loadout.html ...

**30 and 955.** My earlier notes said 29/952 and then 30/939 — both were written
mid-work and both are wrong now.

## What changed since this morning

**The acceptance test was judging a frame nobody renders.** It measured each
hull's mounts against its bounding box as the file stores it, while `cc_viewer`
recentres every hull on that box before drawing it. **71 of 258 models are not
centred on their own origin.** The M2 Hercules is 13.11 units off; its A2 and C2
siblings are not — same base hull, same 149 ports, same scale to four decimals,
and only the M2 was refused at 14 of 15 mounts outside. In the frame the viewer
draws: 140 of 149, the C2's number exactly.

The four Constellation variants are the corroboration: three failed identically
at 3 of 22 and the Aquila passed, because the Aquila's model carries a 2.9-unit
baked offset the others do not. They agree now.

**Two more defects fell out of looking:**

- **The same ship was placed twice under two spellings.** `ANVL_Hornet_F7A_MK1`
  from its transform file and `anvl_hornet_f7a_mk1` from the ships.json row -
  the collision guard compares exact strings, so both survived, both wrote the
  same file, second won. Manifest said 182 ships for 180 files. Same for
  `ESPR_Prowler_Utility`. Claims are folded to lower case now.
- **The overlay reads the placement DIRECTORY, not its manifest** - so a hull
  refused by a new run kept its file from an old one and kept being emitted. The
  run now reconciles its own directory and **exits fatally if it cannot**,
  naming the files. On this Linux mount deletion is blocked, so I moved 93 stale
  files to `_to_delete/hardpoint-placement-stale-2026-08-27/` - **worth a look
  before you delete them**, but nothing current depends on them.

## Two models are broken and it is not our pipeline

    Avenger_Stalker.glb   [ 1.40,  0.49,  1.91]   <- a tenth the size
    Avenger_Titan.glb     [14.00,  5.40, 19.52]       of its own siblings
    Aurora_SE.glb         [87.58, 38.93, 18.50]   <- 87 wide
    Aurora_CL/ES/LN/MR    [ 8.22,  4.35, 18.52]       against 8.2

Not fixed by me and not blocking anything - recorded so it is not rediscovered.

## Numbers, verified without a build

    placement                 146 converted, 137 passed, 9 failed
    overlay                   93 hulls / 955 ports
    client fleet records      30 hulls / 2,612 ports, 0 collisions
    overlay entries matching nothing                        0
    client model files the ship page references         30/30
    client model files shadowing an existing record         0
    direct markers from the client records                304
    classes emitting zero markers                           0
    ship page, all markers on CIG coordinates    163 -> 165

M2 Hercules 12 dots on a ship that had no marker record at all. Mantis 6.

## New check, runnable without a database

    python checks/_verify_placement_gate.py

Exits 0. Three broken frames plus a negative control.

**It has now reverted two of my own changes.** A proportional gate lets a
transposed axis through on every hull tested; and expanding every base hull to
its name-variants placed 75 more hulls with a 100% pass rate, which turned out
to mean containment cannot see a wrong airframe at all - a Gladius's mounts fit
inside a Hammerhead. Both reverted. Full working in
`docs/FINDING_the-acceptance-test-was-judging-a-frame-nobody-renders-2026-08-27.md`.

**The conclusion worth carrying:** the 96 ship-page classes still on name-derived
markers **cannot be reached by name-based inheritance.** They need their own
`.cga` decoded out of Data.p4k. Measured, not assumed.

Nothing commits or pushes without Sleven's go-ahead.

— C1
