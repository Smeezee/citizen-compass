/**
 * NO SHIP PAGE PRINTS ANOTHER SHIP'S NAME ON ITS ARMOUR.
 *
 * ORDER: NEXT.md Q1, from
 * HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md (C3).
 *
 * THE DEFECT
 * ==========
 * `build_loadout_data.py` took the armour's display name from the ITEM's own
 * record, and that field carries the wrong ship's name on 31 of 91 named
 * armour records - 34%.
 *
 *     ARMR_RSI_Perseus     printed  "Constellation Andromeda Ship Armor"
 *     ARMR_AEGS_Idris_P    printed  "Hammerhead Ship Armor"
 *     ARMR_ORIG_890J       printed  "350r Ship Armor"
 *
 * The NUMBERS were never wrong - armour resolves through each ship's own
 * Loadout, so no ship ever showed another ship's multipliers. It is a labelling
 * bug on a page whose whole claim is that the numbers can be trusted.
 *
 * WHAT IS ASSERTED, AND WHY IT IS NOT "THE NAME EQUALS THE SHIP"
 * ==============================================================
 * The condition is the order's own words: a heading must not name a ship OTHER
 * than the one whose page it is on. That is deliberately not "the heading
 * starts with this ship's name", which would only be a restatement of however
 * the fix happens to compose the string - it would pass anything the current
 * implementation produces and would have to be rewritten if the wording ever
 * changed.
 *
 * So: a heading fails if it contains the display name of a DIFFERENT ship and
 * does NOT contain this ship's own. That is true of the defect, false of a
 * correct page, and independent of how the name is built.
 *
 * Longest names are tested first so that "Constellation Andromeda" is credited
 * before "Constellation", and a ship whose name is a substring of this ship's
 * own name is never counted against it.
 *
 * IT IS CHECKED IN A BROWSER, AND IT IS CHECKED IN THE DOM
 * ========================================================
 * Section 1 reads the page's own ARMOR table for every ship that has armour -
 * that is the data the page renders from, loaded by the real page.
 * Section 2 opens named ship pages and reads the text actually in the
 * paragraph, because data that is right in a table and wrong on screen is the
 * failure this project keeps finding.
 *
 * Usage: node checks/_verify_armour_naming.mjs
 */
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEPLOY = join(HERE, "..", "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

/* Named in the handoff as reproducible instances. Rendered, not just read. */
/* Display names as the page holds them - they carry the manufacturer. */
const RENDER_SAMPLE = ["RSI Perseus", "Origin 890 Jump", "Aegis Hammerhead"];

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

const failures = [];
function check(cond, label, detail) {
  if (cond) { console.log(`  ok   ${label}`); return true; }
  console.log(`  FAIL ${label}${detail ? "  " + detail : ""}`);
  failures.push(label + (detail ? "  " + detail : ""));
  return false;
}

const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.goto(`${base}/loadout.html`, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);

console.log("==================================================================");
console.log("ARMOUR NAMING - no ship page names another ship's armour");
console.log("==================================================================");

const report = await page.evaluate(() => {
  /* THE NAMES HAVE TO BE COMPARED BARE.
     A ship's display name carries its manufacturer - "RSI Perseus",
     "RSI Constellation Andromeda", "Origin 890 Jump" - and the armour heading
     does not: it reads "Constellation Andromeda Ship Armor". A first version of
     this check compared the full display names, found neither the ship's own
     name nor any other inside the heading, and reported GREEN against a build
     that is provably broken. It was green because it could not see, which is
     the failure it was written to catch.
     Bare name = display name minus its leading manufacturer token. */
  const bare = (n) => {
    const parts = String(n || "").split(" ");
    return parts.length > 1 ? parts.slice(1).join(" ") : "";
  };
  const names = [];
  for (const k in SHIPS) {
    const b = bare(SHIPS[k] && SHIPS[k].n);
    if (b) names.push(b);
  }
  names.sort((a, b) => b.length - a.length);   // longest first

  const out = { total: 0, withArmour: 0, offenders: [], missing: [] };
  for (const k in SHIPS) {
    const s = SHIPS[k];
    out.total++;
    if (!s || !s.arm) continue;
    const a = ARMOR[s.arm];
    if (!a) { out.missing.push({ ship: s.n, arm: s.arm }); continue; }
    out.withArmour++;
    const heading = String(a.n || "");
    const own = bare(s.n);
    const lc = heading.toLowerCase();
    if (own && lc.includes(own.toLowerCase())) continue;   // names itself: fine
    const other = names.find(n => n !== own && lc.includes(n.toLowerCase()));
    if (!other) continue;

    /* A VARIANT WEARING ITS BASE HULL'S ARMOUR IS NOT THE DEFECT.
       71 armour records are shared by more than one ship: the Gladius record
       covers the Valiant, the Dunlevy and the Pirate, and "Gladius Ship Armor"
       on a Gladius Valiant page is the honest label - they are the same hull.
       Reading the order's words literally flagged 52 ships, of which 21 were
       this. The defect is a heading naming an UNRELATED ship.
       Structural test, not a list: this ship is a variant of that one when its
       bare name starts with the other's followed by a space. */
    const o = other.toLowerCase(), me = own.toLowerCase();
    if (me === o || me.startsWith(o + " ")) continue;
    out.offenders.push({ ship: s.n, arm: s.arm, heading, names: other });
  }
  return out;
});

console.log(`\n1. every ship that carries armour, read from the page's own table`);
console.log(`   ${report.total} ships, ${report.withArmour} carry armour\n`);
check(report.withArmour > 0,
      `there are armour-carrying ships to check  (${report.withArmour})`,
      "nothing was asserted");
check(report.missing.length === 0,
      `every ship's armour key resolves to a record  (${report.missing.length} missing)`,
      report.missing.slice(0, 3).map(m => `${m.ship}->${m.arm}`).join(", "));
if (!check(report.offenders.length === 0,
      `no armour heading names a different ship  (${report.offenders.length} do)`,
      "")) {
  for (const o of report.offenders.slice(0, 12)) {
    console.log(`        ${o.ship.padEnd(28)} ${o.arm.padEnd(28)} prints "${o.heading}"  -> names ${o.names}`);
  }
  if (report.offenders.length > 12) {
    console.log(`        ... and ${report.offenders.length - 12} more`);
  }
}

/* ---- 2. and it is the text on the page, not only the table ---- */
console.log(`\n2. rendered in the DOM, on the ships the handoff names`);
for (const want of RENDER_SAMPLE) {
  const hit = await page.evaluate((w) => {
    const key = Object.keys(SHIPS).find(k => (SHIPS[k].n || "") === w);
    if (!key) return { absent: true };
    return { key, ship: SHIPS[key].n, arm: SHIPS[key].arm || null };
  }, want);
  if (hit.absent) { console.log(`  --   ${want} is not a ship on this site`); continue; }
  if (!hit.arm) { console.log(`  --   ${want} carries no armour`); continue; }

  await page.goto(`${base}/loadout.html#${encodeURIComponent(hit.key)}`,
                  { waitUntil: "networkidle" });
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  const text = await page.evaluate(() => {
    const els = [...document.querySelectorAll("p.sub2")];
    const el = els.find(e => /cannot be changed/i.test(e.textContent || ""));
    return el ? (el.textContent || "").replace(/\s+/g, " ").trim() : null;
  });
  if (!text) { console.log(`  --   ${want}: the armour block is not rendered in this state`); continue; }
  const shown = text.split(".")[0];
  const bad = await page.evaluate(([t, ownFull]) => {
    const bare = (n) => { const p = String(n || "").split(" ");
                          return p.length > 1 ? p.slice(1).join(" ") : ""; };
    const names = [];
    for (const k in SHIPS) { const b = bare(SHIPS[k] && SHIPS[k].n); if (b) names.push(b); }
    names.sort((a, b) => b.length - a.length);
    const own = bare(ownFull);
    const lc = t.toLowerCase();
    if (own && lc.includes(own.toLowerCase())) return null;
    const other = names.find(n => n !== own && lc.includes(n.toLowerCase()));
    if (!other) return null;
    const o = other.toLowerCase(), me = own.toLowerCase();
    if (me === o || me.startsWith(o + " ")) return null;   // variant of that hull
    return other;
  }, [shown, hit.ship]);
  check(!bad, `${hit.ship.padEnd(16)} armour reads "${shown}"`,
        `names ${bad} instead`);
}

await browser.close();
server.close();

console.log("\n==================================================================");
if (failures.length) {
  console.log(`${failures.length} failed`);
  console.log("RED.");
  process.exit(1);
}
console.log("GREEN - no ship page prints another ship's name on its armour.");
process.exit(0);
