# WORK ORDER — drive the loadout bench from real data

Approved 2026-08-02. Replaces the invented data in `testing/_src/loadout.src.html` with the game-file data already collected, sealed and gated.

Hard rule 13 applies: file an `inbox/` update on intake, on each phase completing, and on any stop.

---

## The finding this rests on — verified, not assumed

Everything this feature needs is **already on disk**, in snapshot `20260801T204744Z`. Nothing new has to be collected.

**Slots.** 316 ship files, each with a `Loadout` array carrying `HardpointName`, `Type`, `Grade`, `MinSize`, `MaxSize`, `CompatibleTypes`, `ClassName` and `Editable`. Claude-02 checked one file; **I sampled ten across manufacturers and got 10/10 with the full schema** — Avenger Stalker 67 slots, Prowler Utility 103, Asgard 106, Constellation Taurus 115, Centurion 45.

**Parts.** `ship-items.json`, 29 MB, **5,384 components** with `className`, `type`, `subType`, `size`, `grade`, `name`, `reference` and a nested `stdItem`. 202 WeaponGun, 317 Turret, 188 WeaponDefensive, 885 ManeuverThruster, 381 MainThruster, 238 FlightController, 210 Armor.

**Compatibility.** Already on each slot as `CompatibleTypes`. No inference needed.

**Prices.** Each component's `reference` is the **Star Citizen UUID** — the exact key UEX joins on, and source 6 landed 5,566 of them.

**Use snapshot `20260801T204744Z`, not `20260731T041451Z`.** The latter is the superseded copy with the `.git` problem.

**Blender is not required for any of this.** Model markers are a separate, later job.

---

## What is there now

`loadout.src.html` is a working prototype whose entire ship list is **1,153 characters — one ship, the Drake Vulture** — and whose every component, stat and price is invented. The slot structure and sizes follow the real shape; nothing else does.

**That is why the ship-page entry point is deliberately not wired.** Linking it from every ship would dead-end 315 of 316. The LOADOUT tab has been removed; the link goes in at Phase 6, when it works everywhere.

---

## PHASE 0 — the blocker nobody has named

**There are four ship inventories on this project and they do not agree.**

```
254   live site
316   scunpacked ship JSONs
243   model folders (235 in the deploy)
232   PostgreSQL
```

`CURRENT-STATE.md` already carries the open item: 62 DB ships with no registry entry, 108 registry entries with no DB row. **This pipeline forces that decision** — every phase below needs to know what "a ship" is and which name is canonical.

**Do not paper over it with a name-matching heuristic.** That is exactly the rot the UEX manifest warns about, in a different place. Produce a resolution table — one row per canonical ship, with its site name, its JSON filename, its model folder, its DB id, and an explicit `null` plus a reason where one is absent.

**Report the counts before building anything on it:** how many resolve across all four, how many are missing from each, and what the residual is. If that number is ugly, say so — it is better known now than discovered at Phase 5.

---

### PHASE 0 STATUS — largely done, 2026-08-02. Do not redo it.

The cross-reference has been run and the table is on disk at
`data-layer/ship_resolution.json`.

**Method, on Sleven's call:** anchor on the 254 live ships as the trusted set,
match outward into the 316 game files, and **classify the residue rather than
discard it.** Nothing was thrown away.

```
254   live ships
215   matched to a game file
  2   ambiguous
 37   no game file
  6   tier variants set aside (same ship, different equipment tiers)
 95   game files not on the site
```

**The 37 are corroboration, not a gap. 33 of them are ships the site already
flags `pledge_only`** — concept ships — and the game files independently agree
by not containing them. Two datasets built separately reaching the same answer.

**4 need a human** — site says `purchasable`, no game file: 600i Explorer,
Ares Inferno, Ares Ion, Nova Tank. Ares Inferno and Ion are expected to be in
the game, so a naming mismatch is more likely than a real absence. **Investigate
before concluding.**

**Matching rules that made it work, worth keeping:**
- Game-file `Name` carries a manufacturer prefix the site does not use
  ("RSI Aurora CL" vs "Aurora CL"). **Match on suffix** rather than trying to
  enumerate prefixes — it handles every variant without knowing any of them.
- `_tier_N.json` files are the same ship at different equipment tiers. The base
  file is canonical. **Keep the variants** — they are what a stock-vs-upgraded
  view needs later.
- RSI ships carry a `gs_` designation in the filename that the display name
  omits.

**Still outstanding on Phase 0:**
1. **PostgreSQL's 232 is not in the table** — it could not be reached from the
   session that built this. Run the same join and close the fourth column.
2. The 95 game-only files are grouped by career (53 Combat, 14 Industrial,
   13 Support, 12 Transporter, 9 Exploration, 8 Multi-Role, 6 ground vehicles,
   5 Competition) but not individually classified. **Parked by Sleven** — do
   not spend time on it in this order.

**Use `ship_resolution.json` as Phase 1's input.** Do not re-derive the mapping;
if you disagree with a row, say which and why rather than rebuilding the table.

---

## PHASE 1 — slot extractor

For each resolved ship, read its `Loadout` array and emit a normalised per-ship record: slot id, display name, group, type, size range, compatible types, stock `ClassName`, and whether it is editable.

- **Preserve `Editable: false`.** A fixed slot is a fact about the ship, not a UI detail — and the current bench already models it as `fixed`.
- **Do not flatten the size range.** `MinSize`/`MaxSize` is what makes the compatible-parts list correct.
- Record the source snapshot id and file on every record. Provenance travels with the data.

---

## PHASE 2 — parts catalogue

