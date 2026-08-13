/* _verify_conflict.js — proves the binding-conflict check by behaviour.

   THE BUG THIS EXISTS FOR IS REAL AND SHIPPED. The first profile this tool
   produced for real hardware bound one button to two actions that are both
   live while you are sat in the seat:

     js3_button29 -> v_flightready   (spaceship_general)
     js3_button29 -> v_atc_request   (spaceship_movement)

   Nothing warned, because the check only ever looked inside a single
   actionmap. Every conflict that matters in flight crosses actionmaps.

   RULE 12. This file does not merely assert the fix; it re-runs the whole
   suite against a MUTATED copy of the same source with the fix removed, and
   fails if that copy passes. A check that has never seen its subject broken
   is not yet known to work.

       node testing/_src/_verify_conflict.js

   It extracts the live KBEDIT module out of keybinds.src.html rather than
   restating it, so what is tested is what ships. */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const HERE = path.join(__dirname);
const PAGE = path.join(HERE, 'keybinds.src.html');
const MODES = path.join(HERE, 'kb_modes.gen.js');
const EXPORT = path.join(HERE, 'sc_export.js');

/* ---- pull the real module out of the page ----------------------------- */
function kbeditSource() {
  const html = fs.readFileSync(PAGE, 'utf8');
  const start = html.indexOf('window.KBEDIT = (function(){');
  if (start < 0) throw new Error('KBEDIT no longer starts with its marker in keybinds.src.html');
  const end = html.indexOf('\n})();', start);
  if (end < 0) throw new Error('could not find the end of the KBEDIT module');
  return html.slice(start, end + '\n})();'.length);
}

/* KB_CATEGORIES is a top-level `const`, so it is lexical to its own script
   and invisible across vm scripts. Concatenating puts everything in one
   scope — which is also how the browser sees it. */
function load(kbedit) {
  const ctx = vm.createContext({ console });
  ctx.window = ctx;
  vm.runInContext(
    fs.readFileSync(EXPORT, 'utf8') + '\n' +
    fs.readFileSync(MODES, 'utf8') + '\n' +
    kbedit, ctx, { filename: 'kbedit-under-test' });
  return ctx.KBEDIT;
}

/* ---- the fixtures ------------------------------------------------------
   Real actionmaps and real categories, from the game's own data:
     spaceship_general  @ui_CCSpaceFlight
     spaceship_movement @ui_CCSpaceFlight   <- live together
     player             @ui_CCFPS           <- not live with either
     spaceship_auto_weapons  null           <- CIG publishes no category  */
const BINDS = [
  { map: 'spaceship_general',  action: 'v_flightready', input: 'js1_button29' },
  { map: 'spaceship_general',  action: 'v_eject',       input: 'js1_button4'  },
  { map: 'player',             action: 'v_use',         input: 'js1_button29' },
  { map: 'spaceship_auto_weapons', action: 'v_auto_x',  input: 'js1_button7'  }
];

function run(kbedit, label) {
  const KBEDIT = load(kbedit);
  KBEDIT.load({ profileName: 'test', devices: [], binds: BINDS });

  let failures = 0, checks = 0;
  const check = (name, cond, detail) => {
    checks++;
    if (cond) { console.log('  PASS  ' + name); return; }
    failures++;
    console.log('  FAIL  ' + name + (detail ? '\n          ' + detail : ''));
  };

  console.log('\n== ' + label + ' ==');

  /* THE ONE THAT SHIPPED BROKEN. */
  const across = KBEDIT.conflict('spaceship_movement', 'v_atc_request', 'js1_button29');
  check('a button already used in spaceship_general is flagged when bound in ' +
        'spaceship_movement — both are live in flight',
        !!across && across.action === 'v_flightready',
        'conflict() returned ' + JSON.stringify(across));
  check('and it names the other actionmap, because "already Flight Ready" alone ' +
        'reads like a mistake on this screen',
        !!across && across.map === 'spaceship_general' && across.sameMap === false,
        JSON.stringify(across));

  /* The behaviour that already worked and must not regress. */
  const within = KBEDIT.conflict('spaceship_general', 'v_atc_request', 'js1_button4');
  check('a conflict inside one actionmap is still caught',
        !!within && within.action === 'v_eject' && within.sameMap === true,
        JSON.stringify(within));

  /* Not everything that shares a token is a conflict. A warning that fires on
     things that are never live together is a warning people learn to ignore. */
  const unrelated = KBEDIT.conflict('player', 'v_emote', 'js1_button4');
  check('a token reused in an actionmap that is NOT live alongside is not flagged',
        unrelated === null,
        JSON.stringify(unrelated));

  const free = KBEDIT.conflict('spaceship_movement', 'v_roll', 'js1_button99');
  check('an unused input is not a conflict', free === null, JSON.stringify(free));

  const self = KBEDIT.conflict('spaceship_general', 'v_flightready', 'js1_button29');
  check('an action is not in conflict with itself', self === null, JSON.stringify(self));

  /* A LIMIT, ASSERTED SO IT STAYS VISIBLE rather than being discovered later.
     CIG publishes no category for spaceship_auto_weapons, so we have no
     evidence it is live with spaceship_movement and do not claim it is. */
  const noCat = KBEDIT.conflict('spaceship_movement', 'v_roll', 'js1_button7');
  check('KNOWN GAP: a map CIG gives no category is only checked against itself',
        noCat === null,
        'if this now returns a conflict, someone added a simultaneity source — ' +
        'update this check deliberately rather than deleting it');

  console.log('  ' + (failures ? failures + ' of ' + checks + ' FAILED'
                               : 'all ' + checks + ' passed'));
  return failures;
}

/* ---- the real thing ---------------------------------------------------- */
const real = kbeditSource();
const realFailures = run(real, 'the shipped KBEDIT');

/* ---- and the same suite with the fix taken back out --------------------- */
const MUTATION = 'var together = (b.map===map) ||';
if (real.indexOf(MUTATION) < 0) {
  console.log('\nCANNOT MUTATE: the cross-actionmap test no longer looks the way ' +
              'this file expects, so the proof that these checks can fail did NOT run.');
  console.log('Re-point the mutation deliberately. Reporting this as a failure, ' +
              'because an unproven gate is not a passing one.');
  process.exit(1);
}
const mutant = real.replace(MUTATION, 'var together = (b.map===map) || false &&');
console.log('\n--- the same checks, with cross-actionmap detection removed ---');
console.log('    (these MUST fail; if they pass, the checks above prove nothing)');
const mutantFailures = run(mutant, 'KBEDIT with the fix removed');

console.log('');
if (realFailures) {
  console.log('FAILED: ' + realFailures + ' check(s) against the shipped module.');
  process.exit(1);
}
if (!mutantFailures) {
  console.log('FAILED: the mutant passed every check, so these checks cannot ' +
              'detect the bug they are named after.');
  process.exit(1);
}
console.log('ALL CHECKS PASSED, and the mutant failed ' + mutantFailures +
            ' of them — so the checks can fail.');
process.exit(0);
