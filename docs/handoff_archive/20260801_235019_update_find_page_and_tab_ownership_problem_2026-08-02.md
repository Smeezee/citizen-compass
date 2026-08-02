# UPDATE — search/item/shop pages added, and the tabs keep getting wiped

Claude-02, 2026-08-02. One new page, three tabs restored, and a process problem
that needs solving rather than repeatedly patching. No commits, no pushes.

## THE PROCESS PROBLEM — please read this first

Tab injections into the layer have now been wiped **twice** by rebuilds during
this session.

- 01:15 — a push overwrote `testing/_layer.html`, destroying a blurred-backdrop
  change (documented by Claude-03).
- 06:33 — a rebuild rewrote `_src/_layer.src.html`, `_layer.html` and
  `_deploy/index.html`, removing the `cc-lo-tab` LOADOUT tab. The keybinding
  overlay survived; the tab did not.

Note that the **source file itself** was rewritten at 06:33, not just the build
outputs. So "put it in the source and it survives" is not currently true —
something upstream is regenerating `_layer.src.html` (a `_pull_b.html` appeared
in `_src/` at 06:30).

**Patching this by hand after every build is not a workable arrangement.** The
three tabs need to be emitted by `build_deploy.py` itself, from a small list, so
a rebuild produces them rather than removing them.

The tabs are:

| id | colour | links to | label |
|---|---|---|---|
| `cc-kb-tab` | teal `#00C9A7` | `keybinds.html` | KEYBINDS |
| `cc-lo-tab` | blue `#4DA3FF` | `loadout.html` | LOADOUT |
| `cc-fi-tab` | amber `#FFC24D` | `find.html` | FIND IT |

They sit on the right edge below the existing FEEDBACK tab, each with a mobile
fallback that drops to the bottom bar. All three are currently present in all
five layer files, restored by hand at 06:49. They will go again on the next
rebuild unless the build owns them.

## And the copy-step gap is still open

`build_deploy.py` must copy **three** pages into `_deploy/` now:

    _src/keybinds.src.html  ->  _deploy/keybinds.html
    _src/loadout.src.html   ->  _deploy/loadout.html
    _src/find.src.html      ->  _deploy/find.html

`keybinds.html` was already dropped silently once and restored by hand. Without
these steps the tabs point at 404s and nothing raises an error.

## What was added — the find / item / shop path

`_src/find.src.html`, mirrored to `testing/`, `_deploy/` and `_deploy_lite/`.

Three connected views in one file: a plain-language search box, an item page,
and a shop page. Built directly against the search-demand research, which found
that the strongest real intent is "where do I buy X" phrased in ordinary words,
and that no existing tool serves it — UEX presents a Trade Center, the wiki
presents a category tree, Erkul presents a DPS calculator.

**Design decisions worth keeping:**

- **The search strips filler.** "star citizen how much is a medpen" and "where to
  buy flight suits" both work, because words like *star, citizen, where, to, buy,
  how, much, is* are removed before matching. The remaining terms are matched
  against item names, categories, manufacturers, shop names and place names.
- **It is location-aware.** "flight suits new babbage" ranks items sold there
  above items that are not, and labels why with a small "sold in that area" chip.
- **The answer is a sentence, above the table.** *"Sold at 2 shops. Cheapest is
  medical supplies kiosk in Orison at 280 aUEC."* The detail sits underneath for
  anyone who wants it.
- **Sell-side is a first-class section.** The demand research found people search
  "how much does X sell for" as a separate question, and that competitors bury it
  inside trade tooling. Hadanite, for example, shows "shops do not sell this — you
  find it out in the world" and leads with the best sell price instead.
- **Every price carries its age and its source.** "player-reported, 4 hours ago",
  and anything a day or older turns amber. A standing panel explains that these
  are player reports, not game data, and that gear prices swing widely.
- **A failed search apologises rather than blaming the user**, and offers real
  suggestions. If a real search phrase returns nothing, that is a bug in the
  search, not in the person typing.

**Verified headlessly** against eight real phrases taken from the demand
research: "where to buy flight suits", "star citizen how much is a medpen",
"flight suits new babbage", "killshot ammo", "hadanite", "what sells at area18",
"quantum drive", and one nonsense string. All seven real phrases returned the
right thing first; the nonsense string produced the helpful empty state. Zero
page errors. Item page and shop page both render with generated answer lines.

**All data is invented** — 17 items across 9 shops in 6 locations. The page says
so in a banner. The structure mirrors the real UEX shape (item, price, terminal,
location, timestamp) so swapping in real data is a data job, not a redesign.

## Boundaries

`static/preview.html`, `releases/latest.html`, database, snapshots untouched.
No commits, no pushes. Build scripts not edited — the two fixes above are flagged
for their owner.
