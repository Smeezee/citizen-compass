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
   * The only writes are into the backup folder and the mirror copies of it
     (D: primary, E: secondary). The source repo is read only.

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
    # MIRROR TARGETS, changed 2026-08-06.
    #
    # This used to point at E: alone, which was simply the wrong drive. The
    # actual layout of this machine is:
    #
    #   C:  Local Disk   1.81 TB   the original, and where the staging copy goes
    #   D:  My Book      3.63 TB   EXTERNAL. The real backup target.
    #   E:  New Volume   1.81 TB   internal secondary. Useful, but it is in the
    #                              same box as C: - it does not survive losing
    #                              the machine, so it cannot be the primary.
    #
    # D: is now primary and E: is kept as a second mirror. Two mirrors are
    # wanted and were explicitly approved. Both are written; neither is
    # optional (see the preflight - a missing mirror drive is now fatal).
    #
    # NOTE: D: is exFAT. That is why the copies below use neither /COPYALL nor
    # /SEC - exFAT has no NTFS ACLs and requesting them fails every file.
    [string]   $MirrorRoot       = 'D:\cc-backup',
    [string[]] $SecondMirrorRoot = @('E:\cc-backup'),
    [string] $DbName     = 'citizen_compass',
    [string] $DbUser     = 'postgres',
    [string] $DbHost     = '127.0.0.1',
    [int]    $DbPort     = 5432,
    [int]    $ExpectedShipCount = 254,
    [switch] $SkipMirror,
    # -FullMirror: put the two IRREPLACEABLE trees into the mirror copy.
    #
    # The C: copy excludes six directories. Four are genuinely rebuildable
    # (venv, __pycache__, .cache, node_modules). Two are NOT, and they are only
    # on that list because this script was written for a small disk:
    #
    #   sc-ships                     ~7.3 GB. The comment below says
    #                                "re-downloadable from Hugging Face", but
    #                                that pack's redistribution rights are on
    #                                record as UNESTABLISHED. If it disappears
    #                                upstream, so does the 3D viewer.
    #   data-layer\external-sources  The sealed snapshots. Re-pulling UEX gives
    #                                TODAY's prices, not 1 August's. These are
    #                                the start of the historical record and
    #                                cannot be re-fetched at all.
    #
    # When set, the MIRROR excludes only the four rebuildable ones. The C: copy
    # keeps its existing exclusions - that copy is for speed. Defaults unchanged:
    # without this switch the script behaves exactly as before.
    [switch] $FullMirror,
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

<#
 Invoke-Robocopy — run robocopy as a DETACHED process and return its exit code.

 WHY THIS EXISTS (2026-08-06):
 The 2026-08-05 run was killed mid-file. robocopy had been invoked inline, so
 it inherited the caller's lifetime; when the caller was terminated on a
 timeout, the copy died with a file half-written. A truncated file is present
 at the destination, so a file COUNT still matched - which is precisely the
 failure Verify-MirrorTree.ps1 was later written to catch.

 Start-Process -PassThru gives three things the inline call did not:

   1. A real process object, so the exit code comes from the PROCESS rather
      than from $LASTEXITCODE, which any intervening pipeline can clobber.
   2. /LOG: writes robocopy's own record straight to disk as it goes. If this
      run is interrupted, that log is the only evidence of how far it got.
   3. Output does not flow through the PowerShell pipeline at all, so the 5.1
      native-stderr problem documented above simply cannot arise here.

 WaitForExit() is deliberate. The COPY must finish before verification reads
 the destination, or the verifier races the writer and reports truncation that
 is merely incomplete. What must not block is the TOOL CALL - so the whole
 script is launched detached, and inside it each copy is awaited in order.

 QUOTING: Start-Process does not quote for you. 'Blender Foundation' and
 'done ships' both contain spaces. Trailing backslashes are trimmed before
 quoting because robocopy reads "C:\path\" as an escaped quote and mangles
 the argument.
