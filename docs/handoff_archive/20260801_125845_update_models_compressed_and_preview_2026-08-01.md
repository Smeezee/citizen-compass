# All 234 ship models compressed; shareable preview built — 2026-08-01

Cowork session. No commits, no pushes. Everything below is on disk and ready for review.

## Model compression — done, 3.40 GB → 344 MB

All 234 `sc-ships/*/model_scaled.glb` files compressed with Draco. **Zero failures.** Plus Asgard, which had only `model.glb` and no scaled variant — compressed from that, giving 235 files total.

Representative results: Aurora LX 1.09 → 0.16 MB, Carrack 5.61 → 0.55 MB, L-22 Alpha Wolf 12.37 → 1.19 MB, Apollo Triage 22.27 → 2.23 MB. Largest output is Starfarer Gemini at 5.22 MB.

Geometry is preserved — Alpha Wolf 1,345,659 → 1,341,318 vertices (99.7%). Verified visually, not just numerically: original and compressed were loaded side by side into a real three.js scene and rendered at full-ship framing and at hull-panel close-up. Indistinguishable. The loss is quantization rounding, not deleted detail.

`gltf-transform optimize` (simplify + Draco) was tested and **rejected** — it reaches 100–260 KB but deletes ~95% of vertices. Not suitable for the hero viewer.

**Six ships have no 3D model on disk at all** and are a genuine gap, not an oversight: 85X, Arrastra, Fury, Mantis, Merchantman, PTV.

### The compressor

`testing/_tools/cc-compress.cjs` plus two `.wasm` files — a self-contained esbuild bundle of `@gltf-transform/core` + `draco3dgltf`, about 1.1 MB total. No `npm install` required; it runs on the Node already present.

```
node cc-compress.cjs <sc-ships-dir> <out-dir> [startIndex] [count]
```

Resumable and idempotent — skips outputs newer than their source, so it can be run in slices and re-run safely. Emits a JSON report per run.

Note: an ES-module build of this fails. Draco's emscripten glue uses dynamic `require`, so it must be bundled as CJS.

## Shareable preview built — `testing/_deploy/`

`index.html` (1.4 MB) + `models/` (235 files, 343 MB). 344 MB total. Intended for Netlify Drop as a **new** site; publishing is the operator's step.

221 model paths wired, covering 228 of 254 ship rows (several ship IDs share a model folder). Every path in `CC_EMBED` was verified to resolve to a file that exists.

Carries a password gate (`apples`). **It is client-side and can be bypassed via developer tools** — recorded plainly so nobody mistakes it for access control. It stops casual discovery of the URL, nothing more. Server-side protection would need a Netlify paid plan.

## Two real bugs fixed in `testing/_layer.html`

**1. A temporal-dead-zone crash was killing half the layer.** `apply()` runs at load and did `typeof renderer` on a `let` declared 85 lines below. On a `let`/`const` that is a ReferenceError, not a safe undefined check — so `apply()` threw and **every statement after it never ran**, taking the 3D viewer wiring and the clickable rows with it. The display panel still appeared because it is built before that call, which is why the failure presented as "some features are missing" rather than an obvious break. Declaration hoisted.

**2. Row matching had silently stopped working.** `decorate()` matched rows with `SHIPS.find(s => s.name === label)`. The live page now appends a link glyph, so `td.textContent.trim()` yields `"Avenger Stalker 🔗"` against a stored name of `"Avenger Stalker"`. Every lookup missed and every row was skipped without complaint. Replaced with a normalised lookup index.

**Worth generalising:** exact string matching against rendered page text is brittle by construction, and the silent `return` on a miss is why this sat unnoticed. Any future hook into live-page content should normalise and should log loudly when a lookup fails. Same shape as hard rule 12 — the code reported success while doing nothing.

## Other layer changes

- RSI links removed from the matrix rows. The ship name is plain text and the whole cell is clickable; the RSI link now lives on the ship detail page. All 229 URLs are retained in `CC_RSI` and were also exported to JSON/CSV.
- `DISPLAY` tab now toggles. It was `classList.add('open')` — it could only ever open.
- Default text size is now **130%** (was 100%), at the operator's request, still adjustable.
- `#cc-back` enlarged and made scale-aware — it was a fixed 15px, so it stayed small when everything else scaled up.

## .gitignore — added, please keep

`testing/` was entirely untracked and **not ignored**, so a `git add .` would have swept in 344 MB of GLB. Added:

```
testing/index.html
testing/_deploy/
testing/_models/
testing/_tools/
```

`testing/_layer.html` and `testing/build.py` remain tracked source. Verified with `git add -n testing/` — stages exactly those two files and nothing else.

## Two caveats for whoever works this repo next

**Stale `.git/index.lock`.** The Cowork device bridge cannot unlink files, so every `git` command run through it leaves an `index.lock` that git itself could not clean up. That blocks the next git operation with "Another git process seems to be running." Several were created and moved to `_to_delete/` during this session, and the repo was left clean. If you hit that error and no git process is actually running, this is why.

**Cleanup needed — the bridge cannot delete.** Please remove manually:
- `testing/_tools/node_modules/` and `testing/_tools/gltf-tools.tar.xz` — a partially-extracted first attempt, abandoned because the mount is too slow for thousands of small files
- `_to_delete/` — contains only moved-aside git lock files

## Not committed

Nothing was committed or pushed. `testing/_layer.html`, `testing/build.py` and the `.gitignore` change are the only things here worth committing; everything else is ignored build output.
