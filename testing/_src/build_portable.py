import base64, json, os, re, glob

T='/home/claude/t128/node_modules/three'
def rd(p, b=False):
    return open(p,'rb').read() if b else open(p,encoding='utf-8').read()

three   = rd(f'{T}/build/three.min.js')
gltf    = rd(f'{T}/examples/js/loaders/GLTFLoader.js')
orbit   = rd(f'{T}/examples/js/controls/OrbitControls.js')
draco   = rd(f'{T}/examples/js/loaders/DRACOLoader.js')
wrapper = rd(f'{T}/examples/js/libs/draco/draco_wasm_wrapper.js')
wasm_b64= base64.b64encode(rd(f'{T}/examples/js/libs/draco/draco_decoder.wasm', True)).decode()

# ---- embedded models -------------------------------------------------------
models={}
for f in sorted(glob.glob('/home/claude/demo/models/*.glb')):
    folder=os.path.basename(f)[:-4].replace('_',' ')
    models[folder]=base64.b64encode(rd(f,True)).decode()
# fix names that legitimately contain a hyphen/dash
ren={'L 22 Alpha Wolf':'L-22 Alpha Wolf','Khartu Al':'Khartu-Al'}
for a,b in ren.items():
    if a in models: models[b]=models.pop(a)
print('embedded:', len(models), 'ships,', sum(len(v) for v in models.values())/1048576, 'MB b64')

site  = rd('/home/claude/latest.html')
layer = rd('/home/claude/cc-testing-layer.html')

# ---- 1. strip CDN script tags ---------------------------------------------
cdn = re.findall(r'<script src="https://cdn\.jsdelivr\.net[^"]*"></script>\s*', layer)
assert len(cdn)==3, cdn
for t in cdn: layer = layer.replace(t,'',1)

# ---- 2. patch model loading to use embedded data ---------------------------
old_start = "  const url=CC_DIR+encodeURIComponent(dir)+'/'+CC_FILE, t0=performance.now();"
i = layer.index(old_start)
j = layer.index("status.textContent='model failed", i)
j = layer.index("});", j)+3
new_load = """  const t0=performance.now();
  const b64=CC_EMBED[dir];
  if(!b64){ still.style.display='none'; empty.style.display='flex';
    empty.innerHTML='<div>3D model not bundled in this portable build.</div>'+
      '<div style="opacity:.75;font-size:14px">'+Object.keys(CC_EMBED).length+
      ' of '+Object.keys(CC_MODELS).length+' matched ships carry a model here. '+
      'The full library is 243 ships.</div>';
    status.textContent=''; size(); return; }
  const bin=atob(b64), buf=new Uint8Array(bin.length);
  for(let n=0;n<bin.length;n++) buf[n]=bin.charCodeAt(n);
  loader.parse(buf.buffer,'',g=>{
    if(tok!==openTok) return;   // an earlier ship's model must not land here
    clearModel();current=g.scene;
    current.traverse(o=>{if(o.isMesh&&o.material)
      (Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.side=THREE.DoubleSide);});
    scene.add(current); const i=frame(current);
    still.style.transition=''; still.style.opacity=0;
    status.textContent=dir+' \\u00b7 '+((performance.now()-t0)/1000).toFixed(1)+'s \\u00b7 '+
      i.sz.x.toFixed(1)+' \\u00d7 '+i.sz.y.toFixed(1)+' \\u00d7 '+i.sz.z.toFixed(1)+
      ' \\u00b7 '+(b64.length*0.75/1048576).toFixed(2)+' MB draco';},
    e=>{if(tok!==openTok)return;
      status.textContent='model failed to decode';console.warn('[cc]',dir,e);});"""
layer = layer[:i] + new_load + layer[j:]

# no images bundled - don't attempt a fetch that will 404.
# a silent no-op here ships a page that requests a thumbnail that cannot exist,
# so both substitutions are asserted rather than assumed.
_a = "  const img=CC_DIR+encodeURIComponent(dir)+'/image.webp';\n"
_b = "  still.src=img;\n"
assert _a in layer, "portable build: thumbnail path line not found"
assert _b in layer, "portable build: still.src assignment not found"
layer = layer.replace(_a,"")
layer = layer.replace(_b,"  still.style.display='none';\n")

# ---- 2b. robust row matching -----------------------------------------------
# the live page appends a link glyph to ship names, so exact === matching fails
old_match = """    const label=td.textContent.trim(); if(!label)return;
    const ship=SHIPS.find(s=>s.name===label); if(!ship)return;"""
assert old_match in layer
new_match = """    const label=td.textContent.trim(); if(!label)return;
    const ship=CC_LOOKUP(label); if(!ship)return;"""
layer = layer.replace(old_match, new_match)

old_click = "    td.querySelector('.cc-open').onclick=()=>open(ship);"
assert old_click in layer
new_click = """    const _a=td.querySelector('a[href]');
    if(_a) CC_RSI[ship.id]=_a.getAttribute('href');   // captured, not discarded
    td.innerHTML='<span class="cc-open'+(CC_HAS3D(ship.id)?' cc-has3d':'')+'">'+
                 ship.name+'</span>';
    td.style.cursor='pointer';
    td.onclick=()=>open(ship);"""
layer = layer.replace(old_click, new_click)

