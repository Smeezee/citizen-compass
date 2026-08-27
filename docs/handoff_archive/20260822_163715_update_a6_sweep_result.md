# Update - A6, the sweep ran: 44 ok, 2 failed, 2 skipped

Full control sweep finished in 161s. 0 NOT RUN.

**44 ok. Two failures, and neither is what it looks like at first glance.**

## 1. `_verify_g3_matcher_delta.py` - NOT PERFORMED, correctly

`CC_GEO_DIR` is not set, so the build can read no geometry and the check
cannot look at anything. It said so and exited 2 rather than passing. That is
rule 11 working, not a regression.

## 2. `_verify_deploy_drift.py` - the check's model of the build is stale

Six copied pages reported as differing from their `_src` source:
download, keybinds, find, stick-test (byte compare) and loadout, holo (the
either-side-of-the-vendor-marker compare).

**The cause is A1/A3, and the files are correct.** The build now appends the
attribution block - the trademark strip, plus the source and contact notice on
ship pages - to every page on the way into `_deploy`. Diffed
`download.html`: the only difference is that injected block, nothing else.

The check still describes those pages as COPIED VERBATIM, which stopped being
true the moment the build began injecting. Note what the same run proved one
section later:

- `index.html` is byte-identical after a rebuild
- **and so is every copied file**

So `_deploy` IS what the build produces. Nothing was hand-edited into it. The
byte-compare against raw `_src` is asking the wrong question now.

Its plant test still works: a hand edit planted into `_deploy/download.html`
was reported, then restored byte for byte, and the planted copy moved aside to
`_to_delete\deploy_drift_plant_20260822163253` rather than deleted.

## Next

Teaching the drift check about the attribution block the same way it already
knows about the vendor marker and the model-path seam: a DECLARED, narrow
transform, with everything either side of it still compared byte for byte -
not an exemption for the whole file. Then re-running it against known-bad
input to confirm it still fails when it should.

Not touching any legal text to do it - the check will read the one
`attribution.py` constant rather than carry a second copy (rules 8 and 14).

A6's deploy-to-testing half has NOT run. Waiting on the drift check being
honest again first, and on Sleven for the deploy itself.
