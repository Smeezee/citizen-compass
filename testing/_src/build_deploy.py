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


# The device panel has one writer: device_engine.js. Inject it into both hosts
# BEFORE EITHER HOST IS READ - not merely before the pages are copied.
#
# THIS USED TO SIT AFTER index.html HAD ALREADY BEEN WRITTEN. _layer.src.html is
# read into `layer` just below and index.html is built from that string, so
# injecting afterwards updated the file on disk but not the copy already in
# memory. A device_engine.js change therefore reached index.html only on the
# NEXT build, and the build reported success either way. The old comment here
# claimed "a build can never ship a stale copy" while the code shipped exactly
# that.
#
# Found 2026-08-09 by grepping the built index.html for a symbol the engine
# patch had just added, and not finding it.
import subprocess as _sp
_r=_sp.run([sys.executable, os.path.join(SRC,'inject_engine.py')],
           capture_output=True, text=True)
sys.stdout.write(_r.stdout)
if _r.returncode!=0:
    sys.exit("ENGINE INJECTION FAILED - refusing to build:\n"+_r.stdout+_r.stderr)

# ---------------------------------------------------------------------------
# BEHAVIOURAL GATES. Run before anything is written, and fail closed.
#
# Each of these harnesses exists because the behaviour it covers shipped
# broken, and each proves itself by re-running against a deliberately broken
# copy of its own subject - so a harness that has quietly stopped testing
# anything reports that instead of a pass. See rule 12.
#
# FAIL CLOSED WHEN node IS ABSENT, exactly as inject_engine.py does. node is
# already a build dependency; the alternative is a build that skips its own
# tests and still says "safe to deploy".
# ---------------------------------------------------------------------------
import io, shutil as _sh
_node = _sh.which("node")
if _node is None:
    sys.exit("NODE NOT ON PATH, so the behavioural gates could not run.\n"
             "Refusing to build rather than deploy code whose tests were skipped.")

for _h in ("_verify_slots.js", "_verify_conflict.js", "_verify_poll.js",
           "_verify_navkeys.js", "_verify_loadout_data.js"):
    _p = os.path.join(SRC, _h)
    if not os.path.exists(_p):
        sys.exit("MISSING GATE: %s is gone. A gate that has been deleted is not a\n"
                 "gate that passed - restore it or remove it from this list\n"
                 "deliberately." % _h)
    _r = _sp.run([_node, _p], capture_output=True, text=True)
    if _r.returncode != 0:
        sys.stdout.write(_r.stdout)
        sys.stderr.write(_r.stderr)
        sys.exit("GATE FAILED: %s. Refusing to build." % _h)
    print("gate passed: %s" % _h)

# The holo placement gate is Python, and it is run TWICE: once normally, and
# once with --prove, which feeds it a per-axis normalisation and a 3x wrong
# scalar and requires it to reject them. The node harnesses each prove
# themselves on every run; this one does the same rather than relying on
# somebody having typed --prove by hand at some point in the past.
_holo = os.path.join(SRC, "_verify_holo_placement.py")
if not os.path.exists(_holo):
    sys.exit("MISSING GATE: _verify_holo_placement.py is gone. A gate that "
             "has been deleted is not a gate that passed.")
for _args, _what in (([], "checks"), (["--prove"], "self-proof")):
    _r = _sp.run([sys.executable, _holo] + _args, capture_output=True, text=True)
    if _r.returncode != 0:
        sys.stdout.write(_r.stdout)
        sys.stderr.write(_r.stderr)
        sys.exit("GATE FAILED: _verify_holo_placement.py %s. Refusing to build."
                 % _what)
    print("gate passed: _verify_holo_placement.py (%s)" % _what)

