# PRE-LIVE PUNCH LIST

    started  2026-08-22, at L16 of ORDER_the-ship-page-2026-08-22-FINAL
    rule     EVERY ENTRY CARRIES A NUMBER and says whether it BLOCKS going
             live. An entry with no number is a feeling, and a list of
             feelings cannot be worked through.
    scope    Every page, dataset and empty state on the testing site.
    keep     Maintained. When a number moves, move it here.

---

## HOW TO READ THIS

**BLOCKS** means: shipping with this unfixed would put something on a public
page that is wrong, invented, or reads as broken. Three of those are on this
list.

**DOES NOT BLOCK** means: it is a real gap, the site says so out loud where a
visitor meets it, and an honest gap is not a defect. Most of this list is that.
This project's standard is that we may not know something; it is not that we
must know everything before we open.

---

## BLOCKS GOING LIVE

### 1. Nothing in the shop layer is VERIFIED — 0 of 7,932 shop items, 0 of 823 terminals

`FIND_COUNTS` reads `shop_items_verified: 0` and `terminals_verified: 0`
against 7,932 items and 823 terminals. 26,657 price rows are on the page and
not one of them has been checked against the game by a person.

**Why it blocks:** /find is where a visitor reads a number and then spends real
time flying somewhere. Every other honest-gap entry on this list costs somebody
a shrug. This one costs them a trip.

**Not "verify all 7,932".** Verify enough to state a rate, and put the rate on
the page.

### 2. The live worker still 404s

The testing site is deployed and gated. The live URL serves nothing.

**Why it blocks:** it is the definition of not being live.

### 3. Sleven has not opened the ship page in a browser

Every control on it proves LOGIC and RENDERED HTML. **No control on this
machine proves that a browser draws anything**, because there is no browser
here and none was installed (rule 7). The 3D viewer, the hull markers, the
tabs and the CSS have never been seen.

**Why it blocks:** the markers are positioned by projecting hull coordinates
onto a canvas every frame. That is exactly the kind of thing that is right in
the arithmetic and wrong on the screen.

---

## DOES NOT BLOCK — real gaps, stated on the page where a visitor meets them

### Ships and models

| # | Gap | Where it shows |
|---:|---|---|
| **25** | models whose name matches no mount-data key — no hardpoints derivable | ship page says no mount positions measured |
| **8** | models refused by the alignment gate (proportions vs published dims) | same |
| **4** | models the dataset holds with no mounts listed | same |
| **44** | hulls with a model and NO hull markers (the three rows above, plus ambiguity drops) | ship page states it, list-driven swapping still works |
| **115** | hulls with a game file and no 3D model — L14 case 1, e.g. **Origin M80** | "No 3D model available for X", full readout unaffected |
| **33** | ships CIG has not built at all — L14 case 2 | listed, disabled, reason given, nothing claimed about loadout |
| **20** | of 221 linked ships carry no model | as above |
| **0** | `unchecked_hull` — **this is now zero.** The order listed 21; the G3 geometry rebuild and the current alignment gate have closed it. | — |

### Ports and components

| # | Gap | Where it shows |
|---:|---|---|
| **134** | editable ports whose type has NO catalogue part at that size | rendered, marked `nofit`, says the game files list no part |
| **6,454** | ports genuinely EMPTY in the game files | rendered as empty, which is what they are |
| **1,450** | parts CIG has never given a display name (`<= PLACEHOLDER =>`) | named from their className, marked, never offered in a picker |
| **48** | ports where CIG's own fitted part fails CIG's own declared rule | the stock part is offered anyway; the game mounts it there |
| **14** | hull-marker points dropped as ambiguous | no marker; the list still reaches the port |
| **1,092** | ports accepting `WeaponPersonal` with **no catalogue to fill them** | out of scope — the catalogue is UEX data, not `ship-items.json` |

### Armour and liveries

| # | Gap | Where it shows |
|---:|---|---|
| **11** | records with no armour port — 9 exosuits, plus **Greycat PTV** and **Aegis Idris-P** | armour panel says the files list none |
| **31** | armour items no ship fits | not carried |
| **46** | hulls with a paint port CIG left untagged, so no livery can be stated | livery panel says the files list none |
| **79** | liveries under 9 tags (`Paint_Aurora`, `Paint_Cutlass`, `Paint_400i`, `Paint_Apollo`, `Paint_Hermes`, `Paint_Omega`, `Paint_Wolf`, `Paint_Pisces_Expedition`, `ANVL_Hornet_F7A_Mk2`) that **no port asks for** | unreachable; nobody can fit them |
| **1** | port tag (`300_Seat_Paint`) no livery answers | — |

### Schema

| # | Gap | Where it shows |
|---:|---|---|
| **0** | fields in `app/models.py` for hull damage resistance. `damage_type` exists on weapons — the attacking side — and **nothing for the defending side.** L5's whole dimension is absent from the database. | The ship page reads generated data, so the page is complete; **the database is not.** Anything built on the DB will not see armour. |

### Keybinds

Modes and devices the page dims, rather than pretending to support: carried by
`kb_modes.gen.js` across FLIGHT, ONFOOT, EVA, VEHICLE, CAMERA and SOCIAL, each
with its own `_UNBOUND` list. **Dimming is the honest state and it is already
what the page does.**

