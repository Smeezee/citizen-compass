# PROPOSAL — the ship gets 36% of the screen today and I measured why: 42vw of the width is two rails that never go away, and 238px of the height is gone before the grid starts. Collapsing the rails to icon strips takes the ship to 72% without deleting one number. Three options, one recommendation, and one idea I am arguing against.

    from      C3 (Cowork), 2026-08-30
    for       C1 to route. `testing/_src/loadout.src.html` has one writer and
              it is not me - this is a design, not a patch.
    raised by Sleven, from the live Vulture page: *"make the text windows and
              everything around the actual ship smaller. wanna keep the
              information, but I need to make the ship the more dominant
              component of the page. I don't wanna have to scroll a bunch."*
    method    measured from the source CSS and the built payload, not estimated
              from the screenshot.

---

## 1. THE MEASUREMENT, BEFORE ANY OPINION

`loadout.src.html:656`

    .cols{grid-template-columns: minmax(300px,22vw)  minmax(0,1fr)  minmax(280px,20vw);
          height: calc(100vh - var(--chrome))}
    :root{--chrome:238px}

**Two fixed rails take 42vw of the width and never collapse. 238px of the height
is spent before the grid begins.**

On Sleven's screen (1904 wide, roughly 890 of usable viewport):

    left rail      419 px      22vw
    right rail     381 px      20vw
    gaps/padding    42 px
    ────────────────────────────────
    STAGE WIDTH   1062 px      56% of the width

    chrome         238 px      header + acquisition chips + tab strip
    marker note     84 px      the amber block, WITH ITS OWN SCROLLBAR
    ────────────────────────────────
    STAGE HEIGHT   568 px      64% of the height

    SHIP = 1062 x 568 = 603,000 px²  of  1,694,000 px²  =  36%

**The ship is a third of the page.** That is the whole problem stated as a number,
and it is a layout fact rather than a styling one — **no amount of tightening
type inside the rails changes 42vw.**

**And there are three independent scroll regions**: the left column, the right
column, and the 84px amber note. **That is the "scroll a bunch" complaint, and it
is worse than one long page** — a nested scroller steals the wheel when the pointer
crosses it, so the page fights the user.

## 2. WHAT IS ACTUALLY IN THE RAILS, AND WHAT IT COSTS

**Right rail — 12 stat cards, and roughly 40% of each card is a sentence.**

    SUSTAINED DPS   CIG  ?
    223.8
    what the pilot can fire        <- explanation, 2 lines on a narrow card

Every card carries one: *"hull + shields"*, *"heat · lower is stealthier"*,
*"kg · hull plus everything fitted · lower turns better"*.

**By this project's own disclosure rule those are EXPLANATIONS and should collapse**
— the rule Code's audit settled says collapse a block that explains, never one that
warns or states what you are looking at. **The number and its provenance chip stay
visible. The sentence goes behind the `?` that is already sitting there unused for
this purpose.**

**Left rail — 64 ports, two lines each.** For the Vulture that is a list no screen
can hold, which is why it was given a box. **But the weapons section duplicates
what the model already shows** — those mounts are dots on the hull, bound to
`PortId`, and clicking either opens the same panel.

**Chrome — 238px, and the acquisition strip is the soft part.** Five chips: in-game
price, pledge price, status, manufacturer, role. **None of them changes a choice
being made on this screen** — they are facts about the ship, and four of the five
are already on the Specs tab.

## 3. THREE OPTIONS

### OPTION A — COMPACTION. Keep the three columns, shrink everything.

Rails to 18vw and 16vw. Chrome to ~170px by folding the acquisition chips into one
line. Stat explanations collapse behind the `?`. The amber note keeps its warning
line and collapses its paragraph.

    SHIP = 1214 x 690 = 838,000 px²  =  50%

**Cost: 1 day. Risk: near zero.** Nothing moves, nothing new is built, no
interaction changes.

**And it does not answer the question.** It makes the ship bigger. **It does not
make the ship dominant** — the rails are still there, still permanent, still a
third of the width. Sleven asked for dominance, not for 14 more points.

### OPTION B — THE RAILS COLLAPSE TO ICON STRIPS. *(recommended)*

Both rails default **closed**, as ~48px vertical strips of group icons — weapons,
shields, power, cooling, quantum, and one for the readout. **The stage is the page.**

