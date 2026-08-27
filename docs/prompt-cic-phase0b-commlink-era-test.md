# ADDENDUM TO THE CIC BRIEF — Phase 0b, one hour, and it may close a nine-year hole

    from      C3 (Cowork), 2026-08-08
    for       CIC, via Sleven
    follows   claude/prompt-cic-historical-archive-recon.md (Phase 0 complete)

---

## Why this addendum exists (for Sleven)

CIC's Phase 0 was good work — it tested what was asked, gave checkable proof values, respected
both gates, and flagged the middle era as **untested rather than assumed**. That last part is
the discipline this project keeps asking for and rarely gets.

**But read the result against our own coverage and there's a hole CIC's report doesn't name:**

    2013 – ~2016     archive pages READABLE          ✓ covered
    ~2017 – 2026     archive = JS shells             ✗ no coverage
                     our sealed snapshots start 2026-07-31
    2026-07-31 on    our own snapshots               ✓ covered

**That middle band is roughly nine years, and it contains most of the ships in the game.**
Anything removed or renamed between 2017 and mid-2026 currently falls into a gap that neither
the archive (per Phase 0) nor our snapshots can reach.

**CIC tested the middle era with the wrong page type, and that's my fault in the brief, not
its.** I asked for a *ship page* from ~2019. Ship pages are exactly the thing we now know is
JS-rendered. **Comm-Links are news articles, and news articles are normally server-rendered so
search engines can index them** — and CIC already proved a 2013 Comm-Link was fully readable
with its publication date baked into the static text.

**So the real question is not "are 2019 ship pages readable" — it's "did Comm-Links stay
static as the rest of the site went JavaScript."** If they did, the middle band is largely
recoverable, because Comm-Links carry announcement dates, removal notices, sale windows and
patch notes. That is the factual spine the preservation model needs, and it would matter far
more than any ship page.

One hour to find out. That's Phase 0b.

---

=== PASTE TO CIC FROM HERE ===

# Phase 0b — did Comm-Links stay readable as the rest of the site went JavaScript?

Good work on Phase 0. One correction to my own brief before we go further: I asked you to test
the middle era using a **ship page**, and ship pages are precisely the thing your results show
are JavaScript shells. That was a bad choice of test on my part.

**The question that actually matters:** you proved a 2013 Comm-Link is fully readable with its
publication date in the static HTML. Comm-Links are news articles, and news articles are
usually server-rendered so they can be indexed by search engines — so they may have stayed
readable even as ship pages went JavaScript.

If they did, that recovers roughly nine years (≈2017–2026) that we currently cannot reach from
any source. That band contains most of the game's ships.

**Please test one Comm-Link from each of these periods** — any Comm-Link, the topic does not
matter, we are testing the page type not the content:

    ~2017      ~2020      ~2023      ~2025

For each, report: archived URL, capture date, **readable / partly / empty**, and as proof one
or two factual values you can actually see in the text — ideally the article's own publication
date and its transmission/article ID, since those are what we would anchor timeline facts to.

**Then answer one question plainly:** through what date do Comm-Links stay readable in the
archive? If they are readable all the way to the present, say so — that is the single most
useful sentence you can give us right now.

## Also worth five minutes: patch notes

If Comm-Links hold up, check whether **patch notes** for any middle-era version are reachable
and readable the same way. Patch notes state when things were added and removed, which is
exactly the lifecycle data we are trying to build. Report the same three fields.

## On the slug problem — stop guessing, enumerate instead

You noted the Aurora slugs you guessed returned no index hits. Don't guess them.

**The capture index supports prefix and wildcard queries.** Rather than guessing a slug,
query the *path prefix* and let it return every URL ever captured beneath it — for example
everything the archive ever saw under the site's `/pledge/ships/` path, or under
`/pledge/Paint/`. That turns slug discovery from guesswork into enumeration.

**That enumerated list is itself a deliverable, not just a means to one.** A list of every
ship and paint URL CIG ever published, with first and last capture dates, *is* the historical
index we are trying to build — it does not require reading a single page, and it works even
for the eras where pages are empty shells.

## Real slugs from our own data, so you don't have to guess the modern ones

These are pulled from our own UEX snapshot and are genuine current-era paths:

    https://robertsspaceindustries.com/pledge/Paint/Aurora-Green-And-Gold-Paint
    https://robertsspaceindustries.com/pledge/Paint/Aurora-Light-And-Dark-Grey-Paint
    https://robertsspaceindustries.com/pledge/Paint/Aurora-Invictus-Blue-And-Gold-Paint

Paint URLs follow `/pledge/Paint/<Title-Case-Hyphenated-Name>-Paint`, and packages sit under
`/pledge/Packages/...`. We hold **31 Aurora livery slugs** and 601 paint store URLs in total —
if you need more of them for index queries, ask and we'll hand over the list rather than have
you rediscover it.

## Unchanged

Same rules as before: facts and citations only, never CIG's prose, no images, cite every claim
with URL and capture date, flag uncertainty rather than smoothing it, and report what you
could not find. **Phases 1 and 2 remain gated on Sleven's approval** — this addendum is still
Phase 0 work, testing feasibility rather than harvesting anything.

=== PASTE TO CIC ENDS ===

---

## Assessment of Phase 0, for the record

**What CIC got right:** tested the actual question, gave specific checkable proof values
rather than assertions, distinguished 158 KB of HTML from 3.2 KB of readable text (which is
the right measurement and not an obvious one), stopped at three failures per rule 6 instead of
grinding, and explicitly labelled the middle era untested. It also independently confirmed the
CDX index works and produced a real bracketing example — the Aurora LX sale pinned to early
May 2013 from URL metadata alone.

**What I cannot do:** verify any of it from this session. `web.archive.org` is blocked by this
environment's content restrictions, and I am not routing around that. **Per the standing rule
that CIC's output is a claim until verified locally, this remains unverified** — though the
proof values are specific enough that Sleven can spot-check one URL in under a minute, and I
would suggest exactly that before Phase 1 is approved.

**One small data-quality item found while pulling the slugs:** one of our stored paint URLs
(`Aurora Foundation Festival Livery`) carries a Google Analytics tracking string
(`?_gl=1*clcjgo*...`). Tracking parameters should be stripped before any of these URLs are
published or used as identifiers — they are session junk, not part of the address.
