# RESPONSE — CIC. The wall passes decider C cleanly. The map fails, and it fails by telling the player something false.

    from      CIC (Claude in Chrome), 2026-08-31
    for       C1 + Sleven
    order     ORDER-CIC-open-our-page-and-tell-us-if-it-is-just-another-one-2026-08-31
    file      the-wall.html, 4,297,041 bytes, mtime 2026-08-31
    rule 16   MEASURED / COULD NOT DETERMINE / NOT LOOKED AT on every claim.

    instrument   The Browser pane refuses Windows file:// URLs, so the page was
                 staged and rendered in headless Chromium at a pinned 1440x900,
                 which is a BETTER instrument for this job than the pane was for
                 Fleetyards. Caveat carried honestly: system fonts may differ
                 from Sleven's machine by a few pixels. Nothing below turns on a
                 few pixels.

    screenshots  Committed beside the concept file, in
                 data-layer/derived/main-page-concepts/ :
                   CIC-2026-08-31_map-mole-selected.png
                   CIC-2026-08-31_wall-fold-1440x900.png

---

## 1. DECIDER C — WE PASS, AND WE PASS BY A LOT

Same rule applied to us as to Fleetyards: one screen, no click, no tab switch, no scroll.

    OURS, 1440x900, scrollY 0

    card container  .blk s3      y  365 – 738
      ship image    .shot        y  366 – 616
      in-game price              y  668 – 687     "34,398,000 aUEC"
      pledge price               below, same card
      shop + place               below, same card
    viewport                            900
    headroom left                       162 px

    FLEETYARDS, same viewport, for comparison

    hero image / 3D              y  146 – 746
    in-game price                y 1482 – 1502    582 px BELOW the fold
    shop location                behind a button

**MEASURED PASS.** Roughly ten ship cards are fully visible in the first screen, and each
one carries the render, the aUEC price, the pledge price, the shop and the place. Erkul has
the price, the shop and the place with **zero imagery anywhere**. Fleetyards has the
imagery and puts the price 582 px down and the shop behind a click.

**This is real and it is the strongest thing on the page.**

### The filters cost 40% of the first screen

    header / search / mode tabs     y    0 – 56
    CAREER, GROUP BY, HOW YOU
      CAN GET IT                    y   56 – 235
    "254 of 254 ships"              y  ~260
    manufacturer band               y  285 – 350
    FIRST SHIP PIXEL                y   366        40.7% of a 900 px fold

Erkul spends about 90 px before its first card. **We spend 366.** That is the price of
twenty career chips, three grouping options and four availability options all being open
at once. It is a real cost and it is the cheapest thing on this list to fix — the filter
block collapses behind one control (`$('ftoggle')` already exists in the source).

---

## 2. THE MAP — THE HARD VERDICT

**It does not carry spatial information, and the spatial information it appears to carry
is false.** This is the "worse than a list" case C1 asked me to test for, and it is met.

### What is actually in the SVG — MEASURED

    1 svg, viewBox 0 0 780 560, rendered 1082 x 777 at y 285
    85 circles      80 are Math.random() starfield, regenerated every render
                     5 are shop markers, ALL r=18, ALL fill #1C3050
    10 text nodes    5 place names + 5 "shop · system" captions
     0 paths
     0 lines
     0 ellipses

No orbits. No system boundaries. No scale. No legend. No jump links. **Nothing encodes
which system a dot is in except a 10 px grey caption under it.**

The panel bottom sits at y 1062. **On a 900 px laptop screen two of the five shops are
below the fold** — a map of five points that does not fit on one screen.

### The projection is the defect — MEASURED from source and data

`_wall.tpl.html:430` min–max normalises x and y across the five dealer points onto the
canvas with 95 px padding. The coordinates in `the-wall.html` are real and enormous:

    New Deal          Lorville      Hurston     x  12,850,128,103   stanton
    Astro Armada      Area18        ArcCorp     x  18,586,917,330   stanton
    Crusader Showroom Orison        Crusader    x -18,956,880,483   stanton
    Teach's           Levski        Delamar     x  -9,641,669,472   nyx
    Buy & Fly         Ruin Station  Pyro        x -52,336,834,868   pyro

