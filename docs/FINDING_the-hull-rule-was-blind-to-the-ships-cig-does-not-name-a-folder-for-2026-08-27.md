# FINDING — the hull rule found 120 of 18,891 .cga entries and was exactly right about every one of them. It was also blind to fifteen ships whose geometry was sitting in the archive the whole time, because CIG does not always name a folder for the ship inside it. A second rule fixes it without a single fuzzy match, and it is an authority rather than a pattern.

    from      C1 (Cowork), 2026-08-27 evening
    changes   build_hardpoint_transforms.py
    adds      probe_hull_rule_rejects.py, probe_missing_hull_cga.py,
              probe_join_by_hardpoint_names.py  (read-only diagnostics)
    result    transforms 116 -> 135 hulls · overlay 93/955 -> 106/1,082 ports
              ship page 165 -> 181 classes fully on CIG coordinates
    status    BUILT. Deployed by Code.

---

## 1. WHERE THE 96 WERE STUCK

After the frame fix, 165 of the ship page's classes had every drawn marker on
CIG's own coordinates and **96 had none** — still carrying name-derived markers
that sit a median 0.488 of a half-extent from the real mount.

The obvious theory was that those ships have no decoded hull. **The question
nobody had asked was why the decoder stopped at 116.**

## 2. THE RULE, AND WHY IT IS GOOD

`build_hardpoint_transforms.py` takes the `.cga` whose stem equals **a
contiguous run of its own folder path**:

    DRAK\Vulture\DRAK_Vulture.cga              segs DRAK, Vulture
    DRAK\Cutlass\Black\DRAK_Cutlass_Black.cga  segs DRAK, Cutlass, Black
    ANVL\Carrack\Exterior\ANVL_Carrack.cga     "anvl_carrack" is a run

Exact equality, no fuzzy matching. It is a good rule — **120 accepted out of
18,891 entries, and it is right about all 120.** The archive is overwhelmingly
furniture: bunk beds, dashboards, toilets, lockers, escape pods. A pattern loose
enough to catch the missing hulls would catch those too.

## 3. WHAT IT CANNOT SEE

    AEGS\Sabre\AEGS_Sabre_Raven.cga            segs AEGS, Sabre
    MISC\Freelancer_v2\MISC_Freelancer.cga     segs MISC, Freelancer_v2
    ORIG\300_Series\ORIG_300I.cga              segs ORIG, 300_Series
    AEGS\Idris_Frigate\Exteriors\AEGS_Idris.cga

**Every one is a hull. None equals any run of its folders.** CIG names the
folder for the family and the file for the ship, and the two do not always meet.

Measured across the whole archive, the rule rejects 18,771 entries and
**1,515 of them are named for their own ship and then something more** — the
shape both a variant and a part have. Reading that list by eye is not a method.

## 4. THE SECOND RULE IS A LOOKUP, NOT A PATTERN

**Exact equality against CIG's own `ClassName` column in `ships.json`.**

Not a name pattern. Not a similarity score. A membership test against the list
of ships CIG publishes. It cannot admit a prop, because **there is no ship class
called `aegs_hab_bunkbed_sq_player`** — and a stem that merely resembles a class
name still matches nothing.

    folder rule     120 candidates
    class-name rule  19 more
    ------------------------------
                    139, of which 135 resolve to a real header

The two ambiguous cases are **dropped and named, never picked**: `AEGS_Javelin`
and `GLSN_Basher` each have two paths claiming the name, one of them under a
`dmg` folder. A damage-state model is not a near miss to be repaired.

**Where there is no ships.json snapshot the rule is OFF and the run says so out
loud** rather than quietly returning the smaller answer.

## 5. WHAT IT BOUGHT

    transforms      116 hulls -> 135
    placement       146 converted -> 160 · 137 passed -> 150
    overlay         93 hulls / 955 ports -> 106 hulls / 1,082 ports
    ship page       165 classes fully on CIG coordinates -> 181

Newly on real coordinates: **the whole Freelancer family** (base, DUR, MAX,
MIS), **Cutlass Black and Red**, **Constellation Aquila and both Phoenixes**,
**300i**, **Sabre Raven**, **Vanguard Hoplite**, **Fury LX**, **MPUV 1T**.

## 6. AND THE 4.10 SNAPSHOT CAME IN UNDERNEATH IT

Code's 4.10 clone finished mid-session. `build_hardpoint_placement.py` takes
the newest snapshot by design, so **this run scaled every hull against 4.10
lengths rather than 4.9** and the manifest's `dimensions` field now points
there. Nobody chose that; the newest changed. Acceptance still passes 150 of
160, so nothing moved badly — **but a provenance change nobody decided is worth
saying out loud rather than leaving in a diff.**

