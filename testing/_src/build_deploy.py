import atexit, base64, json, math, os, re, glob, sys
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

# ---------------------------------------------------------------------------
# Q31: COMMENTS DO NOT SHIP. THEY STAY IN _src.
#
# Sleven, 2026-08-29: nothing on the public site may hint it was built by
# anything other than a person - not the pages, and not the source behind them.
# The pages were already clean. View-source was not: 1,114 comment blocks, and
# 45 of them read as a conversation between a person and several named agents.
#
# One function, used at EVERY point where text enters _deploy, so there is no
# second path a file can arrive by. The scanner is testing/_src/strip_comments.py
# and it is proven separately by checks/_verify_comment_strip.py, which hands
# every stripped file to `node --check` rather than believing the stripper.
#
# @license and @preserve survive - holo.html carries three.js's MIT header and
# removing it would breach the licence the library is used under.
# ---------------------------------------------------------------------------
sys.path.insert(0, SRC)
import strip_comments as _strip
_stripped_total = 0

def _for_deploy(name, text):
    """The only way text becomes a file in _deploy."""
    global _stripped_total
    try:
        out, n = _strip.strip_for(name, text)
    except ValueError as _exc:
        sys.exit("COMMENT STRIP REFUSED on %s: %s -- the file is not shaped "
                 "the way the scanner expects, and guessing would ship a "
                 "truncated page. Nothing was written." % (name, _exc))
    _stripped_total += n
    return out

# ---------------------------------------------------------------------------
# THE BUILD RECEIPT - so a FAILED BUILD CANNOT BE FOLLOWED BY AN UPLOAD.
#
# 2026-08-27: build and deploy were chained in one command, the build exited 1,
# and the deploy read only its own output and put twelve wrong models live. The
# browser-check gate could not have stopped it - that gate runs the BROWSER
# checks, and what failed here was a BUILD gate.
#
# The gate cannot be "a build must have run", because a deploy legitimately does
# not require one. So the build leaves evidence of how it ENDED, and the deploy
# refuses on evidence of failure.
#
# It is written OUTSIDE _deploy on purpose. Anything inside would have to be
# taught to the deploy guard, and a guard that has learned to expect one more
# unexpected file is worth slightly less.
#
# WHY IT PERSISTS ACROSS INVOCATIONS RATHER THAN BEING SCOPED TO ONE.
# The order says "if a build ran in this invocation and failed, stop". A receipt
# on disk is strictly stronger: it also catches a build that failed an hour ago
# and a deploy attempted afterwards without rebuilding, which is the same
# payload in the same suspect state. A receipt is cleared only by a build that
# reaches the end.
RECEIPT = os.path.join(SRC, '.last_build.json')
_BUILD_DONE = {'ok': False}


def _write_receipt(status, code, detail=''):
    import json as _rj
    import datetime as _rd
    try:
        with open(RECEIPT, 'w', encoding='utf-8') as _fh:
            _rj.dump({'status': status, 'exit_code': code,
                      'detail': str(detail)[:400],
                      'live': LIVE, 'pid': os.getpid(),
                      'at': _rd.datetime.now().isoformat(timespec='seconds')},
                     _fh, indent=1)
    except OSError:
        # A build that cannot write its own receipt must not therefore look
        # successful, but neither should it die here. The deploy treats a
        # MISSING receipt as "no build to judge" and an unreadable one as
        # failure, so silence is the safe direction.
        pass


_write_receipt('running', None, 'build started')

# sys.exit is how every gate in this file refuses, so that is where the exit
# code is. Wrapping it is what makes the receipt carry the real number rather
# than a guess.
_real_exit = sys.exit


def _exit_recording(arg=0):
    if not _BUILD_DONE['ok']:
        code = arg if isinstance(arg, int) else (0 if arg is None else 1)
        _write_receipt('failed', code, '' if isinstance(arg, int) else arg)
    _real_exit(arg)


sys.exit = _exit_recording


@atexit.register
def _receipt_final():
    # Covers the path sys.exit does not: an uncaught exception. On 2026-08-27
    # this build died on a TypeError, which is exactly that path.
    if _BUILD_DONE['ok']:
        return
    import json as _rj
    try:
        with open(RECEIPT, encoding='utf-8') as _fh:
            if _rj.load(_fh).get('status') == 'running':
                _write_receipt('failed', 1,
                               'build ended without reaching the end and '
                               'without calling sys.exit - most likely an '
                               'uncaught exception')
    except (OSError, ValueError):
        pass

def rd(p, b=False):
    if not os.path.exists(p):
        sys.exit("BUILD INPUT MISSING: %s\n"
                 "This build cannot invent it. Nothing was written." % p)
    return open(p,'rb').read() if b else open(p,encoding='utf-8').read()


# THE DISCLOSURE-BAR CSS, SUBSTITUTED FROM ONE FILE.
#
# ORDER_the-disclosure-bar: "One pattern, one implementation, used on every
# explanatory block on the site. Not five variations that drift apart." Three
# pages needed the same rules, so they read them from _disc.css rather than
# each carrying a copy.
#
# FAILS CLOSED IN BOTH DIRECTIONS. A page asking for the CSS that does not get
# it renders its bars unstyled - a summary with no chrome, which still works but
# is not what was designed - and that would ship silently. A marker present with
# the file missing stops the build. The file present and used by nobody is
# reported rather than passed over, because that is how a shared implementation
# quietly becomes an unused one while every page grows its own copy again.
CC_DISC_MARKER = '/* CC_DISC_CSS */'
_disc_css_path = os.path.join(SRC, '_disc.css')
_disc_css = rd(_disc_css_path) if os.path.exists(_disc_css_path) else None
_disc_used = []

# ---------------------------------------------------------------------------
# A1 + A3. THE ATTRIBUTION FURNITURE, ON EVERY PAGE, FROM ONE DEFINITION.
#
# The trademark notice had THREE different wordings across this site and two
# pages carrying none. It now has one, in testing/_src/attribution.py, and every
# page takes it from there - so a typo in a required legal notice is a thing
# that can be fixed once rather than found six times.
#
# THE CONTACT ADDRESS IS READ FROM CONFIGURATION AND ITS ABSENCE FAILS THE
# BUILD. A page that promises a way to complain and does not have one is worse
# than a page that promises nothing, so this refuses rather than rendering
# "contact:" followed by a blank.
sys.path.insert(0, SRC)
import attribution as _attr

# WHEN THE CONTACT IS REQUIRED, AND WHY IT IS NOT REQUIRED YET.
#
# DECIDED-BY-DEFAULT, and written down because it is a real reading of the
# order rather than a shortcut around it.
#
# A3 says the source-and-contact notice goes on "any page that displays ship
# content", and that a build with no configured address must FAIL. Taken
# literally today, that fails every build - and worse, if it did not, it would
# put a notice on the site saying the ship models "are Cloud Imperium Games'
# own, taken from the holoviewer". THAT IS NOT TRUE TODAY. Every model
# currently on this site came from the scunpacked pipeline and the Fan Kit.
# No RSI holoviewer asset has been fetched; the order forbids fetching one.
#
# So rendering A3's notice right now would be a FALSE STATEMENT on the page,
# which is the one thing this project does not do. The notice has to appear
# when the content it describes appears, and not before.
#
# The trigger is therefore A4's tag: if ANY asset is registered as CIG-sourced,
# the promise is on the site and the build REFUSES without a contact address.
# Zero tagged assets, no promise made, no address needed. The first tagged
# asset turns the requirement on by itself, with nobody remembering to.
#
# Easy to reverse in either direction: set CC_TAKEDOWN_CONTACT and the notice
# renders today; register one CIG asset and the build demands one.
_CONTACT_KEYS = ('CC_TAKEDOWN_CONTACT', 'TAKEDOWN_CONTACT')
_contact = None
for _k in _CONTACT_KEYS:
    _contact = os.environ.get(_k) or _contact
if not _contact:
    _envf = os.path.join(REPO, '.env')
    if os.path.exists(_envf):
        with open(_envf, encoding='utf-8') as _fh:
            for _line in _fh:
                _line = _line.strip()
                if not _line or _line.startswith('#') or '=' not in _line:
                    continue
                _key, _val = _line.split('=', 1)
                if _key.strip() in _CONTACT_KEYS:
                    _contact = _val.strip().strip('"').strip("'")

