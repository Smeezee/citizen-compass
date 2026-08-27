# Update - H1 rebuilt and H1f shipped. Version 4f397e10.

Commit `22d5d9c`. Sweep **59 ok, 0 failed, 3 skipped, 0 NOT RUN**. Upload diff:
`/cc_viewer.js` and `/loadout.html`, 498 unchanged.

On the site now: **Solid + lines in amber**, grid on, scanlines off, with a
**Look** control top-left of the stage opening the panel - six styles, five
colour swatches, three sliders, spin/grid/scanlines. Closed by default, Escape
or an outside click closes it, floats so the page is still 1080 of 1080 and 768
of 768.

## Two of my constraints were overturned and the reasoning is kept

I shipped three styles and hard-coded the sliders, arguing a visitor should
enjoy the page rather than tune it. Sleven's point: **on this page the tuning IS
the enjoyment.** A developer's tuning panel and a visitor's controls look
identical in a screenshot; the difference is whether anybody wants to touch
them, and he does.

## The white had a real cause, and my own control was hiding it

`edgeOpacity` clamps into [0.12, 0.55], tuned against four ~200-350k-vertex Fan
Kit models. On the Liberator - 1,102,122 vertices - **the formula asks for 0.063
and the floor doubles it.** The floor never protects anything: on a sparse hull
the formula already returns a high number the *ceiling* catches, so it only ever
bites the dense hulls, which are exactly the ones that saturate. Replaced with
one density factor across edges, wireframe and points.

**And my control reported 0.00% white while Sleven was looking at white
line-work**, because it modelled one fragment per pixel for every pass. The
depth pre-pass deduplicates SURFACES. It does not deduplicate LINES - coincident
edges at the same depth all draw and all add.

At the shipped defaults, densest hull in the fleet:

    panel 4.85%   solidlines 3.76%   solid 0.00%
    hull  0.00%   wire       0.09%   points 4.18%

Panel is close to the 5% line and that is worth knowing rather than rounding
away. Worst a user can reach (lineInt 2.0, detail 80) is 30.90% - reported, not
asserted: a bright setting somebody chose is not a bright default.

## That control was also leaking its own state

Section 3 drove each slider to its extremes and never restored them, so section
5 measured `lineInt=1.8, detail=70` and reported it as the default - 30.9% for a
configuration nobody ships. **Found by dumping the passes, not by the numbers
looking wrong**; a saturating hull was exactly what I expected to see, which is
what makes that kind of leak dangerous. CC_HOLO is snapshotted and restored now.

## The load-bearing negative

`--mutate-noop` makes `setStyle` record the name while `_applyHolo` ignores it,
and **all 15 style pairs collapse to one signature.** That is the "every button
sets a class and nothing redraws" build, caught.

## Also

I deployed ahead of the sweep on Sleven's word, having run all twelve page
controls individually first. The sweep then came back clean, so it cost nothing
- but the order of those two is worth noting.

Next: H1b, the leader-line labels, including the deconfliction the prototype has
NOT solved - the Sabre collides at 8 hardpoints and the Perseus has 35.
