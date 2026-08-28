# ORDER — build and deploy. Sleven watched the page and gave three instructions; all three are done, and one of them needs a browser check from you that I cannot run.

**2026-08-27 22:20 local · C1** — read from `date`.

## What he said, on the deployed page

> *"When you click a hard point, the whole ship shifts... I really want the ship
> to stop shifting when we open a thing. If I'm looking straight at the ship and
> it would be the ship's right wing but it'd be on my left, it should open the
> menu on the left side of the screen. If I'm looking at the front of it and I
> click on the ship's left wing, it should open it on the right. Not shift the
> whole thing... Is there any way we can make it a little bit more see through?
> It needs to get fleshed out and smoothed out."*

## 1. The ship no longer moves

`setObstruction` still records how much of the stage the panel covers - callers
pass it and a check reads it - but **it no longer touches the camera**, and
`reframe()` no longer applies the sideways shift. The hull stays exactly where
the person put it.

**I did not delete the setter.** Accepting a number and pretending to act on it
is worse than either deleting it or keeping it honest; it stores, and the
comment says so.

## 2. The panel opens on the marker's own side of the screen

`panelPlacement` decided **"right, unless there is no room"** - which is why
almost every panel opened right, and why the ship was being panned left to make
space. That pan was the whole defect.

Now: dot in the left half of the stage → panel on the left rail. Dot in the
right half → right rail. **Two stable positions, pinned to the edge**, not a
panel that lands somewhere new for every marker. Vertically it still centres on
the dot.

**The old "a panel must never cover its own marker" rule is retired
deliberately** - it is the reason the panel always went to the far side, which
is the reason the ship had to move. The panel is glass and the hull is now
see-through, so a dot behind it is dimmed rather than lost, and the leader line
still runs to it.

## 3. The hull is see-through, and it is a control rather than my taste

`solid` was `transparent: false` - completely opaque - and the only way to see
into a ship was `xray`, a different look entirely. There was no "a little bit".

New `CC_HOLO.hullAlpha`, default **0.86**, with a fourth slider in the look
panel labelled **See-through**. At 1.0 the material goes back to genuinely
opaque rather than sitting transparent at full alpha. It saves with the other
appearance settings, and an older save without the key simply gets the new
default - no revision bump, nobody's settings are discarded.

Front faces only, depth still written, so it reads as glass rather than the
additive soup `xray` exists to replace.

## 4. And one thing on the page was lying

The provenance note under the model still said the dots are worked out from each
mount's **name** and **"are not measured from the model."**

**That was true when it was written and it is false now.** 1,693 mounts across
166 hulls carry the positions CIG published. The page was telling readers its
best feature was a guess.

Rewritten to say the measured part is measured, the fallback is still an
estimate, and - because the marker file carries no provenance - **that it cannot
tell you which of the two this particular ship's dots are.**

### THE ONE THING I NEED FROM YOU

`loadout_marker.gen.js` is `[PortId, x, y, z]`. **If it carried a fourth
element - the `placed_from` your merge already sets to `'client'` - the page
could say per ship, per dot, which are CIG's and which are estimates**, and that
hedge comes out. It is your emitter and your call; I have not touched it.

## Checks I re-baselined, all mine, all still able to fail

    _verify_stage_panel.mjs    the panel-side rule, and a NEW assertion that
                               the camera's target is UNCHANGED after a click
    _verify_ship_page.mjs      N9's wording - it asserted the old apology
    _verify_marker_coverage    matched on the sentence rather than the note
    _verify_marker_absence     same
    _verify_look_panel.mjs     four sliders now, asserted BY NAME as well as
                               by count, so one vanishing still fails

**A RULE 12 GAP I AM NOT GOING TO PAPER OVER.** The new "the ship did not move"
assertion reports **NOT PERFORMED** in the script harness - that viewer stub
exposes no camera controls. **The single most important thing Sleven asked for
has no check that actually fires.** It needs a browser check, and browser checks
are yours. Until one exists, "the ship does not move" is verified by looking at
it, not by the suite.

## Everything else

Every page check green. The two reds here are `_verify_deployed_links` and
`_verify_find_deployed`, both of which need the live site this VM cannot reach.

Testing only. Nothing to the live site without Sleven's go-ahead.

— C1
