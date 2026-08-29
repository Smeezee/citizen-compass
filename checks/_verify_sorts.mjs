/**
 * E10 - "BEST" IS A JUDGEMENT AND THIS SITE DOES NOT MAKE JUDGEMENTS.

 *
 * RULE16: INDEPENDENT - the forbidden word is named here, from the rule, and the
 * shipped markup either contains it or does not. The orderings are
 * recomputed from the data and compared against what the page listed, so a
 * sort that quietly ranked by something else is caught by arithmetic rather
 * than by the page's own label for it.
 *
 * Sleven, 2026-08-23: "We do not determine what is best. Ever. We just provide
 * the information. The user determines what's best."
 *
 * Four factual sorts, each named for the measurement it performs. Every one
 * toggles. The button says what the NEXT click will do; an arrow on the active
 * sort says what the list is doing NOW - because a button that renames itself
 * leaves somebody unable to tell which state they are in, and both halves are
 * needed or the control is a riddle.
 *
 * THE LOAD-BEARING NEGATIVE IS THE THIRD CLICK. A build that reverses once and
 * then sticks passes every single-toggle check ever written, so the order asks
 * for it by name and it is section 4 below.
 *
 * IR AND EM ARE SEPARATE AXES AND THAT IS THE POINT OF SECTION 3. Asserting
 * that "Coolest" sorts by IR is worth nothing on a port where IR and EM happen
 * to rank the parts identically - the check would pass against a build that
 * still summed them. So the port used is one whose parts rank DIFFERENTLY
 * under the two, found from the data, and it is NAMED in the output.
 *
 * MUTATORS
 *   --mutate-nothird   the toggle sets the direction instead of flipping it,
 *                      so a second click reverses and every click after that
 *                      does nothing. Section 4 must fail.
 *   --mutate-sumsig    Coolest goes back to sorting on IR+EM. Section 3 must
 *                      fail, and it can only fail on a port where the two
 *                      disagree - which is why section 3 finds one.
 *   --mutate-nostate   the direction arrow is dropped, leaving the renaming
 *                      button as the only indication of which way the list
 *                      runs. Section 5 must fail.
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const MUTS = {
  "--mutate-nothird": [
    [/if\(sort===so\.dataset\.s\) sortDesc=!sortDesc;/,
     "if(sort===so.dataset.s) sortDesc=false;"],
  ],
  "--mutate-sumsig": [
    [/if\(k==="ir"\)   return \{key:"ir",  hi:"Hottest",  lo:"Coolest",  low:true\};/,
     'if(k==="ir")   return {key:"irem", hi:"Hottest",  lo:"Coolest",  low:true};'],
  ],
  "--mutate-nostate": [
    [/const arrow = active \? \(sortDesc \? "&#9660;" : "&#9650;"\) : "";/,
     'const arrow = "";'],
  ],
};
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
if (MUT && !MUTS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }

const mutate = MUT ? MUTS[MUT].slice() : [];
if (MUT === "--mutate-sumsig") {
  /* The summed key has to exist on the parts or the sort becomes a no-op and
     the mutation would plant nothing. */
  mutate.push([/const a=px\[axis\.key\]\|\|0, b=py\[axis\.key\]\|\|0;/,
    "const gv=function(o){return axis.key==='irem'?((o.ir||0)+(o.em||0))"
    + ":(o[axis.key]||0);};const a=gv(px), b=gv(py);"]);
}
if (MUT) console.log(`*** MUTATED: ${MUT} ***`);

const H = loadPage({ mutate,
  srcDir: process.env.CC_SRCDIR || null,
  pageFile: process.env.CC_PAGE || null });
const { record, finish, state } = reporter(false);
const { g, run, el, openShip, SHIPS } = H;

/* ---------- helpers ---------- */
/* The rendered list, in the order the page put it in. Read off the emitted
   markup rather than from the sort function, because the question is what a
   reader sees. */
/* THE SORTED STACK, WHICH IS NOT THE WHOLE LIST. B2 lifts the fitted part out
   and pins it to the top, and the sort governs only what follows - so comparing
   the full list against its own reverse would fail on the pinned row every
   time, and "the second click reverses the list" would be untestable. */
