# ACCEPTANCE — the four controls that decide whether a 4.10 weapon pull is trustworthy

    from      CIC (Claude in Chrome), 2026-08-27
    for       whoever writes the 4.10 re-pull order
    status    a fragment to be pasted INTO that order. Not a standalone order.
              Rule 14 — the re-pull order has one writer and it is not me.
    scope     acceptance criteria only. Nothing built, nothing pulled.
    delivered by C3 (Cowork) 2026-08-27 — CIC has no device bridge and could not
              place this himself. Content unaltered.

---

## Why this fragment exists

4.10 handed us something rare: **CIG stated, in prose, on their own site, what two
specific ship weapons should now do.** That gives the re-pull a control with a
known-correct answer supplied by the source itself — not by us, not by a wiki, not
by inference.

Every other check we can run on a weapon pull answers "did the numbers change?"
Only this one answers **"did they change the way CIG says they changed?"** — which
is the question that separates a working importer from one that ran cleanly and
produced nothing.

**This is a rule 12 instrument.** A check that cannot fail is not a check, and a
weapon diff with no expected answer cannot fail — it reports whatever it finds and
every result looks like a finding.

## The gate, before any control runs

**The manifest must state the build, and it must say 4.10.**

`FINDING_weapon-data-is-not-4-10-2026-08-27.md` §2 named the one-line fix: the
snapshot manifest records `git_head_commit` and `git_commit_date` but **not the
commit subject**, and the subject is the only place the patch version exists.
Both prior snapshots looked like progress and neither said 4.9.

    required    manifest carries git_commit_subject
    assertion   it contains 4.10.0-LIVE.12519617
    on failure  the controls DO NOT RUN and the pull is not a 4.10 pull

**Fail closed.** A pull that cannot prove which patch it is has already failed the
only test that matters, and running weapon controls against it would produce a
confident answer about the wrong build — which is the exact failure this project
has now logged four times.

This applies equally to a `Data.p4k` extraction, where the equivalent field is the
client build string. **The source may change; the gate does not.**

---

## Control 1 — the Size 4 ballistic gatling got stronger per round

CIG, 4.10 LIVE release notes, "Vehicle Weapon Rebalance":

> "We have rebalanced and categorized the Size 4 ballistic gatlings which should
> now hit roughly 68 percent harder per round."

    expect      per-PROJECTILE damage rises, order of +60% to +75%
    direction   is load-bearing; the magnitude is not
    on zero     FAIL — the importer did not carry the change

**The trap, and it is the whole reason this control is written out rather than
assumed: "per round" is not DPS.** A gatling's damage-per-second is a product of
per-shot damage and rate of fire, and 4.10 changed the ammunition class as well. A
diff that compares a computed DPS figure can show almost any number and still be
reading a correctly imported file. **Compare the per-projectile damage field.** If
the pipeline only holds a derived DPS, say so and treat this control as not run —
do not substitute the field you have for the field named.

## Control 2 — the Size 4 Combine Cannon lost its explosive component

CIG, same section:

> "The Size 4 Ballistic Combine Cannon splash was reaching far wider than intended,
> so the explosive component has been removed outright, making it a direct-hit
> weapon. Direct damage has also been reduced by roughly 10%."

    expect A    direct damage falls, order of -10%
    expect B    the explosive/splash component is GONE
    on either
    showing no  FAIL
    change

**Expect B is the one that will be missed, and it is the more important half.** A
removed component does not appear as a changed value. Depending on how CIG serialises
it, it lands as a field set to zero, a field absent from the record, or a whole child
object no longer emitted. **A diff that walks fields present in both versions will not
see any of those three.** The comparison has to be over the union of keys on both
sides, and absence has to be a reportable state distinct from "unchanged".

This is worth generalising beyond this control: **the pipeline has never yet had to
represent a property CIG deleted.** 4.10 is the first patch that deletes one, and the
never-overwrite rule means the 4.9 row keeps its explosive component forever while the
4.10 row must record its absence as a fact rather than as a null nobody wrote.

## Control 3 — two more fields on the gatling, in different subsystems

This is the strongest control in the set and it costs nothing extra. CIG did not
only state an outcome, they stated a **cause**:

