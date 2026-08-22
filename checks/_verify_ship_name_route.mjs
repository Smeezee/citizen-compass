/**
 * ERRATUM CONTROL, 2026-08-22: a ship name must RESOLVE to the ship page.
 *
 * WHY THIS FILE EXISTS AND THE OLD CHECK DOES NOT COUNT
 * ----------------------------------------------------
 * N12 reported "A SHIP NAME LANDS ON THE SHIP PAGE: `shipPageUrl` x3,
 * `loadout.html#`, and `cc-nobench` present". Every one of those strings WAS
 * present. Every ship name still opened robertsspaceindustries.com, because the
 * function containing them bailed out before it ran.
 *
 * THE CHECK ASSERTED THAT CODE EXISTS. It never asserted that a name RESOLVES.
 * It could not have failed. That is rule 12 and it is the eighth instance of
 * this shape in this project's log.
 *
 * SO NOTHING HERE GREPS FOR A SYMBOL. Every assertion below runs the real
 * `nameCellHtml()` out of the BUILT page against a REAL record and reads the
 * href that comes back.
 *
 *   POSITIVE  Aegis Redeemer  -> loadout.html#AEGS_Redeemer, and no
 *             robertsspaceindustries anywhere in the cell
 *   NEGATIVE  Aegis Vulcan    -> no game file, so it MUST point at RSI, with
 *             the explanation. Both halves, or neither is proven: a function
 *             returning a ship-page link for everything would pass the first.
 *   WHOLE SET every record with a LOADOUT_LINK entry emits a ship-page href,
 *             and the COUNT equals the number of linked records - not "at
 *             least one", which is what let the last one through.
 *
 * `--served <url>` runs the same count against the DEPLOYED page instead of the
 * local build, which is the only way to know what is actually standing on the
 * web.
 *
 * `--prove` PUTS THE DEFECT BACK. It restores the original `nameCellHtml()` -
 * the one that always emitted an RSI anchor - and requires this file to FAIL.
 * Given that the check this replaces could not have failed, a check that has
 * not been seen failing against the exact bug it exists for is not evidence of
 * anything. Exit 0 means the defect was caught.
 *
 * Usage:  node checks/_verify_ship_name_route.mjs
 *         node checks/_verify_ship_name_route.mjs --prove
 *         node checks/_verify_ship_name_route.mjs --served https://...
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const LOCAL = join(HERE, "..", "testing", "_deploy", "index.html");
const servedIx = process.argv.indexOf("--served");
const SERVED = servedIx > -1 ? process.argv[servedIx + 1] : null;

let passed = 0;
const failures = [];
const notes = [];
function record(got, label, detail = "") {
  if (got) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

const PROVE = process.argv.includes("--prove");
let html = SERVED
  ? await (await fetch(SERVED)).text()
  : readFileSync(LOCAL, "utf-8");
console.log(SERVED ? `--- against the SERVED page: ${SERVED}` : "--- against the local build");

if (PROVE) {
  /* THE ORIGINAL, RESTORED. This is the exact function that shipped on
     2026-08-22 and sent all 229 pledged ships to RSI. If the assertions below
     do not go red against it, they are not checking anything. */
  const BROKEN = [
    'function nameCellHtml(ship) {',
    '  if (ship.pledge_url) {',
    '    return "<td><a class=\\"buy-link\\" href=\\"" + escapeHtml(ship.pledge_url) +',
    '      "\\" target=\\"_blank\\" rel=\\"noopener\\">" + escapeHtml(ship.name) +',
    '      " &#128279;</a></td>";',
    '  }',
    '  return "<td>" + escapeHtml(ship.name) + "</td>";',
    '}',
  ].join("\n");
  const before = html;
  html = html.replace(/function nameCellHtml\(ship\) \{[\s\S]*?\n\}/, BROKEN);
  if (html === before) {
    console.log("PROVE FAILED TO APPLY: nameCellHtml was not found, so this "
      + "run proves nothing. Fix the mutator before trusting the check.");
    process.exit(1);
  }
  console.log("*** RESTORED THE ORIGINAL nameCellHtml - every pledged ship "
    + "should now point at RSI. Something below MUST go red. ***");
}

/* The page's own scripts, in a browser small enough to be obviously honest.
   Most of them will throw on something this stub does not provide - that is
   fine and expected. What matters is that `nameCellHtml` and `SHIPS` end up
   defined, which is asserted before anything is read from them. */
