/**
 * RULE16: UNPROVEN - the expected defaults are read from CCViewer.HOLO - the
 * module under test - so a wrong DEFAULT_COLOUR would be asserted against
 * itself and pass. What IS independent is the behaviour: the discard, the
 * re-stamp and the survival are driven through real localStorage in a real
 * browser, and both mutations are planted in the served bytes.
 *
 * P4e / P4f - THE APPEARANCE REVISION, IN BOTH DIRECTIONS.
 *
 * ORDER: docs/ORDER_the-panel-will-not-close-2026-08-27.md, P4e and P4f,
 * assigned to Code by docs/ORDER_the-split-2026-08-27.md.
 *
 * WHAT P3 BUILT, AND WHY IT NEEDS TWO CHECKS RATHER THAN ONE.
 * H1f-2 made the saved appearance permanent on Sleven's own instruction -
 * "as long as possible... I'd hate to have to come in after a couple of days
 * and have to redo it". P3b then had to let a CHANGED DEFAULT reach somebody
 * who already has a save, without throwing away settings people chose.
 *
 * Those two requirements pull in opposite directions, and a check on either
 * one alone is satisfied by code that fails the other:
 *
 *   - Discard nothing, ever   -> P4f passes. P4e fails. This is the bug P3
 *                                existed to fix: Sleven's cyan overwriting
 *                                every retune at boot for weeks.
 *   - Discard everything, always -> P4e passes. P4f fails, and H1f-2's
 *                                permanence is quietly dead while the suite
 *                                stays green.
 *
 * THE SECOND ONE IS WHY P4f IS LOAD-BEARING and is written here as a real
 * assertion rather than a comment.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT (rule 12). Each mutation is planted in the
 * bytes the browser parses, and each must make this exit non-zero:
 *
 *   --mutate-norev        the rev comparison forced false, so a pre-revision
 *                         blob restores intact. P4e MUST go red. If it does
 *                         not, this file is not testing the discard.
 *   --mutate-alwaysreset  the rev comparison forced true, so every load
 *                         discards. P4f MUST go red. If it does not, this
 *                         file would accept the "discard everything always"
 *                         implementation that destroys permanence.
 *
 * A mutation whose pattern is not found in the served bytes reports
 * MUTATION DID NOT APPLY and exits non-zero, rather than running a check that
 * silently tested nothing.
 *
 * Usage: node checks/_verify_settings_revision.mjs [--mutate-...]
 */
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

const SHIP = "arrow";
const PAGE = `loadout.html?cc=${SHIP}#${SHIP}`;

/* The one line P3b turns on. Both mutations rewrite it, in opposite
   directions, and neither is allowed to miss quietly. */
const REV_TEST = "saved.rev !== CC_HOLO.REV";

const MUTATORS = {
  "--mutate-norev": {
    file: "cc_viewer.js",
    from: REV_TEST,
    to: "false /* MUTATED: rev comparison removed */",
    breaks: "P4e",
  },
  "--mutate-alwaysreset": {
    file: "cc_viewer.js",
    from: REV_TEST,
    to: "true /* MUTATED: every load discards */",
    breaks: "P4f",
  },
};

const argv = process.argv.slice(2);
const unknown = argv.filter((a) => !(a in MUTATORS));
if (unknown.length) {
  console.error(`UNKNOWN MUTATOR ${unknown.join(", ")}`);
  process.exit(2);
}
const mutation = argv.length ? MUTATORS[argv[0]] : null;
if (argv.length > 1) {
  console.error("One mutation at a time. Two at once cannot be attributed.");
  process.exit(2);
}

/* ------------------------------------------------------------------ server */
const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".glb": "model/gltf-binary", ".png": "image/png",
  ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ico": "image/x-icon",
};
let mutationApplied = false;

