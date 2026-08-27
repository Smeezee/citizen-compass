# ORDER — Every ship is a hologram. The look becomes the product.

    from    C1
    date    2026-08-22
    for     Code
    status  RUN CONTINUOUSLY. H1 through H9, in order, no decision gates.
    lives   docs/PROTOTYPE_holographic-ship-viewer.md is the LIVING document
            for this feature. Fold findings back into its section 3.

---

## The decision

**Sleven, 2026-08-22:**

> *"The way that view needs to be enjoyable to look at. This is a key feature of
> our website over everybody else's, and it needs to look good... I don't see why
> we can't make all of our ships look like this. That's a perfect view. I don't
> ever have to worry about the paint and trying to get that right if we can make
> them look the way these look."*

**The holographic render style is now the ship page's primary presentation, for
every ship, not a prototype for four.**

**And the second half of that sentence is the important half.** The texture
problem is not solved by finding textures — **it is dissolved by not needing
them.** Our 235 models have no textures. RSI's have none. Fleetyards' materials
are not ours to take. **A hologram does not want a texture; the absence of one is
the material.** C3 established this on 2026-08-08 in
`FINDING_hologram-display-concept-2026-08-08.md` and Sleven has now arrived at it
independently and made it the direction.

---

## The correction that changes the whole shape of this job

**Sleven's framing was that RSI's models unblock this. They do not, and nothing
does. It was never blocked.**

CIC's live capture settled what RSI serves: OpenCTM, one mesh, exterior hull
only, no node hierarchy, **zero per-ship textures** — the same bare geometry we
already hold, and behind the one path `robots.txt` disallows.

**Measured on this machine, right now:**

    316   ships in the data
    235   .glb model FILES on disk
    201   ships wired to a model
    115   ships rendering NOTHING
     40   model files ON DISK, wired to no ship at all

**Forty models we already own are sitting in `testing/_deploy/models/` pointing
at nobody.** Including `Liberator.glb`, `Carrack_w_C8X.glb`, `Kraken.glb`,
`Galaxy.glb`, `Nautilus.glb`, `Orion.glb`, `Pioneer.glb`, `Endeavor.glb`,
`Hull_D.glb`, `Hull_E.glb`.

**And several of them match ships on the missing list by eye:**

    Caterpillar_Pirate_Edition.glb              Drake Caterpillar Pirate
    Hammerhead_Best_In_Show_Edition_2949.glb    Aegis Hammerhead 2949 BIS
    Nox_Kue.glb                                 Aopoa Nox Kue
    Dragonfly_Yellowjacket.glb                  Drake Dragonfly Yellowjacket
    F7C-M_Super_Hornet_Heartseeker_Mk_I.glb     Anvil F7C-M Hornet Heartseeker Mk I
    Carrack_w_C8X.glb                           Anvil Carrack

**This is the same defect that hid the Ares Inferno for a week: a name-matching
failure, not a missing asset.**

