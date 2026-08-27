# UPDATE — I2 DONE: the live site has a deploy script. It was NOT run.

    from  Code, 2026-08-21
    item  I2 of the 2026-08-21 order
    sha   0a4d5ed

`scripts/deploy_live.ps1` + `wrangler.live.toml`, mirroring the testing pair.
Different worker (`citizencompass` vs `citizencompasstesting`), its own file,
and the two names are read out of BOTH configs and refused if they match.

**-WhatIf, run for real:** worker `citizencompass`, url
`https://citizencompass.citizencompass-contact.workers.dev`, 497 files,
350.8 MB, 235 models, version v0.4.0 read out of the payload itself.

**The control, from outside rather than from the flag:** after the dry run that
URL and its /index.html both return **404** — the worker still does not exist,
so nothing was published. The testing site returned 200 throughout.

Both scripts publish `testing/_deploy`, because what you review has to be the
bytes that ship. `build_deploy.py --live` omits the password gate and the
"testing <date>" stamp, and **each script refuses the other's payload** by
looking at the bytes. Every refusal was observed firing, then made repeatable:
`checks/_verify_deploy_guards.py`, 43 assertions, runs the real scripts.

BLOCKED ON YOU, and this is the stop the order built in: the live worker does
not exist. Only you create it. Nothing ships without your say-so.

Also for you to decide separately: citizencompass.netlify.app is still serving.
Nothing here can touch it; retiring it is manual.

Next: I3, docs/RELEASING-THE-SITE.md.
