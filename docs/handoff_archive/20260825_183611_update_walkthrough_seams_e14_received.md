# Update — three orders received (walkthrough, panel seams, E14 enumeration)

**Received from C1, 2026-08-25.**

**Verification of 9cd9a2a came back from a real render.** Pure white (all three
channels blown) on four hulls: ice 43.87-71.23% -> 0.032-2.391%; amber, mint,
cyan and rose were 0.000% before AND after — they never blew out at all. The
errata's severity ranking was wrong (it had measured luminance>0.9, which for a
pale colour just means being pale); the mechanism was right. Mean luminance cost
1.0-3.9% against my predicted 0.7-2.0% — my sphere-of-normals model at one
head-on view under-counts grazing normals. Knee closed.

**Now starting, in order:**

1. **The walkthrough** — `ORDER_slevens-walkthrough-A-to-Anvil-2026-08-23.md`
   as corrected by `AMENDS_the-model-gap-is-three-different-things-2026-08-24.md`.
   AMENDS read first. W1/W2 of the order are superseded. Priority is **W4**:
   six ships with no markers, five of them the same ships falling through to an
   RSI link — one root cause, find the mechanism, do not patch six pages. Then
   **W3**: Retaliator 4 markers, Sabre Peregrine 2, each Ballista 2 — two
   separate fixes, raise coverage AND state "showing 2 of 30" on the page.
2. **Panel seams** — `ORDER_panel-seams-from-real-parts-2026-08-25.md`. S2 is
   the careful one: the triangle floor is derived per hull, never pinned.
3. **E14** — the enumeration, both directions.

Standing: no `git add -A`, no live deploy, no release.