# ---------------------------------------------------------------------------
# EVERY EXECUTABLE INLINE SCRIPT MUST PARSE.
#
# inject_engine.py syntax-checks the injected engine. Nothing checked the rest
# of the page - and on 2026-08-12 a newline inside a string literal reached
# both hosts and was caught only because somebody happened to run `node
# --check` by hand. This removes the "happened to" from the other 90% of the
# JavaScript on these pages.
#
# <script type="application/json"> data islands are NOT JavaScript and are
# skipped: reporting those as syntax errors would be a check that cries wolf,
# which is how checks get switched off.
# ---------------------------------------------------------------------------
import re as _re, tempfile as _tf
_SCRIPT = _re.compile(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", _re.S | _re.I)
_TYPE = _re.compile(r"""\btype\s*=\s*["']([^"']+)["']""", _re.I)
_JS_TYPES = {"text/javascript", "application/javascript", "module",
             "application/ecmascript", "text/ecmascript"}

def _check_inline_js(path):
    html = io.open(path, encoding="utf-8").read()
    n = 0
    for _m in _SCRIPT.finditer(html):
        _t = _TYPE.search(_m.group(1))
        if _t and _t.group(1).strip().lower() not in _JS_TYPES:
            continue
        code = _m.group(2)
        n += 1
        line0 = html.count("\n", 0, html.index(code))
        _fd, _tmp = _tf.mkstemp(suffix=".js")
        os.close(_fd)
        io.open(_tmp, "w", encoding="utf-8", newline="").write("\n" * line0 + code)
        _r = _sp.run([_node, "--check", _tmp], capture_output=True, text=True)
        os.unlink(_tmp)
        if _r.returncode != 0:
            sys.exit("SYNTAX ERROR in %s, inline script %d - refusing to build:\n%s"
                     % (os.path.basename(path), n, _r.stderr))
    if n == 0:
        sys.exit("NO EXECUTABLE INLINE SCRIPTS FOUND in %s. That is not a page this\n"
                 "build understands, and reporting a pass on it would be a check\n"
                 "that never looked." % os.path.basename(path))
    return n

for _pg in (LAYER, os.path.join(SRC, "keybinds.src.html")):
    print("inline JS parses: %s (%d blocks)"
          % (os.path.basename(_pg), _check_inline_js(_pg)))

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

# ---- 2e. HELP drawer data ---------------------------------------------------
# The walkthrough graph and the vendor table have exactly one writer:
# data-layer/processed/. They are substituted in here rather than pasted into
# _layer.src.html, so the page can never drift from the data files.
#
# These asserts are the point. A missed substitution would ship a HELP drawer
# that opens, looks fine, and contains nothing - a silent success. The renderer
# in the layer also refuses to draw if it ever sees a placeholder survive, so
# the failure is caught at build time AND at run time.
_HELP_DATA = [
    ('cc-help-data',   'keybind_troubleshooting.json'),
    ('cc-vendor-data', 'vendor_support.json'),
]
for _el, _fn in _HELP_DATA:
    _path = os.path.join(REPO, 'data-layer', 'processed', _fn)
    _raw = rd(_path)
    try:
        _obj = json.loads(_raw)
    except ValueError as _e:
        sys.exit("%s is not valid JSON (%s). Refusing to build a HELP drawer "
                 "around data that will not parse in the browser." % (_fn, _e))
    # ensure_ascii keeps the payload 7-bit; escaping '<' means a future data
    # edit can never close the <script> tag it is sitting inside.
    _js = json.dumps(_obj, ensure_ascii=True, separators=(',', ':')).replace('<', r'\u003c')
    _old = '<script type="application/json" id="%s">{"__BUILD_INJECTS__":"%s"}</script>' % (_el, _fn)
    if _old not in layer:
        sys.exit("HELP DATA PLACEHOLDER MISSING for %s. _layer.src.html no longer "
                 "carries the exact placeholder this build substitutes, so the "
                 "drawer would ship empty. Nothing was written." % _el)
    layer = layer.replace(
        _old, '<script type="application/json" id="%s">%s</script>' % (_el, _js), 1)
    print('help data injected: %s (%d bytes)' % (_fn, len(_js)))

# The placeholder must not survive anywhere in the page.
# The runtime guard inside the layer names this token too, so match the
# placeholder SHAPE rather than the bare word - otherwise this check fires
# on its own tripwire and no build can ever pass.
if '{"__BUILD_INJECTS__"' in layer:
    sys.exit("A __BUILD_INJECTS__ placeholder survived substitution. Refusing to "
             "ship a HELP drawer that would render nothing.")

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
# ---------------------------------------------------------------------------
# LOADOUT_LINK - record id -> the class id the bench is keyed on
# ---------------------------------------------------------------------------
#
# The ship page needs to open the bench on the ship being looked at. The site's
# ship records carry a record number and a display name; the bench is keyed on
# the game's class id. Joining those on the NAME at runtime is the failure mode
# data-layer/ship_resolution.json exists to have closed, so the join happens
# ONCE, here, against that artifact, and what ships is an id -> id table.
#
# Built from the page that was just assembled, so the record ids are exactly the
# ones the page holds rather than ones read from a second source that could
# disagree with it.
_res = json.loads(rd(os.path.join(REPO, 'data-layer', 'ship_resolution.json')))
_m = re.search(r'const SHIPS\s*=\s*(\[.*?\]);', out, re.S)
if not _m:
    sys.exit("could not find the SHIPS array in the assembled page, so the "
             "loadout entry point cannot be keyed on record ids. Nothing written.")
_site_ships = json.loads(_m.group(1))

_lo_src = rd(os.path.join(SRC, 'loadout_data.gen.js'))
_lm = re.search(r'LOADOUT_SHIPS\s*=\s*(\{.*?\})\s*;', _lo_src, re.S)
if not _lm:
    sys.exit("could not read LOADOUT_SHIPS out of loadout_data.gen.js. Nothing written.")
_bench = json.loads(_lm.group(1))
_bench_by_stem = {k.lower(): k for k in _bench}

_stem_by_site = {}
for _r in _res.get('matched', []):
    _stem_by_site[_r['site']] = _r['file'].rsplit('.', 1)[0].lower()

_link, _offered, _absent, _absent_names = {}, 0, 0, []
for _s in _site_ships:
    _stem = _stem_by_site.get(_s['name'])
    _cls = _bench_by_stem.get(_stem) if _stem else None
    if _cls:
        _link[str(_s['id'])] = _cls
        _offered += 1
    else:
        _absent += 1
        if len(_absent_names) < 8:
            _absent_names.append(_s['name'])

# EVERY SHIP ACCOUNTED FOR, and the two numbers must sum to the total. A spot
# check on one ship is how 315 dead ends would ship unnoticed.
if _offered + _absent != len(_site_ships):
    sys.exit("loadout link accounting does not add up: %d + %d != %d"
             % (_offered, _absent, len(_site_ships)))
if _offered == 0:
    sys.exit("no ship resolved to a bench entry, so the loadout control would "
             "never appear. Refusing to ship a dead entry point.")
print('loadout entry point: %d of %d ships offer the bench, %d correctly do not'
      % (_offered, len(_site_ships), _absent))
print('  no bench data (first few): %s' % ', '.join(_absent_names))

_link_js = ('<script>const LOADOUT_LINK=%s;</script>'
            % json.dumps(_link, ensure_ascii=True, separators=(',', ':')).replace('<', r'\u003c'))
if '</body>' in out:
    out = out.replace('</body>', _link_js + '\n</body>', 1)
else:
    out = out + _link_js

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
    # The public download page. Its job is to describe the SmartScreen warning
    # before somebody meets it, because the collector ships unsigned by ruling.
    ('download.src.html', 'download.html'),
    ('keybinds.src.html', 'keybinds.html'),
    ('loadout.src.html',  'loadout.html'),
    ('find.src.html',     'find.html'),
    ('kb_modes.gen.js',  'kb_modes.gen.js'),
    # The exporter ships as its own file rather than inlined into the page:
    # inlining would create a second copy of code that already has an owner in
    # testing/_src/sc_export.js, under the order-1 round-trip suite. Rule 14.
    ('sc_export.js',     'sc_export.js'),
    # The action browser's data, generated by build_kb_actions.py. Shipped as
    # its own file for the same reason as sc_export.js: 110 KB of action data
    # pasted into the page would be a second copy of keybinds_site.json.
    ('kb_actions.gen.js', 'kb_actions.gen.js'),
    # The holo viewer. Carries the CC_VENDOR_THREE marker, so the copy loop
    # inlines three.js/DRACO into it - no vendor/ directory in _deploy.
    ('holo.src.html',    'holo.html'),
    ('holo_data.gen.js', 'holo_data.gen.js'),
    ('loadout_data.gen.js', 'loadout_data.gen.js'),
    # A gamepad diagnostic that shares NO code with the site. That
    # independence is the point: it answers "can this browser see the
    # stick at all" without our own detection logic in the way. Copied
    # verbatim - no vendor marker, no styling, no nav.
    ('stick-test.src.html', 'stick-test.html'),
]
# VENDOR INLINING FOR COPIED PAGES - §0 option 1, not a new allowed directory.
#
# index.html gets three.js pasted into it by the build above. A page copied by
# PAGES got nothing, and _deploy has no directory a <script src="vendor/..."> 
# could point at - only images/, models/ and fonts/ are allowed there. Opening a
# vendor/ directory would be a deliberate guard edit for something this avoids
# needing at all, so instead a page that wants three.js SAYS SO with a marker and
# the copy step fills it in.
#
# Pages without the marker are copied byte-for-byte exactly as before, so this
# changes nothing for keybinds/loadout/find and the .gen.js files.
#
# ONE WRITER: the marker is substituted inside this same copy loop rather than by
# a second pass over _deploy afterwards. Rule 14.
CC_VENDOR_MARKER = '<!-- CC_VENDOR_THREE -->'
_vendor_block = f"""<script>{three}</script>
<script>{orbit}</script>
<script>{gltf}</script>
<script>{draco}</script>
<script>
/* draco decoder, inlined - no network, same bytes index.html uses */
const CC_DRACO_WRAPPER = {_json.dumps(wrapper)};
const CC_DRACO_WASM_B64 = {_json.dumps(wasm_b64)};
</script>"""

