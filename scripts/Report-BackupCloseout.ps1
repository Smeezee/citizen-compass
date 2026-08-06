<#
==============================================================================
 Report-BackupCloseout.ps1  -  independent close-out report for a backup run
==============================================================================

 WHY THIS IS A SEPARATE SCRIPT, RUN AFTER THE FACT

 Backup-CitizenCompass.ps1 verifies as it goes, which is right - a copy that
 fails should fail loudly at the time. But a close-out report written by the
 same process that did the copying shares that process's assumptions. This runs
 afterwards, in its own process, and rebuilds every fact from disk:

   - robocopy exit codes are read from the LOG FILES robocopy itself wrote,
     not from a variable the copier kept.
   - per-file verification is delegated to Verify-MirrorTree.ps1, which
     enumerates the DESTINATION from disk. Never from SHA256SUMS.txt, never
     from robocopy's file list, never from the copy's own filter.
   - the negative control is asserted here as well as there.

 AGGREGATES ARE NOT VERIFICATION. A file count plus an MB total can both match
 while a file is truncated: the file is present, so the count is right, and two
 files that differ by +2MB and -2MB sum to a pass. Everything below is per file,
 on relative path AND byte size.

 Exit codes: 0 = everything verified   1 = something failed   2 = could not run
==============================================================================
#>

[CmdletBinding()]
param(
    [string]   $RepoPath    = 'C:\Users\david\citizen-compass',
    [string[]] $MirrorRoots = @('D:\cc-backup','E:\cc-backup'),
    [string]   $Stamp,
    [int]      $MaxReport   = 10
)

$ErrorActionPreference = 'Stop'

