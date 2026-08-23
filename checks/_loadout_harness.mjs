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

  /* E11: CHILDREN ARE REAL NOW, AND THE OLD STUB IS WHY THEY HAD TO BE.
     `children` returned [] and `childElementCount` returned 0, always. That is
     not a simplification - it silently disabled a whole code path. renderMarkers
     writes its markup ONCE and then positions the elements every frame through
     `box.children`; against the old stub the write happened and THE ENTIRE
     POSITIONING LOOP WAS SKIPPED, on every control that has ever driven this
     page. No check has ever seen where a marker was put.
     E11 is a defect about exactly that - labels placed and abandoned while the
     hull turns - so a stub that cannot observe positions could not have caught
     it and cannot verify the fix.
     Top-level tags only. This is not a parser and does not pretend to be one:
     it reads the opening tags a render emits, keeps their attributes, and gives
     each one a `style` object the page can write into. Nesting is ignored,
     which is honest for the two layers that use it - markers are flat buttons
     and leader lines are flat <line> elements. */
  const TAG = /<(div|button|line|span)\b([^>]*?)(\/?)>/gi;
  const ATTR = /([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*"([^"]*)"/g;
  function parseChildren(html) {
    const out = [];
    let m;
    TAG.lastIndex = 0;
    while ((m = TAG.exec(String(html || "")))) {
      /* ENTITIES ARE DECODED, BECAUSE A BROWSER DECODES THEM. An attribute
         written `data-text="M2C &quot;Swarm&quot;"` reaches the page as
         `M2C "Swarm"`, and a control measuring the raw string would measure a
         name eight characters longer than the one on screen - which is exactly
         what it did, and it reported five label overlaps that were not there.
         Decoding here rather than in each control keeps one answer to "what
         does this attribute say". */
      const unent = (v) => String(v)
        .replace(/&quot;/g, '"')
        .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
        .replace(/&#(\d+);/g, (_, d) => String.fromCharCode(Number(d)))
        .replace(/&amp;/g, "&");
      const attrs = {};
      let a;
      ATTR.lastIndex = 0;
      while ((a = ATTR.exec(m[2]))) attrs[a[1].toLowerCase()] = unent(a[2]);
      const style = {};
      for (const part of String(attrs.style || "").split(";")) {
        const i = part.indexOf(":");
        if (i > 0) {
          style[part.slice(0, i).trim()] = part.slice(i + 1).trim();
        }
      }
      const dataset = {};
      for (const k of Object.keys(attrs)) {
        if (k.indexOf("data-") === 0) dataset[k.slice(5)] = attrs[k];
      }
      const node = {
        tagName: m[1].toUpperCase(), _attrs: attrs, style, dataset,
        className: attrs.class || "",
        classList: {
          add(c) { if (!node.className.split(/\s+/).includes(c)) {
            node.className = (node.className + " " + c).trim(); } },
          remove(c) { node.className = node.className.split(/\s+/)
            .filter((x) => x && x !== c).join(" "); },
          toggle(c, on) { const has = node.className.split(/\s+/).includes(c);
            const want = (on === undefined) ? !has : !!on;
            if (want) node.classList.add(c); else node.classList.remove(c); },
          contains(c) { return node.className.split(/\s+/).includes(c); },
        },
        getAttribute(k) { return node._attrs[String(k).toLowerCase()]; },
        setAttribute(k, v) { node._attrs[String(k).toLowerCase()] = String(v); },
      };
      out.push(node);
    }
    return out;
  }

  const els = new Map();
  const el = (id) => {
    if (!els.has(id)) {
      const node = {
        id, textContent: "", className: "", value: "",
        style: {}, onclick: null, onchange: null, href: "", hidden: false,
        classList: { add() {}, remove() {}, toggle() {} },
        removeAttribute(a) { this[a] = ""; },
        setAttribute(a, v) { this[a] = v; },
        _html: "", _kids: [],
        /* Reparsed on write, and NOT on read: the page positions children by
           mutating their style AFTER the write, and re-parsing on every read
           would throw those mutations away - which would leave this stub
           reporting the markup's original numbers no matter what the page did
           to them. That would be the same blindness in a new place. */
        get innerHTML() { return this._html; },
        set innerHTML(v) { this._html = String(v); this._kids = parseChildren(v); },
        get childElementCount() { return this._kids.length; },
        get children() { return this._kids; },
        /* A STATED STAGE SIZE, so B3's placement maths runs on real numbers
           rather than on zero. 960x540 is a plausible desktop stage and it is
           a STUB, not a measurement: nothing here proves the panel fits a real
           viewport, only that the arithmetic places it inside the box it was
           given. The pure function is driven separately with its own numbers,
           including numbers chosen to make it flip. */
        clientWidth: 960, clientHeight: 540,
      };
      els.set(id, node);
    }
    return els.get(id);
  };

  let currentHash = "";
  const clickHandlers = [];
  const keyHandlers = [];
  const inputHandlers = [];
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
        /* H1f's sliders are `input`, not `click` - a control that only
           captured clicks could not reach them at all. */
        if (t === "input") inputHandlers.push(fn);
      },
      querySelector: () => null,
      /* H1g: THE ROOT ELEMENT, BECAUSE THE DIM IS WRITTEN ONTO IT.
         CC_THEME sets one custom property per token on documentElement.style.
         Recording them rather than discarding them is what lets a control
         assert the page APPLIED the palette, separately from asserting that
         palette() computed a good one - a build where apply() writes nothing
         passes every arithmetic assertion and dims not one pixel. */
      documentElement: {
        _props: {}, _attrs: {},
        style: {
          setProperty(k, v) { this._props[k] = String(v); },
          getPropertyValue(k) { return this._props[k] || ""; },
          _props: {},
        },
        setAttribute(k, v) { this._attrs[k] = String(v); },
        getAttribute(k) { return this._attrs[k] || null; },
      },
    },
  };
  sandbox.document.documentElement.style._props =
    sandbox.document.documentElement._props;
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
  const entry = blocks.findIndex((b) => /function renderAll\s*\(/.test(b));
  if (entry < 0) {
    console.log("NO PAGE SCRIPT FOUND - none of the " + blocks.length
      + " inline <script> blocks defines renderAll(). Refusing to assert "
      + "against a page this cannot drive.");
    process.exit(2);
  }
  /* H1g: THE PAGE'S OWN SCRIPT IS NOW MORE THAN ONE BLOCK.
     CC_THEME has to run in the HEAD - a returning visitor with Blackout saved
     would otherwise get one frame of a full-brightness page in the dark, which
     is the exact injury the feature exists to prevent - so the page carries a
     head block and an end-of-body block. Taking only the block with
     renderAll() in it would leave every control driving a page where CC_THEME
     does not exist, and the first symptom would be controls that pass while
     the palette is never applied.
     Every block from the head down to the entry point is run, in document
     order, exactly as a browser would. Vendor blocks stay excluded because
     they are all AFTER the entry point in the built page - three.js and the
     DRACO decoder are appended, not prepended - and running a megabyte of
     vendor code against a DOM stub is what the original filter was for. */
  const preamble = blocks.slice(0, entry);
  let script = blocks[entry];
  /* MUTATIONS APPLY ACROSS EVERY BLOCK THAT RUNS, not only the entry point.
     H1g's palette lives in the head block, and a `--mutate-oldpalette` that
     silently matched nothing in the entry block would have left the mutated
     run identical to the clean one - a negative control that cannot plant its
     defect, reporting a pass. The "matched nothing" refusal is therefore
     across the set: a pattern must land somewhere. */
  for (const [pattern, replacement] of mutate) {
    let hit = false;
    for (let i = 0; i < preamble.length; i++) {
      const before = preamble[i];
      preamble[i] = preamble[i].replace(pattern, replacement);
      if (preamble[i] !== before) hit = true;
    }
    const before = script;
    script = script.replace(pattern, replacement);
    if (script !== before) hit = true;
    if (!hit) {
      console.log(`MUTATION DID NOT APPLY - ${pattern} matched nothing in any `
        + `of the ${preamble.length + 1} script blocks, so this run proves `
        + `nothing. Fix the mutator before trusting the check.`);
      process.exit(1);
    }
  }

  vm.runInContext(dataJs, sandbox, { filename: "loadout_data.gen.js" });
  for (const s of EXTRA) vm.runInContext(s, sandbox, { filename: "gen" });
  for (let i = 0; i < preamble.length; i++) {
    vm.runInContext(preamble[i], sandbox,
      { filename: `loadout.src.html:head[${i}]` });
  }
  vm.runInContext(script, sandbox, { filename: "loadout.src.html:script" });
  const g = (expr) => vm.runInContext(expr, sandbox);
  const run = (stmt) => vm.runInContext(stmt, sandbox);

  /* A STUB VIEWER. The marker layer will not render without one, and where a
     point projects to is irrelevant to every question these controls ask. */
  const VIEW = `_view={_s:false,boot(){},start(){},size(){},cancel(){},`
    + `clear(){},stop(){},current:{},unitScale(){return 1;},`
    /* A REAL PROJECTION, not a constant. It returned {640,360} for every
       marker, which is fine for "did a click reach the handler" and
       useless for anything spatial: H1b's labels all landed on one
       point and the layout looked broken when it was the stub. This is
       an orthographic map of the hull's unit coordinates onto a 960x540
       stage - deterministic, and it separates markers that are apart on
       the hull. */
    + `project(x,y,z){return{x:480+x*430,y:270-y*250,depth:z*0.5};},`
    + `spinning(){return this._s;},setSpin(v){this._s=!!v;return this._s;},`
    /* E4: the page tells the viewer how much of the stage a panel is
       covering. Recorded rather than swallowed, so a control can assert that
       the page asked - and asked for the right amount. */
    + `_obs:0,setObstruction(f){this._obs=Math.max(0,Math.min(0.8,Number(f)||0));`
    + `return this._obs;},obstruction(){return this._obs;},`
    /* H1f: the look API. A STUB, and it records what the page asked for.
       Whether the real viewer's passes actually change is
       _verify_holo_render.mjs's question, against the real module; this one's
       question is whether the PAGE builds the controls and calls them. Two
       different claims and they need two different harnesses. */
    + `style:'solidlines',_col:0xffb545,_sl:{lineInt:1,detail:24,glow:0.55},`
    + `_grid:true,_scan:false,calls:[],`
    + `modes(){return [['panel','Panel lines'],['solidlines','Solid + lines'],`
    + `['solid','Solid holo'],['hull','Lit hull'],['wire','Wireframe'],`
    + `['points','Points']];},`
    + `colours(){return [0x5fd8ee,0x7dffb4,0xffb545,0xff6b8a,0xe8f4ff];},`
    + `setStyle(s){this.calls.push('style:'+s);this.style=s;return s;},`
    + `colour(){return this._col;},`
    + `setColour(c){this.calls.push('colour:'+c);this._col=c;return c;},`
    + `slider(k){return this._sl[k];},`
    + `setSlider(k,v){this.calls.push('slider:'+k+'='+v);this._sl[k]=v;return v;},`
    + `gridOn(){return this._grid;},`
    + `setGrid(v){this.calls.push('grid:'+!!v);this._grid=!!v;return this._grid;},`
    + `scanlines(){return this._scan;},`
    + `setScanlines(v){this.calls.push('scan:'+!!v);this._scan=!!v;return this._scan;},`
    + `remember(){this.calls.push('remember');return true;},`
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
    g, run, el, openShip, dispatch, key, clickHandlers, keyHandlers,
    inputHandlers, pickerNow,
    session: sandbox.sessionStorage || null,
    /* What the page WROTE onto the root element, and what it stamped there.
       Read back rather than inferred, so "the palette was applied" is a
       measurement of the page's own effect. */
    rootProps: sandbox.document.documentElement._props,
    rootAttr: (k) => sandbox.document.documentElement.getAttribute(k),
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
