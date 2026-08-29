/**
 * B4 acceptance: THE PAGE OPENS CALM, AND REMEMBERS THE CHOICE.

 *
 * RULE16: UNPROVEN - the page's own state is both the subject and the evidence: it
 * is asked whether rotation is running and whether the choice was stored.
 * The independent half is the SEQUENCE the control imposes - open cold,
 * stop, reload, open a different ship - which is a series of events the
 * page does not choose and cannot anticipate.
 *
 * Sleven: "the ship just constantly spins." A stop control existed, and that
 * is not the same as opening still - it makes a visitor undo something they
 * never asked for, on every ship, before they can look at the thing they came
 * to see.
 *
 * BOTH HALVES ARE LOAD-BEARING AND THE ORDER SAYS SO. "It does not spin" also
 * passes on a build where spin is BROKEN, so the negative half - a stored
 * preference brings it up spinning - is what separates "off by default" from
 * "off because it does not work".
 *
 * THREE STORAGE WORLDS, all three driven, because "we handled it" is not the
 * same as "we tried it":
 *   none        no sessionStorage at all, which is this harness and also a
 *               page opened as a file:// URL in some browsers
 *   working     seeded with a real value
 *   throwing    storage disabled, which throws on every access - the case a
 *               page falls over on if it reads storage without a guard
 *
 * PROVEN AGAINST KNOWN-BAD INPUT:
 *   --mutate-default   the default goes back to spinning
 *   --mutate-forget    the toggle stops writing the preference
 *   --self-test        inverts every expectation
 * Each must exit non-zero.
 *
 * Usage: node checks/_verify_spin_default.mjs
 *        [--self-test] [--mutate-default] [--mutate-forget]
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";
import { loadPage, reporter, SRC } from "./_loadout_harness.mjs";

const SELFTEST = process.argv.includes("--self-test");
const MUT_DEFAULT = process.argv.includes("--mutate-default");
const MUT_FORGET = process.argv.includes("--mutate-forget");

const mutate = [];
if (MUT_DEFAULT) {
  mutate.push([/let spinOn = storedSpin\(\) === true;/,
               "let spinOn = storedSpin() !== false;"]);
  console.log("*** MUTATED: no stored preference means SPINNING again - the "
    + "state Sleven complained about. Something below MUST notice. ***");
}
if (MUT_FORGET) {
  mutate.push([/function toggleSpin\(\)\{ spinOn=!spinOn; rememberSpin\(spinOn\); applySpin\(\); \}/,
               "function toggleSpin(){ spinOn=!spinOn; applySpin(); }"]);
  console.log("*** MUTATED: the toggle no longer remembers the choice, so "
    + "somebody who wants it spinning re-clicks on every ship. ***");
}

const { record, finish, state } = reporter(SELFTEST);

/* Every world needs its own page: `spinOn` is initialised once, at load, from
   whatever storage said then. Reloading is the only honest way to ask "what
   does this page do when it opens". */
const fresh = (opts) => loadPage({ mutate, ...opts });

const firstShip = (H) => Object.keys(H.SHIPS)
  .find((k) => (H.SHIPS[k].slots || []).length);

/* ------------------------------------- 1. NO STORED PREFERENCE: calm ------ */
console.log("--- 1. first load, no stored preference ---");
{
  const H = fresh({});
  record(H.g("storedSpin")() === null,
    "there is no stored preference to read");
  record(H.g("spinOn") === false,
    "the page opens NOT spinning", String(H.g("spinOn")));

  H.openShip(firstShip(H));
  H.run("applySpin();");
  record(H.g("_view").spinning() === false,
    "_view.spinning() is false - the viewer is actually still, not merely "
    + "labelled still",
    String(H.g("_view").spinning()));
  record(H.el("cc-spin").textContent === "Start spin",
    "and the button reads \"Start spin\"", H.el("cc-spin").textContent);
  record(/Start the ship rotating/.test(H.el("cc-spin").title || ""),
    "with a title that offers to start it", H.el("cc-spin").title);
  state.notes.push("no preference: spinOn=false, viewer still, button reads "
    + "Start spin");
}

/* --------------------- 2. NEGATIVE: a stored preference brings it up spinning */
console.log("\n--- 2. NEGATIVE: stored preference = spinning ---");
{
  const H = fresh({ local: { ccSpin: "1" } });
  record(H.g("storedSpin")() === true, "the stored preference reads as spinning");
  record(H.g("spinOn") === true,
    "the page comes up SPINNING - so \"it does not spin\" above is a default, "
    + "not a broken feature", String(H.g("spinOn")));

  H.openShip(firstShip(H));
  H.run("applySpin();");
  record(H.g("_view").spinning() === true,
    "_view.spinning() is true - the viewer is really turning",
    String(H.g("_view").spinning()));
  record(H.el("cc-spin").textContent === "Stop spin",
    "and the button offers to stop it", H.el("cc-spin").textContent);
  state.notes.push("stored 1: spinOn=true, viewer spinning, button reads "
    + "Stop spin");
}

