# FINDING — §9's three re-measurements. All three unchanged by 4.10, and the armour count that three documents disagreed about is 5.

**Written by Code, 2026-08-27.** §9 of `WORKORDER_the-4-10-pull-2026-08-27.md`.

    before  20260827T030607Z   4.9.0-LIVE.12344265
    after   20260827T225641Z   4.10.0-LIVE.12519617
    tool    scripts/remeasure_4_10.py
    record  data-layer/derived/weapon-diff-4-10/remeasure_20260827T225641Z.json

---

## 1. Every shield is still identical by damage type

    before  73 shield items | 1 Absorption profile | 1 Resistance profile
    after   73 shield items | 1 Absorption profile | 1 Resistance profile

**Unchanged by 4.10.** `DECISION` stands: there is nothing to compare, so the
"do not build a shield comparison by damage type" ruling holds.

The single profile, **as ranges, not collapsed** — C1 established today that
publishing the 45% flat is wrong at the bottom of the range, where a shield
absorbs **none** of a ballistic hit:

    Physical      Minimum 0     Maximum 0.45      <- a RANGE
    Energy        Minimum 1     Maximum 1         <- fixed
    Distortion    Minimum 1     Maximum 1
    Thermal       Minimum 1     Maximum 1
    Biochemical   Minimum 1     Maximum 1
    Stun          Minimum 1     Maximum 1

## 2. Thermal, Biochemical and Stun — unchanged, and never exactly inert

                  deals it        resists it
    Thermal       0 -> 0          1 -> 1
    Biochemical   0 -> 0          1 -> 1
    Stun          0 -> 0          0 -> 0

**No weapon in either patch deals any of the three.** That half of the claim
holds exactly.

**The other half was never exactly true, and 4.10 did not change it.** One
record resists Thermal and Biochemical — and it is the same one in both patches:

    ARMR_AEGS_Javelin_Invulnerable
    Physical 0.75 · Energy 0 · Distortion 0 · Thermal 0 · Biochemical 0 · Stun 1

**An invulnerability record, not a ship anyone flies.** So "0 defences resist
them" is substantially true and not literally true, it was already so on 4.9,
and the patch is not the reason.

**My first run reported this as "NO LONGER INERT".** That was wrong: the counts
had not moved. The verdict now compares after to before rather than to zero,
because §9 asks whether the PATCH changed something — testing against zero
blames 4.10 for a state that predates it. The fix is in the tool.

## 3. The armour profiles — 8, 9 and 10 are all counts of scaffolding. The answer is 5.

The written record disagreed with itself three ways: C3 counted **9**,
`CURRENT-STATE` said **10**, the work order said **EIGHT**.

    RAW, every armour record
      before  210 items, 10 profiles
      after   210 items,  9 profiles

    REAL SHIP ARMOUR ONLY
      before  5 profiles
      after   5 profiles          <- UNCHANGED

**All three published numbers counted scaffolding.** What the 210 records
actually are:

    119   literally named "<= PLACEHOLDER =>"
     90   real ship armour
      1   ARMR_AEGS_Javelin_Invulnerable
    ----
    210

And the raw count moving 10 → 9 is not a gameplay change either: **the profile
that vanished belonged to a `<= PLACEHOLDER =>` record** (Energy 1.1,
Physical 0.75).

The five real profiles, unchanged across the patch:

     64 items   Physical 0.75   Energy 0.6
     15 items   Physical 0.7    Energy 0.5
      7 items   Physical 0.8    Energy 0.65
      3 items   Physical 0.85   Energy 0.7
      1 item    Physical 0.6    Energy 0.4

Distortion, Thermal, Biochemical and Stun read 1 on every one of them — no
armour in the game modifies those four.

## What this means for the S4 gatling question

CIG's note said the S4 gatling was *"unable to defeat armor a Size 4 weapon
should defeat,"* and §9 called that a sentence about these fields.

**These fields did not move.** Five profiles before, five after, the same five.
Taken with the main finding — the S4 gatlings byte-identical while the S3 rose
68.4% — **nothing on either side of that sentence changed in this build.**
Neither the weapon nor the armour it was said to be unable to defeat.

## An aside that corroborates today's other fix

The invulnerability record's display name in the raw data is
**"Hammerhead Ship Armor"** on a Javelin class. That is the armour-naming defect
fixed earlier today, visible from a completely different direction — and one
more reason the fix derives the name from the ship rather than from the item.

## Limits, stated

Both sides of every comparison come from scunpacked, so this shows one source
agreeing with itself across two commits. That is the right shape for *did it
change*, and it cannot tell you whether the extraction is faithful to the game.
The independent source is the client's own p4k, which is C1's lane and was not
used. The tool carries the same statement as a `RULE16: UNPROVEN` label.

---

*Code, 2026-08-27.*
