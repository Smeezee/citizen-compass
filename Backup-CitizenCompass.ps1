<#
==============================================================================
 Backup-CitizenCompass.ps1
==============================================================================
 Pre-departure emergency backup for the Citizen Compass project.
 Written 2026-07-31 for the August 3 Minnesota departure.

 SAFETY GUARANTEE — this script contains no delete operation of any kind.
   * No Remove-Item, no del, no rmdir, no dropdb.
   * robocopy is called with /E (copy), never /MIR (mirror, which deletes).
   * The Postgres restore test creates a throwaway database and LEAVES it.
     Dropping it is a separate manual step, printed at the end, so that this
     script's "deletes nothing" guarantee is absolute rather than conditional.
   * The only writes are into the backup folder and the E: copy of it.
     The source repo is read only.

 WHAT IT CAPTURES
   1. Full git history including unpushed commits   -> .bundle file
   2. Full working-tree copy incl. UNCOMMITTED work -> repo\ folder
   3. Fresh Postgres dump                           -> .dump file
   4. Blender addons folder (the CC Hardpoint Tool) -> blender-addons\
   5. SHA-256 of everything                         -> SHA256SUMS.txt

 WHY BOTH 1 AND 2: git bundle only captures COMMITTED work. As of writing,
 the repo has 3 unpushed commits PLUS uncommitted work that the bundle alone
 would silently miss - the Stage 1 provenance manifests, models\done ships\
 (HPs.blend and hand-placed hardpoint JSON), and the Gladius / Constellation
 Aquila API pulls. The folder copy is what catches those.

 USAGE
   powershell -ExecutionPolicy Bypass -File .\Backup-CitizenCompass.ps1
==============================================================================
#>

[CmdletBinding()]
param(
    [string] $RepoPath   = 'C:\Users\david\citizen-compass',
    [string] $BackupRoot = 'C:\cc-backup',
    [string] $MirrorRoot = 'E:\cc-backup',
    [string] $DbName     = 'citizen_compass',
    [string] $DbUser     = 'postgres',
    [string] $DbHost     = '127.0.0.1',
    [int]    $DbPort     = 5432,
    [int]    $ExpectedShipCount = 254,
    [switch] $SkipMirror,
    [switch] $SkipDbTest,
    # Set this when running unattended (e.g. driven by Claude Code). It stops
    # the script prompting for a password on a console nobody is watching.
    # With it set, a missing PGPASSWORD skips the DB steps loudly instead of
    # hanging forever - the git bundle, folder copy and Blender addons still run.
    [switch] $NonInteractive
)

$ErrorActionPreference = 'Stop'
$script:Warnings = @()
$script:Failures = @()

# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------
function Write-Step   { param($m) Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok     { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Write-Warn   { param($m) Write-Host "  [WARN] $m" -ForegroundColor Yellow
                        $script:Warnings += $m }
function Write-Fail   { param($m) Write-Host "  [FAIL] $m" -ForegroundColor Red
                        $script:Failures += $m }
function Write-Info   { param($m) Write-Host "  $m" -ForegroundColor Gray }

function Test-Command {
    param([string]$Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

<#
 Invoke-Native — run an external .exe and capture BOTH streams as plain strings.

 WHY THIS EXISTS (bug fixed 2026-07-31):
 Windows PowerShell 5.1 turns every stderr line from a native executable into a
 NativeCommandError record when you capture it with 2>&1. Under
 $ErrorActionPreference = 'Stop' that becomes a TERMINATING error - even when the
 program succeeded and exited 0.

 This bit for real: `git bundle verify` writes its success message
 ("<file> is okay") to stderr, which is normal git behaviour. The first version of
 this script captured it with 2>&1 and killed itself on a PASSING verification,
 aborting the backup at step 1.

 Fix: drop to 'Continue' for the duration of the call so stderr lines stay ordinary
 strings, then restore the previous preference. Success is judged by $LASTEXITCODE
 ONLY - never by whether the program wrote to stderr.
#>
function Invoke-Native {
    param([Parameter(Mandatory)][scriptblock] $Command)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $Command 2>&1 | ForEach-Object { [string]$_ }
    }
    finally {
        $ErrorActionPreference = $prev
    }
}

Write-Host @"

  CITIZEN COMPASS - PRE-DEPARTURE BACKUP   [v2]
  This script reads and copies. It deletes nothing.
  v2 fixes the PowerShell 5.1 native-stderr bug that aborted v1 at step 1.

"@ -ForegroundColor White

# ==========================================================================
# PREFLIGHT - fail closed before writing anything
# ==========================================================================
Write-Step 'PREFLIGHT'

if (-not (Test-Path -LiteralPath $RepoPath)) {
    throw "Repo path not found: $RepoPath"
}
Write-Ok "Repo found: $RepoPath"

foreach ($tool in @('git','pg_dump','psql')) {
    if (Test-Command $tool) { Write-Ok "$tool available" }
    else                    { Write-Fail "$tool NOT on PATH" }
}
if ($script:Failures.Count -gt 0) {
    throw "Required tools missing. Fix PATH and re-run. Nothing was written."
}

# Timestamped backup folder so re-runs never overwrite an earlier backup.
$Stamp      = Get-Date -Format 'yyyyMMdd-HHmmss'
$BackupDir  = Join-Path $BackupRoot $Stamp
$MirrorDir  = Join-Path $MirrorRoot $Stamp

# Free space check on C:
$cDrive = Get-PSDrive -Name ($BackupRoot.Substring(0,1)) -ErrorAction SilentlyContinue
if ($cDrive) {
    $freeGb = [math]::Round($cDrive.Free / 1GB, 1)
    if ($freeGb -lt 15) { Write-Warn "Only ${freeGb}GB free on $($BackupRoot.Substring(0,2)) - backup may not fit" }
    else                { Write-Ok  "${freeGb}GB free on $($BackupRoot.Substring(0,2))" }
}

# E: presence check (non-fatal - we still want the C: backup if E: is absent)
if (-not $SkipMirror) {
    if (Test-Path -LiteralPath ($MirrorRoot.Substring(0,3))) {
        $eDrive = Get-PSDrive -Name ($MirrorRoot.Substring(0,1)) -ErrorAction SilentlyContinue
        if ($eDrive) {
            $eFreeGb = [math]::Round($eDrive.Free / 1GB, 1)
            Write-Ok "$($MirrorRoot.Substring(0,2)) present, ${eFreeGb}GB free"
        }
    } else {
        Write-Warn "$($MirrorRoot.Substring(0,2)) not present - will skip the mirror step"
        $SkipMirror = $true
    }
}

New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
Write-Ok "Backup folder: $BackupDir"

# ==========================================================================
# 1. GIT BUNDLE - full history, including the unpushed commits
# ==========================================================================
Write-Step '1. GIT BUNDLE (committed history)'

Push-Location $RepoPath
try {
    # Record the exact state we are capturing, for the record.
    $branch   = (git rev-parse --abbrev-ref HEAD 2>$null)
    $headSha  = (git rev-parse HEAD 2>$null)
    $ahead    = (git rev-list --count origin/main..HEAD 2>$null)
    $dirty    = (git status --porcelain 2>$null)

    Write-Info "branch: $branch"
    Write-Info "HEAD:   $headSha"
    Write-Info "commits ahead of origin/main: $ahead"
    Write-Info "uncommitted / untracked entries: $(@($dirty).Count)"

    $bundlePath = Join-Path $BackupDir "citizen-compass-$Stamp.bundle"
    Invoke-Native { git bundle create $bundlePath --all } | ForEach-Object { Write-Info $_ }
    $bundleExit = $LASTEXITCODE

    if (-not (Test-Path -LiteralPath $bundlePath) -or $bundleExit -ne 0) {
        Write-Fail "Bundle was not created (git exit $bundleExit)"
    } else {
        # Verify before trusting it. An unverified bundle is not a backup.
        # NOTE: git writes "<file> is okay" to STDERR on SUCCESS. Judge by exit
        # code only - the presence of stderr output means nothing here.
        $verify = Invoke-Native { git bundle verify $bundlePath }
        if ($LASTEXITCODE -eq 0) {
            $sizeMb = [math]::Round((Get-Item $bundlePath).Length / 1MB, 1)
            Write-Ok "Bundle verified OK (${sizeMb} MB)"
            $verify | ForEach-Object { Write-Info $_ }
        } else {
            Write-Fail "Bundle FAILED verification: $($verify -join ' | ')"
        }
    }

    # Save the state summary alongside it.
    @"
Citizen Compass backup state
Captured: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')
Repo:     $RepoPath
Branch:   $branch
HEAD:     $headSha
Commits ahead of origin/main: $ahead

--- git status --short at capture time ---
$($dirty -join "`n")
"@ | Set-Content -Path (Join-Path $BackupDir 'GIT-STATE.txt') -Encoding UTF8
    Write-Ok 'GIT-STATE.txt written'
}
finally { Pop-Location }

# ==========================================================================
# 2. WORKING-TREE COPY - this is what catches the UNCOMMITTED work
# ==========================================================================
Write-Step '2. WORKING-TREE COPY (catches uncommitted work)'

$repoCopy = Join-Path $BackupDir 'repo'

# Excluded because they are large AND genuinely re-obtainable:
#   venv               -> rebuild from requirements.txt
#   sc-ships           -> re-downloadable from Hugging Face (incl. the
#                         model_scaled.glb files, regenerable via rescale_all_ships.py)
#   __pycache__/.cache -> build artifacts
#   data-layer\external-sources -> raw public snapshots, re-pullable.
#                         The MANIFESTS live elsewhere and ARE included -
#                         those are the irreplaceable provenance record.
$excludeDirs = @(
    (Join-Path $RepoPath 'venv'),
    (Join-Path $RepoPath 'sc-ships'),
    (Join-Path $RepoPath '__pycache__'),
    (Join-Path $RepoPath '.cache'),
    (Join-Path $RepoPath 'node_modules'),
    (Join-Path $RepoPath 'data-layer\external-sources')
)

Write-Info 'Excluding: venv, sc-ships, __pycache__, .cache, node_modules, data-layer\external-sources'
Write-Info 'INCLUDING: .git, models (incl. "done ships"), data-layer\external-source-manifests, docs, logs, checks, scripts'

# /E    = copy subdirs including empty ones
# /XD   = exclude directories
# /R:2  = 2 retries, /W:5 = 5s wait
# NOTE: /MIR is deliberately NOT used - it would delete files at the target.
$roboArgs = @(
    $RepoPath, $repoCopy, '/E',
    '/XD') + $excludeDirs + @(
    '/R:2','/W:5','/NFL','/NDL','/NJH','/NP'
)

Invoke-Native { robocopy @roboArgs } | ForEach-Object { if ($_ -match '\S') { Write-Info $_ } }

# robocopy exit codes: 0-7 = success (with varying detail), 8+ = real failure
$roboExit = $LASTEXITCODE
if ($roboExit -ge 8) {
    Write-Fail "robocopy repo copy failed with exit code $roboExit"
} else {
    $fileCount = (Get-ChildItem -LiteralPath $repoCopy -Recurse -File -ErrorAction SilentlyContinue).Count
    Write-Ok "Working-tree copy complete ($fileCount files, robocopy code $roboExit)"
}

# Spot-check the specific irreplaceable items we know about.
$mustExist = @(
    'repo\models\done ships\HPs.blend',
    'repo\models\done ships\buccaneer_hardpoints.json',
    'repo\models\done ships\cutlass_black_hardpoints.json',
    'repo\data-layer\external-source-manifests'
)
foreach ($rel in $mustExist) {
    $p = Join-Path $BackupDir $rel
    if (Test-Path -LiteralPath $p) { Write-Ok  "captured: $rel" }
    else                           { Write-Warn "MISSING:  $rel" }
}

# ==========================================================================
# 3. POSTGRES DUMP
# ==========================================================================
Write-Step '3. POSTGRES DUMP'

$skipDbEntirely = $false

if (-not $env:PGPASSWORD) {
    if ($NonInteractive) {
        Write-Fail 'PGPASSWORD not set and running non-interactively - skipping dump and restore test.'
        Write-Info  'Re-run with $env:PGPASSWORD set beforehand to capture the database.'
        $skipDbEntirely = $true
    } else {
        Write-Info 'PGPASSWORD is not set in this session.'
        $sec = Read-Host -Prompt "  Postgres password for user '$DbUser'" -AsSecureString
        $env:PGPASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    }
}

$dumpPath = Join-Path $BackupDir "$DbName-$Stamp.dump"

# -Fc = custom format: compressed, and restorable selectively with pg_restore
if (-not $skipDbEntirely) {
    Invoke-Native { pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName -Fc -f $dumpPath } |
        ForEach-Object { Write-Info $_ }
    if ($LASTEXITCODE -ne 0) { Write-Fail "pg_dump exited $LASTEXITCODE" }
}

if ($skipDbEntirely) {
    Write-Warn 'Database NOT captured - see the failure above'
}
elseif (Test-Path -LiteralPath $dumpPath) {
    $dumpKb = [math]::Round((Get-Item $dumpPath).Length / 1KB, 1)
    Write-Ok "Dump written (${dumpKb} KB)"
    if ($dumpKb -lt 20) {
        Write-Warn "Dump is very small (${dumpKb} KB) - could be schema-only. The restore test below is what proves it."
    }
} else {
    Write-Fail 'pg_dump produced no file'
}

# ==========================================================================
# 4. RESTORE TEST - an untested backup is not a backup
# ==========================================================================
Write-Step '4. RESTORE TEST (into a throwaway database)'

if ($SkipDbTest -or $skipDbEntirely) {
    Write-Warn 'Restore test not run - backup of the database is UNVERIFIED'
}
elseif (-not (Test-Path -LiteralPath $dumpPath)) {
    Write-Fail 'No dump to test'
}
else {
    # Underscores only - a hyphen in a database name needs quoting everywhere
    # it is later referenced, including in the dropdb command printed at the end.
    $testDb = "cc_restore_test_$($Stamp -replace '-','_')"
    Write-Info "Creating throwaway database: $testDb"

    $createSql = 'CREATE DATABASE "' + $testDb + '";'
    Invoke-Native { psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c $createSql } |
        ForEach-Object { Write-Info $_ }

    if (Test-Command 'pg_restore') {
        # pg_restore routinely writes progress and non-fatal notices to stderr.
        # That is not failure - only the exit code is.
        Invoke-Native { pg_restore -h $DbHost -p $DbPort -U $DbUser -d $testDb $dumpPath } |
            ForEach-Object { Write-Info $_ }
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "pg_restore exited $LASTEXITCODE - the ship count below is the real test"
        }
    } else {
        Write-Fail 'pg_restore not on PATH'
    }

    # Count ships. If the table name differs, list what IS there rather than
    # failing silently - a wrong table name should not read as a bad backup.
    $countRaw = Invoke-Native {
        psql -h $DbHost -p $DbPort -U $DbUser -d $testDb -t -A -c 'SELECT COUNT(*) FROM ships;'
    }
    $countTxt = ($countRaw | Out-String).Trim()

    if ($LASTEXITCODE -eq 0 -and $countTxt -match '^\d+$') {
        $count = [int]$countTxt
        if ($count -eq $ExpectedShipCount) {
            Write-Ok "RESTORE VERIFIED: $count ships (expected $ExpectedShipCount)"
        } elseif ($count -gt 0) {
            Write-Warn "Restore returned $count ships, expected $ExpectedShipCount - investigate before trusting this dump"
        } else {
            Write-Fail 'Restore returned 0 ships - dump is likely schema-only'
        }
    } else {
        Write-Warn "Could not count ships (table name may differ). Tables present:"
        Invoke-Native {
            psql -h $DbHost -p $DbPort -U $DbUser -d $testDb -t -A `
                 -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1;"
        } | ForEach-Object { Write-Info "    $_" }
    }

    Write-Info ''
    Write-Info "Throwaway DB '$testDb' was LEFT IN PLACE on purpose."
    Write-Info 'This script never deletes. Drop it yourself when done - command printed at the end.'
    $script:TestDbName = $testDb
}

# ==========================================================================
# 5. BLENDER ADDONS - the CC Hardpoint Tool lives OUTSIDE the repo
# ==========================================================================
Write-Step '5. BLENDER ADDONS (not in the repo - would otherwise be lost)'

$blenderBase = Join-Path $env:APPDATA 'Blender Foundation\Blender'
$addonDest   = Join-Path $BackupDir 'blender-addons'

if (Test-Path -LiteralPath $blenderBase) {
    $versions = Get-ChildItem -LiteralPath $blenderBase -Directory -ErrorAction SilentlyContinue
    if (-not $versions) { Write-Warn "No Blender version folders under $blenderBase" }

    foreach ($v in $versions) {
        $src = Join-Path $v.FullName 'scripts\addons'
        if (Test-Path -LiteralPath $src) {
            $dst = Join-Path $addonDest $v.Name
            Invoke-Native { robocopy $src $dst /E /R:2 /W:5 /NFL /NDL /NJH /NP } | Out-Null
            if ($LASTEXITCODE -lt 8) {
                $n = (Get-ChildItem -LiteralPath $dst -Recurse -File -ErrorAction SilentlyContinue).Count
                Write-Ok "Blender $($v.Name) addons captured ($n files)"
            } else {
                Write-Warn "Blender $($v.Name) addon copy returned $LASTEXITCODE"
            }
        }
    }

    # Confirm the Hardpoint Tool specifically made it.
    if (Test-Path -LiteralPath $addonDest) {
        $hit = Get-ChildItem -LiteralPath $addonDest -Recurse -Filter *.py -ErrorAction SilentlyContinue |
               Select-String -Pattern 'Citizen Compass|CC Hardpoints|hardpoint' -List -ErrorAction SilentlyContinue |
               Select-Object -First 5
        if ($hit) {
            Write-Ok 'CC Hardpoint Tool found in the captured addons:'
            $hit | ForEach-Object { Write-Info "    $($_.Path)" }
        } else {
            Write-Warn 'Addons copied, but no file matching the Hardpoint Tool was identified - check manually'
        }
    }
} else {
    Write-Warn "Blender appdata folder not found at $blenderBase - addon NOT backed up"
}

# ==========================================================================
# 6. SHA-256 MANIFEST
# ==========================================================================
Write-Step '6. SHA-256 MANIFEST'

$sumsPath = Join-Path $BackupDir 'SHA256SUMS.txt'
$hashLines = Get-ChildItem -LiteralPath $BackupDir -Recurse -File |
    Where-Object { $_.Name -ne 'SHA256SUMS.txt' } |
    ForEach-Object {
        $h = Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256
        $rel = $_.FullName.Substring($BackupDir.Length).TrimStart('\')
        "{0}  {1}" -f $h.Hash, $rel
    }

$hashLines | Set-Content -Path $sumsPath -Encoding UTF8
Write-Ok "$($hashLines.Count) files hashed -> SHA256SUMS.txt"

# ==========================================================================
# 7. MIRROR TO E:
# ==========================================================================
Write-Step '7. COPY TO E: (second physical device)'

if ($SkipMirror) {
    Write-Warn 'Mirror step skipped - backup exists on C: only'
} else {
    New-Item -ItemType Directory -Path $MirrorDir -Force | Out-Null
    # /E not /MIR - again, nothing at the destination is ever deleted.
    Invoke-Native { robocopy $BackupDir $MirrorDir /E /R:2 /W:5 /NFL /NDL /NJH /NP } |
        ForEach-Object { if ($_ -match '\S') { Write-Info $_ } }

    if ($LASTEXITCODE -ge 8) {
        Write-Fail "Mirror to E: failed with code $LASTEXITCODE"
    } else {
        Write-Ok "Mirrored to $MirrorDir"

        # Re-hash the E: copy and compare against the manifest.
        Write-Info 'Verifying E: copy against SHA256SUMS.txt ...'
        $expected = @{}
        Get-Content -LiteralPath $sumsPath | ForEach-Object {
            if ($_ -match '^([0-9A-Fa-f]{64})\s\s(.+)$') { $expected[$Matches[2]] = $Matches[1] }
        }

        $bad = 0; $checked = 0
        foreach ($rel in $expected.Keys) {
            $mp = Join-Path $MirrorDir $rel
            if (-not (Test-Path -LiteralPath $mp)) { Write-Warn "missing on E: $rel"; $bad++; continue }
            $actual = (Get-FileHash -LiteralPath $mp -Algorithm SHA256).Hash
            $checked++
            if ($actual -ne $expected[$rel]) { Write-Fail "HASH MISMATCH on E: $rel"; $bad++ }
        }
        if ($bad -eq 0) { Write-Ok "All $checked files on E: match their hashes" }
        else            { Write-Fail "$bad file(s) failed verification on E:" }
    }
}

# ==========================================================================
# SUMMARY
# ==========================================================================
Write-Step 'SUMMARY'

$totalMb = [math]::Round(
    ((Get-ChildItem -LiteralPath $BackupDir -Recurse -File |
      Measure-Object -Property Length -Sum).Sum / 1MB), 1)

Write-Host ""
Write-Host "  Backup folder : $BackupDir"        -ForegroundColor White
if (-not $SkipMirror) {
    Write-Host "  E: copy       : $MirrorDir"    -ForegroundColor White
}
Write-Host "  Total size    : ${totalMb} MB"     -ForegroundColor White
Write-Host "  Warnings      : $($script:Warnings.Count)" -ForegroundColor $(if($script:Warnings.Count){'Yellow'}else{'Green'})
Write-Host "  Failures      : $($script:Failures.Count)" -ForegroundColor $(if($script:Failures.Count){'Red'}else{'Green'})
Write-Host ""

if ($script:Warnings.Count) {
    Write-Host "  WARNINGS:" -ForegroundColor Yellow
    $script:Warnings | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
    Write-Host ""
}
if ($script:Failures.Count) {
    Write-Host "  FAILURES:" -ForegroundColor Red
    $script:Failures | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    Write-Host ""
}

Write-Host "  STILL TO DO BY HAND:" -ForegroundColor Cyan
Write-Host "    1. Copy the backup folder to the laptop you're taking." -ForegroundColor Gray
Write-Host "    2. Upload it to cloud storage - the only copy that survives losing the trailer." -ForegroundColor Gray
if ($script:TestDbName) {
Write-Host "    3. Drop the throwaway test database when you're satisfied:" -ForegroundColor Gray
Write-Host "       dropdb -h $DbHost -p $DbPort -U $DbUser $($script:TestDbName)" -ForegroundColor Gray
}
Write-Host ""

if ($script:Failures.Count) { exit 1 } else { exit 0 }
