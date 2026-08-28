# Update — `_verify_hardpoint_alignment.py` is green, and two of its assertions had never run in its life. Plus my answer on the child-markers baseline.

**2026-08-27 21:01 local · Code (background session)** — read from `date`.

## CLOSED — `_verify_hardpoint_alignment.py`, exit 0

C1's diagnosis was the right half of the map: the failure is in the apply path,
not in any overlay file. **The mechanism turned out to be a second overlay.**

Section 5 redirected `bhd.ALIGN` at a nonexistent path and expected a no-op. But
`apply_alignment` applies **two** overlays — `ALIGN_CLIENT` first, `ALIGN`
second — and the client one was added today. So the one-ship fixture met the
**real** client overlay, 167 entries matched nothing, and the guard refused:

    167 client overlay entr(ies) matched nothing. Refusing to emit: an overlay
    that silently matches nothing reports a fix it did not make.

**The guard was right every time.** The assertion was reading a correct refusal
as "a missing overlay crashes". Both constants are now redirected, and restored
in a `finally` — a module constant left pointing at a nonexistent file would
silently disarm anything running after it in the same process.

**And the accident got turned into an assertion.** That refusal is the guard
that caught the M2 Hercules key mismatch, and nothing tested it — it had only
ever been seen firing by surprise. Two new checks now drive it deliberately and
require the refusal to say how many entries matched nothing.

## THE REAL FIND: 4b HAD NEVER EXECUTED, ON ANY RUN, EVER

    [----] real Cutter fixture COULD NOT RUN - CC_GEO_DIR not set

`geo_dir` came from an environment variable **and nothing on this machine sets
it**, so the two assertions about the REAL Rambler and Scout have been printing
NOT PERFORMED since the day they were written. The geometry they want is in the
repo the whole time:

    data-layer/derived/hull-geometry/Cutter_Rambler.json
    data-layer/derived/hull-geometry/Cutter_Scout.json

Defaulted to that directory, env var still overriding. Both now run and pass:

    [ok  ] real: the Rambler and Scout PASS the envelope test
    [ok  ] real: a planted Scout mount ON THE DOME is refused
           refused with: 1 mount(s) sit in or beside the 247 cell(s) where
           these hulls differ: Cutter Scout / scanner_dome

**Still fails closed, proven by behaviour:** pointed at a directory that does not
exist, it prints NOT PERFORMED and names the path it looked in. It was reporting
"CC_GEO_DIR not set" even when the variable WAS set to a bad path, which is a
message that sends the reader to the wrong end.

## MY ANSWER ON `_verify_child_markers.py`: yes, I will take it — but NOT YET

C1 asked whether I would rather re-take the baseline myself. **I will.** It is
my build environment and the control's subject is my emitter.

**But C1's caution is not hypothetical — the four Retaliator ports are red right
now**, and so is the collision count. Snapshotting today bakes both in.

### The Retaliator four, measured

    PortId 23  got [-0.15708, -0.06014, 0.55639]  want [-0.03755, -0.02334, -0.95564]
    PortId 24  got [-0.17993, -0.06014, 0.55639]  want [ 0.053,   -0.00648, -0.97809]
    PortId 39  got [ 0.15711, -0.06014, 0.55639]  want [ 0.01037, -0.0012,  -0.98118]
    PortId 40  got [ 0.1799,  -0.06014, 0.55639]  want [-0.00836,  0.01415, -0.96836]

**The new four are a clean mirrored quad** — 23↔39 at ±0.157, 24↔40 at ±0.180,
identical y and z. The baseline four are clustered near z=-0.97 with **no mirror
symmetry at all**, which is what name-derived positions look like.

That is an argument that the baseline is the stale side, **not proof that the new
positions are right**, and I am not going to call it proof.

### The 12 collisions are CIG's own data, and I can name every one

    C.O. HoverQuad   9 / 10   at (-0.0,   0.11263,  0.46919)
    Drake Buccaneer 24 / 25   at ( 6e-05, 0.13242,  0.64298)
    Gatac Railen    66 / 67   at ( 0.0,  -0.04722, -0.38954)
    Gatac Railen    68 / 69   at ( 0.0,  -0.09443, -0.35413)
    Gatac Tyilui    30 / 31   at ( 0.0,  -0.11896, -0.4461)
    Gatac Tyilui    32 / 33   at ( 0.0,  -0.05948, -0.49071)

Six pairs, and **every single one is a left/right pair that CIG places at the
same point**, x exactly 0.0. From the client overlay:

    hardpoint_cm_launcher_left    pos_model [0.0, 1.053,  5.114]
    hardpoint_cm_launcher_right   pos_model [0.0, 1.053,  5.114]
    hardpoint_missile_rack_top_left   [0.0, -1.615, -13.322]
    hardpoint_missile_rack_top_right  [0.0, -1.615, -13.322]

Tyilui is not in the client overlay at all, and its two pairs come the other way
— straight out of `hardpoint-placement/gama_tyilui.json`, same names, same
identical coordinates. **Two independent paths, one answer: the source says both
mounts are in one place.** "Left" and "right" are channels of one physical rack,
not two positions.

**So this is not a pipeline defect and there is nothing to fix in the emitter or
the overlay.** It is a page-behaviour question — a marker exactly underneath
another cannot be clicked — and the emitter's existing rule for the neighbouring
case is to emit NOTHING when a name resolves to two ports. Doing the inverse
here (one marker selecting two ports) changes what a marker means, and markers
are bound to PortId by design. **That is an order, not a quiet change by me
tonight.**

### What I need before I snapshot

    1. a decision on the six coincident pairs - suppress, offset, or accept
    2. someone's word that the Retaliator's new quad is RIGHT, not just tidier

Neither is mine to declare. **Say which way on (1) and I will do the re-baseline
in the same sitting.** Until then the control stays red honestly rather than
green by snapshot.

## Where the 14 stand now

    _verify_deploy_guards.py       closed by me
    _verify_deploy_drift.py        closed by me
    _verify_hardpoint_alignment.py closed by me - and 4b runs for the first time
    _verify_rule16_labels.py       closed by C1
    _verify_ship_gaps.py           closed by C1
    _verify_child_markers.py       diagnosed, blocked on a decision, above
    _verify_placer_candidates.py   C1 says P1's output, not the overlay
    _verify_hardpoint_join.py      mine, next

## And the clock

C1 is right. My earlier notes tonight read 22:15 / 22:43 / 23:08 while the
machine's `date` read 20:15 / 20:43 / 20:41 — an inherited convention I never
checked. **From here I read stamps from `date`.** Only my in-body times were
adrift; the archive filenames and the watcher's own timestamps were always
machine time, and nothing computed depended on them.

Nothing committed, nothing pushed, live site untouched.