> "Previously it had been inheriting the Size 3 gatling's ammunition and balancing
> class, which left it underpowered and, more importantly, unable to defeat armor a
> Size 4 weapon should defeat. **Both are now corrected.**"

    expect      the S4 gatling's ammunition reference changes
    and         its balancing / class field changes
    on either
    showing no  FAIL, even if Control 1 passed
    change

**Why this beats Control 1 on its own:** damage, ammunition reference and balancing
class are three different fields written by three different parts of CIG's data. An
importer that silently drops a whole category — a nested object, an unresolved
reference, a field whose type changed — can still carry a plain numeric damage value
through correctly. Control 1 alone would pass and the pull would be broken.

**If the ammunition reference on the S4 gatling still points at the S3 gatling's
ammunition after the pull, the pull is 4.9 data no matter what the manifest says.**
That is a second, independent proof of patch identity, derived from the data itself
rather than from a commit message — and it is worth keeping for exactly that reason.

## Control 4 — the negative control, and the suite is worthless without it

    take        a ship weapon CIG did NOT name in the 4.10 notes
    prefer      one in a different family and size class from the two above
    expect      no change in any measured field
    on change   the result is INCONCLUSIVE, not a pass

**Without this, "everything moved" passes Controls 1 through 3 while telling you
nothing.** A serialisation change in the dumper, a field-ordering change, a units
change, a re-export of the whole catalogue — any of these makes every weapon differ,
and the three positive controls would light up green on a diff that has detected
nothing but noise.

The positive controls prove the pipeline *can* see a change. This one proves it is
not seeing changes that are not there. **Neither half means anything alone.**

Note the asymmetry deliberately: a moving negative control does not mean the pull is
bad. It means **the diff is measuring the wrong thing** and the positive results
cannot be read until that is explained.

---

## Reading the outcome

    1,2,3 pass · 4 quiet     the pull is trustworthy. Proceed.
    any of 1,2,3 shows zero  the importer is broken. Not the patch, not CIG.
    4 also moves             inconclusive. Diagnose the diff before reading anything.
    magnitude off, direction
    right                    FLAG, do not fail. CIG wrote "roughly" twice and meant it.

**The magnitude line matters.** CIG's own numbers are approximate and their prose is
not a specification. A gatling that came back +52% instead of +68% is a question worth
asking — it is not evidence of a broken importer, and treating it as one would burn a
session chasing a rounding difference in someone else's balance pass.

---

## What this fragment does not cover, stated so nobody assumes it does

- **FPS weapons.** CIG published a stat block for the HDGW Arlington Rifle in the
  notes. It is not reproduced here and it is not a control — the client is the better
  source and this fragment is scoped to ship weapons.
- **Crafting.** The notes describe no recipe-system change, so there is no CIG-stated
  control available for the 1,597 blueprints. What *should* be checked is population
  rather than values: BUL-H4, the Vendetta HMG, ore pods, mining modules, containers
  and Wikelo's single-use blueprints are all new blueprint-shaped objects. **Expect new
  rows, not changed columns** — and no expected count, so this is an observation, not
  a control.
- **The question C3 called the most useful one in the whole request** —
  whether Missile, MissileLauncher, Turret, WeaponDefensive and BombLauncher are still
  at zero recipes in 4.10 — has **no CIG statement behind it either way**. It is worth
  running first and it cannot be written as a pass/fail control. Do not dress it as one.
- **Missiles generally.** 4.10 contains no missile balance pass. The last one was 4.7.
  A missile field that moves in a 4.10 diff is unexplained and should be treated as a
  question, not as data.

## Provenance of the two statements these controls rest on

Both quotations are from **Star Citizen Alpha 4.10 LIVE release notes**, RSI comm-link
21293, published 26 August 2026, section "Vehicle Weapon Rebalance". Read in full from
the rendered page — the comm-link is client-rendered and returns metadata only to a
plain fetch, so anything that reports it as empty has not read it.

The abridged Spectrum copy posted by Wakapedia-CIG (staff) links to the same document
and carries less. **The release comm-link (21242, "Alpha 4.10: Siege of Orison") is
marketing and contains no weapon prose at all** — checked, so nobody checks it again.
