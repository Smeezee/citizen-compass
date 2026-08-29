# Update — the deploy-drift defect is fixed: the control no longer writes to the artifact it audits, and the guard was proven by disabling it. Q7 is 105 of 105.

**2026-08-29 10:10 local · Code (background session)**

## THE RULING

**A checker is not a writer of the artifact it audits.** `testing/_deploy` has
one writer — `build_deploy.py` — and `_verify_deploy_drift.py` is not it. That is
rule 14 applied to the one artifact where nobody had applied it.

I named three options on the 28th. **I took none of them.** Not "the sweep
refuses mutating controls" (fixes ordering only, not the evidence loss), not
"snapshot the payload first" (moves the problem to whoever remembers to), and
not "stop rebuilding and report" — **that one would have thrown away the only
honest proof an assembled file has.** `index.html` is built from
`releases/latest.html` plus a dozen substitutions; there is no source to compare
it to. Rebuild-and-compare is the whole proof.

**So: SNAPSHOT, REBUILD, COMPARE, RESTORE.** The comparison is untouched and
nothing is exempted from it. Afterwards every file the rebuild wrote is put back
byte for byte.

## WHAT IT COST BEFORE, FOR THE RECORD

    ORDERING      a control's result depended on where its name sorted
                  relative to "d"
    EVIDENCE      a "before" copy taken at 23:37 on the 28th was an "after"
    A REAL ABORT  the deploy gate refused an upload because this control moved
                  the payload between two of Sleven's commands

## THE FILES IT WAS WRITING, WHICH WERE MORE THAN I THOUGHT

`build_deploy.py` writes **four generated files into `testing/_src`** as well as
the payload — `loadout_model`, `loadout_marker`, `loadout_eng`, `craft_data` —
**and its own receipt**, `.last_build.json`, which `deploy_testing.ps1` reads to
decide whether a build succeeded.

**That last one is a defect on its own.** A rebuild run for AUDIT was leaving
behind a receipt saying a build had completed ok. The receipt is now restored
with everything else.

The watched set is **discovered, not listed** — 77 files this run. A hand-written
list would go stale the day a fifth generated file appears, and it would fail
silently, which is the exact shape of thing this control exists against.

## THE GUARD IS PROVEN BY BEHAVIOUR, BOTH WAYS

Every other assertion in section 4 is measured BEFORE the restore runs, so all
of them would still pass if the restore quietly did nothing. **So the restore
has its own assertion, and I made it fail on purpose.**

    PROBE: a copy with restore() replaced by a no-op

    FAIL  and _deploy and _src are byte for byte as this control found them
          (still moved: testing\_deploy\loadout_marker.gen.js,
           testing\_src\.last_build.json, testing\_src\loadout_marker.gen.js)

Named all three. The probe is in `_to_delete/probes-20260829/`, never deleted.

**And verified from OUTSIDE the control**, because a manifest built by the code
under test proves nothing: an independent script hashed all 612 files under
`_deploy` and `_src` before and after — assets by size and mtime, 445 MB of
models not worth hashing.

    612 file(s) recorded ... IDENTICAL - the control left nothing moved

Twice, on two consecutive runs. `--self-test` still inverts and exits 1.

## IT IMMEDIATELY FOUND SOMETHING THE OLD BEHAVIOUR HID

    FAIL  and so is every copied file (moved: loadout_marker.gen.js)
    -   259 hulls, 6060 markers.
    +   259 hulls, 6058 markers.

**The deployed testing payload is two markers behind its sources.** Real drift,
not non-determinism — `index.html` rebuilt byte-identical beside it.

**The old behaviour would have reported this once and then buried it.** Run one
rebuilt the file, so run two found the payload already matching and went green.
A finding that disappears when you look again is worse than no finding. It now
stays red until somebody runs the build deliberately.

**I have not run that build.** It is a payload change and it wants a deploy
behind it; that is a separate decision and it is Sleven's, not something to
staple onto a checker fix.

## AND Q7 CLOSED WHILE I WAS IN THERE

C1 labelled `_verify_panel_dismiss.mjs` INDEPENDENT. The gate asked for the
baseline line to come out, so it came out:

    labelled 105  (56 INDEPENDENT, 49 UNPROVEN)   unlabelled 0   malformed 0
    0 gap(s) still on the list

`rule16_baseline.txt` is now empty of entries and says why. **Q7 is 105 of 105.**

## STANDING

Files changed: `checks/_verify_deploy_drift.py`, `checks/rule16_baseline.txt`.
Nothing committed. A full sweep is running to confirm the fix in the place it
was built for — the first sweep in this repo that cannot be perturbed by its own
drift control.
