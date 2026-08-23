/**
 * COLOUR ARITHMETIC FOR H1g. Luminance, contrast, and colour-vision
 * deficiency simulation.
 *
 * WHY THIS IS A MODULE. Three things need it and they must agree: the page's
 * own palette builder (which enforces the contrast floor at run time), the
 * dim control, and the colourblindness control. Three copies of a colour
 * transform is three chances for the page to be measured against maths it does
 * not itself use - rule 14, one writer per fact.
 *
 * WHAT IS MODELLED AND WHAT IS NOT, stated plainly because it bounds every
 * assertion built on this file:
 *
 *   - Contrast is WCAG 2.x relative luminance. That is an exact formula on
 *     sRGB values and is not an approximation of anything.
 *   - CVD simulation is Vienot, Brettel and Mollon 1999 for protanopia and
 *     deuteranopia, and Brettel 1997's two-plane construction for tritanopia.
 *     These model DICHROMACY - the complete absence of one cone class. They do
 *     NOT model anomalous trichromacy, which is far more common and milder.
 *     Simulating the severe case is the conservative choice and it is the one
 *     stated: a pair that survives dichromacy survives the anomalous forms.
 *   - THERE IS NO OBSERVER HERE. These are published matrices applied to
 *     numbers. No person looked at anything. A pair this file calls
 *     distinguishable is one whose SIMULATED coordinates are far apart, which
 *     is a model and is reported as one.
 */

/* ---------- sRGB ---------- */

export function hex2rgb(h) {
  let s = String(h).trim().replace(/^#/, "");
  if (s.length === 3) s = s[0] + s[0] + s[1] + s[1] + s[2] + s[2];
  if (!/^[0-9a-fA-F]{6}$/.test(s)) throw new Error("not a hex colour: " + h);
  return [parseInt(s.slice(0, 2), 16), parseInt(s.slice(2, 4), 16),
          parseInt(s.slice(4, 6), 16)];
}

export function rgb2hex(c) {
  const b = (v) => Math.max(0, Math.min(255, Math.round(v)))
    .toString(16).padStart(2, "0");
  return "#" + b(c[0]) + b(c[1]) + b(c[2]);
}

/* sRGB 0..255 -> linear-light 0..1, the piecewise transfer function. */
export function toLinear(c) {
  return c.map((v) => {
    const x = v / 255;
    return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
  });
}

export function fromLinear(l) {
  return l.map((x) => {
    const v = Math.max(0, Math.min(1, x));
    const s = v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
    return s * 255;
  });
}

/* WCAG relative luminance and contrast ratio. */
export function luminance(hexOrRgb) {
  const rgb = Array.isArray(hexOrRgb) ? hexOrRgb : hex2rgb(hexOrRgb);
  const l = toLinear(rgb);
  return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2];
}

export function contrast(a, b) {
  const la = luminance(a), lb = luminance(b);
  const hi = Math.max(la, lb), lo = Math.min(la, lb);
  return (hi + 0.05) / (lo + 0.05);
}

/* COMPOSITE. Several colours on this page are stated as rgba() over a known
   parent - `.src.cig` is a 16%-alpha blue over the panel. Contrast against the
   declared colour would be measuring a colour nobody ever sees. */
export function over(fgHex, alpha, bgHex) {
  const f = hex2rgb(fgHex), b = hex2rgb(bgHex);
  return rgb2hex([0, 1, 2].map((i) => f[i] * alpha + b[i] * (1 - alpha)));
}

/* SCALE IN LINEAR LIGHT. Multiplying linear-light RGB by k multiplies relative
   luminance by exactly k and leaves the chromaticity alone, so a dimmed colour
   is the same colour with less light rather than a different colour. Doing it
   in sRGB space instead would shift hue and would make the luminance figure a
   guess. */
export function dimBy(hex, k) {
  return rgb2hex(fromLinear(toLinear(hex2rgb(hex)).map((x) => x * k)));
}

/* ---------- CVD ---------- */

/* Linear sRGB -> LMS, Hunt-Pointer-Estevez normalised to D65, as used by
   Vienot 1999. */
const RGB2LMS = [
  [0.31399022, 0.63951294, 0.04649755],
  [0.15537241, 0.75789446, 0.08670142],
  [0.01775239, 0.10944209, 0.87256922]];
