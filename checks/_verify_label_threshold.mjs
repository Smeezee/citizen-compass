/**
 * R1 - THE SOLVER DECIDES WHETHER LABELS ARE ON, NOT A COUNTER.
 *
 * Sleven, on the Aegis Reclaimer: "everything works the way it's supposed to,
 * but it doesn't have the names like the other ones do."
 *
 * IT WAS NOT BROKEN. 15 markers, every one resolving to a real port with a real
 * hardpoint name and a fitted part, and ONE OVER a threshold of 14 that H1b
 * invented. A working feature that the person using it concluded was a broken
 * page - the third time in two days, after the silent markers and the panel
 * labelled `Look`.
 *
 * THE THRESHOLD WAS MEASURABLY WRONG, not merely arbitrary, and section 1
 * re-measures that every run rather than quoting it.
 *
 * WHAT MAKES THE SOLVER RIGHT IS NOT THAT IT DISAGREES WITH 14 TODAY. Measured
 * across the fleet, the largest hull that places every label cleanly carries 17
 * and the smallest that cannot carries 23 - so a count of 20 would give the
 * same answers as the solver on today's data, and this file says so rather than
 * implying the solver is vindicated by a disagreement it does not have.
 *
 * What makes it right is that the answer MOVES WITH THE THING BEING ASKED
 * ABOUT. Section 4 shrinks the stage and the Reclaimer's answer flips with its
 * marker count unchanged - which no number in the source can follow, and which
 * is exactly what happens on a laptop, a split screen or a phone.
 *
 * MUTATORS
 *   --mutate-alwayson    labels are on whatever the solver says. The order's
 *                        load-bearing negative: without it, "everything is on"
 *                        passes every other assertion here.
 *   --mutate-countagain  the count threshold of 14 comes back, and the
 *                        Reclaimer goes dark again.
 *   --mutate-caption     the off-state stops saying how many have no room, so
 *                        it is a status line again rather than a control.
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const MUTS = {
  "--mutate-alwayson": [
    [/function labelsWanted\(dropped\)\{\s*if\(allLabels!==null\) return allLabels;\s*return !dropped;\s*\}/,
     "function labelsWanted(dropped){ if(allLabels!==null) return allLabels;"
     + " return true; }"],
  ],
  "--mutate-countagain": [
    [/function labelsWanted\(dropped\)\{\s*if\(allLabels!==null\) return allLabels;\s*return !dropped;\s*\}/,
     "function labelsWanted(dropped){ if(allLabels!==null) return allLabels;"
     + " return markersFor(shipId).length<=14; }"],
  ],
  "--mutate-caption": [
    [/\? `<b>\$\{total\} hardpoints<\/b> &middot; \$\{dropped\} \$\{\s*dropped===1\?"has":"have"\} no room`/,
     '? `<b>${total} hardpoints</b> &middot; labels off on a hull this busy`'],
  ],
};
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
if (MUT && !MUTS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }
if (MUT) console.log(`*** MUTATED: ${MUT} ***`);

const H = loadPage({ mutate: MUT ? MUTS[MUT] : [], viewer: true,
  srcDir: process.env.CC_SRCDIR || null,
  pageFile: process.env.CC_PAGE || null });
const { record, finish, state } = reporter(false);
const { g, run, el, openShip, SHIPS, MARKS } = H;

const box = () => el("cc-labels");
const shownNow = () => Number(box()["data-shown"] || 0);
const noRoomNow = () => Number(box()["data-dropped"] || 0);
const hintNow = () => String(el("cc-labelcount").innerHTML || "")
  .replace(/<[^>]*>/g, " ").replace(/&middot;/g, "·").replace(/\s+/g, " ").trim();
const find = (frag) => Object.keys(SHIPS).find(
  (k) => (SHIPS[k].n || "").includes(frag) && (MARKS[k] || []).length);

console.log("==========================================================");
console.log("R1 - the solver decides, and the Reclaimer was never broken");
console.log(MUT ? `MUTATED: ${MUT}` : "clean page");
console.log("==========================================================");

/* =====================================================================
   1. THE FLEET, RE-MEASURED. Not quoted from the order.
   ===================================================================== */
