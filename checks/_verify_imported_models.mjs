/**
 * RULE16: INDEPENDENT - geometry is measured in a real browser through the
 * site's own viewer, and the decisive control is a valid GLB with no meshes
 * SYNTHESISED HERE - a file the build has never produced and cannot have
 * agreed with.
 *
 * M5e - THE IMPORTED SHIPS RENDER SOMETHING, AND THE CHECK CAN TELL WHEN ONE
 *       DOES NOT.
 *
 * ORDER: docs/ORDER_the-fifteen-are-not-missing-2026-08-27.md, M5e:
 *   "A check that fails if any of the eleven renders an empty scene. THE
 *    CONTROL: it must also fail when pointed at one of the three not-found
 *    ships. A check that passes on a ship with no model is not checking
 *    anything."
 *
 * THE CONTROL AS WRITTEN COULD NOT BE RUN, AND THAT IS SAID RATHER THAN
 * QUIETLY SUBSTITUTED.
 * The three not-found ships - Command Module, Power Suit, Vanduul Mauler - are
 * NOT ROWS ON THIS SITE AT ALL. There is no page and no model URL to point at.
 * The order was written before that was known.
 *
 * What replaces it is stricter than what was asked for, because the interesting
 * failure is not a missing file:
 *
 *   CONTROL 1 - a model URL that 404s. The harness must report empty.
 *   CONTROL 2 - a VALID GLB carrying a scene with no meshes, synthesised here
 *               and served from this harness. It fetches 200, it parses, the
 *               loader succeeds, and it renders NOTHING. This is the real
 *               silent-success shape: a broken import produces exactly this,
 *               and a check that only looks for a 404 sails straight past it.
 *
 * If either control comes back "renders geometry", this file goes red.
 *
 * WHY IT LOADS MODEL URLS RATHER THAN SHIP PAGES.
 * Not every imported ship has a loadout bench (Arrastra does not) and not every
 * one is in the holo page's hardpoint-driven list. Driving the ship pages would
 * silently skip those, which is the failure mode this whole file exists to
 * avoid. So it uses the SITE'S OWN VIEWER - the real CCViewer, real three.js,
 * real Draco loader, in a real browser - and points it at each model URL.
 *
 * WHAT "EMPTY" MEANS HERE, MEASURED RATHER THAN ASSUMED.
 * A model renders when the loaded root exists, carries at least one Mesh, those
 * meshes carry a non-zero vertex count, and the bounding box has real extent.
 * A root that loaded as an empty group, or as a mesh with zero vertices, is an
 * empty scene however successfully it fetched.
 *
 * Usage: node checks/_verify_imported_models.mjs [--only Ship,Ship]
 */
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
const MANIFEST = join(ROOT, "data-layer", "derived", "model-availability",
                      "import_manifest.json");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

const EMPTY_GLB_PATH = "/__control_valid_but_empty.glb";
const MISSING_PATH = "/models/__control_this_model_does_not_exist.glb";

/** A structurally valid GLB: one scene, one node, no meshes. Parses fine. */
function emptyGlb() {
  const doc = { asset: { version: "2.0", generator: "citizen-compass M5e control" },
                scene: 0, scenes: [{ nodes: [0] }], nodes: [{ name: "empty" }] };
  let js = Buffer.from(JSON.stringify(doc), "utf8");
  if (js.length % 4) js = Buffer.concat([js, Buffer.alloc(4 - (js.length % 4), 0x20)]);
  const head = Buffer.alloc(12);
  head.write("glTF", 0, "ascii");
  head.writeUInt32LE(2, 4);
  head.writeUInt32LE(12 + 8 + js.length, 8);
  const ch = Buffer.alloc(8);
  ch.writeUInt32LE(js.length, 0);
  ch.write("JSON", 4, "ascii");
  return Buffer.concat([head, ch, js]);
}

const argv = process.argv.slice(2);
const onlyArg = argv.indexOf("--only");
const only = onlyArg >= 0 ? new Set(argv[onlyArg + 1].split(",").map(s => s.trim())) : null;

if (!existsSync(MANIFEST)) {
  console.error(`NOT PERFORMED: ${MANIFEST} does not exist, so there is no list of `
    + `imported ships to check. Run the M5 import first. Reporting this as not `
    + `performed rather than as a pass.`);
  process.exit(1);
}
const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));
let ships = manifest.ships;
if (only) ships = ships.filter(s => only.has(s.ship));
if (!ships.length) {
  console.error("NOT PERFORMED: no ships selected.");
  process.exit(1);
}

