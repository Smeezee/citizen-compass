# ORDER — The picker redesign (REV 2, CONSOLIDATED — supersedes rev 1 entirely)

    from    C1
    date    2026-08-22, revised same day after Sleven drove the deployed page
    for     Code
    files   testing/_src/loadout.src.html, testing/_src/cc_viewer.js,
            testing/_src/build_deploy.py,
            data-layer/derived/holo-hardpoints/place_fleet.py
    status  RUN CONTINUOUSLY. B0 through B9, in order, no decision gates.

**This file is rev 2 and it REPLACES rev 1 at this same path.** Nothing from rev 1
survives except by being restated here. The inbox watcher does not overwrite, so
this was written directly to `docs/` on purpose — do not go looking for a
timestamped second copy.

---

## What changed, and why B0 is new

Sleven drove the deployed page on the Avenger Stalker and the Origin 400i and
reported: *"None of the hard points did anything... that tells me that not all
the ships have been done."*

**He is right about the symptom and wrong about the cause, and the real cause is
worse.** Every ship has been done. The markers are being rendered correctly, for
the correct ports, in the correct places. **They are simply not clickable, and
they do not say so.**

Measured across the whole fleet, from the generated data:

    1,200  hull markers on 157 hulls
      418  CLICKABLE           34.8%
      782  SILENT              65.2%   <-- clicking does nothing, says nothing
        0  unresolvable

    61 hulls where EVERY SINGLE MARKER IS SILENT.

The two he happened to open:

    Aegis Avenger Stalker    7 markers,  5 clickable,  2 silent
    Origin 400i             10 markers,  2 clickable,  8 silent

**And the silent ones are the interesting ones.** By hardpoint name, the biggest
silent families are countermeasure launchers (159 across their spelling
variants), `hardpoint_turret`, `hardpoint_missile_rack_left/right`, and
`hardpoint_weapon_nose`. On the 400i the dead ones are literally
`hardpoint_missile_left`, `hardpoint_missile_right`,
`hardpoint_remote_turret_top` and `hardpoint_remote_turret_bottom` — the four
things a person would click first.

**Why it happens:** `selectPort()` opens with

    if(!swappable(slot)){ sel=null; renderPicker(); return false; }

A fixed port therefore clears the selection and re-renders the same empty
prompt. From the outside that is indistinguishable from a broken button.
`renderMarkers()` meanwhile draws a marker for every entry in `LOADOUT_MARK`
without asking whether it can be selected.

**This is the same defect class as N1 and the RSI-link erratum:** the code is
doing exactly what it was told, the control asserted the mechanism rather than
the experience, and the failure was only visible to a person with a mouse.

---

## B0 — A MARKER THAT DOES NOTHING MUST STOP EXISTING IN THAT FORM

Highest priority. Everything else on this page is cosmetic next to a control
that lies.

**A fixed port keeps its marker and becomes informative rather than inert.**
Clicking it opens a panel — in the same place the picker opens — that names the
part fitted there, its manufacturer, its size, the port's own label, **why the
game does not allow it to be changed**, and the `last_verified_patch` tag. This
is L4's rule applied to the model instead of only to the list: *a fixed port is
shown, not hidden, because "countermeasure launcher — LOCKED" tells a visitor
nothing about their ship.*

**Fixed markers must also LOOK different before they are clicked.** A person
should be able to tell at a glance which dots they can act on. Do not use colour
alone; use a different fill or ring so it survives colourblindness and a dim
monitor.

**Do not "fix" this by deleting the fixed markers.** Sleven's standing position
on fixed ports is that they stay visible because they are part of the ship. The
countermeasure launchers on a Vanguard are real, they are where the marker says
they are, and a visitor asking "what is that dot on the wing" deserves an
answer.

    CONTROL: drive the Origin 400i. Assert all 10 markers respond - 2 open a
    picker, 8 open the fixed panel naming the fitted part. Assert the string
    the panel renders for hardpoint_missile_left actually contains that port's
    fitted item's NAME, not a placeholder.
    NEGATIVE CONTROL, load-bearing: a swappable marker must still open the
    PICKER and not the fixed panel. Without it, a build that shows the fixed
    panel for everything passes.
    FLEET CONTROL: assert zero markers across all 157 hulls fall through to
    "click did nothing". Count them and print the count. It must be 0, and the
    check must be able to report a non-zero number rather than assuming success.

## B1 — The left column shrinks to what a person can act on

Sleven: *"over on the left should be shrink down and only show what's actually
listed."*

Fixed ports leave the loadout column entirely and move to the **Specs** tab.
`renderCol()`'s `<details>` fold at the bottom goes away with them.

**They must stay findable.** The existing sub-line already counts them —

    N ports · N can be changed · N fixed

— keep it, and make "N fixed" a control that takes you to Specs. In Specs they
keep everything L4 gave them: the fitted part, manufacturer, port label, the
reason it is locked in the game's own terms, and the patch tag.

