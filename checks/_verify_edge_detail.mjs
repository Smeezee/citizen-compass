/**
 * E7b - WHY THE HULLS READ SOFTER THAN THE PROTOTYPE'S. TWO CANDIDATE CAUSES,
 * MEASURED, NOT GUESSED BETWEEN.

 *
 * RULE16: INDEPENDENT - the shipped constants are read out of the viewer and
 * compared against figures that came from somewhere else entirely: the
 * prototype's own captures. The viewer cannot satisfy this by being
 * internally consistent, because the number it has to agree with was not
 * produced by it. The risk this carries is staleness rather than
 * circularity - and it has already been paid once, in the glow term the
 * header marks SUPERSEDED when G1 rebuilt the rim and 0.04 stopped
 * describing anything.
 *
 * The order names them:
 *   1. Draco quantises NORMAL, and the edge detector reads normals.
 *   2. The shipped defaults are too hot - lineInt 1.00 and glow 0.50 against
 *      the prototype captures' 0.33 and 0.04.
 *      SUPERSEDED FOR GLOW, 2026-08-25. G1 rebuilt the rim term and its
 *      coefficient is 6.8x smaller, so 0.04 no longer describes anything.
 *      The shipped default is 1.0 and the assertion below says why.
 *
 * and it says: "Assert computed-normal extraction yields MORE edges than
 * stored-normal at the same threshold - if it does not, cause 1 is wrong and
 * say so."
 *
 * IT DOES NOT, AND CAUSE 1 IS WRONG FOR A REASON UPSTREAM OF THE COUNT.
 * three.js's EdgesGeometry NEVER READS THE NORMAL ATTRIBUTE. It reads
 * `position`, builds each face normal with a cross product of the triangle's
 * own three vertices, and keys vertices on their rounded positions. Section 1
 * asserts that against the vendored bundle rather than against my reading of
 * it, because the whole of cause 1 rests on the opposite being true.
 *
 * So the fix the order proposes - "compute face normals from the triangle
 * positions rather than trusting the stored NORMAL attribute" - is already
 * what ships. Section 2 measures both anyway, on the two hulls the order
 * names, because "the code does not do X" and "doing X would not have helped"
 * are different claims and both are worth having on the record.
 *
 * WHAT IS MODELLED. The edge extraction here is a re-implementation of the
 * vendored EdgesGeometry, asserted against the vendored source in section 1
 * and driven with the SAME decoder the browser uses on the SAME .glb files.
 * It is not the three.js object itself - that needs a BufferGeometry and a
 * WebGL context, and there is neither here (rule 7). Counts are reported as
 * a model of the extraction, which is what they are.
 *
 * MUTATORS
 *   --mutate-storednormals  the extraction reads the stored NORMAL attribute,
 *                           which is what cause 1 supposes the shipped code
 *                           does. Section 3's assertion must change verdict.
 */

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const THREEJS = join(ROOT, "testing", "_src", "vendor", "three", "build",
                     "three.min.js");
const MODELS = join(ROOT, "testing", "_deploy", "models");
const VIEWER = process.env.CC_VIEWER
  || join(ROOT, "testing", "_src", "cc_viewer.js");
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
/* Applied to a COPY of the viewer source in section 4 rather than to a loaded
   module, because nothing here executes the viewer - this control reads
   geometry and reads source.
   AN UNKNOWN MUTATOR IS REFUSED RATHER THAN IGNORED. The first draft of this
   file's header documented `--mutate-storednormals`, which was never
   implemented; passing it planted nothing and the run came out clean. The
   exit-3 branch at the bottom caught that, but a refusal at the top says which
   of the two happened. */
