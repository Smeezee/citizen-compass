# FINDING — the 29 are joined and live. 196 ships now render, 39 still bare, and the guard the order asked for is not the one that already existed.

    built by  Code, 2026-08-16
    order     "29 SHIPS ALREADY HAVE THEIR HARDPOINTS. JOIN THE NAMES."
    source    docs/FINDING_68-ships-without-hardpoints-2026-08-16.md (C3)
    rulings   DECISION_hull-configuration-acquisition-2026-08-16.md
              DECISION_shared-hulls-are-fine-unless-the-shape-differs
    verified  by fetching the deployed dataset back from the testing site

---

## Acceptance, in order

**1. All five Auroras and all three Hercules render.** Fetched back from
`citizencompasstesting.citizencompass-contact.workers.dev/holo_data.gen.js`:

    Aurora Mk I CL   10      A2 Hercules Starlifter   29
    Aurora Mk I ES   10      C2 Hercules Starlifter   29
    Aurora Mk I LN   10      M2 Hercules Starlifter   29
    Aurora Mk I LX   10
    Aurora Mk I MR   10

The Auroras are 10 each as the order said. **The Hercules are 29, not 41** —
see the correction below. Nothing was padded to reach a number.

**2. The 16 paints and editions resolve BY RULE**, and the rule is:

> the base is the longest mount-data key whose words all appear, in order,
> inside the model's name

Proved with names that have never existed anywhere — not in the data, not in
the finding, not in this repo:

    Gladius_Emerald_Jubilee_Edition_2955  ->  Gladius
    Hammerhead_Wikelo_Sneak_Special       ->  Hammerhead
    Reclaimer_Luminalia_2957_Livery       ->  Reclaimer

No code change, no line added. The next Best In Show edition and every future
Wikelo livery already work.

**Negative controls, all refusing:** `Zeus_Mk_II_MR`, `Ares_Inferno`,
`Kraken_Privateer`, `Galaxy`, `Wobbly_Nonsense_Hull` resolve to **nothing**. The
Zeus is the sharpest — its ES and CL siblings are in the data, and C3's own
first pass used fuzzy matching and handed the MR its sibling's mounts before
throwing the result away.

**3. A deliberately wrong mapping is refused, observed** — and the guard that
refuses it is not the one that already existed. See below.

**4. New totals.** 167 + 29 = **196 ships, 2,177 hardpoints, and not one ship in
the viewer now shows zero.** Residual, unchanged from C3's breakdown:

    27  group B - no mount data anywhere (23 are concept ships; Ares Inferno,
        Ares Ion, E1 Spirit and Zeus Mk II MR are real gaps)
     7  group C - rejected by the placement proportion guard
     5  group D - correctly zero, no conventional weapon mounts
    --
    39  still bare, all deliberately untouched

**5. Verified live**, by fetching the deployed dataset back (394,559 bytes),
not by a successful deploy.

---

## THE CORRECTION THAT MATTERS: the proportion guard does not catch a wrong pair

The order names the trap exactly: *"a Gladius wearing a Hammerhead's hardpoints
looks authoritative and is a lie."*

I wrote in the builder that the existing shape guard would catch that — the same
`resolve_frame` that refused 7 ships in the original run. **Then I measured it,
and it does not.** A Gladius-shaped hull offered Hammerhead dimensions scores a
proportion error of **0.11 against a threshold of 0.35**. It sails through.

The reason is not a bug. `resolve_frame` compares SHAPE and is deliberately
blind to size, because the model library mixes metres, centimetres and
normalised units in one folder. And a scale band cannot rescue it either — I
measured `model_units_per_metre` across all 167 placed ships and **19 of them
legitimately sit between 0.2 and 0.8**, so there is no gap to put a threshold in.

**So a third check was added, and it is the one that can actually tell those two
ships apart.** An edition is the same mesh with a different skin, so its bounding
box must match the base hull's own model to within 2%:

    Gladius vs Gladius re-skinned    accepted
    Gladius vs Hammerhead            REFUSED - worst axis differs by 83.5%
    Gladius vs a Gladius at 2x       REFUSED - an edition is not a scaled hull

**It runs on 9 of the 16 rule-resolved pairs.** For the other 7 the base hull has
no model on disk to compare against, and that is reported as **NOT PERFORMED**
rather than counted as a pass:

    Anvil_Ballista_Dunestalker, Anvil_Ballista_Snowblind,
    Caterpillar_Pirate_Edition, Cutlass_Black_Best_In_Show_Edition_2949,
    Dragonfly_Black, F7C-M_Super_Hornet_Heartseeker_Mk_I,
    Gladius_Pirate_Edition

Those seven rest on the name rule and the proportion guard, and the record says
so out loud.

---

## Two more corrections

**The Hercules carry 29 mounts each in the dataset the viewer reads, not 41.**
`ship_mounts.json` holds 29 for the A2 — 10 turrets, 4 countermeasures, 2 bomb
launchers, 13 other. Where C3's 41 came from I could not establish; the flat
legacy `ship_specs.json` in this repo has no Hercules row at all. **Reported
rather than reconciled**, because the only way to make 29 into 41 here would be
to invent twelve mounts.

**One pair was ambiguous, and the ambiguity turned out not to be about
anything.** `F7C-M_Super_Hornet_Heartseeker_Mk_I` matches both
`F7C-M Super Hornet Mk I` and `F7C-M Hornet Heartseeker Mk I` — five words each,
no non-arbitrary tie-break. Both carry **identical mount data**: the same ten
ports and the same published dimensions. So the tie is broken by asking whether
it is a tie about anything: identical mounts, pick either; different mounts, stay
refused.

---

## What had to be built to get here, and why

**The placement could not simply be re-run.** `place_fleet.py` ran in a cloud
sandbox against `/home/claude/fleet/geo` — decoded geometry that is not in this
repo — and it needs numpy, which is not installed on this machine and which
nothing here may install without asking.

**So the hull vertices are decoded locally**, by
`testing/_src/decode_glb_points.js`, using the DRACO decoder **already vendored
for the viewer** — the same decoder, on the same files, that a visitor's browser
runs. Four things went wrong on the way and each is written down where it
happened:

- the emscripten Module is a **thenable**, so `resolve(m)` adopted it instead of
  returning it and the process hung silently
- `onRuntimeInitialized` and `onModuleParsed` **never fire** in this build —
  measured with a probe that recorded every callback it was given
- `Decoder` exists as a stub from the first millisecond, so its presence is not
  readiness; the check is now *construct one and see*
- node buffers writes to a pipe, so a blocked event loop loses the output that
  would have said where it blocked

**And the placement is a pure-Python port that is checked against the original
rather than trusted.** Placing the 100i — a ship `place_fleet.py` already placed
— reproduces its frame exactly and its markers to within 0.052 in unit space
(5% of hull length would be 0.10; a wrong frame or nose would be a whole ship
away). If the port ever drifts, that check fails before 29 ships are placed with
it.

**`hardpoints_fleet.json` keeps its single writer.** The recovered ships are a
separate dataset merged at read time, and a key collision is a hard failure
rather than an overwrite — rule 14, and the third time this project has paid for
ignoring it.

---

## Where it lives

    testing/_src/decode_glb_points.js         hull vertices, via the vendored DRACO
    build_hardpoint_join.py                   the join, the guards, the placement port
    data-layer/derived/holo-hardpoints-join/  hardpoints_join.json + report + manifest
    checks/_verify_hardpoint_join.py          23 checks, every one driven with
                                              input that must fail it
    build_holo_data.py                        merges the two datasets for the viewer
