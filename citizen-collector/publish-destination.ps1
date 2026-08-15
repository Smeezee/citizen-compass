# publish-destination.ps1 - put the send address and key where collectors find them.
#
#   powershell -ExecutionPolicy Bypass -File .\publish-destination.ps1
#   powershell -ExecutionPolicy Bypass -File .\publish-destination.ps1 -Publish
#
# Without -Publish it changes nothing: it prints exactly what it would write and
# stops. Run it that way first.
#
# ---------------------------------------------------------------------------
# WHY THIS EXISTS
# ---------------------------------------------------------------------------
#
# Sleven's wife's collector updated itself cleanly, she pressed SEND, and got a
# 27 MB zip on her disk and nothing else. Nothing was broken - the updater
# replaces the executable and never touches collector-settings.txt, so her
# send_url and send_key were still blank, and blank means "write a zip locally
# and stop".
#
# The fix is that the destination travels on the feed the collector already
# fetches and already trusts enough to download and run a binary from. After
# this runs, a contributor installs, opens it, presses SEND. Nothing to type.
#
# ---------------------------------------------------------------------------
# ONE PROMPT, BOTH HALVES - and the value never leaves this process
# ---------------------------------------------------------------------------
#
# The key has to be in two places at once: as UPLOAD_KEY on the Worker, and in
# the feed. If they ever disagree, every collector in the world is refused with
# 403 and the only symptom is "sending stopped working".
#
# So this asks ONCE and writes both. It is never printed, never logged, never
# written to a scratch file, and never passed as a command-line argument -
# command lines are visible to other processes and land in shell history.
#
# It IS written into releases/collector-latest.json, which is public. That is
# the whole point and it is deliberate: see docs/ROTATING-THE-UPLOAD-KEY.md.
# The key is a revocable channel identifier, not a secret, and what actually
# bounds abuse lives in the Worker.

param(
    [switch] $Publish,

    # Skip setting the Cloudflare secret - use when only the feed needs
    # rewriting and UPLOAD_KEY is known to be correct already.
    [switch] $SkipSecret,

    [string] $SendUrl = "https://collector-receiver.citizencompass-contact.workers.dev",
    [string] $Repo = "Smeezee/citizen-compass"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Split-Path -Parent $here
$feedPath = Join-Path $repoRoot "releases\collector-latest.json"

function Fail($m) { Write-Host ""; Write-Host "REFUSED: $m" -ForegroundColor Red; exit 1 }
function Step($m) { Write-Host ""; Write-Host "== $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "   ok   $m" -ForegroundColor Green }
function Note($m) { Write-Host "        $m" -ForegroundColor DarkGray }

# ---------------------------------------------------------------------------
# THE FEED MUST ALREADY EXIST
# ---------------------------------------------------------------------------
Step "reading the current feed"
if (-not (Test-Path $feedPath)) {
    Fail "$feedPath does not exist. Cut a release first - this adds a destination to a feed, it does not invent one."
}
$existing = $null
try {
    $existing = [IO.File]::ReadAllText($feedPath) | ConvertFrom-Json
} catch {
    Fail "the existing feed is not valid JSON ($($_.Exception.Message)). Fix that before adding to it."
}
foreach ($f in @("version", "url", "sha256")) {
    if (-not $existing.$f) { Fail "the existing feed has no '$f'. Refusing to rewrite a feed I do not understand." }
}
Ok "version $($existing.version), sha256 $($existing.sha256.Substring(0,16))..."

# ---------------------------------------------------------------------------
# THE KEY
# ---------------------------------------------------------------------------
Step "the upload key"
Write-Host "        Type or paste the upload key. It is not echoed." -ForegroundColor Yellow
Write-Host "        The SAME value goes to Cloudflare and into the feed, from this one" -ForegroundColor DarkGray
Write-Host "        prompt, so the two cannot drift apart." -ForegroundColor DarkGray
Write-Host ""
$secure = Read-Host "        upload key" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $key = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}
if ([string]::IsNullOrWhiteSpace($key)) { Fail "no key given. Nothing was changed." }
if ($key.Length -lt 16) {
    Fail "that key is only $($key.Length) characters. It is published, so it should at least not be guessable. Nothing was changed."
}
Ok "read a $($key.Length)-character key (not shown, not logged)"

# ---------------------------------------------------------------------------
# WHAT WOULD HAPPEN
# ---------------------------------------------------------------------------
Step "the plan"
Write-Host "        feed        $feedPath"
Write-Host "        send_url    $SendUrl"
Write-Host "        send_key    <the value you just typed - never printed>"
if (-not $SkipSecret) {
    Write-Host "        cloudflare  wrangler secret put UPLOAD_KEY  (same value)"
} else {
    Write-Host "        cloudflare  SKIPPED (-SkipSecret) - UPLOAD_KEY must already match"
}

if (-not $Publish) {
    Write-Host ""
    Write-Host "Dry run. Nothing was written, set, committed or pushed." -ForegroundColor Yellow
    Write-Host "Re-run with -Publish when it looks right."
    exit 0
}

# ---------------------------------------------------------------------------
# CLOUDFLARE FIRST
# ---------------------------------------------------------------------------
# The secret before the feed, deliberately. Publishing a key the Worker does not
# yet accept would tell every collector to use credentials that are refused;
# setting a secret nobody has been told about yet refuses only the machines that
# were already going to be refused a moment later. The short window belongs on
# the side that is already broken.
if (-not $SkipSecret) {
    Step "setting UPLOAD_KEY on the Worker"
    $errFile = [IO.Path]::GetTempFileName()
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        # Piped on stdin, never as an argument.
        $key | & npx --yes wrangler secret put UPLOAD_KEY 2>$errFile | Out-Null
        $code = $LASTEXITCODE
        $err = [IO.File]::ReadAllText($errFile)
    } finally {
        $ErrorActionPreference = $prev
        Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
    }
    if ($code -ne 0) {
        Fail "could not set UPLOAD_KEY (exit $code).`n$err`nThe feed was NOT touched, so nothing has changed for anybody."
    }
    Ok "UPLOAD_KEY set on the Worker"
}