sys.path.insert(0, os.path.join(REPO, 'scripts'))
import cig_assets as _cig
_cig_count = _cig.tagged_count()

if _cig_count and not _contact:
    sys.exit(
        "NO TAKEDOWN CONTACT CONFIGURED, and %d CIG-sourced asset(s) are\n"
        "registered - refusing to build.\n"
        "\n"
        "Every page showing that content carries a notice saying that if Cloud\n"
        "Imperium Games would like it removed, they can write to us and it will\n"
        "be removed. That promise needs a real address behind it.\n"
        "\n"
        "Set CC_TAKEDOWN_CONTACT in the environment or in .env, for example:\n"
        "    CC_TAKEDOWN_CONTACT=takedown@example.com\n"
        "\n"
        "This build will not ship a page that offers a way to complain and then\n"
        "does not provide one. Nothing was written." % _cig_count)

if _cig_count:
    print('CIG-sourced assets registered: %d - source notice WILL be rendered'
          % _cig_count)
    print('takedown contact: configured (%d chars, not shown)' % len(_contact))
elif _contact:
    print('takedown contact: configured; no CIG-sourced assets registered yet, '
          'so the source notice renders on its own terms')
else:
    print('CIG-sourced assets registered: 0 - no source notice, and no contact '
          'needed until there is one')

_TM_BLOCK = _attr.trademark_block()
_SRC_BLOCK = _attr.source_notice(_contact) if (_cig_count and _contact) or (_contact and _cig_count) else None


def _with_attribution(_txt, _name, _ship_content):
    """Put the always-visible trademark strip on a page, and the source and
    contact notice on any page that shows ship content.

    A page that already carries a compliant sticky bar keeps it - index.html
    inherits one from the site itself - but its TEXT is normalised to the one
    constant, in the assembled output only. releases/latest.html is the live
    site's own source and is not edited here (hard rule 8); the discrepancy
    between its wording and CIG's is reported instead.
    """
    if 'class="trademark-bar"' in _txt:
        # Normalise the inherited bar's text to the one constant. The site's
        # own copy omits the full stop CIG's wording carries.
        import re as _r
        _txt = _r.sub(r'(<div class="trademark-bar">)(.*?)(</div>)',
                      lambda m: m.group(1) + _attr.TRADEMARK_HTML + m.group(3),
                      _txt, count=1, flags=_r.S)
        _add = _attr.TRADEMARK_CSS
    else:
        _add = _TM_BLOCK
    if _ship_content and _SRC_BLOCK:
        _add = _SRC_BLOCK + "\n" + _add
    # WHERE IT GOES, and why this is not simply "before </body>".
    #
    # Only ONE of the seven pages actually writes a </body>. Most close with
    # </html>, and two close with neither, because they are hand-written HTML
    # that browsers forgive. A rule that assumed </body> put the notice on one
    # page and refused the rest - and an absent legal notice looks exactly like
    # one nobody checked.
    if '</body>' in _txt:
        return _txt.replace('</body>', _add + "\n</body>", 1)
    if '</html>' in _txt:
        return _txt.replace('</html>', _add + "\n</html>", 1)
    return _txt.rstrip() + "\n" + _add + "\n"


# Which pages show ship models or imagery, and therefore carry A3's notice.
# Named rather than guessed: a page that shows a ship and does not say where it
# came from is the thing this order exists to prevent.
_SHIP_CONTENT_PAGES = {'index.html', 'loadout.html', 'holo.html'}

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
# RULE 15, the subprocess half. text=True with no encoding= decodes the child
# with the platform default - cp1252 here - and the children of this build print
# SHIP NAMES. San'tok.yai carries a macron; Yeng'tu and "Shredder" carry curly
# quotes. The reader thread dies on the first one and the build stops with a
# UnicodeDecodeError that names no ship. Same defect that stopped
# run_all_controls.py at control 14 of 98 on 2026-08-27. Every _sp.run below
# says encoding= for the same reason.
_r=_sp.run([sys.executable, os.path.join(SRC,'inject_engine.py')],
           capture_output=True, text=True, encoding="utf-8", errors="replace")
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
             capture_output=True, text=True, encoding="utf-8",
             errors="replace", cwd=REPO)
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
             capture_output=True, text=True, encoding="utf-8",
             errors="replace", cwd=REPO)
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
    _r = _sp.run([_node, _p], capture_output=True, text=True,
                 encoding="utf-8", errors="replace")
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
    # encoding + errors, and `or ""` on the write. BOTH are rule 15.
    #
    # This gate prints SHIP NAMES, and San'tok.yai is spelled with a macron.
    # Decoding its output with the platform default is the same cp1252 trap the
    # rule is about, one process removed. And on 2026-08-27 the gate genuinely
    # failed, and this block crashed on `write() argument must be str, not None`
    # BEFORE printing why - so the build died with a TypeError and the real
    # finding was invisible. A gate failing is information; a gate failure that
    # takes out its own reporter is a gate failure nobody can act on.
    _r = _sp.run([sys.executable, _holo] + _args, capture_output=True, text=True,
                 encoding="utf-8", errors="replace")
    if _r.returncode != 0:
        sys.stdout.write(_r.stdout or "(the gate produced no stdout)\n")
        sys.stderr.write(_r.stderr or "")
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

def _check_inline_js(path, require_any=True):
    # require_any: the two SOURCE pages this was written for must contain
    # scripts, and a page that suddenly has none is a defect worth refusing on.
    # The post-strip pass over _deploy re-uses the parser but not that rule -
    # download.html legitimately carries no script, and refusing on it would be
    # a check crying wolf at a page that is exactly as it should be.
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
        _r = _sp.run([_node, "--check", _tmp], capture_output=True, text=True,
                     encoding="utf-8", errors="replace")
        os.unlink(_tmp)
        if _r.returncode != 0:
            sys.exit("SYNTAX ERROR in %s, inline script %d - refusing to build:\n%s"
                     % (os.path.basename(path), n, _r.stderr))
    if n == 0 and require_any:
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
             capture_output=True, text=True, encoding="utf-8",
             errors="replace", cwd=REPO)
sys.stdout.write(_r.stdout)
if _r.returncode != 0:
    sys.stderr.write(_r.stderr)
    sys.exit("VERSION CHECK FAILED - refusing to build. Fix it in ONE place:\n"
             "    python set_version.py --set <N.N.N>")

site  = rd(SITE)
layer = rd(LAYER)

# ---- 1. NO CDN TAGS TO STRIP - index.html has no 3D viewer any more (N3) ---
#
# _layer.src.html used to pull three.js, GLTFLoader and OrbitControls from a
# CDN for local development, and this build stripped all three before inlining
# vendored copies. The ship panel and its viewer are retired: index is a LIST.
#
# THE ASSERT IS KEPT AND INVERTED rather than deleted. A CDN tag reappearing in
# the layer means somebody has put a viewer back on index, and this build would
# otherwise inline three.js again without anybody noticing the page had doubled
# in size.
cdn = re.findall(r'<script src="https://cdn\.jsdelivr\.net[^"]*"></script>\s*', layer)
if cdn:
    sys.exit("_layer.src.html references a CDN again: %s\n"
             "index.html is a list and carries no 3D viewer (N3). A CDN tag "
             "here means a viewer has come back. Nothing was written." % cdn)

# ---- 2. NO MODEL LOADING TO PATCH - the viewer is gone from index (N3) -----
#
# This step used to swap `ccModelSource()` so the built page read models from
# embedded data URIs, assert cc_viewer.js was referenced, assert the DRACO
# wiring was present, rewrite the thumbnail path, and hoist a declaration out
# of a temporal-dead-zone bug in the viewer's own wiring.
#
# All five were about a viewer index.html no longer has. They are replaced by
# ONE refusal, because the thing worth checking is no longer "did the patch
# apply" but "has a viewer come back without the build being told".
for _gone, _what in (
        ('ccModelSource', 'the model-source seam'),
        ('cc-canvas"></canvas>', 'a viewer canvas'),
        ('<script src="cc_viewer.js">', 'the shared viewer module'),
        ('CC_DRACO_WASM_B64', 'the DRACO decoder')):
    if _gone in layer:
        sys.exit("_layer.src.html carries %s (%s) again. index.html is a LIST "
                 "and loads no 3D geometry (N3); if a viewer belongs here now, "
                 "this build needs teaching rather than working around. "
                 "Nothing was written." % (_gone, _what))

