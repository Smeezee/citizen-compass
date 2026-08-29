/**
 * P3/P7: does the ship page fit on one screen?

 *
 * RULE16: UNPROVEN - it computes a layout budget from the stylesheet's own numbers
 * at a stated viewport rather than measuring a render, so a page that lays
 * out differently from this arithmetic passes.
 * 
 * WORTH DISTINGUISHING FROM _verify_colour_headroom.mjs, which
 * re-implements the shader's maths and IS independent. There the answer is
 * fully determined by the constants and the formula, so a second
 * implementation is a genuine second opinion. Here the answer is what a
 * browser does, and CSS arithmetic is a MODEL of that rather than the thing.
 * _verify_camera_framing.mjs is the control that actually looks.
 *
 * WHAT THIS MEASURES, AND THE LIMIT SAID FIRST
 * --------------------------------------------
 * There is no browser on this machine and none was installed (rule 7), so
 * nothing here is a rendered layout. What it does is arithmetic on the page's
 * OWN DECLARED CSS: it reads the height, padding, border, gap and margin of
 * every block in the vertical stack out of the stylesheet the page ships, and
 * sums them at a given viewport.
 *
 * That is a MODEL, and it is stated as one. It is reproducible, it moves when
 * the CSS moves, and it is the only honest number available without a browser.
 * It cannot see text wrapping, so a heading that wraps to two lines is counted
 * as one - which means THE REAL PAGE IS AT LEAST AS TALL AS THIS SAYS, never
 * shorter. Reporting an under-estimate as a pass would be the wrong direction
 * to be wrong in, so every unknown is rounded up rather than down.
 *
 * Usage:  node checks/_verify_ship_page_fits.mjs
 *         node checks/_verify_ship_page_fits.mjs --json
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const PAGE = join(HERE, "..", "testing", "_src", "loadout.src.html");
const html = readFileSync(PAGE, "utf-8");
const css = (html.match(/<style>([\s\S]*?)<\/style>/) || ["", ""])[1];
/* Comments out, so a rule following one is still findable. */
const cssClean = css.replace(/\/\*[\s\S]*?\*\//g, "");
const JSON_OUT = process.argv.includes("--json");

/**
 * THE STYLESHEET AS IT APPLIES AT ONE VIEWPORT WIDTH.
 *
 * "Last declaration wins" is only true among rules that are actually in
 * effect. This file has three `@media(max-width:...)` blocks, and reading the
 * flat text made `rule(".cols")` return the 820px MOBILE override on every
 * lookup - so the model was reading a one-column layout while claiming to
 * measure the desktop one, and reporting a number with no relationship to the
 * CSS it was pointed at.
 *
 * That is the third time this tool has measured the wrong thing while looking
 * confident, which is a lesson about tools rather than about CSS: a measuring
 * instrument needs its own control. `--selftest` below is it.
 *
 * So: drop the media blocks that do not apply at `vw`, and append the ones
 * that do at the end, where a real cascade would put them.
 */
function sheetFor(vw) {
  const blocks = [];
  let base = cssClean.replace(
    /@media\s*\(([^)]*)\)\s*\{((?:[^{}]|\{[^{}]*\})*)\}/g,
    (all, cond, body) => {
      const mx = /max-width\s*:\s*(\d+)px/.exec(cond);
      const mn = /min-width\s*:\s*(\d+)px/.exec(cond);
      const applies = (!mx || vw <= +mx[1]) && (!mn || vw >= +mn[1]);
      if (applies) blocks.push(body);
      return "";
    });
  return base + "\n" + blocks.join("\n");
}

let passed = 0;
const failures = [];
function record(got, label, detail = "") {
  if (got) { passed++; if (!JSON_OUT) console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim()); if (!JSON_OUT) console.log(`  FAIL ${label} ${detail}`); }
}

/* ---- the smallest CSS reader that can answer the question --------------- */
let SHEET = cssClean;   // set per viewport by measure()

