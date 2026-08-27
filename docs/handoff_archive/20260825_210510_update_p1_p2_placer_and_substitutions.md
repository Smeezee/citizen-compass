# Update — P1 and P2 done. Deployed 35107c34. Not committed.

**Deployed to testing: `35107c34-dc46-4f51-88c4-dd82f8847243`.**
Previous commit `903055c` (W4/E14/W3). Nothing committed since.

## P1 — the loop is open

`build_matched.py` seeded its candidate set from `hardpoints_fleet.json` and
then skipped every seeded hull when widening. The seed is gone. Candidates are
derived from **what has mount data and decoded geometry**, by four exact rules:

    1. the ship's own name                 166 hulls
    2. the slug minus its maker segment     19
    3. the whole slug                        0
    4. the name minus a leading maker word,  1  (MISC Reliant Kore, whose slug
       ONLY when that word is the slug's        is `misc-reliant` - the base
       own maker segment                       slug, so rule 2 lands nowhere)

**And the last read of the output went too.** `bare` - the name without its
manufacturer - was copied out of `hardpoints_fleet.json` with a fallback. It is
derived structurally now, proven against all 178 recorded values before the
read was removed: **0 mismatches.**

    candidates                175 -> 186
    hulls placed              169 -> 178
    markers                  1210 -> 1252 on 159 -> 163 hulls
    rejections                92, every one named with its reason

**NEGATIVE CONTROL, the load-bearing one: 169 of 169 previously placed hulls
are byte-identical. Markers that moved: ZERO.** Crowding unchanged at 117
markers on 19 hulls. Nine hulls gained: ATLS, Arrow, Constellation Aquila,
Cutlass Black, Gladius, Khartu-al, MDC, ROC, ROC-DS. **Cutlass Black has its 17
mounts.**

**The order predicted 175 -> 235. It is 186, and 235 was never reachable.** 235
(now 239) is the count of DECODED HULLS. The candidate set is the intersection
with `ship_mounts.json`, and only 186 of its 278 entries resolve to a hull. The
92 refusals are mostly Wikelo specials, Best In Show editions and unreleased
ships. Two are real name gaps worth a decision and are NOT fuzzy-matched:
`A2 Hercules Starlifter` against the folder `A2 Hercules`, and `Ares Star
Fighter Inferno` against `Ares Inferno`.

## P2 — and one of my own conclusions was wrong

Repointed: **Arrow**, **Constellation Aquila**, **Cutlass Black**, **Gladius**,
and **Valkyrie Liberator** (Sleven's item 19 - its model was already built and
decoded, and nothing pointed at it).

**BUT THE MESHES SAY THE ORDER'S FRAMING - AND MINE - WAS PARTLY WRONG.**
md5 of the source `model_scaled.glb`:

    Cutlass Black  ==  Cutlass Black Best In Show 2949   74a30f66...  IDENTICAL
    Gladius        !=  Gladius Valiant                                DIFFERENT
    Gladius        ==  Gladius Pirate Edition            04f0c9a0...  IDENTICAL
    Valkyrie       !=  Valkyrie Liberator Edition                     DIFFERENT

**A visitor asking for a Cutlass Black was NOT shown a paint job of it - the
skin folder holds byte-identical geometry.** The picture was right. What that
mapping cost was the hardpoints: no `Cutlass_Black` geometry existed, so the
placer could not see the ship. Repointing it is correct, and "shown a paint
job" is not the reason. **Gladius and Valkyrie Liberator were genuinely the
wrong hull.**

**Cloudflare confirmed it from the other end:** the deploy uploaded 5 assets,
not 7. `Cutlass_Black.glb` and `Gladius.glb` deduped against the skin and the
Pirate Edition by content hash. The compressor is deterministic and the bytes
are the same.

**Three more of the same class, found by measuring rather than by the order,
and deliberately NOT changed:** `Ballista Dunestalker` and `Ballista Snowblind`
render the base Ballista, and all three files are md5 `1c939472...` - the same
mesh. Repointing them would add a megabyte of duplicate payload for no visible
difference. Reported and left alone.

