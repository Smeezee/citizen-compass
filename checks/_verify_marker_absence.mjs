/**
 * E1: a hull with nothing on it says WHICH KIND of nothing.
 *
 * Sleven: "some ships don't even have hard points at all." Measured on the
 * deployed data: 201 ships render a model, 159 carry hull markers, and the
 * rest DRAW A HULL AND PUT NOTHING ON IT. The page said nothing about that, so
 * a visitor could not tell "this ship has no weapon mounts" from "this page is
 * broken".
 *
 * THE PROTOTYPE SOLVED ONE OF THE TWO CASES AND ITS WORDING IS ADOPTED
 * VERBATIM. But there are two, and saying the wrong one is a lie:
 *
 *   no weapon mounts at all   the Tumbril Cyclone. Nothing exists to mark.
 *   mounts but no positions   the Drake Cutlass Black - 117 ports, 42 of them
 *                             changeable, a hull that draws perfectly. Telling
 *                             that visitor "no weapon mounts" would be false
 *                             about a ship carrying 42.
 *
 * TOLD APART FROM THE DATA, never from a list of ship names - which is why the
 * fleet sweep below checks every hull against its own port types rather than
 * checking the two the errata happened to name.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-onemsg   the Cyclone's wording is used for both cases, which is
 *                     the tempting shortcut and is a lie about the Cutlass.
 *   --mutate-silent   the note goes back to empty, which is the state Sleven
 *                     found.
 *   --self-test       inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_marker_absence.mjs
 *        [--self-test] [--mutate-onemsg] [--mutate-silent]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_ONE = process.argv.includes("--mutate-onemsg");
const MUT_SILENT = process.argv.includes("--mutate-silent");

const mutate = [];
if (MUT_ONE) {
  mutate.push([/const ch=\(sh\.slots\|\|\[\]\)\.filter\(swappable\)\.length;/,
    'return `<b>This hull carries no weapon mounts in the data &mdash; nothing'
    + ' to mark on it.</b>`; const ch=0;']);
  console.log("*** MUTATED: both cases get the Cyclone's wording - a lie about "
    + "any hull that has mounts and no positions. ***");
}
if (MUT_SILENT) {
  mutate.push([/if\(!n\)\{ el\.innerHTML=noMarkerNote\(\); return; \}/,
               'if(!n){ el.innerHTML=""; return; }']);
  console.log("*** MUTATED: the note is empty again - the state Sleven "
    + "found. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, MARKS, el, openShip, g } = H;
const MODELS = g("MODELS");
const TYPES = g("TYPES");

const MARKABLE = new Set(["WeaponGun", "Turret", "MissileLauncher",
  "WeaponDefensive", "WeaponMining", "BombLauncher", "SalvageHead",
  "TractorBeam", "EMP", "Missile", "Bomb"]);
const mountsOf = (sh) => (sh.slots || [])
  .filter((s) => MARKABLE.has((TYPES[s.t] || {}).t));

const NONE_MSG = /no weapon mounts in the data/;
const NOPOS_MSG = /no measured positions/;
const noteFor = (k) => { openShip(k); return el("markernote").innerHTML || ""; };

/* ------------------------------------------------ the three populations */
const withModel = Object.keys(SHIPS).filter((k) => MODELS[k]);
const marked = withModel.filter((k) => (MARKS[k] || []).length);
const silent = withModel.filter((k) => !(MARKS[k] || []).length);
console.log("--- the populations, from the data ---");
console.log(`    ships with a model      ${withModel.length}`);
console.log(`    ...carrying markers     ${marked.length}`);
console.log(`    ...carrying NONE        ${silent.length}`);
record(silent.length > 20,
  "there really are hulls that draw a model and mark nothing on it",
  `${silent.length}`);

