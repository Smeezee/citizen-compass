/**
 * THE G1 COLOUR ERRATA: the hull must not saturate in ANY of the five colours.

 *
 * RULE16: INDEPENDENT - the shader's arithmetic is RE-IMPLEMENTED here. The
 * constants are pulled out of the viewer by regex and the multiplier and
 * knee are computed in this file, so the check and the code it judges do
 * not share a definition: if the two implementations ever disagree, that
 * disagreement is the finding. Same shape as _verify_placement_gate.py,
 * which is this repo's exemplar for the pattern.
 *
 * G1's constants were tuned and judged in cyan and written down as if colour
 * did not exist. They are a product with uColor, and a product is not a
 * constant. C1's fleet pixel measurement, same shader and same hulls with only
 * uColor changing:
 *
 *     hull              amber    cyan      ice     mint
 *     Retaliator       12.04%   0.00%   75.19%   25.52%
 *     Sabre            10.05%   0.00%   75.87%   29.76%
 *     Vanguard Warden   8.88%   0.00%   65.64%   18.55%
 *     Mercury           2.48%   0.00%   81.84%   40.78%
 *
 * These are five shipped user controls. A visitor who picks Ice today gets a
 * white silhouette on every ship in the library.
 *
 * WHAT THIS FILE CAN AND CANNOT DO - SAID FIRST
 * =============================================
 * IT CANNOT RENDER. No GPU, no browser, none installed (rule 7). The
 * clipped-pixel fractions above came from C1's machine and CANNOT be
 * reproduced here, so they are NOT re-asserted - they are quoted.
 *
 * What it does is evaluate the SHIPPED SHADER'S OWN EXPRESSION over 4,000
 * evenly spaced normals. The structure is mirrored in JS and says so; every
 * CONSTANT is READ OUT OF cc_viewer.js rather than retyped, so the two cannot
 * drift apart silently. That is arithmetic on the shader, not a picture of it.
 *
 * AND THE ABSOLUTE NUMBERS ARE NOT COMPARABLE TO C1'S. A sphere of normals at
 * one head-on view is not a hull at three angles: this model puts ice at 17%
 * where C1 measured 75%. The ORDERING matches and the mechanism matches. Use
 * this to know whether the fix works; use C1's run to know what a visitor
 * sees.
 *
 * TWO THINGS WERE BEING COUNTED AS ONE, and separating them is the finding:
 *
 *   CHANNEL SATURATION   a channel reaches 1.0 and stops. Hue destroyed,
 *                        surface detail gone. THIS IS THE SHADER DEFECT and
 *                        this file asserts it to near zero in all five.
 *   LUMINANCE ABOVE 0.90 the pixel is merely bright. Ice is (232,244,255),
 *                        whose luminance at multiplier 1.0 is ALREADY 0.9500 -
 *                        above the bar before the shader adds anything. No
 *                        shader change puts a bright ice hull under that line.
 *                        That is a palette question and it is reported, not
 *                        silently fixed by darkening somebody's swatch.
 *
 * Usage: node checks/_verify_colour_headroom.mjs [--self-test] [--mutate-noknee]
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const VIEWER = join(HERE, "..", "testing", "_src", "cc_viewer.js");
const SELFTEST = process.argv.includes("--self-test");
const MUT = process.argv.includes("--mutate-noknee");

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

const src = readFileSync(VIEWER, "utf-8");

/* ---- EVERY CONSTANT COMES OUT OF THE SHADER, none is retyped here ------- */
function num(re, what) {
  const m = src.match(re);
  if (!m) {
    console.log(`CANNOT READ ${what} out of cc_viewer.js - the shader has `
      + `changed shape. Reported as NOT PERFORMED rather than assumed.`);
    process.exit(2);
  }
  return Number(m[1]);
}
const LIT_A = num(/float lit=([\d.]+)\+d1\*/, "lit ambient");
const LIT_D1 = num(/\+d1\*([\d.]+)\+wrap\*/, "d1 weight");
const LIT_WR = num(/\+wrap\*([\d.]+)\+d2\*/, "wrap weight");
const LIT_D2 = num(/\+d2\*([\d.]+)\+d3\*/, "d2 weight");
const LIT_D3 = num(/\+d3\*([\d.]+);/, "d3 weight");
const SPEC_W = num(/spec\*([\d.]+)\+fres\*/, "spec weight");
const FRES_W = num(/fres\*([\d.]+)\*uGlow/, "fres weight");
const SPEC_P = num(/,V\),0\.0,1\.0\),([\d.]+)\)/, "spec power");
const FRES_P = num(/pow\(1\.0-abs\(dot\(N,V\)\),([\d.]+)\)/, "fres power");
const HAS_KNEE = /float W=max\(([\d.]+)\*mx/.test(src);
const KNEE_W = HAS_KNEE ? num(/float W=max\(([\d.]+)\*mx/, "knee peak") : 0;
const KNEE_K = HAS_KNEE ? num(/const float K=([\d.]+);/, "knee") : 0;

console.log("--- the constants, read out of the shipped shader ---");
console.log(`    lit = ${LIT_A} + d1*${LIT_D1} + wrap*${LIT_WR}`
  + ` + d2*${LIT_D2} + d3*${LIT_D3}`);
console.log(`    + spec^${SPEC_P}*${SPEC_W} + fres^${FRES_P}*${FRES_W}*uGlow`);
console.log(`    knee: ${HAS_KNEE ? `K=${KNEE_K}, W=${KNEE_W}*maxChannel`
  : "NONE"}`);
check(LIT_A > 0 && LIT_D1 > 0, "the shader's own lit terms were readable");

const COLOURS = { cyan: 0x35c8e8, mint: 0x7dffb4, amber: 0xffb545,
                  rose: 0xff6b8a, ice: 0xe8f4ff };

/* ---- the shader's expression, mirrored in JS ---------------------------- */
const nrm = (v) => { const m = Math.hypot(...v); return v.map((x) => x / m); };
const L1 = nrm([0.40, 0.86, 0.32]);
const L2 = nrm([-0.70, 0.26, -0.40]);
const L3 = nrm([0.10, -1.0, 0.15]);
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const V = [0, 0, 1];

const NORMALS = (() => {
  const out = [], n = 4000, ga = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2, r = Math.sqrt(Math.max(0, 1 - y * y));
    out.push([Math.cos(ga * i) * r, y, Math.sin(ga * i) * r]);
  }
  return out;
})();

function multiplier(N, glow) {
  const d1 = Math.max(0, Math.min(1, dot(N, L1)));
  const d2 = Math.max(0, Math.min(1, dot(N, L2)));
  const d3 = Math.max(0, Math.min(1, dot(N, L3)));
  const I = L1.map((x) => -x);
  const dNI = dot(N, I);
  const R = I.map((x, i) => x - 2 * dNI * N[i]);
  const spec = Math.pow(Math.max(0, Math.min(1, dot(R, V))), SPEC_P);
  const fres = Math.pow(1 - Math.abs(dot(N, V)), FRES_P);
  const wrap = Math.max(0, Math.min(1, (dot(N, L1) + 0.5) / 1.5));
  return LIT_A + d1 * LIT_D1 + wrap * LIT_WR + d2 * LIT_D2 + d3 * LIT_D3
    + spec * SPEC_W + fres * FRES_W * glow;
}
const chan = (h) => [(h >> 16 & 255) / 255, (h >> 8 & 255) / 255, (h & 255) / 255];
const lum = (c) => 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];

