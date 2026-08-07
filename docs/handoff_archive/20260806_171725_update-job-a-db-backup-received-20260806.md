# Update: Job A received - database backup (DB is currently UNBACKED UP)

**Received 2026-08-06.** Sleven flagged that the file trees are verified on both
mirrors but the Postgres dump was skipped and correctly recorded as a failure.
State right now: **two copies of the files, zero copies of the data.**

`citizen_compass_backup_20260730.dump` in the repo root (69,037 bytes, dated
2026-07-30) is **NOT a current backup** and will not be reported as one.

## What I am about to do

1. **Prove the control first**, using the stale dump as the test subject:
   copy it to scratch (never touch the original), restore the clean copy to a
   scratch database, then corrupt the copy by flipping bytes in the **middle**
   (not the header - a mangled header fails for the wrong reason), and confirm
   the restore **fails**. Drop the scratch database.
   Per Hard Rule 12: if a deliberately corrupted dump restores clean, the check
   cannot fail and is worthless. I stop and report rather than let it bless a
   real backup.
2. **Take the real dump** and verify it the same way - restore to scratch and
   **count the ships**, reporting live count and restored count as two separate
   numbers. Drop the scratch database.
3. **Copy to both mirrors** and verify per file with the same verifier that
   caught the external-sources failure, with the destination side **enumerated
   from disk, not from a manifest**.

Then Job B: group the uncommitted Jobs 3-5 / collector work into logical
commits, add by name only (no `git add -A`), and **wait for confirmation before
pushing**.

PGPASSWORD is in the environment for this session. It will not be echoed,
logged, or written anywhere.
