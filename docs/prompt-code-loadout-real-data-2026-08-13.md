# PROMPT FOR CODE — the loadout page is a hand-typed mockup. Wire it to the 316 real ships and ship it tonight.

    from    C1, 2026-08-13
    for     Code
    status  GO-AHEAD to build, commit, push AND deploy.
              Sleven: "let's try to push for that and get that done today...
              we should be able to get that done by 2200."
    target  Deployed to the testing site by 22:00 local.

    KEYBINDS ARE ON HOLD. Sleven: "Hold everything on the key binds for now. If
    they're functional at the moment, that's fine." Do not spend any of tonight
    on the keybind page, the exporter, or the device panel. They work well
    enough and the remaining tests need his hardware, not your time.

    COLLECTOR IS ALSO PAUSED tonight — the upload/update/installer work is real
    but it is behind this. Nothing in this order touches `citizen-collector/`.

---

## 0. What is actually wrong, measured just now

`testing/_src/loadout.src.html` is 432 lines and its data is typed by hand:

```js
const SHIPS = { ...4 entries, 1155 bytes... }   // vulture + 3
const P     = { ...16 entries, 1881 bytes... }  // 16 components
```

There is a `.mock` banner in the CSS and on the page, so it is honestly labelled
— it is a design prototype that got deployed, not a product. `loadout.html` is
live at 23 KB.

**Meanwhile the real data is sitting on disk, joined and proven:**

```
data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/ships.json       90.7 MB
data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/ship-items.json  29.3 MB
data-layer/ship_resolution.json                                                         53.8 KB
```

- **316 ships**, **5,384 items**, **36,584 fitted-component instances**
- **100% join** on WeaponGun, Turret, WeaponDefensive, MissileLauncher, Missile,
  Shield, MainThruster, ManeuverThruster, Cooler, PowerPlant, Radar, QuantumDrive,
  CargoGrid, FuelIntake, FuelTank, Armor, LifeSupportGenerator, FlightController
- WeaponAttachment 97% — **every one of the 33 misses is the same fire
  extinguisher magazine**, an FPS item correctly absent from a ship catalogue
- Display, Misc, Seat, Door and the controller nodes are 0% — **a category
  boundary, not a join failure.** CIG does not model doors and screens as statted
  purchasable items. Do not chase these.

Evidence: `docs/FINDING_ship-loadout-display-research.md`.

**And the maths is already proven, so do not invent any:**
`docs/FINDING_ship-aggregation-rules-proven-2026-08-08.md` — shields
(top-2-generator redundancy cap) **267/267 exact**; DPS (the `IsPilotSlaveable`
outermost-lock rule) **275/275 exact** against CIG's own `PilotDps`; 10 of 11
power categories at 100%. Plus
`docs/FINDING-aggregation-addendum-power-distortion-groundvehicles-20260808.md`
and `docs/FINDING-aggregation-rules-shields-solved-20260808.md`.

**`ships.json` already carries CIG-computed aggregates** for the stock loadout —
`ShieldsTotal`, `Power`, `Cooling`, `Emission` by contributing group,
`Distortion.Pool`. **Prefer CIG's number over your own where CIG publishes one**,
and where you compute your own, check it against CIG's and report the match rate.
A disagreement is a finding, not something to paper over.

## 1. Build `build_loadout_data.py` → `loadout_data.gen.js`

**Follow the pattern that already works twice** — `build_holo_data.py` →
`holo_data.gen.js` (267 KB, 167 ships, shipping fine) and `build_kb_actions.py`
→ `kb_actions.gen.js` (114 KB). Same shape: one generator, one writer, a header
comment saying what generated it and from which snapshot, `PAGES` entry, done.

### The TRIM is the whole trick, and Sleven asked what it means

Each record in `ship-items.json` carries on the order of forty fields. **The page
displays about eight.** Ship the eight.

