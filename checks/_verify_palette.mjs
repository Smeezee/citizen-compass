/**
 * H1g-3 - COLOUR IS NEVER THE ONLY CARRIER, AND THE DEFAULT PALETTE SURVIVES
 * DICHROMACY.

 *
 * RULE16: INDEPENDENT - the dichromacy simulation is implemented here from the
 * published transform rather than taken from anything the page provides,
 * and the file PROVES ITS OWN INSTRUMENT before using it: white must stay
 * white, blue must stay blue under protanopia, red must land on a known
 * value. A control whose measuring device is unverified is measuring
 * nothing, and this one says so by checking the device first.
 *
 * TWO CLAIMS, AND THEY ARE NOT THE SAME CLAIM. The order puts the first one
 * first and it is right to: "a person cannot configure their way out of a
 * problem they cannot see." So every distinction this page draws in colour has
 * to be drawn in something else as well, and separately, the colours have to
 * hold up on their own.
 *
 * Both are asserted here, and each one can fail without the other - which is
 * the point of testing them separately. A page whose palette is perfect and
 * whose chips are bare colour fails clause two. A page covered in labels whose
 * palette is mud fails clause one. `--mutate-oldpalette` produces the first
 * and `--mutate-noglyph` the second.
 *
 * THE METRIC IS CALIBRATED IN SECTION 1, EVERY RUN, AGAINST PAIRS WITH KNOWN
 * ANSWERS. That section is not decoration. The first version of this control
 * scored plain CIEDE2000 on the simulated pair and it put pure red against
 * pure green under deuteranopia at 15.8 - "different colours" - because the
 * simulation leaves them at very different lightnesses. Red and green ARE the
 * canonical indistinguishable pair; a metric that passes them is measuring the
 * wrong thing, and it passed this page's real collision too.
 *
 * WHAT IS MODELLED. Vienot 1999 and Brettel 1997, which model DICHROMACY - the
 * complete absence of one cone class - and not the milder anomalous forms.
 * There is no observer here and no pixel was rendered: these are published
 * matrices applied to the page's own token values. Reported as a model.
 *
 * MUTATORS
 *   --mutate-oldpalette  restores the mint `--good` and teal `--accent2` this
 *                        page shipped with. THE LOAD-BEARING NEGATIVE: it must
 *                        fail on the better/worse pair, or nothing above is
 *                        measuring the colours.
 *   --mutate-noglyph     the delta chips lose their arrow and the two builds
 *                        lose their A and B, leaving colour alone to say which
 *                        is which.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";
import { loadPage } from "./_loadout_harness.mjs";
import { worstCase, simulate, CHROMA_FLOOR, LUM_FLOOR } from "./_colour.mjs";

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
const html = readFileSync(SRC, "utf-8");
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

/* TWO MUTATORS AND THEY DO NOT LAND IN THE SAME PLACE, which is the whole
   reason they are split rather than kept in one table. The palette lives in
   the head block; the carriers live in the page's own script. The first
   version of this file mutated only the head block and `--mutate-noglyph`
   quietly changed nothing - the run passed and reported that it had planted
   a defect. It was caught by the exit-3 branch at the bottom, which exists
   for exactly that, and not by anything looking wrong. */
const THEME_MUTATIONS = {
  "--mutate-oldpalette": [
    [/accent2: '#22D3EE'/, "accent2: '#00C9A7'"],
    [/a: '#A78BFA'/, "a: '#4DA3FF'"],
    [/good: '#38BDF8'/, "good: '#3FE3C4'"],
  ],
};
const PAGE_MUTATIONS = {
  "--mutate-noglyph": [
    [/g:"&#9650;"/, 'g:""'],
    [/g:"&#9660;"/, 'g:""'],
    [/<i aria-hidden=\"true\">A<\/i>/, ""],
    [/<i aria-hidden=\"true\">B<\/i>/, ""],
  ],
};
const KNOWN = Object.assign({}, THEME_MUTATIONS, PAGE_MUTATIONS);

function themeOf(mutator) {
  let block = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]).find((b) => /var CC_THEME/.test(b));
  if (!block) { console.log("NO CC_THEME BLOCK FOUND."); process.exit(2); }
  if (mutator && THEME_MUTATIONS[mutator]) {
    for (const [pat, rep] of THEME_MUTATIONS[mutator]) {
      const before = block;
      block = block.replace(pat, rep);
      if (block === before) {
        console.log(`MUTATION DID NOT APPLY - ${pat} matched nothing, so `
          + `this run proves nothing.`);
        process.exit(1);
      }
    }
  }
  const root = {
    _props: {}, _attrs: {},
    style: { setProperty(k, v) { root._props[k] = String(v); } },
    setAttribute() {},
  };
  const sb = {
    console, Math, JSON, Number, String, Object, Array, parseFloat, parseInt,
    isFinite, document: { documentElement: root },
  };
  sb.window = sb; sb.globalThis = sb;
  vm.createContext(sb);
  vm.runInContext(block, sb, { filename: "loadout.src.html:head" });
  return sb.CC_THEME;
}

