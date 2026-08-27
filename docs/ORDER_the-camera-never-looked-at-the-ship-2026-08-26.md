# ORDER — the camera never looked at the ship

**2026-08-26 · C1 · for Code**
**Priority: this is the whole fleet. Every ship page has been dark since 66a0e40 deployed.**

---

## What Sleven reported

Ten or more ships at random, all identical: black viewer panel with a small
ring in the middle, no hull, and the status bar reading
`34 hardpoints · 34 have no room`. Page chrome, loadout list, stats rail and
provenance all correct. Only the model is absent.

## What is actually happening

**The model loads fine. The camera is 25 kilometres away from it.**

On the Aegis Vanguard Harbinger — a hull 38.0 × 8.1 × 40.7 metres, bounding
radius 28.1 m — the page finishes loading the GLB in 2.3 s, decodes it through
DRACO, adds it to the scene, and then parks the camera at **25,022.7 metres**
from the target. Near plane 24,972, far plane 25,107. The ship is a sub-pixel
speck. Every hardpoint projects into the same handful of pixels, so the label
solver is right to refuse all of them: there genuinely is no room.

The ring Sleven sees in the middle is the stage disc, seen from 25 km.

This is not thin data, not a missing model, not a broken worker, not DRACO.
`_view.current` is populated, `CCViewer.hasDraco()` is true, the status line
computed `2.3s · 38.0 × 8.1 × 40.7`, the scene holds 7 children. Everything
worked except where the camera ended up.

## The cause, exactly

`Viewer.prototype._fitProjected()` (cc_viewer.js, introduced in **66a0e40**,
2026-08-23, G2) iterates the projected bounding box to fit the hull:

- it moves `camera.position` outward along the target-to-camera direction
- it calls `camera.updateMatrixWorld()` and `camera.updateProjectionMatrix()`
- it projects the eight box corners and scales the distance by the worst
  overshoot

**It never aims the camera.** `lookAt` does not appear anywhere in
cc_viewer.js. `controls.update()` — the thing that actually turns the camera
toward `controls.target` — runs in `frame()` *after* the fit loop has already
finished. So every pass measures a projection taken from a camera pointing
wherever it happened to be pointing, which on first load is `boot()`'s default
orientation, not at the ship.

Because the camera is not aimed at the ship, sliding it further away does not
shrink the ship in frame — the ship just drifts further off-axis. The loop
reads that as "still overshooting" and pushes again. Six passes, compounding:

| pass | worst overshoot | camera distance |
|---|---|---|
| enter | — | 99.3 m |
| 0 | 3.923 | 99.3 to 423.3 |
| 1 | 2.302 | 423.3 to 1,059.5 |
| 2 | 2.100 | 1,059.5 to 2,417.9 |
| 3 | 2.029 | 2,417.9 to 5,332.2 |
| 4 | 1.999 | 5,332.2 to 11,588.8 |
| 5 | 1.986 | 11,588.8 to **25,022.7** |

The overshoot converging on ~2.0 instead of falling toward 0.92 is the
signature: distance is not buying frame coverage, because the ship is not in
the middle of the frame.

## Fleet-wide, measured

The deployed build, driven in a real headless Chromium against the real
`testing/_deploy` bytes. `ratio` is camera distance over hull bounding radius;
a sane value is around 2.5-3.

| ship | distance | hull radius | ratio | status bar |
|---|---|---|---|---|
| Aegis Vanguard Harbinger | 25,022.7 | 28.1 | 890x | 34 hardpoints · 34 no room |
| Aegis Avenger Stalker | 1,018.2 | 1.2 | 843x | 14 · 14 no room |
| Drake Cutlass Black | 19,072.0 | 22.7 | 840x | 38 · 38 no room |
| Drake Vulture | 6,541.7 | 7.3 | 892x | 6 · 6 no room |
| RSI Polaris | 31,273.4 | 36.1 | 865x | 133 · 133 no room |
| Anvil Carrack | 67,861.0 | 75.7 | 897x | 19 · 19 no room |
| MISC Freelancer | 17,420.2 | 20.7 | 840x | 24 · 24 no room |
| Origin 300i | 12,925.2 | 15.1 | 855x | 12 · 12 no room |
| Aegis Retaliator | 35,923.4 | 41.3 | 871x | 24 · 24 no room |
| Aegis Gladius | 10,997.7 | 13.3 | 826x | 18 · 18 no room |

Ten of ten. The ratio is between 826 and 897 on every hull, which is what a
compounding loop with a fixed pass count does: it is the same multiplication
every time, so the failure is uniform. **This is not a per-ship data problem.
It is one line, on all 239 hulls.**

## Why every control is green

`_verify_holo_render.mjs`, `_verify_hull_solid.mjs`, `_verify_stage_floor.mjs`
and the rest load `cc_viewer.js` into a Node `vm` sandbox against a **stub
THREE**. There is no real `PerspectiveCamera`, no `matrixWorldInverse`, no
`OrbitControls`.

E5 (`e8f1dd8`, yesterday) rebuilt the stage-floor control's stub `project()`
and its own commit message describes it as *"a look-at view basis built from
the camera's position and the target it is aimed at"*. That is the defect,
inverted: **the stub camera always looks at the target, and the real camera
never does.** The control models the behaviour the page is missing, so it
cannot see that the page is missing it. Twenty-three assertions, 239 hulls,
fully green, while every ship page on the site was blank.

