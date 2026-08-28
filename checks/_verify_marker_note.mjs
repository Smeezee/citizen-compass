/**
 * DOES THE SENTENCE ABOVE THE MODEL DESCRIBE *THIS* SHIP?
 *
 * RULE16: INDEPENDENT - the numbers this control expects are computed HERE,
 * from `loadout_marker.gen.js` - the data file - by re-implementing the
 * grouping rule out of that file's own header rather than importing the page's
 * `mountsFor()`. The page and this control therefore reach the count by two
 * routes, and a bug in the page's grouping shows up as a disagreement instead
 * of being copied into the expectation. The actual numbers are read out of the
 * rendered HTML, not out of a page variable.
 *
 * WHY THIS EXISTS AS ITS OWN FILE.
 * `_verify_ship_page.mjs` N9 has asserted the marker note's honesty since it
 * was written, and its header records C1 as the author of that block inside a
 * file Code owns. That is one artifact with two writers, which is the exact
 * thing rule 14 forbids and `OWNERS.md` was written to end. So the marker-note
 * assertions move here, to a file C1 owns outright, and Q14 asks Code to
 * delete the three that are now duplicated. Until he does, N9's two
 * fleet-wide assertions fail on purpose - see Q14.
 *
 * WHAT THE NOTE HAS BEEN WRONG ABOUT, TWICE, WHICH IS WHY IT NEEDS A CONTROL.
 *   1. It called every dot an estimate after CIG's geometry had been decoded -
 *      understating the best thing on the site.
 *   2. It then said it "cannot yet tell you which of the two you are looking
 *      at on this particular ship" for a full day AFTER Q9 gave every dot its
 *      own provenance. A hedge outliving its reason is not a small error: it
 *      is the page declining to use a field somebody built for it.
 * Both failures look like caution. Neither is. **The rule is that the note
 * describes the ship on screen and nothing wider.**
 *
 * RULE 12 - THE CONTROLS, both real reverts rather than invented damage:
 *   --mutate-fleetwide  puts the fleet-wide hedge back. Every per-ship
 *                       assertion must go red.
 *   --mutate-blind      drops the provenance out of mountsFor(), which is the
 *                       state before this change. The all-CIG ship then reads
 *                       as entirely estimated and must be caught.
 * Its --self-test inverts every expectation, per the suite's convention.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { loadPage, reporter, SRC } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_FLEET = process.argv.includes("--mutate-fleetwide");
const MUT_BLIND = process.argv.includes("--mutate-blind");

const mutate = [];
if (MUT_FLEET) {
  mutate.push([/const pv=mountProvenance\(shipId\);/,
    "const pv={cig:0,est:0,total:n};"]);
  mutate.push([/let body;\n  if\(pv\.est===0\)\{/,
    "let body;\n  if(false){"]);
  mutate.push([/\}else if\(pv\.cig===0\)\{/,
    "}else if(false){"]);
  mutate.push([/<b>Hover any dot and it tells you which kind it is\.<\/b>/,
    "<b>This page cannot yet tell you which of the two you are looking at "
    + "on this particular ship</b>, and 1,693 mounts across 166 hulls are "
    + "placed from the game files."]);
  console.log("*** MUTATED: the note is fleet-wide again and hedges about "
    + "every ship. The per-ship assertions MUST notice. ***");
}
if (MUT_BLIND) {
  mutate.push([/from:\(rep\.length>4\?rep\[4\]:""\),/, 'from:"",']);
  console.log("*** MUTATED: mountsFor() drops the provenance, which is the "
    + "state before Q9 was used. Every ship now reads as estimated. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, el, openShip } = H;

/* ---------------------------------------------------------------------- */
/* THE EXPECTATION, COMPUTED FROM THE DATA FILE AND NOT FROM THE PAGE.     */
/* The grouping rule is quoted from loadout_marker.gen.js's own header and  */
/* from the emitter that wrote it: a mount is everything sharing the text   */
/* before the first ".", and the dot drawn for it is the SHALLOWEST member. */
/* ---------------------------------------------------------------------- */
const raw = readFileSync(join(SRC, "loadout_marker.gen.js"), "utf8");
const MARKS = JSON.parse(raw.slice(raw.indexOf("{", raw.indexOf("="))).trim()
  .replace(/;\s*$/, ""));

function expected(cls) {
  const by = new Map();
  for (const m of MARKS[cls] || []) {
    const id = String(m[0]);
    const i = id.indexOf(".");
    const root = i < 0 ? id : id.slice(0, i);
    if (!by.has(root)) by.set(root, []);
    by.get(root).push(m);
  }
  let cig = 0;
  for (const ms of by.values()) {
    ms.sort((a, b) => {
      const da = String(a[0]).split(".loadout.").length;
      const db = String(b[0]).split(".loadout.").length;
      return da - db || (String(a[0]) < String(b[0]) ? -1 : 1);
    });
    if ((ms[0][4] || "") === "cig") cig++;
  }
  return { cig, est: by.size - cig, total: by.size };
}

