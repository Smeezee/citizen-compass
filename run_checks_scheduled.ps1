<#
==============================================================================
 run_checks_scheduled.ps1
==============================================================================
 The single entry point for the scheduled auditor run (Path C, Part D).

 ONE SCRIPT, ONE TASK. This project has twice lost work to two writers on one
 target - two handoff generators on LATEST_HANDOFF.md, and two sessions on one
 layer. So exactly one scheduled task calls this, and this decides what runs
 today. Adding a second task is the failure mode, not the feature.

 SCHEDULE
   file    - every day. Cheap, stdlib only.
   db      - every day, after file.
   sources - weekly (Sunday). snapshot_integrity re-hashes every sealed
             snapshot; source 1 alone is 4.5 GB across ~29,000 files.
   network - weekly (Sunday). Runs pip-audit, which does not need to be daily.

 TWO ENVIRONMENT SETTINGS THAT ARE NOT OPTIONAL
 ----------------------------------------------
 Both were found the hard way during this order, and a scheduled run has no
 console to show either failure on:

   PYTHONIOENCODING=utf-8
     Without it the run DIES on the first non-ASCII ship name. The first full
     lifecycle run crashed with UnicodeEncodeError on the macron in tok.yai.
     This is the FIFTH time cp1252 has broken this pipeline, and the first on
     stdout rather than a file open - so hard rule 14 does not cover it.

   PATH must include venv\Scripts
     schema_drift shells out to `alembic`. If alembic is not on PATH the
     checker returns LIMITATION - "not available" - instead of DEFECT, so a
     REAL schema drift silently stops being reported while the run still looks
     healthy. That is a silent success, and scheduling it without this line
     would have manufactured one daily.

 A RUN THAT FINDS NOTHING STILL LOGS THAT IT RAN. A dead scheduler and a clean
 bill of health must never look the same.
==============================================================================
#>

[CmdletBinding()]
param(
    [string] $ProjectPath = 'C:\Users\david\citizen-compass',
    # Override to force the weekly groups on a day that is not Sunday.
    [switch] $IncludeWeekly,
    [switch] $WeeklyOnly
)

$ErrorActionPreference = 'Continue'

$python  = Join-Path $ProjectPath 'venv\Scripts\python.exe'
$logDir  = Join-Path $ProjectPath 'logs'
$logFile = Join-Path $logDir 'checks_scheduled.log'

if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

function Write-Log([string] $msg) {
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    # Encoding is stated here for the same reason it is stated everywhere else
    # in this project - ship names are not ASCII.
    Add-Content -Path $logFile -Value $line -Encoding utf8
    Write-Output $line
}

Write-Log "=== scheduled auditor run starting (pid $PID) ==="

if (-not (Test-Path $python)) {
    Write-Log "FATAL: python not found at $python - nothing ran."
    exit 1
}

# See the header. Neither of these is optional.
$env:PYTHONIOENCODING = 'utf-8'
$env:PATH = (Join-Path $ProjectPath 'venv\Scripts') + ';' + $env:PATH

$isSunday = (Get-Date).DayOfWeek -eq 'Sunday'
$runWeekly = $IncludeWeekly -or $WeeklyOnly -or $isSunday

$groups = @()
if (-not $WeeklyOnly) { $groups += 'file'; $groups += 'db' }
if ($runWeekly)       { $groups += 'sources'; $groups += 'network' }

Write-Log ("groups this run: {0} (weekly groups {1})" -f ($groups -join ', '),
           $(if ($runWeekly) { 'included' } else { 'skipped - not Sunday' }))

$overallStart = Get-Date
$failed = @()

foreach ($g in $groups) {
    $start = Get-Date
    Write-Log "--- group '$g' starting ---"

    $output = & $python (Join-Path $ProjectPath 'run_checks.py') `
        --group $g --source-process "run_checks_scheduled.ps1" 2>&1
    $code = $LASTEXITCODE
    $elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)

    # run_checks.py exits 1 when it FOUND a DEFECT. That is the checker doing
    # its job, not the run failing, so the two are logged differently - a
    # findings-only layer that treated findings as errors would train everyone
    # to ignore its exit code.
    $summary = ($output | Select-String -Pattern '^\d+ findings:' | Select-Object -First 1)
    $lifecycle = ($output | Select-String -Pattern '^\s+lifecycle:' | Select-Object -First 1)
    $checkers  = ($output | Select-String -Pattern '^\s+checkers:'  | Select-Object -First 1)

    if ($summary)   { Write-Log ("group '$g' " + $summary.ToString().Trim()) }
    else            { Write-Log "group '$g' produced no findings summary line" }
    if ($checkers)  { Write-Log ("group '$g'" + $checkers.ToString().TrimEnd()) }
    if ($lifecycle) { Write-Log ("group '$g'" + $lifecycle.ToString().TrimEnd()) }

    if ($code -eq 0) {
        Write-Log "group '$g' completed in ${elapsed}s - no DEFECT"
    } elseif ($code -eq 1) {
        Write-Log "group '$g' completed in ${elapsed}s - DEFECTs present (exit 1, expected when findings exist)"
    } else {
        $failed += $g
        Write-Log "group '$g' FAILED in ${elapsed}s with exit code $code"
        $tail = ($output | Select-Object -Last 12) -join ' | '
        Write-Log "group '$g' last output: $tail"
    }
}

$total = [math]::Round(((Get-Date) - $overallStart).TotalSeconds, 1)

if ($failed.Count -gt 0) {
    Write-Log "=== run finished in ${total}s - $($failed.Count) group(s) FAILED: $($failed -join ', ') ==="
    exit 2
}

Write-Log "=== run finished in ${total}s - all $($groups.Count) group(s) completed ==="
exit 0
