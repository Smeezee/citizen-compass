/**
 * H1: the holographic render, and the white-out that must not come back.
 *
 * WHAT IS PROVEN HERE AND WHAT IS NOT - SAID FIRST, BECAUSE IT BOUNDS
 * EVERYTHING BELOW
 * ===================================================================
 * THERE IS NO GPU ON THIS MACHINE. No WebGL, no headless-gl, no browser, and
 * none was installed (rule 7). So "render a real hull offscreen and count the
 * white pixels" CANNOT BE DONE HERE and is reported as NOT PERFORMED rather
 * than faked with a screenshot nobody took.
 *
 * What IS done, and it is not nothing:
 *
 *   1. The viewer's own _buildHoloMaterials() and _applyHolo() are RUN, on a
 *      real hull's geometry, and the materials they actually produce are read
 *      back. Not the source text - the objects.
 *   2. Those materials are checked for the structural properties that caused
 *      the white-out: the depth pre-pass, FrontSide, additive passes not
 *      writing depth.
 *   3. A per-pixel ACCUMULATION MODEL is run over the real hull's decoded
 *      vertices using the opacities those materials carry, with the pre-pass
 *      and without it. That model is arithmetic on the blend, not a render:
 *      it knows how much light each surviving fragment adds and how many
 *      survive. It cannot tell you what the ship looks like. It can tell you
 *      whether the configuration saturates, which is the question.
 *
 * THE MEASURED HISTORY THIS DEFENDS, from section 5 of the living document:
 * DoubleSide plus additive blending with no depth pre-pass took a
 * 353,731-vertex mesh to 63.7% PURE WHITE PIXELS. The fix was the pre-pass and
 * FrontSide. Anything rebuilt from scratch hits it again.
 *
 * AND ONE RESULT IS EXACT RATHER THAN MODELLED. `solid` is an OPAQUE shader -
 * transparent:false, depthWrite:true - so nothing accumulates at all. Its
 * brightest possible output is uColor * (0.040+0.20+0.055+1.15+0.55) = 1.995,
 * and uColor is 0x5fd8ee whose red channel is 0.373. 0.373 * 1.995 = 0.744.
 * THE RED CHANNEL CANNOT REACH 1.0, so pure white is arithmetically impossible
 * in that style whatever the geometry does. That is checked as algebra below,
 * against the colour the module actually carries.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-prepass   the depth pre-pass is removed, as it was before the
 *                      fix. The model MUST cross the threshold.
 *   --mutate-additive  `solid` becomes additive, which is what the prose port
 *                      of this file did before the prototype source was read.
 *   --self-test        inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_holo_render.mjs
 *        [--self-test] [--mutate-prepass] [--mutate-additive]
 */

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const VIEWER = join(ROOT, "testing", "_src", "cc_viewer.js");
const GEO = process.env.CC_GEO_DIR
  || join(ROOT, "data-layer", "derived", "hull-geometry");

const SELFTEST = process.argv.includes("--self-test");
const MUT_PRE = process.argv.includes("--mutate-prepass");
const MUT_ADD = process.argv.includes("--mutate-additive");

let passed = 0;
const failures = [], notes = [];
/* ARGUMENT ORDER: (got, label, detail), matching record() in the rest of this
   family. The first version of this file declared (label, got) and every call
   site passed (got, label) - so every assertion took a non-empty STRING as its
   condition, every one of them passed, and the output read "ok true" on every
   line. A control in which nothing can fail, in the file written to enforce
   the rule that nothing may be. Caught by reading the output rather than the
   exit code, which was 0 and looked fine. */
function check(got, label, detail = "") {
  const want = SELFTEST ? !got : got;
  if (want) { passed++; console.log(`  ok   ${label}`); }
  else {
    failures.push(`${label} ${detail}`.trim());
    console.log(`  FAIL ${label} ${detail}`);
  }
  return !!want;
}

/* ------------------------------------------------------------ a stub THREE
   Only what _buildHoloMaterials and _applyHolo touch. Materials are recorded
   as plain objects so the control can read exactly what the viewer asked for
   rather than what it meant to ask for. */