**The split stays `swappable(s)`, which is `!!s.fit`, which is the port's own
`Editable` flag.** No list of types anywhere in it. The day CIG makes fuel tanks
swappable they move columns on the next data build with nobody editing code.
That property is the point and it must survive this change.

    CONTROL: left column contains ZERO non-swappable ports; Specs contains ALL
    of them; the two counts sum to the port total.
    NEGATIVE: a ship with no fixed ports renders a valid Specs tab and does NOT
    render an empty "Fixed" heading.

## B2 — One compact row per slot, only the selected one opens, FITTED PINNED TOP

The left column is one line per swappable port: size, what is fitted, the port's
plain label. Nothing else at rest. Clicking a row opens the picker **inline
beneath that row**; the rows above and below stay visible. Only one row is open
at a time; opening a second closes the first.

**This deletes the current full-column takeover** and the `← Components` button
with it. Closing the open row IS going back. Losing your place in a list you
were reading is the thing being fixed.

**THE FITTED PART IS PINNED TO THE TOP OF THE PICKER, with its full detail.**
This is a real defect Sleven hit, not a nicety: he opened the Avenger's
`Turret mount - size 4`, which offers **74 parts**, and the fitted one was not
visible anywhere on screen because the list sorts by DPS. **A person cannot see
what they are replacing.** Pin it, label it clearly as what is currently fitted,
and let the sort govern only the rest of the list.

Everything already correct about the picker stays: only parts that actually fit
this port on this ship, Best / Quietest / Lightest, hover previews the change,
a part that does not fit is absent rather than greyed.

    CONTROL: open the Avenger Stalker's turret mount port. Assert the FIRST
    entry rendered is the fitted part, on all three sort modes.
    NEGATIVE: click row 1, assert rows 2..n are still present and visible; then
    click row 5 and assert row 1's picker is GONE. Without the second half, a
    build that opens every row also passes.

## B3 — Weapons are chosen ON the model. Internal components are not.

Sleven's own scoping, and it is the rule for this item:

> *"the guns and missiles and stuff, and the gimbals and stuff, that can go on
> the hardpoint attachments with its own specialized place... I understand the
> components can't go in there, we don't have a proper way to hardpoint them."*

So the page has **two homes, split by whether the thing is physically on the
hull:**

