# Two real bugs found and fixed in testing/_layer.html — 2026-08-01

Found while building a portable concept build. Both were live in `testing/_layer.html` and both are now fixed; `testing/index.html` has been rebuilt. The live site was not touched.

## Bug 1 — a temporal-dead-zone crash killed half the layer

`apply()` runs at load. At what was line 517 it does:

```js
if(typeof renderer!=='undefined' && renderer) setTimeout(size,80);
```

`renderer` was declared at line 602 with `let`. **On a `let`/`const`, `typeof` inside the temporal dead zone throws a ReferenceError — it is not a safe undefined check.** That idiom is only safe for `var` or genuinely undeclared identifiers.

So `apply()` threw `Cannot access 'renderer' before initialization` at load, and **every statement after it never executed** — the entire 3D viewer setup and the row-click wiring included. The display panel still rendered because it is built before `apply()` is called, which is why the failure looked like "some features are missing" rather than an obvious break.

Fix: the `let renderer,scene,camera,controls,current,raf,loader;` declaration is hoisted to the top of the layer script.

## Bug 2 — ship rows stopped matching, so nothing was clickable

`decorate()` matched rows to ship records with an exact compare:

```js
const ship=SHIPS.find(s=>s.name===label);
```

The live page now appends a link glyph to ship names, so `td.textContent.trim()` yields `"Avenger Stalker 🔗"` while `SHIPS[].name` is `"Avenger Stalker"`. Every lookup returned undefined and every row was skipped silently.

This is drift between the live page and the layer — the exact failure mode the layer architecture exists to survive. It did survive it in the sense that nothing broke visibly; it just quietly stopped working.

Fix: added `CC_NORM` (strips emoji/symbol codepoints and collapses whitespace) and a `CC_LOOKUP` index built once from `SHIPS`. Matching is now on the normalised form. Also added a guard so clicking the RSI link inside a cell follows the link instead of opening the detail panel.

**Verified after fix:** 254 of 254 rows clickable, 234 showing as having a matched model folder, zero page errors.

**Worth noting for future layer work:** exact string matching against rendered page text is brittle by construction. Any future hook into live-page content should normalise, and should log loudly when a lookup misses rather than `return`ing silently — a silent skip is why this sat unnoticed. This is the same shape as hard rule 12: the code reported success while doing nothing.

## Portable concept build produced

A single self-contained HTML was built for showing the project to other people without a local server:

- Full site plus the testing layer, all 254 ships clickable
- three.js r128, GLTFLoader, OrbitControls, DRACOLoader and the Draco WASM decoder all inlined — **no CDN, no network**
- 15 ships carry Draco-compressed models embedded as base64, decoded in-browser and handed to `GLTFLoader.parse()` so nothing is ever fetched
- 15.0 MB total, opens from `file://` by double-clicking

Verified in a headless browser from `file://`: Carrack renders in 1.0s from its embedded 0.55 MB Draco model, display engine presets apply correctly, zero page errors, zero external requests other than Google Fonts and the site's own currency API, both of which degrade gracefully offline.

This is a demo artifact, not a deliverable to commit — `sc-ships/` stays gitignored and no GLB was added to the repo.

## Note on the CDN dependency

`testing/_layer.html` still loads three.js from `cdn.jsdelivr.net` for local use. That is fine on a machine with internet, but it means the testing area's 3D viewer silently stops working offline or if jsdelivr is blocked. Worth vendoring those four files under `testing/` at some point so the testing area has no external runtime dependency.
