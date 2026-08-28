/**
 * B3 acceptance: WEAPONS ARE CHOSEN ON THE MODEL. INTERNAL COMPONENTS ARE NOT.
 *
 * RULE16: UNPROVEN - the load-bearing assertion compares the marker entrance
 * against the list entrance and requires byte-identical panels. Both are
 * produced by the page, so it proves the two routes agree with EACH OTHER
 * and cannot prove either is right. The rule deciding which home a port
 * opens in is stated here and driven across the whole fleet, and that is
 * the independent half.
 *
 * Sleven's own scoping is the rule for the item:
 *
 *   "the guns and missiles and stuff, and the gimbals and stuff, that can go
 *    on the hardpoint attachments with its own specialized place... I
 *    understand the components can't go in there, we don't have a proper way
 *    to hardpoint them."
 *
 * So the split is whether the thing is PHYSICALLY ON THE HULL, answered by the
 * only honest test available - whether the model carries a marker for that
 * port. A port with a marker has a position. A power plant does not, and this
 * project has already ruled that it gets a menu rather than an invented
 * marker.
 *
 *   marker  -> a panel over the model stage, anchored near the dot
 *   no marker -> the inline picker under its row, where B2 put it
 *
 * ONE SELECTION PATH, TWO ENTRANCES. selectPort() is documented as "THE ONE
 * PLACE A PORT GETS SELECTED. Both routes come here." The assertion that
 * defends it is not that the two routes both do something - it is that they
 * produce the IDENTICAL result, byte for byte and position for position.
 *
 * WHAT THIS CAN AND CANNOT PROVE ABOUT GEOMETRY. There is no browser here, so
 * the stage is a stated 960x540 stub and nothing below measures a real
 * viewport. What IS proven is the arithmetic: panelPlacement() is a pure
 * function and it is driven directly with numbers chosen to make it flip, to
 * pin, and to clamp - including a stage too narrow for any placement at all.
 * Geometry reasoned about in a browser is geometry nobody ever checks.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-cover     placement returns the marker's own position, so the
 *                      panel sits on top of the dot it belongs to.
 *   --mutate-internal  every port is treated as hull-mounted, so power plants
 *                      get a panel over the model they have no place on.
 *   --self-test        inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_stage_panel.mjs
 *        [--self-test] [--mutate-cover] [--mutate-internal]
 */

import { loadPage, reporter } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_COVER = process.argv.includes("--mutate-cover");
const MUT_INTERNAL = process.argv.includes("--mutate-internal");

