/**
 * H1f: the look controls exist, are closed by default, and every one of them
 * reaches the viewer.
 *
 * Sleven on the first pass: "It looks good for the first pass, but it's
 * definitely not where I want it... I don't see that." The renderer landed and
 * nothing a person can press did.
 *
 * TWO CLAIMS, TWO HARNESSES, AND THEY ARE NOT THE SAME CLAIM.
 *   this file                 the PAGE builds the controls and calls the
 *                             viewer when they are pressed
 *   _verify_holo_render.mjs   the VIEWER's passes actually change, pairwise
 *                             across all six styles, against the real module
 * A control that only checked the first would pass on a viewer that ignored
 * every call; one that only checked the second would pass on a page with no
 * buttons. The first pass shipped exactly that second failure.
 *
 * WHERE IT GOES. The prototype's panel is a permanent right-hand column; P7
 * measured this page at 1080 of 1080 and 768 of 768 and there is no room for
 * one. So it floats over the stage - and "costs zero page height" is asserted
 * from the CSS rather than believed.
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-open     the panel starts open, which is the disclosure rule
 *                     inverted and would cover the model on first sight.
 *   --mutate-inert    the buttons render but never call the viewer - the
 *                     "sets a class and nothing happens" build.
 *   --self-test       inverts every expectation.
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_look_panel.mjs
 *        [--self-test] [--mutate-open] [--mutate-inert]
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { loadPage, reporter, SRC } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_OPEN = process.argv.includes("--mutate-open");
const MUT_INERT = process.argv.includes("--mutate-inert");

const mutate = [];
if (MUT_OPEN) {
  mutate.push([/let tuneShown=false;/, "let tuneShown=true;"]);
  console.log("*** MUTATED: the panel starts OPEN, covering the model. ***");
}
if (MUT_INERT) {
  mutate.push([/if\(ts&&_view\)\{ _view\.setStyle\(ts\.dataset\.style\);/,
               "if(ts&&_view){ /* inert */"]);
  console.log("*** MUTATED: the style buttons render and call nothing. ***");
}

const H = loadPage({ mutate });
const { record, finish, state } = reporter(SELFTEST);
const { SHIPS, el, openShip, g, dispatch, key } = H;

const shipKey = Object.keys(SHIPS).find(
  (k) => /avenger stalker/i.test(SHIPS[k].n || ""));
openShip(shipKey);
const panel = () => el("cc-tune-panel");
const html = () => panel().innerHTML || "";

/* ------------------------------------------- 1. CLOSED BY DEFAULT ------- */
console.log("--- 1. closed by default ---");
record(panel().hidden === true,
  "the look panel is CLOSED when a ship opens - progressive disclosure, the "
  + "page's simplest true state first", String(panel().hidden));
record(!html(),
  "and it has rendered nothing at all, so it costs nothing to have");

/* ------------------------------------------- 2. IT OPENS, WITH EVERYTHING */
console.log("\n--- 2. one control opens it, and everything is in it ---");
const threw = dispatch(["#cc-tune"]);
record(!threw, "the opener does not throw", threw || "");
record(panel().hidden === false, "the panel opens");
const h = html();
const count = (re) => (h.match(re) || []).length;
record(count(/data-style=/g) === 6,
  "ALL SIX styles are present - C1's three-not-six trim is overturned",
  String(count(/data-style=/g)));
record(count(/data-colour=/g) === 5, "five colours",
  String(count(/data-colour=/g)));
/* FOUR SINCE 2026-08-27. The fourth is `hullAlpha`, added on Sleven's own
   request - *"is there any way we can make it a little bit more see through,
   a little bit more transparent"*. The count is asserted by NAME as well as by
   number, so a slider silently disappearing still fails here rather than being
   masked by a new one arriving. */
record(count(/data-slider=/g) === 4,
  "and the four sliders - line intensity, line detail, glow, see-through",
  String(count(/data-slider=/g)));
record(/data-slider="lineInt"/.test(h) && /data-slider="detail"/.test(h)
  && /data-slider="glow"/.test(h) && /data-slider="hullAlpha"/.test(h),
  "and each of the four is the one it is supposed to be, by name");
record(/data-view="scan"/.test(h),
  "scanlines are a control, which Sleven asked for by name");
record(/data-view="grid"/.test(h) && /data-view="spin"/.test(h),
  "along with the grid and auto-spin");
for (const s of ["panel", "solidlines", "solid", "hull", "wire", "points"]) {
  record(new RegExp(`data-style="${s}"`).test(h), `  style: ${s}`);
}
state.notes.push(`the panel carries 6 styles, 5 colours, 4 sliders and 3 view `
  + `toggles`);