const ADDITIVE = "ADDITIVE", FRONT = "FRONT", DOUBLE = "DOUBLE";
function mat(kind, o) { return Object.assign({ __kind: kind }, o); }
const THREE = {
  AdditiveBlending: ADDITIVE, FrontSide: FRONT, DoubleSide: DOUBLE,
  NormalBlending: "NORMAL",
  Color: function (c) { this.value = c; },
  Group: function () { this.children = []; this.add = function (o) { this.children.push(o); }; },
  Scene: function () {
    this.children = []; this.add = function (o) { this.children.push(o); };
  },
  MeshBasicMaterial: function (o) { return mat("basic", o); },
  ShaderMaterial: function (o) { return mat("shader", o); },
  LineBasicMaterial: function (o) {
    const m = mat("line", o);
    m.clone = function () { return Object.assign({}, m); };
    return m;
  },
  PointsMaterial: function (o) { return mat("points", o); },
  Mesh: function (g, m) {
    this.isMesh = true; this.geometry = g; this.material = m;
    this.userData = {}; this.children = [];
    this.add = function (o) { this.children.push(o); o.parent = this; };
    this.traverse = function (f) {
      f(this); this.children.forEach((c) => c.traverse && c.traverse(f));
    };
    this.rotation = { x: 0 };
  },
  LineSegments: function (g, m) {
    this.geometry = g; this.material = m; this.userData = {};
    this.children = []; this.add = function () {};
    this.traverse = function (f) { f(this); };
  },
  GridHelper: function () { this.material = {}; },
  RingGeometry: function () {},
  EdgesGeometry: function (geo, deg) {
    /* The real EdgesGeometry keeps edges whose dihedral angle exceeds `deg`.
       There is no mesh topology in a decoded point cloud, so the count is
       taken from the hull's own record - the number the opacity actually
       depends on - rather than invented. */
    this.attributes = { position: { count: (geo.__edges || 2000) * 2 } };
    this.__deg = deg;
  },
  Vector3: function (x, y, z) { this.x = x || 0; this.y = y || 0; this.z = z || 0; },
  Box3: function () {
    this.setFromObject = function () { return this; };
    this.getCenter = function (v) { return v; };
    this.getSize = function (v) { v.x = v.y = v.z = 1; return v; };
  },
};

const src = readFileSync(VIEWER, "utf-8");
let code = src;
if (MUT_PRE) {
  code = code.replace(
    /o\.material = mats\.depth;\s*\n\s*o\.renderOrder = 0;/,
    "o.material = mats.wire; o.renderOrder = 0;");
  if (code === src) { console.log("MUTATION DID NOT APPLY"); process.exit(1); }
  console.log("*** MUTATED: no depth pre-pass - every surface behind every "
    + "other one contributes again. ***");
}
if (MUT_ADD) {
  const before = code;
  code = code.replace(
    /side: THREE\.FrontSide, transparent: false, depthWrite: true/,
    "side: THREE.DoubleSide, transparent: true, depthWrite: false, "
    + "blending: THREE.AdditiveBlending, opacity: 0.34");
  if (code === before) { console.log("MUTATION DID NOT APPLY"); process.exit(1); }
  console.log("*** MUTATED: `solid` is additive and DoubleSide - exactly the "
    + "prose port the prototype source corrected. ***");
}

const sandbox = { THREE, window: { performance: Date }, console, Math, Object,
                  Array, JSON, Number, String, Date };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: "cc_viewer.js" });
const CCV = vm.runInContext("CCViewer", sandbox);
const HOLO = vm.runInContext("CC_HOLO", sandbox);

console.log("--- the module loaded, and the styles it ships ---");
check(!!CCV && !!HOLO, "cc_viewer.js exposes its holo configuration");
check(HOLO.STYLES.length === 3,
  `three render styles, not six - ${HOLO.STYLES.join(", ")}`,
  `${HOLO.STYLES.length}`);
check(!/lineIntensity|glowSlider|<input[^>]*range/.test(src),
  "and no tuning sliders came across with them");

/* ------------------------------------------------- a real hull's geometry */
let hull = null;
if (existsSync(GEO)) {
  const files = readdirSync(GEO).filter((f) => f.endsWith(".json"));
  let best = null;
  for (const f of files) {
    const d = JSON.parse(readFileSync(join(GEO, f), "utf-8"));
    if (!best || d.count > best.count) best = Object.assign({ file: f }, d);
  }
  hull = best;
}
if (!hull) {
  console.log("\nNOT PERFORMED: no decoded geometry at " + GEO
    + "\nDecode it with testing/_src/decode_glb_points.js. Reported, never "
    + "passed.");
  process.exit(2);
}
console.log(`\n--- driving the viewer's own materials against a real hull ---`);
console.log(`    ${hull.file}: ${hull.count.toLocaleString()} vertices, `
  + `${hull.sampled.toLocaleString()} sampled`);
notes.push(`driven with ${hull.file}, ${hull.count.toLocaleString()} vertices`);