const mutate = [];
if (MUT_COVER) {
  mutate.push([/return \{left: Math\.round\(left\), top: Math\.round\(top\), side: side\};/,
               "return {left: Math.round(px), top: Math.round(py), side: side};"]);
  console.log("*** MUTATED: the panel is placed AT the marker, covering the "
    + "dot that was clicked. Something below MUST notice. ***");
}
if (MUT_INTERNAL) {
  mutate.push([/if\(onStage\(slot\)\) return "stage";/,
               'return "stage";']);
  console.log("*** MUTATED: every port is treated as hull-mounted - power "
    + "plants get a panel over the model. Something below MUST notice. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, MARKS, el, openShip, g, run, dispatch, key, PARTS,
        flushTimers } = H;

const STAGE_W = 960, STAGE_H = 540;   // what the harness's stub reports

/* ------------------------------------------- 0. the placement arithmetic */
console.log("--- 0. panelPlacement, driven with numbers chosen to break it ---");
{
  const place = g("panelPlacement");
  const W = g("PANEL_W"), GAP = g("PANEL_GAP");
  record(typeof place === "function", "the placement is a pure function");
  record(W > 100 && GAP > 0, `the panel box is declared once - ${W}px, ${GAP}px gap`);

  /* RE-BASELINED 2026-08-27 BY THE SESSION THAT CHANGED THE RULE (C1).
     These four asserted the OLD rule - "prefer the right, flip left only when
     there is no room, and never cover the marker" - and they were correct
     about it.

     SLEVEN CHANGED THE RULE, in his own words: *"if I'm looking straight at
     the ship and it would be the ship's right wing but it'd be on my left, it
     should open the menu on the left side of the screen... I really want the
     ship to stop shifting when we open a thing."* The panel follows the dot's
     SCREEN side now, which is what removed the reason the hull was being
     panned aside on every click.

     THE "NEVER COVER THE MARKER" ASSERTION GOES WITH IT, and deliberately:
     that rule is why the panel always went to the far side, which is why the
     ship had to move. The panel is glass and the hull now renders at
     `hullAlpha`, so a dot behind it is dimmed rather than lost.

     WHAT IS ASSERTED INSTEAD IS THE NEW RULE, and it still fails in both
     directions - a panel that ignored the side, or one that drifted off an
     edge, is caught here. */
  const a = place(100, 270, STAGE_W, STAGE_H, W, 340, GAP);
  record(a.side === "left",
    "a marker on the LEFT of the stage opens the panel on the LEFT",
    JSON.stringify(a));
  record(a.left >= 0 && a.left + W <= STAGE_W,
    "and the panel is fully on the stage", `${a.left}..${a.left + W}`);

  const b = place(STAGE_W - 40, 270, STAGE_W, STAGE_H, W, 340, GAP);
  record(b.side === "right",
    "a marker on the RIGHT of the stage opens the panel on the RIGHT",
    JSON.stringify(b));
  record(b.left + W <= STAGE_W && b.left >= 0,
    "and that one is fully on the stage too", `${b.left}..${b.left + W}`);

  /* THE HINGE, asserted so a rule that always answered one side would fail.
     Either side of the midpoint must give a DIFFERENT answer. */
  const l = place(Math.floor(STAGE_W/2) - 1, 270, STAGE_W, STAGE_H, W, 340, GAP);
  const r = place(Math.floor(STAGE_W/2) + 1, 270, STAGE_W, STAGE_H, W, 340, GAP);
  record(l.side === "left" && r.side === "right",
    "the side flips across the middle of the stage - it is not a constant",
    `${l.side} / ${r.side}`);
  record(l.left !== r.left,
    "and the two sides are different places", `${l.left} vs ${r.left}`);

  /* A stage narrower than the panel cannot honour the side; it must still
     stay on the stage rather than overflowing. */
  const narrow = place(20, 270, Math.round(W * 0.8), STAGE_H, W, 340, GAP);
  record(narrow.left >= 0, "on a stage narrower than the panel it stays put",
    `${narrow.left}`);

  /* Clamped vertically at both ends. */
  const top = place(100, 5, STAGE_W, STAGE_H, W, 340, GAP);
  record(top.top >= 0, "a marker near the top does not push it off the top",
    `${top.top}`);
  const bot = place(100, STAGE_H - 5, STAGE_W, STAGE_H, W, 340, GAP);
  record(bot.top + 340 <= STAGE_H,
    "and one near the bottom does not push it off the bottom",
    `${bot.top + 340} of ${STAGE_H}`);

  /* A stage too narrow for ANY placement. It must still land inside the box
     rather than returning a negative or an overflow - the honest fallback. */
  const tiny = place(150, 100, 300, 200, W, 340, GAP);
  record(tiny.left >= 0 && tiny.left + W >= 0,
    "a stage narrower than the panel still yields a placement inside it, "
    + "rather than a negative offset",
    JSON.stringify(tiny));
}

/* ------------------------------------------------ 1. a marker opens a panel */
console.log("\n--- 1. clicking a marker opens a panel OVER THE STAGE ---");
const key400i = Object.keys(SHIPS).find(
  (k) => /400i/i.test(SHIPS[k].n || "") && /origin/i.test(SHIPS[k].m || ""));
record(!!key400i, "the Origin 400i is in the ship table");
openShip(key400i);

const marks = MARKS[key400i] || [];
const swapMark = marks.find((m) => {
  const s = SHIPS[key400i].slots.find((x) => x.p === m[0]);
  return s && s.fit;
});
record(!!swapMark, "it has a swappable port with a marker on the hull");
const slot = SHIPS[key400i].slots.find((x) => x.p === swapMark[0]);
state.notes.push(`driven with ${SHIPS[key400i].n}, port `
  + `${H.portName(slot)} (${slot.id})`);

/* V2: A DOT ADDRESSES A MOUNT NOW, so this clicks the way a person does -
   the dot, then the weapon if the mount asked which one. The assertion below
   is unchanged: this port's own panel must open, anchored where the dot is. */
const clickMarker = (portId) => {
  const root = String(portId).split(".")[0];
  const rep = H.g(`(mountOf(shipId, ${JSON.stringify(portId)})||{}).p`) || portId;
  const btn = {
    tagName: "BUTTON", dataset: { mount: root, port: rep },
    closest: (s) => (s === "#cc-marks button[data-mount]"
                     || s === "#cc-marks button[data-port]") ? btn : null,
  };
  let threw = null;
  for (const fn of H.clickHandlers) {
    try { fn({ target: btn, preventDefault() {} }); } catch (e) { threw = e.message; }
  }
  const opened = el("cc-panel");
  if (!opened.hidden && (opened.innerHTML || "").includes("data-mountport")) {
    const row = {
      tagName: "BUTTON", dataset: { mountport: portId },
      closest: (s) => (s === "#cc-panel button[data-mountport]" ? row : null),
    };
    for (const fn of H.clickHandlers) {
      try { fn({ target: row, preventDefault() {} }); } catch (e) { threw = e.message; }
    }
  }
  return threw;
};

const panelState = () => {
  const p = el("cc-panel");
  return {
    hidden: p.hidden,
    html: p.innerHTML || "",
    left: parseInt(p.style.left, 10),
    top: parseInt(p.style.top, 10),
    side: p["data-side"],
    forSlot: p["data-for"],
    anchor: p["data-anchor"],
  };
};

run(`sel=null;renderAll();`);
record(el("cc-panel").hidden === true, "nothing is open to begin with");
const threwMark = clickMarker(swapMark[0]);
record(!threwMark, "clicking the marker does not throw", threwMark || "");
const viaMark = panelState();
const selViaMark = JSON.parse(g("JSON.stringify(sel)") || "null");

record(viaMark.hidden === false, "the panel is OPEN");
record(viaMark.forSlot === slot.id, "and it belongs to that port",
  String(viaMark.forSlot));
record(/data-part=/.test(viaMark.html),
  "with the port's own picker inside it, not an empty box");
record(!el("colA").innerHTML.includes('class="inlinepick"'),
  "and NOTHING opened inline - the picker is over the model, not in the list");

/* A COMPUTED POSITION, INSIDE THE STAGE. Read off the element the page wrote,
   not recomputed here - a control that redid the sum would agree with itself. */
const W = g("PANEL_W");
record(Number.isFinite(viaMark.left) && Number.isFinite(viaMark.top),
  "it carries a computed position, in pixels",
  `${viaMark.left},${viaMark.top}`);
record(viaMark.left >= 0 && viaMark.left + W <= STAGE_W,
  `and that position is inside the ${STAGE_W}x${STAGE_H} stage horizontally`,
  `${viaMark.left}..${viaMark.left + W}`);
record(viaMark.top >= 0 && viaMark.top <= STAGE_H,
  "and inside it vertically", `${viaMark.top}`);

/* AND IT DOES NOT COVER ITS OWN MARKER. */
{
  const [ax] = String(viaMark.anchor).split(",").map(Number);
  record(Number.isFinite(ax), "the panel records the anchor it was placed from",
    String(viaMark.anchor));
  record(ax < viaMark.left || ax > viaMark.left + W,
    "and the marker is NOT underneath it - the dot you clicked is still there",
    `marker x=${ax}, panel ${viaMark.left}..${viaMark.left + W}`);
}

/* ------------------------------- 2. THE ROW OPENS THE SAME PANEL, SAME PLACE */
console.log("\n--- 2. the row is the second entrance to the SAME panel ---");
run(`sel=null;renderAll();`);
record(el("cc-panel").hidden === true, "closed again before the second route");
const threwRow = dispatch([".slot[data-slot]"],
  { dataset: { slot: slot.id, col: "A" } });
record(!threwRow, "clicking the port's left-column row does not throw",
  threwRow || "");
const viaRow = panelState();
const selViaRow = JSON.parse(g("JSON.stringify(sel)") || "null");

record(viaRow.hidden === false, "the row opens the panel too");
record(viaRow.html === viaMark.html,
  "with the IDENTICAL content - the same bytes, not a second mechanism that "
  + "happens to look alike",
  `${viaRow.html.length} vs ${viaMark.html.length} chars`);
record(viaRow.left === viaMark.left && viaRow.top === viaMark.top,
  "in the IDENTICAL place",
  `${viaRow.left},${viaRow.top} vs ${viaMark.left},${viaMark.top}`);
record(viaRow.forSlot === viaMark.forSlot, "for the identical port");
record(JSON.stringify(selViaRow) === JSON.stringify(selViaMark)
  && selViaMark !== null,
  "and one selection state describes both",
  `${JSON.stringify(selViaRow)} vs ${JSON.stringify(selViaMark)}`);
state.notes.push("marker and row produce byte-identical panels at identical "
  + "coordinates - one selection path, two entrances");

/* ---------------------------- 3. AN INTERNAL COMPONENT NEVER LEAVES THE LIST */
console.log("\n--- 3. an internal component opens in the LIST, never on the model ---");
{
  const shipKey = Object.keys(SHIPS).find((k) => {
    const sh = SHIPS[k];
    return (sh.slots || []).some((s) => s.fit && s.t === "pow")
      && (MARKS[k] || []).length;
  });
  record(!!shipKey, "found a hull with a power plant AND hull markers - so "
    + "this is not passing merely because the ship has no model");
  openShip(shipKey);
  const pow = SHIPS[shipKey].slots.find((s) => s.fit && s.t === "pow");
  record(!!pow, "the power plant port is editable", pow ? pow.id : "");
  record(g("onStage")(pow) === false,
    "and the model carries no marker for it - it has no honest position");

  const threw = dispatch([".slot[data-slot]"],
    { dataset: { slot: pow.id, col: "A" } });
  record(!threw, "clicking its row does not throw", threw || "");
  record(el("cc-panel").hidden === true,
    "NO panel opened over the model - a power plant is not on the hull");
  record(el("colA").innerHTML.includes(`data-for="${pow.id}"`),
    "and its picker opened inline, in the list, under its own row");
  state.notes.push(`internal component ${pow.id} on ${SHIPS[shipKey].n} opens `
    + `inline and never over the stage`);
}

/* ------------------------------------------- 4. ESCAPE, AND THE BACKGROUND */
console.log("\n--- 4. Escape closes it, and so does the model background ---");
openShip(key400i);
{
  clickMarker(swapMark[0]);
  record(el("cc-panel").hidden === false, "panel open");
  const threw = key("Escape");
  record(!threw, "Escape does not throw", threw || "");
  record(el("cc-panel").hidden === true, "Escape closes it");
  record(g("sel") === null, "and clears the selection", JSON.stringify(g("sel")));
}
{
  clickMarker(swapMark[0]);
  record(el("cc-panel").hidden === false, "panel open again");
  /* A click on the stage that is NOT a marker and NOT inside the panel. */
  const threw = dispatch(["#cc-stage"]);
  record(!threw, "clicking the model background does not throw", threw || "");
  /* P1e DEFERS THE RENDER ON PURPOSE - it clears the selection during the
     click and calls setTimeout(renderAll, 0), so that rebuilding the DOM does
     not happen underneath the branches that have not run yet. Asserting
     straight after the click asked the page a question it had not answered
     yet; until 2026-08-27 the harness threw deferred callbacks away entirely,
     so this read as a page defect for as long as P1e has existed.
     The selection is checked FIRST because that part IS synchronous - if the
     click did nothing at all, this fails here rather than after a flush that
     had nothing to run. */
  record(g("sel") === null && g("mountSel") === null,
    "the click clears the selection during the event, before any render",
    JSON.stringify([g("sel"), g("mountSel")]));
  const ran = flushTimers();
  record(ran > 0, "and it DEFERRED a render rather than doing nothing",
    `${ran} deferred callback(s) ran`);
  record(el("cc-panel").hidden === true, "and it closes the panel");
}
{
  /* THE NEGATIVE HALF: a click INSIDE the panel must not close it, or the
     picker would shut the instant anybody tried to use it. */
  clickMarker(swapMark[0]);
  const threw = dispatch(["#cc-stage", "#cc-panel"]);
  record(!threw, "clicking inside the panel does not throw", threw || "");
  record(el("cc-panel").hidden === false,
    "and does NOT close it - otherwise the picker would shut on first use");
}

/* ------------- 4b. THE SHIP DOES NOT MOVE WHEN A PANEL OPENS -------------
   WAS: "E4: the stage gives up width to the panel and re-centres."

   That is no longer true and the section is rewritten rather than deleted,
   because the reason it changed matters. Sleven, on the deployed page:
   *"when you click a hard point, the whole ship shifts... I really want the
   ship to stop shifting when we open a thing."*

   E4 was solving a real problem - a hull left as a sliver beside a panel -
   and it solved it by moving the thing the person is looking at. The panel
   follows the marker's screen side now, so nothing needs to be moved out of
   its way.

   WHAT IS ASSERTED HERE NOW IS THE OPPOSITE OF WHAT IT USED TO ASSERT: the
   viewer is still TOLD how much is covered, because callers pass it and a
   reader may want it - and the camera must not respond. */
console.log("\n--- the panel opens and the ship stays exactly where it was ---");
openShip(key400i);
{
  run("sel=null;renderAll();");
  record(g("_view").obstruction() === 0,
    "with nothing open, the stage is not obstructed",
    String(g("_view").obstruction()));

  clickMarker(swapMark[0]);
  const obs = g("_view").obstruction();
  const W = g("PANEL_W");
  record(obs > 0, "opening a panel tells the viewer the stage is covered",
    String(obs));
  record(Math.abs(obs - W / STAGE_W) < 1e-6,
    `and by the right amount - the panel's own width over the stage's `
    + `(${W}/${STAGE_W})`, String(obs));

  /* THE LOAD-BEARING ONE. The camera's look-at point before and after a
     marker is clicked must be IDENTICAL. If anybody reinstates the pan - or
     makes setObstruction reframe again - this is what says so.

     Reported as NOT PERFORMED rather than passed if the harness's viewer has
     no controls to read, because "could not look" and "did not move" are
     different statements. */
  const tgtBefore = g("_view").controls && g("_view").controls.target
    ? JSON.stringify(["x","y","z"].map(k => g("_view").controls.target[k])) : null;
  if (tgtBefore === null) {
    console.log("     NOT PERFORMED - this harness's viewer exposes no camera "
      + "controls, so 'the ship did not move' could not be measured here. "
      + "Reported, never passed.");
  } else {
    clickMarker(swapMark[0]);
    const tgtAfter = JSON.stringify(
      ["x","y","z"].map(k => g("_view").controls.target[k]));
    record(tgtAfter === tgtBefore,
      "*** the camera's target is UNCHANGED - the ship did not shift ***",
      `before ${tgtBefore} after ${tgtAfter}`);
  }

  /* And the panel is on the same side as the marker it belongs to, measured
     on a real selection rather than on the arithmetic alone. */
  const p = panelState();
  const [ax] = String(p.anchor).split(",").map(Number);
  const expect = (ax <= STAGE_W / 2) ? "left" : "right";
  record(p.side === expect,
    "and the panel opened on the marker's own side of the stage",
    `marker x=${ax} of ${STAGE_W}, panel ${p.side}, expected ${expect}`);
  state.notes.push(`panel covers ${(obs * 100).toFixed(1)}% of the stage and `
    + `the hull does not move; marker at x=${ax} opened the panel ${p.side}`);

  run("sel=null;renderAll();");
  record(g("_view").obstruction() === 0,
    "and closing it gives the whole stage back - the NEGATIVE half, without "
    + "which a build that never un-obstructs also passes",
    String(g("_view").obstruction()));
}

/* --------------------------------- 5. THE SPLIT, ACROSS THE WHOLE FLEET --- */
console.log("\n--- 5. every port opens in exactly the home its marker decides ---");
{
  let checked = 0, bad = 0;
  const offenders = [];
  for (const k of Object.keys(SHIPS)) {
    const sh = SHIPS[k];
    const ed = (sh.slots || []).filter((s) => s.fit);
    if (!ed.length || !(MARKS[k] || []).length) continue;
    openShip(k);
    for (const s of ed) {
      run(`sel={slot:${JSON.stringify(s.id)}};renderAll();`);
      const onStage = g("onStage")(s);
      const panelOpen = el("cc-panel").hidden === false;
      const inlineOpen = el("colA").innerHTML.includes(`data-for="${s.id}"`);
      checked++;
      if (panelOpen !== onStage || inlineOpen === onStage) {
        bad++;
        if (offenders.length < 6) offenders.push(`${k}/${s.id}`);
      }
    }
  }
  console.log(`\n    port selections driven ${checked}`);
  record(checked > 2000, "the sweep drove thousands of selections, not a few",
    `${checked}`);
  record(bad === 0,
    "a port with a marker ALWAYS opens over the stage and one without ALWAYS "
    + "opens in the list - no exceptions across the fleet",
    bad ? `${bad} wrong, e.g. ${offenders.join(", ")}` : "");
  state.notes.push(`fleet: ${checked} port selections, every one in the home `
    + `its marker decides`);
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_COVER || MUT_INTERNAL)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
