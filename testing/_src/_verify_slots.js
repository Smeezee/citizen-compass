/* _verify_slots.js — proves the 1..N slot reconciler by BEHAVIOUR, not by
   reading it.

   RULE 12. A check that cannot fail is not a check. This file exists to be
   run against BOTH versions of device_engine.js:

       node testing/_src/_verify_slots.js                     -> must PASS
       node testing/_src/_verify_slots.js <old device_engine.js> -> must FAIL

   The second form is the whole point. The counter this replaced —
   `rememberSlot(p,(slotOf(p)%8)+1)` — passes no test below, and if a future
   edit reintroduces per-device slot guessing, these assertions go red rather
   than the suite going quiet.

   It runs device_engine.js inside a `vm` context with the smallest browser
   stubs the engine actually touches, so the code under test is the shipped
   file, not a paraphrase of it. */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const HERE = __dirname;
const ENGINE = process.argv[2] || path.join(HERE, 'device_engine.js');
const EXPORT = path.join(HERE, 'sc_export.js');

/* ---- the smallest browser the engine will run in ---------------------- */
function makeWorld(padIds, storedSlots) {
  const store = {};
  if (storedSlots) store['cc.js.slots.v2'] = JSON.stringify(storedSlots);
  /* v1 is seeded too, always. If the engine still reads v1 the version bump
     did not happen, and the "3+ is repaired" case below would pass for the
     wrong reason. */
  if (storedSlots) store['cc.js.slots.v1'] = JSON.stringify(storedSlots);

  const pads = padIds.map((id, i) => ({
    index: i, id: id, mapping: '', buttons: [], axes: []
  }));

  const noop = () => {};
  const el = {
    innerHTML: '', id: '', textContent: '', style: {}, classList: { toggle: noop },
    appendChild: noop, addEventListener: noop, closest: () => null,
    getAttribute: () => null, querySelectorAll: () => [], querySelector: () => null
  };
  /* The panel host. Rendering is allowed to run for real — a crash or a wrong
     control in the generated markup is exactly the sort of thing a test that
     stopped short of rendering would miss. */
  const host = Object.assign({}, el, { querySelectorAll: () => [] });
  const handlers = {};
  const world = {
    dev: 'JOY',
    capture: true,
    OPEN: true,
    ID_: '',
    $: () => host,
    console: console,
    navigator: { getGamepads: () => pads },
    localStorage: {
      getItem: k => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: k => { delete store[k]; }
    },
    setInterval: () => 0,
    clearInterval: noop,
    requestAnimationFrame: () => 1,
    cancelAnimationFrame: noop,
    CustomEvent: function (n, o) { this.type = n; this.detail = o && o.detail; },
    document: {
      addEventListener: (t, fn) => { (handlers[t] = handlers[t] || []).push(fn); },
      getElementById: () => null,
      createElement: () => Object.assign({}, el),
      head: { appendChild: noop },
      body: el,
      querySelector: () => null,
      querySelectorAll: () => []
    }
  };
  world.window = world;
  world.self = world;
  world.globalThis = world;
  world.window.addEventListener = (t, fn) => { (handlers[t] = handlers[t] || []).push(fn); };
  world.window.dispatchEvent = noop;
  world.addEventListener = world.window.addEventListener;

  const ctx = vm.createContext(world);
  vm.runInContext(fs.readFileSync(EXPORT, 'utf8'), ctx, { filename: 'sc_export.js' });
  vm.runInContext(fs.readFileSync(ENGINE, 'utf8'), ctx, { filename: path.basename(ENGINE) });
  return { ctx, pads, store, handlers, host };
}

/* Slot for every connected stick, in pad order. Read through the same
   `slotOf` the panel, the prefix and the export all read through — asking a
   private variable instead would test something nobody uses. */
function slotsOf(w) {
  return w.pads.map(p => w.ctx.slotOf(p));
}

/* Click the swap control the way a person does: through the delegated
   document handler, not by calling an internal. Returns nothing; the point
   is that the observable state moves (or is explained). */
function clickSwap(w, padIndex) {
  const target = {
    closest: sel => (sel === '.cc-slot'
      ? { getAttribute: a => (a === 'data-slot' ? String(padIndex) : null) }
      : null)
  };
  (w.handlers.click || []).forEach(fn => fn({ target }));
}

