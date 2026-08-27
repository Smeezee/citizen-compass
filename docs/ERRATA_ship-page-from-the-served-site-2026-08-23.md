# ERRATA — four things Sleven found by driving the deployed site, 2026-08-23

    from    C1
    for     Code
    source  Sleven's own pass over citizencompasstesting.citizencompass-contact.workers.dev
            Gladius Valiant, Cutlass Black, Origin 125a, Zeus Mk II ES
    status  FOLD INTO THE CURRENT RUN. Do not open a separate run for these.

**What is working, said first because it is most of the page.** B0's fixed panel
renders exactly as ordered — the 125a's missile bay opens *"What is fitted here /
The port itself / Why it cannot be changed... its `Editable` flag is off in the
game files, so no loadout screen anywhere — ours or CIG's"*. B1's fixed count is
a link. B2 pins CURRENTLY FITTED at the top and highlights the source row. B3
opens over the stage. B4 opens still. B7 shows Turret DPS *"what gunners add —
needs crew"* beside Missile Payload. **All six are visibly correct on the wire.**

The four below are what he found wrong.

---

## E1 — 44 ships draw a hull and put NOTHING on it

**Sleven:** *"some ships don't even have hard points at all."*

Measured against the deployed data:

    201  ships render a model
    157  ...and carry hull markers
     44  ...and carry ZERO markers

**The Drake Cutlass Black is one of them** — 117 ports, 42 changeable, a model
that draws perfectly, and not one dot. Also: Aegis Eclipse, Aegis Javelin, Aegis
Gladius Pirate, Anvil C8R Pisces Rescue, every Argo ATLS variant, Argo CSV-SM,
both Argo MPUVs.

**This is not the B0 defect and it is not a bug in the viewer.** These hulls have
no entry in `LOADOUT_MARK` at all, so nothing is drawn and nothing can be
clicked. **The page simply says nothing about it**, and a visitor cannot tell
"this ship has no weapon mounts" from "this page is broken".

**The prototype already solved exactly this and its wording is the fix.** Capture
05, the Tumbril Cyclone:

    This hull carries no weapon mounts in the data — nothing to mark on it.

**But do not copy it blindly, because the two cases are NOT the same and saying
the wrong one would be a lie.** The Cyclone genuinely carries no weapon mounts.
**The Cutlass Black carries 42 changeable ports and we simply have no positions
for them.** Those need different sentences:

- **No weapon mounts in the data** → the Cyclone's wording, unchanged.
- **Mounts exist, positions do not** → say that. *"This ship's 42 changeable
  ports are listed on the left. We have no measured positions for them yet, so
  there is nothing to mark on the hull."* The list still works; the model is
  just a picture on this hull.

**Distinguish the two from the data, never from a hardcoded list of ships.**

    CONTROL: assert the Cyclone-class message appears ONLY on hulls whose weapon
    mount count is genuinely zero, and the no-positions message ONLY on hulls
    with mounts and no LOADOUT_MARK entry.
    NEGATIVE: a hull WITH markers must show neither message.

## E2 — 513 parts render as a name and two zeros

**Sleven:** *"some of them don't provide any information."*

He is looking at the Gladius Valiant's `Turret mount · size 3`, where the options
under the fitted gimbal read:

    Remote Turret
    Aegis Dynamics
    IR 0   EM 0

That is the whole row. The record behind it is
`{"m":"Aegis Dynamics","ms":0,"n":"Remote Turret","s":4,"t":"tur"}` — **so the
page is not dropping anything. There is nothing else in it.**

**Fleet-wide: 513 of 3,283 parts carry no headline stat at all** — no DPS, HP,
range, power, cooling, SCU or mass:

    162  fut   fuel tanks
    145  qft   quantum fuel tanks
    124  wat   weapon attachments
     42  tur   turrets
     13  rad   radar
      8  crg   cargo
      7  sdt   self destruct
      4  wpn / 4 fui / 3 qig

**`IR 0 EM 0` is true and useless.** A row of zeros reads as broken data when it
is actually a part whose interesting properties are of a different kind.

**Show what the thing IS instead of what it scores.** A turret's real facts are
how many guns it takes and at what size — *"Remote Turret · takes 2 × S3 ·
gunner-operated"* is worth reading; two zeros are not. A fuel tank's fact is its
capacity. A weapon attachment's is what it attaches to.

**Where a part genuinely has no numbers anywhere, say so in words** — *"no
published stats"* — rather than printing zeros that look like measurements.
**A zero is a claim. An absence is not.** That is the same rule B7 applied to the
turret DPS row and it applies here unchanged.

    CONTROL: assert no rendered row shows ONLY "IR 0 EM 0" and nothing else.
    NEGATIVE: a part WITH real stats still shows them - otherwise a build that
    prints "no published stats" on everything also passes.

## E3 — The marker positions on the live site are PRE-B5 AND PRE-B6

**Sleven:** *"some of the hard points are not exact, and they need to be
adjusted."*

