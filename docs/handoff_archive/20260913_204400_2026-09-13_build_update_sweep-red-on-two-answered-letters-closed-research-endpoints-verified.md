# Build update - the 20:08 sweep was red on one control (two of Build's letters answered in place); Build closed both; Research's RSI endpoints are wired and verified from the watcher's own record

**Code (Build), 2026-09-13. Clock read at 20:42:21.**

**The sweep (20:08 to 20:41, trays quiet, no filings inside the window):**
- **132 passed, 1 failed:** `_verify_correspondence.py`
- **Fingerprint `fb3f7ca0...`,** unchanged: the payload is the P15 build.
- **The gate refused. No deploy.**

**The red:** two Build letters were answered IN PLACE and left in open trays:
- Architecture's answer on the P15 receipt (`open/architecture/`)
- Research's answer on the endpoint memo (`open/research/`)

**Build closed both,** as the asker: `Status: Closed` plus a `CLOSED:` record, dropped through `inbox/` to `answered/`. Rule 5 does not apply: 2 letters.

**Research's endpoints, CHECKED against the watcher's own record (not taken):**
- `rsi-watcher.exe -status`: all three sources are configured (known 25 / 18 / 12), last OK at 01:35Z, 0 failures.
- `logs/rsi-watcher.log`: comm-link 1 new, and the card `sc-brain/cig-firehose/comm-link/21315.json` is on the shelf.
- **`OWNERS.md` L199-200 claims `rsi-watcher/` and `setup_rsi_watcher_task.ps1`,** and `_verify_owners` PASSES.
- **The scheduled task stays unregistered,** as ordered: it is the Owner's word.

**Next:**
1. **one more quiet full sweep**
2. **if the gate passes, `scripts/deploy_testing.ps1` as its own visible step** (the auto-mode guard rightly refused chaining the deploy onto the sweep unseen), then the served-page check
3. the P15 receipt

**Uncommitted, needing Sleven's hand (code):**
- `rsi-watcher/*.go`, `go.mod`, `.gitignore`, `README.md`
- `setup_rsi_watcher_task.ps1`
- `roadmap-watcher/livever.go`, `roadmap-watcher/livever_test.go`
- the P15 set (listed in the P15 receipt)
