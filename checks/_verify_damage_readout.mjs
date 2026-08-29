/**
 * B7 acceptance: THE DAMAGE READOUT, TOLD APART.

 *
 * RULE16: INDEPENDENT - the numbers the readout must show are taken from the parts
 * data and compared against what was rendered, so a readout that displays a
 * confident wrong figure fails. The distinction the section is named for -
 * telling two damage kinds apart - is decided from the data's own fields,
 * not from how the page chose to group them.
 *
 * The page showed one figure - Sustained DPS, noted "pilot-fired weapons".
 * Correct, and not enough. Measured across the fleet:
 *
 *   214 ships  pilot guns only          the readout was the whole truth
 *    61 ships  pilot guns AND turrets   it was half the truth
 *    11 ships  turrets only             it said 0 - actively wrong
 *   206 ships  carry missiles           counted nowhere at all
 *
 * (The order recorded 208 missile carriers; measured here it is 206, counting
 * only records that have slots at all. The figure is reported rather than
 * rounded to the one that was expected.)
 *
 * Sleven's correction is the rule: "just because it has turrets, and those
 * turrets are manual, doesn't mean there's not guns for the pilot to shoot."
 * The figures are NOT merged. One number cannot mean both "what you can do
 * alone" and "what a crew can do".
 *
 * ALL FOUR POPULATIONS ARE DRIVEN BY NAME, and turret-only is the load-bearing
 * one: on those eleven hulls the pilot figure is 0 and TRUE, and a bare 0 in a
 * number row reads as a broken stat rather than as a fact about the ship.
 *
 * THE NEGATIVE HALF: a pilot-only ship shows NO turret row at all. Not a
 * turret row reading 0. A zero is a claim, and on a ship with no turret it is
 * the wrong one.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-merge  turret DPS is added back into the pilot figure
 *   --mutate-zero   the turret row renders on every ship, reading 0 where
 *                   there are no turrets
 *   --self-test     inverts every expectation
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_damage_readout.mjs
 *        [--self-test] [--mutate-merge] [--mutate-zero]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_MERGE = process.argv.includes("--mutate-merge");
const MUT_ZERO = process.argv.includes("--mutate-zero");

const mutate = [];
if (MUT_MERGE) {
  mutate.push([/r\.tdps\+=p\.dps\|\|0; r\.talpha\+=p\.alpha\|\|0;/,
               "r.dps+=p.dps||0; r.alpha+=p.alpha||0;"]);
  console.log("*** MUTATED: turret guns are summed back into the pilot figure "
    + "- the Perseus-at-16,596-DPS mistake. Something below MUST notice. ***");
}
if (MUT_ZERO) {
  mutate.push([/if\(ra\.hasTurret\)\{\s*\n\s*h\+= stat\("Turret DPS"/,
               'if(true){\n    h+= stat("Turret DPS"']);
  console.log("*** MUTATED: the turret row renders on every ship, reading 0 "
    + "where there are none. The negative half MUST notice. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, PARTS, el, openShip, g, run } = H;

/* ------------------------------------------- the four populations, measured */
const classify = (sh) => {
  const sl = sh.slots || [];
  const pilotGun = sl.some((s) => !s.turret
    && (PARTS[s.stock] || {}).dps);
  const turret = sl.some((s) => s.turret
    && ["wpn", "tur", "mlr"].includes(s.t));
  const missile = sl.some((s) => s.t === "msl");
  return { pilotGun, turret, missile };
};

