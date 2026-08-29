/**
 * R4 - GOING BACK GOES BACK.

 *
 * RULE16: UNPROVEN - the position it restores to and the position it recorded are
 * both the page's own state, so a module that stored the wrong scroll and
 * restored it faithfully would pass. What is independent is the SEQUENCE:
 * the control navigates away and back rather than asking whether the module
 * believes it would.
 *
 * Sleven: "If I'm sitting at the very bottom of the page and I click the
 * Cyclone TR... I wanna look at the other Cyclone - bam, right back to Avenger
 * Stalker at the very top. Fix it."
 *
 * WHAT IS DRIVEN HERE. `cc_listmem.js` itself, and the ship-list adapter out of
 * the built index.html, both running against a DOM stub with a real matrix of
 * rows in it. Not a paraphrase of either: the module's own attach/save/restore
 * and the adapter's own capture/apply.
 *
 * WHAT IS NOT. There is no browser and no layout (rule 7), so `scrollTo` is a
 * recorded number rather than a rendered position, and "restored to within a
 * few pixels" is asserted on that number. What that DOES prove is the whole of
 * the defect: the offset was never stored at all, so nothing could have put it
 * back. What it cannot prove is that a real document was tall enough at the
 * moment of restore - which is why the module retries, and why the retry is
 * asserted separately with a document that grows.
 *
 * THE LOAD-BEARING NEGATIVE IS THE ORDER'S OWN: return to a list never visited
 * this session and land at the TOP. A build that restores a stale offset from
 * a DIFFERENT list passes every other check in this file.
 *
 * MUTATORS
 *   --mutate-oneglobalkey  every list shares one storage key, so the ship list
 *                          restores an offset left by another list. The order's
 *                          named failure.
 *   --mutate-scrollonly    the state is dropped and only the offset is kept -
 *                          a position restored into a differently-filtered
 *                          list, which is a different wrong place.
 *   --mutate-noclickmark   the row that was opened is not recorded.
 */

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");
const MODULE = process.env.CC_LISTMEM
  || join(ROOT, "testing", "_src", "cc_listmem.js");
const INDEX = process.env.CC_INDEX
  || join(ROOT, "testing", "_deploy", "index.html");

