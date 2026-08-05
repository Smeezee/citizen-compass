import base64, json, os, re, glob, sys

# ---------------------------------------------------------------------------
# Repo-relative build. This script used to hardcode a cloud-sandbox path, which
# made testing/_deploy/index.html unreproducible on the project machine - the
# artifact existed but nothing here could regenerate it. Everything now
# resolves from this file's location, so it runs anywhere the repo is checked
# out. Vendored three.js lives beside it so no npm install is required.
#
#   run:  python testing/_src/build_deploy.py
# ---------------------------------------------------------------------------
SRC  = os.path.dirname(os.path.abspath(__file__))          # testing/_src
REPO = os.path.dirname(os.path.dirname(SRC))               # repo root
T    = os.path.join(SRC, 'vendor', 'three')
OUT  = os.path.join(REPO, 'testing', '_deploy')
SITE  = os.path.join(REPO, 'releases', 'latest.html')
LAYER = os.path.join(SRC, '_layer.src.html')

def rd(p, b=False):
    if not os.path.exists(p):
        sys.exit("BUILD INPUT MISSING: %s\n"
                 "This build cannot invent it. Nothing was written." % p)
    return open(p,'rb').read() if b else open(p,encoding='utf-8').read()

three   = rd(os.path.join(T,'build','three.min.js'))
gltf    = rd(os.path.join(T,'examples','js','loaders','GLTFLoader.js'))
orbit   = rd(os.path.join(T,'examples','js','controls','OrbitControls.js'))
draco   = rd(os.path.join(T,'examples','js','loaders','DRACOLoader.js'))
wrapper = rd(os.path.join(T,'examples','js','libs','draco','draco_wasm_wrapper.js'))
wasm_b64= base64.b64encode(rd(os.path.join(T,'examples','js','libs','draco','draco_decoder.wasm'), True)).decode()

# ---- embedded models -------------------------------------------------------
import re as _re
os.makedirs(OUT, exist_ok=True)
_mdir = os.path.join(OUT, 'models')
have = {os.path.basename(p) for p in glob.glob(os.path.join(_mdir, '*.glb'))}
if not have:
    sys.exit("NO MODELS FOUND in %s\n"
             "Refusing to build a deploy page that would 404 every ship.\n"
             "Nothing was written." % _mdir)
safe = lambda n: _re.sub(r'[^A-Za-z0-9._-]+','_',n)
import json as _json
_cc = _json.loads(_re.search(r'const CC_MODELS = (\{.*?\});', open(LAYER,encoding='utf-8').read(), _re.S).group(1))
models={}
missing=[]
for _id, folder in _cc.items():
    fn = safe(folder)+'.glb'
    if fn in have: models[folder]='models/'+fn
    else: missing.append(folder)
print('mapped', len(models), 'folders |', len(set(models.values())), 'unique files | unmatched:', len(set(missing)))
if missing: print('  unmatched sample:', sorted(set(missing))[:8])
# fix names that legitimately contain a hyphen/dash
ren={'L 22 Alpha Wolf':'L-22 Alpha Wolf','Khartu Al':'Khartu-Al'}
for a,b in ren.items():
    if a in models: models[b]=models.pop(a)


site  = rd(SITE)
layer = rd(LAYER)

# ---- 1. strip CDN script tags ---------------------------------------------
cdn = re.findall(r'<script src="https://cdn\.jsdelivr\.net[^"]*"></script>\s*', layer)
assert len(cdn)==3, cdn
for t in cdn: layer = layer.replace(t,'',1)

