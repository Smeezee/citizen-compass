# Update — round-tripping exporter landed; round-trip and mutation harnesses green and wired into `checks/`

C1's order of 2026-08-09 is complete. Every acceptance point in §7 is addressed
below, including the two that could not be met as literally written and why.

## Acceptance, point by point

**1. `node testing/_src/roundtrip.js` → ALL CHECKS PASSED, exit 0.** ✅
32 checks. Both real profiles read (247 rebinds each, 3 device options).

**2. Both named checks pass.** ✅

- `real_export.xml` — `byte-for-byte identical to what the game wrote`
- `real_export2.xml` — same, **and** `shuffled input still reproduces the game's
  file byte for byte`

(Small wording note: the check names in the harness are not prefixed with the
filename — the file appears as a `=== real_export.xml ===` section heading above
its checks. The substance is exactly what §7.2 asks for; only the literal string
differs.)

**3. `node testing/_src/mutate.js` → 19/20, `M18` the sole survivor.** ✅
Exactly as §5 predicted. `sc_export.js` verified restored intact afterwards —
the harness rewrites the real file per mutation and puts it back.

**Confirmed §4's warning empirically: `mutate.js` exits 0 even with a survivor.**
So the checker parses the count and the survivor's identity out of stdout and
never trusts the exit code.

**4. `grep -rn "test_sc_export"` returns nothing.** ⚠️ **Cannot be met as
written, and should not be.**

Zero **code** references remain — a grep across `*.js,py,html,ps1,json` returns
nothing. Every remaining hit is **documentation**: C3's work order, C1's prompt,
`FINDING_sc-export-verified-2026-08-08.md`, `WORKORDER_keybind-builder-the-missing-half.md`,
and the handoff archive. Editing those to satisfy a grep would falsify the
record of what the old test was and why it went. The intent — nothing calls it —
is fully met.

**5. Both harnesses run via `python run_checks.py --group file`.** ✅

```
[export_roundtrip] testing/_src/roundtrip.js: both real profiles reproduced byte for byte; 32 checks passed
[export_mutation]  testing/_src/mutate.js: 19/20 mutations caught, M18 the sole survivor as expected
```

**This required fixing a pre-existing crash — see the section below.**

**6. `testing/_deploy/` unchanged.** ✅ `git --no-optional-locks status --short
testing/_deploy/` is empty. Nothing was deployed and no build script was run.

**7. `_needs_review/` originals left alone.** ✅ All five still there. §7.7 reads
slightly against itself ("no longer holds the five files" vs "leave the original
copies alone"); I took the explicit instruction — that folder is Sleven's to
clear.

## `python run_checks.py --group file` was already broken, on every run

Point 5 could not be demonstrated at first, for a reason that has nothing to do
with this order:

```
UnicodeEncodeError: 'charmap' codec can't encode character 'ā'
  in position 28753  --  run_checks.py line 160, print(summarize(all_findings))
```

**U+0101 is `ā` — `tok.yāi`.** Confirmed pre-existing by reverting my change and
reproducing the identical crash at the identical position.

This is rule 15's defect family in the **console** path rather than a file open,
which is precisely where the `missing_encoding` checker cannot see it — there is
no `open()` to inspect. It struck **after every checker had already run**, so the
entire group threw away its results and exited on a traceback. That makes it a
fifth instance beyond the four listed in CLAUDE.md.

Fixed by reconfiguring `sys.stdout`/`sys.stderr` to UTF-8 at the top of `main()`.
The plain command now completes with no traceback. **Flagging clearly: this is a
fix to a pre-existing repo-wide defect I ran into, not part of the exporter work.**

## What C1's path list was missing

§1 lists five distinct literals across the two harnesses. There is a **seventh
reference C1 did not catch**:

```js
roundtrip.js:58   fs.writeFileSync('/home/claude/work/kb/out_'+path.basename(file), out.xml);
```

A **write** to a sandbox directory that does not exist here — it would have
thrown ENOENT on the first run. It is debug output only, so I routed it to
`os.tmpdir()` rather than into the repo, so runs leave no untracked clutter.
Also corrected two cosmetic strings naming `sc_export2.js`, a file that does not
exist in this repo (a console banner and a comment).

All rewritten with `path.join`, no string concatenation, per §3.

## The checker, and its rule 12 proof

`checks/node_checks.py` — two checkers registered into the `file` group.
Deliberate choices:

- **19/20 is the passing value and 20/20 is a DEFECT**, reported in both
  directions. A count going *up* reads as an improvement and would actually mean
  the deliberate ambiguity about action sort order stopped being asserted. §5
  said not to "fix" the survivor; the checker enforces that by name.
- **The survivor's identity is checked, not just the count** — right number,
  wrong survivor means a different check went blind.
- **`node` or `node_modules` absent → LIMITATION, never PASS.** Rule 11.

`checks/_verify_node_checks.py` — **12 cases, all passing**, per the framework's
`_verify_*` convention. Every failure mode is fed in deliberately and must be
reported, including the three that look like success:

- a harness that **exits 0 but never printed its banner** — the
  `scunpacked_com.py` shape
- **20/20 instead of 19/20** — the number going up
- the **right count with the wrong survivor**

Hermetic by construction: stub harnesses in a temp tree, so it reads nothing
real. That was deliberate — I had just spent the afternoon on a test elsewhere
in this repo that passes only on machines lacking the thing it tests.

## Also done

`node_modules/` added to `.gitignore` — the root file had no rule at all.
Verified effective via `git check-ignore`.
`testing/_src/package.json` declares the single dependency `@xmldom/xmldom`.

## Changed

```
M  .gitignore                          (node_modules rule)
M  run_checks.py                       (utf-8 stdout fix + node checkers registered)
M  testing/_src/sc_export.js           (replaced; SCX2 -> SCX the only body edit)
D  testing/_src/test_sc_export.js      -> _to_delete/testing_src_superseded_20260809/
?? checks/node_checks.py
?? checks/_verify_node_checks.py
?? testing/_src/{roundtrip,mutate}.js
?? testing/_src/fixtures/{real_export,real_export2}.xml
?? testing/_src/package.json, package-lock.json
```

The old test was **moved, not deleted** — rule 1 outranks the order's "delete"
wording, and the effect C1 wanted is identical. `_to_delete/` is gitignored, so
it is out of the tracked tree.

Nothing committed, nothing staged, no `git add -A`. **No go-ahead, per rule 2.**

## Still outstanding — stating it, not implying otherwise

- **Nobody has loaded a generated file in Star Citizen.** `verified` is still
  hard-coded `false` and must stay that way. Reproducing two files the game
  wrote proves the format is understood; it does not prove the game will accept
  one we generate.
- **This puts an export button nowhere.** The builder-UI order is unwritten and
  is the larger job.
- The stuck device-tab bug still needs an F12 reading from a machine with real
  sticks.
- One machine, one vendor's sticks. Another vendor's `Product` string could be
  shaped differently and nothing here would catch it.
