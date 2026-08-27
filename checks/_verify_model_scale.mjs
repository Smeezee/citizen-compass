/**
 * RULE16: UNPROVEN - for the 19 Fleetyards imports the MODEL and the
 * PUBLISHED DIMENSIONS both come from the same Fleetyards record, so this
 * can only show that source agreeing with itself - if Fleetyards is wrong
 * about a ship's length, the model is scaled to that wrong length and this
 * reports ratio 1.000. It is genuinely independent for the 12 pre-existing
 * ships, whose geometry is ours and whose target is not. An independent
 * source would be CIG's own published dimensions or an in-game measurement,
 * and neither was used.
 *
 * THE IMPORTED SHIPS ARE THE SIZE THEY SAY THEY ARE.
 *
 * WHY THIS EXISTS
 * ===============
 * On 2026-08-27 nineteen models were imported and fifteen landed at the wrong
 * size - a Pitbull 0.001 m across, a Tyilui at 0.007, an Odin at 0.07 - while
 * every model already here was correct. Nothing caught it. The build was green,
 * the render check was green, and the ships LOOKED right on screen, because the
 * viewer frames the camera to whatever it is given. A hull three orders of
 * magnitude too small is invisible to every check that only asks "did something
 * render".
 *
 * So this asks the question none of them did: IS IT THE RIGHT SIZE.
 *
 * THE RULE
 * --------
 * A model's largest real dimension must equal the ship's largest published
 * dimension, within 2%. Both sides are axis-independent, because the imported
 * models do not share the length-along-Z convention the existing fleet uses and
 * a check that assumed one would fail 19 ships for being turned around.
 *
 * The published figures come from the same Fleetyards record the model came
 * from, so there is no join to get wrong.
 *
 * THE CONTROL, WHICH IS A REAL KNOWN-BAD INPUT AND NOT A SIMULATED ONE (rule 12)
 * -----------------------------------------------------------------------------
 *   node checks/_verify_model_scale.mjs --control-old
 *
 * serves the PRE-FIX files - the actual wrong-size models, kept under
 * _to_delete (this repo deletes nothing) - and every assertion below must
 * go red against them. Not a mutated byte, not a
 * planted value: the genuine defect this file was written to catch, fed back in.
 *
 * If --control-old comes back GREEN, this check does not work and the pass on
 * the real files means nothing.
 *
 * Usage:
 *   node checks/_verify_model_scale.mjs
 *   node checks/_verify_model_scale.mjs --control-old
 */
import { createServer } from "node:http";
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
const AVAIL = join(ROOT, "data-layer", "derived", "model-availability");
const REPORT = join(AVAIL, "scale_fix_report.json");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

const TOLERANCE = 0.02;
const controlOld = process.argv.includes("--control-old");

/* EVERY REPORT, NOT THE FIRST ONE.
   The scale rule has been applied to two populations on two runs - the 19
   Fleetyards imports, then the 12 pre-existing models the fleet audit caught -
   and each run writes its own report. Reading only `scale_fix_report.json`
   would have checked the 19 and left the 12 unverified while still printing
   GREEN, which is the shape of pass this file exists to refuse. */
const reports = readdirSync(AVAIL)
  .filter(f => f.startsWith("scale_fix_report") && f.endsWith(".json"))
  .sort();
if (!reports.length) {
  console.error(`NOT PERFORMED: no scale_fix_report*.json in ${AVAIL}. Run `
    + `scripts/fix_model_scale.py first. Reporting this as not performed `
    + `rather than as a pass.`);
  process.exit(1);
}
const seen = new Set();
const report = { ships: [] };
for (const f of reports) {
  const r = JSON.parse(readFileSync(join(AVAIL, f), "utf8"));
  for (const s of r.ships || []) {
    if (seen.has(s.deploy_name)) continue;   // a later run supersedes an earlier
    seen.add(s.deploy_name);
    report.ships.push(s);
  }
}
console.log(`reading ${reports.length} report(s): ${reports.join(", ")}`);

