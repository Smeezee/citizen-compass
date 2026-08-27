# BRIEF FOR CIC — historical Star Citizen recon, phased, test-first

    from      C3 (Cowork), 2026-08-08
    for       CIC, via Sleven
    purpose   Feed the preservation model in
              claude/WORKORDER_preservation-model-and-never-delete-rule.md
    paste     Sleven: hand CIC everything from "=== BRIEF STARTS ===" down.

---

## Why this brief exists (context for Sleven, not for CIC)

Sleven wants Citizen Compass to preserve what Star Citizen *used to* have — removed ships,
retired paints, dead locations like Port Olisar — with a blunt "this doesn't exist anymore"
disclaimer. That needs external history, because our sealed snapshots only reach back to
2026-07-31 and anything removed before then is in no file we hold.

**Three things shape this brief:**

1. **A known technical risk.** C1 already verified that RSI's modern ship pages, roadmap,
   Ship Matrix and Spectrum bodies are JavaScript-rendered and return empty shells to a plain
   fetch. **Archived copies will very likely be the same empty shells.** That is an inference,
   not a verified fact — so the brief tests it in Phase 0 before anyone spends real effort.
   Old-era RSI pages (2013-2016) were far more static and may be perfectly readable. Nobody
   knows yet. **One hour of testing decides whether this is a week of work or a dead end.**

2. **A better first target than page content.** The Internet Archive publishes a *capture
   index* — a machine-readable list of which URLs were archived and when, with no page content
   involved. **That index alone answers "when did this page first appear and when did it stop
   existing," which is exactly the `first_seen` / `last_seen` / `status` data the preservation
   model needs.** It is metadata about URLs, not CIG's creative work, and it is useful even if
   every archived page turns out to be an empty shell. That is why Phase 1 harvests the index
   before anyone reads a single page.

3. **The rights line is Sleven's, and this brief does not cross it.** Sleven has already
   ruled, in `docs/CORRECTION_extracted-textures-are-not-changed.md` and the description-rights
   hold: **factual data is fine; CIG's written descriptions, artwork and other creative assets
   are not ours.** This brief applies that existing ruling to a new source and asks CIC for
   *facts and citations only* — dates, names, prices, what changed when — never CIG's prose or
   images. **Whether that existing ruling extends to archived RSI pages at all is Sleven's call
   and nobody else's (rule 8).** Do not start Phase 1 or 2 until he says so. Phase 0 is a
   feasibility test that reads nothing into the project and can run regardless.

---

=== BRIEF STARTS ===

# CIC — historical Star Citizen recon for the Citizen Compass preservation project

## What we're doing and why

Citizen Compass is building a permanent record of things Star Citizen **used to have** and no
longer does — removed ships (the Aurora Mk I is being retired now), retired paints, and dead
locations like Port Olisar. Every such entry will carry a blunt disclaimer: *this no longer
exists in the game.*

We hold sealed game-file snapshots going back only to 2026-07-31. Everything removed before
that date exists in no file we have. That's the gap you're filling.

## Hard rules — these are not negotiable

1. **Facts only. Never CIG's prose.** Bring back dates, names, prices, dimensions, version
   numbers, and what changed when. **Do not copy CIG's marketing or description text, and do
   not bring back images.** If a fact only exists inside a sentence of CIG copy, report the
   *fact* in your own words and cite where you saw it. We will write our own descriptions.
2. **Cite every single claim** with the exact URL and the capture date. A fact without a
   source is unusable to us — we will throw it out rather than publish it.
3. **Separate confirmed from uncertain, explicitly.** If you found one source, say so. If two
   sources disagree, report both and say they disagree. **Never smooth over a conflict.**
4. **Never guess a date.** "Between March and June 2016" is a useful answer. A made-up precise
   date is worse than no answer, because it will get published and believed.
5. **Report what you could not find**, by name. A gap we know about is manageable. A gap we
   don't know about becomes a wrong page on the site.
6. **Stop and report if a phase looks unproductive.** Do not push through. Three failed
   attempts at the same thing means stop and tell us.

## PHASE 0 — feasibility test. Do this first. Nothing else starts until it reports.

**This is the whole decision point, and it should take under an hour.**

The concern: RSI's modern site is JavaScript-rendered, so archived copies may be empty shells
with no real content in them. Old RSI pages may be fine. **Test it.**