# ---- 2. patch model loading to use embedded data ---------------------------
old_start = "  const url=CC_DIR+encodeURIComponent(dir)+'/'+CC_FILE, t0=performance.now();"
i = layer.index(old_start)
# anchored on the staleness guard, which every loader callback now carries
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
  loader.load(b64,g=>{
    if(tok!==openTok) return;   // an earlier ship's model must not land here
    clearModel();current=g.scene;
    current.traverse(o=>{if(o.isMesh&&o.material)
      (Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{
        m.side=THREE.DoubleSide;
        /* The models carry no textures and one material named "Default".
           glTF's spec default is metalness 1.0 - a mirror - which with no
           environment reads as a white blob. CC_HULL is declared in
           _layer.src.html; this block is the one the deploy build uses. */
        m.color=new THREE.Color(CC_HULL.color);
        m.metalness=CC_HULL.metalness;
        m.roughness=CC_HULL.roughness;
        m.envMapIntensity=1.0;
        m.needsUpdate=true;
      });});
    scene.add(current); const i=frame(current);
    still.style.transition=''; still.style.opacity=0;
    status.textContent=dir+' \\u00b7 '+((performance.now()-t0)/1000).toFixed(1)+'s \\u00b7 '+
      i.sz.x.toFixed(1)+' \\u00d7 '+i.sz.y.toFixed(1)+' \\u00d7 '+i.sz.z.toFixed(1)+
      ' \\u00b7 draco';},
    x=>{if(tok!==openTok)return;
      if(x.lengthComputable)status.textContent='loading '+Math.round(x.loaded/x.total*100)+'%';},
    e=>{if(tok!==openTok)return;
      status.textContent='model failed to load';console.warn('[cc]',dir,e);});"""
layer = layer[:i] + new_load + layer[j:]

# thumbnails ride along with the deploy build as resized webp, so the stage
# is never blank while a model streams in.
_img_old = "  const img=CC_DIR+encodeURIComponent(dir)+'/image.webp';\n"
_img_new = "  const img='images/'+CC_SAFE(dir)+'.webp';\n"
# a silent no-op here would ship a page that 404s every thumbnail while looking
# like a clean build - this substitution has to be proven, not assumed
assert _img_old in layer, "thumbnail src line not found - build_full.py is out of step with the layer"
layer = layer.replace(_img_old, _img_new)


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
const CC_SAFE = n => String(n).replace(/[^A-Za-z0-9._-]+/g,'_');
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

# ---- password gate ---------------------------------------------------------
GATE = """<style>
html.cc-locked, html.cc-locked body{overflow:hidden !important}
html.cc-locked body > *:not(#cc-gate){display:none !important}
#cc-gate{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;
  justify-content:center;background:#070C14;
  font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}
#cc-gate .box{width:min(92vw,430px);background:#0E1B2E;
  border:1px solid rgba(0,201,167,.35);border-radius:12px;padding:34px 32px;
  box-shadow:0 26px 70px rgba(0,0,0,.65)}
#cc-gate h1{margin:0 0 6px;font-size:25px;color:#E6F1F8;font-weight:700;letter-spacing:.01em}
#cc-gate p{margin:0 0 22px;font-size:15px;line-height:1.5;color:#7E97A8}
#cc-gate label{display:block;font-size:13px;color:#7E97A8;margin:0 0 7px;
  text-transform:uppercase;letter-spacing:.09em}
#cc-gate input{width:100%;box-sizing:border-box;background:#081120;
  border:1px solid rgba(0,201,167,.32);border-radius:7px;padding:13px 15px;
  color:#E6F1F8;font-size:17px;outline:none}
#cc-gate input:focus{border-color:#00C9A7;box-shadow:0 0 0 3px rgba(0,201,167,.16)}
#cc-gate button{width:100%;margin-top:15px;background:#00C9A7;border:0;border-radius:7px;
  padding:14px;font-size:16px;font-weight:700;color:#04202A;cursor:pointer}
#cc-gate button:hover{background:#3FE3C4}
#cc-gate .err{margin-top:13px;font-size:14px;color:#FF6B6B;min-height:19px}
#cc-gate .ft{margin-top:20px;font-size:12.5px;color:#4E6373;line-height:1.5}
</style>
<div id="cc-gate">
  <div class="box">
    <h1>Citizen Compass</h1>
    <p>Private preview. Enter the password you were given.</p>
    <label for="cc-pw">Password</label>
    <input id="cc-pw" type="password" autocomplete="off" autocapitalize="off" spellcheck="false">
    <button id="cc-go">Enter</button>
    <div class="err" id="cc-err"></div>
    <div class="ft">Star Citizen&reg; and Roberts Space Industries&reg; are registered
      trademarks of Cloud Imperium Rights LLC. Unofficial fan project.</div>
  </div>
