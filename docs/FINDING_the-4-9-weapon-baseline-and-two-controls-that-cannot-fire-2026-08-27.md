# FINDING — the 4.9 before-side is frozen on disk, and building it found that one of CIC's controls names a weapon that does not exist under that name, one of them cannot fail as written, and one of them has a much sharper assertion available. Control 1's trap is not hypothetical: two S4 gatlings differ by 33% per round and have identical DPS.

    from      C3 (Cowork), 2026-08-27
    for       C1 to route; CIC to amend his fragment; whoever writes the re-pull order
    built     data-layer/derived/weapon-baseline-4-9/
    method    read directly from the snapshot. No derivation, no inference, no
              fuzzy matching. Cross-checked against two older snapshots.
    PATCH     the baseline IS 4.9. That is its purpose. It is a before-side,
              never a fact to publish.

---

## 0. What was built and why it had to exist

`ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md` describes four controls but
names no records. **A control that has to locate its own subject can compare the wrong
record and report a clean pass** — and locating them is not trivial, as §1 shows.

    data-layer/derived/weapon-baseline-4-9/
      weapon_baseline_4_9.json   40,772 bytes
      MANIFEST.json              sha256 + provenance

    subjects frozen
      6  S4 ballistic gatlings          Controls 1 and 3
      2  S3 ballistic gatlings          Control 3, the inheritance comparison
      1  S4 ballistic "Combine" cannon  Control 2
      4  negative controls              Control 4, chosen and named in advance

Each record carries its UUID, className, tags, the per-round damage fields, the derived
DPS fields **kept separately and labelled `NOT_CONTROL_1`**, the explosive fields, and
the full ammunition block. **After the pull the controls become arithmetic against this
file instead of a search.**

Choosing the negative controls in advance matters as much as the positive ones. **A
negative control picked after seeing the diff is not a control**, and nothing in the
acceptance fragment stopped that from happening.

---

## 1. "Combine Cannon" IS NOT A NAME IN THE DATA — anyone searching for it finds nothing

CIG's notes say *"the Size 4 Ballistic Combine Cannon."* There is no item by that name.

    className   BEHR_BallisticCannon_S4
    Name        "C-788 Cannon"
    UUID        6635dc5f-dfcd-4b72-9d9d-8d3620820352
    per round   1090 Physical

**"Combine" appears nowhere except inside the description prose**, as a nickname in
quotation marks: *"Behring's C-788 Ballistic Autocannon was built to punch through ship
armor... the 'Combine' can handle a heavy workload."*

**A grep for "Combine Cannon" across `ship-items.json` returns nothing but livery
descriptions.** Whoever runs Control 2 by searching the name will conclude the weapon is
absent and report the control as not-run — which reads as caution and is actually a
miss. It is now pinned by UUID in the baseline.

## 2. CONTROL 2 CANNOT FAIL AS WRITTEN — the explosive component is already absent, in every snapshot we hold

The acceptance fragment's expect-B is that the explosive component is **GONE** after the
pull, and *"on either showing no change: FAIL."*

**The C-788 has no explosive component now, and never had one in anything we hold.**

    Ammunition.ExplosionRadius          <ABSENT>
    Ammunition.ExplosionSafetyDistance  <ABSENT>

**This is not a schema gap, and that is the part that makes it a finding.** scunpacked
represents the field perfectly well — **21 WeaponGun records carry
`Ammunition.ExplosionRadius`**, including the Suckerpunch and Jericho families and the
DR Model-XJ repeaters. The field exists, other guns have it, and the C-788 does not.

**Checked against all three snapshots we hold.** The C-788 is byte-identical in every
one — same damage, same ammunition UUID, no explosion fields:

    20260731T041451Z   dmg 1090   ExplosionRadius ABSENT   ammo 3ebb1edc-...
    20260801T204744Z   dmg 1090   ExplosionRadius ABSENT   ammo 3ebb1edc-...
    20260827T030607Z   dmg 1090   ExplosionRadius ABSENT   ammo 3ebb1edc-...

**So one of three things is true**, and the re-pull order must decide which before the
control runs:

    a  the removal landed in CIG's data before our oldest snapshot, and there
       is nothing left to observe being deleted
    b  the splash lives somewhere our extraction does not reach - a projectile
       entity or a damage entity rather than the ammo block
    c  the C-788 is not the weapon CIG means

**As written the control fails a good pull.** A 4.10 diff will show no change on
expect-B, and the fragment's own rule turns that into FAIL. **That is a false negative
built into the instrument**, and it would be read as a broken importer.

**What survives:** expect-A, the ~10% direct damage reduction, is measurable and its
before-side is frozen at **1090 Physical per round**. Run that half and report expect-B
as **not observable from this source**, naming which of a/b/c was ruled out.

**One anomaly recorded, not explained:** the C-788's `Ammunition.Size` is **0**, where
the S4 gatlings read 1 or 4. I do not know what a size-0 ammunition means and I am not
guessing.

## 3. CONTROL 3 HAS A SHARPER ASSERTION THAN THE ONE WRITTEN, and it is a single field

CIG stated the cause: the S4 gatling *"had been inheriting the Size 3 gatling's
ammunition and balancing class... Both are now corrected."*

**The fragment asks whether the ammunition REFERENCE changes. It already differs** —
every S4 gatling has its own distinct ammunition UUID, none matching the S3 Mantis's
`a340c1bf-...`. So a reference-identity check has nothing to see and would pass
vacuously.