console.log("\n--- 1. what the solver actually says, over every hull ---");
const census = [];
{
  const keys = Object.keys(SHIPS).filter((k) => (MARKS[k] || []).length);
  for (const k of keys) {
    openShip(k);
    census.push({ k, n: (SHIPS[k].n || k), markers: (MARKS[k] || []).length,
                  noRoom: noRoomNow() });
  }
  const clean = census.filter((c) => c.noRoom === 0);
  const dirty = census.filter((c) => c.noRoom > 0);
  /* THE INVARIANT IS "EVERY MARKED HULL WAS DRIVEN", NOT "159 HULLS WERE".
     159 was the fleet size on the day this was written. P1 widened the
     placer's candidate set and the number became 163, so a control that had
     nothing to do with the placer went red on a legitimate change - and the
     next person's cheapest move is to edit the number, which is how a count
     ends up being maintained instead of an assertion.
     Compared against the marker table itself: if the sweep skips a hull, this
     still fails, and it fails for the reason it was written to catch. */
  const marked = Object.keys(SHIPS).filter((k) => (MARKS[k] || []).length);
  record(census.length === marked.length && census.length > 100,
    `all ${census.length} hulls that carry markers were driven through the `
    + `solver`, `${census.length} driven, ${marked.length} carry markers`);
  record(clean.length > dirty.length * 10,
    "the great majority place every label with no overlaps",
    `${clean.length} clean, ${dirty.length} not`);
  for (const d of dirty.sort((a, b) => b.noRoom - a.noRoom)) {
    console.log(`    ${String(d.markers).padStart(3)} markers -> `
      + `${String(d.noRoom).padStart(2)} with no room   ${d.n}`);
  }
  state.notes.push(`solver census: ${clean.length} of ${census.length} hulls `
    + `place every label cleanly`);

  /* THE HONEST COMPARISON WITH THE NUMBER THIS REPLACES. */
  const wouldHide = census.filter((c) => c.markers > 14);
  const wrongly = wouldHide.filter((c) => c.noRoom === 0);
  record(wrongly.length > 0,
    "the old threshold of 14 hid labels on hulls that place PERFECTLY - which "
    + "is the defect, stated as a number",
    `${wrongly.length} of ${wouldHide.length}: `
    + `${wrongly.map((c) => `${c.n} (${c.markers})`).join(", ")}`);
  record(wouldHide.length - wrongly.length === census.filter(
    (c) => c.noRoom > 0 && c.markers > 14).length,
    "and it caught nothing the solver does not",
    `${wouldHide.length - wrongly.length} genuinely crowded`);

  /* AND THE PART THAT IS NOT A WIN, SAID PLAINLY. */
  const maxClean = Math.max(...clean.map((c) => c.markers));
  const minDirty = Math.min(...dirty.map((c) => c.markers));
  record(maxClean < minDirty,
    "on TODAY's fleet a count between those two would agree with the solver - "
    + "so the solver is not vindicated by disagreeing, and section 4 is what "
    + "makes the case", `largest clean ${maxClean}, smallest crowded ${minDirty}`);
}

/* =====================================================================
   2. THE HULL SLEVEN NAMED.
   ===================================================================== */
console.log("\n--- 2. the Aegis Reclaimer ---");
{
  const k = find("Reclaimer");
  record(!!k, "the Reclaimer is in the data with markers", String(k));
  openShip(k);
  record((MARKS[k] || []).length === 15,
    "it carries 15 markers - one over the invented line",
    String((MARKS[k] || []).length));
  /* NOTHING WAS MISSING, and that is the item. Every marker resolves to a port
     with a name and a part. */
  const resolved = g(`markersFor(shipId).filter(function(m){
    var sl = slotByPort(m[0]);
    return !!(sl && portLabel(sl.h)); }).length`);
  record(resolved === 15,
    "and every one of them resolves to a real port with a real hardpoint "
    + "name - nothing was missing", `${resolved} of 15`);
  record(noRoomNow() === 0,
    "the solver places all 15 with no overlaps", `${noRoomNow()} with no room`);
  record(shownNow() === 15,
    "so labels are ON by default, with nothing clicked", `${shownNow()} up`);
  record(/all labelled/.test(hintNow()),
    "and the page says so", hintNow());
}

/* =====================================================================
   3. THE NEGATIVE THE ORDER NAMES: a hull that cannot place defaults OFF.
   ===================================================================== */
console.log("\n--- 3. a hull the solver cannot fully place ---");
{
  const k = find("Perseus");
  record(!!k, "the RSI Perseus is in the data", String(k));
  openShip(k);
  record(noRoomNow() > 0,
    "the solver cannot place them all", `${noRoomNow()} with no room`);
  record(shownNow() === 0,
    "so labels are OFF by default - without this, a build where everything is "
    + "on passes every other assertion here", `${shownNow()} up`);
  /* R1b: AND IT READS AS A CONTROL, WITH ITS REASON. */
  const hint = hintNow();
  record(/9 have no room/.test(hint),
    "the line says how many have no room, as a number a reader can check",
    hint);
  record(/show all labels anyway/.test(hint),
    "and offers the way past it in words that invite a press", hint);
  record(!/this busy/.test(hint),
    "and does NOT fall back to a status caption about the hull being busy");
  /* Both the other two of the four. */
  for (const nm of ["Idris-P", "Polaris"]) {
    const kk = find(nm);
    if (!kk) continue;
    openShip(kk);
    record(shownNow() === 0 && noRoomNow() > 0,
      `${nm} defaults off too, for the same measured reason`,
      `${noRoomNow()} with no room`);
  }
}