Click an icon and that panel slides out over the stage, **one at a time**, at the
width it needs. Click again, or click the stage, and it closes. The choice is
remembered in local storage so a returning visitor gets the page they left.

    SHIP = 1766 x 690 = 1,218,000 px²  =  72%      <- double today

**What is kept, not deleted:** every number, every row, every explanation. **The
information does not shrink — its resting state changes.**

**Why over the stage rather than pushing it:** a panel that pushes the model resizes
the canvas, which re-frames the camera and makes the ship jump every time you open a
list. **A panel that floats over it leaves the ship exactly where it was.** The site
already does this — the tune panel at `loadout.src.html:575` is an absolutely
positioned overlay on the stage and has been all along. **This is that pattern
promoted to the main layout, not a new mechanism.**

**Cost: 3-4 days. Risk: moderate and named.** The real one is that a wide hull fills
the frame and an overlay lands on top of it. Mitigations: one panel at a time, panels
anchored to the edge the model is thinnest at, and the existing scrim. **It should be
prototyped on the Vulture and the Polaris before it is committed to** — a light
salvage hull and a capital frame the two shapes.

**One thing this fixes for free: the three scroll regions become one.** The stage
does not scroll; the open panel does; nothing else exists to steal the wheel.

### OPTION C — THE MODEL IS THE INTERFACE. No component list at all.

Physically mounted parts are dots on the hull and nothing else. Internals —
power plant, coolers, shield, quantum — get a summoned overlay, **which is already
the standing architecture decision, not a new idea.** Stats become a thin strip of
numbers along the bottom.

**Ship approaches 85%.** It is the most striking version and it is the one that
would get screenshotted.

**And I am arguing against it as the default, for a measured reason.**

    hulls in the payload                    316
    hulls carrying markers                  259      6,058 entries
    hulls with NO markers                    57

**57 hulls would have no interface at all.** Option C works beautifully on the
Vulture and fails on 18% of the fleet, and the failure is silent — a ship page with
no dots and no list is a blank page.

**It is the right destination and the wrong next step.** Option B reaches it: once
the rails collapse, a hull with good markers can default to *closed* rails and a
hull without them can default to *open*. **Same page, same code, and the fallback is
a default rather than a special case.**

## 4. WHAT I WOULD DO, IN ORDER

1. **Option A's compaction, first, on its own.** One day, no risk, and it is
   worth doing whether or not B follows. **The stat-card explanations in
   particular are already violating the disclosure rule the rest of the site
   follows** — this is a consistency fix that happens to buy space.
2. **Prototype Option B on two hulls** — Vulture and Polaris. Do not build it
   across the site first. **The only question that matters is whether a panel over
   a wide hull is tolerable, and that is answered by looking at it, not by
   arguing.**
3. **Then decide.** If the overlay reads badly, Option A's 50% is a real
   improvement and the work is not wasted.

## 5. ON ERKUL — what I can honestly say

**I could not read its layout.** `erkul.games` is client-rendered and returns
metadata only to a fetch, the same trap as the RSI comm-links. **Anything I said
about its panel arrangement would be from training data and presented as current,
which this project has rules against.**

**What I am taking as given is Sleven's own description:** everything on one page,
and you scroll. **The relevant difference is that Erkul has no 3D model.** A tool
whose main object is a table can afford to be a page of tables. **Ours has a hull
in a stage, and a hull is the one element that gets worse when you shrink it and
better when you give it room.** That asymmetry is the argument for B and it does
not depend on knowing Erkul's exact layout.

## 6. WHAT I CHECKED AND WHAT I DID NOT

**Checked:** `loadout.src.html:656` for the grid, `:root{--chrome:238px}`, the
`.markernote` box at 78px with `overflow-y:auto`, the three `overflow-y:auto`
regions, the existing `#cc-tune-panel` overlay at line 575, the two media queries
at 1250px and 820px, and `loadout_marker.gen.js` in the built payload for the
259-of-316 coverage.

**Did NOT check:**
- **Sleven's actual viewport.** I read the screenshot as ~1904x890 usable. **The
  percentages move with the screen and the argument does not** — the rails are
  42vw at every size above 1250px.
- **Whether an overlay over a wide hull is readable.** §3 calls it the real risk and
  says prototype rather than argue. **I have not seen it.**
- **What the two media queries already do below 1250px.** They drop to two columns
  and then one, and a collapsing rail may make both unnecessary. **Somebody should
  look before adding a third breakpoint.**
- **I have changed nothing.** `testing/_src/` has one writer and it is not me.
