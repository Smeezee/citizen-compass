# Update - C1's three pinned checks: two re-pinned and proven, one is telling us something real. Not deploying.

Answering `ORDER_the-box-is-fixed-190-ships-three-pinned-checks-need-your-numbers-2026-09-06.md`.

## FIRST, A CORRECTION TO THE ORDER'S OWN FIGURES

The order says G3 now gains **5** ships: `85X, Ares_Inferno, Ares_Ion,
Aurora_SE, Starlite`. **On disk it gains 3:** `Ares_Inferno, Ares_Ion,
Aurora_SE`. No 85X, no Starlite. Measured twice, before and after my change.
Flagging it because you asked me to refuse bad data rather than fit to it - one
of us is reading a different tree and it is worth knowing which.

## 1. `_verify_g3_matcher_delta.py` - RE-PINNED, and to names rather than a count

Was: `placed` delta == 2, and `gained == ["Ares_Inferno","Ares_Ion"]`.
Now: a named set of three, and **every gained ship faces the shape check**, not
just the two Ares the file was written for.

**A count was the wrong pin and always was.** It moves whenever a hull is
decoded, which is routine, so it goes red for something that is not a defect -
and the fix each time is to type a bigger number, which is the habit that file
exists to refuse. What the count stood in for is "the loosening caught only what
it was for", so that is what is pinned now. A fourth name still turns it red.

**Aurora_SE was checked before being pinned in**, not assumed: it is placed with
a real mount count and a measured shape error, same as the two Ares. If it had
been waved through I would have stopped here instead.

Its failure path is already proven - the pre-edit run went red on exactly this
assertion, with exactly this data.

    VERIFY PASSED - the second pass moves exactly the 3 pinned ships, by name,
    and each one faced the shape check.

## 2. `_verify_stage_floor.mjs` - RE-PINNED to 10, and to names

The file's own comment says a new hull landing in a tail "still goes red, which
is precisely when somebody should look." Looked:

**Nothing moved. ZERO hulls crossed a tail boundary.** Of the 31 hulls your
`hull_box()` fix regenerated, the only one whose fraction changed at all is the
Fury, 48.5% -> 49.4%, middle to middle. The seven high hulls of the errata are
**exactly the seven you did not regenerate**, unchanged. The three additions -
600i Executive Edition, Arrastra, Merchantman - had no decoded geometry until
tonight. **Three arrived; none moved.** Your fix moved no hull's resting class.

Both tails are now pinned BY NAME, bottom as well as high. Ten names can tell
the difference between the right ten hulls and one silently swapping with
another; a count of 10 cannot. All 23 assertions pass, 258 hulls.

## 3. `_verify_holo_render.mjs` - one half fixed, ONE HALF IS TELLING US SOMETHING REAL

### The `detail` failure was the check's fault, and it is fixed properly

`detail` is the EdgesGeometry threshold - it changes the EDGE COUNT. The render
signature carries the line material's opacity, **not the edge count**, so it
only ever saw `detail` second-hand through `ccEdgeOpacity()`. On a hull dense
enough, that opacity is pinned to the floor **your own E7b comment at
cc_viewer.js:447 puts there on purpose** - so the signature reads identical from
detail 8 to 80 while the geometry underneath changes by a factor of three.

Measured: 0.0396 at every value of detail, which is the 0.040 your comment
predicts for the densest hull. **The viewer is not broken. The check was
watching the one quantity that cannot see the thing it was asserting about.**

The fingerprint now carries the edge count too - hull-independent and stronger
than what it replaces. **Proven by mutation:** with `setSlider('detail')` made
not to rebuild, in a scratch copy of `cc_viewer.js`, the assertion goes red.
Your file was not touched.

### The pre-pass negative control - STOPPING HERE, this one is yours

    panel with NO pre-pass, DoubleSide -> 1.22% pure white
    FAIL: and with the pre-pass removed the same hull blows past the threshold

That assertion exists to prove the 5% threshold is not vacuous. **On the Tyilui
it is simply false**, and for the same reason as above: what keeps this hull
under 5% is the floored line opacity, not the pre-pass. So the <=5% pass in
section 5 **is not evidence about the pre-pass on this hull at all** - the
control has quietly stopped demonstrating the thing it was written to
demonstrate. That is a rule 12 loss of meaning, not a number that drifted.

**I am not re-pinning this one.** The obvious repair - assert that removing the
pre-pass raises saturation measurably (0.24% -> 1.22%, about 5x) instead of that
it crosses 5% - changes what the control MEANS, and it rests on the floor/
intensity reasoning in your E7b comment, which is yours. Widening 5% until 1.22%
fits is exactly what your order said not to do, and I am not doing that either.

**Tell me which and I will make it, or make it yourself.**

## Not deployed

The sweep cannot be green while that one is red, so per your order and rule 25
there is no TESTING deploy. Nothing was uploaded. The full sweep is running now
to confirm nothing else moved - in particular that the 19 exit-code changes I
made earlier did not break any control's pass path. I will file the result.

## Also on disk since your order

12 control files now exit 2 (NOT RUN) instead of 1 where they print NOT
PERFORMED - 19 sites, 18 proven by making each one fire. See
`2026-09-06_update_exit-2-done-18-of-19-proven.md`. None of them is yours.
