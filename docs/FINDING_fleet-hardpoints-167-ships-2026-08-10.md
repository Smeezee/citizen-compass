# FINDING — hardpoints now exist for 167 ships and 1,798 mounts, up from 4 ships and 35. The model library turns out to use three different scales, which is the same class of bug that hid every marker.

    from      C3 (Cowork), 2026-08-10
    for       C1 -> Code
    output    data-layer/derived/holo-hardpoints/hardpoints_fleet.json  (641 KB)
              + MANIFEST.json, place_fleet.py, placement_report.json
    method    ship_specs.json for mounts; the 235 .glb decoded in a browser for
              geometry; the four-ship derivation scaled up with two things that
              were assumptions before now measured per ship.
    scope     nothing on the project machine outside data-layer/derived/ was
              touched. Code's files are unchanged.

---

## 1. The numbers

    ships with mount data              278
    ships with a model under that name 174
    ships placed                       167
    hardpoints placed                1,798
    skipped, each with a stated reason   7

    by kind   mount 584 · other 533 · countermeasure 346 · missile 321 · gun 14

**1,722 of 1,798 were placed from words actually present in the mount name.** The
other 76 had nothing readable and sit at the generic default; they are marked
with an empty `read` list so the page can treat them differently rather than
present a guess with the same confidence as a reading.

Re-verified on this dataset, independently of the earlier one: **25,150 ports,
every single one with `position: null`, none with a real coordinate.** Nobody has
CIG's numbers. That has now been confirmed twice from two different files.

## 2. What had to stop being an assumption

Four hand-picked Fan Kit models let me assume things that are not true across 174
exported `.glb`.

**Which axis is which.** The Fan Kit hulls were all beam/up/length in the same
order. Rather than trust that, every hull's bounding box is now matched against
CIG's own published length, width and height for that ship — on **proportions**,
not absolute size, so it survives any scale. A hull whose shape does not agree
with its own spec sheet is refused and reported, not placed in a frame nobody
checked.

**Which end is the nose.** Measured per ship: the cross-sectional spread in the
slab at each end of the length axis. Tails carry engines, wings and hull; noses
are narrow. The wider end is the tail.

## 3. The finding inside the finding — the model library has three scales

The first version of the frame check compared absolute sizes and threw away **50
of 174 ships**. Looking at what it rejected is the useful part:

    Asgard            hull measures 3,388 x 1,333 x 4,856   -> centimetres
    Avenger Stalker   hull measures 1.4 x 0.49 x 1.91       -> normalised, ~unit size
    most others       hull measures ~= published metres     -> metres

Measured against each ship's own published length:

    158 ships   ~1     metres
      8 ships   <0.5   normalised / small
      1 ship    ~100   centimetres

**Three conventions in one folder, with nothing recording which is which.** This
is the same class of bug that put every hardpoint marker fifty ship-lengths off
the Sabre last night — a number whose unit lives in someone's head rather than in
the data.

So the output does two things about it. The position field is called
`pos_model`, **not** `pos_m`, because it is in whatever units that model uses and
calling it metres would be a lie on nine ships. And `frame.model_units_per_metre`
records the measured scale per ship, so a consumer can convert instead of guess.
There is also a `unit` field normalised to the hull's longest axis, which is safe
whatever the model does; **that is the one to prefer.**

This is worth a checker in the auditor layer independently of the viewer: a model
whose bounding box disagrees with its own published dimensions by more than a
sensible factor is either mis-scaled or mis-named, and both matter to the ship
pages.

## 4. Two defects found by checking, not by looking

Neither would have been visible in a screenshot of one ship.

**Nine hulls are not centred on their own lateral axis** — the Scorpius is 35% of
its own width off. The side test assumed the centreline was zero, which put every
"left" mount on the wrong side of those ships. Now measured from the hull's own
midpoint.

**Left/right pairs were landing on the correct sides but at different distances
out**, because the nearest sampled vertex differs on each side. Correct, and it
reads as broken. Pairs are now mirrored across the hull centreline and re-snapped
to a real vertex on the far side, so they stay on geometry and look deliberate.

    left/right pairs mirrored correctly   421 -> 469
    pairs still on the same side           3  -> 1
    pairs still lopsided                  57  -> 11

Mirroring then created a new problem — it bypassed the separation pass and
overlaps went from 15 ships to 28. A marker under another marker cannot be
clicked, and that is a silent failure, so separation is re-run **after** mirroring
now. Final state: **0 markers off the hull**, 11 ships where two markers are still
within 2% of hull size of each other, worst case about 1% — close, not stacked,
and listed in the report rather than smoothed over.

## 5. The seven that were skipped

    Clipper, Defender, Eclipse, Nova, Pulse, Pulse LX
        the hull's proportions do not match its own published dimensions
    Javelin
        no published dimensions to check against

**These are not failures of the placement — they are disagreements between two of
your own data sources**, and each one is either a mis-named model or a wrong spec
sheet. Worth someone looking at, and worth not papering over: placing markers on a
hull whose orientation nobody could confirm is exactly how you get a convincing,
wrong picture.

## 6. What Code needs to know about the shape

The four-ship file was `name -> [hardpoints]`. This is
`name -> {maker, bare, model, dimension, pilot_dps, weapons, frame, hardpoints}`,
because the extra fields are things the page needs and would otherwise be looked
up twice.

Each hardpoint carries `where`, `port`, `kind`, `pos_model`, `unit`, `read`,
`items`. **`items` is the mount, not the gun** — ship_specs gives the equipped
mount per port and the ship's weapon list separately, and it does not say which
gun sits in which mount. I did not invent that pairing. `weapons` at ship level
holds the guns with their DPS, and the page should present them as the ship's
armament rather than attach them to specific markers.

`build_holo_data.py`'s matcher does not need changing — I reproduced its exact
rule (strip a known manufacturer prefix, then exact match on the CC_SAFE key) so
everything here matches by construction.

## 7. What I checked and what I did not

**Checked:** every one of the 174 models decoded and verified complete before use
(five were truncated by a staging timeout and were re-fetched, not silently
dropped); every marker's distance to real geometry on all 167 ships; every pair's
separation; 481 left/right pairs for mirroring; the frame decision against
published dimensions on every ship; and rendered six ships I never tuned against,
on a plain grey hull with no glow, because a hologram effect can hide a badly
placed marker.

**Did NOT check:**
- **Whether any individual marker is where the gun really is.** These are derived
  from words and hull shape. They are approximately right and the viewer must
  keep saying so.
- The 76 mounts with nothing readable in their name are placed at a generic
  default. They are flagged, not fixed.
- The Hammerhead's six turrets look plausible rather than correct — a ship with
  known, specific turret positions is exactly where derivation is weakest, and I
  have no way to check it from the data.
- Nothing here has been through the actual viewer. It needs the two fixes from
  last night's finding first, and those are Code's to apply.
- Left and right still rest on the handedness assumption from the first
  hardpoints finding. Nothing in these models can confirm it either.