From `ship-items.json`, emit a trimmed catalogue keyed by `className` — because that is what the slots reference.

- Keep only what can occupy a slot. **1,077 of the 5,384 records are Paints**; they are not loadout components.
- Carry `reference` (the UUID) on every record. Without it, Phase 3 cannot happen.
- Pull displayed stats from `stdItem` rather than inventing them. **If a stat is absent, it is absent** — show nothing, never a plausible-looking default.

---

## PHASE 3 — prices, and the honesty problem

Join component `reference` → UEX `items.uuid` → `items_prices_all` → terminal → location.

**This is where the feature earns the site's tagline** — "know where to buy, before you fly," applied to components.

**And it is where it can most easily mislead.** Component stats come from game files (Tier A). Prices come from UEX, which states its own tolerance as **±20% on commodities and ±100% on items** (Tier C, never auto-promoted).

So a shopping list mixes tiers, and a confident-looking total built on ±100% data will do more damage to trust than showing nothing.

**Required:**

- Every displayed price carries its tier and the date it was gathered.
- **A component with no UEX match shows "no price on record" — never a zero, never a blank that reads as free.** The matrix already makes this distinction for pledge-only ships; follow it.
- A total is only shown when every line has a price. A partial total is a wrong total.
- Report the join rate as a number. "How many of the fitting components actually have a price" is the single most useful figure this phase produces, and it is also the honest limit of the feature.

---

## PHASE 4 — how the data reaches the page

**This is an architecture decision, not an implementation detail, and it is the first of its kind on this site.**

Every page here today is one self-contained file with its data baked in. That is why the live site has no backend dependency at all and why a deploy is a folder of static files.

Loadout data will not fit that pattern: rough order of 3 MB of slots and 1 MB of trimmed parts. Inlining it into one page is not viable.

**Two options, and state which you took and why:**

**A. Static JSON alongside the page.** `loadout.html` fetches `data/ships/<id>.json` and `data/parts.json` on demand. Keeps the zero-backend property, deploys as ordinary files, works on Cloudflare exactly as today, cacheable, no new failure mode.

**B. FastAPI.** The backend finally powers something a visitor sees. More flexible, and the ship detail panel would want it eventually anyway — but it makes the site depend on a running service for the first time, and Railway currently powers nothing.

**Recommendation: A, now.** The dependency-free property is worth more than the flexibility at this stage, the data is read-only and changes per patch rather than per request, and B remains open later without rework. **Do not take B without asking.**

---

## PHASE 5 — wire the bench

Replace the invented `SHIPS` object and parts list with the generated data.

**Delete the invented data. Do not keep it as a fallback.** A fallback that renders plausible numbers when the real data fails to load is indistinguishable from working software, which is the worst possible failure mode for a page whose entire purpose is telling people what things cost.

An empty state that says why is correct. A confident wrong answer is not.

---

## PHASE 6 — the ship-page entry point

Only now. The ship detail page already has a Loadout panel reading "awaiting data" — that is where the link goes, so it opens on the ship you are already looking at.

`loadout.html` already reads `#shipId|buildA|buildB` from the hash, so this is a link, not a rewrite.

**Wire it only for ships the data actually covers**, and show the panel's existing "awaiting data" state for any that are not. A link that dead-ends is worse than a panel that says it does not know yet.

---

## Rule 12 — the cases that must be shown to fail

Each of these will occur in a real run. Prove each is handled before trusting any of it:

1. A ship in the site's list with **no** JSON file
2. A `Loadout` slot whose `ClassName` is **not** in the parts catalogue
3. A component with **no** `reference` UUID
4. A UUID with **no** UEX price
5. A ship whose `Loadout` array is empty or absent
6. A `CompatibleTypes` value matching **nothing** in the catalogue

**A pipeline that has only ever been run on the Vulture is untested.** Run it across all 316 and report the failure counts per case — those counts are the real state of the data, and they belong in the manifest.

---

## Why this is Stage 2, and should be built as Stage 2

Stage 2 — validate and promote — does not exist. Not one line. This work is **exactly** what Stage 2 does: take sealed snapshots, check them, resolve them against each other, and emit clean records with provenance and tier attached.

**Build it as the first Stage 2 pipeline, not as a bespoke loadout importer.** The ship identity resolution, the provenance stamping, the tier tagging and the join-rate reporting are all things every later dataset needs. Doing it as a one-off means doing it twice and having two of everything that disagree — which is the failure pattern this project has hit three separate times already.

Auditors flag, never fix. Same rule here: this pipeline **reports** what does not resolve; it never guesses.

---

## Also outstanding, from Claude-02's report

- **`testing/_deploy_lite/`** — 243 files, hand-made, nothing generates it. Make it a real build target or remove it. **A mystery folder that looks like a build output will eventually be treated as one.**
- **`testing/_src/kb_overlay.inc.html`** — no build script references it and the overlay is already inlined in the layer. Remove it or wire it in. An unreferenced include that looks load-bearing is worse than neither.
- **Copy step: done.** `build_deploy.py` now copies `keybinds.src.html` and `loadout.src.html` into `_deploy/`, proven against known-bad input — exit 1 on a missing source, both files restored after deletion.

## Boundaries

- Live site, `releases/latest.html`, sealed snapshots untouched. Snapshots are read-only inputs.
- No promotion into PostgreSQL in this order unless Phase 4 option B is chosen, which requires asking first.
- If a phase blocks, write to `inbox/`, stop that phase, and say what blocked. **Phase 0 blocking is a likely and acceptable outcome** — it is an open decision, not an engineering failure.
