# Update - received: wire pilot_dps into the 3D viewer

Order in, starting now. The design question I was blocked on is answered:

- per hardpoint on click: that weapon's own DPS beside the item name and size
- per ship, without clicking: the pilot DPS total
- `pilot_alpha` only if it does not crowd; sustained is the number people compare
- the viewer's per-ship total MUST equal the loadout bench's, asserted not assumed
- the 24 of 167 without `pilot_dps` say it is unavailable - never blank, never 0
- the derived-position caveat stays about POSITION; DPS is read from game files
  and must not inherit that warning

Aggregation is settled and will not be re-derived: IsPilotSlaveable outermost-lock,
275/275 against real PilotDps, FixedWeapons.DpsTotal vs PilotDps trap documented.

Acceptance is all 167 counted and summing, five ships cross-checked against the
bench, a negative control on the unavailable wording, and verification by fetching
the deployed page back from the live URL rather than by a successful deploy.

Previous unit (the inverted scrubber) is filed and closed before starting this.
