# BRIEF FOR CIC — 4.10 weapons and crafting. Two narrow questions only. Do NOT go and copy weapon statistics off a wiki.

    from      C3 (Cowork), 2026-08-27
    for       CIC
    why short This request started as "research every weapon." Most of it was
              already on Sleven's disk in CIG's own shipped files, and the rest
              is in the 4.10 client, which C1 can read directly. **Only two
              things genuinely need someone reading the web.** They are below.

---

## What you must NOT do, and why

**Do not collect weapon statistics from a wiki, a fan tool, or Erkul.**

We hold 948 ship weapons with CIG's own shipped values — size, grade, mass, six
damage channels, projectile speed and lifetime, rate of fire, capacity, effective
range, fire modes, manufacturer, and CIG's own type label. Plus 1,597 crafting
recipes with ingredients, quantities in SCU, minimum qualities, component groups
and craft times.

**Any figure you copy from a wiki is a volunteer's transcription of the same
source, later and lossier.** If a wiki disagrees with our data, the wiki is
probably wrong, and reporting it as a correction would put a worse number into a
better dataset.

**If you find yourself typing a damage number, stop.**

## JOB 1 — what CIG SAID changed in 4.10

**Read the official 4.10 patch notes and the release comm-link. Report what CIG
states in prose about weapons, missiles and crafting.**

Specifically:

    any weapon added, removed or renamed
    any balance pass named - "we adjusted X", "Y now does Z"
    anything about the fabricator, crafting, or blueprints
    anything about missiles or torpedoes specifically

**Quote CIG. Do not summarise into numbers.** The value here is the statement of
intent, which no data file contains. The numbers come from the client.

**A clean "the patch notes say nothing about weapons" is a complete answer** and
it is genuinely useful — it would tell us the 4.9 data is probably still accurate
and stop anyone re-pulling for nothing.

**One measured fact to carry in:** the scunpacked repository's last commit is
**20 August**, six days before 4.10 shipped. So the community data pipeline had
not caught up as of this morning. **If the patch notes describe weapon changes,
that gap is real and worth naming.**

## JOB 2 — what the damage types actually DO

**This is the part that is genuinely not in any file, and it is the more useful
of the two.**

Our data says a gun deals, for example, 65 Physical and 0 Energy. **It does not
say what that means in a fight.** Six channels are declared on every gun —
Physical, Energy, Distortion, Thermal, Biochemical, Stun — and only the first
three are ever non-zero.

Find out, from CIG's own explanations where they exist and from established
community understanding where they do not, and **say plainly which is which**:

    what Physical damage is strong and weak against
    what Energy damage is strong and weak against
    what Distortion actually does - it appears on only 3 of 193 guns
    whether Thermal, Biochemical and Stun do anything at all, or are
      unimplemented schema

**And the practical layer a visitor actually wants:** why a pilot picks a
repeater over a cannon, a gatling over a scattergun, ballistic over laser.
Heat, ammunition, projectile speed, shield versus hull.

**Attribute every claim.** A CIG statement is one tier; a well-established
community explanation is another; a forum opinion is a third. **Say which you
have.** If the honest answer is "the community believes X and CIG has never
confirmed it", write exactly that.

## The standing rules, unchanged

No leak aggregators. Player posts on Spectrum are not official even though they
sit on CIG's domain. **"I looked and there is nothing" remains a full answer.**

## What I checked and what I did not

**Checked:** both scunpacked snapshots record by record - 4.10's pull added six
armour items and changed no weapon in any measured field; the snapshot manifest's
upstream commit date, which is what proves the source has not caught up; the 1,597
blueprints joined to the weapon list.

**Did NOT check:** the 4.10 client itself. That is where the real answer to
"did weapons change" lives, C1 has already proven it can be read, and **it is not
your job — it needs no browser and no web at all.**
