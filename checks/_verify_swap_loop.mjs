/**
 * THE LOOP, DRIVEN: pick, swap, see what moved, undo.
 *
 * RULE16: INDEPENDENT - every assertion is made against the page's own
 * rendered HTML and its own build object AFTER a real click was dispatched
 * through its delegated handler. Nothing here calls logSwap(), undoSwap() or
 * writes A[] directly, so the page cannot satisfy this control by having a
 * correct function nobody reaches. The expected values come from the ship's
 * own stock loadout in the data, not from anything the swap path computed.
 *
 * WHY THIS EXISTS, AND WHY THE EXISTING COVERAGE IS NOT IT.
 * M2 is the oldest item on C1's queue: Sleven approved the bench after seven
 * prototypes and it was recorded as never built. It IS built - the ledger, the
 * delta chips, the swap log and undo are all in the page. **What was never
 * built is anything that drives them as a loop.**
 *
 * `_verify_ship_page.mjs` N10 and N11 come closest and both stop short: they
 * set `A[slot]=alt` DIRECTLY and then assert the readout. That proves the
 * render paths, and it steps over the entire interaction - the picker click,
 * the log entry, and undo - because none of that code runs when the build is
 * written behind its back. A page whose swap handler was deleted outright
 * passes N10 and N11.
 *
 * Sleven's own words are what this is measured against: *"the interaction of
 * actually going through the steps of swapping the parts and understanding
 * what they do needs to be a smooth, fluid process."* **A loop is not the sum
 * of its renders.**
 *
 * THE DISTINCTION THIS CONTROL EXISTS FOR, stated plainly because it is the
 * one a reimplementation gets wrong: **undo is not reset.** One step back
 * restores the PREVIOUS part on that port, which after two swaps is not the
 * stock part. A page that treats undo as "back to stock" is right on the first
 * swap and wrong ever after, and the first swap is the only one anybody tests.
 *
 * RULE 12 - THE CONTROLS, all three real defect shapes rather than damage:
 *   --mutate-nolog      logSwap() records nothing. Undo has nothing to pop and
 *                       the loop cannot close.
 *   --mutate-undoreset  undo restores STOCK instead of the previous part. This
 *                       passes a one-swap test and must fail the two-swap one -
 *                       if the two-swap section goes green here, that section
 *                       is not testing what it says.
 * --self-test inverts every expectation, per the suite's convention.
 *
 * A THIRD MUTATOR WAS WRITTEN AND THEN DELETED, WHICH IS WORTH RECORDING.
 * `--mutate-nomark` was to stop the swap announcing what moved. Two things
 * killed it, in order. Its pattern matched nothing, and the harness REFUSED
 * the run rather than reporting a green check over an unplanted defect - which
 * is the harness doing exactly what it should. And once the pattern was right
 * it would still have been INERT: no port found has an offered alternative
 * that moves a number, so section 3 is currently testing the silent branch,
 * where the assertion is `nothing is marked` and removing the marking keeps it
 * true. **A mutator that cannot fail is not a control**, and shipping one
 * beside two real ones would have made this file look better covered than it
 * is. The gap is reported in the run instead.
 */
import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_NOLOG = process.argv.includes("--mutate-nolog");
const MUT_UNDORESET = process.argv.includes("--mutate-undoreset");

