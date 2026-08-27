/**
 * RULE16: INDEPENDENT - the page is read in a real browser and the rule it
 * is judged against comes from the ORDER, encoded here by a different author
 * than the page - and the three mutations inject shapes the build never
 * emitted.
 *
 * D1 / D2 - THE DISCLOSURE BAR'S TWO CONTROLS.
 *
 * ORDER: docs/ORDER_the-disclosure-bar-2026-08-27.md, section "Rule 12 - two
 * controls, both able to fail". Queue item Q7.
 *
 *   D1  No warning is ever collapsed. Every block that WARNS, reports an ERROR,
 *       or states WHAT THE VISITOR IS LOOKING AT RIGHT NOW must render open.
 *       Mutation: collapse the download page's antivirus notice -> must go red.
 *
 *   D2  No collapsed bar is empty of fact. A collapsed bar must carry a stamp
 *       and a source line while still collapsed - not just an opener label.
 *       Mutation: strip a bar to "More info >" -> must go red.
 *
 * THE STATE OF THE FEATURE, SAID PLAINLY
 * ======================================
 * At the time of writing the collapse pattern IS NOT IMPLEMENTED. The 13 amber
 * explanatory blocks are all rendered open; there is no <summary> anywhere in
 * the payload and nothing is collapsed.
 *
 * That makes D2's subject set EMPTY, and an empty subject set is not a pass.
 * D2 reports NOT PERFORMED and exits non-zero rather than going green over
 * nothing - "no collapsed bar is empty of fact" is trivially true when there
 * are no collapsed bars, and reporting that as success is the exact failure
 * this project calls silent success.
 *
 * D1 CAN pass honestly today, because the warnings genuinely do render open.
 * Its mutation proves it would notice if one stopped.
 *
 * BOTH MUTATIONS WORK BEFORE THE FEATURE EXISTS, because each one injects the
 * shape it is testing into the served bytes:
 *
 *   --mutate-collapse-warning  wraps the download page's antivirus notice in a
 *                              closed <details>. D1 must go red.
 *   --mutate-hollow-bar        injects a collapsed bar whose only content is an
 *                              opener label. D2 must go red.
 *   --mutate-good-bar          injects a WELL-FORMED collapsed bar, carrying a
 *                              stamp and a source line. D2 must stay GREEN.
 *                              Without this one, a D2 that simply always failed
 *                              would look identical to a D2 that works.
 *
 * WHAT D2 ACCEPTS AS "FACT", AND WHY IT IS NOT KEYED ON MARKUP
 * ============================================================
 * The bar is C1's to build and I do not know what attributes it will carry, so
 * asserting on a class or a data- attribute would either constrain C1's
 * implementation or quietly stop matching it. D2 asserts on what a READER gets:
 * the text visible while the bar is collapsed, with the opener label removed,
 * must be at least 20 characters and must contain at least one digit.
 *
 * "More info >" fails both. The pattern the order specifies -
 * "PATCH 4.9  from Star Citizen's game files - scunpacked 20260801T204744Z" -
 * passes both, and would still pass if C1 restructures the markup entirely.
 *
 * NOTHING HERE EDITS DISCLOSURE, ATTRIBUTION OR LICENCE TEXT (hard rule 8).
 * It only asserts that such text is present and readable. Where it finds a gap
 * it reports it.
 *
 * Usage:
 *   node checks/_verify_disclosure.mjs
 *   node checks/_verify_disclosure.mjs --mutate-collapse-warning
 *   node checks/_verify_disclosure.mjs --mutate-hollow-bar
 *   node checks/_verify_disclosure.mjs --mutate-good-bar
 */
import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, extname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEPLOY = join(HERE, "..", "testing", "_deploy");
process.env.PLAYWRIGHT_BROWSERS_PATH =
  process.env.PLAYWRIGHT_BROWSERS_PATH || join(HERE, ".playwright-browsers");

const PAGES = ["index.html", "loadout.html", "find.html", "keybinds.html", "download.html"];

/* Phrases that identify a block the order says must NEVER collapse. Taken from
   the order's own table, and matched on the visitor-facing words rather than on
   a class, so a restyle does not silently drop one out of the set. */
