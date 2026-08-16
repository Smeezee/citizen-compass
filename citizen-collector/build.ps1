# build.ps1 - build the collector, with the flag that was missing for months.
#
#   powershell -ExecutionPolicy Bypass -File .\build.ps1
#   powershell -ExecutionPolicy Bypass -File .\build.ps1 -Master
#   powershell -ExecutionPolicy Bypass -File .\build.ps1 -Both
#
# ---------------------------------------------------------------------------
# WHY THIS FILE EXISTS
# ---------------------------------------------------------------------------
#
# Seven source files said this program is built `-H windowsgui`. No build
# command anywhere passed it. `grep windowsgui` across every .ps1 returned
# nothing, and both shipped binaries carried subsystem 3 - CONSOLE.
#
# Subsystem 3 means Windows creates a console for every launch. On Windows 11
# that console is Windows Terminal, which is the black box with a tab named
# "Citizen Collector" that Sleven photographed four times in one day. It is also
# why closing it killed the collector: closing a console terminates the process
# attached to it.
#
# Everyone read the comment and believed it. The comment was the defect.
#
# So the flag now lives in a script rather than in a README instruction that
# people retype from memory, and make-release.ps1 READS THE SUBSYSTEM BYTE out
# of the finished binary and refuses to publish anything that is not 2. A
# comment claiming a property is exactly what hid its absence; the check reads
# the artifact.

param(
    [switch] $Master,
    [switch] $Both
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $here

function Fail($m) { Write-Host ""; Write-Host "REFUSED: $m" -ForegroundColor Red; Pop-Location; exit 1 }
function Ok($m)   { Write-Host "   ok   $m" -ForegroundColor Green }
function Step($m) { Write-Host ""; Write-Host "== $m" -ForegroundColor Cyan }

# THE FLAG. -H=windowsgui sets the PE subsystem to 2 (GUI), so Windows creates
# no console. Everything else about the build is unchanged.
$guiFlag = "-H=windowsgui"

function Build($tags, $out) {
    Step "building $out"
    if ($tags) {
        & go build -tags $tags -ldflags $guiFlag -o $out .
    } else {
        & go build -ldflags $guiFlag -o $out .
    }
    if ($LASTEXITCODE -ne 0) { Fail "go build failed for $out" }

    $sub = Get-PESubsystem (Join-Path $here $out)
    if ($sub -ne 2) {
        Fail "$out was built with subsystem $sub, not 2 (GUI). It would open a console window on every launch."
    }
    Ok "$out  subsystem 2 (GUI) - no console window"
}

# Get-PESubsystem reads the byte, rather than trusting the flag was applied.
#
# The whole lesson of this defect is that an intention is not an outcome. The
# build asks the finished file what it actually is.
function Get-PESubsystem($path) {
    $fs = [IO.File]::OpenRead($path)
    try {
        $br = New-Object IO.BinaryReader($fs)
        $fs.Position = 0x3C
        $peOff = $br.ReadInt32()
        $fs.Position = $peOff
        if ($br.ReadUInt32() -ne 0x00004550) { throw "not a PE file: $path" }   # 'PE\0\0'
        # COFF header is 20 bytes; Subsystem sits 68 bytes into the optional header.
        $fs.Position = $peOff + 4 + 20 + 68
        return $br.ReadUInt16()
    } finally {
        $fs.Dispose()
    }
}

if ($Both) {
    Build $null "collector.exe"
    Build "master" "collector-master.exe"
} elseif ($Master) {
    Build "master" "collector-master.exe"
} else {
    Build $null "collector.exe"
}

Write-Host ""
Write-Host "Done. Verified by reading the subsystem byte out of the built file," -ForegroundColor Green
Write-Host "not by trusting that the flag was passed." -ForegroundColor Green
Pop-Location
