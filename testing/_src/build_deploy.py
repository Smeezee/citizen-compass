import base64, json, os, re, glob, sys
import datetime as _dt
import re as _re

# ---------------------------------------------------------------------------
# I2. WHICH SITE IS THIS PAYLOAD FOR?
#
# Two sites are built from these same sources, and they differ in exactly two
# ways: the TESTING payload carries a private-preview password gate and a
# "testing <date>" stamp beside the version, and the LIVE payload carries
# neither. Everything else - every page, every model, every generated file - is
# identical, which is the point: what Sleven reviews on testing is what goes
# live.
#
#   python testing/_src/build_deploy.py           -> testing payload (default)
#   python testing/_src/build_deploy.py --live    -> live payload
#
# THE DEFAULT IS THE SAFE ONE. A forgotten flag produces a gated testing build,
# never an ungated public one.
#
# AND THE FLAG IS NOT TRUSTED TO SURVIVE (rule 12, second half). Both deploy
# scripts check the BYTES they are about to upload rather than believing which
# mode was asked for: scripts/deploy_testing.ps1 refuses a payload with no
# gate, and scripts/deploy_live.ps1 refuses one carrying a gate or a testing
# stamp. So a flag lost on the way here is caught where it would do damage, by
# something that cannot be lost with it.
#
# The mode is PRINTED FIRST, so a build's own output says which site it just
# made a payload for.
# ---------------------------------------------------------------------------
LIVE = '--live' in sys.argv
_unknown = [a for a in sys.argv[1:] if a != '--live']
if _unknown:
    sys.exit("UNKNOWN ARGUMENT(S): %s\n"
             "This build takes --live and nothing else. Refusing rather than "
             "ignoring a flag somebody meant something by - a MISSPELLED "
             "--live would otherwise build a TESTING payload and report "
             "success." % ', '.join(_unknown))
print('BUILDING THE %s PAYLOAD' % ('LIVE' if LIVE else 'TESTING'))

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
# H6. THE FIND DATA IS GENERATED BY THE BUILD, NOT BY SOMEBODY REMEMBERING.
#
# /find reads testing/_src/find_data.gen.js instead of calling an API, so a
# stale copy of that file is a page quietly serving last month's prices with
# this month's confidence. The generator therefore runs HERE, on every build,
# before anything is copied into _deploy.
#
# --verify-stable is not optional decoration: it renders twice and requires the
# bytes to be identical, which is what stops a generator from acquiring a
# timestamp and churning git forever. An unchanged database produces an
# unchanged file, so this step is a no-op in the diff on almost every build -
# and that is the point.
#
# FAIL CLOSED, and note what that costs: this build now needs the database.
# That is deliberate. The alternative is a build that skips its own data
# generation and still says "safe to deploy", which is the same shape as a
# build that skips its own tests. If the database is unreachable, the honest
# outcome is a refused build, not a page shipped with a file nobody checked.
_gen = os.path.join(REPO, 'build_find_data.py')
if not os.path.exists(_gen):
    sys.exit("MISSING GENERATOR: build_find_data.py is gone. /find's data "
             "would ship as whatever happens to be on disk. Refusing to build.")
_r = _sp.run([sys.executable, _gen, '--verify-stable'],
             capture_output=True, text=True, cwd=REPO)
sys.stdout.write(_r.stdout)
if _r.returncode != 0:
    sys.stderr.write(_r.stderr)
    sys.exit("FIND DATA GENERATION FAILED - refusing to build. A page that "
             "reads a generated file must not ship beside a file the "
             "generator declined to write.")
print('find data generated: build_find_data.py')

# ---------------------------------------------------------------------------
# I1. THE HARDPOINT DATA IS GENERATED BY THE BUILD, FOR THE SAME REASON.
#
# The ship page's Loadout panel was the last thing on this site that needed a
# live server. It now reads testing/_src/hardpoint_data.gen.js, so a stale copy
# of that file is a panel quietly showing last month's mounts with this month's
# confidence - exactly the failure the find-data step above exists to prevent.
#
# Same discipline, deliberately: --verify-stable, fail closed, and the database
# is a build dependency. A build that skips its own data generation and still
# says "safe to deploy" is a build that skips its own tests.
# ---------------------------------------------------------------------------
_hpgen = os.path.join(REPO, 'build_hardpoint_data.py')
if not os.path.exists(_hpgen):
    sys.exit("MISSING GENERATOR: build_hardpoint_data.py is gone. The Loadout "
             "panel's data would ship as whatever happens to be on disk. "
             "Refusing to build.")