const NEVER_COLLAPSE = [
  { page: "download.html", needle: "quarantine",            what: "antivirus warning about the visitor's own machine" },
  { page: "find.html",     needle: "did not load",          what: "price data error state" },
  { page: "find.html",     needle: "not available",         what: "download-unavailable error state" },
  { page: "find.html",     needle: "Nothing is listed here", what: "empty state" },
  { page: "keybinds.html", needle: "Ctrl+Alt+Del",          what: "control that will not work while in use" },
  { page: "keybinds.html", needle: "Windows key",           what: "control that will not work while in use" },
];

const argv = process.argv.slice(2);
const MUT = {
  "--mutate-collapse-warning": "D1",
  "--mutate-hollow-bar": "D2",
  "--mutate-good-bar": "D2-positive",
};
const unknown = argv.filter(a => !(a in MUT));
if (unknown.length) { console.error(`UNKNOWN MUTATOR ${unknown.join(", ")}`); process.exit(2); }
if (argv.length > 1) { console.error("One mutation at a time."); process.exit(2); }
const mutation = argv[0] || null;

const HOLLOW_BAR = `<details class="ccbar" data-disclosure><summary>More info &rsaquo;</summary><p>hidden body</p></details>`;
const GOOD_BAR = `<details class="ccbar" data-disclosure><summary>PATCH 4.9 &middot; from Star Citizen's game files &middot; scunpacked 20260801T204744Z &nbsp; Where these numbers come from &rsaquo;</summary><p>hidden body</p></details>`;

let mutationApplied = false;

