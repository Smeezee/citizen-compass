# Update — `--include-deployed` ran for the first time: 104 ok, 1 failed. The failure was real, and it exposed a deadlock in the gate I built last night.

**2026-08-28 12:40 local · Code (background session)** — Sleven ran
`python checks/run_all_controls.py --include-deployed`.

    104 ok, 1 failed, 0 skipped, 0 NOT RUN, in 640s

**Run with `venv\Scripts\python.exe` rather than bare `python`** — the 32-bit
interpreter on PATH has no `dotenv`, the runner spawns children with
`sys.executable`, and every control touching `app.database` would have come back
NOT RUN.

## The two opt-in network controls that had never run in a sweep both passed

    _verify_deployed_links.mjs   SWEEP CLEAN - and the canary proves the sweep
                                 can report
    _verify_find_deployed.mjs    Real rows came back from the deployed origin

## The one failure was true, and useful

    _verify_picker_deployed.mjs
      FAIL the served ship page is byte-identical to the one just built
           served 17e9e4705de6856f   local ad81f666d41d3d88

**The deployed site was one C1 feature behind.** `loadout.src.html` was written
at **10:50:43** — ten minutes after my deploy — with the identical-options note:
the line that appears when every option on a port is the same part in a different
wrapper. C1's own control for it, `_verify_identical_options.mjs`, was already in
the tree and passing; only the served bytes were stale.

## AND IT EXPOSED A DEADLOCK I BUILT LAST NIGHT

That control asserts **the served page matches the one just built**. Under Q10's
gate, that failure went into the receipt, the receipt went red, and the deploy
that would have fixed it was refused.

**The deploy was blocked by the absence of the deploy.**

The fix is not a whitelist. The three `--include-deployed` controls answer a
different question — `NEEDS` in the runner already says so in its own words,
*"a statement about the live site, not about this working tree"* — so the receipt
now records which failures are of that kind and `sweep_gate.check()` reports them
without blocking:

    sweep : 1 control(s) failed ABOUT THE LIVE SITE rather than about this payload:
            LIVE     _verify_picker_deployed.mjs
            These do not block: one of them asserts the SERVED page matches the
            one just built, which no action before a deploy can make true.
            Deploying is their remedy, and re-running with --include-deployed
            afterwards is how you find out whether it worked.
    sweep : 104 control(s) green against this exact payload
    gate exit=0

**Reported whether or not they block.** A live-site failure is real information -
the served site is behind, or is broken - and hiding it here would be the silent
success this file exists against.

**This is the second time a design of mine has been wrong in a way only running
it could show.** The gate was proven against seven kinds of bad receipt and none
of them was this one, because nothing had ever run the sweep the way Sleven just
did.

## Deployed, and the loop closes

    ef57ca6b-3602-420b-9915-00710ddd84f1   1 file uploaded: /loadout.html

Re-ran all three afterwards:

    _verify_picker_deployed.mjs   ok - "the served ship page is byte-identical
                                  to the one just built"   30/30
    _verify_deployed_links.mjs    ok
    _verify_find_deployed.mjs     ok

## AND THE CENSUS IS WORTH READING ON ITS OWN

From the SERVED bytes, not from a build log:

    6,326 markers  /  4,388 clickable  /  1,938 fixed-but-informative  /  0 SILENT
    hulls entirely silent:  0   (was 61)

**782 silent markers and 61 fully-silent hulls, down to zero.** That was Sleven's
"the dots don't do anything" on the 400i, and it is measured on the deployed
site over the wire rather than asserted from a local file.

Also on the served page: the Origin 400i shows 52 markers, 44 picker, 8 fixed, 0
silent; the Avenger's turret mount lists its fitted part first on all three
sorts; and the grid is `calc(100vh - 238px)` with internally-scrolling columns,
so the inline picker and the stage panel cost the page no height at either
1920x1080 or 1366x768.

Nothing committed since `1a1b4b7`. Q7 stands at 81 of 104.
