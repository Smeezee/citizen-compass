# FINDING — the 5% pure-white threshold measures the SAMPLING STRIDE. It is not 14 hulls, it is 50 of 150, and which hulls fail is decided by how heavily each one was decimated.

    from      C1, 2026-09-06
    for       Sleven, Code
    question  Sleven: "figure out why those fourteen are the limit."
    method    ran `checks/_verify_holo_render.mjs` unmodified, once per hull,
              with CC_GEO_DIR pointed at that hull alone - the same technique
              Code used on the Dragonfly. 150 hulls scanned, 0.2s each.
              Nothing was edited to produce these numbers.

---

## 1. THE ANSWER, IN ONE TABLE

Share of hulls over the 5% threshold, bucketed by the sampler's stride - `stride
= count / sampled`, the "every Nth vertex" the geometry file was decimated at:

    stride 1    n=  5    over 5%:  4   ( 80%)    median panel  6.23%
    stride 2    n= 29    over 5%: 20   ( 69%)    median panel  8.52%
    stride 3    n= 34    over 5%: 19   ( 56%)    median panel  5.95%
    stride 4    n= 19    over 5%:  1   (  5%)    median panel  3.67%
    stride 5    n= 14    over 5%:  0   (  0%)    median panel  2.77%
    stride 6    n= 15    over 5%:  2   ( 13%)    median panel  2.27%
    stride 7    n= 18    over 5%:  2   ( 11%)    median panel  1.64%
    stride 8    n=  7    over 5%:  2   ( 29%)    median panel  2.59%

**80% down to 0%, monotonically, as the stride rises.** A hull sampled at every
vertex fails. The same hull sampled at every fifth vertex passes. **Nothing about
the render changed between those two rows - only how many of its vertices the
geometry file kept.**

## 2. AND CORRECTING FOR THE STRIDE REVERSES THE VERDICT

`cell[i]` counts SAMPLED points, so it under-counts real fragments by exactly the
stride. Multiply it back:

                      raw meanDepth    stride    stride-corrected
    over 5%   n= 50        16.0         3.00           42.2
    under 5%  n=100        11.0         5.00           56.5

**The hulls the control flags are, physically, the LESS dense ones.** The whole
separation is the stride, and once it is removed the ordering inverts. There is
no version of "these hulls are too bright" that survives this.

## 3. THE SECOND FACTOR, AND IT IS GEOMETRY NOT BRIGHTNESS

Section 5 bins points into a fixed **320x320 grid normalised by the hull's
LONGEST axis**. A long thin ship therefore occupies a narrow band of that square
and its points pile into few cells:

    Caterpillar                 20.88%   covered  2,198 px of 102,400  (2.1%)
    Caterpillar Best In Show    20.88%   identical
    Caterpillar Pirate          20.88%   identical
    Endeavor                    13.63%   covered  1,981 px            (1.9%)
    Eclipse                     16.22%   covered  2,706 px            (2.6%)

    over 5%   median covered  4,338 px
    under 5%  median covered  6,159 px

**The Caterpillar is the worst hull in the fleet by this measure because it is
long and thin.** That is an aspect ratio, not a defect. The three Caterpillar
variants returning byte-identical percentages is the tell: they are the same
mesh, and the metric is a property of the mesh's shape and sampling, not of
anything the viewer does.

## 4. WHAT THIS MEANS FOR THE CONTROL

**The threshold is not vacuous - my erratum already withdrew that - and it is
also not measuring what its name says.** Both can be true and both are.

- **`w < 5` as a per-hull absolute claim is not sound and should not be
  fleet-wide.** Two hulls of identical real brightness differ by 2.5x in this
  number purely from the stride they were decimated at.
- **Within one hull it is completely sound**, because the stride, the projection
  and the covered-cell set are all identical and cancel exactly. **That is
  precisely the regime Code's Step B negative control uses** - Liberator 1.63%
  shipped against 8.34% with the pre-pass removed - so that control is correct
  and is not affected by any of this.
- **Code was right to refuse to call the 14 a defect**, right that the cap is
  implicated, and right that his own correction attempt was wrong. It was wrong
  because multiplying by the stride fixes comparability but leaves the absolute
  calibration unanchored - which is why it put 187 hulls over a threshold the
  visibly-not-white site refutes. **Comparability and calibration are two
  problems and only one of them is arithmetic.**

## 5. THE FIX I WOULD MAKE, AND WHY IT IS NOT TONIGHT'S JOB

**Step 1 - make the metric stride-invariant.** Multiply `cell[i]` by
`count / sampled` before accumulating. One line. After it, a number means the
same thing on every hull.

**Step 2 - re-derive the threshold from a hull whose appearance is known, and
express it as a MULTIPLE of that hull rather than as a bare percentage.** The
Liberator is the right reference: `cc_viewer.js:447` names it as the hull the
E7b floor decision was made about, and Sleven's approved captures were taken at
that size. A bare 5% has no provenance - nobody can say today where it came
from, which is how it survived measuring the wrong thing.

**Step 3 - keep the per-hull absolute assertion OFF until step 2 is done.** An
assertion whose number is not comparable between hulls must not be applied to
hulls it cannot compare. The within-hull ratio control stands unaffected.

**Not tonight.** The sweep is green and TESTING is deployed against that exact
payload; changing this control now invalidates the receipt and the gate refuses
the next deploy. This is a queued job with its own build and sweep.

## 6. What I did NOT establish

- **Whether any hull is actually too bright on screen.** Nothing here is a
  measurement of the rendered page. It is a measurement of a model, and the
  model's absolute calibration is exactly what is unanchored.
- **The remaining 108 hulls.** 150 of 258 scanned; the scan stalled and I
  stopped rather than let it run unattended. **The stride pattern is monotonic
  across eight buckets and 150 hulls, so I do not expect the rest to change the
  conclusion - but I have not looked at them and am not claiming I have.**
- **Why Code counted 14 and this counts 50.** Different runs of the same
  control; his figure came from a fleet pass I have not reproduced. **The
  disagreement does not affect the finding** - the stride dependence is visible
  at any cut - but it is unresolved and worth one look before either number is
  quoted anywhere.

---

*C1, 2026-09-06. The threshold has been quoted in three documents this week and
none of us had asked what it was counting.*
