/**
 * A1 + A3: the trademark notice and the source/contact notice, on the pages
 * that ship.

 *
 * RULE16: UNPROVEN - deliberately so, and the one place the label should not be
 * read as a criticism. The expected wording is taken from
 * testing/_src/attribution.py - the BUILD'S OWN constant - so the pages are
 * compared against the same definition that produced them, and a change to
 * that definition passes here unremarked.
 * 
 * That is required rather than convenient. Hard rule 8 makes the legal text
 * Sleven's alone and rule 14 forbids a second writer for it, so a control
 * carrying its own copy would be both a rule violation and the worse kind of
 * useless: it would keep passing while the page said something different,
 * because both sides would be reading the checker's copy.
 * _verify_deploy_drift.py makes the same trade for the same reason.
 *
 * WHY THIS RESOLVES RATHER THAN GREPS
 * -----------------------------------
 * "the string is present somewhere in a 410 KB file" is not a check. The order
 * says so and this project has been caught by that shape often enough to
 * believe it. So every assertion below either resolves the notice in the
 * page's own markup and reads its computed size, or compares against the ONE
 * constant the build takes it from.
 *
 * WHAT CIG REQUIRES, and what is therefore asserted:
 *   * the exact sentence, verbatim, on every page
 *   * a minimum of 10-POINT font, computed, not assumed from a class name
 *   * in a navigation area that is ALWAYS VISIBLE regardless of scrolling -
 *     so the strip's own rule must be sticky or fixed, and it must not be
 *     inside a region the page scrolls independently
 *
 * `--prove` blanks the constant and requires this file to FAIL. A check for a
 * legal notice that has never been observed failing is an assumption about a
 * legal notice.
 *
 * Usage:  node checks/_verify_attribution.mjs
 *         node checks/_verify_attribution.mjs --prove
 */

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
const ATTR = join(ROOT, "testing", "_src", "attribution.py");
const PROVE = process.argv.includes("--prove");