const TYPES = {
  ".html": "text/html", ".js": "text/javascript", ".json": "application/json",
  ".css": "text/css", ".glb": "model/gltf-binary", ".png": "image/png",
  ".svg": "image/svg+xml", ".woff2": "font/woff2", ".ico": "image/x-icon",
};
const server = createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  const p = join(DEPLOY, rel);
  if (!existsSync(p) || p.endsWith("/")) { res.writeHead(404); return res.end(); }
  let body = readFileSync(p);
  const name = rel.replace(/^\//, "");
  if (mutation && extname(p) === ".html") {
    let t = body.toString("utf8");
    if (mutation === "--mutate-collapse-warning" && name === "download.html") {
      // download.html is emitted as a FRAGMENT - it carries no <body> tag, so
      // an earlier version of this mutation wrapped nothing and said so. The
      // paragraph itself is the target instead.
      const anchor = t.indexOf("Your antivirus may also quarantine it");
      if (anchor >= 0) {
        const start = t.lastIndexOf("<p", anchor);
        const end = t.indexOf("</p>", anchor);
        if (start >= 0 && end > start) {
          t = t.slice(0, start)
            + `<details data-disclosure><summary>Notices &rsaquo;</summary>`
            + t.slice(start, end + 4) + `</details>` + t.slice(end + 4);
          mutationApplied = true;
        }
      }
    }
    if ((mutation === "--mutate-hollow-bar" || mutation === "--mutate-good-bar")
        && name === "index.html") {
      const open = t.indexOf("<body");
      const gt = open >= 0 ? t.indexOf(">", open) : -1;
      if (gt > 0) {
        t = t.slice(0, gt + 1)
          + (mutation === "--mutate-hollow-bar" ? HOLLOW_BAR : GOOD_BAR)
          + t.slice(gt + 1);
        mutationApplied = true;
      }
    }
    body = Buffer.from(t, "utf8");
  }
  res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" });
  res.end(body);
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const failures = [];
const notPerformed = [];
let d1Failures = 0, d2Failures = 0;
function check(cond, label, detail) {
  if (cond) { console.log(`  ok   ${label}`); return true; }
  console.log(`  FAIL ${label}${detail ? "  " + detail : ""}`);
  failures.push(label + (detail ? "  " + detail : ""));
  return false;
}

const { chromium } = await import("playwright");
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

console.log("==================================================================");
console.log("D1 / D2 - THE DISCLOSURE BAR'S CONTROLS");
if (mutation) console.log(`MUTATION ACTIVE: ${mutation} - ${MUT[mutation]} is the target`);
console.log("==================================================================");

/* ---------------------------------------------------- D1: warnings stay open */
console.log("\nD1. no warning, error or you-are-here block is collapsed");
let d1Subjects = 0;
for (const page_ of PAGES) {
  const wanted = NEVER_COLLAPSE.filter(n => n.page === page_);
  if (!wanted.length) continue;
  await page.goto(`${base}/${page_}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  for (const n of wanted) {
    const r = await page.evaluate((needle) => {
      const all = [...document.querySelectorAll("body *")];
      const hit = all.filter(e => (e.textContent || "").includes(needle)
                              && ![...e.children].some(c => (c.textContent || "").includes(needle)));
      if (!hit.length) return { absent: true };
      const el = hit[0];
      const closed = el.closest("details:not([open])");
      const rect = el.getBoundingClientRect();
      return {
        absent: false,
        insideClosedDetails: !!closed,
        rendered: rect.height > 0 && rect.width > 0,
      };
    }, n.needle);
    if (r.absent) {
      console.log(`  --   "${n.needle}" is not on ${page_} at all - not asserted`);
      continue;
    }
    if (!r.insideClosedDetails && !r.rendered) {
      /* PRESENT BUT NOT SHOWING IS NOT A FAILURE. Error and empty states only
         render when the thing has gone wrong. What D1 forbids is a warning
         being COLLAPSED - which is a different condition, and is caught by the
         branch above, because a block inside a closed <details> is reported
         whether or not it happens to be in its own display state. */
      console.log(`  --   ${page_}: ${n.what} is not in this state - not asserted`);
      continue;
    }
    d1Subjects++;
    if (!check(!r.insideClosedDetails,
          `${page_}: ${n.what} is not collapsed`,
          "IT IS INSIDE A COLLAPSED <details>")) d1Failures++;
  }
}
if (!d1Subjects) {
  console.log("  NOT PERFORMED: none of D1's subject blocks were found in the DOM.");
  notPerformed.push("D1 had no subjects");
}

/* -------------------------------------- D2: a collapsed bar still says something */
console.log("\nD2. no collapsed bar is empty of fact");
const bars = [];
for (const page_ of PAGES) {
  await page.goto(`${base}/${page_}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  const found = await page.evaluate(() => {
    const out = [];
    for (const d of document.querySelectorAll("details")) {
      if (d.open) continue;
      const sum = d.querySelector("summary");
      if (!sum) continue;
      const text = (sum.textContent || "").replace(/\s+/g, " ").trim();
      // The opener is the trailing label ending in a chevron. Everything before
      // it is what a reader who never clicks actually gets.
      const inSummary = text.replace(/[^·|]*[›>]\s*$/, "").trim();

      /* THE BAR IS THE LINE THE READER SEES, NOT THE <summary> ELEMENT.
         The order specifies two shapes. The provenance bar carries its stamp and
         its source inside the summary. The split case deliberately does not -
         "the count stays in the sentence and only the four sentences of
         reasoning collapse" - so the reader sees
         "Showing 14 of 15 weapon mounts."  and then an inline "why >".
         Scoping to the summary alone called that bar hollow when a reader
         plainly gets the count.

         So this walks BACKWARDS from the <details> over inline siblings only,
         stopping at the first block-level element, and takes what is actually
         rendered. Two boundaries matter and both are deliberate:

           - it stops at a block boundary, so a bare "More info >" cannot borrow
             the words of the paragraph above it. --mutate-hollow-bar has no
             inline lead-in and still fails.
           - it reads rendered text, so the COLLAPSED body does not count. An
             earlier version took the parent's raw text nodes and swept in 658
             characters of the hidden explanation while missing the visible
             count - it was reading precisely what the reader does not get. */
      let beside = "", n = d.previousSibling;
      while (n) {
        if (n.nodeType === 1) {
          const disp = getComputedStyle(n).display;
          if (!disp.startsWith("inline") && disp !== "contents") break;
          beside = (n.innerText || n.textContent || "") + " " + beside;
        } else if (n.nodeType === 3) {
          beside = n.textContent + " " + beside;
        }
        n = n.previousSibling;
      }
      beside = beside.replace(/\s+/g, " ").trim();
      const fact = (beside + " " + inSummary).trim();
      out.push({ text, fact, inSummary, beside });
    }
    return out;
  });
  found.forEach(f => bars.push({ page: page_, ...f }));
}
console.log(`  collapsed bars found: ${bars.length}`);
if (!bars.length) {
  console.log("");
  console.log("  NOT PERFORMED: there are no collapsed bars anywhere in the payload.");
  console.log("  The disclosure-bar pattern is not implemented yet, so D2 has no");
  console.log("  subject. \"No collapsed bar is empty of fact\" is trivially true");
  console.log("  when there are none, and reporting that as a pass is exactly the");
  console.log("  silent success this control exists to prevent.");
  notPerformed.push("D2 had no subjects - the collapse pattern is not built");
} else {
  for (const b of bars) {
    /* A STAMP, NOT NECESSARILY A NUMBER.
       This asked for a digit, on the reasoning that the order's example bar
       carries "PATCH 4.9" and a snapshot id. That is one of the shapes, not
       all of them: C1's matchup bar reads "MATCHUP  not a rating - no gun here
       is better" and the shop bar "NO PRICE JOIN  shop data is real, the link
       to these parts is not proven". Both carry the load-bearing fact for their
       block and neither has a digit in it, and D2 failed them - a correct bar
       rejected by an over-specified check.

       What the order actually specifies is A STAMP: "the single load-bearing
       fact - the patch, the source, the count. Monospace, high contrast,
       unmissable." So the test is for the stamp's SHAPE - a run of capitals or
       a number - plus substance beyond the opener label.

       "More info >" has neither and still fails, which is checked on every run
       by --mutate-hollow-bar rather than argued here. */
    const hasStamp = /\d/.test(b.fact) || /[A-Z]{3,}/.test(b.fact);
    const longEnough = b.fact.length >= 20;
    if (!check(hasStamp && longEnough,
          `${b.page}: collapsed bar carries a fact, not just an opener`,
          `visible-while-collapsed text was ${JSON.stringify(b.fact)} `
          + `(${b.fact.length} chars, stamp:${hasStamp})`)) d2Failures++;
  }
}

await browser.close();
server.close();

console.log("\n==================================================================");
if (mutation && !mutationApplied) {
  console.error(`MUTATION DID NOT APPLY: ${mutation} found nothing to change. `
    + `The page has drifted from what this mutation targets - say so rather `
    + `than treating this run as a result.`);
  process.exit(2);
}
if (mutation === "--mutate-good-bar") {
  /* Judged on D2 ALONE. A first version failed this control because unrelated
     D1 findings were in the same tally, which would have made a working D2 look
     broken. */
  if (d2Failures) {
    console.log("POSITIVE CONTROL FAILED: a well-formed bar was rejected. D2 is "
      + "too strict and would block a correct implementation.");
    for (const f of failures) console.log(`  - ${f}`);
    process.exit(3);
  }
  console.log("POSITIVE CONTROL PASSED: a well-formed collapsed bar is accepted.");
  process.exit(0);
}
if (mutation) {
  const hit = mutation === "--mutate-collapse-warning" ? d1Failures : d2Failures;
  if (hit) {
    console.log(`${hit} failure(s) in ${MUT[mutation]}, which is what the mutation is for.`);
    console.log(`CONTROL PASSED: ${MUT[mutation]} can detect its defect.`);
    process.exit(0);
  }
  console.log(`CONTROL FAILED: ${MUT[mutation]} did not notice. This control does `
    + `not work and must not be trusted.`);
  process.exit(3);
}
if (failures.length) {
  console.log(`${failures.length} failed`);
  for (const f of failures) console.log(`  - ${f}`);
  console.log("RED.");
  process.exit(1);
}
if (notPerformed.length) {
  console.log("NOT PERFORMED: " + notPerformed.join("; "));
  console.log("Reported as not performed, never as a pass.");
  process.exit(1);
}
console.log("GREEN.");
process.exit(0);