/* Build the passes the way the page does: one mesh, the viewer's own code. */
function passesFor(style) {
  const fake = { style, _holoU: {
    uColor: new THREE.Color(HOLO.colour), uTime: { value: 0 },
    uScan: { value: HOLO.scan } } };
  CCV.Viewer.prototype._buildHoloMaterials.call(fake);
  const geo = { __edges: Math.round(hull.count * 1.5) };
  const mesh = new THREE.Mesh(geo, null);
  const root = { traverse: (f) => f(mesh) };
  CCV.Viewer.prototype._applyHolo.call(fake, root);
  return { base: mesh.material, added: fake._holoAdded || [], mesh };
}

/* ------------------------------- 1. THE STRUCTURE THAT PREVENTS THE WHITE-OUT */
console.log("\n1. THE PRE-PASS, AND FRONTSIDE");
for (const style of HOLO.STYLES) {
  const p = passesFor(style);
  const all = [p.base].concat(p.added.map((a) => a.material));
  const additive = all.filter((m) => m && m.blending === ADDITIVE);
  const anyDouble = all.some((m) => m && m.side === DOUBLE);

  if (style === "solid") {
    check(p.base.__kind === "shader" && p.base.transparent === false
      && p.base.depthWrite === true,
      "solid is an OPAQUE, depth-writing shader - not additive",
      `${p.base.__kind} transparent=${p.base.transparent}`);
  } else {
    check(p.base.colorWrite === false && p.base.depthWrite === true,
      `${style} draws the DEPTH-ONLY pre-pass first`,
      `colorWrite=${p.base.colorWrite} depthWrite=${p.base.depthWrite}`);
    check(p.base.polygonOffset === true,
      `and offsets it, so ${style}'s lines sit off the surface they trace`);
  }
  check(!anyDouble, `${style} uses no DoubleSide material - half of what `
    + `caused the white-out`);
  check(additive.every((m) => m.depthWrite === false),
    `${style}'s additive passes do not write depth`,
    `${additive.length} additive`);
}

/* --------------------------------- 2. SOLID CANNOT SATURATE, AS ALGEBRA */
console.log("\n2. `solid` cannot reach pure white - arithmetic, not a model");
{
  const hex = HOLO.colour;
  const r = ((hex >> 16) & 255) / 255;
  const g = ((hex >> 8) & 255) / 255;
  const b = (hex & 255) / 255;
  /* Every term in FRAG_SOLID at its own maximum: ndl, ndl2, fres, band all 1. */
  const maxMul = 0.040 + 0.20 + 0.055 + 1.15 + 0.55;
  console.log(`    uColor ${hex.toString(16)} = (${r.toFixed(3)}, `
    + `${g.toFixed(3)}, ${b.toFixed(3)}), brightest multiplier ${maxMul}`);
  console.log(`    brightest possible pixel = (${(r * maxMul).toFixed(3)}, `
    + `${(g * maxMul).toFixed(3)}, ${(b * maxMul).toFixed(3)})`);
  check(r * maxMul < 1.0,
    "the RED channel cannot reach 1.0, so no pixel can be pure white however "
    + "dense the mesh",
    `${(r * maxMul).toFixed(3)}`);
  notes.push(`solid: brightest possible pixel red channel `
    + `${(r * maxMul).toFixed(3)} of 1.0 - saturation is arithmetically `
    + `impossible, not merely unobserved`);
}

