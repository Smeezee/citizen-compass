# SPEC — the ship page becomes an instrument. Seven changes, approved by Sleven, plus one live defect that must be fixed first. They are not seven independent items: three of them are preconditions for the others, and two pairs will make the page WORSE if either half ships alone.

    from      C3 (Cowork), 2026-08-30
    for       C1 to route. `testing/_src/` and `NEXT.md` each have one writer
              and neither is me. This is a spec to be routed, not queued.
    APPROVED  Sleven, 2026-08-30, on all seven: *"Honestly, I like all of them...
              expand on all of them... address the problem as a need to fix
              thing, and let's figure out how to make it all work together."*
    replaces  the loose list in DESIGN_the-ship-is-the-instrument-2026-08-30.md.
              That document's reasoning still stands; this is what to build.
    method    measured live in a real browser on the deployed testing page.

---

## 0. THE ONE SENTENCE EVERYTHING ELSE SERVES

> **This page is not a display with a model on it. It is an instrument somebody
> operates thirty times in a sitting, and every change below is judged on the
> fiftieth repetition rather than the first look.**

A display is judged on first read and wants labels. **An instrument is judged on
repetition and wants everything it has already told you to get out of the way.**
That is the whole difference, and it is why "make the ship bigger" and "make the
ship the interface" are the same job rather than two.

---

## D0. THE DEFECT — FIX THIS FIRST, ON ITS OWN, BEFORE ANY OF THE SEVEN

**At a narrow window the ship is almost entirely below the fold, and the page is
2.6 screens tall.**

Measured on the deployed page at a 455 x 898 viewport:

    stage begins at        y = 842
    first screen ends at   y = 898
    stage height           323 px
    ────────────────────────────────────
    SHIP VISIBLE ON THE FIRST SCREEN:  56 px of 323  =  17%
    document height        2,348 px  =  2.61 screens

**CORRECTION TO MY OWN EARLIER CLAIM.** `DESIGN_the-ship-is-the-instrument` §3.1
says the model is *"not on the first screen at all."* **That was read off a
screenshot and it is too strong.** 56px of it is visible. **The defect is real and
the number was wrong** — this is the third time this month I have described a whole
from a part, and it is recorded here rather than quietly corrected.

**Why it is a defect and not a layout preference:** on the page whose stated purpose
is the ship, at that width, a visitor scrolls past a header, a title, a 349-option
dropdown, four lighting controls, three buttons and five acquisition chips before
reaching the thing they came for. **Every one of those is subordinate to the hull and
every one of them is above it.**

**The cause is source order, and nothing else.** Measured:

    DOM order in .cols:  col left  ·  col mid  ·  col right
    computed `order` on all three:  0        <- nobody has set it

At `max-width:820px` the grid collapses to one column and honours source order, so
the parts list comes before the stage.

**The fix is one property.** Give the stage `order:-1` inside the narrow media query
so it leads the stack. **The desktop layout is untouched** — `order` does nothing to
a three-column grid whose columns are placed by template.

**Do this first, alone, and deploy it.** It is minutes of work, it is a live
user-facing fault, and **it must not be bundled into the bigger changes** — a
one-property fix buried inside a layout rewrite cannot be proven on its own.

**Rule 12 for it:** the check that matters asserts the stage's top is above the fold
at 455px width, **and it must be shown failing on today's build first.** A check that
has only ever been seen passing has not been seen.

---

## HOW THE SEVEN FIT TOGETHER — read this before the specs

**They are not a list. Three are preconditions, and two pairs are single features
wearing two names.**

    (3) camera never moves ─────────┐
                                    ├──► (1) rails collapse ──┬─► (2) swap at the dot
    (7) header room ────────────────┤                         └─► also fixes D0
                                    └──► (6) browse button

    (5) per-ship memory ────────────────► (4) next / previous

**The three hard rules that come out of that graph:**

**(3) must land before (1).** If opening a panel resizes the canvas, the camera
reframes. Collapsing rails means opening and closing panels constantly, so shipping
(1) on an unstable camera turns one annoyance into thirty. **(3) is what makes (1)
safe rather than a nice extra.**

**(1) and (2) ship together or not at all.** (2) without (1) gives two ways to swap a
part and a stage still too small to aim at. (1) without (2) makes the ship big and
hides its controls behind icons the visitor has no reason to click. **In between,
the page is worse than it is today.**