**A THIRD library exists and has never been merged.** The prototype renders the
Drake Cutlass Black and the RSI Constellation Aquila from **Fan Kit `.ctm`** —
and the live page has **no model for either of them**. Fourteen hero ships, one
per manufacturer, already extracted at `Downloads\Fankit_2025_11_19\`.

**So: two model libraries, neither complete, never merged, and forty files
orphaned inside one of them. Finish that before anyone talks to CIG.**

---

## H1 — Port the holographic render into the live viewer

The look is the deliverable. `cc_viewer.js` gets the prototype's rendering.

### THE EXACT LOOK, PINNED BY SLEVEN 2026-08-23

He sent one capture and said: *"this is what I'm talking about, this is how I
want all of the ships, this is the key to it all."*

**The Aegis Sabre, and the combination is specific — do not approximate it:**

    STYLE    Solid + lines      not Panel lines, not Wireframe
    COLOUR   BLUE / cyan        CHANGED 2026-08-23 - see below
    LABELS   All labels ON      every hardpoint carries a leader line
    VIEW     grid on, lit disc, scanlines off

**COLOUR CORRECTION, Sleven, 2026-08-23:** *"our default should not be yellow. It
should be blue."* **Amber is withdrawn as the default.** C1 pinned it from the
amber Sabre capture; Sleven has now seen all five rendered on real hulls and
chosen blue. **Blue/cyan is the default; amber stays as one of the five
controls.**

**`Solid + lines` in amber with every label showing is THE default state of the
ship page.** The other styles and colours remain available as controls; this is
what a visitor sees before touching anything.

**THE PROTOTYPE'S SOURCE IS NOW IN THE REPO AND YOU PORT FROM IT, NOT FROM
SCREENSHOTS.** `docs/holo-viewer-prototype-src/` — `viewer.js` (60,670 B),
`viewer.css` (5,725 B), `viewer.html`, plus a README mapping every item in this
order to the function that implements it. The 12.5 MB of inline model blobs and
the 657 KB of vendored three.js are stripped; what is left is 66 KB and it is all
ours. **Read `README.md` there before writing a line of H1.**

**Take from the prototype, exactly:**

- The **stage**: dark field, the lit disc under the hull, the grid.
- **ALL SIX render styles. C1's "three, not six" trim is OVERTURNED by Sleven,
  2026-08-23**, in his own words: *"I liked the ability from the prototype to
  change the shading and all that stuff... the style, the panel lines, the solid
  plus lines, the solid holo, wireframe, points, lit hull."* `Solid + lines` is
  the default; the other five are controls.
- **The five colours stay as a control, and amber is the default.**
- **The depth-only pre-pass and `FrontSide`.** Non-negotiable and the reason is
  measured: `DoubleSide` plus additive blending with no pre-pass took a
  353,731-vertex mesh to **63.7% pure white pixels**. Leave the pre-pass out and
  it happens again.

**TAKE THE THREE SLIDERS. C1's "do not take them" instruction is OVERTURNED by
Sleven, 2026-08-23** — *"being able to change the line density, being able to
change the colour... I like this."* Line intensity, line detail and glow are
controls, not hard-coded values.

**C1 was wrong twice in the same paragraph and the reason is worth keeping:** the
argument was that a visitor should enjoy the page, not tune it. **Sleven's point
is that on this page the tuning IS the enjoyment** — different people want to
look at a ship differently, and being able to change it is the feature. A
developer's tuning panel and a visitor's controls look identical in a
screenshot; the difference is whether anyone wants to touch them, and he does.

    CONTROL: render a real hull offscreen in each of the three styles and assert
    pure-white pixel share is BELOW 5% in all three.
    NEGATIVE CONTROL, load-bearing: build one frame with the pre-pass disabled
    and assert it FAILS that threshold. Without it, "the pre-pass works" also
    passes on a build that never renders.

## H1f — THE CONTROL PANEL SHIPS. All of it. This is what the first pass missed.

**Sleven drove the deployed page 2026-08-23:** *"It looks good for the first
pass, but it's definitely not where I want it... I don't see that."*

**What landed: the renderer.** White line-work on a dark field, the grid, the
disc, markers where a hull has them, the honest note, and E1's message where it
does not. That part is right and is not to be touched.

**What did not land: everything a person can press.** Measured against the
prototype, the deployed page is missing:

    STYLE       panel lines / solid + lines / solid holo / lit hull /
                wireframe / points          - ALL SIX, none present
    COLOUR      five swatches               - none present, and the hull
                                              renders WHITE where amber is the
                                              pinned default
    SLIDERS     line intensity / line detail / glow    - none present
    VIEW        auto-spin / grid / scanlines / hide back faces / loadout list
    HARDPOINTS  show markers / guns / racks / CM / turret guns / all labels /
                mirror L/R / auto-frame
    LABELS      H1b - no leader lines, no names on the model at all

**Scanlines specifically:** *"I kinda like... we never see the scanlines."* They
are in the prototype, they are not on the page, and he wants them available.

### Where it goes, because the page must still fit one screen

P7 measured the ship page at 1080 of 1080 and 768 of 768. **The prototype's panel
is a permanent right-hand column and this page has no room for one** — the right
column is `EVERYTHING THAT MOVES`.

**So: a collapsible control panel anchored to the STAGE, closed by default,
opening over the model.** One control in the corner of the viewer opens it,
Escape and a click outside close it. It costs zero page height because it floats
over the stage, exactly as B3's picker panel already does.

**This is progressive disclosure, which is this project's own standing rule** —
the page opens at its simplest true state and every layer is opt-in. A visitor
who wants a picture of a ship gets one. A visitor who wants to change how it
looks presses one thing and gets everything.

### H1f-2 — THE SETTINGS FOLLOW THE PERSON FROM SHIP TO SHIP

**Sleven, 2026-08-23, after driving two ships:** *"when you select one setup, it
should remember that, the whole time you're on the page."*

**It does not today.** He set Solid holo on the C1 Spirit; the next ship came
back at the default. **Every control in the panel persists** — style, colour, all
three sliders, and every view toggle — across ship changes, for the whole visit.

**PERSIST IT INDEFINITELY. Sleven, 2026-08-23, asked directly:** *"as long as
possible, really... I'd hate to have to come in after a couple of days and have
to redo it. We can make it to where it stays once a user sets it. That'd be
preferred."*

**Once set, it stays until the person changes it.** Not for a session, not for a
day. It survives closing the browser, restarting the machine, and weeks between
visits. Restore on load; fall back cleanly to the defaults when nothing is
stored.

**State the real limits honestly rather than implying more than we deliver.**
This site has no accounts, so the setting lives in the browser. That means it is
**per-browser and per-device** — set on the desktop, it does not follow to a
phone — and it is lost if somebody clears their site data or browses privately.
**Do not build an account system to fix that.** The failure mode is mild: the
page comes back at the defaults, which are good defaults.

**It does raise the stakes on E6.** If a person loses their settings and cannot
find the panel again, they cannot get back to what they had. **The panel being
discoverable is what makes the persistence safe to rely on.**

**The one thing that does NOT persist is a per-ship accident** — camera angle and
zoom reset per ship, because they are about that hull, not about how the person
likes to look at things.

    CONTROL: set a non-default style, colour and slider value, change ship, and
    assert all three survived. Then reload the page and assert they survived
    that too.
    NEGATIVE CONTROL: with nothing stored, assert the page opens on the DEFAULTS
    - Solid + lines, blue. A build that persists nothing and a build that
    persists everything both pass a survival check alone; only the fallback
    assertion separates them.

### Rules

- **Port from `docs/holo-viewer-prototype-src/viewer.js`.** All of this exists
  and works. Reimplementing it from the screenshots is how the first pass ended
  up with a renderer and no controls.
- **Amber is the default hull colour**, not white. That was pinned on 2026-08-23
  and the deployed page does not honour it.
- **`Solid + lines` is the default style.**
- **Every control must work in every combination.** Six styles x five colours is
  thirty looks; the marker coding of H1e must stay legible in all of them, which
  is why H1e asks for shape as well as colour.

    CONTROL: drive the served page. Assert all six style controls exist, change
    the render, and that the change is OBSERVABLE - a render hash or pixel
    signature that differs per style, not merely that a class was set.
    Assert the five colours change the rendered colour.
    Assert each slider changes the render across its range.
    NEGATIVE CONTROL, load-bearing: assert that two DIFFERENT styles do not
    produce the same signature. Without it, a build where every button sets a
    class and nothing redraws passes every other assertion.
    CONTROL: page height at 1920x1080 and 1366x768 with the panel OPEN and
    CLOSED. Open must not exceed closed - it floats, it does not push.

## H1g — THE CONTROLS ARE AN ACCESSIBILITY FEATURE, AND THE PAGE DOES NOT DIM

**Sleven, 2026-08-23, and this REPLACES the reason recorded in H1f.** The
controls were written up as *"on this page the tuning is the enjoyment."* That is
true and it is not the requirement. His own words:

> *"The aim is to make the page something that if they wanna have it up on a
> second or third monitor... when we adjust the colouring of the page, it sets
> the tone of what they're doing, so it's easier on their eyes. I've played
> extensively in the dark, and I always hated having a page that I couldn't force
> to dark mode... trying to do something in a game."*

> *"What if people are colourblind and certain colours we use, they're not able
> to see? It's gonna look horrible."*

**The use case is a second monitor, in a dark room, for hours, beside a running
game.** That generates testable criteria; "enjoyment" does not.

### H1g-1 — THE WHOLE PAGE DIMS, NOT THE MODEL

**What shipped in H1f only affects the 3D model.** The stat tiles, the component
list, the headings and the chrome are unchanged. **A dimmed hologram beside a
bright white panel does not solve the problem** — the ship gets darker and the
thing burning his eyes stays exactly as bright.

**One page-level control, not six.** Nobody should tune five sliders to stop a
page hurting.

- **Three named presets, one click each: `Day`, `Night`, `Blackout`.** Presets
  are what a person reaches for mid-flight when they do not want to fiddle.
- **A fine slider underneath**, for anyone who wants exactly their own level.
- **It dims EVERYTHING together** — text, tiles, headings, borders, the header
  bar, the model. Not the background alone.

    CONTROL: render the page at each preset and assert the BRIGHTEST rendered
    element is below that preset's luminance ceiling. Assert the ceiling, not
    that a class was set - dimming the ground while a white number stays at full
    is the exact failure this catches.
    NEGATIVE: at `Day`, assert the page is NOT below the Night ceiling. A build
    that renders everything dark always would otherwise pass.

### H1g-2 — CONTRAST HAS A FLOOR, EVEN AT BLACKOUT

A dark page with grey-on-grey text is a different injury. **Every preset must
still meet a text-contrast minimum against its own background.** Dimming reduces
absolute brightness; it must not reduce legibility.

    CONTROL: at EVERY preset, assert every text/background pair meets the
    contrast floor. The Blackout preset is the load-bearing case.

### H1g-3 — COLOURBLINDNESS: FIX THE DEFAULT FIRST, THEN ALLOW THE CHOICE

**Sleven's instinct is right and it is the second half of the answer. This is the
first half, and it is the more important one:**

**A person cannot configure their way out of a problem they cannot see.** If a
marker's kind is conveyed only by being orange rather than pink, somebody with
red-green colour vision deficiency does not know what they are missing, so no
colour picker helps them. **The primary rule is that colour must never be the
only carrier of meaning.** H1e already requires shape alongside colour on
markers; this extends it to the whole page.

**The default palette has a real collision, measured from the deployed
`loadout.html`:**

    #FF8A00 / #FF6B00   orange - headings, CIG badges, accents
    #8FE3C8             mint green - the computed stat numbers
    #FF6B6B             red - warnings

**Orange against mint-green is the classic deuteranopia/protanopia failure**, and
those two carry the most meaning on the ship page — orange marks what came from
CIG, green marks what we computed. **Red-green deficiency affects roughly one man
in twelve.** Red `#FF6B6B` against orange `#FF8A00` is a second bad pair.

