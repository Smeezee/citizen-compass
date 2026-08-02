# UPDATE — Pre-departure backup v2 completed, one warning worth investigating (2026-07-30)

Ran `Backup-CitizenCompass.ps1` v2 `-NonInteractive`, script untouched per instruction. v2's fix for the v1 PowerShell native-stderr bug worked - full run completed, exit 0, all 7 steps ran (git bundle, working-tree copy, Postgres dump, restore test, Blender addon capture, SHA-256 manifest, E: mirror).

## Result: 1 WARN, 0 FAIL

**Backup folder:** `C:\cc-backup\20260730-233853`
**E: copy:** `E:\cc-backup\20260730-233853` (all 598 files hash-verified against SHA256SUMS.txt)
**Total size:** 502.3 MB

**The one warning, flagged by the script itself, not investigated further this round:**
`Restore returned 232 ships, expected 254 - investigate before trusting this dump`

Worth noting for whoever looks at this next: every DB check run this session (checker framework, registry-sync comparison, rescale script's chassis cross-reference) has consistently read 232 ships from the live Postgres DB - so 232 looks like it may be the actual current count, and 254 may be a stale expected-value baseline hardcoded in the backup script rather than a sign the dump itself is bad. Not confirmed either way - flagging per the script's own warning rather than assuming.

**CC Hardpoint Tool:** confirmed captured - `C:\cc-backup\20260730-233853\blender-addons\4.5\citizen_compass_hardpoints.py` (4 addon files total captured from the live Blender 4.5 install).

**Still to do by hand (per the script's own output, not done by me):**
1. Copy the backup folder to the laptop being taken.
2. Upload to cloud storage.
3. Drop the throwaway restore-test database when satisfied: `dropdb -h 127.0.0.1 -p 5432 -U postgres cc_restore_test_20260730_233853` (left in place on purpose, script never deletes).

## Script not edited, not touched. Nothing committed/pushed. Full verbatim output already given to the user directly in-conversation.
