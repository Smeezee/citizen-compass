/**
 * THE SHIP PAGE, RUNNING, FOR A CONTROL TO DRIVE.
 *
 * WHY THIS IS A MODULE AND NOT COPIED INTO EACH CONTROL
 * ----------------------------------------------------
 * `_verify_ship_page.mjs` and `_verify_marker_response.mjs` each carry their
 * own copy of this DOM stub. The B run adds several more controls that need
 * the same thing, and a stub duplicated seven times is seven writers for one
 * fact (rule 14): the day the page starts touching a DOM property none of the
 * copies implement, the copies diverge one at a time and each control silently
 * measures a slightly different page.
 *
 * WHAT IT IS. The smallest browser the page actually touches - elements are
 * plain objects carrying the handful of properties the render paths write, so
 * what a control asserts is the HTML the page produced rather than a paraphrase
 * of it.
 *
 * WHAT IT IS NOT, stated plainly because it bounds every control built on it:
 * there is no layout, no CSS, no geometry and no browser. It proves the page's
 * LOGIC and the markup it emits. It cannot prove that something is visible, or
 * where on screen it lands. There is no browser on this machine and none was
 * installed (rule 7). Where an item's acceptance is genuinely about pixels,
 * the control says so rather than pretending this measured them.
 *
 * `mutate` takes [regexp, replacement] pairs applied to the page's script
 * before it runs, and REFUSES to continue if a pattern did not match - a
 * mutation that quietly did nothing would leave the control proving that a
 * healthy page is healthy while claiming to have planted a defect.
 */

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import vm from "node:vm";

const HERE = dirname(fileURLToPath(import.meta.url));
export const SRC = join(HERE, "..", "testing", "_src");