# ---- 2b. NOTHING TO MATCH - the cell is emitted, not rewritten -------------
#
# This step existed to make a POST-RENDER REWRITER work: it swapped an exact
# name compare for a normalising lookup, because the site appends a link glyph
# to ship names and `td.textContent` therefore read "Redeemer 🔗". It then
# injected CC_NORM, CC_LOOKUP, CC_SAFE, CC_RSI and CC_HAS3D to support it.
#
# ALL OF IT WAS SCAFFOLDING FOR MATCHING ON DISPLAY TEXT, and on 2026-08-22 the
# normalising lookup turned out not to be applied at all - every ship name
# still opened RSI. The fix was not a better normaliser. It was to stop having
# a second writer: the build now computes each cell and `nameCellHtml()` emits
# it once (see the CC_SHIPLINK block further down).
#
# The refusal above already fails the build if a rewriter comes back.


# ---- 2c. NOTHING LEFT TO HOIST - the viewer is off index (N3) --------------
#
# This step hoisted `let _ccView=null, current=null;` above `apply()`, which
# read `typeof _ccView` eighty lines before the declaration. On a `let` that is
# a temporal-dead-zone ReferenceError rather than a safe undefined check, so
# apply() threw at load and every statement after it - the whole viewer wiring
# and the clickable rows - never ran.
#
# The viewer is retired and so is the reader. Kept as a refusal rather than
# removed: if a `let` declaration for a viewer reappears above apply(), the
# same TDZ bug comes with it, and it is silent.
if "let _ccView" in layer or "let renderer,scene,camera" in layer:
    sys.exit("_layer.src.html declares a 3D viewer again. index.html is a list "
             "(N3), and the declaration this build used to hoist carried a "
             "temporal-dead-zone bug that silently killed everything after "
             "apply(). Nothing was written.")

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
# N3: `libs` IS NOT INJECTED. index.html carried three.js (603 KB),
# OrbitControls, GLTFLoader, the DRACO decoder and its wasm as base64, plus the
# embedded model map - about 1.07 MB of vendor payload downloaded by everyone
# who opened a TABLE. The viewer moved to the ship page, which gets the same
# bytes through the CC_VENDOR_THREE marker, once, on the page that draws.
out = site[:k] + '\n<!-- Citizen Compass portable concept build -->\n' + layer + '\n' + site[k:]

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

# ---------------------------------------------------------------------------
# ERRATUM 2026-08-22. EVERY SHIP NAME STILL OPENED RSI, AND THE CONTROL COULD
# NOT HAVE FAILED.
#
# WHAT WAS WRONG. `decorate()` in the layer rewrote the name cell AFTER the site
# had rendered it, finding the ship by reading the cell's own text. But
# `nameCellHtml()` appends a link glyph - `Redeemer &#128279;` - so
# `td.textContent.trim()` was "Redeemer 🔗", the lookup missed, the function
# bailed silently, and the cell kept the RSI anchor it was born with. 229 of 254
# rows. There was NO route to any ship page at all.
#
# WHY THE GLYPH IS NOT THE BUG. Trimming the emoji would have fixed the symptom
# and left the design: one writer rendering a cell and a second racing to
# rewrite it, matched ON DISPLAY TEXT - the exact thing this project banned two
# days ago when 22 names turned out to be shared by 51 records.
#
# THE FIX. The BUILD decides, per record, what that cell should be, and
# `nameCellHtml()` reads the decision. One writer. No observer, no timers, no
# text matching, and no runtime lookup that can miss.
#
# It is injected BEFORE the site's own script, because `buildMatrix()` runs
# synchronously inside it - LOADOUT_LINK used to go in before `</body>`, which
# is after the matrix has already been built. A table that renders before its
# data arrives is the same defect one layer down.
_cell = {}
for _s in _site_ships:
    _sid = str(_s['id'])
    _cls = _link.get(_sid)
    if _cls:
        _dir = _cc.get(_sid)
        _cell[_sid] = {'h': 'loadout.html#' + _cls,
                       'm': 1 if (_dir and safe(_dir) + '.glb' in have) else 0}
    elif _s.get('pledge_url'):
        # No game file, so no ship page - and 27 of these 33 have a pledge page
        # that is the ONLY route they have. Taking it away to satisfy the letter
        # of "a name must not go to RSI" would leave the row with no link at all.
        _cell[_sid] = {'h': _s['pledge_url'], 'r': 1}
    # neither: no entry, and nameCellHtml renders a plain name

_have_page = sum(1 for v in _cell.values() if not v.get('r'))
_rsi_only = sum(1 for v in _cell.values() if v.get('r'))
if _have_page < 200:
    sys.exit("only %d ship rows resolved to a ship page. Expected ~221. The "
             "row links would be mostly dead. Nothing was written." % _have_page)
print('ship-name cells: %d point at the ship page, %d at RSI (no game file), '
      '%d plain' % (_have_page, _rsi_only, len(_site_ships) - len(_cell)))

_link_js = ('<script>const LOADOUT_LINK=%s;\nconst CC_SHIPLINK=%s;</script>\n'
            % (json.dumps(_link, ensure_ascii=True, separators=(',', ':')).replace('<', r'\u003c'),
               json.dumps(_cell, ensure_ascii=True, sort_keys=True,
                          separators=(',', ':')).replace('<', r'\u003c')))

_ANCHOR = '<script>\nconst SHIPS = ['
if _ANCHOR not in out:
    _ANCHOR = 'const SHIPS = ['
    if _ANCHOR not in out:
        sys.exit("could not find the site's SHIPS declaration, so the row-link "
                 "data cannot be injected before the matrix is built. The names "
                 "would all still point at RSI. Nothing was written.")
    out = out.replace(_ANCHOR, '</script>' + _link_js + '<script>' + _ANCHOR, 1)
else:
    out = out.replace(_ANCHOR, _link_js + _ANCHOR, 1)

# ---- nameCellHtml emits the cell, and is the ONLY thing that does ----------
_CELL_OLD = """function nameCellHtml(ship) {
  if (ship.pledge_url) {
    return `<td><a class="buy-link" href="${escapeHtml(ship.pledge_url)}" target="_blank" rel="noopener">${escapeHtml(ship.name)} &#128279;</a></td>`;
  }
  return `<td>${escapeHtml(ship.name)}</td>`;
}"""
_CELL_NEW = """function nameCellHtml(ship) {
  /* ONE WRITER. The build decided what this cell should be - see CC_SHIPLINK -
     and this reads the decision. Nothing rewrites the cell afterwards.
     The last two branches are the untouched original, kept so that
     releases/latest.html opened on its own still behaves exactly as it always
     has when the build data is absent. */
  const _n = escapeHtml(ship.name);
  const _L = (typeof CC_SHIPLINK !== "undefined") ? CC_SHIPLINK[String(ship.id)] : null;
  if (_L && !_L.r) {
    return `<td><a class="cc-open${_L.m ? "" : " cc-nomodel"}" href="${_L.h}">${_n}</a></td>`;
  }
  if (_L && _L.r) {
    return `<td><a class="cc-open cc-nobench buy-link" href="${_L.h}" target="_blank" rel="noopener" title="The game files carry no build for this ship yet, so it has no ship page. This opens its RSI pledge page.">${_n} &#128279;</a></td>`;
  }
  if (ship.pledge_url) {
    return `<td><a class="buy-link" href="${escapeHtml(ship.pledge_url)}" target="_blank" rel="noopener">${_n} &#128279;</a></td>`;
  }
  return `<td>${_n}</td>`;
}"""
if _CELL_OLD not in out:
    sys.exit("the site's nameCellHtml() is not the shape this build replaces. "
             "Every ship name would keep pointing at RSI, which is the defect "
             "this replacement exists to fix. Nothing was written.")