# ---------------------------------------------------------------------------
# THE FEED
# ---------------------------------------------------------------------------
Step "writing the destination into the feed"

$feed = [ordered]@{
    version   = [string]$existing.version
    url       = [string]$existing.url
    sha256    = [string]$existing.sha256
    notes     = [string]$existing.notes
    min_from  = [string]$existing.min_from
    send_url  = $SendUrl
    send_key  = $key
}

# NO BYTE-ORDER MARK.
#
# Set-Content -Encoding UTF8 on Windows PowerShell 5.1 prepends EF BB BF, and
# Go's encoding/json - which is what update.go parses this with - rejects a
# leading BOM outright. It broke this exact file on 2026-08-14 and looked
# perfectly fine in an editor the whole time.
$json = ($feed | ConvertTo-Json -Depth 3)
[IO.File]::WriteAllText($feedPath, $json, (New-Object System.Text.UTF8Encoding($false)))

# READ IT BACK. Writing a file only proves a file was written; the question is
# whether the program on somebody else's machine can read it.
$bytes = [IO.File]::ReadAllBytes($feedPath)
if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Fail "the feed was written with a UTF-8 BOM. No collector could read it. Nothing has been pushed."
}
$readBack = $null
try {
    $readBack = [IO.File]::ReadAllText($feedPath) | ConvertFrom-Json
} catch {
    Fail "the feed just written is not valid JSON ($($_.Exception.Message)). Nothing has been pushed."
}
if ($readBack.send_url -ne $SendUrl) { Fail "the feed read back has the wrong send_url. Nothing has been pushed." }
if ($readBack.send_key -ne $key)     { Fail "the feed read back does not carry the key that was typed. Nothing has been pushed." }
if ($readBack.version -ne $existing.version -or $readBack.sha256 -ne $existing.sha256) {
    Fail "writing the destination changed the release fields. Nothing has been pushed."
}
Ok "feed parses, carries the destination, and its release fields are unchanged"

# ---------------------------------------------------------------------------
# PUBLISH - one path, never -A
# ---------------------------------------------------------------------------
Step "publishing the feed"
Push-Location $repoRoot
try {
    & git add -- "releases/collector-latest.json"
    if ($LASTEXITCODE -ne 0) { Fail "git add failed. Nothing pushed." }

    # The message must not contain the key. It says what changed, not to what.
    & git commit -m "Collectors are told where to send, so nobody has to type it" | Out-Null
    if ($LASTEXITCODE -ne 0) { Note "nothing to commit - the feed may already say this" }

    & git push
    if ($LASTEXITCODE -ne 0) { Fail "git push failed. The Worker key MAY already be rotated - re-run once the push works, or collectors will be refused." }
} finally {
    Pop-Location
}
Ok "pushed"

# ---------------------------------------------------------------------------
# PROVE IT IS LIVE - over the real network, with the parser that matters
# ---------------------------------------------------------------------------
Step "checking what is actually published"
$raw = "https://raw.githubusercontent.com/$Repo/main/releases/collector-latest.json"
$live = $null
for ($i = 1; $i -le 6; $i++) {
    try {
        $live = Invoke-RestMethod -Uri "$raw`?cc=$([DateTime]::UtcNow.ToString('yyyyMMddHHmmss'))" -TimeoutSec 30
        break
    } catch {
        Note "attempt $i of 6: $($_.Exception.Message)"
        Start-Sleep -Seconds 5
    }
}
if (-not $live) { Fail "the published feed could not be fetched back. Collectors may not see the destination." }
if ($live.send_url -ne $SendUrl) { Fail "the PUBLISHED feed does not carry the expected send_url." }
if (-not $live.send_key)         { Fail "the PUBLISHED feed carries no send_key." }
Ok "the live feed carries the destination"

Write-Host ""
Write-Host "DONE. Every collector picks this up on its next update check." -ForegroundColor Green
Write-Host ""
Write-Host "    send_url  $SendUrl"
Write-Host "    send_key  <published in the feed - not printed here>"
Write-Host ""
Write-Host "Nobody has to open a text file on any machine. To rotate later, see"
Write-Host "docs/ROTATING-THE-UPLOAD-KEY.md - it is one command."