_r = _sp.run([sys.executable, _hpgen, '--verify-stable'],
             capture_output=True, text=True, cwd=REPO)
sys.stdout.write(_r.stdout)
if _r.returncode != 0:
    sys.stderr.write(_r.stderr)
    sys.exit("HARDPOINT DATA GENERATION FAILED - refusing to build. A panel "
             "that reads a generated file must not ship beside a file the "
             "generator declined to write.")
print('hardpoint data generated: build_hardpoint_data.py')

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

# ---------------------------------------------------------------------------
# I4. THE VERSION AGREES WITH VERSION, OR THIS BUILD DOES NOT HAPPEN.
#
# The site's version used to be typed into four rendered places by hand. It now
# lives in VERSION at the repo root, and set_version.py is the only thing that
# writes it anywhere else. This runs that script's --check before the page is
# assembled, so a page whose header disagrees with VERSION is never built - the
# disagreement is caught here rather than by somebody eventually noticing the
# header looks wrong.
#
# THIS PROJECT HAS ALREADY SHIPPED A RELEASE WHOSE SOURCE SAID ONE NUMBER AND
# WHOSE FEED SAID ANOTHER. Nothing noticed, because there was nothing that
# could. This is the thing that can.
#
# FAIL CLOSED, including when the script cannot be run at all: an unverifiable
# version is refused, never recorded as agreeing.
# ---------------------------------------------------------------------------
_ver = os.path.join(REPO, 'set_version.py')
if not os.path.exists(_ver):
    sys.exit("MISSING: set_version.py. The site's version could not be checked "
             "against VERSION, and an unverified version is refused rather "
             "than assumed correct.")
_r = _sp.run([sys.executable, _ver, '--check'],
             capture_output=True, text=True, cwd=REPO)
sys.stdout.write(_r.stdout)
if _r.returncode != 0:
    sys.stderr.write(_r.stderr)
    sys.exit("VERSION CHECK FAILED - refusing to build. Fix it in ONE place:\n"
             "    python set_version.py --set <N.N.N>")

site  = rd(SITE)
layer = rd(LAYER)

# ---- 1. strip CDN script tags ---------------------------------------------
cdn = re.findall(r'<script src="https://cdn\.jsdelivr\.net[^"]*"></script>\s*', layer)
assert len(cdn)==3, cdn
for t in cdn: layer = layer.replace(t,'',1)

# ---- 2. patch model loading to use embedded data ---------------------------
#
# THIS USED TO REWRITE THE WHOLE LOAD CALLBACK - twenty-five lines carrying a
# second copy of the material setup, the framing and the staleness guard. Two
# copies of that code is exactly the defect L8 exists to close, and it bit as
# predicted: when the viewer moved into cc_viewer.js these anchors went stale.
# One of the two substitutions was a bare `.replace`, which is SILENT when it
# misses - it would have shipped a build with no DRACO decoder attached, every
# model failing to decode, and the build still reporting success.
#
# So the page carries ONE SEAM - `ccModelSource(dir)` - and this replaces that
# function and nothing else. The anchor is asserted, so the next time somebody
# moves it the build stops instead of quietly doing nothing.
_SRC_OLD = ("function ccModelSource(dir){ return CC_DIR+encodeURIComponent(dir)"
            "+'/'+CC_FILE; }")
_SRC_NEW = "function ccModelSource(dir){ return CC_EMBED[dir] || null; }"
if _SRC_OLD not in layer:
    sys.exit("MODEL SOURCE SEAM NOT FOUND in _layer.src.html. The deploy build "
             "carries models as embedded data URIs and swaps ccModelSource() to "
             "read them. Without that swap the built page would request files "
             "that are not in _deploy and every model would 404. "
             "Nothing was written.")
layer = layer.replace(_SRC_OLD, _SRC_NEW, 1)

