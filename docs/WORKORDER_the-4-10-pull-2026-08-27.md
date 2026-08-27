# WORK ORDER — pull 4.10. There is no prerequisite, the before-side is already frozen on disk, and two of the four acceptance controls are amended here because as written they would fail a good pull.

    from      C3 (Cowork), 2026-08-27
    for       C1 to route -> Code to execute
    writer    ONE, and it is this document. Rule 14. CIC's acceptance fragment is
              folded in below rather than referenced, so nobody runs two versions.
    basis     ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md      (CIC)
              FINDING_the-4-9-weapon-baseline-...-2026-08-27.md         (C3)
              ERRATUM_the-manifest-gate-already-exists-...-2026-08-27.md (C3)
    target    scunpacked-data at 4.10.0-LIVE.12519617

---

## 0. READ THIS FIRST — the step every prior document opened with is deleted

**Every document filed today, including mine and CIC's, says to add
`git_commit_subject` to the snapshot manifest before pulling. Do not do it.**

The field exists as **`git_head_subject`**, has since 1 August, is captured at
`gate_scunpacked_snapshot.py:118`, is validated there at line 127, and is already a
hard gate in `build_patch_diff.py:84`. **Adding a second key for one fact is the defect,
not the fix.** Full working in the erratum.

**Nothing blocks this pull. Start at step 1.**

## 1. ACQUIRE

Clone scunpacked-data **with git-lfs** into a new `.partial` snapshot directory, then:

    python scripts/external_sources/gate_scunpacked_snapshot.py <run_id>

**Known risk, from this project's own record:** the clone is ~1.42 GB and a previous
attempt died at ~52% against a 10-minute ceiling, leaving a directory with no usable
HEAD. **An interrupted clone is a failure, not a partial** — there is nothing
recoverable in it. Give it room.

**Second known trap, and the gate already covers it:** a clone made without git-lfs
replaces `items.json` with a 130-byte text stub describing itself. File count unchanged,
structure unchanged, nothing visibly missing. **The LFS pointer scan is why this gate
exists — do not skip ahead of it.**

**Do not rename out of `.partial` by hand.** The gate does that, and only when all five
pass. This has been violated once before under time pressure and was correctly recorded
as a process failure.

## 2. THE PATCH GATE — one assertion, existing field

    assert  manifest.git_metadata_captured_before_stripping.git_head_subject
            contains "4.10.0-LIVE.12519617"

**Fail closed.** If it does not, this is not a 4.10 pull and **no control below runs.**
A pull that cannot prove its build produces a confident answer about the wrong one, which
this project has now logged four times — and the fifth was believing the gate for that
was missing.

**Sanity value:** the current snapshot reads `4.9.0-LIVE.12344265`. If the new one reads
the same string, the upstream repo has not moved and there is nothing to diff. **Say so
and stop** — that is a clean result, not a failure.

## 3. THE BEFORE-SIDE IS ALREADY ON DISK — do not go looking for these weapons

    data-layer/derived/weapon-baseline-4-9/weapon_baseline_4_9.json
    data-layer/derived/weapon-baseline-4-9/MANIFEST.json

Thirteen subjects, each pinned by **UUID**, with the per-round fields and the derived DPS
fields stored separately under a key literally named `NOT_CONTROL_1`. **Diff against this
file. Do not re-locate the weapons by name** — §4 explains why that fails.

## 4. CONTROL 1 — the S4 ballistic gatlings, per ROUND

    field       Ammunition.ImpactDamage.Physical   (also Weapon.Damage.AlphaTotal,
                                                    Modes[].DamagePerShot)
    expect      rises, order of +60% to +75%
    on zero     FAIL - the importer did not carry the change

**The trap is real and it is in the baseline, not just in the argument.** The AD4B reads
84.4 per round and the Revenant reads 63.3 — 33% apart — and **both have DPS of exactly
1266.** A diff keyed on DPS calls them the same weapon. Rate of fire absorbs everything.

**If the pipeline only holds a derived DPS, report Control 1 as NOT RUN.** Do not
substitute the field you have for the field named.

**Magnitude off, direction right → FLAG, do not fail.** CIG wrote "roughly" and meant it.

## 5. CONTROL 2 — AMENDED. Half of it runs; the other half cannot fail as written.

**The weapon is `BEHR_BallisticCannon_S4`, display name "C-788 Cannon", UUID
`6635dc5f-dfcd-4b72-9d9d-8d3620820352`.** CIG calls it the "Combine Cannon" and **there
is no item by that name** — "Combine" appears only as a nickname inside the description
prose. A search by name returns nothing, and reporting that as "weapon absent" would read
as caution while being a miss.

**5a. RUNS.** Direct damage falls, order of −10%. Before-side: **1090 Physical per
round.**

**5b. DOES NOT RUN, and forcing it fails a good pull.** CIC's expect-B is that the
explosive component is GONE. **It is already absent, in all three snapshots we hold** —
31 July, 1 August, 27 August, byte-identical, no `Ammunition.ExplosionRadius`, no
`ExplosionSafetyDistance`.

**This is not a hole in our extraction.** 21 other `WeaponGun` records carry
`Ammunition.ExplosionRadius` — the Suckerpunch and Jericho families, the DR Model-XJ
repeaters. The field works. The C-788 does not have it.

    Report expect-B as NOT OBSERVABLE FROM THIS SOURCE and say which is true:
      a  the removal predates our oldest snapshot
      b  the splash lives where our extraction does not reach
      c  the C-788 is not the weapon CIG means

**A no-change result on 5b means the question was never answerable here. It does not
mean the importer is broken.**

