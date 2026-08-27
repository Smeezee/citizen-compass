/* DIAGNOSTIC, not a gate. Measures every deployed model through the site's own
 * viewer and compares its largest real dimension to the ship's largest
 * published dimension. Writes a JSON result. Asserts nothing, changes nothing.
 *
 * Written 2026-08-27 after the imported models were found to be in a different
 * space from the rest of the fleet. The question this answers is the obvious
 * next one: has anything ever checked the 234 that were already here.
 *
 *   node checks/_diag_fleet_scale_audit.mjs <jobs.json> <out.json>
 */
import { createServer } from "node:http";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";
const HERE = dirname(fileURLToPath(import.meta.url));
const DEPLOY = join(HERE, "..", "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");
const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const outPath = process.argv[3];
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
const page = await browser.newPage({ viewport: { width: 900, height: 600 } });
await page.goto(`${base}/loadout.html`, { waitUntil: "networkidle" });
await page.evaluate(() => { if (typeof view === "function") view(); });
await page.waitForFunction(() => typeof _view !== "undefined" && _view !== null, null, {timeout:25000});
await page.waitForTimeout(400);
const out = [];
let n = 0;
for (const j of jobs) {
  n++;
  const m = await page.evaluate(async (u) => {
    let err = null;
    await new Promise(res => { let d=false; const fin=(e)=>{if(!d){d=true;if(e)err=String(e.message||e);res();}};
      setTimeout(()=>fin(), 60000);
      _view.load(u, { onLoad: ()=>fin(), onError: (e)=>fin(e) }); });
    if (!_view.current) return { err, max: null };
    const b = new THREE.Box3().setFromObject(_view.current);
    const s = b.getSize(new THREE.Vector3());
    return { err, max: Math.max(s.x,s.y,s.z), x:s.x, y:s.y, z:s.z };
  }, `${base}/models/${encodeURIComponent(j.file)}`);
  const ratio = (m && m.max) ? m.max / j.target_max : null;
  out.push({ ...j, measured_max: m ? m.max : null, x: m?m.x:null, y: m?m.y:null,
             z: m?m.z:null, ratio, error: m ? m.err : "no measurement" });
  if (n % 25 === 0) console.log(`  ${n}/${jobs.length}`);
}
await browser.close(); server.close();
writeFileSync(outPath, JSON.stringify(out, null, 1), "utf8");
console.log(`wrote ${outPath} (${out.length} models)`);