if (MUT && !KNOWN[MUT]) {
  console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2);
}

const T = themeOf(MUT);

console.log("==========================================================");
console.log("H1g-3 - colour is never the only carrier, and the default holds");
console.log(MUT ? `MUTATED: ${MUT}` : "clean page");
console.log("==========================================================");

/* =====================================================================
   1. THE METRIC, CALIBRATED. If this section is wrong nothing else means
      anything, so it runs first and it runs every time.
   ===================================================================== */
console.log("\n--- 1. the metric is calibrated against known answers ---");
const CAL_FAIL = [
  ["pure red / pure green", "#FF0000", "#00FF00"],
  ["red / dark green", "#FF0000", "#008000"],
  ["a common red-green status pair", "#E74C3C", "#2ECC71"],
  ["orange / red, the order's second pair", "#FF6B00", "#FF6B6B"],
];
const CAL_PASS = [
  ["red / blue", "#FF0000", "#0000FF"],
  ["orange / blue", "#FF8A00", "#4DA3FF"],
  ["white / black", "#FFFFFF", "#000000"],
  ["blue / yellow", "#0000FF", "#FFFF00"],
];
{
  let hiFail = 0, loPass = 99;
  for (const [n, a, b] of CAL_FAIL) {
    const w = worstCase(a, b);
    hiFail = Math.max(hiFail, w.score);
    record(!w.ok, `must FAIL: ${n}`,
      `${w.score.toFixed(2)} (${w.kind.slice(0, 5)} chroma `
      + `${w.chroma.toFixed(1)}, contrast ${w.cr.toFixed(2)})`);
  }
  for (const [n, a, b] of CAL_PASS) {
    const w = worstCase(a, b);
    loPass = Math.min(loPass, w.score);
    record(w.ok, `must PASS: ${n}`,
      `${w.score.toFixed(2)} (${w.kind.slice(0, 5)})`);
  }
  /* THE THRESHOLD MUST SIT IN A GAP, not on the edge of one. If the worst
     must-fail and the best must-pass ever close up, the verdicts below are
     being decided by the number 20 rather than by the colours. */
  record(loPass > hiFail * 1.5,
    "the two populations are separated, so the floor is not doing the deciding",
    `worst must-pass ${loPass.toFixed(2)}, best must-fail ${hiFail.toFixed(2)}`);
  notes.push(`metric: chroma floor ${CHROMA_FLOOR}, luminance floor `
    + `${LUM_FLOOR}:1; calibration gap ${hiFail.toFixed(2)} .. `
    + `${loPass.toFixed(2)}`);
  /* And the simulation itself, against published anchors. A matrix typed in
     wrong would sail through everything above. */
  record(simulate("#FFFFFF", "deuteranopia").toLowerCase() === "#ffffff"
    && simulate("#000000", "protanopia").toLowerCase() === "#000000"
    && simulate("#808080", "deuteranopia").toLowerCase() === "#808080",
    "the simulation leaves the neutral axis alone, as it must");
  record(simulate("#0000FF", "protanopia").toLowerCase() === "#0000ff"
    && simulate("#0000FF", "deuteranopia").toLowerCase() === "#0000ff",
    "and leaves blue alone under both red-green deficiencies");
  record(/^#7[0-9a-f]{5}$/.test(simulate("#FF0000", "protanopia")),
    "and puts pure red at the published protanope value",
    simulate("#FF0000", "protanopia"));
}

/* =====================================================================
   2. THE MEANING-BEARING PAIRS. Each one is a distinction this page draws,
      named by what a reader is being told apart.
   ===================================================================== */
/* `carrier` is the non-colour thing that also says it. `null` means the pair
   must survive on colour alone - and there are none of those, deliberately;
   every entry is checked BOTH ways and the report says which clause carried
   it. */