**He is right, and the reason is sequencing rather than a new defect.** Your own
B9 entry says it plainly: *"the marker POSITIONS are unchanged by this run. B5
and B6 both changed the derivation and neither was promoted."* Then the
promotion was stopped mid-run over the `turretOf` problem. **So the deployed site
is showing this morning's positions and neither fix has ever reached a screen.**

Two of his captures are the symptom, and they are useful as acceptance tests:

- **Aegis Gladius Valiant**, port `Turret mount · size 3`, labelled **"Gun
  nose"** — its marker sits at the **bottom-left** of the hull. A nose gun is at
  the nose.
- **Origin 125a**, port labelled **"Weapon missilebay front"** — its marker sits
  **mid-body**.

**Both are name-derived placements that B6 is meant to improve.** Neither is
evidence that B6 failed, because B6 has not run against the deployed data.

**So E3 is not new work. It is the B5/B6 promotion, blocked on `turretOf` being
populated on zero of 1,798 points.** Finish that, promote, redeploy, and re-check
these two ports specifically.

    ACCEPTANCE, named because they are Sleven's own reproduction:
      Gladius Valiant "Gun nose"        must move toward the nose
      Origin 125a "missilebay front"    must move toward the front
    Both are longitudinal, so they test the nose-end detection directly.

## E4 — The stage does not reframe when a panel opens

Smaller, and visible in one capture. On the Origin 125a with the countermeasure
panel open, **the hull is a small sliver at the far left** while the panel
occupies most of the stage. The ship is neither centred nor scaled to what is
left of the viewport.

The prototype has an `Auto-frame` control for exactly this. **When a panel opens
over the stage, the camera should reframe to the remaining visible area** so the
ship and its selected marker stay in view together.

**The selected marker must stay on screen** — that is the whole point of choosing
a gun where the gun is, and B3's rule that the panel must not cover its own
marker is defeated if the hull drifts out from under it.

    CONTROL: open a panel on a real ship and assert the selected marker's
    projected position lies inside the stage's remaining visible rectangle.
    NEGATIVE: with no panel open, the framing must be unchanged.

---

## Order of work

**E3 first** — it is already in flight and it unblocks itself. E2 next, because
513 rows of zeros is the most-seen defect of the four. Then E1, then E4.

**None of these opens a new run.** Fold them into the current one, ledger entry
each, Rule 12 control on each, and the standing rules hold: no `git add -A`, no
live deploy, no fuzzy matching.

---

## E5 — THE DISC IS AT y=0 AND THE MODELS ARE CENTRED ON y=0, SO EVERY SHIP IS BURIED

**Sleven, 2026-08-23:** *"the Avenger Stalker is like buried into the floor. Some
ships don't even have that floor thing there. Is there any way we can go through
all of them and make sure they're all correct?"*

**Nobody has to go through anything. It is one fix and it corrects all 235 at
once.**

### Measured across every model on disk

Reading the `POSITION` accessor min/max out of all 235 `.glb`, and asking where
`y=0` falls between each hull's own bottom and top:

    y=0 near the hull's BOTTOM (sits on the disc)     4
    y=0 in the middle of the hull                   224
    y=0 HIGH in the hull (sinks badly)                7

**The Avenger Stalker measures exactly 50.0%.** It is not a broken model — it is
cut in half by the ground plane, and **so is almost every other ship on the
site.** It simply reads worse on some silhouettes than others, which is why it
looked like a handful of bad ships rather than a systemic one.

**The seven worst, all more than half-buried:**

    75.9%  Vanguard Harbinger        72.4%  SRV
    75.8%  Vanguard Sentinel         65.9%  Valkyrie / Valkyrie Liberator
    73.4%  Hurricane                 65.1%  Hawk

### The cause, and why it is one line

**The disc is drawn at y=0. The models are centred on their own origin, which is
roughly their middle.** Neither is wrong on its own; together they bury the ship.

This is the same family as the scale problem already recorded in `place_fleet.py`
— the library holds **158 ships in metres, 8 normalised and 1 in centimetres**,
and the hulls are not centred consistently (the Scorpius is 35% of its own width
off its centreline). **Anything that assumes a fixed position in model space
across this library will be wrong on most of it.**

### The fix

**Do not draw the disc at y=0. Draw it at the hull's measured `min[1]`** — the
actual bottom of the bounding box that is already computed to frame the shot.
Every ship then sits ON the disc, whatever its origin or scale, with no per-ship
data and no list to maintain.

**Same for the missing discs.** If the disc is sized from a fixed figure rather
than the measured footprint, it will vanish or swallow the screen on the
odd-scaled models. **Derive its radius from the measured bounding box too**, and
report any hull where the result is degenerate rather than drawing nothing
silently.

    CONTROL: for every one of the 235 models, assert the hull's measured min[1]
    is at or above the disc plane - no geometry below the floor, fleet-wide.
    NEGATIVE CONTROL, load-bearing: run it against the CURRENT build and assert
    it FAILS on at least 224 hulls. A check that passes today is measuring
    nothing.
    CONTROL: assert a disc is present and has a non-degenerate radius on all 235,
    and name any hull where the radius had to be clamped.

