# Update — finished: swept, deployed, and all five steps closed

**2026-09-05 · Code (Build)**

## 1-2. Sweep and deploy

    120 ok, 0 failed, 3 skipped, 0 NOT RUN
    receipt payload 0fb74255dd4710f5 = the payload deployed
    Version ID d96e2dc1-316d-4fbd-9a23-363edab60c3a

**Testing only. No `-IgnoreSweep`.** The three skips are the deployed-only
controls, which cannot run before the thing they check exists.

Verified from the SERVED bytes, cache-busted: `_inspect` and `loadout` both
byte-identical to the payload, `models/Hammerhead.glb` 200 at 4,153,816 bytes.

The payload had never been deployed before this. It is out.

## 5. The takedown notice is off the inspector

    _inspect.html    source-notice NO    takedown NO    trademark YES
    index.html       source-notice YES   takedown YES   trademark YES
    loadout.html     source-notice YES   takedown YES   trademark YES
    holo.html        source-notice YES   takedown YES   trademark YES
    find.html        source-notice NO    takedown NO    trademark YES

Done by removing `_inspect.html` from `_SHIP_CONTENT_PAGES` in
`build_deploy.py` - reversing a line I added yesterday on C1's order. Only the
source-and-takedown block is withdrawn, and only from that page.

**Rule 8 says that wording is Sleven's alone and out of my hands. He directed
this himself, in writing, with his reason.** The comment in the file records
that, so nobody later reads it as a session editing legal text on its own
judgement.

## 4. The drift control refuses a foreign journal

`recover_interrupted()` ran FIRST, before any assertion, and copied preserved
files back over their targets using absolute paths from a journal it did not
write. On 2026-09-05 that journal was written on a Cowork VM and listed eighty
paths under `/sessions/rcw-.../`. It crashed on Windows.

**The crash was the only thing that prevented eighty source and deploy files
being overwritten.** Safe by accident is not safe.

It now refuses any journal whose recorded paths are not under this checkout,
names them, restores nothing, and **leaves the marker alone** - because that
journal may still be the live recovery record of the machine that wrote it, and
clearing it here would strand that restore.

**Proven both ways:**

    foreign journal (the real /sessions/... case)  REFUSED, 0 restored, no crash
    local journal                                  not refused, recovery intact

The second half matters as much as the first: a guard that disabled recovery
would be a different defect wearing the same fix.

## 3. Q2 and Q5 re-run against what is actually on disk

**Q5: 256 of 256 clean.** No load failures, nothing empty, nothing invisible,
nothing overflowing. Zero retries and zero page errors.

    fleet median coverage 6.24%  ->  invisible bar 1.56%  (min observed 2.63%)

`docs/contact_sheet_20260905/index.html`, 256 shots, 12 MB, rebuilt 16:32.

**It needed a whole re-run, not a resume.** An interrupted pass had left 224
current images beside 32 stale ones under an index from 09:25 describing C1's
replacement models. A sheet that is half one fleet and half another is worse
than no sheet, which is C1's own point.

Median coverage moved 2.45% -> 6.24% between the two runs. Different models and
a different fit, so the older figures do not carry over; this is the sheet that
matches what is being served.

**Q2 caught a defect in my own harness.** It printed "the file has a single mesh
and a single node, so two separated hulls cannot be present" while reporting
**985 mesh objects**. That sentence was written while C1's single-mesh
replacement was on disk and survived the revert as a hard-coded conclusion
sitting beside numbers that contradicted it. It now computes the clustering:

    85X: largest empty gap along X 0.63 m = 5.2% of a 12.05 m spread, 25 / 960

**That is not a clearance.** The file on disk is the 939-node original Sleven
marked as two ships. C1's 8.75 m separation was measured in un-normalised
coordinates and the deployed copy is scale-fixed and recentred, so the picture
is still the answer and his mark stands.

Other Q2 answers against the served payload: the X1's materials are entirely
double-sided, so the see-through cause is absent; all three X1s now carry
distinct geometry signatures, though X1 and X1_Force share an identical triangle
count and extent and are near-twins rather than genuinely different.

## Noted, no action

`ORDER_the-material-field-was-swapped-and-the-decode-still-does-not-work` is
marked for information, payload untouched, nothing mine to do. Read, not acted
on.