function rule(selector) {
  /* Last declaration wins among the rules IN EFFECT at this viewport.
   *
   * Comments are stripped first, and that is not tidiness: this used to anchor
   * on `(^|[},])`, so a rule written directly after a block comment - which is
   * most of them in this file - never matched at all. */
  const esc = selector.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp("(?:^|[};])\\s*" + esc + "\\s*\\{([^}]*)\\}", "gm");
  let m, body = null;
  while ((m = re.exec(SHEET))) body = m[1];
  return body;
}
function decl(selector, prop) {
  const body = rule(selector);
  if (!body) return null;
  const m = new RegExp("(?:^|;)\\s*" + prop + "\\s*:\\s*([^;]+)").exec(body);
  return m ? m[1].trim() : null;
}
/** px value of a length, resolving min()/vh/vw against the viewport. */
function px(v, vh, vw) {
  if (v == null) return 0;
  v = String(v).trim();
  const mn = /^min\(([^)]*)\)$/.exec(v);
  if (mn) return Math.min(...mn[1].split(",").map((x) => px(x, vh, vw)));
  const mx = /^max\(([^)]*)\)$/.exec(v);
  if (mx) return Math.max(...mx[1].split(",").map((x) => px(x, vh, vw)));
  if (v.endsWith("vh")) return parseFloat(v) / 100 * vh;
  if (v.endsWith("vw")) return parseFloat(v) / 100 * vw;
  if (v.endsWith("px")) return parseFloat(v);
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}
/** vertical padding+border of a rule. */
function chrome(selector, vh, vw) {
  const body = rule(selector) || "";
  let t = 0;
  const pad = /(?:^|;)\s*padding\s*:\s*([^;]+)/.exec(body);
  if (pad) {
    const parts = pad[1].trim().split(/\s+/).map((x) => px(x, vh, vw));
    t += parts.length === 1 ? parts[0] * 2
       : parts.length === 2 ? parts[0] * 2
       : parts.length === 3 ? parts[0] + parts[2]
       : parts[0] + parts[2];
  }
  for (const p of ["padding-top", "padding-bottom"]) {
    const d = decl(selector, p); if (d) t += px(d, vh, vw);
  }
  const bd = /(?:^|;)\s*border\s*:\s*([^;]+)/.exec(body);
  if (bd) t += px(bd[1].split(/\s+/)[0], vh, vw) * 2;
  const bb = decl(selector, "border-bottom");
  if (bb) t += px(bb.split(/\s+/)[0], vh, vw);
  for (const p of ["margin-top", "margin-bottom"]) {
    const d = decl(selector, p); if (d) t += px(d, vh, vw);
  }
  const mg = /(?:^|;)\s*margin\s*:\s*([^;]+)/.exec(body);
  if (mg) {
    const parts = mg[1].trim().split(/\s+/).map((x) => px(x, vh, vw));
    t += parts.length === 1 ? parts[0] * 2
       : parts.length === 2 ? parts[0] * 2
       : parts[0] + (parts[2] ?? parts[0]);
  }
  return t;
}

/**
 * The vertical stack of the DEFAULT ship page, in document order, as the
 * markup declares it. Each entry names the selector whose box it is and a
 * FLOOR for its content height - the smallest it can be with one line of what
 * it holds. Floors, so the total is a lower bound on the real page.
 */
const ROW_PX = 44;      // one component row, floor
const TILE_PX = 74;     // one stat tile, floor

function stack(vh, vw, shape) {
  const rows = [];
  const add = (name, sel, content) =>
    rows.push({ name, px: Math.round(content + chrome(sel, vh, vw)) });

  add("body top padding", "body", 0);
  add("header (name, prices, RSI)", ".top", 30);
  add("acquisition strip", ".acq", 22 + 19 + 3);

  if (shape === "columns") {
    /* THE THREE-COLUMN SHAPE. The tallest column sets the height, and a column
       that declares its own overflow is CAPPED at that height rather than
       growing - which is the whole mechanism by which the page stops
       scrolling. If it does not declare one, it grows and the page grows with
       it, so the model must not quietly assume the cap. */
    /* THE SELECTOR HAS TO BE THE ONE THE PAGE ACTUALLY USES. This looked for
       `.cols .col`, the page declares `.cols .col.left, .cols .col.right`, and
       the lookup returned null - so `capped` was false and the model silently
       fell back to "the list sets the height", reporting a number that had
       nothing to do with the CSS it was supposed to be reading. Twice now this
       tool has measured the wrong thing while looking confident. */
    const capped = /auto|scroll/.test(
      decl(".cols .col.left, .cols .col.right", "overflow-y") || "");
    const gridH = decl(".cols", "height");
    /* `calc(100vh - var(--chrome))` - resolve the variable from :root. */
    const chromeVar = px(decl(":root", "--chrome"), vh, vw);
    const calc = /calc\(\s*100vh\s*-\s*var\(--chrome\)\s*\)/.test(gridH || "")
      ? vh - chromeVar : px(gridH, vh, vw);
    const listed = capped && calc ? calc : ROW_PX * 21;
    add("three columns (tallest sets the height)", ".cols",
        Math.max(listed, px(decl(".cols", "min-height"), vh, vw)));
  } else {
    add("3D stage", "#cc-stage", px(decl("#cc-stage", "height"), vh, vw));
    add("marker honesty note", ".markernote", 19 * 4);
    add("stage wrapper margin", ".stagewrap", 0);
  }

  add("tab strip", ".tabs", 20);

  if (shape !== "columns") {
    /* THE OLD SHAPE put the readout and then the component list BELOW the tab
       strip, one after the other, with nothing capping either. */
    add("readout block", ".outcome", TILE_PX * 2 + 26 + 90);
    add("components column (21 open slots)", ".col", ROW_PX * 21);
  }
  return rows;
}

