# Update — order received: the camera never looked at the ship

**2026-08-26 · Code**

Received `docs/ORDER_the-camera-never-looked-at-the-ship-2026-08-26.md` from C1.

**What it says:** every ship page has rendered black since 66a0e40 (G2,
2026-08-23). The model loads fine; `_fitProjected` in `testing/_src/cc_viewer.js`
never aims the camera before measuring the projection, so the fit loop reads a
permanent overshoot and pushes the camera outward six times, compounding to
~850x the hull's bounding radius. Measured on ten hulls, ratio 826x-897x. The
"34 hardpoints, 34 have no room" status line is correct - at 25 km every marker
lands in the same pixel.

**What I am about to do, in the order the ORDER gives:**

1. F1 - `this.camera.lookAt(target)` as the first line inside the fit loop.
2. F2 - recompute the box after the hull is translated onto the disc, and hand
   that box to `_fitProjected` / `_setClip`.
3. Rebuild and deploy to **testing only**. The ORDER says explicitly: do not
   deploy the live site.
4. Re-run the existing check sweep; all of it should stay green.

**Not starting yet:** F3, the real-browser control. It asks for Playwright and a
headless Chromium on the build machine - a new dependency outside the repo, so
it needs Sleven's go-ahead (rule 6). Question goes to him with the F1/F2 result.

**Noted for the record:** the ORDER identifies a Rule 12 hole. Every viewer
control loads `cc_viewer.js` into a Node `vm` against a stub THREE whose camera
always looks at its target - so the controls model the exact behaviour the page
is missing, and 23 assertions across 239 hulls stayed green while the whole
fleet was dark. No control renders the real page in a real browser.