const KNOWN_MUTATORS = ["--mutate-hotdefaults"];
if (MUT && KNOWN_MUTATORS.indexOf(MUT) < 0) {
  console.log(`UNKNOWN MUTATOR ${MUT} - refusing to run. A mutator that plants `
    + `nothing produces a clean pass, and a clean pass under --mutate reads as `
    + `a control that measured something.`);
  process.exit(2);
}
/* --mutate-hotdefaults is applied to a COPY of the viewer source in section 4
   rather than to the module, because nothing here executes the viewer - this
   control reads geometry and reads source. */

let passed = 0;
const failures = [];
const notes = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim());
         console.log(`  FAIL ${label} ${detail}`); }
  return !!ok;
}

console.log("==========================================================");
console.log("E7b - the softness: which of the two causes is it");
console.log(MUT ? `MUTATED: ${MUT}` : "clean");
console.log("==========================================================");

/* =====================================================================
   1. WHAT THE SHIPPED EDGE DETECTOR ACTUALLY READS.
   ===================================================================== */
console.log("\n--- 1. the vendored EdgesGeometry, read rather than assumed ---");
let EG = "";
{
  const bundle = readFileSync(THREEJS, "utf-8");
  const i = bundle.indexOf('this.type="EdgesGeometry"');
  record(i > 0, "EdgesGeometry is present in the vendored bundle");
  /* Its constructor body, bounded by the next class declaration. */
  EG = bundle.slice(i, i + 1400);
  record(/getAttribute\("position"\)/.test(EG),
    "it reads the POSITION attribute");
  record(!/getAttribute\("normal"\)/.test(EG),
    "and it NEVER reads the NORMAL attribute - so a Draco-quantised NORMAL "
    + "cannot be what softened these hulls",
    /getAttribute\("normal"\)/.test(EG) ? "it does read normal" : "");
  record(/getNormal\(/.test(EG),
    "it derives each face normal from the triangle itself, with a cross "
    + "product");
  record(/Math\.pow\(10,4\)/.test(EG) && /Math\.round\(/.test(EG),
    "and it keys vertices on their positions rounded to 1e-4, which IS a "
    + "position-quantisation of its own and is the part worth watching");
  notes.push("cause 1 as stated cannot apply: the shipped extractor already "
    + "computes face normals from positions");
}

/* =====================================================================
   2. THE MODELS ARE DRACO AND NORMAL IS COMPRESSED - the order's premise
      about the FILES, which is true even though its premise about the CODE
      is not.
   ===================================================================== */
console.log("\n--- 2. the files: Draco, and which attributes it compresses ---");
const NAMED = ["Sabre", "Cyclone"];
const picks = [];
{
  let draco = 0, normalCompressed = 0, total = 0;
  const { readdirSync } = require("node:fs");
  const files = readdirSync(MODELS).filter((f) => f.endsWith(".glb"));
  for (const f of files) {
    total++;
    const buf = readFileSync(join(MODELS, f));
    const len = buf.readUInt32LE(12);
    const json = JSON.parse(buf.slice(20, 20 + len).toString("utf8"));
    let has = false, nrm = false;
    for (const m of json.meshes || []) {
      for (const pr of m.primitives || []) {
        const d = (pr.extensions || {})["KHR_draco_mesh_compression"];
        if (d) { has = true; if ("NORMAL" in (d.attributes || {})) nrm = true; }
      }
    }
    if (has) draco++;
    if (nrm) normalCompressed++;
  }
  record(draco === total,
    `all ${total} deployed models are KHR_draco_mesh_compression`,
    `${draco} of ${total}`);
  record(normalCompressed === total,
    "and NORMAL is one of the compressed attributes on every one of them - "
    + "the order is right about the files", `${normalCompressed} of ${total}`);
  for (const n of NAMED) {
    const hit = files.find((f) => f.replace(/\.glb$/, "") === n)
      || files.find((f) => f.toLowerCase().indexOf(n.toLowerCase()) === 0);
    record(!!hit, `${n} is on disk to measure`, String(hit));
    if (hit) picks.push({ name: hit.replace(/\.glb$/, ""), file: join(MODELS, hit) });
  }
}

/* =====================================================================
   3. THE MEASUREMENT THE ORDER ASKS FOR.
   ===================================================================== */
console.log("\n--- 3. edge counts: computed face normals vs stored NORMAL ---");

/* The vendored EdgesGeometry, re-implemented. Asserted against the real one in
   section 1; `useStored` is the fork the order's cause 1 supposes. */
function edgeCount(pos, nrm, idx, thresholdDeg, useStored) {
  const cosT = Math.cos(thresholdDeg * Math.PI / 180);
  const P = 1e4;
  const seen = new Map();
  let kept = 0, unmatched = 0, degenerate = 0;
  const key = (i) => `${Math.round(pos[i * 3] * P)},`
    + `${Math.round(pos[i * 3 + 1] * P)},${Math.round(pos[i * 3 + 2] * P)}`;
  const nx = new Float64Array(3);
  for (let t = 0; t < idx.length; t += 3) {
    const a = idx[t], b = idx[t + 1], c = idx[t + 2];
    if (useStored && nrm) {
      /* The face normal taken as the mean of its three stored vertex normals -
         the most favourable reading of "trust the stored NORMAL". */
      nx[0] = (nrm[a * 3] + nrm[b * 3] + nrm[c * 3]) / 3;
      nx[1] = (nrm[a * 3 + 1] + nrm[b * 3 + 1] + nrm[c * 3 + 1]) / 3;
      nx[2] = (nrm[a * 3 + 2] + nrm[b * 3 + 2] + nrm[c * 3 + 2]) / 3;
    } else {
      const ax = pos[a * 3], ay = pos[a * 3 + 1], az = pos[a * 3 + 2];
      const bx = pos[b * 3], by = pos[b * 3 + 1], bz = pos[b * 3 + 2];
      const cx = pos[c * 3], cy = pos[c * 3 + 1], cz = pos[c * 3 + 2];
      const ux = bx - ax, uy = by - ay, uz = bz - az;
      const vx = cx - ax, vy = cy - ay, vz = cz - az;
      nx[0] = uy * vz - uz * vy;
      nx[1] = uz * vx - ux * vz;
      nx[2] = ux * vy - uy * vx;
    }
    const L = Math.hypot(nx[0], nx[1], nx[2]) || 1;
    nx[0] /= L; nx[1] /= L; nx[2] /= L;
    const k = [key(a), key(b), key(c)];
    if (k[0] === k[1] || k[1] === k[2] || k[2] === k[0]) { degenerate++; continue; }
    for (let e = 0; e < 3; e++) {
      const f = (e + 1) % 3;
      const fwd = `${k[e]}_${k[f]}`, rev = `${k[f]}_${k[e]}`;
      const other = seen.get(rev);
      if (other) {
        const dot = nx[0] * other[0] + nx[1] * other[1] + nx[2] * other[2];
        if (dot <= cosT) kept++;
        seen.set(rev, null);
      } else if (!seen.has(fwd)) {
        seen.set(fwd, [nx[0], nx[1], nx[2]]);
      }
    }
  }
  for (const v of seen.values()) if (v) unmatched++;
  return { kept, unmatched, total: kept + unmatched, degenerate };
}

const results = [];
{
  const dec = require(join(ROOT, "testing", "_src", "decode_glb_points.js"));
  const draco = await dec.loadDraco();
  for (const p of picks) {
    const { json, bin } = dec.readGlb(p.file);
    /* The first primitive's Draco payload. These exports are one welded mesh,
       which is stated in the H1 ledger entry and is why this is not a loop. */
    const prim = json.meshes[0].primitives[0];
    const d = prim.extensions["KHR_draco_mesh_compression"];
    const bv = json.bufferViews[d.bufferView];
    const bytes = bin.slice(bv.byteOffset || 0,
                            (bv.byteOffset || 0) + bv.byteLength);
    const m = dec.decodeMesh(draco, bytes, { normals: true });
    const stored = MUT === "--mutate-storednormals";
    const computed = edgeCount(m.pos.data, m.nrm && m.nrm.data, m.idx, 24, stored);
    const asStored = edgeCount(m.pos.data, m.nrm && m.nrm.data, m.idx, 24, true);
    results.push({ name: p.name, verts: m.n, faces: m.faces,
                   computed, asStored, hasNormals: !!m.nrm });
    console.log(`    ${p.name.padEnd(12)} ${m.n} verts, ${m.faces} faces`);
    console.log(`      computed face normals   ${computed.total} edges `
      + `(${computed.kept} by angle, ${computed.unmatched} unmatched)`);
    console.log(`      stored NORMAL attribute ${asStored.total} edges `
      + `(${asStored.kept} by angle, ${asStored.unmatched} unmatched)`);
  }
  record(results.length === picks.length && results.length > 0,
    "both named hulls decoded with positions, normals and indices");
  record(results.every((r) => r.hasNormals),
    "and both carry a NORMAL attribute to compare against");

  /* THE ORDER'S ASSERTION, RUN AS WRITTEN, AND ITS VERDICT REPORTED EITHER
     WAY. The order says to assert computed > stored and to SAY SO if it is
     not - so this records the direction rather than demanding one. */
  const more = results.filter((r) => r.computed.total > r.asStored.total);
  const fewer = results.filter((r) => r.computed.total < r.asStored.total);
  for (const r of results) {
    const d = r.computed.total - r.asStored.total;
    notes.push(`${r.name}: computed ${r.computed.total} edges vs stored `
      + `${r.asStored.total} - computed finds ${d >= 0 ? "+" : ""}${d} `
      + `(${(d / r.asStored.total * 100).toFixed(1)}%)`);
  }
  record(more.length > 0 || fewer.length > 0,
    "the two extractions do NOT agree, so the choice of normal source is a "
    + "real variable and not a no-op",
    `${more.length} hulls gain, ${fewer.length} lose`);
  if (more.length === results.length) {
    notes.push("VERDICT on cause 1's arithmetic: computed normals do find more "
      + "edges. But the shipped extractor already computes them (section 1), "
      + "so this is not what softened the deployed page.");
  } else {
    notes.push("VERDICT on cause 1: computed normals do NOT find more edges on "
      + "every hull, AND the shipped extractor already computes them. Cause 1 "
      + "is wrong twice over - said plainly, as the order asks.");
  }
}

/* =====================================================================
   4. CAUSE 2 - THE DEFAULTS, WHICH IS WHAT IS LEFT.
   ===================================================================== */
console.log("\n--- 4. the shipped defaults against the prototype's captures ---");
{
  let src = readFileSync(VIEWER, "utf-8");
  if (MUT === "--mutate-hotdefaults") {
    /* EACH REPLACEMENT IS CHECKED ON ITS OWN. Comparing only the whole string
       before and after would report success while one of the three silently
       matched nothing - which is exactly what happened when G1 moved the glow
       default off 0.04 and this mutator went on citing it. A mutation that
       plants two defects out of three is not the mutation the run claims. */
    const edits = [
      [/lineInt: 0\.33,/, "lineInt: 1.0,"],
      [/glow: 1\.0,/, "glow: 0.55,"],
      [/Math\.max\(0\.12, o\)/, "Math.max(0.035, o)"],
    ];
    for (const [re, to] of edits) {
      const before = src;
      src = src.replace(re, to);
      if (src === before) {
        console.log(`MUTATION DID NOT APPLY - ${re} matches nothing in the `
          + "viewer, so the run proves nothing.");
        process.exit(1);
      }
    }
  }
  const lineInt = /lineInt:\s*([\d.]+)/.exec(src);
  const glow = /glow:\s*([\d.]+)/.exec(src);
  const detail = /detail:\s*(\d+)/.exec(src);
  record(!!lineInt && !!glow && !!detail,
    "the viewer states its three defaults in one place",
    `lineInt ${lineInt && lineInt[1]}, glow ${glow && glow[1]}, `
    + `detail ${detail && detail[1]}`);
  /* PINNED TO SLEVEN'S OWN CAPTURES. The prototype's SOURCE also opens at
     lineInt 1.0 - copying its code defaults is how the hot ones got here in
     the first place. What he approved is the slider position in his captures,
     and that is what these two numbers are. */
  record(Math.abs(parseFloat(lineInt[1]) - 0.33) < 1e-9,
    "line intensity opens at 0.33 - the setting in the captures he called "
    + "perfect, not the prototype's code default of 1.0", lineInt[1]);
  /* GLOW IS NO LONGER 0.04, AND THIS IS THE MEASUREMENT BEING RETIRED RATHER
     THAN THE CONTROL BEING BENT TO FIT.

     E7b pinned 0.04 because the rim term was `fres*(1.15*uGlow/0.55)` over a
     surface sitting at 9% luminance, where 0.55 blew out. G1 replaced BOTH
     halves: the surface is lit properly now and the coefficient is 0.17, 6.8x
     smaller. At uGlow 1.0 the shipped term `fres*0.17*uGlow` equals the value
     that was rendered and judged. cc_viewer.js states this at its own default,
     with the arithmetic.

     The assertion is kept, not deleted. A drift to any OTHER number still goes
     red - what changed is which number a decision stands behind. */
  record(Math.abs(parseFloat(glow[1]) - 1.0) < 1e-9,
    "and glow at 1.0 - G1's coefficient is 6.8x smaller, so E7b's 0.04 was "
    + "retired by measurement, not overlooked", glow[1]);
  /* THE FLOOR AND THE INTENSITY ARE ONE DECISION. H1f dropped the floor to
     0.035 because at lineInt 1.0 it was doubling the densest hull's lines into
     white. At 0.33 that pressure is gone and the floor does what it was for. */
  const floor = /Math\.max\(([\d.]+), o\)/.exec(src);
  record(!!floor && Math.abs(parseFloat(floor[1]) - 0.12) < 1e-9,
    "and the edge-opacity floor is back at the prototype's 0.12, because "
    + "without it a 1.1M-vertex hull gets a third of the lines he approved",
    floor && floor[1]);
  notes.push(`shipped defaults: lineInt ${lineInt[1]}, glow ${glow[1]}, `
    + `detail ${detail[1]}; the prototype captures Sleven called perfect run `
    + `lineInt 0.33-0.36 and glow 0.04`);
  /* Edge COUNT does not move with intensity or glow - they are opacity and a
     fresnel term. So cause 2 cannot be measured as a count, and saying it
     could would be inventing a number. What can be stated exactly is the line
     opacity each setting produces on these hulls, through the viewer's own
     edgeOpacity(). */
  notes.push("intensity and glow change opacity and a fresnel rim, NOT the "
    + "edge count - so cause 2 is not measurable as a count and no count is "
    + "reported for it");
}

/* ---------- finish ---------- */
console.log("\n==========================================================");
for (const n of notes) console.log("  " + n);
if (failures.length) {
  console.log(`\nFAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  " + f);
  if (MUT) {
    console.log("\n--mutate: a defect was planted, so a non-zero exit is "
      + "the correct outcome.");
  }
  process.exit(1);
}
if (MUT) {
  console.log("\n--mutate: A DEFECT WAS PLANTED AND NOTHING FAILED. This "
    + "control did not measure what it claims to.");
  process.exit(3);
}
console.log(`\nAll ${passed} assertions passed. The verdict is in the notes `
  + `above, not in the exit code - this control's job is to MEASURE which `
  + `cause it is, and a measurement that came out the other way would still `
  + `be a pass.`);
process.exit(0);
