# Update — E5's control runs again. Sweep is 79 ok, 0 failed.

**Committing next. No deploy: this changes a control, not the page.**

## The decision you asked for

`_verify_stage_floor.mjs` had been red since G2 added `_fitProjected()`, which
calls `camera.updateMatrixWorld()`. The stub camera had no such method, so the
control died with a TypeError. **E5's guarantee - the hull stands on the disc,
and the disc fits the hull - has not been verified on any run since.** It is
verified again now, on all 239 hulls.

## Why the cheap fix would have been worse than the crash

The stub's `project()` was `return this` - world coordinates, unchanged.
Adding an empty `updateMatrixWorld(){}` removes the TypeError and leaves
`project()` handing metres to code that expects normalised device coordinates
between -1 and 1. Every corner would read as a massive overshoot, the fit loop
would shove the camera away six times on every hull, and **the control would
report PASS on a framing nobody had checked, 239 times.** That is the rule 12
shape exactly, so the projection is the real one: a look-at basis from the
camera's position and the target it is aimed at, then the standard perspective
divide.

The stub camera now shares its `target` Vector3 with `controls.target`, which
is what makes `controls.target.set(...)` in `frame()` actually turn the camera,
the way `controls.update()` does on the page. Aspect is 960x540, the same stage
size the rest of the checks measure at.

## Section 0, and it earned its place on the first run

**Every assertion in the file depends on arithmetic written for this control
rather than on the page's own code.** So the projection is checked first,
against answers fixed by the definition of a perspective camera: at distance d
the visible half-height is d*tan(fov/2), the half-width is that times the
aspect, the near plane is z = -1 and the far plane is z = +1.

**It immediately caught a defect in my own projection.** `up` had a spurious
negation, so a point above the axis projected to y = **-1**. The Y axis was
upside down.

**And all fifteen fleet assertions PASSED with it upside down**, because a
symmetric fit does not care which way up it is wrong. Without section 0 this
would have shipped as a green control measuring a mirrored camera.

    ok  a point at the camera's target lands dead centre
    ok  one half-height above the axis lands on the top edge
    ok  one half-width to the side lands on the right edge - aspect applied
    ok  half that distance lands halfway - linear in the plane
    ok  a point on the near plane reads z = -1
    ok  a point on the far plane reads z = +1
    ok  a point BEHIND the camera reads z > 1, which _fitProjected keys on
    ok  the projection is NOT the identity

## Controls

**23 assertions, all passing, on all 239 hulls.** Every existing mutation still
fires, and one was added:

    --mutate-centred      1   the hull is re-centred instead of floored
    --mutate-fixedring    1   the disc goes back to a fixed 1.50 radius
    --mutate-noclamp      1   a zero-footprint hull draws an invisible ring
    --mutate-flatproject  1   NEW - project() returns world coordinates again

**The new mutation exposed a real gap in the mutation harness.** I first added
it to the `MUTATIONS` table, which rewrites `cc_viewer.js` before loading it.
`project()` is not in `cc_viewer.js` - it is this control's own stub - so the
patch matched nothing and the run reported **"MUTATION DID NOT APPLY"** and
exited 1. It exited 1 for the wrong reason, and only the existing guard made
that visible instead of it reading as a catch. Wired to the stub directly
instead; it now fails five of section 0's eight assertions with the exact
numbers the no-op produces (9.0 for the near plane, -91.0 for the far).

**That is twice in two days a mutation has failed for the wrong reason** - the
same thing happened with `--mutate-reseed` in the P1 control, where a temp copy
could not find its inputs. Both were caught by reading the output rather than
the exit code. Worth naming as a pattern: **a mutation that exits non-zero has
not necessarily fired.**

## Sweep

    79 ok, 0 failed, 3 skipped, 0 NOT RUN

The three skips are the deliberate opt-in network controls -
`_verify_deployed_links.mjs`, `_verify_find_deployed.mjs` and
`_verify_picker_deployed.mjs`. **All three were run by hand after today's
deploy and all three are green**, including B8's acceptance on the served
bytes: Origin 400i, 52 markers, 44 picker, 8 fixed, 0 silent.

**This is the first fully green sweep of the run.** It was 72 ok / 4 failed
when the walkthrough order started.

## Queued, not started

`claude/FINDING_the-dimension-table-has-collisions-2026-08-26.md` - an auditor
deciding each collision by MEASURED extents, flags only, no auto-fix, no
hand-corrections, and the proportion guard untouched.
