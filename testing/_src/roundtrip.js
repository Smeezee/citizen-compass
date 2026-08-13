/* Round-trip acceptance test.

   Take a mapping file Star Citizen itself wrote, read it with our
   parser, write it back out with our builder, and compare.

   If we cannot reproduce a file the game produced, the exporter is
   wrong — regardless of how reasonable its output looks. That is the
   whole point: "looks fine" is what let a 0-DPS Sabre through once
   already.

   Two levels of comparison:
     SEMANTIC  every (map, action, input, activationMode) tuple, the
               device declarations, the categories, the profile name.
     BYTE      the file, character for character, including CRLF.
   Byte-exact is not required for the game to load a file, but it is
   the only comparison with no judgement in it, so it is the one that
   can fail honestly.
*/
const fs = require('fs');
const path = require('path');
const os = require('os');
const {DOMParser} = require('@xmldom/xmldom');
const SCX2 = require('./sc_export.js');

const REPO = path.join(__dirname, '..', '..', 'data-layer', 'processed') + path.sep;
const site = JSON.parse(fs.readFileSync(REPO+'keybinds_site.json','utf8'));
const cats = JSON.parse(fs.readFileSync(REPO+'actionmap_categories.json','utf8'));

/* The game's canonical actionmap order, taken as first-seen order in
   keybinds_site.json — which is itself derived from the game's own
   defaultProfile.xml, so the order is the game's, not ours. */
const mapOrder = [];
for(const r of site) if(mapOrder.indexOf(r.map)<0) mapOrder.push(r.map);

let failures = 0;
function check(name, ok, detail){
  console.log((ok?'  PASS  ':'  FAIL  ')+name+(detail&&!ok?'\n         '+detail:''));
  if(!ok) failures++;
}

function tuples(p){
  return p.binds.map(b=>[b.map,b.action,b.input,b.activationMode||''].join(''));
}

function roundtrip(file){
  console.log('\n=== '+path.basename(file)+' ===');
  const original = fs.readFileSync(file,'utf8');
  const parsed = SCX2.parse(original, DOMParser);

  console.log(`  read: ${parsed.binds.length} rebinds, ${parsed.devices.length} device options, profile "${parsed.profileName}"`);

  const out = SCX2.build(parsed.binds, {
    profileName: parsed.profileName,
    categories: cats,
    mapOrder: mapOrder,
    devices: parsed.devices
  });

  fs.writeFileSync(path.join(os.tmpdir(), 'out_'+path.basename(file)), out.xml);

  /* --- semantic --- */
  const back = SCX2.parse(out.xml, DOMParser);
  const a = tuples(parsed).slice().sort();
  const b = tuples(back).slice().sort();
  check('every rebind survives the round trip', JSON.stringify(a)===JSON.stringify(b),
        'in '+a.length+' out '+b.length+'; missing '+JSON.stringify(a.filter(x=>!b.includes(x)).slice(0,5))+
        '; extra '+JSON.stringify(b.filter(x=>!a.includes(x)).slice(0,5)));
  check('profile name preserved', parsed.profileName===back.profileName);
  check('device <options> preserved', JSON.stringify(parsed.devices)===JSON.stringify(back.devices),
        JSON.stringify(back.devices));
  check('<devices> block preserved', JSON.stringify(parsed.declared)===JSON.stringify(back.declared),
        'orig '+JSON.stringify(parsed.declared)+'\n         ours '+JSON.stringify(back.declared));

  /* --- byte --- */
  const same = out.xml === original;
  check('byte-for-byte identical to what the game wrote', same);
  if(!same){
    const ol = original.split('\r\n'), nl = out.xml.split('\r\n');
    let shown = 0;
    for(let i=0;i<Math.max(ol.length,nl.length) && shown<8;i++){
      if(ol[i]!==nl[i]){
        console.log(`         line ${i+1}\n           game: ${JSON.stringify(ol[i])}\n           ours: ${JSON.stringify(nl[i])}`);
        shown++;
      }
    }
    console.log(`         lines: game ${ol.length}, ours ${nl.length}`);
  }
  return {parsed, out};
}

