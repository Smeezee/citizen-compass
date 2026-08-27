# PROMPT FOR CODE — fix the two defects hiding the holo viewer, then swap in hardpoints for 167 ships instead of 4

    from    C1, 2026-08-10
    for     Code
    basis   docs/FINDING_holo-viewer-renders-two-defects-fixed-2026-08-10.md (C3)
            docs/FINDING_fleet-hardpoints-167-ships-2026-08-10.md (C3)
    urgent  the currently DEPLOYED /holo page has both defects live right now.
              Sleven was told minutes ago it's ready to test — it renders, but
              the hull blows out white and every marker sits ~50 ship-lengths
              off the hull, invisible. That's on me, not a new regression: the
              cm-vs-metres unit mismatch was in the original hardpoints data
              and nobody caught it before deploy. Fix and reverify before he
              opens it, if the timing works out.
    scope   testing/_src/holo.src.html, build_holo_data.py. Build only — do not
              deploy. A separate go-ahead covers pushing this live, same as
              every other order.

Both fixes below are proven and measured in C3's finding, not theoretical —
demonstrated at runtime against the actual deployed page, photographed,
before/after numbers included. This should be mechanical, not exploratory.

---

## 1. Fix the white-hull blowout

**Cause:** the hologram material is `transparent + AdditiveBlending +
DoubleSide + depthWrite:false`. On a 353,731-vertex hull that sums near face +
far face + every internal face along the view ray — wherever the ship is deep,
the sum saturates and the hull goes flat white. Measured: 63.7% of the visible
Sabre was pure white before the fix, 0.0% after.

**Fix — a depth-only pre-pass, plus FrontSide on the hull:**

```js
hull.material.side = THREE.FrontSide;

var depth = new THREE.Mesh(hull.geometry, new THREE.MeshBasicMaterial({
  colorWrite: false, depthWrite: true, side: THREE.FrontSide,
  polygonOffset: true, polygonOffsetFactor: 1.2, polygonOffsetUnits: 1.2
}));
depth.renderOrder = -1;
hull.renderOrder = 1;
hull.parent.add(depth);
```

The pre-pass writes depth and draws nothing; the additive pass then fails the
depth test on anything behind the nearest surface, which is the actual cause.
`polygonOffset` avoids z-fighting between the two coincident meshes.

**Verify by measuring, not by eye** — same method C3 used: render, sample
pixels, report % pure-white and % near-white before/after, plus total lit-pixel
count (should barely move — a fix that also dims the ship overall is not this
fix).

## 2. Fix the marker position scale — but read this carefully, the fix differs by dataset

**For the 4-ship dataset currently live** (`hardpoints.json`, Cutlass/Aquila/
Sabre/Cyclone): its `pos` field is centimetres, the site's `.glb` models are
metres. Multiply by `0.01` before use:

```js
marker.position.multiplyScalar(0.01);  // cm -> m
```

Verified: `Weapon left nose` on the Sabre becomes `z = -11.80` against a hull
half-length of `11.94` — on the nose, correctly.

**This does NOT carry over unchanged to the 167-ship fleet dataset in §3.**
Read that section before assuming `* 0.01` is the permanent fix — it isn't.
Do §1 and §2 first against the existing 4-ship data, confirm 8/8 markers land
on the Sabre's hull, THEN move to §3. Two unit systems in flight at once is
exactly the bug class both findings are about — don't let it happen a third
time.

**Two more things to carry over from the finding, both worth keeping:**

- Marker size scales to hull size (`span * 0.018`) instead of a fixed 0.43
  units — otherwise a marker that reads fine on a 24 m fighter is a speck on a
  61 m Constellation.
- Once the depth pre-pass exists, markers need `depthTest:false` to not be
  hidden by the hull's own depth buffer, or they need to fade instead. See the
  decision below — don't pick one silently.

**Decision — far-side markers fade to 30%, they do not show through the hull.**
`depthTest:false` on markers would make them show through solid geometry,
which reads as "this ship is transparent," not as a UI convention. The
prototype faded far-side markers instead, and that's the better default: it
keeps the illusion that you're looking at a real hologram of a solid object.
Implement fade, not depthTest:false. If you disagree with the read here, say so
in the writeup rather than silently picking the other option — this is a
product-feel call, not a hard technical constraint, so it's worth a sentence
either way.

## 3. Swap in the 167-ship fleet dataset

**Source:** `data-layer/derived/holo-hardpoints/hardpoints_fleet.json` (641 KB)
+ `MANIFEST.json`, from C3 — 167 ships, 1,798 hardpoints, up from 4 ships / 35.
Read the finding (`FINDING_fleet-hardpoints-167-ships-2026-08-10.md`) in full
before touching `build_holo_data.py` — the shape changed, not just the count.