**(4) without (5) actively destroys the user's work.** The ship and the loadout are
carried in the same URL hash, so next/previous built the obvious way discards the
build. **(5) is not an enhancement to (4). It is the half that stops it being
harmful.**

**And one convergence worth stating:** (1) also fixes D0 for good, because a page
whose rails are icon strips has no reason to stack the same way. **D0 is fixed twice
— once now with one property, once structurally later.** That is deliberate, not
waste: the cheap fix ships tonight, the structural one removes the possibility.

---

## THE SEVEN

### (3) THE CAMERA NEVER MOVES — the precondition, and the cheapest thing here
*Build first of the seven.*

**The rule:** *the only thing that moves is the thing that changed.*

When a part is swapped, a panel opened, or a panel closed:

    the camera        does not move. Not a nudge, not a refit, not a re-centre.
    the hull          stays at the same angle, the same zoom, the same position
    the canvas        is NOT resized - a resize reframes, so panels FLOAT over
                      the stage rather than pushing it
    the readout       does not redraw whole. Only the figures that moved change,
                      and each marks itself for about a second with its delta

**Why it is first:** every other change increases how often panels open and close.
**On a page where the camera drifts, that is thirty small betrayals a session** —
the operator re-finds their place before every action, and the tool feels
exhausting without ever feeling broken.

**The precedent already exists.** `#cc-tune-panel` is an absolutely positioned
overlay on the stage and has been all along. **This promotes an existing pattern; it
does not invent one.**

**Rule 12:** record the camera matrix, swap a part, assert it is unchanged. **It must
be shown failing against a deliberately-reframing build**, or it is a check that has
only ever agreed with itself.

**Not checked by me:** whether a swap currently moves the camera at all. **If it
already holds still, this is a check rather than a change** — and that is worth
finding out in ten minutes before anybody budgets for it.

---

### (7) HEADER ROOM — four controls become one
*Build second. Cheap, independent, and it pays for (4) and (6).*

**Measured: ten controls in the top strip today.**

    ← All ships · ship dropdown · Day · Night · Blackout · intensity slider
    · Undo · Back to stock · Try another alongside · Copy share link · FIND

**The seven changes add two more. Twelve is not a header.**

**Day, Night, Blackout and a percentage slider are four controls for one decision,
and it is a decision nobody makes twice in a session.** By §0's test that is exactly
what may be tucked away: it has told you what it does, and it does not need to keep
saying so.

**Collapse them into one lighting control** that opens to the same four choices.
Four slots become one.

**Regroup the rest by what each is for:**

    NAVIGATION   browse · prev · next · dropdown       left, together
    THE BUILD    undo · back to stock                  by the build, not the header
    THE VIEW     lighting                              one control
    SHARING      copy link · try alongside             right, and quiet

**Undo moving out of the header is not cosmetic.** By §0 it is the most-repeated
control on the page and it belongs where the hand already is — beside the build,
with a keyboard binding.

---

### (6) THE WAY BACK BECOMES A REAL BUTTON
*Build third. Independent of everything else, immediately better.*

**Measured today:**

    ← All ships    76 x 22 px   15px/700   orange text   background: TRANSPARENT
    ship title    196 x 30 px   21px/700

**A third the size of its neighbour, at the same weight, with no shape at all.** The
eye reads the ship name and never registers the link.

**But size is the symptom. The fault is that three intents share one corner and the
wrong one got the smallest control:**

    "I know which ship I want"     the 349-option dropdown       425 px
    "show me the one beside it"    does not exist yet            (4)
    "let me go and browse"         a 76 px text link             <- the way out

**Build it as:** a bordered button at header-control size, top-left where a home
affordance is expected, using the site accent **as its border rather than as a fill**.

**Label it with what is behind it.** *All ships* is thinner than the thing it opens.
**Browse all 349 ships** earns its width by carrying a number nothing else on the
page states, and it tells a first-time visitor that the site is a catalogue rather
than one page.

**The caution matters as much as the change: it must not become the loudest thing on
the screen.** The hull is the loudest thing. **Bordered, not filled** — enough to
stop it disappearing, not enough to compete.

