# DECISION + SPEC — the main page is the DRYDOCK, with the Market's constraint sliders as its filter, the Market's listing row as its second view, and the Orrery as a mode you toggle into. The Field Guide is out. The Bridge's ideas go to the ship page, not here.

    from      C3 (Cowork), 2026-08-30
    for       C1 to route
    DECIDED   by Sleven, 2026-08-30, after walking five complete competing
              main-page designs. His words are quoted per decision below.
    working   three browsable mockups are now in the repo, real data, 315 hulls:
                data-layer/derived/main-page-concepts/five-main-pages.html
                data-layer/derived/main-page-concepts/slipway.html
                data-layer/derived/main-page-concepts/deck-sifter-yard.html
              Open them in a browser. They run offline, no build step.
    related   PROPOSAL_make-the-ship-the-page-2026-08-30.md
              SPEC_the-ship-page-becomes-an-instrument-2026-08-30.md
              DESIGN_the-front-page-and-the-url-defect-2026-08-30.md

---

## 0. HOW THIS WAS ARRIVED AT — because the method is the useful part

Five COMPLETE main pages were built and run against the project's own 315-hull
dataset. **Not five features — five whole products**, each with its own full feature
set, its own layout and its own reason to exist. Sleven then picked apart which
parts earn a place.

**That is the correction that made this work.** Earlier rounds produced components
and called them designs. **A design is a page somebody could ship; a component is a
thing you argue about.** Anything proposed for this page from here should be
presented the same way.

---

## 1. THE DECISIONS

### 1.1 DRYDOCK — THIS IS THE MAIN PAGE

> *"I very much like the dry dock."*

**Adopted as the base.** Its own feature set, as built and approved:

    every hull as a TRUE-SCALE silhouette in its own bay
    search across name, manufacturer, role and career
    career filter chips, colour-coded, multi-select
    five sort orders - longest, shortest, name, cargo, crew
    three figures per bay: length, crew, cargo
    a COMPARE TRAY that rises from the bottom when two hulls are picked
    a live count of what is showing

**The scale is the spine and it must not be softened.** Every bay shares one scale,
so a Gladius is genuinely tiny beside a Reclaimer. **That is the thing no other tool
in this hobby does** — Fleetyards shows photographs, spviewer shows numbers, Erkul
shows neither. Measured: none of the three renders a single 3D model or a single
scale comparison.

### 1.2 MARKET — TWO PARTS IN, THE REST OUT

> *"The idea you have at the budget ceiling, that idea, I really like that concept.
> I would like to utilize that in our page... setting the cruise and stuff. That's a
> feature right there that I like. And, yeah, I kinda like how the market looks. You
> have the image of the ship, and the name, the information about it."*

**IN — the constraint sliders, as the Drydock's filter mechanism.** Not chips alone:
ceilings and floors you set and watch the fleet answer.

    budget ceiling          a price you will not go over
    crew ceiling            at most this many people
    plus, from the same idea: cargo floor, length ceiling, speed floor

**Why this beats the chips it joins:** a chip answers *what kind*; a slider answers
*what I can actually have*. **They are different questions and the page needs both.**

**IN — the listing row as a SECOND VIEW of the same fleet.** Silhouette, name,
status badge, the facts on one line, the figure on the right. **Bays for looking,
rows for comparing** — same data, same filters, one toggle between them.

**OUT — everything else about the Market**, including it being its own page.

### 1.3 ORRERY — A MODE INSIDE THE DRYDOCK

> *"I absolutely agree with you. I think that should be a feature, something you
> could toggle into from the dry dock. Absolutely."*

**Adopted exactly as that: a third view, not a page.** Bays · Rows · Sky.

    five rings by size class      snub/ground · light · medium · heavy · capital
    one point of light per hull   colour is career
    search DIMS THE SKY           matches stay burning, everything else fades
    click a point                 a glass card with the figures and the way through

**It carries a true fact no table can show:** the inner rings are crowded and the
outer ring is nearly empty. **Star Citizen is overwhelmingly a game of small ships
with a handful of enormous ones**, and the shape of the sky says so instantly.