**The schema is different from the 4-ship file, on purpose:**

```
old:  name -> [hardpoints]
new:  name -> {maker, bare, model, dimension, pilot_dps, weapons, frame, hardpoints}
```

Each hardpoint now carries `where`, `port`, `kind`, `pos_model`, `unit`,
`read`, `items`.

**`pos_model` is NOT centimetres and does NOT get `* 0.01`.** It's in whatever
coordinate space that specific ship's own `.glb` was decoded in — C3 measured
it directly off each mesh, so it already matches that model's local space.
**Plug `pos_model` straight into the loaded model's local coordinates with no
scale conversion.** The `frame.model_units_per_metre` field exists for anyone
who wants a real-world metre number (a UI label, a comparison) — it is not a
placement input. Confusing those two is exactly the bug in §2; don't reproduce
it going the other direction.

If you want a placement value that's guaranteed unit-safe regardless of which
of the three model conventions (metres / centimetres / normalised) a given
ship's `.glb` turned out to use, `unit` (normalised to the hull's longest axis,
-1..1) is the field C3 recommends preferring — multiply by the actual loaded
mesh's own bounding-box half-extent on each axis. Either `pos_model` (direct)
or `unit` (bbox-relative) is defensible; picking one and saying which, and why,
is the requirement — same discipline this project already holds build-mechanics
calls to.

**`items` is the mount, not the gun.** ship_specs gives the equipped mount per
port; it does not say which gun sits in which mount. Don't invent that pairing.
Render `weapons` (ship-level, with DPS) as the ship's armament list separately
from the hardpoint markers, same as the mount-name-only markers already do.

**`build_holo_data.py`'s matcher does not need to change** — C3 reproduced its
exact matching rule (strip manufacturer prefix, exact match on the CC_SAFE
key), so the new fleet file matches existing site ship IDs by construction.

**7 ships were deliberately skipped** (Clipper, Defender, Eclipse, Nova, Pulse,
Pulse LX — hull proportions don't match published dimensions; Javelin — no
published dimensions exist to check against). These should fall through to the
same honest "no derived hardpoint data" state the Cyclone already uses. Not a
new code path, just confirm the existing one still catches ships absent from
the new file.

**76 of 1,798 hardpoints have nothing readable in the mount name** and sit at a
generic default position, flagged with an empty `read` list in the data. Doesn't
need special UI treatment for this pass — just don't let it silently look as
confident as a real reading if you're already touching the hardpoint panel.

## 4. What NOT to do

- Do not apply `* 0.01` to the new fleet dataset's `pos_model` — see §3.
- Do not invent a gun-to-mount pairing — `items` is the mount only.
- Do not touch fonts or `MANUAL_MATCHES` — both still explicitly Sleven's open
  calls, unrelated to this order.
- Do not run `place_fleet.py` or re-derive anything — C3's output is final for
  this pass; this order is about consuming it correctly, not re-deriving it.
- Do not deploy. Build only — a separate go-ahead covers pushing this live.
- Do not `git add -A`.

## 5. Acceptance

1. Render the Sabre, headless or otherwise, **served over `http://`, not
   `file://`** — a DRACO worker is blocked under `file://` by Chromium's origin
   rules regardless of flags, which is exactly what made last night's build
   read as "unverified" when it wasn't. Screenshot or pixel-sample it.
2. Pure-white / near-white pixel percentage measurably drops to ~0% on the
   Sabre, lit-pixel count roughly unchanged (not just dimmer overall).
3. All 8 of the Sabre's markers land on or very near the hull surface, not
   off in space — check distance from each marker to the nearest hull vertex.
4. Far-side markers fade rather than show through solid geometry.
5. After the §3 swap: spot-check at least 3 ships spanning the three measured
   model-scale conventions from the fleet finding — one ~1 metres/unit
   (typical), one of the 8 normalised/small ships (e.g. Avenger Stalker), the
   one ~100 (centimetre-scale) ship — and confirm markers land on each hull
   correctly. This is the actual regression test for the bug class both
   findings describe; don't skip it because most ships are "the normal case."
6. Ships with no fleet-dataset entry (the 7 skipped, plus anything outside the
   167) fall through to the existing no-hardpoint-data state, not an error or
   a blank canvas.
7. `python testing/_src/build_deploy.py` and `check_deploy_clean.py` both still
   pass clean.

## 6. Report back

Same shape as the other holo-viewer handoffs: the before/after pixel
measurements, the marker-to-hull distance check, which far-side-marker
approach you implemented and why if you changed the call in §2, the
`pos_model` vs `unit` choice and why, and explicit confirmation of which ships
you spot-checked across the three scale conventions.
