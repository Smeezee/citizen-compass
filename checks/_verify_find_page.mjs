/**
 * E1/E3/E4 acceptance for testing/_deploy/find.html, driven against a REAL API.
 *
 * No browser is available on this machine and nothing was installed to get one
 * (rule 7 - downloaded code is data, not something to run). So instead of a
 * reimplementation of the page, this loads THE PAGE'S OWN SCRIPT, verbatim,
 * out of find.html, gives it the handful of browser globals it touches
 * (document / location / fetch / addEventListener), and calls its real view
 * functions against the running API.
 *
 * That is weaker than a browser in one specific way, stated plainly rather
 * than glossed: it proves the page's LOGIC and the HTML it generates, and it
 * does NOT prove layout, CSS, or that a browser's CORS enforcement is
 * satisfied. The CORS headers are checked separately, over real HTTP, in
 * checks/_verify_shop_api.py's sibling run - see the ledger.
 *
 * What it does prove, which is what E1/E3/E4 actually ask for:
 *   - the invented-data block is gone and nothing references it
 *   - real rows come back and are rendered
 *   - buy and sell land in SEPARATE columns (E3)
 *   - every price row shows its snapshot and its age, and unverified data is
 *     visibly flagged (E4)
 *   - a search matching nothing produces an honest empty state, not a spinner
 *     and not filler (the E control)
 *   - an unreachable API produces a visible failure, not a hang
 *
 * Usage:  node checks/_verify_find_page.mjs [apiBase]
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const PAGE = join(HERE, "..", "testing", "_deploy", "find.html");
const API = process.argv[2] || "http://127.0.0.1:8077";

let passed = 0;
const failures = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

const html = readFileSync(PAGE, "utf-8");

// ---------------------------------------------------------------- static
console.log("--- E1: the invented data is gone ---");
record(!/const LOC\s*=/.test(html), "the invented LOC table is gone");
record(!/const SHOP\s*=/.test(html), "the invented SHOP table is gone");
record(!/const ITEM\s*=/.test(html), "the invented ITEM table is gone");
record(!/Seventeen invented items/.test(html),
  "the 'seventeen invented items' explainer is gone");
record(/api\/v1\/shop/.test(html), "the page calls /api/v1/shop");

console.log("\n--- E2: the banner and the legal text are UNTOUCHED ---");
record(/MOCKUP — prices and shops are invented/.test(html),
  "the MOCKUP banner is still present, because the deployed API is not "
  + "confirmed (E2)");
record(/Cloud Imperium Rights LLC/.test(html),
  "the trademark footer is intact (rule 8 - never edited)");
record(/unofficial Star Citizen fan site/.test(html),
  "the Fan Kit disclaimer is intact (rule 8)");

// ------------------------------------------------------- load the real JS
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

let currentHash = "";
const view = { innerHTML: "" };
const qBox = { value: "", onkeydown: null };

const sandbox = {
  console,
  fetch,
  URLSearchParams,
  Date,
  Number,
  Math,
  String,
  encodeURIComponent,
  decodeURIComponent,
  isNaN,
  addEventListener() {},
  scrollTo() {},
  location: { get hash() { return currentHash; }, set hash(v) { currentHash = v; }, search: `?api=${API}` },
  document: {
    querySelector: (s) => (s === "#view" ? view : s === "#q" ? qBox : null),
    getElementById: (id) => (id === "view" ? view : id === "q" ? qBox : null),
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(script, sandbox, { filename: "find.html:script" });
record(typeof sandbox.route === "function", "the page's own script loaded and exposes route()");

async function render(hash) {
  // The leading "#" matters: route() does location.hash.slice(1), because a
  // real browser hash always carries it. Without it every route fell through
  // to home() and the first version of this control "passed" the search test
  // only because the home page's hint text happens to contain the word
  // "Omnisky". A control that green-lights the wrong page is worse than none.
  currentHash = "#" + hash;
  view.innerHTML = "";
  await sandbox.route();
  return view.innerHTML;
}

function reload(apiBase) {
  // A FRESH context. Re-running the script in the same one throws on the
  // const API_BASE redeclaration, which is a harness bug rather than a page
  // bug - the page is only ever loaded once in a browser.
  const fresh = { ...sandbox, location: { ...sandbox.location, search: `?api=${apiBase}` } };
  fresh.window = fresh;
  fresh.globalThis = fresh;
  vm.createContext(fresh);
  vm.runInContext(script, fresh, { filename: "find.html:script(reload)" });
  return fresh;
}

// -------------------------------------------------------------- live runs
console.log("\n--- E1: real rows come back and render ---");
const health = await fetch(`${API}/health`).then(r => r.ok).catch(() => false);
if (!health) {
  console.log(`  FAIL the API at ${API} is not answering - cannot verify`);
  process.exit(1);
}

const search = await render("s/omnisky");
record(/Omnisky/.test(search), "a search for 'omnisky' renders real item names");
record(/result/.test(search), "and states how many results there were");
record(!/invented/i.test(search.replace(/<!--[\s\S]*?-->/g, "")),
  "and the word 'invented' appears nowhere in the rendered output");

const item = await render("i/item:1");
record(/Omnisky III Cannon/.test(item), "an item page renders the real item");
record(/aUEC/.test(item), "with real prices in aUEC");

console.log("\n--- E3: buy and sell are SEPARATE columns ---");
record(/<th>Buy<\/th>/.test(item) && /<th>Sell<\/th>/.test(item),
  "the price table has a Buy column AND a Sell column");
record(!/average|blended|avg/i.test(item),
  "and no averaged or blended figure appears anywhere on the page");
// A row where one side has no data must render blank, never 0.
record(/—<span class="conf"> no data<\/span>/.test(item),
  "a missing side renders as a blank marked 'no data', not as 0",
  "no blank cell was produced - check an item with a one-sided price");
record(!/>0<\/span>/.test(item), "and no price cell contains a bare 0");

console.log("\n--- E4: provenance and the unverified flag ---");
record(/snapshot 20260801T235530Z/.test(item),
  "every price row names the snapshot it came from");
record(/reported /.test(item), "and how old the underlying report is");
record(/not verified against a patch/.test(item),
  "unverified data is VISIBLY FLAGGED rather than shown as though confirmed");

console.log("\n--- D3 via the page: a terminal renders its stock ---");
const terminal = await render("p/111");
record(/Ship Weapons/.test(terminal), "the terminal page renders the real terminal");
record(/<th>Buy<\/th>/.test(terminal) && /<th>Sell<\/th>/.test(terminal),
  "with buy and sell separate here too");
record(/Orison, Crusader, Stanton/.test(terminal),
  "and a resolved location with no 'None' in it");
record(!/None/.test(terminal.replace(/no data/g, "")),
  "no literal 'None' anywhere in the rendered terminal page");

console.log("\n--- THE CONTROL: a search matching nothing ---");
const empty = await render("s/zzzz_no_such_item_zzzz");
record(/Nothing matched/.test(empty), "shows an honest empty state");
record(!/Looking…/.test(empty), "and is NOT left on the loading placeholder");
record(!/aUEC/.test(empty), "and invents no filler rows");

console.log("\n--- THE OTHER CONTROL: an unreachable API ---");
// A dead port. The page must SAY so - the failure this guards against is a
// spinner that never resolves, which looks identical to a slow network.
const offlineSandbox = reload("http://127.0.0.1:9");
currentHash = "#s/omnisky";
view.innerHTML = "";
await offlineSandbox.route();
const offline = view.innerHTML;
record(/can't reach the price data/.test(offline),
  "an unreachable API produces a visible, explained failure");
record(!/Looking…/.test(offline), "and not a spinner left running forever");

console.log("\n" + "=".repeat(62));
if (failures.length) {
  console.log(`FAILED ${failures.length} of ${passed + failures.length}:`);
  failures.forEach(f => console.log("  -", f));
  process.exit(1);
}
console.log(`All ${passed} assertions passed against ${API}.`);
console.log("NOT PROVEN HERE (stated rather than implied): browser layout, CSS,");
console.log("and real browser CORS enforcement. No browser is available on this");
console.log("machine and none was installed to get one.");
