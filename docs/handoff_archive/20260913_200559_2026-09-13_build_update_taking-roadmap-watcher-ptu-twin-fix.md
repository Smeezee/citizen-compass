# Build update - taking the twin fix: roadmap-watcher/livever.go cannot read RSI's reworded PTU line (non-colliding, Code's own file)

**Code (Build), 2026-09-13.** Found while proving the RSI watcher. The live board now reads `PTU Version: Alpha 4.10.1 PTU - 12578875`. `roadmap-watcher/livever.go`'s PTU pattern accepts only a bare number or `ø`, so it reports "could not read the PTU version".

**Under the Owner's standing rule** (`claude/RULING_non-colliding-work-just-do-it-2026-09-14.md`): `roadmap-watcher/` is Code's in `OWNERS.md`, and the change touches no other desk's path.

**The change:**
- **the same stated exact shapes as `rsi-watcher/livebuild.go`:** an optional `Alpha `, the dotted version, an optional ` PTU`, and an optional ` - <build>`
- the build number is kept in a new `PTUBuild` field
- `ø`, none and n/a keep meaning NONE
- **a test on today's description, word for word,** and a mutation proving the test can fail

**Not touched:** whether roadmap-watcher's own scheduled task is running. Its log has no live-version line since 2026-08-30; that is flagged to Architecture, and the scheduler is the Owner's.
