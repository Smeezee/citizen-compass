# update - the front page is now columns, on Sleven's pick, 2026-09-06

He was not opposed to the row version but said it must not be one long
continuous scroll - **"it kinda needs to be broken up... side by side rather than
going down."** Asked to choose, he picked **two or three columns**.

Same file, rebuilt: `data-layer/derived/main-page-concepts/the-index.html` (940 KB)

## What changed

Every ship is now a compact card in a **column grid that fills the screen width**
- four columns at 1440 px, five at 1920, one on a phone - still grouped by
manufacturer with the per-maker count. **Nothing was removed from the face of the
card**: name, in-game or pledge, role, length, crew, cargo, the aUEC price, which
dealer it is at, the extra cost at the dearer shop, and the pledge price.

## Measured, three widths, real browser

    first paint              80 ms   (was 112)
    DOM ready               137 ms
    page height           9,997 px   (was 22,372 - less than half)
    cards rendered      254 of 254
    columns at 1440px         4
    console errors            0

Two faults from the row version are fixed: cards no longer stretch to match the
tallest in their row, and long notes clamp to two lines instead of dominating a
card.

## Still open, unchanged from the last note

The ship images are outlines, not renders - **he has said he expects those to be
different**, and 258 own-rendered thumbnails already exist on disk unused. The
Fan Kit's 57 manufacturer logos are also unused and would carry the group headers.
Neither is done and neither should be assumed.

**Not queued, not deployed, nothing committed.**

C1, 2026-09-06.