const drivable = Object.keys(SHIPS).filter((k) => (MARKS[k] || []).length);
const allCig = drivable.find((k) => {
  const e = expected(k); return e.total > 3 && e.est === 0;
});
const mixed = drivable.find((k) => {
  const e = expected(k); return e.cig > 0 && e.est > 0;
});
const noCig = drivable.find((k) => {
  const e = expected(k); return e.total > 0 && e.cig === 0;
});

record(!!allCig, "found a hull whose dots are ALL from CIG", allCig || "none");
record(!!mixed, "found a hull with a MIXTURE", mixed || "none");
state.notes.push(`all-CIG: ${allCig} ${JSON.stringify(expected(allCig))}`);
state.notes.push(`mixed:   ${mixed} ${JSON.stringify(expected(mixed))}`);
state.notes.push(noCig ? `no-CIG:  ${noCig} ${JSON.stringify(expected(noCig))}`
  : "no-CIG:  none in this build - that branch is UNPROVEN today");

/* WHITESPACE IS FLATTENED BEFORE EVERY MATCH, AND FINDING OUT WHY COST A
   FALSE PASS. The note is authored as an indented template literal, so
   "the game's own geometry" reaches the DOM as "the game's own\n      geometry"
   and /game's own geometry/ does not match it. That showed up honestly as ONE
   red assertion in section 1 - and silently as a GREEN one in section 5, where
   the same phrase is asserted ABSENT. A regex that can never match passes every
   negative test in the file. Flattened once, here, rather than per assertion. */
const flat = (s) => String(s).replace(/\s+/g, " ");
const noteFor = (k) => { openShip(k); return flat(el("markernote").innerHTML); };
const digits = (s) => (s.match(/\d[\d,]*/g) || []).map((d) =>
  Number(d.replace(/,/g, "")));

/* ------------------------------------------------ 1. the all-CIG ship */
console.log("\n--- 1. a ship whose dots are all CIG's says so, without hedging ---");
{
  const e = expected(allCig), note = noteFor(allCig);
  record(/all/i.test(note) && /game's own geometry/i.test(note),
    "it says ALL of this model's dots come from the game's own geometry");
  record(/not one of them is estimated/i.test(note),
    "and says plainly that none of them is estimated");
  record(!/cannot yet tell you which/i.test(note),
    "and does NOT hedge about which kind they are - the field exists now");
  record(digits(note).includes(e.total),
    `and states this ship's own count, ${e.total}`, digits(note).join(","));
  record(!digits(note).includes(1693) && !digits(note).includes(166),
    "and quotes NO fleet-wide figure - the reader is looking at one ship");
}

/* -------------------------------------------------- 2. the mixed ship */
console.log("\n--- 2. a ship with a mixture states both numbers ---");
{
  const e = expected(mixed), note = noteFor(mixed);
  record(digits(note).includes(e.cig),
    `it states how many are CIG's: ${e.cig}`, digits(note).join(","));
  record(digits(note).includes(e.est),
    `and how many are estimated: ${e.est}`, digits(note).join(","));
  record(/estimate/i.test(note) && /snapped/i.test(note) && /name/i.test(note),
    "and still says what the fallback method IS, not just that it exists");
  record(/hover any dot/i.test(note),
    "and points the reader at the per-dot answer");
}

/* ------------------------------ 3. the promise the note just made */
console.log("\n--- 3. hovering a dot really does tell you ---");
{
  openShip(mixed);
  const marks = el("cc-marks").innerHTML;
  const labels = [...marks.matchAll(/aria-label="([^"]*)"/g)].map((m) => m[1]);
  const approx = labels.filter((l) => /position approximate/i.test(l));
  const e = expected(mixed);
  record(labels.length === e.total,
    `one marker per mount, ${e.total} of them`, `${labels.length} rendered`);
  record(approx.length === e.est,
    `exactly the ${e.est} estimated dot(s) say so in their label`,
    `${approx.length} said so`);
  record(approx.length > 0 && approx.length < labels.length,
    "and the CIG dots stay silent - the label marks the EXCEPTION, not "
    + "every dot");
}

/* ------------------------------------------- 4. the unchanging claim */
console.log("\n--- 4. what a port IS was never estimated and still is not ---");
{
  const note = noteFor(allCig);
  record(/not estimated/i.test(note) && /(size|type|fitted)/i.test(note),
    "the note keeps saying that a port's size, type and fitting are exact");
}

/* --------------------------------------------- 5. the no-CIG branch */
if (noCig) {
  console.log("\n--- 5. a ship with no CIG dots says THAT, plainly ---");
  const e = expected(noCig), note = noteFor(noCig);
  record(/estimated/i.test(note) && !/game's own geometry/i.test(note),
    "it says the dots are estimated and does not claim decoded geometry");
  record(digits(note).includes(e.total) || e.total === 1,
    `and states this ship's count, ${e.total}`);
} else {
  state.notes.push("branch 5 (a ship with NO CIG dots) was NOT EXERCISED - "
    + "no such hull carries markers in this build. It is UNPROVEN, not passing.");
}

finish("The expected counts were computed from loadout_marker.gen.js by "
  + "re-implementing its grouping rule, never by asking the page.");
