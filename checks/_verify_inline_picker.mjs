/**
 * B2 acceptance: THE PICKER OPENS UNDER ITS ROW, AND THE FITTED PART IS FIRST.
 *
 * TWO SEPARATE COMPLAINTS, BOTH SLEVEN'S, BOTH REAL.
 *
 * 1. The picker took the whole column, so opening a port meant losing your
 *    place in the list you were reading. P5 created that by fixing something
 *    else: the picker used to render ~1,050px down a 1,952px page, and moving
 *    it into the column put it where the eye was at the cost of the list.
 *    It now opens INLINE beneath the row that was clicked, with the rows above
 *    and below still on screen, and only one row open at a time.
 *
 * 2. He opened the Avenger's size-4 turret mount, which offers 74 parts sorted
 *    by DPS, and THE PART ALREADY FITTED WAS NOWHERE ON SCREEN. A person
 *    cannot see what they are replacing. The fitted part is now lifted out of
 *    the sort and pinned to the top, labelled, exactly once.
 *
 * WHAT THIS CANNOT PROVE: that anything is visible. There is no browser here.
 * It proves the rows are in the emitted markup and that the open one is where
 * it should be. Whether it fits at 1366x768 is B8's job, at a stated viewport,
 * against the deployed bytes.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-pin    the fitted part is left in the sort instead of pinned -
 *                   which is exactly the state Sleven hit.
 *   --mutate-multi  every row opens its picker at once, so "only one at a
 *                   time" stops being true.
 *   --self-test     inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_inline_picker.mjs
 *        [--self-test] [--mutate-pin] [--mutate-multi]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_PIN = process.argv.includes("--mutate-pin");
const MUT_MULTI = process.argv.includes("--mutate-multi");

const mutate = [];
if (MUT_PIN) {
  mutate.push([/const pinned = opts\.indexOf\(cur\)>=0 \? cur : null;/,
               "const pinned = null;"]);
  console.log("*** MUTATED: nothing is pinned - the fitted part goes back into "
    + "the sorted list, where Sleven could not find it. ***");
}
if (MUT_MULTI) {
  mutate.push([/if\(active\)\{\s*\n\s*h\+=`<div class="inlinepick"/,
               'if(true){\n      h+=`<div class="inlinepick"']);
  console.log("*** MUTATED: every row opens its picker at once. \"Only one "
    + "row is open\" MUST stop being true. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, el, openShip, g, run, dispatch, PARTS } = H;

const key = Object.keys(SHIPS).find(
  (k) => /avenger stalker/i.test(SHIPS[k].n || ""));
record(!!key, "the Aegis Avenger Stalker is in the ship table", key || "");
const SH = SHIPS[key];
openShip(key);

const swap = SH.slots.filter((s) => s.fit);
const fitsCount = (s) => (g("FITS")[s.fit] || []).length;

/* ------------------------------- 1. THE TURRET MOUNT, THE FITTED PART FIRST */
console.log("\n--- 1. the fitted part is FIRST, on every sort ---");
/* THE PORT SLEVEN ACTUALLY OPENED, named by its type rather than found by
   "the longest list" - which was the first version of this line and picked the
   wrong port. The Avenger's flight controller offers 238 parts, more than the
   turret mount's 74, so "longest" quietly drove this whole block against a
   port the order never mentioned. The order says turret mount; this asks for a
   turret mount. */
const turret = swap.filter((s) => s.t === "tur")
  .sort((a, b) => (b.s || 0) - (a.s || 0))[0];
record(!!turret, "the Avenger Stalker has a turret mount port");
const nOpts = turret ? fitsCount(turret) : 0;
record(nOpts > 40,
  `and it offers a list long enough for this to matter - ${nOpts} parts, `
  + `at size ${turret ? turret.s : "?"}`,
  `${nOpts}`);
state.notes.push(`driven with ${SH.n}: ${g("tname")(turret.t)} size `
  + `${turret.s}, ${nOpts} parts fit it - the port Sleven opened and could not `
  + `find the fitted part in`);

const fittedKey = SH.slots.find((s) => s.id === turret.id).stock;
record(!!(fittedKey && PARTS[fittedKey]),
  "the game data names what is fitted there",
  fittedKey ? (PARTS[fittedKey] || {}).n : "nothing");

