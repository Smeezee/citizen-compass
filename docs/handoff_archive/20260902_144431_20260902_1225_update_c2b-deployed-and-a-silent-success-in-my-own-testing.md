# Update — C2b deployed; and I caught a silent success in my own test loop

**Code**

## Deployed

Version ID `637c5bb2-d1e1-4c1d-8e06-7f35645af842`. Testing only.

The payload carries C2b: `"last_verified_patch": "4.10"` and
`"game_build": "4.10.0-LIVE.12519617"`, both derived from the snapshot's
manifest rather than typed.

**The deploy gate did its job first.** `deploy_testing.ps1` refused the payload
until the control sweep vouched for it, and `-IgnoreSweep` was not used.
`checks/run_all_controls.py`: **113 ok, 0 failed, 3 skipped, 0 not run**, 1039s.
The three skips are the deployed-only controls, which cannot run before the
thing they check exists.

## A silent success, mine, in the loop I used to check the deploy

I ran the three deployed-only controls afterwards with:

    for f in ...; do node "$f" >/dev/null 2>&1; echo "$(basename $f) EXIT=$?"; done

All three reported **EXIT=0** and I nearly wrote that down as three passes.

**`$(basename $f)` runs before `$?` is expanded, and resets it.** Every one of
those exit codes was `basename`'s, not node's. The loop could not have reported
a failure - it was a check that could not fail, in the exact shape rule 12
names, and it was mine.

Caught it because a control that had been crashing all afternoon suddenly
"passed" and that was too convenient to accept. Re-run with the status captured
into a variable first:

    _verify_deployed_links.mjs   EXIT=0
    _verify_find_deployed.mjs    EXIT=0
    _verify_picker_deployed.mjs  EXIT=1

Nothing self-healed. Two pass, one is still red.

## The one red control, unchanged and still not mine to fix quietly

`_verify_picker_deployed.mjs` dies booting the built page:

    ReferenceError: NodeFilter is not defined
      at decorate (cc_glossary.inc.html)
      -> glossPage -> renderAll

`testing/_src/cc_glossary.inc.html:176` calls
`document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null)`. Neither
`NodeFilter` nor `createTreeWalker` exists in `checks/_loadout_harness.mjs`. The
glossary is injected into the BUILT page only, which is why the source page
boots clean and the built one does not.

Proven not to be mine: I reconstructed the pre-V3 source, rebuilt from it, and
it crashes identically.

**It blocks nothing** - the sweep gate skips deployed-only controls, so this has
been red and invisible rather than red and stopping anything. That is the part
worth fixing.

**Not fixing it on my own initiative.** The harness is Code's, so I may write
it, but the honest repair is a real `createTreeWalker` that actually walks text
nodes. A stub that returns nothing would make the control green while the
glossary decorated nothing - the same trick as a stub camera that always looks
at its target, which is what cost the fleet four days. That is worth an order,
not a guess.

**`testing/_src/cc_glossary.inc.html` has no owner in `OWNERS.md`.** Second
unowned path found today; the file itself says finding one is worth reporting.