**Report the count of hulls whose apparent resting position changed, and by how
much on the worst one.**

---

## E7 — The Wireframe button does nothing, and the hulls read softer than the prototype's

**Sleven, 2026-08-23, driving the deployed panel on three or four ships:** *"the
wireframe button inside the Look did not work. It didn't do anything. And the
ships weren't as well detailed as the ones in the prototype."*

**Two separate faults. Take them separately.**

### E7a — A style button that changes nothing

**This is the exact failure H1f's negative control was written to catch:**

> *assert that two DIFFERENT styles do not produce the same signature. Without
> it, a build where every button sets a class and nothing redraws passes every
> other assertion.*

**Either that control was not implemented, or it was implemented in a way that
could not fail.** Find out which and say so plainly — the answer matters more
than the fix, because the same shape will recur on the next control panel.

Then: **assert every one of the six styles produces a render signature distinct
from all five others**, pairwise, on a real hull. Not that a class was set, not
that a handler ran — that the pixels differ.

### E7b — Detail. TWO candidate causes, both measurable, do not guess between them

**Do not treat this as "our models are worse".** They are not. Measured earlier,
same two ships:

    Sabre     ours 353,731 v / 617,052 t    prototype 342,587 v / 621,882 t
    Cyclone   ours  81,341 v / 144,646 t    prototype  80,094 v / 144,714 t

**Same geometry.** The softness is in how it is drawn, not in what is being
drawn. Two candidates:

**1. Draco quantises the NORMALS, and the edge detector reads normals.**
Every model on disk is `KHR_draco_mesh_compression`, and **NORMAL is one of the
compressed attributes** — verified on Sabre, Cyclone and C1 Spirit. The
prototype's `.ctm` are not Draco.

Panel-line and wireframe extraction decides whether to draw an edge from the
**angle between adjacent face normals**, against the `LINE DETAIL` threshold
(24°). Quantised normals shift those angles, so edges near the threshold drop
out or flicker in. **That is exactly what "less detailed" looks like.**

**The fix needs no re-export: compute face normals from the triangle positions
rather than trusting the stored NORMAL attribute.** A face normal derived from
three vertices is exact for that face; the stored per-vertex normal is a
compressed approximation. Positions are quantised too but far less sensitively —
an edge either exists in the geometry or it does not.

**2. The defaults are wrong, and full intensity hides detail.**
The deployed page opens at `Line intensity 1.00`. **Sleven's own prototype
captures — the ones he called perfect — run at 33% and 36%, with glow at 0.04.**
At full intensity the lines bloom into each other and the hull reads as a solid
mass; his 33% capture is the crisp one.

**Ours also opens at `Glow 0.50` against the prototype's 0.04.**

**Measure both before changing anything.** Render one hull four ways — stored
normals at 1.00 glow 0.50, stored normals at 0.33 glow 0.04, computed normals at
1.00, computed normals at 0.33 — and report an edge count and a picture for each.
**One of those two causes will dominate and the numbers will say which.**

    CONTROL: report edge counts for all four combinations on the same hull.
    Assert computed-normal extraction yields MORE edges than stored-normal at the
    same threshold - if it does not, cause 1 is wrong and say so.
    THEN set the defaults from the measurement, not from C1's guess.

**If cause 2 dominates, the defaults become intensity 0.33 and glow 0.04** — his
own settings, which he arrived at by eye and which are on record in his captures.

---

## E8 — Labels appear only after a marker is clicked, then never leave

**Sleven, 2026-08-23, on the Anvil C8R Pisces Rescue:** *"that wasn't there until
I clicked one of the hardpoints, and then it popped up. And then when I clicked
out, it stayed."*

H1b's rule is that **labels ship in the default view** — they are what make a
derived position honest. Below the 14-marker threshold they should be on when the
page opens. On a 4-hardpoint hull they were off until a click, then stuck on.

**CORRECTED BY SLEVEN, 2026-08-23. ONE fault, not two.** *"Them sticking was
not [the problem]. I'd actually prefer if they were there as soon as the player
loaded in, so they could get an idea of what they were looking at and where
everything was located."*

**Labels ON from load is the intent.** The only defect is that they were absent
until a click. Sticking afterwards is correct behaviour, not a bug — do not
"fix" it.

    CONTROL: load a hull under the threshold and assert labels render BEFORE any
    interaction.
    NEGATIVE: select a marker and dismiss it, then assert labels are STILL
    showing. A build that resets them on dismiss is wrong.

## E9 — 238 flight blades offered, 5 of them distinguishable, most named after other ships

**Sleven:** *"what exactly is a flight blade? And an Anvil C8R Pisces able to put
an Avenger Stalker flight blade? I don't know what that is or why it's even on
there... I could be wrong, so please do the research."*

**He is right to be suspicious. The research, with sources.**

### What a flight blade actually is — established, not guessed

Star Citizen Wiki: *"a vehicle component that adjusts the flight behavior of a
vehicle. It is plugged into the ship's computer port."* Two tunings exist:

    PHB   Precision Handling Balanced   - manoeuvrability
    TSB   Top Speed Balanced            - speed

