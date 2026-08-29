/**
 * RULE16: INDEPENDENT - the camera's position is read out of a REAL browser
 * after a REAL click on a real marker, and compared against itself before the
 * click. Nothing here consults the code's own opinion of whether it moved; the
 * only inputs are two readings of the same object and three deliberately
 * broken builds that must each be caught.
 *
 * THE SHIP MUST NOT MOVE WHEN A PANEL OPENS.
 *
 * THE DEFECT, reported by Sleven on the deployed page, 2026-08-27:
 *   "When you click a hard point, the whole ship shifts... I really want the
 *    ship to stop shifting when we open a thing... it needs to get fleshed
 *    out and smoothed out."
 *
 * E4 had the viewer PAN the hull sideways so an opening panel would not cover
 * it. The arithmetic was right and the remedy was wrong: it moved the thing
 * the person was looking at, on every single click. The panel follows the
 * marker's screen side now and the camera is not touched at all.
 *
 * WHY THIS IS A REAL-BROWSER CONTROL. The vm harness's viewer stub exposes no
 * camera, so the assertion that matters reports NOT PERFORMED there - which is
 * how this file came to exist. A control that cannot see the camera cannot say
 * whether the camera moved.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT. Each mutation is planted in the bytes the
 * browser parses and each MUST make this exit non-zero:
 *   --mutate-pan        the E4 sideways shift restored in reframe(), and
 *                       setObstruction made to call it again. Section 2 must
 *                       go red: the hull moves on click.
 *   --mutate-alwaysright  panelPlacement returned to "prefer the right".
 *                       Section 3 must go red on a left-hand marker.
 *   --mutate-opaque     hullAlpha forced to 1. Section 4 must go red.
 *
 * Usage: node checks/_verify_stage_still.mjs [--mutate-...]
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

const argv = process.argv.slice(2);
const MUT = argv.find((a) => a.startsWith("--mutate-")) || "";

/* EACH MUTATOR IS A LIST OF EDITS, because restoring E4 takes two and either
   one alone proves nothing.

   `reframe()` still exists and is still called on a resize or a model change -
   so putting the SHIFT back on its own moves nothing on a click, and making
   setObstruction CALL it on its own re-centres on a centre the camera is
   already at. Split across two mutators, both would pass, and a mutator that
   passes is worse than no mutator: it reports that a defect was planted and
   survived, which reads as the check being weak rather than the plant being
   inert. E4 is one defect and it is planted as one. */
const MUTATIONS = {
  "--mutate-pan": [
    ["cc_viewer.js",
     /this\.controls\.target\.set\(c\.x, c\.y, c\.z\);/,
     "this.controls.target.set(c.x + (s.x||1)*(this._obstruct||0)*0.5, c.y, c.z);"],
    ["cc_viewer.js",
     /this\._obstruct = f;\n    return f;/,
     "this._obstruct = f;\n    this.reframe();\n    return f;"],
  ],
  /* The old placement: right unless there is no room. */
  "--mutate-alwaysright": [
    ["loadout.html",
     /let side = \(px <= sw\/2\) \? "left" : "right";/,
     'let side = "right";'],
  ],
  /* A hull with no see-through at all. */
  "--mutate-opaque": [
    ["cc_viewer.js", /hullAlpha: 0\.\d+,/, "hullAlpha: 1.0,"],
  ],
};
if (MUT && !MUTATIONS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }

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

if (!existsSync(DEPLOY)) notPerformed(`no built payload at ${DEPLOY}`);

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
  if (MUT) {
    /* EVERY EDIT IN THE MUTATOR MUST APPLY. One of two landing would plant
       half a defect and test against it. */
    for (const [file, re, rep] of MUTATIONS[MUT]) {
      if (!p.endsWith("/" + file)) continue;
      const before = body.toString("utf-8");
      const after = before.replace(re, rep);
      if (after === before) {
        console.log(`MUTATION DID NOT APPLY - ${MUT} matched nothing in the `
          + `served ${file}, so this run would have proven nothing.`);
        process.exit(2);
      }
      body = Buffer.from(after, "utf-8");
    }
  }
  res.writeHead(200, { "Content-Type": TYPES[extname(f)] || "application/octet-stream" });
  res.end(body);
});

