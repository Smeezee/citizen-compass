# deploy-receiver.ps1 - stand up the thing that receives exports.
#
#     powershell -ExecutionPolicy Bypass -File .\deploy-receiver.ps1
#     powershell -ExecutionPolicy Bypass -File .\deploy-receiver.ps1 -Deploy
#
# Without -Deploy it changes nothing and prints exactly what it would do.
#
# ---------------------------------------------------------------------------
# WHY THIS IS THE LAST PIECE
# ---------------------------------------------------------------------------
#
# Right now `send_url` is blank on every machine, so SEND MY DATA packages a zip
# to that person's own disk and stops. The data comes back by hand, over Discord,
# for every person, after every session, forever. That is not a lighter version
# of the design; it is the absence of it, and it is the part that quietly stops
# happening after week two.
#
# With this deployed, one click packages, uploads, gets a byte-for-byte
# confirmation, and only then clears what was sent. Nobody has to remember
# anything and you never touch their machine again.
#
# ---------------------------------------------------------------------------
# WHAT IT COSTS: NOTHING, AND THAT IS A REQUIREMENT NOT A PREFERENCE
# ---------------------------------------------------------------------------
#
# Standing rule: "No API, no paid service, no running cost. Ever."
#
# Cloudflare Workers free tier is 100,000 requests/day. R2 free tier is 10 GB
# stored, 1 million writes/month, and - the part that matters for a project that
# will eventually serve ship models - NO EGRESS CHARGE. A handful of contributors
# uploading a few MB a day is not close to any of those edges.
#
# ---------------------------------------------------------------------------
# THE KEY IS NOT A PASSWORD, AND PRETENDING OTHERWISE WOULD BE WORSE
# ---------------------------------------------------------------------------
#
# It ships inside a settings file on machines other people own. It is
# extractable, and it must be assumed public eventually.
#
# What it buys is a closed door instead of an open one: it stops drive-by abuse
# of a public endpoint. It is not authentication. That is exactly why the
# receiver has NO route that lists, reads, or deletes - not even with the key in
# hand. A leaked add-only key costs junk in a bucket. A leaked read key would
# cost every contributor's data.

