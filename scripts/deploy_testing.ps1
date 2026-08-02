<#
==============================================================================
 deploy_testing.ps1  -  one-command deploy of the TESTING site to Cloudflare
==============================================================================

 USAGE
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1 -WhatIf

 SCOPE - READ THIS BEFORE CHANGING ANYTHING
   Deploys testing/_deploy/ to Cloudflare Workers static assets.
   It does NOT touch the live site. citizencompass.netlify.app stays on
   Netlify, hand-deployed. Nothing in this script can reach it.

 ------------------------------------------------------------------------------
 API TOKEN - SCOPED, NEVER A GLOBAL API KEY
 ------------------------------------------------------------------------------
 A Global API Key grants full account access including DNS and billing. This
 script refuses to use one. Create a scoped token instead, at
 https://dash.cloudflare.com/profile/api-tokens

 FINAL PERMISSION LIST - recorded here so the token can be rotated later
 without rediscovering what it needed:

     Account | Workers Scripts | Edit          <- required, minimum
     Account Resources: Include | <this account only>

 Started from that minimum deliberately. Any permission added beyond it MUST
 be appended here together with the deploy error that forced it, so the list
 stays a record of what is actually needed rather than what someone guessed
 might be. If a deploy fails with an authorization error, add ONE permission,
 retry, and write down which error it fixed.

     ADDITIONS FOUND NECESSARY IN PRACTICE:
       (none yet - the minimum above has not yet been tested against a real
        deploy. Update this block the first time it is.)

 Token is read from .env as CLOUDFLARE_API_TOKEN. .env is gitignored and
 confirmed untracked. The token is never echoed, logged, or passed on a
 command line - it is handed to wrangler through the environment only.

 ------------------------------------------------------------------------------
 NO CUSTOM DOMAIN
 ------------------------------------------------------------------------------
 Stays on *.workers.dev by design. Do not add a route or a custom domain here.
==============================================================================
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $ProjectPath = 'C:\Users\david\citizen-compass',
    [switch] $SkipVerify
)

$ErrorActionPreference = 'Stop'

$config    = Join-Path $ProjectPath 'testing\wrangler.toml'
$assetsDir = Join-Path $ProjectPath 'testing\_deploy'
$envFile   = Join-Path $ProjectPath '.env'

function Fail($msg) { Write-Host "DEPLOY ABORTED: $msg" -ForegroundColor Red; exit 1 }

if (-not (Test-Path $config))    { Fail "missing $config" }
if (-not (Test-Path $assetsDir)) { Fail "missing $assetsDir - nothing to deploy" }
if (-not (Test-Path (Join-Path $assetsDir 'index.html'))) {
    Fail "$assetsDir has no index.html - refusing to publish a site with no entry point"
}

# --- sanity-check the payload BEFORE uploading ------------------------------
# A deploy that silently dropped the models folder still serves a page that
# looks completely correct. Catch it here as well as after.
$files = Get-ChildItem $assetsDir -Recurse -File
$modelCount = @($files | Where-Object { $_.Extension -eq '.glb' }).Count
$totalMB = [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 1)
$largest = ($files | Sort-Object Length -Descending | Select-Object -First 1)

Write-Host "payload : $($files.Count) files, $totalMB MB"
Write-Host "models  : $modelCount .glb files"
Write-Host "largest : $($largest.Name) ($([math]::Round($largest.Length/1MB,2)) MB)"

if ($modelCount -lt 1) { Fail "no .glb model files found in $assetsDir - the models folder is missing" }

# Cloudflare free-tier ceilings, checked against current docs 2026-08-01.
if ($files.Count -gt 20000) { Fail "$($files.Count) files exceeds Cloudflare's 20,000-file limit per Worker version" }
if ($largest.Length -gt 25MB) { Fail "$($largest.Name) is over Cloudflare's 25 MiB per-file limit" }

# --- credentials ------------------------------------------------------------
# TWO ACCEPTED PATHS, checked in this order:
#
#   1. wrangler is ALREADY authenticated (e.g. `wrangler login` stored an OAuth
#      credential outside .env). If so, use it - do not demand a token that is
#      not needed.
#   2. otherwise, a scoped CLOUDFLARE_API_TOKEN from .env.
#
# Path 1 is checked by BEHAVIOUR - asking wrangler itself - rather than by
# looking for a credential file, because the file's location has moved between
# wrangler versions and an absent file is not proof of an absent credential.
# .env is read FIRST, and the reason is accuracy rather than precedence.
# wrangler v4 loads .env from the project directory itself, so once a token is
# present `wrangler whoami` reports "authenticated" BECAUSE OF that token. An
# earlier version of this block asked whoami first and then announced
# "already authenticated - no .env token needed", which was simply false: the
# .env token was what authenticated it. Checking .env first means the script
# can say which credential is actually in use instead of guessing.
$token = $null
if (Test-Path $envFile) {
    foreach ($line in Get-Content $envFile -Encoding utf8) {
        if ($line -match '^\s*CLOUDFLARE_API_TOKEN\s*=\s*(.+?)\s*$') {
            $token = $matches[1].Trim().Trim('"').Trim("'")
        }
        if ($line -match '^\s*CLOUDFLARE_GLOBAL_API_KEY\s*=') {
            Fail "CLOUDFLARE_GLOBAL_API_KEY found in .env. A Global API Key grants DNS and billing access. Use a scoped token (see this script's header) and remove that line."
        }
    }
}