**They are real, and they are really bought.** 46 of them carry prices in our own
UEX shop data, and third-party sellers list them **as per-ship kits** — "RSI
Scorpius Series Flight Blades Kit", "Anvil Arrow Flight Blades Kit". CIG
announced them on Spectrum as *"Introducing Flight Blades: Shape Your Ship's
Behavior"*.

**The wiki page is a stub and does NOT state whether a blade made for one ship
fits another. The Spectrum thread body could not be retrieved. So the
cross-compatibility question is NOT settled by any source we have** — do not let
anyone write it down as settled.

### What our own data says, measured

    238 flight controllers in LOADOUT_PARTS
      5 DISTINCT stat signatures among all 238

    143 identical   mass 35, size 1, IR 0, EM 0, power 4
     52 identical   ... power 6
     23 identical   ... power 8
     10 identical   ... power 10
     10 identical   ... power 2

**Every one is mass 35, size 1, zero IR, zero EM.** The only field that varies is
power draw. **So the picker offers 238 choices that are, by our own numbers, five
things** — and 143 of them are literally indistinguishable from each other.

### The two problems, and they are separate

**1. The offer is almost certainly wrong.** Every purchasable blade is named
`<Ship> PHB Flight Blade` / `<Ship> TSB Flight Blade`, and they are sold as
per-ship kits. Our fitment rule matches on **type and size only**, so every
size-1 FlightController in the game matches every FlightController port. **The
game's own naming and its shops both say ship-specific; our rule says universal.
That is a real disagreement and it must be surfaced, not resolved by guessing.**

**INVESTIGATE, then report before changing behaviour:** does `ships.json` or the
wiki `ports` data carry anything that constrains a blade to a hull — a tag, a
`compatible_types` sub_type, a required_tags entry? **If it does, use it.** If it
does not, say so plainly and propose the options; do not silently narrow the list
on a hunch, and do not silently keep offering 238.

**2. Even if 238 is technically correct, showing it is useless.** A list where
143 entries are numerically identical is not a choice. At minimum: **group
identical parts, state the count, and show what actually differs** — which here
is one number, power draw. This is the same shape as H1c grouping missiles under
their rack.

**And answer Sleven's actual question on the page.** "Flight blade" appears with
no explanation anywhere. The hover copy this project already writes for stat
tiles applies: *a part that changes how the ship handles — PHB tunes for
manoeuvrability, TSB for top speed.*

    CONTROL: report whether a hull-constraining field exists, by name, with the
    count of blades it admits for the C8R Pisces. Assert the rendered list length
    matches that count.
    NEGATIVE: if no such field exists, assert the list is GROUPED - distinct
    signatures shown, identical ones collapsed with a count - and that the total
    still accounts for all 238.

## E10 — "Best" is a judgement and this site does not make judgements

**Sleven, 2026-08-23:** *"there's an option that says Best. That needs to go. We
do not determine what is best. Ever. We just provide the information. The user
determines what's best."*

**Remove `Best`.** It is the one control on the page that tells a visitor what to
think, and it sits inside a page whose entire character is stating what is known
and how well it is known.

**Replace the sort row with four factual sorts**, each named for the measurement
it performs, not for a verdict:

    MOST <stat>    the port's own headline figure, descending - "Most damage" on
                   a gun, "Most shielding" on a shield generator. Factual: it
                   says what it sorts by.
    COOLEST        lowest IR. Heat. What a heat-seeker sees.
    QUIETEST       lowest EM. Electronics. What a radar sees.
    LIGHTEST       lowest mass.

**Splitting IR from EM is Sleven's own ask** — *"what about something for the EM?
Because we are able to track that with different components putting out different
types of signals."* They are different signatures that matter to different
players: somebody dodging missiles cares about IR, somebody avoiding detection
cares about EM. **Today `Quietest` sums them, which serves neither.**

### EVERY SORT TOGGLES, AND THE BUTTON SAYS WHAT THE NEXT CLICK WILL DO

**Sleven, 2026-08-23:** *"If they click the button twice, it takes it to the
opposite. When you click Quietest, it brings the quietest one to the top. That
button should switch to Loudest. So when you click it again, it takes you to the
loudest one. It flips the stack, and then the button turns back to Quietest.
Same for Lightest, and any other like that."*

    Coolest   <-> Hottest        IR
    Quietest  <-> Loudest        EM
    Lightest  <-> Heaviest       mass
    Most <x>  <-> Least <x>      the port's headline figure

**The label shows what the NEXT click will do, not what is currently shown.**
That is Sleven's spec and it is unambiguous; implement exactly that.

**APPROVED BY SLEVEN 2026-08-23 after driving a working example** of both
behaviours side by side (`sort-toggle-example.html`, delivered in chat). His
words: *"Yeah. I like that. We can go with your way."* **This is a requirement,
not advice.**

