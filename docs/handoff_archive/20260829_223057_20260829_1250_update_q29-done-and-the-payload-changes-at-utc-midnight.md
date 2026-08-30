# Update — Q29 is built and proven in both modes, the new draco control now reads as NOT RUN instead of FAIL, and chasing a moved fingerprint found that the payload rewrites itself at UTC midnight.

**2026-08-30 03:50 UTC / 2026-08-29 22:50 local · Code (background session)**

## Q29 — DONE

    exit 0          PASSED
    exit 2          NOT RUN, with the control's own reason printed
    anything else   FAILED

    106 ok, 0 failed, 0 skipped, 1 NOT RUN, in 778s
    NOTRUN _verify_marker_mesh_distance.py  exit 2  NOT PERFORMED - NO_DRACO...

**Nothing was made to pass.** The gate still refuses, in its own words:

    sweep : the last sweep of THIS payload was not clean.
            NOT RUN  _verify_marker_mesh_distance.py
            A control that could not be run is counted against the
            sweep, never as a pass.
    GATE EXIT 1

**Proven in both modes, probes parked in `_to_delete/probes-20260829/`:**

    NORMAL     exit 0 -> ok     exit 1 -> FAIL     exit 2 -> NOTRUN + reason
    SELF-TEST  exit 2 -> NOTRUN

**The self-test half is the one that mattered.** There `ok = (code != 0)`, so
before this change a control that COULD NOT LOOK was counted as having CAUGHT
the planted defect — the silent success this suite exists against, wearing the
colours of the test meant to find it.

## AND I DID Q30 TO MYSELF WITHIN THE HOUR

My `--only` probe run overwrote the full receipt, exactly as C1's did. It failed
closed and the gate caught it — **and I have changed my mind about whether that
is sufficient.** Two sessions destroyed the same artifact the same day, both
doing legitimate work. "The gate catches it" is what you say about a defect you
have decided to keep. **A subset run should write its own receipt somewhere
else.** Mine to fix if Sleven wants it.

## THE PAYLOAD REWRITES ITSELF AT UTC MIDNIGHT

The sweep's fingerprint moved from `add0c868` to `0f4f5ff3` with nobody having
built anything. All twenty payload files were fetched from the served site and
compared. **Nineteen identical. `index.html` differs by two lines, and both are
a date.**

    -testing 2026-08-29        build_deploy.py:741
    +testing 2026-08-30        _stamp = datetime.now(timezone.utc).strftime(...)

**Three guards assume a rebuild is reproducible and it is not:**

- **`_verify_deploy_drift.py`, mine** — its entire proof of the assembled file
  is "rebuild and require the bytes not to move". A sweep straddling 00:00 UTC
  will report a drift that does not exist. It has not happened yet only because
  tonight's sweep began after the rollover.
- **`sweep_gate.py`'s fingerprint** — content-based, so the clock silently
  invalidates a clean receipt.
- **The served site** — today's deploy shipped `08-29`, local now says `08-30`.
  Neither is wrong and they do not match.

`docs/FINDING_the-payload-changes-at-utc-midnight-2026-08-30.md`, with three
options. **I would declare the stamp as a fourth narrow injection in the drift
control**, the way the vendor marker and trademark strip already are. Small
change, my file, not made without a word.

## TWO FALSE TRAILS ON THE WAY, BOTH MINE

- A first comparison said EVERY file differed. `sha256sum FILE` prefixes its
  output with a backslash when the path contains one, shifting `cut -c1-12` by a
  character. Hashing through stdin removed the filename and the artifact.
- A second said two pages differed when they had simply not been fetched — the
  worker answers `/loadout`, not `/loadout.html`, and returns 307. **An empty
  response hashes perfectly well**: `e3b0c442...` is the SHA-256 of nothing and
  it sits in a comparison looking exactly like data.

## STANDING

    Q26  withdrawn - my measurement was a photograph too
    Q29  done
    Q30  open, and my answer changed: not sufficient

**Uncommitted:** `checks/run_all_controls.py`, `checks/_diag_offhull.mjs`, the
UTC finding. **Not done:** `npm i draco3d`, which I have asked about properly
rather than acting on a conditional offer.
