# Update — the stamp fix is built and proven. Sweep running, nothing uploaded.

**2026-09-11 12:15 CDT / 17:15 UTC.** Sleven: *"fix the stamp"*. Both halves of
the restated P24 are done and neither is deployed yet.

## HALF ONE — THE FRONT DOOR CARRIES THE STAMP

The build now injects `testing <date>` into the page the front door serves,
beside its version, in the same place and from the same clock read as the
assembled page's stamp, and **only when not LIVE** — where it would be the lie.

    <span id="ver">v0.4.0 · <b id="cnt">0</b> ships
      <span style="opacity:.6;font-weight:400">testing 2026-09-11</span></span>

**It fails closed.** If the front-door page has no `<span id="ver">` to sit
beside, the build refuses and says why, rather than shipping an unstamped
testing front door.

## HALF TWO — THE GUARDS STOP NAMING `index.html`

Both deploy scripts now ask which page the front door serves and prove the gate
and the stamp on it **as well as** on `index.html` — index stays in, because a
`--live` build strips both from it and dropping it would narrow the guard while
fixing it.

**The name is asked for in ONE place**, `testing/_src/front_door.py`, called by
both scripts — the same reasoning `checks/sweep_gate.py` carries in its own
header. **It fails closed:** if the name cannot be determined the deploy is
refused rather than falling back to `index.html`, which is the exact defect
being fixed.

## RULE 12 — EVERY NEW REFUSAL WAS SEEN FIRING

    the front door with NO STAMP                     refused
    the front door with NO GATE                      refused
    FRONT_DOOR_PAGE unreadable                       refused, NOT defaulted
    a hand-edited stamp DATE                         reported by drift

Each planted, run, read, restored byte for byte and verified afterwards. Aside
copies in `_to_delete/q55_stamp_rule12_proof_20260911/`.

**And the proof earned its keep twice over:**

**1. It found a bug in my own guard.** `& python $tool | Select-Object -First 1`
stops the pipeline on its first line, which **kills the process and leaves
`$LASTEXITCODE` at -1** — so a resolver that worked perfectly reported failure
and aborted every deploy. It passed nothing and refused everything, which is the
safe direction, but it was wrong and only the proof showed it. Fixed in both
scripts: capture first, then take the line.

**2. It found that my first date check was worthless.** The gap check accepted
any well-formed date, so a stamp hand-edited from `2026-09-11` to `1999-09-11`
walked straight through. **The stamp's whole value is that its date comes from
the clock rather than from someone typing.** The date is now cross-checked
against `index.html`'s stamp — a different file in the same payload, stamped by
the same build from one clock read, so they agree or something edited one of
them.

## AND A CLAIM OF MINE THAT WAS WRONG, CORRECTED IN THE CONTROL ITSELF

I taught `_verify_deploy_guards.py`'s fixture to build a payload with a front
door, and wrote in the comment that **an index-only guard would now fail this
control. That was false.** Both fixture pages were driven by the same
gate/stamp toggles, so an index-only guard passes every case — **which is
precisely how the real defect survived.**

**So the fixture gained the asymmetric case, and it is the real one:**
`index.html` perfect, front door missing its stamp. Then the same with the
gate. Then the live script's half — a stamp on the front door alone must still
stop a live publish.

    1b. THE FRONT DOOR ALONE IS UNMARKED - index.html is perfect
      PASS  deploy_testing.ps1 REFUSES a payload whose FRONT DOOR carries no
            stamp, even though index.html does
      PASS  and names the stamp as the reason
      PASS  and never got as far as its dry run
      PASS  ...no password gate, even though index.html does
      PASS  deploy_live.ps1 REFUSES a payload stamped on the FRONT DOOR alone

**An index-only guard passes all three. That is what makes them worth having**,
and it is the shape this morning's regression had. `_verify_deploy_guards.py`:
**123 passed, 0 failed**, up from 116.

## STATE

    build           ok, front door stamped 2026-09-11
    drift           16 passed, 0 failed, stamp injection declared and pinned
    deploy guards   123 passed, 0 failed
    sweep           running (sweep4.log)
    uploaded        NOTHING. Served / is still unstamped until this goes up.

*Code, 2026-09-11 12:15 CDT.*