const MUTS = {
  /* EVERY LIST SHARES ONE KEY, which is the order's own named failure: a
     build that restores a stale offset left by a DIFFERENT list. Both the read
     and the write have to lose the key or the two halves simply stop matching
     and nothing is restored at all - which fails for the wrong reason. */
  "--mutate-oneglobalkey": [
    [/var raw = s\.getItem\(PREFIX \+ key\);/, "var raw = s.getItem(PREFIX);"],
    [/try \{ s\.setItem\(PREFIX \+ key, JSON\.stringify\(v\)\); return true; \}/,
     "try { s.setItem(PREFIX, JSON.stringify(v)); return true; }"],
    [/if \(!v \|\| v\.k !== key\) return false;/, "if (!v) return false;"],
  ],
  "--mutate-scrollonly": [
    [/if \(spec\.apply && v\.s\) \{/, "if (false) {"],
  ],
  "--mutate-noclickmark": [
    [/save\(spec\.key, spec\.idOf \? spec\.idOf\(a\) : null\);/, "save(spec.key);"],
  ],
};
const MUT = process.argv.slice(2).find((a) => a.startsWith("--mutate-")) || "";
if (MUT && !MUTS[MUT]) { console.log(`UNKNOWN MUTATOR ${MUT}`); process.exit(2); }
if (MUT) console.log(`*** MUTATED: ${MUT} ***`);

let passed = 0;
const failures = [];
const notes = [];
function record(ok, label, detail = "") {
  if (ok) { passed++; console.log(`  ok   ${label}`); }
  else { failures.push(`${label} ${detail}`.trim());
         console.log(`  FAIL ${label} ${detail}`); }
  return !!ok;
}

if (!existsSync(INDEX)) {
  console.log(`NOT PERFORMED - ${INDEX} is not built, so the ship-list adapter `
    + `cannot be read. Reported as not performed rather than as passed.`);
  process.exit(2);
}

/* ---------------------------------------------------------------- the stub */
/* A LIST PAGE, SMALL BUT REAL. Rows with the link shape the build emits, a
   search box, a window that records where it was scrolled to, and one storage
   that persists across the "pages" in a run - because the whole question is
   what survives a navigation. */
function makePage(rows, sharedStore) {
  const listeners = {};
  const store = sharedStore || {};
  const mk = (tag, attrs, parent) => {
    const node = {
      tagName: String(tag).toUpperCase(), _attrs: { ...(attrs || {}) },
      children: [], parentNode: parent || null, style: {}, value: "",
      className: (attrs && attrs.class) || "",
      classList: {
        add(c) { if (!node.className.split(/\s+/).includes(c))
          node.className = (node.className + " " + c).trim(); },
        remove(c) { node.className = node.className.split(/\s+/)
          .filter((x) => x && x !== c).join(" "); },
        contains(c) { return node.className.split(/\s+/).includes(c); },
        toggle(c, on) { const has = node.classList.contains(c);
          const want = on === undefined ? !has : !!on;
          if (want) node.classList.add(c); else node.classList.remove(c); },
      },
      getAttribute(k) { return node._attrs[k] === undefined ? null : node._attrs[k]; },
      setAttribute(k, v) { node._attrs[k] = String(v); },
      hasAttribute(k) { return k in node._attrs; },
      addEventListener() {},
      dispatchEvent(e) {
        (node._on || {})[e && e.type] && node._on[e.type](e);
        return true;
      },
      closest(sel) {
        let n = node;
        while (n) { if (matches(n, sel)) return n; n = n.parentNode; }
        return null;
      },
      querySelector(sel) { return descend(node, sel)[0] || null; },
      querySelectorAll(sel) { return descend(node, sel); },
      appendChild(c) { c.parentNode = node; node.children.push(c); return c; },
    };
    if (parent) parent.appendChild(node);
    return node;
  };
  const matches = (n, sel) => {
    if (!n || !n.tagName) return false;
    /* Only the shapes this page actually uses, and they are literal. A
       selector engine here would be a second implementation of something no
       assertion below depends on. */
    if (sel === "tr") return n.tagName === "TR";
    if (sel === "a.cc-open") {
      return n.tagName === "A" && n.classList.contains("cc-open");
    }
    const m = /^a\.cc-open\[href\$="#(.+)"\]$/.exec(sel);
    if (m) {
      return n.tagName === "A" && n.classList.contains("cc-open")
        && String(n.getAttribute("href") || "").endsWith("#" + m[1]);
    }
    return false;
  };
  const descend = (root, sel) => {
    const out = [];
    const walk = (n) => {
      for (const c of n.children) { if (matches(c, sel)) out.push(c); walk(c); }
    };
    walk(root);
    return out;
  };

  const byId = {};
  const doc = {
    documentElement: { scrollTop: 0 },
    body: { scrollTop: 0 },
    getElementById: (id) => byId[id] || null,
    addEventListener(t, fn) { (listeners[t] = listeners[t] || []).push(fn); },
    _fire(t, ev) { (listeners[t] || []).forEach((fn) => fn(ev)); },
  };
  /* THE BODY STARTS EMPTY, BECAUSE IT DOES. The base page ships
     `<tr><td colspan=10>Loading ships</td></tr>` and fills the table from
     script afterwards - so the adapter runs against an empty list and the
     sorter that publishes CC_MATRIX_STATE has not built yet either. A stub
     that handed the adapter a finished table would be testing an order of
     events this page never has, and section 4 would pass against a build whose
     apply() could never see the matrix state. */
  const tbody = mk("tbody", { id: "matrix-body" }, null);
  byId["matrix-body"] = tbody;
  const search = mk("input", { id: "shipSearch" }, null);
  search._on = {};
  byId.shipSearch = search;

  /* THE WINDOW IS THE GLOBAL, because in a browser it is. The adapter
     publishes `window.CC_LISTMEM_SHIPS` and the module reads `window.scrollY`;
     a `window` that is some other object would make both of those land
     somewhere no assertion looks - a stub faithful about everything except the
     one thing under test. */
  const sandbox = {
    console, Math, JSON, String, Number, Object, Array, Date, isFinite,
    setTimeout: () => 0,
    document: doc,
    history: { scrollRestoration: "auto" },
    scrollY: 0,
    _scrolls: [],
    scrollTo(x, y) { sandbox.scrollY = y; sandbox._scrolls.push(y); },
    addEventListener(t, fn) { (listeners[t] = listeners[t] || []).push(fn); },
    _fire(t) { (listeners[t] || []).forEach((fn) => fn()); },
    sessionStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; },
      _dump: () => ({ ...store }),
    },
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  const fill = (ids) => {
    for (const r of ids || []) {
      const tr = mk("tr", {}, tbody);
      const td = mk("td", {}, tr);
      mk("a", { class: "cc-open", href: "loadout.html#" + r }, td);
    }
    return tbody;
  };
  return { sandbox, doc, win: sandbox, store, search, tbody, mk, fill };
}

