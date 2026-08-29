/**
 * E5 - EVERY HULL STANDS ON THE DISC, AND THE DISC IS SIZED TO THE HULL.

 *
 * RULE16: UNPROVEN - it drives the viewer's OWN frame() and _fitTable(), so the
 * sizing rule being judged is the sizing rule doing the judging. The
 * independent half is the population: every hull in the fleet is put
 * through it rather than a chosen few, so a rule that works on the ships
 * somebody thought of and fails on the Idris is still caught.
 *
 * WHAT THIS DRIVES. The viewer's OWN `frame()` and `_fitTable()`, once per
 * model, against a Box3 built from that model's real measured bounds - the
 * `min`/`max` recorded in data-layer/derived/hull-geometry, which is the same
 * POSITION accessor extent the errata read out of the .glb.
 *
 * WHAT IT CANNOT DO. There is no GPU and no browser here (rule 7). Nothing is
 * rendered and no pixel is read. What is asserted is where `frame()` PUTS the
 * hull and what radius `_fitTable()` gives the disc - arithmetic on the real
 * numbers, run through the shipping code path, reported as that and not as a
 * screenshot.
 *
 * A CORRECTION TO THE ORDER, MEASURED. E5 says "the models are centred on
 * their own origin" and gives per-hull percentages - 75.9% for the Vanguard
 * Harbinger, 4 hulls near the bottom, 224 in the middle, 7 high. Those figures
 * are correct ABOUT THE FILES and this control reproduces them exactly in
 * section 1. They are not what the page did. `frame()` subtracted the
 * BOUNDING-BOX CENTRE, which overrides whatever the file says, so the page
 * buried every hull at exactly 50% - all 235, including the 4 the errata
 * records as already sitting on the disc. The Avenger Stalker measuring
 * "exactly 50.0%" is the tell: a model-origin problem does not land on a round
 * number.
 *
 * So the load-bearing negative fails on 235, where the order predicted at
 * least 224. Both numbers are asserted, because the order's 224 is a real
 * measurement of a real thing and it is worth being able to see that this
 * control reproduces it.
 *
 * MUTATORS
 *   --mutate-centred   frame() goes back to o.position.sub(c). Must bury at
 *                      least 224 hulls - the order's own load-bearing
 *                      negative.
 *   --mutate-fixedring _fitTable stops measuring and returns the prototype's
 *                      1.50. Must fail on the hulls that outgrow it.
 *   --mutate-noclamp   a degenerate footprint yields a zero radius and is
 *                      drawn as nothing, silently.
 */

import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
/* B8's pattern: CC_VIEWER points this at a cc_viewer.js fetched from the
   origin, so the fleet-wide assertions can be re-run against the bytes a
   visitor is actually sent rather than against the working tree. */
const VIEWER = process.env.CC_VIEWER
  || join(ROOT, "testing", "_src", "cc_viewer.js");
const GEO = process.env.CC_GEO_DIR
  || join(ROOT, "data-layer", "derived", "hull-geometry");
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";

let passed = 0;
const failures = [];
const notes = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim());
         console.log(`  FAIL ${label} ${detail}`); }
  return !!ok;
}

/* ---------- the fleet, as measured bounds ---------- */
const HULLS = readdirSync(GEO).filter((f) => f.endsWith(".json"))
  .map((f) => {
    const d = JSON.parse(readFileSync(join(GEO, f), "utf-8"));
    return { name: f.slice(0, -5), min: d.min, max: d.max, count: d.count };
  })
  .filter((h) => Array.isArray(h.min) && Array.isArray(h.max));

if (HULLS.length < 200) {
  console.log(`NOT PERFORMED - only ${HULLS.length} hull bounds found under `
    + `${GEO}. This control is about the whole fleet and will not report a `
    + `pass on a fraction of it.`);
  process.exit(2);
}

