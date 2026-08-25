/**
 * G1 to G5 - THE HULL READS AS A SOLID OBJECT.
 *
 * WHAT THIS CONTROL CANNOT DO, FIRST, BECAUSE IT BOUNDS EVERYTHING BELOW.
 *
 * The order's load-bearing control is a PIXEL measurement: "report 'not clean
 * surface' per hull, before and after, fleet-wide - the fraction of pixels
 * inside an eroded silhouette that differ from a surface-only pass at the same
 * camera." C1 produced those numbers from a headless browser reading its own
 * framebuffer.
 *
 * THERE IS NO BROWSER AND NO GPU ON THIS MACHINE and none was installed
 * (rule 7). That measurement is NOT PERFORMED here. It is not approximated, it
 * is not swapped for something that sounds similar, and it is not reported as a
 * pass. The same goes for the depth-buffer bit count, which is a property of
 * the WebGL context and cannot be read without one.
 *
 * WHAT IS DONE INSTEAD, and it is a different claim rather than a weaker
 * version of the same one:
 *
 *   the shader constants ARE the order's, read out of the shipped source
 *   the fragment arithmetic is EVALUATED - the head-on brightness that was the
 *     whole defect is computed, before and after, exactly
 *   Lit hull is byte-for-byte unchanged, which is the order's negative control
 *     and is a source-level fact this machine can establish completely
 *   near and far are driven through the REAL frame() over all 235 measured
 *     hulls, with a real perspective projection, at full zoom in and out
 *
 * MUTATORS
 *   --mutate-oldfrag    the 9% shader comes back. The brightness section must
 *                       fail.
 *   --mutate-nowrap     the `wrap` term is dropped - the one the order calls
 *                       load-bearing. Surfaces turning away from the key light
 *                       go black again.
 *   --mutate-linedefault  the default goes back to `solidlines`.
 *   --mutate-offsetsurface  polygonOffset goes back on the depth pre-pass.
 *   --mutate-modelfar   near/far go back to max/500 and max*60.
 */

import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const VIEWER = process.env.CC_VIEWER
  || join(ROOT, "testing", "_src", "cc_viewer.js");
const GEO = process.env.CC_GEO_DIR
  || join(ROOT, "data-layer", "derived", "hull-geometry");

const MUTS = {
  "--mutate-oldfrag": [
    [/float lit=0\.165\+d1\*0\.870\+wrap\*0\.155\+d2\*0\.235\+d3\*0\.070;/,
     "float lit=0.040+d1*0.20+d2*0.055;"],
  ],
  "--mutate-nowrap": [
    [/\+wrap\*0\.155/, "+wrap*0.0"],
  ],
  "--mutate-linedefault": [
    [/DEFAULT: 'solid',/, "DEFAULT: 'solidlines',"],
  ],
  "--mutate-offsetsurface": [
    [/depth: new THREE\.MeshBasicMaterial\(\{\s*colorWrite: false, depthWrite: true \}\),/,
     "depth: new THREE.MeshBasicMaterial({ colorWrite: false, "
     + "depthWrite: true, polygonOffset: true, polygonOffsetFactor: 1.2, "
     + "polygonOffsetUnits: 1.2 }),"],
  ],
  "--mutate-modelfar": [
    [/var near = Math\.max\(dist - r \* 1\.8, dist \* 0\.02\);\s*var far = dist \+ r \* 3\.0;/,
     "var near = (r*2)/500; var far = (r*2)*60;"],
  ],
};
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
if (MUT && !MUTS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }
if (MUT) console.log(`*** MUTATED: ${MUT} ***`);

let passed = 0;
const failures = [];
const notes = [];
const notPerformed = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim());
         console.log(`  FAIL ${label} ${detail}`); }
  return !!ok;
}

let src = readFileSync(VIEWER, "utf-8");
if (MUT) {
  for (const [pat, rep] of MUTS[MUT]) {
    const before = src;
    src = src.replace(pat, rep);
    if (src === before) {
      console.log(`MUTATION DID NOT APPLY - ${pat} matched nothing, so this `
        + `run proves nothing.`);
      process.exit(1);
    }
  }
}

console.log("==========================================================");
console.log("G1-G5 - the hull reads as a solid object");
console.log(MUT ? `MUTATED: ${MUT}` : "clean");
console.log("==========================================================");

