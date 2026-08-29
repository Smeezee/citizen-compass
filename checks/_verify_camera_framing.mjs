/**
 * F3 - THE FIRST CONTROL IN THIS REPO THAT SEES WHAT A VISITOR SEES.

 *
 * RULE16: INDEPENDENT - it serves the real payload over HTTP and drives a real
 * browser, then measures the framing from what was actually drawn. Every
 * other viewer control loads cc_viewer.js into a Node vm against a stub;
 * this one does not ask the viewer anything, it looks at the result. A
 * framing bug that the viewer reports as correct is exactly what this
 * catches and the vm-based controls cannot.
 *
 * Every other viewer control loads cc_viewer.js into a Node `vm` against a stub
 * THREE. Those stubs have no real PerspectiveCamera, no matrixWorldInverse, no
 * OrbitControls - and their stub camera ALWAYS LOOKS AT ITS TARGET, which is
 * exactly the behaviour the page was missing. So on 2026-08-26, twenty-three
 * assertions across 239 hulls stayed green while every ship page on the site
 * rendered black, framed at 826x-897x the hull's own bounding radius.
 *
 * A CONTROL THAT CANNOT SEE WHAT A VISITOR SEES IS NOT A CONTROL OVER WHAT A
 * VISITOR SEES. That is the standing rule the browser was approved for, in
 * docs/DECISION_the-checks-get-a-real-browser-2026-08-26.md.
 *
 * WHAT THIS DOES. Serves the BUILT testing/_deploy over a local static server,
 * loads the real loadout page in a real headless Chromium, waits for the real
 * GLB to decode through DRACO into a real WebGL scene, and then reads two
 * numbers off the live viewer:
 *
 *     camera.position.distanceTo(controls.target)
 *     the loaded hull's bounding radius
 *
 * and asserts the ratio lands in the band. Nothing is stubbed. Nothing is
 * modelled. If the page is dark, this goes red.
 *
 * THE BAND IS 1.8 TO 6.0 AND IT IS SET AGAINST WHAT SHIPPED. F1+F2+A1 measure
 * 2.00-3.01 across all 239 hulls, median 2.35. The band is deliberately NOT
 * narrowed to hug that: a band tight enough to fail on a legitimate reframe is
 * a band somebody widens in a hurry at the wrong moment. It still fails hard on
 * the 850x runaway and on the Asgard's 412x.
 *
 * NOT the table in ORDER_the-camera-never-looked-at-the-ship - those figures
 * were measured with F1 only and are mislabelled "after both".
 *
 * PROVEN AGAINST KNOWN-BAD INPUT. The server can serve a MUTATED cc_viewer.js,
 * so the defect is planted in the bytes the browser actually parses:
 *   --mutate-nolookat   F1 undone - the camera never aims.
 *   --mutate-behind     V1 undone - the camera goes back to +Z, behind the tail.
 *   --mutate-noplanes   A1 undone - the fit depends on boot()'s clip planes.
 * The first and third must go red. --mutate-behind is a FRAMING-NEUTRAL defect
 * and is asserted differently; see section 3.
 *
 * IF THE BROWSER CANNOT RENDER, THIS REPORTS NOT PERFORMED AND EXITS NON-ZERO.
 * It never reports a pass it did not measure.
 *
 * Usage: node checks/_verify_camera_framing.mjs [--mutate-...] [--hulls N]
 */
import { createServer } from "node:http";
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
const GEO = join(ROOT, "data-layer", "derived", "hull-geometry");

process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

const LO = 1.8, HI = 6.0;
const argv = process.argv.slice(2);
const MUT = argv.find((a) => a.startsWith("--mutate-")) || "";
const N_ARG = argv.indexOf("--hulls");
const WANT_N = N_ARG >= 0 ? Number(argv[N_ARG + 1]) : 10;

const MUTATIONS = {
  "--mutate-nolookat": [/\n\s*this\.camera\.lookAt\(target\);/, "\n"],
  "--mutate-behind": [/ty \+ d \* 0\.42, -d \* 0\.85\)/, "ty + d * 0.42, d * 0.85)"],
  "--mutate-noplanes": [
    /this\.camera\.near = Math\.max\(\(_dist - _reach\) \* 0\.5, _dist \* 1e-4, 1e-6\);\s*\n\s*this\.camera\.far = \(_dist \+ _reach\) \* 2 \+ 1;/,
    ""],
};
if (MUT && !MUTATIONS[MUT]) {
  console.log(`UNKNOWN MUTATOR ${MUT}`);
  process.exit(2);
}

