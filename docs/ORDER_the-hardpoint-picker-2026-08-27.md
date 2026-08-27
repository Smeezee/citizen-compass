# ORDER — the hardpoint picker, on every ship

**2026-08-27 · C1 · for Code · approved by Sleven after seven prototypes**

**Scope: the hull-marker interaction and the picker that opens from it. That is
all.** The left-panel rebuild is still parked, and the "inside the ship" dock
from the prototype is explicitly NOT in this order — Sleven called it sloppy
and questioned why a cargo grid is in it. He is right; it needs its own pass.

C1 holds a working prototype (Drake Vulture, real model, real data) and can
supply exact values for anything below that reads as ambiguous.

---

## Why this exists

Sleven's brief: *"It can't just be a display of components and names. The
interaction of actually going through the steps of swapping the parts and
understanding what they do needs to be a smooth, fluid process ... I want
anybody who stumbles onto our website, never heard of it before, to actually
enjoy the experience of figuring out what the best setup for their ship is."*

Six static layout proposals were rejected before this one. **The product is not
the list. It is the loop:** pick a mount, understand what is on it, see what a
change would do, keep it or undo it.

---

## H1 — the hull shows nothing until it is asked

**Markers are dots. No names, no boxes, nothing floating over the hull.**

The current permanent labels fight each other and the ship for the same pixels;
on anything busier than a fighter they cover the model they are describing.
This was Sleven's own diagnosis and his own fix.

- **Hover a dot** → a single compact chip appears just above it, carrying the
  fitted part's name and the mount type. It disappears on mouse-out.
- **Click a dot** → the picker opens.
- **A mount the game fixes gets a visibly different dot**: smaller, thinner
  border, no glow, no hover-grow. It must not look like a button.

## H2 — the picker docks and stays put

It opens **beside the mount that was clicked**, then **stops moving.** Rotating
the hull underneath must not drag the panel around the screen — the prototype
did that at first and Sleven's verdict was that it looked interesting for four
seconds and was annoying after that.

- A dotted leader line runs from the panel to its dot and **follows the dot**,
  so the tie to the mount survives the rotation.
- **It must clamp inside the stage on both axes, measured after render, not
  estimated.** The prototype's first attempt guessed the height from a formula
  and coolers ran off the bottom of the screen.
- Escape closes it. Clicking off it closes it.

## H3 — no scrolling inside the picker. Ever.

**Show the best 4 by the active sort, plus the fitted part pinned.** Five rows,
no scrollbar, on every ship and every component type.

The footer states the truth plainly: `best 4 of 26 · re-sort to see others`.
Re-sorting is how a person reaches the rest — not a scroll wheel.

## H4 — the sort tabs use THE SITE'S OWN VOCABULARY

**This is not a place to invent words.** `loadout.html`'s own WATCH table
already settled this project's stat names and they are the ones to use:

    Sustained DPS · Alpha strike · Effective HP · Shield regen · IR signature ·
    EM signature · Total mass · Fitted containers · Radar sensitivity ·
    Radar piercing · Mining throughput · Mining range · Beam range · Beam force

Tabs carry the short form a player actually says — **DPS, Alpha, EM, IR, Mass,
Shield HP, Regen, Cooling, Power** — and each is one word so nothing wraps or
runs off the panel edge.

**The tabs are per component type.** A weapon offers DPS / Alpha / EM / Mass. A
cooler offers Cooling / EM / Mass. A shield offers Shield HP / Regen / EM /
Mass. **A cooler must never be offered "biggest hit".** Which stat leads is a
property of the component, not of the page.

## H5 — every row earns its place

Per option: **its own size chip**, the part name, manufacturer and family, the
value of the active stat with its unit, and **the delta against what is
currently fitted** — coloured, and correct about direction. Lower EM and lower
mass are improvements and must read green.

The fitted row shows a small `FITTED` tag instead of a value and delta.

## H6 — a fixed mount shows its DATA, not an apology

The prototype's first version put a sentence where the numbers should be and
Sleven could not read anything about the part. **A fixed mount now renders the
part's real stats** — name, manufacturer, size, and every published figure
under the site's own labels.

Where CIG publishes nothing, say **"No stats published for this part"** — that
is a fact about the data. The "fixed by the game, still counts toward every
number on the right" line moves to the footer where it belongs.

## H7 — the mirror is an OPTION, never a feature

On a mount that has a mirror twin, a switch appears: *"Also change the other
side to match."* **It is OFF by default.**

Sleven's ruling, in his words: *"it should be an option to select both wings at
the same time IF you plan to put both wings to the same guns. Maybe somebody
wants to swap that up."*

- The twin's dot highlights while the switch is on, so the second thing being
  changed is visible before it changes.
- **On a mount with no mirror the switch does not exist** — that is the
  difference between an option and a feature.
- Open question, deliberately unresolved: whether the switch should remember
  its state across mounts within a session. It resets today. Decide it after
  somebody has swapped four pairs in a row, not before.

## H8 — the consequence is visible before the commit

**Hovering an option moves the numbers in the right rail**, showing the build
you would have. Not after clicking — while deciding.

The rail's existing behaviour is unchanged otherwise; this only adds a preview
state that clears on mouse-out.

## H9 — auto-spin is off by default, with a control

`boot()` sets `controls.autoRotate` true and the prototype tried to override it
with a flag afterwards, which did nothing. **Use `setSpin()` / `spinning()` —
they already exist**, and they exist because Sleven reported this exact defect
once already. Read the button's label from `spinning()`, never from a local
variable.

Ship a **reset view** control beside it.

---

## The look

**Rounded, softly translucent panels with faint corner brackets and a quiet
palette.** Sleven chose this from six treatments and named the parts: the
angles from the glass style, the corner marks and monospace figures from the
HUD style, the colours from the quiet style.

Specifically: hairline borders rather than heavy ones; a desaturated blue-grey
accent rather than hard cyan; muted green and red on deltas rather than alarm
colours; monospace for numbers and the `FITTED` tag, proportional for names.
The fitted row is a soft tint and a small tag — **it must not be the loudest
thing in the panel.**

---

## What this must survive

**The prototype was a Drake Vulture: four mounts.** The real test is the RSI
Polaris at 29 mounts and the Perseus at 37. Before this ships:

- dots must not pile into an unreadable cluster at those counts
- the hover chip must not flicker between neighbouring dots
- the picker must still open somewhere sensible when the mount is at the edge
  of the stage

**If 29 dots is unworkable, say so with a screenshot rather than shipping it
and letting Sleven find out.**

---

## Known gaps, stated rather than hidden

**Marker positions are derived from CIG's hardpoint names and are approximate.**
The Vulture's guns are named `hardpoint_weapon_nose_left` / `_right`, so they
plot at the nose tip while the guns physically sit beside the cockpit. The page
already discloses that positions are derived. Nothing here makes that worse and
nothing here fixes it.

**Markers are weapons-only, and that is wrong for industrial ships.** The
Vulture's two salvage heads — `hardpoint_salvage_laser` — get no marker at all,
while two countermeasure launchers do. On a salvage ship the salvage arms are
the defining hardware and they are invisible on the hull. **Not in this order.
Filed so it is not lost.**

**The panel's content is provisional.** Sleven: *"not sure if I fully agree on
the info that's in the ship hardpoints, but that can get fixed later."* Build
what is specified; expect it to move.

Do not deploy the live site. Testing only.