let code = readFileSync(MODULE, "utf-8");
if (MUT) {
  for (const [pat, rep] of MUTS[MUT]) {
    const before = code;
    code = code.replace(pat, rep);
    if (code === before) {
      console.log(`MUTATION DID NOT APPLY - ${pat} matched nothing, so this `
        + `run proves nothing.`);
      process.exit(1);
    }
  }
}

/* The ship adapter, lifted out of the BUILT page rather than retyped, so what
   runs here is what ships. */
const indexHtml = readFileSync(INDEX, "utf-8");
const adapter = (() => {
  const i = indexHtml.indexOf("var KEY = 'ships';");
  if (i < 0) return null;
  const open = indexHtml.lastIndexOf("<script>", i);
  const close = indexHtml.indexOf("</script>", i);
  return (open < 0 || close < 0) ? null
    : indexHtml.slice(open + "<script>".length, close);
})();

/* The page's real order: the module, then the adapter, then - later - the rows
   and the sorter's state. `rows` are filled AFTER, and `matrix` is installed
   between, exactly as the sorter's retry loop does it. */
function boot(rows, sharedStore, matrix) {
  const P = makePage([], sharedStore);
  vm.runInContext(code, P.sandbox, { filename: "cc_listmem.js" });
  if (adapter) vm.runInContext(adapter, P.sandbox, { filename: "index:adapter" });
  if (matrix) P.sandbox.CC_MATRIX_STATE = matrix;
  P.fill(rows);
  return P;
}

const ROWS = ["AEGS_Avenger_Stalker", "TMBL_Cyclone_TR", "TMBL_Cyclone_RN",
              "AEGS_Reclaimer", "RSI_Perseus"];

console.log("==========================================================");
console.log("R4 - returning to a list returns to where you were");
console.log(MUT ? `MUTATED: ${MUT}` : "clean");
console.log("==========================================================");

/* =====================================================================
   1. THE ADAPTER IS THE ONE THAT SHIPS.
   ===================================================================== */
console.log("\n--- 1. what is being driven ---");
{
  record(!!adapter, "the ship-list adapter was lifted out of the BUILT "
    + "index.html, not retyped here", adapter ? `${adapter.length} chars` : "");
  record(/cc_listmem\.js/.test(indexHtml),
    "and the built page loads the shared module");
  record(/CC_MATRIX_STATE/.test(indexHtml),
    "and exposes the matrix's sort/filter state for it to restore");
}

/* =====================================================================
   2. THE NEGATIVE THE ORDER NAMES, FIRST, because everything else is only
      worth something if this holds.
   ===================================================================== */
console.log("\n--- 2. a list never visited this session opens at the top ---");
{
  const shared = {};
  /* ANOTHER LIST LEAVES A DEEP OFFSET, AND IT DOES IT BY USING THE MODULE
     RATHER THAN BY HAVING A RECORD TYPED INTO STORAGE HERE. A hand-written key
     would only reproduce the collision if this file guessed the same key
     format the module uses - so a mutation that changed that format would make
     the fixture stop matching and the run would pass for the wrong reason,
     which is exactly what the first version of this section did. */
  /* A DIFFERENT PAGE, so the ships adapter is not on it. Booting the ships
     page and calling it "another list" made its OWN pagehide store a ships
     record at 4,300 - and the section then failed on the clean build, for a
     reason that had nothing to do with what it was testing. */
  const other = makePage([], shared);
  vm.runInContext(code, other.sandbox, { filename: "cc_listmem.js" });
  other.sandbox.CCListMem.attach({
    key: "find", scroller: function () { return null; },
    capture: function () { return { q: "omnisky" }; },
  });
  other.sandbox.scrollY = 4300;
  other.sandbox._fire("pagehide");
  record(other.sandbox.CCListMem.peek("find") !== null,
    "a different list really did store a deep offset",
    JSON.stringify(other.sandbox.CCListMem.peek("find")));

  const P = boot(ROWS, shared);
  P.sandbox.CC_LISTMEM_SHIPS.restore();
  record(P.win.scrollY === 0,
    "the ship list is at the top - a stale offset from a DIFFERENT list does "
    + "not reach it", `scrollY ${P.win.scrollY}`);
  record(P.win._scrolls.length === 0,
    "and nothing scrolled at all - the top is reached by doing nothing, not "
    + "by scrolling to zero", JSON.stringify(P.win._scrolls));
  record(P.sandbox.CCListMem.peek("ships") === null,
    "because there is no record for this list to read",
    JSON.stringify(P.sandbox.CCListMem.peek("ships")));
}