/* =====================================================================
   4. THE ANSWER MOVES WITH THE STAGE. This is the case for a solver.
   ===================================================================== */
console.log("\n--- 4. the same hull, a smaller stage, a different answer ---");
{
  const k = find("Reclaimer");
  openShip(k);
  const wide = { shown: shownNow(), noRoom: noRoomNow() };
  run(`document.getElementById('cc-stage').clientWidth=300;
       document.getElementById('cc-stage').clientHeight=200;
       document.getElementById('cc-canvas').clientWidth=300;
       document.getElementById('cc-canvas').clientHeight=200;
       renderLabels();`);
  const narrow = { shown: shownNow(), noRoom: noRoomNow() };
  record((MARKS[k] || []).length === 15,
    "the marker count has not changed", String((MARKS[k] || []).length));
  record(wide.noRoom === 0 && narrow.noRoom > 0,
    "but on a 300x200 stage the labels no longer fit - the SAME 15 markers, a "
    + "different answer", `${wide.noRoom} -> ${narrow.noRoom} with no room`);
  record(wide.shown > 0 && narrow.shown === 0,
    "so the default flips, which is a thing no number in the source could have "
    + "followed", `${wide.shown} -> ${narrow.shown} labels up`);
  state.notes.push(`the Reclaimer: 15/15 placed at 960x540, `
    + `${narrow.noRoom} with no room at 300x200`);

  /* PUT THE STAGE BACK. This section is the only one that changes it, and
     leaving it at 300x200 made sections 5 and 6 measure a hull that no longer
     fits its own labels - four assertions failing on a page that was correct.
     THIRD TIME A CONTROL OF MINE HAS LEAKED ITS OWN STATE INTO A LATER
     SECTION; the first two are in the ledger under H1f and H1b, and all three
     were found by numbers being wrong in a way the feature could not explain
     rather than by a run failing where the defect was. */
  run(`document.getElementById('cc-stage').clientWidth=960;
       document.getElementById('cc-stage').clientHeight=540;
       document.getElementById('cc-canvas').clientWidth=960;
       document.getElementById('cc-canvas').clientHeight=540;
       renderLabels();`);
  record(noRoomNow() === 0,
    "and the stage is put back, so what follows measures the page rather than "
    + "this section's leftovers", `${noRoomNow()} with no room`);
}

/* =====================================================================
   5. THE READER'S CHOICE STILL WINS, IN BOTH DIRECTIONS.
   ===================================================================== */
console.log("\n--- 5. the toggle overrides the solver, both ways ---");
{
  const on = find("Reclaimer"), off = find("Perseus");
  openShip(on);
  record(shownNow() === 15, "the Reclaimer opens with labels up");
  H.dispatch(["#cc-lbl-toggle"]);
  record(shownNow() === 0, "pressing the control hides them", `${shownNow()}`);
  record(/labels off/.test(hintNow()) && !/no room/.test(hintNow()),
    "and the line says it was the READER's choice, not the page's - the hull "
    + "places fine and the page must not claim otherwise", hintNow());
  H.dispatch(["#cc-lbl-toggle"]);
  record(shownNow() === 15, "and pressing it again brings them back",
    `${shownNow()}`);

  openShip(off);
  record(shownNow() === 0, "the Perseus opens with labels down");
  H.dispatch(["#cc-lbl-toggle"]);
  record(shownNow() > 20,
    "and 'show all labels anyway' shows the ones that DO fit rather than "
    + "nothing", `${shownNow()} up, ${noRoomNow()} with no room`);
}

/* =====================================================================
   6. A SELECTION IS ALWAYS LABELLED, EVEN ON A CROWDED HULL.
   ===================================================================== */
console.log("\n--- 6. clicking a marker on a hull with labels off ---");
{
  const k = find("Perseus");
  openShip(k);
  record(shownNow() === 0, "labels start down");
  const slot = g(`(function(){
    var m = markersFor(shipId)[0];
    return m ? slotByPort(m[0]) : null; })()`);
  record(!!slot, "a marker resolves to a port to select", slot && slot.id);
  run(`sel={slot:${JSON.stringify(slot.id)}}; renderLabels();`);
  record(shownNow() === 1,
    "selecting one labels THAT ONE and only that one", `${shownNow()}`);
  record(noRoomNow() > 0,
    "and the line still reports the hull's own fit, not what is on screen",
    `${noRoomNow()} with no room`);
}

finish(MUT
  ? "--mutate: a defect was planted, so a non-zero exit is the correct outcome."
  : "");