const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".glb": "model/gltf-binary", ".png": "image/png",
  ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ico": "image/x-icon",
};
const server = createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  if (rel === EMPTY_GLB_PATH) {
    const b = emptyGlb();
    res.writeHead(200, { "content-type": "model/gltf-binary" });
    return res.end(b);
  }
  const p = join(DEPLOY, rel);
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
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto(`${base}/loadout.html`, { waitUntil: "networkidle" });
await page.waitForFunction(() => typeof _view !== "undefined" || typeof view === "function",
                           null, { timeout: 25000 });
await page.evaluate(() => { if (typeof view === "function") view(); });
await page.waitForFunction(() => typeof _view !== "undefined" && _view !== null,
                           null, { timeout: 25000 });
await page.waitForTimeout(500);

const draco = await page.evaluate(() => CCViewer.hasDraco());
console.log("==================================================================");
console.log("M5e - THE IMPORTED MODELS RENDER, AND EMPTY IS STILL DETECTED");
console.log(`the site's own viewer, real browser.  DRACO wired: ${draco}`);
console.log("==================================================================");
if (!draco) {
  console.log("\n  NOT PERFORMED: the viewer reports no DRACO decoder, and every");
  console.log("  file here is Draco-compressed. Nothing would load, and a red");
  console.log("  result would mean the harness, not the models.");
  await browser.close(); server.close();
  process.exit(1);
}

/** Load one URL through the real viewer and measure what reached the scene. */
async function measure(url) {
  return await page.evaluate(async (u) => {
    const outcome = await new Promise((res) => {
      let done = false;
      const finish = (o) => { if (!done) { done = true; res(o); } };
      setTimeout(() => finish({ timeout: true }), 45000);
      _view.load(u, { onLoad: () => finish({ loaded: true }),
                      onError: (e) => finish({ error: String(e && e.message || e) }) });
    });
    const v = _view;
    if (!v || !v.current) return Object.assign(outcome, { meshes: 0, verts: 0, extent: 0 });
    let meshes = 0, verts = 0;
    v.current.traverse(o => {
      if (o.isMesh && o.geometry) {
        meshes++;
        const pos = o.geometry.attributes && o.geometry.attributes.position;
        if (pos) verts += pos.count;
      }
    });
    const box = new THREE.Box3().setFromObject(v.current);
    const s = box.getSize(new THREE.Vector3());
    return Object.assign(outcome,
      { meshes, verts, extent: Math.max(s.x, s.y, s.z) || 0 });
  }, url);
}

console.log(`\n1. the ${ships.length} imported model(s) must render geometry`);
for (const s of ships) {
  const url = `${base}/models/${encodeURIComponent(s.deploy_name)}`;
  const m = await measure(url);
  const detail = `${String(m.meshes).padStart(3)} mesh ${String(m.verts).padStart(9)} verts `
               + `extent ${Number(m.extent).toFixed(2)}`
               + (m.error ? `  LOADER ERROR: ${m.error}` : "")
               + (m.timeout ? "  TIMED OUT" : "");
  check(m.meshes > 0 && m.verts > 0 && m.extent > 0,
        `${s.ship.padEnd(30)} ${detail}`,
        (m.meshes > 0 && m.verts > 0) ? "" : "EMPTY SCENE");
}

console.log("\n2. THE CONTROLS - these must be seen as empty");
console.log("   (the three not-found ships the order named are not rows on this");
console.log("    site at all, so these stand in - see the header of this file)");

const c1 = await measure(`${base}${MISSING_PATH}`);
check(c1.meshes === 0 && c1.verts === 0,
      `a model URL that 404s renders nothing  (${c1.error ? "loader errored, as expected" : "no error raised"})`,
      `meshes=${c1.meshes} verts=${c1.verts} - the harness reported geometry for a file that does not exist`);

const c2 = await measure(`${base}${EMPTY_GLB_PATH}`);
check(c2.loaded === true,
      "a valid-but-empty GLB LOADS successfully - the interesting case",
      `outcome=${JSON.stringify(c2)}`);
check(c2.meshes === 0 && c2.verts === 0,
      "and it is still reported as an empty scene",
      `meshes=${c2.meshes} verts=${c2.verts} - THIS IS THE SILENT SUCCESS. A file `
      + `that parses and renders nothing was counted as a rendering ship.`);

/* And having proved it can see empty, prove it has not simply gone blind:
   re-load a real model and confirm the same harness reports geometry again. */
const back = await measure(`${base}/models/${encodeURIComponent(ships[0].deploy_name)}`);
check(back.meshes > 0 && back.verts > 0,
      `and it still sees geometry afterwards (${ships[0].ship} re-loaded)`,
      `meshes=${back.meshes} verts=${back.verts}`);

await browser.close();
server.close();

console.log("\n==================================================================");
if (failures.length) {
  console.log(`${failures.length} failed`);
  for (const f of failures) console.log(`  - ${f}`);
  console.log("RED.");
  process.exit(1);
}
console.log("GREEN - every imported model renders, and both controls were seen "
  + "as empty.");
process.exit(0);