/* ------------------------- 3. A STORED "off" IS DISTINCT FROM NO PREFERENCE */
console.log("\n--- 3. a stored 'off' is read, not merely defaulted to ---");
{
  const H = fresh({ local: { ccSpin: "0" } });
  record(H.g("storedSpin")() === false,
    "a stored 0 reads as false, not as null",
    String(H.g("storedSpin")()));
  record(H.g("spinOn") === false, "and the page opens still");
  /* The distinction matters: null and false produce the same first frame, and
     collapsing them would make the negative control above unprovable. */
  const none = fresh({});
  record(none.g("storedSpin")() === null && H.g("storedSpin")() === false,
    "\"no preference\" and \"prefers off\" stay distinct, even though they "
    + "look identical on screen");
}

/* ------------------------------- 4. THE CHOICE IS REMEMBERED, FOR REAL ---- */
console.log("\n--- 4. toggling writes the preference ---");
{
  const H = fresh({ local: {} });
  H.openShip(firstShip(H));
  record(H.g("spinOn") === false, "opens still");
  const threw = H.dispatch(["#cc-spin"]);
  record(!threw, "clicking the control does not throw", threw || "");
  record(H.g("spinOn") === true, "it starts spinning");
  record(H.g("_view").spinning() === true, "and the viewer follows");
  /* H1f-2: THE PERSISTENT STORE, NOT THE SESSION ONE. B4 kept this in
     sessionStorage on the argument that a spin preference is about one
     sitting. Sleven reversed that - "as long as possible, really" - so reading
     `H.session` here would now pass against a page that had quietly gone back
     to a session lifetime, which is the thing this line exists to prevent. */
  record(H.local._dump().ccSpin === "1",
    "and the choice is written to the PERSISTENT store",
    JSON.stringify(H.local._dump()));
  record(!H.session._dump().ccSpin,
    "and NOT to the session one - it has to outlive the browser closing",
    JSON.stringify(H.session._dump()));

  H.dispatch(["#cc-spin"]);
  record(H.g("spinOn") === false, "clicking again stops it");
  record(H.local._dump().ccSpin === "0",
    "and that is written too - the memory is not one-way",
    JSON.stringify(H.local._dump()));

  /* AND A NEW PAGE HONOURS IT. Writing to storage proves nothing on its own if
     nothing ever reads it back. Seeded into the PERSISTENT store with the
     session one left empty, which is what a browser looks like the next
     morning. */
  const H2 = fresh({ local: { ccSpin: "1" } });
  record(H2.g("spinOn") === true,
    "a page loaded afterwards honours what was written - the round trip "
    + "closes");
}

/* ---------------------- 5. STORAGE DISABLED MUST NOT BREAK THE PAGE ------- */
console.log("\n--- 5. a browser with storage disabled ---");
{
  let H = null, boom = null;
  try { H = fresh({ sessionThrows: true }); } catch (e) { boom = e.message; }
  record(!boom, "the page still loads when every storage access throws",
    boom || "");
  if (H) {
    record(H.g("spinOn") === false,
      "and falls back to the calm default rather than to nothing");
    let threw = null;
    try { H.openShip(firstShip(H)); H.dispatch(["#cc-spin"]); }
    catch (e) { threw = e.message; }
    record(!threw, "and the control still works, it just cannot remember",
      threw || "");
    record(H.g("spinOn") === true, "the toggle took effect in this session");
  }
}

/* ------------------------------ 6. THE MARKUP AGREES WITH THE DEFAULT ----- */
console.log("\n--- 6. the markup opens in the same state the script does ---");
{
  /* Until applySpin() first runs, the static markup IS what a visitor reads. A
     button saying "Stop spin" over a still ship is the page contradicting
     itself, briefly, on every load. */
  const html = readFileSync(join(SRC, "loadout.src.html"), "utf-8");
  const btn = (html.match(/<button[^>]*id="cc-spin"[\s\S]*?<\/button>/) || [""])[0];
  record(!!btn, "the spin control is in the markup");
  record(/>\s*Start spin\s*</.test(btn),
    "and its initial label is \"Start spin\", matching the default",
    btn.replace(/\s+/g, " ").slice(0, 90));
  record(/title="Start the ship rotating"/.test(btn),
    "with a matching title");
}

finish(
  SELFTEST ? "--self-test: expectations were inverted, so a non-zero exit is "
    + "the correct outcome."
  : (MUT_DEFAULT || MUT_FORGET)
    ? "--mutate: a defect was planted, so a non-zero exit is the correct "
      + "outcome."
    : "");
