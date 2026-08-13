/* _verify_poll.js — proves the device poll loop has exactly one owner.

   §3 of the master order. `rafId` had five writers, two of them in the host
   pages, and the symptom was Sleven's: input works, dies, comes back on its
   own, dies again.

   WHAT THIS HARNESS MODELS, AND WHAT IT DOES NOT.

   It drives device_engine.js with a controllable requestAnimationFrame, so
   frames are delivered deliberately rather than by a real clock. That lets it
   reproduce the one interleaving a browser really can produce and
   `cancelAnimationFrame` really cannot prevent: A FRAME THE BROWSER HAS
   ALREADY COMMITTED TO RUNNING. Cancelling an id whose callback is already
   dispatched does nothing, and old-style code re-arms from inside that
   callback — which is a second loop nobody holds a handle on.

   It does NOT claim to reproduce every interleaving in C1's analysis. A
   single-threaded harness cannot land an event in the middle of another
   callback. What it does establish is stronger than a reproduction anyway:
   the invariant "at most one loop, always" is asserted directly, and the
   generation guard that provides it is shown to be load-bearing by removing
   it and watching these checks fail.

       node testing/_src/_verify_poll.js
*/
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ENGINE = path.join(__dirname, 'device_engine.js');
const EXPORT = path.join(__dirname, 'sc_export.js');

function makeWorld(engineSrc) {
  const noop = () => {};
  const el = {
    innerHTML: '', id: '', textContent: '', style: {}, dataset: {},
    classList: { toggle: noop, add: noop, remove: noop },
    appendChild: noop, insertBefore: noop, removeChild: noop,
    addEventListener: noop, closest: () => null, getAttribute: () => null,
    querySelectorAll: () => [], querySelector: () => null, children: []
  };
  const host = Object.assign({}, el);

  /* A frame queue we control. `pending` is what the browser is holding;
     `deliver` runs one callback the way a browser would. */
  const frames = new Map();
  let nextId = 1;

  const pads = [{ index: 0, id: 'VKBsim Gladiator EVO L (Vendor: 231d Product: 0201)',
                  mapping: '', buttons: [], axes: [] }];

  const world = {
    dev: 'JOY', capture: true, OPEN: true, ID_: '', console: console,
    $: () => host,
    navigator: { getGamepads: () => pads },
    localStorage: { getItem: () => null, setItem: noop, removeItem: noop },
    setInterval: () => 0, clearInterval: noop, setTimeout: () => 0,
    requestAnimationFrame: fn => { const id = nextId++; frames.set(id, fn); return id; },
    cancelAnimationFrame: id => { frames.delete(id); },
    CustomEvent: function (n, o) { this.type = n; this.detail = o && o.detail; },
    document: {
      addEventListener: noop, getElementById: () => null,
      createElement: () => Object.assign({}, el),
      head: { appendChild: noop }, body: el,
      querySelector: () => null, querySelectorAll: () => []
    }
  };
  world.window = world;
  world.self = world;
  world.addEventListener = noop;
  world.dispatchEvent = noop;

  const ctx = vm.createContext(world);
  vm.runInContext(fs.readFileSync(EXPORT, 'utf8'), ctx, { filename: 'sc_export.js' });
  vm.runInContext(engineSrc, ctx, { filename: 'device_engine.js' });

  return {
    ctx,
    queued: () => frames.size,
    /* One animation frame, as a browser runs it: the id is retired BEFORE
       the callback runs, because by then the browser has committed. */
    tick() {
      const ids = [...frames.keys()];
      let ran = 0;
      for (const id of ids) {
        const fn = frames.get(id);
        frames.delete(id);
        fn();
        ran++;
      }
      return ran;
    },
    /* Hand back a callback the browser had already dispatched — the exact
       thing cancelAnimationFrame cannot take back. */
    capture() {
      const id = [...frames.keys()][0];
      const fn = frames.get(id);
      return { id, run: () => fn() };
    }
  };
}