**Every Star Citizen system has its own local origin. Stanton-local and Pyro-local
coordinates are not in a shared frame of reference.** Projecting them onto one linear
canvas treats numbers measured from different origins as if they were commensurable. The
coordinates are real; the projection is not valid.

**The measured consequence, in rendered units:**

    Orison  ↔ Levski     107      DIFFERENT SYSTEMS
    Lorville ↔ Area18    193      same system
    Orison  ↔ Lorville   266      same system
    Orison  ↔ Area18     353      same system

**Levski, in Nyx, is drawn as Orison's nearest neighbour — three times nearer than Area18,
which is in the same system as Orison.** The picture says the opposite of the truth.

### And it lands on the exact feature meant to justify the map

Select the MOLE. The two stocking dealers are **Lorville (Stanton)** and **Levski (Nyx)** —
and they are the two markers the map draws closest together, 269 units apart, with Area18,
Orison and Ruin Station all further away. **The map's best moment tells the player its
biggest lie.**

### What partly rescues it, and must be credited

The side panel prints, in orange, directly under the two shops:

> **"1 of these is outside Stanton — a jump, not a cruise."**

**The page already knows.** That sentence is exactly right and no surveyed tool says
anything like it. But **when a picture and a caption disagree, the picture wins** — the
dots are read before the sentence, and the dots say "these are neighbours".

### What the map genuinely does that a list does not

Selecting a ship keeps stocking dealers at r=18 and prints the price **on** the dot, while
non-stocking dealers shrink to r=11 and darken. "Which of the five carry this, and at what
price" in one glance. **That is real.**

**But it is information about set membership, not about space** — and the list panel
beside it already renders exactly that, in a fifth of the area, *with stock counts the map
does not show* (121 / 68 / 12 / 37 / 14 in stock).

### The fix, because the idea is worth keeping

Group by system first — three labelled regions or three panels — project each system's
coordinates **within its own region**, and render inter-system distance as a labelled jump
rather than as pixels. Keep the price-on-the-dot and dim-the-rest behaviour, which is the
good part and survives the change untouched.

**Until then, the list beside it is strictly better and the map should not ship.**

### Smaller, same panel

All five rows in the side list carry a **"cheapest"** tag under the price. Every shop
cannot be cheapest. It presumably means "the cheapest ship at this shop", but rendered as
a right-aligned tag under a number it reads as a claim about the shop. Ambiguous.

---

## 3. MANUFACTURER GROUPING — REAL, AND IT EARNS ITS SPACE

**MEASURED: 12 groups, not eighteen.** Anvil, RSI, Aegis, Drake, Origin, Crusader,
Consolidated Outland, Esperia, Kruger, Aopoa, Gatac, Banu.

Each band is 75 px and carries **a logo, the name, and real aggregates**:

    Anvil Aerospace
    39 hulls · longest 126 m          24 in game   33 in store   3 shops

**That is a summary, not a heading**, and it is the answer to C1's question. A heading you
scroll past is dead weight. A band that tells you Anvil has 39 hulls, that 24 are buyable
in game, and that they are spread over 3 shops is information available **nowhere else in
the surveyed set** — Erkul, Fleetyards and CStone are all flat alphabetical with no
manufacturer grouping at all.

**The scroll cost is real but smaller than feared.** Group tops across an 18,465 px
document: 302, 2657, 4734, 8259, 9810, 12963, 14707, 15314, 16564, 16904, 17271, 17686.
The last four are one row each (340–415 px). You are not scrolling past eighteen headings;
you are scrolling past twelve, eight of which are large enough to be worth stopping at.

---

## 4. SIZE-BY-LENGTH — THE CUE LANDS, THE CROP UNDOES IT

**MEASURED.** Four image-height tiers at a constant 269 px width:

    112 px   25 images        cropped top and bottom
    150 px   20 images        ≈ native aspect, no crop
    196 px   11 images        cropped left and right
    250 px    3 images        cropped left and right, hardest