/* ------------------------------------- 3. THE DEFAULTS SLEVEN PINNED ---- */
console.log("\n--- 3. the pinned default state ---");
record(g("_view").style === "solidlines",
  "the ship opens on Solid + lines", g("_view").style);
record(g("_view").colour() === 0xffb545,
  "in AMBER, not cyan - the deployed first pass did not honour this",
  "0x" + g("_view").colour().toString(16));
record(g("_view").scanlines() === false,
  "with scanlines off but available");
record(g("_view").gridOn() === true, "and the grid on");

/* ------------------------------- 4. EVERY CONTROL REACHES THE VIEWER ---- */
console.log("\n--- 4. every control reaches the viewer ---");
g("_view").calls.length = 0;
dispatch(["#cc-tune-panel button[data-style]"], { dataset: { style: "wire" } });
dispatch(["#cc-tune-panel button[data-colour]"],
  { dataset: { colour: "8257972" } });
dispatch(["#cc-tune-panel button[data-view]"], { dataset: { view: "scan" } });
dispatch(["#cc-tune-panel button[data-view]"], { dataset: { view: "grid" } });
const calls = g("_view").calls.slice();
console.log("    calls: " + JSON.stringify(calls));
record(calls.some((c) => c === "style:wire"),
  "a style button calls setStyle on the viewer");
record(calls.some((c) => c.startsWith("colour:")),
  "a swatch calls setColour");
record(calls.some((c) => c.startsWith("scan:")),
  "the scanlines toggle calls setScanlines");
record(calls.some((c) => c.startsWith("grid:")), "the grid toggle calls setGrid");
record(calls.filter((c) => c === "remember").length >= 4,
  "and every one of them is remembered for the session, so a person who sets "
  + "amber wireframe does not re-set it on the next ship",
  `${calls.filter((c) => c === "remember").length} remembers`);

/* THE SLIDERS, which are input events rather than clicks. */
g("_view").calls.length = 0;
for (const [id, k] of [["tune-int", "lineInt"], ["tune-det", "detail"],
                       ["tune-glo", "glow"], ["tune-alpha", "hullAlpha"]]) {
  H.clickHandlers.length + 0;   /* no-op, keeps the shape obvious */
  const node = { dataset: { slider: k }, value: k === "detail" ? "70" : "150",
                 closest: (s) => (s === "#cc-tune-panel input[data-slider]"
                                  ? node : null) };
  for (const fn of (H.inputHandlers || [])) {
    try { fn({ target: node }); } catch (e) { /* reported below */ }
  }
}
record((H.inputHandlers || []).length > 0,
  "the page listens for slider input at all",
  `${(H.inputHandlers || []).length} handlers`);
const sc = g("_view").calls.filter((c) => c.startsWith("slider:"));
record(sc.length === 4, "and all four sliders reach the viewer",
  JSON.stringify(sc));

/* ------------------------------------------- 5. IT CLOSES ---------------- */
console.log("\n--- 5. Escape and a click outside close it ---");
/* The opener TOGGLES, and section 4 left the panel open. Assert that rather
   than assuming a state - the first version of this block clicked the opener
   expecting to open it and closed it instead. */
record(panel().hidden === false, "section 4 left it open");
dispatch(["#cc-tune"]);
record(panel().hidden === true, "the opener toggles it shut again");
dispatch(["#cc-tune"]);
record(panel().hidden === false, "and back open");
key("Escape");
record(panel().hidden === true, "Escape closes it");
dispatch(["#cc-tune"]);
record(panel().hidden === false, "reopened again");
dispatch(["#cc-stage"]);
record(panel().hidden === true,
  "and a click on the stage outside it closes it too");

/* ------------------------------- 6. ZERO PAGE HEIGHT, FROM THE CSS ------ */
console.log("\n--- 6. it floats: open must not exceed closed ---");
{
  const page = readFileSync(join(SRC, "loadout.src.html"), "utf-8");
  const css = (page.match(/<style>([\s\S]*?)<\/style>/) || ["", ""])[1]
    .replace(/\s+/g, "");
  record(/#cc-tune-panel\{position:absolute/.test(css),
    "the panel is absolutely positioned, so it is out of the page's flow");
  record(/#cc-tune\{position:absolute/.test(css),
    "and so is the control that opens it");
  record(/#cc-tune-panel\{[^}]*max-height:calc\(100%-\d+px\)/.test(css),
    "and it is bounded by the STAGE's height, so it cannot grow past it");
  record(/height:calc\(100vh-var\(--chrome\)\)/.test(css),
    "while the grid is still sized off the viewport - the page cannot grow");
  state.notes.push("page height with the panel OPEN equals CLOSED: it is "
    + "position:absolute inside #cc-stage and bounded by the stage height, so "
    + "it is out of flow by construction rather than by measurement");
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_OPEN || MUT_INERT)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
