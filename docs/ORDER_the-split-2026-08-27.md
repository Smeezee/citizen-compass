# ORDER — Who has which artifact, from now until this is done

**C1, 2026-08-27. For Code. Read this before touching anything.**

Sleven: *"If Code's not doing anything right now, so Code can do something, and
you can do whatever he's not doing that still progresses us forward. That was
the whole original plan."*

Correct, and the reason it stopped working is that both of us were queued behind
the same files. Rule 14 says one writer per artifact. **This order names the
writer for each one.** It does not change the rule; it applies it.

---

## C1 IS THE WRITER OF THESE. CODE DOES NOT EDIT THEM.

    testing/_src/loadout.src.html
    testing/_src/cc_viewer.js
    checks/_verify_panel_dismiss.mjs
    probe_ship_geometry.py
    extract_p4k_entry.py

**P1, P2, P3 and P3d from `ORDER_the-panel-will-not-close-2026-08-27.md` are
ALREADY WRITTEN into the first two.** That order is now a record of why, not a
job. Do not implement it again.

- **P1** — the dismiss branch names both `sel` and `mountSel`, drops the
  `#cc-stage` scoping, and is moved to the END of the click handler so every
  specific branch returns first. Both states cleared on dismiss.
- **P2** — `#cc-panel` borders in `var(--line)` like every other panel on the
  page, with corner brackets in a new `--bracket` token at low alpha.
- **P3** — `CC_HOLO.REV`, written into the saved blob, and a saved blob at a
  lower or missing rev loses its appearance keys once and is re-stamped.
- **P3d** — one quiet line in the look panel on the load where that happened.

`node --check` passes on `cc_viewer.js` and on the new check.

## CODE IS THE WRITER OF THESE. C1 DOES NOT TOUCH THEM.

    the build and the deploy
    everything under data-layer/derived/model-availability/
    the model import pipeline and the models themselves
    checks/ other than _verify_panel_dismiss.mjs

---

## CODE-1 — BUILD, CHECK, DEPLOY. FIRST, BECAUSE SLEVEN CANNOT SEE ANY OF IT YET.

**C1 could not build.** `build_deploy.py` fails at `build_find_data.py` with
`ModuleNotFoundError: No module named 'sqlalchemy'` — the device mount is a
Linux VM with no project venv **and no network**, so the dependency cannot be
installed there either. That is a hard limit of where C1 runs, reported rather
than worked around. It is not a defect in the build.

    python build_deploy.py
    node checks/_verify_panel_dismiss.mjs
    node checks/_verify_panel_dismiss.mjs --mutate-selonly      # MUST go red
    node checks/_verify_panel_dismiss.mjs --mutate-stagescope   # MUST go red
    node checks/_verify_panel_dismiss.mjs --mutate-accent       # MUST go red
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

**Every mutator must be observed to fail.** A mutator that passes means the
control is not testing the defect, and C1 wrote both the fix and the check, so
this is the only independent evidence either is real. If a mutation reports
`MUTATION DID NOT APPLY`, the pattern has drifted from the source — say so, do
not adjust the source to suit the check.

**The settings revision has no check yet and that is a gap, not an oversight.**
P4e and P4f in the panel order still need writing: seed `localStorage.ccHolo`
with an unstamped blob and prove the defaults win; seed one at the current REV
and prove it survives. **The second is load-bearing** — without it, P3b passes
trivially by discarding everything always, and H1f-2's permanence dies while the
suite stays green. Code writes those two; they are in `checks/`.

## CODE-2 — THE TWELVE MODELS AND THE FLEET SWEEP

`ORDER_the-fifteen-are-not-missing-2026-08-27.md`, M4 and M5, unchanged.

**Code has network. C1 does not** — `api.fleetyards.net` is refused by this
session's egress proxy and the device VM has no network at all. That is why
the fleet sweep in that order is Code's and not C1's, and why the 46 fleet names
C1 collected through a summarising fetch tool are thrown out rather than used.

Eleven go in. The 85X waits on a human — `85x-limited` 404s and `85x` is a
different record.

## CODE-3 — NOTHING. Do not start the p4k work.

`FINDING_the-coordinates-are-in-the-client-2026-08-27.md` is C1's lane and C1 is
still in it. **176 `hardpoint_*` nodes were found in `DRAK_Vulture.cga`, with
transforms in the same chunk, and the record layout is NOT yet decoded.** No
table exists. Do not build against one.

---

## What Sleven gets to see, and when

CODE-1 is the whole of it. Until the build runs and the deploy script fires, the
picker still cannot be dismissed and his saved cyan settings still overwrite
every default on load. **Nothing C1 wrote today is visible to him until that
deploy.**

---

*C1, 2026-08-27.*
