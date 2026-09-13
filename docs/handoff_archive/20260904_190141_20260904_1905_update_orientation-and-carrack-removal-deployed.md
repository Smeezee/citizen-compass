# Update — deployed: inspector orientation fix and the two Carrack bundles gone

**2026-09-04 · Code**

Covers both orders in one rebuild:

    ORDER_every-ship-faced-backwards-in-the-inspector-2026-09-04  (C1, 18:25)
    ORDER_drop-the-two-carrack-c8x-packages-rebuild-2026-09-04    (C1, 18:37)

**Sweep vouched first: 116 ok, 0 failed, 3 skipped**, payload `27f6d133fd5c78e0`.

**The gate refused one attempt before this and it was right to.** Sleven asked
for the deploy while the sweep was still running, so the receipt still named the
previous payload. I ran it rather than predicting the outcome, and it aborted
with "THE CONTROL SWEEP DOES NOT VOUCH FOR THIS PAYLOAD". `-IgnoreSweep` was
offered and not used.

## Verified from the served bytes, cache-busted

    /_inspect                   200, 1,156,865 bytes, byte-identical to payload
    orbit Math.PI+0.9           2 occurrences - initial state and orbit.set()
    fit radius 1.45             yes
    vertexColors disabled       yes
    source notice               yes

    models/C8X_Pisces_Expedition.glb   200, 437,160 bytes  - the real snub, kept
    models/Carrack_w_C8X.glb           404                 - correctly gone

All three deployed-only controls pass.

Sleven's marks are keyed by filename and survive the redeploy; his counter now
reads out of 256.

## The thing worth carrying forward

**This is the second file today to open its camera at +Z when forward is -Z.**
I fixed it in `cc_viewer.js` this morning as V1, after Sleven described the hulls
as "a blob of colours until I rotated it". The inspector was written separately
and made the same assumption independently, and it cost him 93 ships of walking
before he stopped bothering to report it.

`cc_viewer.js` is untouched and still opens at `-d * 0.85` - confirmed by C1 and
independently by me this morning against the point clouds, where the Sabre
measures 3.7 m wide at low Z and 23.3 m at high Z.

**The convention is measured and documented in `place_hardpoints.py` lines 28-34.
It is enforced nowhere.** Two files, the same wrong assumption, found three hours
apart by two different routes, one of them being a human manually turning 93
ships around. A third page will make it again.

`checks/_verify_camera_framing.mjs` already drives a real browser and reads
`camera.position` off the live viewer, so the shape of the answer exists - it
asserts the framing ratio but says nothing about which side of the hull the
camera opens on. **Not writing it unasked**, and it would be a control over a
page C1 owns, but it is a small addition to a control that already exists and it
closes a defect that has now cost real time twice in one day.
