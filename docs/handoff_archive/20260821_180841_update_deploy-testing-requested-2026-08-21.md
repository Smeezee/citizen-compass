# UPDATE — deploying the TESTING site, on Sleven's say-so

    from  Code, 2026-08-21
    ask   "deploy the testing site so I can review it"

Following docs/RELEASING-THE-SITE.md section 5, steps 1-2 only:

  1. rebuild the testing payload (default, no --live)
  2. deploy_testing.ps1 -WhatIf
  3. deploy_testing.ps1 for real
  4. verify from the served origin, not from the exit code

THE LIVE SITE IS NOT TOUCHED. Nothing in deploy_testing.ps1 can reach it, and
this run does not go near deploy_live.ps1 or wrangler.live.toml.

This is the first deploy carrying I1 - the hardpoint panel reading a generated
file instead of calling the API.
