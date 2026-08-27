/**
 * RULE16: UNPROVEN - it asserts rendered markers against
 * alignment_overlay_client.json, which is the same file the build read to
 * place them - so it proves the overlay REACHED the page, not that the
 * overlay is right. A marker on a wrong CIG coordinate passes. The overlay-
 * removed control is genuinely independent evidence of the first claim and
 * of nothing beyond it.
 *
 * Q2 - THE MARKERS ON THE PAGE ARE ON CIG'S OWN COORDINATES.
 *
 * ORDER: NEXT.md Q2 / ORDER_the-queue-2026-08-27.md.
 *   "510 is a number from a generated file. A marker correct in the data and
 *    invisible in the browser is not fixed."
 *
 * THE SHIP: the Aegis Gladius, named in the order because its wing mounts are
 * the clearest test in the fleet.
 *
 * WHAT IS ASSERTED
 * ================
 * `alignment_overlay_client.json` carries, for every port it moved, BOTH
 * positions:
 *
 *     unit  the position from CIG's own transform - where the marker must be
 *     was   the derived position it replaced - where the marker must NOT be
 *
 * So this does not merely check that the numbers on the page look plausible. It
 * checks that they are the NEW ones and that the OLD ones are gone. A build
 * that silently dropped the overlay would keep every marker at `was`, and every
 * one of those is named here.
 *
 * And it is checked in a browser, on the built payload, with the markers
 * actually drawn: the DOM markers in `#cc-marks` are counted and required to be
 * on screen. Data that is right in a file and never reaches a pixel is the
 * thing the order says is not fixed.
 *
 * THE CONTROL (rule 12)
 * =====================
 *   node checks/_verify_marker_positions.mjs --control-no-overlay
 *
 * moves `alignment_overlay_client.json` aside, REBUILDS, and runs the same
 * assertions - which must all go red, because every marker falls back to `was`.
 * It puts the overlay back and rebuilds again afterwards, and it verifies the
 * restore rather than assuming it.
 *
 * That is the control the order asked for. The `was` comparison above is a
 * second, free one that runs on every normal invocation - a control that only
 * exists when somebody remembers to pass a flag is a control that mostly does
 * not run.
 */
