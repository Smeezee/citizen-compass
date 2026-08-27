/* DIAGNOSTIC, not a gate. Enumerates every block carrying the amber
 * explanatory treatment (#1A1206 ground / #6B4C12 border) across the site,
 * with its text, so the audit ORDER_the-disclosure-bar demands can be recorded
 * per block. Asserts nothing, changes nothing. */
import { createServer } from "node:http";
import { readFileSync, existsSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";
const HERE = dirname(fileURLToPath(import.meta.url));
const DEPLOY = join(HERE, "..", "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");
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
const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const PAGES = ["index.html","loadout.html","find.html","keybinds.html","download.html"];
const out = [];
for (const f of PAGES) {
  await page.goto(`${base}/${f}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1800);
  const blocks = await page.evaluate(() => {
    const AMBER = "rgb(26, 18, 6)";          // #1A1206
    const res = [];
    for (const el of document.querySelectorAll("*")) {
      const cs = getComputedStyle(el);
      if (cs.backgroundColor !== AMBER) continue;
      if (el.closest("[data-amber-counted]")) continue;   // outermost only
      el.setAttribute("data-amber-counted", "1");
      const r = el.getBoundingClientRect();
      res.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className || "").toString().slice(0, 40),
        id: el.id || null,
        h: Math.round(r.height),
        visible: r.height > 0 && r.width > 0,
        text: (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 150),
      });
    }
    return res;
  });
  blocks.forEach(b => out.push({ page: f, ...b }));
  console.log(`${f.padEnd(15)} ${blocks.length} amber block(s)`);
}
await browser.close(); server.close();
writeFileSync(process.argv[2] || "amber_blocks.json", JSON.stringify(out, null, 1), "utf8");
console.log(`\ntotal ${out.length}`);
for (const b of out) console.log(`  ${b.page.padEnd(14)} ${String(b.cls).padEnd(14)} h=${String(b.h).padStart(4)}  ${b.text.slice(0,90)}`);