out = out.replace(_CELL_OLD, _CELL_NEW, 1)

# index.html is written HERE, not in the PAGES copy loop, so the shared
# disclosure CSS has to be substituted here too. It was missed the first time
# and the marker shipped as a literal CSS comment - the bar rendered unstyled
# and the build said nothing, because the "used by nobody" guard was satisfied
# by the OTHER two pages. A guard that passes because somebody else used the
# thing is not covering this page.
if CC_DISC_MARKER in out:
    if _disc_css is None:
        sys.exit("index.html asks for the shared disclosure CSS and "
                 "testing/_src/_disc.css is missing. Refusing.")
    out = out.replace(CC_DISC_MARKER, _disc_css)
    _disc_used.append('index.html')

out = _with_attribution(out, 'index.html', True)
open(OUT+'/index.html','w',encoding='utf-8',newline='').write(
    _for_deploy('index.html', out))

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

# ---------------------------------------------------------------------------
# M1. AN EDITION INHERITS ITS BASE HULL'S MODEL.
#
# 113 ships said "no 3D model available" and 76 of them are editions of a ship
# whose model we already hold - the Cutlass Black BIS2950 while DRAK_Cutlass_
# Black has one, the Carrack BIS2950 while ANVL_Carrack has one. Sleven ruled
# on this on 2026-08-14: a shared hull is correct unless the ships differ in
# external SHAPE, and an edition is paint and fitted parts. The ruling existed;
# the join was never built.
#
# THE JOIN IS EXACT AND IT IS NOT MADE HERE. build_model_inheritance.py does it
# by stripping an enumerated suffix from the ClassName and requiring the base to
# exist and to have a model - no fuzzy matching, no name similarity. This reads
# its output and applies it.
#
# THE 37 IN needs_human_review.json ARE NOT TOUCHED, and several would be wrong
# to touch: Idris-P and Idris-M differ at the nose, Sabre and Sabre Firebird are
# different airframes, Hornet Mk I and Mk II are different shapes. They are
# asserted against here so a future edit to the generator cannot quietly widen
# the rule into them.
#
# APPLIED BEFORE THE TAKEDOWN FILTER BELOW, DELIBERATELY. An inherited model is
# the same FILE as its base's, so if that file is withdrawn the edition must
# lose it too. Doing this afterwards would republish a withdrawn asset under a
# different ship's name.
# ---------------------------------------------------------------------------
_inh_dir = os.path.join(REPO, 'data-layer', 'derived', 'model-inheritance')
_inh_map = os.path.join(_inh_dir, 'model_inheritance.json')
_inh_hold = os.path.join(_inh_dir, 'needs_human_review.json')
_inherited = 0
if os.path.exists(_inh_map):
    with open(_inh_map, encoding='utf-8') as _f:
        _inh = json.load(_f)
    _held = set()
    if os.path.exists(_inh_hold):
        with open(_inh_hold, encoding='utf-8') as _f:
            for _r in json.load(_f):
                _held.add(_r.get('class_name') if isinstance(_r, dict) else _r)
    _absent = set(_model_absent)
    for _r in _inh:
        _cls, _base, _file = (_r.get('class_name'), _r.get('inherits_from'),
                              _r.get('model_file'))
        if not _cls or not _file:
            continue
        if _cls in _held:
            sys.exit("MODEL INHERITANCE TRIED TO MAP A SHIP HELD FOR HUMAN "
                     "REVIEW: %s. These are held because auto-mapping several "
                     "of them would be WRONG - different airframes, not "
                     "different paint. Nothing was written." % _cls)
        # The base must genuinely have resolved to this model in THIS build.
        if _model_by_class.get(_base) != _file:
            continue
        # ALREADY HAS ONE - LEAVE IT. An edition that resolved to its own model
        # is not a gap and must not be overwritten by its base's.
        if _cls in _model_by_class:
            continue
        _model_by_class[_cls] = _file
        _absent.discard(_cls)
        _inherited += 1
    _model_absent[:] = sorted(_absent)
    # THE ACCOUNTING INVARIANT IS ABOUT THE SHIP-PAGE LINK SET, and inheritance
    # deliberately reaches wider than it: most of the 76 editions carry a
    # loadout without carrying a ship-page link, which is why gating on
    # _model_absent alone inherited nothing on the first attempt. So the
    # invariant is restated over the linked ships only, and still has to hold.
    _linked_with_model = sum(1 for _c in _link.values() if _c in _model_by_class)
    if _linked_with_model + len(_model_absent) != len(_link):
        sys.exit("model inheritance broke the ship-page accounting: "
                 "%d + %d != %d. Nothing was written."
                 % (_linked_with_model, len(_model_absent), len(_link)))
    print('model inheritance: %d editions took their base hull\'s model '
          '(%d still have none)' % (_inherited, len(_model_absent)))
else:
    print('model inheritance: no map at %s - nothing inherited'
          % os.path.relpath(_inh_dir, REPO))

# THE PATH SEAM, and it is the same shape as ccModelSource.
#
# In _src the page is opened from disk beside ../sc-ships/. In _deploy the
# models are siblings under models/. One template, substituted at copy time,
# asserted both ways - rather than the page guessing which world it is in.
# ---------------------------------------------------------------------------
# A4. A WITHDRAWN ASSET IS WITHDRAWN FROM THE PAGE TOO, not just from the disk.
#
# The takedown moves the file out of _deploy and stamps `removed` on its
# register record. THE STAMP IS THE DURABLE HALF. Deleting the file alone would
# last exactly until the next model sync put it back, and nobody would notice
# because the page would simply start working again.
#
# So the build reads the stamp, drops those ships out of the model map, and
# publishes the list separately as LOADOUT_WITHDRAWN. The page then has enough
# to say WHY the model is missing - "removed at the rights holder's request" -
# instead of falling into the generic "no model for this hull yet" case, which
# would be a false statement about a ship whose model we removed on purpose.
# ---------------------------------------------------------------------------
_withdrawn_models = _cig.withdrawn_files('model')
_withdrawn_classes = sorted(
    c for c, f in _model_by_class.items() if f in _withdrawn_models)
for _c in _withdrawn_classes:
    del _model_by_class[_c]
if _withdrawn_classes:
    print('TAKEDOWN IN EFFECT: %d ship(s) had their model withdrawn at the '
          'rights holder\'s request' % len(_withdrawn_classes))

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
    '/* A4: ships whose 3D model was removed at the rights holder\'s\n'
    '   request. Kept SEPARATE from the plain no-model case so the page\n'
    '   can say which is which - calling a withdrawn model "we have no\n'
    '   model yet" would be untrue. */\n'
    'const LOADOUT_WITHDRAWN=%s;\n'
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
       json.dumps(_withdrawn_classes, ensure_ascii=True,
                  separators=(',', ':')).replace('<', r'<'),
       json.dumps(_rsi_by_class, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':')).replace('<', r'<'),
       json.dumps(_info_by_class, ensure_ascii=True, sort_keys=True,
                  separators=(',', ':')).replace('<', r'<')))
open(os.path.join(SRC, 'loadout_model.gen.js'), 'w',
     encoding='utf-8', newline='\n').write(_model_js)
# THE TWO NUMBERS ARE DIFFERENT SETS AND THE LINE SAYS SO. This printed
# "279 of 221 linked ships" the moment M1 landed, because it was measuring the
# whole model map against the ship-page link set - and inheritance reaches
# ships that carry a loadout without carrying a link. A count that exceeds its
# own denominator is the line reporting something it is not counting.
print('ship-page models: %d of %d linked ships carry one, %d correctly do not'
      % (sum(1 for _c in _link.values() if _c in _model_by_class),
         len(_link), len(_model_absent)))
print('models resolved in total: %d ships (%d of them by inheritance)'
      % (len(_model_by_class), _inherited))

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
_mark_inherited, _mark_stacked = 0, 0
_mark_coincident = 0
_mark_prov = {'cig': 0, 'est': 0, 'anc': 0}


