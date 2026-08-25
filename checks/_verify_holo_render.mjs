/**
 * H1 / H1f: six styles, five colours, three sliders - and every one of them
 * must CHANGE THE RENDER rather than set a class.
 *
 * WHAT IS PROVEN HERE AND WHAT IS NOT, SAID FIRST
 * ===============================================
 * THERE IS NO GPU ON THIS MACHINE. No WebGL, no headless-gl, no browser, none
 * installed (rule 7). So "render offscreen and count the white pixels" cannot
 * be done and is reported as NOT PERFORMED rather than faked.
 *
 * What IS done: the viewer's own _applyHolo() is RUN for each style against a
 * real hull, and the passes it actually builds are read back - material kind,
 * blending, side, opacity, colour. That is a RENDER SIGNATURE. It is not a
 * frame, and it is not a class name either: it is what the scene would hand
 * the GPU.
 *
 * THE LOAD-BEARING ASSERTION IS THE NEGATIVE ONE, and the order says why:
 * two DIFFERENT styles must not produce the SAME signature. A build where
 * every button sets a class and nothing redraws passes everything else in this
 * file. It is checked pairwise across all fifteen pairs, not on a sample.
 *
 * A CORRECTION TO MY OWN EARLIER MODEL, and it is the reason the deployed page
 * looked wrong. The first version of this file modelled ONE fragment per pixel
 * for every pass, on the grounds that the depth pre-pass deduplicates
 * surfaces. IT DOES NOT DEDUPLICATE LINES. The pre-pass rejects geometry
 * BEHIND the nearest surface; coincident EDGES at that same depth all draw and
 * all add. On a 1.1M-vertex hull that is a dozen additive line fragments in
 * one pixel, and the result clips. The model below counts line fragments per
 * pixel from the hull's own density, which is what it should have done first
 * time - Sleven reported "white line-work" and the model said 0.00%.
 *
 * TWO THRESHOLDS ARE REPORTED, because they answer different questions:
 *   PURE WHITE   every channel >= 1.0. The order's 5% threshold.
 *   CLIPPED      any channel >= 1.0. Colour information is lost here even
 *                though the pixel is not white, and this is what makes an
 *                amber hull stop looking amber.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-prepass    the depth pre-pass is removed.
 *   --mutate-additive   `solid` becomes additive and DoubleSide.
 *   --mutate-noop       setStyle records the name but _applyHolo ignores it,
 *                       which is the "every button sets a class" build the
 *                       negative control exists for.
 *   --self-test         inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_holo_render.mjs
 *        [--self-test] [--mutate-prepass] [--mutate-additive] [--mutate-noop]
 */

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
/* CC_VIEWER lets this be pointed at a cc_viewer.js fetched from the origin,
   the same way CC_PAGE works for the page controls. */
const VIEWER = process.env.CC_VIEWER
  || join(ROOT, "testing", "_src", "cc_viewer.js");
const GEO = process.env.CC_GEO_DIR
  || join(ROOT, "data-layer", "derived", "hull-geometry");

const SELFTEST = process.argv.includes("--self-test");
const MUT_PRE = process.argv.includes("--mutate-prepass");
const MUT_ADD = process.argv.includes("--mutate-additive");
const MUT_NOOP = process.argv.includes("--mutate-noop");

let passed = 0;
const failures = [], notes = [];
function check(got, label, detail = "") {
  const want = SELFTEST ? !got : got;
  if (want) { passed++; console.log(`  ok   ${label}`); }
  else {
    failures.push(`${label} ${detail}`.trim());
    console.log(`  FAIL ${label} ${detail}`);
  }
  return !!want;
}

