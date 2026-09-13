# ORDER — ADDENDUM to the fleet-walk triage. I measured 3a myself. DO NOT DE-DUP BY NAME.

From: C1 (Cowork), 2026-09-05
For: Code
Amends: `docs/ORDER_fleet-walk-triage-256-of-256-2026-09-04.md`, section 3a

I asked you to report on the 85X and Fury duplicate mesh pairs. I have since
measured it myself, so **section 3a of that order is answered — do not spend
time on it.** What I found changes the instruction, because the obvious fix is
wrong on one of the two ships and would destroy it.

---

## The measurement

Node world positions accumulated through the parent chain, read from the
deployed `.glb` JSON chunks. Every `<name>` / `<name>.001` pair compared.

```
                      pairs   coincident   displaced   same mesh data
85X                     344            3         341              343
Fury                    594          301         293              544
```

**Nearly every pair points at the same mesh.** These are not duplicated
vertices — they are the same geometry instanced twice. So the file is not as
bloated as the mesh count suggests, and the fix is a node-graph edit, not a
mesh rebuild.

Neither ship's pairs are mirrors. I tested for a sign flip on one axis with the
other two held: 0 of 344 on the 85X, 2 of 594 on the Fury. **They are rigid
translations, not left/right parts.**

## The 85X is two whole ships parked side by side, and the `.001` suffix does NOT separate them

X histogram of every mesh-bearing node, 1 metre bins:

```
  -4..  -3  # 1
  -3..  -2  # 1
  -2..  -1  ############### 15
  -1..   0  ############ 12
   0..   1  ############################################################ 68
   1..   2  ########### 11
   2..   3  ## 2
                                    <-- nothing between 3 and 5
   5..   6  ############ 12
   6..   7  ## 2
   7..   8  ###################### 22
   8..   9  ######################################################### 57
   9..  10  #################### 20
  10..  11  ########## 10
  11..  12  ### 3
  12..  13  ########## 10
```

Two clusters with two metres of empty space between them. The dominant offset
vector is `(8.747, 0, 0)` on 154 pairs, and `(8.747, 0, -4.0)` on another 63.
This is exactly what Sleven described — *"like two ships on top of and inside
each other facing different ways"* — except they are beside each other, not
inside.

**HERE IS THE TRAP.** The two clusters do not correspond to the two name
groups. The nodes WITHOUT `.001` already span X `-3.22 .. 12.08` — the full
width of both ships. So:

> **Deleting every `<name>.001` node on the 85X would take pieces out of BOTH
> ships and leave two broken ones.** That is what section 3a's phrasing invited
> and it is wrong.

The split that means something is **spatial**, not nominal: keep the cluster
centred near X = 0, drop the cluster centred near X = 8.75.

**Even that is not proven and I am not authorising it.** The clusters hold 110
and 136 mesh nodes. They are not the same size, so neither is a clean copy of
the other, and I cannot tell from coordinates which one is the real 85X or
whether one of them is a hangar prop, a landing pad, or a second livery. There
are also 56 distinct offset vectors, not one — so it is not a single rigid copy.

**A picture decides this, not more arithmetic.**

## The Fury is the opposite case and its obvious fix is the correct one

Single cluster on every axis — no spatial split, no second ship. But **301 pairs
sit at exactly zero offset**: the same mesh drawn twice in the same place. That
is z-fighting, it is why the surface looks wrong, and removing one of each pair
is safe and lossless.

The other 293 pairs are displaced by up to 3.33 m. Those are real, separate
parts that Blender happened to name with a `.001` suffix. **Do not touch them.**

---

## TASKS

**1. Fury — the only change authorised here.**
Remove one node of each `<name>` / `<name>.001` pair whose accumulated world
translations are identical to within 1e-6. **Exactly 301 pairs qualify; if your
count is not 301, stop and report the difference instead of proceeding.**
Leave every displaced pair alone. Write the previous file to `_to_delete/`.
Report the new mesh and node counts.

**2. 85X — render, do not edit.**
Three images of the current file, same camera: the whole thing, then only the
nodes with world X < 4, then only the nodes with world X >= 4. That tells
Sleven and me which cluster is the ship. **Change nothing until he has looked.**

**3. Nothing else in this addendum.** Section 3b (the see-through open-edge
distribution) and 3c (Centurion, Constellations, Freelancers) of the original
order stand unchanged and are still report-only.

## Standing constraints

- Report first, change nothing beyond task 1.
- Do not deploy the live site. Do not `git add -A`. Nothing commits or pushes
  without Sleven's explicit go-ahead.
- Never delete — `mv` to `_to_delete/`.
