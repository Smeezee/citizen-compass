# FINDING — the hardpoint acceptance test measured the hull where the file puts it, not where the viewer draws it. Seventy-one of 258 models are not centred on their own origin, and the M2 Hercules was refused for it while the C2 and A2 passed on identical data. Fixed. Then I tried to fix a second thing, and a control I wrote ten minutes earlier proved me wrong.

    from      C1 (Cowork), 2026-08-27 evening
    changes   build_hardpoint_placement.py, build_hardpoint_overlay.py
    adds      checks/_verify_placement_gate.py
    reverts   one change of my own, on the evidence of that check
    status    BUILT. Ships in the next build; nothing deployed by me.

---

## 1. THE SYMPTOM — one variant refused, its two siblings passed, on the same numbers

    crus_starlifter_a2   PASS    149 ports   scale 0.99602
    crus_starlifter_c2   PASS    149 ports   scale 0.99449
    crus_starlifter_m2   FAIL    149 ports   scale 0.99450
                         "14 of 15 exterior mounts land outside the hull"

Same base hull. Same decoded hardpoints. Same scale to four decimal places. One
refusal. **A difference that large with inputs that identical is not the data.**

## 2. THE CAUSE — the model, and it is a whole class

Reading the three models' bounding boxes:

    A2_Hercules.glb    extent 70.2 x 24.7 x 94.4    centre  0.12  0.05  0.05
    C2_Hercules.glb    extent 71.0 x 21.8 x 94.5    centre  0.00  0.08  0.00
    M2_Hercules.glb    extent 71.0 x 21.8 x 94.5    centre  0.01 13.11  5.58

**The M2's geometry sits 13.11 units above its own origin.** Its siblings do
not. And the acceptance test asked "is this mount inside `[box.min, box.max]`"
— a box that, on the M2, does not contain the origin the mounts are measured
from.

**`cc_viewer.frame()` recentres every hull before drawing it:**

    o.position.x -= c.x;  o.position.y -= box.min.y;  o.position.z -= c.z;

So the frame a visitor sees is the box **centred on the origin**. The test was
judging a frame that is never rendered.

Against the box as drawn: **M2 goes from 11 of 149 inside to 140 of 149 — the
C2's number exactly.**

**This is not confined to one ship.** Of 258 models in the payload, **71 sit
more than 1% of their longest span off their own origin**:

    Ranger RC     33%      Scorpius   26%      Ursa      21%
    Cyclone       20%      Tyilui   14.5%      M2      13.9%
    Arrastra    13.4%      85X      11.9%      Hull D     9%

The median across all 258 is 0.0016%, so most of the fleet was unaffected and
the old test was right about them. That is exactly why this survived.

## 3. THE CORROBORATION IS BETTER THAN THE ARGUMENT

I did not have to be believed about the frame. **Four Constellation variants
carry the same airframe**, and before the fix three of them failed identically
at 3 of 22 while the fourth passed:

    Constellation_Andromeda.glb   centre  0.000  0.000  0.000    FAIL 3/22
    Constellation_Phoenix.glb     centre  0.000  0.049 -0.001    FAIL 3/22
    Constellation_Taurus.glb      centre  0.000  0.529  0.001    PASS
    Constellation_Aquila.glb      centre  0.001  2.896  2.182    PASS  <- odd one

**The Aquila's baked offset was hiding three mounts its identical siblings
report.** After the fix all four agree. A change that makes four variants of one
hull stop disagreeing is being checked by something other than the person who
made it.

## 4. WHAT MOVED

    hulls converted   148        (unchanged)
    passed            138 -> 139
      gained          M2 Hercules, Valkyrie, ARGO SRV
      lost            Constellation Aquila, Spirit A1

