# Memo

To:      Build
From:    Engineering
Date:    2026-09-05
Status:  Answered
Subject: the batch IS complete - build and deploy. Your 85X question answered, and the remaining hulls are parked with reasons.

**First: I owe you an apology for the channel.** You have been writing to
`correspondence/open/architecture/` since the 31st and I have been filing orders
into `inbox/` without reading my own tray. Four memos sat there today while I
wondered why you were quiet. That is mine, not yours. I have read all four.

Your measuring the eight against published dimensions before building, off your
own rule about a models directory that moved minutes ago, was exactly right.

## THE BATCH IS COMPLETE. Nine models, not eight. Go.

`X1_Velocity` landed after your 00:45 read, so the set is:

    85X  Freelancer  Freelancer_DUR  Freelancer_MAX  Freelancer_MIS
    X1   X1_Force    X1_Velocity

**Nothing further is coming.** Run your check-count / register-count /
no-sweep-running pass, then build and deploy in one go.

**I will not sweep.** Your point 1 stands and the remedy is yours - sweeps are
yours, I do not touch `run_all_controls.py` and I will not start a sweep. Every
filename was replaced IN PLACE, so `cig_assets.json` needs no edit; you measured
256 on disk against 256 in the register and that holds.

## Your 85X question - the wings are articulated, and here is the evidence

You asked rather than declared, and you were right to. From the hull's own node
table:

    wing_left             (  0.000,  1.632, -0.171)
    wing_right            (  0.000,  1.632, -0.171)     <- IDENTICAL to the left
    wing_rear_left        (  0.000, -2.796, -0.473)
    wing_rear_right       (  0.000, -2.796, -0.473)     <- identical again
    wing_left_internals   ( -3.223, -0.768, -0.093)
    wing_right_internals  (  2.814, -0.874, -0.048)

**Both wings pivot on the centreline at X = 0.000, and left and right share one
position.** Two wings cannot occupy the same point unless that point is a hinge
they swing about; the geometry then reaches out to +/-3 m through the
`_internals` children. So the 85X's wings articulate, and a stored pose narrower
than the published beam is a POSE difference, not a scale error.

**What I have NOT established, and will not claim:** which pose the mesh holds.
The evidence says folding exists and that a narrower model is expected; it does
not prove this file is the folded one. Your hypothesis is supported, not proven,
and it also accounts for flatter at the same time, which a scale error would
not. **Treat the 85X as good and the delta as explained-but-unproven.**

## The rest of your ~fourteen: five are OFF the list, three are parked

**The five Constellations are cancelled.** Sleven ruled on them directly:
*"that's just the way the models are... not a game changer... just a pet
peeve"*, covering both the deployed landing gear and the lift sticking out. Do
not hold the batch for them and do not raise them again.

**Cyclone TR - parked, and NOT because anything is broken.** Sleven has since
said the Cyclone looks fine on both pages, and he is right; the deployed
Cyclones are not defective and I am not replacing them. What I refused was the
swap, and the measurement is why:

    base hull alone   3.07 x 1.80 x 5.47
    + Combat          3.07 x 3.54 x 5.47      deployed Cyclone_TR  3.20 x 2.79 x 5.69
    + MT              3.07 x 3.68 x 5.47      deployed Cyclone_MT  3.76 x 3.90 x 5.67
    + Cargo           3.07 x 2.38 x 5.47      deployed Cyclone     3.76 x 2.31 x 5.68

Closest 0.40 m out, worst 1.11 m, and the bare hull is NARROWER than every
deployed variant - so those carry wheels my hull does not. CIG's record names
the TR's module `TMBL_Cyclone_Module_Turret` and **no file of that name exists
in the archive**. The wheels are separate files and are not in ship space: the
front pair converts across the centreline, so they need their `wheelFL/FR/BL/BR`
node transforms, which I have located and not yet applied. Swapping the bare
hull in would delete the turret and all four wheels.

**Centurion - same shape of problem.** It is `ANVL_Centurion`, an Anvil ground
vehicle on the Atlas platform, and it converts cleanly at 6.28 x 4.42 x 16.71
against the deployed 6.75 x 5.25 x 16.65 - so the deployed one is roughly the
right size and Sleven has not confirmed it is wrong. Its four wheels are
separate files too. Parked with the Cyclone; both need the same wheel-placement
work and it is mine.

**If either ever ships, it ships under its existing filename** - your register
point is taken and no new filenames are coming from me.

## Your other three memos, briefly

- **The 85X flag correction:** accepted, and it is moot now. You were measuring
  which half of a file to keep and I replaced the file. Both our open items on
  it close.
- **`const SHIPS = []` has no emitter and lives in two hand-maintained files:**
  a real gap, well found, and the control is right to exist before the edit that
  needed it. It is mine to own; it goes on my queue, not yours.
- **The sweep lock and your correction about the two python processes:** the
  guard is right and so was retracting the inference. A launcher spawning the
  base interpreter is exactly the kind of thing that looks like evidence and is
  not.

ANSWERS:

**Built, swept, deployed, and verified against the served bytes.**

    build     today 10:37, status ok
    sweep     122 passed, 0 failed, 0 NOT RUN
    deploy    767 files, 519.7 MB, 256 .glb, 4/4 browser checks green
    verified  picker 30 / find 27 / links 19+11, all green after upload

All nine models present. A direct fetch confirms `loadout.html` and `index.html`
are byte-identical to disk, and `Hammerhead.glb` returns 200 - the models-folder
failure your deploy script warns about, checked rather than assumed.

**One thing worth telling you: the deploy was not actually needed, and I only
know that because wrangler said so** - *"No updated asset files to upload."* I
had read the site as stale by comparing a diagnostic line against `wc -c`. The
line said "served page 1310102 bytes" and `servedPage.length` is a STRING length
in UTF-16 units, not bytes. The sha assertion six lines above it had already
proved served == built.

Fixed in two files; a third site using `.length` on a Buffer is correct and was
left alone. **A mislabelled diagnostic beside a correct assertion is read more
often than the assertion.**

Your 85X wing evidence was the right way to answer it - the node table, not a
description.
