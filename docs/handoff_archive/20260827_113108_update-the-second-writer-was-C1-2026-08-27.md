# Update — the second writer you detected in `testing/` was C1, not a Code session

**C1, 2026-08-27 11:31 local. For the Code session that claimed M4.**

Your M4 handoff reads:

> *"A second Code session has been running since 10:59:49 and is actively
> writing `testing/_src/sc_export.js` (11:16), `loadout.src.html` and
> `cc_viewer.js` (11:09), and `checks/_verify_panel_dismiss.mjs` (11:11) — that
> is `ORDER_the-panel-will-not-close-2026-08-27.md` in flight. Hard rule 14: one
> writer per artifact. I am staying out of that area entirely."*

**Staying out was right. The attribution was wrong, and the difference matters
because it leaves a job unowned.**

Those writes are C1's. Sleven authorised C1 to take the writer role on those
files this morning, specifically so the two of us stop queueing behind each
other. `docs/ORDER_the-split-2026-08-27.md` landed at 11:23, three minutes after
your handoff — you had not seen it when you wrote that line.

## What that changes

**P1, P2, P3 and P3d are WRITTEN, not in flight.** `loadout.src.html` and
`cc_viewer.js` are finished and `node --check` passes on both. There is no
second Code session that is going to build them.

**So CODE-1 is yours and it is unowned right now.** Build, run
`checks/_verify_panel_dismiss.mjs` with each of its three mutators — every one
must go red — and deploy to testing. C1 could not: the device mount is a Linux
VM with no project venv and no network, so `build_deploy.py` dies on
`ModuleNotFoundError: sqlalchemy` and cannot be fixed there.

**Until that deploy runs, none of today's work exists for Sleven.** The picker
still cannot be dismissed and his saved settings still overwrite every default
at boot. `testing/_deploy/` is still 06:14 this morning.

Do not edit `testing/_src/loadout.src.html`, `testing/_src/cc_viewer.js` or
`checks/_verify_panel_dismiss.mjs` — rule 14 still holds, C1 is just the writer
rather than the other Code. If a mutator reports `MUTATION DID NOT APPLY`, say
so and stop; do not adjust the source to suit the check.

## And on M4 — it beat the brief

19 ships we cannot show a model for have one on Fleetyards, against the 12 C1
found by hand, and you joined on `scIdentifier` rather than on names alone.
Four of those are hulls C1's fifteen-ship list never contained: the 600i
Executive Edition, Arrastra, Aurora Mk II, Aurora SE, Fury, Merchantman and
Odin. Holding M5 until Sleven has seen the join table is the right call and C1
is not overriding it.

*C1*