Required:

1. **Audit every place colour alone carries meaning** — the CIG / SUMMED badges,
   stock vs changed, marker kinds, warning states — and give each a second
   carrier: a shape, an icon, a text label, a border style.
2. **Fix the DEFAULT palette so it survives deuteranopia, protanopia and
   tritanopia simulation**, rather than relying on the user to repair it.
3. **THEN keep the colour controls**, as the escape hatch for anything the
   default still gets wrong for a given person.

    CONTROL: simulate deuteranopia, protanopia and tritanopia over a rendered
    page and assert every meaning-bearing pair remains distinguishable.
    NEGATIVE, load-bearing: run the simulation against the CURRENT palette and
    assert it FAILS on the orange/green pair. A check that passes on today's
    colours is measuring nothing.

### Why this item outranks most of the rest of this order

**This is the site's actual thesis, in Sleven's words:** *"make the experience of
all the different tools at one location and make it more user friendly."*

Every other Star Citizen tool starts from the same extracted game files, so the
data is nobody's advantage. **Being usable — in a dark room, on a second screen,
by somebody who cannot separate orange from green — is not something a competitor
copies from a data dump.** It is the differentiator, and it is the half nobody
else in that tools directory is doing.

## H1b — THE LABELS ARE THE FEATURE, and they are the answer to the marker problem

