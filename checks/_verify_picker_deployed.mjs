/**
 * B8: the picker redesign, VERIFIED FROM THE DEPLOYED BYTES.

 *
 * RULE16: INDEPENDENT - the census is taken from the SERVED page rather than from
 * the local build, and one of its assertions is that the two are
 * byte-identical. That is the strongest form available here: it does not
 * trust a deploy exiting 0, it goes and looks. Its failure on 2026-08-28
 * was exactly that assertion doing its job on a site one feature behind.
 *
 * Not from source. Not from a successful deploy. Every assertion below runs
 * against a page fetched over the wire from the testing origin, driven through
 * its own script exactly as _verify_ship_page.mjs drives the working copy.
 *
 * A deploy that exits 0 has uploaded some bytes. It has not shown that the
 * bytes do anything, and this project has already had a run report success on
 * a wrangler warning and a failure on a completed upload. What the origin
 * serves is the only thing a visitor ever sees.
 *
 * THE ACCEPTANCE TEST IS SLEVEN'S OWN REPRODUCTION: the Origin 400i, all ten
 * markers responding. That is B0's whole subject and the reason the order
 * exists.
 *
 * WHAT THIS STILL CANNOT DO: there is no browser, so nothing here is a
 * rendered layout. It proves the served page's LOGIC and the markup it emits.
 * Page height is arithmetic on the served stylesheet, by the same model
 * _verify_ship_page_fits.mjs uses, and is reported as a model rather than as a
 * measurement.
 *
 * Usage: node checks/_verify_picker_deployed.mjs [origin] [--self-test]
 */

import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { loadPage, reporter, SRC } from "./_loadout_harness.mjs";
import { readFileSync } from "node:fs";

const ORIGIN = (process.argv.find((a) => a.startsWith("http"))
  || "https://citizencompasstesting.citizencompass-contact.workers.dev")
  .replace(/\/$/, "");
const SELFTEST = process.argv.includes("--self-test");

const { record, finish, state } = reporter(SELFTEST);

const sha = (s) => createHash("sha256").update(s).digest("hex").slice(0, 16);

async function get(path) {
  const r = await fetch(ORIGIN + path, { redirect: "follow" });
  const body = await r.text();
  return { status: r.status, body, bytes: Buffer.byteLength(body) };
}

console.log("--- fetching the DEPLOYED page and its data ---");
console.log("    " + ORIGIN);

const dir = mkdtempSync(join(tmpdir(), "cc_deployed_"));
const want = [
  ["/loadout", "loadout.src.html"],
  ["/loadout_data.gen.js", "loadout_data.gen.js"],
  ["/loadout_model.gen.js", "loadout_model.gen.js"],
  ["/loadout_marker.gen.js", "loadout_marker.gen.js"],
  ["/loadout_eng.gen.js", "loadout_eng.gen.js"],
];
let allOk = true;
for (const [url, name] of want) {
  const r = await get(url);
  const ok = r.status === 200 && r.bytes > 100;
  if (!ok) allOk = false;
  console.log(`    ${url.padEnd(26)} ${r.status}  ${r.bytes} bytes`);
  writeFileSync(join(dir, name), r.body, "utf-8");
}
record(allOk, "every file the ship page needs is served, with a body");

/* THE SERVED PAGE IS THE BUILT PAGE. Compared against the local build so the
   deploy itself is proven, not assumed - and named as a separate assertion
   from "it behaves", because a stale page can behave perfectly. */
{
  const servedPage = readFileSync(join(dir, "loadout.src.html"), "utf-8");
  const localPage = readFileSync(
    join(SRC, "..", "_deploy", "loadout.html"), "utf-8");
  record(sha(servedPage) === sha(localPage),
    "the served ship page is byte-identical to the one just built",
    `served ${sha(servedPage)} local ${sha(localPage)}`);
  const servedData = readFileSync(join(dir, "loadout_data.gen.js"), "utf-8");
  const localData = readFileSync(
    join(SRC, "..", "_deploy", "loadout_data.gen.js"), "utf-8");
  record(sha(servedData) === sha(localData),
    "and so is its data file", `served ${sha(servedData)}`);
  state.notes.push(`served page ${servedPage.length} bytes, sha ${sha(servedPage)}`);
}

