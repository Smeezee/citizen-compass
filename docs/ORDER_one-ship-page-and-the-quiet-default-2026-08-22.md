# ORDER — one ship page, and it opens quiet. RUN CONTINUOUSLY.

    from    C1, 2026-08-22, after a long design conversation with Sleven.
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
              **Testing deploy at the end is automatic** (D1 standing rule).
    ledger  APPEND, items N-.

    SUPERSEDES docs/ORDER_one-ship-page-not-two-2026-08-22.md, which you have
    read but not started. Its N1-N6 are carried forward here, unchanged in
    intent, plus everything Sleven ruled after seeing the deployed build.

---

## 0. THE PRINCIPLE. Everything below is an instance of it.

**THE PAGE OPENS AT ITS SIMPLEST TRUE STATE. EVERY EXTRA LAYER IS SOMETHING THE
PERSON ASKS FOR.**

Sleven, on what the page should feel like:

> "Kinda like how a video game holds your hand in the beginning so you learn what
> you do, but it makes it seem like you're doing it yourself. Well, it's just
> guiding you."

> "The users gotta enjoy what they're doing. Enjoy looking at what they're
> looking at. Understand what they're looking at."

**That is the acceptance test for this whole order.** If a person has to be told
what they are seeing, it is wrong.

**The tutorial is the numbers moving.** Nobody has to be told a cooler changes
their heat signature. They swap one, IR drops, weapon power drops with it, and
they have learned the mechanic by doing it. **That is the entire lesson and it
needs no text.**

**What this RULES OUT, and these are hard noes:** no welcome modal. No guided
tour. No "click here to get started" overlay. No arrows. **Every one of those
announces that somebody is being taught, which is the exact feeling this design
exists to avoid.**

## 1. ONE SHIP PAGE. The second one goes.

**Carried from the superseded order, and the diagnosis stands:** there are two
ship views and two `cc_viewer` instances. `_layer.src.html` has a ship panel with
its own model, Acquisition, Record, a slot summary and a button reading "Open in
the loadout bench ↗". `loadout.src.html` has the real ship page.

**L9 said "do not build a third page." It never said "retire the second one."**
The defect is C1's wording. You obeyed it exactly.

**N1. THE SHIP NAME OPENS THE SHIP PAGE.** Every route in — matrix, search,
Related strip — lands on the ship page. **Delete the "Open in the loadout
bench ↗" button.**
*Control:* no path from the list reaches a ship without landing on the ship page.
Assert over every entry point that exists.

**N2. MOVE THE ACQUISITION BLOCK ACROSS. LOSE NOTHING.**

    In-game price · Pledge price · Sold at · View on RSI
    Confidence · Last verified · Record number
    the slot-structure summary and its provenance note · Related ships

- **Price, pledge price and the RSI link → the ship page header.** First things
  somebody wants, and the reason they arrived.
- **Sold at and shop detail → the `Where to buy` tab.** It exists for this.
- **Confidence, last verified, record number → with the provenance the page
  already shows.** One provenance treatment, not two.
- **Related ships → the foot of the ship page.**
*Control:* **name every field above in the ledger one at a time and tick it off.**
A field silently dropped in a consolidation is exactly what this catches.

**N3. RETIRE THE INDEX PANEL AND ITS VIEWER.** Index is a **list**. It loads no
3D model at all.
*Control:* opening the index fetches **no** model geometry. **Watch the network.
Do not assume.** That is the measurable half of "one page".
**Keep the left sidebar** — Ship Purchase Matrix, Development Progress, Sale
Calendar, Legend & Sources are site navigation.

**N4. ONE VIEWER INSTANCE, ONE MODEL LOAD PER SHIP.**
*Control:* opening a ship fetches its geometry **once**; moving between tabs
fetches no further geometry and does not reinitialise the viewer.

## 2. THE PAGE OPENS ON ONE BUILD. Ruled by Sleven.

> "The build A and build B, I don't think that needs to be there. It should only
> be a feature if the user wants to see it."

**N5. ONE BUILD BY DEFAULT.** The second build does not exist until asked for.
**The button reads exactly: `Try another alongside`.**
Chosen deliberately — *try* is an experiment rather than a decision, and
*alongside* promises the current build is not going anywhere. **Do not reword
it.** "Compare builds" was explicitly rejected.
**When open, the second panel carries `Discard this one`** — says what happens
and which one goes. Not a bare "Remove".
**A and B labels appear ONLY once the second build exists.** Before that there is
just the ship — no letters.

