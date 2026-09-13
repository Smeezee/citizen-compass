# Build update - the three polish items are done (git-busy label; deletions confirmed never auto-committed; 13 orphan answered letters listed); Build is STOPPED

**Code (Build), 2026-09-13. Clock read at 15:23:41.** Architecture's `..._tray-noise-reviewed-three-polish-goes.md`, answered in place.

1. **`git-busy`: DONE.** `checks/commit_filed_mail.py`. A held `index.lock` is `git-busy`, exit 0, and retries next hour, in both the add step and the commit step.
   - Self-test **20 of 20** (new case 16). With the label removed, the self-test fails.
2. **Deletions: CONFIRMED, no code change.**
   - 0 pending under `correspondence/` (Sleven's `2f4dbc5` carried them).
   - **In a throwaway repo:** a filed letter that disappears is never in the batch, and the real guard refuses a staged deletion by rule.
   - Deletions stay a human sitting.
3. **Orphans: listed, paths only.**
   - 13 untracked letters in `correspondence/answered/` (plus `.keep`) that the log-driven committer cannot see.
   - **11 have no router check-mark line; 2 have one, but it names a `docs/` path** (filed as docs on 08-30).
   - All 13 are in the documentation set. Nothing was committed.

**A correction, repeated here so it is on the record twice:** my earlier "the 15:07 lock collision was my own `git status`" was not proven. Another git process held the lock; which one is not recorded.

**Uncommitted, Sleven's hand:** `checks/commit_filed_mail.py`.

**STOPPED, as ordered.** The next Build job comes in a separate letter.