console.log('ROUND-TRIP ACCEPTANCE TEST — sc_export.js');
console.log('canonical actionmap order: '+mapOrder.length+' maps from keybinds_site.json');

const r1 = roundtrip(path.join(__dirname, 'fixtures', 'real_export.xml'));
const r2 = roundtrip(path.join(__dirname, 'fixtures', 'real_export2.xml'));

/* ---- facts the test also asserts, so a regression is loud ---- */
console.log('\n=== schema facts asserted ===');
const all = r1.parsed.binds.concat(r2.parsed.binds);
check('explicit unbinds are recognised, not dropped',
      all.filter(b=>SCX2.isUnbind(b.input)).length > 300,
      String(all.filter(b=>SCX2.isUnbind(b.input)).length));
check('mo1_ inputs are accepted by famOf',
      all.filter(b=>b.input.startsWith('mo1_')).length>0 &&
      all.filter(b=>b.input.startsWith('mo1_')).every(b=>SCX2.famOf(b.input).fam==='mouse'));
check('no binding in either real file is refused',
      all.every(b=>SCX2.reject({map:b.map,action:b.action,input:b.input,activationMode:b.activationMode})===null),
      JSON.stringify(all.filter(b=>SCX2.reject({map:b.map,action:b.action,input:b.input}))
                        .slice(0,3)));
const hi = Math.max(...all.map(b=>{const m=/_button(\d+)$/.exec(b.input);return m?+m[1]:0;}));
check('highest button number carried through is 29', hi===29, 'got '+hi);
check('GUID derivation reproduces the left stick',
      SCX2.guidFromVidPid('231d','0201')==='{0201231D-0000-0000-0000-504944564944}',
      SCX2.guidFromVidPid('231d','0201'));
check('GUID derivation reproduces the right stick',
      SCX2.guidFromVidPid('231d','0200')==='{0200231D-0000-0000-0000-504944564944}');
check('Chrome id string yields the same VID/PID',
      JSON.stringify(SCX2.parseGamepadId('VKB Gladiator NXT EVO L (Vendor: 231d Product: 0201)'))
      === JSON.stringify({vid:'231d',pid:'0201',name:'VKB Gladiator NXT EVO L'}),
      JSON.stringify(SCX2.parseGamepadId('VKB Gladiator NXT EVO L (Vendor: 231d Product: 0201)')));
const dup = SCX2.duplicates(r2.parsed.binds);
check('the 13 multi-action inputs in test3cr are detected', dup.length===13, 'got '+dup.length);
check('js1_x is reported as driving roll and lateral strafe',
      !!dup.find(d=>d.input==='js1_x' && d.on.length===2));
check('modifier combinations are still refused',
      SCX2.reject({map:'m',action:'a',input:'kb1_a+lshift'})!==null);
check('ms1_ is still refused',
      SCX2.reject({map:'m',action:'a',input:'ms1_x'})!==null);

/* ---- build from UNSORTED input ----
   The round trip alone cannot prove the sorting rules, because the file
   we read from is already in the game's order — feeding it back in the
   order we read it would reproduce it even with no sorting at all. The
   builder will hand us bindings in whatever order the user clicked, so
   shuffle deterministically and demand the same bytes out. */
console.log('\n=== built from shuffled input (the builder\'s real case) ===');
function shuffle(arr){                       /* deterministic: reversed, then odd/even interleave */
  const a=arr.slice().reverse(), out=[];
  for(let i=0;i<a.length;i+=2) out.push(a[i]);
  for(let i=1;i<a.length;i+=2) out.push(a[i]);
  return out;
}
for(const [file,parsed] of [['real_export.xml',r1.parsed],['real_export2.xml',r2.parsed]]){
  const shuffled = shuffle(parsed.binds);
  check(file+': shuffle actually changed the order',
        JSON.stringify(shuffled)!==JSON.stringify(parsed.binds));
  const out = SCX2.build(shuffled, {
    profileName: parsed.profileName, categories: cats,
    mapOrder: mapOrder, devices: parsed.devices
  });
  check(file+': shuffled input still reproduces the game\'s file byte for byte',
        out.xml === fs.readFileSync(path.join(__dirname,'fixtures',file),'utf8'),
        (()=>{ const ol=fs.readFileSync(path.join(__dirname,'fixtures',file),'utf8').split('\r\n'),
                     nl=out.xml.split('\r\n');
               for(let i=0;i<Math.max(ol.length,nl.length);i++)
                 if(ol[i]!==nl[i]) return `first diff line ${i+1}\n           game: ${JSON.stringify(ol[i])}\n           ours: ${JSON.stringify(nl[i])}`;
               return 'lengths differ'; })());
}

