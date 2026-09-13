# ORDER — STOP RESEARCHING, FIX THE MARKED SHIPS AND DEPLOY TESTING.

From: C1 (Cowork), 2026-09-05
For: Code

Sleven walked all 256 ships and his verdict is that they look good apart from
the handful he marked. **He is right and I lost the plot.** I went from his
short defect list to rebuilding the model pipeline from the game client. That
research is real and it is written down, but it is not what he asked for and it
is not blocking anything. **It is now parked.**

This order is the short list, done, built and deployed to testing. Nothing else.

---

## 1. Clear the 20 stale marks

Already fixed by deploys that landed while he was still walking:

- **600i Executive Edition** — vertex colours.
- **Carrack w C8X**, **Carrack Expedition w C8X** — removed from the list.
- **Seventeen "facing away / needs turning around" marks** — fixed by the orbit
  change. All seventeen predate that deploy.

Move them to a resolved state with his note text preserved. Do not silently
delete the notes.

## 2. Three framing re-checks

Fit radius went `1.2 -> 1.45` after he marked these. Render each at the current
radius and confirm the whole hull is in frame:

- ATLS
- ATLS GEO
- Reliant Kore

If one is still cropped, report it. Do not change the global radius — that
affects all 256 and it is my call.

## 3. The Fury — remove the doubled geometry. AUTHORISED.

594 `<name>` / `<name>.001` pairs. **Exactly 301 of them sit at identical world
positions** — the same mesh drawn twice in the same place, which is what makes
its surface look wrong. Remove one node of each of those 301 pairs.

**Only the pairs whose accumulated world translations match to within 1e-6.**
The other 293 are displaced by up to 3.33 m and are real, separate parts. Leave
them.

**If your count is not exactly 301, stop and report the difference.** Preserve
the previous file under `_to_delete/`.

## 4. The 85X — REPORT ONLY, and do not de-duplicate it by name

It is **two complete ships parked side by side, 8.75 m apart.** X histogram of
its mesh nodes has two clusters with two clear metres of empty space between
them: one centred near X = 0, one near X = 8.75.

**The `.001` suffix does NOT separate them.** The nodes without `.001` already
span the full width of both ships, so deleting every `.001` would take pieces
out of both and leave two broken hulls. The split that means something is
spatial, not by name.

**Task: render three images, same camera — the whole file, then only nodes with
world X < 4, then only nodes with world X >= 4.** That shows which cluster is
the real 85X. Change nothing until Sleven has looked.

## 5. Build and deploy testing

Then report what changed.

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

---

## Still open, NOT in this order — do not start these

Centurion (wrong ship), the five Constellations (gear down), the four
Freelancers (old airframe), X1 / X1 Force / X1 Velocity / Cyclone TR
(see-through). I have a way to rebuild those specific hulls from the game files
and that is my job, not yours. You will get finished replacement `.glb` files or
you will get told it did not work.

## Standing constraints

- **Testing only. Do not deploy the live site.**
- Do not `git add -A`. Nothing commits or pushes without Sleven's explicit
  go-ahead.
- Never delete — `mv` to `_to_delete/`.
