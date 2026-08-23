/**
 * H1g-1 and H1g-2 - THE WHOLE PAGE DIMS, AND IT STAYS LEGIBLE WHILE IT DOES.
 *
 * WHAT THIS MEASURES AND WHAT IT CANNOT, stated first because it bounds every
 * number below.
 *
 * The order asks for the page to be RENDERED at each preset and for the
 * brightest rendered element to be under a ceiling. There is no browser on
 * this machine and none was installed (rule 7), so no pixel is read here.
 *
 * What is done instead is stronger than "a class was set" and weaker than a
 * render, and the difference is worth being precise about. The page's colours
 * all come from ONE token set. Section 1 proves that claim by scanning the
 * stylesheet for any colour literal outside the token block - if it finds one,
 * everything after it is void, because a stray `#fff` would be both a colour
 * the dim never reaches and a colour this control never sees. Given that, the
 * brightest token AT a preset is the brightest thing the page can paint at
 * that preset, and that is the figure asserted.
 *
 * The gap that remains: a token could be declared and then never used, which
 * would make the peak pessimistic, not optimistic. Erring bright is the safe
 * direction for a ceiling.
 *
 * MUTATORS
 *   --mutate-modelonly   apply() writes the model's level and nothing else -
 *                        H1f's behaviour, which is the defect H1g-1 names.
 *   --mutate-nofloor     the contrast floor stops firing. H1g-2's negative.
 *   --mutate-alwaysdark  every level renders as Blackout. This is the order's
 *                        own stated negative for H1g-1: without it, a build
 *                        that is simply dark all the time passes every ceiling.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";
import { luminance, contrast, dimBy, over } from "./_colour.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
/* B8's PATTERN: THESE BYTES CAN COME FROM THE ORIGIN.
   `CC_PAGE` points this control at a page fetched from the deployed site and
   `CC_SRCDIR` at the generated data beside it, so "verified from the served
   bytes" means the same assertions ran against what a visitor is actually
   sent - rather than against the working tree, which is a different claim and
   a weaker one. Unset, both default to testing/_src. */
const SRCDIR = process.env.CC_SRCDIR
  || join(HERE, "..", "testing", "_src");
const SRC = process.env.CC_PAGE
  || join(SRCDIR, "loadout.src.html");
const ARG = process.argv.slice(2);
const MUT = ARG.find((a) => a.startsWith("--mutate-")) || "";

const html = readFileSync(SRC, "utf-8");

/* ---------- the reporter ---------- */
let passed = 0;
const failures = [];
const notes = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim());
         console.log(`  FAIL ${label} ${detail}`); }
  return !!ok;
}

/* ---------- load CC_THEME out of the page, mutated if asked ---------- */