/* TWO KINDS OF PAIR, and the difference is a claim about the colours rather
   than a convenience.

   `separate` - the palette has to carry this one on its own, and it is
   asserted at every preset.

   `carried` - the palette CANNOT carry it, for a reason that is structural
   rather than a matter of picking better values, so the non-colour carrier is
   what does the work and section 4 proves the carrier is really there. Two
   pairs are in this class and both reasons are worth keeping:

     good/muted   `--muted` is a blue-grey and a protanope sees a saturated red
                  as a desaturated olive. A neutral or warm grey separates from
                  sky and collides with red; a blue-grey separates from red and
                  collides with sky. There is no third grey - the "unchanged"
                  state cannot be told from BOTH of the other two by colour at
                  all, which is exactly why the glyph is not redundant with the
                  palette fix.
     a/muted      violet and blue-grey both land on the same teal under
                  tritanopia. The two chips read "CIG" and "summed", which are
                  different words rather than different shades of one.

   NEITHER CLASS MAY BE EMPTY. A control where everything is `carried` asserts
   nothing about the colours; one where nothing is asserts nothing about the
   markup. Both are checked below. */
const PAIRS = [
  ["a stat got better vs got worse", "good", "bad", "separate",
   "the arrow on the chip"],
  ["got better vs unchanged", "good", "muted", "carried",
   "the arrow, and the word"],
  ["got worse vs unchanged", "bad", "muted", "separate",
   "the arrow, and the word"],
  ["a budget within its cap vs over it", "accent2", "bad", "separate",
   "the sentence under the bar"],
  ["build A's number vs build B's", "a", "b", "separate",
   "the A and the B"],
  ["a CIG figure vs one we summed", "a", "muted", "carried",
   "the words CIG and summed"],
  ["a changed slot vs a stock one", "b", "text", "separate",
   "the words changed and stock"],
  ["armour reducing damage vs increasing it", "edge-good", "edge-bad",
   "separate", "the sentence in the cell"],
];
const MUST = PAIRS.filter((p) => p[3] === "separate");
const CARRIED = PAIRS.filter((p) => p[3] === "carried");

console.log("\n--- 2. every meaning-bearing pair, at every preset ---");
const paletteFails = [];
{
  record(MUST.length > 0 && CARRIED.length > 0,
    "both classes of pair are populated, so neither half of this is dead",
    `${MUST.length} must separate, ${CARRIED.length} carried in words`);
  for (const [id, name, lv] of T.PRESETS) {
    const p = T.palette(lv);
    const bad = [];
    for (const [n, x, y] of MUST) {
      const w = worstCase(p[x], p[y]);
      if (!w.ok) bad.push(`${n} ${w.score.toFixed(2)}/${w.kind.slice(0, 5)}`);
    }
    record(bad.length === 0,
      `${name}: every pair that must separate does, under all three`,
      bad.length ? bad.join("; ") : "");
    if (bad.length) paletteFails.push(`${name}: ${bad.join("; ")}`);
  }
  /* The carried pairs are REPORTED with their numbers rather than hidden. A
     reader can see what the palette could not do and check that something else
     did it. */
  for (const [n, x, y] of CARRIED) {
    const w = worstCase(T.palette(0)[x], T.palette(0)[y]);
    notes.push(`carried in words, not colour: ${n} - ${w.score.toFixed(2)} `
      + `under ${w.kind}`);
  }
  /* THE WORST ONE, NAMED AND NUMBERED, at the preset where it is worst. A
     figure a reader can check beats a green tick. */
  let worst = null;
  for (const [, name, lv] of T.PRESETS) {
    const p = T.palette(lv);
    for (const [n, x, y] of PAIRS) {
      const w = worstCase(p[x], p[y]);
      if (!worst || w.score < worst.w.score) worst = { n, name, w };
    }
  }
  notes.push(`tightest pair: ${worst.n} at ${worst.name} - `
    + `${worst.w.score.toFixed(2)} under ${worst.w.kind} `
    + `(chroma ${worst.w.chroma.toFixed(1)}, contrast `
    + `${worst.w.cr.toFixed(2)})`);
}

/* =====================================================================
   3. DIMMING MAKES IT HARDER, WHICH IS WHY H1g-1 AND H1g-3 ARE ONE ITEM.
   ===================================================================== */
