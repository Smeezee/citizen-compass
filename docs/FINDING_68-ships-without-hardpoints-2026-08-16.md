# FINDING — 68 ships show a bare hull. Only 27 are actually missing data. **29 of them already have every hardpoint we need, sitting under a name that does not join** — including the entire Aurora line and all three Hercules.

    from      C3 (Cowork), 2026-08-16
    for       C1 + Sleven
    ask       "68 ships have no hardpoint data. Why not, one ship at a time,
              and which of them can be fixed?"
    method    joined testing/_deploy/models against ship_mounts.json,
              hardpoints_fleet.json, placement_report.json and ship_specs.json
              on Sleven's machine. Every ship checked individually.
    scope     research only. Nothing built, nothing changed, citizen-collector
              untouched.

---

## 1. The 68, sorted

    E  name mismatch - data exists on BOTH sides, keys do not join      29
    B  no mount data anywhere - genuinely absent                        27
    C  rejected by the placement step                                    7
    D  correctly zero - no conventional weapon mounts                    5
    A  mount data but no model                                           0

**"68 missing" is wrong in the direction that matters. 29 of them are a name
mapping away from working, and they are the ships people actually fly.**

## 2. GROUP E — 29 ships, already have their hardpoints

**Two distinct causes, both trivially fixable, neither needing new data.**

### E1 — the mount data uses CIG's full name, the model file uses the short one (12)

    model file                  mount data key            weapon mounts waiting
    Aurora_CL                   Aurora Mk I CL                    10
    Aurora_ES                   Aurora Mk I ES                    10
    Aurora_LN                   Aurora Mk I LN                    10
    Aurora_LX                   Aurora Mk I LX                    10
    Aurora_MR                   Aurora Mk I MR                    10
    A2_Hercules                 A2 Hercules Starlifter            41
    C2_Hercules                 C2 Hercules Starlifter            41
    M2_Hercules                 M2 Hercules Starlifter            41
    600i_Explorer               600i                              17
    Mercury                     Mercury Star Runner               17
    M50                         M50 Interceptor                    8
    C8R_Pisces                  C8R Pisces Rescue                  8

**That is 213 hardpoints already extracted and sitting on disk.** The Aurora is
the starter ship — the most widely owned hull in the game — and all five variants
are here. The Hercules line carries 41 mounts each.

### E2 — the model is a paint or edition, the mount data is under the base ship (16)

    Carrack_w_C8X                            -> Carrack
    Carrack_Expedition_w_C8X                 -> Carrack Expedition
    Caterpillar_Best_In_Show_Edition_2949    -> Caterpillar
    Caterpillar_Pirate_Edition               -> Caterpillar
    Cutlass_Black_Best_In_Show_Edition_2949  -> Cutlass Black
    Gladius_Pirate_Edition                   -> Gladius
    Hammerhead_Best_In_Show_Edition_2949     -> Hammerhead
    Reclaimer_Best_In_Show_Edition_2949      -> Reclaimer
    Valkyrie_Liberator_Edition               -> Valkyrie
    Mustang_Alpha_Vindicator                 -> Mustang Alpha
    F7C-M_Super_Hornet_Heartseeker_Mk_I      -> F7C-M Super Hornet Mk I
    Anvil_Ballista_Dunestalker               -> Ballista Dunestalker
    Anvil_Ballista_Snowblind                 -> Ballista Snowblind
    Argo_Mole_Carbon_Edition                 -> MOLE
    Argo_Mole_Talus_Edition                  -> MOLE
    Dragonfly_Black                          -> Dragonfly

**These are the ships Sleven already ruled on two days ago.** The
`DECISION_shared-hulls-are-fine-unless-the-shape-differs` ruling established that
a paint variant shares its parent's hull. **If the hull is the same, the hardpoint
positions are the same** — so the parent's placement is valid for the variant, by
the same reasoning that closed the duplicate-model question.

### E3 — one character (1)

    Khartu-Al.glb   vs   mount key "Khartu-al"

**Capital A against lowercase a.** 5 mounts, 2 weapons, 1,635 pilot DPS, all
extracted and waiting. This one is not a naming convention problem; it is a typo
that cost a whole ship.

## 3. GROUP C — 7 rejected in placement, and the report says exactly why

Six were thrown out by the **proportion check** — the guard added after the first
fleet run silently mangled 50 ships. It compares the model's shape against CIG's
published dimensions and refuses when they disagree:

    Clipper     err 0.66   model 49.5 x 13.0 x 27.2   published 26.5 x 21 x 18
    Defender    err 0.60   model 16.9 x  5.9 x 37.8   published 24.5 x 24.5 x 5
    Eclipse     err 0.54   model 36.9 x  4.0 x 20.5   published 24.5 x 24.5 x 5
    Nova        err 0.37   model  7.3 x  5.1 x 15.9   published 20 x 12 x 11
    Pulse       err 0.53   model  0.79 x 0.89 x 2.75  published 3.5 x 2.5 x 1.5
    Pulse LX    err 0.53   (same model as Pulse)

**Look at the Defender and the Eclipse: both are given the same published
dimensions, 24.5 x 24.5 x 5.** They are completely different ships. **The
published figures are wrong for at least one of them, and the guard is doing its
job by refusing.** The bug is in the source data, not the placement step.