const server = createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  const p = join(DEPLOY, rel);
  if (!existsSync(p) || p.endsWith("/")) { res.writeHead(404); return res.end(); }
  let body = readFileSync(p);
  if (mutation && rel.replace(/^\//, "") === mutation.file) {
    const text = body.toString("utf8");
    if (text.includes(mutation.from)) {
      mutationApplied = true;
      body = Buffer.from(text.split(mutation.from).join(mutation.to), "utf8");
    }
  }
  res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
  res.end(body);
});

const failures = [];
const notes = [];
function check(cond, label, detail) {
  if (cond) { console.log(`  ok   ${label}`); return true; }
  console.log(`  FAIL ${label}${detail ? " " + detail : ""}`);
  failures.push(label + (detail ? " " + detail : ""));
  return false;
}
function notPerformed(why) {
  console.log(`\n  NOT PERFORMED: ${why}`);
  console.log("  Reporting this as not performed rather than as a pass.");
  failures.push(`not performed: ${why}`);
}

const hex = (n) => (typeof n === "number" ? "0x" + n.toString(16) : String(n));

await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const pageErrors = [];
page.on("pageerror", (e) => pageErrors.push(String(e)));

/* NAVIGATE, NOT goto-the-same-URL. `loadout.html?cc=arrow#arrow` differs from
   the current URL only by its hash, and Chromium treats that as a SAME-DOCUMENT
   navigation: no reload, no fresh viewer, no second read of storage. A first
   draft of this file did exactly that and every assertion below reported the
   state of the FIRST load, which is a check that cannot see what it is testing.
   page.reload() forces the document to be built again. */
async function loadAndSettle(fresh) {
  if (fresh) await page.reload({ waitUntil: "networkidle" });
  else await page.goto(`${base}/${PAGE}`, { waitUntil: "networkidle" });
  try {
    await page.waitForFunction(
      () => typeof _view !== "undefined" && _view !== null, null,
      { timeout: 20000 });
  } catch { return false; }
  await page.waitForTimeout(400);
  return true;
}

/** Seed the store, then reload so the viewer reads the seed on construction. */
async function seedAndReload(blob) {
  await page.evaluate((b) => localStorage.setItem("ccHolo", JSON.stringify(b)), blob);
  return loadAndSettle(true);
}

const stateOf = () => page.evaluate(() => {
  let stored = null;
  try { stored = JSON.parse(localStorage.getItem("ccHolo") || "null"); } catch (e) {}
  return {
    style: (typeof _view !== "undefined" && _view) ? _view.style : null,
    colour: (typeof _view !== "undefined" && _view) ? _view._colour : null,
    REV: CCViewer.HOLO.REV,
    DEFAULT: CCViewer.HOLO.DEFAULT,
    DEFAULT_COLOUR: CCViewer.HOLO.DEFAULT_COLOUR,
    lineInt: CCViewer.HOLO.lineInt,
    wasReset: !!CCViewer.HOLO.wasReset,
    stored,
  };
});

console.log("==================================================================");
console.log("P4e / P4f - THE APPEARANCE REVISION");
if (mutation) console.log(`MUTATION ACTIVE: ${argv[0]} - ${mutation.breaks} must go red`);
console.log("==================================================================");

if (!(await loadAndSettle())) {
  notPerformed("the viewer never initialised on " + PAGE + ", so no appearance "
    + "was ever restored. Nothing was asserted.");
  await browser.close(); server.close();
  process.exit(1);
}

if (mutation && !mutationApplied) {
  console.error(`\nMUTATION DID NOT APPLY: "${mutation.from}" was not found in `
    + `${mutation.file} as served. The pattern has drifted from the source. `
    + `Say so - do not adjust the source to suit the check.`);
  await browser.close(); server.close();
  process.exit(2);
}

const first = await stateOf();
const REV = first.REV;
const AMBER = first.DEFAULT_COLOUR;
const CYAN = 0x5fd8ee;                       // COLOURS[0], and not the default
console.log(`\nthis build: REV=${REV}  DEFAULT=${first.DEFAULT}  `
  + `DEFAULT_COLOUR=${hex(AMBER)}`);