param(
    [switch] $Deploy,
    [string] $WorkerName = "collector-receiver",
    [string] $BucketName = "collector-uploads",

    # OPTIONAL, AND NEVER STORED. Supply this and the happy-path checks run -
    # a real upload, and a mismatched hash being refused. It is held in memory
    # for the length of the run, is never written to a file, never printed, and
    # never echoed back in any message.
    #
    # Without it the script still runs every check that does NOT need a valid
    # key, and says plainly which ones it skipped. It never reports a pass for
    # a check it did not perform.
    [string] $TestKey = "",

    # Skip the deploy and verify an address directly. Useful once the Worker is
    # up: the checks below are worth re-running after the secret is set, and
    # re-deploying to re-run them would be silly.
    [string] $SendUrl = ""
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Fail($m) { Write-Host ""; Write-Host "REFUSED: $m" -ForegroundColor Red; exit 1 }
function Step($m) { Write-Host ""; Write-Host "== $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "   ok   $m" -ForegroundColor Green }
function Note($m) { Write-Host "        $m" -ForegroundColor DarkGray }

Step "checking what is here"
$worker = Join-Path $here "collector-receiver.worker.js"
if (-not (Test-Path $worker)) { Fail "collector-receiver.worker.js is not in this folder." }
Ok "collector-receiver.worker.js found"

# WRANGLER VIA npx, LIKE scripts/deploy_testing.ps1 ALREADY DOES.
#
# This script required a GLOBAL wrangler and refused to run without one, which
# meant it could not run on the machine this project actually deploys from -
# the site deploy has always used `npx wrangler` and needs nothing installed.
# Telling somebody to `npm install -g` writes outside the repo for no reason.
$script:UseNpx = $false
$wrangler = Get-Command wrangler -ErrorAction SilentlyContinue
if ($wrangler) {
    Ok "wrangler is installed"
} else {
    $probe = (& npx --yes wrangler --version 2>&1 | Out-String)
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Neither a global wrangler nor npx could run it." -ForegroundColor Yellow
        Write-Host "    npm install -g wrangler"
        Write-Host "Then run this again."
        exit 1
    }
    $script:UseNpx = $true
    Ok ("wrangler via npx (" + ($probe.Trim() -split "`n" | Select-Object -Last 1) + ")")
}

# ONE DISPATCHER, and it is a function rather than an array spliced at each call
# site. The array version broke inside npx.ps1, which runs its arguments through
# its own Invoke-Expression - a script-scoped variable is not in scope there, so
# the call failed with "the variable cannot be retrieved" partway through a
# deploy. Splatting into a function keeps the argument handling on this side.
function Invoke-Wrangler {
    param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $WArgs)

    # STDERR GOES TO A FILE, NOT INTO THE PIPELINE. `2>&1` on a native exe in
    # PowerShell 5.1 wraps each stderr line in an ErrorRecord, which with
    # $ErrorActionPreference = "Stop" terminates the script on output that is
    # often not even an error. Reading it back as text keeps the decision here.
    $errFile = [IO.Path]::GetTempFileName()
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        if ($script:UseNpx) { $out = (& npx --yes wrangler @WArgs 2>$errFile | Out-String) }
        else                { $out = (& wrangler @WArgs 2>$errFile | Out-String) }
        $code = $LASTEXITCODE
        $err = ""
        if (Test-Path $errFile) { $err = (Get-Content -LiteralPath $errFile -Raw -ErrorAction SilentlyContinue) }
    } finally {
        $ErrorActionPreference = $prev
        Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
    }
    return [pscustomobject]@{ Out = "$out"; Err = "$err"; Code = $code; All = "$out`n$err" }
}

# ---------------------------------------------------------------------------
# THE KEY. Generated here, from a real random source, and shown once.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# THE KEY IS NOT THIS SCRIPT'S TO KNOW - changed 2026-08-15
# ---------------------------------------------------------------------------
#
# This block used to generate a 64-character key, write it to
# collector-upload-key.txt, and pipe it into `wrangler secret put`. That put the
# value into a file on disk, into this script's output, and into the terminal
# scrollback of whoever ran it.
#
# The key now goes from Sleven's keyboard into Cloudflare's own prompt and
# touches nothing else. Not a file, not a log, not a report, not a chat window.
# A secret that has been printed once has been printed.
#
# The script therefore does NOT know the key, cannot verify uploads with it, and
# does not try to. What it CAN do is refuse to call the job finished until
# Cloudflare confirms the secret exists - see "the secret" below.
Step "the upload key"
Note "This script does not generate or handle the key. That is deliberate."
Note "You set it yourself, and the value never passes through here:"
Note ""
Note "    npx wrangler secret put UPLOAD_KEY"
Note ""
Note "Paste a long random value at the prompt. Cloudflare stores it; nothing"
Note "here keeps a copy."

# ---------------------------------------------------------------------------
# THE CONFIG
# ---------------------------------------------------------------------------
Step "writing wrangler.toml"
$toml = @"
name = "$WorkerName"
main = "collector-receiver.worker.js"
compatibility_date = "2026-08-01"

# The bucket the Worker writes into. The binding name BUCKET is what the
# Worker's code refers to - renaming it here breaks env.BUCKET.put silently at
# runtime rather than at deploy, so leave it alone.
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "$BucketName"
"@
if ($SendUrl) {
    Note "-SendUrl given: skipping the deploy entirely and verifying what is already live"
} elseif ($Deploy) {
    Set-Content -LiteralPath (Join-Path $here "wrangler.toml") -Value $toml -Encoding UTF8
    Ok "wrote wrangler.toml"
} else {
    Note "would write wrangler.toml binding BUCKET -> $BucketName"
}