**Sixteen site rows render a differently-named folder. After the fix: 0
STAND-IN, 4 identical-mesh, 12 no-own-folder.** Built-and-unreachable is down
to 14 and every one carries a stated reason.

## Controls

`checks/_verify_placer_candidates.py` — 16 assertions.
`checks/_verify_model_substitutions.py` — 15 assertions.

    _verify_placer_candidates   normal 0 | --self-test 1 | --mutate-oldrules 1
    _verify_model_substitutions normal 0 | --self-test 1 | --mutate-standin 1
                                | --mutate-unnamed 1

**Two things went wrong building the P1 control and both are worth recording.**

**1. A mutation that failed for the wrong reason.** `--mutate-reseed` imported
a broken copy of `build_matched.py` from a temp directory. The copy derived its
input paths from `__file__`, so it died on `MISSING INPUT: <temp>/
ship_mounts.json` and exited 1 - which looks exactly like the mutation being
caught, with not one assertion having executed. The loader now pins the
builder's input paths back to the real ones.

**2. A mutation I could not make fire, reported rather than dropped.** Once it
ran, restoring the fleet seed changed **nothing** - 186 candidates either way.
The reason is the finding: all 178 recorded hulls resolve, under the new rules,
to exactly the model they were already placed against, so seeding adds no
member the derivation would not produce anyway. **That is the evidence removing
the seed was safe, and also why no behavioural test can tell the two builds
apart.** Rule 12 says a mutation that cannot fail is not a mutation, so it is
named in the control's docstring and replaced with `--mutate-oldrules`, which
restores the narrow slug-only resolution and drops the candidate set 186 -> 117.

The invariant itself is guarded by a **planted ghost**: a hull invented in
`hardpoints_fleet.json` that no resolver could produce. It must never reach the
candidate set.

## Four sweep failures caused by this work, all fixed by unpinning a count

Sweep is now **76 ok, 2 failed, 3 skipped** (was 72/4/3).

- **`_verify_marker_absence.mjs`** looked the Cutlass Black up BY NAME as its
  "mounts but no positions" example - against its own docstring, which says
  "told apart from the data, never from a list of ship names". P1 gave the
  Cutlass Black markers, so the control went red reporting "not found" about a
  ship that had just been fixed. It now picks the case from the data and names
  whichever hull it used. **A control that fails when its example ship gets
  better is measuring the example.**
- **`_verify_label_threshold.mjs`** pinned `census.length === 159`. Compared
  against the marker table itself now.
- **`_verify_stage_floor.mjs`** pinned the errata's census at 4/224/7 over 235
  hulls. The two TAILS are the finding and stay exact; the middle is asserted
  to account for the rest of a 239-hull library.
- **`_verify_g3_matcher_delta.py`** had reported NOT PERFORMED on every
  scheduled run since it was written, because nothing in the sweep set
  `CC_GEO_DIR`. Honest and useless. It now defaults to
  `data-layer/derived/hull-geometry/` - the same fallback `build_matched.py`
  already uses, so the check and the build cannot read different geometry. **It
  runs, and it passes, for the first time.** The NOT PERFORMED path still fires
  on an absent or empty directory - verified.

**Still red, still reported, still not faked: `_verify_stage_floor.mjs`**
crashes on `this.camera.updateMatrixWorld` - `_fitProjected()` needs a real
perspective projection and the control's hand-written THREE stub has none.
E5's stage-floor guarantee remains unverified.

## Preserved, per rule 1

    hardpoints_fleet.pre-P1-20260826.json
    placement_report.pre-P1-20260826.json
    matched.pre-P1-20260826.json

## Next

`ORDER_children-inherit-their-turret-2026-08-26.md`, which the sequence note
says runs after this one. Held: coverage reported against ELIGIBLE ports only -
no target selectors, no weapon regen pools - and the Retaliator's four working
markers (PortIds 23/24/39/40) pinned by exact coordinate.
