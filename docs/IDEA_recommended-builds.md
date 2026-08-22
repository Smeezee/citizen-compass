# IDEA — "the best build for this ship". PARKED. Nothing is built for this.

    from    Code, 2026-08-22, written at L15 of ORDER_the-ship-page-2026-08-22-FINAL
    status  PARKED. Not started, not designed, not scheduled.
    why     Sleven: *"that can come later with much more research"*

---

## What it is

A ship page that answers "what should I put on this?" rather than only "what
can I put on this?" — a named, opinionated loadout per hull, with a sentence
saying what it is for.

## Why it is parked, in Sleven's words

> "that can come later with much more research"

That is not a scheduling note. It is the whole problem stated in six words: a
recommendation is only worth reading if somebody has done the research, and
nobody has. A recommended build assembled from the numbers we already have
would be an opinion wearing the costume of a measurement, which is the one
thing this site is built not to do.

## THE TENSION, NAMED — because it is what to design around

**§0 of the order says the page has no opinion.**

> "We don't need to name any of these builds... we just have to make it all
> available for them to build anything they want with any type of thing in
> mind. If they wanna take a Hammerhead and max it with racing and agility
> parts, they can. That's their choice."

**A recommendation IS an opinion.** So this feature and the page's founding
principle point in opposite directions, and pretending otherwise is how it
would get built badly.

That tension is not a reason to refuse it. It is the design constraint. What it
rules out is the shape most sites reach for first:

- **Not a default.** Nothing may arrive pre-recommended. The page opens on the
  ship's own stock loadout, as it does today, and a recommendation is something
  a visitor asks for.
- **Not a ranking.** "Best" implies one axis. The Hammerhead-with-racing-parts
  case is exactly the player this site is for, and a build that scores badly on
  a combat axis is not a worse build — it is a different question.
- **Not anonymous.** A recommendation needs an author and a date on it. "The
  site says" is the failure mode; "measured against 4.9, by X, for Y" is not.
- **Not silent about its own basis.** The same CIG / summed distinction the
  readout already carries applies double here. A recommendation built on our
  sums is a weaker claim than one built on CIG's figures, and the page already
  knows how to say which.

## What it would need before it could be built

1. **A stated purpose per recommendation.** "Best" is unanswerable; "longest
   time on station for a solo miner in 4.9" is answerable. The purpose is the
   feature; the parts list is the output.
2. **A measurement basis nobody has yet.** Effective DPS against real armour
   profiles now exists (L5). Time-to-kill, sustained-fire duration against
   capacitor and cooling, and quantum range under real fuel burn do not.
3. **Authorship and a patch stamp**, carried like `last_verified_patch` is
   today, so a recommendation ages visibly instead of quietly.
4. **A way to disagree with it on the page.** A recommendation a visitor cannot
   immediately edit is a dead end; one that loads into build B is a starting
   point. The bench already does A/B, so the mechanism exists.

## What already exists that this would sit on

- Per-port fitment (L3) — so a recommendation can never name an unmountable part.
- The full readout (L6) — so its claims can be checked against the same numbers
  a visitor sees.
- The armour matchup (L5) — the first real "good against what?" axis on the site.
- The share link (L12) — a recommendation is a URL, not a new data structure.

## What must NOT happen

- **Do not build any of this.** Not a stub, not a placeholder tab, not a
  hidden flag. The order says build nothing for L15 and this document is the
  entire deliverable.
- **Do not compute a "score" per part** as groundwork. A score is the opinion,
  arriving early and unlabelled.
- **Do not let it become a default view.** §0.