/* =====================================================================
   1. G1 - THE CONSTANTS ARE THE ORDER'S.
   ===================================================================== */
console.log("\n--- 1. the shader the order specified, read out of the source ---");
{
  const want = [
    ["L1", "normalize(vec3(0.40,0.86,0.32))"],
    ["L2", "normalize(vec3(-0.70,0.26,-0.40))"],
    ["L3", "normalize(vec3(0.10,-1.0,0.15))"],
    ["specular exponent", "46.0"],
    ["fresnel exponent", "1.0-abs(dot(N,V)),3.2"],
    ["wrap", "clamp((dot(N,L1)+0.50)/1.50,0.0,1.0)"],
    ["lit", "0.165+d1*0.870+wrap*0.155+d2*0.235+d3*0.070"],
    ["combine", "spec*0.42+fres*0.17"],
  ];
  for (const [name, frag] of want) {
    record(src.indexOf(frag) >= 0, `${name} is verbatim from the order`, frag);
  }
  /* THE `wrap` TERM IS THE ONE THE ORDER CALLS LOAD-BEARING. Asserted on its
     own so a build that kept it in the source and multiplied it by zero still
     fails. */
  record(/wrap\*0\.155/.test(src),
    "and `wrap` carries a NON-ZERO coefficient - without it, surfaces turning "
    + "away from the key light go black and the ship loses its far side again");
}

/* =====================================================================
   2. THE ARITHMETIC. The defect was a number; this computes it.
   ===================================================================== */
console.log("\n--- 2. head-on brightness, evaluated ---");
{
  const norm = (v) => {
    const l = Math.hypot(v[0], v[1], v[2]) || 1;
    return [v[0]/l, v[1]/l, v[2]/l];
  };
  const dot = (a, b) => a[0]*b[0] + a[1]*b[1] + a[2]*b[2];
  const cl = (x) => Math.max(0, Math.min(1, x));
  const L1 = norm([0.40, 0.86, 0.32]);
  const L2 = norm([-0.70, 0.26, -0.40]);
  const L3 = norm([0.10, -1.0, 0.15]);

  /* Pull the coefficients out of the SOURCE rather than repeating them, so this
     measures the shipped shader and not a copy of it. */
  const m = /float lit=([\d.]+)\+d1\*([\d.]+)\+wrap\*([\d.]+)\+d2\*([\d.]+)\+d3\*([\d.]+);/
    .exec(src);
  const old = /float lit=([\d.]+)\+d1\*([\d.]+)\+d2\*([\d.]+);/.exec(src);
  const co = m ? m.slice(1).map(Number) : null;
  record(!!co || !!old, "the lit() coefficients are readable from the source",
    m ? m[0] : (old ? old[0] : "neither shape found"));

  const litOf = (N) => {
    const d1 = cl(dot(N, L1)), d2 = cl(dot(N, L2)), d3 = cl(dot(N, L3));
    const wrap = cl((dot(N, L1) + 0.50) / 1.50);
    if (co) return co[0] + d1*co[1] + wrap*co[2] + d2*co[3] + d3*co[4];
    return Number(old[1]) + d1*Number(old[2]) + d2*Number(old[3]);
  };
  /* THE OLD SHADER, FOR COMPARISON. Its numbers are fixed history, not read
     from the file - the file no longer contains them. */
  const litOld = (N) => {
    const nd1 = cl(dot(N, norm([0.35, 0.9, 0.30])));
    const nd2 = cl(dot(N, norm([-0.6, -0.2, -0.5])));
    return 0.040 + nd1*0.20 + nd2*0.055;
  };

  /* A camera looking down -Z at the nose of a ship: the surface normal points
     straight back at it, so fresnel is zero by construction and diffuse is all
     there is. This is the view Sleven could not read. */
  const headOn = [0, 0, 1];
  const now = litOf(headOn), then = litOld(headOn);
  console.log(`    head-on   was ${then.toFixed(4)}   now ${now.toFixed(4)}`
    + `   (${(now/then).toFixed(2)}x)`);
  record(then < 0.12,
    "the OLD shader put a head-on surface at under 12% of the colour - the "
    + "defect, as a number", then.toFixed(4));
  record(now > 0.30,
    "and the new one puts it above 30%, where it reads as a surface",
    now.toFixed(4));
  notes.push(`head-on lit: ${then.toFixed(4)} -> ${now.toFixed(4)} `
    + `(${(now/then).toFixed(2)}x)`);

  /* THE FAR SIDE. A normal turned away from the key light is what `wrap`
     exists for, and it is where a missing wrap term shows. */
  const away = norm([-0.40, -0.86, -0.32]);
  const awayNow = litOf(away);
  console.log(`    away from key light   ${awayNow.toFixed(4)}`);
  record(awayNow > 0.12,
    "a surface turned fully away from the key light still reads - this is what "
    + "the wrap term buys and what its absence costs", awayNow.toFixed(4));

  /* AND NOTHING CLIPS. A shader that fixed darkness by blowing out is a
     different defect. */
  let worst = 0;
  for (let i = 0; i < 4000; i++) {
    const th = Math.acos(1 - 2*((i % 100) / 99));
    const ph = 2*Math.PI*(Math.floor(i/100) / 40);
    const N = [Math.sin(th)*Math.cos(ph), Math.cos(th), Math.sin(th)*Math.sin(ph)];
    worst = Math.max(worst, litOf(N));
  }
  console.log(`    worst lit over 4,000 normals   ${worst.toFixed(4)}`);
  record(worst <= 1.35,
    "and the brightest possible diffuse term stays near 1 - the fix is light, "
    + "not blow-out", worst.toFixed(4));
  notes.push(`worst diffuse lit over 4,000 normals: ${worst.toFixed(4)}`);
}