## 7. WHERE IT STOPS, AND WHY I STOPPED THERE

91 classes still have no CIG hardpoints. Measured, not guessed:

    an exactly-named .cga exists and is now decoded          8
    exists but is ambiguous (Javelin)                        1
    NO exactly-named .cga anywhere                          82

**For those 82 the geometry exists and nothing says which hull is theirs.**
`ANVL_Pisces.cga` is in the archive while the ship page calls the ship
`ANVL_C8_Pisces`; `ANVL_Lightning_F8.cga` is there while the class is
`ANVL_Lightning_F8C`. ships.json carries no geometry path — I checked every
field on the row.

**Matching them by name is the fuzzy matching this project has banned twice.**

So I tried a structural join instead: a class's weapon ports carry CIG's own
`HardpointName`, and that string IS the node name in the `.cga`. If every one of
a class's port names appears in exactly one decoded hull, that hull holds its
mounts — CIG's identifiers deciding, not the filename.

**It yields four matches and two of them are junk:**

    GRIN_ROC       -> MISC_Prospector    (1 port - a mining laser name they share)
    GRIN_ROC_DS    -> MISC_Prospector    (1 port)
    ORIG_X1_Force  -> ORIG_X1            (3 ports)
    ORIG_X1_Velocity -> ORIG_X1          (2 ports)

A one-port set matching proves nothing. Partial coverage looks far more
promising — `ANVL_C8_Pisces` 6 of 8 in `ANVL_Pisces`, `AEGS_Sabre_Comet` 8 of 11
in `AEGS_Sabre`, `MISC_Fury_Miru` 14 of 16 in `MISC_Fury` — **but turning that
into a rule means choosing a coverage threshold, and I have no way to validate
one.**

**That is exactly the trap I fell into twice already today.** The acceptance
test cannot referee it: containment is one-sided, so a wrong hull that is
merely larger passes, and rescaling each class by its own length erases what
little discrimination remains. I would be shipping dots I could not check.

**So it stops here, deliberately, with the measurement written down.** What
would settle it is a second independent signal that has to agree with the
structural one — the two models' own geometry, or something in CIG's part tree
that names a hull. Neither is a five-minute job and neither should be guessed
at.

## 8. What I checked and what I did not

**Checked:** all 18,891 `.cga` entries under Ships against both rules; the
reject list grouped by shape; every one of the 91 remaining classes for an
exactly-named file; every ships.json field on a sample row for a geometry path;
the structural hardpoint-name join across all 137 decoded hulls; the placement
directory against its manifest (160 and 160, zero stale); overlay entries
matching nothing (0); client records colliding with existing ones (0); and the
marker-emitter join port by port (304 markers, zero classes emitting none).

**Did NOT check:** whether the Javelin's non-`dmg` path is the right one — two
paths claim the name and refusing is the standing rule. Did not resolve the 82.
Did not build or deploy; the build needs PostgreSQL and that is on the project
machine.

## 9. AND THEN THE OTHER HALF: NINE OF TEN REFUSALS WERE A POSE, NOT A FRAME

With the hull rule fixed, ten hulls still failed placement. Reading *which*
mounts were outside changed the picture entirely:

    Constellation   gun_laser_top_left/right, turret_base_upper
                    0.53-0.71 above a 13.2-unit-tall hull   <- the top turret
    Spirit A1       turret_rear, 0.12 above 8.6             <- 1.4%
    Defender        both missile racks, 0.28 below 5.9
    Reliant         both wing-tip guns, 1.01 beyond 11.1    <- the wings move

**These are stowed-pose mismatches.** The GLB is one pose and the mount is
where the game puts it. Refusing the whole hull threw away nineteen good
Constellation ports to avoid drawing three arguable ones — and the fallback is
the name-derived marker set, a median 0.488 of a half-extent from the mount.
**The refusal was worse than the thing it refused.**

### The gate did not loosen. A second signal was added.

Section 5 of the frame finding records why a proportional gate is dead: a
transposed axis displaces only about a sixth of the mounts, so no count of
offenders can separate a pose from a frame error.

**So the count was not asked to.** Exterior left/right pairs must all mirror,
measured on the CONVERTED cloud in the viewer's own frame:

    hull            as-is    transposed    scaled x4
    Gladius         13/14       0/14         13/14
    Hammerhead      21/22       0/22         21/22
    Constellation     8/8        0/8           8/8
    Sabre             9/9        0/9           9/9

**A transpose destroys it completely. A uniform scale does not touch it.** That
is exactly the complement of containment, which catches a wrong scale and
cannot reliably see a transpose. Two signals, two different failure modes,
neither derived from the other.

    frame proven   -> out-of-box mounts withheld individually, hull placed
    not proven     -> any mount outside refuses the whole hull, as before

