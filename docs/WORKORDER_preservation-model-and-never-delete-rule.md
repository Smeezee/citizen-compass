# WORK ORDER / FINDING — the preservation mission needs one hard rule set BEFORE the next patch import, or history is lost silently

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1 (→ Code)
    ask       Sleven: "I want to give people everything Star Citizen has had, even if it's
              old stuff, with a blunt disclaimer — this doesn't exist anymore, this is what
              used to be. Even paints that aren't available. Same with Port Olisar. It's
              history I want to keep alive."
    urgency   The rule in §3 must land before the next snapshot import. After that, the
              loss is silent and unrecoverable.

---

## 1. Two things verified on disk, which frame the whole job

**The Aurora Mk I is already saved, by accident of good discipline.** All six variants are
sealed in `snapshots/20260801T204744Z/ships.json`:

    RSI Aurora Mk I LX / LN / ES / SE / MR / CL     (+ RSI Aurora Mk II)

CIG is reportedly removing the Mk I. **We already hold its stats, loadout and dimensions at
patch 4.9.** The existing Phase 1 snapshot rule captured it before anybody knew there was a
reason to. That is the architecture working, and it is worth saying out loud.

**Port Olisar is the counter-example, and it is already lost.** The location gazetteer
resolves 2,066 entities; **Port Olisar is not one of them.** It survives in our data only as
two incidental artefacts:

    "Port Olisar - Stanton"      a holographic decoration item, placeholder description
    "Stuck at Olisar T-Shirt"    "...recreates the infamous ASOP terminal screen frequently
                                  seen at Port Olisar. Anyone who's visited this bustling
                                  transportation hub can relate to the gnawing fear of
                                  seeing this screen..."

**The station is gone from the files. A souvenir t-shirt describing it is not.** That is the
failure mode in miniature: once CIG removes something, it leaves our derived data completely,
and only stray references survive.

## 2. The mission is a real differentiator, not a nice-to-have

Erkul, Hardpoint.io, SPViewer and UEX all answer **"what is."** None answers **"what was."**
A reference that can say *this ship existed from 2013 to 2026, here were its stats, here is
what replaced it, and here is why it went* is not competing with any of them. It is also the
only part of the catalogue that **cannot be regenerated later** — a current-state tool can
always be rebuilt from today's files; a historical record cannot be rebuilt from anything
once the window closes.

## 3. THE RULE — importers never delete

**Hard rule, to be enforced by construction, not by memory:**

> **An importer may create a row and may update a row. It may never delete one.**
> An entity absent from the current patch is marked absent. It is not dropped.

**Why this is urgent rather than tidy:** the natural behaviour of a patch importer is to
write what the patch contains. When the Aurora Mk I disappears from `ships.json`, a normal
import simply does not write it — and if the loader replaces rather than merges, the row is
gone. **Nothing errors. The run reports success.** That is precisely the silent-success
failure shape this project has now logged five times (the robocopy `[\/]` bug, the `$null→0`
exit code, `wrangler pages deploy`, the vacuous privacy check, the unreachable schema-version
branch). It should be assumed to be the default outcome unless prevented.

**Acceptance test, with the negative control the project's hard rule 12 requires:** import a
patch with a deliberately removed entity; the row must survive with `status=retired` and
`last_seen_patch` set. Then break the guard and confirm the row disappears — a check that
cannot fail is not a check.

## 4. Row lifecycle — extends `last_verified_patch`, does not replace it

The existing decision (every row carries `last_verified_patch`) already answers *"is this
current?"* Preservation needs *"when did this exist, and what happened to it?"* Proposed
addition, in the hybrid-schema style already settled (real indexed columns for anything
queried, JSONB only for the tail):

    first_seen_patch    text     first patch we ever observed it in
    last_seen_patch     text     last patch it appeared in
    status              enum     live | retired | renamed | replaced | never_released | unknown
    successor_id        fk       Aurora Mk I -> Aurora Mk II; nullable
    removal_note        text     plain-English, Citizen Compass's own words
    evidence_tier       enum     sealed | external | testimony   (see §5)

`status` and `evidence_tier` are indexed columns, not JSONB — both will be filtered on
constantly ("show me everything retired", "show me only what we can prove").

**`unknown` is deliberate and load-bearing.** An entity that vanished before we started
sealing must not be silently labelled `retired` — we do not know that it was retired rather
than renamed. Guessing here would manufacture false history, which is worse than a gap on a
site whose whole premise is being trustworthy about provenance.

## 5. Three tiers of history, three different sources — be honest about which is which

**Tier 1 — sealed.** Anything present in a snapshot we hold. Authoritative, free, already
done. The Aurora Mk I lives here. **Our snapshots begin 2026-07-31**, so Tier 1 is currently
about one week deep going backwards, and grows forward from here. Every future patch widens
it. This is the tier that costs nothing and must never be lost.

**Tier 2 — external.** Things removed before we started sealing: Port Olisar, the Aurora's
2019 stats, retired paint artwork. Not in any file we hold. Would need an outside source, and
**every outside source carries a rights question that is Sleven's alone** — rule 8. Not
proposing a source here.

**Tier 3 — testimony.** The part that was never in any file at all: *you logged into Port
Olisar, called a ship out, and flew around nothing.* No schema ever held that. No scrape
recovers it. It exists only because people remember it.

**Tier 3 is the strategic point.** It is the one thing a competitor cannot copy from a data
dump, it is the natural home of the AI Historian's "continuously updated with verified
fan-sourced info" model, and it is a coherent answer to why the Historian can be
subscription-funded while the underlying data stays free forever on Citizen Compass: **the
data can be handed over; the memory has to be told.** Consistent with the standing split, not
a change to it.

## 6. The disclaimer is a feature, and it should be data-driven

Sleven's own framing — *"give them that disclaimer very bluntly"* — should not be a hand-written
banner per page. It should be generated from `status` + `last_seen_patch` + `evidence_tier`,
so it cannot drift out of sync with the data and cannot be forgotten on a new page type.
Roughly:

    retired   "The Aurora Mk I was removed from Star Citizen. Last seen in patch 4.9.
               These figures are preserved from our sealed 4.9 snapshot and are not current."
    unknown   "This existed in Star Citizen and no longer does. We hold no sealed data for
               it; the details below come from <source> and are not verified against a
               game file."

The second shape matters more than the first: **it tells the reader exactly how much to trust
the page**, which is the same discipline as `location_pattern_verified` on the collector
sidecars and the front end's unverified-data flag. Same idea, applied to time.

## 7. Recommended order

1. **Set the never-delete rule and the acceptance test first.** Cheap now; the next import is
   the deadline. Everything else can follow at any pace.
2. Add the lifecycle columns and backfill `first_seen_patch`/`last_seen_patch` from the
   snapshots already sealed. Mechanical, no judgement calls.
3. Ship the retired-paint case first as the pilot — **498 of 1,099 liveries already have no
   store URL**, which is a ready-made, already-verified retired set with real names. It
   proves the whole pattern end to end without needing a single external source.
4. Only then consider Tier 2 sourcing, which is blocked on Sleven's rights call regardless.

## 8. What I did not do

- Did not write or modify any importer, schema, or migration — Code's lane.
- Did not decide any rights question about external historical sources. Rule 8.
- Did not verify *how* CIG is removing the Aurora Mk I, only that we already hold it. The
  removal claim is Sleven's; I checked our side of it, not CIG's.
- Have not audited the current importers to see whether any of them already delete. **That
  check should happen before the next import** and I have not done it.