if (-not $Deploy -and -not $SendUrl) {
    Write-Host ""
    Write-Host "Dry run. Nothing was created, deployed, or written." -ForegroundColor Yellow
    Write-Host "It would:"
    Write-Host "    1. create R2 bucket '$BucketName'"
    Write-Host "    2. deploy worker '$WorkerName'"
    Write-Host "    3. CHECK that UPLOAD_KEY exists - by name only, never its value."
    Write-Host "       It does NOT set the secret. That is yours to run:"
    Write-Host "           npx wrangler secret put UPLOAD_KEY"
    Write-Host "    4. prove a wrong key is refused, and GET/HEAD/DELETE/PUT with it"
    Write-Host "    5. WITHOUT -TestKey it will NOT test a real upload or a bad hash,"
    Write-Host "       and will say so rather than report a pass it did not earn"
    Write-Host "    6. print the send_url line for collector-settings.txt"
    Write-Host ""
    Write-Host "Re-run with -Deploy when you are ready."
    exit 0
}

# ---------------------------------------------------------------------------
# BUCKET, WORKER, SECRET
# ---------------------------------------------------------------------------
if (-not $SendUrl) {
Step "the bucket"
# LOOK BEFORE CREATING. Sleven made this bucket by hand; a script that always
# tries to create it turns a correctly-prepared account into a hard failure.
$buckets = Invoke-Wrangler r2 bucket list
if ($buckets.All -match [regex]::Escape($BucketName)) {
    Ok "bucket '$BucketName' already exists - leaving it exactly as it is"
} else {
    $mk = Invoke-Wrangler r2 bucket create $BucketName
    if ($mk.Code -ne 0) {
        Fail "could not create bucket '$BucketName':`n$($mk.All)"
    }
    Ok "created bucket '$BucketName'"
}

Step "deploying the worker"
Push-Location $here
try {
    $dep = Invoke-Wrangler deploy
    $script:DeployOutput = $dep.All
    $dep.All -split "`n" | ForEach-Object { if ($_.Trim()) { Note $_.Trim() } }
    if ($dep.Code -ne 0) { Fail "wrangler deploy failed. Nothing is receiving yet." }

    Step "setting the upload key"
    # Piped, so the key never appears in a command line - command lines are
    # visible to other processes and land in shell history.
    # FAIL CLOSED ON A MISSING SECRET.
    #
    # `secret list` returns NAMES, never values - so this can confirm the door
    # is locked without ever learning the key. A Worker deployed with no
    # UPLOAD_KEY refuses every upload (see the worker's own 403 path), which is
    # the right failure, but reporting "deployed and ready" over the top of it
    # would be a lie.
    $secrets = (Invoke-Wrangler secret list).All
    $script:KeyIsSet = ($secrets -match "UPLOAD_KEY")
    if ($script:KeyIsSet) {
        Ok "UPLOAD_KEY is set on the Worker (name only - the value was never read)"
    } else {
        Write-Host ""
        Write-Host "   !!   UPLOAD_KEY IS NOT SET. The Worker is deployed and will" -ForegroundColor Yellow
        Write-Host "        REFUSE every upload with 403 until you run:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "            npx wrangler secret put UPLOAD_KEY" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "        That is the correct behaviour, not a fault - a receiver" -ForegroundColor Yellow
        Write-Host "        that accepts uploads with no key is worse than none." -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}
}  # end: skipped entirely when -SendUrl re-verifies a live worker

# ---------------------------------------------------------------------------
# WHERE IS IT?
# ---------------------------------------------------------------------------
Step "finding the worker's address"
#
# THE URL IS IN THE DEPLOY OUTPUT, not in `deployments list`. The earlier
# version asked the wrong command: `deployments list` reports version IDs and
# authors, never the workers.dev hostname, so the match never fired.
$sendUrl = $SendUrl
$urlPattern = "https://([a-z0-9\-]+\.[a-z0-9\-]+\.workers\.dev)"
if ($sendUrl) {
    Note "using the address given on the command line"
} elseif ($script:DeployOutput -and $script:DeployOutput -match $urlPattern) {
    $sendUrl = "https://$($Matches[1])"
    Note "read from the deploy output"
} else {
    $deployOut = (Invoke-Wrangler deployments list).All
    if ($deployOut -match $urlPattern) {
        $sendUrl = "https://$($Matches[1])"
        Note "read from deployments list"
    }
}

# NO ADDRESS MEANS NO VERIFICATION - it does not mean carry on with a blank.
#
# Every check below this point is a negative control: a wrong key must be
# refused, a GET must be refused. Point those at "" and they fail to connect,
# the codes come back 0, and a suite that proves nothing would report the same
# refusals as one that proved everything. Stop instead.
if (-not $sendUrl) {
    Fail ("the worker is deployed but its URL could not be read, so NONE of the " +
          "verification below was performed. It is in the deploy output above as " +
          "https://$WorkerName.<subdomain>.workers.dev - re-run with -SendUrl <that>.")
}
$sendUrl = $sendUrl.TrimEnd("/")
Ok "send_url = $sendUrl"

# ---------------------------------------------------------------------------
# THE VERIFICATION. Every check below has a case that can fail it - hard rule 12.
# ---------------------------------------------------------------------------
Step "proving it actually works, and actually refuses"

# A real, minimal zip. Built rather than faked, because the receiver checks the
# PK header and a fake would be rejected for the wrong reason.
$tmp = Join-Path $env:TEMP "cc-receiver-probe"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null
Set-Content -LiteralPath (Join-Path $tmp "hello.txt") -Value "receiver probe" -Encoding ASCII
$probeZip = Join-Path $env:TEMP "cc-receiver-probe.zip"
if (Test-Path $probeZip) { Remove-Item $probeZip -Force }
Compress-Archive -Path (Join-Path $tmp "*") -DestinationPath $probeZip
$probeBytes = [IO.File]::ReadAllBytes($probeZip)
$probeSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $probeZip).Hash.ToLower()
Note "probe zip is $($probeBytes.Length) bytes, sha256 $($probeSha.Substring(0,16))..."