/* ---- assertions -------------------------------------------------------- */
let failures = 0, checks = 0;
function check(name, cond, detail) {
  checks++;
  if (cond) { console.log('  PASS  ' + name); return; }
  failures++;
  console.log('  FAIL  ' + name + (detail ? '\n          ' + detail : ''));
}
function isPermutationOf1toN(slots) {
  const n = slots.length, seen = new Set(slots);
  if (seen.size !== n) return false;
  for (let i = 1; i <= n; i++) if (!seen.has(i)) return false;
  return true;
}

const VKB_L = 'VKBsim Gladiator EVO L (Vendor: 231d Product: 0201)';
const VKB_R = 'VKBsim Gladiator EVO R (Vendor: 231d Product: 0200)';
const VKB_3 = 'VKBsim Gladiator EVO 3 (Vendor: 231d Product: 0202)';

console.log('\n== Acceptance 0: one stick, fresh browser ==');
{
  const w = makeWorld([VKB_L], null);
  check('a lone stick is js1', slotsOf(w)[0] === 1, 'got js' + slotsOf(w)[0]);
  clickSwap(w, 0);
  check('swap on a lone stick does NOT produce js2', slotsOf(w)[0] === 1,
        'got js' + slotsOf(w)[0] + ' after one click');
  for (let i = 0; i < 10; i++) clickSwap(w, 0);
  check('ten clicks on a lone stick leave it js1', slotsOf(w)[0] === 1,
        'got js' + slotsOf(w)[0] + ' after eleven clicks');
  check('and the page states why nothing happened',
        typeof w.ctx.slotNote === 'string' && /nothing to swap/i.test(w.ctx.slotNote),
        'slotNote was ' + JSON.stringify(w.ctx.slotNote));
  w.ctx.renderDevice();
  check('the control renders DISABLED rather than inviting a dead click',
        /<button class="slotswap" disabled/.test(w.host.innerHTML),
        'the rendered swap control was not disabled');
}

console.log('\n== Acceptance 1: two sticks swap, and only ever swap ==');
{
  const w = makeWorld([VKB_L, VKB_R], null);
  check('two sticks come up js1 and js2',
        String(slotsOf(w)) === '1,2', 'got ' + slotsOf(w));
  clickSwap(w, 0);
  check('one click exchanges them', String(slotsOf(w)) === '2,1',
        'got ' + slotsOf(w));
  const seen = new Set([String(slotsOf(w))]);
  let everOutOfRange = false;
  for (let i = 0; i < 10; i++) {
    clickSwap(w, 0);
    const s = slotsOf(w);
    seen.add(String(s));
    if (!isPermutationOf1toN(s)) everOutOfRange = true;
  }
  check('ten more clicks visit exactly two states',
        seen.size === 2, 'visited ' + [...seen].join('  |  '));
  check('NO js3, EVER — every state is a permutation of 1..2',
        !everOutOfRange, 'a state outside 1..2 occurred');
}

console.log('\n== Acceptance 2: a stored slot of 3+ is repaired on load ==');
{
  /* Exactly the state sitting in his friend's browser: the counter walked a
     lone stick up to js5 and localStorage kept it. */
  const w = makeWorld([VKB_L], { '231d:0201': 5 });
  check('a stored js5 is not obeyed for a single stick', slotsOf(w)[0] === 1,
        'got js' + slotsOf(w)[0]);
  const stored = JSON.parse(w.store['cc.js.slots.v2'] || '{}');
  check('and the corrected value is re-stored, not merely ignored',
        stored['231d:0201'] === 1,
        'localStorage still holds ' + JSON.stringify(stored));
}
{
  const w = makeWorld([VKB_L, VKB_R], { '231d:0201': 7, '231d:0200': 4 });
  check('two sticks with two out-of-range stored slots reconcile to 1..2',
        isPermutationOf1toN(slotsOf(w)), 'got ' + slotsOf(w));
}
{
  /* Both devices remembering the SAME slot. A per-device answer cannot see
     this; it is the collision case the reconciler exists for. */
  const w = makeWorld([VKB_L, VKB_R], { '231d:0201': 1, '231d:0200': 1 });
  check('two sticks both remembering js1 do not both get js1',
        isPermutationOf1toN(slotsOf(w)), 'got ' + slotsOf(w));
}