## 6. CONTROL 3 — AMENDED, and the replacement is stronger than the original

CIC's version asks whether the ammunition **reference** changes. **It already differs** —
every S4 gatling has its own ammunition UUID and none matches the S3 Mantis's
`a340c1bf-...`. **That check passes vacuously and proves nothing.**

**The inheritance is visible in one integer:**

    weapon                       weapon size   Ammunition.Size   per round
    AD4B Ballistic Gatling            4              4              84.4
    Breakneck S4 Gatling              4              4              52
    Revenant Gatling                  4              1              63.3
    Revenant Gatling (LowPoly)        4              1              63.3
    Relentless L-21 Gatling           4              1              63
    TMSB-5 Gatling                    4              1              52.7
    -----------------------------------------------------------------
    Mantis GT-220 Gatling (S3)        3              1              19

**Four of six Size 4 gatlings fire ammunition typed Size 1 — the Size 3 value.** That is
CIG's stated cause, sitting in a field.

    assert      Ammunition.Size reads 4 on the S4 ballistic gatlings
    on 1        FAIL, even if Control 1 passed

**For the balancing-class half:** the S3 and S4 ammunition blocks share **11 of 21 fields
identically** — `Pierceability` 14, `MaxPenetrationThickness` 0.5, `PhysicalDimensions`,
`FlightPhysics`, `ImpulseScale`, `Mass`, `BulletType`, the three `DamageFalloff` levels.
**Any of those moving on the S4 while the S3 holds still is the correction landing.**
Offered as a candidate, not asserted as the mechanism.

**Control 3 is a second, independent proof of patch identity** — derived from the data
rather than a commit message. Keep it for that reason alone.

## 7. CONTROL 4 — the negative controls, chosen BEFORE the diff exists

    KLWE_LaserRepeater_S1_ATLS    CF-117 Bulldog Repeater      S1   alpha 11.3
    ESPR_LaserCannon_S2           Lightstrike II Cannon        S2   alpha 74
    BEHR_BallisticRepeater_S3     SW16BR3 "Shredder" Repeater  S3   alpha 45
    TOAG_LaserRepeater_S3         Yeng'tu Repeater             S3   alpha 41

Four families, three size classes, none named in the 4.10 notes. **Already frozen in the
baseline.** A negative control picked after seeing the diff is not a control, and nothing
in the original fragment prevented that.

    expect      no change in any measured field
    on change   INCONCLUSIVE, not a pass - diagnose the diff before reading anything

**Calibration, measured rather than assumed:** all three snapshots we hold span 27 days
and are **identical on every control subject.** Total stillness is this pipeline's normal
behaviour across a month. **If the negative controls move, that is not normal.**

## 8. READING THE OUTCOME

    1, 3 pass · 5a passes · 4 quiet      trustworthy. Proceed.
    any of 1, 3, 5a shows zero           the importer is broken. Not the patch.
    4 also moves                         inconclusive. Diagnose the diff first.
    magnitude off, direction right       FLAG, do not fail.
    5b shows nothing                     EXPECTED. Report which of a/b/c.

## 9. AFTER THE PULL — three things that must be re-measured, not assumed

Everything below was measured on 4.9 and a weapon rebalance is exactly what changes it.

- **"Every shield in the game is identical by damage type"** — 73 items, one Absorption
  pattern, one Resistance pattern. **Re-measure.** If it still holds, the "do not build a
  shield comparison" ruling stands.
- **"Thermal, Biochemical and Stun are inert on both sides"** — 0 weapons deal them, 0
  defences resist them. **Re-measure both halves.**
- **The armour damage-multiplier profiles — EIGHT, not ten.** CIG's note says the S4
  gatling was *"unable to defeat armor a Size 4 weapon should defeat,"* which is a
  sentence about these fields.

## 10. NOT IN SCOPE, stated so nobody assumes it is

- **FPS weapons.** CIG published a stat block for the HDGW Arlington Rifle. The client is
  the better source and this order is ship weapons.
- **Crafting.** No recipe-system change in the notes, so no CIG-stated control exists for
  the 1,597 blueprints. **Expect new rows, not changed columns** — BUL-H4, the Vendetta
  HMG, ore pods, mining modules, containers, Wikelo's single-use blueprints. An
  observation, not a control.
- **Whether Missile, MissileLauncher, Turret, WeaponDefensive and BombLauncher are still
  at zero recipes.** Worth running first, has no CIG statement either way, **cannot be
  written as pass/fail. Do not dress it as one.**
- **Missiles generally.** No 4.10 missile pass; the last was 4.7. A missile field that
  moves is a question, not data.

## 11. Provenance and what nobody has checked

Both CIG quotations are from **Alpha 4.10 LIVE release notes, RSI comm-link 21293,
26 August 2026, "Vehicle Weapon Rebalance"** — read from the rendered page by CIC. The
comm-link is client-rendered and returns metadata only to a plain fetch, so anything
reporting it empty has not read it. Comm-link 21242 is marketing and carries no weapon
prose; checked, so nobody checks it again.

**Not checked by anyone:**
- **Whether `Ammunition.Size` is what CIG means by "ammunition".** §6 states the pattern
  and the correlation. **Inferred, and labelled inferred.**
- **Which of §5b's a/b/c is true.** Needs `Data.p4k` or CIG.
- **Whether `build_patch_diff.py`'s existing subject gate has a test that could fail it.**
  Rule 12 applies and there is a fixture that looks right. **Looking right is not having
  been run**, and if Code is in that file anyway, it is worth ten minutes.