/* =====================================================================
   3. THE OFFSET SURVIVES A NAVIGATION, BY BOTH ROUTES BACK.
   ===================================================================== */
console.log("\n--- 3. scroll down, open a ship, come back ---");
{
  const shared = {};
  const A = boot(ROWS, shared);
  A.win.scrollY = 4300;
  /* Open the Cyclone TR the way a person does. */
  const link = A.tbody.querySelectorAll("a.cc-open")
    .find((a) => /Cyclone_TR/.test(a.getAttribute("href")));
  record(!!link, "the Cyclone TR is in the list to click");
  A.doc._fire("click", { target: link });
  A.win._fire("pagehide");
  const rec = JSON.parse(shared["ccList:ships"] || "null");
  record(rec && rec.y === 4300,
    "leaving the list records where it was", JSON.stringify(rec && rec.y));

  /* ROUTE ONE: the page's own "All ships" link - a plain navigation to
     index.html, which is an ARRIVAL. */
  const B = boot(ROWS, shared);
  B.sandbox.CC_LISTMEM_SHIPS.restore();
  record(Math.abs(B.win.scrollY - 4300) <= 2,
    "arriving back by the All ships link restores the offset",
    `scrollY ${B.win.scrollY}`);

  /* ROUTE TWO: browser Back. The same arrival, and that is the point - there
     is no second code path for it to diverge from. */
  const C = boot(ROWS, shared);
  C.sandbox.CC_LISTMEM_SHIPS.restore();
  record(C.win.scrollY === B.win.scrollY,
    "and arriving back by browser Back lands in the SAME place - both are an "
    + "arrival, so they cannot diverge", `${C.win.scrollY} vs ${B.win.scrollY}`);

  /* AND THE ROW IS MARKED. */
  const tr = C.tbody.querySelectorAll("tr")
    .find((r) => r.classList.contains("cc-came-from"));
  record(!!tr, "the row that was opened is marked on return",
    tr ? (tr.querySelector("a.cc-open") || {}).getAttribute?.("href") : "none");
}

/* =====================================================================
   4. THE STATE TRAVELS WITH IT, NOT JUST THE NUMBER.
   ===================================================================== */
console.log("\n--- 4. search, sort and filter come back too ---");
{
  const shared = {};
  /* A matrix state of the shape the built page exposes, installed the way the
     sorter installs it: after the adapter, before the rows. */
  let cur = { col: null, dir: 0, dealer: null, budget: null,
              buyOnly: false, q: "" };
  const A = boot(ROWS, shared, {
    get: () => ({ ...cur }), set: (v) => { cur = { ...v }; return true; },
  });
  A.sandbox.CC_MATRIX_STATE.set(
    { col: 2, dir: -1, dealer: null, budget: 3000000, buyOnly: true,
      q: "cyclone" });
  A.win.scrollY = 1800;
  A.win._fire("pagehide");
  const rec = JSON.parse(shared["ccList:ships"] || "null");
  record(rec && rec.s && rec.s.q === "cyclone" && rec.s.col === 2
    && rec.s.buyOnly === true,
    "the search text, the sorted column and the filters are all recorded",
    JSON.stringify(rec && rec.s));

  let applied = null;
  const B = boot(ROWS, shared, {
    get: () => ({}), set: (v) => { applied = v; return true; },
  });
  B.sandbox.CC_LISTMEM_SHIPS.restore();
  record(applied && applied.q === "cyclone",
    "and are handed back to the list on arrival",
    JSON.stringify(applied));
  record(applied && applied.col === 2 && applied.dir === -1
    && applied.budget === 3000000 && applied.buyOnly === true,
    "every one of them, not just the search box", JSON.stringify(applied));
  record(Math.abs(B.win.scrollY - 1800) <= 2,
    "with the offset", `scrollY ${B.win.scrollY}`);
}

