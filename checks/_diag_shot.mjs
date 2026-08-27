import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { join, extname } from "node:path";
const ROOT="C:/Users/david/citizen-compass";
const DEPLOY = join(ROOT, "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH = join(ROOT, "checks", ".playwright-browsers");
const TYPES={".html":"text/html",".js":"text/javascript",".json":"application/json",".css":"text/css",".glb":"model/gltf-binary",".png":"image/png"};
const server=createServer((req,res)=>{const p=join(DEPLOY,decodeURIComponent(req.url.split("?")[0].split("#")[0]));
 if(!existsSync(p)||p.endsWith("/")){res.writeHead(404);return res.end();}
 res.writeHead(200,{"content-type":TYPES[extname(p)]||"application/octet-stream"});res.end(readFileSync(p));});
await new Promise(r=>server.listen(0,"127.0.0.1",r));
const base=`http://127.0.0.1:${server.address().port}`;
const {chromium}=await import("playwright");
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:900,height:640}});
await page.goto(`${base}/loadout.html`,{waitUntil:"networkidle"});
await page.evaluate(()=>{if(typeof view==="function")view();});
await page.waitForFunction(()=>typeof _view!=="undefined"&&_view!==null,null,{timeout:25000});
await page.waitForTimeout(600);
const out=process.argv[2];
for(const f of process.argv.slice(3)){
  await page.evaluate(async u=>{await new Promise(res=>{let d=false;const fin=()=>{if(!d){d=true;res();}};
    setTimeout(fin,45000);_view.load(u,{onLoad:fin,onError:fin});});}, `${base}/models/${encodeURIComponent(f)}`);
  await page.waitForTimeout(1200);
  const el = await page.$('#cc-stage') || await page.$('#cc-canvas');
  await (el||page).screenshot({path: join(out, f.replace(/\.glb$/,'')+".png")});
  console.log("shot", f);
}
await browser.close(); server.close();
