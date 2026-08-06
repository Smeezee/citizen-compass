<#
==============================================================================
 Verify-MirrorTree.ps1  -  per-file verification of a copied tree
==============================================================================

 WHY THIS EXISTS

 The previous check compared an aggregate file COUNT and an aggregate MB total.
 That is not a verification, for two independent reasons:

   1. AGGREGATES CANCEL. Two files that differ by +2 MB and -2 MB sum to a
      pass. A count plus a total can both match while the contents are wrong.

   2. A TRUNCATED FILE IS INVISIBLE TO A COUNT. The 2026-08-05 run was killed
      mid-copy. Whatever file robocopy had open at that instant is short on the
      destination. It is present, so the count matches. It is the exact failure
      that run produced, so it is the exact failure this check must catch.

 AND IT MUST NOT BE TAUTOLOGICAL

 If a checker builds its expected file list using the same filter code that
 drove the copy, it is comparing the copy to itself and cannot fail. So:

   - the DESTINATION is enumerated independently, from disk. Never from
     SHA256SUMS.txt, never from robocopy's own log, never from the copy's
     file list.
   - comparison is PER FILE, on relative path AND byte size.
   - the first N mismatches are named, with both sizes, not merely counted.

 TWO CONTROLS, because a checker that reads nothing passes everything:

   POSITIVE - a file known to be INCLUDED must be found at the destination.
              If this fails, the destination enumeration is broken or empty.
   NEGATIVE - a file known to be EXCLUDED (something under .cache) must be
              ABSENT from the destination. If this passes when the checker
              cannot actually see the destination, it passes vacuously - so it
              is only credited when the positive control passed too, and it is
              reported as NOT PERFORMED when no excluded file exists to test
              with. An untested control is never reported as a pass.

 Exit codes:  0 = verified   1 = mismatches found   2 = could not verify
==============================================================================
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string] $Source,
    [Parameter(Mandatory)][string] $Destination,
    # Directory NAMES excluded by the copy, matched at any depth.
    [string[]] $ExcludedDirNames = @('venv','__pycache__','.cache','node_modules'),
    [int] $MaxReport = 10
)

$ErrorActionPreference = 'Stop'

function Say  { param($m) Write-Host "  $m" -ForegroundColor Gray }
function Good { param($m) Write-Host "  [OK]   $m" -ForegroundColor Green }
function Bad  { param($m) Write-Host "  [FAIL] $m" -ForegroundColor Red }
function Note { param($m) Write-Host "  [NOTE] $m" -ForegroundColor Yellow }

if (-not (Test-Path -LiteralPath $Source))      { Bad "source not found: $Source";      exit 2 }
if (-not (Test-Path -LiteralPath $Destination)) { Bad "destination not found: $Destination"; exit 2 }

Write-Host ""
Write-Host "Verify-MirrorTree" -ForegroundColor Cyan
Say "source      : $Source"
Say "destination : $Destination"
Say "excluding   : $($ExcludedDirNames -join ', ')"