That is a Rule 12 hole with a name now: *no control renders the actual page in
a real browser.* Every claim about the viewer's framing since 66a0e40 has been
a claim about a stub.

## The fix — two lines, both proven

**F1 — aim the camera before measuring it.** One line inside the fit loop in
`_fitProjected`, before `updateMatrixWorld()`. With it, the Harbinger converges
on 81.8 m instead of 25,022.7 m, and the hull renders.

**F2 — fit the box the hull is actually in.** `frame()` measures `box` from the
object, then translates the object to stand it on the disc, then hands
`_fitProjected` the **pre-translation** box. The corners it fits are where the
hull used to be. This is a second, smaller defect that F1 alone does not
remove: with F1 the loop oscillates (0.707, 1.024, 0.877, 0.939, 0.912, 0.924)
and lands on whatever pass 5 happened to be. Recomputing the box after the
translation converges in **three** passes and exits on the convergence test
instead of running out of passes.

`_hullOrigin`, `_hullSize` and `_fitTable(sz)` all read `sz`, which is
translation-invariant, so **F2 moves no marker relative to the hull.** Only the
corners handed to `_fitProjected` and `_setClip` change.

Result after both, same hulls:

| ship | distance | ratio | status bar |
|---|---|---|---|
| Aegis Vanguard Harbinger | 81.8 | 2.9 | 34 hardpoints · **8** no room |
| Aegis Avenger Stalker | 3.4 | 2.8 | all placed |
| Drake Cutlass Black | 66.2 | 2.9 | 38 · **11** no room |
| Drake Vulture | 21.8 | 3.0 | all placed |
| RSI Polaris | 99.6 | 2.8 | 133 · **95** no room |
| Anvil Carrack | 218.5 | 2.9 | 19 · **3** no room |
| MISC Freelancer | 57.6 | 2.8 | 24 · **1** no room |
| Origin 300i | 40.9 | 2.7 | all placed |
| Aegis Retaliator | 106.0 | 2.6 | 24 · **2** no room |
| Aegis Gladius | 37.9 | 2.8 | all placed |

The Polaris still shows 95 of 133 with no room. **That is the label-crowding
cost C1/C2 already flagged and it is a separate decision, not part of this
fix.** It is now visible because the hull is visible.

## F3 — the control this needs, and the choice behind it

Nothing in `checks/` can catch this class of defect, because nothing renders.
Three options, and they are not equal:

1. **Install Playwright + headless Chromium on the build machine and add one
   real-browser control** that loads the built `testing/_deploy/loadout.html`
   over a local static server for a sample of hulls, reads
   `camera.position.distanceTo(controls.target)` and the hull's bounding
   radius, and asserts the ratio lands in a band (say 1.8-6.0). Mutation:
   remove the `lookAt` line, and the control must go red on every sampled hull.
   *Cost: a browser download on the build machine and a slower control (~9 s
   per hull, so sample 8-12, not 239).* **This is the recommendation.** It is
   the only option that measures the thing the visitor sees, and it retires an
   entire category of "green stub, black page".

2. **Make the stub camera unfaithful on purpose** — give it a `quaternion` and
   a `project()` that uses it, so a camera that was never aimed projects like
   one. *Cost: no new dependency, but it is re-implementing three.js in the
   test harness, which is exactly the road that produced this bug. Every future
   three.js behaviour has to be hand-modelled correctly before a control can
   test against it.* Cheaper today, worse in a year.

3. **Do nothing and rely on the walkthrough.** Sleven found this one. He should
   not be the render regression test.

I recommend (1), and (2) only if a browser on the build machine is genuinely
unacceptable — in which case (2) should be scoped to *this* stub, with the
mutation proving it fires.

## Order of work

1. **F1**, deploy, and check the Harbinger by eye. The site is dark right now;
   this is the line that turns it back on.
2. **F2** in the same pass.
3. Re-run the existing sweep. All of it should stay green — F1 and F2 change
   only camera placement, and every stub-based assertion about materials,
   clip-plane ratios, markers and the floor is untouched.
4. **F3**, as a separate commit, with the mutation.

Do not deploy the live site. Testing only.

---

## The changes

`testing/_src/cc_viewer.js`, in `Viewer.prototype._fitProjected`, inside the
`for (k = ...)` loop — add the first line:

```js
      this.camera.lookAt(target);
      this.camera.updateMatrixWorld();
      this.camera.updateProjectionMatrix();
```

`testing/_src/cc_viewer.js`, in `Viewer.prototype.frame` — replace:

```js
    this._fitProjected(box, ty, 6);
    this._setClip(box, ty);
```

with:

```js
    /* THE BOX ABOVE IS WHERE THE HULL WAS, NOT WHERE IT IS. It was measured
       before the three lines that stand the hull on the disc, so its corners
       are the pre-translation ones. _setClip only reads the size, which is
       translation-invariant, but _fitProjected fits the CORNERS - and fitting
       corners the hull has moved away from is why the loop never converged. */
    var fitBox = new THREE.Box3().setFromObject(o);
    this._fitProjected(fitBox, ty, 6);
    this._setClip(fitBox, ty);
```

---

## Questions

1. F3 option (1) — Playwright and a headless Chromium on the build machine —
   approved? It is a new dependency on the machine that builds the site, and it
   is the only way a control can see what a visitor sees.
2. If not, is option (2) acceptable as the fallback, scoped to the stub camera
   only?