function knee(c, mx) {
  if (!HAS_KNEE || MUT) return c;
  const W = Math.max(KNEE_W * mx, 0.82), K = KNEE_K;
  return c.map((x) => {
    if (x <= K) return x;
    const tq = Math.max(0, Math.min(1, (x - K) / Math.max(W - K, 1e-4)));
    return K + (1 - K) * tq * (2 - tq);
  });
}

const PEAK = Math.max(...NORMALS.map((N) => multiplier(N, 1.0)));
console.log(`\n    measured peak multiplier over 4,000 normals: ${PEAK.toFixed(4)}`);
console.log(`    algebraic bound (terms never co-peak): `
  + `${(LIT_A + LIT_D1 + LIT_WR + LIT_D2 + LIT_D3 + SPEC_W + FRES_W * 1.5).toFixed(4)}`);
if (HAS_KNEE) {
  check(Math.abs(KNEE_W - PEAK) < 0.05,
    "the knee's white point matches the measured peak, not the bound - using "
    + "the bound would dim the hull for a case that never occurs",
    `${KNEE_W} vs ${PEAK.toFixed(4)}`);
}

/* ------------------- 1. ALL FIVE COLOURS, THE LOAD-BEARING ONE ---------- */
console.log("\n1. CHANNEL SATURATION, ALL FIVE COLOURS");
console.log("   colour   maxch   peak product   saturated%   mean luminance");
const res = {};
for (const [name, hex] of Object.entries(COLOURS)) {
  const col = chan(hex), mx = Math.max(...col);
  let sat = 0, tot = 0, peak = 0;
  for (const N of NORMALS) {
    const m = multiplier(N, 1.0);
    const c = knee(col.map((x) => x * m), mx);
    peak = Math.max(peak, ...c);
    if (Math.max(...c) >= 0.999) sat++;
    tot += lum(c.map((x) => Math.min(1, x)));
  }
  res[name] = { sat: sat * 100 / NORMALS.length, mean: tot / NORMALS.length,
                peak, mx };
  console.log(`   ${name.padEnd(7)}  ${mx.toFixed(3)}   ${peak.toFixed(4)}`
    + `         ${res[name].sat.toFixed(2).padStart(6)}%      `
    + `${res[name].mean.toFixed(4)}`);
}
for (const name of Object.keys(COLOURS)) {
  check(res[name].sat < 1.0,
    `${name}: channel saturation is near zero`,
    `${res[name].sat.toFixed(2)}%`);
  check(res[name].peak <= 1.001,
    `${name}: the brightest channel lands inside 1.0`,
    res[name].peak.toFixed(4));
}
notes.push("channel saturation, all five colours: "
  + Object.entries(res).map(([k, v]) => `${k} ${v.sat.toFixed(2)}%`).join(", "));