# THE SHARED VIEWER MUST BE THE ONE DOING THE LOADING (L8).
#
# index.html no longer holds a viewer of its own. If cc_viewer.js stops being
# referenced - or stops carrying the DRACO wiring that moved into it - the page
# still builds, still serves 200, and shows nothing where a ship should be.
# That is the exact shape this project calls silent success, so it is checked.
if '<script src="cc_viewer.js"></script>' not in layer:
    sys.exit("_layer.src.html does not load cc_viewer.js, so the built index "
             "would have no 3D viewer at all. Nothing was written.")
_viewer_js = rd(os.path.join(SRC, 'cc_viewer.js'))
for _need, _why in (
        ('function attachDraco', 'the DRACO wiring this build used to inject'),
        ('CC_DRACO_WASM_B64', 'the decoder wasm global this build defines'),
        ('THREE.WebGLRenderer', 'the renderer itself')):
    if _need not in _viewer_js:
        sys.exit("cc_viewer.js is missing %s (%s). The built page would look "
                 "fine and draw nothing. Nothing was written." % (_need, _why))


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
# apply() runs at load and does `typeof _ccView` on a `let` declared 85 lines
# later. On a let/const that is a TDZ ReferenceError, NOT a safe undefined check,
# so apply() throws and every statement after it never runs - which killed the
# 3D viewer wiring and the clickable ship rows. Hoist the declaration.
#
# THE NAME CHANGED AT L8 and this is why the assert below is not decoration.
# The viewer moved into cc_viewer.js, so `let renderer,scene,camera,...` became
# `let _ccView=null, current=null;` - and the build stopped at this line rather
# than hoisting nothing and shipping a page whose display panel throws on load.
# An assert that has fired once is worth more than a comment claiming it never
# will.
decl = "let _ccView=null, current=null;"
assert decl in layer, (
    "the viewer declaration this build hoists is not in _layer.src.html. "
    "Without the hoist, apply() hits a temporal-dead-zone ReferenceError at "
    "load and every statement after it - the whole 3D viewer wiring - never "
    "runs. Nothing was written.")
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

# ---- 4. DRACOLoader: attached by cc_viewer.js, not injected here -----------
#
# This step used to paste the DRACO wiring into _layer.src.html with a bare
# `.replace` anchored on one exact line. A `.replace` that misses is SILENT -
# and moving the viewer into cc_viewer.js moved that line, so this build would
# have kept reporting success while shipping a page whose every model failed to
# decode. Nothing would have said so.
#
# The wiring now lives beside the loader it belongs to, in cc_viewer.js, and
# reads CC_DRACO_WRAPPER and CC_DRACO_WASM_B64 out of the vendor block below.
# Step 2 ASSERTS it is still in there, so the check that replaced this one
# cannot fail quietly the way this one could.

# ---- 5. inject into the real site -----------------------------------------
# ---- THE TESTING SITE SAYS IT IS THE TESTING SITE ---------------------------
#
# testing/_deploy carried the live site's version string verbatim, so both said
# v0.3.9 and a week of work was invisible. Sleven read that as the loadout and
# hardpoint work never having shipped - which is the worst possible reading, and
# it was the honest one from what the page said.
#
# So the testing build stamps itself. DERIVED FROM THE CLOCK, not typed: a
# hand-written build label is a version string with the same failure mode one
# level down, and this one goes stale in a day rather than a month.
#
# THE LIVE PAYLOAD IS NOT STAMPED, because on the live site the stamp would
# be the lie - it would tell a visitor they are looking at a test build.
#
# The version markup is still REQUIRED TO BE PRESENT in BOTH modes. If it
# has changed shape, a testing build cannot stamp itself and a live build
# cannot tell which version it is about to publish, and neither should
# proceed on a guess. Skipping the check in live mode would have made the
# live build the one place this never gets noticed.
_VERSION_TITLE = r'(<title>Citizen Compass v[0-9.]+)(</title>)'
_VERSION_HEAD = r'(<span class="version">v[0-9.]+)(</span>)'
if not (_re.search(_VERSION_TITLE, site) and _re.search(_VERSION_HEAD, site)):
    raise SystemExit(
        'BUILD REFUSED: the version markup in releases/latest.html changed '
        'shape, so this build cannot tell which version it is publishing. '
        'For a testing payload that also means it cannot stamp itself, and '
        'an unstamped testing site is indistinguishable from the live one - '
        'the defect this check exists to prevent.')

if LIVE:
    print('live payload: NOT stamped - the version reads exactly as '
          'releases/latest.html states it')