**It moves hulls in BOTH directions and that matters.** A frame correction that
only ever passed more hulls would be indistinguishable from a loosened
threshold. Two hulls now fail that used to pass, because their offsets were
flattering them.

    overlay           93 hulls / 952 ports -> 93 hulls / 955 ports
    new records       29 hulls / 2,486 ports -> 30 hulls / 2,612 ports
                      (the M2 Hercules joins - 12 markers on a ship that had none)
    ship page         163 classes fully on CIG coordinates -> 165

**The viewer and the overlay were both already correct** and neither was
touched. I patched `cc_viewer.js` first, on the theory that `_hullOrigin`
should track the offset — then measured, found the mount cloud fits the
origin-centred box and not the raw one, and reverted it before it went
anywhere. The viewer's `{x: 0, y: sz.y/2, z: 0}` is right *because* the viewer
recentres the mesh.

## 5. THEN I BROKE THE GATE, AND A CHECK I HAD JUST WRITTEN CAUGHT IT

With the frame fixed, nine hulls still failed — but at 1 of 10, 1 of 12, 2 of
11, 3 of 22. **Small numbers, and the all-or-nothing gate was throwing away 19
good Constellation ports to avoid drawing 3 arguable ones.** Worse, the fallback
is the name-derived marker set, which sits a median **0.488 of a half-extent**
from the real mount. The refusal left the reader with something worse than what
was refused.

So I made the gate proportional — refuse above half, withhold individual ports
below it — and reasoned that the boundary was not tuned because the observed
failures cluster at 8–18% and the one frame error was 93%, with nothing between.

**That reasoning was fine and the conclusion was wrong.**
`checks/_verify_placement_gate.py`, written minutes earlier for exactly this
purpose, feeds the gate three deliberately broken frames. With the gate at half:

    transposed lateral/vertical axis   PASSED on 6 of 6 hulls
      Eclipse 10 of 59 outside · Hammerhead 24 of 97 · Redeemer 4 of 100
    wrong scale (x4)                   PASSED on 5 of 6 hulls

**Ships are wider than they are tall.** Swap those two axes and most mounts stay
inside the larger extent — a transposed axis displaces about a sixth of them,
and walks straight through a half threshold. **The transposed axis is the exact
defect this test exists to catch.** I had traded the gate's whole reason to exist
for three hulls of coverage.

Reverted. The gate is all-or-nothing again, and the check now encodes that rule
and passes: clean hulls accepted, all three broken frames refused.

**What would actually earn a per-port gate** is a test that catches a transpose
regardless of how many mounts it displaces — the *shape* of the mount cloud
against the shape of the hull rather than a count of offenders. Not built today.
Named so the next person does not re-derive the same wrong shortcut.

## 6. WHAT THE CHECK IS AND WHY IT DOES NOT IMPORT THE THING IT CHECKS

`checks/_verify_placement_gate.py` re-implements the gate rather than importing
it. Importing would make it agree by construction — rule 16. It carries a
**negative control** as well as three positive ones: the unmodified hull must
still pass, because a gate stuck on "refuse" proves nothing either.

It needs no database and no browser. Python and the placement output, nothing
else.

## 7. What I checked and what I did not

**Checked:** bounding boxes of all 258 models in the payload; the M2 against
its two siblings on identical inputs; the four Constellation variants; the full
before/after of the placement and overlay manifests; that no client record
collides with an existing fleet record (0 of 30); that all 30 model files are
referenced by the ship page and none shadows an existing record; that every
overlay entry still matches something (939 of 939); and the marker-emitter join
port by port — **304 direct markers, zero hulls emitting none.**

**Did NOT check:** whether the 71 off-centre models are off-centre in CIG's own
files or in whatever exported them — that is somebody else's pipeline and the
fix here does not depend on the answer. Did not build or deploy; I cannot, the
build needs PostgreSQL and that is on the project machine.

## 8. TWO MORE DEFECTS FELL OUT OF LOOKING, AND A THIRD THING I TRIED DID NOT WORK

### 8a. The same ship was being placed twice, keyed by two spellings of its name

