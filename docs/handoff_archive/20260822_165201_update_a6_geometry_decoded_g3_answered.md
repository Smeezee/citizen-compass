# Update - the last sweep failure answered rather than excused

Sweep after the drift fix: **45 ok, 1 failed, 2 skipped, 0 NOT RUN, 147s.**
The one remaining failure was `_verify_g3_matcher_delta.py` exiting 2 - "NOT
PERFORMED, CC_GEO_DIR is not set".

That is the correct refusal, and the sweep counting it against the run is
correct too. But I8 set the precedent on 2026-08-21: answered, not excused.
Same here.

## Geometry decoded

235 models through `testing/_src/decode_glb_points.js`, using the DRACO decoder
already vendored in `testing/_src/vendor/three/` - the same decoder, on the same
files, that a visitor's browser runs. Nothing downloaded, nothing new executed
(rule 7).

    data-layer/derived/hull-geometry/   235 files, 345 MB, exit 0

Gitignored, with the reason written into `.gitignore` next to the entry: it is
regenerable on demand from models that are themselves gitignored, it is an
input to the matcher controls via `CC_GEO_DIR`, and it is not source. Measured
one model first (1.6 MB, 0.3s) before committing to the other 234.

## The control, run for real

`CC_GEO_DIR=data-layer/derived/hull-geometry` -> **exit 0, 8 of 8.**

    bucket            pass 1   both   delta
    placed                33     35      +2
    skipped               27     25      -2
    rule                  20     22      +2
    refused                8      8      +0

Two ships gained, and it still names them: **Ares_Inferno and Ares_Ion**, each
placed with a real mount count and a measured shape error rather than waved
through. Nothing lost - the second pass cannot take a ship away from the first.
The 25 still-refused ships are still refused, by name. Same answer I8 got,
which is the point of holding geometry constant.

Full sweep re-running with `CC_GEO_DIR` set. Expecting 46 ok, 0 failed.

Still not deployed to testing. That half of A6 is outward-facing and waits on
Sleven.
