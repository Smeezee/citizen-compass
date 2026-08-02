# BUILD PLAN — Citizen Compass front end

**For Claude Code. Prepared by Claude-02, Cowork session 2026-08-01/02.**

This is a plan, not an order. It specifies what to build and why. Four working
prototypes already exist on disk as reference implementations — use them for
layout and behaviour, replace their invented data with real data.

---

## 1. STATUS OF WHAT ALREADY EXISTS

| file | what it is | data |
|---|---|---|
| `testing/_src/find.src.html` | search + item page + shop page | **all invented** |
| `testing/_src/loadout.src.html` | A/B component comparison | **all invented** |
| `testing/_src/keybinds.src.html` | keybinding reference + live tester | transcribed from screenshots, **unverified** |
| `testing/_src/kb_overlay.inc.html` | keybind overlay, spliced into the layer | same |

Every one runs, has been tested headlessly, and is deployed to `_deploy/`.
**None of them touches real data.** The structures deliberately mirror the real
data shapes so swapping in live data is a data job, not a redesign.

Treat them as executable specifications. If a decision in this document
contradicts the prototype, this document wins — the prototypes were built fast.

---

## 2. THE POSITION — why this is different from what exists

This is the reasoning behind every design decision below. It came from a demand
survey of what people actually search for, run through Claude in Chrome.

**Every competitor is built for someone who already knows the domain.** UEX's
navigation is *Trade Center, Commodities, Routes, Terminals*. Erkul redirects
to a DPS calculator. The wiki gives you a category tree.

**The people searching are not those people.** Real queries, verbatim:
*"star citizen where to buy flight suits"*, *"how much is the idris in game"*,
*"is it possible to buy ships with in-game currency… (I'm new to the game)"*.

So the position is: **plain answers, legibly presented, honest about how sure
they are.** Not more data. Not more features.

Six rules follow from that, and they apply to every page:

1. **Use ordinary words.** "Where to buy", not "Trade Center".
2. **Answer first, detail second.** Open with a sentence, put the table under it.
3. **Make it readable.** The display engine's accessibility profiles are not a
   side feature — they are the product's identity. Half the audience is new and
   overwhelmed already.
4. **Say when you are not sure.** Every price shows its age and its source.
   Nobody else does this and it is the reason to trust us over a confident
   wrong number.
5. **Cover the small things.** Everyone covers ships. People search for flight
   suits, backpacks, ammo, fabricators, medpens — and get nothing useful.
6. **One page per thing, everything on it.** So nobody has to visit three sites
   to answer one question.

**Do not build:** a DPS calculator (Erkul owns it), trade-route optimisation
(UEX owns it), "best ship for mining" opinion content, or 21,849 pages because
the data allows it.

---

## 3. THE DATA, AND WHAT FEEDS WHAT

Six categories, all collected and gated as of 2026-08-02:

| category | what | source |
|---|---|---|
| Things you can own | 316 ships, 21,849 item files, 5,420 FPS gear records, ship components | source 1 |
| Places | 96 systems, 324 planets, 73 moons, 60 stations, 117 outposts, 5 cities, **823 shops**, 1,774 positioned entities with x/y/z and parent hierarchy | sources 1 + 6 |
| Money | **23,734 item prices**, 288 vehicle prices, each tied to a terminal | source 6 (UEX) |
| Who makes it | 311 companies, 152 manufacturers, 74 factions | sources 1, 3, 6 |
| What you do | 5,108 contracts, 1,597 blueprints | source 1 |
| Words | **90,121 labels** — CIG's own names and descriptions | source 1 `labels.json` |

**Join key: Star Citizen UUID.** 5,566 of 7,728 UEX items carry one, and it joins
to `reference` / `stdItem.UUID` in `fps-items.json`. The UEX manifest says so
explicitly: *join on UUID, do not build a name-matching path.*

**UEX is tier C.** Community-reported, ±20% tolerance on commodities and **±100%
on items**. Recorded in its manifest. Never auto-promote it. This is why rule 4
above exists.

### Known data gaps

- **No item images. Zero.** All 7,728 UEX items have an empty `screenshot`
  field and no wiki link. 1,387 (18%) carry an RSI store link. **Design pages
  that work without a picture** and add images by hand only for the items people
  actually search for.
- **No "what it's good for" or "how to use it".** That is writing, not data.
  Roughly 130 of 910 keybinding actions have a CIG-written description; item
  descriptions need checking per source.
- **"Best ship for X" is not in any file.** It is the biggest single demand
  (a 900k-view listicle) and it is opinion. Out of scope for now.

---

## 4. BUILD A — FIND / ITEM / SHOP

**Priority: highest.** This serves the two strongest search intents and three of
the five gaps the demand research identified. Reference: `find.src.html`.