/* ---- the <devices> block, built from scratch ----
   Round-tripping cannot test this either: both real files contain mo1_
   inputs, so the mouse line appears whether or not the rule that a
   keyboard implies a mouse exists. A keyboard-only profile is the case
   that separates them. */
console.log('\n=== <devices> block built from scratch ===');
function devLines(x){ return x.split('\r\n').filter(l=>/^   <(keyboard|mouse|joystick|gamepad) /.test(l)).map(l=>l.trim()); }

const kbOnly = SCX2.build(
  [{map:'spaceship_movement',action:'v_afterburner',input:'kb1_x'}],
  {profileName:'kbonly', categories:cats, mapOrder:mapOrder});
check('a keyboard-only profile still declares the mouse',
      JSON.stringify(devLines(kbOnly.xml))===JSON.stringify(['<keyboard instance="1"/>','<mouse instance="1"/>']),
      JSON.stringify(devLines(kbOnly.xml)));

const twoSticks = SCX2.build(
  [{map:'spaceship_movement',action:'v_roll',input:'js1_x'},
   {map:'spaceship_movement',action:'v_yaw',input:'js2_rotz'}],
  {profileName:'sticks', categories:cats, mapOrder:mapOrder,
   joysticks:[{instance:1,vid:'231d',pid:'0201',name:'VKB Gladiator NXT EVO L'},
              {instance:2,vid:'231d',pid:'0200',name:'VKB Gladiator NXT EVO R'}]});
check('two sticks are declared as two joystick instances, no keyboard',
      JSON.stringify(devLines(twoSticks.xml))===JSON.stringify(['<joystick instance="1"/>','<joystick instance="2"/>']),
      JSON.stringify(devLines(twoSticks.xml)));
check('both joystick <options> lines carry the correct GUID',
      twoSticks.xml.includes('{0201231D-0000-0000-0000-504944564944}') &&
      twoSticks.xml.includes('{0200231D-0000-0000-0000-504944564944}'));
check('a stick with no VID/PID is reported, not silently written',
      (()=>{ const r=SCX2.build([{map:'spaceship_movement',action:'v_roll',input:'js1_x'}],
               {profileName:'x',categories:cats,mapOrder:mapOrder,joysticks:[]});
             return r.warnings.some(w=>/no VID\/PID/.test(w)) && !/type="joystick"/.test(r.xml); })());

/* ---- a limit of the evidence, asserted so it stays visible ----
   We sort actions ASCII-ascending. Case-insensitive sorting would give
   the same result on both real files, so these files cannot tell the two
   apart — no actionmap in either contains a pair that distinguishes them.
   This check asserts that ambiguity. If a future export ever DOES
   distinguish, this check fails and tells us to go and look, rather than
   the sort quietly being wrong. */
function ciSort(a){ return a.slice().sort((x,y)=>{const p=x.toLowerCase(),q=y.toLowerCase();return p<q?-1:p>q?1:0;}); }
const ambiguous = [r1.parsed,r2.parsed].every(p=>{
  const maps={}; p.binds.forEach(b=>{ (maps[b.map]=maps[b.map]||new Set()).add(b.action); });
  return Object.values(maps).every(s=>{ const a=[...s]; return JSON.stringify(a.slice().sort())===JSON.stringify(ciSort(a)); });
});
check('NOT PROVEN: ASCII vs case-insensitive action sort — no real file distinguishes them',
      ambiguous, 'a file now distinguishes them — go and determine which the game uses');

/* ---- actionmap order for a map the canonical list does not know ---- */
const oddMap = SCX2.build(
  [{map:'zzz_not_a_real_map',action:'a',input:'kb1_x'},
   {map:'spaceship_movement',action:'v_afterburner',input:'kb1_y'}],
  {profileName:'odd', categories:cats, mapOrder:mapOrder});