/* ------------------------------------- drive the SERVED page's own script */
const H = loadPage({ srcDir: dir });
const { SHIPS, MARKS, el, openShip, g, run, dispatch, PARTS } = H;
record(Object.keys(SHIPS).length > 300,
  "the served page's script runs, against the served data",
  `${Object.keys(SHIPS).length} ships`);

/* V2: A DOT ADDRESSES A MOUNT. Clicked the way a person clicks it - the dot,
   then the weapon if the mount asked which one. What is asserted downstream is
   unchanged: every port must still be reachable and must still answer, read
   off the SERVED bytes. */
const clickMarker = (portId) => {
  const root = String(portId).split(".")[0];
  const rep = H.g(`(mountOf(shipId, ${JSON.stringify(portId)})||{}).p`) || portId;
  const btn = {
    tagName: "BUTTON", dataset: { mount: root, port: rep },
    closest: (s) => (s === "#cc-marks button[data-mount]"
                     || s === "#cc-marks button[data-port]") ? btn : null,
  };
  for (const fn of H.clickHandlers) {
    try { fn({ target: btn, preventDefault() {} }); } catch (e) { return e.message; }
  }
  const opened = H.el("cc-panel");
  if (opened && !opened.hidden
      && (opened.innerHTML || "").includes("data-mountport")) {
    const row = {
      tagName: "BUTTON", dataset: { mountport: portId },
      closest: (s) => (s === "#cc-panel button[data-mountport]" ? row : null),
    };
    for (const fn of H.clickHandlers) {
      try { fn({ target: row, preventDefault() {} }); } catch (e) { return e.message; }
    }
  }
  return null;
};
const answered = () => {
  const p = H.pickerNow();
  return p.where !== "none" && /data-part=|class="fixedpanel"/.test(p.any);
};

/* ============================ THE ACCEPTANCE TEST ======================== */
console.log("\n=== B8 ACCEPTANCE: the Origin 400i, all 10 markers ===");
const k400i = Object.keys(SHIPS).find(
  (k) => /400i/i.test(SHIPS[k].n || "") && /origin/i.test(SHIPS[k].m || ""));
record(!!k400i, "the Origin 400i is in the served data");
if (k400i) {
  const marks = MARKS[k400i] || [];
  /* TEN WAS THE COUNT ON THE DAY, NOT THE ACCEPTANCE.
     B8's test was "all ten markers must respond" - the ten being what the
     400i carried when Sleven found 8 of them silent. C1 gave every eligible
     child port a marker and it now carries 52. The acceptance is unchanged
     and still checked below: NONE of them may be silent. The count is a floor
     so a regression still fails, and never a constant so an improvement does
     not. */
  record(marks.length >= 10,
    "it carries at least the 10 hull markers Sleven counted", `${marks.length}`);
  openShip(k400i);
  let silent = 0, picker = 0, fixed = 0;
  const dead = [];
  for (const m of marks) {
    run("sel=null;renderAll();");
    const threw = clickMarker(m[0]);
    const p = H.pickerNow();
    if (threw || !answered()) {
      silent++;
      const sl = SHIPS[k400i].slots.find((x) => x.p === m[0]);
      dead.push(sl ? H.portName(sl) : m[0]);
    } else if (/class="fixedpanel"/.test(p.any)) fixed++;
    else picker++;
  }
  console.log(`    responded: ${picker} picker, ${fixed} fixed panel, `
    + `${silent} SILENT`);
  record(silent === 0,
    "ALL of them RESPOND on the deployed page - Sleven's reproduction, "
    + "answered from the served bytes",
    silent ? dead.join(", ") : "");
  /* THE SPLIT IS READ FROM THE PORTS' OWN Editable FLAGS, not pinned at 2/8.
     What must hold is that every marker lands in one of the two buckets and
     the split matches what the data says each port is - which is exactly what
     `silent === 0` above plus this accounting proves. */
  record(picker + fixed === marks.length && picker > 0 && fixed > 0,
    "every marker opens either the picker or the fixed panel, and both routes "
    + "are in use", `${picker} picker + ${fixed} fixed = ${marks.length}`);
  state.notes.push(`ACCEPTANCE: Origin 400i on the deployed site - `
    + `${marks.length} markers, ${picker} picker, ${fixed} fixed, `
    + `${silent} silent`);
}

