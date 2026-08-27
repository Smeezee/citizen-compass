# ERRATUM — I called six shared models "defects" this morning. Five of them are defensible, and CIG's own published data says so. One real defect survives, plus one different problem I had mis-filed as a duplicate.

    from      C3 (Cowork), 2026-08-14
    corrects  FINDING_model-fingerprints-and-24-copied-models-2026-08-14.md, §3
    prompted  Sleven asked "see if we can get the right models" - and checking
              whether we could get better ones is what showed most of them are
              already right.
    dataset   data-layer/derived/model-fingerprints/model_integrity.json

---

## 1. What I got wrong

I listed six shared models as defects: C8/C8R Pisces, F7A/F7C Hornet Mk I, Cutlass
Steel, Mustang Gamma/Omega, the four Carracks, and Kraken/Kraken Privateer.

**I reasoned from ship names, not from evidence.** "The C8R is the medical variant
with a different interior bay" is something I asserted; I did not check it, and I
had no way to. That is the same failure this project already logged twice this week
— once on the Drake Marauder paint claim and once on the "legacy design queue"
phrasing — and it is the third time my reasoning has rested on something I never
verified.

## 2. The test I should have run first

CIG publishes length, width, height and mass for most ships. **If CIG publishes the
same figures for two ships, then one hull serving both agrees with CIG's own data
and calling it an error is calling CIG wrong.**

Run against `ship_specs.json`:

    C8 Pisces / C8R Pisces Rescue     16 x 12 x 8      mass 45,243      identical
    F7C / F7A Hornet Mk I             28.25 x 25.5 x 7.5  mass 72,032   identical
    Cutlass Black / Cutlass Steel     37.5 x 26.5 x 11.5  mass 242,177  identical
    Mustang Gamma / Mustang Omega     21.5 x 18 x 9    mass 28,565      identical
    Ironclad / Ironclad Assault       117 x 50 x 25    mass 720,000     identical
    Carrack / Carrack Expedition      126 x 74 x 30    mass 3,275,858   identical
    Aurora Mk I, all variants         19 x 8.75 x 4.5  (mass varies)    identical

**Every pair matches on all four figures.** Not approximately — the same numbers.
Five of my six defects are withdrawn, and the four-way Aurora share joins them.

**This does not prove the ships look alike.** It proves that nothing available to
this project shows they differ, which is a different and more honest claim. If
somebody stands next to a Cutlass Steel in game and it plainly is not a Cutlass
Black, that beats this — a measurement is not a photograph.

## 3. What actually survives

**One defect: `Carrack_w_C8X.glb` and `Carrack_Expedition_w_C8X.glb`.**

Byte-identical to `Carrack.glb`. These files exist for one reason — to show the
Carrack with its C8X snub docked. **A file cannot contain a docked snub and also be
byte-identical to the file without one.** This is not a judgement about ship design;
it is the file contradicting its own name, and no dimension table is needed to see
it.

**One unverifiable: `Kraken` / `Kraken_Privateer`.**

2 vertices apart, bounding boxes identical to three decimals — the signature of a
decal on an unchanged hull. **But `ship_specs.json` has no entry for either Kraken**,
so there are no published figures to test against and nothing available can settle
it. Flagged as unverified, not as wrong. It matters because both sit on the
upcoming-ships list.

**One thing I filed under the wrong heading entirely: `Aurora_LX.glb`.**

I mentioned it as an aside about model quality. It is the more interesting finding
of the two:

    Aurora CL / ES / LN / MR   one shared model   267,000 verts   height 4.355
    Aurora LX                  its own model       28,153 verts   height 3.733

CIG publishes **4.5 m height for every Aurora Mk I variant including the LX**. The
LX model is 14% shorter than its own siblings and 9.5x cruder. So the one Aurora
that does *not* share the hull is the one that disagrees with CIG's data — while
the four that do share it match. **The duplicate was correct and the unique file is
the suspect**, which is the exact reverse of how I framed it.

## 4. "Can we get the right models" — no, and mostly we do not need to

Three routes, all checked:

**The source library is already identical upstream.** Every shared `.glb` traces
back to `sc-ships/`, which holds the original `model.ctm` for 243 ships. I hashed
the `.ctm` files for all six pairs: **byte-identical there too**. So this is not our
conversion or copy step losing a distinction — the models arrived that way. Nothing
to recover.

**The Fan Kit cannot help.** It holds 14 models, one hero ship per manufacturer.
None of the affected ships is among them.

**Which leaves CIG's own site**, and that is not mine to touch. Whether we may pull
model assets from RSI is a licensing question and rule 8 puts it with Sleven alone.
**It is also probably not worth asking**, because §2 says CIG's own published data
does not distinguish these ships either.

**The one worth chasing is the Carrack snub**, and even there the honest question is
whether the source ever had a distinct file — not whether we lost it.

**Worth recording separately:** `sc-ships/` is 4.1 GB and **has no recorded
provenance**. There is no fetch script, no source URL, no manifest — the earliest
reference is a bulk drop into `inbox/`. Every model on the site descends from a
library whose origin is not written down anywhere. That is not urgent, but it is
exactly the shape of thing that becomes unanswerable later, and it should be written
down while somebody still remembers.

## 5. What was produced

`model_integrity.json` gives every shared file a verdict — `defect`,
`inconsistent`, `unverifiable`, `defensible`, `livery` — with the reasoning and the
CIG figures attached. 47 files covered.

**Only three of those verdicts should ever reach a reader.** The 12 livery groups
need no flag at all; flagging a paint variant for sharing a hull would be noise, and
the first version of this work would have produced exactly that.

## 6. What I checked and what I did not

**Checked:** the `.ctm` sources for all six pairs on Sleven's machine; the Fan Kit's
14-model list; `ship_specs.json` for published dimensions and mass on every affected
ship; the Aurora variants against each other and against CIG's figures.

**Did NOT check:**
- **What any of these ships actually look like.** Nobody here has compared them in
  game. Every verdict above is measurement, and measurement is the weaker evidence.
- **Whether the upstream library was right.** If `sc-ships` got it wrong, we
  inherited it and this finding inherits it too.
- **Whether a distinct Carrack-with-snub model exists anywhere.** I established ours
  is not one. I did not establish that a correct one is obtainable.
- Nothing was deleted, renamed or re-fetched.