</div>
<script>
(function(){
  var H = __GATEHASH__;
  function h(s){ s='cc-2026-'+String(s).toLowerCase().trim(); var x=2166136261>>>0;
    for(var i=0;i<s.length;i++){ x^=s.charCodeAt(i); x=Math.imul(x,16777619)>>>0; } return x>>>0; }
  var root=document.documentElement;
  function unlock(){ try{localStorage.setItem('ccGate','1');}catch(e){}
    root.classList.remove('cc-locked');
    var g=document.getElementById('cc-gate'); if(g) g.remove();
    window.dispatchEvent(new Event('resize')); }
  var already=false; try{ already = localStorage.getItem('ccGate')==='1'; }catch(e){}
  if(already){ var g0=document.getElementById('cc-gate'); if(g0) g0.remove(); return; }
  root.classList.add('cc-locked');
  function tryIt(){ var v=document.getElementById('cc-pw').value;
    if(h(v)===H) unlock();
    else { document.getElementById('cc-err').textContent='Not quite - try again.';
           document.getElementById('cc-pw').select(); } }
  document.getElementById('cc-go').onclick=tryIt;
  document.getElementById('cc-pw').addEventListener('keydown',function(e){
    if(e.key==='Enter') tryIt(); });
  setTimeout(function(){ var i=document.getElementById('cc-pw'); if(i) i.focus(); },60);
})();
</script>
"""
def _gh(pw):
    s = 'cc-2026-' + pw.lower().strip()
    x = 2166136261
    for ch in s:
        x ^= ord(ch); x = (x * 16777619) & 0xFFFFFFFF
    return x
GATE = GATE.replace('__GATEHASH__', str(_gh('apples')))
# the gate must be the first thing in <body>
_b = out.lower().index('<body')
_b = out.index('>', _b) + 1
out = out[:_b] + '\n' + GATE + out[_b:]

# newline='' is what makes this build REPRODUCIBLE ACROSS PLATFORMS. Not
# optional, and it has already been lost once to a concurrent edit.
#
# Text mode with the default newline=None translates every '\n' to os.linesep
# on write: '\n' on Linux, '\r\n' on Windows. Identical inputs then produce a
# byte-different artifact depending on which machine ran the build - 8,473
# extra CR bytes here, one per line, and a completely different sha256 despite
# character-for-character identical content.
#
# That breaks the hash comparison that is supposed to prove the built artifact
# matches production: it reports a mismatch for a reason with nothing to do
# with the content, so the next person either chases a phantom change or
# redeploys to "fix" it and churns the live site for nothing.
open(OUT+'/index.html','w',encoding='utf-8',newline='').write(out)

# ---------------------------------------------------------------------------
# Standalone pages that ship alongside index.html.
#
# These are NOT generated - they are authored in _src/ and copied. An earlier
# build silently dropped keybinds.html: no error, no warning, and the KEYBINDS
# tab would have 404'd on a deploy that reported complete success. A file that
# only exists because a human once put it there is a file that vanishes on the
# next build.
#
# Adding a page = one line in PAGES. Missing source = hard failure, never a
# silent skip, because a silent skip is exactly the defect this block exists
# to close.
# ---------------------------------------------------------------------------
import shutil
PAGES = [
    ('keybinds.src.html', 'keybinds.html'),
    ('loadout.src.html',  'loadout.html'),
    ('find.src.html',     'find.html'),
]
_copied, _absent = [], []
for _src_name, _out_name in PAGES:
    _s = os.path.join(SRC, _src_name)
    if os.path.exists(_s):
        shutil.copyfile(_s, os.path.join(OUT, _out_name)); _copied.append(_out_name)
    else:
        _absent.append(_src_name)
if _absent:
    sys.exit("PAGE SOURCE MISSING: %s\n"
             "index.html was written but these pages were NOT copied, so any link\n"
             "to them would 404. Fix the source or remove the entry from PAGES.\n"
             "Failing loudly rather than shipping a page with dead links."
             % ', '.join(_absent))
print('pages copied:', ', '.join(_copied) if _copied else 'none')
print('written:', len(out)/1048576, 'MB')