**N6. KILL THE DOUBLED READOUT.** Every stat currently renders twice with `same`
beside it, fourteen times over. **With one build there is one number.**
*This is not only space.* When everything says `same` all the time, **nothing
catches the eye when something finally is not** — which breaks §0's tutorial.
*Control:* a default ship page shows each stat exactly once.

## 3. FIXED COMPONENTS FOLD AWAY. Ruled by Sleven.

> "It's got thrusters listed as things you could click them, but they're fixed...
> Users don't need to see that information... I'm not saying get rid of them, but
> we need to find a way to tuck them away."

**N7. FIXED PORTS COLLAPSE INTO A CLOSED DISCLOSURE**, labelled with its count —
e.g. `Fixed · not swappable in game (14)`. Open on request. **They still count
toward the readout**, because a thruster affects mass whether or not you chose it.

**N8. THE GROUPING IS DRIVEN BY `Editable`, NEVER BY A LIST OF TYPES.**
**This is the load-bearing half and it is Sleven's own reasoning:** *"if ever it
changes, we already have a foundation built for it."* The day CIG makes fuel
tanks swappable, that component leaves the collapsed group **on the next data
build, with nobody editing code.**
*Control:* flip `Editable` on a fixed port in a test fixture and confirm it moves
out of the collapsed group **with no code change**.

## 4. THE MARKERS ARE ESTIMATED AND THE PAGE MUST SAY SO.

**N9. THE PAGE CURRENTLY MAKES A FALSE CLAIM. Fix it first.**
It says: *"Slot structure measured from this hull's own model geometry and the
game's mount data. Nothing here is estimated."*

**The slot STRUCTURE is real** — count, size, type, all measured. **The DOT
POSITIONS are not.** `place_fleet.py` derives every marker from the hardpoint's
NAME: it reads `hardpoint_weapon_wing_left`, looks "wing" up in a table of target
zones, places a point in that zone of the bounding box, snaps to the nearest hull
vertex, then spreads collisions apart — 17 were "crowded" and pushed.

**And it cannot currently be better.** C1 opened an exported model: **one node,
`Mesh_0`.** No hardpoint nodes, no empties, everything welded into one mesh.
**The real positions are not on disk to read.** The derivation is not laziness;
it is the only thing possible with these exports.

Two parts ARE measured and stay described as such: **which axis is
length/width/height** (checked against CIG's published dimensions, disagreements
skipped rather than guessed) and **which end is the nose**.

**Say it plainly, in the page's own voice:** the marker positions are placed from
the mount's name, not measured from the model. **Do not soften it and do not
bury it.**
*Control:* no wording on the page states or implies a marker position is measured.

**Not ordered here, and NOT to be attempted:** re-exporting models with
hardpoints preserved, or hand-placing in Blender. **Sleven has not decided which,
and it turns on whether the extraction tool can keep hardpoint data — a question
he is answering.** Do not start either.

## 5. TEACHING BY CONSEQUENCE

**N10. THE FIRST SWAP MUST BE UNMISSABLE.** When a part changes, **what moved
announces itself for a beat.** If numbers settle quietly into new values the
moment passes and nothing was learned. This is §0 made concrete.
*Control:* one swap, and the changed readouts are visibly distinguishable from
the unchanged ones without reading them.

**N11. GETTING BACK TO STOCK IS ALWAYS ONE VISIBLE CLICK.** Not in a menu.
**Failure has to be free or nobody experiments**, and experimenting is how the
page teaches.
*Control:* from any modified build, one visible control returns the ship to its
own stock loadout, port for port.

**N12. SWEEP + DEPLOY.** Every control in `checks/`, then deploy to testing per
the standing rule, then **verify from the served bytes**: index carries no
viewer, a ship name lands on the ship page, and the page opens with one build.
Record the URL.

## 6. WHAT MUST NOT HAPPEN

- **No welcome modal, tour, or "click here" overlay.** §0. Hard no.
- **Do not build a new page.** N1.
- **Do not drop a field in the move.** N2. Tick them by name.
- **Do not leave a viewer on index.** N3.
- **Do not reword `Try another alongside`.** N5.
- **Do not group fixed components by a hardcoded type list.** N8.
- **Do not claim a marker position is measured.** N9.
- **Do not start re-exporting or hand-placing models.** N9.
- **Do not deploy the live site. Do not cut a release. Do not `git add -A`.**

## 7. REPORT

- The N2 checklist, field by field, ticked.
- The network trace: what index fetches now, what a ship page fetches.
- The N8 control: what happened when you flipped `Editable`.
- Anything here you think is wrong. **N10 is the part most worth arguing with** —
  making a change announce itself is easy to overdo into something irritating on
  the twentieth swap, and you will see that boundary before C1 does.
