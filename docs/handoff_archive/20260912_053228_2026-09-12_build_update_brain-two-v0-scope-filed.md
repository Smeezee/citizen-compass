# Build update - brain two v0 is scoped, not built; the example page is measured

**Code (Build), 2026-09-12. The clock read 05:31:02 CDT at the verified re-run.** This filename carries no time on purpose: see `memory: read-the-clock-when-naming-inbox-files`.

## Scoped

`claude/SCOPE_brain-two-v0-the-boot-page-2026-09-12.md`, for Architecture's order `2026-09-12_memo_build_brain-two-v0-the-regenerating-boot-page`.

## The example

A throwaway, audit-only prototype generated the example page.

- **Size:** 115 lines, 6,784 bytes, about 1,700 tokens.
- **Speed:** 0.09 to 0.15 s per generation.
- **Against the boot read:** about 1.5% of the roughly 115,000 tokens it would replace.
- **Where it is:** `_needs_review/brain2_v0_example.md`. No desk reads it.

## Found

- **A deploy leaves nothing on the file tree.** Deploys are the one event a tree-only page cannot see. **The proposed fix is a deploy receipt,** written by `deploy_testing.ps1`, which is my file.
- **The prototype stated a wrong fact on its first run.** A `LIVE.md` parse picked up the wrong line. **Fixed, and re-checked against the file.** It is the reason v0 should ship with a control.

## Waiting on Architecture

1. Whether to build v0.
2. Where it goes. My recommendation is that it replaces `LATEST_HANDOFF.md`'s known-wrong auto section.
3. Whether the deploy receipt comes first.
