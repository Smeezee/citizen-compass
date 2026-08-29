/**
 * WHEN EVERY PART ON A PORT IS THE SAME PART IN A DIFFERENT WRAPPER, DOES THE
 * PAGE SAY SO?
 *
 * RULE16: INDEPENDENT - which ports ARE identical is decided here, from the
 * part table, by re-implementing the comparison rather than calling the page's
 * `sameOnEveryStat()`. The page and this control reach the same list by two
 * routes, so a bug in the page's comparison shows up as a disagreement instead
 * of being copied into the expectation. What is read back is the rendered
 * HTML, not a page variable.
 *
 * WHY IT EXISTS. 773 of 813 swappable ports move at least one readout figure
 * when a part is swapped. **18 do not** - flight blades, salvage heads and most
 * bomb racks - because CIG publishes no figure on which their options differ.
 * The page was silent on those ports, and silence and "nothing to report" look
 * identical to a visitor. Sleven's call on 2026-08-28: say it.
 *
 * THE ASSERTION IS TWO-SIDED, and the second half is the one that matters:
 *   A. a port whose options ARE identical carries the line
 *   B. a port whose options are NOT carries nothing
 * Without B this passes on a page that prints the sentence on every port,
 * which would be worse than printing it on none - it would be false on 795 of
 * them.
 *
 * RULE 12 - THE CONTROLS:
 *   --mutate-always  the line appears on every port. B must fire.
 *   --mutate-never   the line never appears. A must fire.
 *   --mutate-name    the comparison stops excluding the part NAME, so no set
 *                    is ever identical and the line silently never shows. This
 *                    is the realistic regression - a stricter comparison looks
 *                    more careful and quietly switches the feature off.
 * --self-test inverts every expectation, per the suite's convention.
 */
import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_ALWAYS = process.argv.includes("--mutate-always");
const MUT_NEVER = process.argv.includes("--mutate-never");
const MUT_NAME = process.argv.includes("--mutate-name");

