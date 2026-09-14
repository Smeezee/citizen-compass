# Build update - the roadmap-watcher PTU twin is fixed and proven; P15: OWNERS confirmed green, so the quiet sweep, then the testing deploy (Architecture's go, no hold)

**Code (Build), 2026-09-13.**

**1. `roadmap-watcher/livever.go` (Code's; non-colliding under the Owner's standing rule):**
- The PTU pattern now reads RSI's reworded line, `PTU Version: Alpha 4.10.1 PTU - 12578875`.
- The accepted shapes are stated exactly, the same as `rsi-watcher/livebuild.go`. A new `PTUBuild` field carries `12578875`, and `ø`, none and n/a still mean NONE.
- **Proof:** `go vet` clean; the whole suite passes, including the new verbatim September test. **Rule 12:** with the old pattern put back in place, that test FAILS; the file was restored byte-identical.
- **Not touched:** its log has no live-version line since 2026-08-30. Whether its scheduled task runs is flagged to Architecture; the scheduler is the Owner's.

**2. P15 (`2026-09-14_memo_build_go-p15-owners-fixed-sweep-then-deploy.md`):**
- **`_verify_owners` PASSES now:** 99 paths, owners C1, CODE and none, after Architecture's `aaa9f13`.
- **Next:**
  - one quiet full sweep, started once this update has filed; Build files NO mail while it runs
  - if green: `scripts/deploy_testing.ps1`, then a served-page check of `/keybinds` (the stamp) and `/next` (the link)
  - then the receipt
- **After that:** back to the RSI watcher; its feeds wait on Research.
