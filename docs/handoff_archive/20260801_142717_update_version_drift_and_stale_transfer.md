# Version drift in Cowork-built artifacts, and the cause — 2026-08-01

Caught by Sleven, who noticed the live site read v0.3.9 while a build he was looking at read v0.3.7.

## What was wrong

Every artifact built in the Cowork container was built from a **v0.3.7** copy of `releases/latest.html` that had been staged into that container on 2026-07-30 and never refreshed. Affected: the portable concept HTML, the intermediate web build, and `testing/_deploy/index.html` (the 344 MB shareable build).

**`testing/index.html` was never affected** — `build.py` runs on the Windows machine against the real `releases/latest.html`, so it tracked v0.3.9 correctly the whole time. The bug was confined to builds assembled in the Cowork container.

## Actual impact — small, but worth stating precisely

Diff between v0.3.7 and v0.3.9 is **23 lines**: the version string, the compiled date (2026-07-24 → 2026-07-30), and four font-size values in the patch banner. **No ship data differs.** What was shown to people was correct data under a stale label, not wrong information.

## Root cause — a stale-read in the file transfer layer, not a build bug

This is the part worth carrying forward.

Re-staging `C:\Users\david\citizen-compass\releases\latest.html` returned a result reporting `"bytes": 205362` — the correct current size. The file that actually landed in the container was **205,274 bytes, md5 `8c53fa72a4fe1f666e416b6f878f28d5`, v0.3.7** — the stale July 30 copy, still carrying its original timestamp.

So the transfer **reported the new file's metadata while delivering the old file's bytes.** A size check against the reported value would have passed. Only a checksum comparison caught it.

Confirmed by staging the same content from a *different* path (`testing/_tools/src_<ts>.html`, a fresh copy made on the machine): that arrived correctly at 205,362 bytes, md5 `0b8be95027992bf5f77cf9341b51f20e`, v0.3.9. The problem is per-path caching in the uploads directory, not the file itself.

**Rule going forward for any Cowork session:** checksum anything staged from the machine against a checksum computed *on* the machine before building on it. Do not trust reported byte counts, and do not trust that re-staging a path refreshes it. If a mismatch appears, copy to a new path on the machine and stage that instead.

This is the same shape as hard rule 12 — the transfer reported success while doing nothing, and the reported metadata was the thing that made it look fine.

## Fixed

All Cowork-built artifacts rebuilt from the current v0.3.9 source and re-verified in a headless browser: version string v0.3.9, compiled date 2026-07-30, 254 clickable ships, 228 carrying 3D models, 130% default text size, Carrack loading in 0.9s from its embedded Draco model, zero page errors.

`testing/_deploy/index.html` on the machine replaced with the corrected build. `testing/index.html` rebuilt from `releases/latest.html` to confirm it was already current — it was.

All four now read v0.3.9: `releases/latest.html`, `static/preview.html`, `testing/index.html`, `testing/_deploy/index.html`.

The temporary source copy used for the clean re-stage was moved to `_to_delete/`.
