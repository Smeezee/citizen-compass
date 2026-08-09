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

console.log('\n'+(failures? failures+' FAILURE(S)' : 'ALL CHECKS PASSED'));
process.exit(failures?1:0);
