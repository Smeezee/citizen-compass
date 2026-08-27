# FINDING — the fresh snapshot is not 4.10 data. Its upstream commit predates the patch. And the fabricator recipes have been on disk the whole time — 1,597 of them.

    from      C3 (Cowork), 2026-08-27
    for       C1 + Sleven
    ask       Sleven: "4.10 has just released... I want the most absolute up to
              date information... entire specs of each weapon that mounts to a
              ship and or missile... and what components it takes to make it
              through the fabricator"
    scope     measurement only. Nothing built, nothing fetched, no page touched.

---

## 1. THE THING TO KNOW BEFORE ANYTHING ELSE

There is a scunpacked snapshot dated **2026-08-27** on disk. It looks current.
**It is not 4.10 data.**

Its own manifest records the upstream commit it was cloned from:

    git_head_commit    db00b749833ebe4c4687f766c15fb88ba093fd6e
    git_commit_date    2026-08-20T12:08:49+02:00

**4.10 went live on 26 August. The upstream repository's last commit is the
20th.** The pull happened after the patch; the data in it was published before.

**So "we pulled fresh data on the 27th" and "we have 4.10 data" are two different
statements, and only the first is true.** A folder name is a pull date, not a
patch version. Anything built on it is 4.9-era regardless of when it landed.

**This is the third time on this project that a conclusion rested on a file being
the file somebody assumed it was**, and it is why the manifest capturing
`git_commit_date` earns its place. Without it this would have shipped as "verified
against 4.10."

## 2. What the fresh snapshot actually changed

Compared record by record against `20260801T204744Z`:

    ships              316 -> 316     no change
    ship-items        5384 -> 5384    no change
    items            21849 -> 21855   +6
    fps-items         5420 -> 5426    +6

**The six additions are armour, and nothing else.** Defiance Helmet Ultimatum,
Kiba Helmet, Calico Helmet Tactical, DustUp Helmet Ultimatum, Oni Kiba Helmet,
and the Sabine Undersuit Ultimatum.

**Zero new weapons. Zero new ships. Zero removals.**

**And every one of the 948 weapon-family items is unchanged in every measured
field** — size, grade, mass, all six damage channels, projectile speed, range,
rate of fire, capacity, effective range, and CIG's own Item Type label. Not one
value moved.

**Read that correctly: it means the SOURCE has not caught up to 4.10.** It does
not mean 4.10 changed no weapons. Those are opposite claims and only the first is
supported.

### CORRECTION, same day, from CIC — and it is sharper than the above

**CIC went to the repository and read the commit titles. The 20 August commit is
titled `4.9.0-LIVE.12344265`.** The 16 July commit our older snapshot came from is
the earlier 4.9 build, `4.9.0-LIVE.12232306`.

**So the comparison in this section was 4.9 against 4.9** — two builds of the same
patch. It was never capable of showing a 4.10 change, and "zero weapons changed"
is an unremarkable result rather than a finding about the patch.

**I framed it as "the source has not caught up," which was the right conclusion
reached without the fact that proves it.** CIC's version is better because it
names the build string.

**And the real 4.10 data landed today at 08:36 UTC**, tagged
`4.10.0-LIVE.12519617` — the exact build string in CIG's own notes. It did not
exist when this was written. **§2 must be re-run against it and until then this
section says nothing about 4.10.**

### The gap that let this happen, and it is one line to fix

Verified on disk: **no build string appears anywhere inside either snapshot's
files.** Grepped both for the `4.x.x-LIVE.nnnnnnnn` pattern — zero hits.

Our manifest captures `git_head_commit` and `git_commit_date`. **It does not
capture the commit MESSAGE, and the message is the only place the patch version
exists.**

    20260801T204744Z    4764726896973204a798325ed0f9ed7253e995e5   2026-07-16
    20260827T030607Z    db00b749833ebe4c4687f766c15fb88ba093fd6e   2026-08-20

**Both rows look like progress. Neither says 4.9.** One extra field —
`git_commit_subject` — and this whole confusion is visible at a glance forever
after. **That is the cheapest fix in this document and it should be done before
the 4.10 pull, so the pull records what it is.**