$usingExistingAuth = $false
if (-not $token) {
    # No token here, so anything wrangler reports must come from a credential
    # stored elsewhere - an OAuth login from `wrangler login`, or a CLOUDFLARE_*
    # environment variable.
    $prevEAP2 = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $who = (& npx wrangler whoami 2>&1 | Out-String)
    $ErrorActionPreference = $prevEAP2
    if ($who -notmatch 'not authenticated') {
        $usingExistingAuth = $true
        $acct = ([regex]::Match($who, '([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+)')).Value
        Write-Host "auth    : no token in .env; wrangler is authenticated by a stored credential$(if($acct){" as $acct"}) - using that"
    }
}

if (-not $usingExistingAuth) {
    if (-not (Test-Path $envFile)) { Fail "no .env at $envFile" }

    # A placeholder is not a credential. This has already been pasted twice as
    # the literal string <TOKEN>; writing it through would fail later as a
    # confusing auth error instead of here as an obvious one.
    if ($token -match '^<.*>$' -or $token -eq 'YOUR_TOKEN_HERE') {
        Fail "CLOUDFLARE_API_TOKEN in .env is a placeholder ('$token'), not a real credential. Replace it with the actual token value."
    }

    if (-not $token) {
        Fail @"
Not authenticated, and CLOUDFLARE_API_TOKEN is not set in .env.

Either run:  npx wrangler login
or create a SCOPED token at https://dash.cloudflare.com/profile/api-tokens with:

    Account | Workers Scripts | Edit
    Account Resources: Include | this account only

and add to .env (gitignored, untracked):

    CLOUDFLARE_API_TOKEN=<token>

Do not use a Global API Key.
"@
    }

    # Handed to wrangler via the environment - never a command line, never echoed.
    $env:CLOUDFLARE_API_TOKEN = $token
    Write-Host "auth    : scoped token loaded from .env (length $($token.Length), not shown)"
}

if (-not $PSCmdlet.ShouldProcess('Cloudflare Workers', "deploy $($files.Count) files from testing\_deploy")) {
    Write-Host ""
    Write-Host "-WhatIf: would run  npx wrangler deploy --config `"$config`"" -ForegroundColor Cyan
    Write-Host "Nothing was uploaded."
    exit 0
}

Write-Host ""
Write-Host "deploying..." -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# $ErrorActionPreference MUST be 'Continue' across this call.
#
# This bit her cost a deploy. Windows PowerShell 5.1 wraps every stderr line
# from a native executable in an ErrorRecord (NativeCommandError). wrangler
# writes an ordinary WARNING to stderr - "Preview URLs will be enabled..." -
# so with $ErrorActionPreference = 'Stop' the script aborted on a WARNING,
# reported exit 1, and looked like a failed deploy.
#
# It was not. wrangler had already uploaded all 477 files and published the
# version; only the PowerShell wrapper failed, AFTER the work was done. So the
# script reported failure on a success - the mirror image of reporting success
# on a failure, and just as misleading.
#
# The exit code is the authority here, not the presence of stderr output.
# ---------------------------------------------------------------------------
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& npx wrangler deploy --config $config
$code = $LASTEXITCODE
$ErrorActionPreference = $prevEAP

$env:CLOUDFLARE_API_TOKEN = $null   # do not leave it in the session

if ($code -ne 0) { Fail "wrangler exited $code" }

Write-Host ""
Write-Host "deploy finished. Exit code 0 is NOT proof it works." -ForegroundColor Yellow
Write-Host "Run the verification below before believing it:" -ForegroundColor Yellow
Write-Host "  1. index.html serves (not a 404 or Cloudflare placeholder)"
Write-Host "  2. the page contains id=`"cc-kb`" and cc-ship::after"
Write-Host "  3. a MODEL serves - e.g. /models/Hammerhead.glb returns 200 with a"
Write-Host "     plausible byte count. A deploy that dropped the models folder"
Write-Host "     still loads and still looks right."
Write-Host "  4. the password gate blocks from a clean context"