/* WHEREVER IT OPENED. B3 gave a hull-mounted port a panel over the stage, and
   the turret mount below is hull-mounted - so the pinning half of this item is
   asserted through the harness's pickerNow(), which reads every home. Pinning
   is a property of the LIST, not of where the list is drawn. */
/* READ THE LIST RENDERER DIRECTLY, not whichever surface happens to be open.
   This control's subject is the ORDER of the offer list and the pin at the top
   of it - "a property of the LIST, not of where the list is drawn", as the
   note above already says. Since the hardpoint-picker order, a mount with a
   hull marker opens the DOCKED picker, which deliberately shows five rows
   (H3): best 4 by the active sort plus the fitted part. Reading that surface
   would test H3's cap instead of the sort, and would make `order.length > 40`
   fail on a page that is working exactly as specified.
   pickerHTML() is the function that builds the full list, and it is unchanged
   by that order - so the assertions below keep their full strength rather than
   being relaxed to fit a surface they were never about. */
const openPicker = (slotId) =>
  H.g("pickerHTML(ship().slots.find(x=>x.id===" + JSON.stringify(slotId) + "))");

/* E10 RENAMED THESE. `best` is gone - the site does not decide what is best
   - and `quiet` split into ir and em. The old names silently fell through
   to the headline axis, so `best` and `light` produced the SAME order and
   the assertion below failed on a page that was working. */
for (const mode of ["head", "ir", "em", "mass"]) {
  run(`sort=${JSON.stringify(mode)};sel={slot:${JSON.stringify(turret.id)}};`
    + `editing="A";renderAll();`);
  const pick = openPicker(turret.id);
  const order = [...pick.matchAll(/data-part="([^"]+)"/g)].map((m) => m[1]);
  record(order.length > 40, `the ${mode} list rendered its parts`,
    `${order.length} rendered`);
  record(order[0] === fittedKey,
    `sorted by ${mode}, the FIRST entry is the fitted part - `
    + `"${(PARTS[fittedKey] || {}).n}"`,
    order.length ? `first was ${(PARTS[order[0]] || {}).n || order[0]}` : "none");
  record(order.filter((k) => k === fittedKey).length === 1,
    `and it appears exactly ONCE, not pinned and listed again (${mode})`,
    `${order.filter((k) => k === fittedKey).length} times`);
  record(/class="pinlabel"/.test(pick),
    `and it is labelled as what is currently fitted, in words (${mode})`);
}

/* The sort still governs the rest - otherwise "pinned first" could be a list
   that stopped sorting altogether. */
{
  const seen = {};
  for (const mode of ["head", "mass"]) {
    run(`sort=${JSON.stringify(mode)};sel={slot:${JSON.stringify(turret.id)}};`
      + `renderAll();`);
    /* EVERYTHING below the pinned entry, not the first handful: two sorts can
       agree on their opening rows and still be different orders, and a check
       that only looked at five would call that a failure. */
    seen[mode] = [...openPicker(turret.id).matchAll(/data-part="([^"]+)"/g)]
      .map((m) => m[1]).slice(1).join(",");
  }
  record(seen.head !== seen.mass,
    "and the sort still governs everything below the pinned entry - the "
    + "headline figure and Lightest are not the same order");
}

/* ------------------------ 2. THE ROWS STAY. ONE OPENS. THE OTHERS CLOSE. --- */
console.log("\n--- 2. the rows stay, and only one is open ---");
/* DRIVEN WITH INTERNAL COMPONENTS. After B3 a hull-mounted port's picker is a
   panel over the model, so the inline container is the home of exactly the
   things with no honest position on a hull - power plants, coolers, shields.
   Those are the rows this half is about. B3's own control asserts the other
   side of the same split. */
run(`sel=null;renderAll();`);
const rowIds = [...el("colA").innerHTML.matchAll(/data-slot="([^"]+)"/g)]
  .map((m) => m[1]);
const inlineIds = rowIds.filter((id) => g("pickerHome")(
  SH.slots.find((s) => s.id === id)) === "inline");
record(rowIds.length === swap.length,
  `the column lists all ${swap.length} ports that can be changed`,
  `${rowIds.length}`);
record(inlineIds.length > 5,
  "and enough of them are internal components to open a fifth inline",
  `${inlineIds.length} of ${rowIds.length} open inline`);
