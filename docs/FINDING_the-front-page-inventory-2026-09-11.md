# FINDING — the front-page inventory. Q53, and it gates Q54, Q55 and Q56.

**Code, 2026-09-11. Read off the SERVED origin, in a real browser, both pages.**

    base   https://citizencompasstesting.citizencompass-contact.workers.dev
    old    /        HTTP 200   396,153 bytes   116 controls   254 ship rows
    new    /next    HTTP 200   138,649 bytes    18 controls   253 ship cards

**Nothing here is read from `testing/_src` or `testing/_deploy`.** Q53 says the
source files are what we believe and the served pages are what a visitor gets,
so every figure below comes from the deployed worker. The five probes are

    checks/_diag_q53_front_page_inventory.mjs   the census, the gate, the hashes
    checks/_diag_q53_round2.mjs                 fields, sorting, currency, strip
    checks/_diag_q53_round3.mjs                 marks, dealers, per-field gaps
    checks/_diag_q53_names.mjs                  the ship list, exact equality
    checks/_diag_q53_patchmark.mjs              where a patch mark could hide

and their raw output is in `_needs_review/q53/*.json`. **Each one carries a
canary and all five passed it** — a capability known absent is probed and must
come back absent, a name that cannot exist must come back reported missing, a
pattern that cannot match must find nothing. Every probe exits 2 if its canary
comes back clean, so none of them is a green light with no bulb in it.

**The gate on the served front page is unlocked with `localStorage
ccGate='1'`,** which is the route `_diag_served_ship.mjs`, `_diag_offhull.mjs`
and `_diag_q49_backlink_walk.mjs` already take. No password was used, read, or
asked for.

**One thing I could not verify and am not going to claim:** whether the served
bytes match the local payload. `checks/_verify_deploy_drift.py` reported
`NOT PERFORMED` — its rebuild half needs PostgreSQL and `python-dotenv`, and
`build_find_data.py` refused to build without them. It failed closed and put
`_deploy` and `_src` back byte for byte, which is correct behaviour. So this
inventory describes **what is served**, which is what Q53 asked for, and says
nothing about whether a rebuild would change it.

> **CORRECTION, 2026-09-11, by the same author.** The cause above is wrong and
> the gap is now closed. **The build was never broken: I ran that control with
> the system Python instead of `venv\Scripts\python.exe`, which is what every
> script in this project uses.** On the right interpreter it passes 16 of 16,
> and the rebuild reproduces `index.html` byte for byte.
>
> **And the gap closed in the strengthening direction:** served `index.html` and
> served `next.html` were both byte-identical to the local payload when checked,
> so this inventory describes the served site AND the payload behind it.

---

## THE SHORT VERSION

**The link half of Q53 was already measured and it was right about the links.
It was wrong about what they meant, in one direction and in favour of the new
page:**

- Three of the eight "absent" links — `#dev`, `#calendar`, `#legend` — are
  **CHANGED, not gone.** The new page carries all three as tab views and all
  three render.
- But the same measurement could not see a **fourth thing that is newly
  broken: nothing on the new page has an address.** A tab click writes neither
  `location.hash` nor `location.search`, and `/next#dev` finds no element of
  that id. No bookmark, no link to a section, no back button.
- And there is a **ninth absent link** the count missed, because it is one
  anchor among 262: `robertsspaceindustries.com/spectrum/community/SC/forum/190048`.

**Four findings are bigger than any single link, and three of them are the kind
this project treats as data-quality rather than layout:**

1. **The per-row confidence note is gone for 203 of 253 ships**, and the new
   page's own footer asserts the opposite.
2. **Nothing sorts.** Nine of the old page's ten columns sort; the new page has
   no sort control of any kind.
3. ~~**One ship is on the old page and not the new one: `Valkyrie
   Liberator`.**~~ **WITHDRAWN 2026-09-11 — see the correction in 2.3.**
   254 rows against 253 cards is right; the conclusion was not. The ship is
   folded onto the Valkyrie's card as an edition, on Sleven's own recorded
   call, and the served card shows `Liberator Edition | $375`.
4. **Five side panels are gone**, and the whole accessibility overlay is one of
   them.

---

## 1. THE CONFIDENCE NOTE, WHICH IS THE ONE THAT WOULD WORRY ME

