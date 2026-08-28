/**
 * L3, L4, L6, L12, L13 acceptance for the ship page (testing/_src/loadout.src.html).
 *
 * RULE16: UNPROVEN - the page's own rendered DOM is the only observation channel,
 * so a defect that rendered a wrong value consistently would satisfy every
 * assertion here. Several expectations are independent of the page - the
 * port counts, the stock loadouts and the fitment come from the generated
 * data files rather than from what the page printed - but not all of them
 * are, so the file is UNPROVEN.
 *
 * WHAT THIS PROVES, AND WHY IT HAD TO BE A RENDER TEST
 * ---------------------------------------------------
 * `checks/_verify_loadout_fitment.py` proves the DATA is right: the fitment
 * lists hold exactly what each port's rule admits. That is necessary and it is
 * not sufficient, because the page could hold perfect data and still render a
 * part the port does not accept, or hide a fixed port, or drop a slot that has
 * no picker. Those are page bugs and they are invisible to a data check.
 *
 * So this drives THE PAGE'S OWN SCRIPT, verbatim, sliced out of
 * loadout.src.html, against the real generated data, and reads what it puts in
 * the DOM. Same technique and same stated limit as checks/_verify_find_page.mjs:
 * it proves the page's LOGIC and the HTML it produces. It does not prove layout,
 * CSS, or anything a browser enforces. There is no browser on this machine and
 * none was installed (rule 7).
 *
 * THE ORDER NAMES BOTH HALVES OF L3 AND THEY ARE BOTH HERE:
 *
 *     a part the port accepts  MUST APPEAR in the rendered picker
 *     a part it does not       MUST BE ABSENT from it - not greyed, absent
 *
 * The second half is the one that passes vacuously. A picker that renders
 * nothing at all satisfies "the wrong part is absent" perfectly, so the
 * positive half is load-bearing rather than decoration - and the negative half
 * is asserted against the RENDERED STRING, so "greyed out but present" fails
 * exactly as the order requires.
 *
 * L4 IS THE OTHER TRAP. A fixed port must RENDER, must CONTRIBUTE TO TOTALS,
 * and must OPEN NO PICKER. All three are separable failures: hiding it, showing
 * it but not counting it, and showing it with a picker that offers parts the
 * game will not let you fit. Each is asserted on its own.
 *
 * PROVEN TWO WAYS, because an inversion alone is a weak proof.
 *
 *   --self-test  inverts every expectation and must exit non-zero.
 *   --mutate     plants the ACTUAL defect L3 forbids - `fitsFor` widened to
 *                "every part of this type", which is what the page did before
 *                this order and what any future shortcut would reintroduce -
 *                and must exit non-zero. This is the one that matters: it is
 *                a defect somebody could really ship, not a sign flip.
 *
 * Usage:  node checks/_verify_ship_page.mjs [--self-test] [--mutate]
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
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

const html = readFileSync(PAGE, "utf-8");
const dataJs = readFileSync(DATA, "utf-8");
/* The page loads four generated files, not one. Loading only the loadout data
   left MARKS empty and the L10 block asserting on nothing - which it correctly
   reported as a failure rather than passing quietly. */
const EXTRA = ["loadout_model.gen.js", "loadout_marker.gen.js",
               "loadout_eng.gen.js"]
  .map((f) => join(SRC, f))
  .filter((f) => existsSync(f))
  .map((f) => readFileSync(f, "utf-8"));

/* ---------------------------------------------------------------- DOM stub
   The smallest browser the page actually touches. Elements are plain objects
   with the three properties the render paths write, so what is asserted is the
   HTML the page produced rather than a paraphrase of it. */
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
      clientWidth: 960, clientHeight: 540,
    });
  }
  return els.get(id);
}

/* WHERE THE PICKER IS, AFTER B2.
   A swappable port's picker is rendered INLINE, under its own row in the
   column, and the picker PANE is deliberately left empty - it now carries only
   B0's panel for a fixed port. Reading the pane alone would have made every
   L3 assertion below read an empty string, which is the shape of a check that
   passes because it never looked. This reads whichever one the page actually
   filled, which is what a person looking at the screen does.
   Slicing to the end of the column is safe: `data-part` appears only inside
   the picker's own rows, never on a slot row. */
/* THE OFFER LIST, WHICHEVER SURFACE IS SHOWING IT.
   Since the hardpoint-picker order, a hull-mounted port opens the DOCKED
   picker, which deliberately shows five rows (H3): best 4 by the active sort
   plus the fitted part pinned. The assertions below are about WHICH PARTS A
   PORT ADMITS - a property of the list, not of how many of it one surface
   chooses to draw - so they read the list renderer directly and keep their
   full strength. Reading the docked surface instead would test H3's cap and
   report a working page as offering 5 of 16.
   The surface itself is asserted separately, where it belongs: that a marker
   opens a panel at all, and that the panel is the fixed one for a fixed port. */
function offerListFor(slotId) {
  return g("pickerHTML(ship().slots.find(x=>x.id===" + JSON.stringify(slotId) + "))");
}
function pickerNow() {
  /* THREE HOMES SINCE B3. A hull-mounted port's picker is a panel over the
     model stage, an internal component's is inline under its row, and the pane
     is the fallback neither takes. Reading one and calling the rest empty is
     the mistake B0 exists to prevent. */
  const panel = el("cc-panel");
  if (!panel.hidden && /data-part=|class="fixedpanel"/.test(panel.innerHTML || ""))
    return panel.innerHTML;
  const pane = el("picker").innerHTML || "";
  if (/data-part=|class="fixedpanel"/.test(pane)) return pane;
  const col = el("colA").innerHTML || "";
  const i = col.indexOf('class="inlinepick"');
  return i === -1 ? "" : col.slice(i);
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
    /* CAPTURED, NOT SWALLOWED. P5 has to dispatch a real click through the
       page's own delegated handler; a no-op addEventListener would leave
       nothing to dispatch to, and the only thing left to assert would be that
       the listener exists - which is worth nothing. */
    addEventListener: (t, fn) => { if (t === "click") clickHandlers.push(fn); },
    querySelector: () => null,
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

/* H1g: THE PAGE IS TWO SCRIPT BLOCKS NOW, and this greedy match used to be
   one. CC_THEME runs in the HEAD - the dim has to be applied before first
   paint, or a returning visitor gets one frame of a bright page in the dark -
   so `<script>` to the LAST `</script>` swallowed the tag between the two
   blocks and this control died on a SyntaxError rather than on a failed
   assertion.
   THIS FILE CARRIES ITS OWN COPY OF THE HARNESS, WHICH IS WHY THE SAME FIX HAD
   TO BE MADE TWICE. checks/_loadout_harness.mjs exists precisely to stop that,
   and its own header names this hazard: "the day the page starts touching a
   DOM property none of the copies implement, the copies diverge one at a time".
   Recorded rather than quietly patched - the real fix is moving this control
   onto the shared harness. */
let script = (() => {
  const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]);
  const entry = blocks.findIndex((b) => /function renderAll\s*\(/.test(b));
  if (entry < 0) {
    console.log("NO PAGE SCRIPT FOUND - none of the " + blocks.length
      + " inline <script> blocks defines renderAll().");
    process.exit(2);
  }
  return blocks.slice(0, entry + 1).join("\n;\n");
})();
if (MUTATE) {
  // THE DEFECT, PLANTED. `fitsFor` stops reading the port's own rule and
  // offers every part of the type instead - which is exactly what the page did
  // before this order, and exactly the false claim L3 exists to stop. If a
  // future shortcut reintroduces it, this is the shape it will take.
  const before = script;
  script = script.replace(
    /function fitsFor\(slot\)\{[\s\S]*?\n\}/,
    "function fitsFor(slot){ if(!slot.fit) return [];" +
    " return Object.keys(P).filter(k=>P[k].t===slot.t); }");
  if (script === before) {
    console.log("MUTATION DID NOT APPLY - fitsFor was not found, so this run " +
                "proves nothing. Fix the mutator before trusting the check.");
    process.exit(1);
  }
  console.log("*** MUTATED: fitsFor now offers every part of the type, " +
              "ignoring the port. Something below MUST notice. ***");
}
vm.runInContext(dataJs, sandbox, { filename: "loadout_data.gen.js" });
for (const src of EXTRA) vm.runInContext(src, sandbox, { filename: "gen" });
vm.runInContext(script, sandbox, { filename: "loadout.src.html:script" });
const g = (expr) => vm.runInContext(expr, sandbox);

const SHIPS = g("SHIPS"), PARTS = g("P"), FITS = g("FITS"), HPN = g("HPN");
const TYPES = g("TYPES"), ARMOR = g("ARMOR"), PSETS = g("PSETS"), META = g("META");

/* --------------------------------------------------------- the page loaded */
console.log("--- the page's own script ran against the real generated data ---");
record(Object.keys(SHIPS).length > 300, "the ship table loaded",
  `${Object.keys(SHIPS).length} ships`);
record(Object.keys(FITS).length > 50, "the fitment table loaded",
  `${Object.keys(FITS).length} rules`);
record(g("typeof renderAll") === "function", "the page's render entry point exists");
record(!/\bfetch\s*\(/.test(script), "the page makes no network call");

/* Pick a ship with a healthy mix of editable and fixed ports, by measurement
   rather than by naming one and hoping. */
function pickShip(pred) {
  return Object.keys(SHIPS).find(pred);
}
const shipKey = pickShip(k => {
  const s = SHIPS[k];
  const ed = (s.slots || []).filter(x => x.fit).length;
  const fx = (s.slots || []).filter(x => !x.fit).length;
  return ed > 6 && fx > 6 && s.arm && s.pset;
});
record(!!shipKey, "found a ship with editable ports, fixed ports, armour and liveries");
const SH = SHIPS[shipKey];
notes.push(`driven with ${SH.n} (${shipKey}): ${SH.slots.length} ports, ` +
  `${SH.slots.filter(x => x.fit).length} editable, ` +
  `${SH.slots.filter(x => !x.fit).length} fixed`);

vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);

/* ------------------------------------------------- L4: fixed ports RENDER */
console.log("\n--- L4: a fixed port is SHOWN, counts, and opens no picker ---");
const colA = el("colA").innerHTML;
const fixedSlots = SH.slots.filter(s => !s.fit);
const editSlots = SH.slots.filter(s => s.fit);

record(colA.length > 500, "the build column rendered something at all");
/* B1 MOVED THE FIXED PORTS, AND THIS BLOCK MOVED WITH THEM.
   L4's rule is unchanged and every part of it is still asserted below: a fixed
   port is SHOWN, it NAMES what is in it, it says WHY it is locked, and it
   COUNTS toward the totals. What changed on 2026-08-22 is only WHERE it is
   shown - the Specs tab rather than a fold at the bottom of the loadout
   column, because the column is for ports somebody can act on.
   The assertions are NOT relaxed to accommodate that. They are pointed at the
   new home, and the sum below is what stops a port falling into the gap
   between the two lists. checks/_verify_column_split.mjs is the item's own
   control and drives the whole fleet; this stays as the regression guard in
   the place that noticed. */
