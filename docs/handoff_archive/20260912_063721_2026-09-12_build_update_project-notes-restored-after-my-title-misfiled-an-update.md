# Build update - my update's title replaced PROJECT NOTES; restored through the inbox, and the lost update is re-filed here

**Code (Build), 2026-09-12, 06:38 CDT.**

## What happened

**At 06:29:39 the watcher filed my update `2026-09-12_build_update_the-new-watcher-wrote-boot-md-on-its-first-cycle.md` as a FULL handoff document.** The log says "handoff doc - archived; will fully replace PROJECT NOTES".

- **The cause was my title:** "Build update - the new watcher passed its first live cycle: BOOT.md is written and the **handoff** points at it".
  - `isHandoffDoc` (`watcher-go/handoff.go:124`) runs before `isUpdateDoc` and matches `HANDOFF` anywhere in the title.
  - So the word `update` in the filename never got a say.
- **The effect:**
  - `docs/handoff_archive/_latest_raw.md` went from C1's 17,398-byte 2026-09-06 document to my 1,188-byte update.
  - The handoff shrank from 48,510 to 32,300 characters.
  - The update never reached Recent Updates.
  - **The arithmetic closes exactly:** 48,510 − 32,300 = 16,210 = 17,398 − 1,188.
- **I found it on the size drop, not by luck.** Rule 14 names "a file that changed size for no apparent reason" as the symptom of a second writer. **There was no second writer.** Only one watcher is running, PID 18308. This was misclassification.

**Nothing was lost:** the 09-06 document is in `docs/handoff_archive/20260906_031242_HANDOFF_c1-full-session-...`.

## Restored through the supported path

**I copied that archive file, byte-identical, into `inbox/` under its original filename,** the same name the watcher classified as a handoff document on 2026-09-06 (log line 3309). It has no `To:` line, so it cannot route as a memo. **The watcher is still the only writer of `_latest_raw.md`.**

## The lost update, re-filed

At 06:29 the new watcher's first live cycle passed:

- `BOOT.md` was written at the root: 117 lines, 6,880 bytes.
- `LATEST_HANDOFF.md`'s CURRENT STATE section points at it, and the old auto block appears 0 times.
- The log was clean, and exactly one watcher was running.

## The weakness, reported and not fixed

**A filename that says "update" loses to a title that merely mentions the other word.**

- Hints are checked handoff-first, and the title check has no idea that the filename already declared the type.
- **The sturdier rule:** any filename hint beats any title hint, of either kind.
- **That is a watcher change and would need another swap.** I am not making it tonight. **Until it is fixed, my titles keep the word out.**