const LMS2RGB = [
  [5.47221206, -4.6419601, 0.16963708],
  [-1.1252419, 2.29317094, -0.1678952],
  [0.02980165, -0.19318073, 1.16364789]];

function mul(m, v) {
  return [0, 1, 2].map((i) => m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2]);
}

/* Vienot's single-plane projections. */
const PROTAN = [[0, 1.05118294, -0.05116099], [0, 1, 0], [0, 0, 1]];
const DEUTAN = [[1, 0, 0], [0.9513092, 0, 0.04866992], [0, 0, 1]];
/* Brettel's tritan construction is two half-planes meeting at the neutral
   axis; the plane is chosen by a discriminant on the stimulus. */
const TRITAN_A = [[1, 0, 0], [0, 1, 0], [-0.86744736, 1.86727089, 0]];
const TRITAN_B = [[1, 0, 0], [0, 1, 0], [0.28137855, 0.72806472, 0]];

export const CVD = ["protanopia", "deuteranopia", "tritanopia"];

export function simulate(hex, kind) {
  if (kind === "normal") return rgb2hex(hex2rgb(hex));
  const lin = toLinear(hex2rgb(hex));
  const lms = mul(RGB2LMS, lin);
  let m;
  if (kind === "protanopia") m = PROTAN;
  else if (kind === "deuteranopia") m = DEUTAN;
  else if (kind === "tritanopia") {
    m = (lms[2] / (lms[0] + 1e-12) < 0.3) ? TRITAN_A : TRITAN_B;
  } else throw new Error("unknown deficiency: " + kind);
  return rgb2hex(fromLinear(mul(LMS2RGB, mul(m, lms))));
}

/* ---------- CIELAB and CIEDE2000 ---------- */

function lin2xyz(l) {
  return [
    0.4124564 * l[0] + 0.3575761 * l[1] + 0.1804375 * l[2],
    0.2126729 * l[0] + 0.7151522 * l[1] + 0.0721750 * l[2],
    0.0193339 * l[0] + 0.1191920 * l[1] + 0.9503041 * l[2]];
}

const WHITE = [0.95047, 1.0, 1.08883];