**Javelin was rejected for a different reason: "no published dimensions."** It is
a 345-metre capital ship with no dimension row at all.

**The guard should not be relaxed to fix these.** It exists because it caught a
real disaster once. The fix is correcting the published dimensions, ship by ship.

## 4. GROUP D — 5 where zero is the right answer

    ATLS        a power-loader suit
    ATLS GEO    the mining variant
    ROC         mining vehicle
    ROC-DS      mining vehicle, two-seat
    MDC         Greycat cargo hauler

**No conventional weapon hardpoints, and the viewer already handles a zero-mount
ship correctly.** These should not be counted as broken.

**One caveat worth raising rather than burying:** the spec rows for the ROC and
ROC-DS carry `hardpoint_mining_arm`, and the ATLS carries hand-weapon ports.
**A mining arm is a physically visible, externally mounted thing** — exactly the
category the viewer was built to show. So "zero weapons" is correct, but "zero
things worth marking" may not be. That is a scope question for Sleven, not a
defect.

## 5. GROUP B — 27 with no mount data anywhere

    Ares Inferno      Ares Ion         Crucible        E1 Spirit
    Endeavor          Expanse          G12             G12a
    G12r              Galaxy           Genesis         Hull D
    Hull E            Kraken           Kraken Privateer  Legionnaire
    Liberator         Nautilus         Nautilus Solstice  Odyssey
    Orion             Pioneer          Ranger CV        Ranger RC
    Ranger TR         Vulcan           Zeus Mk II MR

**Most of these are concept ships that have never flown** — Galaxy, Endeavor,
Crucible, Orion, Pioneer, Hull D, Hull E, Odyssey, Legionnaire. Nobody can fit a
weapon to a ship that does not exist in game, so the absence is correct and no
amount of work here produces data.

**Four are worth separating out**, because they are flyable and the gap is real:

    Ares Inferno     flying now, heavily armed - a size 7 gun
    Ares Ion         flying now, heavily armed
    E1 Spirit        flying now
    Zeus Mk II MR    flying now (the ES and CL variants ARE placed)

**The Zeus is the tell.** Its sibling variants placed fine, so the data pipeline
works for that hull — the MR row is simply missing from `ship_specs.json`. That is
a source-data gap, not a design problem, and it is the same shape as the Aurora
issue one layer further back.

**Kraken and Kraken Privateer also sit here** and connect to the earlier
fingerprint finding: no spec row, no dimensions, no mounts — which is why nothing
could adjudicate their shared hull either.

## 6. Which of these matter — ships people actually fly

**Ranked by who would notice:**

    HIGH   Aurora, all 5 variants        the starter ship. Most-owned hull
                                          in the game. All group E.
    HIGH   A2 / C2 / M2 Hercules         41 mounts each, all group E
    HIGH   Ares Inferno / Ion            group B - real gap, popular gunships
    MED    600i Explorer, Mercury,       group E
           M50, C8R Pisces, Khartu-al
    MED    the 16 paint/edition hulls    group E - Cutlass Black, Gladius,
                                          Hammerhead, Caterpillar, Reclaimer,
                                          Carrack, Valkyrie
    MED    Defender, Eclipse, Nova       group C - wrong published dimensions
    LOW    the 9+ concept ships          group B - correctly empty

**Sleven should confirm this ranking.** I sorted by what the data suggests about
ownership and by which hulls appear across many variants; he flies these and I do
not.

## 7. Fixable, and roughly how — no design, as instructed

**Group E, 29 ships — a lookup table.** Model filename to mount-data key. The
project already has exactly this pattern in `ship_resolution.json`, built the last
time four ships were found hiding behind a name. **This is the same job at seven
times the scale, and it recovers 29 of 68 with no new data.** The paint-variant
half falls straight out of Sleven's shared-hull ruling.

**Group C, 7 ships — correct the published dimensions.** Ship by ship, from CIG's
own figures. **Do not loosen the proportion guard.** The Defender/Eclipse pair
sharing one set of dimensions is proof the guard is right and the data is wrong.

**Group D, 5 ships — nothing to fix**, unless Sleven wants mining arms marked.

**Group B, 27 ships — 23 need CIG to build the ship first.** The other four
(Ares Inferno, Ares Ion, E1 Spirit, Zeus Mk II MR) need a spec row that does not
currently exist and would have to be sourced.

## 8. What I checked and what I did not

**Checked:** all 68 individually against four data files; the placement report's
own stated reasons rather than inferring them; every group-E candidate confirmed
to have real mount counts on the other side, so "a name away" means the hardpoints
genuinely exist.

**Did NOT check:**
- **Whether the group-E hardpoints would place CORRECTLY once joined.** They exist;
  that the placement step accepts them is a separate question and the proportion
  guard may still reject some. **Nobody should promise 29 ships until a run
  proves it.**
- **My first pass used fuzzy name matching and produced four false pairs** —
  Dragonfly Black to Yellowjacket, E1 Spirit to C1 Spirit, G12a to 125a, Zeus MR
  to Zeus ES. All wrong, all discarded. **Everything in §2 is exact or
  containment-based.** Recorded because a fuzzy matcher would have quietly put
  the wrong hardpoints on four ships.
- **Which ships Sleven's crew actually fly.** §6 is inference from the data.
