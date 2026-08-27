/**
 * Q2 / E11b - LABELS ARE THERE ON A COLD LOAD, AND THE ANSWER TO "WHICH PATH"
 * IS THAT E8'S CONTROL WAS NARROW RATHER THAN WRONG.
 *
 * Sleven, on the Anvil C8R Pisces Rescue: "as soon as I loaded in, nothing was
 * there. I clicked one of the hardpoints and they popped up." Four hardpoints,
 * far below the 14 threshold, so they should be on at load.
 *
 * THE PATH, FOUND AND NAMED.
 *
 * E8 put `renderLabels()` in the model's onLoad callback, and that was right
 * and necessary. What it could not fix is that ONLOAD CAN FIRE BEFORE THE
 * STAGE HAS A SIZE. cc_viewer's projection ends:
 *
 *     var w = this.canvas.clientWidth, h = this.canvas.clientHeight;
 *     return { x: (v.x*0.5+0.5)*w, y: (-v.y*0.5+0.5)*h, depth: v.z };
 *
 * With a canvas of zero size EVERY marker projects to (0,0). The markers
 * recovered on the very next frame, because they are in the animation loop.
 * THE LABELS WERE NOT IN IT, so they stayed piled in the top-left corner until
 * something re-rendered the page - and clicking a hardpoint is exactly that.
 * "Nothing was there, then they popped up" is that sentence exactly.
 *
 * SO E8'S CONTROL WAS NARROW, NOT WRONG. It proved renderLabels RUNS at load.
 * It could not prove the positions it computed were USABLE, because the
 * harness's stub projection was a fixed mapping that never depended on canvas
 * size - so the harness was never in the state that produces the defect. The
 * stub reads the canvas now, which is what lets this file reproduce it.
 *
 * AND Q1 IS WHAT FIXES IT. Nothing here changes onLoad; what closes the gap is
 * that positionLabels() runs every frame and recomputes from the projection,
 * so labels self-correct exactly the way markers always did.
 *
 * MUTATORS
 *   --mutate-onceonly  labels leave the frame loop, which is the state that
 *                      produced the report. They must never recover.
 *   --mutate-stalelen  restores the length-equality guard on the projection
 *                      refresh - the freshness test that was not one.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";
import { loadPage, reporter } from "./_loadout_harness.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const VIEWER = process.env.CC_VIEWER
  || join(HERE, "..", "testing", "_src", "cc_viewer.js");

const MUTS = {
  "--mutate-onceonly": [
    [/function onFrameTick\(\)\{\s*renderMarkers\(\);\s*positionLabels\(\);\s*\}/,
     "function onFrameTick(){ renderMarkers(); }"],
  ],
  "--mutate-stalelen": [
    [/\n  renderMarkers\(\);\n  const shown=solveLabels\(\);/,
     "\n  if(_markProj.length!==list.length) renderMarkers();"
     + "\n  const shown=solveLabels();"],
  ],
};
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
if (MUT && !MUTS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }
if (MUT) console.log(`*** MUTATED: ${MUT} ***`);

const H = loadPage({ mutate: MUT ? MUTS[MUT] : [],
  srcDir: process.env.CC_SRCDIR || null,
  pageFile: process.env.CC_PAGE || null });
const { record, finish } = reporter(false);
const { g, run, el, openShip, SHIPS, MARKS } = H;

const canvas = (w, h) => run(
  `document.getElementById('cc-canvas').clientWidth=${w};`
  + `document.getElementById('cc-canvas').clientHeight=${h};`);
const labelsNow = () => [...el("cc-labels").children]
  .filter((c) => (c.style.display || "") !== "none")
  .map((c) => ({ x: parseFloat(c.style.left) || 0,
                 y: parseFloat(c.style.top) || 0 }));
/* Everything piled within a few dozen pixels of the origin is the signature of
   a projection taken against a canvas with no size. */