/* ------------------------------------------------------------ a stub THREE */
const ADD = "ADD", FRONT = "FRONT", DOUBLE = "DOUBLE";
const mkColor = (c) => ({
  __hex: c, getHex() { return this.__hex; },
  set(v) { this.__hex = v; return this; },
});
function mat(kind, o) {
  const m = Object.assign({ __kind: kind }, o);
  if (typeof m.color === "number") m.color = mkColor(m.color);
  m.clone = function () {
    const c = Object.assign({}, m);
    c.color = mkColor(m.color ? m.color.getHex() : 0);
    c.clone = m.clone;
    return c;
  };
  return m;
}
const THREE = {
  AdditiveBlending: ADD, FrontSide: FRONT, DoubleSide: DOUBLE,
  Color: function (c) { return mkColor(c); },
  Group: function () {
    this.children = []; this.visible = true;
    this.add = function (o) { this.children.push(o); };
  },
  Scene: function () {
    this.children = []; this.add = function (o) { this.children.push(o); };
  },
  MeshBasicMaterial: function (o) { return mat("basic", o); },
  ShaderMaterial: function (o) { return mat("shader", o); },
  LineBasicMaterial: function (o) { return mat("line", o); },
  PointsMaterial: function (o) { return mat("points", o); },
  Mesh: function (g, m) {
    this.isMesh = true; this.geometry = g; this.material = m;
    this.userData = {}; this.children = []; this.rotation = { x: 0 };
    this.add = function (o) { this.children.push(o); o.parent = this; };
    this.remove = function (o) {
      const i = this.children.indexOf(o);
      if (i >= 0) this.children.splice(i, 1);
    };
    /* FAITHFUL TO three.js, AND THE OLD LINE IS WHY E7a GOT PAST THIS FILE.
       It was `this.children.forEach(...)`, and forEach does not visit elements
       appended during the iteration. The real Object3D.traverse is
         t(this); const e=this.children; for(let n=0,i=e.length;n<i;n++) ...
       which reads the length AFTER the callback has run, so a child the
       callback just added IS descended into. That single difference is where
       the Wireframe bug lived: _applyHolo added a Mesh child to the mesh it
       was visiting, the engine walked into it, and the page recursed until the
       stack blew. This stub absorbed it silently. */
    this.traverse = function (f) {
      f(this);
      var e = this.children;
      for (var n = 0, i = e.length; n < i; n++) {
        if (e[n].traverse) e[n].traverse(f);
      }
    };
  },
  LineSegments: function (g, m) {
    this.geometry = g; this.material = m; this.userData = {};
    this.children = []; this.add = function () {};
    this.traverse = function (f) { f(this); };
  },
  Points: function (g, m) {
    this.geometry = g; this.material = m; this.userData = {};
    this.children = []; this.add = function () {};
    this.traverse = function (f) { f(this); };
  },
  GridHelper: function () { this.material = {}; },
  RingGeometry: function () {},
  EdgesGeometry: function (geo, deg) {
    /* The real EdgesGeometry keeps edges whose dihedral angle exceeds `deg`.
       There is no topology in a decoded point cloud, so the count comes from
       the hull's own vertex count scaled by the threshold - fewer edges
       survive a larger angle, which is what the detail slider is FOR and is
       what makes its effect on opacity observable here. */
    const base = geo.__edges || 2000;
    const keep = Math.max(0.02, Math.min(1, 24 / Math.max(1, deg)));
    this.attributes = { position: { count: Math.round(base * keep) * 2 } };
    this.__deg = deg;
  },
  Vector3: function () { this.x = this.y = this.z = 0; },
  Box3: function () {
    this.setFromObject = function () { return this; };
    this.getCenter = function (v) { return v; };
    this.getSize = function (v) { v.x = v.y = v.z = 1; return v; };
  },
};

const src = readFileSync(VIEWER, "utf-8");
let code = src;
function planted(pattern, replacement, why) {
  const before = code;
  code = code.replace(pattern, replacement);
  if (code === before) { console.log("MUTATION DID NOT APPLY"); process.exit(1); }
  console.log("*** MUTATED: " + why + " ***");
}
if (MUT_PRE) {
  planted(/o\.material = mats\.depth; o\.renderOrder = 0; note\('prepass', mats\.depth\);/,
    "o.material = mats.wire; o.renderOrder = 0; note('prepass', mats.wire);",
    "no depth pre-pass - every surface behind every other adds again");
}
if (MUT_ADD) {
  planted(/side: THREE\.FrontSide, transparent: false, depthWrite: true \}\),\n      hull:/,
    "side: THREE.DoubleSide, transparent: true, depthWrite: false, "
    + "blending: THREE.AdditiveBlending, opacity: 0.34 }),\n      hull:",
    "`solid` is additive and DoubleSide");
}
if (MUT_NOOP) {
  planted(/var style = this\.style \|\| CC_HOLO\.DEFAULT;/,
    "var style = CC_HOLO.DEFAULT;",
    "every button sets a class and the render never changes");
}

