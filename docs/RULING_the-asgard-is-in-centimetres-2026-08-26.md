# RULING — the Asgard is in centimetres, and the fit loop must not depend on clip planes

**2026-08-26 · C1 · answers Code's two questions after the F1/F2 deploy**

---

## Code's finding, confirmed and closed

Code reports the Asgard still black after F1/F2: its bounding box is
**3,388 × 1,333 × 4,856**, `frame()`'s opening distance of 11,851 is already
past `boot()`'s far plane of 10,000, every corner projects z > 1, the guard
scores that as full overshoot, and the camera runs to 1.25 million. He asks
whether the answer is the hull's units or the clip planes, and flags the
depth-precision cost of simply widening far.

**It is the units, AND the loop is wrong to depend on the planes. Both get
fixed, and they are separate jobs.**

### The Asgard is in centimetres. This is a data defect.

The game files state the Anvil Asgard's dimensions as **48 × 38 × 12 metres**.
The model measures 4,856 × 3,388 × 1,333. Axis-matched largest-to-largest:

    4856 / 48 = 101.2
    3388 / 38 =  89.2
    1333 / 12 = 111.1

**Roughly 100x on every axis. The model was never converted out of
centimetres.** This is the single centimetre-unit hull already recorded in the
model audit — 158 in metres, 8 normalised, 1 in centimetres. It has now been
identified by name.

**Fixing only the clip planes would render it wrong rather than not at all.**
At 100x the stage disc is sized for a 4.8 km hull, the markers are spread
across a football pitch, and the page's own size readout tells the visitor the
Asgard is 4,856 metres long. A ship rendering at a hundred times its stated
size is not better than a black panel — it is a black panel that lies.

### But the loop must not have been defeatable by clip planes in the first place

**This is the ruling that matters, and it is not about the Asgard.**

`_fitProjected` measures geometry. Its answer must not depend on near/far
values that were set for a different scene. Any asset that arrives outside the
size range `boot()` happens to assume — too big today, too small tomorrow —
defeats it the same way, and the failure mode is a black page with no error.
That is a class of defect, not one ship.

**The guard also conflates two different things.** `p.z > 1` is true both for a
corner BEHIND the camera and for a corner BEYOND THE FAR PLANE. They call for
opposite responses:

- **behind the camera** — genuinely not visible, backing off is correct
- **beyond the far plane** — the planes are wrong, and backing off makes it
  worse, which is exactly the 1.25 million-metre runaway

## The order

**A1 — the fit loop sets its own planes, measures, and hands them back.**
Before the passes, `_fitProjected` sets a near/far pair generous enough that no
corner of the box it was handed can fall outside them — derived from the box
and the target, not a constant. `_setClip` runs afterwards, exactly as it does
now, and the tight planes G2 chose are what every rendered frame uses.

**The wide planes exist only during measurement and are never in force for a
frame.** That answers Code's depth-precision objection directly: G2's ratio is
untouched, because nothing is rendered while they are set.

**A2 — split the guard.** Behind the camera and beyond the far plane become two
distinct branches. After A1 the second should be unreachable; a control should
assert that it is, so if it ever fires again we learn rather than run away.

**A3 — rescale the Asgard to metres** in the model pipeline, the same pass that
handled the other rescales. Its model becomes 48.6 × 33.9 × 13.3 or thereabouts
and the page stops publishing a wrong length.

**A4 — an auditor, because nobody caught this by looking.** For every hull,
compare the model's bounding box against the ship record's `dim`. Report any
hull where the two disagree by more than a stated factor. **It flags; it never
rescales** — standing rule, auditors do not fix data. A2 catches the ones so
wrong the camera fails. A4 catches the ones wrong enough to lie but not wrong
enough to break, and there is no reason to believe the Asgard is alone in that
band just because it is alone in the band that crashed.

A1 and A2 are viewer work and belong with F3. A3 and A4 are data-layer work and
are a separate commit.

---

## The second question — my table was wrong, and Code is right

He reports that the "after both" table in
`ORDER_the-camera-never-looked-at-the-ship-2026-08-26.md` reproduces to the
tenth with **F2 undone**, and that with F2 applied the fleet frames at ~2.3x
rather than ~2.9x.

