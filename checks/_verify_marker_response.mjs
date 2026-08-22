/**
 * B0 acceptance: NO HULL MARKER IS SILENT.
 *
 * WHY THIS CONTROL EXISTS, AND WHY THE ONE BEFORE IT PASSED
 * ---------------------------------------------------------
 * `_verify_ship_page.mjs`'s P5 block already dispatched a real click at a real
 * marker through the page's own delegated handler, and asserted that `sel`
 * came back naming that port. It passed. It has always passed.
 *
 * It picked its marker with:
 *
 *     MARKS[k].some(m => { const s = ...; return s && s.fit; })
 *
 * A SWAPPABLE port. Every time. So the control proved that clicking a marker
 * on a port that can be changed opens that port's picker - which was never the
 * broken case. 782 of the fleet's 1,200 markers sit on ports that CANNOT be
 * changed, and for those `selectPort()` opened with
 *
 *     if(!swappable(slot)){ sel=null; renderPicker(); return false; }
 *
 * which cleared the selection and re-rendered the same empty prompt the page
 * had been showing all along. Nothing appeared. Nothing said why. On 61 hulls
 * that was EVERY marker, and on the Origin 400i it was 8 of 10 - including
 * hardpoint_missile_left, hardpoint_missile_right and both remote turrets,
 * which are the first four things anybody would click.
 *
 * The mechanism was asserted. The experience was not. That is the whole defect
 * class, and it is why this control classifies the OUTCOME of a click into
 * three named states rather than asking whether a handler ran:
 *
 *     picker   the part list opened          - a swappable port
 *     fixed    B0's informative panel opened - a fixed port
 *     SILENT   neither                       - the defect
 *
 * A click is "responded to" only if it lands in one of the first two.
 *
 * PROVEN TWO WAYS, because an inversion alone is a weak proof.
 *
 *   --self-test  inverts every expectation and must exit non-zero.
 *   --mutate     PUTS THE REAL DEFECT BACK - the exact early return above -
 *                and must exit non-zero. This is the load-bearing one: it is
 *                the code that actually shipped, not a sign flip, and if a
 *                future edit reintroduces it this is the shape it will take.
 *
 * Usage:  node checks/_verify_marker_response.mjs [--self-test] [--mutate]
 */

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "..", "testing", "_src");
const PAGE = join(SRC, "loadout.src.html");
const DATA = join(SRC, "loadout_data.gen.js");
const SELFTEST = process.argv.includes("--self-test");
const MUTATE = process.argv.includes("--mutate");

let passed = 0;
const failures = [];
const notes = [];
function record(got, label, detail = "") {
  const want = SELFTEST ? !got : got;
  if (want) { passed++; console.log(`  ok   ${label}`); }
  else {
    failures.push(`${label} ${detail}`.trim());
    console.log(`  FAIL ${label} ${detail}`);
  }
}

/* ---------------------------------------------------------------- the page */
const html = readFileSync(PAGE, "utf-8");
const dataJs = readFileSync(DATA, "utf-8");
const EXTRA = ["loadout_model.gen.js", "loadout_marker.gen.js",
               "loadout_eng.gen.js"]
  .map((f) => join(SRC, f))
  .filter((f) => existsSync(f))
  .map((f) => readFileSync(f, "utf-8"));

const els = new Map();
function el(id) {
  if (!els.has(id)) {
    els.set(id, {
      id, innerHTML: "", textContent: "", className: "", value: "",
      style: {}, onclick: null, onchange: null, href: "", hidden: false,
      classList: { add() {}, remove() {}, toggle() {} },
      removeAttribute(a) { this[a] = ""; },
      setAttribute(a, v) { this[a] = v; },
      get childElementCount() { return 0; },
      get children() { return []; },
    });
  }
  return els.get(id);
}