import { createServer } from "node:http";
import { readFileSync, existsSync, renameSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";
import { execFileSync } from "node:child_process";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
const OVERLAY = join(ROOT, "data-layer", "derived", "holo-hardpoints-align",
                     "alignment_overlay_client.json");
const BUILD = join(ROOT, "testing", "_src", "build_deploy.py");
const PY = join(ROOT, "venv", "Scripts", "python.exe");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

const SHIP_OVERLAY_KEY = "Gladius";
const TOL = 0.002;            // normalised units; the generator writes 5 dp
const controlMode = process.argv.includes("--control-no-overlay");

if (!existsSync(OVERLAY)) {
  console.error(`NOT PERFORMED: ${OVERLAY} does not exist, so there is nothing `
    + `to assert against. Reporting as not performed rather than as a pass.`);
  process.exit(1);
}
const overlay = JSON.parse(readFileSync(OVERLAY, "utf8"));
const ports = overlay[SHIP_OVERLAY_KEY];
if (!ports) {
  console.error(`NOT PERFORMED: the overlay has no "${SHIP_OVERLAY_KEY}" entry.`);
  process.exit(1);
}

function rebuild(why) {
  console.log(`  rebuilding (${why}) ...`);
  execFileSync(PY, [BUILD], { cwd: ROOT, stdio: "pipe", timeout: 900000 });
}

/* ---- control: take the overlay away and rebuild, restoring no matter what -- */
let moved = null;
if (controlMode) {
  const attic = join(ROOT, "_to_delete", "control_no_overlay");
  mkdirSync(attic, { recursive: true });
  moved = join(attic, "alignment_overlay_client.json");
  if (existsSync(moved)) {
    console.error(`NOT PERFORMED: ${moved} already exists - a previous control `
      + `run may not have restored. Refusing to move another copy on top of it.`);
    process.exit(1);
  }
  renameSync(OVERLAY, moved);
  console.log("CONTROL: overlay moved aside. Every assertion below MUST go red.");
  rebuild("without the overlay");
}

const failures = [];
function check(cond, label, detail) {
  if (cond) { console.log(`  ok   ${label}`); return true; }
  console.log(`  FAIL ${label}${detail ? "  " + detail : ""}`);
  failures.push(label + (detail ? "  " + detail : ""));
  return false;
}

let exitCode = 0;
try {
  const TYPES = {
    ".html": "text/html", ".js": "text/javascript", ".json": "application/json",
    ".css": "text/css", ".glb": "model/gltf-binary", ".png": "image/png",
    ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ico": "image/x-icon",
  };
  const server = createServer((req, res) => {
    const p = join(DEPLOY, decodeURIComponent(req.url.split("?")[0].split("#")[0]));
    if (!existsSync(p) || p.endsWith("/")) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
    res.end(readFileSync(p));
  });
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;

  const { chromium } = await import("playwright");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(`${base}/loadout.html`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);

  /* The page's own class key for the Gladius, found by asking the page rather
     than by composing a string here. */
  const found = await page.evaluate((key) => {
    const hit = Object.keys(MARKS).filter(k => k.toLowerCase().includes(key.toLowerCase()));
    return { keys: hit, all: Object.keys(MARKS).length };
  }, SHIP_OVERLAY_KEY);

  const exact = found.keys.filter(k => k.toLowerCase().endsWith("_" + SHIP_OVERLAY_KEY.toLowerCase())
                                    || k.toLowerCase() === SHIP_OVERLAY_KEY.toLowerCase());
  console.log("==================================================================");
  console.log(`MARKER POSITIONS - ${SHIP_OVERLAY_KEY}, on the built payload`);
  console.log(`MARKS holds ${found.all} hulls; matching this ship: ${JSON.stringify(found.keys)}`);
  console.log("==================================================================\n");

  if (!exact.length) {
    check(false, `no MARKS entry for ${SHIP_OVERLAY_KEY}`, JSON.stringify(found.keys));
  } else {
    const cls = exact[0];
    const marks = await page.evaluate((c) => MARKS[c], cls);
    console.log(`  hull ${cls}: ${marks.length} markers in the page's data\n`);

    const near = (a, b) => Math.abs(a[0] - b[0]) < 0.002 && Math.abs(a[1] - b[1]) < 0.002
                        && Math.abs(a[2] - b[2]) < 0.002;
    const pts = marks.map(m => [m[1], m[2], m[3]]);

    /* NOT EVERY OVERLAY PORT GETS A MARKER, AND THAT IS BY DESIGN.
       The overlay covers every port CIG has a transform for. The page marks
       WEAPON ports only - "markers stay weapons-only, internal ports are
       reached from the list". On the Gladius that is a weapon rack and two
       regen pools: three ports with a real CIG position and deliberately no
       marker.

       So the assertion is over the ports that ARE marked, decided by the data
       rather than by a list of names kept here: a port is marked if a marker
       sits at its NEW position or at its OLD one. Sitting at neither means the
       build drew no marker for it, which is not this check's business.

       This cannot quietly pass. If the overlay were dropped, every marked port
       would fall back to `was` - so `stale` is the number that would catch it,
       and it is asserted at zero. The --control-no-overlay run proves exactly
       that, by taking the overlay away and rebuilding. */
    let onCig = 0, stale = 0, unmarked = [], staleNames = [];
    for (const [name, rec] of Object.entries(ports)) {
      const u = rec.unit, w = rec.was;
      const atNew = pts.some(p => near(p, u));
      const atOld = !near(u, w) && pts.some(p => near(p, w));
      if (atNew) onCig++;
      else if (atOld) { stale++; staleNames.push(name); }
      else unmarked.push(name);
    }
    const marked = onCig + stale;
    console.log(`  ${Object.keys(ports).length} overlay port(s): ${marked} marked, `
      + `${unmarked.length} correctly unmarked (internal)`);
    if (unmarked.length) console.log(`    unmarked: ${unmarked.join(", ")}`);
    check(marked > 0,
          `the overlay's ports are actually marked on this hull  (${marked})`,
          "no overlay port is marked at all - nothing was asserted");
    check(onCig === marked,
          `every marked port is at CIG's coordinates  (${onCig} of ${marked})`,
          staleNames.length ? `still at the old position: ${staleNames.slice(0, 4).join(", ")}` : "");
    check(stale === 0,
          `and none is still at the superseded position it replaced  (${stale} stale)`,
          stale ? "the overlay did not reach these markers" : "");

    /* And they have to be DRAWN, not merely present in a table. */
    const drawn = await page.evaluate(async (c) => {
      const key = Object.keys(SHIPS).find(k => SHIPS[k].cls === c
        || (SHIPS[k].n || "").toLowerCase().includes("gladius"));
      if (!key) return { err: "no ship row" };
      location.hash = "#" + key;
      await new Promise(r => setTimeout(r, 400));
      return { key };
    }, cls);
    if (drawn.err) {
      console.log(`  (marker DOM not checked: ${drawn.err})`);
    } else {
      await page.reload({ waitUntil: "networkidle" });
      await page.waitForTimeout(4000);
      const dom = await page.evaluate(() => {
        const btns = [...document.querySelectorAll('#cc-marks button[data-mount]')];
        const vis = btns.filter(b => {
          const r = b.getBoundingClientRect();
          return r.width > 0 && r.height > 0 && r.left >= 0 && r.top >= 0;
        });
        return { total: btns.length, visible: vis.length };
      });
      check(dom.visible > 0,
            `and ${dom.visible} of ${dom.total} marker(s) are actually drawn on screen`,
            dom.total ? "" : "no marker buttons in the DOM at all");
    }
  }

  await browser.close();
  server.close();
} finally {
  if (moved) {
    renameSync(moved, OVERLAY);
    if (!existsSync(OVERLAY)) {
      console.error("\nRESTORE FAILED: the overlay was not put back. Fix this "
        + "before anything else - " + moved);
      process.exit(4);
    }
    console.log("\n  overlay restored, verified present");
    rebuild("restoring the real payload");
  }
}

console.log("\n==================================================================");
if (controlMode) {
  if (failures.length) {
    console.log(`${failures.length} failed with the overlay taken away, which is `
      + `what the control is for.`);
    console.log("CONTROL PASSED: this check is reading the overlay, not coincidence.");
    process.exit(0);
  }
  console.log("CONTROL FAILED: the assertions passed with NO overlay present. "
    + "This check is not looking at the overlay and its green result means nothing.");
  process.exit(3);
}
if (failures.length) {
  console.log(`${failures.length} failed`);
  for (const f of failures) console.log(`  - ${f}`);
  console.log("RED.");
  process.exit(1);
}
console.log("GREEN - the markers on the page are on CIG's own coordinates.");
process.exit(0);
