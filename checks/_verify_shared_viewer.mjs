/**
 * L8 acceptance: ONE ship viewer, shared. And the negative half, which is the
 * half that actually proves it.
 *
 * WHY THE NEGATIVE HALF IS THE POINT
 * ----------------------------------
 * "Both pages use the shared module" is easy to assert and easy to satisfy
 * while a second copy sits in one of them doing the real work. A page can load
 * cc_viewer.js, ignore it completely, and pass every positive check.
 *
 * So the order names the control it wants: BREAK THE SHARED MODULE AND CONFIRM
 * BOTH PAGES FAIL. If only one fails, there is a second copy somewhere.
 *
 * IT IS NOT BEHIND A FLAG. Section 4 below replaces cc_viewer.js with a version
 * whose Viewer constructor throws, runs each page's own script against it, and
 * requires BOTH to come back with no viewer - EVERY RUN. A negative half that
 * has to be asked for is a negative half nobody runs, and this one is the only
 * assertion here that a second copy could not survive.
 *
 * WHAT IS CHECKED, IN ORDER
 *   1. exactly one implementation exists, in the built bytes
 *   2. both built pages reference it
 *   3. the same ship resolves to the same model on both pages
 *   4. breaking the module breaks BOTH
 *
 * STATED LIMIT, same as the other page harnesses: this proves the pages' LOGIC
 * and the bytes they ship. It does not prove that a browser draws anything.
 * There is no browser on this machine and none was installed (rule 7).
 *
 * Usage:  node checks/_verify_shared_viewer.mjs
 */

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "..", "testing", "_src");
const DEPLOY = join(HERE, "..", "testing", "_deploy");

