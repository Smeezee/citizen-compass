# ORDER — every ship faced backwards in the inspector. Fixed. Rebuild and deploy.

From: C1 (Cowork), 2026-09-04
For: Code

Sleven walked 93 of the 258 and wrote *"shows facing away from the user... needs to
be turned around"* on twenty ships before he stopped writing it, because it was every
ship. His words: *"I stopped reporting it because it became mundane... it was
distracting me from the purpose, which is to look at the actual ship."*

He was right and it was mine.

## Cause
The inspector's orbit opened at `th = 0.9`, which puts the camera at **positive Z** —
behind these hulls. Rendered the Cutlass Black at the old angle and its engines face
the camera with the nose pointing away.

**`cc_viewer.js` was never wrong.** It sets
`camera.position.set(d*0.75, ty + d*0.42, -d*0.85)` — **negative Z**, the front. The
site has always shown the nose; this page was the odd one out. Sleven asked
specifically that this not "fold over into the project" — it does not, and that is
measured from the viewer's own code, not assumed.

## Fixed in `testing/_src/_inspect.src.html` (C1)
- Orbit now opens at `Math.PI + 0.9`, the same side as the site, over the other
  shoulder. Set in both the initial state and in `orbit.set()`, so returning to a
  ship does not put it back to front.
- Fit radius `1.2 -> 1.45`. Sleven: *"ATLS / ATLS GEO — zoomed in too close, needs to
  zoom out just a little."*

Verified by rendering Cutlass Black, Corsair, Constellation Andromeda, ATLS, Cyclone,
Aurora MR and Vulture at the new angle: nose toward the camera on all of them, 0 page
errors, list reads 256. Previous source preserved at
`_to_delete/_inspect.src.html.pre_orientation_*`.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## The rest of his 27, for the record — NOT acted on
Fixed already, he can clear them: **600i Executive Edition** (vertex colours),
**Carrack w C8X** and **Carrack Expedition w C8X** (removed).

Diagnosed, model-side, not started:
- **85X** — *"like two ships on top of and inside each other facing different ways"*.
  Confirmed: 102 of its 112 meshes appear twice, `<name>` and `<name>.001`. Whoever
  prepared the file duplicated the whole ship in Blender.
- **Centurion** — *"not the right ship"*. Not investigated.
- **The five Constellations** — *"why is the lifted down on this ship but none of the
  others"* — landing gear deployed in the model. Needs checking; may be how RSI
  exported them.
- **Cyclone TR** — see-through. It is not on the 32-ship list from the winding survey,
  so this is a second shape of the same problem and worth a look.

He is 93 ships in and continuing.
