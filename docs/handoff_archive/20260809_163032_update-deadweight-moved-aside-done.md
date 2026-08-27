# Update — dead weight moved aside, ~1.03 GB, all verified

Sleven approved all three groups from the dry run. Everything below was **moved,
never deleted**, into `_to_delete/collector_deadweight_20260809/` per rule 1.

## Moved — 97 files, 1028 MB

- **Group A**, `zips/` — `citizen-collector-20260808.zip`, `-2.zip`, `-3.zip` (524.06 MB)
- **Group B**, `webview2-runtime/` — 80 files (502.06 MB)
- **Group C**, `captures/` — the 7 frames `…_0001`–`…_0007` plus their 7 JSON
  sidecars, 14 files (1.64 MB)

## Verified on both sides, not assumed

Destination: 3 zips, 80 runtime files, 14 frames, 1028 MB total — matches the
manifest exactly.

Still present where they belong:

- `citizen-collector-0.2.0.zip` — the sendable package
- `WEBVIEW2_RUNTIME_PROVENANCE.md` — untouched, as stated in the dry run. It is
  the provenance record for third-party redistributable code and rule 8 puts it
  out of my reach regardless of where the runtime folder went.
- `captures/` down to 282 files, exactly 296 − 14
- `citizen-collector/webview2-runtime/` confirmed gone from source

## Post-cleanup state

`go build` clean. Selftest: **377 pass**, exit 1 on the two `sent-rows` failures
that belong to the other session's 15:35 work and were already failing before
this cleanup — unchanged by it, and still not mine to fix.

The staleness flake did not fire on this run.

## Consequence to remember

`make-release.ps1` will now report `no webview2-runtime folder here, so no
with-runtime package` instead of building one. That was in the dry run Sleven
approved and matches the 08-08 ruling that dropped the bundled browser. If a
with-runtime package is ever wanted again, the runtime is in `_to_delete/`, not
gone.