const pop = { pilotOnly: [], both: [], turretOnly: [], missile: [] };
for (const k of Object.keys(SHIPS)) {
  const sh = SHIPS[k];
  if (!(sh.slots || []).length) continue;
  const c = classify(sh);
  if (c.missile) pop.missile.push(k);
  if (c.pilotGun && c.turret) pop.both.push(k);
  else if (c.pilotGun) pop.pilotOnly.push(k);
  else if (c.turret) pop.turretOnly.push(k);
}
console.log("--- the four populations, counted from the data ---");
console.log(`    pilot guns only    ${pop.pilotOnly.length}`);
console.log(`    pilot AND turrets  ${pop.both.length}`);
console.log(`    turrets only       ${pop.turretOnly.length}`);
console.log(`    carry missiles     ${pop.missile.length}`);
record(pop.pilotOnly.length > 100 && pop.both.length > 20
  && pop.turretOnly.length > 5 && pop.missile.length > 100,
  "all four populations exist and are large enough to drive",
  `${pop.pilotOnly.length}/${pop.both.length}/${pop.turretOnly.length}/`
  + `${pop.missile.length}`);

const rowsFor = (key) => {
  openShip(key);
  return el("stats").innerHTML || "";
};
const hasRow = (html, label) =>
  new RegExp(`<div class="k">${label}(<|\\s)`).test(html);
const valueOf = (html, label) => {
  const i = html.indexOf(`<div class="k">${label}`);
  if (i === -1) return null;
  const m = html.slice(i).match(/<span class="va[^"]*">([^<]*)</);
  return m ? m[1].trim() : null;
};

/* --------------------------------------------- 1. PILOT ONLY, by name ---- */
console.log("\n--- 1. a pilot-only ship (the NEGATIVE half lives here) ---");
{
  const k = pop.pilotOnly.find((x) => /avenger stalker/i.test(SHIPS[x].n))
    || pop.pilotOnly[0];
  const html = rowsFor(k);
  state.notes.push(`pilot-only driven with ${SHIPS[k].n}`);
  record(hasRow(html, "Sustained DPS"),
    `${SHIPS[k].n} shows the pilot figure`);
  record(!/nofigure/.test(html),
    "and it is a real number, not a stated absence");
  record(!hasRow(html, "Turret DPS"),
    "and NO turret row at all - not a turret row reading 0",
    hasRow(html, "Turret DPS") ? valueOf(html, "Turret DPS") : "");
  record(/what the pilot can fire/.test(html),
    "the pilot row says whose guns it is counting");
}

/* --------------------------------------------- 2. BOTH, by name --------- */
console.log("\n--- 2. a ship with pilot guns AND turrets ---");
{
  const k = pop.both.find((x) => /idris/i.test(SHIPS[x].n)) || pop.both[0];
  const html = rowsFor(k);
  state.notes.push(`both driven with ${SHIPS[k].n}`);
  record(hasRow(html, "Sustained DPS"), `${SHIPS[k].n} shows a pilot figure`);
  record(hasRow(html, "Turret DPS"), "AND a turret figure");
  record(/needs crew/.test(html),
    "with the turret one labelled as needing crew");
  const rr = g(`JSON.stringify(calc(A))`);
  const c = JSON.parse(rr);
  record(c.dps > 0 && c.tdps > 0,
    "both figures are non-zero on this hull, so they are really two numbers",
    `pilot ${c.dps}, turret ${c.tdps}`);
  record(c.dps !== c.tdps,
    "and they are different numbers - not one value rendered twice",
    `${c.dps} vs ${c.tdps}`);
}

/* ---------------------------- 3. TURRET ONLY - the load-bearing one ----- */
console.log("\n--- 3. a turret-only ship: 0 is TRUE, and is said in words ---");
{
  const k = pop.turretOnly.find((x) => /hammerhead/i.test(SHIPS[x].n))
    || pop.turretOnly[0];
  const html = rowsFor(k);
  state.notes.push(`turret-only driven with ${SHIPS[k].n} (of `
    + `${pop.turretOnly.length} such hulls)`);
  const c = JSON.parse(g(`JSON.stringify(calc(A))`));
  record(c.dps === 0,
    `${SHIPS[k].n}'s pilot figure really is 0 - the readout was not wrong `
    + `about the number, only about presenting it`, String(c.dps));
  record(!hasRow(html, "Sustained DPS"),
    "so there is no bare 0 in a number row");
  record(/nofigure/.test(html) && /Pilot weapons/.test(html),
    "there is a stated absence instead");
  /* Whitespace-tolerant: the sentence wraps in the source, so the
     rendered HTML carries a newline and an indent in the middle of it.
     Matching the literal string failed on a page that says exactly the
     right thing. */
  record(/fired by a gunner,\s+not by the\s+pilot/.test(html),
    "and it says WHY in words, rather than leaving a 0 to be read as broken");
  record(hasRow(html, "Turret DPS") && c.tdps > 0,
    "while the turret figure is present and real - the firepower is on the "
    + "page, it was simply attributed to nobody before",
    `turret ${c.tdps}`);
}