### The check refuted me a second time, mid-build

The first version was `out == 0 or proven`. `_verify_placement_gate.py`
immediately failed it:

    AEGS_Eclipse   PASSED   59 of 59 exterior outside   (a full-hull offset)
    AEGS_Sabre     PASSED   24 of 63 exterior outside   (a 4x scale)

**Mirroring survives a uniform scale and a uniform offset.** Of course it does —
it answers "are the axes right", not "how big" or "where". A proven frame is not
a licence to ignore containment, and I had just written a rule that said it was.

Bounded by an absolute count, and a count rather than a fraction because the
thing it separates does not scale with the hull:

    stowed-pose mismatches observed     1, 1, 2, 2, 3, 3, 3, 3
    smallest frame error observed      23     (4x scale on the Gladius)
    a full-hull offset                 every mount

**Four sits BELOW the smallest defect by nearly an order of magnitude** — which
is the difference between this and the proportional gate, whose threshold sat
above the defect signal. It is calibrated on observed data and the control is
what keeps it honest: three broken frames go through the real rule and every one
must still be refused. If a future hull needs a fifth withheld mount, the honest
move is to look at that hull.

### Result

    placement    146 -> 160 converted · 137 -> 157 passed · 3 failed
    overlay      93 hulls / 955 ports -> 112 hulls / 1,164 ports
    ship page    165 -> 182 classes fully on CIG coordinates

Nine hulls withhold individual mounts; every one has a perfect mirror. The three
remaining failures each carry a reason anyone can check without me:

    ARGO_MPUV_Transport   no exterior mount at all - nothing could have failed
    VNCL_Glaive           2 of 4 exterior pairs mirror - frame not proven
    VNCL_Scythe           1 of 4 exterior pairs mirror - frame not proven

**The two Vanduul are the interesting refusal.** Their mount names say left and
right and their geometry does not agree. That is not a pose question and it is
not something to wave through — it is the next thing to look at on this front.

## 10. THE TWO VANDUUL ARE NOT A BUG. THEY ARE ASYMMETRIC SHIPS.

`VNCL_Glaive` and `VNCL_Scythe` are refused because their exterior pairs do not
all mirror — 2 of 4 and 1 of 4. **That refusal is correct under the rule and the
reason is not a decode error.** Their decoded transforms, in CIG metres:

    GLAIVE                          X         Y         Z
    countermeasures_left       -2.777    -3.593    -0.112
    countermeasures_right      +2.777    -3.593    -0.112     <- exact mirror
    gun_nose_left              -0.601    10.590    -3.187
    gun_nose_right             +0.609    10.590    -3.187     <- exact mirror
    gun_wing_left              -7.500    17.933    -2.000
    gun_wing_right             +8.344     5.037    -2.214     <- 12.9 m apart in Y
    missile_rack_left         -13.503     6.761    -5.094
    missile_rack_right         -6.734     3.109    -1.567     <- NEGATIVE X

**The Glaive's "right" missile rack is on the left side of the ship.** Its wing
guns sit thirteen metres apart fore-and-aft. The Scythe is the same shape of
thing: nose guns mirror exactly, everything else does not.

**And the decoder is fine, because `VNCL_Blade` mirrors perfectly** — every one
of its four exterior pairs negates in X and agrees in Y and Z, decoded by the
same code in the same run. A broken decode does not fix itself for one Vanduul
hull and break for the other two.

**These ships are genuinely asymmetric, which is what Vanduul ships are.**

### What that costs and why I left it

The rule refuses the Glaive whole over **one** mount outside the box, losing
nine good ports. That is the same complaint that motivated the whole
withholding mechanism, and here it is unresolved.

**The mirror test cannot prove the frame of a ship that is not symmetric**, and
the two pairs that DO mirror on the Glaive would be enough to prove the lateral
axis — a transpose breaks those too. So "at least one exact mirror" would admit
it. But the transposed control shows a transpose can still leave **1 of 39**
pairs matching by accident on the Reclaimer, so "at least one" is not safe, and
picking any number between one and all is a threshold on a four-pair sample.

**So it stays refused, and this section exists so the next person reads
"asymmetric ship" rather than "broken decode" and does not go looking for a bug
that is not there.** What would settle it is a frame proof that does not assume
symmetry at all.

## 11. THE AUTHORITY I SAID DID NOT EXIST — AND I HAD LOOKED IN THE WRONG PLACE

Section 7 of this document says, in my words:

> *"ships.json carries no geometry path — I checked every field on the row."*