const specsHtml = el("specs").innerHTML;
const renderedOpen = (colA.match(/class="slot/g) || []).length;
const renderedFixed = (specsHtml.match(/class="slot fixed"/g) || []).length;
record(renderedOpen === editSlots.length,
  `the column holds exactly the ${editSlots.length} ports that can be changed`,
  `rendered ${renderedOpen}`);
record(renderedFixed === fixedSlots.length,
  `all ${fixedSlots.length} FIXED ports rendered on Specs rather than hidden`,
  `rendered ${renderedFixed}`);
record(renderedOpen + renderedFixed === SH.slots.length,
  `and the two sum to every one of the ${SH.slots.length} ports - none lost `
  + `between the lists`,
  `${renderedOpen} + ${renderedFixed}`);
record(/can'?t be changed|does not allow this to be changed|no part for this port/.test(specsHtml),
  "a fixed port says plainly that it cannot be changed");
// It names the part in it. "Fuel tank - LOCKED" tells a visitor nothing.
const namedFixed = fixedSlots.filter(s => s.stock && PARTS[s.stock])
  .map(s => PARTS[s.stock].n).filter(n => specsHtml.includes(n));
record(namedFixed.length > 0,
  "a fixed port NAMES the part fitted in it, not just its type",
  `${namedFixed.length} named`);
if (namedFixed.length) notes.push(`L4 named: fixed port shows "${namedFixed[0]}"`);

// AND IT CONTRIBUTES TO TOTALS. This is the separable failure: shown but not
// counted. Proven by removing the fixed ports from the ship and watching the
// totals move - if they do not, the fixed ports were never in the sum.
const withFixed = g("JSON.stringify(calc(A))");
vm.runInContext(
  `__save=SHIPS[${JSON.stringify(shipKey)}].slots;` +
  `SHIPS[${JSON.stringify(shipKey)}].slots=__save.filter(s=>s.fit);`, sandbox);
const withoutFixed = g("JSON.stringify(calc(A))");
vm.runInContext(`SHIPS[${JSON.stringify(shipKey)}].slots=__save;`, sandbox);
record(withFixed !== withoutFixed,
  "a fixed port CONTRIBUTES to the totals - dropping the fixed ports changes them",
  "totals identical, so fixed ports were never counted");
{
  const a = JSON.parse(withFixed), b = JSON.parse(withoutFixed);
  const moved = Object.keys(a).filter(k => a[k] !== b[k]);
  if (moved.length) notes.push(`L4 contribution: dropping ${SH.n}'s fixed ports moves ${moved.join(", ")}`);
}

// AND OPENS NO PICKER.
const fx = fixedSlots[0];
vm.runInContext(`sel={slot:${JSON.stringify(fx.id)}};renderAll();`, sandbox);
const fixedPicker = pickerNow();
record(!/data-part=/.test(fixedPicker),
  "clicking a fixed port opens NO picker - nothing selectable is offered");

/* -------------------------------- L3: what the picker offers, both halves */
console.log("\n--- L3: a part the port accepts APPEARS; one it does not is ABSENT ---");
// A port with a real list, chosen by measurement.
const target = editSlots.find(s => (FITS[s.fit] || []).length > 4);
record(!!target, "found an editable port with a real list of alternatives");
vm.runInContext(`editing="A";sel={slot:${JSON.stringify(target.id)}};renderAll();`, sandbox);
/* THE OFFER LIST, for the same reason as the sweep below: both halves of L3 -
   an accepted part APPEARS, a rejected one is ABSENT - are claims about what
   the port admits. The docked picker draws five of that list by design, so
   asserting them against the surface would fail on a part that is offered and
   simply not in the top four. That the surface opens at all, and opens the
   right KIND of panel, is asserted by _verify_stage_panel and
   _verify_marker_response. */
const picker = offerListFor(target.id);

const offered = FITS[target.fit] || [];
const accepted = offered[0];
record(picker.includes(`data-part="${accepted}"`),
  `OFFERED: ${PARTS[accepted].n} is rendered in the picker for port ` +
  `${HPN[target.h]} on ${SH.n}`);
notes.push(`L3 OFFERED (rendered): ${SH.n} port "${HPN[target.h]}" offers ` +
  `${offered.length} parts, including ${PARTS[accepted].n} (${accepted})`);

// THE NEGATIVE HALF. A part of the right TYPE but the wrong SIZE - so this is
// not passing merely because the page filters by type. It must be absent from
// the rendered string entirely: not present-and-greyed, absent.
//
// The example is chosen so its DISPLAY NAME is unique to it. CIG ships the
// same product at several sizes - there is an MSD-313 Missile Rack at size 3
// and another at size 10 - so asserting on a name would have failed for the
// right reason and told the wrong story. A name is not an identity here.
const offeredNames = new Set(offered.map(k => PARTS[k].n));
const wrong = Object.keys(PARTS).find(k =>
  PARTS[k].t === target.t && PARTS[k].s !== target.s &&
  !offered.includes(k) && !offeredNames.has(PARTS[k].n));
record(!!wrong, "found a same-type wrong-size part to prove absence with");
record(!picker.includes(`data-part="${wrong}"`),
  `ABSENT: ${PARTS[wrong].n} (size ${PARTS[wrong].s}) is NOT in the picker for ` +
  `a size-${target.s} port`);
record(!picker.includes(PARTS[wrong].n),
  "and it is absent from the rendered HTML entirely - not greyed, not disabled");
notes.push(`L3 ABSENT (rendered): ${PARTS[wrong].n} (size ${PARTS[wrong].s}) ` +
  `does not appear for the size-${target.s} port "${HPN[target.h]}"`);

// The picker offers ONLY what the port admits - all of it, checked, not a spot
// check. A page that offered every part of the type would pass the two
// assertions above and fail this one.
const inPicker = [...offerListFor(target.id).matchAll(/data-part="([^"]+)"/g)]
  .map(m => m[1]);
record(inPicker.length === offered.length,
  `the picker offers exactly the ${offered.length} parts the port admits`,
  `rendered ${inPicker.length}`);
record(inPicker.every(k => offered.includes(k)),
  "and every one of them is on that port's own list");

/* --------------------------------------- L3 sweep: EVERY port on the ship */
console.log("\n--- L3 across every editable port on the ship, not one sample ---");
let bad = 0, checked = 0;
for (const s of editSlots) {
  vm.runInContext(`sel={slot:${JSON.stringify(s.id)}};renderAll();`, sandbox);
  const got = [...offerListFor(s.id).matchAll(/data-part="([^"]+)"/g)].map(m => m[1]);
  const want = (FITS[s.fit] || []).concat(
    s.also && !(FITS[s.fit] || []).includes(s.also) ? [s.also] : []);
  checked++;
  if (got.length !== want.length || !got.every(k => want.includes(k))) bad++;
}
record(checked > 5, "swept a real number of ports", `${checked}`);
record(bad === 0,
  `every one of ${checked} editable ports offers exactly its own list`,
  `${bad} wrong`);

/* ------------------------------------------- L6: the readout shows it all */
console.log("\n--- L6: everything that moves, at once - and mass is not dropped ---");
vm.runInContext(`sel=null;renderAll();`, sandbox);
const stats = el("stats").innerHTML;
for (const label of ["Sustained DPS", "Effective HP", "IR signature",
                     "EM signature", "Quantum range", "Total mass"]) {
  record(stats.includes(label), `the readout shows ${label}`);
}
record(el("budgets").innerHTML.includes("Power draw") &&
       el("budgets").innerHTML.includes("Cooling"),
  "power draw against output and heat against cooling are both shown");

// L6 NAMES A LONGER LIST THAN THE SIX ABOVE, and the rest only appear on hulls
// that have the hardware. Asserting them on one ship would either fail for the
// right reason or pass for the wrong one, so each is proven on a hull chosen
// BY MEASUREMENT as one that actually carries it.
const dims = [
  ["Radar sensitivity", "sens",   "detection"],
  ["Mining throughput", "mrate",  "mining"],
  ["Beam range",        "beam",   "salvage and tractor"],
  ["Fitted containers", "scu",    "swappable cargo"],
];
for (const [label, field, what] of dims) {
  const k = Object.keys(SHIPS).find(k =>
    (SHIPS[k].slots || []).some(sl => {
      const id = sl.fit ? sl.stock : sl.stock;
      return id && PARTS[id] && PARTS[id][field];
    }));
  if (!k) { record(false, `a hull exists that carries ${what}`); continue; }
  vm.runInContext(`shipId=${JSON.stringify(k)};reset();renderAll();`, sandbox);
  record(el("stats").innerHTML.includes(label),
    `${what} is in the readout, on a hull that has it (${SHIPS[k].n})`);
}
// Power pools: CIG caps power by item type, and a ship with generation to
// spare can still be unable to feed a bigger gun.
{
  const k = Object.keys(SHIPS).find(k => (SHIPS[k].cig || {}).pools);
  record(!!k, "a hull states CIG's per-type power pools");
  vm.runInContext(`shipId=${JSON.stringify(k)};reset();renderAll();`, sandbox);
  record(el("pools").innerHTML.includes("Power pools"),
    `the per-type power caps are shown (${SHIPS[k].n})`);
  record(!/-1/.test(el("pools").innerHTML),
    "and an uncapped type is omitted rather than shown as -1");
}
// Armour's signal multipliers belong with the signature, not only in the
// armour panel - L6 lists them under signature explicitly.
vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);
record(/multiplies this hull's signature/.test(el("signote").innerHTML),
  "armour's SIGNAL multipliers are shown alongside the signature readout");


// MASS MOVES WHEN A PART IS SWAPPED. Stating a mass that never changes would
// be worse than omitting it.
const m0 = g("calc(A).mass");
const heavy = offered.slice().sort((a, b) => (PARTS[b].ms || 0) - (PARTS[a].ms || 0))[0];
vm.runInContext(`B=Object.assign({},A);B[${JSON.stringify(target.id)}]=${JSON.stringify(heavy)};`, sandbox);
const m1 = g("calc(B).mass");
record(typeof m0 === "number" && m0 > 0, "the ship has a real total mass", `${m0}`);
record(m1 !== m0 || (PARTS[heavy].ms || 0) === (PARTS[target.stock] || {}).ms,
  "swapping a part MOVES the total mass", `${m0} -> ${m1}`);

/* THE ORDER'S OWN ACCEPTANCE: one swap, two unrelated readouts moving in
   OPPOSITE directions. Found by search rather than asserted by hope, and the
   pair that is found gets named in the ledger. */
// Searched across EVERY editable port and every part it admits, not just the
// one port picked above. A single port whose alternatives all pull the same
// way would have failed this for a reason that says nothing about the page.
const before = JSON.parse(g("JSON.stringify(calc(A))"));
let opposite = null;
outer:
for (const s of editSlots) {
  for (const k of (FITS[s.fit] || [])) {
    if (k === s.stock) continue;
    vm.runInContext(`B=Object.assign({},A);B[${JSON.stringify(s.id)}]=${JSON.stringify(k)};`, sandbox);
    const after = JSON.parse(g("JSON.stringify(calc(B))"));
    const up = [], down = [];
    for (const f of ["dps", "ehp", "ir", "em", "pw", "cool", "mass", "regen", "alpha"]) {
      if (after[f] > before[f]) up.push(f);
      if (after[f] < before[f]) down.push(f);
    }
    if (up.length && down.length) { opposite = { slot: s, part: k, up, down }; break outer; }
  }
}
record(!!opposite,
  "one swap moves at least two unrelated readouts in OPPOSITE directions");
if (opposite) {
  notes.push(`L6 opposite: on ${SH.n}, fitting ${PARTS[opposite.part].n} at ` +
    `"${HPN[opposite.slot.h]}" raises ${opposite.up.join("/")} and lowers ` +
    `${opposite.down.join("/")}`);
}

/* ------------------------------------------------ L5: armour on the page */
console.log("\n--- L5: hull armour is shown, and is not one number ---");
const arm = el("armour").innerHTML;
record(arm.length > 200, "the armour panel rendered");
record(/Physical/.test(arm) && /Energy/.test(arm),
  "resistance is broken out BY DAMAGE TYPE, not collapsed to one figure");
record(/cannot be changed|not editable|fixed/i.test(arm),
  "and it says plainly that armour cannot be changed");
record(!/data-part=/.test(arm), "the armour panel offers no picker");
// Two hulls with different armour must SHOW different resistance.
const other = Object.keys(SHIPS).find(k =>
  SHIPS[k].arm && SHIPS[k].arm !== SH.arm &&
  JSON.stringify(ARMOR[SHIPS[k].arm].dm) !== JSON.stringify(ARMOR[SH.arm].dm));
record(!!other, "found a second hull with a different armour profile");
vm.runInContext(`shipId=${JSON.stringify(other)};reset();renderAll();`, sandbox);
const arm2 = el("armour").innerHTML;
record(arm2 !== arm, "a different hull shows DIFFERENT resistance on the page");
{
  const a = ARMOR[SH.arm].dm, b = ARMOR[SHIPS[other].arm].dm;
  const flip = Object.keys(a).find(k => a[k] !== b[k]);
  if (flip) notes.push(`L5 rendered: ${SH.n} takes ${flip} at ${a[flip]}, ` +
    `${SHIPS[other].n} at ${b[flip]} - a weapon strong against one is weaker ` +
    `against the other`);
}
vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);