/* ---- P4e. A pre-revision save loses its appearance and gets stamped ---- */
console.log("\nP4e. a stale save does not survive a revision bump");
/* The shape named in the order: a real pre-P3 blob. No rev, because nothing
   ever wrote one. 24041966 is not one of COLOURS - a save can hold any colour
   the picker offered, and the discard must not depend on recognising it. */
const STALE = { style: "solidlines", colour: 24041966, lineInt: 1.0 };
if (!(await seedAndReload(STALE))) {
  notPerformed("the viewer did not initialise after seeding the stale blob");
} else {
  const s = await stateOf();
  check(s.style === s.DEFAULT,
    "the retired style was discarded, the default won",
    `style=${s.style}, wanted ${s.DEFAULT}`);
  check(s.colour === AMBER,
    "the saved colour was discarded, amber won",
    `colour=${hex(s.colour)}, wanted ${hex(AMBER)}`);
  check(s.lineInt !== STALE.lineInt,
    "the stale lineInt did not carry over",
    `lineInt=${s.lineInt}, the stale blob held ${STALE.lineInt}`);
  check(s.stored && s.stored.rev === REV,
    "the blob was re-stamped at the current REV",
    `stored=${JSON.stringify(s.stored)}`);
  check(s.stored && s.stored.style === undefined && s.stored.colour === undefined,
    "the discarded appearance keys are gone from storage, not just ignored",
    `stored=${JSON.stringify(s.stored)}`);
  check(s.wasReset === true,
    "the viewer recorded that it reset, so P3d has something to say");
}

/* ---- P4f. THE LOAD-BEARING ONE. A current save survives. ---- */
console.log("\nP4f. a current save DOES survive - permanence, per H1f-2");
if (!(await seedAndReload({ rev: REV, colour: CYAN }))) {
  notPerformed("the viewer did not initialise after seeding the current blob");
} else {
  const s = await stateOf();
  check(s.colour === CYAN,
    "the saved non-default colour survived the load",
    `colour=${hex(s.colour)}, wanted ${hex(CYAN)}`);
  check(s.colour !== AMBER,
    "and it is NOT the default - a check that cannot tell these apart is not a check",
    `colour=${hex(s.colour)}, default=${hex(AMBER)}`);
  check(s.stored && s.stored.colour === CYAN && s.stored.rev === REV,
    "storage still holds it after the load",
    `stored=${JSON.stringify(s.stored)}`);
  check(s.wasReset === false,
    "and nothing was reset this time",
    `wasReset=${s.wasReset}`);
}

/* ---- the second half of P4f: it must survive a SECOND load too ---- */
console.log("\nP4f-2. and it is still there on the next page load");
if (!(await loadAndSettle())) {
  notPerformed("the viewer did not initialise on the second load");
} else {
  const s = await stateOf();
  check(s.colour === CYAN,
    "still the saved colour after a reload with no reseeding",
    `colour=${hex(s.colour)}, wanted ${hex(CYAN)}`);
}

console.log("");
check(pageErrors.length === 0, "no uncaught page errors",
  pageErrors.slice(0, 2).join(" | "));

await browser.close();
server.close();

console.log("==================================================================");
const passed = "see above";
if (failures.length) {
  console.log(`${failures.length} failed`);
  for (const f of failures) console.log(`  - ${f}`);
  console.log(mutation ? "RED, which is what the mutation is for." : "RED.");
  process.exit(1);
}
console.log("GREEN.");
if (mutation) {
  console.error(`\nBUT A MUTATION WAS ACTIVE (${argv[0]}) AND EVERYTHING PASSED.`);
  console.error(`${mutation.breaks} was supposed to go red. This check is not `
    + `testing what it claims to test.`);
  process.exit(3);
}
process.exit(0);