check('an unknown actionmap is appended, not dropped',
      oddMap.xml.includes('zzz_not_a_real_map') && oddMap.unknownMaps.length===1 &&
      oddMap.xml.indexOf('spaceship_movement') < oddMap.xml.indexOf('zzz_not_a_real_map'));

/* ---- THE DEAD EXPORT, REPRODUCED AND THEN REFUSED ----------------
   This is not a hypothetical. On 2026-08-12 this tool produced a profile
   that Star Citizen would not use, from a machine with exactly two sticks:

     <joystick instance="1"/> <joystick instance="2"/>
     <joystick instance="3"/> <joystick instance="4"/>
     <options type="joystick" instance="3" Product=" VKBsim ... EVO L ..."/>
     <options type="joystick" instance="4" Product=" VKBsim ... EVO R ..."/>
     ...every binding written as js3_* / js4_*

   Four declared, two described, and every token naming a stick the game
   had no reason to believe in. The inputs below are that exact state. If
   any of these four checks ever goes red again, the export has regressed
   to a file that cannot work. */
console.log('\n=== the dead export of 2026-08-12, as an input ===');
const dead = SCX2.build(
  [{map:'spaceship_general', action:'v_flightready', input:'js3_button29'},
   {map:'spaceship_movement',action:'v_roll',       input:'js3_x'},
   {map:'spaceship_movement',action:'v_yaw',        input:'js4_rotz'}],
  {profileName:'dead', categories:cats, mapOrder:mapOrder,
   joysticks:[{instance:3,vid:'231d',pid:'0201',name:'VKBsim Gladiator EVO L'},
              {instance:4,vid:'231d',pid:'0200',name:'VKBsim Gladiator EVO R'}]});

check('js3_/js4_ are renumbered to js1_/js2_ regardless of what the screen said',
      /js1_button29/.test(dead.xml) && /js1_x/.test(dead.xml) && /js2_rotz/.test(dead.xml) &&
      !/js3_/.test(dead.xml) && !/js4_/.test(dead.xml),
      devLines(dead.xml).join(' ') + '  ' +
      (dead.xml.match(/input="js[0-9]_[a-z0-9]+"/g) || []).join(' '));

check('<devices> declares exactly two joysticks, 1 and 2 — no phantoms',
      JSON.stringify(devLines(dead.xml)) ===
      JSON.stringify(['<joystick instance="1"/>','<joystick instance="2"/>']),
      JSON.stringify(devLines(dead.xml)));

/* The invariant the two blocks disagreed about, asserted directly rather
   than inferred from the two checks above. */
function optInstances(x, type){
  return x.split('\r\n')
          .filter(l=>l.indexOf('<options type="'+type+'"')>=0)
          .map(l=>+/instance="(\d+)"/.exec(l)[1]);
}
function devInstances(x, type){
  return devLines(x).filter(l=>l.indexOf('<'+type+' ')===0)
                    .map(l=>+/instance="(\d+)"/.exec(l)[1]);
}
check('the DECLARED joystick set equals the DESCRIBED joystick set',
      JSON.stringify(devInstances(dead.xml,'joystick')) ===
      JSON.stringify(optInstances(dead.xml,'joystick')),
      'declared ' + JSON.stringify(devInstances(dead.xml,'joystick')) +
      ' vs described ' + JSON.stringify(optInstances(dead.xml,'joystick')));

/* Renumbering is only safe because the GUID travels with the stick. If the
   L stick's GUID ever came out attached to js2, renumbering WOULD have
   mismatched a device — so this is the check that licenses the whole
   approach, not a nicety. */
check('each GUID follows its own stick across the renumber (L stays js1)',
      /instance="1" Product=" VKBsim Gladiator EVO L    \{0201231D-0000-0000-0000-504944564944\}"/.test(dead.xml) &&
      /instance="2" Product=" VKBsim Gladiator EVO R    \{0200231D-0000-0000-0000-504944564944\}"/.test(dead.xml),
      (dead.xml.match(/<options type="joystick"[^>]*>/g)||[]).join('\n  '));

