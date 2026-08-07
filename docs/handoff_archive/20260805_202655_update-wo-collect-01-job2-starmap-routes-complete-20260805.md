# Update — job 2 (starmap join + route cost table) complete and verified

**When:** 2026-08-05

WO-COLLECT-01 rev 5 §1.1 and §1.5. Built `scripts/starmap_routes/build_routes.py`
plus `_verify_build_routes.py`. Reads only the sealed snapshot
`20260801T204744Z`; nothing re-pulled. Every row stamped with snapshot + patch
`4.9.188.23497`.

## The join

| | |
|---|---|
| starmap.json | 2,054 rows / 2,054 distinct UUID |
| starmap_positions.json | 1,774 rows / **1,196 distinct uuid** |
| overlap | **1,183** — matches the work order |
| only in starmap | 871 |
| only in positions | 13 |
| **union** | **2,066 entities** |

**The duplicate-UUID trap, which the work order's figures do not mention.**
`starmap_positions.json` has 1,774 rows but only 1,196 distinct uuids. **Nine
uuids account for all 578 extra rows** — they are *template* entities
("Asteroid Cluster" ×90, "Keeger Belt Mission Location" ×120, "Asteroid Mining
Base" ×45) reused across many physical instances, each row carrying different
x/y/z. A dict-keyed join silently keeps the last row and discards up to 119 real
positions; a row-keyed join fans the metadata out 120×. Positions are therefore
kept as a **list per uuid** and the count is reported. A further **18 rows carry
an empty uuid** (`jumppointturrets`, `jumppointlocationsecurity-*`) — counted,
not silently dropped.

## Route costs

Used `FuelConsumptionSCUPerGM`. **`FuelEfficiencyGMPerSCU` is not used and
appears in no output file, with no exemptions** — enforced by a check, not by
memory.

The work order's warning is confirmed on this snapshot, and re-checked on every
run rather than trusted:

- `FuelRequirement10GM == 10 × FuelConsumptionSCUPerGM` — **63/63 drives agree**
- `FuelEfficiencyGMPerSCU == 1/FuelConsumptionSCUPerGM` — **0/63 agree**

If a future snapshot breaks that pair, the build **refuses to run** rather than
publishing wrong fuel costs.

- 63 QuantumDrives, all carrying the fuel model
- **257 of 316 ships** have a quantum drive (59 skipped, counted)
- `range_gm` is **null**, never 0, when tank capacity is unreadable

**Coordinate unit verified, not assumed.** Max sampled Stanton pair = **119.5
Gm**, plausible for a star system, corroborating metres. A wrong unit would have
made every fuel and time figure wrong by a constant factor while still looking
reasonable.

## Pairs — sharded, as instructed

| System | qt_valid destinations | pairs |
|---|---|---|
| stanton | 546 | **148,785** — exactly the work order's figure |
| nyx | 365 | 66,430 |
| pyro | 171 | 14,535 |
| **total** | | **229,750** |

Note `qt_valid` is **1,082 rows but only 770 distinct uuids**. Pairs are built
from rows, because the template uuids denote genuinely different places —
and that is what reproduces the work order's 148,785 exactly.

## Two disagreements with the work order, reported not reconciled

1. **Jump points: 19 matched, 8 positioned, 11 unpositioned.** The order says
   13 unpositioned. `Type.Name == "JumpPoint"` finds only **2** (both
   positioned), so the order is not using the Type field; matching on the name
   containing "jump point" gives 20, of which "Jumptown" is an Outpost, leaving
   **19** — the order's total. The unpositioned count still differs. All 19 are
   listed and flagged; unpositioned ones carry `distances_available: false` and
   are never given a distance.
2. **`starmap_positions.json` has 1,774 rows, not 1,774 entities** (1,196
   distinct).

## Output size — the one place I deviated, stated plainly

"Every ship × every qt_valid pair" is 257 × 229,750 = **59,045,750 rows**. I
measured it by emitting Pyro in full: **281 MB for 915,705 rows**, extrapolating
to **19.0 GB** ship-keyed.

But `fuel_scu` and `travel_secs` depend on the ship **only through two scalars**
from its drive, so two ships with the same drive produce byte-identical rows.
Keying on the 63 drives is lossless — `ships.json` maps every ship to its drive
— and measures **4.7 GB**.

**Default is drive-keyed; `--materialise-ships` emits the literal 19 GB form.**
Routes are off by default (`--emit-routes`) so a run does not silently produce
gigabytes. The pairs table — the actual novel computation — is always emitted.

## Gates proven able to fail — 27 checks, both directions

`_verify_build_routes.py` feeds each guard known-bad input and requires
rejection, then real data and requires acceptance. **It caught a real leak while
being written**: `FuelEfficiencyGMPerSCU` appeared in `MANIFEST.json` inside my
own explanatory note, and I had exempted `drives.json` which published it under
an `_UNUSED` alias. Both fixed at the source rather than exempted — the rule is
now "appears in no output file, any casing, no exceptions", which is checkable
by machine instead of remembered.

Also proven: the fuel guard rejects a 0.1% deviation; pair generation emits
n(n−1)/2 with no self-pairs or duplicates; both cost formulae verified by hand
(1 Gm @ 0.02 SCU/Gm → 0.02 SCU; 1/10 × 60 s → 6 s); null range is never 0.

## Output

`data-layer/derived/starmap-routes/` — `entities.json` (1.2 MB), `ships.json`,
`drives.json`, `jump_points.json`, `MANIFEST.json`, `pairs/` (67 MB, 10 shards).
`pairs/` and `routes/` gitignored; the join, tables and manifest stay tracked —
same separation the external-sources rule uses. Pyro test run (281 MB) moved to
`_to_delete/` per hard rule 1.

**Nothing staged or committed.**

**Next:** the four new jobs just received; old job 3 (the targeting list) is
still outstanding and is not in that list.
