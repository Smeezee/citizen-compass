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
const MUT_LATE = process.argv.includes("--mutate-latelabels");

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
if (MUT_LATE) {
  /* E8's defect, put back: the model arrives and nothing draws the labels, so
     they wait for whatever re-renders the page next. */
  mutate.push([/renderLabels\(\); \},/, "},"]);
  console.log("*** MUTATED: the model's onLoad no longer renders labels - "
    + "they wait for the next renderAll(), which is what a marker click "
    + "supplies. ***");
}

/* B8's pattern: CC_PAGE / CC_SRCDIR point this at bytes fetched from the
   origin, so the same assertions can be run against what a visitor is sent.
   Passing them and having them ignored is worse than not having them - the
   run would report a served-bytes pass it never performed - so they are
   threaded through rather than left to the harness's defaults. */
const H = loadPage({ mutate,
  srcDir: process.env.CC_SRCDIR || null,
  pageFile: process.env.CC_PAGE || null });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, MARKS, el, openShip, g, run } = H;

const SHIPS_UNDER_TEST = ["Sabre", "Polaris", "Perseus"];

/* THE RENDERED GEOMETRY, READ OFF THE ELEMENTS AND NOT OFF THE MARKUP STRING.

   E11 moved the positions out of the innerHTML and onto the elements: the
   markup is written once and every frame after that writes only `style.left`
   and `style.top`, which is what makes 35 labels affordable at 60fps. Scraping
   the string would therefore report the placeholder `left:0px` the render
   emitted and never the position the page actually put the label at - a
   control reading a number that had stopped being the answer.

   The harness models children now, which is what makes this possible. Before
   E11 it returned [] for every element's children, and no control had ever
   seen where anything was put. */