### A1. The search box

Not a filter panel. One text field that takes ordinary English.

**Required behaviour:**

- **Strip filler before matching.** A stop-word list removes: *star, citizen,
  sc, where, to, buy, find, can, i, get, the, a, an, how, much, is, does, cost,
  at, in, on, for, of, do, you, what, price, prices, sell, sells, selling, best,
  in-game, ingame, game, location, locations, shop, shops.* Both
  *"star citizen how much is a medpen"* and *"medpen"* must return MedPen.
- **Match remaining terms against** item name (highest weight), category,
  manufacturer, shop name, and place name.
- **Be location-aware.** *"flight suits new babbage"* must rank items sold at
  New Babbage above ones that are not, and should say why — a small "sold in that
  area" label on the result.
- **Return items, shops and places** in one result list, labelled by type.
- **A failed search apologises and offers suggestions.** It does not blame the
  user. If a real search phrase returns nothing, that is a search bug.

**Test cases — these are real phrases from the demand research and all must
work:** `where to buy flight suits` · `star citizen how much is a medpen` ·
`flight suits new babbage` · `killshot ammo` (must return the **ammo**, not just
the rifle) · `hadanite` · `what sells at area18` · `quantum drive` ·
`where to buy fabricator` · `how much does rmc sell for`.

### A2. The item page

Structure, in order down the page:

1. **Breadcrumb** — Home › Category › Item.
2. **Header** — name, category pill, manufacturer.
3. **One-line description**, from CIG's own words where they exist.
4. **The answer, as a sentence.** *"Sold at 4 shops. Cheapest is Casaba Outlet
   in Area18 at 12,400 aUEC. It sells back for about 9,100."* This is the single
   most important element on the page.
5. **Where to buy it** — table of every shop: shop name (links to shop page),
   location shown as city / planet / system, price. Cheapest row highlighted and
   labelled. **Every price carries its age**; anything a day or older renders in
   amber.
6. **What it sells for** — a separate section, not buried. The research found
   *"how much does X sell for"* is a distinct intent that competitors hide inside
   trade tooling. For items shops do not stock, this section leads instead, and
   the answer line says *"shops don't sell this — you find it out in the world."*
7. **A confidence panel**, in plain English, explaining that prices are player
   reports and gear prices swing widely.
8. **Others in this category** — chips linking sideways.

**The page must look finished when the optional fields are empty.** Most items
will only ever have name, category, shops and price. If the template requires a
picture and a "how to use it", twenty thousand pages look broken. Those four
fields must read as a complete answer on their own.

### A3. The shop page

Same shape, different subject:

- Breadcrumb showing system › planet › city › shop.
- Answer line: *"Stocks 12 things we know about, and buys 3 off you. Cheapest
  here is X at N aUEC."*
- **What they sell** — table linking back to item pages.
- **What they'll buy from you** — separate table.
- **Also at this location** — other shops in the same city.

This directly answers *"what's sold at Lorville"*, which the research found is a
real intent nobody serves.

---

## 5. BUILD B — LOADOUT BENCH

**Priority: second.** Reference: `loadout.src.html`.

### The finding that unblocks it

**Manual Blender hardpoint placement is NOT required for this.**
`ships/drak_vulture.json` carries a `Loadout` array of **85 entries**, each with
`HardpointName`, `Type`, `Grade`, `MinSize`, `MaxSize`, `CompatibleTypes`,
`ClassName` and `Editable`. Every slot, its size range, what fits it, what is
stock, and whether a player can change it — for all 316 ships, from game files.

Blender work is only needed to place 3D markers on the model for the
click-a-turret viewer. That is a separate, later, optional layer.

**Verify this holds across other ships before building on it — one file was
checked.**

### What it does

Two builds of the same ship, side by side, with the difference between them.

- **An outcome bar at the top showing what the ship *does***, not what is
  fitted: DPS, effective HP, speed, quantum range, **IR signature, EM
  signature**, and build cost. Build A and B side by side with a delta on each.
- **Signature is a first-class stat, sized and placed like DPS.** Erkul is a
  damage calculator. Nothing on the market answers *"how visible am I"*, and the
  ship files carry per-component-group emission data (`Emission.IrShields`,
  `EmShields`, `EmGroupsShields` broken down by WeaponGun, Shield, LifeSupport)
  that makes it computable. **This is the differentiator — do not demote it.**
- **Power and cooling budgets, which can go red.** A build that overheats says
  so. Most tools will happily let you design something that cannot fly.
- **Click a slot → a panel of every part that fits**, filtered by the real size
  range and compatible types, sortable by best / cheapest / **quietest**.