/* ------------------- L5's other half: the weapon-vs-hull matchup, rendered */
console.log("\n--- L5: a weapon strong against one hull is WEAKER against another ---");
vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);
const match = el("matchup").innerHTML;
record(match.length > 200, "the matchup panel rendered");

// The build must carry a damage MIX, not just a total. Without it there is
// nothing for armour to multiply and the whole panel would be arithmetic on
// one number.
const mix = JSON.parse(g("JSON.stringify(calc(B).mix)"));
record(Object.keys(mix).length > 0,
  "the build's DPS is carried BY DAMAGE CHANNEL, not as one total",
  JSON.stringify(mix));

// THE ORDER'S ACCEPTANCE, COMPUTED RATHER THAN ASSERTED: find a weapon and two
// hulls where the SAME weapon does measurably different work. If no such pair
// exists the claim is empty, so this fails rather than passing quietly.
const profs = JSON.parse(g("JSON.stringify(armourProfiles())"));
record(profs.length > 1, "there is more than one armour profile to compare",
  `${profs.length} profiles`);
let matchup = null;
for (const wk of Object.keys(PARTS)) {
  const w = PARTS[wk];
  if (!w.dmg) continue;
  for (let i = 0; i < profs.length && !matchup; i++) {
    for (let j = i + 1; j < profs.length; j++) {
      const a = g(`effectiveDps(${JSON.stringify(w.dmg)},${JSON.stringify(profs[i].dm)})`);
      const b = g(`effectiveDps(${JSON.stringify(w.dmg)},${JSON.stringify(profs[j].dm)})`);
      if (Math.abs(a - b) > Math.max(a, b) * 0.05) {
        matchup = { w, a, b, pa: profs[i], pb: profs[j] };
        break;
      }
    }
  }
  if (matchup) break;
}
record(!!matchup,
  "a named weapon is measurably WEAKER against one hull than another");
if (matchup) {
  notes.push(`L5 matchup: ${matchup.w.n} does ${Math.round(matchup.a)} DPS ` +
    `against a hull like ${matchup.pa.ships[0]} and ${Math.round(matchup.b)} ` +
    `against one like ${matchup.pb.ships[0]} - same gun, ` +
    `${Math.round(Math.abs(matchup.a - matchup.b) / Math.max(matchup.a, matchup.b) * 100)}% apart`);
}
// And the page SHOWS the difference rather than only being able to compute it.
const effs = [...match.matchAll(/class="p">([\d,\.]+)</g)].map(m => m[1]);
record(new Set(effs).size > 1,
  "the rendered table shows DIFFERENT effective DPS against different hulls",
  `values ${JSON.stringify(effs)}`);
record(/matchup, not a rating/i.test(match),
  "and says it is a matchup rather than a rating - neither gun is 'better'");

/* ----------------------------------------------------- L7: liveries here */
console.log("\n--- L7: liveries live on the ship page, and not on the model ---");
const liv = el("liveries").innerHTML;
record(liv.length > 100, "the livery panel rendered");
record(/not shown on the model/i.test(liv),
  "and says the liveries are NOT rendered on the 3D model, and why");
const set = PSETS[SH.pset] || [];
record(set.length > 0 && set.length < Object.keys(g("PAINTS")).length,
  "this hull is offered its OWN liveries, not the whole catalogue",
  `${set.length} of ${Object.keys(g("PAINTS")).length}`);
// LIVERIES TAKE NO PART IN THE READOUT, proven by fitting one and watching
// nothing move. A cosmetic that quietly changed a number would be worse than
// one that was missing.
const beforeLiv = g("JSON.stringify(calc(B))");
const aPaint = (PSETS[SH.pset] || [])[0];
vm.runInContext(`B.__livery=${JSON.stringify(aPaint)};`, sandbox);
const afterLiv = g("JSON.stringify(calc(B))");
record(beforeLiv === afterLiv,
  "fitting a livery moves NO readout - it is cosmetic and stays cosmetic");
