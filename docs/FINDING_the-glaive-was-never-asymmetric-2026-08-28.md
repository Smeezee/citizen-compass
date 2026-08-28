# FINDING — the Glaive was never asymmetric. The evidence proving its frame was being filtered out and thrown away.

    from    C1 (Cowork), 2026-08-28
    closes  M4, which stood as "still open, narrowly: a frame proof that does
            not assume symmetry"
    control `checks/_verify_placement_gate.py`, extended and green, now
            carrying the fleet's three hardest hulls by name

---

## 1. WHAT THE RECORD SAID, AND WHAT WAS ACTUALLY TRUE

`build_hardpoint_placement.py` carried this in its own source:

> **EVERY PAIR, NOT MOST.** The Glaive scores 2 of 4 and stays refused — its
> geometry is genuinely asymmetric where the mount names say it should not be.

`CURRENT-STATE.md` repeated it: *the Glaive and Scythe, **asymmetric ships, not
a bug***.

**The Glaive is not asymmetric where its names say it should not be.** Measured
over all its named left/right pairs, in the converted frame, at the same
tolerance:

    hardpoint_gun_nose_left      x = -0.560     _right  x = +0.567
    hardpoint_countermeasures    x = -2.588             x = +2.588
    hardpoint_engine             x = -1.123             x = +1.123
    hardpoint_fuel_intake        x = -2.441             x = +2.441
    hardpoint_powerplant         x = -0.376             x = +0.376

**13 of its 19 named pairs mirror to within 8.7 cm.** It scored 2 of 4 because
the mirror was computed over EXTERIOR mounts only, and the Glaive has almost no
exterior named pairs — its evidence is in the engines, coolers, intakes and
powerplants, which were filtered out before the test ran and discarded.

**The Scythe, refused in the same breath and named in the same sentence, is 1 of
16 and IS genuinely asymmetric.** Filtering had made two different ships look
like one problem, and the shared explanation was right about one of them.

---

## 2. WHY THE FILTER WAS WRONG, IN ONE LINE

**The frame is a property of the hull's coordinate system, not of which mounts
get drawn.** An interior mount's transform comes out of the same node array, in
the same run, through the same conversion as an exterior one. Restricting the
evidence to mounts that happen to be rendered threw away the larger half of it
for no reason anybody had written down.

---

## 3. THE RULE, AND THE OBJECTION IT HAS TO ANSWER

    frame_proven  =  at least 4 named pairs, and at least half of them mirror

**A fraction invites exactly one objection: that it was fitted to admit a ship
somebody wanted in.** So it was measured across the fleet, and then measured
again on every one of those hulls with the lateral and vertical axes
transposed — the defect the mirror exists to catch:

    hulls with 4+ named pairs                              265
    transposed axis, the highest fraction ANY hull reached 0.455
    correct frame, the lowest fraction above the midpoint  0.684
    passing a HALF rule        clean 262 of 265     transposed 0 of 265

**There is nothing between 0.455 and 0.684.** The rule sits in an empty gap
measured on the whole fleet.

**The per-pair tolerance is unchanged.** M4's standing warning — *nobody should
widen the mirror tolerance to get there* — is intact, and the tolerance was
never the lever. What changed is which pairs count and how many must agree.

**The bound that makes it safe is unchanged.** Mirroring survives a uniform
scale and a whole-hull offset, which is why a proven frame buys withholding at
most four mounts and never a pass. A rescaled hull still puts far more than four
outside its box and is still refused by containment.

---

## 4. AND THEN THE CONTROL FOUND SOMETHING OLDER AND WORSE

The gate control took six hulls in directory order. Six hulls that happen to be
first are not an adversarial test, so the fleet's worst case was pinned into it
by name — **the San'tok.yai, the one transposed hull that gets anywhere near the
fraction at 0.455.**

It immediately reported: **a transposed San'tok.yai PASSES THE GATE.**

Not because of the new rule. Because **the mirror was only ever consulted when
something was already outside the box**, and nothing lands outside the
San'tok.yai's box when its axes are swapped — that hull is nearly as tall as it
is wide. Containment had nothing to say and the mirror was never asked. **This
was equally true under the old all-or-nothing rule.** Naming the hard case is
what surfaced it.

**So the mirror is now a veto as well as a licence.** A hull with enough pairs to
judge, whose pairs mostly do not mirror, is refused outright whatever
containment says.

**It costs two hulls, and the cost is the point.** Both Clippers, at 2 of 8, lose
their markers. **A rule that admits the Glaive on the strength of its mirror has
to refuse the Clipper for the lack of one**, or it is not a rule — it is a
preference for the ships somebody wanted in.

A hull with fewer than four named pairs is **not** vetoed. Absence of evidence is
not evidence, and refusing on it would take out a large part of the fleet on no
measurement at all.

---

## 5. THE NET EFFECT

    VNCL_Glaive                       refused  ->  passed, 1 mount withheld
    drak_clipper                      passed   ->  refused
    drak_clipper_collector_military   passed   ->  refused
    VNCL_Scythe                       refused  ->  refused, and now for a
                                                   reason that is measured
    everything else                   unchanged

**60 hulls gained a proven frame and not one of them changed verdict** — they had
nothing outside their box, so it never mattered. That is the shape a safe change
makes: it moves the hulls it was aimed at and leaves the rest alone.

---

## 6. WHAT THE CONTROL LEARNED ABOUT ITSELF

Pinning the Scythe in as a subject made the control fail with *"the gate refuses
an UNMODIFIED hull, so it would refuse everything"*. **The Scythe is refused, on
purpose, and has been all along.** The negative control had quietly assumed every
hull in the placement output has a correct frame — which is false for precisely
the hulls under dispute, and is assuming the conclusion.

The positive half is now scoped to hulls the placer accepted, and refused hulls
are exercised as **named negatives** that must stay refused. The section fails if
no refused hull is among the subjects at all, so the skip cannot become a hole.

---

## 7. WHAT HAPPENS NEXT, SO NOBODY MISREADS A RED CHECK

`checks/_verify_marker_provenance.py` is **RED right now**, naming the Clippers.
That is correct: their dots are still in the deployed marker file labelled `cig`,
and the hull that justified the label has just been refused. **It clears when
Code rebuilds** — Q16.

— C1