const inCorner = (ls) => ls.length > 0 && ls.every((p) => p.x < 120 && p.y < 120);

console.log("==========================================================");
console.log("Q2 / E11b - labels on a cold load, and which path skipped them");
console.log(MUT ? `MUTATED: ${MUT}` : "clean page");
console.log("==========================================================");

/* =====================================================================
   1. THE MECHANISM, IN THE REAL VIEWER AND NOT IN A STUB.
   ===================================================================== */
console.log("\n--- 1. the real projection scales by the canvas ---");
{
  const src = readFileSync(VIEWER, "utf-8");
  record(/this\.canvas\.clientWidth/.test(src)
    && /this\.canvas\.clientHeight/.test(src),
    "cc_viewer's project() multiplies by the canvas's client size",
    "");
  /* Run it. A projection that returns (0,0) for every input is not a theory
     about a race - it is what this function does with an unsized canvas. */
  const sandbox = {
    console, Math, Object, Array, JSON, Number, String, Date, isFinite,
    window: { performance: Date, addEventListener() {} },
    THREE: {
      Vector3: function (x, y, z) {
        this.x = x || 0; this.y = y || 0; this.z = z || 0;
        this.project = function () { return this; };
      },
    },
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(src, sandbox, { filename: "cc_viewer.js" });
  const CCV = vm.runInContext("CCViewer", sandbox);
  const v = Object.create(CCV.Viewer.prototype);
  v.camera = {};
  v.canvas = { clientWidth: 0, clientHeight: 0 };
  const zero = [[0.5, 0.5, 0], [-0.9, 0.2, 0], [0.1, -0.7, 0]]
    .map(([x, y, z]) => v.project(x, y, z));
  record(zero.every((p) => p && p.x === 0 && p.y === 0),
    "and with a canvas of zero size EVERY point projects to (0,0)",
    JSON.stringify(zero));
  v.canvas = { clientWidth: 960, clientHeight: 540 };
  const sized = v.project(0.5, 0.5, 0);
  record(sized && sized.x !== 0 && sized.y !== 0,
    "while a sized canvas gives real coordinates - so the collapse is the "
    + "size and nothing else", JSON.stringify(sized));
}

/* =====================================================================
   2. THE HULL SLEVEN NAMED, LOADED COLD.
   ===================================================================== */
console.log("\n--- 2. the C8R Pisces, cold, with no interaction ---");
const key = g(`Object.keys(SHIPS).find(function(k){
  return /C8R Pisces/i.test(SHIPS[k].n||""); })`);
{
  record(!!key, "the Anvil C8R Pisces Rescue is in the data", String(key));
  record((MARKS[key] || []).length > 0 && (MARKS[key] || []).length <= 14,
    "with markers, and below the label threshold - so labels are on by default",
    `${(MARKS[key] || []).length} markers`);
}

/* A COLD BOOT: no model yet, a load whose callback is held, and nothing
   clicked at any point in this section. */
function coldBoot(w, h) {
  openShip(key);
  run(`__cb=null;
    var base=_view, v={}; for(var k in base) v[k]=base[k];
    v.current=null; v.load=function(u,cb){ __cb=cb; return 1; };
    _view=v; _modelFor=null; sel=null;`);
  canvas(w, h);
  run("renderAll();");
  record(g("!!__cb"), "the page asked the viewer for the model and kept the "
    + "callback");
  run(`_view.current={}; __cb.onLoad({seconds:0.3,size:{x:1,y:1,z:1}});`);
}

console.log("\n--- 3. the normal case: the stage already has a size ---");
{
  coldBoot(960, 540);
  const ls = labelsNow();
  /* V2: ONE LABEL PER MOUNT, NOT PER PORT. The expected number is asked of the
     page's own mountsFor() rather than recomputed here - a control that
     re-implements the grouping it is checking would agree with itself whatever
     the page did. */
  const want = Number(g(`mountsFor(${JSON.stringify(key)}).length`));
  record(ls.length === want,
    "every label is up the moment the model arrives, with nothing clicked",
    `${ls.length} of ${want}`);
  record(!inCorner(ls),
    "and they are on the hull rather than piled at the origin",
    JSON.stringify(ls));
}

console.log("\n--- 4. THE RACE: the model arrives before the stage is sized ---");
{
  coldBoot(0, 0);
  const atLoad = labelsNow();
  /* R1 CHANGED WHAT THIS MOMENT LOOKS LIKE, AND IMPROVED IT. With every marker
     projected to (0,0) the solver now reports that nothing fits, so the page
     shows NO labels rather than a pile of them in the corner. Either way the
     state is wrong and neither is what a reader should be left with - the
     claim this section exists to make is the RECOVERY below, which is the half
     E8's fix could not deliver on its own. Asserted as "not on the hull"
     rather than as "in the corner", so it survives that change instead of
     encoding one moment of it. */
  record(atLoad.length === 0 || inCorner(atLoad),
    "with an unsized canvas nothing usable is drawn - the reported symptom, "
    + "reproduced, and the state E8's fix could not see",
    JSON.stringify(atLoad));

  /* THE STAGE GAINS ITS SIZE AND ONE FRAME RUNS. NOTHING IS CLICKED. */
  canvas(960, 540);
  run("onFrameTick();");
  const after = labelsNow();
  record(after.length > 0,
    "the labels are up once the stage has a size",
    `${after.length}`);
  record(!inCorner(after),
    "AND THEY MOVE ONTO THE HULL ON THE NEXT FRAME, with no interaction of "
    + "any kind - which is what Q1's per-frame path buys and what E8 alone "
    + "could not", JSON.stringify(after));
}

/* =====================================================================
   5. THE PROJECTION REFRESH IS A FRESHNESS TEST, NOT A LENGTH TEST.
   ===================================================================== */
console.log("\n--- 5. a stale projection is not mistaken for a fresh one ---");
{
  /* Two hulls with the SAME marker count. A guard that refreshed only when the
     count changed would place the second hull's labels against the first
     hull's screen positions - and the numbers would look perfectly plausible. */
  const n = (MARKS[key] || []).length;
  const twin = g(`Object.keys(SHIPS).find(function(k){
    return k!==${JSON.stringify(key)}
      && (typeof MARKS!=='undefined') && (MARKS[k]||[]).length===${n}
      && modelUrl(k); })`);
  record(!!twin, `a second hull with exactly ${n} markers exists to switch to`,
    twin ? g(`SHIPS[${JSON.stringify(twin)}].n`) : "none");
  if (twin) {
    openShip(key);
    canvas(960, 540);
    run("allLabels=true; renderLabels();");
    const a = labelsNow();
    /* Move the camera hard, WITHOUT a frame, then change ship. A length-only
       guard reuses the projection taken before the move. */
    run(`_view.project=function(x,y,z){ return {x:900-x*40, y:500-y*40,
      depth:z*0.5}; };`);
    run(`shipId=${JSON.stringify(twin)}; reset(); resetView(); sel=null;
      allLabels=true; renderLabels();`);
    const b = labelsNow();
    const same = a.length === b.length
      && a.every((p, i) => Math.abs(p.x - b[i].x) < 1
                        && Math.abs(p.y - b[i].y) < 1);
    record(!same,
      "switching hulls re-projects rather than reusing the previous hull's "
      + "positions", same ? "identical positions" : "re-projected");
    record(b.every((p) => p.x > 600),
      "and the new positions come from the CURRENT projection",
      JSON.stringify(b.slice(0, 3)));
  }
}

finish(MUT
  ? "--mutate: a defect was planted, so a non-zero exit is the correct outcome."
  : "the path was the unsized canvas at onLoad; E8's control was narrow, not "
    + "wrong");
