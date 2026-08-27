# Update — holo §1 and §2 fixed and MEASURED. §3 fleet swap not done; a new master order arrived mid-task.

Build clean, page parses, **not deployed**.

## §1 The white-hull blow-out — fixed

Depth-only pre-pass: an invisible copy of every hull mesh that writes depth and
draws nothing, `renderOrder -1`, with `polygonOffset` so the two coincident
meshes do not z-fight. The additive pass then fails the depth test on anything
behind the nearest surface, which was the actual cause — a 353k-vertex hull was
summing near face, far face and every internal rib along the view ray. The hull
material also drops from `DoubleSide` to `FrontSide`, since back faces were half
that sum.

## §2 Marker placement — fixed and PROVEN, without needing to render

Headless still cannot decode DRACO, so I measured it analytically instead:
**glTF stores the POSITION accessor's min/max in the JSON chunk, before any
DRACO decoding.** That gives the true hull bounds with no renderer at all.

Sabre hull half-extents: **11.69 x 2.16 x 11.94**, matching the 11.94 half-length
C3's finding cites.

```
mount                          raw pos (cm)         x0.01 (metres)        on hull?
Weapon left nose               [-176, -44, -1180]   [-1.76, -0.44, -11.80]  YES
Countermeasure launcher left   [-789, -82, 778]     [-7.89, -0.82, 7.78]    YES
Weapon missilerack left        [-656, -22, -104]    [-6.56, -0.22, -1.04]   YES
Weapon left wing               [-844, -74, 74]      [-8.44, -0.74, 0.74]    YES
   ... and the four right-hand mirrors
=> 8/8 inside the hull bounding box
```

"Weapon left nose" lands at **z = -11.80 against a hull ending at 11.94** — on
the nose, exactly as the finding predicted. **Without the fix that same marker
sat at z = -1179.9**, about 49 ship-lengths off the hull. That is the "invisible
markers" symptom, quantified.

Also done: marker size now scales with hull span (`span * 0.018`) so a marker
that reads on a 24 m fighter is not a speck on a 61 m Constellation.

**Far-side markers FADE to 30% — I agree with C1's call and did not override
it.** `depthTest:false` would draw markers through solid geometry, which reads
as "this ship is transparent" rather than as a UI convention. Markers now keep
`depthTest:true` (correct, since §1's pre-pass writes real depth) and are dimmed
when they sit behind the hull's midpoint relative to the camera.

**The unit convention is now emitted by the generator**, not assumed by the
page: `HOLO_PLACEMENT = {mode:"cm", scale:0.01}`. Both bugs this viewer has had
were a unit assumption made in the wrong place, so the data states its own
convention and any future dataset states a different one.

## §3 The 167-ship fleet swap — NOT DONE

Stopped here deliberately, because §2 says to prove the 4-ship path first and
**not have two unit systems in flight at once**. Groundwork done and worth
keeping:

**The three scale conventions, measured across all 167 ships:**

```
~1 units/metre (typical)     162 ships   median 0.9747
normalised / small             4 ships   Starlancer TAC 0.0093, San'tok.yai
                                         0.0096, Starlancer MAX 0.0113,
                                         Avenger Stalker 0.0953
~100 (centimetre-scale)        1 ship    Asgard 101.16
```

A **10,000x span**, which decides the next question.

**`unit` over `pos_model`, and I can now say exactly how to use it.** I checked
what `unit` is normalised against rather than assuming: for the 100i the
pos_model/unit ratio is 8.743, 8.757, 8.743 across x/y/z; for the Asgard it is
2427.3, 2426.6, 2427.8. **Identical on every axis** — so `unit` is normalised by
a SINGLE scalar, the hull's longest half-extent.

That matters, because the order says to multiply by "the bounding-box half-extent
**on each axis**". Doing that would stretch every axis that is not the longest.
The correct reconstruction is `unit x (one scalar: the loaded mesh's longest
half-extent)`.

I chose `unit` because it derives scale from the mesh actually in front of us,
so it cannot be wrong regardless of which convention a given `.glb` used —
whereas `pos_model` assumes our decode matches C3's measurement space, and that
assumption fails silently. With a 10,000x span across the fleet, removing the
assumption beats relying on it.

**One correction to the order:** it says the matcher "does not need to change".
It does not need to change because it becomes **unnecessary** — the fleet file is
keyed by bare name (`Sabre`, `100i`) and already carries `model: "Sabre.glb"`
resolved. No manufacturer stripping required.

## Why I stopped

`docs/prompt-code-MASTER-keybinds-and-the-rest-2026-08-12.md` arrived mid-task
(17:17) and names a **root cause for the swap control I shipped** — "the swap
control counts instead of swapping" — plus an analysis of the first real export.
That is the live page Sleven is testing, so it outranks a viewer nobody is
blocked on. Filing this rather than leaving it half-described.