Take only what the page renders — component name, manufacturer, type, size, and
the stats it actually shows (DPS, IR, EM, power draw, heat, plus whatever the
existing mock's `P` shape uses). Drop the rest. **Same ships, same components,
same page — a fraction of the bytes.** Nothing a visitor can see is lost.

**Pick the field list from what `loadout.src.html` actually reads**, not from
what looks interesting. If the page never renders a field, it does not ship. If
you add a field to the page later, you add it to the generator then.

**Target: one file, under about 2 MB.** If the honest trimmed output lands well
above that, do NOT start splitting into per-ship files tonight — say so in the
report with the real number and ship it anyway if it is servable. Per-ship files
are the right long-term shape (it matches the page-per-file decision already on
record for items) but that is a generator change later, not a rewrite, and it is
not what gets a deploy out by 22:00.

## 2. Every ship we have data for. Say plainly what we do not.

**Sleven's words:** *"I would like to get as many of the ships as possible. I
understand if we don't have the information that CIG has not pushed out, that's
— I completely understand."*

So: **all 316 ships that have game-file data get a loadout.** Use
`data-layer/ship_resolution.json` — the join is already done and classified:

```
254   ships on the live site
221   matched to a game file
  0   ambiguous
 33   no game file - every one already flagged pledge_only
 89   game files not on the site
```

**The 33 are concept ships CIG has not built yet.** They cannot have components
because the components do not exist. **The page must say that in plain English**
— "this ship has not been released, so there is no loadout to show" — rather
than rendering an empty panel or omitting it silently. That is the same
discipline as `HOLO_UNMATCHED` in the holo viewer, which is already correct: say
what you cannot show instead of quietly showing less.

**The 89 game files not on the site are mostly special editions** — 53 differ
from their base only in fitted components, 18 are mechanically identical, and
exactly one (the Anvil F8A Lightning) is a genuinely distinct ship. **Include
them.** A "differs only in fitted components" ship is precisely what a loadout
page is for — it is the one page on the site where that difference is the
content rather than noise.

## 3. Wire the page and delete the mockup

- `const SHIPS` and `const P` come out. The page reads `LOADOUT_DATA` from the
  generated file.
- **The `.mock` banner goes.** It is currently telling the truth; once the data
  is real it becomes a lie, and a stale honesty banner is worse than none.
- The ship picker lists every ship with data, plus the unreleased ones shown as
  unavailable with the reason.
- **Keep every comparison feature that already works.** The A/B build compare,
  the ghost preview, the delta percentages, the "% quieter" phrasing for
  lower-is-better stats — that is good work and this order is a data swap, not a
  redesign.

## 4. State provenance on the page

The site's whole premise is provenance, and this is the first page where a
visitor will read numbers and act on them.

- **Name the snapshot** — `20260801T204744Z` — visibly, not in a comment.
- **Where a figure is CIG's own precomputed aggregate, say so.** Where it is ours,
  say that too. The two are not the same claim and the reader deserves to know
  which one they are looking at.
- **Every row carries `last_verified_patch`**, per the standing project rule, and
  the front end flags unverified data. Do not skip this because it is a new page.

## 5. What NOT to do

- **Do not touch the keybind page, the exporter, `device_engine.js`, or
  `sc_export.js`.** On hold by Sleven's explicit instruction tonight.
- **Do not touch `citizen-collector/`.** Separate order, separate evening.
- **Do not invent aggregation maths.** It is proven in the findings named in §0.
  If you need a formula that is not there, say so and leave the field out rather
  than guessing one.
- **Do not chase the 0%-join categories** (Display, Misc, Seat, Door, controller
  nodes). Category boundary, not a bug.
- **Do not `git add -A`.** The tree carries ~220 line-ending-noise files. Stage
  by explicit path.
- **Do not `wrangler pages deploy`.** Use the deploy script. That mistake has
  silently published to a second URL five times in this project's history.
- **Do not add a new top-level directory under `_deploy/`** without editing
  `DEFAULT_ALLOWED_DIRS` — the guard will fail and it will look like a build
  break. If you ship per-ship JSON later, that is the thing to remember.

## 6. Acceptance

1. `/loadout` lists every ship that has game-file data. No mock banner anywhere.
2. Picking a ship shows its real stock loadout, from the snapshot, with real
   component names and manufacturers.
3. An unreleased pledge-only ship is listed and **states why it has no loadout**,
   in words a person understands.
4. A special-edition ship that differs from its base only in fitted components
   shows that difference.
5. Where CIG publishes an aggregate, our displayed figure matches it, or the
   mismatch is reported in your write-up with the count.
6. The A/B compare, ghost preview and delta display all still work against real
   data.
7. `loadout_data.gen.js` has a generated-by header naming the script and the
   snapshot, and is listed in `PAGES`.
8. `python testing/_src/build_deploy.py` and `check_deploy_clean.py` pass clean.
9. Deployed, and the live assets verified byte-for-byte against `_deploy/`.

## 7. Report back

- **The file size.** That is the number that decides whether per-ship splitting
  becomes the next job.
- **How many ships got a loadout, how many did not, and why not** — by category,
  not as one number.
- **The match rate against CIG's own aggregates**, and any disagreement, stated
  plainly rather than smoothed over.
- Anything in the data that surprised you. This dataset has not been rendered
  before and nobody has looked at it through a page.

## Commands

```
python build_loadout_data.py
```

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```
