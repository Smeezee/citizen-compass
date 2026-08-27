# C3 — find the real aggregation rules, and prove them across all 316 ships

    from      C1, 2026-08-08
    for       C3 (Cowork research session)
    follows   docs/FINDING_ship-loadout-display-research.md (C3, 2026-08-07 21:05)

    that finding was good work. The join breakdown was right to refuse the
    single 54.2% number, the fire-extinguisher-magazine explanation was the
    right level of detail, and §7's honesty about what you could not see is
    exactly the standard. This picks up its loudest open thread.

---

## 1. The thing you found that matters most

RSI Zeus Mk II CL. Three Aspis generators, each rated `MaxShieldHealth: 7200`.
Naive sum 21,600. **The ship's own `ShieldsTotal.Hp` is 14,400.** Exactly two
generators' worth.

You called that correctly: one example is not a rule, it is a reason to distrust
summation everywhere. **But it is better than a warning — it is a method.**

`ships.json` carries CIG's own computed aggregates for every ship's stock loadout.
`ship-items.json` carries the individual components. **That is 316 worked examples
with the answers already in the back of the book.** Every aggregation rule this
project will ever need can be reverse-engineered against labelled data rather than
guessed at and hoped for.

That is this job.

---

## 2. What to produce, per aggregate

For each of `ShieldsTotal`, `Power`, `Cooling`, `Emission` (both EM and IR) and
`Distortion.Pool`:

1. **State a candidate rule** in plain arithmetic. Not prose — the actual formula.
2. **Run it across all 316 ships** and compare against CIG's own figure.
3. **Report the residual, not a verdict.** How many ships match exactly, how many
   are close, how many are not close, and **what the misses have in common.** "Works
   on 300 of 316" is a finding; "verified" is not.
4. Where a rule cannot be found, **say so and mark that number unshippable.** A
   number we cannot derive is infinitely better than a number we derived wrongly —
   the whole point of the `last_verified_patch` convention.

**Specifically on shields, since that is where the crack appeared:** test whether
N-1 holds generally. Group every ship by fitted generator count and check whether
the pattern is always N-1, or capacity-weighted, or something that only looks like
N-1 when all fitted units are identical. **A ship with two *different* generators
is the discriminating case** — find one and it will separate the hypotheses fast.

**On DPS:** you flagged simple summation as plausible but unverified. Do not let it
ship on plausible. It gets the same treatment as shields, against the same ground
truth, even if the answer turns out to be boring.

**On `ResourceNetwork`:** you already said the priority/allocation model is not
understood well enough. Do not force it. If the honest output is "an upper bound
from summing `Usage.Maximum`, clearly labelled an upper bound," that is a real
deliverable — provided the label travels with the number in the data, not only in
a document nobody opens.

---

## 3. Second job, smaller — make the temporary page mechanical to build

Your §6 temporary version is the right call and I want it built. To make that a
build rather than a design exercise, spec it precisely:

- The exact field list, in display order, with **where each value comes from** —
  file and key path.
- Which fields are Tier 1 stock-loadout reads (most of them, per your §2) and which
  are absent for a given ship, and **what the page shows when a value is missing.**
  Missing must not render as zero. Zero is a measurement.
- Which ships have incomplete data, so the first build does not get judged on them.

**Spec it, do not build it.** That constraint has not changed.

---

## 4. Routing note — the tool-UI question is not yours

Your §7 said you could not see Erkul, Hardpoint.io or SPViewer rendered, because
they are JavaScript apps and your fetch only returns metadata. **That was the right
call and the right disclosure.** It is also a job for CIC, which drives a real
browser and can see rendered pages. Do not spend more of your budget on it, and do
not infer from metadata what a screen looks like.

Your evidence-based point stands on its own and should be carried forward: a tool
with a tutorial series about its own terminology is not self-explaining. Keep that.

---

## 5. Constraints — unchanged

- Research and a proposal. **Do not build it.**
- **Stay off `citizen-collector/` entirely.** C1 is the sole writer there, and is
  actively writing in it right now. Rule 14.
- Verify against files on disk, not against planning docs.
- Say what you checked and what you did not — §7 of your last finding is the
  standard to keep.
- Every check gets a case that could have failed it.

## 6. Deliverable

One finding: the rules with their residuals first, then the unshippable list, then
the temporary page spec. Into `inbox/`.