def _pid_sort(p):
    """PortIds ordered so the choice between coincident markers is stable.

    Numeric ids sort as numbers, not as text - '9' must come before '10', and
    the six coincident pairs found on 2026-08-27 include exactly that case
    (HoverQuad 9 and 10). Anything non-numeric sorts after, by text, so the
    rule still terminates on ids this file has not seen.
    """
    s = str(p)
    return (0, int(s), "") if s.isdigit() else (1, 0, s)
_NO_INHERIT = os.environ.get('CC_NO_INHERIT') == '1'
if _NO_INHERIT:
    print('CC_NO_INHERIT=1 - the C1 inheritance pass is OFF (the BEFORE state)')
if os.path.exists(_holo):
    _fleet = json.loads(rd(_holo))
    # ---------------------------------------------------------------
    # CIG'S OWN HARDPOINT POSITIONS, APPLIED HERE BECAUSE THIS IS WHERE THE
    # SHIP PAGE'S MARKERS ARE ACTUALLY BORN.
    #
    # `build_holo_data.py` has read an alignment overlay for weeks - and it
    # feeds `holo_data.gen.js`, the HOLO page. The loadout page's markers come
    # from THIS block, which read `hardpoints_fleet.json` raw and applied no
    # overlay at all. So a correction landing in the overlay moved one page and
    # not the other, and the page Sleven actually looks at was the one it
    # missed.
    #
    # What goes on here is `alignment_overlay_client.json`: per-hardpoint
    # transforms decoded out of the ship geometry in Data.p4k and joined to the
    # port by CIG's own `HardpointName`, exact string equality.
    # See docs/FINDING_the-coordinates-are-in-the-client-2026-08-27.md.
    #
    # MEASURED AGAINST WHAT IT REPLACES: the median existing marker sits 0.488
    # of the hull's longest half-extent from the real mount - about half a
    # hull-length - and on the Reclaimer the median is 1.090, further than the
    # hull's own half-length.
    #
    # SAME MATCH-OR-DIE RULE the other overlay uses. An entry naming a ship or
    # a port that is not here is a hard failure, because an overlay that
    # quietly matches nothing reports a fix it did not make.
    # SHIPS THE MARKER DATASET HAS NO RECORD FOR AT ALL.
    #
    # `hardpoints_fleet.json` decides which hulls get markers, and its single
    # writer is `place_fleet.py` - WHICH IS IN THIS REPOSITORY, at
    # data-layer/derived/holo-hardpoints/place_fleet.py, 32,861 bytes.
    #
    # THIS COMMENT SAID THE OPPOSITE UNTIL 2026-08-29, and it was load-bearing.
    # Four documents and one other build script repeated it, and it was the
    # stated reason the nineteen ships imported on 2026-08-27 were written off
    # as a generator nobody has. THAT REASONING IS RETIRED. Its three premises,
    # each re-measured on this machine today rather than repeated:
    #
    #   place_fleet.py is not here      FALSE. It is at the path above, and
    #                                   resolve_frame() at line 110 already
    #                                   solves the orientation problem the way
    #                                   this repo eventually settled on - by
    #                                   matching published proportions rather
    #                                   than assuming an axis - and refuses a
    #                                   hull whose proportions disagree with its
    #                                   own spec sheet.
    #   it needs numpy, not installed   FALSE. numpy 1.26.4 is in the venv.
    #                                   build_hardpoint_join.py:111 still says
    #                                   otherwise; that file has no owner in
    #                                   OWNERS.md, so it is REPORTED here rather
    #                                   than edited from this one.
    #   its input geometry is not here  TRUE, and it is the only premise left
    #                                   standing. /home/claude/fleet/geo was a
    #                                   cloud sandbox and is not on this machine.
    #
    # So the nineteen are blocked on INPUTS, not on a missing generator. Whether
    # they can be regenerated is an open question, not a settled no, and nothing
    # here has tried it.
    # See docs/ERRATUM_place-fleet-py-was-in-the-repo-all-along-2026-08-29.md.
    #
    # The nineteen are still absent from the file today, so they still show no
    # dots: a missing record rather than a marker bug.
    #
    # These records are ADDITIVE and come from CIG's own geometry rather than
    # from a name-derived guess - so they arrive better-placed than the ones
    # they join. A ship already in the dataset is NEVER overwritten here; the
    # merge below refuses that outright rather than preferring one source.
    _fleet_c = os.path.join(REPO, 'data-layer', 'derived',
                            'holo-hardpoints-align',
                            'fleet_records_client.json')
    if os.path.exists(_fleet_c):
        _added = 0
        for _k, _v in json.loads(rd(_fleet_c)).items():
            if _k in _fleet:
                sys.exit('client fleet record would overwrite an existing hull '
                         '(%s) - refusing. This file is additive only.' % _k)
            _fleet[_k] = _v
            _added += 1
        print('client marker records added for %d hull(s) the dataset had none for'
              % _added)

    _align_c = os.path.join(REPO, 'data-layer', 'derived',
                            'holo-hardpoints-align',
                            'alignment_overlay_client.json')
    _cl_moved, _cl_miss = 0, []
    if os.path.exists(_align_c):
        for _k, _ports in json.loads(rd(_align_c)).items():
            _rec_o = _fleet.get(_k)
            if _rec_o is None:
                _cl_miss.append(_k)
                continue
            _bp = {_h['port']: _h for _h in (_rec_o.get('hardpoints') or [])}
            for _pt, _pos in _ports.items():
                _h = _bp.get(_pt)
                if _h is None:
                    _cl_miss.append('%s / %s' % (_k, _pt))
                    continue
                _h['unit'] = _pos['unit']
                if 'pos_model' in _pos:
                    _h['pos_model'] = _pos['pos_model']
                _h['placed_from'] = 'client'
                _cl_moved += 1
        if _cl_miss:
            for _u in _cl_miss[:20]:
                print('  CLIENT OVERLAY names something that is not here: %s' % _u)
            sys.exit('%d client-overlay entr(ies) matched nothing. Refusing to '
                     'build.' % len(_cl_miss))
        print('client hardpoint overlay: %d port(s) moved onto CIG positions'
              % _cl_moved)
    else:
        print('client hardpoint overlay: not present, markers stay derived')
    # ---------------------------------------------------------------
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
    # -----------------------------------------------------------------
    # C1 - A GUN INSIDE A TURRET INHERITS THE TURRET'S POSITION.
    #
    # THE DEFECT. The placer works from ship_mounts.json, which is a flat list
    # of TOP-LEVEL ports. The ship page lists the ports a reader can actually
    # change, and on a turreted hull those are the CHILDREN. On the Aegis
    # Retaliator the placer produced twenty positions - five turret bases, four
    # countermeasure launchers, four racks, five target selectors, two regen
    # pools - and the page asked for `turret_left`, `turret_right` and
    # `hardpoint_class_2`. Four markers survived: the countermeasure launchers,
    # the only ports present on both sides. Sixteen positions were computed and
    # thrown away, and a visitor saw four dots on a torpedo bomber with five
    # manned turrets.
    #
    # THE ANCESTRY IS ALREADY IN THE PORT ID AND NOTHING HAD TO BE INFERRED.
    # A PortId is a PATH: `15.loadout.0.loadout.0` is the gun, inside the mount
    # `15.loadout.0`, inside the turret base `15`. Trimming one `.loadout.N`
    # walks up one level. No name matching, no guessing, and it stays inside
    # the L10 convention because what comes back is still a PortId - the
    # Polaris has thirty ports called MEC and a marker must select one port and
    # no other.
    #
    # THE POSITION IS INHERITED, THE ARRANGEMENT IS NOT A CLAIM. A child sits
    # at its nearest placed ancestor, offset so that siblings do not stack -
    # two guns in one turret at identical coordinates is one marker wearing two
    # labels, and the label solver would make one of them unselectable. Where
    # the port's own name carries a direction the offset follows it, because
    # `turret_left` and `turret_right` really are on opposite sides. Where it
    # does not, the offset is a deterministic ring and means nothing beyond
    # "not on top of its sibling". The radius halves at each level down, so a
    # gun sits at its own mount rather than wandering off it.
    #
    # NONE OF THIS MAKES THE POSITIONS REAL. The parent's position was derived
    # from the hull and the port's name; a child inheriting it is still an
    # estimate, and the page's provenance note must not say otherwise.
    _RING = (0.035, 0.018, 0.009)

    def _dirvec(nm):
        """A unit offset from the port's own name, or None if it has none."""
        nm = (nm or '').lower()
        if 'left' in nm:
            return (-1.0, 0.0)
        if 'right' in nm:
            return (1.0, 0.0)
        if 'top' in nm or 'upper' in nm:
            return (0.0, 1.0)
        if 'bottom' in nm or 'lower' in nm:
            return (0.0, -1.0)
        return None

    def _parent_pid(pid):
        i = str(pid).rfind('.loadout.')
        return str(pid)[:i] if i > 0 else None

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
            # Q9: WHERE THIS DOT CAME FROM, carried with the dot.
            #
            # `placed_from` is set to 'client' a few hundred lines up, on every
            # port the CIG overlay moved. It has always been known here and has
            # never survived into the emitted marker, so the page could not tell
            # a decoded mount from a name-derived estimate and had to hedge
            # about all of them - 1,693 mounts across 166 hulls included.
            _out.append([_cands[0]['p'], round(_u[0], 5), round(_u[1], 5),
                         round(_u[2], 5),
                         'cig' if _hp.get('placed_from') == 'client' else 'est'])
            _mark_prov['cig' if _hp.get('placed_from') == 'client'
                       else 'est'] += 1

        # C3 APPLIES TO THESE MARKERS TOO, and until 2026-08-27 it did not.
        #
        # The inheritance pass below refuses to stack a derived marker on an
        # existing one. The markers above it had no such rule, and six pairs
        # landed exactly on top of each other:
        #
        #   HoverQuad 9/10   Buccaneer 24/25   Railen 66/67 and 68/69
        #   Tyilui 30/31 and 32/33
        #
        # A marker directly underneath another cannot be clicked, so the second
        # port of each pair was unreachable by the picker.
        #
        # NOT A PIPELINE FAULT. Every pair is a left/right pair CIG ITSELF
        # places at one point, x exactly 0.0 - one physical rack or launcher
        # with two logical channels. Two independent sources agree: the client
        # overlay for the first four, hardpoint-placement for the Tyilui.
        #
        # THE LOWER PortId KEEPS CIG'S EXACT COORDINATE, and the upper one gets
        # NO MARKER AT ALL - the same answer this file already gives for an
        # ambiguous name, and the list still reaches every port.
        #
        # THE FIRST VERSION OF THIS DROPPED IT HERE AND LET THE INHERITANCE PASS
        # PUT IT BACK, nudged 0.006 into the first free spot. That kept both
        # ports clickable and looked like the better answer, and it was wrong
        # twice:
        #
        #   * It claims a position CIG does not give. The nudged dot says "this
        #     port is six centimetres that way" when the source says the two
        #     mounts are in one place. Every other marker on the page is CIG's
        #     own coordinate or an honestly-derived child of one.
        #   * `_verify_child_markers.py` caught it within the hour - "no hull
        #     changed without having a nested eligible port to inherit from"
        #     went red on the HoverQuad and the Pulse LX, because a re-placed
        #     TOP-LEVEL port is not an inherited child and the inheritance pass
        #     should not be the thing that puts it back.
        #
        # So the suppressed PortIds are recorded and the inheritance pass below
        # skips them.
        _keep_at, _suppressed = {}, set()
        for _row in _out:
            _xyz = (_row[1], _row[2], _row[3])
            _prev = _keep_at.get(_xyz)
            if _prev is None or _pid_sort(_row[0]) < _pid_sort(_prev[0]):
                _keep_at[_xyz] = _row
        if len(_keep_at) != len(_out):
            _kept_ids = {id(_r) for _r in _keep_at.values()}
            _dropped = [_r for _r in _out if id(_r) not in _kept_ids]
            _suppressed = {str(_r[0]) for _r in _dropped}
            _mark_coincident += len(_suppressed)
            # The provenance tally is incremented as rows are APPENDED, so the
            # rows removed here have to come back out of it. Caught by the
            # totals: 1699+452+4261 came to 6412 against 6400 markers, which is
            # exactly these twelve counted and then dropped.
            for _r in _dropped:
                _mark_prov[_r[4]] -= 1
            _out = [_r for _r in _out if id(_r) in _kept_ids]

        # ---- the inheritance pass -------------------------------------
        # EVERY slot is a possible ancestor, not just the eligible ones: a
        # TurretBase carries no marker of its own and is exactly the thing a
        # gun hangs from.
        _slot_by_pid = {str(s['p']): s for s in _rec['slots']}
        _kids = {}
        for _pid in _slot_by_pid:
            _par = _parent_pid(_pid)
            if _par is not None:
                _kids.setdefault(_par, []).append(_pid)
        for _v in _kids.values():
            _v.sort()

        # A hardpoint NAME that the placer positioned. A name that got two
        # different positions is refused rather than resolved to the first -
        # the same rule the direct pass uses.
        _pos_by_name, _dupe = {}, set()
        for _hp in _hull.get('hardpoints') or []:
            _u = _hp.get('unit')
            _nm = _hp.get('port') or ''
            if not (isinstance(_u, list) and len(_u) == 3) or not _nm:
                continue
            _key = (round(_u[0], 5), round(_u[1], 5), round(_u[2], 5))
            if _nm in _pos_by_name and _pos_by_name[_nm] != _key:
                _dupe.add(_nm)
            _pos_by_name[_nm] = _key
        for _nm in _dupe:
            _pos_by_name.pop(_nm, None)

        _resolved = {}

        def _resolve(pid, depth=0):
            """Where this port sits, or None. Memoised; cycle-safe by depth."""
            pid = str(pid)
            if pid in _resolved:
                return _resolved[pid]
            if depth > 8:
                return None
            _resolved[pid] = None          # guards a malformed path
            _sl = _slot_by_pid.get(pid)
            if _sl is None:
                return None
            _own = _pos_by_name.get(_LHP[_sl['h']])
            if _own is not None:
                _resolved[pid] = _own
                return _own
            _par = _parent_pid(pid)
            if _par is None:
                return None
            # THE ANCESTOR IS USUALLY NOT A SLOT, AND THAT IS THE WHOLE REASON
            # THE FIRST ATTEMPT PLACED NOTHING ON THE RETALIATOR.
            #
            # LOADOUT_SHIPS lists the ports a reader can act on. A TurretBase
            # is not one of them - the Retaliator's five bases, PortIds 15, 18,
            # 28, 94 and 96, have no slot at all - so walking the PortId path
            # up to `15` found nothing and every child resolved to None. The
            # markers stayed at four and the counter still said 2052 inherited
            # fleet-wide, because plenty of OTHER hulls do carry their parent
            # as a slot. A partial mechanism reporting a big number is exactly
            # the shape of thing that gets mistaken for working.
            #
            # But the parent's NAME is on the child already: `hp` is the
            # parent's hardpoint-name index, so `turret_left`'s parent reads
            # `hardpoint_turret_backbottom` - which the placer DID position.
            # So the walk tries the parent slot first, and falls back to the
            # named parent when there is no slot to walk to.
            _base = None
            if _par in _slot_by_pid:
                _base = _resolve(_par, depth + 1)
            if _base is None and _sl.get('hp') is not None:
                _base = _pos_by_name.get(_LHP[_sl['hp']])
            if _base is None:
                return None
            _sibs = _kids.get(_par) or [pid]
            _i = _sibs.index(pid) if pid in _sibs else 0
            _r = _RING[min(len(_RING) - 1, str(pid).count('.loadout.') - 1)]
            _d = _dirvec(_LHP[_sl['h']])
            if _d is None:
                _ang = 2.0 * math.pi * _i / max(1, len(_sibs))
                _d = (math.cos(_ang), math.sin(_ang))
            _p = (_base[0] + _r * _d[0], _base[1] + _r * _d[1], _base[2])
            _resolved[pid] = _p
            return _p

        # CC_NO_INHERIT=1 IS THE BEFORE STATE, so a before/after can be
        # MEASURED rather than described. place_fleet.py carries the same
        # switch for the same reason. It is off unless explicitly set, and the
        # build prints which state it ran in.
        if _NO_INHERIT:
            if _out:
                _marks[_cls] = _out
            continue

        _have = {str(r[0]) for r in _out}
        _taken = {(round(r[1], 5), round(r[2], 5), round(r[3], 5))
                  for r in _out}
        for _sl in sorted(_rec['slots'], key=lambda s: str(s['p'])):
            if (_LT.get(_sl['t']) or {}).get('t') not in _WEAPONY:
                continue
            _pid = str(_sl['p'])
            if _pid in _have:
                continue
            # Suppressed above for sharing CIG's one position with a lower
            # PortId. Re-placing it here would put a derived offset where the
            # source gives no distinct location.
            if _pid in _suppressed:
                continue
            _p = _resolve(_pid)
            if _p is None:
                continue
            # C3: NO TWO MARKERS ON A HULL MAY SHARE COORDINATES TO 5dp.
            # Two siblings whose names give the same direction would otherwise
            # land on each other. Nudged deterministically until unique, so the
            # guarantee is produced rather than hoped for.
            _x, _y, _z = round(_p[0], 5), round(_p[1], 5), round(_p[2], 5)
            _n = 0
            while (_x, _y, _z) in _taken and _n < 64:
                _n += 1
                _a = 2.0 * math.pi * _n / 8.0
                _x = round(_p[0] + 0.006 * _n * math.cos(_a), 5)
                _y = round(_p[1] + 0.006 * _n * math.sin(_a), 5)
            if (_x, _y, _z) in _taken:
                _mark_stacked += 1
                continue
            _taken.add((_x, _y, _z))
            _have.add(_pid)
            # 'anc' EVEN WHEN THE ANCESTOR WAS CIG-PLACED. This dot's position
            # is the ancestor's plus a ring offset, so it is not a coordinate
            # CIG published for THIS port and must not claim to be. What it is
            # honestly is "taken from the mount it sits on", which is what the
            # page can now say about it.
            _out.append([_sl['p'], _x, _y, _z, 'anc'])
            _mark_prov['anc'] += 1
            _mark_inherited += 1

        if _out:
            _marks[_cls] = _out