Source renders are 340 x 191 (aspect 1.78). At 269 wide, the aspect-correct height is
**151 px** — so only the 150 tier shows the whole ship. `object-fit` is **cover** on 39 of
40 sampled.

**So the biggest ships show the least of themselves.** The Carrack — 126 m, the tallest
card on the page — is a tight crop of hull plating. The 24 m Hornets beside it show the
entire airframe. **The size cue reads as intentional, not as a broken grid; it does not
read as a bug.** But it fights the picture it is applied to, and it is backwards: the ship
you most want to look at is the one you see least of.

Cheapest fix: `object-fit: contain` on the 196 and 250 tiers, letterboxed on the card
background. The card stays big, the ship stays whole.

---

## 5. THE NINE EMPTY CARDS — HONEST IN WORDS, NOT IN PICTURES

**MEASURED: exactly 9 cards contain no `<img>` at all. 0 failed loads. 0 empty `src`.**

They render as a flat dark rectangle with the text **"no image and no model"** in ~10 px
grey, bottom-left inside the frame, with the normal name, prices and tags below.

**The wording is honest and the intent is right.** But in a wall of photographs a flat dark
rectangle with low-contrast grey text **reads as a failed image load**, not as a stated
absence. The honest content is there and is nearly invisible. A centred label, a ghosted
outline, or a visibly different card treatment would say the same thing and be believed.

**A small inconsistency worth a line.** The page footer says *"230 carry a real ship image
already in the repo; the other 24 fall back to an outline traced from their own model, and
say so."* That reads as though all 24 get an outline. Nine of them have neither an image
nor a model and say so instead. The sentence is not wrong, but it is easy to read as a
promise the page does not keep.

**A method note against myself.** My first measurement pass reported **186 broken images**.
That was false — the images are 245 lazy base64 payloads that had not decoded when I
measured. Re-measured after a full scroll and settle: 9. **Same failure shape as the
Fleetyards empty hero, caught this time because I went looking for it.**

---

## 6. TWO LOCATION LEVELS AGAINST FOUR AND SIX — WHAT IT COSTS ON SCREEN

    ours        Astro Armada  Area18
    Erkul       Stanton › ArcCorp › Area 18 › IO North Tower
    CStone      Nyx - Levski - Sublevel 01 - Hangar transit -
                Teach's ship shop - Ship Shop

**Ours gets the player to the city. Theirs gets them to the counter.**

In practice the cost is **small for the three Stanton shops and real for exactly one**.
Astro Armada at Area18 and New Deal at Lorville are on the main concourse — a player who
lands there finds the shop. **Teach's at Levski is Sublevel 01 via the hangar transit**,
and that is precisely the kind of thing a first-timer loses ten minutes to.

So the depth we lack is missing where the game is least legible. **But with only five
shops this is one sentence of text per shop, not a structural problem.** Low cost, cheap
fix, and worth doing before the shop count grows.

---

## 7. THE HONEST COMPARISON

### What ours does that none of them do

1. **Picture, in-game price, pledge price, shop and place in one card, in the fold.**
   Measured at §1. Erkul has the price and the place and no imagery at all. Fleetyards has
   the imagery and puts the price 582 px below the fold.
2. **Manufacturer grouping with real per-manufacturer aggregates.** §3. None of the three
   groups by manufacturer at all.
3. **Availability as a filter axis** — In game and store 105 / In game only 74 / Store only
   62 / Neither yet 13. All three tools model availability as a property of a row. **None
   lets you slice the catalogue by how you can get the ship.** This is the quietest idea on
   the page and I think it is the best one.
4. **Concept and pledge-only hulls are present and labelled.** Erkul's Ship Finder returns
   nothing for concept-only ships; ours carries all 254 and says which is which.
5. **Career chips with live counts** across the whole catalogue.

### What they do better than ours — the important half, and it is longer

1. **Location depth.** CStone six levels, Erkul four, ours two. §6.
2. **Stock counts and rental data.** Fleetyards: 28 rental locations at 1/3/7/30-day
   pricing. CStone: a full rental table. Ours: neither. (Our own map panel shows stock
   counts — the wall does not.)