function run(engineSrc, label) {
  let failures = 0, checks = 0;
  const check = (name, cond, detail) => {
    checks++;
    if (cond) { console.log('  PASS  ' + name); return; }
    failures++;
    console.log('  FAIL  ' + name + (detail ? '\n          ' + detail : ''));
  };
  console.log('\n== ' + label + ' ==');

  /* ---- one start is one loop ---- */
  {
    const w = makeWorld(engineSrc);
    w.ctx.pollStart();
    check('one start queues exactly one frame', w.queued() === 1, 'queued ' + w.queued());
    check('ten more starts do not queue a second',
          (() => { for (let i = 0; i < 10; i++) w.ctx.pollStart(); return w.queued(); })() === 1,
          'queued ' + w.queued());
    const ran = w.tick();
    check('one frame runs per tick, and re-arms exactly once',
          ran === 1 && w.queued() === 1, 'ran ' + ran + ', queued ' + w.queued());
  }

  /* ---- THE FRAME THE BROWSER ALREADY COMMITTED TO ----
     Stop the loop, then deliver the frame anyway. This is the case
     cancelAnimationFrame cannot cover, and the one that used to leave a live
     callback with rafId===null — after which the next start makes a second
     loop and both re-arm forever. */
  {
    const w = makeWorld(engineSrc);
    w.ctx.pollStart();
    const inFlight = w.capture();
    w.ctx.pollStop();
    check('stopping clears the queue', w.queued() === 0, 'queued ' + w.queued());
    inFlight.run();
    check('an already-dispatched frame does NOT re-arm after a stop',
          w.queued() === 0, 'a superseded frame queued ' + w.queued() + ' more');
    check('and it is counted rather than absorbed in silence',
          w.ctx.ccStaleFrames === 1, 'staleFrames = ' + w.ctx.ccStaleFrames);
    w.ctx.pollStart();
    check('starting again gives exactly ONE loop, not two',
          w.queued() === 1, 'queued ' + w.queued());
    const ran = w.tick();
    check('and exactly one frame runs', ran === 1 && w.queued() === 1,
          'ran ' + ran + ', queued ' + w.queued());
  }

  /* ---- ACCEPTANCE 6: KBM -> JOY -> KBM, ten times ---- */
  {
    const w = makeWorld(engineSrc);
    w.ctx.pollStart();
    w.tick();
    const before = w.ctx.ccPollCount;
    let everTwo = false;
    for (let i = 0; i < 10; i++) {
      w.ctx.dev = 'KBM';
      w.ctx.pollStop();
      if (w.queued() > 1) everTwo = true;
      w.tick();
      w.ctx.dev = 'JOY';
      w.ctx.startPoll();
      if (w.queued() > 1) everTwo = true;
      const ran = w.tick();
      if (ran > 1) everTwo = true;
    }
    check('ten KBM->JOY switches never produce a second loop', !everTwo,
          'more than one frame was live at once');
    check('exactly one loop is running at the end',
          w.ctx.ccDiag().loopRunning === 1 && w.queued() === 1,
          'loopRunning=' + w.ctx.ccDiag().loopRunning + ' queued=' + w.queued());
    check('and the frame counter is still climbing',
          w.ctx.ccPollCount > before,
          'polls went ' + before + ' -> ' + w.ctx.ccPollCount);
  }

  /* ---- the loop must be able to come back ----
     FINDING_device-poll-cannot-restart-2026-08-10: the poll stopped itself
     and the only way back on was a gamepadconnected event. A self-stop must
     leave the loop restartable by an ordinary start. */
  {
    const w = makeWorld(engineSrc);
    w.ctx.pollStart();
    w.ctx.dev = 'KBM';          /* poll() will ask to stop on its next frame */
    w.tick();
    check('a self-stop really stops', w.queued() === 0 && w.ctx.ccDiag().loopRunning === 0,
          'queued ' + w.queued() + ' loopRunning ' + w.ctx.ccDiag().loopRunning);
    w.ctx.dev = 'JOY';
    w.ctx.startPoll();
    check('and the loop can be started again afterwards — it is not one-way',
          w.queued() === 1 && w.ctx.ccDiag().loopRunning === 1,
          'queued ' + w.queued());
  }

  console.log('  ' + (failures ? failures + ' of ' + checks + ' FAILED'
                               : 'all ' + checks + ' passed'));
  return failures;
}

const real = fs.readFileSync(ENGINE, 'utf8');
const realFailures = run(real, 'the shipped engine');

/* ---- and the same suite with the generation guards removed --------------
   BOTH of them. There are two: one refuses a superseded frame on entry, one
   catches a stop that happened DURING the frame. Removing only the first
   left the second covering for it, and the suite still passed — which would
   have been a proof of nothing dressed up as a proof of something. The
   mutant has to be the OLD behaviour: a frame that re-arms regardless of
   whether anybody asked it to stop. */
const GUARDS = ['if(gen !== pollGen){ ccStaleFrames++; return; }',
                'if(gen !== pollGen) return;'];
const missing = GUARDS.filter(g => real.indexOf(g) < 0);
if (missing.length) {
  console.log('\nCANNOT MUTATE: the generation guard no longer looks the way this ' +
              'file expects, so the proof that these checks can fail did NOT run.');
  console.log('  not found: ' + JSON.stringify(missing));
  console.log('Re-point it deliberately. Reporting a failure, because an unproven ' +
              'gate is not a passing one.');
  process.exit(1);
}
console.log('\n--- the same checks, with BOTH generation guards removed ---');
console.log('    (these MUST fail; if they pass, the checks above prove nothing)');
const mutantFailures = run(
  GUARDS.reduce((s, g) => s.replace(g, ''), real),
  'engine with the guards removed');

console.log('');
if (realFailures) {
  console.log('FAILED: ' + realFailures + ' check(s) against the shipped engine.');
  process.exit(1);
}
if (!mutantFailures) {
  console.log('FAILED: the mutant passed everything, so these checks cannot detect ' +
              'the defect they are named after.');
  process.exit(1);
}
console.log('ALL CHECKS PASSED, and the mutant failed ' + mutantFailures +
            ' of them — so the checks can fail.');
process.exit(0);
