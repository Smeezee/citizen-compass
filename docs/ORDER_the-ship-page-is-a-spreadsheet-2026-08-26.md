# ORDER — the ship page is a spreadsheet

**2026-08-26 · C1 · for Code**
**DO NOT START THIS until F1/F2 from the camera order are deployed and Sleven
has confirmed the hull renders. This is the next job, not a parallel one.**

---

## What Sleven asked for

Four things, in his words:

1. The **left panel** "needs to be reworked somehow. It's way too long. It's
   just a spreadsheet of fucking massive information ... redone with a better
   user readability and understanding ... very simplistic for the user to
   understand what they're looking at."
2. The **right rail**, "possibly do the same thing ... even though I do like
   the one on the right better than the one on the left, but it's not perfect."
3. The **gold provenance box** at the bottom: "needs to be shrunk down into
   something really small ... if they want to know this information, they can
   click it and open it and read it, but that's taking up way too much page."
4. **Switching ships**, especially within a line: "if I'm looking at the
   Avenger Stalker, and I wanna look at the next ship in line to see the
   difference ... the different variants of the Warlock and the Titan and all
   that of the Avenger line, that should be easy to get to."

## What is actually on the page — measured, not estimated

Driven in a real browser at 1600 x 1000 against the built `_deploy` bytes.

**The left column.** Its visible window is 760 px. Its content is:

| ship | rows | of which FIXED | content height | screens of scrolling |
|---|---|---|---|---|
| Aegis Avenger Stalker | 57 | 36 | 1,688 px | 2.2 |
| Aegis Vanguard Harbinger | 88 | 59 | 2,308 px | 3.0 |
| Drake Cutlass Black | 117 | — | — | — |
| RSI Polaris | 305 | 216 | 6,687 px | **8.8** |

Every row is **75 px tall** and carries five separate facts: size chip, item
name, manufacturer, the game's raw port descriptor, and stock/fitted state.

**The right column** is 1,484 px of content in the same 760 px window — two
screens — across 14 stat cards of identical visual weight.

**The ship selector** is a native dropdown with **349 options**.

## The three findings that decide the design

### 1. It is a list of PORTS, not a list of PARTS

The Avenger Stalker shows two MSD-322 Missile Racks, two Ignite II Missiles,
two Tempest II Missiles and two VariPuck S3 Gimbal Mounts — each as its own
75 px row, because each is its own port. **The game has 57 ports. The player
has about fourteen distinct things.**

Collapsing rows that share type, size and fitted part into one row with a
count:

| | today | collapsed | collapsed, editable only |
|---|---|---|---|
| fleet total rows | **26,000** | **9,490** (63.5% fewer) | 3,212 |
| median ship | 70 | 31 | **11** |
| RSI Polaris | 305 | 53 | 9 |
| Aegis Idris-P | 291 | 43 | 6 |
| Aegis Avenger Stalker | 57 | 29 | 14 |
| Anvil Carrack | 100 | 29 | 9 |

**79 ships currently exceed 100 rows. After collapsing, none do.**

### 2. Most of the list is things the visitor cannot act on

216 of the Polaris's 305 rows are fixed ports. 254 of the Idris-P's 291. Fleet
median: **more than half of every list is parts that cannot be changed.**

**This reverses a default, not a decision, and it is stated here so it is not
reversed silently.** The provenance text on the page currently argues fixed
ports are "shown anyway, because a part you cannot change is still part of the
ship and still counts." **That reasoning is correct and is not being
discarded** — the fixed parts stay on the page, reachable in one click, and
still count toward every total. What changes is which of the two audiences the
DEFAULT view serves: someone deciding what to buy sees what they can choose,
and someone auditing the hull opens the rest.

### 3. There is no field in the data that means "same ship family"

Two candidate keys were tested against all 316 ships.

**Hull HP** (`hull`) groups the Avenger Stalker, Titan, Titan Renegade and
Warlock correctly — exactly the four Sleven named — and is clean on 74 of 81
multi-ship groups. **It is still not safe.** Three groups are outright wrong:

    hull 2100      MISC Razor LX  +  Origin 85X
    hull 15350     Anvil Hornet F7CS  +  Crusader Intrepid (+ its Collector edition)
    hull undefined all eight ARGO ATLS variants  +  a PowerSuit

Showing a visitor "Origin 85X" as a variant of the MISC Razor is precisely the
kind of wrong that costs a reference site its credibility.

