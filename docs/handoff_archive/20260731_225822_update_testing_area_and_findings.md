# UPDATE

Cowork session (Claude-01), 2026-07-31 into 2026-08-01. Nothing committed, nothing
pushed, live site untouched, database untouched. All work confined to a new
`testing/` folder plus corrections recorded below.

## Built — testing area at `testing/`

A full copy of the live page with everything experimental layered on top. The live
page is read, never written.

- `testing/build.py` — reads `releases/latest.html`, injects `testing/_layer.html`,
  writes `testing/index.html`. Re-run any time the live page changes and the
  testing area is flush with it again.
- `testing/_layer.html` — the layer. All experimental work lives here.
- `testing/index.html` — generated. Do not hand-edit.

Run it: `python -m http.server 8000` from the project root, then
`http://localhost:8000/testing/`. A local server is required because browsers block
`file://` pages from loading the GLB models.

**Architectural rule, expensive to reverse:** experimental features are built as a
LAYER that attaches to whatever page it is dropped into — finds the table, finds
the search box, hooks on — never woven into the page source. This is why the
testing area cannot drift from live.

### Ship detail pages

Ship names in the matrix became clickable. Opens a full page with a live 3D viewer
(orbit, zoom, auto-rotate) reading from `sc-ships/`, an acquisition panel (aUEC,
dealers, pledge price, RSI link), an erkul-style loadout slot grid, a provenance
line surfacing `confidence` and `last_verified_patch`, and a related-ships strip.
The per-ship `image.webp` displays instantly while the model streams in behind it.

The loadout panel is STRUCTURE ONLY, explicitly labelled as awaiting data, with
nothing invented. Hardpoint data lives in Postgres and reaches this panel once the
API is wired in — which makes the ship page the first thing that genuinely needs
the FastAPI backend, currently powering nothing public.

### Display engine

Five-tab control panel (green DISPLAY tab, right edge, or Alt+D) that changes the
entire page live, not just the new panels. Seven one-click profiles, six typefaces
including Atkinson Hyperlegible and Lexend, weight/tracking/word-spacing/leading
sliders, six backgrounds, accent pickers, text brightness, colour intensity, row
height, border strength and thickness, corner rounding, striping, hover strength,
focus rings, motion off, glow off — plus a CSS export button that emits the chosen
settings ready to paste into the live stylesheet.

Works by overriding the site's own CSS custom properties, which is why backgrounds,
borders and accents all follow. Persists to localStorage.

**Standing instruction from Sleven: this ships in every build from now on.**

## Findings

**Live-site readability is a real problem.** The site uses Rajdhani (condensed,
narrow, thin strokes) and Share Tech Mono (very thin) at 0.78–0.9rem on a dark
background. Light-on-dark bleeds and thin condensed faces amplify it. Reported
independently by two people as fuzzy and requiring concentration to resolve. Those
faces are fine for headings and large numbers, poor for body text. The display
engine exists so a working combination can be found empirically then exported.

**3D models are too heavy to ship.** `sc-ships/` holds 243 folders, 469 GLB files,
7.3 GB. Median 12.8 MB, max 58.7 MB, Vulture 27 MB. Instant off local disk, 10–30
seconds per ship over the internet. **The 2026-07-31 batch rescale changed
dimensions, not file size** — `model.glb` and `model_scaled.glb` have different
hashes and identical byte counts. A compression and decimation pass is a separate
job, same Blender machinery as the rescale.

**234 of 254 site ships map to a model folder.** Unmatched ships say so plainly
rather than failing silently. A few matches are rough: three ATLS variants share
one folder, two Gladius entries collide.

**Location data was already in hand and wrongly recorded as missing.** Snapshot
`20260731T041451Z` contains `starmap_positions.json` (1,774 entities, every one
with x/y/z coordinates, plus `parent_uuid` giving a containment hierarchy),
`starmap.json` (3.0 MB, uninspected), `trade_locations.json` (965 locations),
`fps-items.json` (48 MB, uninspected), plus uncatalogued `blueprints/`,
`contracts/`, `factions/` and `resources/` directories. Only ITEM-LEVEL INVENTORY
BY LOCATION is genuinely missing — `trade_locations.json` carries category tags
("Luxury", "Commodity"), not per-item pricing. UEX (source 6) is the likely answer
and is already partially wired in. Inspecting `fps-items.json` and `starmap.json`
costs nothing and should happen before pursuing an external source.

## Corrections to the record

**CC-05 carries a fabricated citation.** The 2026-08-01 transport dump states the
page-size fix was missed "despite run 1's own manifest recording that a manual test
at 20 had succeeded." No such record exists. The run-1 manifest at
`data-layer/external-source-manifests/20260731T031754Z/03_star-citizen-wiki-api_manifest.json`
records verbatim: "3 independent manual curl tests before the scripted pull even
started (2 of 3 manual attempts also failed 500, 1 succeeded)" — all at
`page[size]=200`. The finding is correct; the provenance is invented. Originated in
Echo's probe prompt and propagated. Amend that sentence.

**Unresolved contradiction.** That manifest records one success at `page[size]=200`
and characterises the fault as "intermittent." The probe recorded 200 failing
deterministically. Both cannot be true. The "intermittent" wording is what stopped
two runs and one analysis from testing the variable. Note it alongside the sealed
manifest; do not amend the manifest.

**CC-18 wording.** It calls `static/index.html` the "live homepage." Section 1 of
the same dump correctly says it is not deployed. Verified: the deployed page carries
the Fan Kit disclaimer, `static/index.html` does not, and it is not served. As
written, CC-18 would lead a reader to believe the live site is non-compliant.
Reword to "undeployed `static/index.html`."

**CC-03 closed on a single success.** The 2026-07-30 backup succeeded. An inbox
update from 2026-07-31 records the backup script failing with exit code 1, and that
is not reflected anywhere in the dump. One manual backup worked; the repeatable
mechanism is unproven. Both copies are in the same building and the live Postgres
database still has no backup or recovery plan. Reopen as partial or add a successor
item.

**Git state asserted two ways.** CC-16 says 17 commits reached origin; section 13
says 4+ ahead and unpushed. Establish ground truth with `git status` and
`git log origin/main..main` before acting on either.

## Also on record

Claude-01 previously reported the source-3 vehicles endpoint as "a real upstream
outage or a permanently broken endpoint." That was wrong — the fault was a
deterministic page-size issue. Echo identified the real cause. Her supporting
citation was invented. Both are true.

## Next

1. Database backup — the only open item where the downside is permanent.
2. Compress and decimate the GLB library so the testing area can be shared as a
   link rather than demonstrated in person.
3. Inspect `fps-items.json` and `starmap.json` — free, already on disk, may close
   the inventory gap without an external source.
4. Export a working readability configuration and consider shipping the display
   panel itself as a live-site feature.
