# FINDING — ten ships drew every hardpoint in a heap the size of a cockpit, and the page called them CIG's own coordinates. Four green controls let it through.

    from    C1 (Cowork), 2026-08-28 / 29
    found   by photographing all 295 ships, not by a check
    status  FIXED in build_hardpoint_placement.py; a new control holds it
    control checks/_verify_marker_spread.py — INDEPENDENT, both directions

---

## 1. WHAT WAS ON THE SITE

The Tiburon drew **all seventeen** of its hardpoint dots in a single cluster in
the middle of the hull. The Xian Scout's four sat on top of each other. The
Mantis, the Hermes, both Auroras, the Basher, the M80, the Starlite and the 600i
Executive Edition, the same.

**Every one of those dots was labelled `cig`** — the page telling a visitor these
were positions CIG published, decoded from the game files. **Confidently wrong is
worse than absent**, and this was as confident as the page gets.

## 2. WHY

The scale rule is *CIG's Length against the hull box's fore/aft extent*, and
fore/aft is taken to be the GLB's Z axis:

    s = Length / ext[2]

**That is only meaningful if ext[2] IS the ship's length. On 19 of 258 models it
is not.**

    Mantis.glb                 X 1680.4   Y(up) 2964.9   Z(len)  629.8
    600i_Executive_Edition     X 5201.8   Y(up) 9026.8   Z(len) 1751.0
    Tiburon.glb                X   84.5   Y(up)   47.5   Z(len)   14.0

A ship is not 2,965 tall and 630 long. On those hulls the scale came off the
wrong axis and every mount collapsed toward the origin.

## 3. THE PART THAT SHOULD WORRY US — FOUR GREEN CONTROLS

    containment   passed. A heap in the middle IS inside the hull box.
    the mirror    passed. A heap is still symmetric about the centreline.
    provenance    passed. The labels honestly described where the numbers came
                  from — the numbers were just wrong.
    the census    passed. Nothing was LOST; the dots were all present.

**Each was asking a real question and not one of them was this one.** Every
existing control asked whether a marker is CORRECT. None asked whether the set
of them is PLAUSIBLE — whether a ship's mounts spread across the ship.

**It took a picture.** 295 ships loaded in a real browser and screenshotted with
their markers on. The Tiburon's clump is unmissable at a glance and invisible to
every assertion we had.

## 4. THE FIX, AND THE INSTINCT I HAD TO OVERRULE

**Placement now refuses a model whose orientation it cannot establish.**

Taking the longest axis as fore/aft would be a guess, and wrong for hulls that
genuinely are wider than they are long. This project refuses ambiguity rather
than resolving it by picking, so a hull whose model measures taller than it is
long is refused: it loses its CIG dots and falls back to name-derived estimates,
which the page labels honestly as estimates.

**I tried twice to keep the ones that looked fine.** Four hulls — the Pitbull,
the Railen, the San'tok.yai and the Reliant — draw dots that spread across them
convincingly, and I built a two-signal guard specifically to spare them. Then:

> Their scale came off the same wrong axis as the Mantis's. Their bounding boxes
> are merely closer to cubic, so the error is small enough to look right.
> **Looking right is not proof.**

They are refused too, and they come back when the models are re-exported in a
known orientation — not because their dots happened to land plausibly.

    placement    276 passed -> 260 passed, 16 refused for orientation
    the page     9 hulls lose their markers entirely; the rest fall back to
                 estimates and say so

Every loss is **declared in `checks/marker_census.json` with the reason**, so it
prints on every run rather than being absorbed.

## 5. THE CONTROL

`checks/_verify_marker_spread.py`. **INDEPENDENT**: the hull's real size is read
out of the `.glb`'s own binary header — the artist's mesh, which this project
does not write at any stage — and compared against the emitted marker positions.

**It needs two signals to refuse**, and the first draft taught me why:

> Refusing on spread alone at 0.5 named the Caterpillar, the Retaliator and the
> Eclipse. **All three were wrong** — their screenshots show dots running nose
> to tail exactly where the guns are. It measured top-level mounts when the page
> draws one dot per mount ROOT including children, and the threshold sat in a
> crowded band rather than an empty one.

Measured on what is actually drawn, heaped hulls run 0.100–0.446 and healthy
ones 0.493–1.756 — a gap of 0.047, which is not enough to hang a verdict on. So
a low spread alone is **reported, never refused**; refusal requires the
independent cause as well.

## 6. WHAT IS STILL OPEN

**Two hulls the placer does not catch.** The M80 and the Starlite pass its
measurement and heap on the page, because the placer measures mounts the page
never draws. The control catches them and goes red, which blocks a deploy —
correct, but the fix belongs one step later, in the emitter, where PortIds
exist. **That file is Code's** and the item is his to take or leave.

## 7. THE ROOT CAUSE, FOUND AFTER THE FIX — AND WHY IT IS NOT FIXED

The models are not badly exported. **The placer is reading the wrong box.**

`glb_box()` takes the accessor `min`/`max`, which are in MESH-LOCAL space.
three.js applies each node's rotation and scale before drawing. On a model whose
node carries a rotation — and the broken ones do, while the working ones carry
none — those are two different objects:

    Mantis.glb    raw accessor bounds    1680.4 x 2964.9 x 629.8
                  with node transform       30.0 x    6.4 x   17.0
    CIG's own dimensions for the Mantis      30.0 /   17.0 /    7.5

    Tiburon.glb   with node transform      121.0 x   20.0 x   68.0
    CIG's own dimensions                    121.0 /   68.0 /   20.0

**Exact.** The transformed box is the ship; the raw one is not.

`glb_box`'s own docstring promised this case was covered — *"so a future model
whose node transforms make the accessor bounds wrong is caught rather than
assumed away"* — and it was not, because **all five hulls it was validated
against have no node rotation at all.** The models that do are precisely the
ones nobody checked.

**I implemented the transform and reverted it.** Applying node scale also
changes the box for every model carrying a `CC_SCALE_ROOT`, which is most of the
fleet, and the placer's scale and acceptance were calibrated against the raw
box. The run that followed refused the Vulture, the Polaris and the
Starlancers — **200+ working hulls destabilised to rescue 16.**

A correct change that breaks everything downstream is not ready. What it needs
is a change-and-compare loop over all 295 ships with a build in it, and the
build needs a database this session cannot reach. **The orientation guard stays
as containment until then, and it is containment, not a fix.** The reasoning is
in the source at `glb_box` so the next person does not rediscover it — or worse,
ship it.

**One thing NOT to conclude from this:** the models do not need re-exporting.
They are fine. We were measuring them wrong.

— C1
