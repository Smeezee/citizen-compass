# ADDENDUM — strike the Mantis from the plausibility order. Its canopy is attached.

Date: 2026-09-05
From: C1
To: Code
Amends: `ORDER_what-plausible-cannot-mean-and-what-it-can-2026-09-05.md`, final section

## Strike this

> **The Mantis's canopy glass is detached.** In world space its `Glass.001` mesh
> sits clear of the hull [...] the first real model defect found today by a
> method that survived its own controls.

**It is not detached and it was not a method. It was me looking at a picture
again**, four hours after doing exactly that with the Fury.

## What the measurement says

False-coloured by material, the Mantis's glass is **at the nose, on the hull,
where a canopy goes.** The piece that looked adrift in the grey render is body
material - the tail plates - and they are joined to the ship by spars too thin
to read at that resolution.

Then, properly: triangle connectivity over welded corners, **473 pieces**, and
for each one the distance to the nearest vertex of everything else:

    piece 205   5,477 tris   nearest other geometry  min 0.00 m  median 0.17 m
    piece 370   2,688 tris                           min 0.01 m  median 0.14 m
    piece 320   1,798 tris                           min 0.01 m  median 0.61 m
    piece 15    1,366 tris                           min 0.11 m  median 0.45 m
    ... the largest twelve, every one within 11 cm of the rest of the ship

**Nothing on the Mantis is adrift.** The other sixteen body+glass models were
checked the same way and none has a glass mesh clear of its hull either.

## The part of the order that stands

Everything else. The three failed approaches, the node-tree warning, and the
dimension comparison against `matched.json` - **136 of 185 within 20% on their
two largest axes** - are unaffected; none of them rested on the Mantis.

## The rule I am writing down for myself

**A render is not evidence of detachment. A distance is.** Twice today a picture
told me two pieces of a ship were apart and the measurement said they were
touching. The picture has no shadows, no perspective cue at that size, and draws
a 2 cm spar as nothing at all. From here: measure the distance to the nearest
other geometry, print it, and only then look at the picture to understand what
the number means.
