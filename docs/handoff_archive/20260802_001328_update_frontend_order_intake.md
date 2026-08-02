# UPDATE — front-end build order received, starting

Filed on intake per rule 13.

## Received

`docs/order-front-end-build.md`, constructed by C1 from C2's plan.
`docs/workorder-front-end-build-plan.md` is the input; the order is the order,
and where they differ the order wins.

## The four corrections I am acting on, not the stale plan

1. **The LOADOUT tab was not wiped by a rebuild.** C1 removed it deliberately on
   Sleven's instruction and a later write restored it. Implementing C2's 8a
   would make that removal impossible. Recommend only, do not implement.
2. **8b is already built and proven.** It needs `find.src.html` added to `PAGES`
   and the guard re-proven with three entries.
3. **The Loadout-array finding is confirmed** — 10 of 10 ships across
   manufacturers carry the full schema. Not re-verifying.
4. **Ship identity is already resolved** — `data-layer/ship_resolution.json`,
   215 of 254 matched. Use it, do not re-derive.

## What I will do, and then stop

1. Add `find.src.html` to `PAGES` and re-prove the guard per rule 12.
2. Report a tab layout recommendation. **No implementation.**
3. Put the backend decision in front of Sleven with the numbers, including the
   hard 20,000-file Cloudflare static-asset ceiling. **Not mine to take.**

Builds A, B and C are downstream of 2 and 3 and I am not starting them.

## Boundaries held

Live site, `releases/latest.html`, `static/preview.html` and sealed snapshots
untouched. No FastAPI work. No tab emission.