**That is correct. The table is F1-only and is mislabelled.** It was measured
against the F1 build; the F2 numbers were taken separately and never folded in.
The Harbinger is 81.8 m / 2.9x with F1 alone and about 71 m / 2.5x with both —
I have that second figure in my own notes and published the first under the
wrong heading.

**F3's band is set against what shipped, which is F1 and F2.** Code's measured
2.0–2.5 across 238 hulls is the real distribution. A band of **1.8 to 6.0**
still holds it comfortably and still fails hard on the 826x–897x runaway and on
the Asgard's 1.25 million, which is what the band is for. **Do not narrow it to
hug 2.0–2.5** — a band tight enough to fail on a legitimate reframe is a band
that gets widened in a hurry by whoever it wakes up.

Code's own numbers, not the order's table, are the reference for F3.

---

# APPENDIX — "no 3D model" is mostly bookkeeping, not a missing model

**Added the same day, because Sleven hit it while checking the fix: the Origin
M80 says "No 3D model available" on our page and RSI's own site shows one.**

Folded in here rather than filed separately — it is the same subject as A3 and
A4, which is model data being wrong rather than model rendering being wrong.

## The count

**113 of 316 ships with a loadout have no model.** That number is misleading.

| | ships |
|---|---|
| say "no 3D model available" today | **113** |
| base ClassName exists, has a model, and the suffix is a known edition marker | **76** |
| everything else — needs a human look | **37** |
| of those, genuinely no model anywhere in any family | **15** |

**76 of the 113 are editions of a ship whose model we already hold**, and the
match is exact — the base ClassName exists in the data, it has a model, and
the suffix is one of the enumerated edition markers (`_BIS####`, `_Showdown`,
`_Teach`, `_BTALA`, `_Collector_*`, `_Exec_*`, `_Tier_N`, `_CitizenCon####`,
`_Pirate`, `_Boarded`, `_TEMP*`). No prefix guessing, no name matching.

Examples: *Drake Cutlass Black* (the BIS2950 edition) has no model while
`DRAK_Cutlass_Black` does. *Anvil Carrack* (BIS2950) has no model while
`ANVL_Carrack` does. *Drake Vulture Teach's Special* has no model while
`DRAK_Vulture` does.

**This is exactly the case Sleven already ruled on**, 2026-08-14:
`DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14.md` — a
shared hull is correct unless the ships differ in external shape. An edition is
paint and fitted parts. **The ruling exists; the join was never built.**

## The order

**M1 — editions inherit their base ship's model, by exact ClassName.** 76 ships
gain a model with no new asset and no download. The suffix list is written
down, not inferred, and a ClassName that does not match one is not touched.

**M2 — the 37 that are not an exact edition match get a human pass, not a
rule.** Several would be WRONG to auto-inherit and that is why they are not in
M1: *Idris-P* and *Idris-M* differ at the nose, *Sabre* and *Sabre Firebird*
are different airframes, *Hornet Mk I* and *Mk II* are different shapes.
Sleven's eye, one list, recorded as data.

**M3 — the 15 real gaps stay honest.** These have no model anywhere, in any
edition, in any family:

    Aegis Tiburon              Greycat PTV
    Argo MOTH                  Greycat UTV
    Drake Command Module       MISC Starlite
    Drake Pitbull              Origin 85X Limited
    Gatac Tyilui               Origin M80
    Grey's Basher              RSI Hermes
    Power Suit                 RSI Mantis
    Vanduul Mauler Destroyer

The page already says the right thing for these — the game files describe the
hull, every number below is real, we have no model. That message stays.

## And the part that is NOT mine to decide

RSI's own site has a model for the M80 and for others on that list of 15.
**Whether anything of theirs may be taken is Sleven's call and nobody else's —
Rule 8, legal and Fan Kit questions are his alone.** Two facts he should have
in front of him when he makes it, and neither is a recommendation:

- Their `robots.txt` forbids `/media/`, and this project's standing rule is
  that we do not fetch under it.
- The Fan Kit's holoviewer models are 14 ships only, in OpenCTM, bare geometry
  — already inventoried, and the M80 is not among them.

So the 15 do not have a technical answer available today. **They have a
question that belongs to Sleven, and 76 ships that need no question at all.**
