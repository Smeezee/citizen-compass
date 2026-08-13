/* Mutation test — hard rule 12.

   A passing test suite proves nothing unless each check can fail.
   This deliberately breaks sc_export.js one rule at a time and
   confirms the round-trip test notices. A mutation that SURVIVES is
   a check that is not really checking anything, and gets reported as
   a gap rather than swept up.

   Each mutation is a real mistake someone could make — most of them
   are mistakes the previous exporter actually made.
*/
const fs=require('fs'), cp=require('child_process'), path=require('path');
const SRC=path.join(__dirname,'sc_export.js');
const orig=fs.readFileSync(SRC,'utf8');

const MUTATIONS=[
 ['M1  omit the joystick <options> line (what the old exporter did)',
  s=>s.replace('if(fams.joystick){\n        var js = opts.joysticks || [];',
               'if(false){\n        var js = opts.joysticks || [];')
      .replace('if(opts.devices && opts.devices.length){',
               'if(opts.devices && opts.devices.length){ opts.devices=opts.devices.filter(function(d){return d.type!=="joystick";});')],

 ['M2  emit actions in canonical order instead of alphabetically',
  s=>s.replace('var actions = Object.keys(byMap[m]).sort();',
               'var actions = Object.keys(byMap[m]);')],

 ['M3  write only the first rebind per action',
  s=>s.replace('rbs.forEach(function(b){','rbs.slice(0,1).forEach(function(b){')],

 ['M4  drop mo from the recognised device prefixes',
  s=>s.replace('var PREFIX = {kb:"keyboard", mo:"mouse", js:"joystick", gp:"gamepad"};',
               'var PREFIX = {kb:"keyboard", js:"joystick", gp:"gamepad"};')],

 ['M5  treat "prefix_ " as an empty binding and skip it',
  s=>s.replace('if(!b || !b.map || !b.action || typeof b.input !== "string" || b.input === "")',
               'if(!b || !b.map || !b.action || typeof b.input !== "string" || b.input === "" || /_ $/.test(b.input))')],

 ['M6  use LF line endings instead of CRLF',
  s=>s.replace('var EOL   = opts.eol || "\\r\\n";','var EOL   = opts.eol || "\\n";')],

 ['M7  sort the categories alphabetically',
  s=>s.replace('emitted.forEach(function(m){\n      var c = cats[m];\n      if(c && !seen[c]){ seen[c]=true; catList.push(c); }\n    });',
               'emitted.forEach(function(m){\n      var c = cats[m];\n      if(c && !seen[c]){ seen[c]=true; catList.push(c); }\n    });\n    catList.sort();')],

 ['M8  put joystick rebinds before keyboard inside an action',
  s=>s.replace('var FAM_ORDER = ["keyboard","mouse","joystick","gamepad"];',
               'var FAM_ORDER = ["joystick","gamepad","keyboard","mouse"];')],

 ['M9  cap button numbers at 12 (the shipped-defaults ceiling)',
  s=>s.replace('if(!famOf(b.input))',
               'if(/_button(1[3-9]|[2-9][0-9])$/.test(b.input)) return "button number above 12";\n    if(!famOf(b.input))')],

 ['M10 swap PID and VID in the GUID',
  s=>s.replace('return "{" + p + v + "-" + GUID_TAIL + "}";',
               'return "{" + v + p + "-" + GUID_TAIL + "}";')],

 ['M11 emit the <devices> block without the mouse',
  s=>s.replace('if(fams.keyboard) fams.mouse = true;','')],

 ['M12 drop activationMode when writing a rebind',
  s=>s.replace("(b.activationMode ? ' activationMode=\"'+esc(b.activationMode)+'\"' : '')","''")],

 ['M13 keep only the last rebind for an action (overwrite, not append)',
  s=>s.replace('(byMap[b.map][b.action] = byMap[b.map][b.action] || []).push(b);',
               'byMap[b.map][b.action] = [b];')],

 ['M14 stop reporting one input on several actions',
  s=>s.replace('if(byInput[k].length>1) out.push','if(false) out.push')],

 ['M15 accept modifier combinations',
  s=>s.replace('if(/[+]/.test(b.input))','if(false)')],

 ['M16 emit actionmaps in first-seen order instead of the game\'s order',
  s=>s.replace('order0.forEach(function(m){ if(byMap[m]) emitted.push(m); });','')],

 ['M17 sort actionmaps alphabetically',
  s=>s.replace('order0.forEach(function(m){ if(byMap[m]) emitted.push(m); });',
               'order0.slice().sort().forEach(function(m){ if(byMap[m]) emitted.push(m); });')],

 ['M18 sort actions case-insensitively (view_move_target_X_pos vs _neg)',
  s=>s.replace('var actions = Object.keys(byMap[m]).sort();',
               'var actions = Object.keys(byMap[m]).sort(function(a,b){a=a.toLowerCase();b=b.toLowerCase();return a<b?-1:a>b?1:0;});')],

 ['M19 drop an unknown actionmap instead of appending it',
  s=>s.replace('mapsSeen.forEach(function(m){ if(emitted.indexOf(m)<0){ emitted.push(m); unknown.push(m); } });','')],

 /* RE-POINTED 2026-08-12. This mutation stopped applying when the <options>
    branch it targeted was replaced by joystickRenumber() - and a mutation that
    does not apply is not a check, it is a line in a report that says SKIP.
    Same defect, aimed at where the decision now lives. */
 ['M20 fabricate a GUID for a stick with no VID/PID',
  s=>s.replace('if(!guid){ orphans.push(order[i]); continue; }',
               'if(!guid){ guid="{0000-0000-0000-0000-504944564944}"; d = d || {name:"Joystick"}; }')],

 /* The two invariants §2 of the master order is about. Both of these
    mutations reproduce the dead export of 2026-08-12 exactly. */
 ['M21 skip the renumber and write whatever the screen said',
  s=>s.replace('c.input = b.input.replace(/^js\\d+_/, "js" + to + "_");',
               'c.input = b.input;')],

 ['M22 declare joysticks by highest instance seen, not by what is described',
  s=>s.replace('inst.joystick = renum.devices.length;',
               '')],

 ['M23 pass an unattested axis without naming it',
  s=>s.replace('if(st === "UNATTESTED" && unattested.indexOf(m[1]) < 0) unattested.push(m[1]);',
               '')],
];

let caught=0, survived=[];
for(const [label,fn] of MUTATIONS){
  const mutated=fn(orig);
  if(mutated===orig){ console.log('  SKIP    '+label+'  (mutation did not apply — pattern not found)'); survived.push(label+' [did not apply]'); continue; }
  fs.writeFileSync(SRC,mutated);
  const r=cp.spawnSync('node',[path.join(__dirname,'roundtrip.js')],{encoding:'utf8'});
  fs.writeFileSync(SRC,orig);
  if(r.status!==0){
    const first=(r.stdout.match(/^  FAIL  .*$/m)||['?'])[0].trim();
    console.log('  CAUGHT  '+label+'\n            -> '+first);
    caught++;
  } else {
    console.log('  SURVIVED '+label+'   <-- the suite does not test this');
    survived.push(label);
  }
}

console.log('\n'+caught+'/'+MUTATIONS.length+' mutations caught.');
if(survived.length){ console.log('SURVIVORS (untested behaviour):'); survived.forEach(s=>console.log('  - '+s)); }
