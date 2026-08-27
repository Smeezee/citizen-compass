# UPDATE — the I-run is complete and pushed

    from  Code, 2026-08-21
    order docs/ORDER_the-public-site-needs-no-server-and-live-gets-a-deploy-script-2026-08-21.md
    head  63a3a21, pushed to origin/main (67e441a..63a3a21, 16 commits)

All eight items DONE. None BLOCKED.

    I1  the hardpoints became a file      a05a021
    I2  deploy_live.ps1, dry run only     0a4d5ed
    I3  docs/RELEASING-THE-SITE.md        05f6a0c
    I4  one source of truth for VERSION   6ef55fc
    I5  what changes when live flips      ebb3a07
    I6  404 sweep, clean                  7245ec9
    I7  no _deploy drift                  e089b02
    I8  sweep, 42 of 42                   1f44a14

THE LIVE SITE WAS NOT DEPLOYED. The worker does not exist; the URL returns 404,
and that 404 is the proof the dry run published nothing.

## Waiting on you

1. **Create the live worker** — only you can. Then `deploy_live.ps1` is ready.
2. **Ship names stop linking straight to RSI** after the flip. Build decision,
   settle it before, not after.
3. **/holo, /download and /stick-test are linked from nowhere.** Intended?
4. **Netlify does not retire itself.** Two public URLs until you take it down.

Nothing else is in flight. `_deploy` holds the TESTING payload, VERSION is
0.4.0, and every control passes.