/* Where the pre-fix models were moved aside to. Newest attic wins. */
let attic = null;
if (controlOld) {
  const base = join(ROOT, "_to_delete");
  const dirs = existsSync(base)
    ? readdirSync(base).filter(d => d.startsWith("pre_scale_fix_")).sort()
    : [];
  if (!dirs.length) {
    console.error("NOT PERFORMED: no _to_delete/pre_scale_fix_* directory, so "
      + "there are no known-bad files to run the control against. The control "
      + "cannot be faked, so this is reported as not performed.");
    process.exit(1);
  }
  attic = join(base, dirs[dirs.length - 1], "models");
  console.log(`CONTROL MODE: serving the pre-fix models from `
    + `${attic.replace(ROOT, ".")}\nEvery assertion below MUST go red.`);
}

const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".glb": "model/gltf-binary", ".png": "image/png",
  ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ico": "image/x-icon",
};
const served = new Set();
const server = createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  let p = join(DEPLOY, rel);
  if (attic && rel.startsWith("/models/")) {
    const alt = join(attic, rel.slice("/models/".length));
    if (existsSync(alt)) { p = alt; served.add(rel); }
  }
  if (!existsSync(p) || p.endsWith("/")) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
  res.end(readFileSync(p));
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const failures = [];
function check(cond, label, detail) {
  if (cond) { console.log(`  ok   ${label}`); return true; }
  console.log(`  FAIL ${label}${detail ? "  " + detail : ""}`);
  failures.push(label + (detail ? "  " + detail : ""));
  return false;
}

const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1024, height: 700 } });
await page.goto(`${base}/loadout.html`, { waitUntil: "networkidle" });
await page.evaluate(() => { if (typeof view === "function") view(); });
await page.waitForFunction(() => typeof _view !== "undefined" && _view !== null,
                           null, { timeout: 25000 });
await page.waitForTimeout(400);

async function extentOf(file) {
  return await page.evaluate(async (u) => {
    await new Promise((res) => {
      let d = false; const fin = () => { if (!d) { d = true; res(); } };
      setTimeout(fin, 60000);
      _view.load(u, { onLoad: fin, onError: fin });
    });
    if (!_view.current) return null;
    const b = new THREE.Box3().setFromObject(_view.current);
    const s = b.getSize(new THREE.Vector3());
    return { max: Math.max(s.x, s.y, s.z), x: s.x, y: s.y, z: s.z };
  }, `${base}/models/${encodeURIComponent(file)}`);
}

console.log("==================================================================");
console.log("MODEL SCALE - the ships are the size they say they are");
console.log(`rule: largest model dimension == largest published dimension, +/-${TOLERANCE * 100}%`);
console.log("==================================================================\n");

for (const s of report.ships) {
  const m = await extentOf(s.deploy_name);
  if (!m) { check(false, `${s.ship}: nothing loaded`); continue; }
  const ratio = m.max / s.target_max;
  check(Math.abs(ratio - 1) <= TOLERANCE,
        `${s.ship.padEnd(28)} ${m.max.toFixed(2).padStart(9)} m  `
        + `wanted ${s.target_max.toFixed(2).padStart(8)} m   ratio ${ratio.toFixed(3)}`,
        `OUT OF BAND`);
}

await browser.close();
server.close();

console.log("\n==================================================================");
if (controlOld) {
  console.log(`control served ${served.size} pre-fix model(s) in place of the live ones`);
  if (!served.size) {
    console.log("THE CONTROL SERVED NOTHING - it tested the live files, not the "
      + "known-bad ones. Reporting as not performed.");
    process.exit(1);
  }
  if (failures.length) {
    console.log(`${failures.length} failed against the known-bad files, which is `
      + `what the control is for.`);
    console.log("CONTROL PASSED: this check can detect a wrong-size model.");
    process.exit(0);
  }
  console.log("CONTROL FAILED: the pre-fix models passed. This check does not "
    + "work, and its green result on the live files means nothing.");
  process.exit(3);
}
if (failures.length) {
  console.log(`${failures.length} failed`);
  for (const f of failures) console.log(`  - ${f}`);
  console.log("RED.");
  process.exit(1);
}
console.log("GREEN - every imported ship is the size its own record says it is.");
process.exit(0);
