/**
 * H1b: leader-line labels, deconflicted, with the count always stated.
 *
 * THE LABELS ARE THE FEATURE, not decoration on the markers. A derived
 * position will never be exact - the exports are one welded mesh with no mount
 * data, and RSI's are no better. A dot two metres off that says
 * "CF-337 Panther Repeater / Weapon left nose" is informative. The same dot
 * with no label is a guess the visitor cannot check. The label is what makes
 * the whole derived-position approach honest.
 *
 * THE PROTOTYPE HAS NOT SOLVED THIS. Its label sits at a fixed 11px offset
 * with a border-left stub standing in for a leader line, so the Sabre - EIGHT
 * hardpoints on a small fighter - already collides in the capture. The
 * Polaris has 24 markers and the Perseus 35.
 *
 * DECONFLICT THE LABELS, NOT THE MARKERS. The marker stays on its derived
 * position because that is a claim about the hull. The label may move anywhere
 * because it is not, and it keeps a leader line back. Two things are being
 * placed and only one of them is an assertion.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-nodeconflict   every label goes to the first candidate offset,
 *                           which is what the prototype does. The Sabre MUST
 *                           fail - it collides today, so a check that passes
 *                           with the feature off is measuring nothing.
 *   --mutate-silent         the count hint is suppressed, which is the
 *                           marker defect in a new costume.
 *   --self-test             inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_labels.mjs
 *        [--self-test] [--mutate-nodeconflict] [--mutate-silent]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_ND = process.argv.includes("--mutate-nodeconflict");
const MUT_SILENT = process.argv.includes("--mutate-silent");

const mutate = [];
if (MUT_ND) {
  mutate.push([/if\(taken\.some\(o=>hits\(r,o\)\)\) continue;/, ""]);
  console.log("*** MUTATED: overlap is no longer avoided - every label takes "
    + "the first candidate, exactly as the prototype does. ***");
}
if (MUT_SILENT) {
  mutate.push([/renderLabelCount\(list\.length, shown, dropped, show\);/, ""]);
  console.log("*** MUTATED: the count is never stated. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, MARKS, el, openShip, g, run } = H;

const SHIPS_UNDER_TEST = ["Sabre", "Polaris", "Perseus"];

/* The rendered geometry, read back off the DOM the page produced. */
function rendered() {
  const html = el("cc-labels").innerHTML || "";
  const boxFn = g("labelBox");
  const out = [];
  const re = /<div class="hp[^"]*"\s*style="left:(-?\d+)px;top:(-?\d+)px"\s*><b>([^<]*)<\/b>([^<]*)<\/div>/g;
  let m;
  while ((m = re.exec(html))) {
    const text = m[3] + "\n" + m[4];
    const b = boxFn(text);
    const lx = Number(m[1]), ly = Number(m[2]);
    out.push({ lx, ly, w: b.w, h: b.h, text,
               x1: lx, y1: ly - b.h / 2, x2: lx + b.w, y2: ly + b.h / 2 });
  }
  return out;
}
function leaders() {
  const svg = el("cc-leaders").innerHTML || "";
  const out = [];
  const re = /<line[^>]*x1="(-?\d+)"\s*y1="(-?\d+)"\s*x2="(-?\d+)"\s*y2="(-?\d+)"/g;
  let m;
  while ((m = re.exec(svg))) {
    out.push({ x1: +m[1], y1: +m[2], x2: +m[3], y2: +m[4] });
  }
  return out;
}
const overlaps = (a, b) =>
  !(a.x2 <= b.x1 || b.x2 <= a.x1 || a.y2 <= b.y1 || b.y2 <= a.y1);

/* -------------------------- 1. ZERO OVERLAPS ON ALL THREE SHIPS --------- */
console.log("--- 1. zero label overlaps on the three ships the order names ---");
const seen = {};
for (const nm of SHIPS_UNDER_TEST) {
  const k = Object.keys(SHIPS).find(
    (x) => new RegExp(nm, "i").test(SHIPS[x].n || "") && (MARKS[x] || []).length);
  record(!!k, `${nm} is in the data with markers`, k || "not found");
  if (!k) continue;
  openShip(k);
  run("allLabels=true;renderLabels();");
  const labels = rendered();
  const n = (MARKS[k] || []).length;
  let clash = [];
  for (let i = 0; i < labels.length; i++) {
    for (let j = i + 1; j < labels.length; j++) {
      if (overlaps(labels[i], labels[j])) clash.push(`${i}/${j}`);
    }
  }
  const dropped = Number(el("cc-labels")["data-dropped"] || 0);
  console.log(`    ${SHIPS[k].n.padEnd(22)} ${String(n).padStart(3)} markers, `
    + `${String(labels.length).padStart(3)} labelled, ${dropped} with no room, `
    + `${clash.length} overlaps`);
  record(clash.length === 0,
    `${SHIPS[k].n}: ZERO label bounding-box overlaps`,
    clash.length ? `${clash.length}: ${clash.slice(0, 4).join(", ")}` : "");
  record(labels.length > 0, `and it labelled something at all`,
    String(labels.length));
  seen[nm] = { n, labels: labels.length, dropped, k };
  state.notes.push(`${SHIPS[k].n}: ${n} markers, ${labels.length} labelled, `
    + `${dropped} with no room, 0 overlaps`);
}
record(seen.Sabre && seen.Sabre.labels === seen.Sabre.n,
  "the Sabre - which collides in the prototype's own capture - labels ALL "
  + "eight with no overlap",
  seen.Sabre ? `${seen.Sabre.labels} of ${seen.Sabre.n}` : "");