**Old page: 254 of 254 rows carry a CONFIDENCE / NOTES cell. 61 distinct
texts.** The top of them:

    165  Confirmed — starcitizen.tools 4.9.0
     13  Flight-ready, no dealer. No in-game dealer confirmed.
      9  Flight-ready, no dealer. No in-game dealer confirmed. Pledge price unconfirmed.
      7  Teach's version is a special loadout (***)
      3  New addition in 4.9.0

**New page: 50 of 253 cards carry any confidence sentence. A patch number
appears on 4.**

That second figure was worth a probe of its own rather than an assumption,
because a mark can sit where a reader never sees it. It does not:

    cards                                      253
    a patch number in rendered text              4
    in a title attribute                         0
    in an aria-label                             0
    in any data-* attribute                      0
    in ANY of those four                         4

The only `data-*` attribute on a card is `data-n`, the ship name, on all 253.

**And the page says otherwise about itself.** Quoted from the served footer:

> *"Every figure carries the patch it was checked against, and a blank means we
> do not know rather than a guess."*

**Measured against the cards it is describing, that sentence is not true of 249
of them.** I am reporting it, not fixing it — but it is the one item on this
list that is a statement to a visitor rather than a missing convenience, and
hard rule 20 is about exactly this: a number with no patch attached is a number
with no date on it.

*This is the same ground as Q61, which already says all 254 of our ship rows
report unverified. Q61 is about the database; this is about what the front page
tells the reader. They are not the same item and closing one does not close the
other.*

---

## 2. THE FULL INVENTORY

**PRESENT** = a visitor can do the same thing. **CHANGED** = they can do it, by
a different mechanism or with a different scope, and the difference is stated.
**ABSENT** = they cannot do it at all.

**No entry below is marked "keep" or "drop". That is Sleven's and it is not
made here** — his instruction was present, absent, changed, then he decides.

### 2.1 Finding a ship

| Capability, as the old page has it | On `/next` | What was measured |
|---|---|---|
| Search box over the ship list | **CHANGED — wider** | old matches ship name and role only: `drake` → 0 rows, `lorville` → 0. New matches ship, job, maker and place: `drake` → 22, `lorville` → 121, and it names the category it matched (`MAKER Drake Interplanetary`). `vulture` → 1 and `mining` → 10 on both. |
| Result count beside the box | **CHANGED** | old `"254 ships total"` → `"10 of 254 ships match"`. New shows a bare `"253"` → `"10"`. |
| Typeahead | **NEW on `/next`** | ghost completion: `vult` shows `vulture`, Enter accepts it and the box becomes `Vulture`. The old page has none. |
| Browse by category | **CHANGED** | old: 19 role buttons, each with a count (`Fighter 59`, `Cargo 44`, `Ground Vehicle 29`, `Exploration 24`, `Racing 20`…). New: 11 career chips (`Combat`, `Transporter`, `Exploration`, `Competition`, `Support`, `Industrial`, `Ground`, `Multi-Role`, `Starter`, `Gunship`, `Snub Fighter`), no counts. **Different taxonomy, not a subset** — the old one is role, the new one is career. |
| Jump to manufacturer | **ABSENT as a control** | old: a `MANUFACTURERS` tab and 18 maker buttons with counts (`AEGIS DYNAMICS 28`, `ANVIL AEROSPACE 39`…). New: the list is grouped under maker headings with counts (`28 ships · 19 buyable in game`), so the **grouping survives and the jump control does not.** |
| Budget filter | **ABSENT** | old: a number input, `e.g. 3,000,000`. Nothing equivalent on the new page. |
| Buy-in-game-only filter | **PRESENT** | old checkbox, new `#buy` chip. **Both give 179** — and the old page's 179 green rows agree with it, which is a cross-check of two different mechanisms landing on one number. |
| Clear-filter button and a filter-state chip with its own Reset | **ABSENT** | `cc-bclr`, `cc-state`, `cc-state-clr`. |
| Sorting | **ABSENT** | old: a click handler on 9 of 10 headers (`SHIP ⇅`, `ROLE ⇅`, `PRICE (AUEC) ⇅`, each dealer column, `PLEDGE PRICE (USD)`). New: no `th`, no sort select, no sort control found anywhere on the page. |

### 2.2 What a row tells you