_mark_js = (
    '/* GENERATED by testing/_src/build_deploy.py - do not hand edit.\n'
    '   Hull markers for the ship page. Each entry is [PortId, x, y, z, from]\n'
    '   where x/y/z are NORMALISED against the hull\'s longest half-extent - the\n'
    '   same convention the holo viewer uses, because there is no fixed\n'
    '   multiplier that could be right across a fleet spanning 10,000x in model\n'
    '   units per metre.\n'
    '\n'
    '   `from` IS THE PROVENANCE OF THAT ONE DOT, added 2026-08-27 (Q9). Before\n'
    '   it, the page knew a fleet-wide story and nothing per-mount, so its note\n'
    '   had to say it "cannot yet tell you which of the two you are looking at\n'
    '   on this particular ship" about every dot on every hull:\n'
    '\n'
    '       cig   CIG published a transform for this port and it is used here,\n'
    '             unchanged. Not a guess and not an estimate.\n'
    '       est   derived - from the mount name and the hull box - because no\n'
    '             decoded transform exists for this port.\n'
    '       anc   taken from the mount this port sits on, plus a ring offset so\n'
    '             siblings do not stack. NOT CIG\'s coordinate for this port\n'
    '             even when the ancestor was cig, which is why it is its own\n'
    '             value rather than inheriting the ancestor\'s.\n'
    '\n'
    '   READ IT BY INDEX. Everything that consumes this file uses m[0]..m[3];\n'
    '   the fifth element is additive and older readers are unaffected.\n'
    '\n'
    '   BOUND TO PortId, NOT TO A HARDPOINT NAME. A name is not unique within a\n'
    '   ship - the RSI Polaris has thirty ports called MEC - and L10 requires a\n'
    '   marker to select one port and no other. Where a name resolved to more\n'
    '   than one weapon port, NO MARKER WAS EMITTED: picking one of two would\n'
    '   be a coin toss dressed as data, and the list still reaches both.\n'
    '\n'
    '   AND WHERE TWO PORTS SHARE ONE POSITION, only the lower PortId carries\n'
    '   a marker. CIG places some left/right pairs at exactly one point - one\n'
    '   physical rack, two logical channels - and the upper one would sit under\n'
    '   the lower where nobody could click it. It gets NO marker rather than a\n'
    '   nudged one: an offset dot would claim a position the source does not\n'
    '   give. Same answer as an ambiguous name, and the list still reaches it.\n'
    '\n'
    '   %d hulls, %d markers. %d points were ambiguous and dropped, %d shared a\n'
    '   position with a lower PortId and gave it up. */\n'
    'const LOADOUT_MARK=%s;\n'
    % (len(_marks), sum(len(v) for v in _marks.values()), _mark_amb,
       _mark_coincident,
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
print('  of those, %d were INHERITED from a placed ancestor (C1); %d could not '
      'be separated from a sibling and were refused'
      % (_mark_inherited, _mark_stacked))
print('  %d marker(s) gave up a position shared with a lower PortId - CIG places '
      'some left/right pairs at one point' % _mark_coincident)
print('  provenance: %d from CIG geometry, %d name-derived, %d taken from a '
      'placed ancestor'
      % (_mark_prov['cig'], _mark_prov['est'], _mark_prov['anc']))

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

# THE CRAFTING DATA, BROUGHT INTO _src SO PAGES CAN COPY IT.
#
# `build_crafting_demand.py` writes craft_data.gen.js into
# data-layer/derived/crafting-demand/, and PAGES copies from _src - so without
# this step the file exists, the page's craftLine() returns nothing, and the
# feature is dead with no error anywhere. C1 named the missing piece as "one
# line in Code's deploy_pages.py"; it was three, and the other two are here and
# in the page's own <script src> block.
#
# FAILS CLOSED ON THE PAIRING, not on the file. If the page ASKS for
# craft_data.gen.js and the generator has not produced it, the page would ship
# with a script tag pointing at nothing - a 404 in the console and a silently
# absent feature. That is refused. A page that does not ask for it needs
# nothing, and a generator output nobody asks for is reported rather than
# copied, so a stale 88 KB does not ride along unnoticed.
_craft_src = os.path.join(REPO, 'data-layer', 'derived', 'crafting-demand',
                          'craft_data.gen.js')
_craft_asked = 'craft_data.gen.js' in rd(os.path.join(SRC, 'loadout.src.html'))
if _craft_asked and not os.path.exists(_craft_src):
    sys.exit('loadout.src.html loads craft_data.gen.js and '
             'data-layer/derived/crafting-demand/craft_data.gen.js does not '
             'exist. Run build_crafting_demand.py, or take the script tag out. '
             'Refusing to ship a page that asks for a file nobody wrote.')
if _craft_asked:
    shutil.copyfile(_craft_src, os.path.join(SRC, 'craft_data.gen.js'))
    print('crafting data: copied into _src (%d bytes)'
          % os.path.getsize(_craft_src))
elif os.path.exists(_craft_src):
    print('crafting data: generated but NOT referenced by any page - not copied')

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
                 encoding='utf-8', newline='\n').write(
                     _for_deploy(_out_name, _txt))
            _copied.append(_out_name)
            continue
        _txt = rd(_s) if _src_name.endswith('.html') else None
        if _txt is not None and CC_DISC_MARKER in _txt:
            if _disc_css is None:
                sys.exit("%s asks for the shared disclosure CSS and "
                         "testing/_src/_disc.css is missing. The page would "
                         "ship its bars unstyled and the build would have said "
                         "nothing. Refusing." % _src_name)
            _txt = _txt.replace(CC_DISC_MARKER, _disc_css)
            _disc_used.append(_out_name)
        if _txt is not None and CC_VENDOR_MARKER in _txt:
            _txt = _txt.replace(CC_VENDOR_MARKER, _vendor_block)
            if 'cdn.jsdelivr.net' in _txt or 'https://unpkg' in _txt:
                sys.exit("%s still references a CDN after vendor inlining. "
                         "The built page would need the network. Nothing shipped."
                         % _src_name)
            _txt = _with_attribution(_txt, _out_name,
                                     _out_name in _SHIP_CONTENT_PAGES)
            open(_dst, 'w', encoding='utf-8', newline='').write(
                _for_deploy(_out_name, _txt))
            _vendored.append(_out_name)
        elif _txt is not None:
            _txt = _with_attribution(_txt, _out_name,
                                     _out_name in _SHIP_CONTENT_PAGES)
            open(_dst, 'w', encoding='utf-8', newline='').write(
                _for_deploy(_out_name, _txt))
        else:
            # EVEN THE UNTOUCHED FILES. A page needing no substitution
            # was copied byte for byte, which would have been the one
            # route comments still shipped by.
            open(_dst, 'w', encoding='utf-8', newline='').write(
                _for_deploy(_out_name, rd(_s)))
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
if _disc_css is not None and not _disc_used:
    sys.exit("testing/_src/_disc.css exists and NO page asked for it. Either a "
             "page lost its %s marker, or the shared implementation has been "
             "abandoned while pages grow their own copies again - which is the "
             "drift the order exists to prevent. Refusing rather than shipping "
             "it quietly." % CC_DISC_MARKER)
print('disclosure CSS: shared from _disc.css into', ', '.join(_disc_used)
      if _disc_used else 'nothing')
print('pages copied:', ', '.join(_copied) if _copied else 'none')
print('written:', len(out)/1048576, 'MB')

# ---------------------------------------------------------------------------
# A4. A WITHDRAWN ASSET THAT HAS COME BACK IS TAKEN OUT AGAIN, LOUDLY.
#
# _deploy/models/ is not regenerated by this build - it is a directory on disk
# that a sync step populates. So a model pulled at CIG's request can reappear
# there without anyone doing anything wrong, and the site would quietly start
# serving it again.
#
# This FAILS SAFE TOWARDS REMOVAL rather than failing the build: refusing to
# build during a takedown is the wrong behaviour at the worst moment. The file
# is moved back out and the fact is printed where it cannot be missed.
# ---------------------------------------------------------------------------
_back = []
for _a in _cig.withdrawn():
    for _f in _cig.deploy_paths(_a, OUT):
        if os.path.exists(_f):
            _attic = os.path.join(REPO, '_to_delete', 'takedown_reappeared')
            _d = os.path.join(_attic, os.path.relpath(_f, OUT))
            os.makedirs(os.path.dirname(_d), exist_ok=True)
            import shutil as _sh2
            _sh2.move(_f, _d)
            _back.append(os.path.relpath(_f, OUT))
if _back:
    print('')
    print('*** A WITHDRAWN ASSET REAPPEARED IN THE BUILD AND WAS REMOVED '
          'AGAIN ***')
    for _r in _back:
        print('    %s' % _r)
    print('    It was stamped `removed` in the register, so something put it '
          'back.')
    print('    Moved to _to_delete/takedown_reappeared/. NOT published.')
    print('')

# ---------------------------------------------------------------------------
# A2 - THE "MADE BY THE COMMUNITY" MARK.
#
# CIG require their mark in the corner of any image built from their assets, at
# no less than 50% opacity and a legible size. This refuses to finish a build in
# which such an image is missing it.
#
# THE REFUSAL IS THE POINT, not the applier. An applier that silently stops
# running produces an unmarked site and no error; "the mark is applied" then
# passes on a build that applies nothing. So this reads the PIXELS of what was
# actually built - see scripts/community_mark.py for how, and for the first
# version of that detection which was measured and found WRONG.
#
# WHAT IS IN SCOPE: every asset the register (A4) records as CIG-sourced with
# kind "image". That is currently zero, so the guard is armed and idle, exactly
# like A3's contact requirement - the first such image registered turns it on
# with nobody having to remember to.
#
# WHAT IS DELIBERATELY NOT IN SCOPE, and reported instead: the 241 ship
# thumbnails already shipping in images/. Their provenance is recorded in
# docs/workorder-image-provenance-and-renders.md, which establishes that the
# upstream pack is governed by terms naming "Made by the Community", and
# equally that it is NOT established whether any individual image is a CIG
# asset, a screenshot or a render. Marking all 241 is a bulk mutation of the
# site's whole visual surface (rule 5) on a Fan-Kit compliance question (rule
# 8: report it, do not fix it), and Part 2 of that same work order plans to
# replace every one of them with our own renders. Reported, not silently done.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import community_mark as _mark

_img_assets = [a for a in _cig.tagged() if a.get('kind') == 'image']
if _img_assets:
    _unmarked, _unbuilt = [], []
    for _a in _img_assets:
        _variant = _a.get('mark_variant', 'white')
        for _f in _cig.deploy_paths(_a, OUT):
            if not os.path.exists(_f):
                _unbuilt.append(_a['file'])
            elif not _mark.has_mark(_f, _variant):
                _unmarked.append('%s (score %.3f, needs >= %.2f)' % (
                    _a['file'], _mark.mark_score(_f, _variant),
                    _mark.MARK_THRESHOLD))
    if _unmarked:
        sys.exit(
            "MADE BY THE COMMUNITY MARK MISSING from %d built image(s):\n"
            "    %s\n"
            "\n"
            "CIG require their mark in the corner of any image built from their\n"
            "assets, at no less than 50%% opacity and a legible size. These are\n"
            "registered as CIG-sourced and do not carry it.\n"
            "\n"
            "This was measured from the built pixels, not read from a flag - so\n"
            "it is also what fires if the compositing step stops running.\n"
            "\n"
            "Apply it with scripts/community_mark.py apply_mark(). Nothing was\n"
            "uploaded." % (len(_unmarked), '\n    '.join(_unmarked)))
    if _unbuilt:
        sys.exit(
            "REGISTERED CIG IMAGE NOT IN THE BUILD: %s\n"
            "It is registered as CIG-sourced but is not where the takedown would\n"
            "look for it. Refusing to ship a register that does not match the\n"
            "site, because that register is the off switch." % ', '.join(_unbuilt))
    print('community mark: %d CIG-sourced image(s), all carry it'
          % len(_img_assets))
else:
    print('community mark: 0 CIG-sourced images registered - guard armed, '
          'nothing to mark')

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

# ---------------------------------------------------------------------------
# Q31: THE STRIP IS PROVEN ON THE WAY OUT, NOT ASSUMED.
#
# checks/_verify_no_agent_traces.py asks whether the words are gone. It would
# be perfectly happy with a strip that also deleted a line of code, because a
# broken page contains no traces either. THIS asks the other question, of the
# thing that lands in _deploy, and it asks node rather than the scanner.
#
# A page that loses a script and still renders is the exact failure this
# project keeps finding, and it would ship looking fine.
# ---------------------------------------------------------------------------
_bad_js = []
for _n in sorted(os.listdir(OUT)):
    _p = os.path.join(OUT, _n)
    if not os.path.isfile(_p):
        continue
    if _n.endswith('.js'):
        _r = _sp.run([_node, '--check', _p], capture_output=True, text=True,
                     encoding='utf-8', errors='replace')
        if _r.returncode != 0:
            _bad_js.append('%s: %s' % (_n, (_r.stderr or '').strip().splitlines()[:1]))
    elif _n.endswith('.html'):
        try:
            _check_inline_js(_p, require_any=False)
        except SystemExit as _e:
            _bad_js.append(str(_e))
if _bad_js:
    sys.exit("BUILD FAILED: the comment strip left JavaScript that does not "
             "parse. Nothing has been uploaded." + "\n  " +
             "\n  ".join(_bad_js))
print('comment strip: %d comment(s) removed on the way into _deploy; '
      'every deployed .js and inline script still parses' % _stripped_total)


if _deploy_guard(OUT, allowed_files=_allowed):
    sys.exit("BUILD FAILED: refusing to leave _deploy in a state that would "
             "publish unexpected files. Nothing has been uploaded.")

# THE LAST STATEMENT IN THE FILE, DELIBERATELY. Everything above it - every
# gate, every generator, the deploy guard - has to have passed for the build to
# be recorded as ok. Anything that stops the script earlier leaves a receipt
# saying so, and the deploy refuses on it.
_BUILD_DONE['ok'] = True
_write_receipt('ok', 0, 'build completed')
print('build receipt: ok  (%s)' % os.path.relpath(RECEIPT, REPO))