**ClassName prefix** (first two underscore tokens) is deterministic and never
mis-groups — Avenger, Freelancer, Cutlass, Vanguard, Sabre, Hornet and Mustang
all come out right, 66 groups in total. **But it leaves 61 ships as
singletons**, and it cannot see families whose members are named
independently. The Origin 300 series is the clearest miss:

    ORIG_300i    ORIG_315p    ORIG_325a    ORIG_350r

Four ships everyone in the game treats as one line, four separate groups.

**This is NOT fuzzy matching and must not become it.** The standing rule holds.

---

## The order

### L1 — the left panel

**L1a. One row per part, not per port.** Rows sharing component type, size and
fitted part collapse into a single row carrying a count: `2 x  MSD-322 Missile
Rack · S3`. Expanding the row lists the individual ports, each still carrying
its own PortId, so the hull marker link is unchanged and every existing
per-port behaviour survives.

**L1b. What can be changed comes first; what cannot is one click away.** The
header already says `57 ports · 21 can be changed · 36 fixed` and `36 fixed` is
already a link — make it the control that reveals them. Default view is the
editable set. Fixed parts still count toward every total, unchanged.

**L1c. The row loses two of its five facts.** Name, size and count stay on the
row. Manufacturer and the raw port descriptor (`Weapon missilerack right wing
— 16 fit`) move behind the row's expansion. They are reference detail; they are
not what somebody scans a list for.

**Target: the Avenger Stalker's left column fits on one screen with no
scrolling** — 14 rows against today's 57.

### L2 — the right rail

**Keep what he likes.** The plain-English caption under each number is the
reason he rates this column above the other. It does not go away.

**L2a. Give the cards a hierarchy.** Four headline cards stay full size —
what the pilot can fire, what the ship can survive, how fast it goes, what it
carries. The remaining ten become compact tiles at roughly half height.

**L2b. The caption moves to the `?` on the compact tiles only.** The headline
four keep their caption visible always.

Target: 1,484 px down to about 800 px — the rail stops being a second scroll.

### L3 — the provenance box

Replace the permanent block with a single line under the viewer:

    Where these numbers come from ›

Clicking opens the existing text in a panel, unchanged and complete. **Nothing
is deleted** — the site's premise is that a reader can tell where a number came
from, and that premise is not weakened by putting the explanation one click
away instead of permanently across the bottom of the stage.

This also fixes a defect nobody filed: **the box is currently clipped.** Its
last paragraph is cut off mid-sentence at 1000 px viewport height, so the text
arguing for full transparency is itself unreadable.

### L4 — moving between ships

**L4a. A variant strip under the ship name.** The other ships in this family as
chips, one click each:

    Aegis Avenger Stalker
    also in this line:  Titan · Titan Renegade · Warlock

**L4b. The family key is DATA, not a rule in the page.** Generate a `family`
field in the data layer:

- Base pass: ClassName prefix, first two underscore tokens. Deterministic.
- **Plus a hand-written exceptions file** naming the families the prefix cannot
  see — the Origin 300 series first. Small, reviewable, checked in, and a human
  decision recorded as data rather than inferred by code.
- **Hull HP is not used as the key.** It is a good cross-check and a poor
  identifier; the three collisions above are the reason.
- Every family a ship belongs to is stated on the ship. No matching at
  read time, on the page or anywhere else.

**L4c. The 349-option dropdown becomes type-to-filter.** A native `<select>`
with 349 entries is only usable by somebody who already knows the ship's exact
full name. The optgroups it already has are good and stay.

---

## Sequencing, and the honest cost

**L3 is small.** One line, a panel, and it recovers roughly 90 px of viewer
height plus fixes the clipping. Do it first — it is the cheapest visible win on
the page.

**L4a/L4c are medium** and need L4b's data field first.

**L1 is the real work** and is the one Sleven actually asked for. It touches
the list builder, the row template, the marker link and the totals. It should
not be rushed and it should not be started while the camera fix is unconfirmed.

**L2 is deliberately last**, because he said he already likes that column. It
is a trim, not a rebuild.

**Nothing here changes a single number.** Every total, every source chip, every
CIG-vs-summed distinction is untouched. This is entirely about how much of it
is on screen at once.

Do not deploy the live site. Testing only.

---

## Questions for Sleven

1. **The default view of the left panel** — editable parts only, with the
   fixed ones one click away? That is the recommendation and it is what makes
   the Polaris go from 305 rows to 9. Say so if you would rather the fixed
   parts stayed visible by default and we will collapse only the duplicates.
2. **Collapsed rows with a count** — is `2 x  MSD-322 Missile Rack` the right
   shape, or do you want the two ports to stay visible as `left wing` /
   `right wing` under it by default rather than on expansion?
3. **The variant strip** — chips under the ship name, or would you rather it
   sat with the picture, next to the model?
