# ORDER — there is ONE ship page. Collapse the second one into it. RUN CONTINUOUSLY.

    from    C1, 2026-08-22
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
              **Testing deploy at the end is now automatic** - the standing rule
              you adopted at D1. Do not ask.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md, items N-.

---

## 0. WHAT IS WRONG, AND IT IS C1'S FAULT NOT YOURS

Sleven, looking at the deployed build: **"why do i have to click to a new screen
what cant we make them one page"**.

He is right. **There are two ship views and two 3D viewers.**

    _layer.src.html (index)   ship panel · its own cc_viewer instance ·
                              Acquisition (in-game price, pledge price, Sold at,
                              View on RSI) · Record (confidence, last verified) ·
                              a slot-structure summary · Related ships ·
                              and a button "Open in the loadout bench ↗"

    loadout.src.html          the real ship page · its own cc_viewer instance ·
                              tabs (Loadout · Engineering · Liveries ·
                              Where to buy · Specs) · the full readout ·
                              the pickers

**L9 said "do not build a third page." It never said "retire the second one."**
You obeyed it exactly and left the old panel standing. The defect is in the
order's wording, not in your reading of it. **L8 is also satisfied and still
produced this** - `cc_viewer.js` is genuinely one implementation; it is just
instantiated on two pages. One implementation, two ship pages. Technically
correct, practically wrong.

## 1. THE RULING

**A ship has ONE page and it is the one built on `loadout.src.html`.**

`index` is the **list** - the matrix, the search, the browse. **Clicking a ship
name opens the ship page directly.** No intermediate panel, no second click, no
second model load.

## 2. THE WORK

**N1. THE SHIP NAME OPENS THE SHIP PAGE.** Every route into a ship - the matrix,
search, the Related strip - lands on the ship page. **Delete the
"Open in the loadout bench ↗" button.** There is nothing left to open it from.
*Control:* no path from the list reaches a ship without landing on the ship page,
asserted over every entry point that exists.

**N2. MOVE THE ACQUISITION BLOCK ONTO THE SHIP PAGE. Lose nothing.**
Everything the old panel carried has to survive the move:

    In-game price · Pledge price · Sold at · View on RSI
    Confidence · Last verified · Record number
    the slot-structure summary and its provenance note
    Related ships

**Where each goes:**
- **Price, pledge price and the RSI link belong in the ship page header** - the
  first things somebody wants and the reason they arrived.
- **Sold at, and the shop detail, go in the `Where to buy` tab** - that tab
  already exists and this is what it is for.
- **Confidence, last verified and the record number** go with the provenance the
  page already shows. Do not invent a second provenance treatment; there is one.
- **Related ships** goes at the foot of the ship page.
*Control:* every field listed above is present on the ship page and reachable.
**Name them one at a time in the ledger and tick them off.** A field silently
dropped in a consolidation is the exact failure this control exists to catch.

**N3. RETIRE THE INDEX SHIP PANEL AND ITS VIEWER.**
Remove the panel and its `cc_viewer` instance from `_layer.src.html`. **Index
loads no 3D model at all** - it is a list.
*Control:* opening the index fetches **no** model geometry. Watch the network,
do not assume. That is the measurable half of "one page".
**Keep the left sidebar** - Ship Purchase Matrix, Development Progress, Sale
Calendar, Legend & Sources are site navigation and belong on the list.

**N4. THE SHIP PAGE OPENS ON THE MODEL, PER SLEVEN'S EARLIER RULING.**
*"I want the 3D model of the ship to be the main focus but then they'll be the
abilities."* The model leads. The readout follows. The tabs are below that.
**Do not let the A/B comparison become the headline** - one build is the subject,
comparison is a feature you turn on.

**N5. ONE VIEWER INSTANCE, ONE MODEL LOAD, PER SHIP VIEW.**
*Control:* opening a ship fetches its geometry **once**. Moving between tabs
fetches no further geometry and does not reinitialise the viewer.

**N6. SWEEP + DEPLOY.** Every control in `checks/`, then deploy to testing per
the standing rule, then **verify from the served bytes** that index carries no
viewer and that a ship name lands on the ship page. Record the URL.

## 3. WHAT MUST NOT HAPPEN

- **Do not build a new page.** N1. There is one, and it already exists.
- **Do not drop a field in the move.** N2. Tick them off by name.
- **Do not leave a second viewer on index.** N3.
- **Do not make A/B the headline.** N4.
- **Do not deploy the live site. Do not cut a release. Do not `git add -A`.**

## 4. REPORT

- The N2 checklist, field by field, ticked.
- The network trace: what index fetches now, and what a ship page fetches.
- Anything here you think is wrong. **N2 is the part most worth arguing with** -
  if a field genuinely has no good home on the ship page, **say which and why**
  rather than quietly leaving it behind on a panel nobody can reach.
