# WORK ORDER — replace `sc_export.js` with the round-tripping version and put both test harnesses in CI. Nothing else.

    from      C3 (Cowork), 2026-08-09
    for       C1 — to turn into a prompt for Code
    evidence  claude/FINDING_exporter-round-trip-passes-2026-08-09.md
    inputs    inbox/sc_export2.js · inbox/roundtrip.js · inbox/mutate.js
    size      small. One file replaced, one file deleted, two files added, CI touched.

---

## 1. What this order is, in one line

Put the exporter that can actually write a Star Citizen mapping file into the repo, under a
test suite that proves it, **before** anyone writes the UI work order that will depend on it.

## 2. Why this is safe to land on its own — and why that is also its limitation

I grepped the whole repo. **`sc_export.js` is called by nothing except `test_sc_export.js`.**
The deployed `testing/_deploy/keybinds.html` contains no reference to `export`, `.xml` or
`ActionMaps` anywhere in it. The module is an orphan — which was already on record in
`claude/WORKORDER_keybind-builder-the-missing-half.md` and is confirmed again here.

That cuts both ways and both halves matter:

**It makes this change risk-free.** There are no call sites to update, no build step to
re-verify, no page that can regress. A file nobody calls cannot break anything when it is
replaced.

**It also means this change does nothing a user can see.** Landing it does not put an
export button on the keybind page, because there is no export button to put it on. Anyone
reading the commit should understand they are correcting a broken component, not shipping
a feature. **Do not let this get described as "keybind export is done."**

## 3. Why the other two pieces are deliberately NOT in this order

**The builder UI is out of scope because it is not an edit — it is new structure, and it
has to be written against the build system rather than beside it.** `CURRENT-STATE.md`
records that `build_deploy.py` substitutes its own copies of some blocks and that
`inject_engine.py` makes `device_engine.js` the single writer of the device panel, with the
consequence spelled out: **patching only the source layer can silently do nothing.** The
device-identity fix has to land inside `device_engine.js` or the build will keep the old
slot-order code and the sticks will still appear swapped — passing review while being
wrong, which is this project's recurring failure shape. That deserves its own order,
written after reading `build_deploy.py` and `inject_engine.py` properly. Neither file is in
the copy of the repo I can see; C1 has the real one.

**The 3D viewer is out of scope because it is blocked on a decision, not on code.** The
prototype inlines four ships at 13.3 MB. The site already has 349 MB of models sitting on
the open internet under `_deploy/`, because the password gate does not cover static assets.
How models get served is Sleven's call and has not been made. Writing viewer code before
that is answered wastes the work.

## 4. The change

| action | path |
|---|---|
| replace | `testing/_src/sc_export.js` ← contents of `inbox/sc_export2.js` |
| delete | `testing/_src/test_sc_export.js` |
| add | `testing/_src/roundtrip.js` ← `inbox/roundtrip.js` |
| add | `testing/_src/mutate.js` ← `inbox/mutate.js` |
| add | the two real exports as fixtures (see §5) |

**Keep the exported name `SCX`.** The new file declares `SCX2`; rename the variable and the
`module.exports` line to `SCX` on the way in, so nothing has to learn a second name. The
name is the only edit Code should make to the file — everything else in it is under test
and changing it will show up as a failure.

`test_sc_export.js` is deleted rather than kept because it asserts the old behaviour: it
requires that a joystick build return `verified:false` **with no `<options>` line**, which
we now know is the defect. Leaving it in place would mean a green test suite defending the
bug. `roundtrip.js` covers everything it covered and 30 things it did not.

## 5. The fixtures, and why they belong in the repo

Both harnesses read the two real exports from Sleven's friend's machine. Without them the
tests cannot run, so they are not optional inputs — they are part of the suite.

    testing/_src/fixtures/real_export.xml    (test1CR)
    testing/_src/fixtures/real_export2.xml   (test3cr)

Update the two `require`/path constants at the top of `roundtrip.js` to point at them.
They are ~21 KB each and contain no personal data beyond a profile name and two device
GUIDs — worth a glance from Sleven before it goes in, but there is nothing in them I would
hold back.

