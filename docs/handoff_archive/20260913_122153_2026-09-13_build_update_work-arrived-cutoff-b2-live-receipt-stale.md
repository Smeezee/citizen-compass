# Build update - work arrived: CUTOFF, B2 live filing, and why the uncommitted receipt is stale

**Code (Build), 2026-09-13. Clock read at 12:21:17.** Sleven's message: "go".

**MY DEFECT FIRST (rule 24).** At 11:34 I told Sleven `correspondence/open/` was empty. I listed files at its top level only; every letter sits in a desk subfolder. The Build tray held two new letters at the time I said that. **A mail check is a tray listing of `correspondence/open/build/`, every time.**

**Two letters from Architecture (Grok covering C1), each with a byte-identical `__2026...` twin (hash-compared):**
- `2026-09-13_memo_build_three-architecture-rulings-b2-enable-cadence-readme-finish-brain.md` (12:11)
- `2026-09-13_memo_build_build-now-b2-live-cutoff-boot-uncommitted.md` (12:18, the newer, and it supersedes the older's sitting ask: the brain sources are committed and pushed as `4510568`; main is 0/0 with origin)

**Checked before acting, not taken:**
- **The watcher swap is done.** The running `inbox_watcher.exe` (PID 27080, started 12:14:13) hashes `f7166705...`, the candidate.
- **BOOT.md DOES carry `## WHAT IS UNCOMMITTED`** at 12:19:44. The letter says it does not. It prints the 09:29:15 receipt as STALE, so **the real defect is that the live beat is not refreshing `logs/uncommitted.json`.** Tracing that.
- **`correspondence/README.md` declares `Owner-action:`** (its `## Owner-action` section).

**Order I am taking:**
1. The stale receipt: find the one-line cause, fix it if it is Build's.
2. `CUTOFF` on `_verify_owner_asks.py`. **The ordered value, 2026-09-12, is one the control is built to refuse** (`CUTOFF TOO EARLY` for on-or-before 09-12). Reading its reasoning before setting anything.
3. B2 real filing and the post-sweep hook, then one live pass with counts per desk.
4. After that, the B3 proposal.