The old page is a ten-column table. The new page is a card. Column for column:

| Old column | On the card | Coverage measured on `/next` |
|---|---|---|
| SHIP | name | 253 / 253 |
| ROLE | role line | 253 / 253 |
| PRICE (aUEC) | `1,508,220aUEC` | **179 / 253** |
| ASTRO ARMADA (AREA18) | folded into one dealer line | named on 61 cards |
| CRUSADER SHOWROOM (ORISON) | " | 10 |
| NEW DEAL (LORVILLE) | " | 118 |
| TEACH'S (LEVSKI) | " | 33 |
| BUY & FLY (RUIN STATION) | " | 7 |
| PLEDGE PRICE (USD) | `$60` | **237 / 253** |
| CONFIDENCE / NOTES | — | **50 / 253** (section 1) |

**The dealer grid is CHANGED, and the change is not a loss of the dealers** —
all five still appear by name. Five columns of ✔ and — become one line naming
the cheapest and the difference: `at New Deal · Lorville`,
`New Deal · Lorville · +67,910 at Teach's`, `Astro Armada · Area18 · same at 2
shops`. 56 distinct dealer lines across 253 cards. **What is no longer readable
is "which of the five stock this ship" at a glance, down a column.** 74 cards
name no dealer at all.

**The card adds three fields the table does not have:** length (`20 m`, 219 of
253), crew (`crew 1`, 223) and cargo (`0 SCU`, 219). **And a picture** — 247 of
253 cards carry an image; the old table has none.

**Status is CHANGED in form.** Old: the whole row is coloured, `row-green` on
179 and `row-orange` on 75. New: a pill on every card, `IN GAME` or `PLEDGE`,
253 of 253.

**Named gaps on the new page, because a gap named is worth more than a
percentage:** 16 cards show no pledge price — `Ballista Dunestalker`,
`Ballista Snowblind`, `Khartu-al`, `San'tok.yai`, `ATLS GEO IKTI`, `ATLS IKTI`,
`ATLS IKTI RAD`, `CSV-FM`, `RAPTOR`, `Starlancer BLD`, `Aurora CL`,
`Aurora ES`, `Aurora LN`, `Aurora LX`, `Aurora MR`, `Nova Tank`. 6 carry no
image — `F7C-M Hornet Heartseeker Mk II`, `CSV-FM`, `MOTH`,
`Genesis Starliner`, `RAPTOR`, `Starlancer BLD`.

*`RAPTOR` is a card on both pages. Rule 26's amendment records that the ship
does not exist — the RSI store tile was the bait on an April Fools page. Q57 is
already open on the sentence; **the card itself is on the new page too**, and
that is a fact for Q57 rather than a new item here.*

### 2.3 The ship list itself

    old   254 rows, 254 distinct names
    new   253 cards, 253 distinct names

**Compared by exact equality, both directions, no normalisation (rule 17).**
That took three extractions to do honestly, and the two that failed are written
into the probe headers rather than quietly discarded:

    td.textContent           picked up a link glyph the old page renders INSIDE
                             the name -> 28 old-only, 27 new-only
    the cell's own text      248 of 254 names live inside an anchor, so this
    nodes only               returned "" for those -> useless
    the anchor's text,       the name as the cell renders it, nothing added and
    else the cell's own      nothing removed

**Result: 28 names on the old page have no exact counterpart on the new one, 27
on the new page have none on the old.** 27 of those 28 are the same name plus a
trailing ` 🔗` — the old page appends a link glyph to the name of every ship
whose row points out to RSI instead of to our own ship page. **I am not matching
them by stripping the glyph** (rule 17), so the honest statement is: the name
text is CHANGED for 27 ships, and both spellings are named in
`_needs_review/q53/names.json`.

**The twenty-eighth has no counterpart under any reading:**

    Valkyrie Liberator      on the old page. Not on the new one.