/* =====================================================================
   3. THE ORDER'S NEGATIVE CONTROL: LIT HULL IS UNTOUCHED.
   ===================================================================== */
console.log("\n--- 3. Lit hull is unchanged ---");
{
  const HULL_FRAG = [
    "var CC_HOLO_FRAG_HULL = [",
  ];
  const i = src.indexOf("var CC_HOLO_FRAG_HULL = [");
  const j = src.indexOf("].join('\\n');", i);
  const body = (i >= 0 && j > i) ? src.slice(i, j) : "";
  record(body.length > 0, "the Lit hull shader is present");
  /* THE ORDER SAYS: judge Lit-hull-to-Lit-hull only. Its own constants are the
     baseline, so they are asserted as literals - if any of them moved, only
     the holo shader was supposed to. */
  for (const frag of ["0.34", "d1*0.86", "d2*0.34", "d3*0.14",
                      "spec*0.95", "fres*0.30"]) {
    record(body.indexOf(frag) >= 0,
      `Lit hull still carries ${frag}`, "");
  }
  record(!/L1=normalize\(vec3\(0\.40,0\.86,0\.32\)\)/.test(body),
    "and it did NOT acquire the holo shader's lights - only the holo shader "
    + "moved");
  void HULL_FRAG;
}

/* =====================================================================
   4. G3 - THE DEFAULT DRAWS NO LINES, AND NOTHING OFFSETS THE SURFACE.
   ===================================================================== */
console.log("\n--- 4. the default style, and polygonOffset ---");
{
  record(/DEFAULT: 'solid',/.test(src),
    "the page opens on `solid`");
  /* THE MISTAKE C1 WROTE DOWN SO IT WOULD NOT BE REPEATED. The depth pre-pass
     IS the hull's surface as far as the depth buffer is concerned, so offsetting
     it displaces the whole hull backwards and the slope-scaled term explodes on
     steep faces - the grid punched through the nose in speckles. */
  const depthMat = /depth: new THREE\.MeshBasicMaterial\(\{[\s\S]*?\}\)/.exec(src);
  record(!!depthMat, "the depth pre-pass material is present");
  record(depthMat && !/polygonOffset/.test(depthMat[0]),
    "and carries NO polygonOffset - offsetting it pushes the whole hull back",
    depthMat ? depthMat[0].replace(/\s+/g, " ").slice(0, 90) : "");
  const edgeMat = /edges: new THREE\.LineBasicMaterial\(\{[\s\S]*?\}\)/.exec(src);
  if (edgeMat && /polygonOffset/.test(edgeMat[0])) {
    const f = /polygonOffsetFactor: (-?[\d.]+)/.exec(edgeMat[0]);
    record(f && Number(f[1]) < 0,
      "the LINES are offset toward the camera, never the surface away",
      f ? f[1] : "");
  } else {
    notes.push("the edge material carries no polygonOffset at all, which is "
      + "also correct - nothing is displaced either way");
  }
  /* And the surface materials themselves. */
  for (const name of ["solid", "hull", "xray"]) {
    const re = new RegExp(name + ": new THREE\\.ShaderMaterial\\(\\{[\\s\\S]*?\\}\\)");
    const mm = re.exec(src);
    if (mm) {
      record(!/polygonOffset/.test(mm[0]),
        `no polygonOffset on the ${name} material`, "");
    }
  }
}

