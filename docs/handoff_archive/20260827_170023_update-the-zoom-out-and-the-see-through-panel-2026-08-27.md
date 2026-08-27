# Update — Sleven found two on the deployed page. Both fixed in my files.

**C1, 2026-08-27 17:18 local.** `cc_viewer.js` and `loadout.src.html`. Both
`node --check` clean. Not built — yours.

> *"why does the ship zoom out when I click the hardpoints?? and is there a way
> to make them see through a little"*

## 1. THE ZOOM-OUT — and the second defect hiding behind it

`Viewer.prototype.reframe()` recomputed the camera distance from the hull's
bounding box every time a panel opened:

    dist = (fit / 2) / tan(fov / 2) * (1 + f * 0.9) * 1.35

**Two things fell out of that and only one of them was reported.**

**The reported one:** `(1 + f * 0.9)` pulls the camera back so the hull fits the
narrower viewport. E4 added it to stop the hull becoming a sliver at the far
edge — and paid for that by **making the ship smaller every time somebody asked
a question about it.**

**The one nobody reported, and it is worse:** the distance was recomputed FROM
SCRATCH, so **any zoom the visitor had set was discarded.** Scroll in to look at
a wing, click the dot on that wing, and the page throws your view away. That
reads as the page being twitchy rather than as a feature undoing your work,
which is exactly why it went unreported while the shrink got noticed.

**Fixed: the distance is now PRESERVED and only the look-at point moves.** A pan,
not a zoom. The ship stays the size the person put it at and slides so the panel
is not sitting on top of it. A distance is computed only on the very first
frame, before there is a viewpoint of theirs to protect.

**If the hull overflows the narrower space, that is now the accepted failure.**
Better than resizing the thing they are trying to look at — the brief is
explicit that you can see the ship while you change it.

## 2. THE SEE-THROUGH PANEL

`#cc-panel` sat on solid `--panel` and hid the part of the hull it was
describing.

**Not a straight `opacity` on the element** — that fades the TEXT with it, and a
half-legible stat is worse than a covered wing. A translucent GROUND plus a
`backdrop-filter` blur: the hull reads through it, the words stay full strength.

    --panelglass: rgba(14,27,46,0.80)   +   blur(9px)

**The `@supports` fallback is the OLD OPAQUE PANEL, not a transparent one.** A
browser without `backdrop-filter` would otherwise put text straight over a
moving 3D hull with nothing between them — unreadable rather than merely plain.

## What I want checked

**The zoom fix needs a real browser and a control that can fail:**

    read camera.position.distanceTo(controls.target)
    click a marker that opens the docked panel
    assert the distance is UNCHANGED to within a pixel of float noise
    assert controls.target DID move (or the panel is not being avoided at all)

**The control: restore the `(1 + f * 0.9)` term in the served bytes** — the
distance assertion must go red. Both assertions matter; without the second, a
`reframe()` that did nothing at all would pass.

`_verify_camera_framing.mjs` already has the harness and the band. This is a
different question — it asks whether the framing SURVIVES an interaction — so it
wants its own file rather than a fifth assertion bolted onto that one.

*C1*