const FLAT_PROJECT = MUT === "--mutate-flatproject";
if (FLAT_PROJECT) {
  console.log("*** MUTATED: project() returns world coordinates unchanged - "
    + "the no-op stub that made this control unrunnable. ***");
}

/* ---------- a THREE stub with a Box3 that actually measures ---------- */
function makeThree() {
  const V3 = function (x, y, z) { this.x = x || 0; this.y = y || 0; this.z = z || 0; };
  V3.prototype.sub = function (o) {
    this.x -= o.x; this.y -= o.y; this.z -= o.z; return this;
  };
  V3.prototype.set = function (x, y, z) {
    this.x = x; this.y = y; this.z = z; return this;
  };
  V3.prototype.clone = function () { return new V3(this.x, this.y, this.z); };
  V3.prototype.lengthSq = function () {
    return this.x * this.x + this.y * this.y + this.z * this.z;
  };
  V3.prototype.normalize = function () {
    const l = Math.sqrt(this.lengthSq()) || 1;
    this.x /= l; this.y /= l; this.z /= l; return this;
  };
  V3.prototype.multiplyScalar = function (s) {
    this.x *= s; this.y *= s; this.z *= s; return this;
  };
  V3.prototype.add = function (o) {
    this.x += o.x; this.y += o.y; this.z += o.z; return this;
  };
  V3.prototype.copy = function (o) {
    this.x = o.x; this.y = o.y; this.z = o.z; return this;
  };
  V3.prototype.dot = function (o) {
    return this.x * o.x + this.y * o.y + this.z * o.z;
  };
  V3.prototype.cross = function (o) {
    const x = this.y * o.z - this.z * o.y;
    const y = this.z * o.x - this.x * o.z;
    const z = this.x * o.y - this.y * o.x;
    return this.set(x, y, z);
  };
  V3.prototype.distanceTo = function (o) {
    const dx = this.x - o.x, dy = this.y - o.y, dz = this.z - o.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  };
  /* A REAL PERSPECTIVE PROJECTION, BECAUSE THE NO-OP MADE THIS CONTROL
     UNRUNNABLE AND WOULD HAVE MADE IT WORSE THAN UNRUNNABLE IF PATCHED
     CARELESSLY.

     `project()` used to `return this` - world coordinates, unchanged. When
     G2 added _fitProjected(), the viewer began calling
     `camera.updateMatrixWorld()`, which the stub camera did not have, and the
     whole control died with a TypeError. It has been red ever since, so E5's
     guarantee - the hull stands on the disc - has not been verified on any run
     since that landed.

     THE TEMPTING FIX IS THE DANGEROUS ONE. Adding an empty
     `updateMatrixWorld(){}` makes the crash go away and leaves project()
     returning metres where the viewer expects normalised device coordinates
     between -1 and 1. Every corner would read as a massive overshoot, the fit
     loop would push the camera away six times on every hull, and the control
     would report PASS on a framing nobody had checked. That is the exact
     shape rule 12 names.

     So the projection is the real one: a look-at view basis built from the
     camera's position and the target it is pointed at, then the standard
     perspective divide. Section 0 below proves it against answers known in
     advance before any assertion is allowed to depend on it. */
  V3.prototype.project = function (cam) {
    /* --mutate-flatproject: what the stub did until 2026-08-26 - world
       coordinates returned unchanged, where the viewer expects normalised
       device coordinates. Section 0 must catch it. */
    if (FLAT_PROJECT) { return this; }
    const t = cam.__target || { x: 0, y: 0, z: 0 };
    const fwd = new V3(t.x - cam.position.x, t.y - cam.position.y,
                       t.z - cam.position.z).normalize();
    let right = fwd.clone().cross(new V3(0, 1, 0)).normalize();
    if (!isFinite(right.x) || right.lengthSq() < 1e-12) {
      right = new V3(1, 0, 0);          /* looking straight up or down */
    }
    /* up = right x forward. NO NEGATION: an earlier draft had one and a
       point above the axis projected to y = -1. Section 0 caught it on the
       first run, which is the entire reason section 0 exists - the fleet
       assertions all PASSED with the Y axis upside down, because a symmetric
       fit does not care which way up it is wrong. */
    const up = right.clone().cross(fwd).normalize();
    const d = new V3(this.x - cam.position.x, this.y - cam.position.y,
                     this.z - cam.position.z);
    const vx = d.dot(right), vy = d.dot(up), vz = -d.dot(fwd);
    const f = 1 / Math.tan(cam.fov * Math.PI / 360);
    const n = cam.near, fa = cam.far;
    const w = -vz;
    const cz = ((fa + n) / (n - fa)) * vz + (2 * fa * n) / (n - fa);
    if (w === 0) { return this.set(0, 0, 2); }
    return this.set((f / cam.aspect) * vx / w, f * vy / w, cz / w);
  };

  /* THE BOX3 IS THE WHOLE POINT AND THE OTHER CONTROL'S IS A STUB THAT LIES.
     _verify_holo_render.mjs has getSize() returning 1,1,1 and getCenter()
     returning whatever it was handed, which is harmless there because nothing
     in that file asks where anything IS. Every assertion in this file is about
     exactly that, so this one reads the object's real bounds and applies the
     object's own position, the way setFromObject does. */
  function Box3() {
    this.min = new V3(); this.max = new V3();
    this.setFromObject = function (o) {
      const b = o.__bounds;
      const p = o.position || { x: 0, y: 0, z: 0 };
      this.min.set(b[0][0] + p.x, b[0][1] + p.y, b[0][2] + p.z);
      this.max.set(b[1][0] + p.x, b[1][1] + p.y, b[1][2] + p.z);
      return this;
    };
    this.getCenter = function (v) {
      return v.set((this.min.x + this.max.x) / 2, (this.min.y + this.max.y) / 2,
                   (this.min.z + this.max.z) / 2);
    };
    this.getSize = function (v) {
      return v.set(this.max.x - this.min.x, this.max.y - this.min.y,
                   this.max.z - this.min.z);
    };
  }

  const grp = function () {
    this.children = []; this.visible = true;
    this.position = new V3(); this.scale = new V3(1, 1, 1);
    this.add = function (o) { this.children.push(o); };
  };
  return {
    AdditiveBlending: "ADD", FrontSide: "FRONT", DoubleSide: "DOUBLE",
    Color: function (c) { return { __hex: c, getHex() { return this.__hex; } }; },
    Group: grp, Scene: grp,
    MeshBasicMaterial: function (o) { return Object.assign({ __k: "basic" }, o); },
    ShaderMaterial: function (o) { return Object.assign({ __k: "shader" }, o); },
    LineBasicMaterial: function (o) { return Object.assign({ __k: "line" }, o); },
    PointsMaterial: function (o) { return Object.assign({ __k: "points" }, o); },
    Mesh: function (g, m) {
      this.isMesh = true; this.geometry = g; this.material = m;
      this.userData = {}; this.children = []; this.rotation = { x: 0 };
      this.position = new V3(); this.scale = new V3(1, 1, 1);
      this.add = function (o) { this.children.push(o); };
      this.traverse = function (f) {
        f(this);
        const e = this.children;
        for (let n = 0, i = e.length; n < i; n++) {
          if (e[n].traverse) e[n].traverse(f);
        }
      };
    },
    LineSegments: function () { this.userData = {}; },
    Points: function () { this.userData = {}; },
    GridHelper: function () { this.material = {}; },
    RingGeometry: function (a, b) { this.__inner = a; this.__outer = b; },
    EdgesGeometry: function () { this.attributes = { position: { count: 2 } }; },
    Vector3: V3,
    Box3,
    MathUtils: { degToRad: (d) => d * Math.PI / 180 },
    DirectionalLight: function () { this.position = new V3(); },
    AmbientLight: function () {},
  };
}

