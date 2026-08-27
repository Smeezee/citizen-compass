/**
 * P1/P2 - THE PANEL CLOSES WHEN YOU CLICK AWAY FROM IT, AND IT DOES NOT SHOUT.
 *
 * WHY THIS IS A REAL-BROWSER CONTROL AND NOT A vm HARNESS ONE.
 * The defect is `e.target.closest(...)` walking a real DOM from a real click at
 * real coordinates over a real WebGL canvas. The vm harness dispatches a
 * synthetic object at a chosen element - which is to say it decides in advance
 * what the click hit, which is the entire question. Same lesson as F3: a
 * control that cannot see what a visitor sees is not a control over what a
 * visitor sees.
 *
 * THE DEFECT. Shipped in aea8206, reported by Sleven on the Anvil Arrow:
 * "I can't click away from it. Once I open it up, there's no way to close it."
 * The dismiss branch read `if(sel && e.target.closest('#cc-stage') ...)`.
 * renderStagePanel() opens #cc-panel from TWO states - `sel` for a selected
 * port, `mountSel` for a mount carrying more than one weapon, with `sel`
 * deliberately null. The test named one. Escape named both.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT. Each mutation is planted in the bytes the
 * browser parses, and each MUST make this exit non-zero:
 *   --mutate-selonly   the `sel &&` first term restored. If the run still
 *                      passes, this file is testing the sel path and has never
 *                      touched the defect.
 *   --mutate-stagescope  the #cc-stage requirement restored - clicking off the
 *                      stage stops closing it.
 *   --mutate-order     the dismiss branch moved back ABOVE the .pi row branch.
 *                      Section 3 must go red: broadening the test without
 *                      moving it eats part selection.
 *   --mutate-accent    #cc-panel's border put back to var(--accent2).
 *                      Section 4 must go red.
 *
 * Usage: node checks/_verify_panel_dismiss.mjs [--mutate-...]
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

/* Each entry: [which served file, pattern, replacement]. */
const MUTATIONS = {
  /* P1e moved the dismiss to the TOP of the handler behind panelKeepsOpen(),
     so every mutator below is written against that shape. The earlier
     end-of-handler patterns are gone deliberately rather than kept "just in
     case" - a mutator that silently matches nothing is worse than no mutator,
     and the server exits non-zero when one fails to apply. */
  "--mutate-selonly": ["loadout.html",
    /if\(\(sel\|\|mountSel\) && !panelKeepsOpen\(e\.target\)\)\{/,
    "if((sel) && !panelKeepsOpen(e.target)){"],
  "--mutate-stagescope": ["loadout.html",
    /if\(\(sel\|\|mountSel\) && !panelKeepsOpen\(e\.target\)\)\{/,
    "if((sel||mountSel) && e.target.closest('#cc-stage') && !panelKeepsOpen(e.target)){"],
  /* THE CONTROL ON SECTION 3, and the reason panelKeepsOpen has a list rather
     than a position. Drop the picker surfaces from it and a click on a part
     row is read as walking away: the panel closes underneath the selection. */
  "--mutate-order": ["loadout.html",
    /\|\| t\.closest\('\.inlinepick'\) \|\| t\.closest\('\.slot\[data-slot\]'\)\n\s*\|\| t\.closest\('\.pi\[data-part\]'\)/,
    ""],
  "--mutate-accent": ["loadout.html",
    /#cc-panel\{position:absolute;z-index:6;background:var\(--panel\);\n border:1px solid var\(--line\);/,
    "#cc-panel{position:absolute;z-index:6;background:var(--panel);\n border:1px solid var(--accent2);"],
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
    const [file, re, rep] = MUTATIONS[MUT];
    if (p.endsWith("/" + file)) {
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

/* THE SHIP IS NAMED BECAUSE OF WHAT IT CARRIES, not because it was handy.
   The Arrow is the hull Sleven was holding when he reported this, and its
   header reads "9 mounts, 19 weapons" - so most of its dots carry more than
   one weapon and take the mountSel route that the old test could not close. */
const SHIP = "ANVL_Arrow";

async function main() {
  let chromium;
  try { ({ chromium } = await import("playwright")); }
  catch (e) { notPerformed("playwright is not installed under checks/. Run:\n"
    + "  cd checks && npm install && npm run install-browser"); }

  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;

  let browser;
  try {
    browser = await chromium.launch({ headless: true,
      args: ["--use-gl=angle", "--use-angle=swiftshader",
             "--enable-unsafe-swiftshader", "--disable-gpu-sandbox"] });
  } catch (e) {
    server.close();
    notPerformed("headless Chromium would not launch: " + e.message);
  }

  console.log("=".repeat(66));
  console.log("P1/P2 - the picker panel, in a real browser");
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
            && document.querySelectorAll('#cc-marks button[data-mount]').length > 0,
      null, { timeout: 45000 });
  } catch (e) { ready = false; }
  if (!ready) {
    await browser.close(); server.close();
    notPerformed(`${SHIP} never produced hull markers within 45s, so nothing `
      + `about dismissing its panel can be measured. Not a pass.`);
  }

  const panelOpen = () => page.evaluate(() => {
    const el = document.getElementById('cc-panel');
    return !!el && !el.hidden && el.getBoundingClientRect().width > 0;
  });
  const stateOf = () => page.evaluate(() => ({
    sel: typeof sel !== "undefined" ? (sel ? sel.slot : null) : "undefined",
    mountSel: typeof mountSel !== "undefined" ? mountSel : "undefined",
  }));

  /* Find a dot that opens the MOUNT LIST - the state the old test could not
     close. Asserted, not assumed: if this hull has no multi-weapon mount the
     run reports NOT PERFORMED rather than quietly testing the easy path. */
  const multi = await page.evaluate(() => {
    const dots = [...document.querySelectorAll('#cc-marks button[data-mount]')];
    for (const d of dots) {
      const mo = mountOf(shipId, d.dataset.mount);
      if (mo && mo.n > 1) return d.dataset.mount;
    }
    return null;
  });
  if (!multi) {
    await browser.close(); server.close();
    notPerformed(`${SHIP} has no mount carrying more than one weapon in this `
      + `build, so the mountSel state cannot be entered and the defect cannot `
      + `be reproduced. Reporting that rather than passing on the sel path.`);
  }

  const clickDot = async (mount) => {
    const box = await page.locator(`#cc-marks button[data-mount="${mount}"]`)
      .first().boundingBox();
    if (!box) return false;
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForTimeout(120);
    return true;
  };
  /* AN EMPTY PATCH OF STAGE, COMPUTED - not a guessed coordinate. It must miss
     the panel, every marker, and the corner controls, or this proves nothing. */
  const emptyStagePoint = () => page.evaluate(() => {
    const st = document.getElementById('cc-stage').getBoundingClientRect();
    const avoid = [...document.querySelectorAll(
      '#cc-marks button, #cc-panel, #cc-tune, #cc-tune-panel, #cc-spin, #cc-dim, #cc-lbl-toggle')]
      .map(e => e.getBoundingClientRect());
    for (let gx = 1; gx < 20; gx++) for (let gy = 1; gy < 14; gy++) {
      const x = st.left + st.width * gx / 20, y = st.top + st.height * gy / 14;
      if (avoid.some(r => x >= r.left - 6 && x <= r.right + 6
                       && y >= r.top - 6 && y <= r.bottom + 6)) continue;
      const el = document.elementFromPoint(x, y);
      if (!el) continue;
      if (el.closest('#cc-panel') || el.closest('#cc-marks button')) continue;
      return { x, y };
    }
    return null;
  });

  /* ---- 1. the mount-list state closes on a click away, inside the stage ---- */
  console.log("\n1. the mount list, dismissed by clicking the stage");
  await clickDot(multi);
  const s1 = await stateOf();
  check(await panelOpen(), "the panel opened from a multi-weapon mount",
        JSON.stringify(s1));
  check(s1.mountSel !== null && s1.mountSel !== "undefined",
        "and it opened into the mountSel state, not sel", JSON.stringify(s1));
  const pt = await emptyStagePoint();
  if (!pt) {
    await browser.close(); server.close();
    notPerformed("no empty patch of stage could be found that misses the panel, "
      + "every marker and the corner controls. Nothing was clicked, so nothing "
      + "is claimed.");
  }
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(150);
  const s2 = await stateOf();
  check(!(await panelOpen()), "clicking empty stage closed it");
  check(s2.sel === null && (s2.mountSel === null),
        "and BOTH sel and mountSel were cleared", JSON.stringify(s2));

  /* ---- 2. it also closes from a click OUTSIDE the stage ---- */
  console.log("\n2. dismissed by clicking off the stage entirely");
  await clickDot(multi);
  check(await panelOpen(), "re-opened");
  const off = await page.evaluate(() => {
    const t = document.querySelector('.tabs') || document.querySelector('.top')
           || document.body;
    const r = t.getBoundingClientRect();
    return { x: r.left + Math.min(40, r.width / 2), y: r.top + r.height / 2 };
  });
  await page.mouse.click(off.x, off.y);
  await page.waitForTimeout(150);
  check(!(await panelOpen()), "clicking off the stage closed it too");

  /* ---- 3. THE LOAD-BEARING NEGATIVE. Selection still works. ---- */
  console.log("\n3. the picker still selects - the control on P1c");
  const sel3 = await page.evaluate(async () => {
    const row = document.querySelector('.slot[data-slot]');
    if (!row) return { skip: "no slot rows" };
    row.click();
    await new Promise(r => setTimeout(r, 150));
    const slot = (typeof sel !== "undefined" && sel) ? sel.slot : null;
    if (!slot) return { skip: "clicking a slot row selected nothing" };
    const before = (editing === "A" ? A : B)[slot];
    /* NOT THE FIRST ROW. H3 pins the FITTED part to the top of the picker, so
       the first row re-applies what is already there and "the part changed"
       can never hold - the check failed on a correct page. Take the first row
       offering something DIFFERENT, and say so if there isn't one rather than
       asserting against a list of one. */
    const rows = [...document.querySelectorAll(
      '.inlinepick .pi[data-part], #cc-panel .pi[data-part]')];
    if (!rows.length) return { skip: "no part rows offered" };
    const pi = rows.find(r => r.dataset.part !== before);
    if (!pi) return { skip: `every row offered is the fitted part (${before})` };
    pi.click();
    await new Promise(r => setTimeout(r, 200));
    const after = (editing === "A" ? A : B)[slot];
    return { before, after, part: pi.dataset.part };
  });
  if (sel3.skip) {
    console.log(`  NOT PERFORMED (section 3): ${sel3.skip}`);
    failures.push(`section 3 could not run: ${sel3.skip}`);
  } else {
    check(sel3.after === sel3.part && sel3.after !== sel3.before,
      "clicking a part row still changes the fitted part",
      `${sel3.before} -> ${sel3.after}, wanted ${sel3.part}`);
  }

  /* ---- 4. the border matches the rest of the page ---- */
  console.log("\n4. the panel borders like every other panel");
  await clickDot(multi);
  const borders = await page.evaluate(() => {
    const g = (s) => { const e = document.querySelector(s);
      return e ? getComputedStyle(e).borderTopColor : null; };
    return { panel: g('#cc-panel'), col: g('.col'), stat: g('.stat') };
  });
  /* COMPARED AGAINST THE PAGE'S OWN COLOUR, not a literal hex. A theme that
     moved both would pass a hex check while telling us nothing. */
  check(borders.panel && borders.col && borders.panel === borders.col,
    "#cc-panel's border colour equals .col's",
    `panel=${borders.panel} col=${borders.col} stat=${borders.stat}`);

  console.log("\n" + "-".repeat(66));
  check(pageErrors.length === 0, "no uncaught page errors",
        pageErrors.slice(0, 3).join(" | "));

  await browser.close();
  server.close();

  console.log("=".repeat(66));
  console.log(`${passed} passed, ${failures.length} failed`);
  if (failures.length) {
    for (const f of failures) console.log(`  - ${f}`);
    console.log(MUT ? "RED, which is what the mutation is for." : "RED.");
    process.exit(1);
  }
  if (MUT) {
    console.log(`MUTATION ${MUT} WAS NOT CAUGHT. This control did not do its `
      + `job and must not be trusted until it does.`);
    process.exit(1);
  }
  console.log("GREEN");
}
main().catch((e) => { try { server.close(); } catch (_) {} 
  console.log("ERROR " + (e && e.stack || e)); process.exit(2); });
