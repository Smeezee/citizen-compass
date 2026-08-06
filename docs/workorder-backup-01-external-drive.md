# WORK ORDER — back everything up to the external drive

    id       WO-BACKUP-01
    from     C2, 2026-08-05
    for      Sleven, with Claude Code
    why      ".env - three secrets, one machine, no backup" is on record as the
             largest single risk in the project. This closes it.

**Machine is up in Minnesota. WD MyBook attached. This is the first real chance
to close a risk that has been open since the project started.**

---

## 1. GOOD NEWS — the script already exists and it is thorough

`Backup-CitizenCompass.ps1` — 22,228 bytes, in the repo root. **Do not write a
new one.** Read from source, it already:

- takes `-BackupRoot` (default `C:\cc-backup`) and `-MirrorRoot`
  (default `E:\cc-backup`)
- checks free space on both before starting
- records the git `HEAD` SHA into the backup
- runs `git fsck`, and correctly judges it by **exit code** rather than by
  stderr — git writes "is okay" to stderr on success
- copies the working tree with `robocopy /E`, **deliberately not `/MIR`**, so
  nothing at the destination is ever deleted
- **restores the database into a throwaway copy and counts ships against an
  expected number** — that is a proven restore, not a hopeful one
- mirrors to the second device

**Two prior runs exist**: `C:\cc-backup\20260730-231753` and `20260730-233853`
(502.3 MB, 598 files hash-verified on the good run). **The other run failed with
exit code 1 and was never diagnosed.** See §5.

---

## 2. THE ONE DECISION — the exclusions were written for a small disk

The script currently skips six things:

    venv                          rebuild from requirements.txt
    sc-ships                      "re-downloadable from Hugging Face"
    __pycache__ / .cache          build artifacts
    node_modules                  rebuildable
    data-layer\external-sources   "raw public snapshots, re-pullable"

**Two of those six are wrong on a multi-terabyte external drive, and one of them
is wrong on principle.**

**`data-layer\external-sources` is NOT re-pullable in the sense that matters.**
Re-pulling UEX today gives you *today's* prices. It does not give you the prices
as they stood on 2026-08-01. Source 2 is a legacy 2022 capture that may not exist
upstream forever. **Those sealed snapshots are the beginning of the historical
record** — the same argument as the append-only ruling. Losing them loses time,
and time cannot be re-downloaded.

**`sc-ships` — 243 ship folders, 469 GLB files, ~7.3 GB** — is called
re-downloadable, but the Hugging Face pack's redistribution rights are already on
record as unestablished. If it disappears upstream, so does the 3D viewer.

**Recommendation: on the MyBook, exclude nothing but `venv`, `__pycache__`,
`.cache` and `node_modules`.** Those four are genuinely rebuildable in minutes.
The exclusions were a space compromise on a small disk and the disk is no longer
small.

**Keep the existing exclusions for the `C:` copy.** That one is for speed.

---

## 3. `.env` — the actual risk, and it needs a deliberate choice

Three secrets. Gitignored, so **not in GitHub**. One machine. No copy anywhere.
**If that drive dies, the database URL, the UEX token and the Cloudflare token
are gone.**

It sits in the repo root, so a full working-tree copy picks it up automatically.

**But think about it before shrugging.** A plaintext secrets file on a drive
that is not yours, in a vehicle, moving between states, is a different risk from
the one you are closing.

**Three options, Sleven's call:**

- **Back it up as-is.** Simplest. Fine if the drive stays with you and the
  machine.
- **Back it up and rotate the two exposed tokens afterwards.** The UEX token was
  screenshotted and the Cloudflare token came over chat twice — **both need
  rotating regardless of backup.** After rotating, a backed-up copy of the old
  values is worthless to anyone.
- **Record the three values in a password manager and exclude `.env`.** Cleanest
  separation, one manual step.

**Do not let this decision stop the backup running tonight.** Run it, then decide.

---

## 4. WHAT MUST BE VERIFIED, NOT ASSUMED — hard rule 12

A backup that has never been restored is not a backup.

- **Assert the drive letter before running.** The order says "D:" and "WD
  MyBook" — **confirm which letter Windows actually assigned.** Get it wrong and
  the mirror step silently skips, because the script treats a missing mirror
  drive as non-fatal by design.