`roundtrip.js` also reads two files that are already in the repo and must not be copied or
duplicated:

    data-layer/processed/keybinds_site.json          the game's canonical actionmap order
    data-layer/processed/actionmap_categories.json   the category lookup

**That the category list in both real exports is reproduced exactly from the repo's own
lookup table is an independent check on that table**, not just on the exporter. If it ever
starts failing, suspect the data file as readily as the code.

## 6. What the API now needs from a caller

Nothing calls it today, so this is documentation for whoever writes the UI order next, not
a migration:

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

**`verified` is hard-coded `false` and must stay false.** No file this tool generated has
ever been loaded by Star Citizen. Reproducing two files the game wrote proves we understand
the format; it does not prove the game will accept ours. If a future change flips that flag
without an in-game load behind it, that is a defect.

## 7. CI

Both harnesses exit non-zero on failure and print a readable line per check, so they wire in
as two plain steps. The only dependency is `@xmldom/xmldom`, for a `DOMParser` in node.

**`mutate.js` rewrites `sc_export.js` in place and restores it after each mutation.** In CI
that is fine. On a developer machine an interrupted run can leave a mutated file on disk —
it restores in a `finally`-shaped pattern but a hard kill will beat it. Worth a line in the
file header if Code wants to be kind to the next person.

**Expect `19/20` from `mutate.js`, not `20/20`.** The survivor is not a gap to fix. Nothing
in either real file distinguishes an ASCII sort from a case-insensitive one, so the
evidence genuinely cannot decide it; `roundtrip.js` asserts that ambiguity deliberately, so
that a future export which *does* distinguish them fails loudly instead of the sort being
quietly wrong for years. **If someone "fixes" the survivor to reach 20/20, they have
invented an answer.** Put the expected count in the CI step name.

## 8. Acceptance — what must be true before this is called done

1. `node testing/_src/roundtrip.js` prints **ALL CHECKS PASSED** and exits 0.
2. Inside it, both of these pass by name — they are the order:
   - `real_export.xml: byte-for-byte identical to what the game wrote`
   - `real_export2.xml: shuffled input still reproduces the game's file byte for byte`
3. `node testing/_src/mutate.js` reports **19/20** with `M18` as the only survivor.
4. `grep -rn "test_sc_export" .` returns nothing.
5. `testing/_deploy/` is unchanged. **This order does not deploy.** If anything under
   `_deploy/` moved, something was done that was not asked for.

Point 5 is the one to watch. The temptation to "while I'm in here" wire the exporter into
the page is exactly what §3 says not to do yet.

## 9. What C1 should NOT do

- Do not touch `device_engine.js`, `keybinds.html`, `kb_modes.gen.js` or any build script.
- Do not run the deploy script.
- Do not edit the body of `sc_export2.js` beyond the `SCX2` → `SCX` rename. If a test fails
  after the rename, the rename is wrong; the file passed 32 checks and 20 mutations as
  written.
- Do not raise `verified` to true.

## 10. Still outstanding after this lands, so nobody thinks it is finished

- **Nobody has loaded a generated file in the game.** Sleven's, ten minutes, and it is the
  only thing that settles whether any of this works.
- The builder UI order is unwritten and is the larger job.
- The stuck device-tab bug needs an F12 console reading from a machine with real sticks; it
  does not reproduce headless.
- One machine, one vendor. Another stick maker could format the `Product` name differently
  and nothing here would catch it.

---

## Commands

Install the one dependency:

```
npm install @xmldom/xmldom
```

Run the round-trip suite:

```
node testing/_src/roundtrip.js
```

Run the mutation suite:

```
node testing/_src/mutate.js
```

Confirm the old test file is gone from the whole repo:

```
grep -rn "test_sc_export" . --exclude-dir=node_modules --exclude-dir=.git
```

Confirm the deploy directory was not touched:

```
git --no-optional-locks status --short testing/_deploy/
```