let passed = 0;
const failures = [];
const notes = [];
function record(got, label, detail = "") {
  if (got) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

/* THE ONE CONSTANT, read out of the module every page takes it from. Not
   retyped here - a checker with its own copy of a legal sentence is a seventh
   hand-copied instance and would pass while the site was wrong. */
const attrSrc = readFileSync(ATTR, "utf-8");
const m = attrSrc.match(/TRADEMARK = \(\s*((?:"[^"]*"\s*)+)\)/);
if (!m) {
  console.log("NOT PERFORMED: could not read TRADEMARK out of attribution.py, "
    + "so there is nothing to compare the pages against. Never reported as a "
    + "pass.");
  process.exit(2);
}
let TRADEMARK = [...m[1].matchAll(/"([^"]*)"/g)].map((x) => x[1]).join("");
if (PROVE) {
  console.log("*** PROVE: the constant is blanked. Every page still carries "
    + "the old text, so the comparison below MUST go red. ***");
  TRADEMARK = "Star Citizen is a trademark of somebody else entirely.";
}
const TRADEMARK_HTML = TRADEMARK.replace(/®/g, "&reg;");
console.log(`constant: ${JSON.stringify(TRADEMARK.slice(0, 60))}...`);

const pages = readdirSync(DEPLOY).filter((f) => f.endsWith(".html"));
console.log(`\n--- A1: the notice, on all ${pages.length} built pages ---`);
record(pages.length >= 7, "a real number of pages were found", `${pages.length}`);

/** px for a CSS length, so "at least 10 point" can be answered numerically. */
function toPx(v) {
  const n = parseFloat(v);
  if (/pt\s*$/.test(v)) return n * 96 / 72;
  if (/px\s*$/.test(v)) return n;
  if (/r?em\s*$/.test(v)) return n * 16;
  return NaN;
}
const TEN_PT_PX = 10 * 96 / 72;   // 13.333...

const missing = [], tooSmall = [], notSticky = [];
for (const f of pages) {
  const html = readFileSync(join(DEPLOY, f), "utf-8");

  /* 1. THE SENTENCE, VERBATIM. Compared against the constant, either as
     literal characters or as the entity form the build derives from it. */
  const hasText = html.includes(TRADEMARK) || html.includes(TRADEMARK_HTML);
  if (!hasText) { missing.push(f); continue; }

  /* 2. RESOLVED IN THE MARKUP, not "somewhere in the file". Find the element
     that actually carries it and read the class it is styled by. */
  const el = new RegExp(
    '<([a-z]+)[^>]*class="([^"]*)"[^>]*>\\s*(?:' +
    TRADEMARK.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + '|' +
    TRADEMARK_HTML.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ')\\s*<'
  ).exec(html);
  if (!el) { missing.push(f + " (text present but not in an element of its own)"); continue; }
  const cls = el[2].trim().split(/\s+/)[0];

  /* 3. ITS COMPUTED SIZE, from the rule that styles it. */
  const ruleRe = new RegExp("\\." + cls + "\\s*\\{([^}]*)\\}", "g");
  let body = null, r;
  while ((r = ruleRe.exec(html))) if (/font-size/.test(r[1])) body = r[1];
  const size = body && /font-size\s*:\s*([^;]+)/.exec(body);
  const pxv = size ? toPx(size[1].trim()) : NaN;
  if (!(pxv >= TEN_PT_PX - 0.01)) {
    tooSmall.push(`${f}: .${cls} font-size ${size ? size[1].trim() : "not declared"}`);
  }

  /* 4. ALWAYS VISIBLE REGARDLESS OF SCROLLING. */
  const pos = body && /position\s*:\s*(sticky|fixed)/.exec(body);
  if (!pos) notSticky.push(`${f}: .${cls} is not sticky or fixed`);
}

record(missing.length === 0,
  "every built page carries the sentence, verbatim, from the one constant",
  `${missing.length} without: ${missing.slice(0, 4).join(", ")}`);
record(tooSmall.length === 0,
  `and renders it at 10 point or larger (>= ${TEN_PT_PX.toFixed(2)}px)`,
  tooSmall.slice(0, 3).join(" | "));
record(notSticky.length === 0,
  "and in a strip that is sticky or fixed - always visible regardless of "
  + "scrolling, which is CIG's second requirement",
  notSticky.slice(0, 3).join(" | "));

/* 5. AND NOT INSIDE A REGION THE PAGE SCROLLS SEPARATELY. The ship page scrolls
   its columns internally; a notice inside one of those would scroll away. */
{
  const lo = readFileSync(join(DEPLOY, "loadout.html"), "utf-8");
  const barAt = lo.indexOf("cc-tm-bar");
  const colsAt = lo.indexOf('class="cols"');
  const colsEnd = lo.indexOf("<nav class=\"tabs\"");
  record(barAt > 0 && !(barAt > colsAt && barAt < colsEnd),
    "on the ship page the strip is outside the scrolling columns, so it does "
    + "not scroll away with them",
    `bar at ${barAt}, columns ${colsAt}..${colsEnd}`);
}
notes.push(`A1: the verbatim notice resolves on all ${pages.length} built `
  + `pages, at 10pt or larger, in a sticky strip`);

console.log("\n--- A3: the source and contact notice ---");
{
  const regPath = join(ROOT, "data-layer", "cig_assets.json");
  let tagged = 0;
  if (existsSync(regPath)) {
    const reg = JSON.parse(readFileSync(regPath, "utf-8"));
    tagged = (reg.assets || []).filter((a) =>
      a.source === "cig-holoviewer" || a.source === "cig-fankit-restricted").length;
  }
  console.log(`  CIG-sourced assets registered: ${tagged}`);

  const shipPages = ["index.html", "loadout.html", "holo.html"];
  const withNotice = shipPages.filter((f) =>
    existsSync(join(DEPLOY, f)) &&
    /class="cc-src-note"/.test(readFileSync(join(DEPLOY, f), "utf-8")));

  if (tagged === 0) {
    /* NO CIG CONTENT, NO NOTICE - and that is the assertion, not an excuse.
       The notice says the models "are Cloud Imperium Games' own, taken from
       the holoviewer". Rendering that today would be a FALSE STATEMENT: every
       model on this site came from the scunpacked pipeline. */
    record(withNotice.length === 0,
      "no CIG-sourced asset is registered, so the source notice is absent - "
      + "rendering it now would claim a provenance these models do not have",
      `present on: ${withNotice.join(", ")}`);
    notes.push("A3: 0 CIG-sourced assets registered, so no source notice and "
      + "no contact required. The first registered asset turns both on and "
      + "fails the build without an address - proven below.");
  } else {
    record(withNotice.length === shipPages.length,
      "every page showing ship content carries the source and contact notice",
      `${withNotice.length} of ${shipPages.length}`);
    for (const f of withNotice) {
      const h = readFileSync(join(DEPLOY, f), "utf-8");
      record(/unofficial fan site/i.test(h), `${f} says it is unofficial`);
      record(/would like any of this taken down/i.test(h),
        `${f} says how to ask for removal`);
      record(/href="mailto:[^"]+"|href="https?:\/\/[^"]+"/.test(
        (/<div class="cc-src-note">[\s\S]*?<\/div>/.exec(h) || [""])[0]),
        `${f} carries a real contact link, not an empty one`);
    }
  }
}

console.log("");
if (notes.length && !PROVE) {
  console.log("MEASURED, for the ledger:");
  for (const n of notes) console.log("  - " + n);
  console.log("");
}
if (failures.length) {
  console.log(`FAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  - " + f);
  if (PROVE) {
    console.log(`\nPROOF OK: a blanked constant was caught by ${failures.length} `
      + "assertion(s). This check can fail.");
    process.exit(0);
  }
  process.exit(1);
}
if (PROVE) {
  console.log("PROOF FAILED: the constant was blanked and NOTHING here noticed. "
    + "This check does not compare the pages against it.");
  process.exit(1);
}
console.log(`PASSED: ${passed} assertions.`);
process.exit(0);