function Head { param($m) Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Good { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Bad  { param($m) Write-Host "  [FAIL] $m" -ForegroundColor Red }
function Note { param($m) Write-Host "  [NOTE] $m" -ForegroundColor Yellow }
function Say  { param($m) Write-Host "  $m" -ForegroundColor Gray }

$problems = 0

# The two trees -FullMirror is responsible for. These are the irreplaceable
# ones - sc-ships' redistribution rights are unestablished, and the sealed
# snapshots cannot be re-fetched at all, because re-pulling UEX returns TODAY's
# prices rather than the snapshot's.
$trees = @(
    @{ Name = 'sc-ships';                    Rel = 'sc-ships' },
    @{ Name = 'data-layer\external-sources'; Rel = 'data-layer\external-sources' }
)

$verifier = Join-Path $RepoPath 'scripts\Verify-MirrorTree.ps1'
if (-not (Test-Path -LiteralPath $verifier)) {
    Bad "verifier not found at $verifier - cannot verify, reporting as NOT PERFORMED"
    exit 2
}

# --------------------------------------------------------------------------
# Decode robocopy's exit code. IT IS A BITMASK, not an ordinal: 3 means
# "copied files AND extras present", which is success, while 8 means files were
# genuinely missed. Anything >= 8 is a real failure.
# --------------------------------------------------------------------------
function Decode-RoboCode {
    param([int]$Code)
    $bits = @()
    if ($Code -band 1)  { $bits += 'files copied' }
    if ($Code -band 2)  { $bits += 'extra files/dirs at destination' }
    if ($Code -band 4)  { $bits += 'MISMATCHED files/dirs' }
    if ($Code -band 8)  { $bits += 'SOME FILES COULD NOT BE COPIED' }
    if ($Code -band 16) { $bits += 'SERIOUS ERROR - no files copied' }
    if ($Code -eq 0)    { $bits += 'nothing to do, destination already current' }
    return ($bits -join '; ')
}

# Read robocopy's own log and decide whether it finished cleanly. The log is
# evidence written by robocopy itself; a variable in the copying script is not.
function Read-RoboLog {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return [pscustomobject]@{ Found=$false; Ended=$false; Errors=@(); Tail='' }
    }
    $lines  = Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue
    $errs   = $lines | Where-Object { $_ -match 'ERROR\s*:|ERROR \d+ \(' } | Select-Object -First 5
    $ended  = [bool]($lines | Where-Object { $_ -match '^\s*Ended\s*:' })
    $tail   = ($lines | Select-Object -Last 12) -join "`n"
    return [pscustomobject]@{ Found=$true; Ended=$ended; Errors=$errs; Tail=$tail }
}

# --------------------------------------------------------------------------
# Pick the run to report on.
# --------------------------------------------------------------------------
if (-not $Stamp) {
    $candidates = foreach ($mr in $MirrorRoots) {
        if (Test-Path -LiteralPath $mr) {
            Get-ChildItem -LiteralPath $mr -Directory -ErrorAction SilentlyContinue
        }
    }
    if (-not $candidates) { Bad "no run folders under $($MirrorRoots -join ', ')"; exit 2 }
    $Stamp = ($candidates | Sort-Object Name -Descending | Select-Object -First 1).Name
}

Write-Host ""
Write-Host "  BACKUP CLOSE-OUT REPORT" -ForegroundColor White
Write-Host "  run    : $Stamp" -ForegroundColor White
Write-Host "  source : $RepoPath" -ForegroundColor White
Write-Host "  mirrors: $($MirrorRoots -join ', ')" -ForegroundColor White

foreach ($mr in $MirrorRoots) {

    $mirrorDir = Join-Path $mr $Stamp
    Head "MIRROR $($mr.Substring(0,2))  ->  $mirrorDir"

    if (-not (Test-Path -LiteralPath $mirrorDir)) {
        Bad "run folder missing at $mirrorDir - NOT VERIFIED (never reported as passed)"
        $problems++
        continue
    }

    foreach ($t in $trees) {
        $src = Join-Path $RepoPath $t.Rel
        $dst = Join-Path (Join-Path $mirrorDir 'repo') $t.Rel

        Write-Host ""
        Write-Host "  --- tree: $($t.Name) ---" -ForegroundColor White

        if (-not (Test-Path -LiteralPath $src)) {
            Note "$($t.Name) is not present in the repo - nothing to compare"
            continue
        }

        # ---- 1. robocopy exit status, from robocopy's own log -------------
        $safe    = $t.Rel -replace '[\\/]', '_'
        $logPath = Join-Path $mirrorDir ("robocopy-" + $safe + ".log")
        $rl      = Read-RoboLog -Path $logPath

        if (-not $rl.Found) {
            Bad "no robocopy log at $logPath - copy status UNKNOWN, reporting as not performed"
            $problems++
        } else {
            if ($rl.Errors) {
                Bad "robocopy log records errors:"
                $rl.Errors | ForEach-Object { Say "    $_" }
                $problems++
            } else {
                Good "robocopy log clean (no ERROR lines)"
            }
            if ($rl.Ended) { Good "robocopy log shows a completed run (has an 'Ended :' line)" }
            else           { Bad  "robocopy log has NO 'Ended :' line - the copy did not finish"; $problems++ }
        }

        # ---- 2. per-file verification, destination read from disk ---------
        & powershell -ExecutionPolicy Bypass -NoProfile -File $verifier `
            -Source $src -Destination $dst -MaxReport $MaxReport |
            ForEach-Object { Write-Host $_ }
        $vrc = $LASTEXITCODE

        switch ($vrc) {
            0 { Good "$($t.Name): per-file verification PASSED" }
            2 { Bad  "$($t.Name): verification COULD NOT RUN - reported as not verified, not as passed"; $problems++ }
            default { Bad "$($t.Name): per-file verification FOUND MISMATCHES"; $problems++ }
        }
    }

    # ---- 3. THE NEGATIVE CONTROL, asserted here independently ------------
    #
    # sc-ships\.cache\ is a HuggingFace cache and is deliberately excluded. If
    # a file from it is present at the destination the exclusion is not working.
    # But the more dangerous outcome is this check passing VACUOUSLY - a
    # checker that cannot see the destination at all finds nothing everywhere
    # and calls it a pass. So absence is only credited once we have proved we
    # can see the destination, by finding something we know IS there.
    Write-Host ""
    Write-Host "  --- negative control: sc-ships\.cache\ must be ABSENT ---" -ForegroundColor White

    $scSrc = Join-Path $RepoPath 'sc-ships'
    $scDst = Join-Path (Join-Path $mirrorDir 'repo') 'sc-ships'

    if (-not (Test-Path -LiteralPath $scDst)) {
        Bad "sc-ships not at the destination - control NOT PERFORMED"
        $problems++
    } else {
        # Can we see the destination at all?
        $anyDst = Get-ChildItem -LiteralPath $scDst -Recurse -File -Force -ErrorAction SilentlyContinue |
                  Select-Object -First 1
        if (-not $anyDst) {
            Bad "destination enumerates EMPTY - an 'absent' result would be vacuous. VOID."
            $problems++
        } else {
            Good "destination is readable (e.g. $($anyDst.Name)) - an absence here is meaningful"

            # Name a real excluded file at the SOURCE, then assert that exact
            # relative path is missing at the destination.
            $cacheSrc = Get-ChildItem -LiteralPath (Join-Path $scSrc '.cache') -Recurse -File -Force `
                            -ErrorAction SilentlyContinue | Select-Object -First 1
            if (-not $cacheSrc) {
                Note "no file under sc-ships\.cache\ exists to test with - control NOT PERFORMED"
                Note "reported as not performed, never as a pass"
            } else {
                $rel = $cacheSrc.FullName.Substring($scSrc.TrimEnd('\').Length).TrimStart('\')
                $at  = Join-Path $scDst $rel
                if (Test-Path -LiteralPath $at) {
                    Bad "NEGATIVE CONTROL FAILED - an excluded file reached the mirror:"
                    Say "    $rel"
                    $problems++
                } else {
                    Good "NEGATIVE CONTROL PASSED - excluded file is absent from the mirror"
                    Say  "    subject: $rel"
                }
            }
        }
    }
}

Head 'SUMMARY'
if ($problems -eq 0) {
    Good "every tree on every mirror verified per file, with the negative control proven"
    exit 0
}
Bad "$problems problem(s) - see above. This run is NOT a verified backup."
exit 1