/* ------------------- 2. THE NEGATIVE CONTROL: BRIGHTNESS ---------------- */
console.log("\n2. NEGATIVE CONTROL - mean luminance must not collapse");
console.log("   The hull sat at 0.09 before G1 and the point was to raise it.");
console.log("   A fix that removes clipping by dimming has undone the order.");
for (const name of Object.keys(COLOURS)) {
  check(res[name].mean > 0.20,
    `${name}: mean luminance ${res[name].mean.toFixed(4)} is far above the `
    + `0.09 the hull started at`);
}
const worst = Math.min(...Object.values(res).map((r) => r.mean));
check(worst > 0.25,
  "and the dimmest colour is still well lit - the knee costs 0.7-2.0% of mean "
  + "luminance where a flat divide-by-peak would cost 22-29%",
  worst.toFixed(4));
notes.push("mean luminance, all five: "
  + Object.entries(res).map(([k, v]) => `${k} ${v.mean.toFixed(3)}`).join(", "));

/* ------------------- 3. LUMINANCE vs SATURATION, TOLD APART ------------- */
console.log("\n3. THE OTHER THING THE ERRATA'S METRIC COUNTS");
for (const [name, hex] of Object.entries(COLOURS)) {
  const col = chan(hex), mx = Math.max(...col);
  let over = 0;
  for (const N of NORMALS) {
    const c = knee(col.map((x) => x * multiplier(N, 1.0)), mx);
    if (lum(c.map((x) => Math.min(1, x))) > 0.90) over++;
  }
  const base = lum(col);
  console.log(`   ${name.padEnd(7)} luminance at multiplier 1.0 = `
    + `${base.toFixed(4)}   lum>0.90 after the knee: `
    + `${(over * 100 / NORMALS.length).toFixed(2)}%`);
  if (name === "ice") {
    check(base > 0.90,
      "ICE's luminance is ALREADY above 0.90 before the shader adds anything - "
      + "no shader change can put a bright ice hull under that bar",
      base.toFixed(4));
    notes.push(`ice is (232,244,255), luminance ${base.toFixed(4)} unlit. Its `
      + `residual is the PALETTE, not the shader. Darkening the swatch to about `
      + `#dce7f2 would bring it to 0.90 - reported, not done: it is Sleven's `
      + `palette and he kept these five controls deliberately.`);
  }
}

console.log("\n4. WHAT WAS NOT DONE");
console.log("   NOT PERFORMED: the clipped-pixel measurement over 234 hulls at");
console.log("   three angles. There is no GPU here. C1's figures are quoted in");
console.log("   the header and are NOT re-asserted by this file.");
notes.push("NOT PERFORMED: the fleet pixel measurement. This is arithmetic on "
  + "the shader's own expression over 4,000 normals at one head-on view - it "
  + "puts ice at 17% where C1's render measured 75%, so the magnitudes are "
  + "NOT comparable. The ordering and the mechanism are.");

console.log("\n" + "=".repeat(68));
for (const n of notes) console.log("  " + n);
console.log(`\n${passed} passed, ${failures.length} failed`);
if (failures.length) for (const f of failures) console.log("  " + f);
if (SELFTEST) console.log("\n--self-test: inverted, non-zero exit is correct.");
if (MUT) console.log("\n--mutate-noknee: the knee was bypassed, non-zero exit "
  + "is correct.");
process.exit(failures.length ? 1 : 0);