A button that renames itself leaves somebody unsure which state they are in — they read "Loudest" and cannot tell whether they are looking at
loudest or about to get it. **So the current state must be visible without
reading the button:** a direction arrow on the active sort, and a list whose top
row is self-evidently the extreme it claims. **The button says what happens next;
something else says what is happening now.** Both, or the control is a riddle.

**This also disposes of `Best` cleanly rather than just deleting it.** `Most
damage` / `Least damage` are two factual sorts on one axis. Neither is a verdict,
and between them they cover what `Best` was reaching for without the site telling
anybody what to want.

    CONTROL: assert the string "Best" appears nowhere in the rendered page.
    CONTROL: assert Coolest orders by IR alone and Quietest by EM alone, on a
    port whose parts rank DIFFERENTLY under the two - if no such port exists the
    check proves nothing, so name the port used.
    CONTROL: click a sort, assert the order; click the SAME control again, assert
    the order is exactly REVERSED and the label has flipped.
    NEGATIVE, load-bearing: assert a THIRD click returns to the first order. A
    build that reverses once and then sticks passes a single-toggle check.

---

## E11 — THE LABELS DO NOT FOLLOW THE SHIP. Two lines apart in the same file.

**Sleven, 2026-08-23, driving the deployed page:** *"They did pop up, but they do
not stay with the ship. I can move the ship around and they just float there...
They're supposed to be attached to the hardpoints. So no matter how you look at
it, no matter how you spin the ship, you can see what name of what part is
attached at what hardpoint."*

**Confirmed in source, and it is one line:**

    loadout.src.html:2439    v.onFrame = renderMarkers;
    loadout.src.html:3164    ... renderMarkers(); renderLabels(); ...

**`renderMarkers` is in the animation loop. `renderLabels` is called once, from
`renderAll`.** So markers track the camera every frame and labels are placed once
and abandoned. Rotate the hull and the ship leaves; the labels stay exactly where
they were, leader stubs pointing at nothing.

**This is the 782-silent-markers shape again:** the code does exactly what it was
told, and H1b's control asserted the labels EXISTED and did not overlap. **It
never asserted they stayed attached to anything.**

### E11a — THE FIX, AND THE TRAP IN IT

**Do NOT simply move `renderLabels()` into `onFrame`.** `layoutLabels()` is a
collision solver — six candidate rings per label, nearest-first, first
non-overlapping position wins. That is what got the Perseus from 15 placed to 26
with zero overlaps. **Running that search 60 times a second on 35 labels will
cost the framerate on exactly the hulls that need it most.**

**Split it in two:**

1. **Every frame, cheap:** the label's anchor and its leader line follow the
   marker. This is the same projection `renderMarkers` already performs — reuse
   it rather than projecting twice.
2. **Throttled, or on camera settle:** the collision solve that decides WHICH
   candidate position each label takes. The arrangement does not need to change
   60 times a second; it needs to be correct when the person stops moving.

**A label must never be visually detached from its marker, at any moment,
including mid-drag.** If a throttled re-solve would leave a label stale for a few
frames, the leader line still has to reach its marker — the line is the promise,
the ring position is the tidiness.

    CONTROL: rotate the camera by a known amount and assert every label's leader
    line still terminates within its marker's radius. Assert it DURING the
    movement, not only after it settles.
    NEGATIVE CONTROL, load-bearing: run the same check against the CURRENT build
    and assert it FAILS. It fails today on every hull, so a check that passes now
    is measuring nothing.
    CONTROL: measure frame time on the Perseus (35 markers) with labels on.
    Report it. If the solve is in the frame loop, this is where it shows.

### E11b — Labels still absent until a click, on some hulls

**E8 was recorded done and the symptom persists.** Sleven, on the Anvil C8R
Pisces Rescue: *"as soon as I loaded in, nothing was there. I clicked one of the
hardpoints and they popped up."* Four hardpoints — far below the 14 threshold, so
they should be on at load.

**Find out which path skips them** — likely a first render that runs before
marker positions exist, or a path where no selection is set. **Say which it was**;
the answer decides whether E8's control was wrong or its coverage was.

    CONTROL: load a hull cold, with no interaction of any kind, and assert labels
    are in the DOM and visible. Do it on a hull that has never been selected.

---

## E12 — Ships rendering as hollow shells. It is face winding, and it is a trade from the white-out fix.

**Sleven, 2026-08-23, on the Crusader Mercury Star Runner:** *"The ship looks so
weird... It looks like it's just a shell. I know it's supposed to be a hologram,
but this one's missing the whole front thing."* **Reports the Origin 600i the
same.**

### The cause, in two lines of `cc_viewer.js`

    571   side: THREE.FrontSide, transparent: false, depthWrite: true
    575   side: THREE.FrontSide, transparent: false, depthWrite: true

**Both solid passes cull back faces.** Any triangle whose winding is reversed is
therefore INVISIBLE — you look straight through the hull and see the inside of
the far side, which is exactly what a missing nose looks like.

**This is a trade made by the white-out fix and it was the right trade.**
`DoubleSide` plus additive blending took a 353,731-vertex hull to 63.7% pure
white pixels. `FrontSide` fixed that. **It also exposed every winding error in
the model set, which `DoubleSide` had been hiding.**