- **Hover a part and the outcome bar previews the change** before committing.
  This is what makes it feel alive; do not replace it with click-then-read.
- **Locked slots greyed out**, driven by the real `Editable` flag.
- **A generated shopping list and trip line.** Parts grouped by location, total
  cost, and a cost-per-improvement pass that flags the worst-value change:
  *"Two stops: Area18 for the guns and coolers, then New Babbage for the shield.
  Weakest value: the Cirrus at 510k — drop it and you save that for the least
  gain."* **Nobody else gives you the trip.** Erkul gives you the build.
- **The build encoded in the URL**, so a loadout is a shareable link.

### Entry point

Not a separate destination. A **Loadout Bench** button on the ship page that
opens with that ship already loaded. Same pattern as the ship detail overlay.

### The real dependency

Component comparison is the first feature that genuinely cannot run from a static
HTML file — you cannot bake 21,849 items into a page. **This is what finally
forces the FastAPI backend to serve something public.** It has been running and
powering nothing for weeks.

---

## 6. BUILD C — KEYBINDING REFERENCE

**Priority: third.** Reference: `keybinds.src.html` and `kb_overlay.inc.html`.

### What already exists in your data

- **910 `ui_CI*` keys in `labels.json`** — the exact action names CIG's Advanced
  Controls screen displays. Verified: `ui_CIToggleCruise` = "Cruise Control
  (Toggle)", `ui_CIATCRequest` = "Request Landing".
- **130 of them have CIG-written descriptions.** *"Contacts ATC and other landing
  services."* A user of the competing tool asked for exactly this and its
  developer said descriptions were "not complete… most keybinds will be missing
  a description." **We have better source material than they do.**
- **53 `ui_CC*` keys** — the top-level modes: FLIGHT, ON FOOT, E.V.A., CAMERA,
  Vehicle, plus (Advanced) variants.
- **42 `ui_CG*` keys** — the category groups: Flight - Movement, Flight - Power,
  Vehicles - Mining, E.V.A. - Zero-G Traversal, and so on.

**Everything except the default key assignments is already on disk.**

### What is missing

