# PROMPT FOR CODE — land the round-tripping exporter and its two test harnesses. Nothing else.

    from    C1, 2026-08-09
    for     Code
    basis   claude/WORKORDER_swap-the-exporter-2026-08-09.md (C3, work order)
            claude/FINDING_exporter-round-trip-passes-2026-08-09.md (C3, evidence)

    C3's order is right and none of its reasoning is reopened here: the module is an
    orphan (nothing calls testing/_src/sc_export.js except the test being deleted), so
    this is genuinely risk-free to land on its own, and it does NOT put an export button
    anywhere. Do not describe this as "keybind export is done."

    Everything below §1 is C1 grounding C3's order against the actual repo before
    handing it to you — C3 said plainly it was working from a partial copy ("Neither
    file is in the copy of the repo I can see"). Four things needed correcting or adding.
    Read this section before the task list; it changes what you'll actually find on disk.

---

## 1. Four corrections to the order, checked against the real repo just now

**The three input files are not in `inbox/`.** They were dropped there, but this repo's
Go watcher only leaves two protected folders inside `inbox/` untouched and files
everything else — a `.js` file isn't a doc it knows how to route, so it landed in
`_needs_review/`, not `inbox/`. As of right now, `_needs_review/` contains:

    _needs_review/sc_export2.js
    _needs_review/roundtrip.js
    _needs_review/mutate.js
    _needs_review/real_export.xml     (test1CR — this IS the §5 fixture)
    _needs_review/real_export2.xml    (test3cr — this IS the §5 fixture)

Both fixtures C3's order asks you to add are already sitting right there. Read all five
from `_needs_review/`, not `inbox/`.

**`roundtrip.js` and `mutate.js` hard-code C3's own Cowork sandbox paths and will not run
anywhere else as-is.** This is bigger than "update the two path constants" in §5 of the
order — it's five separate literals across the two files, all pointing at filesystem
locations that don't exist on this machine:

    roundtrip.js:22   const REPO = '/mnt/user-data/uploads/citizen-compass/data-layer/processed/';
    roundtrip.js:93   roundtrip('/home/claude/work/real_export.xml')
    roundtrip.js:94   roundtrip('/home/claude/work/real_export2.xml')
    roundtrip.js:151  fs.readFileSync('/home/claude/work/'+file, 'utf8')   (byte-compare loop, same two files again)
    mutate.js:13      const SRC = '/home/claude/work/kb/sc_export2.js';
    mutate.js:97      cp.spawnSync('node', ['/home/claude/work/kb/roundtrip.js'], ...)

Fix all six (five distinct literals, one repeated) to be relative to `__dirname` so they
work regardless of who runs them or from where — see the exact rewrite in §3 below.

**One more file reference needs to change and the order doesn't mention it:**
`roundtrip.js:22` also does `require('./sc_export2.js')`. The order has you writing the
new exporter's contents into `testing/_src/sc_export.js` — there is no `sc_export2.js` in
the repo, so that require needs to become `require('./sc_export.js')`. (The local
variable name `SCX2` inside `roundtrip.js` — used 21 more times after the require line —
does not need to change; it's just a local binding, not the export name. Leave it.)

**"Put both test harnesses in CI" doesn't mean GitHub Actions — this repo doesn't have
any.** Checked: no `.github/workflows` directory exists anywhere in the repo. What this
project actually calls its check pipeline is `checks/` + `run_checks.py`
(`--group file` / `db` / `network` / `all`), the pluggable Finding-based framework
documented in `docs/ARCHITECTURE_DECISIONS.md` §4 and run on a schedule via
`run_checks_scheduled.ps1`. That's almost certainly what C3 meant by "CI" — wire
`roundtrip.js` and `mutate.js` into that system, not into a GitHub Actions file that
doesn't exist. See §4 for the specific ask; the exact shape (new file in `checks/` vs. a
function added to an existing one) is your call, you own that framework.

---

## 2. The change (C3's §4, unchanged)

| action | path |
|---|---|
| replace | `testing/_src/sc_export.js` ← contents of `_needs_review/sc_export2.js` |
| delete | `testing/_src/test_sc_export.js` |
| add | `testing/_src/roundtrip.js` ← `_needs_review/roundtrip.js`, paths fixed (§3) |
| add | `testing/_src/mutate.js` ← `_needs_review/mutate.js`, paths fixed (§3) |
| add | `testing/_src/fixtures/real_export.xml` ← `_needs_review/real_export.xml` |
| add | `testing/_src/fixtures/real_export2.xml` ← `_needs_review/real_export2.xml` |

**Keep the exported name `SCX`.** `_needs_review/sc_export2.js` declares `SCX2`. Rename
the variable and the `module.exports` line to `SCX` on the way into `sc_export.js` —
that's the only edit to make to the file's body. Everything else in it is under test;
changing anything else will show up as a failure, and if the SCX2→SCX rename itself
breaks a test, the rename is wrong, not the file (it passed 32 checks and 20 mutations as
written).

`test_sc_export.js` is deleted, not kept: it asserts the old, wrong behaviour (a joystick
build returning `verified:false` with no `<options>` line). `roundtrip.js` supersedes it
— covers what it covered plus 30 things it didn't.

`data-layer/processed/keybinds_site.json` and `actionmap_categories.json` already exist
in the repo at the paths `roundtrip.js` expects (confirmed) — do not copy or duplicate
them, only fix the path used to reach them (§3).

---

## 3. The path fixes, spelled out exactly

`testing/_src/roundtrip.js` — add `const path = require('path');` if not already
required, then:

```js
// was: const REPO = '/mnt/user-data/uploads/citizen-compass/data-layer/processed/';
const REPO = path.join(__dirname, '..', '..', 'data-layer', 'processed') + path.sep;

// was: require('./sc_export2.js')
const SCX2 = require('./sc_export.js');

// was: roundtrip('/home/claude/work/real_export.xml')
// was: roundtrip('/home/claude/work/real_export2.xml')
const r1 = roundtrip(path.join(__dirname, 'fixtures', 'real_export.xml'));
const r2 = roundtrip(path.join(__dirname, 'fixtures', 'real_export2.xml'));
```

And the byte-compare loop around line 142-152 reads the same two files a second time by
the same absolute paths — change that read to the same `path.join(__dirname, 'fixtures',
file)` construction, keyed off whichever of `real_export.xml` / `real_export2.xml` the
loop is on.

`testing/_src/mutate.js` — add `const path = require('path');`, then:

```js
// was: const SRC = '/home/claude/work/kb/sc_export2.js';
const SRC = path.join(__dirname, 'sc_export.js');

// was: cp.spawnSync('node', ['/home/claude/work/kb/roundtrip.js'], {encoding:'utf8'})
const r = cp.spawnSync('node', [path.join(__dirname, 'roundtrip.js')], {encoding: 'utf8'});
```

Use `path.join`, not string concatenation with a literal `/` — this runs on Windows.

---

## 4. CI — wire into `checks/`, not GitHub Actions

Both harnesses already exit non-zero on failure and print a readable line per check, so
they're ready to shell out to. Add a checker (new file, e.g. `checks/node_checks.py`, or
a function in an existing file — your call, you own the framework's conventions) that:

- Runs `node testing/_src/roundtrip.js` from the repo root, reports a `Finding` (severity
  matching how this framework reports a hard failure) if it exits non-zero or its stdout
  doesn't contain `ALL CHECKS PASSED`.
- Runs `node testing/_src/mutate.js` the same way, and specifically checks the reported
  count is **`19/20`** with `M18` named as the survivor (see §5) — not just exit-code
  zero, since a mutation suite can exit 0 while reporting a different pass count than the
  one that's actually correct here.
- Registers into whichever group `run_checks.py --group file` already covers (stdlib +
  git only, no DB/network — matches what these two need: just `node` and one npm
  package).

**The dependency, `@xmldom/xmldom`, needs somewhere to live.** This repo has two existing
patterns for JS dependencies and neither is an exact match: `testing/_src/vendor/`
vendors what actually ships in `_deploy/` (three.js, committed, byte-reproducible);
`testing/_tools/node_modules` uses plain `npm install` for build-only tooling that never
ships (untracked — confirmed 0 files under it are in git). `@xmldom/xmldom` is
test-only, like `_tools`, not shipped, like neither. Simplest: a small
`testing/_src/package.json` declaring just that one dependency, `npm install` run inside
`testing/_src/`. If you'd rather keep it next to the existing `_tools/node_modules`
precedent instead, that's a reasonable call too — your framework, your convention to
extend consistently, not a call I'm making for you.

**Whichever you pick, add `node_modules/` to `.gitignore` if it isn't already covered.**
Checked: the root `.gitignore` has no `node_modules` rule at all right now. `testing/_tools/node_modules`
being untracked today looks like it's simply never been `git add`ed rather than actually
ignored — worth closing that gap while you're in here, since this repo's own standing
caution is "do not `git add -A` until line endings are settled," and an untracked
`node_modules` sitting around is exactly the kind of thing that caution exists to catch.

---

## 5. Expect `19/20`, not `20/20` — do not "fix" the survivor

`M18` (`sort actions case-insensitively`) will survive `mutate.js`. That's correct,
not a gap: neither real fixture file contains a pair of action names that sorts
differently under ASCII versus case-insensitive ordering, so the evidence genuinely
cannot decide it, and `roundtrip.js` asserts that ambiguity deliberately — so a future
export that *does* contain a distinguishing pair fails loudly instead of the sort being
silently wrong for years. **If you land at 20/20, something is wrong with the check, not
right with the code.** Put the expected count (`19/20`, `M18` survivor) in whatever label
the checker reports, so a future regression that changes the count is visible by name.

---

## 6. What the API now needs from a caller — documentation only, nothing calls this yet

Recorded for whoever writes the builder-UI order next (not this order, not yet — see §8):

    build(bindings, opts)
      opts.mapOrder    REQUIRED for correct output — the game's actionmap order,
                       taken as first-seen order in keybinds_site.json
      opts.categories  the actionmap_categories.json object
      opts.devices     verbatim <options> lines, when round-tripping an imported profile
      opts.joysticks   [{instance, vid, pid, name}], when building from live gamepads

    parse(xmlText, DOMParserImpl)   reads a real file: every rebind, the unbinds,
                                    activationMode, and the device declarations

Also public: `reject`, `safeName`, `famOf`, `isUnbind`, `unbindFor`, `duplicates`,
`guidFromVidPid`, `parseGamepadId`, `productString`.

**`verified` is hard-coded `false` and must stay false.** No file this tool has generated
has ever been loaded by Star Citizen. Reproducing two files the game wrote proves the
format is understood; it does not prove the game will accept a generated one. If a future
change flips that flag without an in-game load behind it, that's a defect.

---

## 7. Acceptance — what must be true before this is done

1. `node testing/_src/roundtrip.js` (run from the repo root, after the path fixes in §3)
   prints **ALL CHECKS PASSED** and exits 0.
2. Inside it, both of these pass by name, in this order:
   - `real_export.xml: byte-for-byte identical to what the game wrote`
   - `real_export2.xml: shuffled input still reproduces the game's file byte for byte`
3. `node testing/_src/mutate.js` reports **19/20** with `M18` as the only survivor.
4. `grep -rn "test_sc_export" . --exclude-dir=node_modules --exclude-dir=.git` returns
   nothing.
5. Both harnesses run clean via whatever you wired into `checks/` — i.e.
   `python run_checks.py --group file` shows them, not just the raw `node` invocations.
6. `testing/_deploy/` is unchanged. **This order does not deploy.** If anything under
   `_deploy/` moved, something was done that wasn't asked for — check with
   `git --no-optional-locks status --short testing/_deploy/`.
7. `_needs_review/` no longer holds the five files this order consumed (they've been
   copied into `testing/_src/` in their final form) — leave the original copies in
   `_needs_review/` alone rather than deleting them; that folder is Sleven's to clear,
   same as every other item already sitting in it.

Point 6 is the one to watch hardest. The temptation to "while I'm in here" wire the
exporter into the actual keybind page is exactly what §8 says not to do yet.

---

## 8. What NOT to do

- Do not touch `device_engine.js`, `keybinds.html`, `keybinds.src.html`, `kb_modes.gen.js`,
  or any build script (`build_deploy.py`, `inject_engine.py`, etc.).
- Do not run the deploy script.
- Do not edit the body of `sc_export2.js`'s contents beyond the `SCX2` → `SCX` rename.
- Do not raise `verified` to true.
- Do not build the keybind-builder UI. It's out of scope on purpose — it's new structure
  against the build system (`device_engine.js` is the single writer of the device panel;
  patching only the source layer can silently do nothing), and it needs its own order
  after `build_deploy.py`/`inject_engine.py` are read properly for that specific job.
- Do not touch the 3D viewer / model-serving question. Blocked on a decision that's
  Sleven's, not on code.
- Do not `git add -A`. This repo has standing CRLF/LF churn on ~50 tracked files;
  stage only what this order actually touches.
- Nothing commits or pushes without Sleven's explicit go-ahead.

---

## 9. Still outstanding after this lands — say so, don't imply otherwise

- **Nobody has loaded a generated file in Star Citizen.** The only thing that actually
  settles whether any of this works, and it isn't this order's job to do it.
- The builder UI order is unwritten and is the larger job.
- The stuck device-tab bug needs an F12 console reading from a machine with real sticks;
  it doesn't reproduce headless.
- One machine, one vendor's sticks tested. Another vendor's `Product` string could be
  shaped differently and nothing here would catch it.

---

## Commands

```
cd testing/_src
npm install @xmldom/xmldom
```

```
node testing/_src/roundtrip.js
```

```
node testing/_src/mutate.js
```

```
grep -rn "test_sc_export" . --exclude-dir=node_modules --exclude-dir=.git
```

```
git --no-optional-locks status --short testing/_deploy/
```

```
python run_checks.py --group file
```
