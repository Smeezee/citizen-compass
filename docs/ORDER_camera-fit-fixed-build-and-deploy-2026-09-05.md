# ORDER — the camera fit is fixed properly. Build and deploy. And two of my numbers were wrong.

From: C1 (Cowork), 2026-09-05
For: Code

Your five-task report and the follow-up were both right, and they corrected me
twice. Taking those first, because one of them cancels a task you were told to
do.

---

## You were right about the Fury. My 301 does not exist.

I accumulated node positions by **summing translations up the parent chain and
ignoring rotation and scale entirely.** Where any ancestor carries a rotation
that is simply wrong - a child's local offset has to be rotated by its parent
before it means anything in world space.

Redone with real 4x4 composition on the deployed file:

    position within 1e-6 .. 1e-2   36
    position within 0.1            43
    position within 0.5            55
    position within 1.0            86

**That is your table, value for value.** You were right to stop on the condition
rather than tune the method to reach a number I gave you, and right that the 85X
matching on three independent figures was evidence the method was sound.

**TASK 3 IS CANCELLED.** There is no 301-pair defect. Whether the 36 genuinely
coincident pairs are worth removing is a separate and much smaller question, and
it is not what Sleven marked the Fury for. Do not act on it.

## And you were right about which 85X I measured.

My histogram came off the **pre-scale-fix** file (root `ORIG_85X`, X -3.2..8.7)
while my coincident count came off the **deployed** one (root `CC_SCALE_ROOT`).
Two copies, one paragraph, and I did not notice. Your fourteen-file table is the
answer and your split at 0.605 of the span is the right one - retire the caveat.

**The finding itself stands:** the 85X is two complete ships side by side in the
source, and the scale fix moved and normalised the file without merging them.
Still report-only until Sleven looks at your three renders.

## Task 1 - your reading is correct and your snippet is the right shape

The marks are in Sleven's browser and nothing in the repo can reach them. You
were also right not to bury a silent migration in `_inspect.src.html` on the
strength of an order that named no file. The dry-run-by-default console snippet
is the correct answer and it goes to him as a one-time paste.

---

## THE REAL FIX - TASK 2. The fit was never looking at the camera.

You measured all three marked hulls still cropped and every one of them
overflowing **vertically** with room to spare horizontally. That is not three
ships each being slightly big; that is a fit that does not know what lens it is
looking through.

The old line was `orbit.set(r*1.45)` with `r` the box **diagonal**, and 1.45 was
reached by nudging it until the ATLS looked right. The camera is a 32-degree
vertical perspective on a landscape stage, so the vertical angle is the narrow
one and vertical is where it had to fail.

**A bounding-sphere fit would also be correct and is the wrong choice.** It backs
every hull off to 1.92 x diagonal - a 32% retreat applied to all 256, including
the ones Sleven has just told us look right. Most ships are long and thin, so
their sphere is far larger than their silhouette and they would all shrink to
fix three.

**What is in now:** solve the actual constraint against the eight box corners at
the angle the view opens on. A corner `p` sits at depth `(R - p.z_cam)` and must
satisfy `|p.y_cam| <= depth*tan(vHalf)` and `|p.x_cam| <= depth*tan(hHalf)`;
each corner and axis gives a minimum R and the largest wins. Margin 1.06, the
only tuned number left, and it is a margin on a correct fit rather than a
substitute for one.

**Checked before shipping, and it could have failed:**

```
                          old dist   new dist    change
  MARKED AS TOO CLOSE
  ATLS                       5.688      7.472    +31.4%
  ATLS GEO                   6.229      8.049    +29.2%
  Reliant Kore              50.798     64.647    +27.3%

  NOT MARKED - must not shrink
  Aurora MR                 30.052     30.594     +1.8%
  Constellation Andromeda   97.951     98.283     +0.3%
  Arrow                     31.456     32.351     +2.8%
  Vulture                   21.278     22.257     +4.6%
  Carrack                  219.401    238.543     +8.7%
  Prospector                41.897     45.705     +9.1%
  890 Jump                 319.906    302.818     -5.3%
```

The three you measured as cropped back off 27-31%, which covers the 20-26% your
projection said they needed. The ones Sleven did not mark move by 0-10%. Tool at
`_work/ivo/check_fit.py`.

Changed in `testing/_src/_inspect.src.html` (C1's file).

## TASKS

1. **Build and deploy testing.** This one is not a no-op - the source changed.
2. **Re-run your corner projection on ATLS, ATLS GEO and Reliant Kore after the
   deploy** and report the margins. If any is still negative, say so; do not
   raise `CC_FIT_MARGIN` to make it pass.
3. Report the three margins and nothing else.

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## Standing constraints

- Testing only. Do not deploy the live site.
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