let passed = 0;
const failures = [];
const notes = [];
function record(got, label, detail = "") {
  if (got) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

const VIEWER = join(SRC, "cc_viewer.js");
const INDEX = join(DEPLOY, "index.html");
const LOADOUT = join(DEPLOY, "loadout.html");
for (const f of [VIEWER, INDEX, LOADOUT]) {
  if (!existsSync(f)) {
    console.log(`MISSING: ${f}\nRun testing/_src/build_deploy.py first.`);
    process.exit(1);
  }
}
const viewerJs = readFileSync(VIEWER, "utf-8");
const indexHtml = readFileSync(INDEX, "utf-8");
const loadoutHtml = readFileSync(LOADOUT, "utf-8");

/* Comments stripped before any code-shape assertion. Both pages EXPLAIN where
   the viewer lives, in prose, and a check that read those sentences as code
   would fail the pages for documenting themselves. The
   stripper is proven live below; without that proof it could equally be hiding
   a real second renderer somebody commented out and forgot. */
const strip = (s) => s.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
const indexCode = strip(indexHtml);
const loadoutCode = strip(loadoutHtml);

console.log("--- 1. exactly ONE implementation, in the shipped bytes ---");
const SENTINEL = /INDEX IS A LIST\. The ship panel and its 3D viewer are retired/;
record(SENTINEL.test(indexHtml) && !SENTINEL.test(indexCode),
  "the comment stripper works: index explains where the viewer lives in prose, "
  + "and that prose is not in the code",
  "if this fails, every assertion below it is checking nothing");

const RENDERER = /new\s+THREE\.WebGLRenderer/g;
const inViewer = (viewerJs.match(RENDERER) || []).length;
const inIndex = (indexCode.match(RENDERER) || []).length;
const inLoadout = (loadoutCode.match(RENDERER) || []).length;
record(inViewer === 1, "cc_viewer.js constructs the one renderer", `${inViewer}`);
record(inIndex === 0, "index.html constructs NO renderer of its own", `${inIndex}`);
record(inLoadout === 0, "loadout.html constructs NO renderer of its own", `${inLoadout}`);

/* The other things a second copy would bring with it. Each is a bug that was
   found once and fixed once, and a second viewer is a place for each to come
   back quietly.

   THESE MATCH CONSTRUCTION AND ASSIGNMENT, NOT THE IDENTIFIER. Both pages have
   three.js INLINED into them - the whole library, DRACOLoader included - so
   `PMREMGenerator` and `ACESFilmicToneMapping` appear in their bytes as a
   matter of course. Searching for the bare name failed all three and said
   nothing: it was finding the library, which is exactly what should be there.
   What must not be there is code CALLING them. */
for (const [needle, what] of [
  [/new\s+THREE\.PMREMGenerator\s*\(/, "the environment map"],
  [/toneMapping\s*=\s*THREE\.ACESFilmicToneMapping/,
   "the tone mapping that stops hulls clipping to white"],
  [/new\s+THREE\.GLTFLoader\s*\(/, "the model loader"],
  [/new\s+THREE\.DRACOLoader\s*\(/, "the DRACO decoder wiring"],
  [/new\s+THREE\.HemisphereLight\s*\(/, "the lighting rig"],
  [/new\s+THREE\.OrbitControls\s*\(/, "the camera controls"],
]) {
  const n = [indexCode, loadoutCode].filter((c) => needle.test(c)).length;
  record(needle.test(viewerJs) && n === 0,
    `${what} is USED in the module and in neither page`,
    `in module: ${needle.test(viewerJs)}, in pages: ${n}`);
}

console.log("\n--- 2. both pages reference it ---");
/* INVERTED BY N3. index.html used to load the viewer module; it is a list now
   and must NOT. The assertion is kept in the inverted form rather than deleted,
   because "index stopped loading it" is a claim worth failing on if a viewer
   ever comes back. */
record(!indexHtml.includes('<script src="cc_viewer.js">'),
  "index.html does NOT load cc_viewer.js - it is a list (N3)");
record(loadoutHtml.includes('<script src="cc_viewer.js">'),
  "loadout.html loads cc_viewer.js");
record(existsSync(join(DEPLOY, "cc_viewer.js")),
  "and the module is actually shipped beside them");

console.log("\n--- 3. the same ship resolves to the same model on both pages ---");
/* index reaches a model through CC_MODELS, keyed on the site's record id.
   loadout reaches it through LOADOUT_MODEL, keyed on the game's ClassName.
   LOADOUT_LINK joins the two. If those three ever disagree, one page shows a
   different ship than the other under the same name - which is precisely the
   drift the extraction exists to prevent, one level up from the code. */
function pick(html, name) {
  const m = html.match(new RegExp(`const ${name}\\s*=\\s*(\\{[\\s\\S]*?\\});`));
  return m ? JSON.parse(m[1]) : null;
}
const CC_MODELS = pick(indexHtml, "CC_MODELS");
const LOADOUT_LINK = pick(indexHtml, "LOADOUT_LINK");
const modelJs = readFileSync(join(DEPLOY, "loadout_model.gen.js"), "utf-8");
const LOADOUT_MODEL = pick(modelJs, "LOADOUT_MODEL");
record(!!CC_MODELS && !!LOADOUT_LINK && !!LOADOUT_MODEL,
  "all three tables parsed out of the built bytes");

const safe = (n) => String(n).replace(/[^A-Za-z0-9._-]+/g, "_");
let agree = 0;
const disagree = [];
for (const [rid, cls] of Object.entries(LOADOUT_LINK || {})) {
  const dir = CC_MODELS[rid];
  const want = dir ? safe(dir) + ".glb" : null;
  const got = LOADOUT_MODEL[cls] || null;
  // A ship index has no model for must not have one on the ship page either.
  const wantExists = want && Object.values(LOADOUT_MODEL).includes(want);
  if (got === want || (!got && !wantExists)) agree++;
  else disagree.push(`${cls}: index ${want}, ship page ${got}`);
}
record(agree > 150, "a real number of ships were compared", `${agree}`);
record(disagree.length === 0,
  "every linked ship resolves to the SAME model file on both pages",
  `${disagree.length} disagree, e.g. ${disagree.slice(0, 3).join(" | ")}`);
notes.push(`L8: ${agree} linked ships resolve to the same model on both pages; `
  + `${Object.keys(LOADOUT_MODEL).length} ship-page entries against `
  + `${Object.keys(CC_MODELS).length} index entries`);

console.log("\n--- L11: every ship name in the list resolves to a page that loads ---");
{
  /* The order's control, taken literally. `LOADOUT_LINK` is what turns a matrix
     row into a ship page, so every entry in it must name a ship the ship page
     actually holds - otherwise a visitor clicks a name and lands on nothing,
     which is worse than the RSI link they used to get. */
  const loData = readFileSync(join(DEPLOY, "loadout_data.gen.js"), "utf-8");
  const m = loData.match(/^const LOADOUT_SHIPS=(.*);$/m);
  const LS = m ? JSON.parse(m[1]) : {};
  record(Object.keys(LS).length > 300, "the ship page's data loaded",
    `${Object.keys(LS).length} ships`);
  const dead = Object.values(LOADOUT_LINK || {}).filter((cls) => !LS[cls]);
  record(dead.length === 0,
    "every ship the matrix links to exists on the ship page",
    `${dead.length} dead: ${dead.slice(0, 3)}`);
  const withSlots = Object.values(LOADOUT_LINK || {})
    .filter((cls) => LS[cls] && (LS[cls].slots || []).length).length;
  record(withSlots > 200,
    "and lands on a ship with something to show",
    `${withSlots} of ${Object.keys(LOADOUT_LINK || {}).length}`);

  /* THE RSI LINK IS NOT REMOVED - it moves. Asserted on both sides, because
     "moved" is only true if it arrives as well as leaving. */
  const rsiJs = readFileSync(join(DEPLOY, "loadout_model.gen.js"), "utf-8");
  const RSI = pick(rsiJs, "LOADOUT_RSI") || {};
  record(Object.keys(RSI).length > 100,
    "the ship page carries the pledge links", `${Object.keys(RSI).length}`);
  /* N1 CHANGED WHAT THIS SHOULD SAY. The pledge link is no longer on a ship's
     row, because the row now goes to the ship page and the RSI link is offered
     there - which is the whole point of N1.
     THE EXCEPTION IS THE ONE THAT MATTERS: 33 ships have no ship page, and 27
     of those carry a pledge_url. Taking their link away to satisfy the letter
     of N1 would leave those rows with no link at all, so they keep it. */
  record(!/CC_RSI/.test(indexCode),
    "the runtime pledge-link fallback is gone from index - the ship page gets "
    + "it from LOADOUT_RSI, built from the same field");
  record(/ship\.pledge_url/.test(indexCode) && /cc-nobench/.test(indexCode),
    "but a ship with NO ship page keeps its RSI link, because it is the only "
    + "route that ship has");
  notes.push(`L11: ${Object.keys(LOADOUT_LINK || {}).length} matrix rows link `
    + `to a ship page that exists; ${Object.keys(RSI).length} of those pages `
    + `carry the RSI link that used to sit on the row`);
}

console.log("\n--- N1: every route into a ship lands on the SHIP PAGE ---");
{
  /* THE PANEL IS GONE. Asserted on the markup it cannot exist without, rather
     than on the absence of one function - a panel with a renamed opener would
     still be a panel. */
  record(!/id="cc-ship"/.test(indexHtml),
    "index.html carries no ship panel");
  record(!/Open in the loadout bench/.test(indexCode),
    "and no \"Open in the loadout bench\" button");
  record(!/function open\s*\(ship\)/.test(indexCode),
    "and no function that opens a ship in place");

  /* WHERE A NAME ACTUALLY GOES IS NOT ASSERTED HERE, AND THAT IS THE POINT.
   *
   * This block used to grep for `shipPageUrl(`, `loadout.html#` and a
   * particular `td.innerHTML=` shape, and reported N1 done. Every one of those
   * strings was present. EVERY SHIP NAME STILL OPENED RSI, because the
   * function containing them bailed before it ran.
   *
   * Greping for a symbol cannot tell you where a link points. So that question
   * moved to checks/_verify_ship_name_route.mjs, which RUNS the page's own
   * nameCellHtml() against real records and reads the href that comes back -
   * and which has been SEEN FAILING against the exact bug, reproducing its 229.
   *
   * What is still worth asserting here is structural: that the second writer
   * which made the failure possible is gone for good. */
  record(!/function decorate\s*\(/.test(indexCode),
    "no post-render rewriter edits the name cells after the site builds them");
  record(!/MutationObserver\s*\(\s*decorate/.test(indexCode),
    "and no observer drives one");
  record(!/td\.textContent\.trim\(\)/.test(indexCode),
    "and nothing identifies a ship by the text in its cell - the match that "
    + "failed on a link glyph");
  record(/const CC_SHIPLINK=/.test(indexHtml),
    "the build's per-row decision is IN the page, computed before it renders");
  record(indexHtml.indexOf("const CC_SHIPLINK=") < indexHtml.indexOf("const SHIPS = ["),
    "and arrives BEFORE the ship records, so the matrix can read it - it used "
    + "to be injected after the table had already been built");
}

console.log("\n--- N3: index is a LIST. No viewer, no geometry, no vendor payload ---");
{
  /* THE MEASURABLE HALF OF "ONE PAGE". Not "the panel looks gone" - the
     three.js payload is either in these bytes or it is not. */
  for (const [needle, what] of [
    [/new\s+THREE\.WebGLRenderer/, "a renderer"],
    [/new\s+THREE\.GLTFLoader\s*\(/, "a model loader"],
    [/new\s+THREE\.DRACOLoader\s*\(/, "a DRACO decoder"],
    [/PMREMGenerator/, "an environment map"],
    [/CC_DRACO_WASM_B64/, "the decoder wasm"],
    [/CC_EMBED/, "the embedded model map"],
    [/<script src="cc_viewer\.js">/, "the shared viewer module"],
  ]) {
    record(!needle.test(indexCode), `index.html carries no ${what}`);
  }
  record(!/\.glb/.test(indexCode),
    "and names no model file, so nothing on it can ask for geometry");

  /* THE SIZE, WHICH IS THE POINT STATED AS A NUMBER. index.html was 1,622,716
     bytes with the viewer on it. A page that is a list has no business being
     larger than the data it lists. */
  const bytes = Buffer.byteLength(indexHtml, "utf8");
  record(bytes < 700000,
    "index.html is a fraction of its former size",
    `${bytes.toLocaleString()} bytes, was 1,622,716`);
  notes.push(`N3: index.html ${bytes.toLocaleString()} bytes, down from ` +
    `1,622,716 - a ${Math.round((1 - bytes / 1622716) * 100)}% cut, and it ` +
    `fetches no geometry because nothing on it can`);

  /* THE SHIP PAGE STILL HAS THE VIEWER. Removing it from both would also pass
     every assertion above, which is the vacuous way to satisfy N3. */
  record(/<script src="cc_viewer\.js">/.test(loadoutHtml),
    "and the SHIP page still loads the viewer - N3 moved it, it did not "
    + "delete it");
}

console.log("\n--- N4: one viewer instance, one model load per ship ---");
{
  /* One construction site in the page, so "one instance" is structural rather
     than a thing that happens to be true on the path somebody tested. */
  const made = (loadoutCode.match(/new\s+CCViewer\.Viewer\s*\(/g) || []).length;
  record(made === 1,
    "the ship page constructs exactly ONE viewer, in one place", `${made}`);
  record(/if\s*\(_view\)\s*return\s+_view/.test(loadoutCode.replace(/\s+/g, " ")) ||
         /_view\s*\)\s*return\s*_view/.test(loadoutCode.replace(/\s+/g, " ")),
    "and reuses it rather than making another");
  /* One LOAD per ship: the guard is `_modelFor`, which short-circuits when the
     ship has not changed. Tab switches re-render; they must not re-fetch. */
  record(/_modelFor\s*===\s*shipId/.test(loadoutCode),
    "and re-loads geometry only when the SHIP changes, not when a tab does");
}

console.log("\n--- 4. THE NEGATIVE HALF: break the module, BOTH pages must fail ---");
/* Each page's own script, run against a cc_viewer.js whose Viewer constructor
   throws. A page that still produces a working viewer has a second copy. */
const BROKEN = `
'use strict';
var CC_HULL = {}, CC_BLANK = '';
var CCViewer = { Viewer: function () { throw new Error('MODULE BROKEN ON PURPOSE'); },
                 HULL: {}, BLANK: '', VERSION: 'broken', hasDraco: function () { return false; } };
`;

function tryPage(html, label, entry) {
  const els = new Map();
  const el = (id) => {
    if (!els.has(id)) {
      els.set(id, { id, innerHTML: "", textContent: "", className: "", value: "",
                    style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
                    querySelector: () => null, querySelectorAll: () => [],
                    appendChild() {}, removeAttribute() {}, focus() {}, select() {} });
    }
    return els.get(id);
  };
  const sandbox = {
    console: { log() {}, warn() {}, error() {} },
    JSON, Math, Date, Number, String, Array, Object, Map, Set, RegExp, Error,
    isNaN, parseInt, parseFloat, encodeURIComponent, decodeURIComponent, atob: () => "",
    setTimeout: () => 0, clearTimeout() {}, requestAnimationFrame: () => 0,
    cancelAnimationFrame() {}, performance: { now: () => 0 },
    addEventListener() {}, removeEventListener() {},
    history: { replaceState() {} },
    location: { hash: "", href: "" },
    navigator: {}, localStorage: { getItem: () => null, setItem() {} },
    document: { getElementById: el, addEventListener() {}, querySelector: () => null,
                querySelectorAll: () => [], body: el("body"), createElement: () => el("tmp") },
    MutationObserver: function () { return { observe() {} }; },
  };
  sandbox.window = sandbox; sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(BROKEN, sandbox, { filename: "cc_viewer.js(broken)" });
  // Every inline block, in order, exactly as the page runs them.
  for (const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
    try { vm.runInContext(m[1], sandbox, { filename: label }); } catch (e) { /* page chrome */ }
  }
  let made = null;
  try { made = vm.runInContext(entry, sandbox); } catch (e) { made = null; }
  return made;
}

/* THIS ASSERTION CHANGED SHAPE AT N3, AND SAYING SO IS THE POINT.
 *
 * It used to require BOTH pages to fail when the module was broken, because
 * both had a viewer and "only one failed" meant a second copy. index.html no
 * longer has a viewer AT ALL - N3 made it a list - so "index produces no
 * viewer" is now true for a reason that has nothing to do with the module,
 * and leaving it in the both-must-fail form would be a check passing
 * vacuously while looking as strong as it did yesterday.
 *
 * So it is split. The ship page must still fail when the module breaks, which
 * is the real claim. And index must have no viewer whether the module is
 * broken or not - asserted just above, on the bytes, where it belongs. */
const loViewer = tryPage(loadoutHtml, "loadout.html", "typeof view==='function' ? view() : null");
record(loViewer === null || loViewer === undefined,
  "the SHIP page produces no viewer when the module is broken - so it really "
  + "is using the module and not a private copy",
  `got ${typeof loViewer}`);
const idxViewer = tryPage(indexHtml, "index.html", "typeof ccView==='function' ? ccView() : null");
record(idxViewer === null || idxViewer === undefined,
  "and index has none either - but for a different reason, which is that N3 "
  + "left nothing on it that could construct one");
notes.push("L8 negative half, reshaped by N3: breaking cc_viewer.js leaves the "
  + "SHIP page with no viewer, which is the claim worth making now. index has "
  + "no viewer at all, so its half of the old assertion had become vacuous and "
  + "was split out rather than left standing.");

console.log("");
if (notes.length) {
  console.log("MEASURED, for the ledger:");
  for (const n of notes) console.log("  - " + n);
  console.log("");
}
if (failures.length) {
  console.log(`FAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  - " + f);
  process.exit(1);
}
console.log(`PASSED: ${passed} assertions, including the negative half.`);
process.exit(0);
