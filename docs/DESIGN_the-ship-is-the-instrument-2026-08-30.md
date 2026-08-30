# DESIGN — the page is not a display with a model on it, it is an instrument somebody operates thirty times in a sitting. That reframes all three of Sleven's asks. Next/previous is nearly free because the loadout already lives in the URL hash. The way back is a text link 76px wide sitting beside a title three times its size. And at a narrow window the ship is below the fold entirely.

    from      C3 (Cowork), 2026-08-30
    for       C1 to route. Design only — Sleven: *"this is all designed for the
              moment. We're not pushing anything."*
    raised by Sleven: the model should be the main focus and more interactive;
              simplicity judged by repeat use, because this is the minmax bench
              and not only a display; next/previous ship without leaving the
              viewer; and a way back to the full list with some pop.
    method    measured live in a real browser on the deployed testing page.
    NOT       a copy of Erkul. Sleven's words: a reference for what to do
              better and differently.

---

## 1. WHAT I MEASURED FIRST, because two of these change the answer

    ← All ships     76 x 22 px   15px/700   orange text, TRANSPARENT background
    ship title     196 x 30 px   21px/700
    ship dropdown  425 x 37 px   13.3px/400   349 OPTIONS
    header controls  10 of them in the top strip

    URL   /loadout#AEGS_Avenger_Stalker|,,,,,,,,,|,,,,,,,,,
    history.length   4        - hash changes already push history

**Two things fall out of that URL and they decide most of this document.**

**The ship and its entire loadout live in the hash.** Switching ships is not a
navigation — it is a hash change and an in-place re-render. **So next/previous is
not new plumbing. It is a control on a mechanism that already exists.**

**And the loadout travels with the ship in that same hash.** Which means moving to
the next ship necessarily replaces the build you were working on. **That is the real
design question in Sleven's request, and nobody has asked it yet.** §4.2.

## 2. THE REFRAME — repeat use is a different test, and the page fails it in one specific way

Sleven: *"the simplicity needs to be user focused in using it over and over again...
this is also the loadout set up for people wanting to minmax their ships."*

**A display is judged on first read. An instrument is judged on the fiftieth
repetition.** Those pull in opposite directions: a display wants labels and
explanations, an instrument wants them gone after the first time.

**The loop a minmaxer actually runs:**

    pick a mount  ->  see what fits  ->  swap  ->  read the ONE number that moved
    ->  undo or keep  ->  go again

**The rule that follows, and it is the whole design:**

> **The only thing that moves is the thing that changed.**

**Everything else must hold still — the camera above all.** A swap that reframes the
hull, reflows a panel, or scrolls a list has broken the loop, because the operator
has to re-find their place before they can go again. **Thirty repetitions of
re-finding your place is what makes a tool exhausting rather than hard.**

**This is also the argument for the model being the instrument rather than the
picture.** The mounts are already dots bound to `PortId`, and a dot is a *stable
target*: it is in the same place on the hull every time, which a list row in a
scrolling column is not. **An operator builds muscle memory against geometry, never
against a list that moves.**

**What that means concretely, in priority order:**

1. **The camera never moves on a swap.** Not a nudge, not a refit. If a panel opens,
   it floats over the stage rather than resizing the canvas (which reframes).
2. **Swapping happens at the dot.** Click the mount, the options appear beside it,
   choose, done. The left list stays as the way in for anything with no dot.
3. **The number that changed is marked.** Not the whole readout redrawn — the one
   figure that moved, flagged for a beat with its delta.
4. **Undo is a first-class control, not a header afterthought.** It already exists.
   For an instrument it belongs where the hand is, and it wants a keyboard binding.

## 3. THE MODEL AS THE MAIN FOCUS — where the earlier proposal now stands

`PROPOSAL_make-the-ship-the-page-2026-08-30.md` measured the ship at **34.9% of the
viewport**, with two rails taking **42.0% of the width** and never collapsing. That
stands and this does not repeat it.

**What this document adds is that the space argument and the instrument argument
reach the same answer by different routes.** Collapsing rails give the model room
*and* they give the operator a stable stage that stops being carved up. **One change
serves both, which is the strongest reason to prefer it.**

### 3.1 A MEASURED PROBLEM NOBODY HAS NAMED — at a narrow window the ship is gone

I rendered the deployed page at **451px wide**, the natural size of a docked browser
pane. Below the 820px breakpoint the layout stacks to one column, and the first
screen is:

    header · ship title · a 349-option dropdown · Day/Night/Blackout · three buttons
    · five acquisition chips · then the component list

**The 3D model is not on the first screen at all.** The stack puts the left column at
52vh and the stage at 46vh *after* it, so the model starts below the fold.

**On the page whose entire point is the ship, at that width, the ship is something
you scroll to find.** That is not a styling complaint — it is the stacking order,
and it is the one place where "make the model the focus" is currently reversed
outright.

## 4. NEXT AND PREVIOUS — Sleven's ask, and the two questions inside it

Sleven: *"switch between the ships while you're still in the ship viewer. It only
needs to be the next ship or the ship before it. Nothing more."*

**Taken literally, and it should be.** Two controls, no carousel, no filmstrip, no
"related ships" rail. **The restraint is the feature** — a minmaxer comparing two
hulls wants to flip, not to browse.

### 4.1 The question that decides whether it feels right: NEXT IN WHAT ORDER?

