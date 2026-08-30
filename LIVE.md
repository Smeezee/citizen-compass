# LIVE — what is on the public site, and what proved it

**One writer: C1.** Nothing enters this file on the strength of a build, a
passing check, or a deploy to testing. **Only what a stranger with no password
can load right now, verified by loading it.**

    public site      https://citizencompass.netlify.app
    testing site     https://citizencompasstesting.citizencompass-contact.workers.dev
                     PASSWORD-GATED. Nothing here counts as shipped.

---

## THE CURRENT STATE OF THE PUBLIC SITE

    version          v0.3.9
    ships            254
    page says        "Compiled/updated: 2026-07-30"
    verified         2026-08-27 13:10 local, by fetching the page

**Twenty-eight days.** Not four.

`CRITIQUE_senior-analyst-review-2026-08-27` puts the last ship at 2026-08-23.
**The page itself disagrees and the page wins.** The critique understated this
in the project's favour; the honest figure is worse.

---

## WHAT IS NOT ON IT

Every one of these is built, checked, and reachable only behind a password:

- **Real hardpoint positions from CIG's own game files.** 754 ports across 64
  hulls. Proven in a real browser on the Gladius, with a control that goes red
  when the overlay is removed (`_verify_marker_positions.mjs`, 2026-08-27).
- **The holo viewer**, on 258 models.
- **19 ship models** imported and rescaled to ratio 1.000 — including the
  Mantis and the Hermes, which were blank pages for weeks.
- **The hardpoint picker**, the settings-revision fix, the loadout bench.
- **4.10 keybind extraction**, and a generated profile the game itself accepts.

The public site has none of it. A visitor today sees July.

---

## WHY, AS FAR AS IT IS KNOWN — and one part of this is not a discipline problem

**Netlify deploys were credit-blocked.** Recorded in `CURRENT-STATE.md`: the
testing site moved to Cloudflare because of it, and the live site was left on
v0.3.9 "until that clears". `scripts/deploy_live.ps1` exists (committed 08-21,
`0a4d5ed`) and there is no record in the repo of it ever being run.

**So "nothing has shipped in 28 days" is not purely a focus failure.** Part of
it is a billing state nobody has re-checked. **Whether the block is still in
force is UNKNOWN and is the first thing to find out** — a month of work is
parked behind a question nobody has asked in three weeks. It is on the queue.

---

## CORRECTED ON DISK, NOT YET PUBLIC — 2026-08-30

**The public page says the wrong patch and has since 4.10 shipped.** It reads
*"Alpha 4.9.0 (LIVE July 15-16, 2026)"* and its badge says *Live 4.9.0 / PTU
4.10.0*. **4.10 is live and PTU is empty** — verified from RSI's own roadmap API
field (`data.description`: *"Live Version: 4.10.0 ... PTU Version: ø"*) and from
RSI's own Spectrum thread *"Alpha 4.10 LIVE - Hotfix Central"*, published
2026-08-27.

**Both source files are corrected on disk. NOTHING IS DEPLOYED**, so this is not
a LOG entry and does not go in the table below. The public site still says 4.9.

    Patch: Alpha 4.10.0 "Siege of Orison" (LIVE)  |  Ship data compiled: 2026-07-30
    ● Live 4.10.0       ◆ PTU —

**AND THE FIRST VERSION OF THIS FIX CARRIED AN ERROR OF C1'S, CAUGHT BY CODE.**
It moved `Compiled/updated` to 2026-08-30. **That date is a claim about the
SHIP DATA - when the prices and dealer rows were compiled - and nothing was
compiled.** A header was edited and stamped as though the page had been rebuilt.

**The label is now `Ship data compiled: 2026-07-30`, which is the truth and is
better than what was there before.** The old line said 4.9 was live, which hid
the gap entirely by being wrong about the patch. The page now states both facts
and lets a reader judge the distance between them: **the game is on 4.10, our
numbers are from July.**

**The live date is deliberately absent** — no RSI source states one for 4.10 and
a date that cannot be sourced does not go on the public site.

**Also measured, and never measured before on the PUBLIC files:** 0 AI/agent
traces and 0 spelling defects against the game's own strings, in both files.

**And the live site has TWO source files that disagree by 33 lines** —
`static/preview.html` (the master) and `releases/latest.html` (the mirror, and
the one actually published). The live file pulls its fonts from
`fonts.googleapis.com` where the master embeds them, and the master carries a
second legal paragraph the live file does not. **The legal difference is rule 8
and is untouched.** The patch correction was applied to both identically so the
divergence is unchanged. See
`docs/FINDING_the-live-site-was-a-month-wrong-about-the-patch-and-has-two-source-files-2026-08-30.md`.

---

## THE RULE FOR THIS FILE

An entry is added only when **all four** are true:

1. It is on the public site.
2. Someone loaded the public URL and saw it — not a build log, not a deploy
   exit code, not the testing site.
3. The date and the person or session that verified it are recorded.
4. What proved it is named: a URL fetched, a check run against the public
   origin, a screenshot.

**A deploy that reported success is not evidence.** This project has been
bitten five times by something reporting success while doing nothing, twice on
2026-08-27 alone, once inside C1's own code.

---

## LOG

| date | what shipped | proved by |
|---|---|---|
| 2026-07-30 | v0.3.9, 254 ships | the page's own "Compiled/updated" line, read 2026-08-27 |

**One row. That is the point of this file.**

---

*Maintained by C1. Created 2026-08-27 13:15 local, on Sleven's instruction,
from `CRITIQUE_senior-analyst-review-2026-08-27` Finding 4.*
