# Update — Q53 round one is measured off the served origin

**A correction on my own last update first:** it said the "go" arrived at
"00:1x CDT". The machine says **01:04 CDT / 06:04 UTC** — I typed a placeholder
and left it in. Rule 18 says the clock is read, not estimated, and that applies
to a filing as much as to a report.

**What ran:** `checks/_diag_q53_front_page_inventory.mjs`, new, mine by the
`checks/` default in `OWNERS.md`. Playwright against the **deployed worker**,
not `testing/_deploy` and not `_src` — `RULE16: INDEPENDENT`. The gate is
unlocked with `localStorage ccGate='1'`, which is the route five of this repo's
own diags already take; **no password is used, read or asked for** (rule 23).

**The canary passed.** A capability that does not exist is probed on both pages
and was reported absent both times, so the census is looking rather than
answering. It exits 2 if that canary ever comes back present.

## WHAT IS MEASURED SO FAR

    OLD  /        HTTP 200   116 controls (51 visible)   101 ids   254 ship rows
    NEW  /next    HTTP 200    18 controls (18 visible)    25 ids   253 cards

**Three findings that change what Q54 is:**

1. **THE PASSWORD GATE IS ON THE OLD PAGE AND NOT ON THE NEW ONE.** Served `/`
   comes back `cc-locked` with `#cc-gate` the only visible child of `<body>`.
   Served `/next` has no gate element and no lock class — it renders the whole
   page. `/find`, `/keybinds` and `/loadout` have no gate either, so the gate
   today protects exactly one address, and it is the one Q54 proposes to
   replace. **Stated as measured; the keep-or-drop is Sleven's.**

2. **THE FOUR INTERNAL SECTIONS ARE NOT ABSENT — THEY ARE UNADDRESSABLE.** The
   link half read `#dev`, `#calendar`, `#legend` and `#matrix` as absent from
   the new page, and as *hrefs* that is right. But `/next` carries `v-dev`,
   `v-cal` and `v-legend` as **tab views**, and all three render. What is gone
   is the address: clicking a tab changes neither `location.hash` nor
   `location.search`, and `/next#dev` finds no element of that id. So three of
   those eight are **CHANGED**, not ABSENT — and a fourth thing is newly broken
   that the link count could not see: **nothing on the new page can be
   bookmarked, linked to, or reached with the back button.** `#matrix` has no
   counterpart at all.

3. **254 ship rows against 253 cards.** The old page's own counter says "254
   ships total"; the new page's says "253". **One ship is not on the new page
   and I have not yet identified which** — that is in round two, and I am not
   guessing at it.

**Also measured:** the old page's search matches ship name and role only
(`drake` → 0 rows, `lorville` → 0). The new page's matches ship, job, maker and
place (`drake` → 22, `lorville` → 121) and names the category it matched. That
is CHANGED and wider, not lost.

**The old page carries five side panels** — DISPLAY, HELP, FEEDBACK, KEYBINDS,
FIND IT — and none of the five exists on the new page. The whole accessibility
overlay (7 presets, 11 sliders, 6 font choices, copy/save/reset) is in that
first one.

## NEXT, AND STILL UNMEASURED

Column sorting, the five dealer columns against the card's one dealer line, the
aUEC and pledge-price fields, provenance marks and the confidence note, the
trademark strip wording, `?q=` prefill, and the typeahead's keyboard
behaviour. **Round two, then the inventory document.**

**Nothing on either page has been edited and nothing will be under this item.**
Q53 is a measurement.

*Code, 2026-09-11 01:2x — the probe JSON is at `_needs_review/q53/`.*