**This is not a detail.** Arbitrary order makes the control useless, because the next
ship is a surprise every time and the operator cannot form an expectation.

    a  alphabetical across all 349      predictable, and almost always useless -
                                        the neighbour is a different class entirely
    b  THE LIST YOU ARRIVED FROM        <- recommended
    c  same manufacturer                a special case of b, and narrower

**Recommend b.** If a visitor came from *all Drake ships*, next means the next Drake.
If they came from a search for salvage hulls, next walks the salvage hulls. **The
control inherits the intent the visitor already expressed**, and it needs no new UI
to explain itself.

**It also answers the arriving-cold case honestly:** a visitor landing on a shared
link has expressed no intent, so next falls back to alphabetical **and says so** —
the control's tooltip names the sequence it is walking. **A control that can tell you
what it will do next is not a surprise.**

### 4.2 THE QUESTION NOBODY HAS ASKED — what happens to my build?

**The hash carries the ship AND the loadout together.** So next/previous, built the
obvious way, **discards whatever the operator had configured.**

For a display that is fine. **For a minmax bench it is the worst possible behaviour**
— the user's whole reason for being there is the build, and a navigation control that
silently bins it will be used once.

**Recommend: per-ship memory for the session.** Configure a Vulture, flip to the
Cutlass, flip back — **the Vulture is as you left it.** Held in local storage, keyed
by ship, cleared by the existing *Back to stock*.

**And the sharper version, which is nearly free once memory exists:** flipping ships
with a build in hand is *comparison*, so the readout can hold the previous ship's
figures beside the current one until the operator moves on. **That is the "try another
alongside" button's job done without pressing it.** Offered as a consequence, not a
recommendation — it is a second feature and Sleven asked for two controls.

### 4.3 Shape

    ‹  Drake Cutlass Black          [ ship title ]          Drake Herald  ›

Flanking the title, showing **the name of where you are going** rather than a bare
arrow. **A destination you can read is a control you can use without trying it.**

**Bind the arrow keys.** An operator flipping hulls will not keep reaching for a
mouse target, and this is precisely the repeat-use case from §2.

## 5. THE WAY BACK — and it is doing two jobs badly

Sleven: *"returning to the actual full list of ships... needs to be designed better.
It can't just be 'return to ships'. It's small... it needs to have a little bit of
pop."*

**Measured: 76 x 22px of orange text with no background, next to a 196 x 30px title
at the same weight.** It is a third the size of its neighbour and has no shape at all
— **the eye reads the ship name and never registers the link.**

**But size is the symptom.** The real fault is that three different intents are
crowded into one corner and the wrong one got the smallest control:

    "I know the ship I want"      -> the 349-option dropdown        425px
    "show me the one beside it"   -> does not exist yet             §4
    "let me go browse"            -> a 76px text link               <- the way out

**Recommendation: make it a control with a shape, and put it where the eye starts.**
A bordered button with the site's accent, sized like the other header buttons, at the
top-left where a home affordance is expected — **and give it a real label.** *All
ships* is thinner than what it does; *Browse all 349 ships* tells the visitor what is
behind it and earns its width by carrying a number nothing else on the page states.

**One caution against overcorrecting:** it must not become the loudest thing on the
page. **The ship is the loudest thing.** A bordered button of ordinary header size,
with the accent as its border rather than a filled block, is enough to stop it
disappearing without competing with the hull.

**Do not add a second way back.** A breadcrumb, a hamburger and a link are three
answers to one question, and this page already has ten header controls.

## 6. THE HEADER IS THE REAL CONSTRAINT — ten controls, and that is before adding any

    ← All ships · ship dropdown · Day · Night · Blackout · Undo · Back to stock
    · Try another alongside · Copy share link · FIND

**Sleven's asks add two more.** Eleven or twelve controls in one strip is not a
header, it is a toolbar, and **it is also the 106px of vertical the model wants back.**

**Grouping, by what each one is for:**

    NAVIGATION   back · prev · next · dropdown        left, together
    THE BUILD    undo · back to stock                 near the build, not the header
    THE VIEW     day/night/blackout/intensity         one control that opens, not four
    SHARING      copy link · try alongside            right, and quiet

**Day, Night, Blackout and a percentage slider are four controls for one decision.**
Collapsed to a single lighting control they cost one slot instead of four, and
**nobody sets lighting more than once a session** — which is exactly the §2 test for
what may be tucked away.

## 7. WHAT I CHECKED AND WHAT I DID NOT

**Checked, live, in a real browser on the deployed page:** the geometry, font size,
weight and background of the back link, title and dropdown; the 349-option count; all
ten header controls; the URL hash carrying ship plus loadout; that hash changes push
history; and the stacked layout at 451px with the model below the fold.

**Also measured, on erkul.games at a forced 1904x890:** no canvas at all, 65 SVGs,
document exactly one viewport tall, four panel columns. **Recorded only to say that
its density suits a page with no hero object and ours does not.** Not a model to copy
— Sleven's own framing.

**Did NOT check:**
- **Whether a swap currently moves the camera.** §2's first rule assumes it might.
  **It is one thing to try and it decides how much of §2 is already true.**
- **What the empty comma lists in the hash mean per slot.** I read the shape, not the
  encoding.
- **Whether local storage is already used for anything**, which §4.2 would join.
- **How any of this LOOKS.** Screenshots now work through the bridge, but at the
  docked pane's own width; a forced desktop viewport renders scaled down and small.
  **Every judgement here is geometry and structure, not appearance.**
- **I have changed nothing.** `testing/_src/` has one writer and it is not me.
