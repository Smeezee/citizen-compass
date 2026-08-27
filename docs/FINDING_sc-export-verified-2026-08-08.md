# FINDING — the SC mapping exporter works. Ran its tests, then broke it six ways to prove they mean something. One survivor, and it is cosmetic.

    from      C3 (Cowork), 2026-08-08
    for       C1 + Sleven (→ Code)
    why       C3's own work order said the exporter's correctness was "asserted by its 23
              tests, which I also did not run." Closing that gap before anyone builds a UI
              on top of it.
    scope     `testing/_src/sc_export.js` + `test_sc_export.js`, staged and executed.
              Nothing on the machine was modified — mutations were made to a staged copy
              in a scratch workspace and reverted.

---

## 1. It passes, and the tests are not vacuous

    node test_sc_export.js  ->  passed: 23   failed: 0

The suite needs `data-layer/processed/actionmap_categories.json` on a relative path; without
it the run dies with `ENOENT` before a single check executes. **Worth knowing for CI: a
missing data file here does not read as a failing test, it reads as a crash** — and a crash in
a pipeline that only greps for "failed:" would pass silently.

**Then, per hard rule 12, six deliberate mutations. Five were caught:**

    M1  keyboard GUID changed to a wrong value        CAUGHT  "keyboard options line missing or altered"
    M2  modifier-combo refusal disabled               CAUGHT  "refused binding text leaked into the XML"
    M4  verified:true forced with joystick present    CAUGHT  "joystick output must not be marked verified"
    M5  mouse-rides-keyboard device line removed      CAUGHT  "mouse device missing though a kb1_mouse binding is present"
    M6  refused bindings written into the XML anyway  CAUGHT  "refused binding text leaked into the XML"

**These are the checks that matter.** M4 in particular — the suite refuses to let the code
claim a joystick file is verified when it is not, which is the exact honesty property the whole
design rests on.

## 2. The one survivor — real, but cosmetic, and diagnosed rather than reported

    M3  the explicit `ms1_` refusal disabled          SURVIVED  23/23 still passed

**Why it survives:** the binding is still refused, just by a different rule. With the specific
check removed, `ms1_mouse4` falls through to `famOf()`, which does not recognise `ms` as a
prefix and rejects it anyway. **Behaviour is unchanged; only the explanation degrades:**

    check active    "mouse uses the keyboard prefix (kb1_mouse4), not ms1_"
    check disabled  "input 'ms1_mouse4' has no recognised device prefix (expected kb1_, js1_, gp1_)"

The first tells a user exactly what to do. The second tells them something is wrong.

**Root cause: no test asserts on the refusal *reason*, only on whether a refusal happened.**
`test_sc_export.js:40` checks that `ms1_` is rejected; it never checks why. So the helpful
message could be deleted tomorrow and every test would still pass.

**Not a defect in the output — no bad file can be produced by this.** It is a gap in the tests,
and it matters because that reason string is going to be shown to a person in the binding
builder UI. Recommend one added assertion on the reason text for `ms1_`, which closes it in a
line.

## 3. What this means for the binding builder

**The keyboard path is proven and safe to build on now.** The GUID, the `<options>` line, the
mouse-on-keyboard-prefix rule, only-what-changed output, and the refusal machinery are all
covered by checks that have been seen to fail.

**The joystick path is exactly as unproven as the header says** — and the tests actively
enforce that it never claims otherwise. That remains a ten-minute in-game test, unchanged.

**So the work order's sequencing can be relaxed in one specific way:** the builder's UI, the
action picker, the refusal display and the keyboard/mouse export can all be built and shipped
before Sleven runs the joystick test. Only the joystick half waits. That is a real feature on
its own — 691 labelled actions with 238 plain-English descriptions is already a better place to
rebind than the game's own menu — and it de-risks the joystick work, because when the test
comes back only the device-specific line changes.

## 4. What I checked and what I did not

**Checked:** ran the suite; read `sc_export.js` in full; executed six mutations and reverted
each; verified the M3 survivor's actual behaviour by calling `reject()` directly with the check
both active and disabled; grepped the suite for reason-text assertions.

**Did NOT check:**
- **I did not generate a file and load it in Star Citizen.** Nothing here says the game accepts
  the output — only that the code does what its own documentation claims. **The only test that
  matters is still the in-game one**, and it has not been run.
- Did not test `build()` against a large realistic binding set, only the suite's fixtures.
- Did not test non-ASCII profile names beyond what `safeName()` strips, or duplicate bindings
  on one input.
- **Did not modify anything on Sleven's machine.** All mutation work was on a staged copy in a
  scratch workspace, deleted afterwards.
