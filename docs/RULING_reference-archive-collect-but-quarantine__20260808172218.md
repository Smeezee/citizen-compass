# RULING (Sleven) + ARCHITECTURE — collect CIG's content as a reference corpus, and make "not published" a property of where it lives rather than a promise

    from      C3 (Cowork), 2026-08-08
    ruling    Sleven, 2026-08-08
    for       C1 + Code
    status    Sleven's decision, recorded. The architecture below is C3's proposal for
              carrying it out safely; the decision itself is not re-argued.

---

## 1. The ruling, in Sleven's own framing

> *"I say we collect everything, even the content from CIG. Not gonna use the content per se,
> but having it and knowing what everything looks like and how everything should piece
> together might inspire us to make things different but useful for users nowadays."*

**The distinction being drawn: collect and study, do not republish.** The corpus is reference
material for understanding how CIG structured things and for informing Citizen Compass's own
original work. It is not a source of publishable text or images.

Rights interpretation is Sleven's alone under rule 8 and is not revisited here. What follows
is engineering: how to make that distinction hold in practice, because on this project a
policy alone will not.

## 2. Why a policy alone will not hold

**The load-bearing reason is git, and it has nothing to do with the site.**

Anything committed to the repository is in every clone, every bundle and every backup
permanently. Removing it later is a **history rewrite, not a delete** — and until that rewrite
is done everywhere, "we took it out" is false the moment anyone checks out an earlier commit.
**This is the single most expensive mistake available here, it is irreversible in practice, and
it is one `git add -A` away** — a command this project already carries a standing caution
against for unrelated line-ending reasons.

Secondary, and much cheaper to recover from: this project has logged **five** silent-success
failures where something was published, deleted or skipped while the run reported success. That
pattern is the reason to prefer a structural guarantee over a remembered rule — not any
specific past incident.

**The fix is not more care. It is putting the corpus somewhere no build, deploy or commit can
reach.**

*(An earlier draft of this section also cited the testing site's static-asset behaviour. That
was unnecessary — the corpus never goes near the deploy tree under R1 — and it re-raised a
risk Sleven had already assessed and accepted on the record. Removed.)*

## 3. Proposed architecture — quarantine by location, not by intention

**R1. The reference corpus lives OUTSIDE the repository.** Not in `citizen-compass/`, not in a
gitignored subfolder of it. A sibling directory — e.g. `C:\Users\david\cc-reference\` — with no
path from any build, deploy or publish step. A `.gitignore` entry is not sufficient: it is one
`git add -f` or one misconfigured tool away from failing, and gitignored files still get picked
up by directory-walking scripts.

**R2. Nothing in the corpus is ever an input to a build.** The publishable data layer may not
read from it. If a build ever needs something from the corpus, that is the signal a human
transformation step is missing — not a reason to add a path.

**R3. One-way gate, human-authored.** Facts may leave the corpus. Content may not. A fact
leaves by a person writing a new sentence in Citizen Compass's own words, with the corpus
cited as where it was learned. **Copying is never the mechanism, even for a phrase.** This is
the same line already settled for game-file data: facts yes, creative assets no — applied to a
new source.

**R4. Provenance stamped at collection time, not derived later.** Every stored item records
source URL, capture date, and `usage: reference-only`. A stored item with no provenance is
treated as unusable rather than as probably-fine — the same fail-closed rule the collector's
export already applies to screenshots it cannot prove came from the game.

**R5. Never in git, never in the database.** See §2 — this is the rule the whole arrangement
exists to guarantee, and R1 is what makes it structural rather than remembered.

**R6. The corpus is backed up separately, or not at all.** The existing backup script mirrors
the repo tree to the My Book. If the corpus sits outside the repo (R1), it is outside that
mirror by construction — which is correct. Backing it up is a separate decision; do not solve
it by moving the corpus inside the repo.

## 4. One piece of pushback, offered once

**"Everything" is probably not what the stated purpose needs, and it costs more than a sample
in every dimension that matters.**

The purpose Sleven gave is understanding and inspiration — *how everything looked and how it
pieced together*. That is served by a **representative sample**: a few dozen ship pages across
eras, a set of Comm-Links spanning the format changes, the retired-paint pages, a handful of
patch notes. Enough to see the structure and the house style.

A complete scrape instead buys: far more storage, far more time, a much larger surface for R2
and R5 to fail against, and a corpus too big for anyone to actually read — which defeats the
inspiration purpose it was collected for.

**Against Sleven's own decision priority — maintainability first, convenience last — a curated
corpus beats an undifferentiated one.** A tidy 500-item reference set that someone actually
browses is worth more than 50,000 files nobody opens.

**This is a recommendation, not an objection.** If Sleven wants completeness, R1–R6 still hold
and the plan works; it is just larger. Saying it once and then supporting the call either way.

## 5. What this changes for CIC

CIC's brief currently says facts-and-citations only, no prose, no images. **Under this ruling
that constraint is relaxed for collection and unchanged for publication.** If Sleven approves
content collection, CIC's instruction becomes:

- Collect page content into the reference corpus, with provenance per R4.
- **Continue to report facts only in its findings**, in its own words, exactly as now — the
  findings are a publishable artifact and the corpus is not.
- Still no attempt at anything requiring a login, and still nothing from Sleven's Hangar.

**Phase 1 (URL metadata / capture index) is unaffected and remains the safest, highest-value
first step regardless** — it produces the lifecycle brackets the preservation model needs and
involves no CIG content at all. Recommend it runs first whatever is decided about content.

## 6. What I did not do

- Did not make or revisit the rights decision. Sleven's, rule 8, recorded not analysed.
- Did not build, move or collect anything. No corpus exists yet.
- Did not verify current `.gitignore` contents or the backup script's exact include paths
  against R5/R6 — **both should be checked before any collection starts**, and I have not done
  it.
- Did not assess storage requirements, because scope (§4) is undecided.