/* =====================================================================
   5. G2 - NEAR AND FAR, DRIVEN THROUGH THE REAL frame() ON EVERY HULL.
   ===================================================================== */
console.log("\n--- 5. the clip planes, fleet-wide, at rest and at both zoom stops ---");
{
  const hulls = readdirSync(GEO).filter((f) => f.endsWith(".json"))
    .map((f) => {
      const d = JSON.parse(readFileSync(join(GEO, f), "utf-8"));
      return { name: f.slice(0, -5), min: d.min, max: d.max };
    })
    .filter((h) => Array.isArray(h.min) && Array.isArray(h.max));
  if (hulls.length < 200) {
    console.log(`    NOT PERFORMED - only ${hulls.length} hull bounds under `
      + `${GEO}`);
    notPerformed.push("the fleet-wide clip-plane sweep: hull bounds absent");
  } else {
    const T = makeThree();
    const sandbox = {
      THREE: T, console, Math, Object, Array, JSON, Number, String, Date,
      isFinite, window: { performance: Date, addEventListener() {} },
    };
    sandbox.globalThis = sandbox;
    vm.createContext(sandbox);
    vm.runInContext(src, sandbox, { filename: "cc_viewer.js" });
    const CCV = vm.runInContext("CCViewer", sandbox);

    let worstRatio = 0, worstName = "", clipped = [], vanished = [], nonPos = [];
    let ratios = [];
    for (const h of hulls) {
      const v = Object.create(CCV.Viewer.prototype);
      v.scene = new T.Scene();
      v.camera = T.makeCamera(42);
      /* ONE target object, shared. The stub's project() needs to know where the
         camera is looking, and the viewer keeps that on controls.target - two
         separate vectors would have the fit loop converging against a look-at
         point the projection never used. */
      v.controls = { target: v.camera.__target, update() {} };
      v._colour = 0xffb545;
      const o = new T.Mesh({}, null);
      o.__bounds = [h.min, h.max];
      v.current = o;
      v.frame(o);
      const c = v.clip();
      if (!c || !(c.near > 0)) { nonPos.push(h.name); continue; }
      ratios.push(c.ratio);
      if (c.ratio > worstRatio) { worstRatio = c.ratio; worstName = h.name; }
      /* AT BOTH ZOOM STOPS. OrbitControls' own limits are not declared here, so
         this drives a decade in each direction, which is more than any wheel
         will do in one gesture. */
      for (const k of [0.1, 0.25, 0.5, 2, 4, 10]) {
        const dir = v.camera.position.clone().sub(v.controls.target);
        v.camera.position.copy(v.controls.target)
          .add(dir.multiplyScalar(k));
        v._clipAt = null;
        v.refreshClip();
        const cc = v.clip();
        if (!cc || !(cc.near > 0)) { nonPos.push(h.name + "@" + k); continue; }
        /* Does the hull still sit between the planes? */
        const box = new T.Box3().setFromObject(o);
        const corners = v._boxCorners(box);
        let nearest = Infinity, furthest = 0;
        for (const p of corners) {
          const d = p.distanceTo(v.camera.position);
          nearest = Math.min(nearest, d); furthest = Math.max(furthest, d);
        }
        if (nearest < cc.near) clipped.push(h.name + "@" + k);
        if (furthest > cc.far) vanished.push(h.name + "@" + k);
        /* put it back */
        const back = v.camera.position.clone().sub(v.controls.target);
        v.camera.position.copy(v.controls.target)
          .add(back.multiplyScalar(1 / k));
      }
    }
    record(nonPos.length === 0,
      `near is positive on all ${hulls.length} hulls at every zoom - a zero `
      + `near makes the projection matrix NaN and the camera never recovers`,
      nonPos.slice(0, 5).join(", "));
    ratios.sort((a, b) => a - b);
    const med = ratios[Math.floor(ratios.length / 2)];
    console.log(`    far/near ratio at rest: median ${med.toFixed(1)}, `
      + `worst ${worstRatio.toFixed(1)} (${worstName})`);
    record(worstRatio < 2000,
      "and far/near is a few hundred to one, not the 30,000:1 the model-sized "
      + "planes gave on every hull", worstRatio.toFixed(1));
    notes.push(`far/near at rest: median ${med.toFixed(1)}, worst `
      + `${worstRatio.toFixed(1)} on ${worstName}`);
    record(clipped.length === 0,
      "no hull clips the near plane at any zoom driven",
      clipped.slice(0, 5).join(", "));
    record(vanished.length === 0,
      "and none passes the far plane", vanished.slice(0, 5).join(", "));
  }
}