#>
function Invoke-Robocopy {
    param(
        [Parameter(Mandatory)][string]   $Source,
        [Parameter(Mandatory)][string]   $Destination,
        [string[]] $ExtraArgs = @(),
        [Parameter(Mandatory)][string]   $LogPath
    )

    $raw = @($Source, $Destination) + $ExtraArgs + @("/LOG:$LogPath")

    $quoted = $raw | ForEach-Object {
        if ($_ -match '\s') {
            if ($_ -match '^/LOG:(.+)$') { '"/LOG:' + $Matches[1].TrimEnd('\') + '"' }
            else                         { '"' + $_.TrimEnd('\') + '"' }
        } else { $_ }
    }

    # The destination's PARENT must exist before robocopy is asked to write a
    # log into it, and so must the log's own directory. See RoboLogPath below
    # for the bug this is guarding against.
    $logDir = Split-Path -Parent $LogPath
    if ($logDir -and -not (Test-Path -LiteralPath $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $p = Start-Process -FilePath 'robocopy.exe' -ArgumentList $quoted `
                       -NoNewWindow -PassThru

    # TOUCHING .Handle IS LOAD BEARING - DO NOT REMOVE.
    #
    # Start-Process -PassThru returns a Process object whose exit code is only
    # retained if the handle has been cached. Without this line $p.ExitCode
    # comes back $null, and PowerShell coerces $null to 0 when it is bound to
    # an [int] parameter. On 2026-08-06 that turned a robocopy that copied
    # NOTHING - it died on "ERROR : Invalid Parameter" - into a reported
    # "exit code 0 (nothing to do, destination already current)".
    #
    # 58,257 files and 10.2 GB were reported as successfully mirrored having
    # never been read. Only the independent per-file verifier caught it.
    $null = $p.Handle

    $p.WaitForExit()

    $code = $p.ExitCode
    if ($null -eq $code) {
        # FAIL CLOSED. An exit code we could not read is not a zero. Returning
        # a distinct out-of-band value means every caller's `-ge 8` test treats
        # it as the failure it is, and Show-RoboCode names it explicitly rather
        # than printing a reassuring "nothing to do".
        return $RoboExitUnavailable
    }
    return [int]$code
}

# Distinct from every real robocopy code (0-16) and above the 8+ failure
# threshold, so it fails every existing test without needing new branches.
$RoboExitUnavailable = 9999

<#
 RoboLogPath — build a per-tree log filename from a RELATIVE path.

 THE BUG THIS EXISTS TO KILL (found 2026-08-06):

     $t.Rel -replace '[\/]','_'

 looks like it flattens both separators. It does not. Inside a regex character
 class `\/` is an escaped FORWARD slash, so `[\/]` means "a forward slash" and
 nothing else. A backslash sails straight through.

 So 'data-layer\external-sources' stayed as-is and the log path became

     D:\cc-backup\<stamp>\robocopy-data-layer\external-sources.log

 - a file inside a 'robocopy-data-layer' directory that does not exist.
 robocopy refused the parameter, copied nothing, and (with the $null exit-code
 bug above) reported success. 'sc-ships' has no separator in it, which is
 exactly why the one tree that worked was the one that hid the defect.

 `[\\/]` is the correct class. Written here once so no call site can get it
 wrong again.
#>
function RoboLogPath {
    param([string]$Dir, [string]$RelName)
    $safe = $RelName -replace '[\\/]', '_'
    return (Join-Path $Dir ("robocopy-" + $safe + ".log"))
}

<#
 Show-RoboCode — robocopy's exit status is a BITMASK, not an ordinal.
 Decoded in one place so every call site reports it the same way.
 0-7 are success variants; 8 and 16 are real failures.
#>
function Show-RoboCode {
    param([int]$Code, [string]$Label)
    if ($Code -eq 9999) {
        Write-Info "$Label robocopy EXIT CODE UNAVAILABLE - treated as FAILURE, never as 0"
        return $Code
    }
    $bits = @()
    if ($Code -band 1)  { $bits += 'files copied' }
    if ($Code -band 2)  { $bits += 'extra files/dirs at destination' }
    if ($Code -band 4)  { $bits += 'MISMATCHED files/dirs' }
    if ($Code -band 8)  { $bits += 'SOME FILES COULD NOT BE COPIED' }
    if ($Code -band 16) { $bits += 'SERIOUS ERROR - no files copied' }
    if ($Code -eq 0)    { $bits += 'nothing to do, destination already current' }
    Write-Info "$Label robocopy exit code $Code  ($($bits -join '; '))"
    return $Code
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

# All mirror targets, primary first. Every entry here is written; there is no
# "best effort" member of this list.
$AllMirrorRoots = @($MirrorRoot) + $SecondMirrorRoot | Where-Object { $_ }

# Free space check on C:
$cDrive = Get-PSDrive -Name ($BackupRoot.Substring(0,1)) -ErrorAction SilentlyContinue
if ($cDrive) {
    $freeGb = [math]::Round($cDrive.Free / 1GB, 1)
    if ($freeGb -lt 15) { Write-Warn "Only ${freeGb}GB free on $($BackupRoot.Substring(0,2)) - backup may not fit" }
    else                { Write-Ok  "${freeGb}GB free on $($BackupRoot.Substring(0,2))" }
}

# --------------------------------------------------------------------------
# MIRROR DRIVE PRESENCE - FATAL, changed 2026-08-06.
#
# This check used to warn and carry on: an absent mirror drive set
# $SkipMirror and the run went on to print "Failures: 0" and exit 0. That is
# the SILENT SUCCESS pattern this project has been bitten by repeatedly. The
# whole purpose of a mirror is to put the data on a SECOND physical device;
# a run that never left C: has not done the thing it was asked to do, and it
# must not be able to report success for it.
#
# So: a missing mirror drive is now a hard failure for EVERY mirror in the
# list, not only under -FullMirror.
#
# -SkipMirror remains the one legitimate way out, because that is an explicit
# instruction from the operator rather than a drive quietly not being there.
# An unplugged drive and a deliberate "skip it" are different events and are
# no longer collapsed into the same outcome.
# --------------------------------------------------------------------------
if ($SkipMirror) {
    Write-Warn 'MIRRORS SKIPPED BY REQUEST (-SkipMirror). Backup will exist on C: only.'
} else {
    $missingMirrors = @()
    foreach ($mr in $AllMirrorRoots) {
        $driveRoot   = $mr.Substring(0,3)   # e.g. 'D:\'
        $driveLetter = $mr.Substring(0,1)
        $driveLabel  = $mr.Substring(0,2)   # e.g. 'D:'

        if (Test-Path -LiteralPath $driveRoot) {
            $d = Get-PSDrive -Name $driveLetter -ErrorAction SilentlyContinue
            if ($d) {
                $freeGb = [math]::Round($d.Free / 1GB, 1)
                Write-Ok "$driveLabel present, ${freeGb}GB free  ->  $mr"
            } else {
                Write-Ok "$driveLabel present  ->  $mr"
            }
        } else {
            $missingMirrors += $driveLabel
        }
    }

    if ($missingMirrors.Count -gt 0) {
        # One string, deliberately. Written as "a" + "b" across separate lines
        # this parses as a command invocation with several positional
        # arguments, not a concatenation - Write-Fail would bind only the first
        # fragment to $m and drop the rest into $args unnoticed, so the loudest
        # message in the script would be silently truncated to its first line.
        Write-Fail ("MIRROR DRIVE(S) NOT PRESENT: $($missingMirrors -join ', '). " +
                    "Refusing to continue. A backup that never reaches a second " +
                    "device is not a backup, and this script will not report " +
                    "success for one. Plug the drive in, or pass -SkipMirror to " +
                    "say so deliberately.")
        exit 1
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
#   data-layer\external-sources -> raw public snapshots.
#
#   NOTE, 2026-08-05: the two entries above are the ONLY reason
#   -FullMirror exists. 'sc-ships re-downloadable' overstates it - that
#   pack's redistribution rights are on record as unestablished - and
#   'external-sources re-pullable' is simply wrong: re-pulling UEX
#   returns TODAY's prices, not the sealed snapshot's. They stay
#   excluded HERE, where the exclusion buys speed on C:, and are added
#   to the mirror by step 7b when -FullMirror is set.
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
$repoCopyLog = Join-Path $BackupDir 'robocopy-repo.log'
$roboExit = Invoke-Robocopy -Source $RepoPath -Destination $repoCopy `
    -ExtraArgs (@('/E','/XD') + $excludeDirs + @('/R:2','/W:5','/NFL','/NDL','/NJH','/NP')) `
    -LogPath $repoCopyLog

# robocopy exit codes: 0-7 = success (with varying detail), 8+ = real failure
[void](Show-RoboCode -Code $roboExit -Label 'repo copy:')
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
            $addonLog = Join-Path $BackupDir ("robocopy-blender-" + $v.Name + ".log")
            $addonExit = Invoke-Robocopy -Source $src -Destination $dst `
                -ExtraArgs @('/E','/R:2','/W:5','/NFL','/NDL','/NJH','/NP') `
                -LogPath $addonLog
            if ($addonExit -lt 8) {
                $n = (Get-ChildItem -LiteralPath $dst -Recurse -File -ErrorAction SilentlyContinue).Count
                Write-Ok "Blender $($v.Name) addons captured ($n files)"
            } else {
                Write-Warn "Blender $($v.Name) addon copy returned $addonExit - see $addonLog"
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
# 7. MIRROR TO EVERY CONFIGURED DEVICE
#
# Changed 2026-08-06 from a single E: copy to a list. D: (My Book, external)
# is primary; E: is a second mirror. The loop treats them identically - there
# is no "best effort" member, and a failure on either is a failure of the run.
# ==========================================================================
$MirrorDirs = @()
$mirrorFail = 0

foreach ($mirrorRootItem in $AllMirrorRoots) {

Write-Step "7. COPY TO $($mirrorRootItem.Substring(0,2)) (separate physical device)"

$MirrorDir = Join-Path $mirrorRootItem $Stamp
$MirrorDirs += $MirrorDir

if ($SkipMirror) {
    Write-Warn 'Mirror step skipped by request - backup exists on C: only'
} else {
    New-Item -ItemType Directory -Path $MirrorDir -Force | Out-Null
    # /E not /MIR - again, nothing at the destination is ever deleted.
    $mirrorLog  = Join-Path $BackupDir ("robocopy-mirror-" + $mirrorRootItem.Substring(0,1) + ".log")
    $mirrorExit = Invoke-Robocopy -Source $BackupDir -Destination $MirrorDir `
        -ExtraArgs @('/E','/R:2','/W:5','/NFL','/NDL','/NJH','/NP') `
        -LogPath $mirrorLog
    [void](Show-RoboCode -Code $mirrorExit -Label "mirror to $($mirrorRootItem.Substring(0,2)):")

    if ($mirrorExit -ge 8) {
        Write-Fail "Mirror to $($mirrorRootItem.Substring(0,2)) failed with code $mirrorExit - see $mirrorLog"
        $mirrorFail++
    } else {
        Write-Ok "Mirrored to $MirrorDir"

        # Re-hash the mirrored copy and compare against the manifest.
        Write-Info "Verifying $($mirrorRootItem.Substring(0,2)) copy against SHA256SUMS.txt ..."
        $expected = @{}
        Get-Content -LiteralPath $sumsPath | ForEach-Object {
            if ($_ -match '^([0-9A-Fa-f]{64})\s\s(.+)$') { $expected[$Matches[2]] = $Matches[1] }
        }

        $bad = 0; $checked = 0
        foreach ($rel in $expected.Keys) {
            $mp = Join-Path $MirrorDir $rel
            if (-not (Test-Path -LiteralPath $mp)) {
                Write-Fail "missing on $($mirrorRootItem.Substring(0,2)): $rel"; $bad++; continue
            }
            $actual = (Get-FileHash -LiteralPath $mp -Algorithm SHA256).Hash
            $checked++
            if ($actual -ne $expected[$rel]) {
                Write-Fail "HASH MISMATCH on $($mirrorRootItem.Substring(0,2)): $rel"; $bad++
            }
        }
        if ($bad -eq 0) { Write-Ok "All $checked files on $($mirrorRootItem.Substring(0,2)) match their hashes" }
        else            { Write-Fail "$bad file(s) failed verification on $($mirrorRootItem.Substring(0,2))"; $mirrorFail++ }

        # ------------------------------------------------------------------
        # 7b. -FullMirror: add the two irreplaceable trees.
        #
        # These cannot come from $BackupDir - the working-tree copy in step 2
        # deliberately excluded them - so they are copied from the REPO straight
        # into the mirror, with only the four rebuildable exclusions applied.
        #
        # Bare directory names are used for /XD rather than full paths, so a
        # nested __pycache__ is excluded too. The exclusions in step 2 are
        # absolute paths and therefore only match at the repo root; that is
        # pre-existing behaviour and is left alone.
        # ------------------------------------------------------------------
        if ($FullMirror) {
            Write-Step "7b. FULL MIRROR - the irreplaceable trees -> $($mirrorRootItem.Substring(0,2))"

            $fullTrees = @(
                @{ Name = 'sc-ships';                    Rel = 'sc-ships' },
                @{ Name = 'data-layer\external-sources'; Rel = 'data-layer\external-sources' }
            )
            $fmFail = 0

            foreach ($t in $fullTrees) {
                $src = Join-Path $RepoPath $t.Rel
                $dst = Join-Path (Join-Path $MirrorDir 'repo') $t.Rel

                if (-not (Test-Path -LiteralPath $src)) {
                    # Absent is reported, never silently treated as "done".
                    Write-Warn "$($t.Name) not present in the repo - nothing to mirror"
                    continue
                }

                # Count the source the SAME WAY robocopy will copy it, i.e. with
                # the four exclusions applied. Counting unfiltered and comparing
                # against a filtered destination reports a shortfall that is not
                # real: sc-ships holds 1,675 files of which 724 live in .cache
                # (a HuggingFace cache, correctly excluded), so a naive compare
                # claimed "only 951 of 1675 files reached the mirror" when all
                # 951 eligible files and every one of its 7,570.0 MB had in fact
                # arrived. A false failure is as corrosive as a false pass - it
                # trains the reader to disbelieve the check.
                $excludedNames = @('venv','__pycache__','.cache','node_modules')
                $srcFiles = Get-ChildItem -LiteralPath $src -Recurse -File -Force -ErrorAction SilentlyContinue |
                    Where-Object {
                        $full = $_.FullName
                        -not ($excludedNames | Where-Object { $full -match "\\$([regex]::Escape($_))\\" })
                    }
                $srcCount = $srcFiles.Count
                $srcBytes = ($srcFiles | Measure-Object -Property Length -Sum).Sum
                $srcMb    = [math]::Round(($srcBytes / 1MB), 1)
                Write-Info "$($t.Name): $srcCount files, $srcMb MB -> $dst"

                New-Item -ItemType Directory -Path $dst -Force | Out-Null

                # A durable robocopy log per tree. When a copy is interrupted,
                # this is the only record of how far it got.
                # Built by RoboLogPath - see its header for why the obvious
                # inline -replace was wrong and silently so.
                $roboLog = RoboLogPath -Dir $MirrorDir -RelName $t.Rel

                # /E, NOT /MIR. /MIR deletes anything at the destination that is
                # not at the source, and this script's header states as a
                # guarantee that it contains no delete operation of any kind.
                # /E is equally resumable - it skips files that already match -
                # so nothing is gained by /MIR except the ability to destroy.
                # No /COPYALL and no /SEC: the mirror is exFAT, which has no
                # NTFS ACLs, and requesting them fails every file.
                #
                # Detached via Start-Process - see Invoke-Robocopy's header.
                # This is the 7.5 GB copy that was killed mid-file on
                # 2026-08-05 by running inline under a caller that timed out.
                $rc = Invoke-Robocopy -Source $src -Destination $dst `
                    -ExtraArgs @('/E','/R:2','/W:2','/NP',
                                 '/XD','venv','__pycache__','.cache','node_modules') `
                    -LogPath $roboLog

                # ROBOCOPY EXIT CODE IS A BITMASK, and it is reported here
                # explicitly. 0-7 are success variants; 8 and above is a real
                # failure and is FATAL regardless of what any file count says.
                [void](Show-RoboCode -Code $rc -Label "$($t.Name):")

                if ($rc -ge 8) {
                    Write-Fail "$($t.Name): robocopy exit $rc is a real failure - see $roboLog"
                    $fmFail++
                    continue
                }

                # ------------------------------------------------------------
                # INDEPENDENT PER-FILE VERIFICATION.
                #
                # Not a count, and not derived from the copy. Verify-MirrorTree
                # enumerates the destination from DISK and compares every file
                # by relative path AND byte size, so a truncated file - present,
                # therefore invisible to a count - is caught. It carries a
                # positive and a negative control so a checker that cannot see
                # the destination cannot pass vacuously.
                #
                # It is a separate script run as a separate process on purpose:
                # it shares no filter state with the copy above, so it cannot
                # compare the copy to itself.
                # ------------------------------------------------------------
                $verifier = Join-Path $RepoPath 'scripts\Verify-MirrorTree.ps1'
                if (-not (Test-Path -LiteralPath $verifier)) {
                    Write-Fail "$($t.Name): verifier not found at $verifier - copy is UNVERIFIED"
                    $fmFail++
                    continue
                }

                & powershell -ExecutionPolicy Bypass -NoProfile -File $verifier `
                    -Source $src -Destination $dst |
                    ForEach-Object { Write-Info $_ }
                $vrc = $LASTEXITCODE

                if ($vrc -eq 0) {
                    Write-Ok "$($t.Name): verified per-file against the destination"
                } elseif ($vrc -eq 2) {
                    Write-Fail "$($t.Name): verification COULD NOT RUN - reporting as not verified, not as passed"
                    $fmFail++
                } else {
                    Write-Fail "$($t.Name): per-file verification found mismatches (see above)"
                    $fmFail++
                }
            }

            if ($fmFail -eq 0) {
                Write-Ok "Full mirror complete to $($mirrorRootItem.Substring(0,2)) - both irreplaceable trees verified PER FILE"
            } else {
                Write-Fail "$fmFail full-mirror tree(s) failed on $($mirrorRootItem.Substring(0,2))"
                $mirrorFail += $fmFail
            }
        }
    }
}

}  # end foreach mirror root

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
    $mirrorLabel = 'Mirrors       : '
    foreach ($md in $MirrorDirs) {
        Write-Host "  $mirrorLabel$md"           -ForegroundColor White
        $mirrorLabel = '                '
    }
    if ($mirrorFail -gt 0) {
        Write-Host "  Mirror faults : $mirrorFail" -ForegroundColor Red
    }
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