> **CORRECTION, 2026-09-11 15:0x, added by Code who wrote this finding.**
> **The measurement below is right and the conclusion drawn from it is wrong.**
> There are 254 rows and 253 cards, and `Valkyrie Liberator` is the difference —
> but the ship is **NOT missing from the front page.** It is FOLDED onto the
> Valkyrie's card as an edition, by Sleven's own call recorded in
> `data-layer/derived/main-page-concepts/editions.json` on 2026-09-06
> (`confirmed_by: Sleven`, $375, with his caveat that the two being one hull is
> not yet checked against CIG spec data).
>
> The served Valkyrie card reads
> `Valkyrie | IN GAME | Cargo | 48 m | crew 5 | 90 SCU | 19,845,000aUEC | $375 |
> at Astro Armada · Area18 | **Liberator Edition | $375**`, and searching
> "valkyrie liberator" returns it. **A card count was never going to see that,
> and I should have said "254 rows against 253 cards, cause unestablished"
> rather than "one ship is not on the new page".**
>
> Cause traced under Q55.P18: `build_next_frontpage.py:74` drops any row named
> as a `from_row` in `editions.json`. It is the ONLY folded row in the dataset —
> one parent, one edition.

**The old page also carries `Valkyrie` and `Liberator 🔗` separately, and both
are on the new page.** Whether `Valkyrie Liberator` is a ship the new page drops
or a name the old page should not have had is **not resolved here — rule 19
says an ambiguity is refused and both sides named, not decided by picking the
likelier.** It is the first thing Q55 should settle, and it is one lookup.

### 2.4 Getting somewhere else

| Capability | On `/next` | Measured |
|---|---|---|
| Four section tabs | **CHANGED** | old: `Ship Purchase Matrix`, `Development Progress`, `Sale Calendar`, `Legend & Sources` via `data-target`. New: `ships`, `dev`, `cal`, `legend` via `data-v`, and all four views render. |
| `#matrix` `#dev` `#calendar` `#legend` as addresses | **ABSENT** | all four resolve on the old page and scroll to a real element (`scrollY` 307, 16576, 17602, 17808). On `/next` all four report **no element with that id** and `scrollY` 0. |
| A tab you can link to or bookmark | **ABSENT** | clicking each of the four tabs leaves `location.hash` and `location.search` empty. |
| `#matrix` — the table view itself | **ABSENT** | no counterpart. The list is a card grid. |
| Per-ship link into the ship page | **CHANGED** | `loadout.html#AEGS_Avenger_Stalker` → `loadout.html?from=next#AEGS_Avenger_Stalker`. 248 of 253 cards link; 221 distinct ship-page ids on the old page, 219 on the new. **`AEGS_Javelin` and `ARGO_MOTH` lose their ship page** and link out to RSI instead. |
| `keybinds.html` | **ABSENT** | — |
| `find.html` | **ABSENT** | — |
| RSI patch notes | **ABSENT** | `robertsspaceindustries.com/en/patch-notes`. |
| The Spectrum forum thread | **ABSENT** | `.../spectrum/community/SC/forum/190048`. **Not in the eight.** |
| `robertsspaceindustries.com` and `/pledge` | **CHANGED** | the bare root is gone; `/pledge` becomes `/pledge/ships`. |
| `starcitizen.tools`, `finder.cstone.space`, `uexcorp.space`, the takedown mailto | **PRESENT** | on both. |
| `erkul.games`, `fleetyards.net`, `spviewer.eu` | **NEW on `/next`** | not on the old page. |
| Back to top | **ABSENT** | `#backToTop`. |
| `?q=` prefill | **ABSENT ON BOTH** | `/?q=vulture` and `/next?q=vulture` both load with an empty box. **Never existed, so nothing is lost** — recorded because Q53 asks about bookmarkable URLs and this is the answer for both pages. |

### 2.5 The five side panels, all ABSENT

Every one of these is on the served old page and none is on `/next`.

| Panel | What is in it |
|---|---|
| `DISPLAY` | the accessibility overlay. 5 sub-panels (Quick, Type, Color, Layout, Export), **7 presets** (Site default, *Easier on tired eyes*, *Dyslexia friendly*, *Low vision — 150%, bold, high contrast*, Light mode, Amber on black, *Calm — muted colour, no motion*), **6 font choices**, **11 sliders** (scale, weight, tracking, word spacing, leading, text box, saturation, row padding, border, border width, radius), a CSS export box with Copy, Reset all, and *"Settings saved automatically"*. |
| `HELP` | a stepped help panel with `← Back a step`. |
| `FEEDBACK` | the Jotform form, in an iframe — **which is why it is not in the anchor list; it is a frame `src`, not an `href`** — and a **`Send another response`** button. |
| `KEYBINDS` | a keybinds board with its own search box, device hint, and a `Capture everything (full screen)` control. |
| `FIND IT` | the finder, as a tab. |