const mutate = [];
if (MUT_ALWAYS) {
  mutate.push([/if\(!n\) return "";/, "if(false) return \"\";"]);
  mutate.push([/  if\(parts\.length<2\) return 0;/,
    "  if(parts.length<2) return 0;\n  return parts.length;"]);
  console.log("*** MUTATED: the line appears on every port. B MUST fire. ***");
}
if (MUT_NEVER) {
  mutate.push([/function sameStatLine\(ids, slot\)\{/,
    "function sameStatLine(ids, slot){ return \"\";"]);
  console.log("*** MUTATED: the line never appears. A MUST fire. ***");
}
if (MUT_NAME) {
  mutate.push([/if\(k!=="n"&&k!=="m"\) keys\.add\(k\);/, "keys.add(k);"]);
  console.log("*** MUTATED: the comparison no longer excludes name and maker, "
    + "so nothing is ever identical and the feature is off. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, el, g, run } = H;

const P = JSON.parse(g("JSON.stringify(P)"));
const FITS = JSON.parse(g("JSON.stringify(FITS)"));

/* Re-implemented, not imported. Name and maker are the two fields that are
   ALLOWED to differ - they are what the line tells the reader to choose on. */
const childPorts = (k, slot) => {
  const pre = String(slot.p) + ".";
  return (SHIPS[k].slots || []).some((x) => String(x.p).indexOf(pre) === 0);
};

/* A MOUNT THAT CARRIES OTHER PARTS IS EXCLUDED, and this control is why the
   page excludes it. The first build put the line on the Sabre's missile mount:
   39 racks, all mass 20 at size 4, identical by the part table - and named
   "Gatac Missile Rack 8xS1" and "20xS3" on screen. A rack's real difference is
   its child ports, one level down. True of our data, visibly false to a player.
   Where the difference could be somewhere neither the page nor this check can
   see, the honest answer is silence. */
function identical(ids) {
  const parts = ids.map((k) => P[k]).filter(Boolean);
  if (parts.length < 2) return false;
  const keys = new Set();
  for (const p of parts) {
    for (const k of Object.keys(p)) if (k !== "n" && k !== "m") keys.add(k);
  }
  for (const k of keys) {
    const v = parts[0][k];
    for (let i = 1; i < parts.length; i++) if (parts[i][k] !== v) return false;
  }
  return true;
}

const open = (k, id) => {
  run(`shipId=${JSON.stringify(k)};reset();resetView();`
    + `_view=__mkView();_modelFor=shipId;sel=null;renderAll();`);
  run(`selectPort((ship().slots||[]).find(x=>x.id===${JSON.stringify(id)}), "A");`);
  return ["picker", "cc-panel"]
    .map((e) => { const n = el(e); return n ? n.innerHTML || "" : ""; })
    .join("").replace(/\s+/g, " ");
};
const says = (html) => /identical on every stat the game publishes/i.test(html);

/* Find one port of each kind, by measurement rather than by name - AND ONLY
   ONES WHOSE PICKER THIS CONTROL CAN ACTUALLY READ.
   `pickerHome()` sends a port's list to one of three surfaces. `#picker` and
   `#cc-panel` belong to the selected port alone; the third is the left column,
   which holds the whole ship and cannot be attributed to one port without
   guessing. The first version of this search ignored that, picked the Avenger
   flight blade port - whose picker opens inline - and reported "the picker
   rendered 0 chars" against a page that was rendering it correctly. Ports that
   open inline are skipped, and section C still sweeps 64 of them. */
let same = null, diff = null;
outer:
for (const k of Object.keys(SHIPS)) {
  for (const s of (SHIPS[k].slots || []).filter((x) => x.fit)) {
    const ids = (FITS[s.fit] || []);
    if (ids.length < 2) continue;
    const isSame = identical(ids) && !childPorts(k, s);
    if (isSame && same) continue;
    if (!isSame && diff) continue;
    if (open(k, s.id).length < 50) continue;      // inline picker - not readable here
    if (isSame) same = [k, s, ids]; else diff = [k, s, ids];
    if (same && diff) break outer;
  }
}

record(!!same, "found a port whose options are identical on every published stat",
  same ? `${same[0]} / ${same[1].id} (${same[2].length} options)` : "none");
record(!!diff, "and one whose options genuinely differ",
  diff ? `${diff[0]} / ${diff[1].id}` : "none");
if (!same || !diff) finish("cannot proceed without one of each");

const nameOf = (id) => (P[id] || {}).n || id;
state.notes.push(`identical set: ${same[0]} ${same[1].id} — `
  + same[2].map(nameOf).join(" · "));
state.notes.push(`differing set: ${diff[0]} ${diff[1].id} — `
  + diff[2].slice(0, 3).map(nameOf).join(" · ") + " …");

console.log("\n--- A. the port that has nothing to distinguish says so ---");
{
  const html = open(same[0], same[1].id);
  record(html.length > 50, "the picker rendered", `${html.length} chars`);
  record(says(html), "and states the options are identical on every published stat");
  record(/looks or on price/i.test(html),
    "and tells the reader what IS left to choose on");
  record(new RegExp(`These ${same[2].length} are identical`).test(html),
    `and counts them correctly — ${same[2].length}`);
}

console.log("\n--- B. the port that has something to say does NOT say it ---");
{
  const html = open(diff[0], diff[1].id);
  record(html.length > 50, "that picker rendered too", `${html.length} chars`);
  record(!says(html),
    "and does NOT claim its options are identical — they are not");
}

console.log("\n--- C. across the fleet, the line appears exactly where it should ---");
{
  let checked = 0, wrong = [];
  for (const k of Object.keys(SHIPS).slice(0, 6)) {
    for (const s of (SHIPS[k].slots || []).filter((x) => x.fit)) {
      const ids = FITS[s.fit] || [];
      if (ids.length < 2) continue;
      const html = open(k, s.id);
      if (!html.length) continue;
      checked++;
      const want = identical(ids) && !childPorts(k, s);
      if (says(html) !== want) wrong.push(`${k}/${s.id}`);
    }
  }
  record(checked > 20, `enough ports to mean something — ${checked} checked`);
  record(wrong.length === 0,
    "the page and an independent comparison agree on every one",
    wrong.slice(0, 6).join(", "));
  state.notes.push(`swept ${checked} ports across 6 ships, ${wrong.length} disagreements`);
}

finish("Which ports are identical was decided here, from the part table, "
  + "never by asking the page.");
