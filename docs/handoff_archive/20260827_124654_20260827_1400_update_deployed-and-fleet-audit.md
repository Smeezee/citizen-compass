# Update — Corrected models deployed. And the same defect is in the old fleet.

**2026-08-27 14:00 · Code (background session)** — unit of work finished.

## Deployed

Version `bb6a95ad-3fed-4a91-9890-6abb57eb4384`. 20 files uploaded, 504
unchanged. Build green on every gate.

Verified rather than assumed: index 200 (428,135 bytes), `id="cc-kb"` present,
password gate up, stamp reads `testing 2026-08-27`, models serve
(Odin 2,642,136 / Pitbull 5,092,532 / Tyilui 18,021,240 bytes), and
`_verify_deployed_links.mjs` SWEEP CLEAN with its canary proving the sweep can
report.

**All 19 imported ships are now the size their own record says, live.**

## THE FINDING — the scale defect was never only in the imports

While the build ran I put the same measurement over the **219 models that were
already here**, which nothing had ever checked. Result in
`data-layer/derived/model-availability/fleet_scale_audit.json`.

**178 of 219 are fine** (within 15%). Median ratio 0.983. So the fleet is
mostly right and the published figures are a sound yardstick.

**8 are wrong by about 100x — the same defect the imports had:**

    Orion            1.70 m   published 340.00 m    x199 too small
    San'tok.yai      0.23 m   published  24.00 m    x104
    Crucible         0.89 m   published  90.00 m    x101
    Pioneer          2.47 m   published 247.00 m    x100
    Starlancer TAC   0.84 m   published  83.00 m     x99
    Starlancer MAX   1.01 m   published  83.00 m     x82
    Endeavor        17.11 m   published 200.00 m     x12
    Avenger Stalker  1.91 m   published  20.00 m     x11

**4 more are wrong by about 2.5x:** Polaris 62.62 m against 166, Vulture 12.87
against 33, Nautilus 52.96 against 125, Mule 4.20 against 8.75.

**Those 12 I would fix**, with the tool that just fixed the 19 — it needs only a
different ship list, and the same check would prove it.

## Two tiers I would NOT touch without a human looking

**25 ships at 0.60-0.85**, and the numbers cluster rather than scatter: every
Cyclone variant at exactly 1.5x, every Mk I Hornet at 1.25x, every Vanguard at
1.2x. A clean family pattern like that is as likely to be the published figure
measuring something the model does not include - landing gear, antennas, a
deployed component - as it is to be the model. Guessing here would introduce
errors into ships that are currently right.

**4 ships measure LARGER than published**, and at least two of them look like
the PUBLISHED figure is the wrong one: Eclipse 36.92 m against a published
24.50, Defender 37.79 against 24.50. The Eclipse really is about 36 m. Vulcan
at 97.27 against 38.50 is the odd one and is worth a look on its own.

**This is why the rule is not "make every ratio 1.000".** A ratio away from 1
means the model and the published figure disagree; it does not say which is
wrong. For the 12 above it is not in doubt - a 340 m capital ship rendering at
1.7 m is not a documentation problem.

## Also worth recording

The existing fleet's convention is confirmed by measurement rather than by
assumption: **192 of 219 models have their longest axis on Z**, 22 on X, 5 on Y.
The imported models do not follow it. That is why the scale rule was written
axis-independently, and it is a separate question from scale - not started.

Nothing committed.