/* =====================================================================
   5. A RELOAD IS A NAVIGATION TOO.
   ===================================================================== */
console.log("\n--- 5. the state survives a reload ---");
{
  const shared = {};
  const A = boot(ROWS, shared);
  A.win.scrollY = 2600;
  A.win._fire("beforeunload");
  const B = boot(ROWS, shared);
  B.sandbox.CC_LISTMEM_SHIPS.restore();
  record(Math.abs(B.win.scrollY - 2600) <= 2,
    "a refresh does not dump somebody at the top of 254 rows",
    `scrollY ${B.win.scrollY}`);
}

/* =====================================================================
   6. THE RESTORE WAITS FOR THE ROWS.
   ===================================================================== */
console.log("\n--- 6. restoring into a list that has not rendered yet ---");
{
  const shared = { "ccList:ships": JSON.stringify(
    { y: 3900, s: null, hi: null, k: "ships" }) };
  /* An empty body is what the base page shows while it says "Loading ships". */
  const P = boot([], shared);
  const did = P.sandbox.CC_LISTMEM_SHIPS.restore();
  record(did === false,
    "with no rows yet the restore does NOT fire - scrolling a 200px document "
    + "to 3,900 is the top, which is the defect", String(did));
  record(P.win.scrollY === 0, "and nothing moved", `scrollY ${P.win.scrollY}`);
  /* The rows arrive. */
  const td = P.mk("td", {}, P.mk("tr", {}, P.tbody));
  P.mk("a", { class: "cc-open", href: "loadout.html#AEGS_Reclaimer" }, td);
  const now = P.sandbox.CC_LISTMEM_SHIPS.restore();
  record(now === true && Math.abs(P.win.scrollY - 3900) <= 2,
    "and once they exist it restores", `scrollY ${P.win.scrollY}`);
}

/* =====================================================================
   7. THE BROWSER IS TOLD TO STOP RESTORING ITS OWN.
   ===================================================================== */
console.log("\n--- 7. two restores would fight ---");
{
  const P = boot(ROWS, {});
  record(P.sandbox.history.scrollRestoration === "manual",
    "history.scrollRestoration is set to manual, so the browser's own restore "
    + "does not land somewhere else a moment before ours",
    P.sandbox.history.scrollRestoration);
}

/* =====================================================================
   8. A BROWSER WITH NO STORAGE STILL WORKS.
   ===================================================================== */
console.log("\n--- 8. storage absent or throwing ---");
{
  const P = makePage([], {});
  P.fill(ROWS);
  delete P.sandbox.sessionStorage;
  let boom = null;
  try {
    vm.runInContext(code, P.sandbox, { filename: "cc_listmem.js" });
    if (adapter) vm.runInContext(adapter, P.sandbox, { filename: "index:adapter" });
    P.win._fire("pagehide");
    P.sandbox.CC_LISTMEM_SHIPS.restore();
  } catch (e) { boom = e.message; }
  record(!boom, "a browser without sessionStorage does not throw", boom || "");
  record(P.win.scrollY === 0, "and lands at the top, which is correct");

  const Q = makePage([], {});
  Q.fill(ROWS);
  Q.sandbox.sessionStorage = {
    getItem() { throw new Error("storage disabled"); },
    setItem() { throw new Error("storage disabled"); },
  };
  let boom2 = null;
  try {
    vm.runInContext(code, Q.sandbox, { filename: "cc_listmem.js" });
    if (adapter) vm.runInContext(adapter, Q.sandbox, { filename: "index:adapter" });
    Q.win._fire("pagehide");
    Q.sandbox.CC_LISTMEM_SHIPS.restore();
  } catch (e) { boom2 = e.message; }
  record(!boom2, "and neither does one where every access throws", boom2 || "");
}

console.log("\n==========================================================");
for (const n of notes) console.log("  " + n);
if (failures.length) {
  console.log(`\nFAILED: ${failures.length} of ${passed + failures.length}`);
  for (const f of failures) console.log("  " + f);
  if (MUT) {
    console.log("\n--mutate: a defect was planted, so a non-zero exit is the "
      + "correct outcome.");
  }
  process.exit(1);
}
if (MUT) {
  console.log("\n--mutate: A DEFECT WAS PLANTED AND NOTHING FAILED. This "
    + "control did not measure what it claims to.");
  process.exit(3);
}
console.log(`\nAll ${passed} assertions passed against the shipped module and `
  + `the built page's own adapter.`);
process.exit(0);
