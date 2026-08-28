# Update — I ran it. It refused, correctly, and the live worker returns 404. Stopping to ask before the two steps that would change that.

**2026-08-27 21:54 local · Code (background session)** — Sleven: *"well run it"*.

## I ran it. Here is what it said

    powershell -File .\scripts\deploy_live.ps1 -WhatIf

    === LIVE SITE DEPLOY ===
    build   : last build ok (2026-08-27T21:32:11)
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    LIVE DEPLOY ABORTED: THIS PAYLOAD CARRIES THE PRIVATE-PREVIEW PASSWORD GATE.

**The gate I added an hour ago is working**: `build : last build ok` is the new
receipt gate reading the receipt and passing it. What stopped the run is the
payload-identity refusal that has been there since 2026-08-21.

**Nothing was published. The dry run never reached the point of trying.**

## Two facts that stand between here and a live site

**1. `testing/_deploy` is the TESTING payload.** It carries the private-preview
password gate and the `testing 2026-08-28` stamp. Publishing it would lock every
visitor out behind a password they were never given, which from outside reads as
an outage rather than a mistake. The script says so and refuses.

To publish I would first have to run:

    python testing\_src\build_deploy.py --live

That **strips the password gate and the testing stamp**, and it rewrites the
same directory the testing site publishes. Until it is rebuilt without `--live`,
`deploy_testing.ps1` will refuse - deliberately, each script refuses the other's
payload. So it is not one command, it is: build live, publish, rebuild testing,
redeploy testing.

**2. The live worker does not exist.**

    https://citizencompass.citizencompass-contact.workers.dev/   ->  HTTP 404

`deploy_live.ps1`'s own header says only Sleven creates it. A `wrangler deploy`
against a name that does not exist would **create the public site**, which is
the one thing that file reserves to him by name.

## So I have stopped, and this is why rather than an excuse

*"Run it"* cannot execute as given: the script refuses, correctly. Getting past
that needs a step Sleven did not name (`--live`), which disables the testing
deploy until reverted, and a `wrangler deploy` that would **create** the public
site rather than update it.

**This is the only action in this repo that cannot be taken back**, and Sleven's
recorded position at 14:10 today was that the site is not ready. He may well
have changed his mind - that is entirely his to change - but I am not going to
infer it from three words when the cost of being wrong is a public site nobody
meant to publish.

Asking now, with the exact sequence written out, rather than after.

Nothing built, nothing published, nothing committed, live site untouched.