let passed = 0;
const failures = [];
function check(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); console.log(`  FAIL ${label} ${detail}`); }
  return ok;
}
function notPerformed(why) {
  console.log("\n" + "=".repeat(66));
  console.log("NOT PERFORMED - and that is reported, not passed over.");
  console.log(why);
  console.log("=".repeat(66));
  process.exit(2);
}

/* ------------------------------------------------ the sample, and it is real */
if (!existsSync(DEPLOY)) notPerformed(`no built payload at ${DEPLOY}`);
const modelsDir = join(DEPLOY, "models");
if (!existsSync(modelsDir)) notPerformed(`no models in ${modelsDir}`);

const MODELS = JSON.parse(
  readFileSync(join(DEPLOY, "loadout_model.gen.js"), "utf-8")
    .match(/=\s*(\{[\s\S]*?\});/)[1]);
const SHIPS = JSON.parse(
  readFileSync(join(DEPLOY, "loadout_data.gen.js"), "utf-8")
    .match(/LOADOUT_SHIPS\s*=\s*(\{[\s\S]*?\});/)[1]);

/* A SPREAD, NOT THE FIRST TEN ALPHABETICALLY. The defect this exists to catch
   scaled with hull size, so the sample has to span the fleet's size range -
   and the two hulls that broke differently (the Asgard's units, the Javelin's
   length) are named explicitly rather than left to chance. */
const NAMED = ["ANVL_Asgard", "AEGS_Vanguard_Harbinger", "RSI_Polaris",
               "ANVL_Carrack", "DRAK_Cutlass_Black", "AEGS_Gladius",
               "DRAK_Vulture", "ORIG_300i", "AEGS_Retaliator",
               "MISC_Freelancer", "AEGS_Javelin", "AEGS_Avenger_Stalker"];
const sample = NAMED.filter((k) => MODELS[k]
  && existsSync(join(modelsDir, MODELS[k]))).slice(0, WANT_N);
if (sample.length < 4) notPerformed(
  `only ${sample.length} of the named hulls have a built model - the sample `
  + `would not be representative, so nothing is claimed`);

/* --------------------------------------------------------- the static server */
const TYPES = { ".html": "text/html", ".js": "text/javascript",
                ".json": "application/json", ".glb": "model/gltf-binary",
                ".wasm": "application/wasm", ".css": "text/css",
                ".png": "image/png", ".webp": "image/webp",
                ".woff2": "font/woff2", ".ttf": "font/ttf" };
const server = createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  if (p === "/") p = "/index.html";
  const f = join(DEPLOY, p.replace(/^\/+/, ""));
  if (!f.startsWith(DEPLOY) || !existsSync(f)) { res.writeHead(404); res.end(); return; }
  let body = readFileSync(f);
  /* THE MUTATION IS PLANTED IN THE BYTES THE BROWSER PARSES, not in a copy of
     the module loaded somewhere else. That is what makes this a control over
     the deployed artifact rather than over a rehearsal of it. */
  if (MUT && p.endsWith("/cc_viewer.js")) {
    const [re, rep] = MUTATIONS[MUT];
    const before = body.toString("utf-8");
    const after = before.replace(re, rep);
    if (after === before) {
      console.log(`MUTATION DID NOT APPLY - ${MUT} matched nothing in the `
        + `served cc_viewer.js, so this run would have proven nothing.`);
      process.exit(2);
    }
    body = Buffer.from(after, "utf-8");
  }
  res.writeHead(200, { "Content-Type": TYPES[extname(f)] || "application/octet-stream" });
  res.end(body);
});