**And the model set is exactly where you would expect winding errors.** These are
235 community models from a Hugging Face dataset — *"Star Citizen Fan Assets
(Unofficial)"*, per `sc-ships/README.md` — that have been through extraction,
glTF conversion, a rescale pass and Draco compression. **Nobody in that chain
guaranteed consistent winding, and nothing has ever checked it.**

### DO NOT FIX THIS BY GOING BACK TO DoubleSide

That reintroduces the white-out, which was measured and is worse. **Fix the data,
once, offline** — the same principle as every other derived dataset here.

**1. MEASURE IT ACROSS ALL 235 FIRST.** For each mesh, compute the fraction of
triangles whose face normal points AWAY from the hull's centroid. A correctly
wound closed mesh is near 100%. **Report the distribution and name every model
below a threshold.** This turns "some ships look wrong" into a list.

**2. Then flip the winding on the affected triangles at build time**, and rebuild
those models. It is a data defect; repair it in the data.

**3. Where a mesh is not closed** — an open shell with genuinely no inside — flipping
is meaningless and `FrontSide` will always show a hole from one angle. **Those
must be identified and reported separately, not silently left in the same
bucket.**

    CONTROL: report outward-facing triangle fraction for all 235 models, before
    and after. Assert the Mercury Star Runner and the Origin 600i are both in the
    "below threshold" list BEFORE the fix - if they are not, the diagnosis is
    wrong and stop.
    NEGATIVE CONTROL, load-bearing: assert a model that renders correctly today
    is NOT modified. A pass that flips everything trades one broken set for
    another.
    CONTROL: after the fix, re-run E7b's white-pixel check. The pre-pass and
    FrontSide stay; this must not reintroduce the white-out.

**Sleven is checking more hulls by eye. The measurement above should predict
which ones he finds** — that is the real test of the diagnosis, and it is
available before he reports a single further ship.

---

## E12 IS WITHDRAWN. THE DIAGNOSIS WAS WRONG. DO NOT IMPLEMENT IT.

**Sleven's own screenshots refute it, and they were available before any work
started.** He captured the Crusader Mercury Star Runner in all six styles. In
**Lit hull** the ship renders as a complete, solid, closed object — nose
present, no holes, no see-through. Same geometry, same `THREE.FrontSide`, same
depth pre-pass, same Draco file.

**If the winding were reversed, Lit hull would be holed too. It is not.** The
geometry is fine. Nothing in the model set needs flipping. **Do not run the
winding measurement, do not modify a single model.**

The cause is in the shader, and it is arithmetic. See E13.

---

## E13 — The holo shader renders the hull at roughly 9% brightness. That is the whole defect.

**Sleven, 2026-08-23:** *"I'm staring at the front of the ship, and I'm looking
directly into the ship, I can't tell where the front is. I don't know where the
curvature is... I can see through the bottom, but I can see the top layer that I
can see through on the top."*

He is describing a surface that is nearly black, not a surface that is missing.

### The two shaders, side by side

`CC_HOLO_FRAG` (drives `solid`, and `solidlines` — **the default style**):

    c = uColor*(0.040 + ndl*0.20 + ndl2*0.055 + fres*(1.15*uGlow/0.55) + band*0.55)

`CC_HOLO_FRAG_HULL` (drives `hull`, the one that reads correctly):

    c = base*(0.34 + d1*0.86 + d2*0.34 + d3*0.14) + uColor*(spec*0.95 + fres*0.30)

| term | `solid` | `hull` | ratio |
|---|---|---|---|
| ambient | 0.040 | 0.34 | **8.5x** |
| key diffuse | 0.20 | 0.86 | **4.3x** |
| fill | 0.055 | 0.34 | 6.2x |
| bounce | none | 0.14 | — |
| specular | none | 0.95 | — |

**A camera-facing surface gets the LOWEST fresnel** — `fres = pow(1.0 -
abs(dot(N,V)), 2.3)` goes to zero head-on, by construction. So on the default
style the front of the ship lands at roughly `0.040 + ndl*0.20`, which for a
surface not aimed at the key light is about **0.09 — nine percent of the
colour.** Meanwhile `edges` draws at `opacity 0.44` with `AdditiveBlending`.

**The lines are five times brighter than the surface they trace.** That is why
the ship reads as a see-through wireframe, and why the head-on view carries the
least information of any angle. It is not a hole. It is an unlit hull.

### RSI ships this exact distinction and we got the default backwards

RSI's viewer offers three render types: **Default, X-Ray, Wireframe.** Their
Default is opaque and diffuse-lit — the ship blocks the grid, top surfaces are
bright, undersides are dark, and panel lines are drawn *over* a lit solid.
X-Ray is the see-through one. **Opaque is what they open on; transparent is the
opt-in.**

We ship six styles and open on `solidlines`. **Every style we open on is in the
X-Ray family.** We own exactly one shader that reads as a solid object — `hull`
— and it is desaturated grey, sits fourth in the list, and no one lands on it.

