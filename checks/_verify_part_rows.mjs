/**
 * E2: no part row is a name and two zeros.

 *
 * RULE16: INDEPENDENT - the parts that HAVE headline stats are counted in the data
 * and every one of them is then required to show them: `shown.length ===
 * withStats.length`. A page that silently dropped a figure it was given
 * cannot pass, because the count it must match was never its own.
 *
 * Sleven, on the Gladius Valiant's `Turret mount · size 3`:
 * "some of them don't provide any information." The row read
 *
 *     Remote Turret / Aegis Dynamics / IR 0   EM 0
 *
 * and the page was not dropping anything - there was nothing else in the
 * record. Measured: 513 of 3,283 parts carry no headline stat at all - no DPS,
 * HP, range, power, cooling, SCU or mass.
 *
 * IR 0 EM 0 IS TRUE AND USELESS. A row of zeros reads as broken data when the
 * part is one whose interesting properties are simply of a different kind.
 *
 * Three things had to be true, and all three are asserted here:
 *
 *   1. the facts a stat-less part DOES have are shown. A turret's gun count
 *      and size, a tank's capacity, an attachment's effect. They were in the
 *      snapshot all along and had never been carried across.
 *   2. IR and EM appear only when non-zero, or beside something else.
 *   3. where a part genuinely has nothing, the row SAYS SO IN WORDS.
 *
 * A ZERO IS A CLAIM. AN ABSENCE IS NOT - the same rule B7 applied to the
 * turret DPS row.
 *
 * EVERY PART IS DRIVEN, not a sample: partRow() is the page's own function and
 * it is called here for all 3,283 of them.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-zeros    IR and EM go back to being pushed unconditionally, which
 *                     is exactly the state Sleven photographed.
 *   --mutate-blank    every row's stats are suppressed - which would satisfy
 *                     "no row is only zeros" perfectly, and is why the
 *                     positive half below is load-bearing.
 *   --self-test       inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_part_rows.mjs
 *        [--self-test] [--mutate-zeros] [--mutate-blank]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_ZEROS = process.argv.includes("--mutate-zeros");
const MUT_BLANK = process.argv.includes("--mutate-blank");

const mutate = [];
if (MUT_ZEROS) {
  mutate.push([/if\(measured\|\|p\.ir\|\|p\.em\)\{[\s\S]*?\n  \}/,
    "bits.push(`<span>IR <b>${p.ir||0}</b></span>`);\n"
    + "  bits.push(`<span>EM <b>${p.em||0}</b></span>`);"]);
  console.log("*** MUTATED: IR and EM are pushed unconditionally again - the "
    + "state Sleven photographed. ***");
}
if (MUT_BLANK) {
  mutate.push([/const measured = bits\.length;/,
               "bits.length = 0; const measured = 0;"]);
  console.log("*** MUTATED: every row's stats are suppressed. \"No row is only "
    + "zeros\" would pass; the POSITIVE half must not. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { PARTS, g, run } = H;

const HEAD = ["dps", "ehp", "qt", "cap", "cool", "scu", "ms"];
const FACT = ["gn", "fuel", "mod"];
const keys = Object.keys(PARTS);

console.log(`--- rendering all ${keys.length} parts through partRow() ---`);
run(`__rows = {}; Object.keys(P).forEach(function(k){ `
  + `__rows[k] = partRow(k, false, false); });`);
const rows = JSON.parse(g("JSON.stringify(__rows)"));
record(Object.keys(rows).length === keys.length,
  "every part in the catalogue rendered a row",
  `${Object.keys(rows).length} of ${keys.length}`);

const stOf = (html) => {
  const m = html.match(/<div class="st">([\s\S]*?)<\/div>\s*$/)
    || html.match(/<div class="st">([\s\S]*?)<\/div>/);
  return m ? m[1] : "";
};
const onlyZeros = (st) =>
  /^<span>IR <b>0<\/b><\/span><span>EM <b>0<\/b><\/span>$/.test(st.trim());

/* ------------------------------- 1. THE DEFECT, GONE ------------------- */
console.log("\n--- 1. no row is a name and two zeros ---");
{
  const bad = keys.filter((k) => onlyZeros(stOf(rows[k])));
  record(bad.length === 0,
    "NO part row renders only IR 0 and EM 0",
    bad.length ? `${bad.length}, e.g. ${bad.slice(0, 3).join(", ")}` : "");
  const anyZeroPair = keys.filter((k) => /IR <b>0<\/b>/.test(rows[k])
    && /EM <b>0<\/b>/.test(rows[k]));
  record(anyZeroPair.every((k) => stOf(rows[k]).split("<span>").length > 3),
    "and where IR 0 and EM 0 do appear, they appear BESIDE something else - "
    + "a zero next to real numbers is information",
    `${anyZeroPair.length} rows carry a zero pair`);
  state.notes.push(`${anyZeroPair.length} rows show IR 0 / EM 0 alongside other `
    + `figures; none shows them alone`);
}

