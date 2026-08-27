# ORDER — The hull reads as a solid object. Measured, not proposed.

**Written by C1, 2026-08-23, after building and rendering all of it.** Every
number here came out of a headless browser reading its own framebuffer, not out
of an argument. The demo Sleven judged is `render-bench.html`; these are the
values it runs.

**THIS SUPERSEDES E13's tuning guidance. E12 remains WITHDRAWN — do not
implement it, do not measure winding, do not modify a model.**

---

## What is actually wrong, in one line each

1. **The hull renders at ~9% brightness.** `CC_HOLO_FRAG` is ambient 0.040 +
   key 0.20. Head-on, fresnel contributes zero by construction.
2. **The near plane is derived from the model's size, not the camera's
   distance.** `near = max/500`, `far = max*60` — a ratio of **30,000:1** on
   every hull.
3. **THE LINE PASS IS THE DEFECT.** At 24 degrees we generate **39,425 segments
   on the Aurora LX and 603,154 on the Javelin**, drawn additively over a
   near-black surface. RSI draws about forty lines on a Mercury, and their
   Default has no line overlay at all — what looks like panel seams there is
   geometry catching light.

**Measured: the fraction of each hull showing something other than its own
nearest solid surface runs 20.6% to 67.1% today.** Quietening the lines takes it
to 12.9-45.6%. **Removing the line pass takes it to 0.00% on all ten.**

## G1 — Replace the surface shader

Opaque, diffuse-led. These constants were rendered and judged, not derived:

    vec3 L1=normalize(vec3(0.40,0.86,0.32));
    vec3 L2=normalize(vec3(-0.70,0.26,-0.40));
    vec3 L3=normalize(vec3(0.10,-1.0,0.15));
    float d1=clamp(dot(N,L1),0.0,1.0), d2=clamp(dot(N,L2),0.0,1.0), d3=clamp(dot(N,L3),0.0,1.0);
    float spec=pow(clamp(dot(reflect(-L1,N),V),0.0,1.0),46.0);
    float fres=pow(1.0-abs(dot(N,V)),3.2);
    float wrap=clamp((dot(N,L1)+0.50)/1.50,0.0,1.0);
    float lit=0.165+d1*0.870+wrap*0.155+d2*0.235+d3*0.070;
    vec3 c=uColor*lit+uColor*(spec*0.42+fres*0.17*uRim);

**The `wrap` term is load-bearing** — without it, surfaces turning away from the
key light go black and the ship loses its far side again.

**Leave `uGlow` alone.** The rim was never the problem.

## G2 — Derive near and far from the camera, and fit the projected box

    near = max(dist - boundingSphereRadius*1.8, dist*0.02)
    far  = dist + boundingSphereRadius*3.0

**Clamp near to a positive minimum.** A zero near plane makes the projection
matrix NaN and the camera never recovers — this cost me a blank canvas and it
will cost you one.

Frame by **iterating the projected bounding box**, not the bounding sphere:
project the 8 corners, scale distance by the worst overshoot, repeat ~6 times.
Sphere-fitting leaves long thin hulls tiny in frame.

## G3 — The default style draws NO line pass

Solid shading carries the panel detail. Keep `panel`, `wire` and `points` as the
opt-in family. **This changes what the page OPENS on.**

**DO NOT put `polygonOffset` on the hull material.** I did, in the first pass,
to keep lines off the surface. It displaces the whole hull backwards and the
slope-scaled term explodes on steeply-angled faces — the background grid punched
through the nose in speckles. If lines ever need lifting, offset the LINES
toward the camera, never the surface away.

## G4 — Add a deliberate "See inside", replacing the accidental one

Fresnel-driven alpha, **normal blending — never additive**, depth writes off:

    float f=pow(1.0-abs(dot(N,V)),2.0);
    float lit=0.30+clamp(dot(N,L1),0.0,1.0)*0.75+f*0.95;
    float a=0.085+f*0.62;

This is the split RSI ships — Default and X-Ray as two intentional modes.

## G5 — Build the edge set LAZILY

Only when a style that draws lines is selected. Building 603,154 segments before
the first frame is a visible stall on every capital hull.

---

## Controls

    CONTROL, load-bearing: report "not clean surface" per hull, before and
    after, fleet-wide - the fraction of pixels inside an eroded silhouette that
    differ from a surface-only pass at the same camera. BEFORE must land in
    20-67%. If it does not, this measurement is not reproducing mine and stop.
    AFTER must be at or near 0.00%.
    NEGATIVE CONTROL, load-bearing: Lit hull UNCHANGED on every hull measured.
    Only the holo shader moves. Judge Lit-hull-to-Lit-hull only - CIC measured
    its mask running 2.1-3.1% smaller because the line overlay exceeds the solid
    silhouette, and that difference would read as a regression.
    CONTROL: capture via readPixels inside a rAF callback. preserveDrawingBuffer
    is false; toDataURL returns pure black at max luminance 0 and a check built
    on it would pass while measuring nothing.
    CONTROL: assert no hull clips the near plane or vanishes at the far plane at
    any zoom the controls allow, fully in and fully out.
    CONTROL: state the depth buffer bit count. It measured 24, WebGL2. I had
    guessed 16 and was wrong; if yours reports 16 the picture changes.

## Recorded, not ordered

**The meshes are watertight.** Flat-white FrontSide against DoubleSide, worst
gap **0.87%** (Reliant Kore), most under 0.05%. Nothing anyone reported was a
hole in a model.

**Every model is 1 mesh, 1 primitive, 1 material named "Default", alphaMode
OPAQUE.** There is no glass, no separable canopy, no named parts. Sleven can see
into the Aurora because the canopy geometry is ABSENT. **No shader work closes
that.**
