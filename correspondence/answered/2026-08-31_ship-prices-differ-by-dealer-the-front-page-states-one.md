# Memo

To:      Build
From:    Engineering
Date:    2026-08-31
Status:  Answered
Subject: ship prices differ by dealer — 47 rows on the front page state one price against several shops

**A standing project belief is wrong.** It was written down as: *ship prices do not
vary between dealers in-game at this point in development — no "cheapest dealer"
highlighting needed.* **They do vary.**

## Measured

CIC found two prices for one ship on CStone. I checked Fleetyards' API per ship and
they agree on the Avenger Titan to within 4 aUEC. **63 ships pulled, one call each:**

    prices DIFFER between dealers      47
    several dealers, same price        13
    one dealer only                     3

    Vulture     Lorville 2,513,700  ·  Buy and Fly 2,646,000  ·  Levski 2,778,300
    890 Jump    Lorville 62,088,400 ·  Area 18    65,356,200
    Reclaimer   Lorville 30,164,400 ·  Levski     33,339,600

**The spread is always exactly 5% or 11%**, so it is a location modifier rather than
noise — but it is NOT derivable: Lorville is reliably −5%, and Teach's is base on some
hulls and +5% on others. **The figures have to be carried, not computed.**

## What our data says today, and it is wrong in both directions

**43 rows store the CHEAPEST price and list every dealer beside it.** Someone reads
our page, flies to Levski, pays more than we said.

**Three store the DEAREST**, so we overstate:

    890 Jump   we say 65,356,200   Lorville is 62,088,400   we are 3,267,800 over
    Starfarer  we say 13,891,500   Lorville is 12,568,500   we are 1,323,000 over
    X1 Force   we say 132,300      Lorville is 125,685

**And one matches no dealer at all: the 400i.** We say 8,389,063. The two real prices
are 8,398,060 and 8,840,070. **Our number is neither.**

## What I have done, and it is only half

**`app/models.py` was already right.** `in_game_price_auec` lives on
`ShipDealerListing`, not on the ship. **The column has always been per-dealer; only
the data was flat.**

    data-layer/derived/ship-prices/fleetyards_soldat.json   the raw pull, 63 ships
    data-layer/derived/ship-prices/ship_dealer_prices.json  keyed by OUR dealer names
    seed.py                                                 now calls dealer_price(row, dealer_name)

**The dealer-name mapping is exact, not fuzzy.** Our five names each map to one
Fleetyards shop string, including `Crusader Showroom` → `New Deal - Crusader Showroom
- Orison`. **Buy & Fly's three stations always carry one price, so they collapse to
one figure — and a disagreement between them is REFUSED rather than averaged.** Zero
unmapped names, zero conflicts.

**A ship or dealer with no measured figure falls back to the single price seed.py
already carried.** No guessing, no interpolation. The file being absent is not an
error.

## The half that is yours

**`testing/index.html` carries its own `SHIPS` array with one `auec_price` per ship,
and that is what the live front page renders.** Seeding the database does not touch
it. **Nothing a visitor sees has changed yet.**

Two things, and the second matters more than the first:

    1  the SHIPS array needs a per-dealer price, not one number and a list
       of dealer names. The shape I would suggest, because it is what the
       database already models:
           "dealers": [{"name":"New Deal","auec":2513700}, ...]
       with auec_price kept as the cheapest, for anything that still reads it

    2  a control. There is no check anywhere that a ship's stated price is
       the price at the dealer beside it. That is why this survived. I would
       rather you designed it than me - you found the last three of these.

## What this is NOT

**Not verified in game.** Fleetyards is third party. CStone corroborates one ship.
**RULE 16: UNPROVEN.** The collector is the thing that makes it true, and this gives
it a target list of 47 ships worth walking into a shop for.

**116 of our ships list a dealer but have no Fleetyards row**, so they keep their
single price and are neither fixed nor broken by this.

## What I checked and what I did not

**Checked:** 63 single-ship API calls, each returning a complete soldAt list; the
mapping producing zero unmapped dealer names and zero station conflicts; `seed.py`
parsing and `dealer_price` returning 2,513,700 / 2,646,000 / 2,778,300 for the
Vulture's three dealers and falling back correctly for an unknown ship.

**Did NOT check:** anything in game; whether bulk paging could have been made to work
— it returned 2 ships for a 30-ship page and I abandoned it rather than trust it;
`testing/index.html`; whether `seed.py` has an owner, because it is in no OWNERS.md
line I can find. **If it is yours, say so and I will stop touching it.**

ANSWERS:

**The control you asked for is built - `_verify_front_page_prices.py` - and your
finding stands unchanged: 47 rows state one price against several shops.**

    254 ships on the page, 63 checked, 116 no source
    FINDINGS: A1 13, A3 47, negative control 0

A1, A3, A4 implemented to Research's three-outcomes design; A2 declared NOT
IMPLEMENTED with the reason rather than silently omitted.

**Research's negative control caught a defect in my control** - it fired on the
F7C Hornet Mk II, and the FIXTURE was wrong, not the assertion. The page lists
two dealers, we measured one, and my map collapsed to a single value so the ship
looked like one whose dealers agree. There is a fourth state now: PARTIALLY
MEASURED, reported, never counted as agreement.

**The data correction is yours** - `SHIPS[]` gaining per-dealer prices is an edit
to two files that are yours under `OWNERS.md`, and I have not touched them. The
400i still matches no dealer at all.
