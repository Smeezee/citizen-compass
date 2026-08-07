# Update — received: run the backup to the WD MyBook on D:

**When:** 2026-08-05

Logging on arrival per hard rule 13. Jobs 3 and 4 of the previous batch (the
unreleased-content filter and the FixedReward census) are **not started** and
are now queued behind this.

Six steps, **stop at the first failure**:

1. Confirm D: is the MyBook — filesystem (NTFS vs exFAT changes robocopy long-path
   handling) and free space.
2. Diagnose the 2026-07-30 backup that exited 1 and was never explained. Do not
   run a bigger one without knowing why.
3. Measure the repo size.
4. Add `-FullMirror` to `Backup-CitizenCompass.ps1`. When set, the **mirror**
   copy excludes only the four genuinely rebuildable things (venv, `__pycache__`,
   `.cache`, `node_modules`). `sc-ships` (~7.3 GB, redistribution rights on
   record as unestablished) and `data-layer\external-sources` (the sealed
   snapshots — re-pulling UEX gives *today's* prices, not 1 August's) go **in**.
   The C: copy keeps existing exclusions for speed. **Defaults unchanged.**
5. Run it against `D:\cc-backup` with `-FullMirror`.
6. Verify — exit 0 is not proof. Five explicit checks: `git fsck` **exit code**
   (not its text — git writes "is okay" to stderr on success), a database
   restore reporting an actual ship count, file counts C: vs D:, `.env` present
   in the mirror, and the sealed snapshots spot-checked.

**A skipped mirror step is a FAILURE, not a warning.** The script currently
treats a missing mirror drive as non-fatal; if that fires I am to say so loudly.

`.env` is included deliberately — Sleven's call, back it up then rotate. Noting
that this compounds the standing exposure: the UEX token in that file was
exposed in a screenshot and still has not been rotated, and it will now exist on
an external drive as well.

**Next:** step 1.
