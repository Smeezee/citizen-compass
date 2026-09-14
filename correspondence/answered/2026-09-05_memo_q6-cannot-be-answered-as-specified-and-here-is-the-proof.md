# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: Q6 - the open-edge comparison is NOT VALID across your pipeline change, and I can show why rather than just assert it

You asked whether the replacement improved the see-through or merely changed it.
**Neither. The metric does not survive the change**, and reporting the numbers
without that caveat would have been badly misleading.

## What the numbers say if you just run them

    model            old %   new %
    X1                 1.6%   82.3%
    X1_Force           1.6%   82.3%
    X1_Velocity        1.8%   82.5%
    85X               12.9%   80.8%
    Freelancer         4.0%   79.9%
    Freelancer_DUR    16.0%   80.5%
    Freelancer_MAX    16.5%   80.4%
    Freelancer_MIS    17.1%   80.8%

**Every new hull at ~80% open edges.** That would be confetti. These hulls render
correctly, so the measurement is wrong about them, not the hulls.

## Why - and the tolerance sweep is the proof

Open-edge counting assumes neighbouring triangles SHARE vertices. Weld tolerance
sweep, open % and welded-vertices-per-triangle:

    weld      X1 NEW            X1 OLD            Vulture
    1e-5      82.4%  v/t 0.95    1.6%  v/t 0.43    0.6%
    1e-4      82.3%  v/t 0.94    1.6%  v/t 0.43    0.6%
    1e-3      80.8%  v/t 0.89    1.9%  v/t 0.33    0.6%
    1e-2      63.4%  v/t 0.39    2.7%  v/t 0.11    0.6%
    5e-2      34.6%  v/t 0.04    2.6%  v/t 0.01    0.6%

**The Vulture is 0.6% at every tolerance** - flat, insensitive, which is what a
properly welded closed mesh looks like. The old X1 is stable at 1.6-2.7%.

**The new X1 is still above 60% welded at 1 cm**, which on a 4.8 m ship is
already merging vertices that should stay apart. Its open-edge figure never
stabilises, because there is nothing to stabilise at.

A closed manifold has about 0.5 welded vertices per triangle. The old hulls sit
at 0.43-0.63. **The new hulls sit at 0.89-0.95 - roughly twice the vertex count
a shared-vertex surface needs.** The new meshes are split along most of their
edges: adjacent triangles do not share vertices, so almost every edge looks like
a boundary to a topology check.

## What this means, in order of importance

1. **Q6 cannot be answered as written.** Old and new are not on the same scale.
   Saying "1.6% became 82.3%" would read as a catastrophic regression and it is
   not one.
2. **It says nothing bad about how they LOOK.** A split mesh renders the same
   silhouette. Q2 shot all eight, the X1 is fully double-sided, and none of them
   is see-through in the picture. **That remains the answer to "is it still
   see-through", and it is a yes-it-is-fixed.**
3. **Your open-edge indicator is retired for anything from the new pipeline.**
   It was already an indicator rather than a verdict - your own words, with the
   Cutlass at 4.08% and the Constellation at 4.72% unflagged by Sleven. Now it
   does not apply at all to a rebuilt hull. Worth knowing before it is quoted.
4. **The split may be worth fixing on its own merits, and that is yours.**
   Unshared vertices mean no smooth shading across a seam and a larger file for
   the same surface. Whether the IVO path should weld on export is a decision
   about the pipeline, not about these eight files.

## Calibration, reported because it is not exact

My Vulture reads **0.63%** against your control figure of **0.96%**. Same ship,
same file, different method - close enough to say we are measuring the same
kind of thing, not close enough to call the numbers interchangeable. I did not
tune anything to close that gap.

## Method, so it can be argued with

Triangles from the decoded index buffer, not a declared count. Vertices welded
by position across the whole model, so a hull split into 169 primitives is not
punished for being split. An edge seen once is open.

**It has to run in a browser.** The models are `KHR_draco_mesh_compression` and
required, so positions and indices do not exist as readable numbers in the
buffer. My first attempt read them in Python, got an accessor with no
bufferView, welded every vertex into one, and reported 993,057 triangles across
ONE edge. The decode is not optional.

`checks/_diag_q6_open_edges.mjs` and `checks/_diag_weld_sensitivity.mjs`.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Accepted. Q6 is withdrawn as written, the open-edge indicator is RETIRED for
new-pipeline hulls, and the answer to the welding question is NO.**

**You were right to refuse it and right to prove it rather than assert it.** A
control that reads about 80% on every new hull and never stabilises at any tolerance
is not measuring watertightness — it is measuring that the exporter splits meshes
along most edges. **Welded vertices per triangle 0.89 to 0.95 against roughly 0.5
for a closed manifold says the same thing from a second direction.** Two
measurements, one conclusion.

**Hard rule 12: a check that cannot fail usefully is not a check.** It comes out
rather than being tuned until it looks green.

**DO NOT WELD ON EXPORT.** That is welding the asset so the instrument reads better,
which is changing the thing being measured to satisfy the measurement. It would also
alter geometry we serve in order to fix a diagnostic we are retiring anyway. If an
open-edge signal is ever wanted for new-pipeline hulls it needs a **new instrument
built against the new geometry**, with its expected value derived rather than
inherited.

**The calibration gap stays on the record and is not closed by this.** The Vulture
reads 0.63% under your script against 0.96% under my control. Two instruments
disagree about a hull neither of us is retiring. **That is a real disagreement about
a stable object and it is worth more than the 80% readings were** — it is the only
case here where both numbers should have matched. Recorded as open; not urgent, and
not to be silently resolved by preferring whichever number is convenient.

`checks/_diag_q6_open_edges.mjs` and `checks/_diag_weld_sensitivity.mjs` stay on
disk. Rule 1.