Open these in a real browser via the Internet Archive's "go back in time" view and report,
for each, whether you can actually read ship data (names, prices, stats) as text on the page,
or whether the page is blank / a loading skeleton / an error:

    a) An RSI ship page from roughly 2014       (early static era)
    b) An RSI ship page from roughly 2019       (middle era)
    c) An RSI ship or paint page from 2024-2025 (modern JS era)
    d) An RSI Comm-Link news article from ~2013-2015
    e) The RSI Ship Matrix from any year you can find

**Report back, per URL:** the exact archived URL, the capture date, and a plain
readable / partly readable / empty verdict — plus a couple of real values you could see, as
proof it's genuinely readable rather than looking readable.

**Then state one conclusion:** which eras and page types are worth pursuing, and which are
dead. If everything is empty shells, say so clearly — that is a completely acceptable and
genuinely useful answer, and it saves us weeks.

## PHASE 1 — the capture index. Only after Sleven approves. Metadata, not content.

The Internet Archive exposes a queryable index of *which URLs it captured and when*. This is
listing data — URL, timestamp, HTTP status — not page content.

**Why we want this more than page text:** if a ship's page was captured regularly from 2013
and captures stop in 2026, that brackets when it existed. That gives us first-seen and
last-seen dates for the historical record **without reading CIG's copy at all.**

For each target in the list below, report: first capture date, last capture date, roughly how
many captures exist, and any long gaps.

**Targets, in priority order:**

1. **Aurora Mk I** — all variants (LX, LN, ES, SE, MR, CL). Highest priority; it's being
   removed right now.
2. **Port Olisar** — any RSI page, Comm-Link or patch note that establishes when it arrived
   and when it was removed.
3. **Other removed locations** — Levski is the obvious second one; find others if the index
   shows pages that stopped being captured.
4. **Retired paints** — we already hold 498 retired livery *names*; we want their **first
   available and last available dates**, not their names.
5. **Ships that were renamed** — this one matters to us more than it sounds. Our whole
   catalogue joins on ship name, so a rename silently breaks things. Any evidence of a ship
   changing name, with dates, is high value.

## PHASE 2 — targeted fact extraction. Only if Phase 0 says pages are readable.

Do **not** attempt a broad sweep. Go after these specific facts, in this order:

1. **Original announcement date and original USD price** for each removed or retired ship.
   This exists nowhere else — it is not in game files and never will be.
2. **Concept-to-flyable timeline**: announced, concept sale, flyable, removed.
3. **What replaced what** — e.g. did the Aurora Mk II formally supersede the Mk I, or did
   they coexist? Give evidence, not inference.
4. **Removal announcements** — when CIG said a thing was going away, and what reason they
   gave. **Report the reason as a fact in your own words** ("CIG stated it was removed as part
   of the Stanton rework"), not as a quotation.

## Format we want back

A plain list, one row per fact:

    subject | fact | date (or date range) | source URL | capture date | confidence (high/medium/low)

That's it. No essay. **We will do the writing; you do the finding.** Long prose summaries are
harder for us to verify and slower for us to use than a list with sources on every line.

## What NOT to do

- **Do not download or reproduce images**, including ship renders and paint previews.
- **Do not copy CIG description or marketing text** into your report.
- Do not attempt to reach anything requiring a login, and do not touch Sleven's Hangar for
  this task.
- Do not go to community wikis for **retired paint names** — we already hold all 1,099 and
  it would waste your time. Wikis may be reasonable for *dates* if RSI's own pages are dead,
  but flag it and ask before relying on one.
- Do not fill a gap with a plausible guess. Leave it blank and name it.

=== BRIEF ENDS ===

---

## Notes for Sleven

**The order matters and Phase 0 is the important one.** If archived RSI pages turn out to be
empty JavaScript shells, Phases 1 and 2 change completely and you'll have learned that for an
hour instead of a fortnight. This project has been bitten repeatedly by building on an
unverified premise — this is that same pattern, caught early on purpose.

**Phase 1 is the sleeper.** Capture dates alone give us the lifecycle data the preservation
model actually needs, and they are URL metadata rather than CIG's creative work. Even in the
worst case where every page is unreadable, Phase 1 still produces something usable. If you
only approve one phase, approve that one.

**The rights call is entirely yours**, and this brief is written to keep the ask on the safe
side of the line you already drew — facts and citations, no prose, no images, our own words.
Extending that ruling to archived RSI pages is still your decision, and I'm not making it.

**What I'd expect realistically:** solid results on dates and prices, patchy results on early
ship stats, and very little on Squadron 42 — there was never much structured public data for
it. And for the thing you actually described to me, logging into Port Olisar and flying around
nothing, no archive will have it. **That one only exists because people remember it**, which
is exactly the case for the Historian's fan-testimony side rather than any scrape.