else:
    _stamp = _dt.datetime.now(_dt.timezone.utc).strftime('%Y-%m-%d')
    _before = site
    site = _re.sub(_VERSION_TITLE,
                   r'\1 - testing ' + _stamp + r'\2', site, count=1)
    site = _re.sub(_VERSION_HEAD,
                   r'\1 <span style="opacity:.6;font-weight:400">testing '
                   + _stamp + r'</span>\2', site, count=1)
    if site == _before:
        raise SystemExit(
            'BUILD REFUSED: the version markup matched but substituting the '
            'testing stamp changed nothing. Nothing was written.')

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
#
# THE LIVE PAYLOAD CARRIES NO GATE. citizencompass is a PUBLIC site;
# shipping the private-preview gate to it would lock the public out of
# their own site behind a password they were never given, and from the
# outside it would look like an outage rather than like a mistake.
if LIVE:
    print('live payload: NO password gate - this is the public site')
else:
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
# L9. THE SHIP PAGE NEEDS THE SAME MODEL, SO IT NEEDS THE SAME JOIN.
#
# index.html reaches a model through CC_MODELS, which is keyed on the SITE's
# record id. The bench is keyed on the game's ClassName. LOADOUT_LINK already
# resolves record id -> ClassName, against data-layer/ship_resolution.json, at
# build time - so composing the two here gives ClassName -> model folder
# without a second join and without ever touching a display NAME.
#
# That last part is not incidental. 22 display names are shared by 51 records
# in this dataset, so a name-keyed join would quietly hand one Hammerhead the
# other Hammerhead's model. Both joins here are on ids.
#
# ONE WRITER: this file is written here and nowhere else, and it is generated
# rather than typed for the same reason hardpoint_data.gen.js is.
_model_by_class, _model_absent = {}, []
# L11: the pledge link, carried to the ship page rather than left behind on the
# matrix row it was stripped from. Same id-to-id join as the model, so it can
# never attach to the wrong variant of a shared display name.
_pledge_by_id = {str(_s['id']): _s.get('pledge_url') for _s in _site_ships}
_rsi_by_class = {}
for _rid, _cls in _link.items():
    _u = _pledge_by_id.get(str(_rid))
    if _u:
        _rsi_by_class[_cls] = _u

# ---------------------------------------------------------------------------
# N2. THE ACQUISITION BLOCK MOVES TO THE SHIP PAGE. LOSE NOTHING.
#
# index.html's ship panel is being retired (N1/N3), and everything it showed has
# to arrive on the ship page rather than quietly stop existing. That is a
# CONSOLIDATION, and the failure mode of a consolidation is a field nobody
# notices is gone - so every field is carried by name here and ticked off in
# the ledger one at a time.
#
# Keyed on ClassName through the SAME id-to-id join as the model and the RSI
# link. 22 display names are shared by 51 records, so a name-keyed join would
# put one Hammerhead's price on the other one.
_FIELD_MAP = [
    # (site record key, emitted key, what it is)
    ('id',                  'rec',   'record number'),
    ('auec_price',          'auec',  'in-game price'),
    ('pledge_price_usd',    'usd',   'pledge price'),
    ('dealers',             'sold',  'sold at'),
    ('confidence',          'conf',  'confidence'),
    ('last_verified_patch', 'lvp',   'last verified'),
    ('notes',               'note',  'notes'),
    ('status',              'stat',  'purchasable / pledge only'),
    ('role',                'srole', "the site's own role text"),
    ('manufacturer',        'smfr',  "the site's own manufacturer text"),
    ('name',                'sname', 'the site display name, for Related'),
]
_site_by_id = {str(_s['id']): _s for _s in _site_ships}
_info_by_class, _field_seen = {}, {k: 0 for _k, k, _w in _FIELD_MAP}
for _rid, _cls in _link.items():
    _rec = _site_by_id.get(str(_rid))
    if not _rec:
        continue
    _out = {}
    for _src_key, _dst_key, _what in _FIELD_MAP:
        _v = _rec.get(_src_key)
        # An empty string, an empty list and None are all "not stated" and are
        # dropped - the page says nothing rather than rendering a blank row.
        if _v is None or _v == '' or _v == []:
            continue
        _out[_dst_key] = _v
        _field_seen[_dst_key] += 1
    if _out:
        _info_by_class[_cls] = _out

