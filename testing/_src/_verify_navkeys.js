/* _verify_navkeys.js — End / Home / Page Up / Page Down scroll the tester,
   and a deliberate rebind still binds them.

   §4 of the master order said to VERIFY the behaviour rather than assume it
   was done, because two greppable hits existed. Both of those hits made it
   worse: `CODE['End']` resolving is precisely why the handler called
   preventDefault on it. This asserts what the page actually does.

   It slices the REAL handler registrations out of keybinds.src.html and runs
   that source text, stubbing only what the handlers reach for. Restating the
   logic here would test a paraphrase, which is worth nothing.

       node testing/_src/_verify_navkeys.js
*/
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const PAGE = path.join(__dirname, 'keybinds.src.html');

const START = '/* THE PAGE HAS TO STILL BE READABLE WHILE IT IS LISTENING.';
const END = "setMods();render();},{capture:true});";

function handlerSource() {
  const html = fs.readFileSync(PAGE, 'utf8');
  const a = html.indexOf(START);
  if (a < 0) throw new Error('the nav-key comment marker is gone from keybinds.src.html');
  /* The SECOND occurrence of END closes the keyup handler; the first closes
     keydown. */
  const b1 = html.indexOf(END, a);
  const b2 = html.indexOf(END, b1 + 1);
  if (b1 < 0 || b2 < 0) throw new Error('could not find both handler registrations');
  return html.slice(a, b2 + END.length);
}

function makeWorld(src, opts) {
  const events = [];
  const world = {
    console,
    dev: 'KBM',
    capture: true,
    modeIx: 0,
    MODES: [{ data: {}, label: 'Flight' }],
    /* Only the four keys under test plus one ordinary key as a control. */
    CODE: { End: 'End', Home: 'Home', PageUp: 'PgUp', PageDown: 'PgDn', KeyA: 'A' },
    down: new Set(),
    held: {},
    lastTap: {},
    setMods: () => {},
    render: () => {},
    fire: () => {},
    performance: { now: () => 0 },
    addEventListener: (t, fn) => { events.push([t, fn]); }
  };
  world.window = world;
  world.KBREBIND = opts.rebinding
    ? { listening: () => true }
    : { listening: () => false };
  const ctx = vm.createContext(world);
  vm.runInContext(src, ctx, { filename: 'keybinds-navkeys' });
  return { ctx, events };
}

/* Fire a real-shaped event at both registered handlers and report whether
   anybody stopped the browser's default — which IS the scroll. */
function press(w, code) {
  let prevented = false;
  const ev = {
    code, repeat: false, button: 0,
    preventDefault: () => { prevented = true; },
    stopPropagation: () => {}
  };
  w.events.forEach(([t, fn]) => { if (t === 'keydown') fn(ev); });
  const up = {
    code, repeat: false,
    preventDefault: () => { prevented = true; },
    stopPropagation: () => {}
  };
  w.events.forEach(([t, fn]) => { if (t === 'keyup') fn(up); });
  return prevented;
}

let failures = 0, checks = 0;
function check(name, cond, detail) {
  checks++;
  if (cond) { console.log('  PASS  ' + name); return; }
  failures++;
  console.log('  FAIL  ' + name + (detail ? '\n          ' + detail : ''));
}

const SRC = handlerSource();

console.log('\n== Capture ON, nothing listening: the page must still scroll ==');
{
  const w = makeWorld(SRC, { rebinding: false });
  check('two handlers were registered', w.events.length === 2,
        'registered ' + w.events.length);
  ['End', 'Home', 'PageUp', 'PageDown'].forEach(code => {
    check(code + ' is left alone, so the page scrolls', press(w, code) === false,
          code + ' was still preventDefault()ed');
  });
  check('an ordinary key is STILL captured — the tester has not been disabled',
        press(w, 'KeyA') === true,
        'KeyA was not preventDefault()ed, so the tester would miss it');
}

console.log('\n== A cell is listening: a deliberate rebind outranks scrolling ==');
{
  const w = makeWorld(SRC, { rebinding: true });
  ['End', 'Home', 'PageUp', 'PageDown'].forEach(code => {
    check(code + ' is captured while rebinding, so it can be bound',
          press(w, code) === true,
          code + ' was allowed to scroll instead of being bound');
  });
}

/* ---- and the proof these checks can fail (rule 12) ---------------------- */
const GUARD = 'if(!navMayScroll(e))e.preventDefault();';
if (SRC.split(GUARD).length - 1 !== 2) {
  console.log('\nCANNOT MUTATE: expected the guard on both handlers, so the proof ' +
              'that these checks can fail did NOT run. Re-point it deliberately.');
  process.exit(1);
}
console.log('\n--- the same checks, with the old unconditional preventDefault ---');
console.log('    (the scrolling ones MUST fail)');
{
  const w = makeWorld(SRC.split(GUARD).join('e.preventDefault();'), { rebinding: false });
  let mutantFailures = 0;
  ['End', 'Home', 'PageUp', 'PageDown'].forEach(code => {
    if (press(w, code) !== false) mutantFailures++;
  });
  console.log('  ' + mutantFailures + ' of 4 nav keys swallowed by the old code');
  if (mutantFailures !== 4) {
    console.log('\nFAILED: the old behaviour did not fail these checks, so they ' +
                'prove nothing.');
    process.exit(1);
  }
}

console.log('\n' + (failures ? 'FAILED ' + failures + ' of ' + checks + ' checks'
                             : 'ALL ' + checks + ' CHECKS PASSED, and the old behaviour fails them'));
process.exit(failures ? 1 : 0);