const MUTATIONS = {
  "--mutate-modelonly": [
    /if \(root && root\.style && root\.style\.setProperty\) \{/,
    "if (false) {"],
  /* THE FLOOR STOPS EXISTING - floorUp hands back the curve's own answer and
     never checks it against the ground. Aimed at the FUNCTION rather than at
     one line inside it, because the floor is now a solve plus a bisection and
     neutering only the solve would leave the bisection to put it back. */
  "--mutate-nofloor": [
    /CC_THEME\.floorUp = function \(baseHex, k, groundHex\) \{/,
    "CC_THEME.floorUp = function (baseHex, k, groundHex) "
    + "{ return this.dim(baseHex, k); }; "
    + "CC_THEME._retired = function (baseHex, k, groundHex) {"],
  "--mutate-alwaysdark": [
    /var lv = level < 0 \? 0 : \(level > 1 \? 1 : level\);/,
    "var lv = 1;"],
};

function loadTheme(mutator) {
  let block = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]).find((b) => /var CC_THEME/.test(b));
  if (!block) {
    console.log("NO CC_THEME BLOCK FOUND. Refusing to assert against a page "
      + "this cannot drive.");
    process.exit(2);
  }
  if (mutator) {
    const [pattern, replacement] = MUTATIONS[mutator] || [];
    if (!pattern) {
      console.log(`UNKNOWN MUTATOR ${mutator}`);
      process.exit(2);
    }
    const before = block;
    block = block.replace(pattern, replacement);
    if (block === before) {
      console.log(`MUTATION DID NOT APPLY - ${pattern} matched nothing, so `
        + `this run proves nothing.`);
      process.exit(1);
    }
  }
  const root = {
    _props: {}, _attrs: {},
    style: { setProperty(k, v) { root._props[k] = String(v); } },
    setAttribute(k, v) { root._attrs[k] = String(v); },
  };
  const sandbox = {
    console, Math, JSON, Number, String, Object, Array, parseFloat, parseInt,
    isFinite,
    document: { documentElement: root },
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(block, sandbox, { filename: "loadout.src.html:head" });
  return { T: sandbox.CC_THEME, root, sandbox };
}

const { T, root } = loadTheme(MUT);

console.log("==========================================================");
console.log("H1g-1 / H1g-2 - the page dims, and stays legible");
console.log(MUT ? `MUTATED: ${MUT}` : "clean page");
console.log("==========================================================");

/* =====================================================================
   1. EVERY COLOUR IS A TOKEN. Everything downstream depends on this.
   ===================================================================== */
console.log("\n--- 1. the token set is the complete set of colours ---");
{
  const style = html.slice(html.indexOf("<style>"), html.indexOf("</style>"));
  const rootStart = style.indexOf(":root{");
  const rootEnd = style.indexOf("}", style.indexOf("--leaderline"));
  record(rootStart > 0 && rootEnd > rootStart,
    "the stylesheet has one :root token block");
  const outside = style.slice(0, rootStart) + style.slice(rootEnd + 1);
  /* Comments are prose and may quote a colour - the whole point of several of
     them is to record what a value USED to be. Strip them before scanning, or
     the check fails on its own documentation. */
  const code = outside.replace(/\/\*[\s\S]*?\*\//g, "");
  const literals = [...code.matchAll(/#[0-9A-Fa-f]{3,8}\b|rgba?\([^)]*\)/g)]
    .map((m) => m[0]);
  record(literals.length === 0,
    "no colour literal survives outside the token block",
    literals.length ? `found ${literals.length}: ${literals.slice(0, 6)}` : "");
  notes.push(`stylesheet scanned: ${code.length} chars outside :root, `
    + `${literals.length} colour literals`);

  /* The declared Day values and palette(0) must be the same thing. If they
     drift, the page paints one palette before the script runs and a different
     one after - a flash nobody would call a bug because both look plausible. */
  const decl = {};
  for (const m of style.slice(rootStart, rootEnd)
    .matchAll(/--([a-z0-9-]+)\s*:\s*([^;}]+)/gi)) {
    decl[m[1]] = m[2].trim().toLowerCase().replace(/\s+/g, "");
  }
  const day = T.palette(0);
  const drift = Object.keys(day).filter((k) =>
    (decl[k] || "").replace(/\s/g, "") !== String(day[k]).toLowerCase());
  record(drift.length === 0,
    "the stylesheet's Day values ARE palette(0), token for token",
    drift.length ? `drifted: ${drift.slice(0, 6)}` : "");
  record(Object.keys(decl).length === Object.keys(day).length,
    "and neither side declares a token the other does not",
    `css ${Object.keys(decl).length} vs engine ${Object.keys(day).length}`);
}

/* =====================================================================
   2. THE ARITHMETIC AGREES WITH THE CONTROL'S OWN.
      The page cannot import checks/_colour.mjs, so there are two copies of
      the sRGB transfer function and the compositing. Rule 14's hazard, made
      into an asserted invariant instead of a hope: a divergence here would
      mean everything below measures maths the page does not use.
   ===================================================================== */
console.log("\n--- 2. the page's colour maths is the control's colour maths ---");
{
  const probe = Object.values(T.BASE).concat(
    ["#000000", "#FFFFFF", "#010101", "#7F7F7F", "#FF0000"]);
  let lumMax = 0, dimBad = 0, mixBad = 0;
  for (const h of probe) {
    lumMax = Math.max(lumMax, Math.abs(T.lum(h) - luminance(h)));
    for (const k of [0.06, 0.12, 0.4, 0.7, 1, 1.9]) {
      if (T.dim(h, k).toLowerCase() !== dimBy(h, k).toLowerCase()) dimBad++;
    }
    for (const a of [0.08, 0.14, 0.42, 0.65]) {
      if (T.mix(h, a, "#12233A").toLowerCase()
        !== over(h, a, "#12233A").toLowerCase()) mixBad++;
    }
  }
  record(lumMax < 1e-12, "relative luminance agrees to 1e-12",
    `max diff ${lumMax}`);
  record(dimBad === 0, "the linear-light dim agrees on every probe",
    `${dimBad} mismatches`);
  record(mixBad === 0, "compositing agrees on every probe",
    `${mixBad} mismatches`);
}

/* =====================================================================
   3. THE PRESETS EXIST, AND THE CONTROL FOR THEM IS ON THE PAGE.
   ===================================================================== */
console.log("\n--- 3. three presets and a fine slider, in the page chrome ---");
{
  const names = T.PRESETS.map((p) => p[1]);
  record(names.length === 3 && names.join(",") === "Day,Night,Blackout",
    "the three presets are Day, Night and Blackout", names.join(","));
  record(/id="cc-dim"/.test(html),
    "the page carries the brightness group");
  /* IN THE HEADER, NOT OVER THE STAGE. A preset a person reaches for
     mid-flight must not cost an extra click to reveal. */
  const top = html.slice(html.indexOf('<div class="top">'),
    html.indexOf('<div class="acq"'));
  record(/id="cc-dim"/.test(top),
    "and it is in the header bar, so a preset is ONE click, not two");
  /* Its OWN tag, not "somewhere in the next 400 characters" - the first
     version of this line matched the `hidden` on the Back-to-stock button two
     elements later and reported a defect that was not there. An assertion
     whose regexp reaches past its subject measures whatever is nearby. */
  const tag = (top.match(/<div class="dim" id="cc-dim"[^>]*>/) || [""])[0];
  record(tag !== "" && tag.indexOf(" hidden") < 0,
    "and it is not hidden behind a disclosure", tag);
}

/* =====================================================================
   4. H1g-1 - THE BRIGHTEST THING THE PAGE CAN PAINT, AT EACH PRESET.
   ===================================================================== */
console.log("\n--- 4. the brightest element falls with the preset ---");
const CEILING = { day: 1.00, night: 0.50, blackout: 0.30 };
const peaks = {};
{
  const dayPeak = T.peak(0);
  for (const [id, name, lv] of T.PRESETS) {
    const ratio = T.peak(lv) / dayPeak;
    peaks[id] = ratio;
    if (id === "day") continue;
    record(ratio <= CEILING[id],
      `${name}: the brightest token is at or under ${CEILING[id] * 100}% of Day`,
      `measured ${(ratio * 100).toFixed(1)}%`);
  }
  /* THE ORDER'S OWN NEGATIVE, and it is why --mutate-alwaysdark exists: a
     build that renders everything dark whatever you press satisfies every
     ceiling above and is not the feature. */
  record(peaks.day > CEILING.night,
    "Day is NOT below the Night ceiling - the presets actually differ",
    `Day ${(peaks.day * 100).toFixed(1)}% vs ceiling `
    + `${CEILING.night * 100}%`);
  record(peaks.night > peaks.blackout,
    "and Night is brighter than Blackout",
    `${(peaks.night * 100).toFixed(1)}% vs `
    + `${(peaks.blackout * 100).toFixed(1)}%`);

  /* EVERY token falls, not just the brightest. The failure H1g-1 names is a
     dimmed ground with a white number left on it, and a peak taken over the
     whole set would catch that - but only because the white number IS the
     peak. Asserting it token by token catches the same defect on any token. */
  const day = T.palette(0), black = T.palette(1);
  const risen = Object.keys(day).filter((k) => String(day[k]).startsWith("#")
    && luminance(black[k]) > luminance(day[k]) + 1e-9);
  record(risen.length === 0,
    "and NO token is brighter at Blackout than at Day",
    risen.length ? `${risen.length} rose: ${risen.slice(0, 6)}` : "");
  /* EVERY INK LOSES LIGHT. Inks only - grounds are already close to black and
     a face is dark text that has to STAY dark, so requiring those to fall by a
     tenth would be requiring the wrong thing. The first version of this line
     swept all 31 tokens and failed on one of them for exactly that reason. */
  const inks = Object.keys(T.INKS);
  const fell = inks.filter((k) => luminance(black[k]) < luminance(day[k]));
  record(fell.length === inks.length,
    "and EVERY ink lost light",
    `${fell.length} of ${inks.length}: `
    + `${inks.filter((x) => !fell.includes(x))}`);
  /* MOST OF THEM LOSE A LOT. The ones that do not are pinned to the contrast
     floor, and an ink at the floor can only fall as far as its ground falls -
     which is H1g-2 working, not H1g-1 failing. So the exemption is not a list
     of names: a small drop is allowed ONLY where the pair is sitting on the
     floor at Blackout, which is a condition that has to be true of the colour
     rather than asserted about it. */
  const small = inks.filter((k) =>
    luminance(black[k]) >= luminance(day[k]) * 0.9);
  const unpinned = small.filter((k) =>
    contrast(black[k], black[T.INKS[k]]) > T.FLOOR + 0.15);
  record(unpinned.length === 0,
    "and every ink that barely moved is pinned to the contrast floor",
    unpinned.length ? `not pinned: ${unpinned}` : "");
  notes.push(`inks pinned to the floor at Blackout: `
    + `${small.length ? small.join(", ") : "none"}`);
  /* The faces move the other way and that is correct, but it must be true on
     purpose rather than by accident. */
  const faces = Object.keys(T.FACES);
  record(faces.every((k) => luminance(black[k]) <= luminance(day[k]) + 1e-9),
    "and no button face got brighter while the page got darker");
}

/* =====================================================================
   5. H1g-2 - THE CONTRAST FLOOR, AT EVERY PRESET.
   ===================================================================== */
console.log("\n--- 5. every text pair clears the floor, Blackout included ---");
{
  for (const [id, name, lv] of T.PRESETS) {
    const p = T.palette(lv);
    let worst = 99, worstName = "";
    for (const [ink, ground] of Object.entries(T.INKS)) {
      const c = contrast(p[ink], p[ground]);
      if (c < worst) { worst = c; worstName = `${ink} on ${ground}`; }
    }
    record(worst >= T.FLOOR - 1e-9,
      `${name}: every ink clears ${T.FLOOR}:1 against its own ground`,
      `worst ${worst.toFixed(2)} (${worstName})`);
    notes.push(`${name.padEnd(9)} peak ${(peaks[id] * 100).toFixed(1)}% of Day`
      + `   worst text contrast ${worst.toFixed(2)} (${worstName})`);
  }
  /* Button faces are text on a filled accent, which is a pair the ink/ground
     table does not describe - the ground is the accent itself. */
  for (const [id, name, lv] of T.PRESETS) {
    const p = T.palette(lv);
    const pairs = [["onaccent", "accent"], ["onblue", "a"],
                   ["onteal", "accent2"]];
    let worst = 99, wn = "";
    for (const [f, b] of pairs) {
      const c = contrast(p[f], p[b]);
      if (c < worst) { worst = c; wn = `${f} on ${b}`; }
    }
    record(worst >= T.FLOOR - 1e-9,
      `${name}: filled buttons clear the floor too`,
      `worst ${worst.toFixed(2)} (${wn})`);
  }
  /* BLACKOUT IS FLOOR-LIMITED AND THAT IS THE POINT. The curve asks for 12%
     and does not get it; the floor is what decides. If this ever stopped
     being true the floor would have gone slack without anything failing. */
  const black = T.palette(1);
  const bodyContrast = contrast(black.text, black.panel2);
  record(Math.abs(bodyContrast - T.FLOOR) < 0.06,
    "at Blackout the body text sits ON the floor, not above it",
    `contrast ${bodyContrast.toFixed(2)} vs floor ${T.FLOOR}`);
  const curveAsked = T.curve(T.INK, 1);
  const actual = luminance(black.text) / luminance(T.BASE.text);
  record(actual > curveAsked * 1.4,
    "and the floor - not the curve - is what set it",
    `curve asked ${(curveAsked * 100).toFixed(0)}%, floor returned `
    + `${(actual * 100).toFixed(0)}%`);
}

/* =====================================================================
   6. THE FINE SLIDER IS CONTINUOUS AND THE PRESETS SIT ON IT.
   ===================================================================== */
console.log("\n--- 6. the fine slider, and the presets on it ---");
{
  let monotone = true, prev = Infinity;
  for (let i = 0; i <= 100; i++) {
    const v = T.peak(i / 100);
    if (v > prev + 1e-9) monotone = false;
    prev = v;
  }
  record(monotone, "brightness never rises as the slider goes up");
  const distinct = new Set();
  for (let i = 0; i <= 100; i += 5) distinct.add(T.peak(i / 100).toFixed(4));
  record(distinct.size >= 15,
    "and the slider is genuinely continuous, not three values in disguise",
    `${distinct.size} distinct levels across 21 samples`);
  for (const [id, name, lv] of T.PRESETS) {
    record(T.presetAt(lv) === id,
      `${name}'s level is recognised as ${name} by the control`);
  }
  record(T.presetAt(0.31) === null,
    "and a level between two presets lights neither of them");
}

/* =====================================================================
   7. THE PAGE ACTUALLY APPLIES IT. Arithmetic that never reaches the DOM
      is the H1f defect in a new place.
   ===================================================================== */
console.log("\n--- 7. the palette reaches the root element ---");
{
  T.apply(1);
  const written = root._props;
  const day = T.palette(0);
  const missing = Object.keys(day).filter((k) => !(`--${k}` in written));
  record(missing.length === 0,
    "apply() writes EVERY token onto the root element",
    missing.length ? `${missing.length} never written: `
      + `${missing.slice(0, 6)}` : "");
  const black = T.palette(1);
  const wrong = Object.keys(black)
    .filter((k) => written[`--${k}`] !== black[k]);
  record(wrong.length === 0,
    "and writes the values for the level it was given",
    wrong.length ? `${wrong.length} wrong: ${wrong.slice(0, 4)}` : "");
  record(root._attrs["data-dim"] === "blackout",
    "and stamps which preset the page is at",
    `data-dim=${root._attrs["data-dim"]}`);

  /* THE MODEL IS PART OF THE PAGE. H1g-1's whole complaint is that H1f dimmed
     the model alone; the inverse - dimming the page and leaving the model
     bright - is the same defect facing the other way. */
  record(/CC_DIM_SINK/.test(html),
    "the page routes the level to the model as well as to the tokens");
  record(/brightness\('\s*\+\s*k|brightness\('\+k/.test(html)
    || /style\.filter\s*=/.test(html),
    "and the model is scaled rather than left at full brightness");
}

/* =====================================================================
   8. THE LEVEL IS REMEMBERED, AND STORAGE THROWING DOES NOT KILL THE PAGE.
   ===================================================================== */
console.log("\n--- 8. the level survives, and a browser without storage does too ---");
{
  const store = {};
  const s2 = loadThemeWith({
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
  });
  s2.T.apply(0.55); s2.T.save();
  record(store[s2.T.KEY] === "0.55",
    "the level is written to the PERSISTENT store", JSON.stringify(store));
  /* H1f-2: AND IT IS NOT THE SESSION ONE. A brightness chosen for a dark room
     is not a fact about one sitting. Handing the page a session store and no
     persistent one has to leave nothing written - otherwise this file would
     pass against a build that had gone back to a session lifetime. */
  const sessionOnly = {};
  const s2b = loadThemeWith(null, {
    getItem: (k) => (k in sessionOnly ? sessionOnly[k] : null),
    setItem: (k, v) => { sessionOnly[k] = String(v); },
  });
  s2b.T.apply(0.55); s2b.T.save();
  record(Object.keys(sessionOnly).length === 0,
    "and a page with ONLY a session store writes nothing - the lifetime is "
    + "the persistent one and not whatever happens to be available",
    JSON.stringify(sessionOnly));
  const s3 = loadThemeWith({
    getItem: () => "0.55", setItem() {},
  });
  record(Math.abs(s3.T.level - 0.55) < 1e-9,
    "and a fresh load comes back at it", `level ${s3.T.level}`);
  let threw = false;
  try {
    const s4 = loadThemeWith({
      getItem() { throw new Error("storage disabled"); },
      setItem() { throw new Error("storage disabled"); },
    });
    s4.T.save();
    record(s4.T.level === 0,
      "a browser with storage disabled still gets Day, and does not throw");
  } catch (e) { threw = true; }
  record(!threw, "and nothing in the theme path throws when storage does");
}

/* H1f-2: THE PAGE READS localStorage NOW, so this installs one. Leaving the
   parameter named `sessionStorage` and handing it over as that would have made
   every persistence assertion below pass against a page that never wrote
   anything - the guard in CC_THEME._store returns null when the store it wants
   is absent, and a null store swallows every write silently. */
function loadThemeWith(localStorage, sessionStorage) {
  const block = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]).find((b) => /var CC_THEME/.test(b));
  const root2 = {
    _props: {}, _attrs: {},
    style: { setProperty(k, v) { root2._props[k] = String(v); } },
    setAttribute(k, v) { root2._attrs[k] = String(v); },
  };
  const sb = {
    console, Math, JSON, Number, String, Object, Array, parseFloat, parseInt,
    isFinite, localStorage, sessionStorage,
    document: { documentElement: root2 },
  };
  sb.window = sb; sb.globalThis = sb;
  vm.createContext(sb);
  vm.runInContext(block, sb, { filename: "loadout.src.html:head" });
  return { T: sb.CC_THEME, root: root2 };
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
console.log(`\nAll ${passed} assertions passed against the page's own theme.`);
if (MUT) {
  console.log("\n--mutate: A DEFECT WAS PLANTED AND NOTHING FAILED. This "
    + "control did not measure what it claims to.");
  process.exit(3);
}
process.exit(0);
