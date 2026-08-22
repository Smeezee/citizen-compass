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

### Ship page payload

The default ship page ships **3.5 MB raw / 275 KB gzipped** of loadout data,
against 431 KB / 37 KB before this order. The growth is scope, not bloat — 25,875
ports instead of ~4,300 slots of five types — but it all arrives whether or not
anybody opens a tab.

**The addendum's per-layer loading (§2, M1) is the answer to this**, and it is
measured there rather than assumed here.

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
