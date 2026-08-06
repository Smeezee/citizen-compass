<#
==============================================================================
 Test-DatabaseBackup.ps1  -  dump, RESTORE, count, prove, mirror
==============================================================================

 A dump nobody has restored is a file, not a backup. This takes the dump,
 restores it into a scratch database, counts the ships, and asserts the count
 matches the live database. Then it corrupts a copy and requires the restore to
 FAIL on it - because a restore test that passes a deliberately broken dump has
 proved nothing.

 ---------------------------------------------------------------------------
 THE SECRET
 ---------------------------------------------------------------------------
 PGPASSWORD is read from the environment and is NEVER written to a file, echoed,
 logged, passed on a command line, or included in any output. It is not even
 length-reported. If it is absent this script REFUSES to run rather than
 prompting, because a prompt on an unattended console hangs forever.

 ---------------------------------------------------------------------------
 WHY THE CORRUPTION CONTROL TARGETS THE DATA SECTION
 ---------------------------------------------------------------------------
 Measured on 2026-08-06 against a real 170,357-byte dump:

   corrupted region      pg_restore --list
   ------------------    -----------------
   header / magic        caught  (exit 1, "unsupported version")
   TOC                   caught  (exit 1, "could not read from input file")
   middle of data        NOT CAUGHT - exit 0, lists perfectly
   near end of data      NOT CAUGHT - exit 0, lists perfectly

 So a cheap `--list` integrity check would declare a dump with a shredded data
 section perfectly healthy. The control below corrupts the DATA SECTION
 specifically and drives it through a real pg_restore into a real database,
 because that is the only path that actually reads those bytes.

 ---------------------------------------------------------------------------
 DROPPING THE SCRATCH DATABASE
 ---------------------------------------------------------------------------
 Hard rule 3 forbids DROP DATABASE against a database this process did not
 create. Both scratch databases here ARE created by this process, in this run,
 and are dropped only through Remove-ScratchDb, which refuses any name that
 does not match the generated prefix AND was not recorded as created by this
 run. The live database name is additionally denied by name.

 Exit codes: 0 = verified   1 = failed   2 = could not run (never a pass)
==============================================================================
#>

[CmdletBinding()]
param(
    [string]   $RepoPath    = 'C:\Users\david\citizen-compass',
    [string]   $DbName      = 'citizen_compass',
    [string]   $DbUser      = 'postgres',
    [string]   $DbHost      = '127.0.0.1',
    [int]      $DbPort      = 5432,
    [string]   $BackupRoot  = 'C:\cc-backup',
    [string[]] $MirrorRoots = @('D:\cc-backup','E:\cc-backup'),
    [string]   $Stamp
)

$ErrorActionPreference = 'Stop'

function Head { param($m) Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Good { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Bad  { param($m) Write-Host "  [FAIL] $m" -ForegroundColor Red }
function Note { param($m) Write-Host "  [NOTE] $m" -ForegroundColor Yellow }
function Say  { param($m) Write-Host "  $m" -ForegroundColor Gray }

$problems = 0
$script:CreatedDbs = @()

# Run a native tool without letting PowerShell 5.1 turn its stderr into a
# terminating error. Success is judged by exit code ONLY - pg_restore and
# pg_dump both write ordinary progress to stderr.
function Invoke-Native {
    param([Parameter(Mandatory)][scriptblock]$Command)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & $Command 2>&1 | ForEach-Object { [string]$_ } }
    finally { $ErrorActionPreference = $prev }
}

function Invoke-Psql {
    param([string]$Db, [string]$Sql)
    $out = Invoke-Native { psql -h $DbHost -p $DbPort -U $DbUser -d $Db -t -A -c $Sql }
    return [pscustomobject]@{ Code = $LASTEXITCODE; Text = ($out | Out-String).Trim() }
}

# --------------------------------------------------------------------------
# Guarded drop. This is the only destructive operation in the file.
# --------------------------------------------------------------------------
function Remove-ScratchDb {
    param([Parameter(Mandatory)][string]$Name)

    if ($Name -eq $DbName) {
        Bad "REFUSING to drop '$Name' - that is the LIVE database"
        $script:problems++
        return
    }
    if ($Name -notmatch '^cc_restore_test_[0-9a-z_]+$') {
        Bad "REFUSING to drop '$Name' - name does not match the scratch pattern"
        $script:problems++
        return
    }
    if ($script:CreatedDbs -notcontains $Name) {
        Bad "REFUSING to drop '$Name' - this run did not create it"
        $script:problems++
        return
    }

    Invoke-Native { psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c ('DROP DATABASE IF EXISTS "' + $Name + '";') } | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Good "scratch database dropped: $Name"
        $script:CreatedDbs = $script:CreatedDbs | Where-Object { $_ -ne $Name }
    } else {
        Bad "could not drop scratch database $Name (exit $LASTEXITCODE) - drop it by hand"
        $script:problems++
    }
}