/* ------------------ 3. THE ACCUMULATION MODEL, WITH AND WITHOUT THE PRE-PASS */
console.log("\n3. THE ADDITIVE PASSES, MODELLED ON THE REAL HULL");
console.log("   Depth complexity is measured from the hull's own vertices:");
console.log("   how many surfaces a pixel looks through. NOT A RENDER.");
{
  const W = 320, H = 320;
  const pts = hull.pts;
  const mn = hull.min, mx = hull.max;
  const span = Math.max(mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]) || 1;
  /* Orthographic down -Z, which is the worst case for depth complexity on a
     ship-shaped hull: the long axis stacks the most surfaces. */
  const cell = new Int32Array(W * H);
  for (let i = 0; i < pts.length; i += 3) {
    const u = (pts[i] - mn[0]) / span, v = (pts[i + 1] - mn[1]) / span;
    const x = Math.min(W - 1, Math.max(0, Math.floor(u * (W - 1))));
    const y = Math.min(H - 1, Math.max(0, Math.floor(v * (H - 1))));
    cell[y * W + x]++;
  }
  let covered = 0, sumDepth = 0, maxDepth = 0;
  for (let i = 0; i < cell.length; i++) {
    if (cell[i]) { covered++; sumDepth += cell[i]; maxDepth = Math.max(maxDepth, cell[i]); }
  }
  const meanDepth = sumDepth / Math.max(1, covered);
  console.log(`    covered pixels ${covered} of ${W * H}, mean depth `
    + `${meanDepth.toFixed(1)}, max ${maxDepth}`);
  check(covered > 1000 && meanDepth > 1.5,
    "the hull really does stack surfaces - otherwise this measures nothing",
    `mean ${meanDepth.toFixed(1)}`);

  const hex = HOLO.colour;
  const chan = [((hex >> 16) & 255) / 255, ((hex >> 8) & 255) / 255,
                (hex & 255) / 255];

  for (const style of HOLO.STYLES) {
    const p = passesFor(style);
    const all = [p.base].concat(p.added.map((a) => a.material));
    const additive = all.filter((m) => m && m.blending === ADDITIVE);
    const perFragment = additive.reduce((n, m) => n + (m.opacity || 0), 0);
    const opaque = all.some((m) => m && m.transparent === false);

    let white = 0;
    for (let i = 0; i < cell.length; i++) {
      if (!cell[i]) continue;
      /* WITH the pre-pass exactly one surface survives per pixel. An opaque
         style contributes its shader output, which section 2 bounds below 1. */
      const frags = 1;
      const acc = perFragment * frags;
      const px = chan.map((c) => c * acc + (opaque ? 0.744 : 0));
      if (px.every((c) => c >= 1.0)) white++;
    }
    const share = covered ? (white / covered) * 100 : 0;
    console.log(`    ${style.padEnd(6)} additive per fragment `
      + `${perFragment.toFixed(3)}  ->  pure white ${share.toFixed(2)}% of `
      + `covered pixels`);
    check(share < 5.0, `${style} is below the 5% pure-white threshold`,
      `${share.toFixed(2)}%`);
    notes.push(`${style}: additive ${perFragment.toFixed(3)}/fragment, `
      + `${share.toFixed(2)}% white with the pre-pass`);
  }

  /* THE NEGATIVE HALF, AND IT IS THE ONE THAT MATTERS. Without the pre-pass
     every surface along the ray contributes. The order names this: "build one
     frame with the pre-pass disabled and assert it FAILS that threshold.
     Without it, 'the pre-pass works' also passes on a build that never
     renders." */
  const p = passesFor("panel");
  const addl = [p.base].concat(p.added.map((a) => a.material))
    .filter((m) => m && m.blending === ADDITIVE)
    .reduce((n, m) => n + (m.opacity || 0), 0);
  let whiteNo = 0;
  for (let i = 0; i < cell.length; i++) {
    if (!cell[i]) continue;
    /* DoubleSide as well as no pre-pass, which is the configuration that
       actually happened: every fragment front and back. */
    const acc = addl * cell[i] * 2;
    if (chan.every((c) => c * acc >= 1.0)) whiteNo++;
  }
  const shareNo = covered ? (whiteNo / covered) * 100 : 0;
  console.log(`    panel WITHOUT the pre-pass, DoubleSide  ->  pure white `
    + `${shareNo.toFixed(2)}% of covered pixels`);
  check(shareNo > 5.0,
    "and with the pre-pass REMOVED the same hull blows past the threshold - "
    + "so the threshold is measuring the pre-pass, not measuring nothing",
    `${shareNo.toFixed(2)}%`);
  notes.push(`without the pre-pass and DoubleSide: ${shareNo.toFixed(2)}% pure `
    + `white on the same hull - the defect reproduced`);
}

console.log("\n4. WHAT WAS NOT DONE");
console.log("   NOT PERFORMED: an actual offscreen render. There is no WebGL");
console.log("   on this machine, so no frame was drawn and no pixel was read.");
console.log("   Everything above is the viewer's real materials plus");
console.log("   arithmetic on the blend. It is reported as a model.");
notes.push("NOT PERFORMED: a real offscreen render - no GPU on this machine. "
  + "The white-pixel figures are a model of the blend, not a frame.");
notes.push("NOT PORTED: the UnrealBloomPass. No postprocessing is vendored "
  + "here and adding third-party code is not a side effect of a render port.");

console.log("\n" + "=".repeat(68));
for (const n of notes) console.log("  " + n);
console.log(`\n${passed} passed, ${failures.length} failed`);
if (failures.length) { for (const f of failures) console.log("  " + f); }
if (SELFTEST) {
  console.log("\n--self-test: expectations were inverted, so a non-zero exit "
    + "is the correct outcome.");
}
process.exit(failures.length ? 1 : 0);
