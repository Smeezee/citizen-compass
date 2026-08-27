# FINDING — the sentence C3 wants shipped first is half right, and the wrong half is the number in it. Shield absorption against ballistics is a RANGE from 0 to 0.45, not a value of 0.45. The energy half is exact. And shields carry a SECOND resistance block that is not the one that was declared closed.

    from      C1 (Cowork), 2026-08-27 18:20 local
    corrects  BRIEF_what-to-build-from-the-weapon-data §1 ("SHIP THIS FIRST")
              FINDING_the-interaction-is-computable §2 ("THE HEADLINE")
    method    measured on disk, ship-items.json, snapshot 20260827T030607Z,
              by a session that did not write either document
    PATCH     4.9 data. Structure survives 4.10; values will not.
    status    BUILT. The honest version is on the ship page as of this document.

---

## 1. What was proposed

> *"A shield stops all of a laser's damage and only 45% of a ballistic's. That is
> CIG's own number, identical on all 67 shields... If only one thing ships, ship
> the sentence."*

It was ranked first of six, ahead of everything requiring a calculator, on the
grounds that it costs nothing to publish. **That ranking is right. The sentence
is not.**

## 2. What the file actually says

`stdItem.Shield.Absorption`, every shield item in the snapshot:

    channel        Minimum   Maximum
    Physical       0         0.45      <- A RANGE
    Energy         1         1         <- the only fixed channel
    Distortion     1         1
    Thermal        1         1
    Biochemical    1         1
    Stun           1         1

    shield items                                    73
    distinct Absorption profiles across all of them   1

**Absorption is not a scalar. It is a Minimum and a Maximum**, and on Physical
the two ends are 0 and 0.45. `0.45` is the TOP of that range. At the bottom of
it a shield absorbs **none** of a ballistic hit.

**So "a shield stops 45% of a ballistic" is wrong in the direction that gets a
new player killed** — it promises protection that the bottom of the range does
not provide. The reader most likely to act on that sentence is the one who knows
least.

**CURRENT-STATE has carried this as an open question since 08-22:** *"what
Min/Max mean on the shield blocks (probably charge level, not established)."*
The brief published the Maximum as the value without resolving it.

## 3. The count is 73, not 67

Three counts now exist: the brief says 67, CURRENT-STATE says 73, and this
measurement says **73 shield items, all `Shield.UNDEFINED`, one profile.** I did
not reconcile where 67 comes from — a purchasable filter is the obvious guess and
a guess is not a finding. **What matters is that the uniformity claim survives
either number:** whichever set you take, there is exactly one profile in it.

## 4. THE PART THAT IS NOT A ROUNDING QUARREL — there is a second Resistance block

Every shield also carries `stdItem.Shield.Resistance`, a sibling of Absorption
on the same item:

    Physical       0        0.25
    Energy         0        0
    Distortion     0.75     0.95
    Thermal        0        0
    Biochemical    0        0
    Stun           0        0

    distinct Shield.Resistance profiles across 73 shields   1

The brief flagged the calculator as **"BLOCKED ON ONE THING... shields carry a
`Resistance` block as well as `Absorption` and nobody has established whether
they stack."** That blocker is real and it is still open.

**It was NOT closed by `FINDING_both-open-questions-closed`.** That finding
established that `Durability.Resistance` is item durability — damage to the
component itself rather than to the hull behind it — and it is correct about
that. But `Durability.Resistance` and `Shield.Resistance` are **different blocks
on different paths**, and the shield carries both:

    stdItem.Durability.Resistance   Physical 0.9  Energy 0.9  Thermal 0.1
                                    (one profile / 73, Multiplier+Threshold)
    stdItem.Shield.Resistance       Physical 0-0.25  Distortion 0.75-0.95
                                    (one profile / 73, Minimum+Maximum)

Different shape, different values, different meaning. **Reading the closure of
one as the closure of the other would retire an open question without answering
it** — which is worse than leaving it open, because nobody looks again.

I am not claiming C3 made that leap. I am recording that the two documents sit
four hours apart, name the same word, and the later one reads like a closure.
**It is not one.**

## 5. What shipped instead, and it is still the sentence

The fixed half is stated as fact, the range is stated as a range, and the
tradeoff survives both:

> **Every shield in the game carries identical damage numbers — 73 of 73, one
> profile. No shield you can buy changes any of this. A raised shield stops
> **all** of an energy weapon's damage. Against ballistics it stops **somewhere
> between none and 45%**, and what moves it along that range is not established
> — so a gatling puts at least half its damage through a shield that a laser
> cannot touch at all.**

**"At least half" is the honest floor** and it is derived from the Maximum: if
the most a shield ever absorbs is 45%, then at minimum 55% always gets through.
That is a claim the data supports at every point on the range, which "45% is
absorbed" is not.

**The brief's own argument survives intact.** It said the value of this is that
no other tool states it, that it needs no join and no calculator, and that it is
the single most useful thing a new player could read. All three still hold. Only
the number changed, and it changed into a statement that cannot be wrong.

**Live on the ship page**, under `What this build's guns do against armour`,
because the shield is the thing in front of the armour and a reader who stops at
the armour table leaves with half the mechanic. Stamped `SHIELDS · 4.9`, with the
open questions in the body rather than omitted.

## 6. Rule 16, and why this was catchable

**Neither document was measured by the session that wrote it.** Both cite the
same snapshot, and the second cites the first. I opened the file. The range was
visible in the first shield record I printed — `"Physical": {"Minimum": 0,
"Maximum": 0.45}` — and no amount of re-reading the briefs would have shown it,
because both had already collapsed it to a scalar before writing it down.

**That is the rule working as intended, and it cost about four minutes.**

## 7. What I checked and what I did not

**Checked:** all 73 shield items, both blocks, Minimum and Maximum on all six
channels; the Durability block on the same items; that nothing in the repo reads
`Absorption` today, so no wrong number is currently published anywhere; that the
built payload and page source contain no `45%` claim.

**Did NOT check:** what actually moves absorption along the range in the running
game — that is a client question, not a data one, and guessing it here is the
error this document exists to catch. **Did not reconcile 67 versus 73.** Did not
touch the effective-damage calculator; it remains blocked, and now for a reason
written down twice.

---

*C1, 2026-08-27. Measured before it was written, and built before it was filed.*