/* ------------------------- 2. THE POSITIVE HALF - it still shows stats -- */
console.log("\n--- 2. a part WITH real stats still shows them ---");
{
  const withStats = keys.filter((k) => HEAD.some((f) => PARTS[k][f]));
  record(withStats.length > 2000, "most parts do have headline stats",
    `${withStats.length} of ${keys.length}`);
  const shown = withStats.filter((k) => {
    const st = stOf(rows[k]);
    return /DPS|HP|Range|Power|Cooling|SCU|Mass/.test(st);
  });
  record(shown.length === withStats.length,
    "and EVERY one of them still renders at least one - without this, a build "
    + "that blanked every row would pass section 1 perfectly",
    `${shown.length} of ${withStats.length}`);

  /* Sleven's own row, by name. */
  const gun = keys.find((k) => PARTS[k].dps > 100);
  record(/DPS <b>/.test(stOf(rows[gun])),
    `a real gun still shows its DPS - ${PARTS[gun].n}`);
}

/* --------------------- 3. THE FACTS OF A DIFFERENT KIND ---------------- */
console.log("\n--- 3. a stat-less part shows what it IS ---");
{
  const bare = keys.filter((k) => !HEAD.some((f) => PARTS[k][f]));
  const withFact = bare.filter((k) => FACT.some((f) => PARTS[k][f]));
  /* "NOTHING" MEANS NOTHING, and the first version of this line got that
     wrong. Fourteen parts were counted as having nothing while carrying a
     non-zero EM of 17,000, a power draw of 8 and a detection range - facts
     partRow() simply had never rendered. The control was right that the rows
     were poor and wrong about why. partRow() now renders draw and detection,
     and this classifies on everything a row can actually show. */
  const SHOWN = HEAD.concat(FACT, ["pw", "sens", "ir", "em"]);
  const nothing = bare.filter((k) => !SHOWN.some((f) => PARTS[k][f]));
  console.log(`    ${bare.length} parts carry no headline stat`);
  console.log(`      ${withFact.length} now carry a fact of another kind`);
  console.log(`      ${nothing.length} genuinely have nothing`);
  record(bare.length > 400, "the population the errata measured is still there",
    `${bare.length}`);
  record(withFact.length > 300,
    "and most of them now carry a real fact that was in the snapshot all along",
    `${withFact.length}`);

  const turret = bare.find((k) => PARTS[k].gn);
  record(!!turret && /Takes <b>\d+ &times; S\d/.test(stOf(rows[turret])),
    `a turret says how many guns it takes and at what size - `
    + `${turret ? PARTS[turret].n : ""}`,
    turret ? stOf(rows[turret]).slice(0, 60) : "");
  const tank = bare.find((k) => PARTS[k].fuel);
  record(!!tank && /Capacity <b>/.test(stOf(rows[tank])),
    `a fuel tank says its capacity - ${tank ? PARTS[tank].n : ""}`);
  state.notes.push(`stat-less parts: ${withFact.length} of ${bare.length} now `
    + `carry a fact of another kind; ${nothing.length} genuinely have none`);

  /* ------- and the ones that genuinely have nothing say so IN WORDS ---- */
  const worded = nothing.filter((k) => /class="nostat"/.test(rows[k]));
  record(nothing.length === 0 || worded.length === nothing.length,
    "every part with nothing at all says so in words rather than printing "
    + "zeros that look like measurements",
    `${worded.length} of ${nothing.length}`);
  record(nothing.length === 0
    || !nothing.some((k) => /IR <b>0<\/b>/.test(rows[k])),
    "and none of them prints a zero at all");
  if (nothing.length) {
    const ex = nothing[0];
    console.log(`    e.g. ${PARTS[ex].n}: `
      + `${stOf(rows[ex]).replace(/<[^>]+>/g, " ").trim()}`);
  }
}

/* ------------------------------------ 4. THE LITERAL STRING, H8's rule -- */
console.log("\n--- 4. and no placeholder reaches a row (H8) ---");
{
  /* ON A SCREEN, which means the VISIBLE TEXT and not the markup.
     Two shield records are keyed SHLD_BANU_S01_Placeholder_SCItem, so the
     string appears in a data-part attribute - and their display names are
     "Suldrath" and "Sukoran", which are real. H8 is about the literal string
     reaching a reader, not about a key that happens to contain the word, and
     the first version of this assertion could not tell the two apart. */
  const visible = (h) => h.replace(/<[^>]*>/g, " ");
  const ph = keys.filter((k) => /PLACEHOLDER/i.test(visible(rows[k])));
  record(ph.length === 0,
    "no part row shows the string PLACEHOLDER to a reader",
    ph.length ? `${ph.length}, e.g. ${ph.slice(0, 2).join(", ")}` : "");
  const inMarkupOnly = keys.filter((k) => /Placeholder/i.test(k));
  record(inMarkupOnly.every((k) => !/PLACEHOLDER/i.test(visible(rows[k]))),
    `and the ${inMarkupOnly.length} records whose KEY contains it render `
    + `their real names instead`,
    inMarkupOnly.map((k) => PARTS[k].n).join(", "));
  const named = keys.filter((k) => PARTS[k].n && PARTS[k].n.length > 3);
  record(named.length > 2000 && named.every((k) => rows[k].includes(PARTS[k].n)),
    "while a part WITH a real name still renders it - otherwise a build that "
    + "blanked every name would also pass",
    `${named.length} named parts`);
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_ZEROS || MUT_BLANK)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
