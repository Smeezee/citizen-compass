/**
 * Q3 / E6 - THE CONTROL PANEL NOBODY COULD FIND, AND H1f-2's PERSISTENCE,
 * WHICH IS WHY IT MATTERS MORE THAN IT DID.
 *
 * Sleven reported the ENTIRE control panel as missing while looking straight
 * at it. The only way in was a word - `Look` - set in the muted colour, in the
 * corner of a stage already carrying muted corner text. It read as a caption on
 * the picture rather than as a thing to press.
 *
 * THREE CHANGES, AND EACH ONE IS ASSERTED SEPARATELY BECAUSE EACH ONE CAN FAIL
 * ON ITS OWN:
 *   the label names what is behind it - `Display`, not `Look`
 *   it carries a gear, the one glyph everybody already reads as "settings"
 *   and on a FIRST VISIT it opens itself, once, and remembers that it did
 *
 * WHY THE AUTO-OPEN IS NOT A NICETY. H1f-2 made every setting in that panel
 * persist indefinitely. Somebody who loses their stored settings - cleared site
 * data, a new browser, private browsing - lands on the defaults and has to find
 * the panel to get back to what they had. Clearing storage clears the seen-flag
 * too, so the recovery path and the first-visit path are THE SAME PATH. That is
 * asserted here rather than left as a comment, because it is the whole argument
 * for storing the flag beside the settings.
 *
 * AND H1f-2 ITSELF IS CHECKED HERE. "The panel is findable" is only worth
 * something if the settings it holds are the ones that outlive a session.
 *
 * MUTATORS
 *   --mutate-oldlabel   the control goes back to a bare `Look`.
 *   --mutate-autoopen   the first visit opens the panel over the hull
 *                       again - V3 retired that, and this is how this
 *                       section is proven able to fail.
 *   --mutate-nagforever the seen-flag is never written, so it opens on EVERY
 *                       visit - the opposite failure, and the one an
 *                       auto-opening panel invites.
 *   --mutate-session    the settings go back to a session lifetime.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { loadPage, reporter } from "./_loadout_harness.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const VIEWER = process.env.CC_VIEWER
  || join(HERE, "..", "testing", "_src", "cc_viewer.js");

/* MARKUP MUTATIONS ARE NOT SCRIPT MUTATIONS, and the harness only patches
   script blocks. `--mutate-oldlabel` changes the BUTTON, which section 1 reads
   out of the file directly - routing it through loadPage() planted nothing and
   the harness said so rather than letting the run come out clean. */
const MARKUP_MUTS = {
  "--mutate-oldlabel": [
    [/><span class="ico" aria-hidden="true">&#9881;<\/span>Display<\/button>/,
     ">Look</button>"],
  ],
};
const MUTS = {
  /* V3, 2026-08-26: `--mutate-nofirst` IS GONE BECAUSE IT SHIPPED. It
     planted the removal of `offerPanelOnce();` as known-bad input, and
     that removal is now the intended behaviour - the mutation became the
     product. The assertion it fed is inverted in section 2.
     `--mutate-autoopen` replaces it and plants the OPPOSITE defect, the
     panel opening itself over the hull again, so section 2 still has a
     failure path it can be proven against. A section whose mutator was
     deleted rather than replaced is a section that can no longer fail. */
  "--mutate-autoopen": [
    ["/* V3, 2026-08-26: THE FIRST-VISIT AUTO-OPEN IS RETIRED",
     "offerPanelOnce();\n/* V3, 2026-08-26: THE FIRST-VISIT AUTO-OPEN IS RETIRED"],
  ],
  "--mutate-nagforever": [
    [/  rememberPanelSeen\(\);\n  tuneOpen\(true\);/, "  tuneOpen(true);"],
  ],
  "--mutate-session": [
    [/function ccStore\(\)\{\n  try\{ return \(typeof localStorage!=="undefined"\) \? localStorage : null; \}/,
     'function ccStore(){\n  try{ return (typeof sessionStorage!=="undefined") ? sessionStorage : null; }'],
  ],
};
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
if (MUT && !MUTS[MUT] && !MARKUP_MUTS[MUT]) {
  console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2);
}
if (MUT) console.log(`*** MUTATED: ${MUT} ***`);