state.notes.push(`inline half driven with ${inlineIds.length} internal `
  + `components; the other ${rowIds.length - inlineIds.length} rows are `
  + `hull-mounted and open over the stage (B3)`);

const clickRow = (id) => dispatch([".slot[data-slot]"],
  { dataset: { slot: id, col: "A" } });

const threw1 = clickRow(inlineIds[0]);
record(!threw1, "clicking row 1 does not throw", threw1 || "");
{
  const col = el("colA").innerHTML;
  const still = [...col.matchAll(/data-slot="([^"]+)"/g)].map((m) => m[1]);
  const missing = rowIds.filter((id) => !still.includes(id));
  record(missing.length === 0,
    "rows 2..n are STILL THERE with row 1 open - the column is not taken over",
    missing.length ? `${missing.length} vanished` : "");
  record(el("colA").hidden === false, "and the column itself is not hidden");
  record((col.match(/class="inlinepick"/g) || []).length === 1,
    "exactly one picker is open",
    `${(col.match(/class="inlinepick"/g) || []).length}`);
  record(col.includes(`data-for="${inlineIds[0]}"`),
    "and it is the one belonging to row 1");
  record(!/id="pickback"|&larr; Components/.test(col),
    "there is no ← Components button - the list never went anywhere");
}

/* THE NEGATIVE HALF, and the order names it: without it, a build that opens
   every row also passes everything above. */
const threw5 = clickRow(inlineIds[4]);
record(!threw5, "clicking row 5 does not throw", threw5 || "");
{
  const col = el("colA").innerHTML;
  record(!col.includes(`data-for="${inlineIds[0]}"`),
    "row 1's picker is GONE - opening a second closes the first");
  record(col.includes(`data-for="${inlineIds[4]}"`),
    "and row 5's is open in its place");
  record((col.match(/class="inlinepick"/g) || []).length === 1,
    "still exactly one open, fleet-wide invariant on this page",
    `${(col.match(/class="inlinepick"/g) || []).length}`);
}

/* Closing is going back, in place. */
{
  const threw = dispatch(["#pickclose"]);
  record(!threw, "the close control does not throw", threw || "");
  const col = el("colA").innerHTML;
  record(!/class="inlinepick"/.test(col) && el("cc-panel").hidden === true,
    "closing leaves no picker open, in any home");
  record([...col.matchAll(/data-slot="([^"]+)"/g)].map((m) => m[1]).length
    === swap.length,
    "and every row is still there - closing is going back, in place");
}

/* ------------------------------------ 3. FLEET: the invariant everywhere --- */
console.log("\n--- 3. exactly one picker, in exactly one home, on every hull ---");
{
  let checked = 0, bad = 0;
  const offenders = [];
  for (const k of Object.keys(SHIPS)) {
    const sh = SHIPS[k];
    const ed = (sh.slots || []).filter((s) => s.fit);
    if (!ed.length) continue;
    openShip(k);
    run(`sel={slot:${JSON.stringify(ed[0].id)}};renderAll();`);
    /* ONE PICKER, IN ONE HOME. Counting only the inline container would have
       scored every hull-mounted port as zero after B3 - so this counts the
       inline containers AND the stage panel together, and requires exactly
       one across both. Two homes open at once is the failure this catches. */
    const inlineN = (el("colA").innerHTML.match(/class="inlinepick"/g) || []).length;
    const panelN = el("cc-panel").hidden ? 0 : 1;
    const paneN = /data-part=|class="fixedpanel"/
      .test(el("picker").innerHTML || "") ? 1 : 0;
    const n = inlineN + panelN + paneN;
    checked++;
    if (n !== 1) { bad++; if (offenders.length < 6) offenders.push(`${k}:${n}`); }
  }
  console.log(`\n    hulls checked ${checked}`);
  record(checked > 300, "every hull with an editable port was checked",
    `${checked}`);
  record(bad === 0,
    "selecting a port opens exactly ONE picker, in ONE home, on every one of them",
    bad ? `${bad} wrong, e.g. ${offenders.join(", ")}` : "");
  state.notes.push(`fleet: ${checked} hulls, exactly one picker open in one `
    + `home when a port is selected`);
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_PIN || MUT_MULTI)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