**This is the part of the capture that matters most and it is easy to miss.**
Every hardpoint carries a **leader line out to a label** naming both the part and
the port:

    CF-337 Panther Repeater
    Weapon left nose

    MSD-423 Missile Rack
    Weapon right missilerack

    Aegis Sabre - Decoy Launcher
    Countermeasure launcher right

**Why this changes the standing marker problem.** Sleven's complaint on the live
site was *"some of the hard points are not exact"*, and E3 of the errata is the
B5/B6 promotion that improves them. **But a derived position will never be
exact** — the exports are one welded mesh with no mount data, and
`AMENDS_extracted-textures-scope` established RSI's are no better. **A labelled
leader line is what makes an approximate position useful anyway.** A dot two
metres off that says *"CF-337 Panther Repeater · Weapon left nose"* is
informative. The same dot with no label is a guess the visitor cannot check.

**So labels are not decoration on top of the markers. They are the thing that
makes the whole derived-position approach honest and readable**, and they ship
with the default view rather than behind a toggle.

### The problem the prototype has NOT solved, and this order must

**Look at the capture: the labels collide.** On the Sabre's right side
`MSD-423 Missile Rack` and `CF-337 Panther Repeater` overlap into an unreadable
stack, and `Weapon left wing` is drawn twice on top of itself. **That is eight
hardpoints on a small fighter.**

    Aegis Sabre               8 hardpoints    already colliding
    RSI Polaris              24 markers
    RSI Perseus              35 markers
    Aegis Idris-M            24 crowded of its own

