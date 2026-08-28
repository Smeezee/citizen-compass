/* DIAGNOSTIC, not a gate. Opens the SERVED testing site (past its own
 * client-side preview gate, which its source documents as not access control),
 * finds the ship whose name matches argv[2] as a regex, and counts the
 * hardpoint dots actually in the DOM.
 *
 * Generalised from _diag_served_hercules.mjs, which hard-coded one ship.
 * Written because the 22:20 build changed marker coordinates on 71 hulls and
 * added 5 more, and no single named ship proves that.
 *
 *   node checks/_diag_served_ship.mjs "Constellation Andromeda" [shot.png]
 */
const BASE = "https://citizencompasstesting.citizencompass-contact.workers.dev";
const WANT = process.argv[2];
if (!WANT) { console.log("usage: node _diag_served_ship.mjs <name regex> [png]"); process.exit(2); }
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH ||
  "C:/Users/david/citizen-compass/checks/.playwright-browsers";
const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
page.on("pageerror", e => console.log("  pageerror:", String(e).slice(0, 120)));

await page.goto(BASE + "/loadout", { waitUntil: "domcontentloaded" });
await page.evaluate(() => { try { localStorage.setItem("ccGate", "1"); } catch (e) {} });
await page.goto(BASE + "/loadout", { waitUntil: "networkidle" });
await page.waitForTimeout(2000);

/* An EXACT name wins over a substring: "Constellation" alone would land on
 * whichever variant sorts first and report it as though it were the ship
 * asked about. That mistake was made by hand on 2026-08-27 with the A2/M2. */
const key = await page.evaluate((want) => {
  if (typeof SHIPS === "undefined") return { err: "SHIPS not defined" };
  const re = new RegExp(want, "i");
  const hits = Object.keys(SHIPS).filter(k => re.test(SHIPS[k].n || ""));
  if (!hits.length) return { err: "no match for " + want };
  const exact = hits.find(k => (SHIPS[k].n || "").toLowerCase() === want.toLowerCase());
  const k = exact || hits[0];
  return { key: k, name: SHIPS[k].n, cls: SHIPS[k].cls || null,
           matched: hits.length, others: hits.map(h => SHIPS[h].n).slice(0, 6) };
}, WANT);
console.log("ship:", JSON.stringify(key));
if (key.err) { await browser.close(); process.exit(1); }

await page.goto(`${BASE}/loadout#${encodeURIComponent(key.key)}`, { waitUntil: "networkidle" });
await page.reload({ waitUntil: "networkidle" });
await page.waitForTimeout(6000);

const out = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('#cc-marks button[data-mount]')];
  const vis = btns.filter(b => { const r = b.getBoundingClientRect();
                                return r.width > 0 && r.height > 0; });
  /* spread, not just count: 6 dots bunched mid-hull is what a frame the
   * emitter could not place into looks like. */
  const xs = vis.map(b => b.getBoundingClientRect().left);
  const ys = vis.map(b => b.getBoundingClientRect().top);
  const span = a => a.length ? Math.round(Math.max(...a) - Math.min(...a)) : 0;
  return {
    markersInDom: btns.length,
    visible: vis.length,
    modelLoaded: (typeof _view !== "undefined" && _view && !!_view.current),
    marksForClass: (typeof MARKS !== "undefined" && typeof shipId !== "undefined"
                    && SHIPS[shipId] && MARKS[SHIPS[shipId].cls])
                   ? MARKS[SHIPS[shipId].cls].length : null,
    spreadPx: { x: span(xs), y: span(ys) },
    shownNow: (typeof shipId !== "undefined") ? shipId : null,
  };
});
console.log(JSON.stringify(out, null, 1));
if (process.argv[3]) await page.screenshot({ path: process.argv[3] });
await browser.close();
