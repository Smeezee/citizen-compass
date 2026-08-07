# Update: Job A COMPLETE - the database is backed up, restored, and mirrored

**Completed 2026-08-06.** The gap is closed. There are now **three copies of
the data** (C:, D:, E:), and the dump has been proven restorable by actually
restoring it.

## Step 2 - the real dump

```
dump           : C:\cc-backup\20260806-172223\citizen_compass-20260806-172223.dump
dump size      : 175,705 bytes (0.17 MB)
ships LIVE     : 232
ships RESTORED : 232      <- restored into a scratch database and counted
```

These are two separately measured numbers, not one number printed twice. The
live count came from `citizen_compass`; the restored count came from
`cc_restore_test_20260806_172223` after a real `pg_restore`.

The harness's own negative control also fired on the real dump: a corrupted
copy was rejected (exit 1) and yielded 0 ships, not 232.

Both scratch databases were created and dropped by that run.

## Step 3 - both mirrors, verified per file

`Verify-MirrorTree.ps1` - the verifier that caught the external-sources
failure - run against each mirror with the **destination enumerated from disk**,
not from any manifest, log, or the copy's own file list:

- **D:** POSITIVE control passed; all 1 expected file present with matching
  byte size. VERIFY PASSED (exit 0).
- **E:** POSITIVE control passed; all 1 expected file present with matching
  byte size. VERIFY PASSED (exit 0).

Its NEGATIVE control reported **NOT PERFORMED** on both, honestly - a
single-file backup directory contains no excluded file to test with. Stated,
not glossed as a pass.

Independent re-hash from disk after the fact, all three locations:

```
C:\cc-backup   175,705 B  136249D1EC40948A576B3F6DED263CD0F0960BBC9E27B1C24971465079D5689D
D:\cc-backup   175,705 B  136249D1EC40948A576B3F6DED263CD0F0960BBC9E27B1C24971465079D5689D
E:\cc-backup   175,705 B  136249D1EC40948A576B3F6DED263CD0F0960BBC9E27B1C24971465079D5689D
```

Byte-identical on all three.

## The verifier was itself tested against known-bad input (hard rule 12)

A verifier nobody has seen fail is an untested gate. Fed two known-bad
destinations on scratch copies:

- **truncated file** (present, so a file-COUNT check passes - the exact
  2026-08-05 failure signature): caught, `a.dump source 175,705 B -> dest
  1,000 B`, **exit 1**.
- **missing file**: caught, `c.txt (10 B at source)`, **exit 1**.

Both failed as required, so the two passes above mean something.

## FOUND - not acted on: four orphaned scratch databases

These are left over from **earlier** runs, not from tonight:

```
cc_restore_test_20260730_233853
cc_restore_test_20260801_144501
cc_restore_test_20260801_203049
cc_restore_test_20260805_205238
```

**I did not drop them.** Hard rule 3 forbids `DROP DATABASE` against a database
this process did not create, and this process did not create any of these.
They are harmless but they hold stale copies of ship data and will accumulate.
Dropping them is Sleven's call.

Worth noting the earlier runs' guarded cleanup did not remove them - probably
because those runs exited before step 4. Cheap fix available if wanted: a
startup sweep that drops only names matching the scratch pattern, but that
would itself be dropping databases the process did not create, so it needs an
explicit decision rather than a quiet addition.

## Still outstanding: PGPASSWORD does not authenticate

The `PGPASSWORD` set in my environment returns
`FATAL: password authentication failed for user "postgres"` against
`127.0.0.1:5432`. The value is clean (no quotes/whitespace/CR/LF) and does not
match `.env`. All work above used the app's own `DATABASE_URL` credential.
No password was echoed, logged, or written anywhere.

`citizen_compass_backup_20260730.dump` in the repo root remains the **stale**
2026-07-30 file and is still not a current backup - the current one is the
`C:\cc-backup\20260806-172223\` dump above.

**Next:** Job B - grouping the uncommitted Jobs 3-5 and collector work into
logical commits. Nothing will be pushed without explicit confirmation.