**A naive port of this to the fleet produces an unreadable mess on every large
ship**, and large ships are exactly where a person most needs to know what is
where.

Solve it properly:

- **Deconflict the LABELS, not the markers.** The marker stays on its derived
  position; the label may move and keep its leader line. Two things are being
  placed and only one of them is a claim about the hull.
- **A leader line must always visibly connect its label to its marker.** A label
  that has drifted free of its line is worse than no label.
- **Above a per-ship threshold, labels are a toggle rather than a default** — but
  the toggle must be obvious and the count stated, e.g. *"35 hardpoints · show
  all labels"*. Silently hiding them is the marker defect in a new costume.
- **Hover and selection always label**, whatever the toggle says.

    CONTROL: render the Sabre (8), the Polaris (24) and the Perseus (35) and
    assert ZERO label bounding-box overlaps on each.
    NEGATIVE CONTROL, load-bearing: disable the deconfliction and assert the
    Sabre FAILS - it collides today, so a check that passes with the feature off
    is measuring nothing.
    CONTROL: assert every rendered label's leader line terminates within its
    marker's radius.

## H1c — Missiles group under the rack that carries them

**Also in the capture, and it fixes something Sleven photographed on the live
site.** The prototype's list reads:

    MISSILES — CARRIED ON THE RACKS ABOVE
      2x  Arrester III Missile      S3
      2x  Thunderbolt III Missile   S3

**The live page renders the same information as eight separate rows** — his
Gladius Valiant capture shows `Pioneer I Missile · Missile 01 attach`,
`Missile 02 attach`, `Missile 03 attach`, `Missile 04 attach` and so on down the
column, each a full row, pushing everything else off screen.

**Group them, count them, and say they are carried on the racks above.** This is
the two-stage structure from the Erkul teardown (section 3d of the living
document): a rack goes in the hardpoint, missiles go in the rack. The list should
show that shape rather than flattening it.

**Do not group things that are NOT the same.** Four `Pioneer I Missile` on one
rack is `4x Pioneer I Missile`. Two Pioneers and two Thunderbolts is two lines.

    CONTROL: the Gladius Valiant's missile rows collapse to one line per distinct
    missile type with a correct count, and the counts sum to the ungrouped total.
    NEGATIVE: a ship carrying two DIFFERENT missiles must render two lines, not
    one line of six.

## H1d — CLICK A MARKER AND IT TELLS YOU WHAT IT IS, INCLUDING HOW SURE WE ARE

**Sleven, 2026-08-23, on the readout panel:** *"To be able to click on the actual
marker, it tells you what it is... like this last screenshot."*

**This panel is the single best thing in the prototype and it must be carried
across word for word in structure.** From his capture, the RSI Constellation
Aquila:

    Countermeasure launcher left top              PILOT-CONTROLLED      [x]

    COUNTERMEASURE
    Aegis Gladius - Decoy Launcher
    Size 2 - Aegis Dynamics
    hardpoint_cm_launcher_right_top

    Position 8.6 / 8.1 / 21.3 m from hull centre - DERIVED from the words
    "side, vert, part" in the mount name plus the hull shape. CIG's own data
    has this coordinate as null for all 53,651 mounts, so no one has the real
    one. Left and right assume a right-handed model; use Mirror L/R if your
    ship looks flipped.

**Why this is the best thing on the page.** Every other honest-gap statement this
project makes lives in a footer nobody reads. **This one appears at the moment a
person asks the question, attached to the specific thing they asked about, with
the actual number in metres.** It tells them what is fitted, who controls it, the
raw port id, where we think it sits, how we worked that out, that CIG themselves
do not have the answer, and which control to press if the handedness looks wrong.