**I checked the row's top-level fields for a PATH. The answer is a NAME, one
level down, and it was there the whole time:**

    anvl_c8_pisces.json  ->  Parts[0].Name == "ANVL_Pisces"

**The root of CIG's own part tree names the hull the ship is built from.**

    classes carrying a root part name      309 of 318
    root name == the class itself          126
    root names a DIFFERENT hull            183, of which 164 were already decoded

It reaches every variant a name rule never could, because it is not a name rule:

    AEGS_Gladius_Valiant    -> AEGS_Gladius
    AEGS_Vanguard_Harbinger -> AEGS_Vanguard
    ANVL_C8_Pisces          -> ANVL_Pisces      no shared prefix at all
    RSI_Ursa_Medivac        -> RSI_Ursa_Rover   nor here
    GRIN_MDC                -> GRIN_MXC         nor here

**It replaced the `cls + "_"` prefix expansion rather than joining it.** That
prefix was a pattern standing in for exactly this fact.

**And it is safe where my earlier name-expansion experiment was not.** That one
sprayed a base's hardpoints across everything sharing its prefix and leaned on
an acceptance test that cannot tell a wrong airframe from a right one. This
needs no such test: only ports whose `HardpointName` exists as a NODE in that
hull are placed, so a module-specific mount on a Harbinger gets **no** position
rather than a wrong one. **The record decides membership; the geometry decides
placement.**

**The same names feed back one stage earlier.** A name CIG uses as a part-tree
root IS a hull name, whether or not any ship is called that — `AEGS_Idris` is
named by six ships and is no ship's own ClassName. Adding the root names to the
decoder's accepted set picked up `AEGS\Idris_Frigate\Exteriors\AEGS_Idris.cga`,
which neither earlier rule could see.

### One collision needed a tie-break, and it is evidence rather than preference

Widening the accepted set made `anvl_hornet_f7a` ambiguous — two paths, one of
which the folder rule accepts. **Dropping both lost a hull that was already
decoded, which is a correction making things worse.** The folder rule requires
the file's name and its LOCATION to agree; the class-name rule requires only
the name. So a folder-rule path beats a class-name-only one. **Two paths of
equal evidence are still dropped and still named** — the Javelin's two are both
folder-rule, one under `dmg`, and picking between them would be a guess.

## 12. AND HALF THE FLEET WAS PARKED IN A TREE NOBODY HAD LOOKED AT

Every hull this decoder had ever seen lives under
`Data\Objects\Spaceships\Ships\`. **Ground vehicles do not.**

    Data\Objects\Spaceships    23,083 .cga entries
    Data\Objects\Vehicles        1,762     <- never scanned

The hulls are sitting at the top of it:

    Vehicles\TMBL\storm\TMBL_Storm.cga
    Vehicles\TMBL\Nova\TMBL_Nova.cga
    Vehicles\ANVL\Ballista\ANVL_Ballista.cga
    Vehicles\ANVL\Atlas\Centurion\ANVL_Centurion.cga

The Cyclones, the Storm, the Nova, the Ursa, the Ballista, the Centurion, the
Spartan and the Lynx were all "no `.cga` anywhere" for that one reason.

`Spaceships` stays narrowed to its `Ships` subtree — the same tree also holds
Turrets, Seats, Rocket_Pods and Derelicts, and those are parts. The Vehicles
tree has no such level, so the segment walk now takes whatever follows the tree
root instead of looking for a fixed `Ships` folder.

## 13. WHERE IT ACTUALLY ENDS

    transforms   116 hulls -> 153
    placement    146 converted -> 284 · 137 passed -> 277
    overlay      93 hulls / 955 ports -> 167 hulls / 1,720 ports
    ship page    165 classes fully on CIG coordinates -> 245
                 91 with none -> 20

**The twenty, each with a reason anyone can check:**

    ARGO_ATLS family (8)    a POWER SUIT, under Characters\PowerSuit. Not a
                            vehicle hull and in neither tree.
    GRIN MDC/MTC/ROC (4)    decoded, and carry no exterior mount at all -
                            nothing there could have failed a check
    TMBL_Cyclone AA/MT/TR   their records name no decoded root
    AEGS_Javelin            two paths, equal evidence, one under `dmg`
    VNCL_Glaive, _Scythe    asymmetric ships - see section 10
    ARGO_MOTH, MISC_Starfarer_Gemini

Nothing in that list is a guess waiting to be taken. Each is a different reason
and none of them is "we did not look".

---

*C1, 2026-08-27. Fifteen ships were behind a rule that was right about
everything it looked at, and nine more behind a refusal that was worse than the
thing it refused. The check said no to me twice on the way.*