## 3. THE FABRICATOR DATA IS ALREADY HERE — 1,597 recipes

Sleven asked whether we could even find out what components a weapon takes to
build. **`data-layer/processed/blueprint_index.json` has held it all along.**

Each recipe carries the output item and its UUID, **craft time in seconds**, the
full ingredient list with quantities in SCU and a minimum quality per ingredient,
the **component groups** the recipe fills, and the **modifiers** each group
applies to the finished item.

A real one, complete — the Omnisky III Cannon:

    craft time      540 seconds
    Frame           Agricium, 0.36 SCU, min quality 1
    Emitter         Hadanite, min quality 1
    Aperture Iris   Dolivine, min quality 1

**By output type:** armour dominates — 217 helmets, 216 torsos, 213 arms, 213
legs, 25 backpacks, 23 undersuits. Then **174 personal weapons**, 96 ship guns,
75 power plants, 74 coolers, 62 shields, 60 radars, 57 quantum drives, 36 weapon
attachments.

Craft times run from **10 seconds to 9,060** — two and a half hours.

**Coverage against our 948 ship weapons:**

    WeaponMining        17 of  23 craftable    73.9%
    SalvageModifier      5 of   7               71.4%
    TractorBeam          8 of  12               66.7%
    SalvageHead          4 of   8               50.0%
    WeaponGun           96 of 193               49.7%
    Turret               0 of 313                0%
    WeaponDefensive      0 of 168                0%
    MissileLauncher      0 of 143                0%
    Missile              0 of  67                0%
    BombLauncher         0 of  14                0%

**Missiles and launchers have ZERO recipes.** Neither do turrets or
countermeasures. **That is a real answer to a real question** — as of this data,
you cannot fabricate a missile, and the ship-weapon crafting system covers guns
and industrial tools only.

**Whether that is still true in 4.10 is exactly what needs checking**, and it is
the single most useful question in this whole request.

## 4. Where 4.10 weapon data actually is, and it is not a wiki

**It is on Sleven's own machine, in the 4.10 client.**

`FINDING_the-coordinates-are-in-the-client-2026-08-27.md` established four days
ago that `Data.p4k` can be read directly — 161 GB archive, 1.36 million entries,
ZIP64 + zstd, extracted clean, node tables decoded and proven on two ships.

**The weapon definitions and the crafting recipes live in the same archive.** The
client on that machine IS 4.10. **It is authoritative, it is same-day, and it
needs nobody's permission to read.**

**A wiki is a volunteer's copy of this, later and lossier.** Sending a researcher
to read one, when the shipped source is on the disk and the tooling to open it is
already written and proven, is the worse of the two available options.

## 5. What genuinely does need an outside source

Two things, and only two:

**What CIG SAID changed in 4.10.** Patch notes name balance passes and new items
in prose. That is a statement of intent and it does not live in any data file.
Worth having beside a diff, never instead of one.

**What the damage types DO.** The data says a gun deals 65 Physical and 0 Energy.
It does not say whether Physical is better against shields or hull, or why a pilot
takes a repeater over a cannon. **That is gameplay meaning and it is not in the
files.**

## 6. What I checked and what I did not

**Checked:** both snapshots record by record; the 948 weapon-family items across
ten measured fields each; the six added items identified by name and type; the
snapshot's own manifest for the upstream commit date, which is what produced §1;
1,597 blueprints joined to the weapon list by UUID.

**Did NOT check:**
- **Whether the 4.10 client's weapon data actually differs from 4.9.** §4 says
  where to look, not what is there. **Nobody should assume the diff is large or
  small until it is run.**
- **The 82 MB star-citizen.wiki items file**, still unopened. It may carry
  damage-versus-shield multipliers, which would answer half of §5 from data.
- **FPS weapon specs.** 174 personal weapons are craftable and 5,426 FPS items
  exist; this finding covers ship weapons and the recipes, not personal weapon
  statistics.
- Nothing was fetched from RSI, and no page or dataset was modified.