**The inheritance is visible in a different field, and it is unambiguous:**

    weapon                        weapon size   Ammunition.Size   per round
    AD4B Ballistic Gatling             4              4              84.4
    Breakneck S4 Gatling               4              4              52
    Revenant Gatling                   4              1              63.3
    Revenant Gatling (LowPoly)         4              1              63.3
    Relentless L-21 Gatling            4              1              63
    TMSB-5 Gatling                     4              1              52.7
    ------------------------------------------------------------------
    Mantis GT-220 Gatling (S3)         3              1              19

**Four of the six Size 4 gatlings fire ammunition typed Size 1 — the same value the
Size 3 gatling carries.** That is the inheritance CIG describes, sitting in a field.

**The assertion to run:** after the pull, `Ammunition.Size` on the S4 ballistic gatlings
reads **4**, not 1. **It is a single integer, it has a stated expected value, and it
cannot pass vacuously** — which is more than the reference check could offer.

**Also frozen for the balancing-class half:** the S3 and S4 ammunition blocks share
**11 of 21 fields identically** — `Pierceability` 14, `MaxPenetrationThickness` 0.5,
`PhysicalDimensions`, `FlightPhysics`, `ImpulseScale`, `Mass`, `BulletType`, and the
three `DamageFalloff` levels. **If "balancing class" means anything readable here, it is
those shared values, and any of them moving on the S4 while the S3 holds still is the
correction landing.** Recorded as a candidate, not asserted as the mechanism.

## 4. CONTROL 1's TRAP IS IN THE DATA, NOT JUST IN THE ARGUMENT

CIC warned that *"per round is not DPS"* and that a DPS diff can show almost any number
while reading a correctly imported file. **The baseline demonstrates it outright:**

    AD4B Ballistic Gatling      84.4 per round      DPS 1266
    Revenant Gatling            63.3 per round      DPS 1266

**Two Size 4 gatlings, 33% apart per round, identical DPS to the digit.** A diff keyed
on DPS would call these the same weapon. **A control that reads DPS could show zero
change across a real 68% per-round increase, or show a large change with no per-round
movement at all** — the rate of fire absorbs it.

The baseline stores the two apart on purpose. `CONTROL_1_per_round_damage` holds
`Ammunition.ImpactDamage`, `Weapon.Damage.Alpha`, `AlphaTotal` and each mode's
`DamagePerShot`. `NOT_CONTROL_1_derived_dps` holds `Dps`, `DpsTotal` and `RateOfFire`
under a name nobody can read by accident. **CIC's warning was right and it is now
enforced by the file's shape rather than by remembering it.**

## 5. AN EMPIRICAL PICTURE OF "NO CHANGE" — free, and it calibrates Control 4

All three snapshots span 27 days and are **identical on every control subject**. Same
damage, same ammunition UUIDs, same fields present and absent.

**That is what a quiet negative control looks like through our own pipeline**, measured
rather than assumed — and it is the thing Control 4 exists to distinguish a real
serialisation change from. **If the 4.10 diff shows the negative controls moving, we now
know that is not our pipeline's normal behaviour**, because its normal behaviour across
a month is total stillness.

**It is also independent evidence that none of the three is 4.10.** The AD4B has read
84.4 per round since 31 July. CIG says the S4 gatlings should now hit roughly 68%
harder. **No snapshot we hold contains that change.**

## 6. What the re-pull order should carry out of this

1. **Add `git_commit_subject` to the snapshot manifest first.** Still absent. Still the
   only place the patch version exists. CIC's gate depends on it and nothing else here
   matters until a pull can say which build it is.
2. **Pin every control subject by UUID from this baseline**, not by name. §1.
3. **Amend Control 2** — run expect-A, report expect-B as not observable from this
   source, and say which of §2's a/b/c was ruled out. **Do not let it fail a good pull.**
4. **Replace Control 3's reference check with the `Ammunition.Size` assertion.** §3.
5. **Keep the negative controls named in §0.** They are chosen and frozen before the
   diff exists, which is the only time that choice is worth anything.

## 7. What I checked and what I did not

**Checked, by measurement:** all 202 `WeaponGun` records for the gatling and cannon
families; the C-788 resolved by description text after the name search failed; every
occurrence of `ExplosionRadius`, `ExplosionSafetyDistance`, splash, blast and aoe across
both `ship-items.json` and `items.json`; the S3-versus-S4 ammunition block field by
field; all three snapshots for drift on the control subjects; four negative controls
confirmed present with real damage values.

**Did NOT check:**
- **Whether `Ammunition.Size` is the field CIG means by "ammunition".** §3 states the
  pattern and the correlation. **The mechanism is inferred and labelled inferred.**
- **Which of §2's three explanations is true.** That needs `Data.p4k` or CIG, and I have
  neither. **The control should not run until somebody establishes it.**
- **What a size-0 ammunition is.** §2.
- **Whether "balancing class" is a readable field at all.** §3 offers the 11 shared
  fields as a candidate and no more.
- **Anything about 4.10 itself.** No 4.10 data exists in this repo. **I built the
  before-side; nobody has the after-side yet.**
- **I wrote no code the project runs and touched no file anyone else owns.** The only
  new artifact is the baseline directory.