async function main() {
  let chromium;
  try { ({ chromium } = await import("playwright")); }
  catch (e) {
    notPerformed("playwright is not installed under checks/. Run:\n"
      + "  cd checks && npm install && npm run install-browser");
  }

  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const port = server.address().port;
  const base = `http://127.0.0.1:${port}`;

  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ["--use-gl=angle", "--use-angle=swiftshader",
             "--enable-unsafe-swiftshader", "--disable-gpu-sandbox"],
    });
  } catch (e) {
    server.close();
    notPerformed("headless Chromium would not launch: " + e.message
      + "\nInstall it with:  cd checks && npm run install-browser");
  }

  console.log("=".repeat(66));
  console.log("F3 - the camera framing, measured in a real browser");
  console.log(MUT ? `*** MUTATED: ${MUT} ***` : "clean build");
  console.log(`serving ${DEPLOY}`);
  console.log(`band ${LO} - ${HI}, ${sample.length} hulls`);
  console.log("=".repeat(66));

  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(String(e.message || e)));

  /* WEBGL FIRST, BEFORE ANY MEASUREMENT. A browser that cannot make a context
     would fail every hull below and it would look like a framing defect. */
  await page.goto(`${base}/loadout.html?cc=webglprobe`,
                  { waitUntil: "domcontentloaded" });
  const gl = await page.evaluate(() => {
    try {
      const c = document.createElement("canvas");
      const g = c.getContext("webgl2") || c.getContext("webgl");
      return !!g;
    } catch (e) { return false; }
  });
  if (!gl) {
    await browser.close(); server.close();
    notPerformed("this Chromium has no WebGL context, so nothing about the "
      + "rendered page can be measured here. Reporting that rather than a pass.");
  }
  console.log("  webgl: yes\n");

  /* --mutate-noplanes HAS A PRECONDITION, AND IT IS NO LONGER MET.
     A1 stops the fit depending on boot()'s clip planes. That only CHANGES an
     outcome for a hull whose opening camera distance already exceeds boot()'s
     far plane of 10,000 - which, until this morning, was the Asgard at 11,851
     because its model was in centimetres. A3 rescaled it, so as of now no hull
     in the fleet triggers the branch A1 defends.

     So this mutation is INERT ON CURRENT DATA. The honest report is NOT
     PERFORMED with the reason, not a pass - a mutation that cannot fail proves
     nothing, and saying "caught" or "clean" about it would be a claim nobody
     measured. A2's beyondFar counter is the standing evidence that the branch
     stays unreached; see checks/_verify_camera_framing's section 2 and the
     fleet sweep in the A1 proof. */
  if (MUT === "--mutate-noplanes") {
    const FOV = 42, BOOT_FAR = 10000;
    let worst = 0, worstName = "";
    for (const cls of sample) {
      const g = join(GEO, MODELS[cls].replace(/\.glb$/, "") + ".json");
      if (!existsSync(g)) continue;
      const d = JSON.parse(readFileSync(g, "utf-8"));
      if (!d.min || !d.max) continue;
      const sz = [0, 1, 2].map((i) => d.max[i] - d.min[i]);
      const maxAxis = Math.max(...sz);
      const dd = maxAxis / (2 * Math.tan((FOV / 2) * Math.PI / 180)) * 1.55;
      const open = dd * Math.sqrt(0.75 * 0.75 + 0.42 * 0.42 + 0.85 * 0.85);
      if (open > worst) { worst = open; worstName = cls; }
    }
    if (worst <= BOOT_FAR) {
      await browser.close(); server.close();
      notPerformed(
        `--mutate-noplanes is INERT on the current fleet and this run proves
`
        + `nothing either way.

`
        + `A1 only changes an outcome when a hull's opening camera distance
`
        + `exceeds boot()'s far plane of ${BOOT_FAR}. The largest in this sample
`
        + `is ${worstName} at ${worst.toFixed(0)}. The Asgard used to open at
`
        + `11,851 because its model was in centimetres; A3 rescaled it, which
`
        + `removed the only hull that reached the branch A1 defends.

`
        + `A1 is a guard against a CLASS of defect - any asset arriving outside
`
        + `the size range boot() assumes - not against one ship. It is still
`
        + `right, and A2's beyondFar counter is what watches the branch. But
`
        + `this mutator cannot demonstrate it today, and reporting a pass would
`
        + `be exactly the silent success this file exists to prevent.`);
    }
  }

  const rows = [];
  for (const cls of sample) {
    /* A CHANGING QUERY STRING, AND IT IS LOAD-BEARING. Navigating between two
       URLs that differ only by their HASH is a SAME-DOCUMENT navigation: the
       browser does not reload and the page script never re-runs, so shipId
       keeps whatever the previous visit left it on. The first version of this
       control did exactly that and reported four hulls with byte-identical
       distance and radius - a pass measuring one ship four times. The query
       parameter forces a real document load per hull. */
    await page.goto(`${base}/loadout.html?cc=${encodeURIComponent(cls)}#${cls}`,
                    { waitUntil: "domcontentloaded" });
    /* Wait for the REAL model: _view.current is set only after the GLB has
       decoded and been added to the scene. */
    let ready = true;
    try {
      await page.waitForFunction(
        () => typeof _view !== "undefined" && _view && _view.current
              && _view.camera && _view.controls,
        null, { timeout: 45000 });
    } catch (e) { ready = false; }
    if (!ready) {
      rows.push({ cls, err: "model never arrived within 45s" });
      continue;
    }
    const m = await page.evaluate(() => {
      const b = new THREE.Box3().setFromObject(_view.current);
      const s = b.getSize(new THREE.Vector3());
      const radius = Math.sqrt(s.x * s.x + s.y * s.y + s.z * s.z) / 2;
      const dist = _view.camera.position.distanceTo(_view.controls.target);
      return {
        shipId: (typeof shipId !== "undefined") ? shipId : null,
        dist, radius, size: [s.x, s.y, s.z],
        camZ: _view.camera.position.z - _view.controls.target.z,
        near: _view.camera.near, far: _view.camera.far,
        diag: _view._fitDiag || null,
      };
    });
    rows.push({ cls, ...m, ratio: m.dist / m.radius });
  }

  await browser.close();
  server.close();

  /* ------------------------------------------------------------- 1. framing */
  console.log("--- 1. every sampled hull is framed like a ship, not a speck ---");
  console.log("hull                          dist     radius    ratio");
  for (const r of rows) {
    if (r.err) { console.log(`${r.cls.padEnd(28)} ${r.err}`); continue; }
    console.log(`${r.cls.padEnd(28)}${r.dist.toFixed(1).padStart(9)}`
      + `${r.radius.toFixed(1).padStart(10)}${(r.ratio.toFixed(2) + "x").padStart(9)}`);
  }
  console.log();
  const loaded = rows.filter((r) => !r.err);
  check(loaded.length === rows.length,
    "every sampled hull actually loaded its model in the browser",
    `${loaded.length} of ${rows.length}`);
  /* THE HULL ON SCREEN IS THE HULL THAT WAS ASKED FOR. Without this the
     control passes while measuring one ship over and over, which is what it
     did on its first run. */
  const wrongShip = loaded.filter((r) => r.shipId !== r.cls);
  check(wrongShip.length === 0,
    "and the page is showing the hull that was asked for, not the last one",
    wrongShip.map((r) => `${r.cls} showed ${r.shipId}`).slice(0, 3).join(", "));
  /* AND THE HULLS DIFFER FROM EACH OTHER. Identical radii across a sample
     spanning a 1.2m fighter and a 76m explorer is not a measurement. */
  const radii = new Set(loaded.map((r) => r.radius.toFixed(3)));
  check(radii.size > 1 || loaded.length <= 1,
    "and the sampled hulls are genuinely different sizes",
    `${radii.size} distinct radii across ${loaded.length} hulls`);
  for (const r of loaded) {
    check(r.ratio >= LO && r.ratio <= HI,
      `${r.cls} is framed within ${LO}-${HI}`, `${r.ratio.toFixed(2)}x`);
  }

  /* ------------------------------------------------- 2. the planes handed back */
  console.log("\n--- 2. the fit handed the clip planes back ---");
  for (const r of loaded) {
    /* _setClip owns the rendered frame. If A1's wide measurement planes were
       still in force, far would be enormous relative to the hull. */
    check(r.far < r.radius * 200,
      `${r.cls} renders on tight planes, not the fit's wide ones`,
      `far ${r.far.toFixed(1)} vs radius ${r.radius.toFixed(1)}`);
  }

  /* --------------------------------------------------------- 3. the nose, V1 */
  console.log("\n--- 3. the page opens on the nose, not the tail ---");
  /* FORWARD IS -Z, measured in place_hardpoints.py and confirmed against the
     point clouds. A camera that opens on the front sits at negative Z relative
     to the target. This is a SEPARATE assertion from the ratio because turning
     the camera around does not change how big the ship is in frame - so
     --mutate-behind is framing-neutral and only this section can catch it. */
  for (const r of loaded) {
    check(r.camZ < 0, `${r.cls} opens in front of the hull`,
      `camera z offset ${r.camZ.toFixed(1)}`);
  }

  /* ------------------------------------------------------- 4. nothing threw */
  console.log("\n--- 4. the page did not throw on the way ---");
  check(pageErrors.length === 0, "no uncaught page errors",
    pageErrors.slice(0, 3).join(" | "));

  console.log("\n" + "=".repeat(66));
  if (failures.length) {
    console.log(`FAILED: ${failures.length} of ${passed + failures.length}`);
    for (const f of failures.slice(0, 12)) console.log("  " + f);
    if (MUT) console.log("\n--mutate: a defect was planted, so a non-zero "
      + "exit is the CORRECT outcome.");
    process.exit(1);
  }
  console.log(`PASSED: ${passed} assertions, measured in a real browser.`);
  if (MUT) {
    console.log("\n*** THE PLANTED DEFECT WAS NOT CAUGHT. That is a failure of "
      + "this control, not a pass. ***");
    process.exit(1);
  }
  process.exit(0);
}

main().catch((e) => {
  try { server.close(); } catch (_e) {}
  console.log("STOPPED: " + (e && e.stack || e));
  process.exit(2);
});
