# FINDING — 87% of dots land exactly on their ship. Ten do not, on four hulls, and now we can say which.

    from    C1 (Cowork), 2026-08-29
    method  every ship shot TWICE - once with markers, once with them hidden -
            and each marker's screen position tested against the clean silhouette
    tool    offhull.py (audit, not a sweep control: it needs a browser and 50
            minutes, so it is run deliberately rather than on every build)

---

## 1. THE MEASUREMENT

2,193 dots across 259 ships, each one asked a single question: **how far is it
from the nearest pixel of its own ship?**

    on the hull, exactly (0px)   1,912 of 2,193    87.2%
    p90                          1px
    p99                          12px
    worst                        38px

**A dot cannot be tested against a picture that contains it**, so each ship was
photographed a second time with `#cc-marks` hidden, and the marker positions were
read out of the DOM at the same moment. The silhouette is the ship; the dots are
measured against it.

## 2. WHAT IS ACTUALLY WRONG — TEN DOTS, FOUR HULLS

    BANU_Defender          2 of  6 off    port 50 @19px, port 51 @38px
    DRAK_Corsair           3 of 15 off    port 80 @16px, 93 @17px, 94 @33px
      (and its two Exec variants, same model, same three)
    TMBL_Storm_AA          1 of  5 off    port 4 @15px
    VNCL_Glaive            1 of  9 off    port 43 @16px

**Confirmed by eye on the Defender**: two dashed markers sit in open space above
and left of the hull, with nothing under them. The Corsair's are the same shape
of error on a bigger ship.

**These are individual mounts, not a broken hull.** Every one of these ships has
most of its dots correctly placed, which is why nothing caught them: containment
passes (they are inside the box), the mirror passes, the spread test passes, and
provenance is honest. **A single mount in the wrong place is invisible to every
population-level check we have.**

## 3. TWO FALSE POSITIVES, AND BOTH TAUGHT SOMETHING

**The first instrument was a fixed radius.** At 7px it called the Avenger
Titan's forward spike adrift — the geometry there is a few pixels wide, so most
of the sample is background while the dot sits on the ship. **Replaced with the
distance to the nearest hull pixel**, which reads 0 on the hull, single digits on
thin geometry and tens when a dot is genuinely floating. A guess became a
reading, and the threshold could then be put in a gap that can be seen.

**The second was a fixed hull colour** — bright and warm, which is the gold most
ships render as. **The Asgard renders a dull bronze** and the test called all
fifteen of its dots adrift while the picture shows them on the ship. Colour is a
property of the render and it varies; **the background does not**. The hull is
now defined as *materially different from the empty stage*, learned from the
image's own corners, which holds whatever colour a ship renders in.

**Both were caught by looking at the picture the tool was describing.** A
detector that reports 15 of 15 wrong on one ship and 0 of 15 on its neighbour is
describing itself, not the fleet.

## 4. WHAT THIS IS AND IS NOT

**It is an audit, not a control.** It needs a real browser and fifty minutes for
a full pass, so it cannot sit in a sweep. It is run when the marker pipeline
changes, and its output is a contact sheet a person can scan in a minute.

**It does not say the other 2,183 dots are on the right mount** — only that they
are on the ship. A gun marker sitting on the wrong wing passes this test. That
question needs CIG's own port names against the geometry, which is what the
placement pipeline already does.

## 5. NEXT

The ten dots are worth chasing individually: four hulls, and the Corsair's three
repeat across two variants of the same model, so it is really **four distinct
mounts on four distinct ships**. Each one has a decoded CIG transform behind it,
so the question is whether the transform is wrong, or the conversion, or the
model's frame — answerable per mount rather than by rule.

**Two of the four are now fixed, and the cause was a rule that excused itself.**

The Defender's two dots are its countermeasure launchers, at **1.32 of the
hull's own half-extent** — beyond the nose. The acceptance test never saw them,
because it tested lateral and vertical only:

> *the fore/aft axis is where the scale came from and is deliberately NOT
> tested - that would be marking our own homework*

**That is wrong, and it excused the only axis nothing else watches.** The scale
comes from the model's box against CIG's published Length. It is not derived
from any mount position, so a mount landing past the nose is real information,
not a tautology. A mount can leave the hull in three directions and one of them
was unwatched by design.

    26,273 mounts measured
    93 fall outside fore/aft
    7 of those are EXTERIOR mounts that get drawn
      Defender  2 (confirmed floating by photograph)
      Hull C    1 (its nose turret)
      M80       4 (already refused for orientation)

Fore/aft is now tested at the same 6% margin as the other two axes. **Cost:
three mounts withheld on two hulls, both still passing.**

**The Corsair, the Storm AA and the Glaive are a different problem** — their
dots are INSIDE the hull box and still not on geometry, which means they sit in
a gap in the mesh rather than beyond its edge. Containment cannot catch that by
construction. Those three remain open, and per Sleven's instruction they wait
until everything else is finished.

— C1
