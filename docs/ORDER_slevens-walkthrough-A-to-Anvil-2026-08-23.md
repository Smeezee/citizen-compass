# ORDER — Sleven's walkthrough, Aegis through Anvil. Nineteen reports, six causes.

**Sleven walked the ship list alphabetically on 2026-08-23 and reported nineteen
defects.** They are not nineteen problems. **They are six, and most of his
reports are the same few causes seen from different pages.**

**Everything below marked CONFIRMED was checked against the repo before this
order was written.** Where his report and the data disagree, the data is quoted
and the disagreement is stated rather than smoothed over.

---

## W1 — Four ships have no model file at all. CONFIRMED. So do six more he has not reached yet.

**Absent from `sc-ships/` entirely:**

    Tiburon
    Arrow
    F7C-M Super Hornet Heartseeker Mk II
    Odin

**His four "no 3D model" calls are correct, four for four.**

**And the same check found six more he has not walked to yet** — folders that
exist with no model of any kind inside:

    85X · Arrastra · Fury · Mantis · Merchantman · PTV

**Note `Fury` is empty while `Fury LX` and `Fury MX` both have models.** The
same pattern may hold elsewhere; the base name is the one that is missing.

**Do not have Sleven find the rest by hand.** E14 in the errata already orders
the enumeration; this is its first confirmed output and it should be folded in.

    CONTROL: report the full list of ships that appear in the site's ship list
    but have no loadable model, and the reverse - models on disk with no ship
    page. Both directions. State both counts.

## W2 — The Asgard's graphical glitch has a cause, and it is unique in the library. CONFIRMED.

**`Asgard/` contains `image.webp`, `model.ctm` and `model.glb` — but NO
`model_scaled.glb`.** Every other ship that has a model has the scaled file.
**The Asgard is the only one in 234 that does not.**

Sleven: *"Major graphical glitches. Exact cause still needs investigation."*
**This is almost certainly it** — the page is either falling back to the
unscaled mesh or failing partway.

**Separately, and this compounds it:** CIC recorded on 2026-08-22 that **the
Asgard publishes the Valkyrie's dimensions.** So its scale is wrong from two
directions at once.

    CONTROL, load-bearing: state which file the Asgard page actually loads
    today. If it is model.glb, say so - that is the bug. If it is loading
    model_scaled.glb, that file does not exist and the diagnosis is wrong; stop
    and say so.
    CONTROL: after generating the missing model_scaled.glb, assert the Asgard's
    rendered bounding box is in the same range as its neighbours. It has 14
    markers already placed - assert they still land on the hull.

## W3 — "Hardpoints not set up" is thin coverage, not absent data. CONFIRMED, and it contradicts his wording.

He reported the Retaliator, the Sabre Peregrine and all three Ballistas as
having no hardpoints or not being set up. **All of them DO have markers.** The
counts are the problem:

| ship | markers placed |
|---|---|
| Aegis Retaliator | **4** |
| Aegis Sabre Peregrine | **2** |
| Anvil Ballista | **2** |
| Anvil Ballista Dunestalker | **2** |
| Anvil Ballista Snowblind | **2** |
| Aegis Reclaimer | 15 |
| Anvil Asgard | 14 |
| Anvil Hawk | 8 |
| Anvil Hurricane | 8 |
| Anvil Valkyrie | 5 |

**A Retaliator with four markers reads to a visitor exactly like a Retaliator
with none.** That is a torpedo bomber with turrets; four is indistinguishable
from broken.

**Two separate things to fix and they must not be conflated:**

1. **Raise coverage** where the placement pipeline resolved only a handful of
   ports. Report, per hull, ports total vs ports with a marker.
2. **Say so on the page.** A hull showing 2 of 30 ports must state that it is
   showing 2 of 30. Right now the reader cannot tell thin data from broken code,
   and Sleven could not either — which is why this arrived as five separate
   bug reports instead of one.

    CONTROL: report the ports-with-markers / ports-total ratio for all 159
    hulls that have markers. Name every hull under 25%.

## W4 — Six ships have no markers at all, and they are the SAME six that fall through to RSI links. CONFIRMED, and the overlap is the finding.

**Zero markers, not present in `loadout_marker.gen.js`:**

    Eclipse · Nautilus · Vulcan · Crucible · Legionnaire · Liberator

**Sleven's separate complaint** — *"still has its RSI link"*, *"no ship page,
only links to the RSI website"* — **names Nautilus, Vulcan, Crucible,
Legionnaire and Liberator. Five of the same six.**

**That is not a coincidence and it should be treated as one root cause, not
two.** The hypothesis: these hulls are not fully registered in the site's ship
data, so they get neither a marker set nor an internal page, and the front end
falls back to an external link.

**Do not fix the symptom on each page.** Find the single place a ship becomes
"real" to the site and report why these six do not qualify.

    CONTROL, load-bearing: state the mechanism by which a ship gets an internal
    page rather than an RSI link, and show why each of the six fails it. If the
    six fail for DIFFERENT reasons, the single-cause hypothesis is wrong - say
    so and treat them separately.
    NEGATIVE CONTROL: name a ship that passes the same check and gets a proper
    page, and show what it has that these six do not.

## W5 — Sleven's own design ruling, and he is right

> *"We should be able to provide ship information even without a 3D model."*

**A missing model must not cost a visitor the stats, the loadout, the prices or
the where-to-buy.** The model is one panel on a page full of data that does not
depend on it.

**Any ship without a model gets its full page, with an honest empty state in the
model panel** — the same shape as the existing "no measured positions" notice,
which is already the right pattern.

## W6 — Two single-ship defects

**Aegis Reclaimer** — *"One of the front hardpoints is listed as the wrong item
on the salvaging tool."* A named component is wrong on a specific port. Identify
the port, state what it currently resolves to and what it should be, and say
whether the error is in the source data or in the resolution step. **Do not
patch the display.**

**Aegis Tiburon** — no background picture as well as no model. Note that the
`Tiburon` folder is absent entirely, so it has no `image.webp` either. Same root
as W1.

**Anvil F7C-M Super Hornet Heartseeker Mk I** — has a model on disk, but no
clickable link to its 3D model page. **The asset exists and the route to it does
not.** Likely the same registration gap as W4 — check it against that mechanism
first rather than treating it as a separate link bug.

## W7 — Marker placement accuracy, reported but unverified

**Anvil Hawk** — *"Hardpoints may be misplaced in the add-ons. Needs
verification."* It has 8 markers. This is a placement-quality question, not a
presence question, and it belongs with the scatter work rather than here.

**Do not act on "may be" without measuring.** If a check for marker-on-hull
placement does not already exist, that is the deliverable, not a per-ship
adjustment.

---

## TWO THINGS FOR SLEVEN, NOT FOR CODE

**Item 15 on his list is unresolved.** Voice-to-text produced *"invoice card"*
for an Anvil ship between the Hawk and the Legionnaire, reported as *"hardpoints
do not line up correctly"*. Alphabetically that lands on the **Hurricane** or a
**Hornet** variant. **Per his own standing rule, proper nouns are asked, not
guessed.** No work should be scheduled against this line until he names it.

**Item 19, the Anvil Valkyrie Liberator, is answerable.** It is the **Valkyrie
Liberator Edition**, a limited variant of the Anvil Valkyrie. **We have a model
for it on disk** — `Valkyrie Liberator Edition/` is complete with all four
files. Its problem is the missing ship page, which is W4, not a mystery about
what the ship is.