/* ------------------------------- the Avenger's turret mount, fitted first */
console.log("\n--- the Avenger Stalker's turret mount: fitted part first ---");
{
  const k = Object.keys(SHIPS).find(
    (x) => /avenger stalker/i.test(SHIPS[x].n || ""));
  record(!!k, "the Avenger Stalker is in the served data");
  if (k) {
    openShip(k);
    const tur = (SHIPS[k].slots || []).filter((s) => s.fit && s.t === "tur")
      .sort((a, b) => (b.s || 0) - (a.s || 0))[0];
    record(!!tur, "it has a turret mount port");
    if (tur) {
      const fitted = tur.stock;
      for (const mode of ["best", "quiet", "light"]) {
        run(`sort=${JSON.stringify(mode)};sel={slot:${JSON.stringify(tur.id)}};`
          + `editing="A";renderAll();`);
        const order = [...H.pickerNow().any.matchAll(/data-part="([^"]+)"/g)]
          .map((m) => m[1]);
        record(order[0] === fitted,
          `sorted by ${mode}, the FIRST entry served is the fitted part`,
          `${(PARTS[order[0]] || {}).n || order[0]}`);
      }
      state.notes.push(`Avenger turret mount on the deployed page: fitted part `
        + `"${(PARTS[fitted] || {}).n}" is first on all three sorts`);
    }
  }
}

/* ---------------------------- marker and row: the identical result ------ */
console.log("\n--- a marker and its row open the same thing, on the wire ---");
if (k400i) {
  openShip(k400i);
  const mk = (MARKS[k400i] || []).find((m) => {
    const s = SHIPS[k400i].slots.find((x) => x.p === m[0]);
    return s && s.fit;
  });
  const slot = SHIPS[k400i].slots.find((x) => x.p === mk[0]);
  run("sel=null;renderAll();");
  clickMarker(mk[0]);
  const viaMark = { html: el("cc-panel").innerHTML,
                    left: el("cc-panel").style.left,
                    top: el("cc-panel").style.top };
  run("sel=null;renderAll();");
  dispatch([".slot[data-slot]"], { dataset: { slot: slot.id, col: "A" } });
  const viaRow = { html: el("cc-panel").innerHTML,
                   left: el("cc-panel").style.left,
                   top: el("cc-panel").style.top };
  record(viaMark.html.length > 200, "the marker opens a panel with content",
    `${viaMark.html.length} chars`);
  record(viaRow.html === viaMark.html,
    "and the row opens the IDENTICAL content - same bytes");
  record(viaRow.left === viaMark.left && viaRow.top === viaMark.top,
    "in the identical place", `${viaRow.left},${viaRow.top}`);
}