function New-ScratchDb {
    param([string]$Name)
    Invoke-Native { psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c ('CREATE DATABASE "' + $Name + '";') } | Out-Null
    if ($LASTEXITCODE -ne 0) { return $false }
    $script:CreatedDbs += $Name
    return $true
}

# ==========================================================================
# PREFLIGHT - fail closed
# ==========================================================================
Head 'PREFLIGHT'

if (-not $env:PGPASSWORD) {
    Bad 'PGPASSWORD is not set in this process environment.'
    Say 'Refusing to run. This script never prompts (a prompt on an unattended'
    Say 'console hangs forever) and never reads a password from a file.'
    Say ''
    Say 'Set it in the shell that LAUNCHES Claude Code, then restart it:'
    Say '    $env:PGPASSWORD = ''...''   ; claude'
    Say 'A variable set in another terminal cannot reach this process - Windows'
    Say 'builds a child environment from its parent, not from the registry.'
    exit 2
}
Good 'PGPASSWORD present in environment (value never displayed or written)'

foreach ($tool in @('pg_dump','pg_restore','psql')) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) { Good "$tool available" }
    else { Bad "$tool NOT on PATH"; exit 2 }
}

$live = Invoke-Psql -Db $DbName -Sql 'SELECT COUNT(*) FROM ships;'
if ($live.Code -ne 0 -or $live.Text -notmatch '^\d+$') {
    Bad "could not count ships in the LIVE database: $($live.Text)"
    exit 2
}
$liveCount = [int]$live.Text
Good "live database '$DbName' holds $liveCount ships"

if (-not $Stamp) { $Stamp = Get-Date -Format 'yyyyMMdd-HHmmss' }
$backupDir = Join-Path $BackupRoot $Stamp
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$dumpPath = Join-Path $backupDir "$DbName-$Stamp.dump"

# ==========================================================================
# 1. DUMP
# ==========================================================================
Head '1. DUMP'
Invoke-Native { pg_dump -h $DbHost -p $DbPort -U $DbUser -d $DbName -Fc -f $dumpPath } |
    ForEach-Object { Say $_ }
if ($LASTEXITCODE -ne 0) { Bad "pg_dump exited $LASTEXITCODE"; exit 1 }
if (-not (Test-Path -LiteralPath $dumpPath)) { Bad 'pg_dump produced no file'; exit 1 }

$dumpBytes = (Get-Item $dumpPath).Length
Good ("dump written: {0} ({1:N0} bytes, {2:N2} MB)" -f (Split-Path -Leaf $dumpPath), $dumpBytes, ($dumpBytes/1MB))

# ==========================================================================
# 2. RESTORE IT - the whole point
# ==========================================================================
Head '2. RESTORE INTO A SCRATCH DATABASE'
$scratch = "cc_restore_test_$($Stamp -replace '-','_')"
if (-not (New-ScratchDb $scratch)) { Bad "could not create scratch database $scratch"; exit 1 }
Good "created scratch database: $scratch"

Invoke-Native { pg_restore -h $DbHost -p $DbPort -U $DbUser -d $scratch $dumpPath } | ForEach-Object { Say $_ }
$restoreCode = $LASTEXITCODE
if ($restoreCode -ne 0) { Note "pg_restore exited $restoreCode - the ship count below is the real test" }

$rest = Invoke-Psql -Db $scratch -Sql 'SELECT COUNT(*) FROM ships;'
if ($rest.Code -ne 0 -or $rest.Text -notmatch '^\d+$') {
    Bad "could not count ships in the restored database: $($rest.Text)"
    $problems++
    $restoredCount = -1
} else {
    $restoredCount = [int]$rest.Text
    if ($restoredCount -eq $liveCount) {
        Good "RESTORE VERIFIED: restored $restoredCount ships, live has $liveCount - MATCH"
    } else {
        Bad "COUNT MISMATCH: live $liveCount, restored $restoredCount"
        $problems++
    }
}

# ==========================================================================
# 3. NEGATIVE CONTROL - a corrupted dump MUST fail to restore
# ==========================================================================
Head '3. NEGATIVE CONTROL - corrupt a copy, require the restore to FAIL'

$badDump = Join-Path $env:TEMP "cc-corrupt-$Stamp.dump"
Copy-Item -LiteralPath $dumpPath -Destination $badDump -Force

