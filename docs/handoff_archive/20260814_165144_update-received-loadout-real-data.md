# Update — received the loadout order. Keybinds and collector on hold; loadout only tonight.

`docs/prompt-code-loadout-real-data-2026-08-13.md`. Receipt per rule 13.
Target: deployed to the testing site by 22:00. Started 16:51.

## The job

`testing/_src/loadout.src.html` is a hand-typed mockup - 4 ships, 16 components,
honestly labelled `.mock`. The real data is on disk and already joined: 316
ships, 5,384 items, 36,584 fitted-component instances, snapshot
`20260801T204744Z`.

```
1  build_loadout_data.py -> loadout_data.gen.js   (follow build_holo_data.py)
2  every ship with data; say plainly what we do not have
3  wire the page, delete SHIPS/P and the .mock banner
4  provenance on the page - snapshot name, CIG's aggregate vs ours
5  build, verify, DEPLOY
```

## What I am NOT touching

Keybind page, exporter, `device_engine.js`, `sc_export.js`, `citizen-collector/`.
All on hold by explicit instruction.

## The one thing I will do first

§1 says pick the field list from **what the page actually reads**, not from what
looks interesting - that trim is the difference between a servable file and a
90 MB one. So the first step is reading `loadout.src.html` to enumerate every
field it renders, before touching the generator.

## Where I expect to have to say something uncomfortable

§0 says prefer CIG's precomputed aggregate over ours and **report the match
rate**, and that a disagreement is a finding rather than something to smooth
over. The aggregation maths is proven at 267/267 and 275/275 in existing
findings, so a mismatch would be news. I will report the rate either way.
