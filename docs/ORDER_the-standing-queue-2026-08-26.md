# ORDER — the standing queue. Work it end to end without stopping.

**2026-08-26 · C1 · for Code · supersedes the "stop and report" line in every
order filed today**

---

## Why this order exists

**Six orders today ended with "stop and report", and Code obeyed all six.**
Each stop cost between ten and fifty minutes of nothing happening, and every
restart needed Sleven to notice the silence and relay a message by hand. That
is roughly two hours of dead clock, and none of it was caused by the work.

**Those gates were right when a question was genuinely open. They are not right
now.** Everything below is already approved. Nothing in it needs Sleven's
permission to begin, and none of it should end in a pause waiting for one.

**Work the queue top to bottom. Do not stop between items.**

---

## The stop rule, and it is narrow

Stop mid-queue for exactly three things:

1. **A control goes red and the cause is a real defect you cannot resolve
   inside the item you are on.** A red control caused by the change itself is
   part of the work, not a stop - today's V2 pass fixed seven of them and kept
   going, which was correct.
2. **A decision that is genuinely Sleven's**: anything legal, Fan Kit or
   trademark (Rule 8), or a design choice about what the visitor sees that is
   not already settled in a filed order.
3. **Something in front of you contradicts a standing ruling.** Say so rather
   than picking a side.

**"I finished an item" is not a reason to stop.** File the update, take the
next one.

**"I finished the whole queue" IS a reason to stop.** Report and hold.

## Commit as you go, and do not push

Nothing has been committed since `e8f1dd8` this afternoon, and there are now
several days of work in the tree. **Commit each item as it completes**, with
the reasoning in the message as usual. **Do not push, do not deploy the live
site, do not cut a release** - standing rules, unchanged.

Deploy to **testing** after each item that changes what a visitor sees, so
Sleven can look at any point without waiting for the queue to drain.

---

## The queue

### 1. A1 and A2 — the fit loop stops depending on clip planes

`docs/RULING_the-asgard-is-in-centimetres-2026-08-26.md`.

`_fitProjected` sets its own generous near/far, derived from the box and the
target, before the passes, and restores them after. `_setClip` still owns every
rendered frame, so G2's depth ratio is untouched. A2 splits the `p.z > 1` guard
into "behind the camera" and "beyond the far plane", which call for opposite
responses; after A1 the second branch should be unreachable and a control
should assert that.

**The Asgard is black on the deployed site right now.** This is the item that
turns it on. Note it will then render ~100x oversized - that is A3, below, and
it is a separate defect.

### 2. Wire the model inheritance — 76 ships gain a model, no new assets

`data-layer/derived/model-inheritance/` is generated, gated by four assertions
and green. `build_model_inheritance.py` at the repo root regenerates it and is
re-runnable every patch.

76 editions map to the base hull whose model we already hold, joined on exact
ClassName suffix strip, no fuzzy matching. This is Sleven's 2026-08-14
shared-hull ruling finally wired up. `needs_human_review.json` holds the 37 that
are deliberately NOT auto-mapped - **do not map those**, several would be wrong.

### 3. A3 and A4 — the Asgard's units, and the auditor that would have caught it

Same ruling. Rescale the Asgard to metres in the model pipeline. Then the
auditor: for every hull, compare the model's bounding box against the ship
record's `dim` and report any that disagree beyond a stated factor. **It flags.
It never rescales.** The Asgard is alone in the band that crashed the camera;
there is no reason to believe it is alone in the band that merely lies.

### 4. F3 — the real-browser control

`docs/DECISION_the-checks-get-a-real-browser-2026-08-26.md` - approved by
Sleven, including installing Playwright and a headless Chromium under
`checks/`. Test-only; nothing reaches the site.

Load the built `testing/_deploy/loadout.html` over a local static server for a
sample of 8-12 hulls, read `camera.position.distanceTo(controls.target)` and
the hull's bounding radius, assert the ratio lands in **1.8 to 6.0**. Set the
band against what actually shipped - Code's own measured 2.0-2.5 across 238
hulls - **not against the table in the camera order, which was F1-only and
mislabelled.**

Mutations that must fail it: remove the `lookAt` line; restore the positive Z
in `frame()`; restore the pre-A1 clip dependency.

### 5. C6 — prove the diff tool on 4.9 before it meets 4.10

`docs/ORDER_catching-up-to-4-10-2026-08-26.md`, amendment at the end.

Acquire `4.9.0-LIVE.12344265` as a properly gated snapshot - all five gates,
git metadata captured before `.git` is stripped, no shortcuts because it is a
dry run. Build C5 and run it on that pair against our `12232306` baseline. Both
controls: the self-diff must come back empty, and the planted single-field
change must be reported exactly once, in the right file, on the right ID.

**Five weeks between two 4.9 builds should produce a small, boring diff.** If it
reports hundreds of changes or none at all, the tool is wrong and not the data.
Say which happened before drawing any conclusion.

**Do not promote the new snapshot.** The site keeps serving `20260801T204744Z`
and keeps saying 4.9.

### 6. C3 — the DataForge record walk

C3a is answered: `Game2.dcb` decompresses cleanly through the method this
project already owns, 331 MB, no dependency needed. The remaining work is
resolving `structDefinitions` and `propertyDefinitions` into a schema, then
walking `recordDefinitions` through the typed value arrays.

**This one is genuinely open-ended and it is last for that reason.** Two things
about how to run it:

- **The field names in the probe are UNVERIFIED.** They follow documented field
  order; nobody has walked a table to confirm a count belongs to the field it is
  printed against. Verify them first, and correct the probe's output if they are
  wrong.
- **File an update at each real milestone** - schema resolved, first record
  walked, first ship reconstructed and checked against the 4.9 snapshot's
  `ships.json`. Progress updates are not stops. Keep going.

**Three offsets have been read wrong today by three different code paths** -
the ZIP64 EOCD at 24 instead of 32, the DataForge header at 4 instead of 16,
and the wrong zstd DLL that answered its version probe and then segfaulted.
**In a binary format a plausible table is not evidence of a correct offset.**
Assert the identities and feed them known-bad input.

---

## NOT in this queue, and why

**The left panel rebuild** - `docs/ORDER_the-ship-page-is-a-spreadsheet-2026-08-26.md`.
C1 has sent Sleven a working mockup built from real data and it is waiting on
his eye. **That one IS gated, legitimately: it is a design decision about what
the visitor sees, which is his.** Do not start it.

**Anything under `/media/` on robertsspaceindustries.com.** Their robots.txt,
standing rule.
