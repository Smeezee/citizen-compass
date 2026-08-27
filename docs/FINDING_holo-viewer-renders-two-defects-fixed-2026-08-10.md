# FINDING — the holo viewer does render a ship. Two defects were hiding it: the hull blows out to white, and every hardpoint marker is drawn fifty ship-lengths away. Both causes found, both fixes proven and measured.

    from      C3 (Cowork), 2026-08-10
    for       C1 -> Code
    answers   docs/handoff_archive/20260809_174930_update-browser-verification-...md
              ("the ship model never finishes loading", "I am not claiming the
              viewer renders a ship")
    method    the DEPLOYED testing/_deploy/holo.html, staged into a separate
              container and run in its own headless Chromium. Nothing on the
              project machine was touched. Both fixes applied at RUNTIME and
              photographed, so the recommendation is a demonstration rather than
              an opinion.

---

## 1. It renders. Code's failure was the environment, not the page.

The hull loads, the DRACO decoder resolves, and a Sabre appears. Scene survey:

    hull meshes      1   (353,731 vertices)
    marker meshes    8   (SphereGeometry — all 8 hardpoints present)
    hull size        23.38 x 4.32 x 23.88   <- real Sabre dimensions, correct scale
    three.js         r128

**Code's headless run was served over `file://`.** A worker loaded from a
`file://` page is blocked by Chromium's origin rules whatever flags are set, and
the DRACO decoder is a worker — so it hung, exactly as reported. Served over
`http://` it resolves immediately. **Code's caution was right and its diagnosis
was right; only the conclusion "unverified" can now be lifted.**

## 2. DEFECT 1 — 63.7% of the visible ship is pure white

Measured off the rendered image, not judged by eye. Nearly two-thirds of the hull
had no detail at all.

**Cause, from the page's own material:**

    transparent:true, blending:THREE.AdditiveBlending,
    depthWrite:false, side:THREE.DoubleSide

Additive blending sums every fragment along the view ray. With `DoubleSide` and
no depth pre-pass, that is the near surface **plus the far surface plus every
internal face**, on a 353,731-vertex mesh. Wherever the ship is deep, the sum
saturates and the hull goes flat white.

This is the same failure the Fan Kit prototype hit on the Constellation Aquila
and the fix is the same one.

**Fix — a depth-only pre-pass, plus FrontSide:**

    hull.material.side = THREE.FrontSide;

    var depth = new THREE.Mesh(hull.geometry, new THREE.MeshBasicMaterial({
      colorWrite:false, depthWrite:true, side:THREE.FrontSide,
      polygonOffset:true, polygonOffsetFactor:1.2, polygonOffsetUnits:1.2 }));
    depth.renderOrder = -1;  hull.renderOrder = 1;
    hull.parent.add(depth);

The pre-pass writes depth and draws nothing. The additive pass then fails the
depth test on everything behind the nearest surface, which is the whole cause.
`polygonOffset` stops the two z-fighting.

**Measured, same browser, same frozen camera:**

    pure white   BEFORE 63.7%   AFTER 0.0%
    near white   BEFORE 70.8%   AFTER 0.0%
    lit pixels   BEFORE 48,581  AFTER 49,544

The lit-pixel count barely moves, which is the check that matters: **the fix
removed saturation, not the ship.** A "fix" that made the hull dimmer overall
would show up as a large drop there.

## 3. DEFECT 2 — the markers are in centimetres, the hull is in metres

All 8 markers exist, are `visible:true`, and are drawn at coordinates like:

    [-176.1, -43.9, -1179.9]

against a hull that measures **23.38 x 4.32 x 23.88**. So a marker for a 24-metre
ship is being placed 1,180 units out — **roughly fifty ship-lengths away.** Zero
of the eight were inside the hull's bounding box. That is why nobody has ever
seen one, in any browser.

**This is my fault, not Code's.** `hardpoints.json` carries two position fields
and I documented neither prominently enough:

    "pos"  : centimetres from hull centre     <- what the page used
    "unit" : normalised, longest axis -1..1

The finding that shipped with it said "centimetres" in the schema line and the
work order did not repeat it. Given the site's `.glb` models are in metres, the
page needed `pos / 100`.

**Fix:**

    marker.position.multiplyScalar(0.01);          // cm -> m

Verified against the data rather than by eye: `Weapon left nose` becomes
`z = -11.80` against a hull half-length of `11.94` — **on the nose**, which is
where a mount called "weapon left nose" belongs.

**Result: 8 of 8 markers on screen**, on the hull, at the nose, wings, mid-body
and belly.

**Two smaller things fixed alongside, both worth keeping:**

*The marker was a fixed 0.43 units across regardless of hull size.* On a 24 m
fighter that is reasonable; on a 61 m Constellation it would be a speck. Scaled
to the hull instead — `span * 0.018` — so a marker reads the same on any ship.

*Markers need `depthTest:false` once the depth pre-pass exists*, or the new depth
buffer hides any marker sitting on or just inside the skin. **That is a decision,
not just a fix:** `depthTest:false` means far-side markers show through the hull.
The prototype instead faded far-side markers to 30% so the ship still shows what
it carries without pretending the back is the front. Either is defensible;
picking one silently is not.

## 4. What this does to the viewer's status

    renders a ship               was "NOT VERIFIED"   -> PROVEN, photographed
    holo shading readable        was unknown          -> was broken, fixed, measured
    markers visible on the hull  was unknown          -> was broken, fixed, 8 of 8
    Mirror L/R                   still not observed
    two ships have no model      unchanged — library gap, see the duplicates finding

## 5. The bigger prize, now that the mechanism is proven

The viewer currently offers 2 ships because hardpoints exist for 4. That is not a
limit of the approach — it is how many I ran the derivation against.

**Checked on the project machine:** `data-layerrawhardpoints/ship_specs.json`
holds **295 ships and every one of them has named ports** — the same
`name` / `position: null` shape the whole derivation is built on. Cross-matching
those names against the 235 `.glb` in `_deploy/models/` on an exact match:

    295  ships with port data
    173  of them also have a model
    122  no model under that name

**So the ceiling is around 173 ships, not 2**, and looser name matching would
raise it further. What stands between here and there is hull geometry: the
derivation needs vertices, and the `.glb` are DRACO-compressed, so they have to
be decoded before they can be measured. That is now known to work — this
container decoded one in a browser tonight.

That is a scoped job, not a research question. I have not started it.

## 6. What I did NOT do

- **I did not touch anything on the project machine.** Both fixes were applied at
  runtime in a staged copy so they could be measured. `holo.src.html` is Code's
  file and is unchanged.
- **I did not verify Mirror L/R**, or clicking a marker, or the Cyclone. One ship,
  one camera angle, one browser.
- **I did not run the derivation against the other 169 ships.** §5 is a measured
  opportunity, not work delivered.
- The `depthTest` question in §3 is left open deliberately — it changes what the
  viewer claims about the far side of a ship, and that is a call to make on
  purpose.
