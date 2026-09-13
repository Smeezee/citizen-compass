# update - the front page demo is now complete against the current page, 2026-09-06

Sleven asked for the whole front page built the way we have agreed, **with the
current live page as the reference**. I read `static/preview.html` first rather
than working from memory of it, and carried every part of it across.

`data-layer/derived/main-page-concepts/the-index.html` (2.45 MB concept artefact)

## Everything the current page has, carried over

    Ship Purchase Matrix        -> the card grid, all 254 ships
    Development Progress        -> 8 ships, the CitizenCon-2026 note kept whole
    Sale Calendar               -> 5 events, windows and meaning
    Legend & Sources            -> 4 status meanings + the four sources
    the currency picker         -> USD EUR GBP CAD AUD JPY
    the patch badge bar         -> Live 4.10.0 "Siege of Orison", PTU empty
    ship data compiled          -> 2026-07-30, stated plainly
    the Idris-P price conflict  -> still shown, still unresolved, by design
    the legal footer            -> unofficial fan site + the trademark line

**Nothing was dropped.** The tables became cards because he has ruled twice that
tables are unusable on his phone; the words in them are unchanged.

## Three things added, each from studying the others today

1. **The place, not just the shop.** "at Astro Armada - Area18". Erkul prints the
   place and we were throwing ours away - `frontpage_data.json` has carried
   `place` and `body` for every dealer all along.
2. **The price gap, in the card.** "+264,600 at Teach's". Nobody else states it.
3. **Links out.** Erkul for loadouts, Fleetyards for fleet tracking, SPViewer for
   stat comparison, under a heading that says *better tools for other jobs*.
   Fleetyards links to three competitors from every ship page and it makes them
   look confident, not weak. Ours linked nowhere.

## Measured, real browser

    first paint       252 ms
    cards             254 of 254
    page height    10,992 px   (the live matrix is a 254-row table)
    console errors      0
    tabs              all four render

**Honest gap:** the currency picker needs the internet for live rates. Offline it
says so and stays on USD rather than showing a stale number - the live page keeps
its own `open.er-api.com` call.

**Not queued, not deployed, nothing committed.** This is the demo he asked to see.

C1, 2026-09-06.