/* =====================================================================
   6. G5 - NO EDGE SET FOR THE DEFAULT STYLE.
   ===================================================================== */
console.log("\n--- 6. the edge set is built lazily ---");
{
  /* EdgesGeometry must be constructed inside the branch that draws lines and
     nowhere else. 603,154 segments on a Javelin before the first frame is a
     visible stall on every capital hull, and the old default drew them. */
  const occurrences = (src.match(/new THREE\.EdgesGeometry/g) || []).length;
  record(occurrences === 1,
    "EdgesGeometry is constructed in exactly one place",
    String(occurrences));
  const i = src.indexOf("new THREE.EdgesGeometry");
  const guard = src.lastIndexOf("if (style ===", i);
  const guardLine = src.slice(guard, src.indexOf("{", guard));
  record(/panel/.test(guardLine) && /solidlines/.test(guardLine),
    "and only under the branch for the styles that draw lines",
    guardLine.replace(/\s+/g, " "));
  record(!/solid'\s*\)/.test(guardLine.replace(/solidlines/g, "")),
    "which does not include the default", guardLine.replace(/\s+/g, " "));
}

/* ---------- what was not performed ---------- */
notPerformed.push(
  "the order's load-bearing pixel measurement - 'not clean surface' per hull, "
  + "before and after, fleet-wide. It needs a framebuffer read inside a rAF "
  + "callback. There is no browser and no GPU here (rule 7).");
notPerformed.push(
  "the depth-buffer bit count. It is a property of the WebGL context; C1 "
  + "measured 24 on WebGL2 and that figure stands unverified by this machine.");

