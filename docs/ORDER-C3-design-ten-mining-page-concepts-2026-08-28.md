# ORDER for C3 — design ten mining pages. Deeply detailed, creative, interactive, and a HUD somebody actually enjoys using.

    from      C1 (Cowork), 2026-08-27 23:40 local
    for       C3
    raised by Sleven, in his own words: *"design 10 deeply detailed ideas on
              how to build a page for mining... it needs to be creative and
              somewhat interactive and easily used with a visually appealing
              HUD"*
    deliver   ONE document into `inbox/`. Ten concepts. Not a survey.

---

## 1. WHY THIS IS WORTH A SESSION

Citizen Compass is a ship reference. **Mining is the half of the game the site
has never spoken to**, and the data for it has been sitting on the machine
unopened. Measured today:

    resources.json          274 mineable · 244 cave harvestable
                             25 salvageable · 14 harvestable
    crafting demand          37 materials, with what each one is FOR
    raw -> refined           30 pairs CIG states outright
    rarity tiers             27 commodities: common/uncommon/rare/epic/legendary
    recipes                  1,607, each with build time and an ingredient tree
    ships with a mining or salvage port     23
      MOTH 9 · Vulture 6 · Reclaimer 6 · Salvation 4 · Fortune 3 · MOLE 3
      · Prospector 1
    mining parts on the ship page           20

**The single strongest number we hold:** `Aslarite` is required by **856 of the
1,607 recipes**. Ouratite 495, Laranite 353, Tungsten 266. That is a demand
ranking for the entire crafting economy, derived from CIG's own recipes, and
**no tool states it.**

Every figure above is on disk right now. Nothing in this order needs new data.

---

## 2. WHAT I NEED BACK, AND WHY THE FORMAT MATTERS

**Ten concepts. Each one a SPEC, not a pitch.** A paragraph of enthusiasm is
not designable and not costable. Each concept carries, in this order:

1. **The question a player has** — in a player's words, not ours. If you cannot
   write the question, the concept is a feature looking for a user.
2. **The screen** — what is on it, where, and what the eye hits first. Sketch it
   in monospace if that is clearest.
3. **The interaction** — what the person does, and what changes when they do.
   Name the control: slider, toggle, hover, drag, click-through.
4. **Which data feeds it**, by file and field, from §1. **A concept that needs
   data we do not have goes in §5 instead**, not in the ten.
5. **What it CANNOT say**, stated as the page would state it. This site's
   standard is that a page says what it does not know.
6. **Build cost** — hours, days, or "needs a decision first" — and what the
   riskiest part is.
7. **Why somebody would come back to it.** A page nobody returns to is a
   brochure.

**Rank all ten at the end**, by value against buildability, and say which one
you would build first and why. **Disagreeing with the order of the list is part
of the job**, not a liberty.

---

## 3. THE HOUSE STYLE, WHICH IS NOT NEGOTIABLE AND IS NOT A CAGE

**The look already exists** — go and read `testing/_deploy/loadout.html` in a
browser before designing anything. Dark field, cyan and amber, a holographic
3D stage, monospace figures, disclosure bars that fold the explanation away
until asked for. **The mining page must feel like the same product**, not a
bolt-on.

**HUD means legible under pressure, not busy.** Sleven's word is *"visually
appealing"* and his consistent complaint across this project has been noise:
too many lines, hulls reading as a solid mass, panels that shift things around.
**A HUD that looks like a HUD in a screenshot and is unreadable in use is a
failure of this order, not a success of it.**

**Interactive means CLIENT-SIDE.** The site is static HTML on Cloudflare
Workers with no backend and no database at read time. Sliders, filters, sorts,
hovers, a 3D stage, local storage — all available. Anything needing a server
call is out.

**One page must work on a phone.** Not all ten, but say which of yours do.

---

## 4. THE CONSTRAINTS THAT WILL KILL A CONCEPT IF YOU MISS THEM

**PRICES ARE NOT OURS AND CANNOT BE VERIFIED.** CIG ships **no prices at all** —
the only cost-like fields in the entire export are `AmmoCost` and
`CostPerBullet`. Every price on this site comes from UEX, a community source,
and **0 of 26,657 rows are verified**. A concept that answers *"where do I sell
this for the most"* is building on sand and must say so on its own face.
See `FINDING_the-economy-data-we-never-opened-2026-08-28.md` §4a.

**THE TRADE-LOCATION GRAPH IS CAPABILITY, NOT INVENTORY.** 96,717 entries in
`commodity_trade_locations.json` look like a "where to sell" dataset and are
not: every one is tag-matched, and a "Security Checkpoint" appears to trade all
109 commodities. **Do not build a concept on it.** I nearly published a number
from it and the check is what stopped me.

**NO FUZZY MATCHING, anywhere, in anything.** Exact equality or refuse. This
project has been bitten twice.

**Fan Kit Agreement: non-commercial only.** No ads, no donations, no paid
access, no recolouring or distorting CIG assets.

**Say what is measured and what is estimated.** Every number on this site
carries its provenance or it does not ship.

---

## 5. A SEPARATE SECTION FOR WHAT WE CANNOT BUILD YET

Some of the best mining ideas will need data we do not hold — live rock scans,
prospecting yields, refinery times, actual market stock. **Put those in a
section of their own with what each one would need**, and where that data might
come from. That list is worth as much as the ten, because it tells Sleven what
the ceiling is.

**Do not pad the ten with concepts that cannot be built.** Ten buildable, plus
an honest list of what is out of reach.

---

## 6. WHAT NOT TO DO

- Do not design a price comparison table. It is somebody else's game and we
  cannot verify a single row.
- Do not propose a login, an account, or anything that stores a person's data
  on a server.
- Do not propose scraping RSI. `/media/` is disallowed by their robots.txt and
  rights questions are CLOSED.
- Do not write a market-analysis essay. Ten designs.
- Do not assume a number without opening the file it is in. If a figure in §1
  looks wrong, **check it and tell me it is wrong** — that has happened four
  times this week and every one improved the work.

---

## 7. DONE-WHEN

One document in `inbox/`, ten concepts each carrying all seven fields from §2,
ranked, with a first pick and a reason — plus §5's out-of-reach list.

**Take the time it needs.** This is a design job, not a survey, and the mining
data has been sitting unopened long enough that a week of it being unopened is
cheaper than a bad page.

— C1
