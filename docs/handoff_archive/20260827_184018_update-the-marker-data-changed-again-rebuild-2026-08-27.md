# Update — the hardpoint data changed after my last two notes. Rebuild from current files, not from what I said earlier.

**2026-08-27 19:05 local · C1** — supersedes the port counts in my two earlier
notes. The instruction is the same: build and deploy testing.

## What changed

The acceptance test in `build_hardpoint_placement.py` was measuring each hull's
mounts against its bounding box **as the file stores it**, while `cc_viewer`
recentres every hull on that box before drawing it. So the test judged a frame
that is never rendered.

**71 of the 258 models in the payload are not centred on their own origin.** The
M2 Hercules is 13.11 units off; its A2 and C2 siblings are not. Same base hull,
same 149 decoded ports, same scale to four decimals — and only the M2 was
refused, at 14 of 15 mounts outside. Against the box as drawn: 140 of 149, the
C2's number exactly.

**The four Constellation variants are the corroboration.** Three failed
identically at 3 of 22 and the Aquila passed, because the Aquila's model carries
a 2.9-unit baked offset the other three do not. After the fix all four agree.

## The numbers to expect now

    hulls passed        138 -> 139   (gained M2 Hercules, Valkyrie, ARGO SRV
                                      lost Constellation Aquila, Spirit A1)
    overlay             93 hulls / 952 ports -> 93 hulls / 939 ports
    new fleet records   29 hulls / 2,486 ports -> 30 hulls / 2,612 ports

**So the build's own lines should now read 30 and 939, not 29 and 952.** My
earlier notes said 29 and 952 and they are out of date — the files on disk are
right, the notes were written before this.

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 939 port(s) moved onto CIG positions
    disclosure CSS: shared from _disc.css into ... loadout.html ...

It moves hulls in both directions on purpose. A frame correction that only ever
passed more hulls would be indistinguishable from a loosened threshold.

## There is a new check and it is runnable without a database

    python checks/_verify_placement_gate.py

Three broken frames — transposed axis, 4x scale, a full-hull-length offset —
plus a negative control that the unmodified hull still passes. It exits 0 today.

**It has already earned its place.** I also made the gate proportional, so a hull
with one or two mounts proud of a stowed-pose mesh would keep the rest of its
markers. That check refuted it in one run: at a half threshold **a transposed
lateral/vertical axis survives on every hull tested** — ships are wider than
they are tall, so swapping those axes only displaces about a sixth of the
mounts. That is the exact defect the gate exists to catch. Reverted.

Full working:
`docs/FINDING_the-acceptance-test-was-judging-a-frame-nobody-renders-2026-08-27.md`

## Verified before handing it over, without a build

    client records colliding with an existing fleet record      0 of 30
    client model files the ship page references                30 of 30
    client model files shadowing an existing record                   0
    overlay entries matching nothing                                  0
    direct markers the client records emit                          304
    classes emitting zero markers                                     0

Mantis 6 dots. M2 Hercules 12, on a ship that had no marker record at all.

Nothing commits or pushes without Sleven's go-ahead.

— C1
