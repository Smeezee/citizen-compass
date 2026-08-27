# ERRATA — G1's constants only work in cyan. I judged them in one colour and wrote them as if colour did not exist.

**C1, 2026-08-24.** Ran the fleet pixel measurement that
`ORDER_the-hull-reads-solid-2026-08-23.md` calls for and that Code correctly
declared his machine could not perform — no browser, no GPU, and he did not
install one or swap in a lookalike check.

**Code's implementation is faithful.** The shader constants in
`testing/_src/cc_viewer.js` are the order's, verbatim. `CC_HOLO_FRAG_HULL` is
untouched, so the negative control holds. `_setClip` derives near/far from the
camera with the clamp. Default style is `solid`. **The defect below is in the
order, not in the work.**

---

## The measurement, 234 hulls, three angles each, Code's shipped shader

    clipping (>90% luminance), fleet maximum   12.042%
    hulls over 1% clipped                          72
    near:far ratio, median                       12.9   (was 30,000)
    hulls under 5,000 rendered pixels                0
    silhouette gap, median                      0.035%

**The order predicted zero clipping. Seventy-two hulls clip.**

## The cause is the colour, and it is arithmetic

Same shader, same hulls, same camera. Only `uColor` changes:

| hull | amber (shipped default) | cyan | ice | mint |
|---|---|---|---|---|
| Retaliator | 12.04% | 0.00% | **75.19%** | 25.52% |
| Sabre | 10.05% | 0.00% | **75.87%** | 29.76% |
| Vanguard Warden | 8.88% | 0.00% | **65.64%** | 18.55% |
| Mercury Star Runner | 2.48% | 0.00% | **81.84%** | 40.78% |

`lit` peaks at `0.165+0.870+0.155+0.235+0.070 = 1.495`, and the shader then adds
`spec*0.42` and `fres*0.17*uGlow`. **Peak multiplier is about 2.085.** Any
colour channel above roughly `122/255` saturates.

    Ice   0xe8f4ff = (232,244,255)  every channel already near full -> white blob
    Mint  0x7dffb4 = (125,255,180)  green already full
    Amber 0xffb545 = (255,181,69)   red already full
    Cyan  0x35c8e8 = ( 53,200,232)  red is LOW, and that is the only reason

**These are five shipped user controls, not hypotheticals.** A visitor who picks
Ice today gets a white silhouette on every ship in the library.

## AND CYAN IS NOT SAFE EITHER - IT IS UNDER THE BAR BY TWO POINTS

At peak, cyan lands at roughly `0.2126*110 + 0.7152*255 + 0.0722*255 = 224`
against a 229.5 threshold. **Its green and blue channels are already clipped;
only the low red channel keeps the weighted luminance under the line.**

**So my earlier "0.00% on all 234" was partly where I set the bar**, not proof
of headroom. Reporting that rather than letting the clean number stand.

## What has to change, and it is G1's, not Code's

**The brightness has to be normalised against the chosen colour** so the peak
product lands inside 1.0 whatever the user picks — scale `lit` by the colour's
own headroom, or clamp the total. **Do not fix this by pinning the palette to
cyan.** Sleven overturned a constraint of mine already to keep those controls:
*"on this page the tuning IS the enjoyment."*

    CONTROL, load-bearing: report clipped-pixel fraction for ALL FIVE colours
    on the four hulls above. Every colour must land near zero. A fix verified
    in one colour is the exact mistake this errata exists to correct.
    CONTROL: report peak `lit` and the resulting per-channel product for each
    of the five colours, computed not eyeballed.
    NEGATIVE CONTROL: mean luminance must not collapse. The hull was at 9%
    before G1 and the point was to raise it - a fix that removes clipping by
    dimming everything back down has undone the order.

## The rule this cost

**I tuned in cyan, judged in cyan, and wrote the constants down as if they were
absolute.** They are a product with `uColor`, and a product is not a constant.
Code implemented exactly what I specified, on a machine that could not have
caught it, and said so plainly instead of guessing.

**State the conditions a measured value was measured under, or it is not a
measurement.**

---

# ADDENDUM, same day — the knee works, and MY METRIC WAS WRONG TWICE OVER

**C1, after running the pixel control on Code's committed fix (`9cd9a2a`).**

## The metric I specified could not tell blown-out from pale

The errata's control said "clipped fraction". I measured **fraction of hull
pixels over 90% luminance**. For a colour that is already nearly white — Ice is
`(232,244,255)` — a correctly lit, entirely unclipped pixel sails over that bar
just by being pale. **The number was measuring the colour, not the defect.**

The metric that measures actual lost detail is **all three channels at 254+**,
i.e. pure white. Measured both ways, before and after, four hulls, five colours:

| hull | colour | pure white BEFORE | pure white AFTER |
|---|---|---|---|
| Retaliator | **ice** | **54.52%** | 0.107% |
| Sabre | **ice** | **64.82%** | 0.391% |
| Vanguard Warden | **ice** | **43.87%** | 2.391% |
| Mercury Star Runner | **ice** | **71.23%** | 0.032% |
| all four | amber | 0.000% | 0.000% |
| all four | mint | 0.000% | 0.000% |
| all four | cyan | 0.000% | 0.000% |
| all four | rose | 0.000% | 0.000% |

## So the original errata was wrong about which colours were broken

**I reported amber clipping 12% and mint 30-40%. Neither ever blew out at all** —
0.000% before and after. They were bright, not clipped.

**Ice was the whole defect, and it was far worse than I said**: up to **71% of
the hull rendered as flat white**, not the 82% "over 90% luminance" I quoted,
which conflated two different things.

**The direction of the fix was right and the diagnosis of the mechanism was
right.** The ranking of severity across colours was not.

## The negative control passes

Mean luminance cost of the knee, measured:

    ice    -3.4% to -3.9%
    mint   -2.3% to -2.4%
    cyan   -1.7% to -2.5%
    amber  -1.5% to -1.6%
    rose   -1.0%

Code predicted 0.7-2.0%; the true range is **1.0-3.9%**, slightly wider than his
estimate and nowhere near a collapse. His own measured alternatives were 22-29%
for a flat scale and 13-17% for extended Reinhard. **The knee costs a twentieth
of what the obvious fix would have.**

## Verdict

**G1's colour errata is closed.** The knee removes the real defect on the only
colour that had one, leaves the other four numerically untouched, and costs a
few percent of brightness.

## The rule this cost, again

Three times this session a control of mine has carried a wrong definition: a
see-through check that returned 0% on a visibly broken render, a byte-identity
rule that would have called exporter re-welding a fleet regression, and now a
brightness threshold that cannot distinguish a blown highlight from a pale
colour.

**Every one was a proxy standing in for the thing that mattered. Measure the
property under discussion, not the one that is easy to compute.**
