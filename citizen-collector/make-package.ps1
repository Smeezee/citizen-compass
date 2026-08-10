# make-package.ps1 - build the zip you hand to somebody else.
#
# Run this from the citizen-collector folder:
#     powershell -ExecutionPolicy Bypass -File .\make-package.ps1
#
# WHY A SCRIPT AND NOT A PREBUILT ZIP
#
# It builds from whatever collector.exe is sitting here right now, so it cannot
# ship a binary older than the one being tested. The button in the master
# window does the same job; this exists for when you would rather see it happen
# in a terminal.
#
# WHAT GOES IN, AND WHAT DELIBERATELY DOES NOT
#
#   collector.exe            the crew build. NOT collector-master.exe -
#                            that one has Sleven's own tools in it.
#   collector-settings.txt   a FRESH copy with defaults, not yours
#   README.txt               written for the person receiving it
#
# NOT included, on purpose:
#   captures\                     your screenshots
#   gamelog-dataset.json          your data
#   collector-install-id.txt      your contributor id - they must get their
#                                 own, or their reports would be counted as
#                                 yours and every agreement number would be
#                                 wrong
#   collector-scrub-salt.bin      your pseudonym salt
#   collector-consent.txt         your agreement is not theirs to inherit
#   collector-auto.log            your session history

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
$stamp = Get-Date -Format "yyyyMMdd"
$stage = Join-Path $env:TEMP "citizen-collector-package"
$dest  = Join-Path $here "citizen-collector-$stamp.zip"

if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

foreach ($f in @("collector.exe", "README-FOR-TESTERS.txt")) {
    $src = Join-Path $here $f
    if (-not (Test-Path $src)) { throw "missing: $f" }
}

Copy-Item (Join-Path $here "collector.exe") $stage
Copy-Item (Join-Path $here "README-FOR-TESTERS.txt") (Join-Path $stage "README.txt")

# A FRESH settings file, not the one on this machine. Copying yours would ship
# your paths and any experiment you left switched on.
@"
# citizen-collector settings
#
# Plain text. One setting per line, "name = value".
# Lines starting with # are notes and are ignored.
# Delete this file to go back to the defaults.

# Watch and capture automatically while the game is running.
auto = true

# Take a picture every this many SECONDS even when nothing changes.
interval_seconds = 60

# How often to check the game log, in seconds.
poll_seconds = 2

# Never take two pictures closer together than this, in seconds.
debounce_seconds = 3

# Take pictures on menu changes, loading screens and spawning too. Off by
# default - those turned out to be almost all of the useless ones.
capture_low_value = false

# While a shop or inventory terminal is open, keep taking pictures this often
# so a list longer than the screen is recorded as you scroll. 0 = one picture.
burst_seconds = 2

# Never more than this many pictures for one terminal.
burst_max_frames = 24

# Where the pictures go. Relative names are next to this file.
out = captures
"@ | Set-Content -Path (Join-Path $stage "collector-settings.txt") -Encoding UTF8

# NO RUNTIME. Not "optional" - gone.
#
# This used to copy ~500 MB of WebView2 so the package would work on a machine
# without it. Since the browser fallback landed, a machine without WebView2 gets
# the interface as a browser tab instead of nothing, so the runtime buys exactly
# nothing and costs a file too big for Discord to accept.
#
# Sleven made a package with the old option on 2026-08-08 and got 271 MB he
# could not send. That is the entire reason this block is a comment now.

if (Test-Path $dest) { Remove-Item $dest -Force }
Write-Host "compressing..."
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $dest

$mb = [math]::Round((Get-Item $dest).Length / 1MB, 1)
Write-Host ""
Write-Host "wrote $dest  ($mb MB)"
Write-Host ""
Write-Host "It contains no captures, no dataset, no install id, no salt, and no"
Write-Host "consent record - the person who receives it gets their own."
Remove-Item $stage -Recurse -Force