3. **Per-row provenance shown to the visitor.** CStone stamps every shop row with a
   verified date. Ours flags confidence per ship but nothing per shop row.
4. **A real 3D model in the hero, one click.** Fleetyards renders the GLTF holo in place.
   Ours has flat renders and nine blanks.
5. **A cart and a buy route.** Erkul assembles a multi-shop shopping list with a running
   total and reorderable stops. **We have nothing like it.**
6. **Density.** Erkul puts roughly twelve items in the fold; we put about ten, after
   spending 40% of the screen on filters.
7. **A freshness stamp on the price itself.** Erkul: "Prices updated 14 hours ago."
   Fleetyards: a UTC timestamp on every ship. Ours: an honest footer, but nothing per row.
8. **Cross-linking out.** Fleetyards links to Erkul, SPViewer, Game Files and Ship Matrix
   from every ship page. Ours links nowhere.

### What ours does WORSE than the spreadsheet it replaces — nobody had looked

1. **You cannot sort. There is no sort control on the page at all.** The spreadsheet let
   you order 254 ships by price and read the answer off the top. The wall offers filters
   and grouping and no ordering. **This is the regression I would raise first** — "what is
   the cheapest ship I can actually buy" was one click on the old page and is now
   unanswerable without reading every card.
2. **You cannot scan a column.** A table lets the eye run down one field across 254 rows.
   A masonry wall in 12 groups across 18,465 px cannot be read that way, by construction.
3. **18,465 px of scroll** to reach the last manufacturer, against one sorted table.
4. **No side-by-side comparison.** A table row-compares for free; cards do not.

### The single thing that would make a player pick ours

**It is the only page that answers "what can I actually get right now" as a first-class
question — filter to *In game only*, and every ship you see is one you can go and buy, with
its picture, its price and its shop on the same card.** Erkul cannot filter that way and
excludes concept hulls entirely; Fleetyards and CStone treat availability as a footnote on
a row.

**That is a real answer, not "nothing yet". But it currently sits behind a map that
misinforms and a page that cannot be sorted, and both of those will be noticed first.**

---

## 8. COULD NOT DETERMINE

**The ship zoom.** Clicking a card did not open a detail view in headless Chromium —
document height and body text were unchanged. **I am not reporting this as broken.** The
handler exists in source (`_wall.tpl.html:521`, delegated from `#stage` onto
`.blk[data-n]`, calling `zoom(n)`), and the failure is more likely my instrument than the
page. Someone should click it on Sleven's own machine.

**Worth knowing from that source read:** `zoom()` already handles per-shop price variance —
if `priceRange(s).varies` it renders *"In-game price: lo – hi aUEC"* and a green *"Cheapest
at: <shop>"*. **That is the feature the CStone finding said we would need if dealer prices
really do differ.** It is already written.

---

## 9. THE OTHER TOOLS — NAME ONLY, NOT LOOKED AT

Dropped by C1 as unable to move a decider: `spviewer.eu`, `sc-trade.tools`, `ccugame.app`,
`robertsspaceindustries.com/pledge/ships`.

Others named in this session's searches or in project docs, none examined:
`uexcorp.space`, `starcitizen.tools`, `hangarbase.org`, `scfocus.org`,
`starcitizenhelp.com`, `HangarXPLOR`, `Starjump`, `StarShip42` (myfleet.gg's predecessor),
`ATLAS deck maps`, `SC DataHub`, `vectisfps.com`, `stoppingpower.io`, `scfpscalculator.com`.
**All NOT LOOKED AT. None surveyed, none judged.**

### On `survey.cstone.space` — my recommendation is do not spend the approval yet

C1 offered one approval for it, on the grounds that a spatial counter-example would mean
our map is not new. **The finding above changes that calculus.** Our map has to be rebuilt
whether or not somebody else has one, because as it stands it misinforms. Whether
Cornerstone renders a survey map somewhere is interesting; it is not what decides the next
move. **Spend the approval after the map is corrected, when the question becomes "is ours
still distinctive", not before, when the question is "is ours truthful".**

Sleven's call, not mine — but that is the recommendation.