_copied, _absent, _vendored = [], [], []
for _src_name, _out_name in PAGES:
    _s = os.path.join(SRC, _src_name)
    if os.path.exists(_s):
        _dst = os.path.join(OUT, _out_name)
        _txt = rd(_s) if _src_name.endswith('.html') else None
        if _txt is not None and CC_VENDOR_MARKER in _txt:
            _txt = _txt.replace(CC_VENDOR_MARKER, _vendor_block)
            if 'cdn.jsdelivr.net' in _txt or 'https://unpkg' in _txt:
                sys.exit("%s still references a CDN after vendor inlining. "
                         "The built page would need the network. Nothing shipped."
                         % _src_name)
            open(_dst, 'w', encoding='utf-8', newline='').write(_txt)
            _vendored.append(_out_name)
        else:
            shutil.copyfile(_s, _dst)
        _copied.append(_out_name)
    else:
        _absent.append(_src_name)
if _vendored:
    print('three.js inlined into:', ', '.join(_vendored))
if _absent:
    sys.exit("PAGE SOURCE MISSING: %s\n"
             "index.html was written but these pages were NOT copied, so any link\n"
             "to them would 404. Fix the source or remove the entry from PAGES.\n"
             "Failing loudly rather than shipping a page with dead links."
             % ', '.join(_absent))
print('pages copied:', ', '.join(_copied) if _copied else 'none')
print('written:', len(out)/1048576, 'MB')

# ---------------------------------------------------------------------------
# DEPLOY GUARD - last thing before anything can be uploaded.
#
# Everything in _deploy is served PUBLICLY. On 2026-08-06 a failed
# `wrangler pages deploy` run from inside _deploy left a .wrangler/cache/
# folder behind, and the next deploy published the account id and account name
# at /.wrangler/cache/wrangler-account.json.
#
# _deploy is a directory on disk. Any tool, any half-finished command, any
# editor swap file can write into it, and whatever is there goes to the
# internet on the next deploy with nobody looking. So the build refuses to
# finish while anything unexpected is sitting in it.
#
# The allowed FILE list is passed from PAGES above rather than duplicated, so
# adding a page still means editing exactly one list.
# ---------------------------------------------------------------------------
from check_deploy_clean import enforce as _deploy_guard
_allowed = {'index.html'} | {_o for _s, _o in PAGES}
if _deploy_guard(OUT, allowed_files=_allowed):
    sys.exit("BUILD FAILED: refusing to leave _deploy in a state that would "
             "publish unexpected files. Nothing has been uploaded.")
