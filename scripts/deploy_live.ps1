<#
==============================================================================
 deploy_live.ps1  -  one-command deploy of the LIVE (public) site to Cloudflare
==============================================================================

 USAGE
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1 -WhatIf
   powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1

 READ THIS FIRST
   THE PUBLIC SITE IS THREE WEEKS BEHIND BECAUSE THERE WAS NO BUTTON. The
   testing site has deployed with one guarded command since 2026-08-01; the
   live site has been moved by hand, by one person, from memory. That is the
   defect this script exists to close - not a broken deploy, an absent one.

   This is a mirror of scripts/deploy_testing.ps1 and deliberately so: the same
   unknown-file guard on the same bytes, the same fail-closed handling when the
   guard cannot run, the same payload sanity checks, the same credential
   handling, the same -WhatIf. Where it differs it differs because the LIVE
   site is public, and every one of those differences is a refusal.

 STATUS AT THE TIME OF WRITING (2026-08-21)
   THE WORKER DOES NOT EXIST YET. citizencompass.citizencompass-contact.workers.dev
   returned 404 when this was written. Only Sleven creates it. THIS SCRIPT HAS
   NEVER BEEN RUN FOR REAL - only with -WhatIf. Do not be the one who runs it
   for real without being asked to.

 ------------------------------------------------------------------------------
 WHAT IT PUBLISHES, AND WHAT IT REFUSES
 ------------------------------------------------------------------------------
 Publishes testing/_deploy - the SAME directory the testing site publishes,
 because Sleven reviews the testing site and then that exact payload goes live.
 Two build directories would mean the thing reviewed and the thing shipped were
 never the same bytes.

 The two payloads differ in exactly two ways, both made by the build:

     python testing/_src/build_deploy.py           gated, "testing <date>" stamp
     python testing/_src/build_deploy.py --live    neither

 So this script REFUSES a payload that carries either one:

   * THE PRIVATE-PREVIEW PASSWORD GATE. Publishing it to the public site would
     lock the public out of their own site behind a password they were never
     given. From the outside that reads as an outage, not as a mistake, so
     nobody would report it as one.

   * THE "testing <date>" STAMP. It exists to make the testing site
     distinguishable from the live one. On the live site it is simply false.

 It also refuses to publish under the TESTING worker's name - see below.

 ------------------------------------------------------------------------------
 THE NAME CHECK, WHICH IS THE ONE THAT MATTERS
 ------------------------------------------------------------------------------
 The Worker name IS the subdomain. A wrong name here does not fail and does not
 update the existing site: it CREATES A SECOND SITE at a second URL and reports
 a completely successful deploy. testing/wrangler.toml carries a note about the
 last time this project did that.

 So the name is not trusted to a comment. This script reads `name` out of BOTH
 wrangler.live.toml and testing/wrangler.toml and refuses to run if they match.
 Structural, not remembered - it cannot be evaded by editing one file, because
 the check is on the relationship between the two.

 ------------------------------------------------------------------------------
 API TOKEN - SCOPED, NEVER A GLOBAL API KEY
 ------------------------------------------------------------------------------
 Identical to deploy_testing.ps1, and for the same reason: a Global API Key
 grants full account access including DNS and billing. This script refuses to
 use one. Create a scoped token at
 https://dash.cloudflare.com/profile/api-tokens

     Account | Workers Scripts | Edit          <- required, minimum
     Account Resources: Include | <this account only>

 Read from .env as CLOUDFLARE_API_TOKEN. .env is gitignored. The token is never
 echoed, logged, or passed on a command line - it is handed to wrangler through
 the environment only.

     ADDITIONS FOUND NECESSARY IN PRACTICE:
       (none - this script has never been run against a real deploy. Update
        this block the first time it is, together with the error that forced
        each addition.)

 ------------------------------------------------------------------------------
 NOTHING HERE TOUCHES NETLIFY
 ------------------------------------------------------------------------------
 citizencompass.netlify.app is where the live site is TODAY, hand-deployed.
 This script cannot reach it, will not take it down, and does not know it
 exists beyond this paragraph. Retiring it is a separate, manual decision -
 see docs/RELEASING-THE-SITE.md.
==============================================================================
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $ProjectPath = 'C:\Users\david\citizen-compass'
)

$ErrorActionPreference = 'Stop'