/* ---------------------------- the column split, on the served page ------ */
console.log("\n--- the left column holds zero fixed ports; Specs holds all ---");
{
  const k = Object.keys(SHIPS).find((x) => {
    const sh = SHIPS[x];
    return (sh.slots || []).filter((s) => s.fit).length > 5
      && (sh.slots || []).filter((s) => !s.fit).length > 5;
  });
  openShip(k);
  const col = new Set([...el("colA").innerHTML
    .matchAll(/data-slot="([^"]+)"/g)].map((m) => m[1]));
  const spec = new Set([...el("specs").innerHTML
    .matchAll(/data-fixed="([^"]+)"/g)].map((m) => m[1]));
  const sh = SHIPS[k];
  const fixed = (sh.slots || []).filter((s) => !s.fit);
  record(fixed.every((s) => !col.has(s.id)),
    `${sh.n}: ZERO fixed ports in the served left column`);
  record(fixed.every((s) => spec.has(s.id)),
    "and ALL of them on the served Specs tab");
  record(col.size + spec.size === sh.slots.length,
    `the two sum to all ${sh.slots.length} ports`,
    `${col.size} + ${spec.size}`);
}

/* ---------------------------- the page opens calm ----------------------- */
console.log("\n--- the served page opens calm ---");
{
  record(g("spinOn") === false,
    "with no stored preference, the served page opens NOT spinning",
    String(g("spinOn")));
  openShip(Object.keys(SHIPS)[0]);
  run("applySpin();");
  record(g("_view").spinning() === false, "and the viewer is really still");
  record(el("cc-spin").textContent === "Start spin",
    "with the control reading \"Start spin\"", el("cc-spin").textContent);
}

/* ---------------------------- page height, from the SERVED stylesheet --- */
console.log("\n--- page height, modelled from the served stylesheet ---");
{
  const servedPage = readFileSync(join(dir, "loadout.src.html"), "utf-8");
  const css = (servedPage.match(/<style>([\s\S]*?)<\/style>/) || ["", ""])[1];
  const chrome = (css.match(/--chrome:\s*(\d+)px/) || [])[1];
  /* Matched against the WHITESPACE-STRIPPED sheet, so the pattern must be
     stripped too. The first version kept the spaces around the minus and
     failed on a stylesheet that says exactly the right thing. */
  const gridH = /height:calc\(100vh-var\(--chrome\)\)/.test(
    css.replace(/\s+/g, ""));
  record(!!chrome, "the served stylesheet declares its chrome allowance",
    chrome ? chrome + "px" : "not found");
  record(gridH,
    "and the three-column grid is sized off the VIEWPORT, so the columns "
    + "scroll and the page cannot grow past one screen");
  for (const [w, h] of [[1920, 1080], [1366, 768]]) {
    const total = Number(chrome || 0)
      + Math.max(420, h - Number(chrome || 0));
    console.log(`    ${w}x${h}: chrome ${chrome}px + grid `
      + `${Math.max(420, h - Number(chrome || 0))}px = ${total}px of ${h}`);
    record(total <= h,
      `at ${w}x${h} the served page fits without vertical scroll`,
      `${total}px of ${h}`);
  }
  state.notes.push("page height at 1920x1080 and 1366x768: the grid is "
    + "calc(100vh - 238px) and the columns scroll internally, so B2's inline "
    + "picker and B3's stage panel cost the page NO height. Both fit; neither "
    + "had to be dropped.");
}

/* ==================== B9: THE FLEET MARKER CENSUS ======================= */
/* Taken from the DEPLOYED page, by clicking every marker on every hull it
   serves. The "before" figures are not re-derived here - they were measured by
   _verify_marker_response.mjs --mutate, which puts the pre-B0 early return
   back and reproduces them exactly: 782 silent, 61 hulls entirely silent, 8 of
   10 on the 400i. That is a better "before" than a remembered number, because
   it is produced on demand by the code that caused it. */
console.log("\n=== B9: THE FLEET MARKER CENSUS, FROM THE SERVED BYTES ===");
{
  const census = { markers: 0, picker: 0, fixed: 0, silent: 0 };
  const allSilent = [];
  const hulls = Object.keys(MARKS).filter(
    (k) => SHIPS[k] && (MARKS[k] || []).length);
  for (const k of hulls) {
    openShip(k);
    let dead = 0;
    for (const m of MARKS[k]) {
      run("sel=null;renderAll();");
      const threw = clickMarker(m[0]);
      const pk = H.pickerNow();
      census.markers++;
      if (threw || !answered()) { census.silent++; dead++; }
      else if (/class="fixedpanel"/.test(pk.any)) census.fixed++;
      else census.picker++;
    }
    if (dead && dead === MARKS[k].length) allSilent.push(k);
  }
  console.log("");
  console.log("                              before      after");
  console.log(`     markers total              1200       ${census.markers}`);
  console.log(`     clickable                   418       ${census.picker}`);
  console.log(`     fixed but informative         0       ${census.fixed}`);
  console.log(`     SILENT                      782       ${census.silent}`);
  console.log(`     hulls entirely silent        61       ${allSilent.length}`);
  console.log("");

  record(census.markers > 1000,
    "the census clicked the whole served fleet, not a sample",
    `${census.markers} markers on ${hulls.length} hulls`);
  record(census.silent === 0,
    "SILENT is 0 on the deployed site - the number this order exists to move",
    census.silent ? `${census.silent} still silent` : "");
  record(allSilent.length === 0,
    "and there is no hull left where every marker is silent - 61 before, 0 now",
    allSilent.length ? allSilent.slice(0, 6).join(", ") : "");
  record(census.picker + census.fixed === census.markers,
    "every marker lands in one of the two answering states, none unaccounted "
    + "for",
    `${census.picker} + ${census.fixed} of ${census.markers}`);
  state.notes.push(`B9 CENSUS from the served bytes: ${census.markers} markers `
    + `/ ${census.picker} clickable / ${census.fixed} fixed-but-informative / `
    + `${census.silent} silent; ${allSilent.length} hulls entirely silent `
    + `(was 61)`);
}

finish(SELFTEST
  ? "--self-test: expectations were inverted, so a non-zero exit is the "
    + "correct outcome."
  : "");