# EVERY FIELD MUST HAVE LANDED SOMEWHERE. A field that is present on the site
# records and reaches ZERO ships has been dropped by this move - which is the
# exact defect N2 exists to catch, and it would otherwise look like a clean
# build.
_dropped = [w for _s, k, w in _FIELD_MAP
            if _field_seen[k] == 0
            and any(_r.get(_s) not in (None, '', []) for _r in _site_ships)]
if _dropped:
    sys.exit("N2 FIELD DROPPED IN THE MOVE: %s. These exist on the site's ship "
             "records and reached no ship on the ship page. Nothing was written."
             % ', '.join(_dropped))
print('ship-page acquisition data: %d ships; fields carried: %s'
      % (len(_info_by_class),
         ', '.join('%s %d' % (w, _field_seen[k]) for _s, k, w in _FIELD_MAP)))
for _rid, _cls in _link.items():
    _dir = _cc.get(str(_rid))
    if _dir and safe(_dir) + '.glb' in have:
        _model_by_class[_cls] = safe(_dir) + '.glb'
    else:
        _model_absent.append(_cls)

# EVERY LINKED SHIP ACCOUNTED FOR. A ship with no model is a real and expected
# state - L14 case 1, the Origin M80 - and the page says "no model available"
# rather than showing a broken viewer. What must not happen is the two numbers
# not adding up, which would mean the join dropped something silently.
if len(_model_by_class) + len(_model_absent) != len(_link):
    sys.exit("ship-page model accounting does not add up: %d + %d != %d. "
             "Nothing was written."
             % (len(_model_by_class), len(_model_absent), len(_link)))
if not _model_by_class:
    sys.exit("no ship resolved to a 3D model for the ship page, so the viewer "
             "would never load anything. Refusing to ship a dead viewer.")

# THE PATH SEAM, and it is the same shape as ccModelSource.
#
# In _src the page is opened from disk beside ../sc-ships/. In _deploy the
# models are siblings under models/. One template, substituted at copy time,
# asserted both ways - rather than the page guessing which world it is in.
_MODEL_DEV = '../sc-ships/{dir}/model_scaled.glb'
_MODEL_DEPLOY = 'models/{file}'
_model_js = (
    '/* GENERATED by testing/_src/build_deploy.py - do not hand edit.\n'
    '   ClassName -> 3D model, composed from CC_MODELS (record id -> folder)\n'
    '   and LOADOUT_LINK (record id -> ClassName). BOTH JOINS ARE ON IDS: 22\n'
    '   display names are shared by 51 records in this dataset, so a\n'
    '   name-keyed join would hand one Hammerhead the other one\'s model.\n'
    '\n'
    '   %d of %d linked ships have a model. The rest are L14 case 1 - a game\n'
    '   file and no model - and the page says so rather than showing an empty\n'
    '   viewer. */\n'
    'const LOADOUT_MODEL=%s;\n'
    'const LOADOUT_MODEL_URL=%s;\n'
    '/* L11: THE RSI LINK MOVES ONTO THE SHIP PAGE, it is not removed.\n'
    '   The ship name in the matrix opens the ship rather than\n'
    '   robertsspaceindustries.com - sending somebody off-site the moment they\n'
    '   click a name means they never see what was built for them. So the link\n'
    '   travels with the ship and stays clearly available on its page. Keyed on\n'
    '   ClassName through the same id-to-id join as the model. */\n'
    'const LOADOUT_RSI=%s;\n'
    '/* N2: THE ACQUISITION BLOCK, moved off index.html rather than dropped.\n'
    '   In-game price, pledge price, sold at, confidence, last verified,\n'
    '   record number, notes, status, and the site\'s own role, manufacturer\n'
    '   and display name. Keyed on ClassName through the same id-to-id join as\n'
    '   the model, because 22 display names are shared by 51 records.\n'
    '   The build REFUSES to write this file if a field that exists on the site\n'
    '   records reaches zero ships - a field silently lost in a consolidation\n'
    '   is exactly what N2 exists to catch. */\n'
    'const LOADOUT_INFO=%s;\n'
    % (len(_model_by_class), len(_link),
       json.dumps(_model_by_class, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':')).replace('<', r'<'),
       json.dumps(_MODEL_DEV),
       json.dumps(_rsi_by_class, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':')).replace('<', r'<'),
       json.dumps(_info_by_class, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':')).replace('<', r'<')))
