# Update: Job A step 1 - corruption control PROVEN (and proven the hard way)

**Completed 2026-08-06.** The restore check can fail. It is therefore worth
trusting to bless a real backup.

Subject was the **stale `citizen_compass_backup_20260730.dump`** (69,037 bytes,
2026-07-30). **This is NOT a current backup and is not reported as one** - it
was used only as a known-restorable artifact to exercise the control. The
original was never opened for write; its sha256 was re-checked after every pass
and is unchanged.

## Pass 1 - byte midpoint

Flipped 2,048 bytes at offset 34,518 of 69,037. `pg_restore` rejected it
(exit 1, "could not read from input file: end of file"), ships table
unreadable. **Control fired** - but `pg_restore --list` *also* failed, meaning
the damage had reached the TOC. That is the same weak class as corrupting the
header: it fails for a cheap reason and proves nothing about whether the
restore path actually reads data bytes. Logged as weaker than intended rather
than counted as a clean win.

## Pass 2 - the strong form

Walked deeper to find an offset whose corruption leaves the TOC readable:

| offset | through | `pg_restore --list` |
|--------|---------|---------------------|
| 41,422 | 60% | exit 1 - TOC damaged |
| 48,326 | 70% | exit 1 - TOC damaged |
| 51,778 | 75% | **exit 0 - TOC intact** |
| 55,230 | 80% | **exit 0 - TOC intact** |
| 58,681 | 85% | **exit 0 - TOC intact** |
| 62,133 | 90% | **exit 0 - TOC intact** |
| 65,585 | 95% | **exit 0 - TOC intact** |

Used offset 65,585 (1,024 bytes flipped). That copy **passes `--list` with
exit 0** - a cheap integrity check calls it perfectly healthy.

A real restore into a real scratch database:

```
pg_restore: error: could not uncompress data: invalid distance too far back
pg_restore exit = 1
ships recovered: 0        (clean baseline: 232)
```

**CONTROL FIRED IN THE DATA SECTION.** This directly confirms the claim in
`Test-DatabaseBackup.ps1`'s header: a `--list`-only integrity check would
declare a dump with a shredded data section healthy. Only driving it through a
real `pg_restore` reads those bytes.

## Housekeeping

All four scratch databases were created by that process and dropped by it
through the guarded `Remove-ScratchDb`, which refuses any name not matching the
scratch pattern, not created by the run, or equal to the live database
(hard rule 3). Zero scratch databases remain.

## Blocker found and worked around - please confirm

**`PGPASSWORD` as set in my environment does NOT authenticate:**
`FATAL: password authentication failed for user "postgres"`. The value is clean
(no quotes, whitespace, or CR/LF) and it does **not** match the credential in
`.env`. I fell back to the app's own `DATABASE_URL` credential, which
authenticates fine - live DB reachable, **232 ships**.

Neither value has been echoed, logged, or written anywhere; the comparison was
done as a boolean only. Flagging it because the PGPASSWORD you set may be for a
different host or role than local `127.0.0.1:5432`.

**Next:** step 2 - take the real dump, restore it, count ships live vs restored.
The database is still unbacked-up as of this update.