**A DESIGN FAULT IN THE MOCKUP THAT MUST BE FIXED BEFORE BUILDING.** In what was
demonstrated, **a dot's position on its ring means nothing** — the spacing is even
and arbitrary. The eye assumes position carries meaning and it does not, which makes
the picture quietly dishonest.

**The fix, and it makes the view better rather than merely honest:** let the angle
carry the manufacturer. Each maker owns a wedge, so **distance from centre is size
and angle is who built it.** Both dimensions then mean something, and a company's
whole spread across every size class becomes visible in one glance.

### 1.4 BRIDGE — NOT HERE. IT BELONGS TO THE SHIP PAGE.

> *"I feel like there's part of the bridge that could be utilized in the actual ship
> viewer page."*

**Agreed, and it lands on work already specced.** The Bridge's real contributions are
about operating one ship, which is `SPEC_the-ship-page-becomes-an-instrument`'s
subject:

    keyboard first          arrows step, slash filters, enter opens
    the readout never hides twelve figures always on screen, nothing behind a click
    a contact list          a compact, always-present index of what you can switch to

**That third one is the interesting overlap.** The ship page spec asks for next/
previous ship. **The Bridge shows what next/previous looks like when it is a
LIST rather than two arrows** — and that is worth weighing against the arrows before
either is built.

**Route to the ship-page spec. Do not build it into the main page.**

### 1.5 FIELD GUIDE — OUT

> *"It's very neat and very straight to the point, but I just don't think it meets my
> requirements."*

**Closed.** Recorded so nobody proposes it again. **One idea inside it is worth
keeping in the drawer** — the *telling it apart* note, which names a ship's nearest
sibling and states exactly how it differs. That is a teaching device, it needs no new
data, and it would sit naturally on a ship page. **Not scheduled, not lost.**

---

## 2. WHAT THE MAIN PAGE IS, ASSEMBLED

    ┌──────────────────────────────────────────────────────────────────┐
    │  CITIZEN COMPASS    [ search 315 hulls ]        BAYS · ROWS · SKY │
    │  career chips ································· 315 shown        │
    ├───────────────┬──────────────────────────────────────────────────┤
    │ CONSTRAINTS   │                                                  │
    │ budget    ▓▓▓ │   the fleet, in whichever of the three views     │
    │ crew      ▓▓  │   is selected — bays, rows, or sky               │
    │ cargo     ▓   │                                                  │
    │ length    ▓▓▓ │                                                  │
    │               │                                                  │
    │ 41 still fit  │                                                  │
    ├───────────────┴──────────────────────────────────────────────────┤
    │  COMPARE:  [ Drake Vulture ]  [ MISC Prospector ]   compare two → │
    └──────────────────────────────────────────────────────────────────┘

**One fleet. One set of filters. Three ways to look at it. One compare tray across
all three.** The view toggle changes only how the ships are drawn — never what is in
the set, never the filters, never the compare tray.

**That single rule is what makes three views cost less than three pages.**

## 3. THE ONE THING THAT CAN SINK THE BUDGET SLIDER — read before scheduling it

**We have no verified prices, and the budget ceiling is a price feature.**

    CIG ships NO prices at all. The only cost-like fields in the entire
    export are AmmoCost and CostPerBullet.
    Every price on this site comes from UEX, a community source.
    0 of 26,657 rows are verified.

**The prices in the Market mockup are generated for the demo.** They are not real and
were labelled as such on every row.

**Three ways forward, and this is Sleven's call rather than a technical one:**

    a  ship the slider on community prices, labelled unverified on its own face
       - honest, useful, and the site already carries UEX data with that caveat
    b  ship the OTHER ceilings now - crew, cargo, length, speed - and add
       budget when a price source can be stood behind
    c  do not do budget at all

**Recommend b as the build order regardless of which is chosen.** The slider
mechanism is the valuable part and it works identically on crew and cargo. **Build
the mechanism against data we can stand behind, then add price as one more slider if
and when it is decided.** Nothing is wasted either way.

## 4. WHAT TO BUILD, IN ORDER

    1  the Drydock as the main page              bays view only, no toggles yet
       search · career chips · sorts · scale silhouettes · compare tray
    2  the constraint sliders                    crew, cargo, length, speed
       NOT budget - see §3
    3  the rows view                             second toggle, same fleet
    4  the sky view                              third toggle, with §1.3's fix
    5  budget slider                             only after §3 is decided