export function loadPage({ mutate = [], session = null,
                           sessionThrows = false, srcDir = null,
                           pageFile = null } = {}) {
  /* `srcDir` lets a control drive bytes that came from somewhere else. B8
     fetches the DEPLOYED page and its data files into a temp directory and
     points this at them, so what is asserted is what the ORIGIN SERVES rather
     than what the working tree holds. Same harness, same assertions, different
     bytes - which is the only way "verified from the served bytes" means more
     than "the deploy exited 0". */
  const dir = srcDir || SRC;
  const html = readFileSync(pageFile || join(dir, "loadout.src.html"), "utf-8");
  const dataJs = readFileSync(join(dir, "loadout_data.gen.js"), "utf-8");
  const EXTRA = ["loadout_model.gen.js", "loadout_marker.gen.js",
                 "loadout_eng.gen.js"]
    .map((f) => join(dir, f))
    .filter((f) => existsSync(f))
    .map((f) => readFileSync(f, "utf-8"));

  const els = new Map();
  const el = (id) => {
    if (!els.has(id)) {
      els.set(id, {
        id, innerHTML: "", textContent: "", className: "", value: "",
        style: {}, onclick: null, onchange: null, href: "", hidden: false,
        classList: { add() {}, remove() {}, toggle() {} },
        removeAttribute(a) { this[a] = ""; },
        setAttribute(a, v) { this[a] = v; },
        get childElementCount() { return 0; },
        get children() { return []; },
        /* A STATED STAGE SIZE, so B3's placement maths runs on real numbers
           rather than on zero. 960x540 is a plausible desktop stage and it is
           a STUB, not a measurement: nothing here proves the panel fits a real
           viewport, only that the arithmetic places it inside the box it was
           given. The pure function is driven separately with its own numbers,
           including numbers chosen to make it flip. */
        clientWidth: 960, clientHeight: 540,
      });
    }
    return els.get(id);
  };

  let currentHash = "";
  const clickHandlers = [];
  const keyHandlers = [];
  const sandbox = {
    console, JSON, Math, Date, Number, String, Array, Object, Map, Set, RegExp,
    Error, isNaN, parseInt, parseFloat, encodeURIComponent, decodeURIComponent,
    setTimeout: () => 0,
    addEventListener() {},
    history: {
      replaceState(_a, _b, url) { currentHash = String(url).replace(/^#/, ""); },
    },
    location: {
      get hash() { return "#" + currentHash; },
      set hash(v) { currentHash = String(v).replace(/^#/, ""); },
    },
    navigator: {},
    document: {
      getElementById: (id) => el(id),
      /* CAPTURED, NOT SWALLOWED. A control has to dispatch a real event
         through the page's own delegated handler; a no-op addEventListener
         would leave nothing to dispatch to, and the only thing left to assert
         would be that a listener exists - which is worth nothing, and is
         exactly the mistake the RSI-link erratum was. */
      addEventListener: (t, fn) => {
        if (t === "click") clickHandlers.push(fn);
        if (t === "keydown") keyHandlers.push(fn);
      },
      querySelector: () => null,
    },
  };
  /* SESSION STORAGE, OPTIONAL AND THREE-WAY.
     Absent (the default) is a browser that has none, which is also what this
     harness is. `session` installs a working one seeded with real values.
     `sessionThrows` installs one that throws on every access, which is what a
     browser with storage disabled actually does - and is the case a page
     falls over on if it reads storage without a guard. All three are
     reachable, because "we handled it" is not the same as "we tried it". */
  if (sessionThrows) {
    sandbox.sessionStorage = {
      getItem() { throw new Error("storage disabled"); },
      setItem() { throw new Error("storage disabled"); },
    };
  } else if (session) {
    const store = { ...session };
    sandbox.sessionStorage = {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      _dump: () => ({ ...store }),
    };
  }

  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);

  /* THE PAGE'S OWN SCRIPT, PICKED BY WHAT IS IN IT.
     The _src file has one inline script, so "first <script> to last </script>"
     worked. The BUILT page has three.js, GLTFLoader, OrbitControls and the
     DRACO decoder inlined as well - that pattern would swallow all of them and
     run a megabyte of vendor code against a DOM stub. So every inline block is
     read and the one carrying the page's entry point is chosen. */
  const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1]);
  let script = blocks.find((b) => /function renderAll\s*\(/.test(b));
  if (!script) {
    console.log("NO PAGE SCRIPT FOUND - none of the " + blocks.length
      + " inline <script> blocks defines renderAll(). Refusing to assert "
      + "against a page this cannot drive.");
    process.exit(2);
  }
  for (const [pattern, replacement] of mutate) {
    const before = script;
    script = script.replace(pattern, replacement);
    if (script === before) {
      console.log(`MUTATION DID NOT APPLY - ${pattern} matched nothing, so `
        + `this run proves nothing. Fix the mutator before trusting the check.`);
      process.exit(1);
    }
  }

  vm.runInContext(dataJs, sandbox, { filename: "loadout_data.gen.js" });
  for (const s of EXTRA) vm.runInContext(s, sandbox, { filename: "gen" });
  vm.runInContext(script, sandbox, { filename: "loadout.src.html:script" });
  const g = (expr) => vm.runInContext(expr, sandbox);
  const run = (stmt) => vm.runInContext(stmt, sandbox);

  /* A STUB VIEWER. The marker layer will not render without one, and where a
     point projects to is irrelevant to every question these controls ask. */
  const VIEW = `_view={_s:false,boot(){},start(){},size(){},cancel(){},`
    + `clear(){},stop(){},current:{},unitScale(){return 1;},`
    + `project(){return{x:640,y:360,depth:0};},`
    + `spinning(){return this._s;},setSpin(v){this._s=!!v;return this._s;},`
    + `load(){return 1;}};`;

  /* `spin` is deliberately OPTIONAL and unset by default. Forcing spinOn on
     every openShip() would overwrite whatever the page decided at load, which
     is exactly the thing B4's control exists to observe - and it did, until
     this was found: the stored-preference case came up still because the
     harness had just turned it off. */
  const openShip = (key, opts = {}) => {
    const spin = ("spin" in opts) ? `spinOn=${!!opts.spin};` : "";
    run(`shipId=${JSON.stringify(key)};reset();resetView();${spin}`
      + VIEW + `_view._s=spinOn;_modelFor=shipId;sel=null;renderAll();`);
  };

  /* Dispatch through the page's own delegated handler, with the element a
     browser would have handed it. `matches` is the set of selectors this
     element should answer `closest()` for. */
  const dispatch = (matches, extra = {}) => {
    const node = {
      tagName: "DIV", dataset: extra.dataset || {},
      parentNode: null,
      classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
      closest: (s) => (matches.includes(s) ? node : null),
      ...extra,
    };
    let threw = null;
    for (const fn of clickHandlers) {
      try { fn({ target: node, preventDefault() {} }); }
      catch (e) { threw = e.message; }
    }
    return threw;
  };

  const key = (k) => {
    let threw = null;
    for (const fn of keyHandlers) {
      try { fn({ key: k, preventDefault() {} }); } catch (e) { threw = e.message; }
    }
    return threw;
  };

  /* WHERE A PICKER ACTUALLY IS, after B2 and B3 gave it three possible homes.
     Reading one of them and calling the other two silent is precisely the
     mistake B0 exists to prevent, so this reads all three and says which. */
  const pickerNow = () => {
    const pane = el("picker").innerHTML || "";
    const panel = el("cc-panel").hidden ? "" : (el("cc-panel").innerHTML || "");
    const col = el("colA").innerHTML || "";
    const i = col.indexOf('class="inlinepick"');
    const inline = i === -1 ? "" : col.slice(i);
    return { pane, panel, inline,
             any: panel || inline || pane,
             where: panel ? "stage" : inline ? "inline" : pane ? "pane" : "none" };
  };

  return {
    g, run, el, openShip, dispatch, key, clickHandlers, keyHandlers, pickerNow,
    session: sandbox.sessionStorage || null,
    SHIPS: g("SHIPS"), PARTS: g("P"), MARKS: g("MARKS"), HPN: g("HPN"),
    META: g("META"),
    /* A slot's `h` is an INDEX into the hardpoint-name table, not the name.
       Comparing it to a string matches nothing, silently. */
    portName: (s) => (g("HPN")[s.h] || ""),
  };
}

/* The reporting half, so every control in this family counts and inverts the
   same way and a reader can compare two runs line for line. */
export function reporter(selftest) {
  const state = { passed: 0, failures: [], notes: [] };
  const record = (got, label, detail = "") => {
    const want = selftest ? !got : got;
    if (want) { state.passed++; console.log(`  ok   ${label}`); }
    else {
      state.failures.push(`${label} ${detail}`.trim());
      console.log(`  FAIL ${label} ${detail}`);
    }
    return !!want;
  };
  const finish = (extra = "") => {
    console.log("\n==========================================================");
    for (const n of state.notes) console.log("  " + n);
    if (state.failures.length) {
      console.log(`\nFAILED: ${state.failures.length} of `
        + `${state.passed + state.failures.length}`);
      for (const f of state.failures) console.log("  " + f);
    } else {
      console.log(`\nAll ${state.passed} assertions passed against the page's `
        + `own script.`);
    }
    if (extra) console.log("\n" + extra);
    process.exit(state.failures.length ? 1 : 0);
  };
  return { record, finish, state };
}