**Carry every element. None of them is decoration:**

- the port's plain name, and **who controls it** (`PILOT-CONTROLLED` / gunner)
- the category, the part, its size and manufacturer
- **the raw port id** — a person cross-referencing our data against the game
  files needs the real string
- **the derived position in metres from hull centre**
- **the derivation, stated as derivation**, including that CIG's own coordinate
  is null for all 53,651 mounts
- **the handedness caveat and the name of the control that fixes it**

**This replaces the live page's `renderMarkerNote()` block**, which says the same
thing once, generically, at the bottom of the page, with no numbers in it. The
per-marker version is strictly better and the page-level block can go.

### A defect visible in that very panel

**The heading says `left top`. The port id says `right_top`.** Same panel, same
port, opposite sides. The panel's own text explains why — handedness is assumed,
Mirror L/R flips it — **but a label and an id that disagree on screen reads as a
bug regardless of the paragraph underneath.**

Fix: the human label and the raw id must agree, and **the mirror control must
flip BOTH or NEITHER.** If a mirrored view relabels `right` to `left`, it shows
the mirrored id too, or it shows the id unmirrored and says so.

    CONTROL: for every marker on a ship, assert the side word in the heading
    matches the side token in the port id, in both mirror states.
    NEGATIVE: flip the mirror and assert the assertion still holds - a check that
    only passes in one mirror state is testing half the feature.

## H1e — Markers are coded by kind, and the coding is part of the design

Visible across his captures and easy to lose in a port: **markers differ by shape
and colour according to what kind of hardpoint they are** — guns, missile racks,
countermeasures and turrets each read differently at a glance, before anything is
clicked or hovered.

**Keep it, and make it survive the two things that break this kind of coding:**

- **Never colour alone.** Shape must carry the same information, so a
  colourblind visitor and a dim monitor both work.
- **It must not collide with the amber default.** The hull is amber in the
  default view; a marker palette that reads well on cyan may vanish on amber.
  Check the coding in all five hull colours, not just the one it was designed in.

**This also pairs with the existing filter row** — `Guns`, `Racks`, `CM`,
`Turret guns` — which is how a person makes sense of a Polaris. Filters and
coding are the same idea at two scales; carry both.

    CONTROL: assert every marker kind is distinguishable by SHAPE with colour
    removed, and that each kind's marker meets a contrast floor against all five
    hull colours.

## H2 — Wire up the 40 orphan models

For each of the 40 `.glb` files referenced by no ship, resolve it to a ship or
state why it cannot be resolved.

**NO FUZZY MATCHING.** This is a standing rule and it has already produced four
confident wrong pairs — Dragonfly Black→Yellowjacket, E1 Spirit→C1 Spirit,
G12a→125a, Zeus MR→Zeus ES. **In the real pipeline that bolts the wrong hull onto
four ships and nothing catches it.**

Match on exact normalised name, then on `ClassName`, then **stop and list the
residue for a human.** A file nobody can place stays orphaned and is REPORTED,
never guessed.

    CONTROL: report resolved / unresolved counts. Assert every claimed pair
    agrees on MANUFACTURER as an independent field. A Drake file matched to an
    Aegis ship is wrong however good the name looked.

## H3 — Editions share their base hull, per the standing ruling

Most of the 115 are not missing models. They are **edition and paint variants**
— Wikelo War Special, Teach's Special, PYAM Exec, Best In Show, Alliance — of
hulls already on disk.

`DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14` already
rules this: **a shared hull is correct unless the ships differ in external
shape.** Apply it. An edition points at its base hull's model.

**Where an edition has its OWN file** — `Caterpillar_Pirate_Edition.glb`,
`Hammerhead_Best_In_Show_Edition_2949.glb`, `Nautilus_Solstice_Edition.glb` —
**that file wins over the base hull.** Somebody exported it separately for a
reason.

**The page must say which it is showing.** "Showing the base Caterpillar hull —
this edition differs in fitted components, not shape" is honest. Silently
rendering a different ship is not.

    CONTROL: assert every edition resolves to either its own file or a named base
    hull, and that the page states which.
    NEGATIVE: an edition WITH its own file must not fall through to the base.

## H4 — Merge the Fan Kit `.ctm` library

