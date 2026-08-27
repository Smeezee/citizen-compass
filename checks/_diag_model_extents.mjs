/* DIAGNOSTIC, not a gate. Measures the bounding-box extent of any deployed
 * model through the site's own viewer, so imported ships can be compared
 * against ships that were already correct. Asserts nothing. */
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
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
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
await page.goto(`${base}/loadout.html`, { waitUntil: "networkidle" });
await page.evaluate(() => { if (typeof view === "function") view(); });
await page.waitForFunction(() => typeof _view !== "undefined" && _view !== null, null, {timeout:25000});
await page.waitForTimeout(400);
const files = process.argv.slice(2);
console.log("model".padEnd(30) + "  extent      x        y        z");
for (const f of files) {
  const m = await page.evaluate(async (u) => {
    await new Promise(res => { let d=false; const fin=()=>{if(!d){d=true;res();}};
      setTimeout(fin, 45000);
      _view.load(u, { onLoad: fin, onError: fin }); });
    if (!_view.current) return null;
    const b = new THREE.Box3().setFromObject(_view.current);
    const s = b.getSize(new THREE.Vector3());
    return { x:s.x, y:s.y, z:s.z, e: Math.max(s.x,s.y,s.z) };
  }, `${base}/models/${encodeURIComponent(f)}`);
  console.log(f.replace(/\.glb$/,"").padEnd(30) + "  " +
    (m ? `${m.e.toFixed(3).padStart(8)} ${m.x.toFixed(2).padStart(8)} ${m.y.toFixed(2).padStart(8)} ${m.z.toFixed(2).padStart(8)}` : "   (nothing loaded)"));
}
await browser.close(); server.close();