/* Two sticks connected, one of them bound. This is the case that tells the
   two ways of counting joysticks apart: the highest instance any binding
   REFERS to is 1, while the number of sticks we can DESCRIBE is 2. Counting
   the first way is what declared four devices for two sticks. Without this
   case, deleting the fix changes nothing and the suite says PASS - which is
   precisely what mutation M22 demonstrated. */
console.log('\n=== two sticks, one of them bound ===');
const halfBound = SCX2.build(
  [{map:'spaceship_movement',action:'v_roll',input:'js1_x'}],
  {profileName:'half', categories:cats, mapOrder:mapOrder,
   joysticks:[{instance:1,vid:'231d',pid:'0201',name:'VKBsim Gladiator EVO L'},
              {instance:2,vid:'231d',pid:'0200',name:'VKBsim Gladiator EVO R'}]});
check('an unbound but connected stick is declared AND described, not half of each',
      JSON.stringify(devInstances(halfBound.xml,'joystick'))==='[1,2]' &&
      JSON.stringify(optInstances(halfBound.xml,'joystick'))==='[1,2]',
      'declared ' + JSON.stringify(devInstances(halfBound.xml,'joystick')) +
      ' vs described ' + JSON.stringify(optInstances(halfBound.xml,'joystick')));

/* ---- ONE STICK, which is now the common case (§5b) ---------------- */
console.log('\n=== one stick ===');
const one = SCX2.build(
  [{map:'spaceship_movement',action:'v_roll',input:'js1_x'}],
  {profileName:'one', categories:cats, mapOrder:mapOrder,
   joysticks:[{instance:1,vid:'231d',pid:'0201',name:'VKBsim Gladiator EVO L'}]});
check('one stick exports one <joystick>, one <options>, and only js1_ tokens',
      JSON.stringify(devInstances(one.xml,'joystick'))==='[1]' &&
      JSON.stringify(optInstances(one.xml,'joystick'))==='[1]' &&
      !/js[2-9]_/.test(one.xml),
      JSON.stringify(devLines(one.xml)));

/* ---- an unattested axis is NAMED, not merely tolerated ------------ */
console.log('\n=== unattested axis names ===');
const EVID = {x:'PROVEN', y:'PROVEN', z:'PROVEN', rotx:'PROVEN', roty:'PROVEN',
              rotz:'PROVEN', slider1:'PROVEN', slider2:'UNATTESTED'};
const unat = SCX2.build(
  [{map:'spaceship_movement',action:'v_roll',input:'js1_slider2'},
   {map:'spaceship_movement',action:'v_yaw', input:'js1_x'}],
  {profileName:'unat', categories:cats, mapOrder:mapOrder, axisEvidence:EVID,
   joysticks:[{instance:1,vid:'231d',pid:'0201',name:'VKBsim Gladiator EVO L'}]});
check('an unattested axis in the file is named in the warnings',
      unat.unattested.join(',')==='slider2' &&
      unat.warnings.some(w=>/slider2/.test(w) && /UNATTESTED does not mean rejected/.test(w)),
      JSON.stringify(unat.unattested));
check('a proven axis is NOT flagged — the warning has to be worth reading',
      !unat.unattested.includes('x'));
const noEvid = SCX2.build(
  [{map:'spaceship_movement',action:'v_roll',input:'js1_slider2'}],
  {profileName:'noev', categories:cats, mapOrder:mapOrder,
   joysticks:[{instance:1,vid:'231d',pid:'0201',name:'VKBsim Gladiator EVO L'}]});
check('with no evidence table supplied, no claim is made either way',
      noEvid.unattested.length===0 &&
      !noEvid.warnings.some(w=>/UNATTESTED/.test(w)),
      JSON.stringify(noEvid.unattested));

/* ---- the claim about what the game has done with our files -------- */
check('the export no longer claims no file has ever been loaded by the game',
      !one.warnings.some(w=>/never been loaded/i.test(w)) &&
      one.warnings.some(w=>/not the same as the controls behaving correctly/.test(w)),
      one.warnings.join('\n  '));

console.log('\n'+(failures? failures+' FAILURE(S)' : 'ALL CHECKS PASSED'));
process.exit(failures?1:0);