`ANVL_Hornet_F7A_MK1` arrives from its own transform file; `anvl_hornet_f7a_mk1`
arrives from the ships.json row. **Same ship, two claims, keys differing only in
case.** The collision guard compares exact strings, so both survived it, both
were placed, and on a case-insensitive filesystem both wrote the same file with
the second silently winning. `ESPR_Prowler_Utility` the same.

The manifest listed **182 ships for 180 files** and nothing anywhere said so.
This is the silent-overwrite failure this file's own comment says has already
happened five times, arriving a sixth way. Claims are folded to lower case now,
which hands both to the most-specific-base rule that exists to decide them.

### 8b. The next stage reads the DIRECTORY, and the directory kept refused hulls

`build_hardpoint_overlay.py` iterates `os.listdir()` over the placement output.
So a hull this run refuses, but a previous run wrote, **keeps its file and keeps
being emitted** — the refusal is recorded in the manifest and has no effect. A
correction that reports success and changes nothing is worse than none.

It had already happened: an experimental run left **218 files against a manifest
of 182**.

The run now reconciles its own directory and **exits fatally if it cannot**,
naming the files. Not asserted — fired on purpose: a planted `zz_control_stale`
file was detected, could not be deleted on this mount, and the run stopped with
the filename rather than continuing. Deletion succeeds on the project machine;
the fatal path exists for the environments where it does not.

### 8c. Expanding every base hull to its name-variants — tried, measured, reverted

96 ship-page classes still carry name-derived markers and most are variants of
hulls already decoded: Gladius Valiant, Sabre Comet and Raven, the Vanguard
family, Carrack Expedition, the Hornet Mk II family. The expansion only ran for
a base with **no** ships.json row of its own, which looked like an accident of
which branch it was written in.

Removing that condition placed 75 more hulls, **and every one of them passed
acceptance.** That is the shape of a check that cannot fail, so I tested it:

    Gladius mounts in a HAMMERHEAD box     passed, 0 of 64 outside
    Gladius mounts in a RECLAIMER box      passed, 0 of 64 outside
    Gladius mounts in a SABRE box          passed, 0 of 64 outside
    Hammerhead mounts in a SABRE box       refused, 51 of 97

**Containment is one-sided.** It refuses mounts too big for the hull and never
mounts too small for it — and the pipeline rescales each variant by its own
published Length, which erases even that. "It passed acceptance" was never
evidence that a variant shares its base's geometry.

Gating instead on the two models' own bounding boxes — a livery is the same mesh
and its box matches — separated them properly:

    600i Executive Edition vs 600i Explorer   99.8%     Sabre Raven vs Sabre  37.5%
    Aurora Mk II vs the Aurora family         94.8%     Fury LX vs Fury       58.3%
    Avenger Stalker vs its own siblings       90.9%     Reliant Tana/Sen/Mako 82%

**Avenger_Stalker.glb measures [1.4, 0.49, 1.91] while the Titan, Renegade and
Warlock are [14.0, 5.4, 19.52]** — a tenth the size, and it was being placed.
**Aurora_SE.glb is 87.6 wide against 8.2 for every other Aurora.** Those are
broken models and worth someone's attention on their own.

But with that gate on, **the variants that survive are exactly the ones that
share the base's model file — which were already covered before any of this.**
The ships that need coverage are precisely the ones with their own distinct
geometry, and for those the base's hardpoints do not legitimately transfer. Net
effect: no coverage gained, and the Hercules family lost.

**Reverted whole.** The conclusion is worth more than the change: **the
remaining 96 cannot be reached by name-based inheritance at all.** They need
their own `.cga` decoded out of Data.p4k. That is the next piece of real work on
this front, and it is now a measured statement rather than an assumption.

---

*C1, 2026-08-27. One fix, two more defects found by looking, and two of my
own changes reverted by controls I wrote to test them.*