### THE FIX — raise the diffuse terms on `CC_HOLO_FRAG`. Do not touch uGlow.

The target is RSI's Default rendered in our colour: an opaque, diffuse-lit hull
that still carries the holo tint and the panel lines.

**1. Raise ambient and diffuse on `CC_HOLO_FRAG` toward `CC_HOLO_FRAG_HULL`'s
values.** Report the numbers chosen. The specific values are yours to tune, but
the head-on surface must land well clear of 0.09.

**2. Keep `uGlow` where it is.** 0.04 is Sleven's own number from E7b and the
captures he approved run at it. The rim is not the problem.

**3. Give the edge material headroom to sit on a brighter surface.** At
`opacity 0.44` additive over a lit hull the lines may bloom. Adjust and say
what you adjusted.

**4. Leave `panel`, `wire` and `points` alone.** They are the X-Ray family and
they are correct as they are. This changes what the page OPENS on, not what it
offers.

### WHY RAISING DIFFUSE IS NOT THE WHITE-OUT AGAIN

The obvious objection is that brightness was already tried and measured at
63.7% pure white pixels. **That measurement was of `DoubleSide` plus
`AdditiveBlending`** — every overlapping surface accumulating into the same
pixel. Diffuse on an opaque `FrontSide` pass writes each pixel once from one
surface and clamps at 1.0. **It cannot accumulate. It is a different lever.**

    CONTROL, load-bearing: re-run E7b's white-pixel check on the Mercury Star
    Runner and the Origin 600i after the change. Assert the pure-white fraction
    stays below E7b's threshold. If diffuse whites out, the reasoning above is
    wrong and stop.
    CONTROL: report mean rendered luminance of hull pixels BEFORE and AFTER, on
    a head-on view of the Mercury. Before must be low - if the before number is
    already high, this diagnosis is wrong and stop.
    NEGATIVE CONTROL, load-bearing: capture Lit hull before and after and
    assert it is UNCHANGED. Only CC_HOLO_FRAG moves. If Lit hull shifts, the
    edit landed in the wrong shader.

---

## E14 — Ships that claim a 3D model and render nothing. Enumerate them; do not let Sleven click 235 pages.

**Sleven, 2026-08-23:** *"there's a bunch of ships that say they have three d
models. And when I click on them, nothing came in. So I'm gonna literally have
to go through every single thing and check every single ship."*

**He should not.** The manifest is machine-readable and the failure is
machine-detectable. A person clicking 235 pages will miss some, cannot say which
of several failure modes each was, and has to do it again after every rebuild.

**Produce a list.** For every ship whose page claims a model, verify in one
build-time pass:

1. The file named in the manifest **exists** at the served path.
2. It **decodes** — Draco included.
3. It yields a mesh with **non-zero vertex count** and a **finite, non-zero
   bounding box**.

**Report each failure with which of the three it failed**, because they are
three different bugs: a broken path, a corrupt file, and an empty scene do not
share a fix. Report the totals: how many ships claim a model, how many pass,
how many fail at each stage.

    CONTROL, load-bearing: the check must currently FAIL on at least one ship,
    because Sleven has already seen several. A pass rate of 100% means the
    check is not measuring what he is seeing - say so and stop.
    CONTROL: state how the list of "ships that claim a model" was built, and
    the count. If that count is not close to 235, the enumeration is wrong
    before the check even runs.

---

## E13a — The holo shaders bypass tone mapping and sRGB encoding. Two consequences, one of them changes E13's risk.

**CIC asked whether its luminance figures should be linearised before becoming
the before-half of E13's before/after. The answer is NO, and the reason matters
more than the question.**

### The pixel bytes are the shader's raw output. Nothing transforms them.

`cc_viewer.js:379-381` sets `outputEncoding = sRGBEncoding`, `toneMapping =
ACESFilmicToneMapping` and an exposure. **None of it reaches `CC_HOLO_FRAG` or
`CC_HOLO_FRAG_HULL`.**

In the vendored three build, `tonemapping_fragment` and `encodings_fragment`
exist ONLY as `#include` directives inside three's own built-in shader sources
— meshphysical, meshlambert, points, sprite, background and the rest. **A
hand-written ShaderMaterial receives neither unless its source includes them,
and neither of ours contains a single `#include`.**

**CIC's own null control proves it independently.** `scene.background` is
`0x050a12` and CIC measured the panel background as bit-exact **RGB(5,10,18)**,
90.86% of pixels, identical at all four corners. Under sRGB encoding, 5/255
would have emerged near byte 62. **The transfer function is identity.**

So a shader value of 0.09 lands at byte 23, and CIC's Mercury mean of 53.50 is
0.21 in shader units. **Do not linearise. Comparing linearised numbers against
these shaders would introduce an error, not remove one.**

### CONSEQUENCE 1 — the comment at line 377 is wrong and must be corrected

    /* Without tone mapping, anything bright clips straight to pure white and
       the shape disappears into a silhouette. Half of the white-blob fix. */

