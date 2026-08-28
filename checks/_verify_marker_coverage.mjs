/**
 * W3: a hull showing 4 of 24 says it is showing 4 of 24.
 *
 * Sleven walked the ship list on 2026-08-23 and filed the Retaliator, the Sabre
 * Peregrine and all three Ballistas as "hardpoints not set up". Every one of
 * them HAS markers - 4, 2, 2, 2 and 2. The page printed a confident provenance
 * note about "the 4 dots on this model" and never mentioned the other twenty,
 * so a reader could not tell thin data from broken code. Neither could he,
 * which is why one defect arrived as five bug reports.
 *
 * WHAT THIS CONTROL REFUSES TO DO. It does not look for the string "Showing"
 * in the source, and it does not check the five ships the order happened to
 * name. It opens every hull that has markers, reads the note the page actually
 * rendered, and compares the ratio in it against a count this file computes
 * ITSELF from the ship's own port types. A page that printed a plausible pair
 * of numbers would fail here; a page that printed the right pair for the
 * Retaliator and nonsense for the other 158 would fail here too.
 *
 * THE NEGATIVE HALF IS LOAD-BEARING. A hull whose every mount is marked must
 * NOT be told it is missing any, and a hull with no markers at all must keep
 * the E1 absence wording rather than gaining a "0 of 24" line. Without both,
 * a build that printed the coverage sentence unconditionally would pass.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-silent    coverageLine() returns "" - the exact state Sleven
 *                      found, four dots and no denominator.
 *   --mutate-total     the denominator is taken from the markers instead of
 *                      the mounts, so every hull claims full coverage. This is
 *                      the tempting shortcut and it is the lie.
 *   --self-test        inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_marker_coverage.mjs
 *        [--self-test] [--mutate-silent] [--mutate-total]
 */

import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { loadPage, reporter } from "./_loadout_harness.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEPLOY_DIR = join(HERE, "..", "testing", "_deploy");
const DEPLOY_PAGE = join(DEPLOY_DIR, "loadout.html");

const SELFTEST = process.argv.includes("--self-test");
const MUT_SILENT = process.argv.includes("--mutate-silent");
const MUT_TOTAL = process.argv.includes("--mutate-total");

const mutate = [];
if (MUT_SILENT) {
  mutate.push([/if\(!c\.total \|\| !c\.marked\) return "";/,
               'if(true) return "";']);
  console.log("*** MUTATED: coverageLine() is silent again - the state that "
    + "made four markers indistinguishable from none. ***");
}
if (MUT_TOTAL) {
  mutate.push([/const wm=weaponMounts\(ship\(\)\)\.length;/,
               "const wm=n;"]);
  console.log("*** MUTATED: the denominator is the marker count, so every "
    + "hull claims to be fully covered. ***");
}

/* --deployed drives testing/_deploy/loadout.html instead of the source. The
   source having the sentence and the built page not carrying it is a real and
   previously-seen failure, and only the built bytes are what a visitor gets. */
const DEPLOYED = process.argv.includes("--deployed");
const H = DEPLOYED
  ? loadPage({ mutate, srcDir: DEPLOY_DIR, pageFile: DEPLOY_PAGE })
  : loadPage({ mutate });
if (DEPLOYED) console.log("driving the BUILT bytes: " + DEPLOY_PAGE);
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, MARKS, el, openShip, g } = H;
const MODELS = g("MODELS");
const TYPES = g("TYPES");

/* Counted here, independently, from the ship's own port types. If this file
   asked the page for the total there would be nothing left to compare. */
const MARKABLE = new Set(["WeaponGun", "Turret", "MissileLauncher",
  "WeaponDefensive", "WeaponMining", "BombLauncher", "SalvageHead",
  "TractorBeam", "EMP", "Missile", "Bomb"]);
const mountsOf = (sh) => (sh.slots || [])
  .filter((s) => MARKABLE.has((TYPES[s.t] || {}).t)).length;

const noteFor = (k) => { openShip(k); return el("markernote").innerHTML || ""; };
const SHOWING = /Showing\s+(\d+)\s+of\s+(\d+)\s+weapon mounts/;
const ALLMARKED = /All\s+(\d+)\s+of this ship's weapon mounts are marked/;
const nameOf = (k) => (SHIPS[k] || {}).n || k;

const withModel = Object.keys(SHIPS).filter((k) => MODELS[k]);
const marked = withModel.filter((k) => (MARKS[k] || []).length);
const silent = withModel.filter((k) => !(MARKS[k] || []).length);

/* -------------------------------------------- 1. THE FLEET, EVERY HULL */
console.log("--- 1. every hull with markers states its own ratio ---");
{
  let checked = 0, missing = [], wrong = [], full = 0;
  for (const k of marked) {
    const n = (MARKS[k] || []).length;
    const total = mountsOf(SHIPS[k]);
    if (!total) continue;                 // nothing a marker could sit on
    const note = noteFor(k);
    checked += 1;
    if (n >= total) {
      full += 1;
      const m = note.match(ALLMARKED);
      if (!m || Number(m[1]) !== total) wrong.push(`${nameOf(k)} full-coverage`);
      if (SHOWING.test(note)) wrong.push(`${nameOf(k)} claims a shortfall`);
      continue;
    }
    const m = note.match(SHOWING);
    if (!m) { missing.push(nameOf(k)); continue; }
    if (Number(m[1]) !== n || Number(m[2]) !== total) {
      wrong.push(`${nameOf(k)} says ${m[1]}/${m[2]}, data says ${n}/${total}`);
    }
  }
  console.log(`    hulls opened and read   ${checked}`);
  console.log(`    ...fully covered        ${full}`);
  record(checked > 100, "the sweep really covered the fleet", `${checked}`);
  record(missing.length === 0,
    "no hull with a shortfall stayed silent about it",
    missing.length ? `${missing.length}: ${missing.slice(0, 6).join(", ")}`
      : "none");
  record(wrong.length === 0,
    "every ratio on the page matches the ratio in the data",
    wrong.length ? `${wrong.length}: ${wrong.slice(0, 4).join(" | ")}` : "none");
  state.notes.push(`${checked} hulls read from the rendered note; ${full} of `
    + "them fully covered");
}

