# make-release.ps1 - publish a build to GitHub Releases, then point the
# auto-updater at it.
#
# Run from the citizen-collector folder:
#     powershell -ExecutionPolicy Bypass -File .\make-release.ps1 -Version 0.2.0
#     powershell -ExecutionPolicy Bypass -File .\make-release.ps1 -Version 0.2.0 -Publish
#
# Without -Publish it changes NOTHING. It checks everything, prints exactly what
# would happen, and stops. Run it that way first, every time.
#
# ---------------------------------------------------------------------------
# WHY THIS EXISTS
# ---------------------------------------------------------------------------
#
# Discord's free tier refuses anything over 10 MB. The with-runtime package is
# ~162 MB and always will be, because msedge.dll alone is 341 MB uncompressed.
# There is no compression trick that gets under 10 MB - the answer is to stop
# sending the file and start sending a link.
#
# GitHub Releases is the right home for that link, and not only because it is
# free and has a 2 GB per-asset limit:
#
#   THE AUTO-UPDATER ALREADY READS FROM THERE. update.go fetches
#   releases/collector-latest.json off the main branch and downloads the exe it
#   names. So one publish feeds both the first install and every update after
#   it. Two distribution channels that can disagree is a defect waiting to
#   happen; this is one channel.
#
# ---------------------------------------------------------------------------
# THE ORDER OF OPERATIONS IS NOT ARBITRARY
# ---------------------------------------------------------------------------
#
# The exe is a release asset. The feed JSON is a file on the main branch. They
# are published separately, so one of them is live before the other, and the
# order decides what a broken half looks like:
#
#   ASSET FIRST, FEED SECOND  -> a moment where the new build exists and nobody
#                                is told. Harmless.
#   FEED FIRST, ASSET SECOND  -> a moment where every collector in the world is
#                                told to download a URL that 404s. The update
#                                fails on somebody else's machine, for a reason
#                                they cannot see.
#
# So: asset first, always. And the feed is not written at all until the asset
# has been downloaded back from its public URL and its hash checked.
#
# ---------------------------------------------------------------------------
# THE CHECK HAS TO BE ABLE TO FAIL - hard rule 12
# ---------------------------------------------------------------------------
#
# Hashing the local file and writing that hash into the feed proves nothing: it
# is the sender agreeing with itself. The only check worth running is a round
# trip - fetch the asset back over the public internet, hash what actually
# arrived, and compare. That can fail, and it fails for the reasons that
# matter: a truncated upload, the wrong file picked, an asset attached to the
# wrong tag.
#
# -SelfTest proves the comparison itself works by corrupting a byte and
# confirming it is rejected.

