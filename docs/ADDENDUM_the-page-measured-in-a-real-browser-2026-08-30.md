# ADDENDUM — the proposal's numbers were derived from CSS. I have now measured them in a live browser at Sleven's own window size. Two confirm exactly, one was wrong, and Erkul turns out to prove the argument rather than contradict it.

    from      C3 (Cowork), 2026-08-30
    extends   PROPOSAL_make-the-ship-the-page-2026-08-30.md
    method    live DOM geometry via the browser bridge, viewport forced to
              1904x890 to match Sleven's screenshot. Not estimated.

---

## 1. MEASURED, at 1904 x 890

    left rail        419 px
    right rail       381 px
    ─────────────────────────
    RAILS            800 px   =  42.0% of the width   <- CONFIRMED exactly
    stage           1045 x 566
    SHIP AREA                 =  34.9% of the viewport

**The proposal predicted 42vw and ~36%. Both hold.** The ship is closer to a third
than to a half.

## 2. THE THREE SCROLLERS, with their real overflow

    .col.left     650 px visible   1,448 px of content   2.2x
    .col.right    650 px visible   1,309 px of content   2.0x
    .markernote    76 px visible     121 px of content   1.6x

**Every one of them is a wheel trap.** The amber note is the worst of the three in
kind rather than in size: **76 pixels of window over 121 pixels of prose**, sitting
directly under the model where the pointer naturally rests. It will eat scroll
gestures aimed at the page.

## 3. CORRECTED — `--chrome: 238px` is not all above the grid

The proposal implied 238px above the stage. **Measured, only 106px is above it.**
The rest is below: a 36px tab strip at y=766, and **88px between the tab strip and
the bottom of the window for a one-line trademark footer.**

**That 88px is the cheapest height on the page** and no part of the proposal
mentioned it, because CSS alone does not show it. **One line of legal text is
costing more vertical space than the tab strip.**

## 4. ERKUL, MEASURED — and it is the argument, not the counter-argument

`erkul.games`, same forced viewport, read from the live DOM:

    hasCanvas          FALSE          65 SVGs, 1 image. There is no 3D.
    document height    890 px         pagesTall 1.00 - it does NOT scroll
    left nav rail      236 px
    second rail       ~192 px
    core grid         1272 px         grid-cols-3: 843 + 413
    inner split        843 px         grid-cols-2: 413 + 413

**Erkul is a dashboard, and at this window size it fits in one screen without
scrolling at all.** Four panel columns, no hero object.

**That is exactly why its density is the wrong lesson for us.** Erkul can afford
wall-to-wall panels because nothing on its page loses by being crowded — its subject
IS the numbers. **The moment a 3D hull is on the page, panels stop being neutral:
they are taking room from the one element that gets worse when you shrink it.**

**Sleven's instinct is right and Erkul supports it.** Copying Erkul's arrangement
onto a page with a model would produce a worse Erkul with a small picture on it.

## 5. What I checked and what I did not

**Checked, live, in a real browser:** the rail widths, stage box, viewport, all three
scroll regions with their content heights, the position of the tab strip and the gap
below it, and Erkul's full block geometry at the same viewport.

**Did NOT check:**
- **How any of it LOOKS.** Screenshots are failing through the bridge
  (`UnknownVizError`). **Every number here is geometry; none of it is a judgement
  about appearance**, and the overlay question in the proposal still needs eyes.
- **Erkul at a smaller window.** It fits at 1904x890. Sleven says it scrolls, and at
  a narrower window it certainly will. **I measured one size.**
- **Whether the 88px footer gap is deliberate.** It may be holding something I did
  not trigger.
- **I changed nothing.** Viewport emulation was reset after measuring.