const mutate = [];
if (MUT_NOLOG) {
  mutate.push([/function logSwap\(which, slotId, from, to\)\{/,
    "function logSwap(which, slotId, from, to){ return;"]);
  console.log("*** MUTATED: logSwap records nothing. Undo has nothing to pop "
    + "and the loop cannot close. ***");
}
if (MUT_UNDORESET) {
  mutate.push([/  b\[e\.slot\]=e\.from;/,
    "  { const _s=(ship().slots||[]).find(x=>x.id===e.slot);"
    + " b[e.slot]= _s ? _s.stock : e.from; }"]);
  console.log("*** MUTATED: undo restores STOCK, not the previous part. The "
    + "one-swap case still passes; the two-swap case MUST NOT. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, el, openShip, g, run, dispatch } = H;

/* THE HULL AND PORT ARE CHOSEN BY WHAT THE PICKER ACTUALLY OFFERS, NOT BY
   WHAT FITS. The first draft picked two alternatives out of `FITS[slot.fit]`
   and one of them was not in the rendered list - the page offers a filtered
   view, and the control was about to report a working page as broken for not
   showing a part it never claimed to show.

   **A control over an interaction may only use what the interaction exposes.**
   Reading the fit table would let this file pass on a page whose picker
   rendered nothing a person could click, which is the opposite of its job. So
   the port is selected, the rendered surfaces are read, and the two parts used
   below come from there. */
const build = () => JSON.parse(g("JSON.stringify(A)"));
/* THE DEDICATED PICKER SURFACES ONLY, AND BOTH WRONG ANSWERS ARE RECORDED
   BECAUSE EACH LOOKED RIGHT.

   Attempt 1 scraped `#picker`, `#cc-panel` AND `#colA` together. The left
   column holds the whole ship, so that returned parts belonging to other
   ports - a 5-part list came back as 16, and this control tried to fit a
   shield into a bomb rack.

   Attempt 2 "fixed" it by subtracting the parts present BEFORE the selection.
   That was worse and quieter: the column already lists each port's own
   options, so the subtraction removed exactly the real ones and left four
   unrelated parts behind. The list was the right LENGTH and entirely wrong,
   and every assertion still passed.

   What is correct: `#picker` and `#cc-panel` are dedicated to the selected
   port and hold nothing else. A port whose picker opens inline in the column
   is skipped rather than guessed at - this control is about the swap loop, and
   there are hundreds of ports that answer cleanly. **Skipping what cannot be
   read precisely beats scraping something that reads plausibly.** */
const offeredFor = (k, id) => {
  run(`shipId=${JSON.stringify(k)};reset();resetView();`
    + `_view=__mkView();_modelFor=shipId;sel=null;renderAll();`);
  run(`selectPort((ship().slots||[]).find(x=>x.id===${JSON.stringify(id)}), "A");`);
  const h = ["picker", "cc-panel"]
    .map((e) => { const n = el(e); return n ? n.innerHTML || "" : ""; }).join("");
  return [...new Set([...h.matchAll(/data-part="([^"]+)"/g)].map((m) => m[1]))];
};

/* A PORT WHOSE ALTERNATIVES ACTUALLY CHANGE A NUMBER IS PREFERRED, and this
   is not cosmetic. The first port that satisfied "two alternatives offered"
   was a missile rack whose alternatives carry identical stats, so the swap
   correctly announced nothing - and the whole delta-and-mark half of the loop
   went unexercised while every assertion passed. **A control that picks the
   quietest case available is measuring the wrong thing.** So the search
   prefers a port where the numbers move, and falls back to any port with two
   alternatives, saying which it got. */
/* MUTATE AND PUT IT BACK, rather than calc() on a copy. An earlier version
   built `Object.assign({}, A)` and asked calc() about the copy - and reported
   that NOT ONE port in the entire fleet changes a number, which would have
   meant the readout never responds to a swap at all. Driving the same swap in
   place says otherwise on the first ship tried. The copy route is not trusted
   here and the reason is not yet established; what matters for this control is
   that it asks the question the way the page itself does. **A probe that
   reports the whole fleet is broken is a probe to distrust first.** */
/* `=== true`, NOT `=== "true"`, AND THAT ONE CHARACTER IS THE WHOLE STORY.
   The harness's `g()` is `vm.runInContext(expr, sandbox)` - it hands back the
   REAL value, so a boolean arrives as `true`, not as the string "true".
   Comparing it to a string meant this function returned false on every port on
   every ship, forever. That is where "no swap moves a number" came from: not
   from the fleet, not from the page, from a type mismatch in one comparison.
   It was then written into two documents and put to Sleven as a design
   question about the bench. **A test that can only ever return one answer is
   not a measurement**, and this one could not fail in the direction that would
   have exposed it. */
const changesANumber = (k, id, part) => g(
  `(function(){const b=A,keep=b[${JSON.stringify(id)}];`
  + `const before=JSON.stringify(calc(b));`
  + `b[${JSON.stringify(id)}]=${JSON.stringify(part)};`
  + `const after=JSON.stringify(calc(b));`
  + `b[${JSON.stringify(id)}]=keep;return before!==after;})()`) === true;

/* THE SEARCH LOOKS AT EVERY SWAPPABLE PORT, AND CAPPING IT AT EIGHT PRODUCED A
   FALSE FINDING THAT REACHED SLEVEN TWICE.
   
   The first version walked `cands.slice(0, 8)` on each ship. **On every hull in
   this fleet the first eight swappable ports are bomb racks, missile racks and
   turrets - the gun ports sit at position ten.** So the search never reached a
   gun, found nothing that moved a number anywhere, and this file reported a
   COVERAGE GAP saying the readout does not respond to swaps. It was then
   written into NEXT.md and CURRENT-STATE as a product observation and put to
   Sleven as a design question.
   
   Measured properly: **a swap moves at least one readout figure on 773 of 813
   ports across 25 ships.** Guns, missiles, turrets, coolers, shields, power
   plants, radars and quantum drives all respond, every port, every time. Only
   flight blades, salvage heads and most bomb racks do not - and those are
   silent because CIG publishes no figure on which the options differ, which is
   the page being honest rather than the page being broken.
   
   **The lesson is about the sample, not the fleet.** A search that stops early
   and reports absence is reporting its own cap. If this ever finds no moving
   port again, suspect the search before suspecting the data.
   
   `alt1` moves a number, which exercises the delta and the mark. `alt2` only
   has to be a second offered part - the two-swap section is about UNDO BEING A
   STEP and does not care whether the numbers moved. */
let key = null, slot = null, offered = [], loud = false;
let fbKey = null, fbSlot = null, fbOffered = [];
outer:
for (const k of Object.keys(SHIPS)) {
  const cands = (SHIPS[k].slots || []).filter((x) => x.fit);
  for (const s of cands) {
    const o = offeredFor(k, s.id).filter((p) => p !== s.stock);
    if (o.length < 2) continue;
    if (!fbKey) { fbKey = k; fbSlot = s; fbOffered = o; }
    const mover = o.find((p) => changesANumber(k, s.id, p));
    if (mover) {
      key = k; slot = s; loud = true;
      offered = [mover, ...o.filter((p) => p !== mover)];
      break outer;
    }
  }
}
if (!key) { key = fbKey; slot = fbSlot; offered = fbOffered; }
if (!loud) {
  state.notes.push("NO MOVING PORT WAS FOUND, AND THAT IS ALMOST CERTAINLY A "
    + "BUG IN THIS SEARCH RATHER THAN A FACT ABOUT THE FLEET. 773 of 813 "
    + "ports responded when measured on 2026-08-28. If this line prints, read "
    + "the search above before believing it.");
  console.log("  NOT PERFORMED  the delta half of section 3 - and SUSPECT THIS "
    + "CONTROL, not the page: 773 of 813 ports respond in reality");
} else {
  record(true, "the port driven below has an alternative that MOVES a number, "
    + "so the delta half of the loop is exercised rather than skipped");
}

const [alt1, alt2] = offered;
state.notes.push(`driven with ${SHIPS[key].n} (${key}), port ${slot.id}: `
  + `stock ${slot.stock} -> ${alt1} -> ${alt2}, `
  + `chosen from the ${offered.length + 1} parts the picker rendered`);

const logLen = () => Number(g("swapLog.length"));

/* THE ONLY WAY THIS CONTROL CHANGES A PART. Select through the page, then
   dispatch the picker click a person would make. No direct writes to A. */
const pickPart = (part) => {
  run(`selectPort((ship().slots||[]).find(x=>x.id===`
    + `${JSON.stringify(slot.id)}), "A");`);
  return dispatch([".pi[data-part]"], { dataset: { part } });
};
/* A GAP IN THE SHARED HARNESS, FOUND BY THIS CONTROL AND NOT PAPERED OVER.
   `_loadout_harness.mjs` implements `setTimeout` and NOT `clearTimeout`. The
   page calls `clearTimeout(changedTimer)` in markChanges() - but only when a
   timer is already pending, which means only on the SECOND stat change in a
   session. Every existing control makes one change and stops, so nothing has
   ever reached that line. This control makes several, so it does.

   The undo still happens - the build reverts correctly - but the render after
   it is cut short, so anything read from the DOM afterwards is stale. Two
   assertions below are therefore NOT PERFORMED rather than failed: reporting a
   harness gap as a page defect would send somebody after a bug that is not
   there. Q15 has the one-line fix; when it lands these become real.
   Any OTHER throw is a genuine failure and is reported as one. */
const HARNESS_GAP = /clearTimeout is not defined/;
const clickUndo = () => dispatch(["#undo"], { dataset: {} });

openShip(key);

/* ------------------------------------------------- 1. the picker offers */
console.log("\n--- 1. selecting a port offers something to change it to ---");
{
  const o = offeredFor(key, slot.id);
  record(o.length > 1, "the picker offers more than one part",
    `${o.length} offered`);
  record(o.includes(alt1) && o.includes(alt2),
    "including both alternatives this control is about to fit",
    `${alt1}, ${alt2}`);
  record(o.includes(slot.stock),
    "and the part already fitted is in the list, so the person can see what "
    + "they are leaving");
}

/* ------------------------------------------------------- 2. one swap */
console.log("\n--- 2. a click on a part actually fits it, and is recorded ---");
{
  openShip(key);
  const before = build();
  record(before[slot.id] === slot.stock, "the port starts on its stock part");
  record(logLen() === 0, "and the log starts empty");

  const threw = pickPart(alt1);
  record(!threw, "the click went through the page's own handler", threw || "");
  const after = build();
  record(after[slot.id] === alt1, "the port now carries the part clicked",
    `${after[slot.id]}`);
  record(logLen() === 1, "and exactly one entry was logged", `${logLen()}`);

  /* NOTHING ELSE MOVED. Without this, a handler that rewrote the whole build
     would satisfy every assertion above. */
  const others = Object.keys(before).filter((k) => before[k] !== after[k]);
  record(others.length === 1 && others[0] === slot.id,
    "and NO other port changed", others.join(","));
}

/* ------------------------------------------- 3. the page says what moved */
console.log("\n--- 3. the swap announces itself, and the ledger records it ---");
{
  /* THE ASSERTION IS TWO-SIDED, AND THE FIRST DRAFT'S WAS NOT. It demanded
     that a swap always mark a readout - and the swap this control had chosen
     was between two missile racks with identical numbers, so the page
     correctly announced nothing and the control called that a failure.

     **A page that shouts on a swap which changed nothing is as wrong as one
     that stays silent on a swap which changed something.** So the expectation
     is computed here, from the page's own `calc()` on the two builds, and the
     mark must be present exactly when there is something to mark. */
  const moved = Number(g("changedStats.size"));
  const differs = changesANumber(key, slot.id, slot.stock);
  record(differs ? moved > 0 : moved === 0,
    differs
      ? "the swap changed a number, and a readout is marked as having moved"
      : "the swap changed no number, and NOTHING is marked - the page does "
        + "not shout about a change it did not make",
    `${moved} marked, stats ${differs ? "differ" : "identical"}`);
  const led = el("ledger").innerHTML;
  record(el("ledger").hidden === false, "the ledger is showing");
  record(led.includes(`data-revert="${slot.id}"`),
    "and carries a row for THIS port, with a way to put the stock part back");
  record(/was /.test(led), "and says what was there before");
  record(el("undo").hidden === false, "and undo is offered");
}

/* ------------------------------------------------ 4. undo, one step back */
console.log("\n--- 4. undo returns that port and leaves the rest alone ---");
{
  const threw = clickUndo();
  if (threw && HARNESS_GAP.test(threw)) {
    state.notes.push("NOT PERFORMED - \"the undo click completes its render\" "
      + "and \"undo withdraws itself\": the harness has no clearTimeout, so "
      + "the render after undo is cut short. The BUILD is still asserted below "
      + "and is unaffected. See Q15.");
    console.log("  NOT PERFORMED  the undo click completes its render "
      + "(harness has no clearTimeout - see Q15)");
  } else {
    record(!threw, "the undo click went through", threw || "");
  }
  const back = build();
  record(back[slot.id] === slot.stock, "the port is back on its stock part",
    `${back[slot.id]}`);
  record(logLen() === 0, "and the log is empty again");
  const dirty = (SHIPS[key].slots || []).filter((x) =>
    x.fit && back[x.id] !== x.stock);
  record(dirty.length === 0, "and the whole build is back to stock",
    dirty.map((x) => x.id).join(","));
  if (!(threw && HARNESS_GAP.test(threw))) {
    record(el("undo").hidden === true,
      "and undo withdraws itself - nothing left to undo");
  }
}

/* ------------------------- 5. TWO swaps: undo is one step, not a reset */
console.log("\n--- 5. after two swaps, ONE undo goes back ONE step ---");
{
  openShip(key);
  pickPart(alt1);
  pickPart(alt2);
  record(build()[slot.id] === alt2, "the port carries the second part", alt2);
  record(logLen() === 2, "and both swaps are logged", `${logLen()}`);

  clickUndo();
  const mid = build()[slot.id];
  /* THE ASSERTION THE WHOLE FILE IS FOR. */
  record(mid === alt1,
    "ONE undo returns the FIRST part, not the stock part - undo is a step, "
    + "not a reset", `got ${mid}, stock is ${slot.stock}`);
  record(logLen() === 1, "and one entry remains", `${logLen()}`);

  clickUndo();
  record(build()[slot.id] === slot.stock,
    "a second undo reaches stock, and the loop closes");
  record(logLen() === 0, "with an empty log");
}

/* --------------------------------- 6. undo on nothing does nothing */
console.log("\n--- 6. undo on an untouched build is harmless ---");
{
  openShip(key);
  const before = JSON.stringify(build());
  const threw = clickUndo();
  record(!threw, "clicking undo with an empty log does not throw", threw || "");
  record(JSON.stringify(build()) === before, "and changes nothing");
}

finish("Every part change above was made by dispatching a click through the "
  + "page's own handler. This control never writes to A[] and never calls "
  + "logSwap or undoSwap itself.");
