/* DIAGNOSTIC, not a gate. Written by Code (background session) 2026-08-27 to
 * explain why section 2 of _verify_panel_dismiss.mjs is red. Reports, for a
 * set of off-stage click targets, whether the mount panel dismisses.
 * It asserts nothing and gates nothing. */
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";
const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const DEPLOY = join(ROOT, "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");
const { chromium } = await import("playwright");
const TYPES = { ".html":"text/html", ".js":"text/javascript", ".json":"application/json",
                ".css":"text/css", ".glb":"model/gltf-binary", ".png":"image/png" };
const server = createServer((req,res)=>{
  const p = join(DEPLOY, decodeURIComponent(req.url.split("?")[0].split("#")[0]));
  if (!existsSync(p) || p.endsWith("/")) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {"content-type": TYPES[extname(p)] || "application/octet-stream"});
  res.end(readFileSync(p));
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;
const SHIP = process.argv[2] || "arrow";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(`${base}/loadout.html?cc=${SHIP}#${SHIP}`, { waitUntil: "networkidle" });
await page.waitForTimeout(2500);

const openPanel = async () => page.evaluate(async () => {
  const b = document.querySelector('#cc-marks button[data-mount]');
  const marks = [...document.querySelectorAll('#cc-marks button[data-mount]')];
  for (const m of marks) { m.click(); await new Promise(r=>setTimeout(r,120));
    if (typeof mountSel !== "undefined" && mountSel !== null) return true; }
  if (b) b.click();
  await new Promise(r=>setTimeout(r,120));
  return typeof mountSel !== "undefined" && mountSel !== null;
});
const isOpen = async () => page.evaluate(() => {
  const p = document.querySelector('#cc-panel');
  return !!(p && getComputedStyle(p).display !== "none" && p.offsetParent !== null);
});

const targets = [
  [".tabs (what the check clicks)", '.tabs'],
  ["the active tab link",           '.tabs a[data-tab]'],
  ["the spec table",                '.spec, table, .col'],
  ["the page header",               '.top, header'],
  ["the page margin (body edge)",   'BODY_EDGE'],
];
console.log(`ship=${SHIP}  does clicking here dismiss the mount panel?\n`);
for (const [label, sel] of targets) {
  const opened = await openPanel();
  if (!opened) { console.log(`  ${label.padEnd(32)} SKIPPED - could not open a mountSel panel`); continue; }
  const pt = await page.evaluate((s) => {
    if (s === 'BODY_EDGE') return { x: 4, y: window.innerHeight - 4, tag: "BODY-EDGE" };
    const t = document.querySelector(s);
    if (!t) return null;
    const r = t.getBoundingClientRect();
    const x = r.left + Math.min(40, r.width/2), y = r.top + r.height/2;
    const el = document.elementFromPoint(x, y);
    return { x, y, tag: el ? el.tagName + (el.className ? "." + String(el.className).split(" ")[0] : "") : "?" };
  }, sel);
  if (!pt) { console.log(`  ${label.padEnd(32)} SKIPPED - no such element`); continue; }
  await page.mouse.click(pt.x, pt.y);
  await page.waitForTimeout(180);
  const still = await isOpen();
  console.log(`  ${label.padEnd(32)} ${still ? "STAYS OPEN" : "dismisses "}  (hit ${pt.tag})`);
}
await browser.close(); server.close();
