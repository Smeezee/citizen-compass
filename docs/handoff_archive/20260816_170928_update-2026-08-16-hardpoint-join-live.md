# Update - the 29 are joined, live, and one guard turned out not to be a guard

Written up in `docs/FINDING_hardpoint-name-join-2026-08-16.md`. Verified by
fetching the deployed dataset back from the testing site.

**196 ships now render, 2,177 hardpoints, and not one ship in the viewer shows
zero.** 167 + 29.

- All five Auroras: **10 hardpoints each**, as ordered.
- The three Hercules: **29 each, not 41**. `ship_mounts.json` holds 29 for the
  A2 and the legacy `ship_specs.json` has no Hercules row at all. Reported
  rather than reconciled - the only way to make 29 into 41 is to invent twelve.
- 13 by written mapping (E1 + the Khartu-Al capital A), 16 BY RULE.

**The rule, proved with names that have never existed:**
`Gladius_Emerald_Jubilee_Edition_2955` -> Gladius,
`Hammerhead_Wikelo_Sneak_Special` -> Hammerhead,
`Reclaimer_Luminalia_2957_Livery` -> Reclaimer. No code change. Negative
controls all refuse: Zeus Mk II MR, Ares Inferno, Kraken Privateer, Galaxy.

## The correction that matters

I said the existing proportion guard would catch a wrong pair. **I measured it
and it does not.** A Gladius hull offered Hammerhead dimensions scores 0.11
against a 0.35 threshold and sails through - the guard compares SHAPE and is
blind to size on purpose, because the model library mixes metres, centimetres and
normalised units. A scale band cannot rescue it either: 19 of the 167 placed
ships legitimately sit between 0.2 and 0.8 units per metre.

So a third check was added - the edition's bounding box against the BASE HULL'S
OWN MODEL, 2% tolerance. Gladius vs Hammerhead is refused at 83.5%. It runs on 9
of the 16 rule-resolved pairs; for the other 7 the base hull has no model on disk
and that is reported as NOT PERFORMED, never as a pass.

## What had to be built

The placement could not be re-run: `place_fleet.py` ran in a cloud sandbox
against geometry that is not in this repo, and it needs numpy, which is not
installed and which I will not install without asking. So the hull vertices are
decoded locally with the DRACO decoder already vendored for the viewer, and the
placement is a pure-Python port **checked against the original** - placing the
100i reproduces C3's frame exactly and its markers to within 0.052 in unit space.

`hardpoints_fleet.json` keeps its single writer. The recovered ships are a
separate dataset merged at read time, and a key collision is a hard failure.

Not committed - new work, and the go-ahead I have does not cover it. The deploy
was ordered as the verification step and is done.