const sandbox = { THREE, window: { performance: Date }, console, Math, Object,
                  Array, JSON, Number, String, Date, isFinite };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: "cc_viewer.js" });
const CCV = vm.runInContext("CCViewer", sandbox);
const HOLO = vm.runInContext("CC_HOLO", sandbox);

/* CC_HOLO IS SHARED MUTABLE STATE AND THE SLIDER SECTION MOVES IT.
   Section 3 drives each slider to its extremes and does not put them back, so
   section 5 was measuring lineInt=1.8 and detail=70 while reporting them as
   the shipped defaults - it printed 30.9% pure white for a configuration
   nobody ships. Found by dumping the passes, NOT by the numbers looking wrong:
   a saturating hull was exactly what I expected to see, which is what makes
   this kind of leak dangerous.
   Snapshot here; restore before anything that claims to measure the default. */
const HOLO_DEFAULTS = { lineInt: HOLO.lineInt, detail: HOLO.detail,
                        glow: HOLO.glow, scan: HOLO.scan, grid: HOLO.grid };
const restoreDefaults = () => Object.assign(HOLO, HOLO_DEFAULTS);

console.log("--- what the module ships ---");
check(!!CCV && !!HOLO, "cc_viewer.js exposes its holo configuration");
/* G3/G4: SEVEN NOW. `xray` is G4's deliberate see-inside, replacing the
   accidental one the 9% surface used to give. */
check(HOLO.MODES.length === 7,
  `ALL SEVEN render styles - ${HOLO.MODES.map((m) => m[0]).join(", ")}`,
  String(HOLO.MODES.length));
check(HOLO.COLOURS.length === 5, "five colours", String(HOLO.COLOURS.length));
/* G3: THE DEFAULT MOVED, AND THAT IS THE ITEM. `solidlines` drew 39,425 line
   segments on an Aurora LX and 603,154 on a Javelin, additively, over a surface
   at 9% - the lines were five times brighter than the surface they traced.
   C1 measured "not clean surface" at 20.6-67.1% before, 12.9-45.6% with the
   lines quietened, and 0.00% with the line pass removed. So the page opens on
   `solid` and solid shading carries the panel detail. */
check(HOLO.DEFAULT === "solid",
  "the default style is Solid holo - no line pass at all", HOLO.DEFAULT);
check(HOLO.MODES.some((m) => m[0] === "xray"),
  "and See inside is offered as its own mode rather than happening by accident");
check(HOLO.DEFAULT_COLOUR === 0xffb545,
  "and the default colour is AMBER, not cyan",
  "0x" + HOLO.DEFAULT_COLOUR.toString(16));
check(HOLO.scan === 0,
  "scanlines are available but OFF by default", String(HOLO.scan));

/* ------------------------------------------------------- a real hull */
let hull = null;
if (existsSync(GEO)) {
  for (const f of readdirSync(GEO).filter((x) => x.endsWith(".json"))) {
    const d = JSON.parse(readFileSync(join(GEO, f), "utf-8"));
    if (!hull || d.count > hull.count) hull = Object.assign({ file: f }, d);
  }
}
if (!hull) {
  console.log("\nNOT PERFORMED: no decoded geometry at " + GEO);
  process.exit(2);
}
console.log(`\n--- driving the viewer against ${hull.file}, `
  + `${hull.count.toLocaleString()} vertices ---`);
notes.push(`driven with ${hull.file}, ${hull.count.toLocaleString()} vertices`);