console.log('\n== Three sticks: still a permutation, every single click ==');
{
  const w = makeWorld([VKB_L, VKB_R, VKB_3], null);
  check('three sticks come up 1,2,3', String(slotsOf(w)) === '1,2,3',
        'got ' + slotsOf(w));
  let bad = null, exchangesOfTwo = true;
  for (let i = 0; i < 12; i++) {
    const before = slotsOf(w);
    clickSwap(w, i % 3);
    const after = slotsOf(w);
    if (!isPermutationOf1toN(after) && !bad) bad = after;
    /* An exchange moves exactly two devices. A cycle would move three. */
    const moved = before.filter((v, k) => v !== after[k]).length;
    if (moved !== 2) exchangesOfTwo = false;
  }
  check('twelve clicks never leave 1..3', !bad, 'reached ' + bad);
  check('every click exchanges exactly two slots — so "swap" is a true label',
        exchangesOfTwo, 'a click moved a number of devices other than two');
}

console.log('\n== Unplugging: 1..N means something else now ==');
{
  const w = makeWorld([VKB_L, VKB_R], null);
  clickSwap(w, 0);                       /* L is now js2, remembered */
  check('L remembers js2 before the unplug', w.ctx.slotOf(w.pads[0]) === 2,
        'got js' + w.ctx.slotOf(w.pads[0]));
  w.pads.pop();                          /* R goes away */
  (w.handlers.gamepaddisconnected || []).forEach(fn => fn({ gamepad: { index: 1 } }));
  check('with R gone, L is js1 — a remembered js2 is no longer legal',
        w.ctx.slotOf(w.pads[0]) === 1, 'got js' + w.ctx.slotOf(w.pads[0]));
}

/* ---- §5: a stick that reports 128 buttons ----------------------------
   128 is the HID report size, not a count of physical controls — a Gladiator
   has about thirteen. The order asks to CONFIRM that "Hide unused buttons"
   defaults sensibly for a device like that, so this establishes what the
   default actually does rather than reasoning about it. */
console.log('\n== A stick reporting 128 buttons ==');
{
  const w = makeWorld([VKB_L], null);
  /* applyVis reads devDom, which a real render fills from the DOM. The stub
     host returns no elements, so the tiles are supplied directly — the
     function under test is still the shipped one. */
  const tiles = {};
  for (let i = 0; i < 128; i++) {
    tiles['0:' + i] = { ix: i, everPressed: false, vis: null, el: { style: {} } };
  }
  w.ctx.devDom = { btn: tiles, ax: {}, chip: {} };

  w.ctx.applyVis();
  const shownByDefault = Object.values(tiles).filter(t => t.vis).length;
  check('the default shows the first 40 of 128, not all 128',
        shownByDefault === 40, 'showed ' + shownByDefault);

  /* THE REASON THE DEFAULT IS WHAT IT IS. "Unused" means "not pressed since
     the page loaded", and at load NOTHING has been pressed — so defaulting
     this ON would render an empty button grid, which reads as "the page
     cannot see my stick". That is the exact complaint this whole area of the
     page exists to answer, so the default must stay OFF. */
  w.ctx.hideUnused = true;
  w.ctx.applyVis();
  const shownIfHidingUnused = Object.values(tiles).filter(t => t.vis).length;
  check('turning "Hide unused buttons" ON before anything is pressed hides ' +
        'EVERY button — which is why it must not be the default',
        shownIfHidingUnused === 0, 'showed ' + shownIfHidingUnused);

  /* And the escape hatch works: a button above the cap appears on press. */
  w.ctx.hideUnused = false;
  tiles['0:97'].everPressed = true;
  w.ctx.applyVis();
  check('a button above the cap appears the moment it is pressed',
        tiles['0:97'].vis === true);
}

console.log('\n' + (failures ? 'FAILED ' + failures + ' of ' + checks + ' checks'
                             : 'ALL ' + checks + ' CHECKS PASSED'));
process.exit(failures ? 1 : 0);