**And do not add a second way back.** A breadcrumb, a hamburger and a link are three
answers to one question on a page that already has ten controls.

---

### (1) THE RAILS COLLAPSE TO ICON STRIPS
*Build fourth, WITH (2). Requires (3).*

**Measured today: the two rails are 419px and 381px — 42.0% of the width, permanent.
The ship gets 34.9% of the viewport.**

**Both rails default closed**, as ~48px vertical strips of group icons — weapons,
shields, power, cooling, quantum, and one for the readout. **The stage is the page.**

    ship area today          34.9% of the viewport
    with rails collapsed     ~72%          - roughly double

**Behaviour:**

    click an icon      that panel slides out OVER the stage, at the width it needs
    one at a time      opening a second closes the first
    click the stage    closes the open panel
    remembered         the open/closed state persists per visitor (local storage)

**Over the stage, never pushing it — this is (3) restated.** A panel that pushes
resizes the canvas, which reframes the camera. **A panel that floats leaves the hull
exactly where the operator put it.**

**Nothing is deleted.** Every row, every number, every explanation survives. **Only
the resting state changes.**

**It also collapses three scroll regions into one.** Measured today: `.col.left` shows
650px of 1,448px, `.col.right` 650px of 1,309px, and the amber note **76px of 121px**
— a wheel trap sitting exactly where the pointer rests under the model. **With rails
closed the stage does not scroll, the open panel does, and nothing else exists to
steal the wheel.**

**The real risk, named:** a wide hull fills the frame and an overlay lands on top of
it. **Mitigations:** one panel at a time; anchor panels to the edge the hull is
thinnest at; keep the existing scrim. **Prototype on the Vulture and the Polaris
before committing** — a light salvage hull and a capital frame bracket the shapes.
**That question is answered by looking, not by arguing.**

---

### (2) SWAP AT THE DOT
*Build with (1). Requires (3).*

**The mounts on the hull are already bound to `PortId`, and 259 of 316 hulls carry
markers — 6,058 of them.** Clicking a dot and clicking its list row already open the
same panel. **This change makes the dot the primary route rather than the alternate
one.**

    click a mount      the fitting options appear BESIDE that dot, on the stage
    choose             the part swaps; the camera does not move; the changed
                       figure marks itself
    the left list      remains the way in for everything with no dot

**Why the dot beats the row, and it is the §0 argument exactly:** a dot is a *stable
target*. It is in the same place on the hull every time. **A list row in a scrolling
column is not, so muscle memory can form against the model and cannot form against
the list.** For an operator running the loop thirty times, that is the difference
between fast and tiring.

**THE FALLBACK IS NOT OPTIONAL — 57 hulls have no markers.** On those the model
cannot be the interface at all. **Handle it as a default rather than a special
case:** a hull with markers opens with rails closed; a hull without opens with the
parts rail already open. **Same page, same code, no branch — just a different
starting state.**

**Internals stay off the model** — power plant, coolers, shield, quantum drive are
not walked up to in-game. **That is the standing architecture decision and this does
not reopen it.** They live in the rail panel, which is what the rail is for.

---

### (5) PER-SHIP MEMORY
*Build fifth, BEFORE (4). It is the half of (4) that stops it being harmful.*

**Measured: the URL is `/loadout#AEGS_Avenger_Stalker|,,,,,,|,,,,,,` — the ship AND
the whole loadout live in one hash.** Switching ships is an in-place re-render, not a
navigation, and hash changes already push history.

**So next/previous built the obvious way replaces the hash and DISCARDS the build.**

**For a display that is acceptable. For the minmax bench it is the worst possible
behaviour** — the build is the entire reason the operator is there, and a navigation
control that silently bins it gets used once and never again.

    configure a Vulture  ->  flip to the next ship  ->  flip back
    the Vulture is EXACTLY as it was left

**Held in local storage, keyed by ship, for the session. Cleared by the existing
*Back to stock*.** The URL hash keeps doing what it does today so shared links are
unaffected — **memory is a convenience layer over it, never a replacement.**

**One thing to decide rather than assume:** whether memory survives a browser
restart. **Session-only is the safer default** — a build you forgot you made,
reappearing a week later, is its own kind of wrong. Recorded as a choice, not a
recommendation.

