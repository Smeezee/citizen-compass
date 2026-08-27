# Update — new session picks up the collector, 2026-08-08 19:0x

Received the 08-08→08-09 handoff. Starting on its open item #1: re-run
`--selftest` after the 14 fixes, which the previous session made but never
re-ran.

**Immediately flagged, before doing anything else:** the handoff names two
documents as authoritative over CURRENT-STATE.md —

- `claude/RULING_collector-drops-the-bundled-browser-2026-08-08.md`
- `claude/FINDING_selftest-first-run-2026-08-08.md`

**Neither exists.** There is no `claude/` directory in this repo, and neither
filename appears anywhere under `docs/` or elsewhere in the tree. The reasoning
behind the browser-fallback design change and the full selftest finding are
therefore currently unrecorded — only this handoff describes them. Reporting,
not reconstructing.

Also noted: `gh` is not on PATH, so open item #2 (publish the 0.2.0 release via
`make-release.ps1 -Publish -Announce`) is blocked until it is installed.

Next: rebuild and run the full selftest, then report the tail.