param(
    [Parameter(Mandatory = $true)]
    [string] $Version,

    [switch] $Publish,
    [switch] $SelfTest,

    # -Announce commits and pushes the feed, which is the moment every existing
    # collector learns the build exists. Separate from -Publish on purpose: the
    # standing project rule is that nothing pushes without an explicit
    # go-ahead, and typing this switch IS that go-ahead. Without it the script
    # writes the feed file and prints the three git commands.
    [switch] $Announce,

    [string] $Repo = "Smeezee/citizen-compass",

    # Where releases/collector-latest.json lives. Defaults to the sibling
    # citizen-compass repo checkout.
    [string] $RepoPath = ""
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Fail($msg) { Write-Host ""; Write-Host "REFUSED: $msg" -ForegroundColor Red; exit 1 }
function Step($msg) { Write-Host ""; Write-Host "== $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "   ok   $msg" -ForegroundColor Green }
function Note($msg) { Write-Host "        $msg" -ForegroundColor DarkGray }

function Sha256File($path) {
    (Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash.ToLower()
}

# ---------------------------------------------------------------------------
# SELF TEST - run the hash comparison against a case that must fail
# ---------------------------------------------------------------------------
if ($SelfTest) {
    Step "self test: does the hash comparison actually reject a bad file?"
    $a = Join-Path $env:TEMP "cc-selftest-a.bin"
    $b = Join-Path $env:TEMP "cc-selftest-b.bin"
    $bytes = [byte[]](1..4096 | ForEach-Object { $_ % 256 })
    [IO.File]::WriteAllBytes($a, $bytes)
    $bytes[17] = [byte](($bytes[17] + 1) % 256)   # one byte, in the middle
    [IO.File]::WriteAllBytes($b, $bytes)

    $ha = Sha256File $a
    $hb = Sha256File $b

    if ($ha -eq $hb) { Fail "identical hashes for different bytes - the hash is not working" }
    Ok "one changed byte produced a different hash (the check CAN fail)"

    [IO.File]::WriteAllBytes($b, [IO.File]::ReadAllBytes($a))
    if ((Sha256File $b) -ne $ha) { Fail "identical bytes produced different hashes" }
    Ok "identical bytes produced the same hash (the check does not fire spuriously)"

    Remove-Item $a, $b -Force -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "self test passed. The round-trip check in this script is a real check."
    exit 0
}

# ---------------------------------------------------------------------------
# 0. VERSION SANITY
# ---------------------------------------------------------------------------
Step "checking the version string"
if ($Version -notmatch '^\d+(\.\d+)*$') {
    Fail "version '$Version' is not plain dotted numbers. update.go's comparator parses nothing else, and a version it cannot parse compares as NOT NEWER - the update would silently never offer itself."
}
Ok "version $Version parses"

$tag = "collector-v$Version"

# ---------------------------------------------------------------------------
# 1. THE FILES
# ---------------------------------------------------------------------------
Step "checking what is here"

$crew = Join-Path $here "collector.exe"
if (-not (Test-Path $crew)) {
    Fail "collector.exe is not here. The release ships the CREW build, not collector-master.exe - the master build has Sleven's own tools in it."
}
$crewInfo = Get-Item $crew
Ok ("collector.exe  {0:N0} bytes, built {1}" -f $crewInfo.Length, $crewInfo.LastWriteTime)

$master = Join-Path $here "collector-master.exe"
if (Test-Path $master) {
    $masterInfo = Get-Item $master
    # Same guard the Go packager has, for the same reason: shipping a crew build
    # older than the one being tested hands somebody a different program than
    # the one that was verified, and the difference is invisible to them.
    if ($crewInfo.LastWriteTime -lt $masterInfo.LastWriteTime.AddMinutes(-2)) {
        Fail ("collector.exe is older than collector-master.exe ({0} vs {1}). Rebuild the crew binary before releasing it." -f `
            $crewInfo.LastWriteTime, $masterInfo.LastWriteTime)
    }
    Ok "crew build is not older than the master build"
}

# THE CHECK THAT PREVENTS AN ENDLESS UPDATE LOOP.
#
# update.go compares the feed's version against the Version compiled into the
# running exe. Label a release 0.2.0 while the exe still reports 0.1.0 and every
# collector downloads it, installs it, still reports 0.1.0, and is offered the
# same update again on the next check. Forever. Nothing errors.
#
# So ask the BINARY, not main.go. The source says what the next build will
# report, which is not the same question.
$exeVer = (& $crew --version 2>&1 | Select-Object -First 1).ToString().Trim()
if ($LASTEXITCODE -ne 0 -or $exeVer -notmatch '^\d+(\.\d+)*$') {
    Fail "collector.exe could not report its own version (got '$exeVer'). This build predates the --version flag, so rebuild it before releasing - publishing a version that cannot be checked is how the endless-update loop gets shipped."
}
if ($exeVer -ne $Version) {
    Fail "you are labelling this release $Version but collector.exe reports $exeVer. Edit Version in main.go to `"$Version`", rebuild, and run this again. Publishing as-is would offer every collector an update that never satisfies itself."
}
Ok "collector.exe reports $exeVer, which matches the release label"

$readme = Join-Path $here "README-FOR-TESTERS.txt"
if (-not (Test-Path $readme)) {
    Fail "README-FOR-TESTERS.txt is missing. A build handed to somebody with no explanation is not a test, it is an imposition."
}
Ok "README-FOR-TESTERS.txt present"

# ---------------------------------------------------------------------------
# THE UPLOAD KEY MUST NOT GO INTO A PUBLIC RELEASE ASSET
# ---------------------------------------------------------------------------
#
# Step 4 copies collector-settings.txt into the shipped zip, send_key included.
# That was written when packages were handed out privately. A GitHub release is
# public: the zip is downloadable by anyone, so a non-empty send_key here means
# publishing the shared upload key to the whole internet, where it can be used
# to post anything at all into the bucket.
#
# REFUSE, rather than warn. A warning in a wall of green output is not a
# control, and the cost of getting this wrong is rotating a key that every
# collector already has.
$settingsCheck = Join-Path $here "collector-settings.txt"
if (Test-Path $settingsCheck) {
    $leaky = @()
    foreach ($line in (Get-Content -LiteralPath $settingsCheck -Encoding UTF8)) {
        if ($line -match '^\s*#') { continue }
        if ($line -match '^\s*send_key\s*=\s*(\S.*)$') { $leaky += "send_key" }
    }
    if ($leaky.Count -gt 0) {
        Fail ("collector-settings.txt has a non-empty send_key, and step 4 copies that " +
              "file into the release zip. A GitHub release is PUBLIC - publishing it " +
              "would hand the shared upload key to anyone who downloads the package, " +
              "and rotating it means every existing collector stops being able to send. " +
              "Blank send_key here before releasing; give the key to people separately.")
    }
    Ok "collector-settings.txt carries no upload key, so the public zip cannot leak one"
} else {
    Note "no collector-settings.txt to check"
}

# ---------------------------------------------------------------------------
# 2. IS THIS ACTUALLY NEWER THAN WHAT IS PUBLISHED?
# ---------------------------------------------------------------------------
Step "checking against what is already published"
$feedUrl = "https://raw.githubusercontent.com/$Repo/main/releases/collector-latest.json"
try {
    $live = Invoke-RestMethod -Uri "$feedUrl`?cc=$([DateTime]::UtcNow.ToString('yyyyMMddHHmmss'))" -TimeoutSec 20
    Note "currently published: $($live.version)"
    $cmp = [version]("$($live.version).0.0.0".Split('.')[0..3] -join '.')
    $new = [version]("$Version.0.0.0".Split('.')[0..3] -join '.')
    if ($new -le $cmp) {
        Fail "version $Version is not newer than the published $($live.version). Publishing it would put new bytes behind an old label, and no collector would ever offer the update."
    }
    Ok "$Version is newer than the published $($live.version)"
} catch {
    Note "no readable feed yet ($($_.Exception.Message))"
    Note "treating this as the FIRST release. That is fine; it just means there is nothing to compare against."
}

# ---------------------------------------------------------------------------
# 3. HASH THE EXACT BYTES THAT WILL BE UPLOADED
# ---------------------------------------------------------------------------
Step "hashing collector.exe"
$sha = Sha256File $crew
if ($sha.Length -ne 64) { Fail "hash is not 64 hex characters - refusing to publish. update.go refuses a release without one anyway." }
Ok "sha256 $sha"

# ---------------------------------------------------------------------------
# 4. BUILD THE TWO ZIPS
# ---------------------------------------------------------------------------
Step "building the install packages"
$stage = Join-Path $env:TEMP "cc-release-stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

Copy-Item $crew $stage
Copy-Item $readme (Join-Path $stage "README.txt")

# A FRESH settings file. Copying this machine's would ship whatever experiment
# was left switched on, plus this machine's paths.
$settingsSrc = Join-Path $here "collector-settings.txt"
if (Test-Path $settingsSrc) {
    # Strip anything machine-specific rather than shipping it.
    Get-Content $settingsSrc | Where-Object { $_ -notmatch '^\s*(out|log_path|game_log)\s*=' } |
        Set-Content -Path (Join-Path $stage "collector-settings.txt") -Encoding UTF8
    Add-Content -Path (Join-Path $stage "collector-settings.txt") -Value "out = captures" -Encoding UTF8
} else {
    Note "no collector-settings.txt here; the package ships without one and the program uses its defaults"
}

$smallZip = Join-Path $here "citizen-collector-$Version.zip"
if (Test-Path $smallZip) { Remove-Item $smallZip -Force }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $smallZip
$smallMb = [math]::Round((Get-Item $smallZip).Length / 1MB, 1)
Ok "citizen-collector-$Version.zip  ($smallMb MB)  - needs WebView2 already installed"
if ((Get-Item $smallZip).Length -lt 10MB) {
    Note "under 10 MB, so this one still fits a plain Discord message if you ever need that"
} else {
    Note "over 10 MB - Discord will refuse this one too. Use the link."
}

$bigZip = $null
$rt = Join-Path $here "webview2-runtime"
if (Test-Path $rt) {
    Write-Host "        copying the WebView2 runtime (slow, ~500 MB on disk)..."
    Copy-Item $rt (Join-Path $stage "webview2-runtime") -Recurse
    $bigZip = Join-Path $here "citizen-collector-$Version-with-runtime.zip"
    if (Test-Path $bigZip) { Remove-Item $bigZip -Force }
    Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $bigZip
    $bigMb = [math]::Round((Get-Item $bigZip).Length / 1MB, 1)
    Ok "citizen-collector-$Version-with-runtime.zip  ($bigMb MB)  - runs on any Windows machine"
} else {
    Note "no webview2-runtime folder here, so no with-runtime package. Machines without WebView2 will need it installed."
}

Remove-Item $stage -Recurse -Force

# ---------------------------------------------------------------------------
# 5. THE PLAN
# ---------------------------------------------------------------------------
$assetUrl = "https://github.com/$Repo/releases/download/$tag/collector.exe"

Step "the plan"
Write-Host "        tag          $tag"
Write-Host "        repo         $Repo"
Write-Host "        assets       collector.exe"
Write-Host "                     $(Split-Path -Leaf $smallZip)"
if ($bigZip) { Write-Host "                     $(Split-Path -Leaf $bigZip)" }
Write-Host "        updater url  $assetUrl"
Write-Host "        sha256       $sha"

if (-not $Publish) {
    Write-Host ""
    Write-Host "Nothing was published. This was a dry run." -ForegroundColor Yellow
    Write-Host "Re-run with -Publish when it all looks right:"
    Write-Host "    powershell -ExecutionPolicy Bypass -File .\make-release.ps1 -Version $Version -Publish"
    exit 0
}

# ---------------------------------------------------------------------------
# 6. PUBLISH - asset first, always
# ---------------------------------------------------------------------------
Step "publishing"

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host ""
    Write-Host "The GitHub CLI (gh) is not installed, so this script cannot upload for you." -ForegroundColor Yellow
    Write-Host "Either install it (winget install GitHub.cli) or do it by hand:"
    Write-Host ""
    Write-Host "  1. https://github.com/$Repo/releases/new"
    Write-Host "  2. Tag:   $tag"
    Write-Host "  3. Attach: collector.exe, $(Split-Path -Leaf $smallZip)$(if ($bigZip) { ", $(Split-Path -Leaf $bigZip)" })"
    Write-Host "  4. Publish, then re-run this script with -Publish to write and verify the feed."
    exit 1
}

$assets = @($crew, $smallZip)
if ($bigZip) { $assets += $bigZip }

# STDERR TO A FILE, NOT INTO THE PIPELINE. `2>&1` on a native exe in PowerShell
# 5.1 wraps stderr in ErrorRecords; with $ErrorActionPreference = "Stop" that
# kills the script on output that is not necessarily an error. It made the
# "tag already exists" fallback below unreachable - the recovery path existed
# and could never run, so every re-run of a release died at this line.
function Invoke-Gh {
    param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $GhArgs)
    $errFile = [IO.Path]::GetTempFileName()
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $out = (& gh @GhArgs 2>$errFile | Out-String)
        $code = $LASTEXITCODE
        $err = ""
        if (Test-Path $errFile) { $err = [IO.File]::ReadAllText($errFile) }
    } finally {
        $ErrorActionPreference = $prev
        Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
    }
    return [pscustomobject]@{ Code = $code; All = "$out`n$err" }
}

Write-Host "        creating release $tag ..."
$mk = Invoke-Gh release create $tag @assets --repo $Repo --title "Citizen Collector $Version" --notes "Build $Version."
$mk.All -split "`n" | ForEach-Object { if ($_.Trim()) { Note $_.Trim() } }
if ($mk.Code -ne 0) {
    Write-Host "        the tag already exists (or create failed); attaching the assets to it instead..."
    $up = Invoke-Gh release upload $tag @assets --repo $Repo --clobber
    $up.All -split "`n" | ForEach-Object { if ($_.Trim()) { Note $_.Trim() } }
    if ($up.Code -ne 0) { Fail "could not attach the assets. Nothing was written to the feed, so no collector has been told about this build." }
}
Ok "assets attached to $tag"

# ---------------------------------------------------------------------------
# 7. THE ROUND TRIP - fetch it back and check what actually arrived
# ---------------------------------------------------------------------------
Step "downloading it back from the public URL"
$probe = Join-Path $env:TEMP "cc-release-probe.exe"
if (Test-Path $probe) { Remove-Item $probe -Force }

$got = $false
for ($i = 1; $i -le 6; $i++) {
    try {
        Invoke-WebRequest -Uri $assetUrl -OutFile $probe -TimeoutSec 120 -UseBasicParsing
        $got = $true
        break
    } catch {
        Note "attempt $i of 6: $($_.Exception.Message)"
        Start-Sleep -Seconds 5
    }
}
if (-not $got) {
    Fail "the asset is not downloadable at $assetUrl. The feed has NOT been written, so no collector will be told to fetch a URL that does not work."
}

$backSha = Sha256File $probe
Note "sent     $sha"
Note "arrived  $backSha"
if ($backSha -ne $sha) {
    Remove-Item $probe -Force -ErrorAction SilentlyContinue
    Fail "what came back is not what went up. The feed has NOT been written. Delete the release, rebuild, and try again."
}
Ok "round trip verified - the bytes at the public URL are the bytes you built"
Remove-Item $probe -Force -ErrorAction SilentlyContinue

# ---------------------------------------------------------------------------
# 8. THE FEED - written last, and NOT committed
# ---------------------------------------------------------------------------
Step "writing the feed"

if (-not $RepoPath) {
    foreach ($guess in @((Join-Path (Split-Path -Parent $here) "citizen-compass"), (Join-Path $HOME "citizen-compass"))) {
        if (Test-Path (Join-Path $guess ".git")) { $RepoPath = $guess; break }
    }
}
if (-not $RepoPath -or -not (Test-Path $RepoPath)) {
    Fail "cannot find the citizen-compass repo checkout. Pass -RepoPath C:\path\to\citizen-compass. The assets ARE published and verified; only the feed is missing, so nothing is broken - collectors simply are not told yet."
}

$relDir = Join-Path $RepoPath "releases"
if (-not (Test-Path $relDir)) { New-Item -ItemType Directory -Path $relDir | Out-Null }
$feedPath = Join-Path $relDir "collector-latest.json"

$feed = [ordered]@{
    version  = $Version
    url      = $assetUrl
    sha256   = $sha
    notes    = "Build $Version."
    min_from = ""
}
# NO BYTE-ORDER MARK. `Set-Content -Encoding UTF8` on Windows PowerShell 5.1
# prepends ef bb bf, and Go's encoding/json - which is what update.go parses
# this with - refuses a leading BOM with "invalid character looking for
# beginning of value". A feed written that way is unreadable by every collector
# alive, while looking perfectly fine in any text editor.
$feedJson = ($feed | ConvertTo-Json -Depth 3)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($feedPath, $feedJson, $utf8NoBom)

# READ IT BACK AND PARSE IT. Writing a file only proves a file was written.
# The question that matters is whether the program on somebody else's machine
# can read it, so ask that question here, where it can still be fixed.
$rawBytes = [IO.File]::ReadAllBytes($feedPath)
if ($rawBytes.Length -ge 3 -and $rawBytes[0] -eq 0xEF -and $rawBytes[1] -eq 0xBB -and $rawBytes[2] -eq 0xBF) {
    Fail "the feed was written with a UTF-8 BOM. Go's json parser rejects it, so no collector could read this file. Nothing has been announced."
}
try {
    $parsed = [IO.File]::ReadAllText($feedPath) | ConvertFrom-Json
} catch {
    Fail "the feed just written is not valid JSON ($($_.Exception.Message)). Nothing has been announced."
}
if ($parsed.sha256 -ne $sha -or $parsed.version -ne $Version -or -not $parsed.url) {
    Fail "the feed read back does not match what was meant to be written (version '$($parsed.version)', sha '$($parsed.sha256)'). Nothing has been announced."
}
Ok "feed parses, and its version, url and sha256 are the ones just published"
Ok "wrote $feedPath"

if (-not $Announce) {
    Write-Host ""
    Write-Host "PUBLISHED, VERIFIED, AND NOT YET ANNOUNCED." -ForegroundColor Green
    Write-Host ""
    Write-Host "The build is live and downloadable. No collector knows about it until the"
    Write-Host "feed is committed - which is deliberate, and is yours to do:"
    Write-Host ""
    Write-Host "    cd `"$RepoPath`""
    Write-Host "    git add releases/collector-latest.json"
    Write-Host "    git commit -m `"collector $Version`""
    Write-Host "    git push"
    Write-Host ""
    Write-Host "Add ONLY that one path. Do not git add -A on this repo - the line endings"
    Write-Host "are still unsettled and ~50 files show as modified from pure CRLF churn."
    Write-Host ""
    Write-Host "Or re-run with -Announce and this script will do exactly those four lines."
    Write-Host ""
    Write-Host "The link to paste in Discord:"
    Write-Host "    https://github.com/$Repo/releases/tag/$tag" -ForegroundColor Cyan
    exit 0
}

# ---------------------------------------------------------------------------
# 9. ANNOUNCE - the one path, never -A
# ---------------------------------------------------------------------------
Step "announcing it to every collector"

Push-Location $RepoPath
try {
    # ONLY this path. `git add -A` on this repo stages ~50 files that differ by
    # nothing but CRLF, and that has been a standing rule since it happened.
    & git add -- "releases/collector-latest.json" 2>&1 | ForEach-Object { Note $_ }
    if ($LASTEXITCODE -ne 0) { Fail "git add failed. The build is published; only the feed is unannounced." }

    & git commit -m "collector $Version" 2>&1 | ForEach-Object { Note $_ }
    if ($LASTEXITCODE -ne 0) {
        Note "nothing to commit, or the commit failed - continuing to check what is live"
    }

    & git push 2>&1 | ForEach-Object { Note $_ }
    if ($LASTEXITCODE -ne 0) { Fail "git push failed. The build is published but no collector will be told." }
} finally {
    Pop-Location
}
Ok "feed committed and pushed"

# ---------------------------------------------------------------------------
# 10. THE SECOND ROUND TRIP - what does a collector ACTUALLY see?
# ---------------------------------------------------------------------------
#
# A successful push is not the same as a readable feed. raw.githubusercontent
# serves through a CDN with its own cache, so there is a window where the push
# has landed and every collector still reads the old file - or, for a first
# release, still gets a 404.
#
# The check that matters is the one from the collector's side: fetch the exact
# URL update.go fetches, and confirm it names this version. Anything else is
# assuming.
Step "checking what a collector would actually see"
$seen = $false
for ($i = 1; $i -le 10; $i++) {
    try {
        $bust = [DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
        $live = Invoke-RestMethod -Uri "$feedUrl`?cc=$bust$i" -TimeoutSec 20
        if ($live.version -eq $Version -and $live.sha256 -eq $sha) {
            $seen = $true
            break
        }
        Note "attempt $i of 10: still serving version '$($live.version)'"
    } catch {
        Note "attempt $i of 10: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 10
}

if ($seen) {
    Ok "a collector fetching the feed right now sees $Version"
    Write-Host ""
    Write-Host "DONE. Every running collector will offer this build within six hours," -ForegroundColor Green
    Write-Host "and any that is restarted will offer it immediately."
} else {
    Write-Host ""
    Write-Host "PUSHED, BUT NOT YET VISIBLE." -ForegroundColor Yellow
    Write-Host "The push succeeded and the assets are verified, so nothing is broken -"
    Write-Host "GitHub's CDN is still serving the old copy. It usually clears within a"
    Write-Host "few minutes. Check it yourself with:"
    Write-Host "    $feedUrl"
}

Write-Host ""
Write-Host "The link to paste in Discord:"
Write-Host "    https://github.com/$Repo/releases/tag/$tag" -ForegroundColor Cyan
