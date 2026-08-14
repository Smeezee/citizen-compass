/* _verify_loadout_data.js — the loadout dataset must be renderable.

   This page went from four hand-typed ships to 316 real ones, and the data has
   never been through a browser. The failure that matters is not a crash: it is
   a slot pointing at a component that is not in the parts table, which renders
   as the word "empty" on a ship that definitely has guns and looks like a data
   problem nobody can locate.

   So this checks the things the page assumes and cannot check for itself:

     - every slot's `stock` key exists in LOADOUT_PARTS
     - every part carries the fields the page reads for its type
     - the default ship the page picks actually has a loadout
     - CIG's own aggregates are present and are not silently zero
     - the pilot-DPS exclusion reproduces CIG's figure (the proven rule)

   Run:  node testing/_src/_verify_loadout_data.js
         node testing/_src/_verify_loadout_data.js --prove   (rule 12)
*/
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const GEN = path.join(__dirname, 'loadout_data.gen.js');

/* `const` at the top level of a vm script is lexical, not a property of the
   context - so reading ctx.LOADOUT_PARTS afterwards returns undefined. The
   export has to happen INSIDE the same script, where the bindings are in
   scope. Same trap the keybind harness hit with KB_CATEGORIES. */
const ctx = vm.createContext({ out: null });
vm.runInContext(
  fs.readFileSync(GEN, 'utf8') +
  ';out = {LOADOUT_PARTS, LOADOUT_SHIPS, LOADOUT_UNRELEASED, LOADOUT_META};',
  ctx, { filename: 'loadout_data.gen.js' });
const PARTS = ctx.out.LOADOUT_PARTS, SHIPS = ctx.out.LOADOUT_SHIPS;
const UNRELEASED = ctx.out.LOADOUT_UNRELEASED, META = ctx.out.LOADOUT_META;

const prove = process.argv.includes('--prove');

let failures = 0, checks = 0;
function check(name, ok, detail) {
  checks++;
  if (ok) { console.log('  PASS  ' + name); return; }
  failures++;
  console.log('  FAIL  ' + name + (detail ? '\n          ' + detail : ''));
}

console.log('\n== the file loaded and is the right shape ==');
check('all four globals are defined',
      !!(PARTS && SHIPS && UNRELEASED && META),
      'one of LOADOUT_PARTS/SHIPS/UNRELEASED/META is missing');
check('it names its snapshot and patch, on the data not just in a comment',
      !!(META.snapshot && META.last_verified_patch),
      JSON.stringify(META));
/* The bound is "this file is not empty or truncated", not a target. It was
   >500 parts when turret MOUNTS were being emitted as weapons; removing those
   471 statless entries dropped the real count to 470, so the old bound was
   measuring the bug rather than the data. 400 is comfortably below the real
   figure and still catches a generator that produced almost nothing. */
check('a real number of ships and parts',
      Object.keys(SHIPS).length > 300 && Object.keys(PARTS).length > 400,
      Object.keys(SHIPS).length + ' ships, ' + Object.keys(PARTS).length + ' parts');

console.log('\n== every slot points at a part that exists ==');
{
  const missing = [];
  let slots = 0;
  for (const [id, s] of Object.entries(SHIPS)) {
    for (const sl of s.slots || []) {
      slots++;
      // --prove: pretend one key was mistyped, which is the actual failure
      // mode - a generator change that renames keys without renaming
      // references.
      const key = (prove && slots === 1) ? sl.stock + '_TYPO' : sl.stock;
      if (!PARTS[key]) missing.push(s.n + ' / ' + sl.id + ' -> ' + key);
    }
  }
  check('a real number of slots exist at all', slots > 2000, slots + ' slots');
  check('NO slot references a part that is not in the table',
        missing.length === 0,
        missing.length + ' dangling: ' + missing.slice(0, 3).join('; '));
}

console.log('\n== parts carry what the page reads for their type ==');
{
  const needs = { wpn: 'dps', shd: 'ehp', pow: 'cap', col: 'cool', qtm: 'qt' };
  const gaps = {};
  for (const [k, p] of Object.entries(PARTS)) {
    const want = needs[p.t];
    if (!p.n || !p.m) { (gaps.name = gaps.name || []).push(k); }
    if (want && p[want] === undefined) (gaps[p.t] = gaps[p.t] || []).push(k);
  }
  check('every part has a name and a manufacturer',
        !gaps.name, (gaps.name || []).length + ' without');
  // A gap here is reported rather than fatal: a shield with no MaxShieldHealth
  // is a real thing in the files, and the page shows what it has.
  const summary = Object.entries(gaps).filter(([k]) => k !== 'name')
    .map(([k, v]) => k + ':' + v.length).join(' ') || 'none';
  console.log('        parts missing their headline stat, by type: ' + summary);
}

console.log('\n== the page can actually open ==');
{
  const withLoadout = Object.keys(SHIPS).filter(k => (SHIPS[k].slots || []).length);
  check('the default ship the page picks has a loadout',
        withLoadout.length > 0 && (SHIPS[withLoadout[0]].slots || []).length > 0,
        'first with slots: ' + withLoadout[0]);
  const noSlots = Object.keys(SHIPS).filter(k => !(SHIPS[k].slots || []).length);
  check('every ship WITHOUT a loadout says why, rather than rendering blank',
        noSlots.every(k => !!SHIPS[k].why),
        noSlots.filter(k => !SHIPS[k].why).join(', '));
  check('every unreleased ship says why too',
        UNRELEASED.every(u => u.n && u.why),
        'one of the unreleased entries has no name or no reason');
}

console.log('\n== CIG aggregates, and our sum against them ==');
{
  const withCig = Object.values(SHIPS).filter(s => s.cig);
  check('CIG aggregates are present on effectively every ship',
        withCig.length > 300, withCig.length + ' of ' + Object.keys(SHIPS).length);

  let agree = 0, dis = [];
  for (const s of Object.values(SHIPS)) {
    const cig = s.cig || {};
    if (cig.sdps == null || !(s.slots || []).length) continue;
    let ours = 0;
    for (const sl of s.slots) {
      // --prove: drop the turret exclusion, which is the mistake that put the
      // Perseus at 16,596 DPS against CIG's 1,494.
      if (!prove && sl.turret) continue;
      ours += (PARTS[sl.stock] || {}).dps || 0;
    }
    if (!ours) continue;
    if (Math.abs(ours - cig.sdps) <= Math.max(1, cig.sdps * 0.01)) agree++;
    else dis.push(s.n + ' ours ' + Math.round(ours) + ' CIG ' + cig.sdps);
  }
  check('our pilot-DPS sum reproduces CIG on every ship CIG publishes one for',
        dis.length === 0,
        agree + ' agree, ' + dis.length + ' disagree: ' + dis.slice(0, 3).join(' | '));
  console.log('        agreed on ' + agree + ' ships');
}

console.log('\n' + (failures ? 'FAILED ' + failures + ' of ' + checks + ' checks'
                             : 'ALL ' + checks + ' CHECKS PASSED'));
if (prove) {
  if (failures) {
    console.log('PROOF OK: known-bad input is rejected.');
    process.exit(0);
  }
  console.log('PROOF FAILED: known-bad input passed, so these checks are not checking.');
  process.exit(1);
}
process.exit(failures ? 1 : 0);