**Rule 12:** configure, flip away, flip back, assert every slot matches. **It must be
shown failing against a build without memory**, which is today's build, so the
failing case is free.

---

### (4) NEXT AND PREVIOUS
*Build last, with (5) already in place. Requires (7) for the header room.*

**Sleven's ask, taken literally, and it should be: two controls. No carousel, no
filmstrip, no "related ships" rail. The restraint is the feature.**

    ‹  Drake Cutlass Black          [ ship title ]          Drake Herald  ›

**Show the destination's NAME, not a bare arrow.** A control you can read is one you
will use without testing it first — and on a page with 349 ships, an unlabelled
arrow is a dice roll.

**Bind the left and right arrow keys.** An operator comparing hulls will not keep
reaching for a mouse target. This is the §0 test applied directly.

**THE QUESTION THAT DECIDES WHETHER IT FEELS RIGHT: next in what order?**

**This is not a detail.** An arbitrary order makes the control useless, because the
next ship is a surprise every time and no expectation can form.

    a  alphabetical across all 349    predictable, and nearly always useless -
                                      the neighbour is a different class entirely
    b  THE LIST THE VISITOR CAME FROM      <- build this
    c  same manufacturer              a narrower special case of b

**Build b.** Arrived from *all Drake ships*, next is the next Drake. Arrived from a
search for salvage hulls, next walks the salvage hulls. **The control inherits the
intent the visitor already expressed, and needs no UI to explain itself.**

**And it handles the cold-arrival case honestly:** somebody landing on a shared link
has expressed no intent, so next falls back to alphabetical **and says so** — the
control names the sequence it is walking. **A control that can tell you what it will
do next is not a surprise.**

---

## THE ORDER OF WORK, AND WHY

    D0   the below-fold defect        one property, alone, deploy it       NOW
    ──────────────────────────────────────────────────────────────────────────
    1    (3) camera never moves       precondition for everything
    2    (7) header room              cheap, pays for (4) and (6)
    3    (6) browse button            independent, immediately better
    ──────────────────────────────────────────────────────────────────────────
    4    (1) + (2) together           the big one. Prototype on 2 hulls first
    ──────────────────────────────────────────────────────────────────────────
    5    (5) then (4) together        never (4) alone

**Steps 1-3 are each independently shippable and each leaves the page better.** If
the work stops after step 3, nothing is half-built and nothing is worse.

**Step 4 is the only one that must not be shipped in halves**, and it is the only one
that should be prototyped before it is committed to.

**Step 5 is two names for one feature.** Neither half ships alone.

## WHAT IS DELIBERATELY NOT IN THIS SPEC

- **Any change to what the numbers say.** This is arrangement and interaction only.
- **A second way back**, a breadcrumb, or a ship carousel. §(6), §(4).
- **Markers for the 57 hulls that lack them.** (2)'s fallback handles them as a
  default rather than waiting on data.
- **Anything about the readout's CONTENT.** The stat-card explanations should collapse
  behind the `?` that already sits on each card — that is a disclosure-rule
  consistency fix and it belongs to the earlier proposal, not here.
- **Going live.** Sleven's alone, and he has said the site is not ready.

## WHAT I CHECKED AND WHAT I DID NOT

**Checked, live, in a real browser on the deployed page:** the stage's position at
455px (y=842 of an 898px screen, 2.61 screens of document, all three columns at
`order:0` in source order left/mid/right); the rails at 419 and 381px, 42.0% of the
width; the ship at 34.9% of the viewport; all three scroll regions with their content
heights; the back link at 76x22 transparent against a 196x30 title; the 349-option
dropdown; ten header controls; the URL hash carrying ship plus loadout; and that hash
changes push history.

**Did NOT check:**
- **Whether a swap currently moves the camera.** (3) may already be partly true.
  **Ten minutes would tell, and it changes the cost of the first step.**
- **Whether an overlay over a wide hull is readable.** (1)'s named risk. **Not seen,
  and it should be looked at rather than argued about.**
- **Whether local storage is already used** for anything (5) would join.
- **What the comma-separated slots in the hash encode.** I read the shape, not the
  format.
- **How any of this LOOKS.** Screenshots now work through the browser bridge but at
  the docked pane's own width. **Everything here is geometry and structure, not
  appearance.**
- **I have changed nothing**, and I have not touched `NEXT.md`.
