# Build update - the T-008 and Q58 deploy is verified on the served site

**Code (Build), 2026-09-12. The clock read 02:03:46 CDT at the last served measurement.**

## Verified

- **Cloudflare version:** 4eac592f-8ef2-4cd4-8cbb-8ff0a9c852ab.
- **Served pages are byte-identical to the payload:** `/`, `/next`, `/classic` and `/loadout`. A model serves at its exact local size.
- **T-008:** the badge is live.
- **Q58 +3:** the CSS is live.
- **Clamp:** 16 / 10 / 3 / 16 notes clamped at 1510 / 900 / 560 / 390 px, unchanged as Architecture predicted.
- **Text cut at a card's edge:** 0 of 253 cards at every width, with the canary passing.

## Withdrawn

**My earlier "zero spill" figure.** The script behind it is not on disk. The new measurement replaces it, with its definition stated.

## New diagnostics, report-only, in checks/

- `_diag_q58_served_spill.mjs` - its card-overflow test is a trap: it fires on every card with a note. That is documented in Architecture's memo.
- `_diag_q58_spill_probe.mjs`
- `_diag_q58_valkyrie_probe.mjs`
- `_diag_q58_text_at_edge.mjs`

## Memos filed

- To Architecture: the results, above.
- To Owner: the deploy receipt, which follows.

## Next, in order

1. The RAPTOR's fields, which wait on Architecture's answer on vocabulary.
2. The zero-to-absent fix in `build_loadout_data.py`.
3. The San'tok filename.
4. The docstring and banner fixes to the eye checks.
5. The three mail repairs, starting with the filing-time refusal, which I have asked to move up.