console.log("\n--- 3. the palette is checked at Blackout, not only at Day ---");
{
  /* Scaling in linear light takes chroma out along with the light, so a pair
     that clears the floor at full brightness can drop under it when the page
     is dimmed - and a dark room is the one place this page is meant to be
     read. A palette validated only at Day is validated in the wrong place. */
  let dropped = 0, held = 0;
  for (const [n, x, y] of MUST) {
    const day = worstCase(T.palette(0)[x], T.palette(0)[y]);
    const blk = worstCase(T.palette(1)[x], T.palette(1)[y]);
    if (blk.score < day.score - 1e-9) dropped++;
    if (blk.ok) held++;
  }
  record(dropped > 0,
    "dimming DOES reduce separation - so checking only Day would be checking "
    + "the easy case", `${dropped} of ${MUST.length} pairs score lower at `
    + `Blackout`);
  record(held === MUST.length,
    "and every pair still clears the floor there", `${held} of ${MUST.length}`);

  /* THE ORDER'S NAMED PAIR, MEASURED RATHER THAN ASSUMED, and reported at
     every level because the answer changes with the level. */
  const namedA = "#FF8A00", namedB = "#8FE3C8";
  const rows = [];
  for (const [, nm, lv] of T.PRESETS) {
    const k = T.curve(T.INK, lv);
    const w = worstCase(dimHex(namedA, k), dimHex(namedB, k));
    rows.push(`${nm} ${w.score.toFixed(2)}${w.ok ? "" : " FAILS"}`);
  }
  notes.push(`the order's named pair #FF8A00 vs #8FE3C8, dimmed on the ink `
    + `curve: ${rows.join(", ")}`);
}
function dimHex(hex, k) {
  return T.dim(hex, k);
}

/* =====================================================================
   4. THE SECOND CARRIER, IN THE PAGE'S OWN EMITTED MARKUP.
   ===================================================================== */