export function lab(hex) {
  const xyz = lin2xyz(toLinear(hex2rgb(hex)));
  const f = (t) => t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116;
  const fx = f(xyz[0] / WHITE[0]), fy = f(xyz[1] / WHITE[1]),
        fz = f(xyz[2] / WHITE[2]);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

/* CIEDE2000. Written out rather than approximated: CIE76 treats a blue
   difference and a yellow difference of the same size as equal, and this
   file's whole job is telling apart colours in the region where that is least
   true. */
export function deltaE(hexA, hexB) {
  return deltaELab(lab(hexA), lab(hexB));
}

export function deltaELab(A, B) {
  const L1 = A[0], a1 = A[1], b1 = A[2];
  const L2 = B[0], a2 = B[1], b2 = B[2];
  const rad = Math.PI / 180, deg = 180 / Math.PI;
  const C1 = Math.hypot(a1, b1), C2 = Math.hypot(a2, b2);
  const Cb = (C1 + C2) / 2;
  const G = 0.5 * (1 - Math.sqrt(Math.pow(Cb, 7)
    / (Math.pow(Cb, 7) + Math.pow(25, 7))));
  const ap1 = (1 + G) * a1, ap2 = (1 + G) * a2;
  const Cp1 = Math.hypot(ap1, b1), Cp2 = Math.hypot(ap2, b2);
  const hpOf = (bb, aa) => {
    if (bb === 0 && aa === 0) return 0;
    const h = Math.atan2(bb, aa) * deg;
    return h < 0 ? h + 360 : h;
  };
  const hp1 = hpOf(b1, ap1), hp2 = hpOf(b2, ap2);
  const dLp = L2 - L1, dCp = Cp2 - Cp1;
  let dhp = 0;
  if (Cp1 * Cp2 !== 0) {
    dhp = hp2 - hp1;
    if (dhp > 180) dhp -= 360; else if (dhp < -180) dhp += 360;
  }
  const dHp = 2 * Math.sqrt(Cp1 * Cp2) * Math.sin((dhp / 2) * rad);
  const Lbp = (L1 + L2) / 2, Cbp = (Cp1 + Cp2) / 2;
  let hbp;
  if (Cp1 * Cp2 === 0) hbp = hp1 + hp2;
  else {
    hbp = hp1 + hp2;
    if (Math.abs(hp1 - hp2) > 180) hbp += (hbp < 360) ? 360 : -360;
    hbp /= 2;
  }
  const T = 1 - 0.17 * Math.cos((hbp - 30) * rad)
    + 0.24 * Math.cos(2 * hbp * rad)
    + 0.32 * Math.cos((3 * hbp + 6) * rad)
    - 0.20 * Math.cos((4 * hbp - 63) * rad);
  const dTh = 30 * Math.exp(-Math.pow((hbp - 275) / 25, 2));
  const Rc = 2 * Math.sqrt(Math.pow(Cbp, 7)
    / (Math.pow(Cbp, 7) + Math.pow(25, 7)));
  const Sl = 1 + (0.015 * Math.pow(Lbp - 50, 2))
    / Math.sqrt(20 + Math.pow(Lbp - 50, 2));
  const Sc = 1 + 0.045 * Cbp;
  const Sh = 1 + 0.015 * Cbp * T;
  const Rt = -Math.sin(2 * dTh * rad) * Rc;
  return Math.sqrt(Math.pow(dLp / Sl, 2) + Math.pow(dCp / Sc, 2)
    + Math.pow(dHp / Sh, 2) + Rt * (dCp / Sc) * (dHp / Sh));
}

/* CHROMATIC DIFFERENCE ALONE - CIEDE2000 with both colours placed at their
   mean lightness.

   WHY THE LIGHTNESS TERM HAS TO COME OUT, and this is the whole reason the
   first version of this file was wrong. Plain CIEDE2000 puts pure red and pure
   green under deuteranopia at 15.8, comfortably "different", because the
   simulation leaves them at L* 62 and L* 83. They are the canonical
   indistinguishable pair. What the simulation destroyed was the HUE, and a
   metric that scores the leftover lightness cannot see that it is gone.
   Holding L* equal asks the question that is actually being asked: shown at
   the same brightness, are these still two colours or one? */
export function chromaDelta(aHex, bHex) {
  const A = lab(aHex), B = lab(bHex);
  const L = (A[0] + B[0]) / 2;
  return deltaELab([L, A[1], A[2]], [L, B[1], B[2]]);
}

/* THE TEST A MEANING-BEARING PAIR HAS TO PASS, and the thresholds are
   CALIBRATED AGAINST PAIRS WITH KNOWN ANSWERS rather than chosen to make this
   page pass. `_verify_palette.mjs` re-runs that calibration every time.

   A pair survives a deficiency if EITHER it still separates as colour
   (chromaDelta >= CHROMA_FLOOR) OR it separates as plain lightness (WCAG
   contrast >= LUM_FLOOR). The second clause is not a loophole - it is why
   black-on-white works for everybody, and dropping it would fail designs that
   are demonstrably usable.

   CHROMA_FLOOR = 20 sits in a real gap. Measured: the worst must-FAIL pair
   (#FF6B6B / #FF8A00 under protanopia) scores 15.5, and the worst must-PASS
   pair (#0000FF / #FFFF00 under tritanopia) scores 32.0. Anything from about
   16 to 31 would give the same verdicts, so the number is not load-bearing.
   LUM_FLOOR = 3.0 is WCAG 1.4.11's own non-text contrast minimum, taken rather
   than invented. */
export const CHROMA_FLOOR = 20;
export const LUM_FLOOR = 3.0;

export function distinguishable(aHex, bHex, kind) {
  const a = simulate(aHex, kind), b = simulate(bHex, kind);
  const chroma = chromaDelta(a, b), cr = contrast(a, b);
  const score = Math.max(chroma / CHROMA_FLOOR, cr / LUM_FLOOR);
  return { ok: score >= 1, score, chroma, cr, a, b, kind };
}

/* The worst of the three deficiencies, which is the one that decides. */
export function worstCase(aHex, bHex) {
  let worst = null;
  for (const k of CVD) {
    const r = distinguishable(aHex, bHex, k);
    if (!worst || r.score < worst.score) worst = r;
  }
  return worst;
}