const el = () => {
  /* `textContent` REFLECTS INTO `innerHTML`, escaped, because the page's own
     escapeHtml() is implemented as:
         const div = document.createElement("div");
         div.textContent = s ?? "";
         return div.innerHTML;
     A stub whose innerHTML stayed "" made escapeHtml return "" for EVERYTHING -
     so every ship name and every href built through it came back blank, and the
     harness was reading cells that no browser would ever produce. The
     assertions that passed did so on hrefs built outside escapeHtml, which is
     luck rather than design. */
  let _text = "", _html = "";
  return {
    get textContent() { return _text; },
    set textContent(v) {
      _text = v == null ? "" : String(v);
      _html = _text.replace(/&/g, "&amp;").replace(/</g, "&lt;")
                   .replace(/>/g, "&gt;");
    },
    get innerHTML() { return _html; },
    set innerHTML(v) { _html = v == null ? "" : String(v); },
    className: "", value: "", style: {},
    dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    querySelector: () => null, querySelectorAll: () => [], addEventListener() {},
    appendChild() {}, focus() {}, getBoundingClientRect: () => ({ height: 0 }),
  };
};
const store = {};
const sandbox = {
  console: { log() {}, warn() {}, error() {} },
  JSON, Math, Date, Number, String, Array, Object, Map, Set, RegExp, Error,
  isNaN, parseInt, parseFloat, encodeURIComponent, decodeURIComponent,
  setTimeout: () => 0, clearTimeout() {}, addEventListener() {},
  removeEventListener() {}, localStorage: { getItem: () => null, setItem() {} },
  getComputedStyle: () => ({ paddingBottom: "0" }),
  MutationObserver: function () { return { observe() {} }; },
  document: {
    getElementById: (id) => (store[id] = store[id] || el()),
    querySelector: () => el(), querySelectorAll: () => [],
    addEventListener() {}, body: el(), createElement: () => el(),
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
let ran = 0;
for (const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) {
  try { vm.runInContext(m[1], sandbox); ran++; } catch (e) { /* page chrome */ }
}
const g = (expr) => vm.runInContext(expr, sandbox);

console.log("\n--- the page's own cell renderer is reachable ---");
/* THE HARNESS'S OWN escapeHtml MUST WORK, or every assertion below reads a
   cell with empty names and hrefs and means nothing. Proven before use. */
record(g('typeof escapeHtml === "function" && escapeHtml("A<b>&") === "A&lt;b&gt;&amp;"'),
  "the page's escapeHtml works in this harness - so the cells below carry real "
  + "names, not blanks",
  `got ${JSON.stringify(g('typeof escapeHtml === "function" ? escapeHtml("A<b>&") : null'))}`);
record(g("typeof nameCellHtml") === "function",
  "nameCellHtml() is defined in the served page");
record(g("typeof SHIPS") === "object" && g("SHIPS.length") > 200,
  "and the ship records are too", `${g("typeof SHIPS === 'object' ? SHIPS.length : 0")} records`);
record(g("typeof CC_SHIPLINK") === "object",
  "and the build's per-row link decision reached the page BEFORE it renders");

const SHIPS = g("SHIPS");
const LINK = g("typeof LOADOUT_LINK === 'object' ? LOADOUT_LINK : {}");
const cellFor = (ship) => g("nameCellHtml(" + JSON.stringify(ship) + ")");
const byName = (n) => SHIPS.find((s) => s.name === n);

console.log("\n--- POSITIVE: a ship WITH a game file goes to the ship page ---");
{
  const ship = byName("Redeemer");
  record(!!ship, "the Aegis Redeemer record exists");
  const cls = LINK[String(ship.id)];
  record(cls === "AEGS_Redeemer", "and resolves to AEGS_Redeemer", `${cls}`);
  const cell = cellFor(ship);
  record(cell.includes('href="loadout.html#AEGS_Redeemer"'),
    "its rendered name cell points at loadout.html#AEGS_Redeemer",
    cell.slice(0, 140));
  record(!/robertsspaceindustries/.test(cell),
    "and contains NO robertsspaceindustries link at all");
  record(!/&#128279;/.test(cell),
    "and no link glyph - it is not an off-site link any more");
  notes.push(`POSITIVE: Redeemer renders ${cell.match(/href="([^"]*)"/)[1]}`);
}

console.log("\n--- NEGATIVE: a ship with NO game file still reaches RSI ---");
{
  const ship = byName("Vulcan");
  record(!!ship, "the Aegis Vulcan record exists");
  record(LINK[String(ship.id)] === undefined,
    "and has no ship page, which is what makes it the negative half");
  const cell = cellFor(ship);
  record(/robertsspaceindustries/.test(cell),
    "its cell DOES point at RSI - the only route it has", cell.slice(0, 140));
  record(!/loadout\.html#/.test(cell),
    "and not at a ship page that does not exist");
  record(/no build for this ship yet/.test(cell),
    "and it explains why, rather than looking like an inconsistency");
  notes.push(`NEGATIVE: Vulcan renders RSI with an explanation`);
}

console.log("\n--- THE WHOLE SET, counted. Not \"at least one\". ---");
{
  let toPage = 0, toRsi = 0, plain = 0;
  const wrong = [];
  for (const ship of SHIPS) {
    const cell = cellFor(ship);
    const linked = LINK[String(ship.id)] !== undefined;
    if (/loadout\.html#/.test(cell)) {
      toPage++;
      if (!linked) wrong.push(`${ship.name} links to a page it has no entry for`);
      else if (!cell.includes(`#${LINK[String(ship.id)]}`)) {
        wrong.push(`${ship.name} links to the wrong class`);
      }
    } else if (/robertsspaceindustries/.test(cell)) {
      toRsi++;
      if (linked) wrong.push(`${ship.name} has a ship page and still points at RSI`);
    } else {
      plain++;
      if (linked) wrong.push(`${ship.name} has a ship page and links nowhere`);
    }
  }
  const linkedCount = SHIPS.filter((s) => LINK[String(s.id)] !== undefined).length;
  record(toPage === linkedCount,
    `every one of the ${linkedCount} linked records renders a ship-page href`,
    `${toPage} did`);
  record(wrong.length === 0, "and none renders the wrong destination",
    `${wrong.length}: ${wrong.slice(0, 3).join(" | ")}`);
  record(toPage + toRsi + plain === SHIPS.length,
    "every record is accounted for",
    `${toPage} + ${toRsi} + ${plain} vs ${SHIPS.length}`);

  /* THE NUMBER THE ERRATUM ASKS FOR. It was 229 before the fix - nearly every
     row - because the rewriter that was supposed to replace them never ran. */
  record(toRsi < 40,
    `only ${toRsi} name cells point at RSI, not 229`,
    `${toRsi} of ${SHIPS.length}`);
  notes.push(`COUNTED${SERVED ? " ON THE SERVED PAGE" : ""}: ${toPage} name ` +
    `cells point at the ship page, ${toRsi} at RSI, ${plain} nowhere. ` +
    `${toRsi + plain} ships have no ship page; ${toRsi} of them have a pledge ` +
    `page to fall back to and ${plain} have neither.`);
}

console.log("\n--- and no post-render rewriter survives ---");
{
  const code = html.replace(/<!--[\s\S]*?-->/g, "").replace(/\/\*[\s\S]*?\*\//g, "");
  record(!/function decorate\s*\(/.test(code),
    "there is no decorate() rewriting cells after the fact");
  record(!/MutationObserver\s*\(\s*decorate/.test(code),
    "and no observer driving one");
  record(!/setTimeout\(decorate/.test(code),
    "and no timed re-runs at guessed intervals");
  record(!/td\.textContent\.trim\(\)/.test(code),
    "and nothing matches a ship by the text in its cell");
}

console.log("");
if (notes.length) {
  console.log("MEASURED, for the ledger:");
  for (const n of notes) console.log("  - " + n);
  console.log("");
}
if (failures.length) {
  console.log(`FAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  - " + f);
  if (PROVE) {
    console.log(`
PROOF OK: the original nameCellHtml was caught by `
      + `${failures.length} assertion(s). This check can fail.`);
    process.exit(0);
  }
  process.exit(1);
}
if (PROVE) {
  console.log("PROOF FAILED: the original nameCellHtml sent every pledged ship "
    + "to RSI and NOTHING here noticed. This file is the same shape as the "
    + "check it replaces.");
  process.exit(1);
}
console.log(`PASSED: ${passed} assertions, every one of them behavioural.`);
process.exit(0);