/** Which shape is the page in? Detected from the CSS, not assumed. */
function shapeOf() { return rule(".cols") ? "columns" : "stacked"; }

function measure(vw, vh) {
  SHEET = sheetFor(vw);          // the cascade as it applies at THIS width
  const shape = shapeOf();
  const rows = stack(vh, vw, shape);
  const total = rows.reduce((t, r) => t + r.px, 0);
  const fold = rows.slice(0, shape === "columns" ? 3 : 6)
                   .reduce((t, r) => t + r.px, 0);
  return { vw, vh, shape, rows, total, aboveFold: fold, left: vh - fold,
           overflow: total - vh };
}

const A = measure(1920, 1080);
const B = measure(1366, 768);

if (JSON_OUT) {
  console.log(JSON.stringify({ "1920x1080": A.aboveFold, "1366x768": B.aboveFold }));
  process.exit(0);
}

console.log("=".repeat(74));
console.log("P3/P7 - how much vertical space the ship page spends before its content");
console.log("=".repeat(74));
console.log("MODELLED FROM THE PAGE'S OWN CSS, not rendered. No browser exists on");
console.log("this machine (rule 7). Text wrapping is not modelled, so every figure");
console.log("here is a FLOOR - the real page is at least this tall, never shorter.");
for (const [label, m] of [["1920 x 1080", A], ["1366 x 768", B]]) {
  console.log(`\n--- ${label} ---`);
  for (const r of m.rows) if (r.px) console.log(`  ${String(r.px).padStart(5)}px  ${r.name}`);
  console.log(`  ${"-".repeat(5)}`);
  console.log(`  ${"=".repeat(5)}`);
  console.log(`  ${String(m.total).padStart(5)}px  TOTAL DOCUMENT HEIGHT (floor)`);
  console.log(`  ${String(m.vh).padStart(5)}px  viewport`);
  console.log(`  ${m.overflow > 0 ? String(m.overflow).padStart(5) + "px  OVERFLOWS - the page scrolls by this much"
                                  : String(-m.overflow).padStart(5) + "px  spare - the page FITS"}`);
}

console.log("\n--- the instrument's own control ---");
{
  /* A MEASURING TOOL NEEDS ITS OWN CHECK, and this one has earned it. While
     being written it silently measured the wrong thing three separate times:
     a selector anchored so it never matched after a comment, a selector that
     did not exist in the page at all, and the 820px mobile media block winning
     every lookup. Each time it produced a confident, plausible, wrong number.
     Nothing downstream could have told the difference. */
  SHEET = sheetFor(1920);
  const wide = rule(".cols");
  SHEET = sheetFor(800);
  const narrow = rule(".cols");
  record(wide !== narrow,
    "the sheet read at 1920 differs from the sheet read at 800 - media queries "
    + "are applied, not flattened",
    `wide=${JSON.stringify((wide || "").slice(0, 36))} narrow=${JSON.stringify((narrow || "").slice(0, 36))}`);
  record(/minmax/.test(wide || ""),
    "at 1920 it reads the THREE-column rule", (wide || "").slice(0, 46));
  record(/1fr/.test(narrow || "") && !/minmax\(280px/.test(narrow || ""),
    "and at 800 the single-column one", (narrow || "").slice(0, 46));
  SHEET = sheetFor(1920);
  record(px(decl(":root", "--chrome"), 1080, 1920) > 0,
    "and it resolves a custom property rather than reading it as zero",
    `--chrome = ${decl(":root", "--chrome")}`);
  record(chrome(".top", 1080, 1920) > 0 && chrome(".tabs", 1080, 1920) > 0,
    "and it finds padding and margins on rules that follow comments");
}

console.log("\n--- the assertions ---");
/* THE TARGET: enough room left below the fixed stack for a usable column of
   components. A component row is ~44px; fewer than four visible means the
   left column is a scroll bar with a hint of content, which is what "the user
   never has to scroll" is about. */
console.log(`  shape detected from the CSS: ${A.shape}`);
record(A.total <= A.vh,
  "P7: at 1920x1080 the whole page fits without vertical scroll",
  `${A.total}px of ${A.vh} - overflows by ${A.overflow}px`);
record(A.shape === "columns",
  "P1: the page is in the three-column shape");
/* 1366x768 is REPORTED, not failed on, per the order. */
console.log(`  note  at 1366x768 the page is ${B.total}px of 768. `
  + `${B.overflow > 0 ? `It overflows by ${B.overflow}px - that is the next decision.`
                      : `It fits, with ${-B.overflow}px spare.`}`);

console.log("");
if (failures.length) {
  console.log(`FAILED: ${failures.length}`);
  for (const f of failures) console.log("  - " + f);
  process.exit(1);
}
console.log(`PASSED: ${passed} assertions.`);
process.exit(0);
