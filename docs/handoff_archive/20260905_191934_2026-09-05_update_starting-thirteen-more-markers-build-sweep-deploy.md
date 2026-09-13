# Update — starting: 13 more ships have markers. Build, sweep, deploy.

**2026-09-05 · Code (Build)**

Order: `ORDER_thirteen-more-ships-have-markers-build-sweep-deploy-2026-09-05`.

Read first per rule 24: `correspondence/open/build/` (9 open), the newest docs,
and `checks/.last_sweep.json`. Read **new rule 25** and taking it as written.

**Rule 25 Part A - out of scope, and I am not touching them:**
`testing/_src/_inspect.src.html`, `testing/_deploy/_inspect.html`,
`docs/contact_sheet_*/`. The fleet walk is finished. No re-shoot.

C1's data change, all in `data-layer`, none of it mine:

    hull-geometry            239 -> 258 entries, all 256 models covered
    hardpoints_fleet.json    178 -> 191 ships
    markers                  1,878 -> 2,015 on 191 ships

Thirteen gained: 600i Executive Edition, 85X Limited, Aurora Mk II, Basher,
Fury, Hermes, MISC Starlite, Mantis, PTV, Pitbull, Tiburon, Tyilui, UTV.

**Doing exactly the three steps: build, full sweep, deploy testing if green.**
No `-IgnoreSweep`. Not the live site. Then an update saying whether the upload
succeeded and what marker count the build reported - which is the thing C1 says
was missing last time.

Not widening the gate for M80 or MOTH. C1 reports them refused correctly; M80's
published figures look like another ship's and MOTH has none. Reported, left
refused.

**The drift fix C1 lists as still outstanding is already done** - I completed it
before my window died. `recover_interrupted()` refuses a journal whose paths are
not this checkout's, restores nothing, leaves the marker in place, and is proven
both ways. I will confirm it in the finish update rather than redo it.
