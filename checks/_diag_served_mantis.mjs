/* DIAGNOSTIC, not a gate. Opens the SERVED testing site (past its own
 * client-side preview gate, which its source documents as not access control),
 * finds the Mantis, and counts the hardpoint dots actually in the DOM. */
const BASE = "https://citizencompasstesting.citizencompass-contact.workers.dev";
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

const key = await page.evaluate(() => {
  if (typeof SHIPS === "undefined") return { err: "SHIPS not defined" };
  const k = Object.keys(SHIPS).find(k => /mantis/i.test(SHIPS[k].n || ""));
  return k ? { key: k, name: SHIPS[k].n, cls: SHIPS[k].cls || null } : { err: "no Mantis" };
});
console.log("ship:", JSON.stringify(key));
if (key.err) { await browser.close(); process.exit(1); }

await page.goto(`${BASE}/loadout#${encodeURIComponent(key.key)}`, { waitUntil: "networkidle" });
await page.reload({ waitUntil: "networkidle" });
await page.waitForTimeout(6000);

const out = await page.evaluate(() => {
  const btns = [...document.querySelectorAll('#cc-marks button[data-mount]')];
  const vis = btns.filter(b => { const r = b.getBoundingClientRect();
                                return r.width > 0 && r.height > 0; });
  return {
    markersInDom: btns.length,
    visible: vis.length,
    modelLoaded: (typeof _view !== "undefined" && _view && !!_view.current),
    marksForClass: (typeof MARKS !== "undefined" && typeof shipId !== "undefined"
                    && SHIPS[shipId] && MARKS[SHIPS[shipId].cls])
                   ? MARKS[SHIPS[shipId].cls].length : null,
    shownNow: (typeof shipId !== "undefined") ? shipId : null,
  };
});
console.log(JSON.stringify(out, null, 1));
await page.screenshot({ path: process.argv[2] || "mantis.png" });
await browser.close();
