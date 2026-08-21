<#
==============================================================================
 deploy_testing.ps1  -  one-command deploy of the TESTING site to Cloudflare
==============================================================================

 USAGE
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1 -WhatIf

 SCOPE - READ THIS BEFORE CHANGING ANYTHING
   Deploys testing/_deploy/ to Cloudflare Workers static assets, under the
   worker name in testing/wrangler.toml, at
   citizencompasstesting.citizencompass-contact.workers.dev.

   IT DOES NOT TOUCH THE LIVE SITE. citizencompass.netlify.app is where the
   live site is today, hand-deployed on Netlify. Nothing in this script can
   reach it.

   THE LIVE SITE HAS ITS OWN SCRIPT AND ITS OWN CONFIG, added 2026-08-21:
   scripts/deploy_live.ps1 with wrangler.live.toml. Different worker name,
   different URL, checked against each other at deploy time. See
   docs/RELEASING-THE-SITE.md for which command publishes which site.

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

# --- TESTING-ONLY: this payload must be the TESTING payload ------------------
# The pair to the two refusals in scripts/deploy_live.ps1, added 2026-08-21
# with it. That script refuses a payload carrying the private-preview gate or
# the "testing <date>" stamp; this one refuses a payload carrying neither,
# because such a payload is the LIVE build.
#
# WITHOUT THIS HALF THE PAIR DOES NOT WORK. A `--live` build left sitting in
# _deploy would publish an UNGATED private preview to the testing URL and
# report a completely clean deploy - the private preview open to anyone who
# knows the address, discovered later or never.
#
# Checked on the BYTES about to be uploaded rather than on which build flag
# somebody believes they used (rule 12, second half).
$indexFile = Join-Path $assetsDir 'index.html'
$index = Get-Content $indexFile -Raw -Encoding utf8
if (-not $index) { Fail "could not read $indexFile - refusing to deploy unverified content" }

if ($index -notmatch 'id="cc-gate"') {
    Fail @"
THIS PAYLOAD HAS NO PRIVATE-PREVIEW PASSWORD GATE.

That makes it the LIVE build. Publishing it to the testing URL would leave the
private preview open to anyone who knows the address, and the deploy would
report complete success.

Rebuild for testing - the default, no flag:

    python testing\_src\build_deploy.py

then run this script again.
"@
}

if ($index -notmatch '>testing 20[0-9][0-9]-') {
    Fail @"
THIS PAYLOAD CARRIES NO "testing <date>" STAMP, so it is the LIVE build.

An unstamped testing site is indistinguishable from the live one - which is
the exact defect that made a week of work look like it had never shipped.

Rebuild for testing - the default, no flag:

    python testing\_src\build_deploy.py
"@
}

Write-Host "payload : TESTING - password gate present, testing stamp present" -ForegroundColor Green

# --- deploy guard: refuse anything that is not a known asset ----------------
# WHY THIS IS HERE AND NOT ONLY IN THE BUILD
#
# build_deploy.py already runs this same check and refuses to finish a build
# that would leave junk in _deploy. That guard protects the BUILD. It does not
# protect the DEPLOY, because a deploy does not require a build - and that is
# exactly the sequence that leaked wrangler-account.json on 2026-08-06:
#
#   1. a wrangler run executed from inside _deploy failed, leaving .wrangler/
#      behind. No build involved.
#   2. the next deploy uploaded the directory as it stood.
#
# Running this script without rebuilding first would have published it again
# with the build guard never once executing. So the check runs here too, on the
# actual bytes about to be uploaded, immediately before they go.
#
# FAIL CLOSED. If the checker cannot be run at all - python missing, file moved,
# import error - that is NOT a pass. An unverifiable payload is refused, because
# "we could not look" must never be recorded as "we looked and it was fine".
$guard = Join-Path $ProjectPath 'testing\_src\check_deploy_clean.py'
if (-not (Test-Path $guard)) { Fail "deploy guard missing: $guard - refusing to deploy unverified content" }

$prevEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$guardOut = & python $guard $assetsDir 2>&1 | ForEach-Object { [string]$_ }
$guardCode = $LASTEXITCODE
$ErrorActionPreference = $prevEAP

$guardOut | ForEach-Object { Write-Host "  $_" }

if ($null -eq $guardCode) { Fail "deploy guard did not report an exit code - refusing to deploy unverified content" }
if ($guardCode -eq 0) {
    Write-Host "guard   : _deploy contains only known assets" -ForegroundColor Green
} elseif ($guardCode -eq 1) {
    Fail "_deploy contains files that are not known assets (see above). Move them out (never delete - hard rule 1), or add them to the allow-list if they genuinely belong."
} else {
    # Exit 2 is the checker's own "could not check", and any other code is a
    # crash. Both mean unverified, and unverified is refused.
    Fail "deploy guard could not verify $assetsDir (exit $guardCode) - refusing to deploy. This is reported as NOT CHECKED, never as clean."
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