$config        = Join-Path $ProjectPath 'wrangler.live.toml'
$testingConfig = Join-Path $ProjectPath 'testing\wrangler.toml'
$assetsDir     = Join-Path $ProjectPath 'testing\_deploy'
$indexFile     = Join-Path $assetsDir 'index.html'
$envFile       = Join-Path $ProjectPath '.env'

function Fail($msg) { Write-Host "LIVE DEPLOY ABORTED: $msg" -ForegroundColor Red; exit 1 }

Write-Host "=== LIVE SITE DEPLOY ===" -ForegroundColor Yellow

if (-not (Test-Path $config))        { Fail "missing $config" }
if (-not (Test-Path $testingConfig)) { Fail "missing $testingConfig - the name check below cannot be performed, and an unverifiable name is refused, never assumed safe" }
if (-not (Test-Path $assetsDir))     { Fail "missing $assetsDir - nothing to deploy" }
if (-not (Test-Path $indexFile)) {
    Fail "$assetsDir has no index.html - refusing to publish a site with no entry point"
}

# --- the name check ----------------------------------------------------------
# Both names are read from their own files. If either cannot be read, that is a
# refusal and not a pass: "we could not look" must never be recorded as "we
# looked and it was fine".
function Get-WorkerName($path) {
    foreach ($line in Get-Content $path -Encoding utf8) {
        if ($line -match '^\s*name\s*=\s*"([^"]+)"') { return $matches[1] }
    }
    return $null
}

$liveName    = Get-WorkerName $config
$testingName = Get-WorkerName $testingConfig

if (-not $liveName)    { Fail "could not read a worker name out of $config" }
if (-not $testingName) { Fail "could not read a worker name out of $testingConfig" }

if ($liveName -eq $testingName) {
    Fail @"
THE LIVE CONFIG NAMES THE TESTING WORKER ('$liveName').

Deploying would overwrite the testing site with the live payload, or - if the
name is wrong in the other direction - create a SECOND site at a second URL and
report complete success. Two URLs in circulation for one project is a failure
this project has already had once.

Fix the name in wrangler.live.toml. It must not equal the one in
testing\wrangler.toml.
"@
}

Write-Host "worker  : $liveName   (testing is '$testingName' - different, as required)"
Write-Host "url     : https://$liveName.citizencompass-contact.workers.dev"

# --- LIVE-ONLY: this payload must be the LIVE payload ------------------------
# Checked on the BYTES about to be uploaded, not on which build flag somebody
# believes they used. A --live that was lost on the way to the build (rule 12,
# second half) is caught here, where it would do the damage, by something that
# could not be lost with it.
$index = Get-Content $indexFile -Raw -Encoding utf8
if (-not $index) { Fail "could not read $indexFile - refusing to publish unverified content" }

if ($index -match 'id="cc-gate"' -or $index -match 'cc-locked') {
    Fail @"
THIS PAYLOAD CARRIES THE PRIVATE-PREVIEW PASSWORD GATE.

Publishing it to the public site would lock every visitor out behind a password
they were never given, and from the outside that looks like an outage rather
than like a mistake - so nobody would report it as one.

This is the TESTING payload. Rebuild for live:

    python testing\_src\build_deploy.py --live

then run this script again. Remember to rebuild WITHOUT --live afterwards, or
the next testing deploy will refuse (deploy_testing.ps1 checks for the gate the
same way this checks for its absence).
"@
}

if ($index -match '<title>Citizen Compass v[0-9.]+ - testing ' -or
    $index -match '>testing 20[0-9][0-9]-') {
    Fail @"
THIS PAYLOAD CARRIES THE "testing <date>" STAMP.

That stamp exists to make the testing site distinguishable from the live one.
On the live site it is simply false - it would tell every visitor they are
looking at a test build.

This is the TESTING payload. Rebuild for live:

    python testing\_src\build_deploy.py --live
"@
}

# The version string is REQUIRED, and it is reported, because this is the one
# moment somebody is deciding whether to publish it.
if ($index -match '<title>Citizen Compass (v[0-9.]+)</title>') {
    Write-Host "version : $($matches[1])   (from the payload itself, not from a note)"
} else {
    Fail "could not read a version out of $indexFile. Refusing to publish a site whose own version cannot be determined."
}