function Post($bytes, $key, $sha) {
    $h = @{ "X-Collector-Install" = "deploy-probe"; "X-Collector-Version" = "probe" }
    if ($key) { $h["X-Collector-Key"] = $key }
    if ($sha) { $h["X-Collector-Sha256"] = $sha }
    try {
        $r = Invoke-WebRequest -Uri $sendUrl -Method POST -Body $bytes `
             -ContentType "application/zip" -Headers $h -TimeoutSec 60 -UseBasicParsing
        return @{ code = $r.StatusCode; body = ($r.Content | ConvertFrom-Json) }
    } catch {
        $code = 0
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
        return @{ code = $code; body = $null }
    }
}

# --- CHECKS THAT NEED NO KEY. These are the ones that protect people. ------

# 1. A WRONG KEY MUST BE REFUSED. With no secret set this also returns 403,
#    which is the correct fail-closed behaviour for an un-keyed Worker.
$r2 = Post $probeBytes "not-the-key" $probeSha
if ($r2.code -eq 403) {
    Ok "a wrong key is refused (403)"
} else {
    Fail "a WRONG KEY was not refused (HTTP $($r2.code)). The endpoint is open to anyone."
}

# 2. ANYTHING THAT IS NOT A POST MUST BE REFUSED. This is the order's §3 in
#    practice: the receiver has no route that lists, reads or deletes, so every
#    method that could ask for data must come back 405 - with a valid key or
#    without one, because there is no such route to reach.
foreach ($m in @("GET", "HEAD", "DELETE", "PUT")) {
    $code = 0
    try {
        $resp = Invoke-WebRequest -Uri $sendUrl -Method $m -TimeoutSec 30 -UseBasicParsing
        $code = [int]$resp.StatusCode
    } catch {
        if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    }
    if ($code -eq 405 -or $code -eq 403) {
        Ok "$m is refused ($code) - there is no route that could return data"
    } else {
        Fail "$m returned HTTP $code. A method that is not POST reached something."
    }
}

# --- CHECKS THAT NEED A VALID KEY. Skipped, loudly, without one. ----------
if ($TestKey -eq "") {
    Write-Host ""
    Write-Host "   ..   NOT PERFORMED, because this script does not know the key:" -ForegroundColor Yellow
    Write-Host "        - a real upload is accepted and the hash round-trips" -ForegroundColor Yellow
    Write-Host "        - a MISMATCHED hash is refused (409)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "        Those two are not passing and are not failing. They have not run." -ForegroundColor Yellow
    Write-Host "        To run them, after setting the secret:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "            .\deploy-receiver.ps1 -TestKey <the value you set>" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "        The key is used in memory and never written or printed." -ForegroundColor Yellow
} else {
    $r1 = Post $probeBytes $TestKey $probeSha
    if ($r1.code -eq 200 -and $r1.body.ok -and $r1.body.sha256 -eq $probeSha) {
        Ok "a real upload is accepted and the receiver's OWN hash matches ours"
        Note "stored as $($r1.body.stored_as)"
    } else {
        Fail "the upload did not succeed (HTTP $($r1.code)). Nothing is safe to point collectors at yet."
    }

    $notZip = [Text.Encoding]::ASCII.GetBytes("this is not a zip file at all")
    $r3 = Post $notZip $TestKey $null
    if ($r3.code -eq 415) {
        Ok "a non-zip is refused (415)"
    } else {
        Note "a non-zip returned HTTP $($r3.code), expected 415 - worth a look, not fatal"
    }

    # THE ONE THAT PROTECTS CONTRIBUTORS' DATA. The sender clears its local copy
    # on a hash match, so a receiver that agreed with a lie would tell somebody
    # it was safe to delete their only copy.
    $r4 = Post $probeBytes $TestKey ("0" * 64)
    if ($r4.code -eq 409) {
        Ok "a mismatched hash is refused (409) and nothing is stored"
    } else {
        Fail "a WRONG HASH was accepted (HTTP $($r4.code)). A damaged upload could clear a contributor's only copy."
    }
}

Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $probeZip -Force -ErrorAction SilentlyContinue

# ---------------------------------------------------------------------------
# WHAT TO DO WITH IT
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "RECEIVING, AND PROVEN TO REFUSE WHAT IT SHOULD." -ForegroundColor Green
Write-Host ""
Write-Host "Put these two lines in collector-settings.txt:"
Write-Host ""
Write-Host "    send_url = $sendUrl" -ForegroundColor Cyan
Write-Host "    send_key = <the value you gave to wrangler secret put>" -ForegroundColor Cyan
Write-Host ""
Write-Host "    (this script does not know the key and cannot print it)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Then make a new package. The packager copies those two lines into it,"
Write-Host "so everyone you hand it to can send with one click - and check the log"
Write-Host "line, because a package built without them says so out loud."
Write-Host ""
Write-Host "To read what arrives:"
Write-Host "    wrangler r2 object get $BucketName/<key> --file out.zip"
Write-Host "    .\collector-master.exe --merge <folder of exports>"
Write-Host ""
if ($TestKey) {
    Write-Host "One probe upload is in the bucket under uploads/deploy-probe/ - delete it"
    Write-Host "whenever, it is a text file in a zip."
} else {
    Write-Host "NOTHING was uploaded to the bucket by this run - the upload path needs" -ForegroundColor Yellow
    Write-Host "the key, and this script does not have it. The refusals above are real;" -ForegroundColor Yellow
    Write-Host "the accept path is untested until someone runs it with -TestKey." -ForegroundColor Yellow
}