**`Send another response` is Q55's already-fixed requirement, already built.**
Q55 states that if a comment route carries over in any form it must reset after
each submission so one person can send several without reloading. **That control
exists on the old page today.** It is not a thing to design later; it is a thing
not to lose.

**Focusable elements: 379 on the old page, 274 on the new.** Neither page
focuses the search box on `/`; `/next` autofocuses `#q` on load. Pressing `/`
focuses nothing on either page. Escape closes the FEEDBACK and KEYBINDS panels
and **does not close DISPLAY or HELP** — that last one is the old page's own
behaviour and is recorded here only because a keyboard user meets it.

### 2.6 Two more, and neither is mine to touch

**THE PASSWORD GATE — ABSENT on `/next`.** Served `/` comes back with
`html.cc-locked` and `#cc-gate` as the only visible child of `<body>`. Served
`/next` has no gate element and no lock class and renders the whole page.
`/find`, `/keybinds` and `/loadout` have none either, so **the gate today
protects exactly one address, and it is the one Q54 replaces.** Stated as
measured. No recommendation attached.

**THE TRADEMARK AND DISCLAIMER STRIP — CHANGED. REPORTED, NOT EDITED (rule 8).**
Both pages carry the registered-trademark sentence word for word. The
differences, quoted exactly:

    on the old page, not on the new one
      "All content on this site not authored by its host or users are property
       of their respective owners."
      "Official site: robertsspaceindustries.com"

    on the new page, not on the old one
      "Ship imagery © Cloud Imperium Games."

**I have not changed a character of either and will not.** Rule 8 puts
disclaimers, attribution and Fan Kit wording with Sleven alone and says to
report a gap rather than fix it. This is the report.

---

## 3. WHAT MUST MOVE, AND WHY THAT IS A SHORT LIST

Q53's DONE-WHEN asks for the ones that must move separated from the ones
deliberately dropped. **The honest separation is not two lists, it is three**,
because most of these are his call and marking them otherwise would be a desk
deciding by picking.

### 3.1 Already decided — not by me, and quotable

    Send another response      Q55 states the reset-after-submission
                               requirement as Sleven's own, from the round of
                               feedback that produced the form. It survives even
                               if the form is replaced. It is built on the old
                               page and absent from the new one.

    the trademark strip        rule 8. His alone, in both directions - the
                               sentence dropped and the sentence added.

### 3.2 Mechanically required by a swap, whoever decides the rest

    an address for each tab    the old page's four sections are linkable today.
                               After a swap to /next they are not, and any link
                               anyone has already shared to /#dev or /#legend
                               lands on a page with no such element. This is not
                               a feature preference - it is a live URL that
                               stops resolving.

    the gate, or a decision    /next serves ungated. If it becomes the front
    not to have one            door, the front door is ungated. Which of those
                               two he wants is his; that the swap changes it is
                               mechanical.

### 3.3 His call, and I am not making it

Everything else: the confidence note, sorting, the budget filter, the
manufacturer jump, the role taxonomy, the four side panels, back-to-top,
`keybinds.html`, `find.html`, patch notes, the Spectrum thread, the two ships
that lose their ship page, and `Valkyrie Liberator`.

**On the feedback form specifically, Q53 already records that he checked it
himself and it has zero submissions, and that the keep-or-drop is still his and
not made.** Nothing here reopens that.

---

## 4. WHAT THIS ITEM DID NOT TOUCH

**No page was edited. No file in `testing/` was opened for writing. Nothing was
deployed, committed or deleted.** Q53 is a measurement and the five probes are
report-only.

`docs/contact_sheet_*/`, `testing/_src/_inspect.src.html` and
`testing/_deploy/_inspect.html` were not touched — rule 25's out-of-scope list.

**DONE-WHEN, against what Q53 asked for:** every capability of the old front
page is listed and marked PRESENT, ABSENT or CHANGED on the new one; both sides
are read off the served pages rather than either source file; and the ones that
must move are separated from the ones awaiting his call, with the separation
argued rather than asserted.

*Code, 2026-09-11. Probe output in `_needs_review/q53/`; the five probes are in
`checks/`.*
