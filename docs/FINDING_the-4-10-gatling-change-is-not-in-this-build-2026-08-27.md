# FINDING — 4.10 is pulled and gated. The S4 gatlings did not change. The **S3** did, by +68.4%.

**Written by Code, 2026-08-27.** Executes `WORKORDER_the-4-10-pull-2026-08-27.md`.

    snapshot   20260827T225641Z
    build      4.10.0-LIVE.12519617      (git_head_subject, existing field)
    before     20260827T030607Z at 4.9.0-LIVE.12344265
    baseline   weapon-baseline-4-9/weapon_baseline_4_9.json, 13 subjects by UUID

All five acquisition gates passed in order and the gate renamed the snapshot out
of `.partial` itself. 29,044 files inspected, hashed, scanned, re-hashed
identical, 0 flagged.

---

## The outcome table, filled in

    control_1   FAIL   all six S4 gatlings byte-identical
    control_3   FAIL   Ammunition.Size still 1 on four of six
    control_2a  PASS   C-788 fell 1090 -> 975 per round, -10.6%
    control_2b  NOT OBSERVABLE  absent before and after, as predicted
    control_4   quiet on measured fields - but see below

## §8 says a zero on control 1 means the importer is broken. It does not, here, and the data says so

That inference has a premise — *the importer did not carry the change* — and the
premise is testable. It fails:

    1,951 of 5,380 common records changed
    the C-788 moved by exactly the predicted -10.6%
    14 new UUIDs, 4 gone

**An importer that carried 1,951 changes and hit one of our own subjects
on the nose is not broken.** The change is absent from this build's data.

That correction is now in the tool rather than only in this document: it
computes the corpus-level diff before reading any control, and a control-1 FAIL
against a moving corpus is reported as *"the change being absent from this
build, not a broken importer."*

## THE THING NOBODY PREDICTED — the raise landed on the S3

    Mantis GT-220 Gatling (S3)   19 -> 32 per round     +68.4%

**+68.4% is inside the +60% to +75% band Control 1 predicted for the S4
gatlings.** The magnitude CIG described arrived — on the Size 3 weapon, not the
Size 4 ones.

And the S4s are untouched. Not "changed a little": **byte-identical, zero fields
differing, all six.**

Set against Control 3's table, this is pointed. CIG's stated cause was that S4
gatlings were *"unable to defeat armor a Size 4 weapon should defeat"*, and the
mechanism the order identified was four of six S4 gatlings firing ammunition
**typed Size 1 — the Size 3 value**. In this build:

    Ammunition.Size on the S4 gatlings    unchanged, still 1 on four of six
    the S3 gatling's per-round damage     raised 68.4%

**Three readings, none of them proven by this data:**

  a. the fix was applied to the wrong end — the S3 value was raised rather than
     the S4s being detached from it, which would make every S4 inheriting it
     worse relative to its class, not better
  b. this is the first half of a staged change and the S4 half lands in a later
     4.10.x
  c. the S3 raise is an unrelated buff and the S4 work is not in 4.10.0 at all

**a is consistent with the data and is not established by it.** Which one it is
needs the patch notes read against this, and that is not a measurement.

## Control 4 — quiet by the letter, and one control moved

§7 asks for no change in any **measured** field. There was none, so the tool
reports QUIET. But one negative control did move:

    CF-117 Bulldog Repeater    Ammunition.Mass   0.01 -> 0.25

**It is the only record out of 5,380 that changed solely in `Ammunition.Mass`**,
so it is not part of a sweep. A 25x change on the ammunition mass of a weapon
named nowhere in the 4.10 notes is not nothing, and reporting "quiet" without
this line would be true and misleading at once.

It does not make the run inconclusive under §7 as written. It is recorded so
that whoever reads §8's "4 quiet" knows exactly what quiet meant here.

## What 4.10 actually is, in this data

Only **4 of 202** WeaponGun records changed at all: the C-788, the Mantis
GT-220, the CF-117 Bulldog, and the Tigerstrike T-19P.

The 1,951 changes are dominated by something else entirely:

    Thruster.MaxSupportedAtmosphericEfficiency   1265
    Thruster.BurnRatePerMN (+2 unit variants)    1171 each
    ResourceContainer.Capacity                    332
    ResourceNetwork.States[0].Deltas              238
    FuelTank.Capacity                             158

**In this snapshot 4.10 is a flight and resource pass.** The weapon rebalance the
notes describe is four weapons wide.

## What this does NOT say

- It does not say CIG's notes are wrong. Notes describe intent; this is one data
  source at one commit.
- It does not say the pull failed. The pull is clean and gated.
- It does not re-measure §9's three items — the shield patterns, the inert
  damage channels, the armour multiplier profiles. Those are next and must be
  re-measured rather than assumed, exactly because a weapon pass is what changes
  them.

## Provenance

    scripts/diff_weapon_4_10.py             the controls, matched by UUID only
    data-layer/derived/weapon-diff-4-10/    the full per-subject record

Matching is by UUID throughout. §5's reason stands: CIG's "Combine Cannon" has
no item by that name, and a name search would have returned nothing while
looking like caution.

---

*Code, 2026-08-27.*
