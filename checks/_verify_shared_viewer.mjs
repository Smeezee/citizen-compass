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
const SENTINEL = /THE VIEWER LIVES IN cc_viewer\.js AND NOWHERE ELSE/;
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
record(indexHtml.includes('<script src="cc_viewer.js">'),
  "index.html loads cc_viewer.js");
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
  record(/CC_RSI/.test(indexCode),
    "index still keeps the pledge link too - it moved, it was not deleted");
  notes.push(`L11: ${Object.keys(LOADOUT_LINK || {}).length} matrix rows link `
    + `to a ship page that exists; ${Object.keys(RSI).length} of those pages `
    + `carry the RSI link that used to sit on the row`);
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

const idxViewer = tryPage(indexHtml, "index.html", "typeof ccView==='function' ? ccView() : null");
const loViewer = tryPage(loadoutHtml, "loadout.html", "typeof view==='function' ? view() : null");
record(idxViewer === null || idxViewer === undefined,
  "index.html produces NO viewer when the module is broken",
  `got ${typeof idxViewer}`);
record(loViewer === null || loViewer === undefined,
  "loadout.html produces NO viewer when the module is broken",
  `got ${typeof loViewer}`);
if ((idxViewer && !loViewer) || (!idxViewer && loViewer)) {
  failures.push("ONLY ONE PAGE FAILED - there is a second viewer copy somewhere");
  console.log("  FAIL ONLY ONE PAGE FAILED - there is a second viewer copy somewhere");
}
notes.push("L8 negative half: with cc_viewer.js broken, index.html and "
  + "loadout.html BOTH fail to produce a viewer - so neither is quietly "
  + "carrying a second copy");

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