/* A HULL WITH DOTS ON BOTH SIDES OF THE STAGE, which is what section 3 needs.
   The 400i is the ship Sleven was holding when he reported the shift. */
const SHIP = "ORIG_400i";

async function main() {
  let chromium;
  try { ({ chromium } = await import("playwright")); }
  catch (e) { notPerformed("playwright is not installed under checks/. Run:\n"
    + "  cd checks && npm install && npm run install-browser"); }

  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;

  let browser;
  try {
    /* CC_CHROMIUM POINTS THIS AT A BROWSER PLAYWRIGHT DID NOT INSTALL, AND IT
       IS WHAT MADE THIS CONTROL RUNNABLE BY ANYONE BUT CODE.
       C1 could not run it for two days: the Windows headless shell in
       checks/.playwright-browsers cannot execute on the Cowork Linux VM, and
       that VM's network allowlist refuses cdn.playwright.dev. What it DOES
       have is a Chromium at a fixed path under a different build number than
       the npm package expects, which `chromium.launch()` will not find on its
       own. One env var, and the control stops being one machine's privilege.
       Unset, behaviour is exactly as before. */
    const _exe = process.env.CC_CHROMIUM || undefined;
    const _args = ["--use-gl=angle", "--use-angle=swiftshader",
                   "--enable-unsafe-swiftshader", "--disable-gpu-sandbox"];
    if (process.env.CC_NO_SANDBOX === "1") _args.push("--no-sandbox");
    browser = await chromium.launch({ headless: true,
      executablePath: _exe, args: _args });
  } catch (e) {
    server.close();
    notPerformed("headless Chromium would not launch: " + e.message);
  }

  console.log("=".repeat(66));
  console.log("THE SHIP DOES NOT MOVE WHEN A PANEL OPENS - in a real browser");
  console.log(MUT ? `*** MUTATED: ${MUT} ***` : "clean build");
  console.log("=".repeat(66));

  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(String(e.message || e)));

  await page.goto(`${base}/loadout.html?cc=${SHIP}#${SHIP}`,
                  { waitUntil: "domcontentloaded" });
  let ready = true;
  try {
    await page.waitForFunction(
      () => typeof _view !== "undefined" && _view && _view.current
            && _view.controls && _view.camera
            && document.querySelectorAll('#cc-marks button[data-mount]').length > 1,
      null, { timeout: 45000 });
  } catch (e) { ready = false; }
  if (!ready) {
    await browser.close(); server.close();
    notPerformed(`${SHIP} never produced a camera and two or more hull markers `
      + `within 45s, so nothing about the ship moving can be measured.`);
  }

  /* THE CAMERA, READ WHOLE. Both the look-at point and the eye position - a
     pan moves the target, and anything that recomputed distance would move the
     position. Rounded to 1e-6 so floating-point noise is not read as motion,
     and the pan being caught is 0.5 of a hull width. */
  const camera = () => page.evaluate(() => {
    const t = _view.controls.target, p = _view.camera.position;
    const r = (n) => Math.round(n * 1e6) / 1e6;
    return { tx: r(t.x), ty: r(t.y), tz: r(t.z),
             px: r(p.x), py: r(p.y), pz: r(p.z) };
  });
  const dots = async () => page.evaluate(() => {
    const st = document.getElementById('cc-stage').getBoundingClientRect();
    return [...document.querySelectorAll('#cc-marks button[data-mount]')]
      .map(d => { const r = d.getBoundingClientRect();
                  return { mount: d.dataset.mount,
                           cx: r.left + r.width / 2 - st.left,
                           w: st.width }; })
      .filter(d => d.w > 0);
  });
  const clickDot = async (mount) => {
    const box = await page.locator(`#cc-marks button[data-mount="${mount}"]`)
      .first().boundingBox();
    if (!box) return false;
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(220);
    return true;
  };
  const panelSide = () => page.evaluate(() => {
    const el = document.getElementById('cc-panel');
    if (!el || el.hidden) return null;
    return el.getAttribute('data-side');
  });

  /* ---------------------------------------- 1. the stage is alive at all */
  console.log("\n--- 1. the hull and its markers are really there ---");
  const all = await dots();
  check(all.length > 1, `${SHIP} draws ${all.length} markers`, String(all.length));
  const start = await camera();
  check(isFinite(start.tx) && isFinite(start.px),
    "and the camera reads back as numbers", JSON.stringify(start));

  /* ------------------------------- 2. THE ONE THIS FILE EXISTS FOR */
  console.log("\n--- 2. clicking a hardpoint does not move the ship ---");
  const first = all[0];
  const clicked = await clickDot(first.mount);
  check(clicked, "a marker was clickable", first.mount);
  const opened = await panelSide();
  check(opened !== null, "and the panel opened", String(opened));
  const after = await camera();
  const moved = Object.keys(start).filter(k => start[k] !== after[k]);
  check(moved.length === 0,
    "*** the camera is byte-identical before and after - the ship did not "
    + "shift ***",
    moved.length ? `moved on ${moved.join(",")}: `
      + moved.map(k => `${k} ${start[k]}->${after[k]}`).join("  ") : "");

  /* A second click, on a different dot, must not move it either - a pan that
     only fires on the first open would slip past a single measurement. */
  const other = all.find(d => d.mount !== first.mount);
  if (other) {
    await clickDot(other.mount);
    const after2 = await camera();
    const moved2 = Object.keys(start).filter(k => start[k] !== after2[k]);
    check(moved2.length === 0,
      "and a second marker on a different mount does not move it either",
      moved2.join(",") || "");
  }

  /* ------------------------------- 3. the panel opens on the dot's side */
  console.log("\n--- 3. the panel opens on the marker's own side of the stage ---");
  const left = all.filter(d => d.cx <= d.w / 2).sort((a, b) => a.cx - b.cx)[0];
  const right = all.filter(d => d.cx > d.w / 2).sort((a, b) => b.cx - a.cx)[0];
  if (!left || !right) {
    console.log("     NOT PERFORMED - this hull's markers do not fall on both "
      + "sides of the stage, so the rule cannot be exercised in both "
      + "directions. Reported, never passed.");
  } else {
    await clickDot(left.mount);
    const sL = await panelSide();
    check(sL === "left", "a marker LEFT of centre opens the panel on the left",
      `x=${Math.round(left.cx)} of ${Math.round(left.w)}, panel ${sL}`);
    await clickDot(right.mount);
    const sR = await panelSide();
    check(sR === "right", "a marker RIGHT of centre opens it on the right",
      `x=${Math.round(right.cx)} of ${Math.round(right.w)}, panel ${sR}`);
    check(sL !== sR, "and the two answers differ - the side is not a constant",
      `${sL} / ${sR}`);
  }

  /* ------------------------------- 4. the hull is see-through */
  console.log("\n--- 4. the hull renders see-through, as asked for ---");
  const look = await page.evaluate(() => {
    const a = (typeof CC_HOLO !== "undefined") ? CC_HOLO.hullAlpha : null;
    let transparent = null;
    try {
      _view.current.traverse((o) => {
        if (transparent === null && o.isMesh && o.material
            && o.material.uniforms && o.material.uniforms.uAlpha) {
          transparent = !!o.material.transparent;
        }
      });
    } catch (e) { /* reported by the assertions below */ }
    return { alpha: a, transparent };
  });
  check(look.alpha !== null && look.alpha < 1,
    "the hull alpha is below solid", String(look.alpha));
  check(look.transparent === true,
    "and the material it is drawn with is actually transparent",
    String(look.transparent));
  check(look.alpha === null || look.alpha >= 0.25,
    "and not so low the ship disappears", String(look.alpha));

  /* ------------------------------- 5. nothing threw doing any of it */
  console.log("\n--- 5. the page threw nothing while being driven ---");
  check(pageErrors.length === 0, "no uncaught page errors",
    pageErrors.slice(0, 3).join(" | "));

  await browser.close();
  server.close();

  console.log("\n" + "=".repeat(66));
  if (failures.length) {
    console.log(`FAILED: ${failures.length} of ${passed + failures.length}`);
    for (const f of failures) console.log("  " + f);
    process.exit(1);
  }
  console.log(`All ${passed} assertions passed in a real browser.`);
  process.exit(0);
}

main().catch((e) => { try { server.close(); } catch (_) {} 
  console.log("ERRORED: " + (e && e.message ? e.message : e));
  process.exit(2); });
