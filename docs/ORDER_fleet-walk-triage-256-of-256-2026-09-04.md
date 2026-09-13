# ORDER — the whole fleet is walked. 256 of 256. Here is the triage.

From: C1 (Cowork), 2026-09-04
For: Code

Sleven finished the inspector walk. **256 of 256 ships opened and looked at, 34
marked.** That is the first time in this project's life that a human being has
laid eyes on every model we ship.

I triaged all 34 against what is actually on disk and what has already deployed.
They split three ways: **20 already fixed, 3 framing re-checks, 11 real.**

---

## 1. Twenty marks are stale — already fixed by deploys that landed mid-walk

He was marking while we were deploying, so he marked things that were already
repaired by the time he finished. **Do not act on these. They need clearing from
the mark list, nothing else.**

- **600i Executive Edition** — vertex colours. Fixed in the colour-fix deploy.
- **Carrack w C8X**, **Carrack Expedition w C8X** — removed from the list entirely.
- **Seventeen "facing away / needs to be turned around" marks** — fixed by the
  orbit change (`Math.PI + 0.9`). All seventeen predate that deploy.

**Task:** clear those 20 marks from the stored mark set, leaving his note text
intact in the archive. Do not silently drop the notes — move them to a
`resolved` state so the count reads honestly.

---

## 2. Three framing re-checks — cheap, do these first

Fit radius went `1.2 -> 1.45` in the same deploy. These three were marked
"zoomed in too close" **before** that change and have not been re-rendered since:

- ATLS
- ATLS GEO
- Reliant Kore

**Task:** render these three at the current fit radius, confirm the whole hull is
inside the frame with margin, report. If any is still cropped, say so — do not
tune the radius on your own; a global radius change affects all 256 and that is
my call, not a per-ship fix.

---

## 3. Eleven real defects — measured, with numbers

### 3a. Duplicated geometry — two ships in one file

Measured directly from the GLB node graphs:

```
85X    112 meshes    939 nodes    134 duplicate mesh references
Fury   406 meshes   1518 nodes    197 duplicate references
```

Every duplicate is the pair `<name>` and `<name>.001`. Whoever prepared these
files duplicated the entire ship in Blender and saved both copies. Sleven's
words for the 85X — *"like two ships on top of and inside each other facing
different ways"* — are literally accurate.

**Task:** report only. For each of the two, list the duplicate pairs and state
whether the `.001` copy is (a) an exact transform match, (b) offset, or (c)
rotated. **Do not delete anything.** If they are exact matches this is a safe
de-dup; if they are offset or rotated, the file may be encoding something and
removing half of it is destructive. I decide after your report.

### 3b. Still see-through after the solid-hull fix — PARTIAL, not solved

Open-edge measurement across the flagged ships and two controls:

```
X1                        644,367 tris   120,483 open edges   6.23%
X1 Force                  644,367 tris   120,485 open edges   6.23%
Cyclone TR                469,797 tris    47,179 open edges    3.35%
Vulture         (control) 993,057 tris    28,461 open edges    0.96%
Cutlass Black   (control) 264,931 tris    32,433 open edges    4.08%
Constellation Andromeda   940,077 tris   133,105 open edges    4.72%
```

**Read this honestly: the correlation is not clean.** The Cutlass Black at 4.08%
and the Constellation at 4.72% sit inside the flagged band and were **not**
flagged by Sleven. So open-edge percentage alone does not predict what the eye
sees. This is a partial finding and I am recording it as one.

X1 and X1 Force are near-identical files (two edges apart) — same source mesh,
so whatever is wrong is wrong once, not twice.

**Task:** report only. For X1, X1 Force, X1 Velocity and Cyclone TR, tell me
whether the open edges are concentrated in a few large shells or scattered
across the whole hull. That distinction decides whether this is a hole-filling
problem or a winding problem, and I do not want to guess between them.

### 3c. Not yet investigated — three items

- **Centurion** — *"not the right ship"*. Nobody has checked which hull the file
  actually contains. **Task:** identify it — node names, material names, tri
  count against neighbours — and report what ship it looks like.
- **The five Constellations** — landing gear deployed in the model while other
  ships sit clean. **Task:** confirm whether the gear is a separate node that
  could be hidden, or baked into the hull mesh. Report, do not change.
- **The four Freelancers** — Sleven's read is that the airframe is an outdated
  version. **This is the only one of the eleven that would also be wrong on the
  live site**, not just in the inspector. **Task:** report the source and
  `last_verified_patch` of all four Freelancer models so we can see how old they
  actually are.

---

## Standing constraints on this order

- **Report first, change nothing** on section 3. Rule 5 applies: this touches
  more than ten files.
- Do not deploy the live site. Do not `git add -A`. Nothing commits without
  Sleven's explicit go-ahead.
- Section 1 (clearing stale marks) and section 2 (three renders) you may do now.

## RUN — sections 1 and 2 only

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```
