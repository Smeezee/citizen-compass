# Update — dead-weight cleanup: dry run done, STOPPED for a decision (rule 5)

Inventoried the disk items from the handoff (#5 and #6) and produced a
report-only manifest. **Nothing has been moved.** Rule 5 requires the list to be
seen first, so I stopped there.

Proposed destination for everything below: `_to_delete/collector_deadweight_20260809/`
— moved, never deleted, per rule 1.

## The manifest — 1027.77 MB across 97 files

**Group A — superseded packages, 524.06 MB, 3 files** (untracked)
`citizen-collector-20260808.zip` (258.54 MB), `-2.zip` (258.95 MB),
`-3.zip` (6.57 MB). All predate `citizen-collector-0.2.0.zip`, which stays.

**Group B — `webview2-runtime/`, 502.06 MB, 80 files** (untracked, gitignored)

**Group C — the 7 junk frames + their sidecars, 1.64 MB, 14 files**
`20260806T031239Z_0001` … `20260806T033006Z_0007`, all dated 2026-08-05.
Verified: no references to any of them outside `captures/`.

The handoff estimated ~750 MB; the real figure is ~1.03 GB.

## What Group B actually costs, because it is not inert

`webview2-runtime/` is still read by live code and by the release script:

- `ui.go:53` — `resolveBundledRuntime()`, and through it `webview2Available()`
- `make-release.ps1:244-247` — builds the with-runtime package from it

Moving it means **`make-release.ps1` stops producing a with-runtime package**
and reports `no webview2-runtime folder here…` instead. That is consistent with
the 08-08 ruling that dropped the bundled browser and the two-option button, and
the script handles the absence gracefully rather than failing — but it is a
behaviour change to the release path, not just a disk saving, so it is Sleven's
call and not mine.

On this machine nothing breaks: system WebView2 is present, so the collector
would simply use that instead of the bundled copy.

**`WEBVIEW2_RUNTIME_PROVENANCE.md` stays exactly where it is** regardless of
what happens to the runtime folder. It is the provenance record for third-party
redistributable code, and rule 8 puts that class of document off-limits to me.

## Verified the dry run was genuinely a no-op

Rule 12 applies to safety flags as much as to gates, so I checked from the
outside rather than trusting that "report-only" meant it: 4 zips still present,
80 runtime files, 296 capture files, and `_to_delete/collector_deadweight_20260809/`
was never created.

**Waiting on: which of Groups A / B / C to move.**