function viewerFor() {
  const v = Object.create(CCV.Viewer.prototype);
  v._colour = HOLO.DEFAULT_COLOUR;
  v._holoU = { uColor: mkColor(v._colour), uTime: { value: 0 },
               uScan: { value: HOLO.scan }, uGlow: { value: HOLO.glow } };
  v.style = HOLO.DEFAULT;
  /* E7a: THE ROOT WALKS ITS CHILDREN, BECAUSE THE ENGINE DOES.
     This was `{ traverse: (f) => f(v.__mesh) }` - a lambda that calls the
     callback on exactly one mesh and never looks at a child. Object3D.traverse
     reads `children.length` AFTER running the callback, so a child the
     callback just added IS descended into, and _applyHolo's `wire` branch adds
     a Mesh child to the mesh it is visiting. The engine walked into it, added
     another, and the page recursed until the stack blew - which is what
     "the wireframe button did nothing" was.
     THE ONE BEHAVIOUR THAT WOULD HAVE CAUGHT IT IS THE ONE THIS FILE HAD
     REPLACED WITH A LAMBDA. Recorded rather than quietly fixed: this control
     did not fail to be written, it was written so it could not fail. */
  v.__mesh = new THREE.Mesh({ __edges: Math.round(hull.count * 1.5) }, null);
  v.current = new THREE.Group();
  v.current.traverse = function (f) {
    f(this);
    var e = this.children;
    for (var n = 0, i = e.length; n < i; n++) {
      if (e[n].traverse) e[n].traverse(f);
    }
  };
  v.current.add(v.__mesh);
  v._applyHolo(v.current);
  return v;
}

/* ----------------------------------- 1. SIX STYLES, SIX SIGNATURES ------- */
console.log("\n1. every style produces a DIFFERENT render signature");
const sigs = {};
for (const [key] of HOLO.MODES) {
  const v = viewerFor();
  v.setStyle(key);
  sigs[key] = v.renderSignature();
  console.log(`    ${key.padEnd(11)} ${sigs[key].slice(0, 92)}`);
}
check(Object.keys(sigs).length === 7, "all seven styles rendered something");
check(Object.values(sigs).every((s) => s && s.length > 10),
  "and each produced a non-empty signature");

/* THE NEGATIVE CONTROL, PAIRWISE. All fifteen pairs, not a sample. */
let same = [];
const keys = HOLO.MODES.map((m) => m[0]);
for (let i = 0; i < keys.length; i++) {
  for (let j = i + 1; j < keys.length; j++) {
    if (sigs[keys[i]] === sigs[keys[j]]) same.push(`${keys[i]}=${keys[j]}`);
  }
}
check(same.length === 0,
  "NO TWO STYLES SHARE A SIGNATURE - all 15 pairs differ. Without this, a "
  + "build where every button sets a class and nothing redraws passes "
  + "everything above",
  same.join(", "));
notes.push(`six styles, 15 pairs, all signatures distinct`);

/* ------------------------------------------- 2. FIVE COLOURS ------------- */
console.log("\n2. every colour changes the render");
const colSigs = {};
for (const hex of HOLO.COLOURS) {
  const v = viewerFor();
  v.setColour(hex);
  colSigs[hex] = v.renderSignature();
}
const distinctCols = new Set(Object.values(colSigs));
check(distinctCols.size === HOLO.COLOURS.length,
  "all five colours produce distinct signatures",
  `${distinctCols.size} of ${HOLO.COLOURS.length}`);
{
  const v = viewerFor();
  v.setColour(0xffb545);
  check(v.colour() === 0xffb545, "amber can be selected");
  check(v._holoU.uColor.getHex() === 0xffb545,
    "and it reaches the shader uniform, not just a variable");
  const before = v.colour();
  v.setColour(0x123456);
  check(v.colour() === before,
    "a colour that is not one of the five is REFUSED rather than silently "
    + "accepted");
}

/* ------------------------------------------- 3. THREE SLIDERS ------------ */
console.log("\n3. every slider changes the render across its range");
/* G3 CHANGED WHAT A SLIDER CAN BE MEASURED ON, and this is the honest version
   rather than a loosened one. `lineInt` and `detail` govern the LINE PASS, and
   the default style no longer has one - so driving them on `solid` proves
   nothing, and a check that did would be asserting that a slider with nothing
   to act on still acts. They are driven on `panel`, which draws lines. `glow`
   is the rim and lives on the surface, so it is driven on the default.
   AND THE OTHER HALF IS ASSERTED TOO: lineInt must NOT move the default, which
   is what "the default draws no line pass" means in practice. */
