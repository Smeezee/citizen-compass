# update - second front-page concept, built after Sleven rejected the first, 2026-09-06

**He rejected the Slipway and gave the reason, which is the useful part:**

> *"The problem with what you made is that it's not simple to get the information.
> I want to still have the same information already combined on the front. That
> way you can be quick and look at it without having to go deeper. But if you
> want to go deeper, that's going to get the more robust 3D model with
> interactive hardpoints and DPS calculator and full loadout spec and more
> information."*

**The Slipway hid every fact behind clicking a hull. That is the defect.** The
spreadsheet's one real virtue was that everything was on the face of it, and the
replacement threw that away while fixing the look.

## What is built now

    data-layer/derived/main-page-concepts/the-index.html      1.08 MB

One row per ship, **every fact printed, nothing behind a hover or a click**:
name, whether it can be bought in game, role, length, crew, cargo, top speed,
the aUEC price, WHICH dealer that price is at, the spread when shops disagree,
and the pledge price. Grouped by manufacturer with a real count per maker
("Anvil Aerospace - 39 ships, 24 buyable in game"). A true-scale outline sits at
the left of every row, and a thin bar under each name shows length against the
biggest ship in the game.

Search filters as you type across ship, maker and role. Chips filter by career
and by "buyable in game". Clicking a row is the way DOWN into the 3D ship page -
depth is opt-in, exactly as he described.

## Measured in a real browser, not asserted

    first paint            112 ms
    DOM ready              180 ms
    full re-render/search   20 ms
    rows                   254 of 254   (no ship is dropped)
    console errors           0

**All 254 ships appear**, including the 53 with no outline - they render with an
empty slot rather than vanishing, which was a defect in the Slipway.

## What is still missing

1. The deep page it links to is the existing ship page; **the DPS calculator and
   full loadout spec he named are not built** and are a separate job.
2. Per-dealer prices exist for only **63 of 254 ships**. The rest show the single
   figure and the shops that carry it.
3. Manufacturer logos are not used. The Fan Kit has 57 of them and they would do
   more for the look than anything else cheap.

**Not queued, not deployed, nothing committed. A second look for him to react
to.**

C1, 2026-09-06.
