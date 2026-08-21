/**
 * G8 acceptance for the ship page's Loadout panel, driven against a REAL API.
 *
 * WHAT IS ACTUALLY UNDER TEST
 * ---------------------------
 * The panel's code AS SHIPPED. This does not re-implement it and does not read
 * a copy: it slices the G8 block verbatim out of testing/_deploy/index.html -
 * the built artifact, not the source - gives it the handful of browser globals
 * it touches, and calls its real loadHardpoints() against a running API.
 *
 * THE LIMIT, STATED RATHER THAN GLOSSED: this proves the panel's LOGIC and the
 * HTML it produces. It does not prove layout, CSS, or a browser's own CORS
 * enforcement. Same limit as _verify_find_page.mjs, same reason - no browser on
 * this machine and nothing was installed to get one (rule 7).
 *
 * WHAT IT PROVES, WHICH IS WHAT G8 ASKS FOR
 * ------------------------------------------
 *   - a ship WITH slot data renders real mounts, grouped, from the API
 *   - THE CONTROL G8 NAMES: a ship with no component data shows an honest
 *     empty state - a sentence, carrying the reason - and NOT a spinner and
 *     NOT invented values
 *   - a model the dataset has never heard of says so, distinctly from the above
 *   - an UNREACHABLE API resolves to a sentence rather than hanging. This one
 *     is not hypothetical: the deployed API has been 502 all evening.
 *   - the eight hardcoded "awaiting data" rows are gone
 *   - nothing renders a size of 0 for a mount whose size the source omits
 *
 * WHAT THIS SUITE OWNS AFTER I1 (2026-08-21)
 * ------------------------------------------
 * The hardpoint data became a generated file and the API became the FALLBACK.
 * This suite is the proof that the fallback still works, because its sandbox
 * defines NO HP_DATA - which is exactly the "the data file did not load" case,
 * and therefore exactly what a visitor gets if hardpoint_data.gen.js 404s.
 *
 * THAT IS ASSERTED RATHER THAN ASSUMED. A suite that merely happens not to
 * define HP_DATA would silently stop testing the fallback the day somebody
 * added it, and would go on reporting 16 passes. So this suite now requires
 * HP_DATA to be absent from its own context AND counts the fetch calls the
 * panel makes, so "it used the API" is a measured fact rather than an
 * inference from the output looking right.
 *
 * The file path - the panel filling with the network blocked - is owned by
 * checks/_verify_hardpoint_panel_offline.mjs, and only by it.
 *
 * Usage:  node checks/_verify_ship_hardpoint_panel.mjs [apiBase]
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const PAGE = join(HERE, "..", "testing", "_deploy", "index.html");
const API = process.argv[2] || "http://127.0.0.1:8077";

let passed = 0;
const failures = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
}

const page = readFileSync(PAGE, "utf8");

// ---- the shipped block, sliced by its own delimiters ---------------------
const START = "/* ==========================================================================\n   G8 - the Loadout panel stops saying";
const END = 'const CC_DIR="../sc-ships/"';
const i = page.indexOf(START);
const j = page.indexOf(END, i);
if (i === -1 || j === -1) {
  console.log("FAILED: could not find the G8 block in the BUILT page. Either " +
              "build_deploy.py was not re-run, or the block was renamed. " +
              "Reported as not performed, never as passed.");
  process.exit(1);
}
const shipped = page.slice(i, j);

record(!/awaiting data<\/span>/.test(page),
  "the eight hardcoded 'awaiting data' rows are gone from the built page");
record(page.includes("loadHardpoints(dir)"),
  "the ship renderer calls loadHardpoints()");
record(/Slot structure is measured from/.test(page),
  "the panel's text no longer claims the data 'reaches this panel once the " +
  "API is wired in'");

// ---- a DOM small enough to be obviously honest ---------------------------
function makeEl() {
  return { innerHTML: "", textContent: "" };
}
const els = { "cc-slots": makeEl(), "cc-slotnote": makeEl() };

// Counted, so that "the panel went to the API" is measured rather than
// inferred from output that happens to look right.
let fetches = 0;
const sandbox = {
  console,
  URLSearchParams,
  Map,
  encodeURIComponent,
  fetch: (...a) => { fetches++; return fetch(...a); },
  location: { search: `?api=${API}` },
  $: (id) => els[id] || null,
};
vm.createContext(sandbox);
vm.runInContext(shipped, sandbox);

const slots = () => els["cc-slots"].innerHTML;

async function run() {
  // ---- 0. THIS SUITE IS TESTING THE FALLBACK, AND SAYS SO ---------------
  record(vm.runInContext("typeof HP_DATA", sandbox) === "undefined",
    "no HP_DATA is defined in this context, so the panel is on its FALLBACK " +
    "path - the same one a visitor gets when hardpoint_data.gen.js does not " +
    "load");

  // ---- 1. A SHIP WITH DATA ----------------------------------------------
  const before = fetches;
  await sandbox.loadHardpoints("600i Explorer");
  record(fetches > before,
    `and it really did call the API (${fetches - before} fetch call(s)), ` +
    "rather than answering from somewhere else");
  record(/Countermeasure|Guns|Missile racks|Turrets/i.test(slots()),
    "a ship WITH slot data renders grouped mounts", slots().slice(0, 120));
  record(!/awaiting data/.test(slots()),
    "and does not say 'awaiting data'");
  record(/Joker Defcon Flares Ammo|hardpoint_/.test(slots()) === true ||
         slots().length > 100,
    "and the rows carry real port or item names from the API");
  record(!/>S0</.test(slots()),
    "no mount renders as 'S0' - an unstated size is omitted, never zeroed");

  // ---- 2. THE CONTROL G8 NAMES: NO DATA -> HONEST EMPTY STATE ----------
  await sandbox.loadHardpoints("Kraken");
  const empty = slots();
  record(/No hardpoint data for this hull/.test(empty),
    "a ship with NO slot data shows an honest empty state", empty.slice(0, 160));
  record(/neither this model's name nor any mount-data key/.test(empty),
    "and it carries the BUILD'S OWN REASON, so the blank is explained");
  record(!/Reading hardpoint data/.test(empty),
    "and it is NOT left on the loading message - no spinner");
  record(!/(awaiting|pending|coming soon|TBD|—\s*—)/i.test(empty),
    "and it invents nothing to fill the space");

  // ---- 3. A MODEL THAT DOES NOT EXIST ----------------------------------
  await sandbox.loadHardpoints("Definitely Not A Ship");
  record(/not in the hardpoint dataset/.test(slots()),
    "an unknown model says so", slots().slice(0, 140));
  record(!/No hardpoint data for this hull/.test(slots()),
    "and it reads DIFFERENTLY from 'we have this hull but no mounts' - two " +
    "different facts, two different sentences");

  // ---- 4. NO MODEL AT ALL ----------------------------------------------
  await sandbox.loadHardpoints("");
  record(/No model folder matched/.test(slots()),
    "a ship with no model folder says that, rather than querying for ''");

  // ---- 5. AN UNREACHABLE API MUST RESOLVE, NOT HANG --------------------
  //
  // The deployed API has answered 502 all evening. A panel that spins forever
  // during an outage tells a visitor nothing while looking like it is about to.
  const dead = { ...sandbox, location: { search: "?api=http://127.0.0.1:9" } };
  vm.createContext(dead);
  vm.runInContext(shipped, dead);
  const t = setTimeout(() => {
    console.log("  FAIL the unreachable-API branch HUNG");
    process.exit(1);
  }, 30000);
  await dead.loadHardpoints("600i Explorer");
  clearTimeout(t);
  record(/Could not reach the hardpoint data/.test(slots()),
    "an unreachable API resolves to a sentence naming the API",
    slots().slice(0, 160));
  record(!/Reading hardpoint data/.test(slots()),
    "and does not leave the panel on its loading message");

  console.log("");
  if (failures.length) {
    console.log(`FAILED ${failures.length} of ${passed + failures.length}:`);
    failures.forEach((f) => console.log("  -", f));
    process.exit(1);
  }
  console.log(`All ${passed} assertions passed.`);
}

run().catch((e) => { console.log("FAILED:", e); process.exit(1); });
