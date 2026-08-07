# Update — received WO-COLLECT-01 rev 5, three independent jobs

**When:** 2026-08-05

Sleven handed over three jobs, explicitly independent of the crew collector.
Logging on arrival per hard rule 13, before starting any of them.

**Sealed snapshots — do not re-pull:**

- `SC = data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z`
- `UX = data-layer/external-sources/uexcorp/snapshots/20260801T235530Z`

**1. The grabber (§5.1) — DOING FIRST, deadline tonight.** Go, single static
binary, folder `citizen-collector`, no installer. One hotkey → capture the SC
window (Windows.Graphics.Capture, DXGI fallback) → `captures\<utc>_<seq>.png`
plus a sibling `.json` carrying patch, build, UTC, location parsed from
`Game.log`, and the sequence number. Audible confirmation per capture. **No
OCR, no atlas, no vocabulary, no zones.** Sole purpose: answer whether the game
font is legible in a captured frame at Sleven's resolution — open since 2
August, gating the whole reading half of the collector.

**2. Starmap join + route cost table (§1.1, §1.5).** Join `starmap.json` (2,054)
to `starmap_positions.json` (1,774) on UUID; 1,183 overlap, union exceeds
either. Then fuel/time/range per ship × qt_valid destination pair. Must use
`FuelConsumptionSCUPerGM`, never `FuelEfficiencyGMPerSCU` (internally
inconsistent). Sharded output — Stanton alone is 148,785 pairs. 13 of 19 jump
points unpositioned: list and mark, no distances. Stamp every row with snapshot
id and patch `4.9.188.23497`.

**3. Targeting list (§1.2, §5.3).** 281 amenity-carrying locations × 823 typed
terminals from UEX → ranked list of named places with no price data.

**Blocker closed on arrival.** rev 5 §4.4 flags the commodity name list as the
one genuine blocker needing a UEX pull. It is already on disk:
`items_category_36.json` (158, Commodities) + `items_category_87.json` (17,
Harvestables) = 175 names. `names.dat` builds from these; no request needed.

**Standing instruction noted:** never `git add -A`; stage by explicit path.

**Next:** verifying the two snapshot paths exist and are readable, then job 1.