const mutate = MUT ? (MUTS[MUT] || []) : [];
/* `viewer:true` puts a viewer in place before the page script runs, which
   is what a browser has: renderAll() -> showModel() -> view() creates one
   long before offerPanelOnce() is reached. Without it the harness boots a
   page with no viewer, view() returns null, and the first-visit offer is
   correctly declined - so this file would be asserting the no-WebGL case
   while claiming to test the ordinary one. */
const boot = (opts) => loadPage({ mutate, viewer: true,
  srcDir: process.env.CC_SRCDIR || null,
  pageFile: process.env.CC_PAGE || null, ...opts });

const { record, finish } = reporter(false);
let html = readFileSync(process.env.CC_PAGE
  || join(HERE, "..", "testing", "_src", "loadout.src.html"), "utf-8");
if (MUT && MARKUP_MUTS[MUT]) {
  for (const [pat, rep] of MARKUP_MUTS[MUT]) {
    const before = html;
    html = html.replace(pat, rep);
    if (html === before) {
      console.log(`MUTATION DID NOT APPLY - ${pat} matched nothing in the `
        + `markup, so this run proves nothing.`);
      process.exit(1);
    }
  }
}

console.log("==========================================================");
console.log("Q3 / E6 - the control panel is findable, and its settings stay");
console.log(MUT ? `MUTATED: ${MUT}` : "clean page");
console.log("==========================================================");

/* =====================================================================
   1. THE CONTROL SAYS WHAT IS BEHIND IT.
   ===================================================================== */