`defaultProfile.xml`, inside `Data.p4k` (~147 GB, custom archive format —
Python's `zipfile` rejects it on a custom extra field). It supplies four things:
the default binding per action, the modifier definitions, which category each
action belongs to, and **the link between an action's internal name and its
display label**. Without it the 910 names cannot be matched to actions.

`GlebYaltchik/sc-keybind-extract` is a purpose-built extractor worth looking at
before writing one. Three GitHub repos previously reported as holding extracted
default profiles were checked and do **not** (`SC-VRse` is a VR PowerShell tool,
`VectorSigma` is a VoiceAttack profile, `StarCitizenDiff` is unverifiable and
unlicensed). The only public dump found is for 3.0.0 and is years stale.

### Format facts, established by experiment

Two exports were taken from the game, one before and one after changing a single
binding. The difference was exactly one block. Conclusions:

- **Exports contain only changes from default**, never the full set.
- Live bindings live at `USER\Client\0\Profiles\default\actionmaps.xml` and
  always exist. Named exports live at `USER\Client\0\Controls\Mappings\`.
- The two formats differ — exports add a `CustomisationUIHeader` block with a
  device list and categories, and drop the empty joystick instance declarations.
  **An importer must handle both shapes.**
- Input naming: `kb1_down` for keyboard, `js1_button18` / `js1_x` for joystick,
  and **mouse buttons use the keyboard prefix** — `kb1_mouse4`. That last one
  would have been a silent bug.
- To import, a file goes in `Controls\Mappings\` **before launching**, then
  Options → Keybindings → Advanced Controls Customization → Control Profiles.
  Confirmed against RSI's own support documentation. There is also a console
  route, `pp_RebindKeys <filename>`, which bypasses the UI slot limit.

### Scope, and what not to bother with

**Star Binder (starbinder.space) already does the searchable editor**, free, and
imports/exports the XML. Do not rebuild it. Its acknowledged gaps, from its own
roadmap and its users:

- **Visual button maps — on its roadmap, still not delivered.** Ours exists.
- **Descriptions — its developer says most are missing.** We have CIG's.
- Multi-device handling — users report sticks and pedals not detected, axis
  detection needing several tries, device ordering awkward. The developer called
  the device-swap feature "still hamfisted".
- Two devices bound to one action — requested, declined as not worth the effort.
- It is "updated for 4.8" while the game runs 4.9, and skipped 4.7 entirely.

**The category is crowded** — HCS Keybind Editor, DoUrVerse, SC-Binding-Utility,
blackracoon, plus Star Binder. Its developer's YouTube channel has 33
subscribers. Nobody wins this standalone. It is worth building **because it sits
inside Citizen Compass next to the ships and the prices**, not because it beats
five other tools.

### Browser capture limits — real, and worth stating on the page

- Alt+F4, Ctrl+Alt+Del and the Windows key **cannot be captured by any web
  page.** The OS takes them first.
- Ctrl+W, Ctrl+T, Escape and similar need the **Keyboard Lock API**, which
  requires JavaScript-initiated fullscreen. Chrome exits it on a two-second
  Escape hold, and Chrome 130+ prompts for permission. Support is limited —
  Mozilla flags it as experimental and "not Baseline". Build so Chrome and Edge
  get full capture and everything else degrades with a clear message.
- **Use physical key position (`event.code`), never the typed character.** Star
  Citizen binds by position; using the character silently produces broken layouts
  for every non-US keyboard and works fine on yours.
- **Assigning and testing are different jobs.** Even uncapturable keys can be
  assigned and exported — only the press-test is blocked.

---

## 7. ARCHITECTURE DECISIONS ALREADY TAKEN

**Tags, not folders.** Do not copy UEX's category tree — it has a section called
*Consumable* and a *Consumables* inside *Miscellaneous*, and *Other* twice. File
each thing once with tags, then present a small number of plain-language
doorways. A medpen is tagged consumable, medical, carried, emergency and appears
under all of them without being duplicated. This is also the answer to
"where do meds go" — they don't go anywhere, they're described.

**Roughly seven doorways**, named the way people type: Ships · Ship parts ·
Suits & armour · Weapons & ammo · Food, drink & meds · Mining & crafting ·
Places.

**Views are not categories.** "Everything you can eat", "everything sold at New
Babbage", "everything under 5,000 aUEC" are filters over the same tagged pile.
File once, show many ways.

**Components appear in two places.** A quantum drive needs its own item page
*and* appears on the ship pages that use it. People search
*"star citizen quantum drive comparison"* directly; if it only exists as a row on
a ship page, that search finds nothing.

**Shareable state in the URL** for both loadouts and searches. Retrofitting this
is painful; designing it in costs nothing. It is also the mechanism that would
later let a player hand a loadout to the AI Historian — see
`claude/historian-loadout-context.md`.

---

## 8. TWO PROCESS PROBLEMS THAT NEED FIXING FIRST

### 8a. The build does not own the tabs

Three tabs sit on the layer's right edge: `cc-kb-tab` (teal, keybinds.html),
`cc-lo-tab` (blue, loadout.html), `cc-fi-tab` (amber, find.html).

They have been wiped **twice** by rebuilds during this session — at 01:15 and
again at 06:33, the second time including `_src/_layer.src.html` itself, which is
supposed to be the source. Something upstream regenerates it.

**Hand-patching after every build is not workable.** `build_deploy.py` should
emit these three tabs from a small list.

### 8b. The build does not copy the pages

`build_deploy.py` must copy **three** files into `_deploy/`:

    _src/keybinds.src.html  ->  _deploy/keybinds.html
    _src/loadout.src.html   ->  _deploy/loadout.html
    _src/find.src.html      ->  _deploy/find.html

`keybinds.html` was already dropped silently once and restored by hand. Without
these steps the tabs point at 404s and nothing errors.

**Prove both fixes per hard rule 12:** delete the files and remove the tabs, run
the build, assert all six are present afterwards.

---

## 9. SUGGESTED ORDER

1. **Fix 8a and 8b.** Everything else is built on sand until the build is
   reproducible.
2. **Extract `defaultProfile.xml`.** Small, unblocks Build C entirely, and
   removes the last reason anyone is transcribing screenshots by hand.
3. **Wire real data into Build A.** Item page and shop page first, search after —
   the pages are the thing worth finding. This is the highest-demand work and it
   needs the backend serving.
4. **Build B**, once the backend serves components.
5. **Build C**, once the extraction lands.

Parked, documented, not scheduled: the station directory
(`claude/station-directory-plan.md`) and the Historian loadout context
(`claude/historian-loadout-context.md`).

---

## 10. VERIFICATION — HARD RULE 12

For anything built from this plan:

- **The search must be tested against the real phrases in section A1.** A green
  unit test on a tidy query proves nothing; the phrasing is the requirement.
- **Assert a page renders correctly with its optional fields empty.** Most items
  have no description and no image. If the empty state looks broken, the template
  is wrong.
- **Assert prices display their age and source.** A price without provenance on
  screen is the failure this whole position exists to avoid.
- **Assert the compliance footer is present on every page**, including any
  overlay that covers the page footer. The ship overlay was doing exactly that
  until it was fixed on 2026-08-02.
- **After any build, assert the three pages exist in `_deploy/` and the three
  tabs exist in the layer.** Both have failed silently already.
