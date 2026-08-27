# ORDER — The queue. Everything outstanding, in the order it should be done.

    from    C1
    date    2026-08-23
    for     Code
    status  RUN CONTINUOUSLY, top to bottom. No decision gates.
    why     Code went idle with work outstanding across four documents. This is
            the single list. Where it points at another document, that document
            is authoritative for the detail.

**Ledger entry per item with the commit sha. Rule 12 control on every item, with
a negative control that could actually fire. Deploy to testing after any item
that changes what the page LOOKS like. No `git add -A`, no live deploy, no fuzzy
matching.**

---

## FIX FIRST — defects on the deployed site

### Q1 — E11: the labels do not follow the ship

`docs/ERRATA_ship-page-from-the-served-site-2026-08-23.md`, E11.

**`renderMarkers` is in the animation loop and `renderLabels` is not.** Labels
are placed once and abandoned; rotate the hull and they stay where they were.
Sleven found it on two hulls and it is on every one.

**Read E11a before writing code — there is a trap.** Do not move
`renderLabels()` into `onFrame` wholesale; the collision solve is not a 60fps
operation on 35 labels. Anchors and leader lines every frame, the solve
throttled.

**Its negative control fails today on every hull. If your check passes against
the current build, the check is wrong.**

### Q2 — E11b: labels still absent until a click on some hulls

E8 is recorded DONE and the symptom persists on the Anvil C8R Pisces Rescue —
four hardpoints, far below the threshold, nothing until a click. **Find the path
that skips them and say which it was.** The answer decides whether E8's control
was wrong or merely narrow.

### Q3 — E6: the control panel nobody can find

Still not recorded. **Sleven reported the entire control panel as missing while
looking straight at it**, because the only way in is a button labelled `Look`.
Rename it, give it a visible affordance, and auto-open it on a first visit then
remember it has been seen.

**This went up in priority when settings became permanent** — somebody who loses
their stored settings and cannot find the panel cannot get back to what they had.

---

## THEN — the scatter fix

### Q4 — `docs/ORDER_the-scatter-fix-2026-08-23.md`, S1 to S5

Unblocks `--with-children` and **puts the hardpoints back on the Drake Cutlass
Black**, which Sleven has now photographed twice as a hull with nothing on it.

**Ruling stands: children stay off until S2's control reads 24 of 24 on the
Hammerhead.** `docs/RULING_children-stay-off-until-the-scatter-is-fixed-2026-08-23.md`.

---

## THEN — finish the hologram order

`docs/ORDER_every-ship-is-a-hologram-2026-08-22.md`. Outstanding:

### Q5 — H1c: missiles group under the rack that carries them

The Gladius Valiant renders `Pioneer I Missile · Missile 01 attach`,
`02 attach`, `03 attach`… as separate full rows down the column. Group them,
count them, say they are carried on the racks above.

### Q6 — H1d: the click readout panel

The best thing in the prototype and it is not on the live page. Port every
element — including the derived position in metres, the derivation stated as
derivation, and the handedness caveat. **It replaces `renderMarkerNote()`'s
page-level block.**

**And fix the defect inside it:** the heading says `left top` while the port id
says `right_top`. The mirror control flips both or neither.

### Q7 — H1e: markers coded by kind

Shape as well as colour, checked against all five hull colours, not just the one
it was designed in.

### Q8 — H3's wiring, with C3's corrected numbers

**C3's `docs/FINDING_model-resolution-2026-08-22.md` supersedes your H5.** It did
the classification H5 did not:

    ships with no geometry ANYWHERE      12, not 21
    dark ships that are edition variants 90 of 115 - the shared-hull ruling covers them
    Fan Kit models that fill a real gap  exactly 2 - Cutlass Black, Constellation Aquila
    orphans that were a naming problem   8 of 40. The other 32 have no ship record at all.

**H4 shrinks to two ships. Keep it demoted.**

---

## THEN — the visual language

### Q9 — the design batch: 3a, 3b, 3d

`docs/DESIGN_the-visual-language.md`, section 3. **Working demos exist and Sleven
has driven them** — build from those, not from prose:

- **3a, row reflow, SITE-WIDE.** The name holds one line and never stacks; when
  the row runs out of width the data drops to its own line underneath. Every list
  on the site.
- **3b, stat tiles.** Sixteen boxes of equal weight means nothing leads. Value,
  compact graphic against the fleet, and provenance made structural.
- **3d, group headings.** Weight and a count, so a 117-port hull can be skipped a
  group at a time.

**The four settled rules are in section 1 of that document. Read them first** —
particularly 1d, which is why radial gauges were rejected.

### Q10 — navigation: HUD brackets, and a path where there is depth

Sleven's pick, 2026-08-23, after driving ten options.

- **Top level: HUD brackets.** Corner brackets on the active item, nothing else.
- **Depth: a path, and ONLY where a page has something inside it.** Ships,
  Manufacturers, Find and Help have depth; Sale calendar, Development and Sources
  do not, and **no path renders on those at all** — no lonely `Home ›`.
- **Trail, capped at one parent.** Arrived via Drake → `Manufacturers › Drake ›
  Cutlass Black`. Arrived from the matrix → `Ships › Cutlass Black`. A shared
  link with no route falls back to hierarchy.
- **Siblings stay pills.** Loadout / Engineering / Liveries are the same ship seen
  five ways, not depth.
- **Rejected: count cards.** The numbers change and a nav that must stay right
  about 7,932 is a maintenance problem.

---

## Standing note

**Sleven's own method, and it earned its place tonight:** build the demo, then
write the order. Three passes on the compact stat happened because he could click
each one, and none of it would have survived being described in prose.