/* ---------- load the viewer, mutated if asked ---------- */
const MUTATIONS = {
  "--mutate-centred": [
    [/o\.position\.x -= c\.x;\n    o\.position\.y -= box\.min\.y;\n    o\.position\.z -= c\.z;/,
     "o.position.sub(c);"]],
  "--mutate-fixedring": [
    [/var r = \(foot \/ 2\) \* this\.TABLE_MARGIN;/, "var r = 1.50;"]],
  /* THE NO-OP PROJECTION, PUT BACK - and it is the ONE mutation that does not
     belong in this table.
     Every other entry rewrites cc_viewer.js before it is loaded. project()
     is not in cc_viewer.js; it is this control's own stub, so a source patch
     matched nothing and the run reported "MUTATION DID NOT APPLY" - correctly,
     and only because that guard exists. It is wired to the stub directly
     below instead. Registered here with no patches so the unknown-mutator
     guard still accepts the flag. */
  "--mutate-flatproject": [],
  "--mutate-noclamp": [
    [/if \(!isFinite\(r\) \|\| r <= 0\) \{\n      \/\* Nothing measurable/,
     "if (false) {\n      /* Nothing measurable"]],
};
if (MUT && !MUTATIONS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }

let code = readFileSync(VIEWER, "utf-8");
if (MUT) {
  for (const [pat, rep] of MUTATIONS[MUT]) {
    const before = code;
    code = code.replace(pat, rep);
    if (code === before) {
      console.log(`MUTATION DID NOT APPLY - ${pat} matched nothing, so this `
        + `run proves nothing.`);
      process.exit(1);
    }
  }
}

const THREE = makeThree();
const sandbox = {
  THREE, console, Math, Object, Array, JSON, Number, String, Date, isFinite,
  window: { performance: Date, addEventListener() {} },
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox, { filename: "cc_viewer.js" });
const CCV = vm.runInContext("CCViewer", sandbox);

function viewerFor(hull) {
  const v = Object.create(CCV.Viewer.prototype);
  v.scene = new THREE.Scene();
  /* The camera carries the target it is aimed at, because the stub's
     project() needs a view direction and OrbitControls is what supplies one
     in the real page. Sharing the same Vector3 with `controls.target` is what
     makes `controls.target.set(...)` in frame() actually turn the camera,
     exactly as controls.update() does on the page.
     aspect is 960x540 - the harness stage size the rest of the checks use, so
     a fit measured here is a fit at the size the page is measured at. */
  const target = new THREE.Vector3();
  v.camera = {
    fov: 42, aspect: 960 / 540, position: new THREE.Vector3(),
    near: 0.1, far: 1000, __target: target,
    updateProjectionMatrix() {}, updateMatrixWorld() {},
    /* THE STUB ALWAYS BELIEVED THIS AND THE REAL CAMERA DID NOT DO IT.
       project() above builds its view basis from position and __target, i.e.
       it models a camera that is aimed at its target. Until 2026-08-26 the
       page never called lookAt at all, so that belief was false and this
       control could not see it - the fleet framed at ~850x the hull radius
       while 23 assertions stayed green.
       _fitProjected now aims the camera on every pass, which makes the stub's
       standing assumption TRUE rather than merely convenient. Recording the
       aim point is therefore the faithful implementation here, NOT a no-op
       added to silence a TypeError: if the viewer ever aims somewhere other
       than the fit target, project() follows it. */
    lookAt(t) { this.__target.copy(t); },
  };
  v.controls = { target, update() {} };
  v._colour = 0xffb545;
  const o = new THREE.Mesh({}, null);
  o.__bounds = [hull.min, hull.max];
  const info = v.frame(o);
  return { v, o, info };
}

console.log("==========================================================");
console.log("E5 - the hull stands on the disc, and the disc fits the hull");
console.log(MUT ? `MUTATED: ${MUT}` : "clean viewer");
console.log(`${HULLS.length} hulls, bounds read from ${GEO}`);
console.log("==========================================================");

/* =====================================================================
   1. THE ERRATA'S OWN FIGURES, REPRODUCED FROM THE FILES.
      Not because the page uses them - it does not - but because a control
      that contradicts an order should first show it can produce the order's
      number before it says the order was measuring the wrong thing.
   ===================================================================== */
/* =====================================================================
   0. THE STUB'S OWN PROJECTION, AGAINST ANSWERS KNOWN IN ADVANCE.

   EVERY ASSERTION BELOW DEPENDS ON THIS ARITHMETIC BEING RIGHT, and it is
   arithmetic written for this control rather than the page's own code. A
   projection that is quietly wrong would not crash - it would report a
   confident framing for a camera nobody had checked, on all 239 hulls, and
   that is a worse outcome than the TypeError it replaces.

   So it is checked against a case whose answer is fixed by the definition of
   a perspective camera: at distance d from the camera, the visible half-height
   is exactly d*tan(fov/2) and the half-width is that times the aspect. A point
   on that boundary lands on the edge of the frame, ndc +/-1, or the projection
   is wrong.
   ===================================================================== */
console.log("--- 0. the control's own projection, on known answers ---");
{
  const cam = {
    fov: 42, aspect: 960 / 540, near: 1, far: 101,
    position: new THREE.Vector3(0, 0, 10),
    __target: new THREE.Vector3(0, 0, 0),
  };
  const at = (x, y, z) => new THREE.Vector3(x, y, z).project(cam);
  const near = (a, b, tol) => Math.abs(a - b) <= (tol || 1e-6);

  const centre = at(0, 0, 0);
  record(near(centre.x, 0) && near(centre.y, 0),
    "a point at the camera's target lands dead centre",
    `${centre.x.toFixed(6)}, ${centre.y.toFixed(6)}`);

  /* d = 10 to the target; half-height there is 10*tan(21deg). */
  const d = 10, hh = d * Math.tan(42 * Math.PI / 360), hw = hh * (960 / 540);
  const top = at(0, hh, 0);
  record(near(top.y, 1, 1e-9),
    "a point exactly one half-height above the axis lands on the top edge",
    `y=${top.y.toFixed(9)} at height ${hh.toFixed(4)}`);
  const side = at(hw, 0, 0);
  record(near(side.x, 1, 1e-9),
    "and one half-width to the side lands on the right edge, so ASPECT is "
    + "applied and not ignored", `x=${side.x.toFixed(9)}`);
  const inside = at(hw * 0.5, 0, 0);
  record(inside.x > 0.49 && inside.x < 0.51,
    "half that distance lands halfway - the mapping is linear in the plane",
    `x=${inside.x.toFixed(6)}`);

  /* Depth: the near and far planes are -1 and +1 by definition. */
  const onNear = at(0, 0, 10 - cam.near);
  const onFar = at(0, 0, 10 - cam.far);
  record(near(onNear.z, -1, 1e-9), "a point on the near plane reads z = -1",
    onNear.z.toFixed(9));
  record(near(onFar.z, 1, 1e-9), "a point on the far plane reads z = +1",
    onFar.z.toFixed(9));

  /* BEHIND THE CAMERA IS THE CASE _fitProjected TREATS SPECIALLY, so it has
     to actually be detectable. */
  const behind = at(0, 0, 20);
  record(behind.z > 1,
    "a point BEHIND the camera reads z > 1, which is what _fitProjected "
    + "keys on to refuse a shrinking fit", behind.z.toFixed(4));

  /* AND THE NEGATIVE: the old stub returned world coordinates unchanged.
     If anyone reverts to that, this is the assertion that says so. */
  const far_out = at(0, 500, 0);
  record(Math.abs(far_out.y - 500) > 1,
    "the projection is NOT the identity - the no-op stub this replaces would "
    + "have returned 500 here", far_out.y.toFixed(4));
}

console.log("\n--- 1. the errata's file-space census, reproduced ---");
{
  let bottom = 0, middle = 0, high = 0;
  const fracs = [];
  for (const h of HULLS) {
    const ht = h.max[1] - h.min[1];
    if (ht <= 0) continue;
    const f = (0 - h.min[1]) / ht;
    fracs.push([f, h.name]);
    if (f <= 0.05) bottom++; else if (f >= 0.6) high++; else middle++;
  }
  /* THE TAILS ARE THE FINDING; THE MIDDLE IS JUST EVERYTHING ELSE.
     The errata measured 4 / 224 / 7 over a 235-hull library. P1 added four
     decoded hulls and the middle became 228, so pinning all three numbers
     turned a growing library into a failing control. The two tails are what
     the errata was actually about - the hulls that sink into the disc or float
     above it - so they stay exact, and the middle is asserted to account for
     everything remaining rather than to equal a number from August. A new hull
     landing in either tail still goes red, which is precisely when somebody
     should look. */
  record(bottom === 4 && high === 7 && bottom + middle + high === HULLS.length,
    `y=0 falls near the bottom on 4 and high on 7 - the errata's own tails - `
    + `with the other ${middle} in the middle of a ${HULLS.length}-hull `
    + `library (was 235)`, `${bottom} / ${middle} / ${high}`);
  fracs.sort((a, b) => b[0] - a[0]);
  record(fracs[0][1].indexOf("Vanguard_Harbinger") === 0
    && Math.abs(fracs[0][0] - 0.759) < 0.002,
    "and the worst is the Vanguard Harbinger at 75.9%",
    `${fracs[0][1]} ${(fracs[0][0] * 100).toFixed(1)}%`);
  notes.push(`file-space census: ${bottom} bottom, ${middle} middle, `
    + `${high} high - matches the errata`);
}

/* =====================================================================
   2. WHAT THE PAGE ACTUALLY DID, AND WHAT IT DOES NOW.
   ===================================================================== */
console.log("\n--- 2. no geometry below the disc, fleet-wide ---");
const EPS = 1e-9;
let buried = [];
let moved = 0, worstMove = { by: 0, name: "" };
{
  for (const h of HULLS) {
    const { v, o } = viewerFor(h);
    const box = new THREE.Box3().setFromObject(o);
    const table = v.tableInfo();
    const below = table.y - box.min.y;
    if (below > EPS) {
      const ht = (h.max[1] - h.min[1]) || 1;
      buried.push({ name: h.name, frac: below / ht });
    }
    /* How far this hull's resting position changed. Before E5 the bottom sat
       at -height/2; now it sits at the disc. */
    const ht = (h.max[1] - h.min[1]) || 0;
    const wasBottom = -ht / 2;
    const by = Math.abs(box.min.y - wasBottom);
    if (by > EPS) { moved++; if (by > worstMove.by) worstMove = { by, name: h.name }; }
  }
  record(buried.length === 0,
    `every one of the ${HULLS.length} hulls sits at or above the disc plane`,
    buried.length
      ? `${buried.length} still buried, worst `
        + `${(Math.max(...buried.map((b) => b.frac)) * 100).toFixed(1)}%`
      : "");
  notes.push(`hulls whose resting position changed: ${moved} of ${HULLS.length}`
    + `; the largest move is ${worstMove.by.toFixed(2)} model units on `
    + `${worstMove.name}`);
}

/* =====================================================================
   3. THE ORDER'S LOAD-BEARING NEGATIVE, RUN HERE RATHER THAN ONLY UNDER
      --mutate. The old behaviour is arithmetic and can be evaluated
      directly, so "it would have failed on at least 224" is a measurement in
      the clean run too, not only a claim about a mutated one.
   ===================================================================== */
console.log("\n--- 3. the old behaviour, and how many hulls it buried ---");
{
  let old = 0;
  for (const h of HULLS) {
    const ht = h.max[1] - h.min[1];
    if (ht <= 0) continue;
    /* o.position.sub(centre) leaves the bottom at -height/2, below y=0 for
       every hull with any height at all. */
    if (ht / 2 > EPS) old++;
  }
  record(old >= 224,
    "the behaviour this replaces buried at least the 224 the order predicted",
    `${old} of ${HULLS.length}`);
  record(old === HULLS.length,
    "and in fact ALL of them, at exactly 50% - because frame() subtracted the "
    + "bounding-box centre and overrode whatever each file's origin said",
    `${old}`);
}

/* =====================================================================
   4. THE DISC IS SIZED FROM THE FOOTPRINT.
   ===================================================================== */
console.log("\n--- 4. a disc on every hull, with a radius that fits it ---");
{
  let missing = 0, tooSmall = 0, clamped = [];
  let minR = Infinity, maxR = 0;
  for (const h of HULLS) {
    const { v } = viewerFor(h);
    const t = v.tableInfo();
    if (!(t.radius > 0) || !isFinite(t.radius)) { missing++; continue; }
    const foot = Math.max(h.max[0] - h.min[0], h.max[2] - h.min[2]);
    if (t.radius < foot / 2) tooSmall++;
    if (t.clamped) clamped.push(h.name);
    minR = Math.min(minR, t.radius); maxR = Math.max(maxR, t.radius);
  }
  record(missing === 0,
    `all ${HULLS.length} hulls get a disc with a real radius`,
    missing ? `${missing} degenerate` : "");
  record(tooSmall === 0,
    "and no hull overhangs the disc it is standing on",
    tooSmall ? `${tooSmall} overhang` : "");
  record(clamped.length === 0,
    "and no radius had to be clamped",
    clamped.length ? `clamped: ${clamped.slice(0, 8)}` : "");
  notes.push(`disc radius spans ${minR.toFixed(3)} to ${maxR.toFixed(1)} model `
    + `units across the fleet - the fixed 1.50 it replaces was smaller than `
    + `the half-footprint of `
    + `${HULLS.filter((h) => Math.max(h.max[0] - h.min[0], h.max[2] - h.min[2]) / 2 > 1.5).length}`
    + ` of them`);
}

/* =====================================================================
   5. THE ONE THING THIS MUST NOT DO: MOVE A MARKER RELATIVE TO ITS HULL.
      B5/B6 spent a run on where the dots go. Lifting the hull and leaving
      the dots behind would undo all of it, and it would look like a
      placement regression rather than like this change.
   ===================================================================== */
console.log("\n--- 5. no marker moves relative to its hull ---");
{
  const probes = [[0, 0, 0], [0.5, 0.25, -0.3], [-1, 1, 1], [0.9, -0.8, 0.2]];
  let wrong = 0, checked = 0;
  for (const h of HULLS) {
    const { v, o } = viewerFor(h);
    const box = new THREE.Box3().setFromObject(o);
    const c = box.getCenter(new THREE.Vector3());
    const us = (Math.max(h.max[0] - h.min[0], h.max[1] - h.min[1],
                         h.max[2] - h.min[2]) || 1) / 2;
    for (const [ux, uy, uz] of probes) {
      /* project() adds _hullOrigin, so the WORLD point a marker lands on is
         unit*us + origin. It must equal the hull's own centre plus unit*us -
         which is what it was before the hull was lifted. */
      const org = v._hullOrigin;
      const world = { x: ux * us + org.x, y: uy * us + org.y, z: uz * us + org.z };
      const want = { x: c.x + ux * us, y: c.y + uy * us, z: c.z + uz * us };
      checked++;
      if (Math.abs(world.x - want.x) > 1e-6 * us + 1e-9
        || Math.abs(world.y - want.y) > 1e-6 * us + 1e-9
        || Math.abs(world.z - want.z) > 1e-6 * us + 1e-9) wrong++;
    }
  }
  record(wrong === 0,
    `a marker still lands in the same place on the hull, on all ${checked} `
    + `probes across the fleet`, wrong ? `${wrong} moved` : "");
  /* And the camera follows, or the hull is correct and off screen. */
  const { v } = viewerFor(HULLS.find((h) => h.name.indexOf("Avenger_Stalker") === 0)
    || HULLS[0]);
  record(Math.abs(v.controls.target.y - v._hullOrigin.y) < 1e-9,
    "and the camera looks at the hull's centre rather than at the disc",
    `target.y ${v.controls.target.y}, hull centre ${v._hullOrigin.y}`);
}

/* =====================================================================
   6. THE SHIP SLEVEN PHOTOGRAPHED.
   ===================================================================== */
console.log("\n--- 6. the Avenger Stalker, by name ---");
{
  const h = HULLS.find((x) => x.name === "Avenger_Stalker");
  record(!!h, "the Avenger Stalker's bounds are on disk");
  if (h) {
    const { v, o } = viewerFor(h);
    const box = new THREE.Box3().setFromObject(o);
    const ht = h.max[1] - h.min[1];
    record(Math.abs(box.min.y) < 1e-9,
      "and its bottom is exactly on the disc, not 50.0% under it",
      `min.y ${box.min.y}`);
    notes.push(`Avenger Stalker: was 50.0% buried, now 0.0%; it rose `
      + `${(ht / 2).toFixed(2)} model units, half its own height`);
  }
}

/* =====================================================================
   7. THE DEGENERATE CASE, DRIVEN ON PURPOSE.
      No hull in the fleet has a zero footprint, so the clamp never fires on
      real data - which means without this section it is a guard whose failure
      path has never executed, and rule 12 says that is an untested guard no
      matter how many times the run goes green. --mutate-noclamp proved the
      point by changing nothing: the control could not tell the clamp had been
      removed, because nothing ever reached it.
   ===================================================================== */
console.log("\n--- 7. a hull with no footprint is clamped, and says so ---");
{
  const flat = { name: "__degenerate__", min: [0, -2, 0], max: [0, 2, 0] };
  const { v } = viewerFor(flat);
  const t = v.tableInfo();
  record(t.radius > 0 && isFinite(t.radius),
    "a hull with zero width and zero depth still gets a visible disc",
    `radius ${t.radius}`);
  record(t.clamped === true,
    "and the clamp is REPORTED rather than drawn silently - a zero-radius ring "
    + "renders as nothing, which is indistinguishable from the bug this "
    + "replaces", `clamped=${t.clamped}`);
  /* And an outright empty box, which is what a failed decode looks like. */
  const empty = { name: "__empty__", min: [0, 0, 0], max: [0, 0, 0] };
  const e = viewerFor(empty).v.tableInfo();
  record(e.radius > 0 && isFinite(e.radius) && e.clamped === true,
    "and so does a hull with no extent at all",
    `radius ${e.radius}, clamped ${e.clamped}`);
}

/* ---------- finish ---------- */
console.log("\n==========================================================");
for (const n of notes) console.log("  " + n);
if (failures.length) {
  console.log(`\nFAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  " + f);
  if (MUT) {
    console.log("\n--mutate: a defect was planted, so a non-zero exit is the "
      + "correct outcome.");
  }
  process.exit(1);
}
console.log(`\nAll ${passed} assertions passed against the viewer's own `
  + `frame() and _fitTable(), on all ${HULLS.length} hulls.`);
if (MUT) {
  console.log("\n--mutate: A DEFECT WAS PLANTED AND NOTHING FAILED. This "
    + "control did not measure what it claims to.");
  process.exit(3);
}
process.exit(0);