- **Assert free space exceeds the source size** before starting, not after.
- **Assert the database restore step actually ran and reported the ship count.**
  That is the only step that proves the dump is usable.
- **Assert `.env` is present in the backup** — or deliberately absent, per §3.
  Not "probably there."
- **Assert file counts match** between `C:\cc-backup\<stamp>` and the mirror.
- **Assert `git fsck` returned 0**, and read the exit code rather than the text.
- **Assert the sealed snapshots arrived** if §2 is adopted — spot-check
  `20260801T235530Z` for its 114 files and `20260801T204744Z` for `blueprints.json`.

---

## 5. THE FAILED RUN — diagnose it before trusting the next one

`20260730-233853` **failed with exit code 1 and nobody found out why.**

**Do not run the new backup and declare success without knowing what broke last
time.** If it was a locked file, a permission, or a full disk, it will happen
again on a bigger copy. The log from that run should still be in
`C:\cc-backup\20260730-233853\`.

**Ten minutes on that log is worth more than the backup itself**, because it is
the difference between a backup that works and one that appears to.

---

## 6. ONE THING THAT MUST NOT HAPPEN

**Do not `git add -A` on this repo.** C1's note of 2026-08-02: **50 files are
pure CRLF line-ending churn** — 191,317 insertions against 191,317 deletions,
identical counts, 11 of 12 sampled files byte-identical after stripping CR.

`releases/latest.html` and `static/preview.html` are in that list. **Those are
the live site.**

The backup captures the working tree as-is, which is correct and harmless.
**Committing it is not.** Settle the line endings first, separately.

---

## 7. AFTER IT RUNS — what this unblocks

`claude/CURRENT-STATE.md` records Stage 3 as **blocked** on "what serves as the
second offline or offsite archive copy," with the note that a removable drive in
the same dwelling fails the test.

**That is now partly answered and partly not.** The MyBook is a second physical
device, which is a real improvement over one disk. It is **not** offsite — it
travels with the machine. **Say so plainly in the record rather than marking
Stage 3 closed.**

**What already exists elsewhere:** the code is on GitHub, and the built site is
on Cloudflare. **What exists nowhere else:** `.env`, the sealed snapshots, the
database, `sc-ships`, and the models. **That list is what this backup is
actually for.**

---

## 8. COMMANDS

Run in order. **Stop at the first one that fails.**

Confirm the drive letter first:

```powershell
Get-Volume | Select-Object DriveLetter, FileSystemLabel, @{n='FreeGB';e={[math]::Round($_.SizeRemaining/1GB,1)}}, @{n='SizeGB';e={[math]::Round($_.Size/1GB,1)}}
```

Read the log from the run that failed:

```powershell
Get-ChildItem C:\cc-backup\20260730-233853\ -Recurse -Filter *.log | Get-Content | Select-String -Pattern 'FAIL|ERROR|denied|locked' -Context 2,2
```

Check what the backup will actually cost, in size:

```powershell
Get-ChildItem C:\Users\david\citizen-compass -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum | ForEach-Object { '{0:N1} GB' -f ($_.Sum/1GB) }
```

Run the backup, mirroring to the external drive — replace `D:` if §8 step 1 says otherwise:

```powershell
cd C:\Users\david\citizen-compass; .\Backup-CitizenCompass.ps1 -MirrorRoot 'D:\cc-backup'
```

Verify the two copies match:

```powershell
$s = Get-ChildItem C:\cc-backup -Recurse -File | Measure-Object; $d = Get-ChildItem D:\cc-backup -Recurse -File | Measure-Object; "C: $($s.Count) files / D: $($d.Count) files"
```

Confirm `.env` made it:

```powershell
Get-ChildItem D:\cc-backup -Recurse -Filter '.env' -Force | Select-Object FullName, Length, LastWriteTime
```

---

## 9. NOT VERIFIED

- **The drive letter.** Only the three Cowork-connected folders are visible from
  here; no drive list is reachable.
- **Total repo size.** A `du` across the tree timed out through the mount.
  **Measure it before starting** — `sc-ships` alone is ~7.3 GB and `models`
  is separate.
- **Whether the MyBook is formatted NTFS.** If it is exFAT, robocopy will run but
  permissions and long paths behave differently. **Check before, not after.**
- **What broke the 2026-07-30 run.** §5.
- **Whether the script's expected ship count is still correct.** It asserts a
  number; the database has changed since July.
