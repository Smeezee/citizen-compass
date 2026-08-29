/**
 * B1 acceptance: THE LEFT COLUMN HOLDS ONLY WHAT A PERSON CAN ACT ON.

 *
 * RULE16: INDEPENDENT - what belongs in the column is computed HERE from each
 * ship's own slot data, and the page is then required to agree with it:
 * `inCol.size === swapOf(SH).length`. The page cannot satisfy that by
 * being internally consistent, because the set it has to match was derived
 * from the data rather than read back from the DOM.
 *
 * Sleven: "over on the left should be shrink down and only show what's
 * actually listed."
 *
 * Fixed ports leave the loadout column entirely and appear on the Specs tab,
 * keeping everything L4 gave them: the fitted part, its manufacturer, the port
 * label, the reason it is locked in the game's own terms, and the patch tag.
 * The collapsed <details> fold at the bottom of the column goes with them.
 *
 * THE SPLIT IS `swappable(s)`, WHICH IS `!!s.fit`, WHICH IS THE PORT'S OWN
 * `Editable` FLAG. That property is the point of the item and the last
 * assertion here exists to defend it: there is NO LIST OF TYPES anywhere in
 * the decision, so the day CIG makes fuel tanks swappable they change columns
 * on the next data build with nobody editing code.
 *
 * WHAT THIS CANNOT PROVE. There is no browser here, so "the column is
 * shorter" is not measured - what is measured is that the rows are not in it.
 * Height belongs to B8, at a stated viewport, against the deployed bytes.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT, two separate plants, because the item has
 * two separable failures:
 *
 *   --mutate-column   the column renders every port again, fixed ones
 *                     included. The positive half must notice.
 *   --mutate-heading  the Specs "Fixed ports" heading renders even when there
 *                     are none. The negative half must notice.
 *   --self-test       inverts every expectation.
 *
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_column_split.mjs
 *        [--self-test] [--mutate-column] [--mutate-heading]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_COL = process.argv.includes("--mutate-column");
const MUT_HEAD = process.argv.includes("--mutate-heading");

const mutate = [];
if (MUT_COL) {
  /* THE DEFECT: the column shows the fixed ports again, which is the state B1
     changed and the shape any accidental revert takes.
     IT TAKES BOTH HALVES, and finding that out is the reason to plant it
     rather than reason about it. Un-filtering the column ALONE changes
     nothing, because renderSlot() still turns a fixed port away at the door -
     the first version of this mutation did exactly that and this control
     passed, correctly, on a page that was still right. A real revert puts the
     rows back too, so the plant does both. */
  mutate.push([/const open = sh\.slots\.filter\(swappable\);/,
               "const open = sh.slots.slice();"]);
  mutate.push([/if\(!swappable\(s\)\) return;/,
               "if(!swappable(s)){ h+=fixedSpecRow(s)"
               + ".replace('data-fixed=','data-slot='); return; }"]);
  console.log("*** MUTATED: renderCol no longer filters AND renderSlot draws "
    + "fixed rows again - every port is back in the left column. Something "
    + "below MUST notice. ***");
}
if (MUT_HEAD) {
  /* THE OTHER DEFECT: a heading over nothing. A tab that opens onto an empty
     section is the navigation equivalent of an empty picker. */
  mutate.push([/if\(!shut\.length\) return "";/,
               "if(false) return \"\";"]);
  console.log("*** MUTATED: fixedSpecs emits its heading even with no fixed "
    + "ports. The negative half below MUST notice. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, el, openShip, g, run, dispatch } = H;

const swapOf = (sh) => (sh.slots || []).filter((s) => s.fit);
const fixedOf = (sh) => (sh.slots || []).filter((s) => !s.fit);

/* A hull with a healthy mix, chosen by measurement rather than by name. */
const key = Object.keys(SHIPS).find((k) => {
  const sh = SHIPS[k];
  return swapOf(sh).length > 5 && fixedOf(sh).length > 5;
});
record(!!key, "found a hull with both kinds of port to drive", key || "none");
const SH = SHIPS[key];
state.notes.push(`driven with ${SH.n} (${key}): ${SH.slots.length} ports, `
  + `${swapOf(SH).length} swappable, ${fixedOf(SH).length} fixed`);

openShip(key);

/* ------------------------------------- 1. ZERO fixed ports in the column */
console.log("\n--- 1. the left column holds only ports a person can act on ---");
const colA = el("colA").innerHTML;
record(colA.length > 500, "the column rendered something at all",
  `${colA.length} chars`);

const inCol = new Set(
  [...colA.matchAll(/data-slot="([^"]+)"/g)].map((m) => m[1]));
const fixedInCol = fixedOf(SH).filter((s) => inCol.has(s.id));
record(fixedInCol.length === 0,
  "ZERO non-swappable ports appear in the left column",
  fixedInCol.length ? fixedInCol.map((s) => s.id).join(", ") : "");

/* The positive half. Without it, a column that rendered NOTHING would satisfy
   the assertion above perfectly. */
const missing = swapOf(SH).filter((s) => !inCol.has(s.id));
record(missing.length === 0,
  "and every swappable port IS in it - so an empty column cannot pass",
  missing.length ? missing.map((s) => s.id).join(", ") : "");
record(inCol.size === swapOf(SH).length,
  `the column holds exactly the ${swapOf(SH).length} swappable ports`,
  `${inCol.size} rows`);

record(!/fixed-group|<details/.test(colA),
  "the collapsed 'Fixed' fold is gone from the column entirely");

/* --------------------------------------- 2. Specs holds ALL of them, in full */
console.log("\n--- 2. Specs holds all of them, with L4's content intact ---");
const specs = el("specs").innerHTML;
const inSpecs = new Set(
  [...specs.matchAll(/data-fixed="([^"]+)"/g)].map((m) => m[1]));
const missingFromSpecs = fixedOf(SH).filter((s) => !inSpecs.has(s.id));
record(missingFromSpecs.length === 0,
  `ALL ${fixedOf(SH).length} fixed ports appear on the Specs tab`,
  missingFromSpecs.length ? missingFromSpecs.map((s) => s.id).join(", ") : "");
record(inSpecs.size === fixedOf(SH).length,
  "and nothing else is in that list",
  `${inSpecs.size} rows for ${fixedOf(SH).length} fixed ports`);

/* THE SUM. The order asks for it by name, and it is the assertion that catches
   a port falling down the gap between the two lists - which neither half above
   would notice on its own. */
record(inCol.size + inSpecs.size === SH.slots.length,
  `the two lists sum to the port total: ${inCol.size} + ${inSpecs.size} = `
  + `${SH.slots.length}`,
  `got ${inCol.size + inSpecs.size}`);

/* L4's content, on a real row rather than in the abstract. */
{
  const s = fixedOf(SH).find((x) => x.stock && H.PARTS[x.stock]);
  record(!!s, "a fixed port with a fitted part exists to check L4 against");
  if (s) {
    const part = H.PARTS[s.stock];
    const row = specs.slice(specs.indexOf(`data-fixed="${s.id}"`));
    const cell = row.slice(0, row.indexOf("</div>", row.indexOf("</span>")) + 6);
    record(cell.includes(part.n), `the row names the fitted part - "${part.n}"`);
    if (part.m) record(cell.includes(part.m),
      `and its manufacturer - "${part.m}"`);
    record(/does not allow this to be changed|no part for this port/.test(cell),
      "and says why it is locked, in the game's own terms");
    record(/class="tag pv"/.test(cell), "and carries the patch tag");
  }
}

/* ------------------------------- 3. "N fixed" is a control, and it works */
console.log("\n--- 3. \"N fixed\" takes you to where they went ---");
record(/id="tospecs"/.test(colA),
  "the sub-line's fixed count is a control, not plain text");
run(`tab="loadout";renderTabs();`);
record(g("tab") === "loadout", "the page starts on the loadout tab");
const threw = dispatch(["#tospecs"]);
record(!threw, "clicking it does not throw", threw || "");
record(g("tab") === "specs",
  "and it opens the Specs tab - the ports are findable, not hidden",
  g("tab"));

/* ---------------------- 4. NEGATIVE: a hull with no fixed ports at all --- */
console.log("\n--- 4. NEGATIVE: no fixed ports means no empty heading ---");
const noneKey = Object.keys(SHIPS).find(
  (k) => (SHIPS[k].slots || []).length && !fixedOf(SHIPS[k]).length);
record(!!noneKey,
  "the data contains a record with ports and NO fixed ports to drive this with",
  noneKey || "none found");
if (noneKey) {
  state.notes.push(`the negative half is driven with ${SHIPS[noneKey].n} `
    + `(${noneKey}) - the ONLY record in the fleet with ports and no fixed `
    + `ones, which is why it is named rather than searched for again`);
  openShip(noneKey);
  const s2 = el("specs").innerHTML;
  record(s2.length > 200, "its Specs tab still renders, and is not empty",
    `${s2.length} chars`);
  record(/<h2>Specs<\/h2>/.test(s2), "with the Specs heading itself present");
  record(!/Fixed ports/.test(s2),
    "and NO 'Fixed ports' heading over an empty list");
  record(!/data-fixed=/.test(s2), "and no fixed rows, because there are none");
  record(el("colA").innerHTML.includes("0 fixed"),
    "the sub-line says 0 fixed as plain text, with nothing to click");
  record(!/id="tospecs"/.test(el("colA").innerHTML),
    "so there is no control offering to take you to a list that is not there");
}

/* --------------------------- 5. THE SPLIT IS THE Editable FLAG, FLEET-WIDE */
console.log("\n--- 5. the split is the port's own flag, on every hull ---");
{
  let bad = 0, checked = 0;
  const offenders = [];
  for (const k of Object.keys(SHIPS)) {
    const sh = SHIPS[k];
    if (!(sh.slots || []).length) continue;
    openShip(k);
    const col = new Set([...el("colA").innerHTML
      .matchAll(/data-slot="([^"]+)"/g)].map((m) => m[1]));
    const spec = new Set([...el("specs").innerHTML
      .matchAll(/data-fixed="([^"]+)"/g)].map((m) => m[1]));
    checked++;
    for (const s of sh.slots) {
      const where = s.fit ? col : spec;
      const other = s.fit ? spec : col;
      if (!where.has(s.id) || other.has(s.id)) {
        bad++;
        if (offenders.length < 6) offenders.push(`${k}/${s.id}`);
      }
    }
  }
  console.log(`\n    hulls checked ${checked}`);
  record(checked > 300, "every hull with ports was checked, not a sample",
    `${checked} hulls`);
  record(bad === 0,
    "on EVERY hull, each port sits on exactly the side its Editable flag puts "
    + "it - no list of types anywhere in the decision",
    bad ? `${bad} misplaced, e.g. ${offenders.join(", ")}` : "");
  state.notes.push(`fleet: ${checked} hulls, every port on the side its own `
    + `Editable flag puts it`);
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_COL || MUT_HEAD)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
