# Update — the six loadout files are pushed, and C1's holo/loadout join finding independently confirms two things tonight's build hit head-on.

## Pushed

```
ccd3f0c..1d41168  main -> main
local and origin both at 1d411682a4d9ff951dda40ff6a6af1a7ee715982
```

Six files, staged by path:

```
build_loadout_data.py                 510 lines   new
testing/_src/loadout_data.gen.js       21 lines   new (431 KB)
testing/_src/_verify_loadout_data.js  155 lines   new, registered as a build gate
testing/_src/loadout.src.html         457 lines
testing/_src/build_deploy.py          592 lines
testing/_src/check_deploy_clean.py    227 lines
```

A stale `.git/index.lock` blocked the first attempt - 0 bytes, 13 minutes old,
no git process. Moved to `_to_delete/`, per rule 1. Second one this week; both
times the same shape.

## The finding corroborates two things I found the hard way tonight

Read `docs/FINDING_holo-loadout-join-is-100-percent-2026-08-13.md`. Two of its
sections describe, independently, exactly what bit me:

**§4, the three false gaps.** *"PowerPlant, Cooler and MissileLauncher do not
carry a stat block named after themselves... Cooler -> ResourceNetwork as a
CONVERSION: Power 3 -> Coolant 38."*

That is precisely the defect I hit: all 81 coolers came out with no cooling
figure because I read Consumption and Generation but not Conversion, and every
ship would have rendered as overheating. Two independent passes found the same
trap, which is a good sign the finding is right about it recurring.

**§2, the nested tree.** *"A shallow read of Loadout[] finds 14 pilot guns and
260 turrets and looks wrong... the guns hang inside the gimbal mounts.
Recurse, or you will build a weapon picker that cannot see any weapons."*

My walk recurses, so this one I got right by accident of writing it that way
rather than by knowing. Worth having read it.

**§5** confirms the maths I used - the `IsPilotSlaveable` outermost-lock rule
at 275/275, which my generator reproduced independently tonight.

## What it changes for the merge, when that comes

- **The join is exact**: 167/167 ships, 1798/1798 ports, zero misses. The
  expensive part is done, so the 3D swap tool is plumbing rather than research.
- **Coverage differs from tonight's page.** The loadout bench now carries 310
  ships; the hull-marker merge covers the **167** that have hardpoint data.
  ~68 deployed models have none yet.
- **One thing I dropped tonight is worth revisiting there.** I removed
  `MissileLauncher` from the page's slot types because those records carry no
  DPS - but §4 says they do carry stats, under `MissileRack { MissileCount }`.
  Correct to leave them off a DPS bench; wrong to leave them off a hull-marker
  picker, where 157 of the reachable editable slots are MissileLaunchers and
  1245 are Missiles.
- **699 editable slots (5.3%) have no `CompatibleTypes`.** Per the finding those
  must say "we don't know what fits here" rather than showing an empty list -
  the same discipline as the unreleased ships on tonight's page.

## Not doing anything with it yet

It is flagged for the next collector pass, and the collector is paused. Nothing
started, nothing half-built.

Also noted: the watcher needs no restart. No action taken.
