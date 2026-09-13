# update - a first front-page concept exists and it is called the Slipway, 2026-09-06

**Built against the brief filed earlier today, not against the wall or the
drydock.** One file, offline, no build step:

    data-layer/derived/main-page-concepts/the-slipway.html      1.24 MB

## What it is

Every ship drawn as its own top-down outline **at true size against every other
ship**, on one horizontal rail, biggest first. Type to jump. Click a hull for the
card. Drag to pan, ctrl+scroll to zoom, FIT ALL to see the whole fleet at once.

**Why this shape:** measured, not asserted - no other Star Citizen tool renders
ships at true relative scale, and none of the four surveyed has a single canvas
or 3D element on its front page. Erkul, Fleetyards, spviewer and CStone are all
tables or card walls. **And it costs nothing to draw** - flat SVG paths, no
images, no 3D, which is what keeps it fast enough for a player alt-tabbed out of
the game.

**It does not duplicate the 3D viewer**, per Sleven's instruction. There is one
3D area and it stays on the ship page; the card's only action is to open it.

## Measured in a real browser, headless Chromium 1440x900

    load                1.3 s from a cold file:// open
    hulls drawn         201 of 254 (the rest have no outline yet)
    console errors      0
    rail width          14,840 px at the default 1.6 px/m

## What it fixes on the way past

The card shows **per-dealer prices**, so the Vulture reads New Deal 2,513,700 /
Buy & Fly 2,646,000 / Teach's 2,778,300 with the cheapest marked, against a live
front page that prints one figure beside several shops and calls it verified.

## What is WRONG with it, stated before he finds it

1. **The Idris-M and Idris-P outlines are broken in the source data.** At any
   size above a thumbnail they read as scattered blobs, not a ship. The traces
   in `ship-silhouettes/silhouettes_side.json` are fine small and fall apart
   large. **This is a data defect, not a rendering one, and it is not fixed.**
2. **53 ships have no outline at all** and are simply absent from the rail. A
   front page cannot silently drop 53 ships. Unsolved.
3. **FIT ALL is a novelty.** 201 ships at true scale across one viewport makes
   every one of them microscopic. It photographs well and answers nothing.
4. **Not proven to beat a plain search box** for the alt-tab case, which is the
   brief's own measuring stick. Nobody has tested that and I am not claiming it.

## Status

**A first look, for Sleven to react to. Not queued, not built into the site, not
deployed, nothing committed.** The last five concepts were rejected; this one
exists to be argued with, and the arguing is the point.

C1, 2026-09-06.