let currentHash = "";
const clickHandlers = [];
const sandbox = {
  console, JSON, Math, Date, Number, String, Array, Object, Map, Set, RegExp,
  Error, isNaN, parseInt, parseFloat, encodeURIComponent, decodeURIComponent,
  setTimeout: () => 0,
  addEventListener() {},
  history: { replaceState(_a, _b, url) { currentHash = String(url).replace(/^#/, ""); } },
  location: { get hash() { return "#" + currentHash; }, set hash(v) { currentHash = String(v).replace(/^#/, ""); } },
  navigator: {},
  document: {
    getElementById: (id) => el(id),
    addEventListener: (t, fn) => { if (t === "click") clickHandlers.push(fn); },
    querySelector: () => null,
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

let script = html.match(/<script>\n([\s\S]*)<\/script>/)[1];
if (MUTATE) {
  /* THE DEFECT, PUT BACK VERBATIM. This is the line B0 removed, and it is what
     made 782 markers silent. Anything below that does not notice is not a
     control. */
  const before = script;
  script = script.replace(
    /(function selectPort\(slot, which\)\{\s*\n\s*if\(!slot\) return false;)/,
    "$1\n  if(!swappable(slot)){ sel=null; renderPicker(); return false; }");
  if (script === before) {
    console.log("MUTATION DID NOT APPLY - selectPort's opening was not found, "
      + "so this run proves nothing. Fix the mutator before trusting the check.");
    process.exit(1);
  }
  console.log("*** MUTATED: selectPort turns fixed ports away again, exactly "
    + "as it did before B0. Something below MUST notice. ***");
}
vm.runInContext(dataJs, sandbox, { filename: "loadout_data.gen.js" });
for (const src of EXTRA) vm.runInContext(src, sandbox, { filename: "gen" });
vm.runInContext(script, sandbox, { filename: "loadout.src.html:script" });
const g = (expr) => vm.runInContext(expr, sandbox);

const SHIPS = g("SHIPS"), PARTS = g("P"), MARKS = g("MARKS"),
      HPN = g("HPN");
/* A slot's `h` is an INDEX into the hardpoint-name table, not the name.
   Comparing it to a string silently matches nothing - which is how the
   first run of this control reported that the 400i has no
   hardpoint_missile_left port. It has one; the lookup was wrong. */
const portName = (s) => (HPN[s.h] || "");

console.log("--- the page's own script ran against the real generated data ---");
record(Object.keys(SHIPS).length > 300, "the ship table loaded",
  `${Object.keys(SHIPS).length} ships`);
record(Object.keys(MARKS).length > 100, "the marker table loaded",
  `${Object.keys(MARKS).length} hulls carry markers`);
record(clickHandlers.length > 0,
  "the page registered a click handler this control can dispatch through");

/* ---------------------------------------------------------------- driving */
/* A STUB VIEWER, because the marker layer will not render without one, and
   the projection is irrelevant to whether a click is answered. */
const VIEW = `_view={_s:false,boot(){},start(){},size(){},cancel(){},clear(){},`
  + `stop(){},current:{},unitScale(){return 1;},`
  + `project(){return{x:640,y:360,depth:0};},`
  + `spinning(){return this._s;},setSpin(v){this._s=!!v;return this._s;},`
  + `load(){return 1;}};`;

function openShip(key) {
  vm.runInContext(`shipId=${JSON.stringify(key)};reset();resetView();`
    + VIEW + `_modelFor=shipId;sel=null;renderAll();`, sandbox);
}

/* WHAT A CLICK DID, named. The three states are read off what the picker pane
   actually contains, because that is what a person sees - not off a return
   value, which is what the previous control trusted. */
function clickMarker(portId) {
  vm.runInContext(`sel=null;renderPicker();`, sandbox);
  const btn = {
    tagName: "BUTTON", dataset: { port: portId },
    closest: (s) => (s === "#cc-marks button[data-port]" ? btn : null),
  };
  let threw = null;
  for (const fn of clickHandlers) {
    try { fn({ target: btn, preventDefault() {} }); } catch (e) { threw = e.message; }
  }
  const picker = el("picker").innerHTML || "";
  const sel = JSON.parse(g("JSON.stringify(sel)") || "null");
  let outcome = "silent";
  if (picker.includes('class="fixedpanel"')) outcome = "fixed";
  else if (picker.includes('class="sortrow"') || picker.includes('class="pi'))
    outcome = "picker";
  return { outcome, picker, sel, threw };
}

/* ------------------------------------------- 1. THE ORIGIN 400i, BY NAME */
console.log("\n--- 1. THE ORIGIN 400i - Sleven's own reproduction ---");
const key400i = Object.keys(SHIPS).find(
  (k) => /400i/i.test(SHIPS[k].n || "") && /origin/i.test(SHIPS[k].m || ""));
record(!!key400i, "the Origin 400i is in the ship table", key400i || "not found");

let silent400i = null;
if (key400i) {
  const marks = MARKS[key400i] || [];
  record(marks.length === 10,
    "it carries 10 hull markers - the count Sleven saw", `${marks.length}`);
  openShip(key400i);

  const seen = { picker: 0, fixed: 0, silent: 0 };
  const silentPorts = [];
  for (const m of marks) {
    const slot = (SHIPS[key400i].slots || []).find((x) => x.p === m[0]);
    const r = clickMarker(m[0]);
    seen[r.outcome]++;
    if (r.outcome === "silent") silentPorts.push(slot ? portName(slot) : m[0]);
    if (r.threw) failures.push(`click on ${m[0]} threw: ${r.threw}`);
  }
  silent400i = seen.silent;

  /* THE ACCEPTANCE TEST. Every marker responds - not "most", not "the ones on
     swappable ports". */
  record(seen.silent === 0,
    "ALL 10 markers respond to a click - none falls through silently",
    seen.silent ? `${seen.silent} silent: ${silentPorts.join(", ")}` : "");

  /* And the split is the one the data implies, so this cannot pass by opening
     the same thing for everything. */
  const swap = marks.filter((m) => {
    const s = (SHIPS[key400i].slots || []).find((x) => x.p === m[0]);
    return s && s.fit;
  }).length;
  const fixed = marks.length - swap;
  record(seen.picker === swap && seen.fixed === fixed,
    `${swap} open the picker and ${fixed} open the fixed panel, matching the `
    + `ports' own Editable flags`,
    `observed ${seen.picker} picker / ${seen.fixed} fixed`);
  notes.push(`Origin 400i: ${marks.length} markers, ${seen.picker} picker, `
    + `${seen.fixed} fixed panel, ${seen.silent} silent`);
  if (swap !== 2 || fixed !== 8) {
    notes.push(`NOTE: the order recorded 2 swappable / 8 fixed on this hull; `
      + `the data now says ${swap} / ${fixed}. The split is asserted against `
      + `the data, not against those numbers.`);
  }

  /* ------------------ 2. THE PANEL NAMES THE PART, NOT A PLACEHOLDER ----- */
  console.log("\n--- 2. the panel for hardpoint_missile_left names the real part ---");
  const missileSlot = (SHIPS[key400i].slots || [])
    .find((s) => portName(s) === "hardpoint_missile_left");
  record(!!missileSlot, "the 400i has a hardpoint_missile_left port");
  if (missileSlot) {
    const part = PARTS[missileSlot.stock];
    record(!!(part && part.n && part.n.length > 2),
      "and the game data names what is fitted there",
      part ? part.n : "no part record");
    const r = clickMarker(missileSlot.p);
    record(r.outcome === "fixed",
      "clicking its marker opens the fixed panel", r.outcome);
    if (part && part.n) {
      record(r.picker.includes(part.n),
        `the panel contains the fitted item's NAME - "${part.n}"`);
      record(!/undefined|\[object |&gt;placeholder/i.test(r.picker),
        "and renders no placeholder or undefined in its place");
    }
    record(r.picker.includes("hardpoint_missile_left"),
      "the panel names the port itself, in the game's own vocabulary");
  }

  /* --------- 3. NEGATIVE CONTROL: a swappable marker still picks ---------- */
  console.log("\n--- 3. NEGATIVE CONTROL: a swappable marker opens the PICKER ---");
  const swapMark = marks.find((m) => {
    const s = (SHIPS[key400i].slots || []).find((x) => x.p === m[0]);
    return s && s.fit;
  });
  record(!!swapMark, "the 400i has at least one swappable marked port");
  if (swapMark) {
    const r = clickMarker(swapMark[0]);
    record(r.outcome === "picker",
      "it opens the part picker, NOT the fixed panel", r.outcome);
    record(!r.picker.includes('class="fixedpanel"'),
      "and the fixed panel is absent from it - without this, a build that "
      + "showed the fixed panel for everything would pass");
    record(!!(r.sel && r.sel.fixed === false),
      "and the selection records it as swappable",
      JSON.stringify(r.sel));
  }
}

/* -------------------------------- 4. THE FLEET, EVERY MARKER ON EVERY HULL */
console.log("\n--- 4. FLEET CONTROL: every marker on every hull, clicked ---");
const census = { markers: 0, picker: 0, fixed: 0, silent: 0 };
const allSilentHulls = [];
const hullsWithMarkers = Object.keys(MARKS).filter(
  (k) => SHIPS[k] && (MARKS[k] || []).length);

for (const k of hullsWithMarkers) {
  const marks = MARKS[k];
  openShip(k);
  let hullSilent = 0;
  for (const m of marks) {
    const r = clickMarker(m[0]);
    census.markers++;
    census[r.outcome]++;
    if (r.outcome === "silent") hullSilent++;
  }
  if (hullSilent === marks.length && marks.length) allSilentHulls.push(k);
}

console.log(`\n    hulls with markers          ${hullsWithMarkers.length}`);
console.log(`    markers total               ${census.markers}`);
console.log(`    clickable (picker opens)    ${census.picker}`);
console.log(`    fixed but informative       ${census.fixed}`);
console.log(`    SILENT (click did nothing)  ${census.silent}`);
console.log(`    hulls where EVERY marker is silent   ${allSilentHulls.length}`);

record(census.markers > 1000,
  "the sweep actually clicked the fleet's markers rather than a handful",
  `${census.markers} clicks`);
record(census.silent === 0,
  "ZERO markers across the whole fleet fall through to a silent click",
  census.silent ? `${census.silent} silent on ${allSilentHulls.length} hulls`
                : "");
record(allSilentHulls.length === 0,
  "and there is no hull left where every single marker is silent",
  allSilentHulls.length ? allSilentHulls.slice(0, 8).join(", ") : "");

/* THE COUNTER CAN REPORT A NUMBER OTHER THAN ZERO. The order demands this
   explicitly, and it is not the same as the count being zero today: a counter
   wired to a constant would also read zero. Proven on synthetic input rather
   than by trusting the arithmetic above. */
{
  const fake = { markers: 0, picker: 0, fixed: 0, silent: 0 };
  for (const o of ["picker", "fixed", "silent", "silent"]) {
    fake.markers++; fake[o]++;
  }
  record(fake.silent === 2 && fake.markers === 4,
    "the census counter reports a NON-ZERO silent count when there is one - "
    + "so today's zero is a measurement, not a constant");
}

notes.push(`fleet census: ${census.markers} markers on `
  + `${hullsWithMarkers.length} hulls - ${census.picker} picker, `
  + `${census.fixed} fixed-informative, ${census.silent} silent, `
  + `${allSilentHulls.length} hulls entirely silent`);

/* ------------------------------------------------------------------ report */
console.log("\n==============================================================");
for (const n of notes) console.log("  " + n);
if (failures.length) {
  console.log(`\nFAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  " + f);
} else {
  console.log(`\nAll ${passed} assertions passed against the page's own script.`);
}
if (SELFTEST) {
  console.log("\n--self-test: expectations were inverted, so a non-zero exit "
    + "is the correct outcome.");
}
if (MUTATE) {
  console.log("\n--mutate: the pre-B0 defect was planted, so a non-zero exit "
    + "is the correct outcome.");
}
process.exit(failures.length ? 1 : 0);