### Careers with no component behind them

Four careers have ships and no fittable component that serves them:
**Medical (16 ships), Passenger, Repair, Construction.**

**These are HULL PROPERTIES, not builds.** A medical ship is medical because of
its beds and its bay, not because of anything you bolt on. So the ship page
must **say that** rather than offer a dead control — and today it offers no
control at all, which is correct but silent. **Saying it is the work.**

### The testing site's password gate is on index.html only

Measured 2026-08-22 against the deployed origin:

| path | gate present | serves |
|---|---:|---:|
| `/` | **yes** | 200 |
| `/loadout` | no | 200 |
| `/find` | no | 200 |
| `/keybinds` | no | 200 |
| `/holo` | no | 200 |
| `/download` | no | 200 |
| `/stick-test` | no | 200 |

**Pre-existing** — the gate has been index-only since it was introduced, and
`build_deploy.py` injects it into the assembled `index.html` and nowhere else.
Every page in `PAGES` is copied verbatim and none of them has ever carried it.

**It matters more now** than it did, because the ship page is the largest thing
behind that "private preview" and it is reachable by anyone with the URL.

**DOES NOT BLOCK the live site** — the gate is a testing-site device and the
live payload deliberately carries none. It is on this list because the phrase
"private preview" is doing work in the standing testing-deploy rule
(`docs/ARCHITECTURE_DECISIONS.md`) and the preview is less private than it
sounds.

### Ship-page layers that exist as shells

The ship page is tabbed layers with per-layer lazy loading. Some layers are
built, some are a mechanism waiting for data.

| Layer | State | Number |
|---|---|---:|
| **Loadout** | built, and it is the default view | 25,875 ports |
| **Engineering** | built — relays and fuse slots | 678 relays / 1,419 fuses on 305 hulls |
| **Liveries** | built | 915 liveries in 104 hull sets |
| **Specs** | built | dimensions, mass, career, role on 316 |
| **Where to buy** | built as far as the data honestly allows | says what is known and links to FIND |
| **Crew** | **SHELL. No data. Suppressed on all 316 ships.** | 802 seat ports exist and are unread |

**A shell is not a gap in the site; it is a gap in this list.** The Crew tab
appears on no ship, so nobody meets an empty layer. What it costs is that 802
seat ports, 387 pilot seats and 140 bedding positions are in the snapshot and
nothing reads them. `docs/IDEA_unused-ship-data.md` §1 is the design.

**DOES NOT BLOCK.**

### The ship page's payload, and the change that would actually fix it

Per-layer lazy loading is built and it saves **4.4 KB of a 274.8 KB page** —
1.6%. The weight is not in the layers, it is in the ships.

| | gzipped |
|---|---:|
| what the page loads today | 274.8 KB |
| one ship's complete bundle, median | 10.1 KB |
| the ship index for the picker | 3.6 KB |
| **a page that loaded one ship** | **~14 KB** |

**Loading one ship instead of 316 is a 95% cut.** It is not built: 316
generated files, and it touches the deploy guard's allowed-file list. It is a
decision, not an oversight.

**DOES NOT BLOCK** — but it is the largest single improvement available to
this page and it is cheap to describe and moderate to build.

---

## A CLASS OF DEFECT, NOT A SINGLE ENTRY

**`Name` is a label. `ClassName` is the key.** 22 display names are shared by
51 records; a Name-keyed build loses 29 of 316.

This bit **three times in one run** — my own livery check merged the two
Caterpillars, my own diagnostic invented a 999-slot defect that did not exist,
and the ship dropdown rendered "Aegis Hammerhead" twice with no way to tell
them apart.

**Check for it wherever ships are grouped, joined or counted anywhere in this
project.** It is not on this list once; it is a thing to look for.

**Places to look, because this list should name them rather than gesture:**

- any `dict`/`Map` keyed on a ship's display name
- any `SHIPS.find(s => s.name === label)` — index.html had one, and it is why
  `CC_LOOKUP` and `ship_resolution.json` exist
- any `GROUP BY` on a name column in the database
- any report that counts "ships" and gets 287 instead of 316
- any join between two datasets that meets in the middle on a name

**The tell is a count that is lower than it should be and looks plausible.**
316 records becoming 287 does not throw, does not warn, and looks like a
reasonable number of ships.

The same shape one level down: **a hardpoint name is not unique within a
ship.** 287 of 316 hulls have slots sharing one, 11,283 slots in all, and the
RSI Polaris has thirty ports called `MEC`. `PortId` is unique across all 57,759
ports and is what any port-level join must use.

---

## WHAT I THINK ACTUALLY BLOCKS GOING LIVE

Of everything above, **three**: the unverified shop data, the dead live worker,
and the fact that nobody has opened the ship page in a browser.

Everything else on this list is a gap the site states out loud at the point a
visitor meets it. That is the standard this project set — *if we can't verify
it, we say we can't verify it* — and a list of honestly-labelled gaps is not a
reason to stay closed. **Shipping with them is the standard working. Shipping
with unverified prices is the standard failing.**