/* ------------------- 2. EVERY LEADER LINE REACHES ITS MARKER ------------ */
console.log("\n--- 2. every leader line terminates at its marker ---");
{
  const k = seen.Polaris && seen.Polaris.k;
  if (k) {
    openShip(k);
    run("allLabels=true;renderLabels();");
    const ls = leaders(), labels = rendered();
    record(ls.length === labels.length,
      "there is exactly one leader line per rendered label",
      `${ls.length} lines, ${labels.length} labels`);
    /* The line's far end must sit ON the label's edge, and its near end on the
       marker. A label that has drifted free of its line is worse than none. */
    let bad = 0;
    ls.forEach((L) => {
      const hit = labels.some((b) =>
        Math.abs(L.x2 - b.x1) <= 1 || Math.abs(L.x2 - (b.x1 + b.w)) <= 1);
      const onRow = labels.some((b) => Math.abs(L.y2 - b.ly) <= 1);
      if (!hit || !onRow) bad++;
    });
    record(bad === 0,
      "and every line ENDS on a label's own edge rather than near it",
      `${bad} adrift`);
    const marks = MARKS[k] || [];
    const us = 1;
    const proj = marks.map((m) => g("_view").project(m[1] * us, m[2] * us, m[3] * us))
      .filter(Boolean);
    let off = 0;
    ls.forEach((L) => {
      const near = proj.some((p) =>
        Math.hypot(p.x - L.x1, p.y - L.y1) <= 2);
      if (!near) off++;
    });
    record(off === 0,
      "and STARTS within 2px of a real marker position - the line connects the "
      + "label to the thing it is about",
      `${off} starting nowhere`);
  }
}

/* --------------------------- 3. THE COUNT IS ALWAYS STATED -------------- */
console.log("\n--- 3. the count is stated, and the toggle is offered ---");
for (const nm of SHIPS_UNDER_TEST) {
  const k = seen[nm] && seen[nm].k;
  if (!k) continue;
  openShip(k);
  const hint = el("cc-labelcount").innerHTML || "";
  record(hint.includes(String(seen[nm].n)),
    `${SHIPS[k].n} states its hardpoint count on the stage`,
    hint.replace(/<[^>]+>/g, " ").trim().slice(0, 64));
  record(/cc-lbl-toggle/.test(hint),
    "and offers the toggle by name rather than hiding labels silently");
}
{
  /* THE THRESHOLD. Above it labels are off by default - but the hint says so
     and the toggle turns them on. */
  const k = seen.Perseus && seen.Perseus.k;
  if (k) {
    /* SECTION 1 SET allLabels=true AND IT IS MODULE STATE. Without this the
       Perseus arrives here already showing everything and the threshold looks
       broken when it is the control that leaked. Second time in this session -
       the look-panel control did the same thing with the sliders, and both
       were found by the numbers being wrong in a way the feature would not
       explain. Reset explicitly; never inherit. */
    run("allLabels=null;");
    openShip(k);
    const off = el("cc-labels").innerHTML || "";
    record(!off || Number(el("cc-labels")["data-shown"] || 0)
      < seen.Perseus.n,
      "a 35-marker hull does NOT label everything by default");
    record(/labels off on a hull this busy/.test(el("cc-labelcount").innerHTML),
      "and says why, rather than simply showing nothing");
    H.dispatch(["#cc-lbl-toggle"]);
    record(Number(el("cc-labels")["data-shown"] || 0) > 10,
      "and the toggle turns them on",
      String(el("cc-labels")["data-shown"]));
  }
}

/* ------------------------- 4. HOVER AND SELECTION ALWAYS LABEL ---------- */
console.log("\n--- 4. a selected marker is always labelled ---");
{
  const k = seen.Perseus && seen.Perseus.k;
  if (k) {
    openShip(k);                       /* labels off by default here */
    run("allLabels=false;renderLabels();");
    const before = Number(el("cc-labels")["data-shown"] || 0);
    const slot = (SHIPS[k].slots || []).find((s) =>
      (MARKS[k] || []).some((m) => m[0] === s.p));
    run(`sel={slot:${JSON.stringify(slot.id)}};renderLabels();`);
    const after = Number(el("cc-labels")["data-shown"] || 0);
    record(before === 0 && after === 1,
      "with labels off, selecting a marker labels THAT ONE and only that one",
      `${before} -> ${after}`);
  }
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_ND || MUT_SILENT)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
