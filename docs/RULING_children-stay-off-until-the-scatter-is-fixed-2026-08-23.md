# RULING — Turret children stay OFF until the sibling scatter is fixed

**Sleven, 2026-08-23:** *"We'll hold off on shipping the children until we get the
scatter bug fixed. But everything else we can push, and get everything else
flushed out, and then we'll work on that after it's all done."*

**Rule 8 does not apply — this is an engineering call and it is his. Recorded so
nobody re-opens it or quietly flips the flag.**

---

## What ships

    B5 inheritance          BUILT, PROVEN, and OFF by default
    B6 measured extremity   SHIPS
    the rebuilt gate        SHIPS - 169 placed, 6 refused
    everything else in      SHIPS
      the B and H runs

`--with-children` stays off. The control that asserts the shipped dataset holds
**0 inherited and 0 child points** stays in place and stays load-bearing: it must
fail if anyone turns the flag on before the scatter is fixed.

## Why, in one line

**12 of 24 Hammerhead guns landed nearer a different turret than their own.** A
front-left gun drawn beside the rear turret is a confident wrong position, and
this project's standing principle is that a confident wrong answer is worse than
an absent one — hull centre at least looks wrong.

The measured trade, which is what made the call decidable:

    with children:  +160 markers on 5 more hulls
                    crowding 117 -> 451 markers, 19 -> 34 hulls

**+160 markers bought at the cost of quadrupling crowding is a bad trade on its
own**, and it is a worse one now that labels are the ship page's headline feature
(`ORDER_every-ship-is-a-hologram` H1b). 451 crowded markers would make label
deconfliction unsolvable on exactly the ships that need it most.

## What the fix is, when it is picked up

Not "spread the siblings less". **Spread an inherited sibling around ITS TURRET,
not across the hull**, and do not let the collision pass walk it arbitrarily far
from the turret it belongs to. The turret's own position is known and correct;
the children should be bounded by it.

**Deferred, not dropped.** It is the last item after the hologram work, and the
`0 inherited / 0 children` control is what keeps it honest in the meantime.

## Credit where it is due, because the process is the point

**Code built the feature, proved it on the Hammerhead, and then refused to ship
it because its own control caught the scatter.** It also corrected C1 on two
things in the same pass — the crowding figure was worse than reported, and the
placement gate had been built from the already-placed set, so it *"could not
refuse anything"*.

That is Rule 12 working as designed: a control that could have passed quietly
instead fired, and the person with the decision got numbers rather than a
reassurance.