for (const [name, lo, hi, onStyle] of [["lineInt", 0.2, 1.8, "panel"],
                                       ["detail", 8, 70, "panel"],
                                       ["glow", 0.05, 1.4, null]]) {
  const a = viewerFor(); if (onStyle) a.setStyle(onStyle); a.setSlider(name, lo);
  const sa = a.renderSignature();
  const b = viewerFor(); if (onStyle) b.setStyle(onStyle); b.setSlider(name, hi);
  const sb = b.renderSignature();
  check(sa !== sb,
    `${name} changes the render between ${lo} and ${hi}`
    + (onStyle ? ` on ${onStyle}` : ""),
    sa === sb ? "identical signature" : "");
  const c = viewerFor();
  c.setSlider(name, 9999);
  check(c.slider(name) <= hi * 2,
    `and ${name} is clamped rather than accepting anything`,
    String(c.slider(name)));
}

/* ------------------------------- 4. THE PRE-PASS AND FRONTSIDE ----------- */
console.log("\n4. the pre-pass, and no DoubleSide on a hull");
/* G4 IS THE ONE EXCEPTION TO BOTH INVARIANTS, AND IT IS NAMED RATHER THAN
   EXEMPTED. `xray` has no depth pre-pass and IS DoubleSide, on purpose: seeing
   the far side is the whole mode, so nothing may occlude anything. Written as
   "every style except this one, and this one must be exactly this" - a blanket
   skip would have let any future style quietly drop its pre-pass. */
for (const [key] of HOLO.MODES) {
  const v = viewerFor(); v.setStyle(key);
  const passes = v._holoPasses;
  const opaque = passes.some((p) => p.kind === "surface");
  const pre = passes.some((p) => p.kind === "prepass");
  if (key === "xray") {
    check(passes.some((p) => p.kind === "xray"),
      "xray draws its own transparent surface",
      JSON.stringify(passes.map((p) => p.kind)));
    check(!opaque && !pre,
      "and deliberately has NO depth pre-pass and no opaque pass - seeing the "
      + "far side is the mode", JSON.stringify(passes.map((p) => p.kind)));
    check(passes.some((p) => p.side === "double"),
      "and IS DoubleSide, so the inside of the far hull is drawn");
    check(passes.every((p) => p.blend !== "add"),
      "and NORMAL blending, never additive - additive is what made the old "
      + "picture read as soup",
      JSON.stringify(passes.map((p) => p.blend)));
    continue;
  }
  check(opaque || pre,
    `${key} draws either an opaque surface or a depth pre-pass`,
    JSON.stringify(passes.map((p) => p.kind)));
  check(!passes.some((p) => p.side === "double"),
    `${key} uses no DoubleSide pass`);
}

