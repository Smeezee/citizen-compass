layer = open('cc-testing-layer.html', encoding='utf-8').read()

decl = "let renderer,scene,camera,controls,current,raf,loader;"
assert decl in layer
layer = layer.replace(decl, "/* declaration hoisted to the top of this script */", 1)

header = """
/* --- fixes 2026-08-01 ------------------------------------------------------
   1. renderer & co. declared here, not 85 lines down. apply() runs at load and
      tested `typeof renderer`; on a let that is a TDZ ReferenceError, not a safe
      undefined check, so apply() threw and everything after it - the 3D viewer
      and the clickable rows - never ran.
   2. Ship labels carry a trailing link glyph, so exact name matching failed.
   3. RSI links removed from the matrix rows; ship name opens the detail page,
      the RSI link lives inside it. URLs kept in CC_RSI.
   4. DISPLAY tab toggles. Default text size is 130%.
--------------------------------------------------------------------------- */
let renderer,scene,camera,controls,current,raf,loader;
const CC_NORM = s => String(s)
  .replace(/[\\u{1F000}-\\u{1FAFF}\\u{2190}-\\u{27BF}\\u{2B00}-\\u{2BFF}\\u{FE0F}\\u{200D}]/gu,'')
  .replace(/\\s+/g,' ').trim().toLowerCase();
let _ccIndex=null;
function CC_LOOKUP(label){
  if(!_ccIndex){ _ccIndex=new Map();
    SHIPS.forEach(s=>{ const k=CC_NORM(s.name); if(!_ccIndex.has(k)) _ccIndex.set(k,s); }); }
  return _ccIndex.get(CC_NORM(label)) || null;
}
const CC_RSI = {};
SHIPS.forEach(s=>{ if(s.pledge_url) CC_RSI[s.id]=s.pledge_url; });
const CC_HAS3D = id => !!CC_MODELS[String(id)];
"""
layer = layer.replace("const $=id=>document.getElementById(id);",
                      header + "const $=id=>document.getElementById(id);", 1)

old = """    const label=td.textContent.trim(); if(!label)return;
    const ship=SHIPS.find(s=>s.name===label); if(!ship)return;
    td.dataset.ccDone='1';
    const has=!!CC_MODELS[String(ship.id)];
    td.innerHTML='<span class="cc-open'+(has?'':' cc-nomodel')+'">'+td.innerHTML+'</span>';
    td.querySelector('.cc-open').onclick=()=>open(ship);"""
assert old in layer
layer = layer.replace(old, """    const label=td.textContent.trim(); if(!label)return;
    const ship=CC_LOOKUP(label); if(!ship)return;
    td.dataset.ccDone='1';
    const _a=td.querySelector('a[href]');
    if(_a) CC_RSI[ship.id]=_a.getAttribute('href');   // captured, not discarded
    td.innerHTML='<span class="cc-open'+(CC_HAS3D(ship.id)?' cc-has3d':'')+'">'+
                 ship.name+'</span>';
    td.style.cursor='pointer';
    td.onclick=()=>open(ship);""")

old_rsi = "  if(ship.pledge_url){rsi.href=ship.pledge_url;rsi.style.display='';}else rsi.style.display='none';"
assert old_rsi in layer
layer = layer.replace(old_rsi, """  const rsiHref=ship.pledge_url||CC_RSI[ship.id]||null;
  if(rsiHref){rsi.href=rsiHref;rsi.target='_blank';rsi.rel='noopener';rsi.style.display='';}
  else rsi.style.display='none';""")

css = """<style>
#matrix-body td:first-child{cursor:pointer}
#matrix-body .cc-open{border-bottom:1px dotted rgba(0,201,167,.55);transition:color .12s}
#matrix-body td:first-child:hover .cc-open{color:var(--mg-cyan,#00C9A7);border-bottom-style:solid}
#matrix-body .cc-open.cc-has3d::after{content:'3D';margin-left:7px;font-size:.62em;
  letter-spacing:.06em;padding:1px 4px;border-radius:3px;vertical-align:middle;
  background:rgba(0,201,167,.16);color:#00C9A7;border:1px solid rgba(0,201,167,.4)}
</style>
"""
open('cc-testing-layer-fixed.html','w',encoding='utf-8').write(css + layer)
print('machine layer:', len(css+layer), 'bytes')