# Corrupt the DATA SECTION, not the header. A header/TOC corruption is caught
# by pg_restore --list alone and would not prove the RESTORE path does any
# work. Measured 2026-08-06: mid-data corruption passes --list with exit 0.
$fs = [System.IO.File]::Open($badDump, 'Open', 'ReadWrite')
try {
    $mid = [int]($fs.Length / 2)
    $fs.Position = $mid
    $buf = New-Object byte[] 2048
    $read = $fs.Read($buf, 0, $buf.Length)
    for ($i = 0; $i -lt $read; $i++) { $buf[$i] = $buf[$i] -bxor 0xFF }
    $fs.Position = $mid
    $fs.Write($buf, 0, $read)
} finally { $fs.Close() }
Say "corrupted $read bytes at offset $mid of a COPY (the real dump is untouched)"

$scratchBad = "cc_restore_test_$($Stamp -replace '-','_')_neg"
if (-not (New-ScratchDb $scratchBad)) {
    Bad "could not create the negative-control database - control NOT PERFORMED"
    $problems++
} else {
    Invoke-Native { pg_restore -h $DbHost -p $DbPort -U $DbUser -d $scratchBad $badDump } | Out-Null
    $badCode = $LASTEXITCODE

    $badCount = -1
    $bc = Invoke-Psql -Db $scratchBad -Sql 'SELECT COUNT(*) FROM ships;'
    if ($bc.Code -eq 0 -and $bc.Text -match '^\d+$') { $badCount = [int]$bc.Text }

    # The control FIRES if the restore errored, or the data did not survive.
    # Both are the corruption being detected; either is a pass for the control.
    if ($badCode -ne 0) {
        Good "CONTROL FIRED: pg_restore rejected the corrupted dump (exit $badCode)"
        if ($badCount -ge 0 -and $badCount -ne $liveCount) {
            Say "and the wreckage holds $badCount ships, not $liveCount"
        }
    } elseif ($badCount -ne $liveCount) {
        Good "CONTROL FIRED: corrupted dump restored 'clean' but yielded $badCount ships, not $liveCount"
    } else {
        Bad 'CONTROL DID NOT FIRE - a deliberately corrupted dump restored perfectly.'
        Say 'The restore test therefore proves nothing and this run is VOID.'
        $problems++
    }
}

# ==========================================================================
# 4. DROP THE SCRATCH DATABASES
# ==========================================================================
Head '4. DROP THE SCRATCH DATABASES'
foreach ($n in @($script:CreatedDbs)) { Remove-ScratchDb -Name $n }
Remove-Item -LiteralPath $badDump -Force -ErrorAction SilentlyContinue

# ==========================================================================
# 5. COPY TO BOTH MIRRORS AND VERIFY PER FILE
# ==========================================================================
Head '5. MIRROR THE DUMP AND VERIFY PER FILE'

$srcHash = (Get-FileHash -LiteralPath $dumpPath -Algorithm SHA256).Hash
Say "source: $(Split-Path -Leaf $dumpPath)  $dumpBytes bytes  sha256 $($srcHash.Substring(0,16))..."

foreach ($mr in $MirrorRoots) {
    $label = $mr.Substring(0,2)
    if (-not (Test-Path -LiteralPath $mr.Substring(0,3))) {
        Bad "$label not present - dump NOT mirrored there (never reported as done)"
        $problems++
        continue
    }
    $dstDir = Join-Path $mr $Stamp
    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    $dst = Join-Path $dstDir (Split-Path -Leaf $dumpPath)

    Copy-Item -LiteralPath $dumpPath -Destination $dst -Force

    # Verified from DISK at the destination: existence, byte size, then hash.
    # A size match alone would miss silent corruption in transit.
    if (-not (Test-Path -LiteralPath $dst)) {
        Bad "$label : dump missing after copy"; $problems++; continue
    }
    $dstBytes = (Get-Item $dst).Length
    $dstHash  = (Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash

    if ($dstBytes -ne $dumpBytes) {
        Bad ("{0} : SIZE MISMATCH  source {1:N0} B -> dest {2:N0} B" -f $label, $dumpBytes, $dstBytes)
        $problems++
    } elseif ($dstHash -ne $srcHash) {
        Bad "$label : HASH MISMATCH - same size, different content"
        $problems++
    } else {
        Good ("{0} : {1}  {2:N0} bytes  sha256 matches" -f $label, (Split-Path -Leaf $dst), $dstBytes)
    }
}

# ==========================================================================
Head 'SUMMARY'
Say "dump           : $dumpPath"
Say ("dump size      : {0:N0} bytes ({1:N2} MB)" -f $dumpBytes, ($dumpBytes/1MB))
Say "ships live     : $liveCount"
Say "ships restored : $restoredCount"

if ($problems -eq 0) {
    Good 'database dumped, RESTORED, counted, mirrored and verified per file'
    exit 0
}
Bad "$problems problem(s) - this is NOT a verified database backup"
exit 1