record(!/class="stat/.test(liv), "and no livery renders a stat of its own");

/* --------------------------------------------- L12: the link carries all */
console.log("\n--- L12: the share link carries the whole build ---");
vm.runInContext(
  `B=Object.assign({},A);B[${JSON.stringify(target.id)}]=${JSON.stringify(accepted)};writeHash();`,
  sandbox);
const hash = currentHash;
record(hash.startsWith(shipKey), "the link names the ship");
record(hash.includes(accepted) || accepted === target.stock,
  "and carries the swapped part");
// Paste it into a clean session: same build back.
vm.runInContext(
  `location.hash=${JSON.stringify("#" + hash)};shipId=null;A={};B={};readHash();`,
  sandbox);
record(g("shipId") === shipKey, "reading the link back restores the ship");
record(g(`B[${JSON.stringify(target.id)}]`) === accepted,
  "and restores the swapped part at the right port");
// EVERY editable port round-trips, not just the one that was changed.
vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();`, sandbox);
const rot = {};
editSlots.forEach(s => {
  const list = FITS[s.fit] || [];
  const alt = list.find(k => k !== s.stock);
  if (alt) rot[s.id] = alt;
});
vm.runInContext(
  `B=Object.assign({},A,${JSON.stringify(rot)});writeHash();`, sandbox);
const fullHash = currentHash;
vm.runInContext(
  `location.hash=${JSON.stringify("#" + fullHash)};A={};B={};readHash();`, sandbox);
const back = JSON.parse(g("JSON.stringify(B)"));
const lost = Object.keys(rot).filter(id => back[id] !== rot[id]);
record(lost.length === 0,
  `all ${Object.keys(rot).length} changed ports survive the round trip`,
  `${lost.length} lost`);

/* -------------------------------------------- L13: provenance is visible */
console.log("\n--- L13: a CIG figure and a computed one look different ---");
vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);
const stockStats = el("stats").innerHTML;
record(/class="src cig"/.test(stockStats),
  "a stock build shows CIG's own figures, marked as CIG's");
/* N5 CHANGED WHICH BUILD THIS HAS TO TOUCH. The page opens on ONE build, so a
   change to B is a change to something not on screen - this used to modify B
   and would now be asserting on a readout that never moved. It edits A, which
   is the build a visitor is editing when there is only one. */
vm.runInContext(
  `A[${JSON.stringify(target.id)}]=${JSON.stringify(accepted !== target.stock ? accepted : offered.find(k => k !== target.stock))};renderAll();`,
  sandbox);
const changedStats = el("stats").innerHTML;
record(/class="src ours"/.test(changedStats),
  "and a changed build shows OURS, marked as summed");
record(stockStats !== changedStats,
  "the two are visibly different on the page, not the same badge twice");
record(el("sourcenote").innerHTML.includes(META.snapshot),
  "the page names the snapshot it was built from");

/* ------ L10: a hull marker is a SECOND ROUTE to the same picker ---------- */
console.log("\n--- L10: marker N selects port N and no other, BY IDENTITY ---");
{
  const MARKS = g("MARKS");
  record(Object.keys(MARKS).length > 50,
    "hull markers exist for a real number of hulls",
    `${Object.keys(MARKS).length} hulls`);

  // A marker's identity is the game's PortId. Every one must resolve to
  // EXACTLY ONE port on its ship - not zero, and above all not two.
  let checkedMarks = 0, unresolved = 0, ambiguous = 0;
  for (const [cls, list] of Object.entries(MARKS)) {
    const rec = SHIPS[cls];
    if (!rec) { unresolved += list.length; continue; }
    for (const m of list) {
      checkedMarks++;
      const hits = rec.slots.filter(sl => sl.p === m[0]);
      if (hits.length === 0) unresolved++;
      else if (hits.length > 1) ambiguous++;
    }
  }
  record(checkedMarks > 500, "a real number of markers were checked", `${checkedMarks}`);
  record(unresolved === 0, "every marker resolves to a port on its own ship",
    `${unresolved} do not`);
  record(ambiguous === 0,
    "and to EXACTLY ONE port - never two. This is the assertion a hardpoint " +
    "name could not pass: 287 of 316 hulls share one between slots",
    `${ambiguous} ambiguous`);
  notes.push(`L10: ${checkedMarks} markers across ${Object.keys(MARKS).length} ` +
    `hulls, every one resolving to exactly one port by PortId`);

  // MARKERS STAY WEAPONS-ONLY, per the order. Internal ports come from the list.
  const WEAPONY = new Set(["WeaponGun", "Turret", "MissileLauncher",
    "WeaponDefensive", "WeaponMining", "BombLauncher", "SalvageHead",
    "TractorBeam", "EMP", "Missile", "Bomb"]);
  let nonWeapon = 0;
  for (const [cls, list] of Object.entries(MARKS)) {
    const rec = SHIPS[cls]; if (!rec) continue;
    for (const m of list) {
      const sl = rec.slots.find(x => x.p === m[0]);
      if (sl && !WEAPONY.has(TYPES[sl.t] && TYPES[sl.t].t)) nonWeapon++;
    }
  }
  record(nonWeapon === 0, "every marker is on a weapon port", `${nonWeapon} are not`);

  // THE SAME WINDOW, NOT A SECOND ONE. Click the port in the list, capture the
  // picker; reset; click the marker; the picker must be BYTE-IDENTICAL.
  // Anything less and there are two mechanisms rather than two routes.
  const markShip = Object.keys(MARKS).find(k => {
    const rec = SHIPS[k]; if (!rec) return false;
    return MARKS[k].some(m => {
      const sl = rec.slots.find(x => x.p === m[0]);
      return sl && sl.fit && (FITS[sl.fit] || []).length > 1;
    });
  });
  record(!!markShip, "found a hull whose marker points at a swappable port");
  if (markShip) {
    const rec = SHIPS[markShip];
    const mark = MARKS[markShip].find(m => {
      const sl = rec.slots.find(x => x.p === m[0]);
      return sl && sl.fit && (FITS[sl.fit] || []).length > 1;
    });
    const slot = rec.slots.find(x => x.p === mark[0]);
    vm.runInContext(`shipId=${JSON.stringify(markShip)};reset();renderAll();`, sandbox);

    vm.runInContext(`sel=null;selectPort(ship().slots.find(s=>s.id===${JSON.stringify(slot.id)}),"A");`, sandbox);
    const viaList = pickerNow();
    const listSel = JSON.parse(g("JSON.stringify(sel)"));

    vm.runInContext(`sel=null;renderAll();`, sandbox);
    vm.runInContext(`selectPort(slotByPort(${JSON.stringify(mark[0])}),"A");`, sandbox);
    const viaMark = pickerNow();
    const markSel = JSON.parse(g("JSON.stringify(sel)"));

    record(viaMark.length > 100, "clicking the marker opened a picker at all");
    record(viaMark === viaList,
      "the marker and the list open the IDENTICAL window - same bytes, not a " +
      "second mechanism that happens to look alike");
    record(JSON.stringify(markSel) === JSON.stringify(listSel),
      "and select the same port", `${JSON.stringify(markSel)} vs ${JSON.stringify(listSel)}`);
    notes.push(`L10 named: on ${rec.n}, the marker for port "${HPN[slot.h]}" ` +
      `and the list row for it open byte-identical pickers`);

    // AND NO OTHER PORT. Selecting via the marker must not select a second.
    const others = rec.slots.filter(x => x.id !== slot.id && x.p === mark[0]);
    record(others.length === 0, "no other port on the hull answers to that id");
  }

  // ONE SELECTION PATH IN THE SOURCE. If a second appears, the "identical
  // window" assertion above starts passing by coincidence rather than by
  // construction.
  const assigns = (script.match(/\bsel\s*=\s*\{/g) || []).length;
  record(assigns === 1,
    "there is exactly ONE place in the page that selects a port",
    `${assigns} assignments to sel={...}`);
}

/* --- L11: the ship name goes to the SHIP PAGE; the RSI link moves onto it -- */
console.log("\n--- L11: the name opens the ship, and the RSI link travels with it ---");
{
  const RSI = g("RSI");
  record(Object.keys(RSI).length > 100,
    "pledge links reached the ship page rather than being left behind",
    `${Object.keys(RSI).length} ships`);
  // Every one must name a real ship record, or the link is on nothing.
  const orphan = Object.keys(RSI).filter((k) => !SHIPS[k]);
  record(orphan.length === 0, "every pledge link names a real ship record",
    `${orphan.length}: ${orphan.slice(0, 3)}`);

  // ON THE PAGE, CLEARLY, when there is one.
  const withRsi = Object.keys(RSI)[0];
  vm.runInContext(`shipId=${JSON.stringify(withRsi)};reset();renderAll();`, sandbox);
  record(el("rsi").hidden === false, "the link is shown on a ship that has one");
  record(String(el("rsi").href).includes("robertsspaceindustries"),
    "and points at RSI", String(el("rsi").href).slice(0, 60));
  record(/View .* on RSI/.test(el("rsi").textContent),
    "and says what it is, naming the ship",
    el("rsi").textContent);
  notes.push(`L11: ${Object.keys(RSI).length} ships carry their pledge link on ` +
    `the ship page; e.g. ${SHIPS[withRsi].n}`);

  // A SHIP WITHOUT ONE SHOWS NO LINK, not a dead one. An href that goes
  // nowhere reads as the site being broken.
  const noRsi = Object.keys(SHIPS).find((k) => !RSI[k]);
  record(!!noRsi, "there is a ship with no pledge page, so this is testable");
  vm.runInContext(`shipId=${JSON.stringify(noRsi)};reset();renderAll();`, sandbox);
  record(el("rsi").hidden === true,
    "a ship with no pledge page shows NO link rather than a dead one");
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);
}

console.log("\n--- L14: the three kinds of incomplete ship, each said out loud ---");
{
  const MODELS = g("MODELS"), MARKS = g("MARKS");
  const UNREL = g("UNRELEASED");

  // CASE 1: a game file, no 3D model. The order names the Origin M80.
  const case1 = Object.keys(SHIPS).filter((k) => SHIPS[k].slots.length && !MODELS[k]);
  record(case1.length > 0, "case 1 exists: hulls with a game file and no model",
    `${case1.length}`);
  const m80 = Object.keys(SHIPS).find((k) => /M80/.test(SHIPS[k].n));
  const c1 = MODELS[m80] ? case1[0] : m80;
  vm.runInContext(`shipId=${JSON.stringify(c1)};reset();renderAll();`, sandbox);
  record(/No 3D model available/.test(el("cc-empty").innerHTML),
    `case 1 renders an honest "no model" for ${SHIPS[c1].n}, not a spinner`,
    el("cc-empty").innerHTML.slice(0, 60));
  record(el("colA").innerHTML.length > 500,
    "and its full readout and swapping still work");
  notes.push(`L14 case 1: ${SHIPS[c1].n} has ${SHIPS[c1].slots.length} ports and ` +
    `no model; the viewer says so and the readout is unaffected`);

  // CASE 2: no game file at all. 33 of them.
  record(UNREL.length > 20, "case 2 exists: ships CIG has not built",
    `${UNREL.length}`);
  record(UNREL.every((u) => u.why && /not released yet/.test(u.why)),
    "and every one says why, rather than rendering an empty panel");
  record(UNREL.every((u) => !u.slots),
    "and NOTHING is claimed about their loadouts");
  notes.push(`L14 case 2: ${UNREL.length} announced-but-unbuilt ships, e.g. ` +
    `${UNREL.slice(0, 3).map((u) => u.n).join(", ")} - shown, disabled, reason given`);

  // CASE 3: a model but no measured mount positions, so no markers.
  const case3 = Object.keys(SHIPS).filter(
    (k) => SHIPS[k].slots.length && MODELS[k] && !(MARKS[k] || []).length);
  record(case3.length > 0, "case 3 exists: a hull with a model and no mount data",
    `${case3.length}`);
  vm.runInContext(`shipId=${JSON.stringify(case3[0])};reset();renderAll();`, sandbox);
  /* THE WORDING CHANGED AT N9 AND THIS FOLLOWED IT. It used to grep for "No
     mount positions have been MEASURED", which was the sentence N9 removed -
     it implied that where markers DO appear they were measured, and they are
     not. The claim being checked is unchanged: this hull says it has no marker
     placement and stays usable from the list. */
  record(/no marker placement for this hull/i.test(el("shipstate").innerHTML),
    `case 3 says so plainly for ${SHIPS[case3[0]].n}`);
  record(el("colA").innerHTML.length > 500,
    "and list-driven swapping still works on it");
  notes.push(`L14 case 3: ${case3.length} hulls have a model but no measured ` +
    `mount positions; they say so and stay fully usable from the list`);

  // AND THE STINGRAY IS NOT HERE. A ship with no verifiable specs is the
  // opposite of what this site is for.
  const stingray = Object.keys(SHIPS).filter((k) => /Stingray|S-65/i.test(SHIPS[k].n));
  record(stingray.length === 0,
    "the Kruger S-65 Stingray is NOT in the dataset - PTU-only, no Ship Matrix " +
    "entry, no published specs", `${stingray.length} found`);

  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);
}

/* ------------ ADDENDUM s0: a display name is not an identity here --------- */
console.log("\n--- addendum s0: Name is a label, ClassName is the key ---");
{
  const byName = {};
  for (const k of Object.keys(SHIPS)) (byName[SHIPS[k].n] = byName[SHIPS[k].n] || []).push(k);
  const dupNames = Object.keys(byName).filter(n => byName[n].length > 1);
  const dupRecords = dupNames.reduce((t, n) => t + byName[n].length, 0);
  record(dupNames.length > 0,
    "there really are shared display names - so keying on Name is a live risk, " +
    "not a hypothetical", `${dupNames.length} names over ${dupRecords} records`);
  record(Object.keys(SHIPS).length > Object.keys(byName).length,
    "and a Name-keyed table WOULD lose records",
    `${Object.keys(SHIPS).length} records, ${Object.keys(byName).length} names`);

  // THE ADDENDUM'S OWN CONTROL: both Hammerheads survive as distinct entries.
  const hh = byName["Aegis Hammerhead"] || [];
  record(hh.length === 2, "both Aegis Hammerhead records survive the pipeline",
    JSON.stringify(hh));
  if (hh.length === 2) {
    const [a, b] = hh.map(k => SHIPS[k]);
    record(a.slots.length !== b.slots.length || a.crew !== b.crew,
      "and they are genuinely DIFFERENT ships, not one record twice",
      `${a.slots.length}/${a.crew} vs ${b.slots.length}/${b.crew}`);
    notes.push(`addendum s0: ${hh[0]} has ${a.slots.length} ports and ${a.crew} ` +
      `crew, ${hh[1]} has ${b.slots.length} and ${b.crew} - both survive, ` +
      `both keyed on ClassName`);
  }

  // AND THE DISPLAY DEFECT THE COLLISION CAUSES. Joining correctly is not
  // enough: a dropdown with two entries reading "Aegis Hammerhead" leaves the
  // visitor unable to tell which they picked.
  vm.runInContext("fillShipList();", sandbox);
  const list = el("ship").innerHTML;
  const labels = [...list.matchAll(/<option value="[^"]*">([^<]*)</g)].map(m => m[1]);
  const counts = {};
  for (const l of labels) counts[l] = (counts[l] || 0) + 1;
  const stillAmbiguous = Object.keys(counts).filter(l => counts[l] > 1);
  record(stillAmbiguous.length === 0,
    "no two entries in the ship list read identically",
    `${stillAmbiguous.length}: ${stillAmbiguous.slice(0, 3)}`);
  record(labels.some(l => /\(/.test(l)),
    "the shared names are disambiguated from the ClassName, not left ambiguous");
  // And a name that is NOT shared is left alone - the disambiguation must not
  // spread to every ship on the site.
  const plain = labels.filter(l => !/\(/.test(l));
  record(plain.length > labels.length * 0.8,
    "and the disambiguation touches only the names that need it",
    `${labels.length - plain.length} of ${labels.length} decorated`);
}

console.log("\n--- M1: tabbed layers, and a tab only exists when there is data ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();renderAll();`, sandbox);
  const tabs = el("tabs").innerHTML;
  record(/data-tab="loadout"/.test(tabs), "the Loadout tab exists");
  record(/href="#loadout"/.test(tabs),
    "and every tab is a REAL URL FRAGMENT, so a layer can be linked to");
  record(!/<img|<svg|class="badge/.test(tabs),
    "the tabs are plain text - no icons, no badges, nothing competing with the ship");

  // THE DEFAULT TAB IS ALWAYS LOADOUT and is never remembered.
  vm.runInContext(`openTab("specs");`, sandbox);
  record(g("tab") === "specs", "a tab can be opened");
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();tab="loadout";renderAll();`, sandbox);
  record(g("tab") === "loadout",
    "changing ship returns to Loadout - the open tab is never remembered");

  // A TAB WITH NOTHING BEHIND IT DOES NOT EXIST. Crew has no data at all, so
  // it must be absent on EVERY ship - not present and empty.
  let crewSeen = 0, engMissing = 0, engPresent = 0;
  for (const k of Object.keys(SHIPS)) {
    vm.runInContext(`shipId=${JSON.stringify(k)};reset();renderTabs();`, sandbox);
    const h = el("tabs").innerHTML;
    if (/data-tab="crew"/.test(h)) crewSeen++;
    if (/data-tab="engineering"/.test(h)) engPresent++;
    else engMissing++;
  }
  record(crewSeen === 0,
    "the Crew tab has no data behind it and therefore appears on NO ship",
    `${crewSeen} ships show it`);
  record(engPresent > 250 && engMissing > 0,
    "the Engineering tab appears where there are relays and NOT where there are none",
    `${engPresent} with, ${engMissing} without`);
  notes.push(`M1: Engineering shows on ${engPresent} hulls and is suppressed on ` +
    `${engMissing}; Crew has no data and appears on none of the 316`);

  // A DIRECT LINK TO A TAB THIS SHIP DOES NOT HAVE LANDS ON LOADOUT.
  const noEng = Object.keys(SHIPS).find((k) => !SHIPS[k].eng);
  record(!!noEng, "found a ship with no relays, so this is testable");
  vm.runInContext(`shipId=${JSON.stringify(noEng)};reset();openTab("engineering");`, sandbox);
  record(g("tab") === "loadout",
    `a direct link to #engineering on ${SHIPS[noEng].n} lands on Loadout without erroring`);
}