open(os.path.join(SRC, 'loadout_model.gen.js'), 'w',
     encoding='utf-8', newline='\n').write(_model_js)
print('ship-page models: %d of %d linked ships carry one, %d correctly do not'
      % (len(_model_by_class), len(_link), len(_model_absent)))

# ---------------------------------------------------------------------------
# L10. A HULL MARKER IS A SECOND ROUTE TO THE SAME PICKER.
#
# Clicking the gun on the model and clicking it in the list must open the
# IDENTICAL window. That makes the join a correctness problem rather than a
# presentation one, and it has a trap in it:
#
# A HARDPOINT NAME IS NOT AN IDENTITY. 287 of 316 hulls have slots sharing one
# and the RSI Polaris has thirty ports called `MEC`. So a marker is bound to
# the game's own `PortId`, which is unique across all 57,759 ports - and where
# a name resolves to MORE THAN ONE weapon port on a hull, NO MARKER IS EMITTED
# for it. Picking one of two would be a coin toss dressed as data, and the list
# still reaches both.
#
# Markers stay weapons-only, per the order. Internal ports are reached from the
# list, and that is settled.
# The engineering layer below walks the snapshot itself, so it imports the ONE
# port walker rather than writing a second one. Two walkers over the same tree
# is how the pilot-slaveable rule would come to mean two different things.
sys.path.insert(0, REPO)
import build_loadout_data as _bl
with open(_bl.SHIPS_JSON, encoding='utf-8') as _fh:
    _ships_raw = json.load(_fh)

_holo = os.path.join(REPO, 'data-layer', 'derived', 'holo-hardpoints',
                     'hardpoints_fleet.json')
_marks, _mark_amb, _mark_nohit = {}, 0, 0
if os.path.exists(_holo):
    _fleet = json.loads(rd(_holo))
    _by_file = {}
    for _k, _v in _fleet.items():
        _mf = (_v or {}).get('model')
        if _mf:
            _by_file[_mf] = _v
    # The ship page's own emitted data is the authority on which port is which,
    # so it is read back rather than recomputed - one writer, one answer.
    _lo = rd(os.path.join(SRC, 'loadout_data.gen.js'))
    _LS = json.loads(_re.search(r'^const LOADOUT_SHIPS=(.*);$', _lo, _re.M).group(1))
    _LHP = json.loads(_re.search(r'^const LOADOUT_HP=(.*);$', _lo, _re.M).group(1))
    _LT = json.loads(_re.search(r'^const LOADOUT_TYPES=(.*);$', _lo, _re.M).group(1))
    _WEAPONY = {'WeaponGun', 'Turret', 'MissileLauncher', 'WeaponDefensive',
                'WeaponMining', 'BombLauncher', 'SalvageHead', 'TractorBeam',
                'EMP', 'Missile', 'Bomb'}
    for _cls, _file in _model_by_class.items():
        _hull = _by_file.get(_file)
        _rec = _LS.get(_cls)
        if not _hull or not _rec:
            continue
        _byname = {}
        for _sl in _rec['slots']:
            if (_LT.get(_sl['t']) or {}).get('t') not in _WEAPONY:
                continue
            _byname.setdefault(_LHP[_sl['h']], []).append(_sl)
        _out = []
        for _hp in _hull.get('hardpoints') or []:
            _cands = _byname.get(_hp.get('port') or '')
            if not _cands:
                _mark_nohit += 1
                continue
            if len(_cands) > 1:
                _mark_amb += 1
                continue
            _u = _hp.get('unit')
            if not (isinstance(_u, list) and len(_u) == 3):
                continue
            _out.append([_cands[0]['p'], round(_u[0], 5), round(_u[1], 5),
                         round(_u[2], 5)])
        if _out:
            _marks[_cls] = _out