console.log("\n--- 1. the way in ---");
{
  const H = boot({ local: { ccPanelSeen: "1" } });
  const tag = (html.match(/<button[^>]*id="cc-tune"[\s\S]*?<\/button>/) || [""])[0];
  record(tag !== "", "the control is in the markup");
  const text = tag.replace(/<[^>]*>/g, "").replace(/&#\d+;/g, "").trim();
  record(!/^Look$/i.test(text),
    "it is no longer the bare word `Look`, which Sleven read straight past",
    JSON.stringify(text));
  record(/display/i.test(text),
    "it names what is behind it", JSON.stringify(text));
  /* THE GEAR IS NOT DECORATION. It is the only part of this control that is
     recognisable without reading, and Sleven's report was about not seeing the
     control at all. */
  record(/&#9881;/.test(tag),
    "and it carries a gear - the one glyph a person reads as `settings` "
    + "without reading anything");
  record(/aria-hidden="true"/.test(tag),
    "the gear is hidden from a screen reader, which gets the words instead");
  record(/aria-controls="cc-tune-panel"/.test(tag),
    "and the control declares what it opens");
  record(/title="[^"]*style[^"]*"/i.test(tag)
    && /title="[^"]*colour[^"]*"/i.test(tag),
    "with a title that lists what is inside rather than describing an activity",
    (/title="([^"]*)"/.exec(tag) || [])[1]);

  /* AND IT READS AS A CONTROL. `Look` was drawn in --muted on a scrim, which
     is the same treatment as the stage's own hint text. */
  const css = html.slice(html.indexOf("#cc-tune{"),
                         html.indexOf("#cc-tune-panel{"));
  record(/color:var\(--text\)/.test(css),
    "it is drawn in the text colour, not the muted one the stage hints use",
    css.slice(0, 60).replace(/\s+/g, " "));
  record(/border:1px solid var\(--accent2\)/.test(css),
    "and outlined in the accent, so it reads as a thing to press");
  void H;
}

/* =====================================================================
   2. THE FIRST VISIT DOES NOT OPEN IT - V3 INVERTED THIS SECTION.

   It asserted the opposite until 2026-08-26, and the reasoning it asserted was
   never wrong: this panel holds settings that persist indefinitely, so
   somebody who loses their storage lands on defaults and needs a way back to
   what they had, and clearing storage clears the seen-flag too, which makes
   the first-visit path and the recovery path the same path.

   WHAT CHANGED IS THE COST, WHICH NOBODY HAD MEASURED. The panel is 250px on
   a stage that is often 900px wide, so it opened OVER THE HULL - including in
   every screenshot taken of this page during the four days the fleet was
   framed at 850x and those screenshots were being used to argue about how the
   hull renders.

   Q3's gear glyph and the word `Display` are what E6's auto-open was
   compensating for, and they shipped. So the guarantee is now: the button is
   findable (section 1, unchanged), its state persists (section 4, unchanged),
   and it never opens itself over the model.
   ===================================================================== */
console.log("\n--- 2. a first visit, and every visit after ---");
{
  const first = boot({ local: {} });
  record(first.g("tuneIsOpen()") === false,
    "on a first visit the panel does NOT open itself over the hull - the ship "
    + "is what the page opens on");
  record(!first.local._dump().ccPanelSeen,
    "and nothing is written to storage for an offer that was never made",
    JSON.stringify(first.local._dump()));

  /* THE SECOND VISIT IS SEEDED FROM WHAT THE FIRST ONE STORED, not from a
     flag typed in here. Seeding it by hand would pass against a build that
     never wrote the flag at all - which is the opposite failure an
     auto-opening panel invites, and the one --mutate-nagforever plants. */
  const second = boot({ local: first.local._dump() });
  record(second.g("tuneIsOpen()") === false,
    "and neither does any visit after it",
    JSON.stringify(first.local._dump()));

  /* AN EMPTY PANEL MUST NOT OPEN ITSELF. renderTunePanel() draws nothing
     without a viewer, so on a machine with no WebGL the offer would be an
     empty box - worse than nothing, and it would spend the one offer this
     feature gets. Both halves are asserted: no viewer means no offer, and a
     viewer means the offer arrives full. */
  /* V3: THE PANEL IS OPENED BY HAND HERE. What this asserts - that it arrives
     full rather than as an empty box - is still true and still worth
     asserting; it is just no longer reachable by loading the page, so the
     control presses the button the way a visitor does. */
  first.g("tuneOpen(true)");
  const body = first.el("cc-tune-panel").innerHTML || "";
  record(/data-style=/.test(body) && /data-colour=/.test(body),
    "and when a visitor DOES open it, it arrives with its controls already in "
    + "it, not as an empty box", `${body.length} chars`);
  /* THE OTHER HALF. renderTunePanel() draws nothing without a viewer, so on a
     machine with no WebGL the offer would be an empty box - worse than
     nothing, and it would spend the one offer this feature gets. Not offered
     is not the same as offered and empty. */
  const noGl = loadPage({ mutate, local: {} });
  record(noGl.g("tuneIsOpen()") === false,
    "and with no viewer at all it is NOT offered - an empty panel opening "
    + "itself would spend the one offer this feature gets");
  record(!noGl.local._dump().ccPanelSeen,
    "and the offer is not marked as spent, so it arrives on a machine that "
    + "can show it", JSON.stringify(noGl.local._dump()));
}

/* =====================================================================
   3. NO STORAGE MEANS NO NAGGING.
   ===================================================================== */
console.log("\n--- 3. a browser that cannot remember ---");
{
  const none = boot({});
  record(none.g("tuneIsOpen()") === false,
    "with no storage at all the panel does NOT open itself - it could never "
    + "record that it had, so it would open on every single page view");
  let threw = null;
  try {
    const dead = boot({ sessionThrows: true });
    record(dead.g("tuneIsOpen()") === false,
      "and a browser where every storage access throws behaves the same");
  } catch (e) { threw = e.message; }
  record(!threw, "and nothing in this path throws when storage does",
    threw || "");
}

/* =====================================================================
   4. H1f-2 - THE SETTINGS OUTLIVE THE SESSION.
   ===================================================================== */
console.log("\n--- 4. the settings the panel holds are permanent ---");
{
  const src = readFileSync(VIEWER, "utf-8");
  record(/localStorage/.test(src) && !/\(typeof sessionStorage/.test(src),
    "the viewer's own store is the persistent one",
    /\(typeof sessionStorage/.test(src) ? "still session" : "localStorage");

  const H = boot({ local: {} });
  H.openShip(Object.keys(H.SHIPS).find((k) => (H.SHIPS[k].slots || []).length));
  /* Every control in the panel, driven through the page's own handlers. */
  H.dispatch(["#cc-tune-panel button[data-style]"], { dataset: { style: "wire" } });
  H.dispatch(["#cc-tune-panel button[data-view]"], { dataset: { view: "spin" } });
  H.dispatch(["#cc-dim button[data-dim]"], { dataset: { dim: "night" } });
  const stored = H.local._dump();
  /* THE STYLE IS THE VIEWER'S OWN TO STORE, and this harness's viewer is a
     stub that records calls rather than writing anything - so asserting
     `ccHolo` here would be asserting something this file cannot produce, which
     is how a check comes to measure its own scaffolding. What IS this page's
     job is calling remember(); the store it lands in is asserted from
     cc_viewer's source above and driven for real by _verify_holo_render.mjs. */
  record((H.g("_view").calls || []).includes("remember"),
    "the page tells the viewer to remember the style it was just given",
    JSON.stringify(H.g("_view").calls || []));
  record(stored.ccSpin === "1", "the spin choice is written", stored.ccSpin);
  record(!!stored.ccDim, "and the brightness is written", stored.ccDim);
  record(Object.keys(H.session._dump()).length === 0,
    "and NOTHING went into the session store - all three have to outlive the "
    + "browser closing", JSON.stringify(H.session._dump()));

  /* THE ROUND TRIP. Writing proves nothing if nothing reads it back the next
     morning: a fresh page with the persistent store seeded and the session one
     empty, which is exactly what that morning looks like. */
  const back = boot({ local: stored });
  record(back.g("CC_THEME.presetAt()") === "night",
    "a page loaded weeks later comes back at the brightness that was set",
    String(back.g("CC_THEME.presetAt()")));
  record(back.g("spinOn") === true,
    "and at the spin preference");
}

/* =====================================================================
   5. THE RECOVERY PATH IS THE FIRST-VISIT PATH.
   ===================================================================== */
console.log("\n--- 5. somebody who loses their settings can get back ---");
{
  /* V3 CHANGED WHAT THIS SECTION CAN PROMISE, AND THE LOSS IS RECORDED HERE
     RATHER THAN DELETED.

     Clearing site data takes the settings AND the seen-flag, so the person who
     most needs to find the panel is the one whose settings just vanished. E6
     answered that by opening the panel for them. V3 retired the auto-open
     because it opened over the hull, so THAT ANSWER IS GONE: recovery now
     depends entirely on the visitor noticing the `Display` button.

     This assertion is inverted rather than removed so the change is visible to
     whoever reads this file next, and so the remaining half - that they land on
     working defaults rather than on nothing - is still checked. If Sleven wants
     the recovery prompt back, this is the section that says what it cost. */
  const cleared = boot({ local: {} });
  record(cleared.g("tuneIsOpen()") === false,
    "a person whose site data was cleared is NOT shown the panel - V3 traded "
    + "the recovery prompt for an uncovered hull, and the `Display` button is "
    + "the whole of the way back");
  record(cleared.g("CC_THEME.level") === 0,
    "and lands on the defaults rather than on nothing",
    String(cleared.g("CC_THEME.level")));
}

finish(MUT
  ? "--mutate: a defect was planted, so a non-zero exit is the correct outcome."
  : "");
