# Update — CODE-1: build is green, the check is RED, deploy HELD

**2026-08-27 11:50 · Code (background session)** — stopped for a decision.
`ORDER_the-split-2026-08-27.md`, CODE-1. Build and all mutators run. **Not
deployed.** Sleven's call, and the reasons are below rather than summarised.

## The build ran clean

`venv/Scripts/python.exe testing/_src/build_deploy.py` — TESTING payload,
exit 0. (`build_deploy.py` is at `testing/_src/build_deploy.py`, not the repo
root, and it needs the venv interpreter; system python has no sqlalchemy.)

Every gate it owns passed: `_verify_slots`, `_verify_conflict`, `_verify_poll`,
`_verify_navkeys`, `_verify_loadout_data`, `_verify_holo_placement` and its
self-proof, inline JS parse on both source pages, version agreement, and the
deploy guard. Row counts file-vs-database matched: models 235/235, slots
2195/2195. `testing/_deploy` is now 11:33 today, up from 06:14.

## The check is red, and the two failures are NOT the same kind of thing

    7 passed, 2 failed

**Failure 1 — section 2, "clicking off the stage closed it too". This is real,
and it is the half of P1 that did not land.**

Not a check artifact. I probed the deployed bytes directly with a throwaway
diagnostic, clicking five different off-stage targets on the Arrow:

    .tabs (what the check clicks)    STAYS OPEN   (hit A.on)
    the active tab link              STAYS OPEN   (hit A.on)
    the spec table                   STAYS OPEN   (hit DIV.slot)
    the page header                  dismisses
    the page margin (body edge)      dismisses

The dismiss branch itself is correct — it names `sel || mountSel`, the
`#cc-stage` scoping is gone, and it sits at the end of the handler. But the
handler returns earlier at `const tb=e.target.closest('.tabs a[data-tab]')`,
so a click on the tab bar switches tab and never reaches dismiss.

`ORDER_the-panel-will-not-close` names this case in its own words: *"A click on
the spec table, the tab bar, the page margin - anywhere off the stage - leaves
the panel up."* The margin and header now dismiss. **The tab bar still does
not.** The spec-table row is a different matter — `.slot[data-slot]` is
deliberately excluded in the branch, so staying open there looks intended.

**Failure 2 — section 3, the part-row control. This one is a fixture defect.**

    before MRCK_S03_BEHR_Dual_S02
    after  MRCK_S03_BEHR_Dual_S02
    part   MRCK_S03_BEHR_Dual_S02

The check takes the FIRST `.pi[data-part]` offered and asserts
`after !== before`. The first row offered is the part already fitted, so the
click applied correctly and the assertion still cannot hold. Selection is not
broken; the control cannot pass as written.

## The mutators — two proven, one unobservable

    --mutate-selonly     PROVEN.  Section 1 flipped: "clicking empty stage
                         closed it" and "BOTH sel and mountSel were cleared"
                         both went red, with mountSel left at "0".
    --mutate-accent      PROVEN.  Section 4 flipped: panel border
                         rgb(34,211,238) against col rgb(34,54,79).
    --mutate-stagescope  NOT OBSERVED. Output identical to baseline - same
                         7 passed, 2 failed, same two. Its target assertion
                         is ALREADY red, so the mutation changes nothing and
                         cannot be distinguished from no mutation at all.

**That third line is the rule-12 case, exactly.** A mutator whose target is
already failing proves nothing, and reporting it as "went red" would be
reporting a pass the run never earned. It is recorded as not performed.

**`--mutate-order` is documented in the check's header and is not implemented.**
Running it prints `UNKNOWN MUTATOR --mutate-order`. The header describes four
controls; three exist. The missing one is the control on section 3 — the same
section whose fixture is broken.

## What I did not do

- **Did not deploy.** The gate is red. Fail closed; the call is Sleven's.
- **Did not touch `loadout.src.html`, `cc_viewer.js` or
  `_verify_panel_dismiss.mjs`.** C1 is the writer of all three. The tab-bar gap
  and both check defects are C1's to fix.
- **Did not adjust anything to suit the check**, per the order.

New file in my lane: `checks/_diag_panel_dismiss_click_target.mjs` — a
diagnostic, not a gate. It asserts nothing and gates nothing; it exists to say
which off-stage clicks dismiss. Delete or keep as you like.

## For C1

Three items, all in your files:

1. The `.tabs a[data-tab]` branch returns before the dismiss branch. If the tab
   bar is meant to dismiss, the tab branch has to clear `sel`/`mountSel` before
   it returns, or dismiss has to run ahead of it.
2. Section 3 needs a part row that is not the fitted one, or an assertion that
   tolerates re-applying the same part.
3. `--mutate-order` is in the header but not in the mutator table.
