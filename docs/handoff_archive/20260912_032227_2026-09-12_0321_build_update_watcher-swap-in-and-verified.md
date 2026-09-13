# Build update - the watcher swap is in and verified; the three mail repairs are live

**Code (Build), 2026-09-12. The clock read 03:20:14 CDT just before this was written.** I am timing how long this file takes to route.

## The swap

- **Installed:** `inbox_watcher.exe` is now sha256 1dca1fde..., the three-repair build.
- **Rollback:** `_to_delete/inbox_watcher.exe.rollback-20260912` (f9d983b2...).
- **Running:** one watcher, PID 45220, since 03:17:02.

## The live test

Five test letters, all correct:

1. A bare close was refused.
2. A proper close was filed.
3. A signed To: was delivered.
4. A signed From: came home with its signature kept.
5. An identical re-drop was cleared.

All test letters are closed out to `_to_delete/`.

## Checks

- **The mail check, run alone:** PASS.
- **The handoff size** is unchanged across the swap.

## My defects on the way

- **Two aborted attempts,** both harmless and both caused by my own PowerShell: an alias clash, then case-insensitive variable names.
- **Test drafts left under `_needs_review/`** turned the mail check red until I moved them.

## Reported

To Owner. Stopped there, per STEP A.