**ON THE MODEL** — anything with a hull marker: guns, turrets, gimbals, missile
racks, missiles, bomb racks, countermeasures. Clicking its marker opens the
picker (or B0's fixed panel) **as a panel over the model stage**, anchored near
the marker. Choosing a gun happens where the gun is.

**IN THE LIST** — everything internal: power plants, coolers, shields, quantum
drives, radar, flight blades. These have no honest position on the hull and this
project has already ruled that they get a menu rather than invented markers. Do
not give them one.

Panel rules:

- It must **not cover its own marker**. Flip to the other side when there is no
  room.
- **Escape closes it. Clicking the model background closes it.**
- **The left column keeps its rows for hull-mounted ports too.** A person who
  prefers the list must not lose that. Clicking the row opens the same panel in
  the same place as clicking the dot. **One selection path, two entrances.**

`selectPort()` is documented as *"THE ONE PLACE A PORT GETS SELECTED. Both routes
come here."* **Keep that true.** Do not add a second selection path.

    CONTROL: click a marker; assert the panel rendered OVER THE STAGE with a
    computed position inside the stage bounds. Then click that port's LEFT
    COLUMN row and assert the panel opens in the SAME PLACE with the SAME
    content. Assert identity of the result, not merely that both do something.
    CONTROL: assert an internal component (a power plant) opens in the LIST and
    never over the model.

## B4 — The spin is off when the page opens

Sleven: *"the ship just constantly spins."* A stop control exists; that is not
the same as opening calm. Default to not spinning; remember the choice for the
session so somebody who wants it spinning is not re-clicking on every ship.

    CONTROL: first load, no stored preference -> `_view.spinning()` false and the
    button reads "Start spin".
    NEGATIVE: stored preference set to spinning -> comes up spinning. Otherwise
    "it does not spin" passes on a build where spin is broken.

## B5 — A turret gun inherits its position from its turret

Guns inside a turret are named `hardpoint_class_2` and similar. `place_fleet.py`
reads a mount's NAME for position vocabulary and that name contains none, so the
gun falls to the `None` target `(0.50, 0.50, 0.44)` — the middle of the hull.
The position it needs is on its parent, `turret_side_front_left`, which carries
`turret`, `side`, `front` and `left`.

**The parent chain exists upstream and is being thrown away.** `ships.json`
`Loadout[]` is a nested tree; items carry their own child loadouts; the flatten
drops the parent.

1. **Carry the parent's hardpoint name through the flatten** into the slot
   record as its own field. No parent means an explicit null.
2. **In `place_fleet.py`, fall back to the parent's name ONLY when the child's
   own name yields no position vocabulary.** Never instead of it.
3. **Record which happened.** Every placed point states whether it was placed
   from its own name or inherited. `renderMarkerNote()` keeps telling the truth.

**One fallback, one level, from a real parent.** Do not extend this to guessing
from siblings or any other heuristic.

    CONTROL: the Hammerhead. Assert that BEFORE, N markers sit within a small
    radius of hull centre; AFTER, those ports sit at their turret's position;
    and the count landing on the `None` target DROPS.
    NEGATIVE: a gun NOT in a turret is placed identically before and after. A
    fix that moves everything is not this fix.

## B6 — Place against the hull's measured extremity, not a fixed fraction

`TARGET` puts a wing mount at `(0.88, 0.46, 0.52)` of the bounding box on every
hull in the fleet, then snaps to the nearest vertex. That is a guess that a wing
sits at 88% of half-beam on a Vulture and on a Polaris alike.

For a mount whose name names an extremity — wing, pylon, nose, chin, roof,
canopy — take the hull's **actual extreme vertex in the longitudinal band the
name implies** instead of a fixed fraction. The snap stays; it is now snapping to
something already close.

**Honesty rules, non-negotiable:**

- **Still derived from a name, not read from the model.** The exports are one
  welded mesh with no mount nodes. B6 improves the derivation; it does not make
  it a measurement, and `renderMarkerNote()` must not begin claiming otherwise.
- **The 7 hulls SKIPPED for failing the dimension check stay skipped.** Do not
  lower that gate to gain ships.

    CONTROL: report distance moved per ship. Assert the fleet crowding count -
    currently 118 markers across 17 hulls pushed apart - does not get WORSE.
    NEGATIVE: a hull already close to the fixed fractions barely moves. If every
    ship moves a long way, the new measurement is wrong, not the old one.

## B7 — The damage readout is telling three different lies

The page shows Sustained DPS noted *"pilot-fired weapons"*. Correct, and not
enough:

    214 ships   pilot guns only          the readout is the whole truth
     61 ships   pilot guns AND turrets   the readout is half the truth
     11 ships   turrets only             the readout says 0 - actively wrong
    208 ships   carry missiles           counted nowhere at all

Sleven's correction stands: *"just because it has turrets, and those turrets are
manual, doesn't mean there's not guns for the pilot to shoot."* Do not merge
them — one number cannot mean both "what you can do alone" and "what a crew can
do".

Show separate figures, and only the ones a given ship actually has:

- **Pilot** — unchanged. Do not touch the proven `IsPilotSlaveable`
  outermost-lock calculation.
- **Turret** — what gunners add, labelled as needing crew.
- **Missiles** — total payload damage, labelled one-shot. **Never add a
  per-second missile figure to a DPS number.**

**A ship with no turrets shows no turret figure — an absence, not a zero.** A
zero is a claim. On the 11 turret-only ships the pilot figure is 0 and true, and
must say so in words rather than showing a bare 0.

    CONTROL: assert against all four populations by name - a pilot-only ship, a
    both ship, a turret-only ship, a missile carrier. Turret-only is
    load-bearing.
    NEGATIVE: a pilot-only ship shows NO turret row at all, not a turret row
    reading 0.

## B8 — Sweep, deploy to testing, verify from the served bytes

Testing deploys are automatic and need no permission
(`RULING_testing-deploys-are-automatic-2026-08-22.md`). **The live site is not
touched.**

Verify from the **deployed bytes** — not source, not a successful deploy. Drive
the served page:

- **The Origin 400i: assert all 10 markers respond.** This is Sleven's own
  reproduction and it is the acceptance test for B0.
- The Avenger Stalker turret mount: assert the fitted part is first in the list.
- Click a marker, then its left-column row; assert identical result.
- Left column holds zero fixed ports; Specs holds all of them.
- Page opens not spinning.
- **Re-measure page height at 1920x1080 and 1366x768. State both figures.**
- State the version ID and the upload diff, file by file.

## B9 — Report the fleet marker census, before and after

One short block in the ledger:

    markers total / clickable / fixed-but-informative / silent
    hulls where every marker is silent

**Before this order that last number is 61. After it, it must be 0**, and the
check must be capable of printing a number other than 0.

---

## Run rules

- **No decision gates.** Everything is pre-ruled. Genuine ambiguity: take the
  more reversible option, write down that you took it and why, keep going.
- **Ledger entry per item with the commit sha**, as you go.
- **Rule 12 on every item.** A control that cannot fail is not a control. If an
  item's control could be satisfied by a string being present in a file, it is
  the wrong control — drive the behaviour. **B0 exists because the previous
  marker control asserted that a click reached `selectPort`, which it did, on a
  port that then refused it.**
- **Do not `git add -A`.** Do not deploy the live site. Do not cut a release.
- **Do not touch any RSI-sourced asset.** Different order, and the
  reconnaissance said the models are not worth collecting.

## The one thing to argue with

**B2 and B3 both spend vertical space** — an inline picker pushes rows down, a
panel over the stage needs stage room, and P7 left only 85px of slack.

If they cannot both fit at 1366x768, **say so and say which you kept**, rather
than shrinking type to make the numbers work. Sleven's standing note: *"neat and
well thought out", not "smaller".*
