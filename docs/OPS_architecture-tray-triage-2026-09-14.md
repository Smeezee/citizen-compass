# Architecture open-tray triage (Ops, 2026-09-14)

**Count at scan:** ~63 files under `correspondence/open/architecture/`.
**This pass:** answered 3 hottest actionable Build receipts only. Did not clear the tray.

## Classes

| Class | Meaning | Action |
|---|---|---|
| **Actionable now** | Build waiting on a stamp / next-item / GO | Answer in mail-bridge caps (max 3/cycle) |
| **Superseded** | Later commit or letter closed the ask; Status still Open | Close/answer-in-place or move to answered on next cycles |
| **Stale noise** | Pre-cutoff tray-noise, twins, already-cited closed | Batch-close from prior tray-noise dry-run; no new design |
| **Router / B1–B3** | Citation gaps, B3 apply receipts | Process only when Build is blocked; else leave |
| **Owner-gated** | Task Scheduler, LIVE publish, money | Leave for Owner; do not pretend Ops can stamp |

## Hottest remaining (examples, not a full audit)
- B1 router citation-gap letters still Open
- Older "what next" / B3 proposal letters likely superseded by later GOs
- Any letter still demanding Research endpoints for RSI → superseded by Research answer + example settings (2026-09-14)

## Rule for next cycles
Process newest Open Build receipts first. Cap 3. Silence if none new vs `_ops_state`.

## Batch-clean result
See [[OPS_architecture-tray-batch-clean-2026-09-14]] — 63→7 open.
