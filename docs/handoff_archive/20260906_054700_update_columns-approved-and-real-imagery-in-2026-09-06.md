# update - Sleven approved the column shape, and the real ship imagery is in, 2026-09-06

## THE FIRST APPROVAL IN THIS WHOLE LINE OF WORK

Five concepts from the previous C1 were rejected, and two of mine. On the column
version he said **"ok i like that."** That is the first yes anybody has recorded
on a front-page design. **The shape is settled: cards in side-by-side columns,
grouped by manufacturer, every fact on the face of the card, click for depth.**
Do not redesign it. Improve inside it.

## What changed since that yes

`data-layer/derived/main-page-concepts/the-index.html` now carries the **real
ship imagery** instead of traced outlines.

I compared the two sets side by side before choosing, rather than picking on
description:

    data-layer/derived/ship-renders/by_ship_name.json    217 ships
      our own renders of untextured geometry - clean, grey, plainly a schematic
    main-page-concepts/ship_thumbs.json                  245 ships
      CIG's own ship imagery - full colour, real paint, in scene

**The thumbs win and it is not close.** The page went from reading like a
blueprint to reading like a Star Citizen site, with no change to the layout or
to a single fact on the card.

Order of preference in the build: CIG imagery, then our render, then a plain
"no image" box. **Nine ships have neither and say so** rather than showing an
empty frame. Ships that got an image no longer carry an outline - the page never
ships both.

Credit line added to the footer: *ship imagery (c) Cloud Imperium Games -
unofficial fan site*. The register, the source notice and the takedown contact
already exist and are the mechanism; this concept is not deployed and nothing in
it changes them.

## Measured at three widths, real browser

    first paint          180 ms   (was 80 with outlines)
    DOM ready            490 ms
    page height       11,016 px
    cards                254 of 254
    columns at 1440px      4       (5 at 1920, 1 on a phone)
    console errors         0
    file                 2.43 MB

**The 2.43 MB is embedded data URIs and is a CONCEPT ARTEFACT, not a shipping
decision.** The real page serves image files; CIC already flagged a 4.3 MB
data-URI page as unacceptable on the wall. Do not carry this number forward as
though it were the production weight.

**Not queued, not deployed, nothing committed.**

C1, 2026-09-06.