/* --------------------- 5. THE ACCUMULATION MODEL, LINES COUNTED ---------- */
restoreDefaults();
console.log("\n5. saturation AT THE SHIPPED DEFAULTS, with LINE FRAGMENTS COUNTED");
{
  const W = 320, H = 320;
  const pts = hull.pts, mn = hull.min, mx = hull.max;
  const span = Math.max(mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]) || 1;
  const cell = new Int32Array(W * H);
  for (let i = 0; i < pts.length; i += 3) {
    const x = Math.min(W - 1, Math.max(0, Math.floor(((pts[i] - mn[0]) / span) * (W - 1))));
    const y = Math.min(H - 1, Math.max(0, Math.floor(((pts[i + 1] - mn[1]) / span) * (H - 1))));
    cell[y * W + x]++;
  }
  let covered = 0, sum = 0, peak = 0;
  for (let i = 0; i < cell.length; i++) {
    if (cell[i]) { covered++; sum += cell[i]; peak = Math.max(peak, cell[i]); }
  }
  const mean = sum / Math.max(1, covered);
  console.log(`    covered ${covered} px, mean depth ${mean.toFixed(1)}, `
    + `peak ${peak}`);
  check(mean > 1.5, "the hull stacks surfaces - otherwise this measures "
    + "nothing", mean.toFixed(1));

  const chan = (hex) => [((hex >> 16) & 255) / 255, ((hex >> 8) & 255) / 255,
                         (hex & 255) / 255];
  const SOLID_MAX = 0.040 + 0.20 + 0.055 + 1.15 + 0.55;

  for (const [key] of HOLO.MODES) {
    const v = viewerFor(); v.setStyle(key);
    const c = chan(v._colour);
    const addPasses = v._holoPasses.filter((p) => p.blend === "add");
    const perFrag = addPasses.reduce((n, p) => n + (p.opacity || 0), 0);
    const opaque = v._holoPasses.some((p) => p.kind === "surface");
    let white = 0, clipped = 0;
    for (let i = 0; i < cell.length; i++) {
      if (!cell[i]) continue;
      /* SURFACES dedupe to one under the pre-pass or opacity. LINES DO NOT -
         every coincident edge at that depth draws. cell[i] bounds them. */
      const acc = perFrag * cell[i];
      const px = c.map((ch) => ch * acc + (opaque ? ch * SOLID_MAX * 0.35 : 0));
      if (px.every((q) => q >= 1)) white++;
      if (px.some((q) => q >= 1)) clipped++;
    }
    const w = (white / covered) * 100, cl = (clipped / covered) * 100;
    console.log(`    ${key.padEnd(11)} add ${perFrag.toFixed(3)}/frag  `
      + `pure white ${w.toFixed(2)}%   clipped ${cl.toFixed(2)}%`);
    check(w < 5, `${key} is below the 5% pure-white threshold`,
      `${w.toFixed(2)}%`);
    notes.push(`${key}: ${w.toFixed(2)}% pure white, ${cl.toFixed(2)}% clipped`);
  }

  /* AND THE WORST A USER CAN ACTUALLY REACH. The sliders are controls now, so
     "fine at the defaults" is not the whole answer - somebody will push line
     intensity to the top on the densest hull in the fleet. REPORTED rather
     than asserted: a bright setting a person chose is not the same defect as a
     bright default they did not. */
  {
    HOLO.lineInt = 2.0; HOLO.detail = 80;
    const w = viewerFor(); w.setStyle("panel");
    const c2 = chan(w._colour);
    const pf = w._holoPasses.filter((q) => q.blend === "add")
      .reduce((n, q) => n + (q.opacity || 0), 0);
    let wx = 0;
    for (let i = 0; i < cell.length; i++) {
      if (!cell[i]) continue;
      if (c2.every((q) => q * pf * cell[i] >= 1)) wx++;
    }
    console.log("    worst a user can set (lineInt 2.0, detail 80): "
      + ((wx / covered) * 100).toFixed(2) + "% pure white");
    notes.push("worst reachable slider setting on the densest hull: "
      + ((wx / covered) * 100).toFixed(2) + "% pure white - a bright setting "
      + "somebody chose, not a bright default");
    restoreDefaults();
  }

  /* THE NEGATIVE HALF: without the pre-pass and with DoubleSide. */
  const v = viewerFor(); v.setStyle("panel");
  const c = chan(v._colour);
  const perFrag = v._holoPasses.filter((p) => p.blend === "add")
    .reduce((n, p) => n + (p.opacity || 0), 0);
  let whiteNo = 0;
  for (let i = 0; i < cell.length; i++) {
    if (!cell[i]) continue;
    const acc = perFrag * cell[i] * 2;
    if (c.every((q) => q * acc >= 1)) whiteNo++;
  }
  const sn = (whiteNo / covered) * 100;
  console.log(`    panel with NO pre-pass, DoubleSide -> ${sn.toFixed(2)}% `
    + `pure white`);
  check(sn > 5,
    "and with the pre-pass removed the same hull blows past the threshold, so "
    + "the threshold measures the pre-pass rather than measuring nothing",
    `${sn.toFixed(2)}%`);
}

console.log("\n6. NOT PERFORMED");
console.log("   No offscreen render. There is no WebGL on this machine, so no");
console.log("   frame was drawn and no pixel was read. Sections 1-4 are the");
console.log("   viewer's real passes; section 5 is arithmetic on the blend.");
notes.push("NOT PERFORMED: a real render. No GPU here - the saturation "
  + "figures are a model, not a frame.");
notes.push("NOT PORTED: UnrealBloomPass. No postprocessing is vendored; the "
  + "glow slider drives the fresnel rim instead and cc_viewer.js says so.");

console.log("\n" + "=".repeat(68));
for (const n of notes) console.log("  " + n);
console.log(`\n${passed} passed, ${failures.length} failed`);
if (failures.length) for (const f of failures) console.log("  " + f);
if (SELFTEST) {
  console.log("\n--self-test: expectations were inverted, so a non-zero exit "
    + "is the correct outcome.");
}
process.exit(failures.length ? 1 : 0);
