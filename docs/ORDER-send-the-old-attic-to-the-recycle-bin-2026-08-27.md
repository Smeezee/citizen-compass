# ORDER — send 3.1 GB of `_to_delete/` to the Recycle Bin. Sleven asked for it, I verified it, and I am holding back 5 GB on purpose.

**2026-08-27 21:25 local · C1** — Sleven: *"the stuff that's ready to be
deleted... verify that it's just old stuff we don't need anymore. Can you move
it to the recycling bin, and I'll take care of it."*

**Recycle Bin, not delete.** He empties it. Nothing here is unrecoverable.

## What I verified before proposing any of it

**1. Nothing in the repo READS from `_to_delete`.** Every reference is a script
writing INTO it — `fix_model_scale.py`, `scrub_sidecars.py`, `takedown.py` — or
a checker excluding it, `checks/file_checks.py`. It is write-only scaffolding.

**2. The three `*_source1_git` folders are redundant, and this is the one that
mattered.** They are the stripped `.git` of the scunpacked clones, 4.3 GB
between them. The only load-bearing thing in them is the commit subject that
names the build, and **`build_patch_diff.py` reads that from the manifest, not
from git** — `data-layer/external-source-manifests/<run>/01_scunpacked-data_manifest.json`,
under `git_metadata_captured_before_stripping`. Checked all three:

    20260801T204744Z   4.9.0-LIVE.12232306
    20260827T030607Z   4.9.0-LIVE.12344265
    20260827T225641Z   4.10.0-LIVE.12519617    <- your 4.10 pull

**The 4.10 diff work does not depend on those folders.** That is measured, not
assumed.

## THE SPLIT — and I am deliberately not giving you all of it

    TOTAL in _to_delete        8.17 GB   189 items
    SEND TO THE BIN            3.10 GB   157 items   dated before today
    HOLD                       5.07 GB    32 items   dated TODAY

**Why the hold.** Five of today's items are pre-change backups of work that went
in today and has not been through a full day of use:

    pre_scale_fix_20260827T172853Z          1.68 GB
    20260827T030607Z_source1_git            1.40 GB
    20260827T225641Z_source1_git            1.39 GB
    pre_scale_fix_20260827T214809Z / 213542Z 0.58 GB
    pre_holo_regen / pre_overlay_regen / hardpoint-placement-stale

If anything from today needs backing out, those are the before-state. **Binning
a same-day backup to reclaim space is the trade this project should never
make.** Give it a few days; the 4.3 GB of git folders can go with the next
sweep once 4.10 has settled.

## The command

Recycle Bin rather than `Remove-Item`, which is permanent:

    Add-Type -AssemblyName Microsoft.VisualBasic
    $repo = "C:\Users\david\citizen-compass\_to_delete"
    $cut  = Get-Date "2026-08-27 00:00"
    Get-ChildItem -LiteralPath $repo -Force | Where-Object { $_.LastWriteTime -lt $cut } | ForEach-Object {
        if ($_.PSIsContainer) {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($_.FullName,'OnlyErrorDialogs','SendToRecycleBin')
        } else {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($_.FullName,'OnlyErrorDialogs','SendToRecycleBin')
        }
        Write-Host "recycled $($_.Name)"
    }

**Report the count and the freed space back.** If it does not move roughly 157
items and ~3.1 GB, stop and say so rather than re-running it with a wider date.

**Do not widen the cutoff.** The date is the safeguard, not a parameter.

— C1
