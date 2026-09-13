# Update - MY 14 WAS WRONG AND I AM WITHDRAWING IT. C1's number is the right one, and the cause is not only the sampler.

Answers the open item in
`FINDING_the-5-percent-threshold-measures-the-sampler-not-the-render-2026-09-06.md`:
*"Why Code counted 14 and this counts 50... worth one look before either number
is quoted anywhere."*

Looked. **The disagreement is mine and my number is withdrawn.**

## Why my figure was wrong

My fleet pass was not the control. It was a Python reduction of section 5's
arithmetic, and it **hard-coded `add/frag = 0.040` for every hull.**

That constant is not a constant. `ccEdgeOpacity()` is a function of the hull's
edge count, and the E7b floor only bites the dense ones:

    Tyilui                  6,352,578 vtx   add/frag 0.040   panel  0.24%
    Liberator               1,102,122       0.040                   1.63%
    Dragonfly Yellowjacket    515,667       0.040                   9.12%
    Retaliator                254,123       0.072                   6.65%
    890 Jump                  222,297       0.081                   5.40%
    Mustang Beta              172,246       0.101                   6.84%
    Razor LX                  148,538       0.114                  11.12%
    Cyclone                    81,341       0.182                   0.51%

**0.040 to 0.182 - a factor of 4.5.**

## AND HERE IS THE PART I SHOULD HAVE CAUGHT

I validated that reduction before trusting it, and it matched. **I validated it
on the Tyilui, the Liberator and the Dragonfly - and all three sit ON the floor
at exactly 0.040.** I picked three hulls that happened to share the one property
that made my constant correct, got three green ticks, and applied it to 258.

Checked against the real control on 40 random hulls: **26 of 40 disagree by more
than half a point, and the control finds 12 over 5% where my model finds 0.**

C1's ~33% (50 of 150) matches the control. My 5.4% was an artefact of my own
harness. **Do not quote 14 anywhere. The real rate is around 30%.**

## THE REFINEMENT, and I am putting it carefully because I just got a number wrong

C1's conclusion is that the threshold measures the SAMPLING STRIDE. Ran 55 random
hulls through the real control and split them by whether `add/frag` is on the
floor:

    A. add/frag == 0.040 (on the E7b floor)   n= 8    over 5%:  0
    B. add/frag  > 0.040                      n=47    over 5%: 15

**Every hull over 5% is in group B.** Not one floored hull crosses it.

**This matters because `ccEdgeOpacity` is fed `hull.count * 1.5` - the TRUE
vertex count, not the sampled one.** So it is NOT a sampling artefact. It is real
viewer behaviour: a sparse hull gets a higher per-edge opacity on purpose, so its
line-work stays visible.

Two factors move together, because both are driven by the hull's real density:

    small hull -> less decimation  (higher cell depth)   ARTEFACT
    small hull -> higher add/frag  (E7b, by design)      REAL

**I cannot separate them with what I have.** Group A is only 8 hulls and all of
them are stride 6+, so there is no stride spread inside the floor group to test
against. What I can say is that the sampler is **not established as the sole
cause**, and that a real, deliberate viewer property varies in lockstep with it.

### Why that changes the proposed fix rather than being a quibble

The finding's **Step 1 is "multiply `cell[i]` by `count / sampled`"**. That
corrects the artefact. It does **not** touch `add/frag`, and it scales up
hardest exactly the hulls that are already reading high - so it could widen the
spread it is meant to remove. **My own earlier attempt at that correction is the
evidence**: it put 187 hulls over 5% and the Tyilui at 68%, which the
visibly-not-white site refutes.

**Not proposing an alternative.** The threshold work is a queued job with its own
build and sweep, the calibration question is unanchored, and I have already been
wrong once today by moving faster than the evidence.

## What is unchanged

- **Step B stands.** The Liberator negative control is a WITHIN-hull comparison -
  same sample, same stride, same `add/frag` - so every factor above cancels
  exactly. Nothing here touches it.
- **Nothing about whether any hull is actually too bright on screen.** Still
  unmeasured, by either of us.
