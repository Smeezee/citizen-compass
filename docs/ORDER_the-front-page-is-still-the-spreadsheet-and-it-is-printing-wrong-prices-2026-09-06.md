# ORDER — the front page is still the spreadsheet because nobody ever queued the wall, and while it sat there it has been printing wrong prices on 47 ships. Fix the prices first. That is step 1 and it ships alone.

    from      C1, 2026-09-06
    for       Code
    trigger   Sleven: "Why am I still looking at the old system that we had in
              there? What is going on? fix it."
    basis     docs/SPEC_the-front-page-becomes-the-wall-2026-08-31.md - C1's own
              spec, marked "NOT QUEUED", written six days ago and never queued
              by me. That is the answer to his question and it is my failure,
              not a pipeline fault.

---

## 0. THE ANSWER TO WHAT HE ASKED, BEFORE THE TASKS

**Nothing is broken and nothing failed to deploy.** The testing site is current:
the sweep ran green against this exact payload, 524 files went up, and I checked
the shipped marker file's sha256 myself. **He is looking at the old page because
the new page was never built.** 523 of the 524 files were already on the server -
one file changed - so the site looks exactly as it did, because everything since
2026-08-31 has been hardpoints, models and controls.

**And there is a real defect sitting in the old page that the spec named and
nobody actioned.** Verified in the served build just now:

    const SHIPS = [{"id":129,"name":"100i", ...
        "auec_price": 1089270,
        "dealers": ["New Deal","Astro Armada"],
        "confidence": "verified"

    ship_dealer_prices.json says   New Deal      1,089,270
                                   Astro Armada  1,146,600

**The page prints one price beside two shops, it is wrong for one of them by
57,330 aUEC, and the row is labelled `verified`.** 47 ships are like this. The
890 Jump is out by 3,267,800. **The corrected data has been on disk since
2026-08-31** at `data-layer/derived/ship-prices/ship_dealer_prices.json`, 63
ships, mapped to our five dealer names with zero unmapped and zero conflicts.

**That is worse than an old-looking page and it is the thing to fix first.**

## 1. STEP 1 - PER-DEALER PRICES INTO THE SHIPS ARRAY. NO VISUAL CHANGE.

Ship this on its own. The spec says so and the reason holds: everything else
depends on it, and it leaves the page no worse if the rest never happens.

**The shape, and it is what `app/models.py` already models** -
`in_game_price_auec` has always lived on `ShipDealerListing`, never on the ship:

    "dealers": [ {"name": "New Deal",     "auec": 1089270},
                 {"name": "Astro Armada", "auec": 1146600} ]

**Keep `auec_price` as the CHEAPEST of them**, so anything still reading the old
field gets the least wrong answer rather than an arbitrary one.

**I could not trace where `const SHIPS = [` is emitted** - it is searched for in
the assembled page at `build_deploy.py:941` and appears in no `_src` file I can
find. **That is your pipeline. I am not guessing at it.**

**Where a ship is not in the 63:** leave its dealers as they are today. **Do not
invent a per-dealer price and do not spread `auec_price` across the shops** - an
absent price and a copied one are different facts and the page has to be able to
tell them apart.

**Where the 63 disagree with the current `auec_price`:** the file wins for the
per-dealer figures, and **report every ship where the current single price
matches NONE of the dealer prices.** That is a different defect from "one of two
is wrong" and I want it counted, not smoothed.

## 2. STEP 2 - THE CONTROL, AND IT IS THE PART THAT MATTERS

**There is no check anywhere that a ship's stated price is the price at the
dealer printed beside it. That is why this survived six days in plain sight, and
it is the same shape as every other thing we have found this week.**

Write it. I would rather you designed it than that I specified it - you found the
last four of these - but it must at minimum:

- read the DEPLOYED page, not the source, the way `_verify_wall.mjs` reads
  `testing/index.html` live;
- assert every per-dealer figure against
  `data-layer/derived/ship-prices/ship_dealer_prices.json` by **exact equality**
  on our dealer names (rule 17 - the mapping is already exact, do not add a
  matcher);
- **fail when a ship carries one price against two or more dealers that the
  source says differ** - that is the exact defect live today, so it must be a
  state the control can detect;
- carry a control that could fail (rule 12): a mutation that perturbs one dealer
  price and is caught by name.

**`confidence: "verified"` on a row whose price is wrong is its own defect.**
Whatever sets that flag should not be setting it on a ship whose per-dealer
prices we have never checked in game. **Report what sets it. Do not change it in
this order** - it is a labelling rule and it is Sleven's.

## 3. STEP 3 - THE NINE EMPTY SHIPS

245 of 254 have a picture; **9 have nothing.** On a table a missing value is a
dash. On a wall it is a large empty rectangle that reads as broken. **Design the
empty state before anything visual changes.** I did not design one and said so in
the spec; it is still the weakest part.

**`data-layer/derived/ship-thumbs/` does not exist on disk.** The spec cites it
and it is not there. **Find it or say it is gone** before step 4 is planned -
the wall cannot be built without the images and I am not going to discover that
halfway through.

## 4. STEP 4 IS THE WALL, AND IT IS NOT IN THIS ORDER

Steps 1-3 each leave the site better and none is visible as a half-built thing.
**Step 4 is the only one that must not ship in halves**, so it gets its own order
once 1-3 are done and once Sleven has seen the empty state.

**Do not build the map tab.** It is on hold pending CIC.

## 5. Also queued by this order, not for tonight

`docs/FINDING_the-5-percent-threshold-measures-the-sampler-not-the-render-2026-09-06.md`
answers Sleven's other question. **The 5% threshold is measuring the sampling
stride** - 80% of stride-1 hulls fail it and 0% of stride-5 hulls do, and
correcting for the stride reverses which group is denser. **Do not touch that
control while the current sweep receipt is the one holding the deploy open.**

## 6. Rules that still apply

Testing only, never the live site. No `-IgnoreSweep`. Nothing commits or pushes
without Sleven's explicit go-ahead (rule 2), no `git add -A`. Never delete - `mv`
to `_to_delete/`. NO FUZZY MATCHING.

---

*C1, 2026-09-06. He asked why the page has not changed. It has not changed
because I wrote a spec and then spent six days on markers. The price defect is
the part I am least comfortable having left sitting.*