/* --------------------------- 2. THE FIVE SHIPS SLEVEN ACTUALLY REPORTED */
console.log("\n--- 2. the five he filed as \"hardpoints not set up\" ---");
{
  const want = ["Retaliator", "Sabre Peregrine", "Ballista",
    "Ballista Dunestalker", "Ballista Snowblind"];
  /* The page names carry the manufacturer - "Aegis Retaliator". So the match
     is exact-or-exact-suffix and it REFUSES an ambiguous hit rather than
     taking the first: picking one of two Ballistas would be a coin toss
     dressed as a test result. */
  const findExact = (nm) => {
    const hits = marked.filter((x) => nameOf(x) === nm
      || nameOf(x).endsWith(" " + nm));
    return hits.length === 1 ? hits[0] : null;
  };
  for (const nm of want) {
    const k = findExact(nm);
    if (!k) {
      const hits = marked.filter((x) => nameOf(x) === nm
        || nameOf(x).endsWith(" " + nm));
      record(false, `${nm} resolves to exactly one marked hull`,
        hits.length ? `ambiguous: ${hits.map(nameOf).join(", ")}` : "not found");
      continue;
    }
    const n = (MARKS[k] || []).length;
    const total = mountsOf(SHIPS[k]);
    const note = noteFor(k);
    /* THE EXPECTED SENTENCE IS DECIDED BY THE DATA, not by the order. The
       Sabre Peregrine turns out to carry only 2 weapon mounts in the bench, so
       its 2 markers ARE full coverage - telling it that it is missing some
       would be the same class of lie as saying nothing. Asserting SHOWING on
       all five would have hard-coded the order's assumption into the check. */
    if (n >= total) {
      const m = note.match(ALLMARKED);
      record(!!m && Number(m[1]) === total,
        `${nm} is fully covered in the data and says so`,
        m ? `all ${m[1]} marked` : "no full-coverage line printed");
      record(!SHOWING.test(note),
        `${nm} is not told it is missing mounts it does not have`);
      state.notes.push(`${nm}: ${n} of ${total} - FULL coverage in our data`);
      continue;
    }
    const m = note.match(SHOWING);
    record(!!m && Number(m[1]) === n && Number(m[2]) === total,
      `${nm} says so in its own numbers`,
      m ? `showing ${m[1]} of ${m[2]}` : "no ratio printed");
    record(/thin data, not a broken\s+page/.test(note),
      `${nm} tells the reader which of the two it is looking at`);
    if (m) state.notes.push(`${nm}: ${m[1]} of ${m[2]}`);
  }
}

/* ------------------------- 3. THE NEGATIVE HALF - who must NOT be told */
console.log("\n--- 3. the hulls that must not gain a coverage line ---");
{
  const k = silent.find((x) => mountsOf(SHIPS[x]) > 0);
  record(!!k, "a hull with mounts and no markers exists to test against",
    k ? nameOf(k) : "none");
  if (k) {
    const note = noteFor(k);
    record(!SHOWING.test(note) && !ALLMARKED.test(note),
      `${nameOf(k)} keeps the E1 absence wording, not "0 of N"`);
    record(/no measured positions/.test(note),
      "and that wording is still the one E1 shipped");
  }

  const zero = silent.find((x) => mountsOf(SHIPS[x]) === 0);
  if (zero) {
    const note = noteFor(zero);
    record(!SHOWING.test(note) && !ALLMARKED.test(note),
      `${nameOf(zero)} has nothing to count and is told nothing about counts`);
  }

  // WITHOUT THIS the sentence could be printed on every hull unconditionally
  // and section 1 would still be green.
  const fullK = marked.find((x) => {
    const t = mountsOf(SHIPS[x]);
    return t > 0 && (MARKS[x] || []).length >= t;
  });
  if (fullK) {
    const note = noteFor(fullK);
    record(!SHOWING.test(note),
      `${nameOf(fullK)} is fully covered and is NOT told it is missing any`);
  } else {
    record(true, "no fully covered hull in this dataset to test against",
      "skipped honestly, not passed");
  }
}

/* ------------------------------------ 4. the provenance note survived */
console.log("\n--- 4. the coverage line was added, nothing was displaced ---");
{
  const k = marked[0];
  const note = noteFor(k);
  record(/About the \d+ dots? on this model/.test(note),
    "the existing provenance note is still there");
  /* WAS: /not measured from the model/. This section exists to prove the
     coverage line was ADDED WITHOUT DISPLACING the provenance note - it is
     about the note surviving, not about which words are in it. The words
     changed on 2026-08-27 when CIG's own geometry replaced the derived
     positions for most of the fleet, and N9 in _verify_ship_page.mjs is where
     the wording itself is asserted. What is checked here is what this section
     is actually for: the note still explains where the dots come from. */
  record(/geometry|estimate/i.test(note),
    "including the sentence that says where the positions come from");
}

finish();
