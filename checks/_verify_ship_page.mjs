/**
 * L3, L4, L6, L12, L13 acceptance for the ship page (testing/_src/loadout.src.html).
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
const EXTRA = ["loadout_model.gen.js", "loadout_marker.gen.js"]
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
    });
  }
  return els.get(id);
}

let currentHash = "";
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
    addEventListener() {},
    querySelector: () => null,
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

let script = html.match(/<script>\n([\s\S]*)<\/script>/)[1];
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
// EVERY port appears, fixed and editable alike. Counted, not sampled: a
// sample would pass while one group silently vanished.
const rendered = (colA.match(/class="slot/g) || []).length;
record(rendered === SH.slots.length,
  `every one of the ${SH.slots.length} ports rendered - fixed and editable alike`,
  `rendered ${rendered}`);
const renderedFixed = (colA.match(/class="slot fixed"/g) || []).length;
record(renderedFixed === fixedSlots.length,
  `all ${fixedSlots.length} FIXED ports rendered rather than being hidden`,
  `rendered ${renderedFixed}`);
record(/can'?t be changed|does not allow this to be changed|no part for this port/.test(colA),
  "a fixed port says plainly that it cannot be changed");
// It names the part in it. "Fuel tank - LOCKED" tells a visitor nothing.
const namedFixed = fixedSlots.filter(s => s.stock && PARTS[s.stock])
  .map(s => PARTS[s.stock].n).filter(n => colA.includes(n));
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
vm.runInContext(`sel={slot:${JSON.stringify(fx.id)}};renderPicker();`, sandbox);
const fixedPicker = el("picker").innerHTML;
record(!/data-part=/.test(fixedPicker),
  "clicking a fixed port opens NO picker - nothing selectable is offered");

/* -------------------------------- L3: what the picker offers, both halves */
console.log("\n--- L3: a part the port accepts APPEARS; one it does not is ABSENT ---");
// A port with a real list, chosen by measurement.
const target = editSlots.find(s => (FITS[s.fit] || []).length > 4);
record(!!target, "found an editable port with a real list of alternatives");
vm.runInContext(`editing="A";sel={slot:${JSON.stringify(target.id)}};renderPicker();`, sandbox);
const picker = el("picker").innerHTML;

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
const inPicker = [...picker.matchAll(/data-part="([^"]+)"/g)].map(m => m[1]);
record(inPicker.length === offered.length,
  `the picker offers exactly the ${offered.length} parts the port admits`,
  `rendered ${inPicker.length}`);
record(inPicker.every(k => offered.includes(k)),
  "and every one of them is on that port's own list");

/* --------------------------------------- L3 sweep: EVERY port on the ship */
console.log("\n--- L3 across every editable port on the ship, not one sample ---");
let bad = 0, checked = 0;
for (const s of editSlots) {
  vm.runInContext(`sel={slot:${JSON.stringify(s.id)}};renderPicker();`, sandbox);
  const h = el("picker").innerHTML;
  const got = [...h.matchAll(/data-part="([^"]+)"/g)].map(m => m[1]);
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
vm.runInContext(
  `B[${JSON.stringify(target.id)}]=${JSON.stringify(accepted !== target.stock ? accepted : offered.find(k => k !== target.stock))};renderAll();`,
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
    const viaList = el("picker").innerHTML;
    const listSel = JSON.parse(g("JSON.stringify(sel)"));

    vm.runInContext(`sel=null;renderAll();`, sandbox);
    vm.runInContext(`selectPort(slotByPort(${JSON.stringify(mark[0])}),"A");`, sandbox);
    const viaMark = el("picker").innerHTML;
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
  record(/No mount positions have been measured/.test(el("shipstate").innerHTML),
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