function rendered() {
  const boxFn = g("labelBox");
  const out = [];
  for (const kid of el("cc-labels").children) {
    if ((kid.style.display || "") === "none") continue;
    /* The harness decodes entities the way a browser does, so `&#10;` has
       already become a newline and `&quot;` a quote by the time it lands
       here. Decoding again in each control would be a second answer to what
       an attribute says. */
    const text = String(kid._attrs["data-text"] || "");
    const b = text ? boxFn(text) : { w: 0, h: 0 };
    const lx = parseFloat(kid.style.left) || 0;
    const ly = parseFloat(kid.style.top) || 0;
    out.push({ lx, ly, w: b.w, h: b.h, text,
               x1: lx, y1: ly - b.h / 2, x2: lx + b.w, y2: ly + b.h / 2 });
  }
  return out;
}
function leaders() {
  const out = [];
  for (const ln of el("cc-leaders").children) {
    if (String(ln.getAttribute("stroke-opacity") || "1") === "0") continue;
    out.push({ x1: +ln.getAttribute("x1"), y1: +ln.getAttribute("y1"),
               x2: +ln.getAttribute("x2"), y2: +ln.getAttribute("y2") });
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
  /* V2: mounts, not ports - one label per physical mount. */
  const n = Number(g(`mountsFor(${JSON.stringify(k)}).length`));
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
    /* R1b REPLACED THIS SENTENCE, and the replacement is the point of the
       item: "a hull this busy" is a status caption a reader skims past, which
       is how a working Reclaimer got reported as a broken page. The line
       states a NUMBER now - how many have no room - and offers the way past
       it. Asserted on what the page must say rather than on the old wording,
       so this reads as a requirement and not as a spelling. */
    const hint = el("cc-labelcount").innerHTML || "";
    record(/\d+\s+(?:has|have)\s+no room/.test(hint),
      "and says why in a number a reader can check, rather than simply "
      + "showing nothing", hint.replace(/<[^>]*>/g, " ").trim());
    record(/show all labels anyway/.test(hint),
      "and offers the way past it");
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

/* ------------------- 5. E8: THE LABELS ARRIVE WITH THE MODEL ------------- */
/* Sleven, on the Anvil C8R Pisces Rescue: "that wasn't there until I clicked
   one of the hardpoints, and then it popped up. And then when I clicked out,
   it stayed."

   THIS SECTION EXISTS BECAUSE THE REST OF THIS FILE COULD NOT SEE IT. Every
   other section drives a viewer whose `current` is already set, which is the
   state AFTER the model has loaded - so the whole file was measuring the half
   of the timeline that worked. The gap is between renderAll() and the model
   arriving, and reproducing it needs a viewer that has not finished loading.

   Same shape as E7a, one file over: a stub that was faithful about everything
   the assertions looked at. */
console.log("\n--- 5. labels are there before anything is clicked ---");
{
  /* Sleven's own hull if it is in the data, else any hull under the threshold
     with markers - and the one used is NAMED, because "a hull" is not a
     reproduction. */
  const key = g(`(function(){
    var want = Object.keys(SHIPS).filter(function(k){
      var m = (typeof MARKS !== 'undefined' && MARKS[k]) || [];
      return m.length > 0 && m.length <= 14 && modelUrl(k);
    });
    var pisces = want.filter(function(k){
      return /pisces/i.test(SHIPS[k].n || k); })[0];
    return pisces || want[0] || null;
  })()`);
  record(!!key, "a hull under the label threshold, with markers and a model",
    key ? `${g(`SHIPS[${JSON.stringify(key)}].n`)} `
      + `(${(MARKS[key] || []).length} markers)` : "none found");

  if (key) {
    /* A VIEWER THAT HAS NOT FINISHED LOADING. `current` is null, and load()
       keeps the callback instead of calling it - which is exactly where the
       page stood when Sleven looked at it. */
    run(`shipId=${JSON.stringify(key)}; reset(); resetView(); sel=null;
      __loadCb=null;
      (function(){
        var base=_view, v={};
        for (var k in base) v[k]=base[k];
        v.current=null;
        v.load=function(u,cb){ __loadCb=cb; return 1; };
        _view=v;
      })();
      _modelFor=null;
      renderAll();`);
    const beforeLoad = el("cc-labels").innerHTML || "";
    record(beforeLoad === "",
      "with the model still loading there is nothing to label, and nothing is "
      + "drawn - correct, and it is the state the defect never left",
      beforeLoad.slice(0, 40));
    record(g("__loadCb") !== null,
      "the page asked the viewer to load and kept the callback");

    /* The model arrives. NOTHING IS CLICKED. */
    run(`_view.current={};
      __loadCb.onLoad({seconds:0.2,size:{x:1,y:1,z:1}});`);
    const afterLoad = el("cc-labels").innerHTML || "";
    const shownAfterLoad = Number(el("cc-labels")["data-shown"] || 0);
    record(/class="hp/.test(afterLoad) && shownAfterLoad > 0,
      "and the labels are drawn the moment the model arrives, with no "
      + "interaction at all", `${shownAfterLoad} labels`);

    /* AND BACK AGAIN. Select a marker, dismiss it, and the state must be what
       it was - not what the selection left behind. */
    const slot = (SHIPS[key].slots || []).find((x) =>
      (MARKS[key] || []).some((m) => m[0] === x.p));
    if (slot) {
      run(`sel={slot:${JSON.stringify(slot.id)}}; renderLabels();`);
      const during = Number(el("cc-labels")["data-shown"] || 0);
      run("sel=null; renderLabels();");
      const after = Number(el("cc-labels")["data-shown"] || 0);
      record(after === shownAfterLoad,
        "selecting a marker and dismissing it returns the label state to "
        + "where it started", `${shownAfterLoad} -> ${during} -> ${after}`);
    }

    /* THE TOGGLE IS PER SHIP. Hiding labels on a busy hull must not follow you
       to a quiet one, where the hint would then say the hull is busy. */
    const busy = g(`Object.keys(SHIPS).find(function(k){
      var m=(typeof MARKS!=='undefined'&&MARKS[k])||[];
      return m.length>14 && modelUrl(k); })`);
    if (busy) {
      run(`shipId=${JSON.stringify(busy)}; reset(); resetView();
        allLabels=false; renderLabels();`);
      run(`shipId=${JSON.stringify(key)}; reset(); resetView();
        _modelFor=null; renderAll();`);
      record(g("allLabels") === null,
        "and a label choice made on one hull does not follow you to the next",
        String(g("allLabels")));
      run(`allLabels=false; renderLabels();`);
      const hint = el("cc-labelcount").innerHTML || "";
      record(!/this busy/.test(hint),
        "and a quiet hull with labels turned off does NOT claim to be busy",
        hint.replace(/<[^>]*>/g, "").trim().slice(0, 70));
    }
  }
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_ND || MUT_SILENT || MUT_LATE)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
