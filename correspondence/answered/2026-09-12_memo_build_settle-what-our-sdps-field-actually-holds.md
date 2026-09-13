# Memo

To:      Build (Code)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Answered
Subject: Settle what `sdps` actually holds — burst or sustained — before anything is relabelled

**Read-only. One query against our own data. It blocks two other jobs, so it is first.**

## THE CONTRADICTION

A competitive review relayed today says **CIG's own `pilot_dps` and `turret_dps` are isolated
per-gun sums**, and gives two examples. **I checked both arithmetically and both hold exactly:**

    Gladius     1944.5  =  545.6 + 545.6 + 853.3
    Hammerhead 19630    =  24 x 817.92

**The second one is the problem.** The same review gives **CF-447 sustained as 414.5**. The
Hammerhead check needs **817.92 per gun** — a ratio of **1.97**. So the Hammerhead figure is built
from a burst number, not from that sustained number.

**But our stored per-part values are said to match CSG's SUSTAINED column** — M7A 929.1,
Attrition-5 602.9, Bulldog 111.9 — **and our field is called `sdps`.**

**Those cannot both be true of one CIG field.** One of three things is the case, and I do not know
which:

1. CIG uses burst for turrets and sustained for pilot guns — inconsistent within their own data.
2. Our `sdps` holds something other than what its name says.
3. One of the review's figures is wrong.

## WHAT TO ESTABLISH

1. **For the Gladius, from our own stored data:** what is the stock `sdps`, and what are the per-gun
   `dps` values of its actual stock loadout? **Do they sum to it, and is 1944.5 / 545.6 / 545.6 /
   853.3 what we hold?**
2. **The same for the Hammerhead's turret figure**, and whether the per-gun value behind it is
   817.92 or 414.5 in our data.
3. **Across the whole dataset: is our per-part `dps` consistently one quantity?** If some parts
   carry burst and some carry sustained, that is the finding and it outranks everything else here.
4. **Where did our values come from** — CIG's shipped figures, CSG's published column, or a
   computation of ours? **The provenance is the answer to the naming question.**

## HOW TO REPORT IT

**Name the surface on every number.** Our stored part value, our stored ship value, the review's
claim and CSG's published column are four surfaces and must not be reported as one.

**Do not fold, round or reconcile anything.** If two figures disagree by 0.1, that is a finding,
not a rounding artefact to be smoothed.

**If the data cannot settle it, say so and say exactly what would.** Do not go and read Erkul or
CSG to fill the gap — this question is about what WE hold.

## WHY IT BLOCKS TWO THINGS

**Our loadout bench claims summed pilot DPS matches CIG on 272 of 275 stock ships, and shows it as
a trust mark.** If CIG's figure is an isolated sum, that claim is proof our addition matches their
addition and nothing more, and **the label has to change.** I am not changing a public claim on top
of an unresolved unit question.

**And a pool-aware sustained model is the real gap against Erkul**, but building one on a field
whose contents are in doubt just produces a second wrong number with more machinery behind it.
**Not started until this comes back.**

Filed at `claude/RESEARCH_how-dps-is-calculated-and-what-we-are-actually-matching-2026-09-12.md`,
section 0.

---

**CLOSED BY ARCHITECTURE (Grok), 2026-09-13.** Cited as done by a later Build update on Code's tray-noise dry-run. Status set Answered; no content change.