/* ---------------------------------------------- 4. MISSILES ------------- */
console.log("\n--- 4. a missile carrier: a payload, never a per-second ---");
{
  const k = pop.missile.find((x) => /avenger stalker/i.test(SHIPS[x].n))
    || pop.missile[0];
  const html = rowsFor(k);
  const c = JSON.parse(g(`JSON.stringify(calc(A))`));
  state.notes.push(`missiles driven with ${SHIPS[k].n}, payload ${c.mdmg}`);
  record(hasRow(html, "Missile payload"),
    `${SHIPS[k].n} shows a missile payload`);
  record(c.mdmg > 0, "with a real figure behind it", String(c.mdmg));
  record(/one shot, not per second/.test(html),
    "labelled one-shot, in the row itself");
  /* THE ASSERTION THAT MATTERS: it is not folded into a DPS number. */
  const pilotSum = (SHIPS[k].slots || [])
    .filter((s) => !s.turret)
    .reduce((n, s) => n + ((PARTS[s.stock] || {}).dps || 0), 0);
  record(Math.abs(c.dps - pilotSum) < 0.01,
    "and the DPS figure is the pilot's guns and NOTHING ELSE - no missile "
    + "damage folded into a per-second number",
    `dps ${c.dps} vs pilot guns ${pilotSum.toFixed(2)}`);
  record(c.mdmg !== c.dps, "the two are separate values");
}

/* ------------------- 5. THE PILOT CALCULATION IS UNTOUCHED, FLEET-WIDE -- */
console.log("\n--- 5. the proven pilot figure is not disturbed ---");
{
  let checked = 0, off = 0;
  const bad = [];
  for (const k of Object.keys(SHIPS)) {
    const sh = SHIPS[k];
    if (!(sh.slots || []).length) continue;
    const want = (sh.slots || [])
      .filter((s) => !s.turret)
      .reduce((n, s) => n + ((PARTS[s.stock] || {}).dps || 0), 0);
    openShip(k);
    const c = JSON.parse(g(`JSON.stringify(calc(A))`));
    checked++;
    if (Math.abs(c.dps - want) > 0.01) {
      off++;
      if (bad.length < 5) bad.push(`${k}: ${c.dps} vs ${want.toFixed(2)}`);
    }
  }
  console.log(`\n    hulls checked ${checked}`);
  record(checked > 280, "every hull with slots was checked", `${checked}`);
  record(off === 0,
    "on EVERY hull the pilot figure still counts exactly the non-turret guns "
    + "- B7 split the readout without touching the proven calculation",
    off ? `${off} wrong, e.g. ${bad.join("; ")}` : "");

  /* AND THE TURRET HALF IS NOT EMPTY, or the split would be free. */
  let withTurretDps = 0;
  for (const k of pop.both.concat(pop.turretOnly)) {
    openShip(k);
    if (JSON.parse(g(`JSON.stringify(calc(A))`)).tdps > 0) withTurretDps++;
  }
  record(withTurretDps > 30,
    "and the turret figure is non-zero on most hulls that have turrets - the "
    + "firepower that used to be discarded is now counted",
    `${withTurretDps} of ${pop.both.length + pop.turretOnly.length}`);
  state.notes.push(`fleet: ${checked} hulls, pilot figure unchanged on all of `
    + `them; ${withTurretDps} hulls now report turret DPS that was previously `
    + `counted nowhere`);
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_MERGE || MUT_ZERO)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