console.log("\n==========================================================");
for (const n of notes) console.log("  " + n);
console.log("");
for (const n of notPerformed) console.log("  NOT PERFORMED: " + n);
if (failures.length) {
  console.log(`\nFAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  " + f);
  if (MUT) {
    console.log("\n--mutate: a defect was planted, so a non-zero exit is the "
      + "correct outcome.");
  }
  process.exit(1);
}
if (MUT) {
  console.log("\n--mutate: A DEFECT WAS PLANTED AND NOTHING FAILED. This "
    + "control did not measure what it claims to.");
  process.exit(3);
}
console.log(`\n${passed} assertions passed. The pixel measurements above are `
  + `NOT PERFORMED, not passed.`);
process.exit(0);

/* ---------------------------------------------------------------- the stub */
/* A THREE with a REAL perspective projection, because G2's fit loop projects
   the eight corners of the bounding box and a stub that returned the point
   unchanged would make the loop converge on nothing. Look-at basis, camera-space
   transform, perspective divide - the same arithmetic the GPU does. */
function makeThree() {
  function V3(x, y, z) { this.x = x || 0; this.y = y || 0; this.z = z || 0; }
  V3.prototype.set = function (x, y, z) { this.x=x; this.y=y; this.z=z; return this; };
  V3.prototype.copy = function (o) { this.x=o.x; this.y=o.y; this.z=o.z; return this; };
  V3.prototype.clone = function () { return new V3(this.x, this.y, this.z); };
  V3.prototype.add = function (o) { this.x+=o.x; this.y+=o.y; this.z+=o.z; return this; };
  V3.prototype.sub = function (o) { this.x-=o.x; this.y-=o.y; this.z-=o.z; return this; };
  V3.prototype.multiplyScalar = function (s) { this.x*=s; this.y*=s; this.z*=s; return this; };
  V3.prototype.lengthSq = function () { return this.x*this.x+this.y*this.y+this.z*this.z; };
  V3.prototype.length = function () { return Math.sqrt(this.lengthSq()); };
  V3.prototype.normalize = function () {
    const l = this.length() || 1; return this.multiplyScalar(1/l);
  };
  V3.prototype.distanceTo = function (o) {
    return Math.hypot(this.x-o.x, this.y-o.y, this.z-o.z);
  };
  V3.prototype.project = function (cam) {
    /* camera basis from position -> target */
    const f = new V3(cam.__target.x-cam.position.x, cam.__target.y-cam.position.y,
                     cam.__target.z-cam.position.z).normalize();
    let up = new V3(0, 1, 0);
    if (Math.abs(f.y) > 0.999) up = new V3(0, 0, 1);
    const s = new V3(f.y*up.z-f.z*up.y, f.z*up.x-f.x*up.z, f.x*up.y-f.y*up.x)
      .normalize();
    const u = new V3(s.y*f.z-s.z*f.y, s.z*f.x-s.x*f.z, s.x*f.y-s.y*f.x);
    const d = new V3(this.x-cam.position.x, this.y-cam.position.y,
                     this.z-cam.position.z);
    const cx = d.x*s.x + d.y*s.y + d.z*s.z;
    const cy = d.x*u.x + d.y*u.y + d.z*u.z;
    const cz = d.x*f.x + d.y*f.y + d.z*f.z;   /* + is in front */
    if (cz <= 1e-9) { this.x = 0; this.y = 0; this.z = 2; return this; }
    const t = Math.tan((cam.fov * Math.PI / 180) / 2);
    this.x = cx / (cz * t * (cam.aspect || 1.777));
    this.y = cy / (cz * t);
    this.z = 0;
    return this;
  };
  function Box3() {
    this.min = new V3(); this.max = new V3();
    this.setFromObject = function (o) {
      const b = o.__bounds, p = o.position || { x:0, y:0, z:0 };
      this.min.set(b[0][0]+p.x, b[0][1]+p.y, b[0][2]+p.z);
      this.max.set(b[1][0]+p.x, b[1][1]+p.y, b[1][2]+p.z);
      return this;
    };
    this.getCenter = function (v) {
      return v.set((this.min.x+this.max.x)/2, (this.min.y+this.max.y)/2,
                   (this.min.z+this.max.z)/2);
    };
    this.getSize = function (v) {
      return v.set(this.max.x-this.min.x, this.max.y-this.min.y,
                   this.max.z-this.min.z);
    };
  }
  const grp = function () {
    this.children = []; this.visible = true;
    this.position = new V3(); this.scale = new V3(1,1,1);
    this.add = function (o) { this.children.push(o); };
  };
  return {
    AdditiveBlending: "ADD", NormalBlending: "NORMAL",
    FrontSide: "FRONT", DoubleSide: "DOUBLE",
    Color: function (c) { return { __hex: c, getHex() { return this.__hex; } }; },
    Group: grp, Scene: grp,
    MeshBasicMaterial: function (o) { return Object.assign({ __k:"basic" }, o); },
    ShaderMaterial: function (o) { return Object.assign({ __k:"shader" }, o); },
    LineBasicMaterial: function (o) { return Object.assign({ __k:"line" }, o); },
    PointsMaterial: function (o) { return Object.assign({ __k:"points" }, o); },
    Mesh: function (g, m) {
      this.isMesh = true; this.geometry = g; this.material = m;
      this.userData = {}; this.children = []; this.rotation = { x: 0 };
      this.position = new V3(); this.scale = new V3(1,1,1);
      this.add = function (o) { this.children.push(o); };
      this.traverse = function (f) {
        f(this);
        const e = this.children;
        for (let n = 0, i = e.length; n < i; n++) if (e[n].traverse) e[n].traverse(f);
      };
    },
    LineSegments: function () { this.userData = {}; },
    Points: function () { this.userData = {}; },
    GridHelper: function () { this.material = {}; },
    RingGeometry: function () {},
    EdgesGeometry: function () { this.attributes = { position: { count: 2 } }; },
    Vector3: V3, Box3,
    MathUtils: { degToRad: (d) => d*Math.PI/180 },
    DirectionalLight: function () { this.position = new V3(); },
    AmbientLight: function () {},
    makeCamera: function (fov) {
      const c = {
        fov: fov, aspect: 16/9, near: 0.1, far: 100,
        position: new V3(), __target: new V3(),
        updateProjectionMatrix() {}, updateMatrixWorld() {},
      };
      return c;
    },
  };
}
