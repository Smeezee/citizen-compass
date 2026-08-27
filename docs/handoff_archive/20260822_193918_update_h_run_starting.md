# Update - corrections committed c0e93b0; H run starting with the real prototype source

Ledger `a2fe370`. Sweep 54 ok, 0 failed, 3 skipped, 0 NOT RUN.

Shipped: B5's inheritance **built and disabled**, B6, the rebuilt gate (169
placed, 6 refused by name), markers 1,210 on 159 hulls.

The control asserting **0 inherited and 0 child points** in the shipped dataset
stays load-bearing - it fails if anyone turns `--with-children` on before the
scatter is fixed.

**Deferred, not dropped, scheduled after the hologram work:** spread an inherited
sibling around ITS turret rather than across the hull, and stop the collision
pass walking it arbitrarily far from the turret it belongs to. 12 of 24 guns
landing nearer a different turret is a confident wrong position and +160 markers
does not buy it.

## What changed about H1 before I start it

`docs/holo-viewer-prototype-src/` exists now - 66 KB of real source with every
ordered item mapped to its function. **I had already written H1 from the living
document's prose, which is exactly the "reimplement from screenshots" the README
says is no longer necessary.** So my first job on H1 is to check what I wrote
against `buildGeometry` / `edgesFor` / `edgeOpacity` and port rather than
approximate. Anything of mine that disagrees with the prototype loses.

## The errata, folded in

- **E3** is the promotion, done. Its two acceptance ports - Gladius Valiant
  "Gun nose" and Origin 125a "missilebay front" - get re-checked from the served
  bytes at H9.
- **E2** 513 of 3,283 parts have no headline stat and render as a name and two
  zeros. `IR 0 EM 0` is true and useless; a zero is a claim and an absence is
  not.
- **E1** 44 hulls draw a model and carry no markers, and the page says nothing.
  **Two cases needing different sentences** - the Cyclone genuinely has no
  weapon mounts; the Cutlass Black has 42 changeable ports and no positions.
  Distinguished from the data, never from a list of ship names.
- **E4** the stage does not reframe when a panel opens, so the hull becomes a
  sliver at the edge while the panel takes the stage.

Working order: H1 (with E4, since both are the viewer's framing), then E2 and
E1, then H2-H5 - the matching work, where NO FUZZY MATCHING is the rule that
matters - then H6-H8, then H9.