**ACES was never touching the holo materials.** The white-out was fixed by
`FrontSide` plus the depth pre-pass alone. Fix the comment when you touch this
file — it is the kind of wrong note that gets believed later.

### CONSEQUENCE 2 — E13 HAS NO HIGHLIGHT ROLLOFF. THIS RAISES THE STAKES.

Anyone raising diffuse would reasonably assume ACES will roll off the top end.
**It will not.** Output hard-clips at 1.0. Every unit of diffuse added above
clip is lost to flat white, which is the exact failure `FrontSide` was brought
in to end.

### AND THE TWO SHIPS BRACKET THE PROBLEM — TUNE AGAINST THE BRIGHT ONE

CIC's baseline, fraction of hull pixels above 90% luminance:

| ship | mean luminance | above 90% |
|---|---|---|
| Crusader Mercury Star Runner | 53.50 | **0.314%** |
| Origin 600i Touring | 91.75 | **7.255%** |

**Twenty-three times apart, on the same shader and the same settings.** The
600i is already clipping on 7% of its hull before anything is raised.

**Tuning constants that fix the Mercury without checking the 600i will white out
the 600i.** Both ships are the test, and the 600i is the binding one.

    CONTROL, load-bearing: report the above-90% fraction for BOTH ships after
    the change. The Mercury must rise off 0.314%. The 600i must NOT rise
    materially above 7.255%. If satisfying one breaks the other, a single pair
    of constants is insufficient - SAY SO rather than picking a ship to please.

### Metrics retired, so nobody re-runs them

- **Edge-versus-interior split.** Built to test C1's fresnel opinion, which is
  superseded by the shader arithmetic. CIC normalised it against base rate and
  found 1.09x and 1.20x — near chance. **The null result threatens nothing.**
  The raw "81% interior" figure is an artefact of the edge band being 15-17% of
  pixels and must not be quoted.
- **Line density.** Built for the cancelled A-vs-B comparison. It is also
  actively misleading before/after: a fixed L>=128 threshold reports more lines
  purely because the surface got brighter. **Do not carry it forward.**

---

## E13b — SCOPE CORRECTION. E13 is verified across the whole fleet, not across two ships.

**Sleven, 2026-08-23:** *"I found these problems on two ships that I showed you.
But I do know they are on a lot of other ships. Even the ships that I was like,
okay, yeah, this looks good... I still found that they had the same slight
issues... all of the ships need to be fixed, not just a couple."*

**He is right and E13 as written was scoped too narrow.** Two ships was the
right sample to TUNE against. It is the wrong sample to VERIFY against, and the
distinction was mine to make and I did not make it.

**Every hull runs the same shader with the same constants.** The defect is
therefore uniform across the entire model set by construction — which is also
why the ships he thought looked acceptable still felt slightly wrong. **There is
no per-ship work here. There is one change and one fleet-wide measurement.**

### The measurement is scripted and headless. Sleven is not the instrument.

CIC has proven the method end to end: `readPixels` inside a rAF callback, grid
off, markers are DOM overlays and never enter the buffer, background bit-exact
at RGB(5,10,18) so the mask is `R!==5||G!==10||B!==18` with no tolerance, and
the scene is bit-static across frames. **That is a loop, not a person clicking.**

Run it over every hull that has a model, before and after, and report per ship:
hull pixel count, mean luminance, p95, and fraction above 90% luminance.

    CONTROL, load-bearing: the BEFORE run must show the defect fleet-wide, not
    on two hulls. Report how many hulls fall below the Mercury's mean of 53.50
    and how many exceed the 600i's 7.255% above-90%. If the fleet does not
    straddle those two, the two-ship sample was unrepresentative and the tuning
    constants derived from it are wrong - say so and stop.
    CONTROL: report the AFTER distribution, not an average. An average hides
    the hull that went white.
    NEGATIVE CONTROL, load-bearing: Lit hull unchanged on every hull measured,
    not on a sample.

### AND IT BECOMES A STANDING AUDITOR, NOT A ONE-OFF SCRIPT

Sleven: *"plus the ones that are coming."* A script run once cannot answer that.

**This is the auditor pattern the project already decided on** — flag only,
never auto-fix, write findings to the shared results table. A hull whose render
falls outside the fleet band gets flagged on the build that introduces it,
whether that is a new ship, a re-export, or a shader edit nobody expected to
have a visual effect. **Same for E14's model-loads check: one auditor, run every
build, covering both questions.**

Building it as a one-off costs the same today and costs the whole thing again in
six months.

### THE SHIP COUNT IS NOT ESTABLISHED AND NOBODY SHOULD QUOTE ONE

Numbers currently in circulation across this repo: 235 hulls, 243 entries under
`sc-ships/`, 316 ships in the scunpacked snapshot, 159 hulls, 167 ships.
`LATEST_HANDOFF.md` already flags that two of these disagree and that **nobody
has established why.** Sleven says 254.

**E14's enumeration settles this as a side effect and should be treated as its
primary output**, not a by-product: the authoritative count of ships, of ships
claiming a model, and of models that actually load. Until that runs, any number
in a report is somebody's guess.
