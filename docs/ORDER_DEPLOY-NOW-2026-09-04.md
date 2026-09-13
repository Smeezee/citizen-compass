# ORDER — DEPLOY. Nothing else. Sleven is blocked and waiting.

From: C1 (Cowork), 2026-09-04
For: Code

The build is done and clean. Receipt: `2026-09-04T18:50:16 ok`. The payload carries
the orientation fix and the two Carrack bundles removed. **It has not been uploaded**,
so Sleven is still looking at 256 ships facing backwards while he walks them.

He has said go. There is nothing left to decide.

## RUN THIS NOW

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

If the sweep receipt is stale against the new payload and the script refuses, re-run
the sweep and then deploy:

```
python checks\run_all_controls.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

**Do not use `-IgnoreSweep`.** If it refuses for a real reason, say what the reason is
in one line and stop — but say it, do not go quiet.

## Then post ONE line
Deployed, version id, and confirm from the served bytes that `/_inspect` contains
`Math.PI+0.9`.

## For the record — why I am not doing this myself
I cannot. `deploy_testing.ps1` is PowerShell on the Windows machine; a Cowork session
gets a Linux VM with no PowerShell. Calling `wrangler` by hand from here would skip
the sweep, the browser checks and the deploy guard — which is precisely the sequence
that put twelve wrong models live on 2026-08-27. I am not cutting that corner to save
a minute. The button is yours.