# the RSI anchor is stripped from the row above, so drop the old wrapper line too
old_wrap = """    const has=!!CC_MODELS[String(ship.id)];
    td.innerHTML='<span class="cc-open'+(has?'':' cc-nomodel')+'">'+td.innerHTML+'</span>';"""
assert old_wrap in layer
layer = layer.replace(old_wrap, "")

# RSI link now lives only on the detail page
old_rsi = """  if(ship.pledge_url){rsi.href=ship.pledge_url;rsi.style.display='';}else rsi.style.display='none';"""
assert old_rsi in layer
new_rsi = """  const rsiHref=ship.pledge_url||CC_RSI[ship.id]||null;
  if(rsiHref){rsi.href=rsiHref;rsi.target='_blank';rsi.rel='noopener';rsi.style.display='';}
  else rsi.style.display='none';"""
layer = layer.replace(old_rsi, new_rsi)

lookup_js = """
/* Ship names on the page carry a trailing link glyph and stray whitespace.
   Match on a normalised form instead of an exact string compare. */
const CC_NORM = s => String(s)
  .replace(/[\\u{1F000}-\\u{1FAFF}\\u{2190}-\\u{27BF}\\u{2B00}-\\u{2BFF}\\u{FE0F}\\u{200D}]/gu,'')
  .replace(/\\s+/g,' ').trim().toLowerCase();
let _ccIndex=null;
function CC_LOOKUP(label){
  if(!_ccIndex){ _ccIndex=new Map();
    SHIPS.forEach(s=>{ const k=CC_NORM(s.name); if(!_ccIndex.has(k)) _ccIndex.set(k,s); }); }
  return _ccIndex.get(CC_NORM(label)) || null;
}
/* RSI links are stripped from the matrix rows and kept here, so the ship name
   opens the detail page. The link is offered inside that page instead. */
const CC_RSI = {};
SHIPS.forEach(s=>{ if(s.pledge_url) CC_RSI[s.id]=s.pledge_url; });
const CC_HAS3D = id => (typeof CC_EMBED!=='undefined')
  ? !!CC_EMBED[CC_MODELS[String(id)]]
  : !!CC_MODELS[String(id)];
"""
layer = layer.replace("const $=id=>document.getElementById(id);",
                      lookup_js + "const $=id=>document.getElementById(id);", 1)

# ---- 2c. FIX a real pre-existing bug in the layer ---------------------------
# apply() runs at load and does `typeof renderer` on a `let` declared 85 lines
# later. On a let/const that is a TDZ ReferenceError, NOT a safe undefined check,
# so apply() throws and every statement after it never runs - which killed the
# 3D viewer wiring and the clickable ship rows. Hoist the declaration.
decl = "let renderer,scene,camera,controls,current,raf,loader;"
assert decl in layer
layer = layer.replace(decl, "/* declaration hoisted - see below */", 1)
layer = layer.replace("const $=id=>document.getElementById(id);",
                      decl + "\nconst $=id=>document.getElementById(id);", 1)

# ---- 2d. style for the rows now that the anchors are gone ------------------
badge_css = """<style>
#matrix-body td:first-child{cursor:pointer}
#matrix-body .cc-open{border-bottom:1px dotted rgba(0,201,167,.55);transition:color .12s}
#matrix-body td:first-child:hover .cc-open{color:var(--mg-cyan,#00C9A7);border-bottom-style:solid}
#matrix-body .cc-open.cc-has3d::after{content:'3D';margin-left:7px;font-size:.62em;
  letter-spacing:.06em;padding:1px 4px;border-radius:3px;vertical-align:middle;
  background:rgba(0,201,167,.16);color:#00C9A7;border:1px solid rgba(0,201,167,.4)}
</style>
"""
layer = badge_css + layer

# ---- 3. build the inlined library block ------------------------------------
libs = f"""<script>{three}</script>
<script>{orbit}</script>
<script>{gltf}</script>
<script>{draco}</script>
<script>
/* draco decoder, inlined - no network, works from file:// */
const CC_DRACO_WRAPPER = {json.dumps(wrapper)};
const CC_DRACO_WASM_B64 = {json.dumps(wasm_b64)};
</script>
<script>
const CC_EMBED = {json.dumps(models)};
</script>
"""

# ---- 4. attach DRACOLoader with patched library loading --------------------
layer = layer.replace(
    "  loader=new THREE.GLTFLoader(); addEventListener('resize',size);",
    """  loader=new THREE.GLTFLoader();
  const dl=new THREE.DRACOLoader();
  dl._loadLibrary=function(url){
    if(url==='draco_wasm_wrapper.js') return Promise.resolve(CC_DRACO_WRAPPER);
    if(url==='draco_decoder.wasm'){
      const b=atob(CC_DRACO_WASM_B64), a=new Uint8Array(b.length);
      for(let n=0;n<b.length;n++) a[n]=b.charCodeAt(n);
      return Promise.resolve(a.buffer);
    }
    return Promise.reject(new Error('unexpected draco asset '+url));
  };
  loader.setDRACOLoader(dl);
  addEventListener('resize',size);""")

# ---- 5. inject into the real site -----------------------------------------
k = site.lower().rindex('</body>')
out = site[:k] + '\n<!-- Citizen Compass portable concept build -->\n' + libs + layer + '\n' + site[k:]
open('/home/claude/citizen-compass-concept.html','w',encoding='utf-8').write(out)
print('written:', len(out)/1048576, 'MB')
