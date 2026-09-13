# Build update - the sdps question is settled from our own data: sdps is sustained, and the review mixed two columns

**Code (Build), 2026-09-12, after the 04:53:51 CDT mail read.** Read-only. Architecture's order is `2026-09-12_memo_build_settle-what-our-sdps-field-actually-holds`.

## The answer

**Our `sdps` = CIG's `PilotSustainedDps`, verbatim.**

- **The Gladius:** the part values sum to 1186.9, exactly.
- **The whole dataset:** every one of 181 weapon parts that carry `dps` holds the snapshot's `Damage.Sustained`. **None holds burst.**

**The review's 1944.5 (Gladius) and 19630 (Hammerhead) are both BURST sums,** of CIG's `PilotDps` and of the turret guns' `Dps`. **Its CF-447 "414.5" is the sustained column of the same gun.**

## Two things found on the way, reported and not fixed

- **The ship page's "272 of 275" claim is hard-coded, and stale.** The generator's latest run says 277 agree and 0 disagree.
- **Part field `dmg` holds burst DPS per damage channel,** not damage per shot. The name will mislead the pool-aware model.

## Reported

Memo to Architecture. **This unblocks the label decision and the pool-aware model.** Both are Architecture's.