Write-Host "payload : LIVE - no password gate, no testing stamp" -ForegroundColor Green

# --- deploy guard: refuse anything that is not a known asset ----------------
# Identical to deploy_testing.ps1, on the same bytes, for the same reason.
#
# build_deploy.py runs this same check and refuses to finish a build that would
# leave junk in _deploy. That guard protects the BUILD. It does not protect the
# DEPLOY, because a deploy does not require a build - and that is exactly the
# sequence that leaked wrangler-account.json on 2026-08-06: a wrangler run from
# inside _deploy left .wrangler/ behind, and the next deploy uploaded the
# directory as it stood.
#
# FAIL CLOSED. If the checker cannot run at all - python missing, file moved,
# import error - that is NOT a pass. An unverifiable payload is refused.
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
# Same two accepted paths, in the same order, as deploy_testing.ps1:
#
#   1. wrangler is ALREADY authenticated by a stored credential
#   2. otherwise, a scoped CLOUDFLARE_API_TOKEN from .env
#
# .env is read FIRST for accuracy rather than precedence: wrangler v4 loads .env
# from the project directory itself, so once a token is present `wrangler
# whoami` reports "authenticated" BECAUSE OF that token. Asking whoami first
# and then announcing "already authenticated - no token needed" was simply
# false, and deploy_testing.ps1 carries the same note for the same reason.
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

if (-not $PSCmdlet.ShouldProcess("Cloudflare Workers ($liveName)", "PUBLISH THE LIVE SITE: $($files.Count) files from testing\_deploy")) {
    Write-Host ""
    Write-Host "-WhatIf: WOULD PUBLISH THE LIVE SITE." -ForegroundColor Cyan
    Write-Host "-WhatIf:   command   npx wrangler deploy --config `"$config`"" -ForegroundColor Cyan
    Write-Host "-WhatIf:   worker    $liveName" -ForegroundColor Cyan
    Write-Host "-WhatIf:   url       https://$liveName.citizencompass-contact.workers.dev" -ForegroundColor Cyan
    Write-Host "-WhatIf:   payload   $($files.Count) files, $totalMB MB, $modelCount models, from $assetsDir" -ForegroundColor Cyan
    Write-Host "Nothing was uploaded."
    Write-Host ""
    Write-Host "Confirm that from the OUTSIDE rather than from this message:" -ForegroundColor Yellow
    Write-Host "  curl -s -o /dev/null -w '%{http_code}' https://$liveName.citizencompass-contact.workers.dev/"
    Write-Host "  A 404 means the worker still does not exist and nothing was published."
    exit 0
}

Write-Host ""
Write-Host "PUBLISHING THE LIVE SITE..." -ForegroundColor Yellow

# ---------------------------------------------------------------------------
# $ErrorActionPreference MUST be 'Continue' across this call.
#
# Windows PowerShell 5.1 wraps every stderr line from a native executable in an
# ErrorRecord (NativeCommandError). wrangler writes an ordinary WARNING to
# stderr, so with 'Stop' the script aborts on a WARNING and reports a failed
# deploy AFTER the upload has already succeeded - reporting failure on a
# success, which is as misleading as the reverse. This cost a deploy once
# already; see deploy_testing.ps1.
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
Write-Host "  1. https://$liveName.citizencompass-contact.workers.dev/ serves index.html"
Write-Host "     (not a 404 and not a Cloudflare placeholder)"
Write-Host "  2. THERE IS NO PASSWORD PROMPT. Open it in a clean browser context."
Write-Host "     A gate on the public site is the worst outcome this can have."
Write-Host "  3. the page does NOT say 'testing <date>' beside the version"
Write-Host "  4. a MODEL serves - e.g. /models/Hammerhead.glb returns 200 with a"
Write-Host "     plausible byte count. A deploy that dropped the models folder"
Write-Host "     still loads and still looks right."
Write-Host "  5. /find and the ship page's hardpoint panel both fill with no API"
Write-Host "     running. Both read generated files; if either says it could not"
Write-Host "     reach the data, a .gen.js did not ship."
Write-Host "  6. the testing site is STILL THERE and still gated:"
Write-Host "     https://$testingName.citizencompass-contact.workers.dev/"
Write-Host ""
Write-Host "Then, and only then: docs/RELEASING-THE-SITE.md, 'after a live deploy'."