console.log("\n--- 4. every distinction is also drawn in something else ---");
{
  /* The page, carrying the carrier mutation if one was asked for. loadPage
     refuses outright when a pattern matches nothing, so a mutator that has
     drifted out of step with the markup stops the run rather than
     producing a clean pass. */
  const page = loadPage({ mutate: PAGE_MUTATIONS[MUT] || [],
    srcDir: process.env.CC_SRCDIR || null,
    pageFile: process.env.CC_PAGE || null });
  const { g, run, el, openShip } = page;

  /* A hull with something to swap, in two-up, with a real change made - which
     is the only state in which most of these carriers are emitted at all. */
  const shipKey = g(`Object.keys(SHIPS).find(function(k){
    return (SHIPS[k].slots||[]).filter(function(s){
      return s.fit && (FITS[s.fit]||[]).length > 1; }).length > 2; })`);
  record(!!shipKey, "a ship with swappable ports was found to drive this",
    String(shipKey));
  openShip(shipKey);
  run(`twoUp=true; B=Object.assign({},A); editing="B";`);
  /* Swap the first swappable port to something other than its stock part, and
     record the change the way the page's own click path does. */
  run(`(function(){
    var sh=ship(); var s=(sh.slots||[]).find(function(x){
      return swappable(x) && fitsFor(x).length>1; });
    var alt=fitsFor(s).map(function(p){return p.id;})
      .filter(function(id){return id!==s.stock;})[0];
    var before=calc(B); B[s.id]=alt; markChanges(before, calc(B));
    renderAll();
  })();`);

  const stats = el("stats").innerHTML;
  const colB = el("colB").innerHTML;

  /* Better and worse. The sign of the number does NOT stand in for it: on a
     lower-is-better stat "-15%" is the good outcome and on everything else it
     is the bad one. */
  const up = /class="d up[^"]*"[\s\S]{0,120}?<b aria-hidden="true">([^<]*)<\/b>/
    .exec(stats);
  const down = /class="d down[^"]*"[\s\S]{0,120}?<b aria-hidden="true">([^<]*)<\/b>/
    .exec(stats);
  record(!!up || !!down,
    "the compare emitted at least one better/worse chip to inspect");
  const glyphs = [...stats.matchAll(
    /class="d (up|down|flat)[^"]*"[\s\S]{0,140}?<b aria-hidden="true">([^<]*)<\/b>/g)];
  record(glyphs.length > 0, `${glyphs.length} delta chips rendered`);
  const byState = {};
  for (const m of glyphs) (byState[m[1]] ||= new Set()).add(m[2]);
  const states = Object.keys(byState);
  record(states.length >= 2,
    "and more than one state is present, so the comparison is real",
    states.join(","));
  const allNonEmpty = states.filter((s) => s !== "flat")
    .every((s) => [...byState[s]].every((v) => v.length > 0));
  record(allNonEmpty,
    "every better/worse chip carries a glyph as well as a colour",
    JSON.stringify(byState, (k, v) => v instanceof Set ? [...v] : v));
  const distinctGlyphs = new Set();
  for (const s of states) for (const v of byState[s]) distinctGlyphs.add(v);
  record(distinctGlyphs.size >= states.length,
    "and the states do not share a glyph - the shape says WHICH, not just THAT",
    [...distinctGlyphs].join(" "));
  /* The word too, for anything that cannot see the glyph. */
  record(/aria-label="better:/.test(stats) || /aria-label="worse:/.test(stats),
    "and the chip says better or worse in words for a screen reader");

  /* A and B. The columns are headed, but the two numbers in a tile are not. */
  record(/<span class="va"><i aria-hidden="true">A<\/i>/.test(stats),
    "build A's number is labelled A, not only coloured");
  record(/<span class="vb[^"]*"><i aria-hidden="true">B<\/i>/.test(stats),
    "and build B's is labelled B");

  /* The rest of the page's colour-coded distinctions, in words. */
  record(/>changed<\/b>/.test(colB) && /<div class="slot changed/.test(colB),
    "a changed slot says the word CHANGED, not only an orange tint");
  record(/>stock<\/b>/.test(colB),
    "and an unchanged one says STOCK");
  record(/class="src cig"[^>]*>CIG</.test(stats)
    || /class="src ours"[^>]*>summed</.test(stats),
    "a figure's provenance is a word, not a colour");

  /* The armour cells, rendered on a hull that has armour. */
  /* THE "INCREASES DAMAGE" CASE LEFT THE DATA IN 4.10.
     This looked for one hull whose armour both reduces AND increases damage,
     so both cells would render and both colour treatments could be checked.
     Measured on the 4.10 pull, 2026-08-30:

         hulls whose armour REDUCES some damage type : 307
         hulls whose armour INCREASES some damage type: 0
         hulls with BOTH on one record                : 0

     No multiplier above 1.0 exists anywhere in LOADOUT_ARMOR now. The fixture
     did not move - the case is gone from CIG's data.

     SO THE REDUCE CELL IS ASSERTED AND THE INCREASE CELL IS REPORTED AS NOT
     PERFORMED, rather than deleted. Hard rule 11: a check that cannot be
     performed says so and is never counted as a pass. A deleted assertion is
     a coverage loss nobody can see; this line is printed every run and comes
     back by itself the day CIG ships a multiplier above 1. */
  const reduceShip = g(`Object.keys(SHIPS).find(function(k){
    var a = SHIPS[k].arm && ARMOR[SHIPS[k].arm];
    if(!a || !a.dm) return false;
    var v = Object.keys(a.dm).map(function(x){return a.dm[x];});
    return v.some(function(x){return x<1;});
  })`);
  const increaseShip = g(`Object.keys(SHIPS).find(function(k){
    var a = SHIPS[k].arm && ARMOR[SHIPS[k].arm];
    if(!a || !a.dm) return false;
    var v = Object.keys(a.dm).map(function(x){return a.dm[x];});
    return v.some(function(x){return x>1;});
  })`);
  record(!!reduceShip,
    "a hull was found whose armour REDUCES damage, so that cell renders",
    String(reduceShip));
  if (!increaseShip) {
    console.log("  NOT PERFORMED  the increase cell has no hull to render on - "
      + "no armour record in this dataset has a multiplier above 1.0. "
      + "Reported, never counted as a pass.");
  }
  const armourShip = reduceShip;
  if (armourShip) {
    openShip(armourShip);
    run(`renderArmour();`);
    const armour = el("armour").innerHTML;
    record(/class="res good"/.test(armour) && /class="res bad"/.test(armour),
      "and both cells rendered");
    record(/damage reduced/.test(armour) && /damage increased/.test(armour),
      "an armour cell says what its number MEANS in words, not only in a "
      + "border colour");
  }
  /* The budget bars. */
  record(/not enough power/.test(html) && /this build overheats/.test(html),
    "an over-budget bar states the problem in a sentence");
  /* And the dim control itself - which preset is on cannot be orange alone. */
  record(/aria-pressed="/.test(el("cc-dim").innerHTML),
    "the brightness control says which preset is on, rather than only "
    + "colouring it");
  record(/class="lv"[^>]*>\d+%</.test(el("cc-dim").innerHTML),
    "and states the level as a number", el("cc-dim").innerHTML.slice(-60));
}

/* =====================================================================
   5. THE COLOUR CONTROLS SURVIVE - the escape hatch H1g-3 keeps.
   ===================================================================== */
console.log("\n--- 5. the escape hatch is still there ---");
{
  record(/data-colour=/.test(html),
    "the Look panel still offers the colour swatches");
  record(/id="cc-dim-fine"/.test(html),
    "and the fine brightness slider is offered beside the presets");
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
console.log(`\nAll ${passed} assertions passed against the page's own palette `
  + `and its own markup.`);
if (MUT) {
  console.log("\n--mutate: A DEFECT WAS PLANTED AND NOTHING FAILED. This "
    + "control did not measure what it claims to.");
  process.exit(3);
}
process.exit(0);