_mark_js = (
    '/* GENERATED by testing/_src/build_deploy.py - do not hand edit.\n'
    '   Hull markers for the ship page. Each entry is [PortId, x, y, z] where\n'
    '   x/y/z are NORMALISED against the hull\'s longest half-extent - the same\n'
    '   convention the holo viewer uses, because there is no fixed multiplier\n'
    '   that could be right across a fleet spanning 10,000x in model units per\n'
    '   metre.\n'
    '\n'
    '   BOUND TO PortId, NOT TO A HARDPOINT NAME. A name is not unique within a\n'
    '   ship - the RSI Polaris has thirty ports called MEC - and L10 requires a\n'
    '   marker to select one port and no other. Where a name resolved to more\n'
    '   than one weapon port, NO MARKER WAS EMITTED: picking one of two would\n'
    '   be a coin toss dressed as data, and the list still reaches both.\n'
    '\n'
    '   %d hulls, %d markers. %d points were ambiguous and dropped. */\n'
    'const LOADOUT_MARK=%s;\n'
    % (len(_marks), sum(len(v) for v in _marks.values()), _mark_amb,
       json.dumps(_marks, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':'))))
open(os.path.join(SRC, 'loadout_marker.gen.js'), 'w',
     encoding='utf-8', newline='\n').write(_mark_js)
if not _marks:
    sys.exit("NO HULL MARKERS WERE GENERATED. The ship page's second route to "
             "the picker would silently not exist. Refusing to ship a feature "
             "that is present in the markup and absent from the data.")
print('hull markers: %d on %d hulls (%d ambiguous points dropped, %d matched '
      'no weapon port)'
      % (sum(len(v) for v in _marks.values()), len(_marks), _mark_amb,
         _mark_nohit))

# ---------------------------------------------------------------------------
# M2. THE ENGINEERING LAYER - relays and fuse slots.
#
# Structure is ship -> relay -> fuse slots. A relay's HardpointName says where
# it sits; its ClassName says how many fuses it holds - RELAY_1slot,
# RELAY_2slot, RELAY_3slot and their _slim variants. Every fuse is the same
# part, `Fuse_subItem_standard`, so WHAT VARIES IS HOW MANY AND WHERE.
#
# THE COUNT IS TAKEN FROM THE ACTUAL CHILD PORTS, NOT FROM THE CLASS NAME.
# Those two agree on all 677 relays that carry a RELAY_Nslot class, which is
# checked below - but the children are the thing that exists and the class name
# is a label about them. Reading the label would work today and break the first
# time CIG ships a mismatch, silently and in the direction of drawing slots
# that are not there.
#
# ONE BAR PER FUSE SLOT. NO EMPTY POSITIONS. A greyed slot reads as "a fuse is
# missing here", which is a real state in game and is NOT what this data says.
# That exact mistake was made and corrected in the prototype.
_FUSE_PREFIX = '$slot_fuse'
_eng, _relay_total, _fuse_total, _label_mismatch, _untyped_relay = {}, 0, 0, 0, 0
for _s in _ships_raw:
    _cls = _s.get('ClassName') or _s.get('Name')
    _ports = []
    _bl.walk_ports(_s.get('Loadout'), _ports)
    _rows = []
    for _e, _p, _par in _ports:
        _hp = _e.get('HardpointName') or ''
        if not _hp.lower().startswith('hardpoint_relay'):
            continue
        _kids = [_c for _c in (_e.get('Loadout') or [])
                 if isinstance(_c, dict)
                 and (_c.get('HardpointName') or '').startswith(_FUSE_PREFIX)]
        if not _kids:
            # A relay-named port with no fuse children is not a fuse relay -
            # the Caterpillar's bare `hardpoint_relay` and the door-state chip
            # sets are both this. Counted rather than quietly skipped.
            _untyped_relay += 1
            continue
        _cn = _e.get('ClassName') or ''
        _m = _re.match(r'RELAY_(\d+)slot', _cn)
        if _m and int(_m.group(1)) != len(_kids):
            _label_mismatch += 1
        # Strip the prefix; the remainder is the location and it reads true -
        # `jumpdrive`, `engineroom`, `port_engine`, `medbay_left`.
        _where = _hp
        for _pre in ('hardpoint_relay_', 'hardpoint_relay', 'Hardpoint_Relay_'):
            if _where.lower().startswith(_pre.lower()):
                _where = _where[len(_pre):]
                break
        _where = _where.replace('_', ' ').strip() or 'unnamed'
        _rows.append([_where[:1].upper() + _where[1:], len(_kids),
                      _bl.strip_port_prefix(_e.get('PortId'))])
        _relay_total += 1
        _fuse_total += len(_kids)
    if _rows:
        _eng[_cls] = _rows