/* ------------------------------------------- 1. THE TWO CASES, BY NAME */
console.log("\n--- 1. the two cases, on the hulls the errata names ---");
{
  const cyc = silent.find((k) => /cyclone/i.test(SHIPS[k].n || "")
    && !mountsOf(SHIPS[k]).length);
  record(!!cyc, "a hull with genuinely zero weapon mounts exists",
    cyc ? SHIPS[cyc].n : "none");
  if (cyc) {
    const note = noteFor(cyc);
    record(NONE_MSG.test(note),
      `${SHIPS[cyc].n} gets the Cyclone's wording, verbatim`);
    record(!NOPOS_MSG.test(note), "and not the other one");
  }

  /* THIS CONTROL SAID "TOLD APART FROM THE DATA, NEVER FROM A LIST OF SHIP
     NAMES" AND THEN LOOKED THE CUTLASS BLACK UP BY NAME.

     P1 gave the Cutlass Black its own geometry, the placer found it, and it
     gained 17 markers - so it left the silent population and this control went
     red reporting "not found" about a ship that had just been FIXED. A control
     that fails when its example ship gets better is measuring the example, not
     the behaviour.

     The case is chosen from the data instead: a hull that draws a model,
     carries weapon mounts, and has no marker for any of them. Which ship that
     is will change as coverage rises, and the control does not care - it names
     whichever one it used, so the run is still reproducible by reading it.
     When the population empties the check says so and does not silently pass:
     that day, every hull with mounts has positions and the case is retired on
     purpose rather than by accident. */
  const cut = silent.find((k) => mountsOf(SHIPS[k]).length > 0);
  record(!!cut,
    "a hull with weapon mounts and no positions exists to test the second "
    + "case against",
    cut ? SHIPS[cut].n : "NONE LEFT - every hull with mounts now has "
      + "positions, so this case cannot be exercised. Reported, not passed.");
  if (cut) {
    const sh = SHIPS[cut];
    const ch = (sh.slots || []).filter((s) => s.fit).length;
    const note = noteFor(cut);
    record(mountsOf(sh).length > 0,
      "it really does carry weapon mounts - so the Cyclone's sentence would "
      + "be false about it",
      `${mountsOf(sh).length} weapon mounts, ${ch} changeable`);
    record(NOPOS_MSG.test(note),
      "so it gets the no-positions sentence instead");
    record(!NONE_MSG.test(note),
      "and is NOT told it has no weapon mounts - the lie this item exists to "
      + "prevent");
    record(note.includes(String(ch)),
      `and the sentence names its own count - ${ch} changeable ports`);
    state.notes.push(`${SHIPS[cut].n}: ${mountsOf(sh).length} weapon mounts, `
      + `${ch} changeable, no positions - told so in its own numbers`);
  }
}

/* ------------------------------ 2. THE NEGATIVE HALF: a marked hull ---- */
console.log("\n--- 2. a hull WITH markers shows neither message ---");
{
  const k = marked[0];
  const note = noteFor(k);
  record(note.length > 200, `${SHIPS[k].n} still carries its provenance note`,
    `${note.length} chars`);
  record(!NONE_MSG.test(note) && !NOPOS_MSG.test(note),
    "and neither absence message - without this, a build that printed one on "
    + "every ship would pass everything above");
  record(/not measured from the model/i.test(note),
    "the N9 honesty note is untouched");
}

/* --------------------------------- 3. EVERY HULL, FROM ITS OWN DATA ---- */
console.log("\n--- 3. every hull with a model, checked against its own ports ---");
{
  let wrong = 0, none = 0, nopos = 0;
  const bad = [];
  for (const k of withModel) {
    const note = noteFor(k);
    const hasMarks = (MARKS[k] || []).length > 0;
    const hasMounts = mountsOf(SHIPS[k]).length > 0;
    const saysNone = NONE_MSG.test(note);
    const saysNoPos = NOPOS_MSG.test(note);
    let ok;
    if (hasMarks) ok = !saysNone && !saysNoPos;
    else if (!hasMounts) { ok = saysNone && !saysNoPos; if (ok) none++; }
    else { ok = saysNoPos && !saysNone; if (ok) nopos++; }
    if (!ok) { wrong++; if (bad.length < 5) bad.push(SHIPS[k].n); }
  }
  console.log(`    ${none} hulls told "no weapon mounts", `
    + `${nopos} told "no positions", ${marked.length} told neither`);
  record(wrong === 0,
    "EVERY hull gets exactly the message its own data implies, and only that "
    + "one",
    wrong ? `${wrong} wrong, e.g. ${bad.join(", ")}` : "");
  record(none > 0 && nopos > 0,
    "and both messages are actually in use - a rule that only ever fires one "
    + "way has not been tested by the fleet",
    `${none} / ${nopos}`);
  state.notes.push(`fleet: ${none} hulls have no weapon mounts, ${nopos} have `
    + `mounts and no positions, ${marked.length} carry markers`);
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_ONE || MUT_SILENT)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