**1 to 3 are each independently shippable and each leaves the page better than the
day before.** Step 4 is the one worth prototyping before committing.

**Two things that must be settled inside step 1, not after:**

**The silhouettes.** 259 of 316 hulls have models; 57 do not. The mockups draw
proportional stand-ins generated from real length-to-beam ratios. **The built version
should draw the real outline from the model where one exists** — and the 57 need a
designed empty state saying the model is missing, not a blank bay. **This site's
standard is that a page says what it does not have.**

**The click target.** Clicking a bay must reach the ship page. In the mockup a click
loads the compare tray instead. **Decide: click opens the ship, and a separate small
control adds to compare** — that is the ordinary expectation and the mockup gets it
wrong.

## 5. WHAT I CHECKED AND WHAT I DID NOT

**Checked, live in a real browser, at a forced 1400x900:** that spviewer renders one
table of 20 columns and 241 rows in a document exactly one screen tall; that
Fleetyards renders zero tables, 30 cards of 1051x286, and needs 11.04 screens per
page across 9 pages; that Erkul has no canvas element at all, 65 SVGs and a
one-viewport document. **None of the three renders a 3D model or a scale comparison.**

**Checked from our own build:** all 315 hulls carry real dimensions, career, crew,
cargo, mass and performance figures; the front page today is a ten-column purchase
matrix whose five dealer columns are ~85% empty on a typical screen.

**Did NOT check:**
- **Whether the Drydock's grid holds up at 315 bays on a slow machine.** The mockups
  render the full set without complaint in a modern browser. **Nobody has measured it
  on anything else.**
- **Whether the sky view is usable by keyboard or screen reader.** It is a field of
  dots and it is the weakest of the three views on that count. **A list fallback is
  not optional and is not designed.**
- **Any price.** §3.
- **How the real model outlines will look at bay size.** Stand-ins are not the
  article, and a 40-pixel-tall real silhouette may read as mush. **Try one before
  building 315.**
- **I have changed no page and no code.** The three mockups are new standalone files
  under `data-layer/derived/main-page-concepts/` and are wired to nothing.

---

# SUPERSEDED — 2026-09-06. Read this before you build anything from the above.

**The drydock is not the front page and neither is the wall.** Sleven walked five
designs from the previous C1 and two more from this one, and rejected all seven.
The design he approved on 2026-09-06 is a third thing, and this document, the wall
spec, and the mockups they point at are all history now.

**Nothing here rescinds the reasoning.** The method section is still the useful
part and the reason this file is not deleted.

## What he actually approved, and the sentence that got him there

Cards. Grouped by manufacturer A–Z, ships A–Z inside each group. **Every card the
same height. Every fact on the face of the card.**

The sentence that killed the version before it was his: *"The problem with what you
made is that it's not simple to get the information."* That is the whole design
constraint. The drydock's sliders, its three views and its compare tray all put
facts one interaction away, and so did the wall. **A visitor alt-tabbed out of the
game does not have an interaction to spare.**

Depth did not disappear, it moved: *"if you wanna go deeper, that's gonna get the
more robust 3D model with interactive hardpoints and DPS calculator and full
loadout spec."* **The front page is flat and complete. The ship page is deep.**

Two more constraints he stated and that a future design must not lose:

**The 3D is the identity and must not appear twice.** *"You already have a 3D model
area for each ship. So we don't need two 3D models. One on the front page and not
on the second page."* The front page carries pictures, not a viewer.

**Alphabetical, and it is not negotiable.** He caught a version that sorted makers
by ship count and ships by length within a single reply.

## Where it lives

    testing/_src/next.src.html      generated build source, publishes as next.html
    data-layer/derived/main-page-concepts/the-index.html     the working copy
    /tmp/cc/gen6.py                 the generator (NOT in the repo — see the order)

Job B of `docs/ORDER_put-the-new-front-page-up-beside-the-old-one-2026-09-06.md`
turns it into the real `index.html`.

## The superseded mockups, kept and no longer to be built from

    five-main-pages.html   six-front-pages.html   drydock.html   the-wall.html
    slipway.html   the-slipway.html   deck-sifter-yard.html   three-looks.html
    sky-three-ways.html

*C1, 2026-09-06.*
