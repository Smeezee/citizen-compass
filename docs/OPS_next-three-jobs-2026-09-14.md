# OPS — next three coding jobs (ranked)
**Date:** 2026-09-14  
**After:** RSI schedule DONE, tray clean, wake marker-first, livever fold (in flight), P15 unblock GO to Build

## 1. Unblock / land P15 testing deploy (with Build)
Highest user-visible. Ops cleared the three letter defects. Build quiet-sweeps then `deploy_testing`. Ops stands by for any new red that is Architecture-owned. If Build is idle, Ops can run the quiet sweep controls ourselves and hand a green receipt.

## 2. Finish wake-on-mail POST path
Tool + webhook routine + backup cron exist. Agent cannot read host webhook URL from disk. Options: (a) Owner one-click paste from routine panel deep link into `ops-mail-wake-settings.json`, or (b) product change exposing URL to the agent. Until then marker file + 2h backup cron is the live path. Optional: register `CitizenCompass-OpsMailWake` logon task once URL is set.

## 3. SC Brain acquisition step 2+ (non-colliding with Intelligence)
With RSI firehose on a timer, next coding is plumbing that Intelligence can fill: harden `ask_sc_brain.py` / indexes, roadmap pointer sync on watcher wake, and the next acquisition map shelf that does not steal gather (e.g. build-truth ingest from existing roadmap-watcher cards). Coordinate with Intelligence desk; Ops owns tools, they own gather.

### Parked / not next
- Operations desk tray (router desk name) — needs Owner map freeze.
- Org-wide tray wipe of Build’s 85 open — Owner only.
- LIVE publish — Owner only.