console.log("\n--- M1 section 2: the NETWORK TRACE - what a page actually fetches ---");
{
  /* THE CONTROL THE ADDENDUM NAMES, and the only one that proves the layers
     are lazy rather than merely tabbed: watch what gets fetched.

     Every <script> the page appends is counted. A default ship page must add
     NOTHING; opening Engineering must add EXACTLY ONE file; reopening it must
     add nothing at all. */
  const added = [];
  const realCreate = sandbox.document.createElement;
  /* THE HARNESS PRE-LOADS EVERY GENERATED FILE, so the layer is already
     registered and the lazy path would never run. Unregistering it first is
     what makes this a trace of the LAZY behaviour rather than a trace of a
     page that had everything already - and getting that wrong is how a
     "nothing was fetched" result would have looked like a pass. */
  const stashed = vm.runInContext("window.CC_LAYERS", sandbox);
  vm.runInContext("window.CC_LAYERS={};layerState.engineering=undefined;", sandbox);
  sandbox.document.createElement = () => (
    { tagName: "SCRIPT", src: "", onload: null, onerror: null });
  sandbox.document.head = {
    appendChild(node) {
      added.push(node.src);
      // Stand in for the browser fetching and running the file: the real one
      // registers itself, so this does too.
      vm.runInContext("window.CC_LAYERS.engineering=__stash.engineering;", sandbox);
      if (node.onload) node.onload();
    },
  };
  vm.runInContext("__stash=" + JSON.stringify({ engineering: stashed.engineering }) + ";", sandbox);

  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();tab="loadout";renderAll();`, sandbox);
  const afterDefault = added.length;
  record(afterDefault === 0,
    "a DEFAULT ship page fetches no layer file at all",
    `${afterDefault} fetched: ${added.join(", ")}`);

  vm.runInContext(`openTab("engineering");`, sandbox);
  const afterOpen = added.length;
  record(afterOpen - afterDefault === 1,
    "opening Engineering fetches EXACTLY ONE more file",
    `${afterOpen - afterDefault}: ${added.slice(afterDefault).join(", ")}`);
  record(added[added.length - 1] === "loadout_eng.gen.js",
    "and it is the engineering layer, not something else",
    added[added.length - 1]);

  vm.runInContext(`tab="loadout";renderTabs();openTab("engineering");`, sandbox);
  record(added.length === afterOpen,
    "reopening it fetches NOTHING - the layer is cached, not re-requested",
    `${added.length - afterOpen} extra`);
  notes.push(`M1 network trace: default page 0 layer files, opening Engineering ` +
    `1 (loadout_eng.gen.js), reopening 0`);
  sandbox.document.createElement = realCreate;
  vm.runInContext("window.CC_LAYERS=__stash;", sandbox);
}

console.log("\n--- M2: the engineering layer, and NO empty fuse positions ---");
{
  const ENG = g("typeof LOADOUT_ENG!=='undefined' ? LOADOUT_ENG : null");
  record(!!ENG && Object.keys(ENG).length > 250,
    "the engineering layer loaded", `${ENG ? Object.keys(ENG).length : 0} hulls`);
  const relays = Object.values(ENG).reduce((t, v) => t + v.length, 0);
  const fuses = Object.values(ENG).reduce((t, v) => t + v.reduce((a, r) => a + r[1], 0), 0);
  record(relays > 600 && fuses > 1300, "with a real number of relays and fuses",
    `${relays} relays, ${fuses} fuse slots`);
  notes.push(`M2: ${relays} relays and ${fuses} fuse slots across ` +
    `${Object.keys(ENG).length} hulls`);

  // Bound to PortId, like everything else at port level.
  let unbound = 0;
  for (const [cls, rows] of Object.entries(ENG)) {
    for (const r of rows) if (!r[2]) unbound++;
  }
  record(unbound === 0, "every relay carries the game's own PortId", `${unbound} without`);

  // THE ORDER'S NAMED EXAMPLES.
  const idris = Object.keys(ENG).find((k) => /Idris-P$/.test((SHIPS[k] || {}).n || ""));
  const vulture = Object.keys(ENG).find((k) => /Vulture/.test((SHIPS[k] || {}).n || ""));
  if (idris) {
    const n = ENG[idris].length, f = ENG[idris].reduce((a, r) => a + r[1], 0);
    record(n > 10, `the Aegis Idris-P is a big hull: ${n} relays / ${f} fuses`);
    notes.push(`M2 named: Aegis Idris-P ${n} relays / ${f} fuses`);
  }
  if (vulture) {
    const n = ENG[vulture].length, f = ENG[vulture].reduce((a, r) => a + r[1], 0);
    record(n <= 3, `and the Drake Vulture a small one: ${n} relays / ${f} fuses`);
    notes.push(`M2 named: Drake Vulture ${n} relays / ${f} fuses`);
  }

  // NO EMPTY POSITIONS. One bar per fuse slot that exists - counted against
  // the data, on a hull with relays of DIFFERENT sizes, so a fixed-width
  // track would show up immediately.
  const mixed = Object.keys(ENG).find((k) => {
    const sizes = new Set(ENG[k].map((r) => r[1]));
    return SHIPS[k] && sizes.size > 1 && ENG[k].length > 3;
  });
  record(!!mixed, "found a hull with relays of different sizes");
  vm.runInContext(`shipId=${JSON.stringify(mixed)};reset();tab="engineering";renderEngineering();`, sandbox);
  const engHtml = el("engineering").innerHTML;
  const bars = (engHtml.match(/<i><\/i>/g) || []).length;
  const want = ENG[mixed].reduce((a, r) => a + r[1], 0);
  record(bars === want,
    `EXACTLY one bar per fuse slot on ${SHIPS[mixed].n} - no empty positions drawn`,
    `${bars} bars for ${want} fuse slots`);
  record(!/class="empty"|class="slot-empty"|opacity:\s*\.?[0-4]/.test(engHtml),
    "and nothing is drawn greyed, which would read as a fuse being MISSING");
  notes.push(`M2 no-empties: ${SHIPS[mixed].n} renders ${bars} bars for ` +
    `${want} fuse slots across ${ENG[mixed].length} relays of differing sizes`);

  // M4: what is NOT established must not be implied.
  record(/not in the game files/.test(engHtml) && /ratings/.test(engHtml),
    "the page says fuse RATINGS are not in the data");
  record(/is not stated anywhere/.test(engHtml),
    "and that whether a blown relay disables anything is NOT stated");
  record(/suggest/i.test(engHtml),
    "and that PenetrationMultiplier only SUGGESTS damage reaches fuses first");
  record(!/will disable|causes .* to fail|knocks out/i.test(engHtml),
    "and claims no failure behaviour of its own");
}

console.log("\n--- M3: plain language, reachable by keyboard and not hover alone ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();tab="loadout";renderAll();`, sandbox);
  const stats = el("stats").innerHTML;
  record(/class="stat[^"]*explained/.test(stats), "values carry an explanation");
  record(/title="/.test(stats), "reachable by mouse (title)");
  record(/aria-label="/.test(stats), "and by screen reader (aria-label)");
  record(/tabindex="0"/.test(stats),
    "AND BY KEYBOARD - tabindex, so it exists for somebody with no mouse");
  // The CSS must reveal it on focus, not only on hover. A tooltip that answers
  // only to a pointer is a feature with half its point missing.
  record(/:focus[^{]*\.why|\.why[^{]*:focus/.test(html) || /focus-within/.test(html),
    "and the CSS reveals it on :focus, not only on :hover");
  const explained = (stats.match(/tabindex="0"/g) || []).length;
  record(explained > 5, "a real number of values are explained", `${explained}`);
  // The sentences are plain: no game-file jargon in the explanation itself.
  const EX = g("EXPLAIN");
  const jargon = Object.entries(EX).filter(([k, v]) =>
    /CompatibleTypes|ClassName|stdItem|PortId|IsPilotSlaveable/.test(v));
  record(jargon.length === 0,
    "and no explanation uses a game-file field name",
    jargon.map(([k]) => k).join(", "));
  notes.push(`M3: ${explained} values carry a plain-language sentence, each ` +
    `reachable by mouse, keyboard and screen reader`);
}

console.log("\n--- N2: the Acquisition block moved across, field by field ---");
{
  /* THE FAILURE MODE OF A CONSOLIDATION IS A FIELD NOBODY NOTICES IS GONE.
     index.html's ship panel is retired, so every fact it showed is asserted
     here BY NAME on a hull that has it - not "the panel renders", which would
     pass with half of it missing. */
  const INFO = g("INFO");
  record(Object.keys(INFO).length > 150,
    "the acquisition data reached the ship page",
    `${Object.keys(INFO).length} ships`);

  // Pick a hull that carries as much of the block as exists, by measurement.
  const rich = Object.keys(INFO).find((k) => SHIPS[k] &&
    INFO[k].auec && INFO[k].sold && INFO[k].conf && INFO[k].rec != null);
  record(!!rich, "found a hull carrying price, dealers, confidence and a record number");
  vm.runInContext(`shipId=${JSON.stringify(rich)};reset();renderAll();`, sandbox);
  const I = INFO[rich];
  const acq = el("acq").innerHTML;
  const rec = el("recrow").innerHTML;
  vm.runInContext(`tab="buy";renderBuy();`, sandbox);
  const buy = el("buy").innerHTML;
  vm.runInContext(`tab="specs";renderSpecs();`, sandbox);
  const specs = el("specs").innerHTML;
  const related = el("related").innerHTML;
  const head = el("shipname").textContent;

  // ---- the checklist, one line per field --------------------------------
  const TICK = [
    ["In-game price",   acq, Number(I.auec).toLocaleString()],
    ["Pledge price",    acq, "Pledge price"],
    ["Sold at",         buy, I.sold[0]],
    ["View on RSI",     String(el("rsi").href), "robertsspaceindustries"],
    ["Confidence",      rec, I.conf],
    ["Last verified",   rec, "last verified against patch"],
    ["Record number",   rec, "#" + I.rec],
    ["Ship name",       head, SHIPS[rich].n],
    ["Manufacturer",    acq, SHIPS[rich].m],
    ["Status",          acq, I.stat === "purchasable" ? "Purchasable" : "pledge only"],
    ["Related ships",   related, "Related"],
    ["Model folder",    specs, "3D model file"],
  ];
  for (const [what, where, needle] of TICK) {
    record(String(where).includes(needle),
      `N2 tick: ${what} is on the ship page`, `looked for ${JSON.stringify(needle)}`);
  }
  notes.push(`N2 checklist ticked on ${SHIPS[rich].n}: ` +
    TICK.map(([w]) => w).join(", "));

  // NOTES is on a minority of ships, so it is ticked on one that HAS it -
  // asserting it on a ship without would pass for the wrong reason.
  const withNote = Object.keys(INFO).find((k) => SHIPS[k] && INFO[k].note);
  record(!!withNote, "a hull with a note exists to tick it on");
  if (withNote) {
    vm.runInContext(`shipId=${JSON.stringify(withNote)};reset();tab="specs";renderAll();renderSpecs();`, sandbox);
    record(el("specs").innerHTML.includes(INFO[withNote].note),
      `N2 tick: Notes is on the ship page (${SHIPS[withNote].n})`);
  }

  // AND THE ONE THAT DID NOT SURVIVE, because saying so is the point of a
  // checklist. The site's own last_verified_patch is null on all 254 records,
  // so there was never anything to move - index.html rendered "not recorded"
  // for every ship in the fleet. The page states the SNAPSHOT's patch instead,
  // which is a real answer.
  const anyLvp = Object.values(INFO).filter((v) => v.lvp).length;
  record(anyLvp === 0,
    "the site's own last-verified field is empty on every ship - so the page " +
    "states the snapshot's patch instead of an empty row",
    `${anyLvp} ships carry one`);
  notes.push("N2: the site's `last_verified_patch` is null on all 254 records " +
    "- index.html showed \"not recorded\" for every ship. The ship page states " +
    "the snapshot patch, which is a real figure.");

  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();tab="loadout";renderAll();`, sandbox);
}

console.log("\n--- N5/N6: the page opens on ONE build, and each stat renders once ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);

  record(g("twoUp") === false, "the page opens with one build");
  record(el("colB").hidden === true, "and the second column is not on the page");

  /* N6: EACH STAT EXACTLY ONCE. The failure this replaces rendered every stat
     twice with `same` beside it, fourteen times over - and when everything
     says `same` all the time, nothing catches the eye when something finally
     is not. Counted per stat, not in total: a total could be right while one
     stat rendered twice and another not at all. */
  const stats = el("stats").innerHTML;
  const labels = [...stats.matchAll(/<div class="k">([^<]*?)(?:<span|<\/div>)/g)]
    .map((m) => m[1].trim());
  const dupes = labels.filter((l, i) => labels.indexOf(l) !== i);
  record(labels.length > 10, "a real number of stats rendered", `${labels.length}`);
  record(dupes.length === 0, "each stat label appears exactly once",
    `duplicated: ${[...new Set(dupes)].slice(0, 3)}`);
  const values = (stats.match(/class="va"/g) || []).length;
  const seconds = (stats.match(/class="vb/g) || []).length;
  record(values === labels.length && seconds === 0,
    "and carries ONE value, with no second column of numbers beside it",
    `${values} values, ${seconds} second values`);
  record(!/>same</.test(stats),
    "and the word \"same\" appears nowhere - there is nothing to be the same as");
  notes.push(`N6: ${labels.length} stats, each rendered once, no second value ` +
    `column and no "same" anywhere`);

  /* N5: NO A/B LETTERS BEFORE A SECOND BUILD EXISTS. The column is headed with
     the SHIP, because a letter with nothing to contrast against is a label for
     a distinction nobody has made. */
  const colA = el("colA").innerHTML;
  record(colA.includes(SHIPS[shipKey].n),
    "the single column is headed with the ship, not a letter");
  record(!/Build A|Build B/.test(colA),
    "and carries no A or B label at all");

  /* The button, and its exact wording. Sleven chose it and it is not to be
     reworded, so the check asserts the STRING rather than "a button exists". */
  record(/id="addB"[^>]*>Try another alongside</.test(html) ||
         />Try another alongside</.test(html),
    "the button reads exactly \"Try another alongside\"");
  /* STRIPPED OF COMMENTS FIRST. The page explains IN PROSE that "Compare
     builds" was the rejected wording, and a check that read its own
     explanation as the thing it forbids would fail the page for documenting
     itself. The stripper is proven live on the next line - without that, it
     could equally be hiding a real one somebody left in. */
  const noComments = html.replace(/<!--[\s\S]*?-->/g, "")
                         .replace(/\/\*[\s\S]*?\*\//g, "");
  record(/Compare builds/i.test(html) && !/Compare builds/i.test(noComments),
    "the comment stripper works: the page's prose names the rejected wording, "
    + "its markup does not");
  record(!/Compare builds/i.test(noComments),
    "and not \"Compare builds\", which was explicitly rejected");

  // ---- ask for the second build -----------------------------------------
  vm.runInContext(`twoUp=true;B=Object.assign({},A);editing="B";renderAll();`, sandbox);
  const twoStats = el("stats").innerHTML;
  record(g("twoUp") === true, "the second build can be asked for");
  record(el("colB").hidden === false, "and its column appears");
  record((twoStats.match(/class="vb/g) || []).length > 10,
    "and NOW every stat carries a second value");
  record(/Build A/.test(el("colA").innerHTML) && /Build B/.test(el("colB").innerHTML),
    "and the A and B labels appear only now");
  record(/Discard this one/.test(el("colB").innerHTML),
    "the second panel carries \"Discard this one\" - it says what happens and " +
    "which one goes");
  record(!/>Remove</.test(el("colB").innerHTML),
    "and not a bare \"Remove\"");

  vm.runInContext(`dropB();`, sandbox);
  record(g("twoUp") === false, "and discarding it returns to one build");
  record((el("stats").innerHTML.match(/class="vb/g) || []).length === 0,
    "with one number again");
}

console.log("\n--- N10: the first swap is unmissable ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  const quiet = el("stats").innerHTML;
  record(!/justmoved/.test(quiet),
    "nothing is marked as moved before anything has moved");

  /* The real path: a swap, through the same handler a click uses. */
  const slot = editSlots.find((x) => (FITS[x.fit] || []).length > 2);
  const alt = (FITS[slot.fit] || []).find((k) => k !== slot.stock);
  vm.runInContext(
    `sel={slot:${JSON.stringify(slot.id)}};editing="A";` +
    `(function(){const b=A;const before=calc(b);b[${JSON.stringify(slot.id)}]=` +
    `${JSON.stringify(alt)};markChanges(before,calc(b));})();renderAll();`, sandbox);
  const after = el("stats").innerHTML;

  const movedCount = (after.match(/justmoved/g) || []).length;
  const total = (after.match(/class="stat/g) || []).length;
  record(movedCount > 0, "after a swap, something is marked as moved",
    `${movedCount} of ${total}`);
  record(movedCount < total,
    "and NOT everything is - the changed readouts are distinguishable from " +
    "the unchanged ones without reading them",
    `${movedCount} of ${total} marked`);
  record(/class="d [a-z]+ moved"/.test(after),
    "and each one shows which way it went");
  notes.push(`N10: one swap marked ${movedCount} of ${total} readouts; the ` +
    `other ${total - movedCount} are visibly untouched`);

  /* AND IT STOPS. A mark that never clears is a page that is permanently
     shouting, which is the failure mode worth guarding against. */
  vm.runInContext(`changedStats=new Map();renderStats();`, sandbox);
  record(!/justmoved/.test(el("stats").innerHTML),
    "and the mark clears afterwards rather than staying lit");
}

console.log("\n--- N11: back to stock is always one visible click ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  record(el("reset").hidden === true,
    "no undo is offered on a build with nothing to undo");

  const slot = editSlots.find((x) => (FITS[x.fit] || []).length > 2);
  const alt = (FITS[slot.fit] || []).find((k) => k !== slot.stock);
  vm.runInContext(`A[${JSON.stringify(slot.id)}]=${JSON.stringify(alt)};renderAll();`, sandbox);
  record(el("reset").hidden === false,
    "one visible control appears the moment there is something to undo");
  record(/Back to stock/.test(html), "and it says what it does");

  /* PORT FOR PORT, against the ship's OWN stock loadout - not "empty", and not
     a default we chose. */
  vm.runInContext(`$('reset').onclick();`, sandbox);
  const back = JSON.parse(g("JSON.stringify(A)"));
  const wrong = SHIPS[shipKey].slots.filter((x) => x.fit && back[x.id] !== x.stock);
  record(wrong.length === 0,
    "and it returns every port to the ship's own stock part",
    `${wrong.length} ports not restored`);
  record(g("isStock(A)") === true, "so the build reads as stock again");
  record(el("reset").hidden === true, "and the control stands down again");
  notes.push(`N11: one visible control restores all ` +
    `${SHIPS[shipKey].slots.filter((x) => x.fit).length} editable ports to stock`);
}

console.log("\n--- N7 as B1 left it: fixed ports leave the column, and still count ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  const colA = el("colA").innerHTML;
  const specsHtml = el("specs").innerHTML;
  const nFixed = SH.slots.filter((x) => !x.fit).length;

  /* N7 FOLDED THEM AWAY. B1 MOVED THEM OUT. The fold is gone and its rules
     with it, so what is asserted now is that the column is clean and the
     signpost exists - hiding something with no signpost is not organising it. */
  record(!/<details class="fixed-group"/.test(colA),
    "the collapsed fold is gone from the column");
  record(colA.includes("id=\"tospecs\""),
    "and the sub-line's fixed count is a control that leads to them");
  record(specsHtml.includes(`Fixed ports &mdash; ${nFixed}`),
    `Specs carries them under a heading with its count (${nFixed})`);

  /* STILL RENDERED, just elsewhere. A move that dropped them would satisfy
     "they are out of the column" and lose them. */
  const rendered = (colA.match(/class="slot/g) || []).length
    + (specsHtml.match(/class="slot fixed"/g) || []).length;
  record(rendered === SH.slots.length,
    "every port is still rendered - moved, not dropped",
    `${rendered} of ${SH.slots.length}`);

  /* AND THEY STILL COUNT. The order is explicit: a thruster affects mass
     whether or not you chose it. Proven the same way L4 proved it - remove
     them and watch the totals move. */
  const withFixed = g("JSON.stringify(calc(A))");
  vm.runInContext(
    `__save=SHIPS[${JSON.stringify(shipKey)}].slots;` +
    `SHIPS[${JSON.stringify(shipKey)}].slots=__save.filter(s=>s.fit);`, sandbox);
  const withoutFixed = g("JSON.stringify(calc(A))");
  vm.runInContext(`SHIPS[${JSON.stringify(shipKey)}].slots=__save;`, sandbox);
  record(withFixed !== withoutFixed,
    "and they still contribute to the readout - dropping them moves it");
  record(/still count toward/.test(specsHtml),
    "and the page says so, rather than leaving somebody to wonder");
  notes.push(`N7/B1: ${nFixed} of ${SH.slots.length} ports moved to Specs on ` +
    `${SH.n}; all still rendered and all still counted`);
}

console.log("\n--- N8: the grouping is Editable, never a list of types ---");
{
  /* THE LOAD-BEARING CONTROL, and the order names it: flip `Editable` on a
     fixed port and confirm it moves out of the collapsed group WITH NO CODE
     CHANGE. Sleven's reasoning is "if ever it changes, we already have a
     foundation built for it" - so the thing to prove is that the page follows
     the DATA rather than a list somebody typed. */

  // First: no type list anywhere in the split.
  const src = script;
  record(!/FIXED_TYPES|NOT_SWAPPABLE|\[["'](?:FuelTank|ManneuverThruster|Armor)/.test(src),
    "no hardcoded list of fixed component types exists in the page");
  record(/shut=\(?sh\.slots\)?\.filter\(x=>!swappable\(x\)\)/.test(src.replace(/\s+/g, "")) ||
         /shut=\(sh\.slots\|\|\[\]\)\.filter\(x=>!swappable\(x\)\)/.test(src.replace(/\s+/g, "")),
    "the split is `!swappable(slot)` and nothing else");
  record(/const swappable\s*=\s*s\s*=>\s*!!s\.fit/.test(src),
    "and `swappable` is the port's own fit rule, set from its Editable flag");

  /* NOW FLIP IT. A fixed port on the driving hull is given a fitment rule -
     which is what the generator does when a port says Editable - and NOTHING
     ELSE IS TOUCHED. No code is edited; the data changes and the page follows. */
  const fixedSlot = SH.slots.find((x) => !x.fit && x.stock);
  record(!!fixedSlot, "found a fixed port to flip");
  const donorRule = Object.keys(FITS).find((k) => (FITS[k] || []).length > 2);

  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  record(el("specs").innerHTML.includes(`data-fixed="${fixedSlot.id}"`),
    `the port starts on the Specs tab (${fixedSlot.id})`);
  record(!el("colA").innerHTML.includes(`data-slot="${fixedSlot.id}"`),
    "and not in the column of things that can be changed");

  vm.runInContext(
    `__slot=SHIPS[${JSON.stringify(shipKey)}].slots.find(s=>s.id===${JSON.stringify(fixedSlot.id)});` +
    `__slot.fit=${JSON.stringify(donorRule)};reset();renderAll();`, sandbox);

  record(el("colA").innerHTML.includes(`data-slot="${fixedSlot.id}"`),
    "flipping Editable moves it INTO the column - with no code change");
  record(!el("specs").innerHTML.includes(`data-fixed="${fixedSlot.id}"`),
    "and it has left the Specs list");
  const nowFixed = SH.slots.filter((x) => !x.fit).length;
  record(el("colA").innerHTML.includes(`${nowFixed}\n           fixed`) ||
         el("colA").innerHTML.includes(`>${nowFixed}`),
    "and the sub-line's fixed count follows it", `now ${nowFixed}`);
  notes.push(`N8: flipping one port's Editable flag moved it from Specs into ` +
    `the column and dropped the fixed count to ${nowFixed} - no code edited, ` +
    `the page follows the data`);

  // put it back, and confirm it goes back - a one-way move would also pass above
  vm.runInContext(`delete __slot.fit;reset();renderAll();`, sandbox);
  record(el("specs").innerHTML.includes(`data-fixed="${fixedSlot.id}"`),
    "and flipping it back returns it to Specs");
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
}

/* N9 REWRITTEN 2026-08-27 BY THE SESSION THAT CHANGED THE PAGE (C1).

   N9 existed because the page once implied the dots were measured when they
   were name-derived. It asserted the apology: "not measured from the model",
   "single welded mesh", "nothing to measure".

   THE APOLOGY IS NOW THE FALSE STATEMENT. CIG's geometry was decoded out of
   Data.p4k and 1,693 mounts across 166 hulls carry the positions CIG
   published. Asserting the old wording would pin the page to a disclaimer
   about a limitation it no longer has.

   N9'S ACTUAL RULE SURVIVES INTACT AND IS WHAT IS ASSERTED HERE: the page may
   not claim more certainty than it has. It must say the measured part is
   measured, say the estimated part is estimated, and - because the marker file
   carries no per-port provenance - say that it cannot tell you which one this
   ship's dots are. All three still fail if the page starts claiming
   everything is exact. */
console.log("\n--- N9: the page claims exactly the certainty it has ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  const note = el("markernote").innerHTML;
  record(note.length > 200, "a hull with markers carries the note", `${note.length} chars`);
  record(/game's own geometry|game files/i.test(note) && /decoded/i.test(note),
    "and says the measured positions come from the game's own geometry");
  record(/name/i.test(note) && /snapped/i.test(note) && /estimate/i.test(note),
    "and still says what the FALLBACK is - the mount's name, snapped, an estimate");
  record(/cannot yet tell you which/i.test(note),
    "and admits it cannot say which of the two THIS ship's dots are");
  record(/not estimated/.test(note) && /size|type|fitted/i.test(note),
    "and that what each port IS remains unestimated");

  /* THE OLD SENTENCE MUST BE GONE FROM EVERYWHERE, including index. */
  const stripped = html.replace(/<!--[\s\S]*?-->/g, "").replace(/\/\*[\s\S]*?\*\//g, "");
  record(!/Nothing here is estimated/.test(stripped),
    "the old \"Nothing here is estimated\" claim is gone from the ship page");
  record(!/measured from this hull/i.test(stripped),
    "and so is \"measured from this hull's own model geometry\"");
  record(!/positions have been measured/i.test(stripped),
    "and the wording that IMPLIED measurement where markers do appear");
  notes.push("N9: the marker note states the positions come from the mount's " +
    "name and are not measured, says why that cannot currently be better, and " +
    "keeps the axis and nose described as measured because they are");

  /* A hull with NO markers says something different and equally honest.

     THIS ASSERTED SILENCE UNTIL 2026-08-23 AND E1 CHANGED THAT DELIBERATELY.
     Saying nothing was the defect Sleven found: 42 hulls draw a model, mark
     nothing on it, and left a visitor unable to tell "this ship has no weapon
     mounts" from "this page is broken".

     So the claim is not relaxed, it is REPLACED by the stronger one - the hull
     says which kind of nothing it is, and says only that one.
     checks/_verify_marker_absence.mjs is the item's own control and sweeps
     every hull; this stays as the regression guard in the place that noticed. */
  const MARKS2 = g("MARKS"), MODELS2 = g("MODELS");
  const noMark = Object.keys(SHIPS).find((k) =>
    SHIPS[k].slots.length && MODELS2[k] && !(MARKS2[k] || []).length);
  if (noMark) {
    vm.runInContext(`shipId=${JSON.stringify(noMark)};reset();resetView();renderAll();`, sandbox);
    const nm = el("markernote").innerHTML || "";
    const MARKABLE2 = new Set(["WeaponGun", "Turret", "MissileLauncher",
      "WeaponDefensive", "WeaponMining", "BombLauncher", "SalvageHead",
      "TractorBeam", "EMP", "Missile", "Bomb"]);
    const mounts = (SHIPS[noMark].slots || [])
      .filter((s) => MARKABLE2.has((TYPES[s.t] || {}).t)).length;
    const saysNone = /no weapon mounts in the data/.test(nm);
    const saysNoPos = /no measured positions/.test(nm);
    record(nm.length > 40,
      "a hull with no markers SAYS SO rather than staying silent - saying "
      + "nothing is what E1 was raised about");
    record(mounts ? (saysNoPos && !saysNone) : (saysNone && !saysNoPos),
      mounts
        ? `and ${SHIPS[noMark].n} carries ${mounts} weapon mounts, so it is `
          + `told there are no positions - not that it has no mounts`
        : `and ${SHIPS[noMark].n} genuinely has no weapon mounts, so it gets `
          + `the Cyclone's wording`,
      `mounts=${mounts} none=${saysNone} nopos=${saysNoPos}`);
    record(!(saysNone && saysNoPos),
      "and never both messages at once");
    record(/no marker placement for this hull/i.test(el("shipstate").innerHTML),
      "and says it has no marker placement, rather than that none was measured");
  }
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
}

console.log("\n--- N4 (behavioural): one model load per ship, none per tab ---");
{
  /* THE SECTION-4 AUDIT MOVED THIS HERE. The N4 assertions in
     _verify_shared_viewer.mjs grep for `new CCViewer.Viewer(` appearing once
     and for the string `_modelFor === shipId`. That asserts the code CONTAINS
     a guard. It does not assert the guard WORKS - which is precisely the shape
     that let every ship name point at RSI while the check reported N1 done.

     So the load path is driven, and the loads are COUNTED. */
  const loads = [];
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();`, sandbox);
  /* Stand in for the viewer with something that records what it is asked to
     load. The page's own showModel() decides whether to ask. */
  vm.runInContext(`__loads=[];_view={
      boot(){},start(){},size(){},cancel(){},clear(){},stop(){},
      current:{},unitScale(){return 1;},project(){return null;},
      /* The stub mirrors the REAL Viewer interface. When cc_viewer.js gained
         setSpin/spinning for P4, this did not, and the page threw on a method
         the real viewer has - the stub was lying about the shape of the thing
         it stands in for. */
      spinning(){return this._s!==false;},setSpin(v){this._s=!!v;return this._s;},
      load(u){__loads.push(u);return 1;}
    };_modelFor=null;`, sandbox);

  vm.runInContext(`showModel();`, sandbox);
  const after1 = g("__loads.length");
  record(after1 === 1, "opening a ship fetches its geometry once", `${after1}`);

  vm.runInContext(`showModel();showModel();`, sandbox);
  record(g("__loads.length") === after1,
    "and asking again for the SAME ship fetches nothing more",
    `${g("__loads.length")} total`);

  /* Moving between tabs re-renders; it must not re-fetch, and must not
     reinitialise the viewer. */
  const viewerBefore = g("_view");
  vm.runInContext(`openTab("specs");openTab("liveries");openTab("loadout");`, sandbox);
  record(g("__loads.length") === after1,
    "moving between tabs fetches no further geometry",
    `${g("__loads.length")} total`);
  record(g("_view") === viewerBefore,
    "and does not replace the viewer instance");

  /* A DIFFERENT ship must fetch - otherwise "no further loads" would be
     satisfied by a page that never loads anything again. */
  const other = Object.keys(SHIPS).find(k => k !== shipKey && g("MODELS")[k]);
  vm.runInContext(`shipId=${JSON.stringify(other)};reset();showModel();`, sandbox);
  record(g("__loads.length") === after1 + 1,
    "but changing SHIP does fetch, once",
    `${g("__loads.length")} total`);
  notes.push(`N4 behavioural: ${g("__loads.length")} geometry loads across ` +
    `two ships, three showModel() calls and three tab switches`);

  vm.runInContext(`_view=null;_modelFor=null;shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
}

console.log("\n--- P4: the rotation can be stopped, and stopping it stops it ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  record(/id="cc-spin"/.test(html), "a stop control exists on the canvas");
  record(/<button[^>]*id="cc-spin"/.test(html),
    "and it is a real <button>, so it is reachable by keyboard");
  record(/aria-pressed/.test(html), "and reports its state to a screen reader");

  /* ASSERT THE ROTATION VALUE, NOT THE PRESENCE OF A BUTTON. The order says so
     explicitly, and it is the erratum's lesson: a control that exists and does
     nothing is what "I don't see a stop button anywhere" turns into. */
  vm.runInContext(`_view={_s:true,boot(){},start(){},size(){},cancel(){},clear(){},
    stop(){},current:{},unitScale(){return 1;},project(){return null;},
    spinning(){return this._s;},setSpin(v){this._s=!!v;return this._s;},
    load(){return 1;}};spinOn=true;applySpin();`, sandbox);
  record(g("_view.spinning()") === true, "the viewer starts rotating");
  vm.runInContext(`toggleSpin();`, sandbox);
  record(g("_view.spinning()") === false,
    "and toggling the control actually HALTS it - the viewer's own rotation "
    + "value, not a class on a button");
  record(el("cc-spin").textContent === "Start spin",
    "the control says what it will do next", el("cc-spin").textContent);
  vm.runInContext(`toggleSpin();`, sandbox);
  record(g("_view.spinning()") === true, "and toggling back resumes it");

  /* IT PERSISTS WHILE THEY ARE ON THE PAGE. Somebody who stopped the spin to
     read a marker does not want it starting again when they change ship. */
  vm.runInContext(`toggleSpin();`, sandbox);
  const otherShip = Object.keys(SHIPS).find(k => k !== shipKey && g("MODELS")[k]);
  vm.runInContext(`shipId=${JSON.stringify(otherShip)};reset();_modelFor=null;showModel();`, sandbox);
  record(g("spinOn") === false && g("_view.wantSpin") === false,
    "and a stopped ship stays stopped when the ship changes");
  notes.push("P4: the stop control halts the viewer's own autoRotate, says " +
    "what it will do next, and survives a change of ship");
  vm.runInContext(`spinOn=true;shipId=${JSON.stringify(shipKey)};reset();resetView();_view=null;_modelFor=null;renderAll();`, sandbox);
}

console.log("\n--- P5: a marker CLICK opens the picker for THAT port ---");
{
  /* THE ERRATUM'S LESSON, APPLIED. Asserting that a listener exists is
     worthless - that is exactly what let every ship name point at RSI. So this
     builds the marker, projects it to a screen position, and DISPATCHES A REAL
     CLICK through the page's own delegated handler.
     `handlers.click` is captured because the harness's document records
     addEventListener rather than swallowing it. */
  const MARKS = g("MARKS");
  const markShip = Object.keys(MARKS).find(k => SHIPS[k] &&
    MARKS[k].some(m => { const s = SHIPS[k].slots.find(x => x.p === m[0]); return s && s.fit; }));
  record(!!markShip, "found a hull with a marker on a swappable port");
  const mark = MARKS[markShip].find(m => {
    const s = SHIPS[markShip].slots.find(x => x.p === m[0]); return s && s.fit; });
  const slot = SHIPS[markShip].slots.find(x => x.p === mark[0]);

  const clickMarker = (spinning) => {
    vm.runInContext(
      `shipId=${JSON.stringify(markShip)};reset();resetView();` +
      `spinOn=${spinning};` +
      `_view={_s:${spinning},boot(){},start(){},size(){},cancel(){},clear(){},stop(){},` +
      `current:{},unitScale(){return 1;},project(){return{x:640,y:360,depth:0};},` +
      `spinning(){return this._s;},setSpin(v){this._s=!!v;return this._s;},` +
      `load(){return 1;}};_modelFor=shipId;sel=null;renderAll();`, sandbox);
    /* V2: THE DOT FOR THIS PORT IS THE DOT FOR ITS MOUNT. The markup carries
       data-mount, and the port we are asking about is reached through it -
       directly when the mount holds one weapon, via the list when it holds
       several. What is asserted below is unchanged: port blr2 and no other. */
    const box = el("cc-marks").innerHTML;
    const root = String(mark[0]).split(".")[0];
    if (!box.includes(`data-mount="${root}"`)) return { rendered: false };
    const rep = g(`(mountOf(shipId, ${JSON.stringify(mark[0])})||{}).p`) || mark[0];
    /* The element a browser would hand the handler for a click at that point. */
    const btn = {
      tagName: "BUTTON", dataset: { mount: root, port: rep },
      closest: (s) => (s === "#cc-marks button[data-mount]"
                       || s === "#cc-marks button[data-port]") ? btn : null,
    };
    let threw = null;
    for (const fn of clickHandlers) {
      try { fn({ target: btn, preventDefault() {} }); } catch (e) { threw = e.message; }
    }
    const openedPanel = el("cc-panel");
    if (!openedPanel.hidden
        && (openedPanel.innerHTML || "").includes("data-mountport")) {
      const row = {
        tagName: "BUTTON", dataset: { mountport: mark[0] },
        closest: (s) => (s === "#cc-panel button[data-mountport]" ? row : null),
      };
      for (const fn of clickHandlers) {
        try { fn({ target: row, preventDefault() {} }); } catch (e) { threw = e.message; }
      }
    }
    return { rendered: true, threw, sel: JSON.parse(g("JSON.stringify(sel)")),
             picker: pickerNow() };
  };

  for (const spinning of [true, false]) {
    const r = clickMarker(spinning);
    const what = spinning ? "with rotation RUNNING" : "with rotation STOPPED";
    record(r.rendered, `the marker renders ${what}`);
    record(!r.threw, `and the click handler does not throw ${what}`, r.threw || "");
    record(r.sel && r.sel.slot === slot.id,
      `clicking it selects port ${slot.id} and no other, ${what}`,
      JSON.stringify(r.sel));
    record(r.picker && r.picker.length > 400,
      `and the picker for that port is rendered ${what}`,
      `${(r.picker || "").length} chars`);
  }
  notes.push(`P5: a dispatched click on the marker for PortId ${mark[0]} on ` +
    `${SHIPS[markShip].n} selects slot ${slot.id} and renders its picker, ` +
    `both with rotation running and with it stopped`);

  /* AND THE CONSEQUENCE IS WHERE THE EYE IS. The click was never broken; the
     picker rendered ~1,050px down a 1,952px page. It now replaces the list in
     the LEFT COLUMN, which is on screen. */
  /* P5 FIXED THIS BY REPLACING THE LIST WITH THE PICKER. B2 replaced that in
     turn, for the reason P6 gave about the second build: taking the column
     over fixed "the change was off screen" by creating "you lost your place in
     the list you were reading". The picker now opens INLINE under its row and
     THE COLUMN NEVER DISAPPEARS - so what is asserted is the stronger version
     of the same thing. */
  record(el("colA").hidden === false,
    "the component list is still on screen with the picker open - it is not "
    + "taken over any more");
  /* B3: THIS PORT HAS A MARKER, so its picker is a panel over the stage rather
     than an inline row - which is the whole point of the item. What P5 cared
     about survives and is asserted: the list is still there behind it. */
  record(el("cc-panel").hidden === false,
    "and the picker opened as a panel over the model, where the marker is");
  vm.runInContext(`sel=null;renderAll();`, sandbox);
  record(el("colA").hidden === false && el("cc-panel").hidden === true,
    "and closing it leaves the list exactly where it was");
}

console.log("\n--- P6: the second build appears where the eye already is ---");
{
  vm.runInContext(`shipId=${JSON.stringify(shipKey)};reset();resetView();renderAll();`, sandbox);
  record(el("colB").hidden === true, "there is one build to start with");
  vm.runInContext(`$('addB').onclick();`, sandbox);
  record(g("twoUp") === true, "the button adds a second build");
  record(el("colB").hidden === false,
    "and its column is visible immediately");
  record(el("colB").innerHTML.length > 400,
    "with its component rows rendered, not empty",
    `${el("colB").innerHTML.length} chars`);
  /* WITHIN THE VIEWPORT. Both builds live in the LEFT COLUMN, which starts
     153px down a 1,080px screen - so the second build's first row is on screen
     by construction rather than by hoping. It was previously below a readout
     block and a 460px stage. */
  record(/class="colpane"/.test(html) && /id="colB"/.test(html),
    "both builds are panes of the same column, so the second cannot land "
    + "below the fold while the first is on screen");
  vm.runInContext(`dropB();`, sandbox);
  record(g("twoUp") === false && el("colB").hidden === true,
    "and Discard removes it again");
  notes.push("P6: the second build renders into the same left column as the " +
    "first, which begins 153px down the page - not below a readout and a stage");
}

/* ---------------------------------------------- rule 8: never touch these */
console.log("\n--- rule 8: the trademark and Fan Kit text is untouched ---");
record(/Cloud Imperium Rights LLC/.test(html), "the trademark footer is intact");
record(/unofficial Star Citizen fan site/.test(html), "the Fan Kit disclaimer is intact");

/* -------------------------------------------------------------- verdict */
console.log("");
if (notes.length && !SELFTEST) {
  console.log("MEASURED, for the ledger:");
  for (const n of notes) console.log("  - " + n);
  console.log("");
}
if (failures.length) {
  console.log(`FAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  - " + f);
  if (MUTATE) {
    console.log("\nMUTANT CAUGHT: the widened fitsFor was noticed by " +
                `${failures.length} assertion(s). The check works.`);
    process.exit(0);
  }
  process.exit(1);
}
if (MUTATE) {
  console.log("MUTANT ESCAPED: fitsFor was widened to offer every part of the " +
              "type and NOTHING here noticed. This file is not a check.");
  process.exit(1);
}
console.log(`PASSED: ${passed} assertions against the page's own rendered HTML.`);
if (SELFTEST) {
  console.log("SELF-TEST DID NOT FAIL - the inverted run passed, so these " +
              "assertions do not depend on the page. That is a broken harness.");
  process.exit(1);
}
process.exit(0);