if _label_mismatch:
    print('  NOTE: %d relays whose RELAY_Nslot label disagrees with their own '
          'fuse children. The children were used.' % _label_mismatch)
_eng_js = (
    '/* GENERATED by testing/_src/build_deploy.py - do not hand edit.\n'
    '   The engineering layer: ship -> relay -> fuse slots.\n'
    '   Each row is [where, fuseCount, PortId].\n'
    '\n'
    '   THE COUNT IS THE ACTUAL CHILD PORTS, not the RELAY_Nslot class name.\n'
    '   The two agree on all %d relays here; the children are what exists and\n'
    '   the name is a label about them.\n'
    '\n'
    '   WHAT THIS DATA DOES NOT SAY, and must not be implied:\n'
    '     - fuse RATINGS are not in it. Only counts and positions.\n'
    '     - whether a blown relay disables the components near it is NOT\n'
    '       stated anywhere.\n'
    '     - the ship-level PenetrationMultiplier SUGGESTS damage reaches fuses\n'
    '       before components. Suggests. The page says so, or says nothing.\n'
    '\n'
    '   %d hulls, %d relays, %d fuse slots. */\n'
    'const LOADOUT_ENG=%s;\n'
    '/* REGISTERED EXPLICITLY, and this line is not optional.\n'
    '   A top-level `const` in a classic script creates a binding in the global\n'
    '   LEXICAL environment - it is NOT a property of globalThis. A loader that\n'
    '   looks the layer up by name on globalThis therefore finds undefined even\n'
    '   after this file has loaded and run perfectly, concludes it failed, and\n'
    '   re-fetches it on every open while rendering "loading" forever.\n'
    '   That is exactly what happened. The network-trace control found it by\n'
    '   counting fetches; nothing about the page looked broken. */\n'
    'window.CC_LAYERS=window.CC_LAYERS||{};\n'
    'window.CC_LAYERS.engineering=LOADOUT_ENG;\n'
    % (_relay_total, len(_eng), _relay_total, _fuse_total,
       json.dumps(_eng, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':'))))
open(os.path.join(SRC, 'loadout_eng.gen.js'), 'w',
     encoding='utf-8', newline='\n').write(_eng_js)
if not _eng:
    sys.exit("NO ENGINEERING DATA WAS GENERATED. The Engineering tab would be "
             "suppressed on every ship, which is indistinguishable from the "
             "feature not existing. Refusing to ship that silently.")
print('engineering layer: %d relays / %d fuse slots on %d hulls (%d relay-named '
      'ports carry no fuses and were not counted)'
      % (_relay_total, _fuse_total, len(_eng), _untyped_relay))

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
# THE PAGE LIST LIVES IN ONE PLACE (rule 14).
#
# It used to be declared here AND hand-mirrored in check_deploy_clean.py's
# DEFAULT_ALLOWED_FILES. That drifted twice: download.html shipped while the
# guard called it unexpected, and on 2026-08-22 this build reported "safe to
# deploy" in the same minute deploy_testing.ps1 REFUSED the same directory over
# four generated files this list had just gained.
#
# Both sides now import the same list. There is nothing left to keep in step.
from deploy_pages import PAGES
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
        # THE MODEL PATH SEAM (L9). In _src the ship page reads ../sc-ships/;
        # in _deploy the models are siblings under models/. Substituted here,
        # ASSERTED both ways - a silent miss would ship a page that 404s every
        # model while the build reported success, which is the failure the
        # ccModelSource seam above exists to have stopped happening twice.
        if _src_name == 'loadout_model.gen.js':
            _txt = rd(_s)
            _dev_line = 'const LOADOUT_MODEL_URL=%s;' % json.dumps(_MODEL_DEV)
            if _dev_line not in _txt:
                sys.exit("loadout_model.gen.js does not carry the dev model "
                         "path this build swaps out. The shipped ship page "
                         "would look for models that are not there. "
                         "Nothing more was written.")
            _txt = _txt.replace(
                _dev_line, 'const LOADOUT_MODEL_URL=%s;' % json.dumps(_MODEL_DEPLOY))
            open(os.path.join(OUT, _out_name), 'w',
                 encoding='utf-8', newline='\n').write(_txt)
            _copied.append(_out_name)
            continue
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