Fourteen hero models at `Downloads\Fankit_2025_11_19\02_HOLOVIEWERS\`, one per
manufacturer, **including the Cutlass Black and the Constellation Aquila that the
live page currently cannot render at all.**

Convert to `.glb` and wire them in **only where the ship has no model already**.
An existing model is not replaced by a Fan Kit one without a measured reason.

**Every one carries the CIG source tag** so `scripts/takedown.py --yes` catches
it — `cig_assets.json`, per A4 of the attribution order. **A Fan Kit model that
is not tagged is invisible to the off switch**, which is the one promise this
project made to CIG.

    CONTROL: assert each converted model is present in cig_assets.json AND that
    takedown.py removes it in a dry run.
    NEGATIVE: an untagged model must NOT be removed - proving the tag is what
    drives the removal, not a blanket wildcard.

## H5 — Count what is genuinely missing, and only then ask about RSI

After H2, H3 and H4, produce the real number: **ships that fly in game, are not
an edition of something we have, and have no geometry from any of the three
libraries.**

**That number is the only honest input to a decision about RSI's models**, and
until it exists nobody can say whether that conversation is worth having. It may
be small enough that the answer is no.

Report it as a list of ship names, not a count alone.

## H6 — The list beside the model takes the prototype's wording

The prototype's line is better than the live page's and is adopted verbatim in
shape:

    LEFT BODY WEAPON                                        506.7 dps
    Mantis GT-220 Gatling
    S3 · Gallenson Tactical Systems · on a gimbal · PILOT

And the heading that scopes the number: **`PILOT HARDPOINTS — 2104.6 TOTAL DPS`.**

**That heading is most of B7 solved.** A number scoped by the heading above it
beats a number footnoted below it. A turret-only ship gets a heading that says
so, and the eleven ships currently showing a misleading `0` stop being a problem.

## H7 — The empty case, taken word for word

The Cyclone's wording is adopted **verbatim**, not paraphrased:

    This hull carries no weapon mounts in the data — nothing to mark on it.

    COMPONENTS — MENU OVERLAY, NOT HULL-MOUNTED

**A ship with no guns must not look broken. It must look like a ship with no
guns.** This is the internal-versus-external ruling rendered without explanation,
and it is what B3 asks for. The prototype already solved it; do not re-solve it.

## H8 — `<= PLACEHOLDER =>` must never reach a screen

Visible in the prototype's captures 05 and 06, under CARGO GRID and ARMOR: the
literal string `<= PLACEHOLDER =>` renders where a part name belongs, beside a
real size badge and a real manufacturer.

**Show the row, and say the game files carry no name for this part.** Suppressing
it would hide a component that genuinely exists — the size and manufacturer are
real. This matches how the Cyclone's empty state already behaves.

    CONTROL: assert no rendered page contains the substring "PLACEHOLDER".
    NEGATIVE: a part WITH a real name still renders it - otherwise a build that
    blanks every component row also passes.

## H9 — Sweep, deploy to testing, verify from the served bytes, report the census

Testing deploys are automatic (`RULING_testing-deploys-are-automatic-2026-08-22.md`).
**The live site is not touched.**

From the **deployed bytes**, report:

    ships total / rendering a model / by own file / by shared hull / rendering nothing
    orphan model files before  40  ->  after  ?
    pure-white pixel share in each of the three styles

Plus page height at 1920x1080 and 1366x768, the version ID, and the upload diff.

---

## Run rules

- **No decision gates.** Pre-ruled throughout. Genuine ambiguity: take the more
  reversible option, write it down, keep going.
- **Ledger entry per item with the commit sha.**
- **Rule 12 on every item.** A control that cannot fail is not a control.
- **NO FUZZY MATCHING anywhere in H2, H3 or H4.** An unresolved file is reported,
  never guessed.
- **Do not `git add -A`.** Do not deploy the live site. Do not cut a release.
- **Do not fetch anything from RSI.** H5 decides whether that conversation is even
  worth having, and it has not happened yet.

## Sequencing against the picker order

**B0 of `ORDER_the-picker-redesign-2026-08-22.md` comes first** — 782 of 1,200
hull markers currently do nothing when clicked, and 61 hulls have no working
marker at all. **Making more ships beautiful in a viewer whose markers mostly do
nothing makes the defect prettier, not smaller.**

If B0 is already done when this is picked up, run this straight through.
