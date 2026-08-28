# Update — The live dry run, in full. All gates green, nothing published, and the testing payload came back byte for byte.

**2026-08-27 21:59 local · Code (background session)** — Sleven chose the dry
run. Testing version `bbd2a7d7-7979-4980-8984-7f1e9dec042c`.

## What the live script says with a real LIVE payload in front of it

    === LIVE SITE DEPLOY ===
    build   : last build ok (2026-08-27T21:43:00)
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    version : v0.4.0   (from the payload itself, not from a note)
    payload : LIVE - no password gate, no testing stamp
    guard   : _deploy contains only known assets
    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN
    check   : _verify_armour_naming.mjs ... GREEN
    checks  : all browser checks green
    payload : 524 files, 456.7 MB
    models  : 258 .glb files
    largest : Tyilui.glb (17.19 MB)
    auth    : scoped token loaded from .env (length 53, not shown)

    -WhatIf: WOULD PUBLISH THE LIVE SITE.
    -WhatIf:   worker    citizencompass
    -WhatIf:   payload   524 files, 456.7 MB, 258 models
    Nothing was uploaded.

**Both gates I added an hour ago ran on the live path for the first time, on the
real payload, and both passed** - the receipt read and accepted, four browser
checks driven against the very bytes that would have gone out. Two hours ago
this script ran neither.

## Confirmed from the OUTSIDE, which is what the script itself insists on

    https://citizencompass.citizencompass-contact.workers.dev/   ->  HTTP 404

**The worker still does not exist. Nothing was published.** The public site is
exactly as it was.

## The round trip, measured rather than assumed

`--live` rewrites the same directory the testing site publishes, so the risk was
never the dry run - it was leaving the public build sitting in `testing/_deploy`.
I hashed every non-model file before starting and compared after the rebuild:

    files before 266 | now 266 | identical 266
    DIFFERENT: none - the testing payload is byte-for-byte what it was

Redeployed testing to prove the path still works after the round trip:
**"No updated asset files to upload"** - exactly right, because the payload never
actually changed. The served page carries its password gate, and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

## What this told us that the control could not

`_verify_deploy_guards.py` proves the gates refuse bad input against throwaway
trees. **This is the first time the live script has been driven end to end
against the real 456 MB payload**, and the useful new fact is that it gets all
the way through - the guard, four real browser checks, the file and size
ceilings, the credential load - and stops exactly where it is supposed to.

**The version it reports, `v0.4.0`, it read out of the payload itself.** Worth
saying because a version taken from a note is the kind of thing that is right
until the day it is not.

## Where it leaves going live

One command away, and that command is Sleven's:

    python testing\_src\build_deploy.py --live
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1
    python testing\_src\build_deploy.py          <- put testing back
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

**The first real run CREATES the worker** rather than updating one, since the
name 404s today. That remains his to do, and nothing about tonight changes it.

Probe files moved to `_to_delete/probes-2026-08-27/`, never deleted. Nothing
committed, nothing pushed, live site untouched.
