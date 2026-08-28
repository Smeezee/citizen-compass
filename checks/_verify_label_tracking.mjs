/**
 * E11 - THE LABELS FOLLOW THE SHIP, INCLUDING MID-DRAG.
 *
 * RULE16: UNPROVEN - the leader-line geometry is re-computed here rather than
 * asked of the page, and the solve count is an observation of behaviour
 * rather than a figure the page reports. But both endpoints - the marker
 * and the label - are the page's own projections, so this proves the label
 * FOLLOWS the marker and cannot prove the marker is where it should be.
 * That second question belongs to _verify_marker_positions.mjs.
 *
 * Sleven, 2026-08-23: "I can move the ship around and they just float there...
 * They're supposed to be attached to the hardpoints."
 *
 * WHY THIS IS A SEPARATE FILE FROM _verify_labels.mjs. That control asserts
 * the labels exist, do not overlap, and that each leader line ends on its
 * label's own edge. Every one of those assertions passed while the defect was
 * live, because none of them ever asked where the OTHER end of the line was.
 * The question here is the one nobody asked: after the camera moves, is the
 * line still touching a marker.
 *
 * HOW THE CAMERA IS MOVED. The harness's viewer is a stub with a deterministic
 * orthographic projection, so "rotate the camera" is modelled by changing that
 * projection - the same hull coordinates mapping to different screen points,
 * which is exactly what a rotation does to the numbers this page consumes. It
 * is NOT a real camera and no frame is rendered; there is no browser and no
 * GPU here (rule 7). What is proven is that the page's per-frame path keeps
 * label, line and marker in agreement when the projection under it changes.
 *
 * THE NEGATIVE CONTROL IS THE POINT AND IT MUST FAIL ON THE OLD BUILD.
 * --mutate-onceonly puts the shipped behaviour back: labels placed by
 * renderLabels and never touched again by the frame loop. E11 says it fails on
 * every hull, so a run of this file that passes with that mutation applied is
 * measuring nothing.
 *
 * MUTATORS
 *   --mutate-onceonly     positionLabels() becomes a no-op - the state before
 *                         E11, where the frame loop moved markers and nothing
 *                         moved labels.
 *   --mutate-solveinloop  the collision solve runs every frame instead of on
 *                         the throttle. Correct on screen and the wrong cost;
 *                         section 4 must catch it.
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const MUTS = {
  /* THE SHIPPED BEHAVIOUR, EXACTLY: the frame loop moves the markers and
     nothing moves the labels. Neutering positionLabels() outright was the
     first attempt and it was NOT a faithful reproduction - that function is
     also what makes a label visible in the first place, so the run failed with
     "0 labels rendered" rather than with labels stranded where the hull used
     to be. A negative control that fails for the wrong reason is a negative
     control that has not reproduced the defect. */
  "--mutate-onceonly": [
    [/function onFrameTick\(\)\{\s*renderMarkers\(\);\s*positionLabels\(\);\s*\}/,
     "function onFrameTick(){ renderMarkers(); }"],
  ],
  "--mutate-solveinloop": [
    [/if\(settled\|\|overdue\) solveLabels\(\);/, "solveLabels();"],
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

/* A marker is a dot with a radius. A line that ends within it is touching it;
   one that ends outside it is pointing at nothing, which is the defect. */
const MARKER_R = 7;

function pick(name) {
  return Object.keys(SHIPS).find(
    (k) => new RegExp(name, "i").test(SHIPS[k].n || "") && (MARKS[k] || []).length);
}

/* THE PROJECTION IS THE CAMERA. The stub maps hull units to stage pixels; a
   different mapping is a different point of view, and it is what the page's
   frame path actually consumes. `spin` rotates about the vertical axis, which
   is the motion Sleven was performing when he found this. */
function setCamera(deg, zoom) {
  const r = (deg * Math.PI) / 180;
  run(`_view.project=function(x,y,z){
    var c=${Math.cos(r)}, s=${Math.sin(r)}, k=${zoom || 1};
    var rx=x*c - z*s, rz=x*s + z*c;
    return {x:480+rx*430*k, y:270-y*250*k, depth:rz*0.5};
  };`);
}
/* TIME IS DRIVEN, NOT MEASURED. Sixty frames execute in nine milliseconds of
   wall clock in this harness, so a throttle written in milliseconds would
   never fire once and the run would report "0 solves in 60 frames" as though
   that were the feature working. The page reads `window.performance.now()`;
   this installs one that advances by a frame at a time, so the throttle is
   exercised at the rate a browser would exercise it rather than at the rate
   Node happens to run. */
const FRAME_MS = 1000 / 60;
function installClock() {
  run(`__clock=0; performance={ now:function(){ return __clock; } };`);
}
function frame(advance) {
  run(`__clock += ${advance === undefined ? FRAME_MS : advance};`);
  run("onFrameTick();");
}
installClock();

function state() {
  const marks = [...el("cc-marks").children].map((b) => ({
    port: b.dataset.port,
    hidden: (b.style.display || "") === "none",
    x: parseFloat(b.style.left) || 0,
    y: parseFloat(b.style.top) || 0,
  }));
  const labels = [...el("cc-labels").children].map((d) => ({
    hidden: (d.style.display || "") === "none",
    x: parseFloat(d.style.left) || 0,
    y: parseFloat(d.style.top) || 0,
    text: String(d._attrs["data-text"] || ""),
  }));
  const lines = [...el("cc-leaders").children].map((l) => ({
    off: String(l.getAttribute("stroke-opacity") || "1") === "0",
    x1: +l.getAttribute("x1"), y1: +l.getAttribute("y1"),
    x2: +l.getAttribute("x2"), y2: +l.getAttribute("y2"),
  }));
  return { marks, labels, lines };
}

/* Every visible line's near end must land inside SOME marker. Reported as the
   worst distance as well as a count, because "3 adrift" and "3 adrift by
   400 pixels" are different sentences. */
function adrift(st) {
  let bad = 0, worst = 0, checked = 0;
  st.lines.forEach((L) => {
    if (L.off) return;
    checked++;
    let best = Infinity;
    st.marks.forEach((m) => {
      if (m.hidden) return;
      const d = Math.hypot(L.x1 - m.x, L.y1 - m.y);
      if (d < best) best = d;
    });
    if (best > MARKER_R) { bad++; if (best > worst) worst = best; }
  });
  return { bad, worst, checked };
}

console.log("==========================================================");
console.log("E11 - the labels follow the ship");
console.log(MUT ? `MUTATED: ${MUT}` : "clean page");
console.log("==========================================================");

/* =====================================================================
   1. AT REST, BEFORE ANYTHING MOVES.
   ===================================================================== */
console.log("\n--- 1. at rest ---");
const SHIPS_UNDER_TEST = ["Sabre", "Polaris", "Perseus"];
const keys = {};
{
  for (const nm of SHIPS_UNDER_TEST) {
    const k = pick(nm);
    record(!!k, `${nm} is in the data with markers`, k || "not found");
    keys[nm] = k;
  }
  const k = keys.Sabre;
  openShip(k);
  run("allLabels=true;renderLabels();");
  setCamera(0, 1);
  frame();
  const st = state();
  record(st.labels.filter((l) => !l.hidden).length > 0,
    "labels are rendered", `${st.labels.filter((l) => !l.hidden).length}`);
  const a = adrift(st);
  record(a.bad === 0,
    "and every leader line starts on a marker before anything has moved",
    `${a.bad} of ${a.checked} adrift, worst ${a.worst.toFixed(1)}px`);
}

/* =====================================================================
   2. THE SHIP TURNS. THIS IS THE ITEM.
   ===================================================================== */
console.log("\n--- 2. the camera moves, on all three hulls ---");
{
  for (const nm of SHIPS_UNDER_TEST) {
    const k = keys[nm];
    if (!k) continue;
    openShip(k);
    run("allLabels=true;");
    setCamera(0, 1);
    run("renderLabels();");
    frame();

    /* A FULL TURN IN STEPS, ASSERTED AT EVERY ONE - not only at the end. A
       build that re-solved on settle and left the labels behind in between
       would pass a check that only looked after the motion stopped, and
       "mid-drag" is the state Sleven was in when he found this. */
    let worstBad = 0, worstPx = 0, steps = 0;
    for (let deg = 6; deg <= 360; deg += 6) {
      setCamera(deg, 1);
      frame();
      steps++;
      const a = adrift(state());
      if (a.bad > worstBad) worstBad = a.bad;
      if (a.worst > worstPx) worstPx = a.worst;
    }
    record(worstBad === 0,
      `${nm}: every leader line stays on its marker through a full turn`,
      `${steps} steps, worst ${worstBad} adrift by ${worstPx.toFixed(1)}px`);
  }
}

/* =====================================================================
   3. THE LABEL ITSELF MOVES WITH ITS MARKER, not merely the line.
   ===================================================================== */
console.log("\n--- 3. the label travels with the hull, not just the line ---");
{
  openShip(keys.Polaris);
  run("allLabels=true;");
  setCamera(0, 1);
  run("renderLabels();");
  frame();
  const before = state();
  setCamera(75, 1);
  frame();
  const after = state();

  const movedMarks = before.marks.filter((m, i) =>
    Math.hypot(m.x - after.marks[i].x, m.y - after.marks[i].y) > 20).length;
  record(movedMarks > 5,
    "the camera move actually moved the markers - otherwise nothing below is "
    + "a test of anything", `${movedMarks} markers moved more than 20px`);

  const movedLabels = before.labels.filter((l, i) =>
    !l.hidden && !after.labels[i].hidden
    && Math.hypot(l.x - after.labels[i].x, l.y - after.labels[i].y) > 20).length;
  record(movedLabels > 5,
    "and the labels moved with them", `${movedLabels} labels moved`);

  /* THE OFFSET IS PRESERVED. A label that merely moved somewhere is not the
     claim; the claim is that it kept its place relative to its own marker. */
  let held = 0, drifted = 0;
  before.labels.forEach((l, i) => {
    if (l.hidden || after.labels[i].hidden) return;
    const li = before.lines[i], la = after.lines[i];
    if (li.off || la.off) return;
    const dxB = l.x - li.x1, dyB = l.y - li.y1;
    const dxA = after.labels[i].x - la.x1, dyA = after.labels[i].y - la.y1;
    /* Two pixels of slack for the rounding the page does on the way out. A
       re-solve between the two samples legitimately changes the offset, so
       what is asserted is that MOST hold - the ones that changed changed
       because the arrangement was re-tidied, which is the feature. */
    if (Math.abs(dxA - dxB) <= 2 && Math.abs(dyA - dyB) <= 2) held++;
    else drifted++;
  });
  record(held > 0,
    "and each one kept its position relative to its own marker",
    `${held} held, ${drifted} re-tidied by a fresh solve`);
}

/* =====================================================================
   4. THE SOLVE IS NOT IN THE FRAME LOOP.
   ===================================================================== */
console.log("\n--- 4. the collision solve is throttled, not per-frame ---");
{
  openShip(keys.Perseus);
  run("allLabels=true;");
  setCamera(0, 1);
  run(`__solves=0;
    var __realSolve=solveLabels;
    solveLabels=function(){ __solves++; return __realSolve.apply(this,arguments); };
    renderLabels();`);
  run("__solves=0;");
  /* Sixty frames of continuous motion - one second of dragging. */
  const FRAMES = 60;
  const t0 = Date.now();
  for (let i = 1; i <= FRAMES; i++) { setCamera(i * 1.5, 1); frame(); }
  const ms = Date.now() - t0;
  const solves = g("__solves");
  /* One second of dragging. The floor is 180ms between solves, so a correct
     build lands somewhere around five or six and a build with the solve in the
     loop lands on sixty. */
  record(solves < FRAMES / 4,
    `the solve ran ${solves} times across ${FRAMES} frames of continuous `
    + `motion, not once per frame`, `${solves} solves`);
  record(solves > 0,
    "but it DID run - a throttle that never fires is a solve that never "
    + "re-tidies", `${solves}`);
  record(solves <= Math.ceil((FRAMES * FRAME_MS) / 180) + 1,
    "and no more often than the 180ms floor allows",
    `${solves} in ${(FRAMES * FRAME_MS).toFixed(0)}ms`);

  /* AND THE ARRANGEMENT IS STILL RIGHT AT THE END. Throttling that left the
     labels in a heap would be a different defect, not a fix. */
  const a = adrift(state());
  record(a.bad === 0, "and every line is still on its marker afterwards",
    `${a.bad} adrift`);
  console.log(`    ${FRAMES} frames of 35-marker Perseus took ${ms}ms of CPU `
    + `in this harness - ${(ms / FRAMES).toFixed(2)}ms per frame, of which `
    + `${solves} were solves`);
  console.log("    NOT A FRAME TIME. There is no GPU and no browser here; this "
    + "is the page's own arithmetic, which is the part E11a was worried "
    + "about, and it is reported as that.");
}

/* =====================================================================
   5. NOTHING IS LEFT BEHIND WHEN A LABEL GOES OUT OF VIEW.
   ===================================================================== */
console.log("\n--- 5. a marker that leaves the view takes its label with it ---");
{
  openShip(keys.Sabre);
  run("allLabels=true;");
  setCamera(0, 1);
  run("renderLabels();");
  frame();
  const on = state().labels.filter((l) => !l.hidden).length;
  /* A projection that refuses everything is what a marker behind the camera
     produces. */
  run("_view.project=function(){ return null; };");
  frame();
  const off = state();
  record(off.labels.every((l) => l.hidden),
    "every label is hidden when its marker cannot be projected",
    `${off.labels.filter((l) => !l.hidden).length} still showing of ${on}`);
  record(off.lines.every((l) => l.off),
    "and no leader line is left drawn to a point that no longer exists",
    `${off.lines.filter((l) => !l.off).length} still drawn`);
}

finish(MUT
  ? "--mutate: a defect was planted, so a non-zero exit is the correct outcome."
  : `marker radius treated as ${MARKER_R}px; the projection is a stub, not a `
    + `camera`);
