/**
 * H4 / R8: the page says what it can prove, and not more.
 *
 * H4 is the one item in the 2026-08-20 order where the WORDING is the
 * deliverable, so it gets a control of its own rather than three assertions
 * bolted onto a functional suite.
 *
 * THE CONTROL THE ORDER NAMES:
 *   "no wording on the page states or implies a price is measured from the
 *    game."
 *
 * WHY A SCANNER AND NOT A HUMAN READ. A human read passes once, on the day
 * somebody does it. This runs on every build, so the sentence somebody adds
 * next month is scanned too - which is the only way a wording rule survives
 * contact with a page that keeps being edited.
 *
 * AND THE SCANNER IS PROVEN AGAINST KNOWN-BAD TEXT. Every forbidden pattern is
 * run against a sentence that MUST trip it before it is trusted against the
 * real page. A wording checker whose patterns never matched anything would
 * report a clean page forever, which is exactly the shape of silent success
 * this project has logged five times. If a pattern stops matching its own
 * example, this exits non-zero and says which one.
 *
 * WHAT IT DOES NOT DO, stated rather than implied: it cannot judge a sentence
 * it has no pattern for. It catches the claims we know are wrong to make. A
 * genuinely novel overclaim would pass, and the answer to that is to add a
 * pattern here when one is found - not to pretend this is comprehension.
 *
 * --self-test inverts every expectation and must exit non-zero.
 *
 * Usage:  node checks/_verify_find_wording.mjs [--self-test]
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEPLOY = join(HERE, "..", "testing", "_deploy");
const SELFTEST = process.argv.includes("--self-test");

let passed = 0;
const failures = [];
function record(got, label, detail = "") {
  const want = SELFTEST ? !got : got;
  if (want) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

// ---------------------------------------------------------------------------
// THE CLAIMS THIS PAGE MAY NOT MAKE.
//
// Each carries the sentence that must trip it. The example is not decoration:
// it is what makes the pattern testable, and a pattern with no working example
// is a pattern nobody has checked.
// ---------------------------------------------------------------------------
const FORBIDDEN = [
  { why: "says a figure is read out of the game",
    re: /\b(read|taken|pulled|extracted)\s+(straight\s+|directly\s+)?(out of|from)\s+the\s+game\b/i,
    bad: "Prices are read straight out of the game." },
  { why: "says a figure was measured in the game",
    re: /\bmeasured\s+(from|in|off)\s+the\s+game\b/i,
    bad: "Every price is measured from the game." },
  { why: "calls a price official",
    re: /\bofficial\s+price/i,
    bad: "This is the official price at Port Olisar." },
  { why: "calls a price confirmed or verified",
    re: /\b(confirmed|verified)\s+price/i,
    bad: "A confirmed price of 4,000 aUEC." },
  { why: "says flatly that this IS the price",
    re: /\bis\s+the\s+(current\s+)?price\b/i,
    bad: "3,200 aUEC is the price." },
  { why: "calls the data live or real-time",
    re: /\b(live|real[- ]?time|up[- ]to[- ]the[- ]minute)\s+(price|data|figures)/i,
    bad: "Live prices, updated in real-time." },
  { why: "claims accuracy or guarantees",
    re: /\b(guaranteed|accurate to|always accurate|never wrong)\b/i,
    bad: "Guaranteed accurate to the last aUEC." },
  { why: "presents a blended or averaged figure as a price",
    re: /\b(average|averaged|blended|mean)\s+price\b/i,
    bad: "The average price across all shops is 2,900 aUEC." },
  { why: "says the data comes from CIG or Star Citizen itself",
    re: /\b(from|according to)\s+(CIG|Cloud Imperium|the game files)\b/i,
    bad: "Prices from CIG's own data." },
];

// Sentences the page MUST carry. The negative half alone would be satisfied by
// a page that said nothing at all.
const REQUIRED = [
  { why: "states the provable claim in the order's own words",
    re: /UEX reported this price at this terminal in the snapshot taken/i },
  { why: "says plainly that players are the source",
    re: /Star Citizen does not publish its prices\.\s*Players do\./i },
  { why: "says UEX rates the submissions",
    re: /UEX rates how much it trusts each submission/i },
  { why: "refuses the bigger claim in as many words",
    re: /Not "this is the price"/i },
  { why: "says a row can be out of date or wrong",
    re: /A row can be out of date\. A row can be wrong\./i },
  { why: "says nothing here is read out of the game",
    re: /Nothing here is read out of the game/i },
];

// A negated mention is not a claim. The page SAYS "nothing here is read out of
// the game", and a scanner that failed the page for saying so would be
// pushing it toward saying less, which is the opposite of H4.
const NEGATIONS = [
  /nothing here is read out of the game/gi,
  /not\s+read\s+out\s+of\s+the\s+game/gi,
  /does not publish its prices/gi,
  /Not "this is the price"/gi,
];

function scan(text) {
  let stripped = text;
  for (const n of NEGATIONS) stripped = stripped.replace(n, " ");
  return FORBIDDEN.filter(f => f.re.test(stripped));
}

// ---------------------------------------------------------------------------
// FIRST: prove the scanner can fail. Before it is pointed at the real page.
// ---------------------------------------------------------------------------
console.log("--- THE SCANNER, PROVEN AGAINST KNOWN-BAD TEXT ---");
for (const f of FORBIDDEN) {
  const hits = scan(f.bad);
  record(hits.length > 0 && hits.some(h => h.why === f.why),
    `catches: "${f.bad}"`,
    `pattern for "${f.why}" did not match its own example`);
}
const cleanControl = "UEX reported this price at this terminal in the snapshot "
  + "taken 2026-08-01. Nothing here is read out of the game.";
record(scan(cleanControl).length === 0,
  "and does NOT trip on the honest sentence it is meant to allow",
  JSON.stringify(scan(cleanControl).map(h => h.why)));

// ---------------------------------------------------------------------------
// THEN: the real page.
// ---------------------------------------------------------------------------
const html = readFileSync(join(DEPLOY, "find.html"), "utf-8");
const dataJs = readFileSync(join(DEPLOY, "find_data.gen.js"), "utf-8");

let currentHash = "";
const view = { innerHTML: "" };
const qBox = { value: "", onkeydown: null, focus() {}, selectionStart: 0 };
const sandbox = {
  console, URLSearchParams, Date, Number, Math, String, Array, Object, Map, Set,
  JSON, RegExp, Error, isNaN, parseInt, parseFloat,
  encodeURIComponent, decodeURIComponent,
  addEventListener() {}, scrollTo() {},
  location: { get hash() { return currentHash; }, set hash(v) { currentHash = v; },
              search: "" },
  document: {
    activeElement: null,
    querySelector: s => (s === "#view" ? view : s === "#q" ? qBox : null),
    getElementById: id => (id === "view" ? view : id === "q" ? qBox : null),
  },
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(dataJs, sandbox, { filename: "find_data.gen.js" });
vm.runInContext(html.match(/<script>([\s\S]*)<\/script>/)[1], sandbox,
  { filename: "find.html:script" });

function render(hash) {
  currentHash = "#" + hash;
  view.innerHTML = "";
  sandbox.route();
  return view.innerHTML;
}

// The VISIBLE words - tags and attributes removed, so a class name or a URL
// cannot trip a check about English, and a phrase hidden in an attribute
// cannot dodge one.
const visible = h => h.replace(/<[^>]*>/g, " ")
                      .replace(/&[a-z]+;/g, " ")
                      .replace(/\s+/g, " ");

const ROUTES = [
  ["the home page", ""],
  ["a search results page", "s/omnisky"],
  ["an item page with prices", "i/item:1"],
  ["a terminal page", "p/111"],
  ["an empty search", "s/zzzz_no_such_item_zzzz"],
];

console.log("\n--- H4's NAMED CONTROL: nothing implies a price is from the game ---");
const rendered = {};
for (const [label, hash] of ROUTES) {
  const words = visible(render(hash));
  rendered[hash] = words;
  const hits = scan(words);
  record(hits.length === 0, `${label} makes no forbidden claim`,
    hits.map(h => h.why).join("; "));
}

// The page's own source, comments and all. A comment is not shown to a
// visitor, but a comment asserting the wrong thing is how the next author
// learns the wrong thing.
console.log("\n--- and neither does the page source, comments included ---");
// Comment leaders stripped and whitespace collapsed FIRST. A block comment
// wraps sentences across lines with " * " in the middle of them, and without
// this the scanner reads "Nothing here is / read out of the game" as two
// fragments: the negation does not match, the forbidden pattern does, and the
// page fails for containing exactly the sentence H4 asked it to contain.
// Collapsing can only make a pattern MORE likely to match, never less, so this
// cannot hide a real claim.
const flatSource = html.replace(/^\s*\*\s?/gm, " ").replace(/\s+/g, " ");
const sourceHits = scan(flatSource);
record(sourceHits.length === 0, "the whole find.html source is clean",
  sourceHits.map(h => h.why).join("; "));
// And the flattener is proven, so it cannot be the thing that made this pass:
// a forbidden sentence planted with a comment leader through its middle must
// still be caught.
const planted = "Prices are read\n * straight out of the game.";
record(scan(planted.replace(/^\s*\*\s?/gm, " ").replace(/\s+/g, " ")).length > 0,
  "and a forbidden sentence wrapped across comment lines is still caught");

console.log("\n--- what the page MUST say, and where ---");
const itemPage = rendered["i/item:1"];
for (const r of REQUIRED) {
  record(r.re.test(itemPage), `the item page ${r.why}`);
}
record(REQUIRED.every(r => r.re.test(rendered["p/111"])),
  "and so does a terminal page - the caveat is not only on one route");
record(REQUIRED.slice(0, 3).every(r => r.re.test(rendered[""])),
  "and the home page carries it before a visitor searches for anything");

console.log("\n--- R6: the date is on every row, not once at the top ---");
const itemHtml = render("i/item:1");
const rows = (itemHtml.match(/<tr class=/g) || []).length;
const dated = (itemHtml.match(/UEX reported this in the snapshot taken/g) || []).length;
record(rows > 0 && dated === rows,
  `all ${rows} price rows carry their own snapshot date`, `${dated} dated`);

console.log("\n--- the caveat is ABOVE the table, not below it ---");
// A caveat somebody has to scroll past the numbers to reach was written to be
// skipped. This is a positional assertion because position is the point.
const caveatAt = itemHtml.indexOf("Where these numbers come from");
const tableAt = itemHtml.indexOf("<table>");
record(caveatAt >= 0, "the caveat is on the item page");
record(tableAt >= 0, "so is the price table");
record(caveatAt >= 0 && tableAt >= 0 && caveatAt < tableAt,
  "and the caveat comes first", `caveat at ${caveatAt}, table at ${tableAt}`);

console.log("\n" + "=".repeat(62));
if (SELFTEST) {
  console.log("--self-test: expectations were inverted, so a non-zero exit is");
  console.log("the correct outcome.");
}
if (failures.length) {
  console.log(`FAILED ${failures.length} of ${passed + failures.length}:`);
  failures.forEach(f => console.log("  -", f));
  process.exit(1);
}
console.log(`All ${passed} assertions passed.`);
console.log("NOT PROVEN HERE: that no OTHER overclaim exists. This catches the");
console.log("claims we know are wrong to make; a novel one would pass, and the");
console.log("answer to that is a new pattern here, not a claim of comprehension.");