function listedNow() {
  const html = el("picker").innerHTML || "";
  const all = [...html.matchAll(
    /class="pi([^"]*)" data-part="([^"]+)"/g)];
  /* THE FILTER'S WORD BOUNDARIES WERE WRITTEN AS LITERAL BACKSPACE BYTES.
     `/\bpinned\b/` went through a Python string literal on the way into
     this file and `\b` there is 0x08, so the pattern became
     /<BS>pinned<BS>/ and matched nothing - the pinned row was never
     excluded and "the second click reverses the list" failed on it every
     time. Found by the counts not adding up (362 rows against 361 in the
     markup), not by reading the line. Plain substring, no escapes. */
  return all.filter((m) => m[1].indexOf("pinned") < 0).map((m) => m[2]);
}
function sortRowNow() {
  const html = el("picker").innerHTML || "";
  const m = /<div class="sortrow"[\s\S]*?<\/div>/.exec(html);
  return m ? m[0] : "";
}
function buttonsNow() {
  return [...sortRowNow().matchAll(
    /<button data-s="([a-z]+)"[^>]*aria-pressed="(true|false)"[^>]*>([\s\S]*?)<\/button>/g)]
    .map((m) => ({ key: m[1], on: m[2] === "true",
                   /* Tags AND entities, so a reported label reads as a
                      person sees it rather than as "&#9650;Hottest". */
                   label: m[3].replace(/<[^>]*>/g, "")
                     .replace(/&#\d+;/g, "").trim(),
                   /* &#9650; is UP and &#9660; is DOWN - the first version of this line
   read /&#966[05];/, which matches the down arrow and NOT the up one,
   so every ascending sort was reported as carrying no arrow. */
                   arrow: /&#96[56]0;/.test(m[3]) }));
}
function clickSort(key) {
  H.dispatch([".sortrow button[data-s]"], { dataset: { s: key } });
}

console.log("==========================================================");
console.log("E10 - four factual sorts, and every one of them toggles");
console.log("==========================================================");

/* =====================================================================
   1. A PORT TO DRIVE, AND IT IS NAMED.
   ===================================================================== */
console.log("\n--- 1. the port this runs against ---");
/* One whose parts rank DIFFERENTLY under IR and under EM - otherwise section 3
   would pass against a build that still summed the two. */
const found = g(`(function(){
  var best=null;
  Object.keys(SHIPS).forEach(function(k){
    (SHIPS[k].slots||[]).forEach(function(s){
      if(!s.fit) return;
      var ids=fitsFor(s);
      if(ids.length<4) return;
      var byIr=ids.slice().sort(function(a,b){
        return ((P[a]||{}).ir||0)-((P[b]||{}).ir||0)
          || String(a).localeCompare(String(b)); });
      var byEm=ids.slice().sort(function(a,b){
        return ((P[a]||{}).em||0)-((P[b]||{}).em||0)
          || String(a).localeCompare(String(b)); });
      if(byIr.join()===byEm.join()) return;
      /* And the summed order must differ from BOTH, or --mutate-sumsig plants
         a defect nothing can see. */
      var bySum=ids.slice().sort(function(a,b){
        var pa=P[a]||{}, pb=P[b]||{};
        return ((pa.ir||0)+(pa.em||0))-((pb.ir||0)+(pb.em||0))
          || String(a).localeCompare(String(b)); });
      if(bySum.join()===byIr.join()) return;
      if(!best || ids.length>best.n) best={ship:k, slot:s.id, t:s.t, n:ids.length};
    });
  });
  return best;
})()`);
record(!!found,
  "a port was found whose parts rank differently under IR, EM and their sum - "
  + "without one, section 3 would prove nothing",
  found ? `${g(`SHIPS[${JSON.stringify(found.ship)}].n`)} / ${found.slot} `
    + `(${found.t}, ${found.n} parts)` : "none");
if (!found) {
  console.log("\nNOT PERFORMED - no port in the data separates IR from EM, so "
    + "the assertion the order asks for cannot be made. Reported as not "
    + "performed rather than as passed.");
  process.exit(2);
}
const PORT = `${g(`SHIPS[${JSON.stringify(found.ship)}].n`)} - ${found.slot}`;
openShip(found.ship);
run(`sel={slot:${JSON.stringify(found.slot)},col:"A"};`
  + `$('picker').innerHTML=pickerHTML(ship().slots.find(function(s){`
  + `return s.id===${JSON.stringify(found.slot)};}));`);
const reRender = () => run(
  `$('picker').innerHTML=pickerHTML(ship().slots.find(function(s){`
  + `return s.id===${JSON.stringify(found.slot)};}));`);
record(listedNow().length > 0, "and its picker renders a list to sort",
  `${listedNow().length} rows`);

/* =====================================================================
   2. "BEST" IS GONE.
   ===================================================================== */
console.log("\n--- 2. no control tells anybody what is best ---");
{
  const row = sortRowNow();
  record(!/\bBest\b/i.test(row),
    "no sort control is labelled Best", row.slice(0, 120));
  /* SCOPED TO THE CONTROLS, DELIBERATELY. The order says assert the string
     appears nowhere on the page, and it cannot: the fleet contains the
     "Reclaimer Best In Show Edition 2949", which is CIG's name for a real
     ship and not this site making a judgement. Asserting on the whole page
     would fail on a ship name, and loosening it afterwards is how a check
     ends up asserting nothing. */
  const b = buttonsNow();
  record(b.length === 4, "four sorts are offered", b.map((x) => x.key).join(","));
  record(b.map((x) => x.key).join(",") === "head,ir,em,mass",
    "and they are the headline figure, IR, EM and mass",
    b.map((x) => x.key).join(","));
  record(b.filter((x) => x.on).length === 1,
    "exactly one is active at a time",
    String(b.filter((x) => x.on).length));
  const shipNames = g(`Object.keys(SHIPS).filter(function(k){
    return /\\bBest\\b/.test(SHIPS[k].n||""); }).length`);
  if (shipNames > 0) {
    console.log(`  note  ${shipNames} ship name(s) in the data contain the word `
      + `"Best" - CIG's own naming, which is why this assertion is scoped to `
      + `the sort controls rather than to the page`);
  }
}

/* =====================================================================
   3. IR AND EM ARE DIFFERENT SORTS.
   ===================================================================== */
console.log(`\n--- 3. Coolest is IR alone, Quietest is EM alone (${PORT}) ---`);
{
  clickSort("ir"); reRender();
  const byIr = listedNow();
  clickSort("em"); reRender();
  const byEm = listedNow();
  record(byIr.join() !== byEm.join(),
    "the two produce DIFFERENT orders on this port - which is the whole reason "
    + "this port was chosen");
  const irVals = g(`${JSON.stringify(byIr)}.map(function(k){return (P[k]||{}).ir||0;})`);
  const emVals = g(`${JSON.stringify(byEm)}.map(function(k){return (P[k]||{}).em||0;})`);
  const ascending = (a) => a.every((v, i) => i === 0 || a[i - 1] <= v);
  record(ascending(irVals),
    "Coolest orders by IR, ascending, and by nothing else",
    irVals.slice(0, 6).join(" "));
  record(ascending(emVals),
    "Quietest orders by EM, ascending, and by nothing else",
    emVals.slice(0, 6).join(" "));
  /* And NOT by the sum, which is what it used to do. */
  const bySum = g(`fitsFor(ship().slots.find(function(s){
    return s.id===${JSON.stringify(found.slot)};})).slice().sort(function(a,b){
      var pa=P[a]||{}, pb=P[b]||{};
      return ((pa.ir||0)+(pa.em||0))-((pb.ir||0)+(pb.em||0))
        || String(a).localeCompare(String(b)); })`);
  record(byIr.join() !== bySum.join(),
    "and Coolest is NOT the old summed order", "");
}

/* =====================================================================
   4. EVERY SORT TOGGLES - AND THE THIRD CLICK IS THE ONE THAT MATTERS.
   ===================================================================== */
console.log("\n--- 4. one click, two clicks, three clicks ---");
{
  for (const key of ["head", "ir", "em", "mass"]) {
    /* Start from a different axis so the first click is a fresh selection. */
    clickSort(key === "head" ? "mass" : "head"); reRender();
    clickSort(key); reRender();
    const first = listedNow();
    const labelFirst = (buttonsNow().find((b) => b.key === key) || {}).label;

    clickSort(key); reRender();
    const second = listedNow();
    const labelSecond = (buttonsNow().find((b) => b.key === key) || {}).label;

    clickSort(key); reRender();
    const third = listedNow();
    const labelThird = (buttonsNow().find((b) => b.key === key) || {}).label;

    record(second.join() === first.slice().reverse().join(),
      `${key}: the second click reverses the list exactly`,
      `${first.length} rows`);
    record(labelFirst !== labelSecond,
      `${key}: and the label flips`, `${labelFirst} -> ${labelSecond}`);
    /* THE LOAD-BEARING ONE. A build that reverses once and then sticks passes
       everything above. */
    record(third.join() === first.join(),
      `${key}: THE THIRD CLICK RETURNS TO THE FIRST ORDER`,
      third.join() === first.join() ? "" : "it stuck");
    record(labelThird === labelFirst,
      `${key}: and so does the label`, `${labelSecond} -> ${labelThird}`);
  }
}

/* =====================================================================
   5. WHICH WAY THE LIST RUNS IS VISIBLE WITHOUT READING THE BUTTON.
   ===================================================================== */
console.log("\n--- 5. the button says what is next; something says what is now ---");
{
  clickSort("em"); reRender();
  let b = buttonsNow();
  const act = b.find((x) => x.on);
  record(!!act && act.key === "em", "the clicked sort is the active one",
    act && act.key);
  record(!!act && act.arrow,
    "the active sort carries a direction arrow, so the current order is "
    + "readable without decoding a button that renames itself");
  record(b.filter((x) => x.arrow).length === 1,
    "and only the active one does", String(b.filter((x) => x.arrow).length));
  const down = sortRowNow();
  clickSort("em"); reRender();
  const up = sortRowNow();
  record(down !== up, "and the arrow changes when the direction does");
  b = buttonsNow();
  const act2 = b.find((x) => x.on);
  record(!!act2 && /title="showing /.test(sortRowNow()),
    "and the active control states the order it is currently showing",
    (/title="([^"]*)"/.exec(sortRowNow()) || [])[1]);
}

/* =====================================================================
   6. THE HEADLINE AXIS IS THE PORT'S OWN, ACROSS EVERY PORT TYPE.
   ===================================================================== */
console.log("\n--- 6. 'Most <stat>' names the measurement, per port type ---");
{
  const rows = g(`(function(){
    var byType={};
    Object.keys(SHIPS).forEach(function(k){(SHIPS[k].slots||[]).forEach(function(s){
      if(s.fit && !byType[s.t]) byType[s.t]=s; });});
    return Object.keys(byType).sort().map(function(t){
      var s=byType[t];
      return [t, (TYPES[t]&&TYPES[t].n)||t, fitsFor(s).length,
              sortAxis(s,'head').hi, sortAxis(s,'head').key];
    });
  })()`);
  record(rows.length > 20,
    `the headline axis resolves on all ${rows.length} port types in the data`);
  const verdicts = {};
  for (const r of rows) verdicts[r[3]] = (verdicts[r[3]] || 0) + 1;
  record(Object.keys(verdicts).length > 1,
    "and it is NOT one axis for everything - the old map covered five type "
    + "codes by hand and fell through to size for the other twenty-one",
    Object.keys(verdicts).join(" / "));
  for (const r of rows) {
    if (["wpn", "shd", "col", "pow", "qtm", "msl"].includes(r[0])) {
      console.log(`    ${r[0].padEnd(5)} ${String(r[1]).padEnd(20)} `
        + `${String(r[2]).padStart(4)} parts   ${r[3]}`);
    }
  }
  const wpn = rows.find((r) => r[0] === "wpn");
  record(!!wpn && wpn[4] === "dps",
    "a weapon port sorts on damage", wpn && wpn[3]);
  const shd = rows.find((r) => r[0] === "shd");
  record(!!shd && shd[4] === "ehp",
    "a shield generator on shielding", shd && shd[3]);
  const msl = rows.find((r) => r[0] === "msl");
  record(!!msl && msl[4] === "dmgt",
    "and a missile on damage - which the old five-entry map sorted by SIZE",
    msl && msl[3]);
}

finish(MUT
  ? "--mutate: a defect was planted, so a non-zero exit is the correct outcome."
  : `port driven: ${PORT}`);