function Get-RelMap {
    <# Enumerate a tree from DISK into relpath -> size. #>
    param([string]$Root)
    $root = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
    $map  = @{}
    Get-ChildItem -LiteralPath $root -Recurse -File -Force -ErrorAction SilentlyContinue |
        ForEach-Object {
            $rel = $_.FullName.Substring($root.Length).TrimStart('\')
            $map[$rel] = $_.Length
        }
    return $map
}

function Test-IsExcluded {
    param([string]$Rel, [string[]]$Names)
    foreach ($n in $Names) {
        # match the name as a whole path SEGMENT, so a file called
        # "my.cache.json" is not mistaken for something inside .cache\
        if ($Rel -match "(^|\\)$([regex]::Escape($n))(\\|$)") { return $true }
    }
    return $false
}

Say "enumerating destination from disk ..."
$dst = Get-RelMap -Root $Destination
Say "enumerating source from disk ..."
$src = Get-RelMap -Root $Source

Say "destination holds $($dst.Count) files; source holds $($src.Count) files (unfiltered)"

# --------------------------------------------------------------------------
# Classify the source
# --------------------------------------------------------------------------
$expected = @{}   # should be at the destination
$excluded = @{}   # should NOT be
foreach ($rel in $src.Keys) {
    if (Test-IsExcluded -Rel $rel -Names $ExcludedDirNames) { $excluded[$rel] = $src[$rel] }
    else                                                    { $expected[$rel] = $src[$rel] }
}
Say "source classifies as $($expected.Count) expected + $($excluded.Count) excluded"

# --------------------------------------------------------------------------
# CONTROLS FIRST. If the checker cannot see the destination, nothing below it
# means anything, so this is established before any verdict is issued.
# --------------------------------------------------------------------------
Write-Host ""
Write-Host "  controls" -ForegroundColor Cyan

$positiveOk = $false
$positiveSubject = $null
if ($expected.Count -gt 0) {
    # Largest expected file: most likely to exist, and the most useful single
    # subject because a truncation would show up on it.
    $positiveSubject = ($expected.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
    if ($dst.ContainsKey($positiveSubject)) {
        $positiveOk = $true
        Good "POSITIVE control: an included file IS present at the destination"
        Say  "         subject: $positiveSubject"
    } else {
        Bad "POSITIVE control FAILED: '$positiveSubject' is missing from the destination."
        Say "         The destination enumeration is empty, wrong, or pointed at the wrong path."
        Say "         No verdict below can be trusted."
    }
} else {
    Note "POSITIVE control NOT PERFORMED - the source has no non-excluded files"
}

$negativeState = 'not_performed'
if ($excluded.Count -eq 0) {
    Note "NEGATIVE control NOT PERFORMED - no excluded file exists to test with"
    Say  "         Reported as not performed, never as a pass."
} elseif (-not $positiveOk) {
    Note "NEGATIVE control NOT CREDITED - the positive control did not pass, so an"
    Say  "         'absent' result here would be vacuous rather than meaningful."
} else {
    $negSubject = ($excluded.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
    if ($dst.ContainsKey($negSubject)) {
        $negativeState = 'failed'
        Bad "NEGATIVE control FAILED: an excluded file reached the destination"
        Say "         subject: $negSubject"
    } else {
        $negativeState = 'passed'
        Good "NEGATIVE control: a known-excluded file is absent from the destination"
        Say  "         subject: $negSubject"
    }
}

# --------------------------------------------------------------------------
# PER-FILE comparison
# --------------------------------------------------------------------------
Write-Host ""
Write-Host "  per-file comparison" -ForegroundColor Cyan

$missing   = New-Object System.Collections.ArrayList
$truncated = New-Object System.Collections.ArrayList
$orphan    = New-Object System.Collections.ArrayList

foreach ($rel in $expected.Keys) {
    if (-not $dst.ContainsKey($rel)) {
        [void]$missing.Add([pscustomobject]@{ Path = $rel; Source = $expected[$rel] })
    }
    elseif ($dst[$rel] -ne $expected[$rel]) {
        # Size difference on a file that IS present. This is the truncation
        # signature a count check cannot see.
        [void]$truncated.Add([pscustomobject]@{
            Path = $rel; Source = $expected[$rel]; Dest = $dst[$rel]
            Delta = $dst[$rel] - $expected[$rel]
        })
    }
}

foreach ($rel in $dst.Keys) {
    if (-not $src.ContainsKey($rel)) {
        [void]$orphan.Add([pscustomobject]@{ Path = $rel; Dest = $dst[$rel] })
    }
}

function Show-Sample {
    param($items, [string]$label, [scriptblock]$fmt)
    if ($items.Count -eq 0) { return }
    Bad "$label : $($items.Count)"
    $items | Select-Object -First $MaxReport | ForEach-Object { Say ("    " + (& $fmt $_)) }
    if ($items.Count -gt $MaxReport) { Say "    ... and $($items.Count - $MaxReport) more" }
}

Show-Sample $missing 'MISSING from destination' {
    param($i) "{0}  ({1:N0} B at source)" -f $i.Path, $i.Source }

Show-Sample $truncated 'SIZE MISMATCH (truncated or corrupt)' {
    param($i) "{0}  source {1:N0} B -> dest {2:N0} B  ({3:+#;-#;0} B)" -f $i.Path, $i.Source, $i.Dest, $i.Delta }

Show-Sample $orphan 'AT DESTINATION BUT NOT AT SOURCE' {
    param($i) "{0}  ({1:N0} B)" -f $i.Path, $i.Dest }

$verifiedCount = $expected.Count - $missing.Count - $truncated.Count
if ($missing.Count -eq 0 -and $truncated.Count -eq 0) {
    Good "all $($expected.Count) expected files present with matching byte sizes"
} else {
    Say "$verifiedCount of $($expected.Count) expected files verified byte-for-byte by size"
}

# --------------------------------------------------------------------------
Write-Host ""
$fatal = ($missing.Count -gt 0) -or ($truncated.Count -gt 0) -or
         (-not $positiveOk) -or ($negativeState -eq 'failed')

if ($fatal) {
    Bad "VERIFY FAILED"
    exit 1
}
if ($negativeState -ne 'passed') {
    Note "VERIFY PASSED, but the negative control was $negativeState - stated, not glossed."
    exit 0
}
Good "VERIFY PASSED - per-file, with both controls proven"
exit 0
